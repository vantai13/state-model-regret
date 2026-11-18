"""Doan Van Tai — piecewise-real-TM adapter for the imported EV-TE engine.

The C++ extension reuses EV-TE RNG, Sparse, and exact fluid step verbatim by
prefixing its existing source. No edits to EV-TE or E4. Endpoint fast-forwarding
is allowed only when all queues are zero and every modulated load is <= capacity.
"""
import ctypes as ct
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile

import numpy as np

from experiments.ext_validity import ev_te as T

DT, BETA, SLOT = .05, .3, 900.
HOURS = np.array([1., 2., 4., 6.])
TAU_SECONDS = (300., 900.)

_EXTRA = r'''
extern "C" void variable(int N,int A,int E,int D,int S,int H,
 const int*lengths,const int*hs,const double*w,const double*cap,
 double beta,double dt,const double*initial_m,const double*initial_q,
 uint64_t seed,int shortcut,int trace_first,double*out,double*final_m,
 double*final_q,double*backlog){
 RNG rng(seed);double p=-expm1(-2*dt)/2;
 vector<Sparse>route;vector<int>safe;
 for(int s=0;s<S;s++){
  route.emplace_back(A,E,D,w+s*A*E*D);bool ok=true;
  for(int ae=0;ae<A*E;ae++){
   double mu=0;for(int j=0;j<D;j++)mu+=w[(s*A*E+ae)*D+j];
   if((1+beta)*mu>cap[ae%E])ok=false;
  }
  safe.push_back(ok);
 }
 for(int i=0;i<N;i++){
  vector<double>m(initial_m+i*D,initial_m+(i+1)*D),q(A*E),cost(A,0);
  for(int ae=0;ae<A*E;ae++)q[ae]=initial_q[i*E+ae%E];
  int ck=0,t=0;
  for(int s=0;s<S;s++){
   bool empty=std::all_of(q.begin(),q.end(),[](double v){return v==0;});
   if(shortcut && safe[s] && empty){
    // Exact conditional endpoint law of the E4 sampled two-state chain.
    double pend=-expm1(-2*dt*lengths[s])/2;
    if(trace_first && i==0)for(int z=0;z<lengths[s];z++)
     for(int a=0;a<A;a++)backlog[(t+z)*A+a]=0;
    while(ck<H && hs[ck]<=t+lengths[s]){
     for(int a=0;a<A;a++)out[(i*A+a)*H+ck]=cost[a];ck++;
    }
    for(int j=0;j<D;j++)if(rng.uniform()<pend)m[j]=-m[j];
    t+=lengths[s];continue;
   }
   for(int z=0;z<lengths[s];z++,t++){
    if(trace_first && i==0)for(int a=0;a<A;a++){
     double sum=0;for(int e=0;e<E;e++)sum+=q[a*E+e];backlog[t*A+a]=sum;
    }
    for(int a=0;a<A;a++)for(int e=0;e<E;e++)
     cost[a]+=step(q[a*E+e],route[s].load(a*E+e,m,beta)-cap[e],dt);
    for(int j=0;j<D;j++)if(rng.uniform()<p)m[j]=-m[j];
    if(ck<H && t+1==hs[ck]){
     for(int a=0;a<A;a++)out[(i*A+a)*H+ck]=cost[a];ck++;
    }
   }
  }
  std::copy(m.begin(),m.end(),final_m+i*D);
  std::copy(q.begin(),q.end(),final_q+i*A*E);
 }
}
'''
_LIB = None


def native():
    global _LIB
    if _LIB is None:
        source = T._CPP + _EXTRA
        digest = hashlib.sha256(source.encode()).hexdigest()[:20]
        build = Path(tempfile.gettempdir())/f'smr_v7_3_{os.getuid()}_{digest}'
        build.mkdir(exist_ok=True)
        library = build/'kernel.so'
        if not library.exists():
            cpp, target = build/f'kernel_{os.getpid()}.cpp', build/f'kernel_{os.getpid()}.so'
            cpp.write_text(source)
            subprocess.run(['g++','-std=c++17','-O3','-ffp-contract=off','-shared','-fPIC',str(cpp),'-o',str(target)],check=True,capture_output=True)
            os.replace(target,library)
        _LIB = ct.CDLL(str(library))
        f64 = np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
        i32 = np.ctypeslib.ndpointer(dtype=np.int32,flags='C_CONTIGUOUS')
        _LIB.variable.argtypes = ([ct.c_int]*6+[i32]*2+[f64]*2+[ct.c_double]*2
                                  +[f64]*2+[ct.c_uint64]+[ct.c_int]*2+[f64]*4)
        _LIB.variable.restype=None
    return _LIB


def variable(incidence, demand, capacity, modes, queues, seed, *, lengths=None,
             hs=None, dt=DT, beta=BETA, shortcut=True, trace=False, reduce=True):
    """All actions share each OD mode path; return all action endpoint queues."""
    incidence, demand, modes, queues = [np.asarray(x,dtype=float) for x in (incidence,demand,modes,queues)]
    a,e,d = incidence.shape
    if (demand.ndim!=2 or demand.shape[1]!=d or modes.ndim!=2 or modes.shape[1]!=d
            or queues.shape!=(len(modes),e) or not len(demand) or not len(modes)
            or any(not np.isfinite(x).all() for x in (incidence,demand,modes,queues))
            or (incidence<0).any() or (demand<0).any() or (queues<0).any()
            or not np.isin(modes,[-1.,1.]).all() or dt<=0 or beta<0 or beta>1):
        raise ValueError('invalid fluid input shapes or values')
    lengths = np.full(len(demand),round(SLOT/dt),dtype=np.int32) if lengths is None else np.asarray(lengths,dtype=np.int32)
    if lengths.shape!=(len(demand),) or (lengths<1).any():
        raise ValueError('invalid slot lengths')
    total = int(lengths.sum())
    hs = T._hs([total] if hs is None else hs)
    if hs[-1]>total:
        raise ValueError('horizon exceeds supplied training demand')
    # Only simulate to the last requested checkpoint.
    cumulative=np.cumsum(lengths)
    last=int(np.searchsorted(cumulative,hs[-1]))
    lengths=lengths[:last+1].copy()
    lengths[-1]=hs[-1]-(cumulative[last-1] if last else 0)
    demand=demand[:last+1]
    cap=np.ascontiguousarray(np.broadcast_to(capacity,(e,)),dtype=float)
    if not np.isfinite(cap).all() or (cap<=0).any():
        raise ValueError('invalid capacity')
    full_modes, full_e = modes, e
    if reduce:
        upper=(1+beta)*np.einsum('aed,sd->sae',incidence,demand,optimize=True)
        active=(upper>cap).any(axis=(0,1)) | (queues>0).any(axis=0)
        relevant=(incidence[:,active]!=0).any(axis=(0,1))
        incidence=incidence[:,active][:,:,relevant]
        demand=demand[:,relevant]
        modes=modes[:,relevant]
        queues=queues[:,active]
        cap=np.ascontiguousarray(cap[active])
        e,d=incidence.shape[1:]
    weights=np.ascontiguousarray(incidence[None]*demand[:,None,None,:])
    costs=np.zeros((len(modes),a,len(hs)))
    fm, fq=np.empty(modes.shape,dtype=float),np.empty((len(modes),a,e))
    backlog=np.empty((int(hs[-1]),a)) if trace else np.empty(0)
    native().variable(len(modes),a,e,d,len(lengths),len(hs),np.ascontiguousarray(lengths),hs,
                      weights,cap,beta,dt,np.ascontiguousarray(modes),np.ascontiguousarray(queues),
                      seed,int(shortcut),int(trace),costs,fm,fq,backlog)
    if reduce:
        restored=np.zeros((len(modes),a,full_e))
        restored[:,:,active]=fq
        endpoint=full_modes.copy()
        probability=-np.expm1(-2*dt*hs[-1])/2
        rng=np.random.default_rng(T.seed_for(seed,'certified-inactive-OD-endpoints'))
        endpoint[:,~relevant]*=np.where(rng.random((len(modes),int((~relevant).sum())))<probability,-1.,1.)
        endpoint[:,relevant]=fm
        fq,fm=restored,endpoint
    return costs,fm,fq,backlog


def mean_endpoint(model,modes,queues,dt,steps):
    """Endpoint of the SAME discrete conditional-mean fluid path as T.twin_costs.

    With one fast mode, each link drift is d+b*r**k, monotone. The cumulative
    drift minimum is at an endpoint or one of the two steps around its zero.
    """
    decay=np.exp(-2*dt)
    ends=np.empty((len(modes),len(model.weights),len(model.capacity)))
    for a,w in enumerate(model.weights):
        d=w.sum(axis=1)-model.capacity
        b=BETA*(modes@w.T)
        def cumulative(k):
            return dt*(d*k+b*(-np.expm1(-2*dt*k))/(-np.expm1(-2*dt)))
        last=cumulative(steps)
        low=np.minimum(0.,last)
        ratio=np.divide(-d,b,out=np.full_like(b,-1.),where=b!=0)
        root=np.log(np.maximum(ratio,np.finfo(float).tiny))/np.log(decay)
        for k in (np.floor(root),np.floor(root)+1):
            k=np.clip(k,0,steps)
            low=np.minimum(low,cumulative(k))
        ends[:,a]=queues+last-np.minimum(0.,queues+low)
    return np.maximum(0.,ends)


def mean_rollout(incidence,profile,capacity,modes,queues, *, dt=DT,slot_seconds=SLOT,hs=None):
    """Operator forecast; never takes an actual test-night future TM."""
    a,e,d=incidence.shape
    steps=round(slot_seconds/dt)
    hs=np.asarray(np.rint(HOURS*3600/dt),dtype=int) if hs is None else np.asarray(hs,dtype=int)
    # A pathwise envelope, not a numerical small-value threshold.
    if not np.asarray(queues).any() and ((1+BETA)*np.einsum('aed,sd->sae',incidence,profile,optimize=True)<=capacity).all():
        if len(profile)*steps<hs[-1]:
            raise ValueError('profile too short')
        return np.zeros((len(modes),a,len(hs)))
    q=np.repeat(np.asarray(queues)[:,None,:],a,axis=1)
    m=np.asarray(modes).copy()
    costs=np.zeros((len(m),a,len(hs)))
    running=np.zeros((len(m),a)); now=0
    for values in profile:
        remaining=min(steps,int(hs[-1])-now)
        while remaining>0:
            next_h=int(hs[hs>now][0])
            length=min(remaining,next_h-now)
            for action in range(a):
                weights=np.ascontiguousarray((incidence[action]*values)[None])
                cap=np.broadcast_to(capacity,(e,)).copy()
                mod=T.Model(weights,cap,np.ones(d),BETA,[],[])
                if ((1+BETA)*weights.sum(axis=2)<=cap).all() and not q[:,action].any():
                    continue
                cost=T.twin_costs(mod,m,q[:,action],dt,[length])
                running[:,action]+=cost[:,0,0]
                q[:,action]=mean_endpoint(mod,m,q[:,action],dt,length)[:,0]
            m*=np.exp(-2*dt*length)
            now+=length; remaining-=length
            if now in hs:
                costs[:,:,np.flatnonzero(hs==now)[0]]=running
        if now==hs[-1]:
            return costs
    raise ValueError('profile too short')


def warm_instances(incidence,warm,capacity,n,seed):
    d,e=incidence.shape[-1],incidence.shape[-2]
    # Independent per-instance warmup roots; Stay only, from empty at 22:00.
    modes=np.empty((n,d));queues=np.empty((n,e))
    stale={tau:(np.empty((n,d)),np.empty((n,e))) for tau in TAU_SECONDS}
    zero_certificate=((1+BETA)*(warm@incidence[0].T)<=capacity).all()
    # 22:00->23:45, then 23:45->23:55, then 23:55->00:00.
    cuts=[(warm[:7],None,900.),(warm[7:],np.array([12000]),300.),(warm[7:],np.array([6000]),None)]
    for i in range(n):
        root=T.seed_for(seed,f'warm-instance={i}')
        m=np.random.default_rng(root).choice([-1.,1.],size=(1,d));q=np.zeros((1,e))
        if zero_certificate:
            for seconds,label,tau in [(6300.,'to-2345',900.),(600.,'to-2355',300.),(300.,'to-midnight',None)]:
                rng=np.random.default_rng(T.seed_for(root,label))
                m*=np.where(rng.random(m.shape)<-np.expm1(-2*seconds)/2,-1.,1.)
                if tau is not None:
                    stale[tau][0][i],stale[tau][1][i]=m[0],q[0]
            modes[i],queues[i]=m[0],q[0]
            continue
        _,m,fq,_=variable(incidence[:1],cuts[0][0],capacity,m,q,T.seed_for(root,'to-2345'))
        q=fq[:,0];stale[900.][0][i]=m[0];stale[900.][1][i]=q[0]
        _,m,fq,_=variable(incidence[:1],cuts[1][0],capacity,m,q,T.seed_for(root,'to-2355'),lengths=cuts[1][1])
        q=fq[:,0];stale[300.][0][i]=m[0];stale[300.][1][i]=q[0]
        _,m,fq,_=variable(incidence[:1],cuts[2][0],capacity,m,q,T.seed_for(root,'to-midnight'),lengths=cuts[2][1])
        modes[i],queues[i]=m[0],fq[0,0]
    return (modes,queues),stale


def forward_posterior(incidence,last_tm,capacity,state,tau,k,seed):
    m,q=(np.repeat(x,k,axis=0) for x in state)
    # Both supported stale ages lie inside the 23:45 TM slot.
    _,m,fq,_=variable(incidence[:1],last_tm[None],capacity,m,q,seed,lengths=[round(tau/DT)])
    return m,fq[:,0]

# tamper
