"""Doan Van Tai — explicit level0–2 features, no queue/D/cost/gap imports.

Kappa is a memory TIME: covariance decays exp(-2t/kappa). Fluid quantities
are proxies from the stale observation, not posterior/current-state moments.
"""
from fractions import Fraction as F
import json
from pathlib import Path
import math

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
GRID = ROOT/'notes/design/grid_v1_2.json'
FIELDS = frozenset(('id','slice','kappa','alphaA','alphaB','eta','h','lambdaA','yA','yB','target'))
HEADS = ('mu','sigma','bias','tau')
CANDIDATES = {
    'H0': {
        'coordinates_0': ('load_A','log_kappa','quantile_difference','eta'),
        'coordinates_1': ('load_A','log_observation_sum','alphaB','log_h'),
    },
    'H1': {
        'dynamics_0': ('boundary_shift','variance_h_scaled','boundary_joint','B_drain_proxy'),
        'dynamics_1': ('boundary_balance','variance_age_h_scaled','boundary_difference','variance_boundary'),
    },
}


def sanitize(record):
    """Only these exact design fields survive; p_sw/cost/outcome columns are ignored."""
    clean={k:record[k] for k in FIELDS-{'target'} if k in record}
    anchors=record['anchors']
    targets={F(str(a['target'])) for a in anchors}
    if len(targets)!=1:
        raise ValueError('a single declared target per cell required')
    clean['target']=str(next(iter(targets)))
    if set(clean)!=FIELDS or not str(clean['id']).startswith(('M','R')):
        raise ValueError('complete main/held-out design metadata required')
    return clean


def load_design(split='main', *, allow_heldout=False):
    if split not in ('main','heldout') or (split=='heldout' and not allow_heldout):
        raise PermissionError('held-out design features require explicit post-theta authorization')
    # The file already contains public design metadata; select only the declared section.
    return [sanitize(r) for r in json.loads(GRID.read_text())[split]]


def telegraph_variance(h,kappa,amplitude=6.):
    if h<0 or kappa<=0 or amplitude<0:
        raise ValueError('nonnegative window/amplitude and positive memory time required')
    x=h/kappa
    term=(x*x*(1-2*x/3+x*x/3-2*x**3/15+2*x**4/45) if x<1e-4 else
          x+.5*math.expm1(-2*x))
    return amplitude*amplitude*kappa*kappa*term


def values(record):
    if set(record)!=FIELDS:
        raise ValueError('feature input must be the exact sanitized design whitelist')
    r={k:float(F(str(record[k]))) for k in FIELDS-{'id','slice'}}
    k,h,eta=r['kappa'],r['h'],r['eta']
    if k<=0 or h<=0 or not 0<eta<1 or not 0<=r['alphaA']<=1 or not 0<=r['alphaB']<=1:
        raise ValueError('invalid design domain')
    if F(record['target']) not in (F(3,10),F(7,10)):
        raise ValueError('frozen binary target set is .3/.7')
    u=2*eta
    qa=max(0.,r['yA']+(r['lambdaA']+u-10)*1.)
    qb=max(0.,r['yB']+(8-10)*1.)
    def exposure(q,rate,managed):
        drain=10-rate-managed
        return max(0.,drain*h-q)/(1+q+abs(drain)*h)
    ast=exposure(qa,r['lambdaA'],u);asw=exposure(qa,r['lambdaA'],0)
    bst=exposure(qb,8,0);bsw=exposure(qb,8,u)
    vh=2*telegraph_variance(h,k)
    vtotal=2*telegraph_variance(1+h,k)
    # Q02's long-window fluid coefficient is a proxy, not actual finite-h cost.
    proxy=qb*qb/(2*(10-8))*eta/(1-eta)
    result=dict(
        target_signed=1. if F(record['target'])==F(3,10) else -1.,
        load_A=r['lambdaA']/10,log_kappa=math.log(k),
        quantile_difference=r['alphaA']-r['alphaB'],eta=eta,
        log_observation_sum=math.log1p(r['yA']+r['yB']),alphaB=r['alphaB'],log_h=math.log(h),
        boundary_shift=(asw-ast)-(bst-bsw),
        variance_h_scaled=math.log1p(vh/(1+qa*qa+qb*qb)),
        boundary_joint=ast+bsw,
        B_drain_proxy=math.log1p(proxy/(1+h*(1+qa+qb))),
        boundary_balance=ast-bsw,
        variance_age_h_scaled=math.log1p(vtotal/(1+r['yA']**2+r['yB']**2)),
        boundary_difference=asw-bst,
        variance_boundary=math.log1p(vh/(1+h*h))*(ast+asw+bst+bsw),
    )
    if not all(math.isfinite(v) for v in result.values()):
        raise ArithmeticError('finite features required')
    return result


def tensor(records, model, candidate):
    """n x 4 x 3: intercept, shared target, one head-specific scalar feature."""
    names=CANDIDATES[model][candidate]
    rows=[values(r) for r in records]
    return np.asarray([[[1.,v['target_signed'],v[name]] for name in names] for v in rows])


def group(record):
    """Classify using novel design axes, never lambdaA, p_sw or outcomes."""
    k,b,eta,h=map(F,(record['kappa'],record['alphaB'],record['eta'],record['h']))
    if h>8:
        return 'extrapolation'
    novelty=sum((k not in (F(3,10),F(1),F(3)),b not in (F(1,2),F(9,10)),
                 eta not in (F(1,2),F(3,4)),h not in (F(2),F(8))))
    return 'interpolation' if novelty==1 else 'weak_interpolation'
