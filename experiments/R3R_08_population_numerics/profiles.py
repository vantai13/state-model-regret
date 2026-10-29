"""K-independent state costs and stale expectations on the exact action lattice."""
from fractions import Fraction as F
import fcntl
import hashlib
import json
import math
import os
import resource
import time
from pathlib import Path
import numpy as np
from smr.stationary import r2_keep
from . import piecewise as P


def quantum(values):
    denominator=math.lcm(*(F(v).denominator for v in values))
    return F(math.gcd(*(int(F(v)*denominator) for v in values)),denominator)


def get(lam,pre,post,kappa,h,ref,unit,cache,*,cost_budget='1/10000',progress=lambda *a,**k:None):
    dt=F(1,120*ref);H=F(h)/dt
    if H.denominator!=1:raise ValueError('physical horizon not on selected grid')
    H=int(H);params=[str(F(x)) for x in (lam,pre,post,kappa,h,unit,F(cost_budget))]+[ref]
    sources=[__file__,P.__file__,str(Path(P.__file__).with_name('native')/'piecewise.cpp'),'src/smr/stationary.py']
    source=hashlib.sha256(''.join(hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sources).encode()).hexdigest()
    key=hashlib.sha256(json.dumps([params,source]).encode()).hexdigest();folder=Path(cache);folder.mkdir(parents=True,exist_ok=True)
    meta=folder/(key+'.json');data=folder/(key+'.npz')
    constructed=0.
    with (folder/(key+'.lock')).open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if meta.exists():
            record=json.loads(meta.read_text())
            if record['source']!=source or record['parameters']!=params or hashlib.sha256(data.read_bytes()).hexdigest()!=record['sha256']:
                raise ValueError('cost profile checkpoint provenance/bytes mismatch')
            arrays=np.load(data);profiles={}
            for name,item in record['profiles'].items():
                profiles[name]=dict(modes=[(arrays[name+f'_x{m}'],arrays[name+f'_y{m}']) for m in (0,1)],error=P.LD(item['error']),peak_knots=item['peak_knots'])
            progress('cost_profiles_cache_hit',key=key)
        else:
            children=resource.getrusage(resource.RUSAGE_CHILDREN)
            started=time.process_time()+children.ru_utime+children.ru_stime
            amounts=[(F(lam)+s*6+F(load)-10)*dt for s in (-1,1) for load in (pre,post)]
            q=quantum([*amounts,unit]);factor=unit/q
            if factor.denominator!=1:raise ArithmeticError('unaligned action lattice')
            st=tuple(int((F(lam)+s*6+F(pre)-10)*dt/q) for s in (-1,1))
            sw=tuple(int((F(lam)+s*6+F(post)-10)*dt/q) for s in (-1,1))
            keep,ke=r2_keep(dt,F(kappa));scale=P.number(q*dt);raw_budget=P.number(F(cost_budget))/scale
            progress('cost_profiles_started',parameters=params,H=H,increments_st=st,increments_sw=sw)
            Wst=P.idle(H,st,keep,ke,error_budget_raw=raw_budget)
            Wsw=Wst if F(pre)==F(post) else P.idle(H,sw,keep,ke,error_budget_raw=raw_budget)
            d=P.combine(Wsw,Wst,subtract=True)
            Mst=P.mean_idle(H,st,keep,ke);Msw=Mst if F(pre)==F(post) else P.mean_idle(H,sw,keep,ke)
            dh=P.combine(Msw,Mst,subtract=True)
            if F(pre)==F(post):
                for value in (d,dh):
                    value['modes']=[(np.array([0,1],dtype=np.int64),np.zeros(2,dtype=P.LD)) for _ in (0,1)];value['error']=P.LD(0)
            old_d=P.age(d,120*ref,st,keep,ke,error_budget_raw=raw_budget)
            old_h=P.age(dh,120*ref,st,keep,ke,error_budget_raw=raw_budget)
            profiles=dict(Wst=Wst,d=d,dh=dh,old_d=old_d,old_h=old_h)
            flat={name+f'_{axis}{m}':value['modes'][m][i] for name,value in profiles.items() for m in (0,1) for i,axis in enumerate(('x','y'))}
            temporary=folder/(key+'.tmp.'+str(os.getpid())+'.npz');np.savez(temporary,**flat);temporary.rename(data)
            record=dict(parameters=params,source=source,quantum=str(q),factor=int(factor),scale=str(scale),H=H,dt=str(dt),
                        increments_st=list(st),increments_sw=list(sw),
                        saturation_cost=str((F(pre)-F(post))*dt*dt*H*(H+1)/2),
                        saturation_OFF_max_index=max(-1,min(-st[0],-sw[0])) if F(lam)+max(F(pre),F(post))<10 else -1,
                        identical_actions=F(pre)==F(post),
                        profiles={name:dict(error=str(v['error']),peak_knots=v['peak_knots'],knots=[len(x) for x,y in v['modes']]) for name,v in profiles.items()},
                        sha256=hashlib.sha256(data.read_bytes()).hexdigest())
            children=resource.getrusage(resource.RUSAGE_CHILDREN)
            constructed=time.process_time()+children.ru_utime+children.ru_stime-started
            record['cold_cpu_seconds']=constructed
            meta.write_text(json.dumps(record,indent=2)+'\n');progress('cost_profiles_completed',key=key,profiles=record['profiles'])
    return {**record,'profiles':profiles,'key':key,'created_cpu_seconds':constructed}


def values(side,name,indices,mode):
    profile=side['profiles'][name];indices=np.asarray(indices,dtype=np.int64)
    q=np.maximum(0,indices)*side['factor'];scale=P.LD(side['scale'])
    val=P.evaluate(profile,q,mode)*scale
    exact_zero=(indices<0)|(q>=profile['modes'][mode][0][-1])
    if side['identical_actions'] and name!='Wst':exact_zero[:]=True
    error=np.full(len(indices),profile['error']*abs(scale),dtype=P.LD)
    error+=256*P.EPS*(np.max(abs(profile['modes'][mode][1]))+1)*abs(scale)
    val=np.where(exact_zero,P.LD(0),val);error=np.where(exact_zero,P.LD(0),error)
    sat=np.zeros(len(indices),dtype=bool)
    if name=='dh' and mode==0:
        sat=(indices>=0)&(q<=side['saturation_OFF_max_index'])
        val[sat]=P.number(F(side['saturation_cost']));error[sat]=8*P.EPS*(abs(P.number(F(side['saturation_cost'])))+1)
    return val,error,exact_zero,sat
