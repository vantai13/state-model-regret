"""Doan Van Tai — contract-v1.2 cells and factorized pre-decision D.

Rebuilt from the unchanged design scripts; see notes/phases/PHASE_3.md §8
and results/lessons/l3_1/part3/config.json for exact origins and hashes.
Unlike smr.design (L1.8C), both queues have their declared ON/OFF modes.
This module computes no action costs, margins, regrets or contrasts.

The inherited implementation uses age=1 s, mu=10 packet/s, dt=1/(120*ref)
and the +/-6 spectral family (plus the draining deterministic control).
Observations are chosen at coarse dt and held fixed during refinement.
It does not re-anchor lambdaA or generate held-out cells.
"""
import math
from fractions import Fraction as F
from functools import lru_cache

import numpy as np

from smr.stationary import r2_keep
from smr.stationary_spectral import SpectralLaw

LAMBDA_B = F(8)


def lattice(rates,u,dt):
    a=[(r+u-10)*dt for r in rates];den=math.lcm(*(v.denominator for v in a))
    unit=F(math.gcd(*(int(v*den) for v in a)),den)
    return unit,tuple(int(v/unit) for v in a)


@lru_cache(None)
def law_for(lam,u,kappa,refinement):
    dt=F(1,120*refinement);unit,inc=lattice((lam-6,lam+6),u,dt)
    return unit,SpectralLaw(inc,*r2_keep(dt,kappa))


def queue_D(cell,which,ref):
    rates=tuple(cell['rates'+which]);u=cell['u'] if which=='A' else F(0);dt=F(1,120*ref)
    unit,inc=lattice(rates,u,dt);index=cell['y'+which]/unit
    if index.denominator!=1:raise ValueError('observation outside stationary sublattice')
    index=int(index);tau=120*ref;s,e=r2_keep(dt,cell['kappa'])
    if max(inc)<=0:
        if index!=0:raise ValueError('impossible stationary observation for draining deterministic queue')
        prior,bound=.5,0.
    else:
        _,law=law_for(sum(rates)/2,u,cell['kappa'],ref);prior,bound=law.posterior(index)
    size=index+tau*max(0,*inc)+1
    mass=np.zeros((size,2),dtype=np.longdouble);support=np.zeros((size,2),dtype=bool)
    mass[index]=1-np.longdouble(prior),np.longdouble(prior);support[index]=True
    p=np.longdouble(str(s.numerator))/np.longdouble(str(s.denominator))
    for _ in range(tau):
        after=np.zeros_like(mass);active=np.zeros_like(support)
        for m,a in enumerate(inc):
            if a<0:
                after[0]+=mass[:min(-a+1,size),m].sum(dtype=np.longdouble)*np.array([p if m==0 else 1-p,p if m==1 else 1-p])
                active[0]|=np.any(support[:min(-a+1,size),m])
                source=mass[-a+1:,m];reach=support[-a+1:,m];dest=slice(1,size+a)
            elif a>0:
                source=mass[:-a,m];reach=support[:-a,m];dest=slice(a,None)
                assert not np.any(support[-a:,m])
            else:source=mass[:,m];reach=support[:,m];dest=slice(None)
            for mode in (0,1):
                after[dest,mode]+=source*(p if m==mode else 1-p);active[dest,mode]|=reach
        mass,support=after,active
    assert not np.any(support & (mass==0)),'positive support underflow'
    total=mass.sum(dtype=np.longdouble);assert abs(total-1)<1e-12
    error=bound+float((tau*(8+2*max(map(abs,inc)))+4*size)*np.finfo(np.longdouble).eps)
    return unit,mass,support,error


def make_cell(s, lam):
    u = 2 * s['eta']
    unit_a, law_a = law_for(lam, u, s['kappa'], 1)
    unit_b, law_b = law_for(LAMBDA_B, F(0), s['kappa'], 1)
    y_a = law_a.quantile(s['alphaA']) * unit_a
    y_b = law_b.quantile(s['alphaB']) * unit_b
    target_h = y_b / (2 - u) if s['horizon'] == 'rh1' else F(s['horizon'])
    H = math.ceil(target_h * 120)
    return dict(id=f"{s['slice']}@{lam}", slice=s['slice'], lambdaA=lam, kappa=s['kappa'], eta=s['eta'],
                u=u, ratesA=(lam - 6, lam + 6), ratesB=(F(2), F(14)), alphaA=s['alphaA'],
                alphaB=s['alphaB'], yA=y_a, yB=y_b, horizon=s['horizon'], target_h=target_h,
                H_coarse=H, h=F(H, 120), age=F(1))
