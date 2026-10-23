"""Doan Van Tai — reflected two-mode queue with an explicit error certificate.

The finite chain is capped only for the numerical solve. Its output is NOT
declared to be the infinite law. A Lyapunov tail bound, return-time bound and
stationarity residual bound quantify the difference. Inputs are rational keep
probability plus an optional interval radius for a physical R2 probability.
"""
import math
from decimal import Decimal as D, localcontext, ROUND_CEILING, ROUND_FLOOR
from fractions import Fraction as F

import numpy as np
from scipy.sparse import csr_matrix,eye
from scipy.sparse.linalg import splu


class StationaryBudgetError(RuntimeError):
    pass


def _d(v):
    v=F(v)
    return D(v.numerator)/D(v.denominator)


def r2_keep(dt,T,digits=70):
    """Center and a conservative rational interval radius around exp-based keep."""
    if dt<=0 or T<=0: raise ValueError('positive dt and T')
    with localcontext() as c:
        c.prec=digits
        z=-2*_d(dt)/_d(T)
        e=z.exp(); s=(1+e)/2
        # Covers exp rounding and argument/division rounding at this precision.
        radius=D(10)**(-(digits-5))*(1+abs(z))
        return F(s),F(radius)


def tail_plan(increments,keep,keep_error=F(0),tail_tol=1e-20):
    off,on=increments; keep=F(keep); err=F(keep_error)
    if any(type(x) is not int for x in increments) or not off<0<on or off+on>=0:
        raise ValueError('integer increments off<0<on, negative stationary drift')
    if math.gcd(-off,on)!=1: raise ValueError('reduce to the coprime queue lattice first')
    if not 0<keep-err<=keep+err<1 or err<0 or not 0<tail_tol<1:
        raise ValueError('irreducible probability interval and tail tolerance required')
    P=np.array([[float(keep),float(1-keep)],[float(1-keep),float(keep)]])
    best=None
    with localcontext() as c:
        c.prec=70
        ps=(_d(keep),_d(1-keep)); pe=_d(err)+D('1e-60')
        for t in np.geomspace(1e-7/max(abs(off),on),4/max(abs(off),on),160):
            K=np.exp(float(t)*np.array(increments))[:,None]*P
            values,vectors=np.linalg.eig(K)
            i=int(np.argmax(values.real)); v=np.abs(vectors[:,i].real)
            if min(v)<=0: continue
            vd=[D(str(float(x/min(v)))) for x in v]
            td=D(str(float(t))); ratios=[]
            with localcontext() as up:
                up.prec=70; up.rounding=ROUND_CEILING
                for m,a in enumerate(increments):
                    exp_upper=(td*D(a)).exp().next_plus()
                    terms=sum((ps[0 if m==n else 1]+pe)*vd[n] for n in (0,1))
                    ratios.append(exp_upper*terms/vd[m])
                lam=max(ratios)
                if lam>=1: continue
                pref=max(vd)/min(vd)/(1-lam)
                cutoff=int(((pref/D(str(tail_tol))).ln()/td).to_integral_value(rounding=ROUND_CEILING))
                # Verify chosen cutoff rather than relying on log rounding.
                bound=pref*(-td*cutoff).exp().next_plus()
                while bound>D(str(tail_tol)):
                    cutoff+=1; bound=pref*(-td*cutoff).exp().next_plus()
            item=dict(cutoff=cutoff,theta=str(td),lambda_upper=str(lam),
                      prefactor_upper=str(pref),tail_bound=str(bound))
            if best is None or cutoff<best['cutoff']: best=item
    if best is None: raise StationaryBudgetError('no negative exponential drift certificate found')
    return best


def stationary_two_mode(increments,keep,keep_error=F(0),tail_tol=1e-20,
                        tv_tol=1e-10,cap_limit=50000,refinements=4):
    """Return float mass[q,mode] with a conservative infinite-law error bound."""
    plan=tail_plan(increments,keep,keep_error,tail_tol)
    cap=plan['cutoff']; s=float(keep)
    if cap>cap_limit:
        raise StationaryBudgetError(f'required cap {cap} exceeds declared limit {cap_limit}')
    n=2*(cap+1); edges=[]; rr=[]; cc=[]; data=[]
    for q in range(cap+1):
        for m,a in enumerate(increments):
            i=2*q+m; end=min(cap,max(0,q+a))
            for mode in (0,1):
                j=2*end+mode; p=s if m==mode else 1-s
                edges.append((i,j,m==mode))
                if i and j: rr.append(i-1); cc.append(j-1); data.append(p)
    Q=csr_matrix((data,(rr,cc)),shape=(n-1,n-1))
    occupation_lu=splu((eye(n-1,format='csc')-Q.T).tocsc())
    b=np.zeros(n-1); b[0]=1-s
    trial=occupation_lu.solve(b)
    h=splu((eye(n-1,format='csc')-Q).tocsc()).solve(np.ones(n-1))
    if np.any(~np.isfinite(h)) or np.any(h<0): raise ArithmeticError('invalid hitting-time trial')
    if np.max(h)>1e18: raise StationaryBudgetError('return time exceeds declared precision envelope')
    with localcontext() as c:
        c.prec=70
        sd,ed=_d(keep),_d(keep_error)+D('1e-60'); ps=(sd,1-sd)
        z=[D(1)]+[D.from_float(float(v)) for v in trial]
        for _ in range(refinements):
            residual=z.copy(); residual[0]=D(0)
            for i,j,same in edges:
                if j: residual[j]-=z[i]*ps[0 if same else 1]
            correction=occupation_lu.solve(np.array([-float(v) for v in residual[1:]]))
            for i,v in enumerate(correction,1): z[i]+=D.from_float(float(v))
        if any(v<0 for v in z): raise ArithmeticError('negative invariant occupation after refinement')
        norm=sum(z); pi=[v/norm for v in z]
        # Bellman supersolution for return to state (q=0,off).
        hd=[D(0)]+[D.from_float(float(v)) for v in h]
        with localcontext() as low:
            low.prec=70; low.rounding=ROUND_FLOOR
            residual_h=hd.copy()
            for i,j,same in edges:
                if i and j:
                    with localcontext() as up:
                        up.rounding=ROUND_CEILING
                        term=(ps[0 if same else 1]+ed)*hd[j]
                    residual_h[i]-=term
            minimum=min(residual_h[1:])
        if minimum<=0: raise ArithmeticError('return-time supersolution not certified')
        with localcontext() as up:
            up.prec=70; up.rounding=ROUND_CEILING
            T=max(hd)/minimum
        incoming_low=[D(0)]*n; incoming_high=[D(0)]*n
        for i,j,same in edges:
            p=ps[0 if same else 1]
            with localcontext() as low:
                low.rounding=ROUND_FLOOR
                incoming_low[j]+=pi[i]*(p-ed)
            with localcontext() as up:
                up.rounding=ROUND_CEILING
                incoming_high[j]+=pi[i]*(p+ed)
        with localcontext() as up:
            up.rounding=ROUND_CEILING
            residual_tv=sum(max(abs(lo-v),abs(hi-v)) for lo,hi,v in zip(incoming_low,incoming_high,pi))/2+D(n)*D('1e-60')
            norm_error=abs(sum(pi)-1)+D(n)*D('1e-60')
            mass=np.array([float(v) for v in pi]).reshape(cap+1,2)
            conversion=sum(abs(D.from_float(float(x))-v) for x,v in zip(mass.flat,pi))
            tail=D(plan['tail_bound'])
            error=(1+2*T)*tail+2*T*(residual_tv+norm_error)+conversion+norm_error
        if error>D(str(tv_tol)):
            raise ArithmeticError(f'infinite-law error bound {error} exceeds {tv_tol}')
    certificate=dict(**plan,return_time_upper=str(T),residual_tv_upper=str(residual_tv),
                     infinite_law_error_upper=str(error),keep_error=str(keep_error),
                     law='symmetric keep interval supplied by caller',
                     cap_used_for_numerical_solve=True,cap_is_physical_buffer=False)
    return mass,certificate


def quantile(mass,alpha):
    if not 0<alpha<1: raise ValueError('quantile level must lie in (0,1)')
    q=int(np.searchsorted(np.cumsum(mass.sum(axis=1)),alpha,side='left'))
    if q>=len(mass): raise ArithmeticError('quantile beyond available law')
    return q


def quantile_interval(mass,alpha,law_error):
    if not 0<alpha<1 or not 0<=law_error<1: raise ValueError('invalid quantile/error')
    cdf=np.cumsum(mass.astype(np.longdouble).sum(axis=1))
    error=law_error+4*len(mass)*np.finfo(np.longdouble).eps
    lower=int(np.searchsorted(cdf+error,alpha,side='left'))
    upper=int(np.searchsorted(cdf-error,alpha,side='left'))
    return lower,(upper if upper<len(cdf) else None)


def conditional_mode_interval(mass,q,law_error):
    if type(q) is not int or not 0<=q<len(mass) or not 0<=law_error<1:
        raise ValueError('invalid backlog index/error')
    probability=float(mass[q].sum())
    if probability<=law_error: raise ArithmeticError('conditioning event not certified positive')
    return mass[q]/probability,min(1.,2*law_error/(probability-law_error)+16*np.finfo(float).eps)
