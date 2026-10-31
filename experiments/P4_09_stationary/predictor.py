"""Doan Van Tai — parameter-only stationary/M0 predictor, AI-assisted.

No finite-horizon M1 cost, losses, contrasts or Cref enter this module.
Stationary laws are the existing slotted true-law input of the controlled study.
"""
from fractions import Fraction as F
import json
import math
from pathlib import Path

import numpy as np

from experiments.R3R_08_population_numerics import law_cache, profiles, quadrature
from experiments.R3R_08_population_numerics import piecewise as P
from smr.stationary import r2_keep


class StationaryCache:
    def __init__(self, root, cache):
        self.root,self.cache = Path(root),Path(cache)
        self.index = {}
        self.used = {}
        fingerprint = law_cache.fingerprint()
        for path in sorted((self.root/'results/lessons').glob('**/native_cache/stationary/*.json')):
            data = json.loads(path.read_text())
            if data.get('source_fingerprint') != fingerprint:
                continue
            lam,u,k,ref = data['parameters']
            self.index.setdefault((F(lam)+F(u),F(k),int(ref)),(path,lam,u))

    def get(self, mean_load, kappa, ref):
        key = (F(mean_load),F(kappa),ref)
        if key not in self.used:
            old = self.index.get(key)
            if old:
                path,lam,u = old
                unit,law,lawkey = law_cache.get(F(lam),F(u),F(kappa),ref,path.parent)
            else:
                unit,law,lawkey = law_cache.get(F(mean_load),F(0),F(kappa),ref,self.cache/'stationary')
                path = self.cache/'stationary'/(lawkey+'.json')
            self.used[key] = (unit,law,str(path),lawkey)
        return self.used[key]


def mean_side(lam, pre, post, kappa, h, ref, K, unit, law):
    """Only mean_idle kernels; profiles.get/P.idle must never be called here."""
    dt = F(1,120*ref)
    H = h/dt
    if H.denominator != 1:
        raise ValueError('horizon not on fixed slotted grid')
    H = int(H)
    amounts = [(lam+s*6+load-10)*dt for s in (-1,1) for load in (pre,post)]
    quantum = profiles.quantum([*amounts,unit])
    factor = unit/quantum
    if factor.denominator != 1:
        raise ValueError('unaligned mean action lattice')
    inc = [tuple(int((lam+s*6+load-10)*dt/quantum) for s in (-1,1)) for load in (pre,post)]
    keep,ke = r2_keep(dt,kappa)
    mst,msw = [P.mean_idle(H,i,keep,ke) for i in inc]
    dh = P.combine(msw,mst,subtract=True)
    data = dict(profiles={'dh':dh},factor=int(factor),scale=P.number(quantum*dt),
                identical_actions=pre==post,
                saturation_OFF_max_index=max(-1,min(-inc[0][0],-inc[1][0])) if lam+max(pre,post)<10 else -1,
                saturation_cost=str((pre-post)*dt*dt*H*(H+1)/2))
    cap = max((int(x[-1])+int(factor)-1)//int(factor) for x,y in dh['modes'])
    grid = quadrature.build(law,K,cap)
    fields = {name:[] for name in ('h','eh','zero','sat')}
    for mode in (0,1):
        values = profiles.values(data,'dh',grid['indices'],mode)
        for name,value in zip(fields,values):
            fields[name].append(value)
    result = {name:np.column_stack(value).ravel() for name,value in fields.items()}
    result['w'] = grid['mass'].ravel()
    result['w_error'] = grid['l1_error']
    return result


def action_mismatch(A,B,s):
    """Action indicator, never mathematical sign comparison; retain exact ties."""
    gap = A['h'][:,None]+B['h'][None,:]
    error = A['eh'][:,None]+B['eh'][None,:]
    certified = (A['zero'][:,None]&B['zero'][None,:])|(A['sat'][:,None]&B['sat'][None,:])
    gap = np.where(certified,P.LD(0),gap)
    error = np.where(certified,P.LD(0),error)
    weights = A['w'][:,None]*B['w'][None,:]
    mismatch = ((gap<0)!=(s<0))
    ambiguous = (gap-error<0)&(gap+error>=0)
    return dict(P_mis=float((weights*mismatch).sum(dtype=P.LD)),
                M0_tie_mass=float((weights*(gap==0)).sum(dtype=P.LD)),
                M0_ambiguous_mass=float((weights*ambiguous).sum(dtype=P.LD)))


def predict(parameters, cache, *, ref=4, K=320):
    a,b,k,e,h,c = map(F,parameters)
    u = 2*e
    if min(a,b)<6 or u<=0 or max(a+u,b+u)>=10 or k<=0 or h<=0 or c!=0:
        raise ValueError('predictor requires stable primary two-path regime')
    requested = (a+u,b,a,b+u)
    components = [cache.get(load,k,ref) for load in requested]
    moments = [law.mean*P.number(unit) for unit,law,path,key in components]
    errors = [law.mean_error*P.number(unit) for unit,law,path,key in components]
    r_stay,r_switch = moments[0]+moments[1],moments[2]+moments[3]
    s,es = r_switch-r_stay,sum(errors)
    symmetric = a==b
    if symmetric:
        s = P.LD(0)
    elif abs(s)<=es:
        return dict(status='NOT_READY_STATIONARY_SIGN',s=float(s),s_error=float(es))
    A = mean_side(a,u,F(0),k,h,ref,K,components[0][0],components[0][1])
    B = mean_side(b,F(0),u,k,h,ref,K,components[1][0],components[1][1])
    pm = action_mismatch(A,B,s)
    minimum = min(r_stay,r_switch)
    if minimum<=0:
        raise ValueError('stationary normalizer must be positive')
    return dict(status='PREDICTED',GM_pred_pctC=float(100*abs(s)*P.LD(pm['P_mis'])/minimum),
                r_Stay=float(r_stay),r_Switch=float(r_switch),s=float(s),s_error=float(es),
                stationary_symmetry_zero=symmetric,**pm,
                K_predictor=K,ref_predictor=ref,
                stationary_sources=[dict(effective_load=str(load),path=path,key=key) for load,(unit,law,path,key) in zip(requested,components)],
                uncertainty='Mean-only quadrature estimate, not a certified predictor interval')


def features(key):
    a,b,u,k,h,c = map(F,key.split('|'))
    return np.array([float(a/10),float(b/10),float(u/10),math.log(float(k)),math.log(float(h))])


def nearest(key, training, *, leave_out=False):
    target = features(key)
    candidates = [r for r in training if not leave_out or r['key']!=key]
    if not candidates:
        raise ValueError('no 1-NN reference after physical-key exclusion')
    best = min(candidates,key=lambda r:(float(np.sum((features(r['key'])-target)**2)),r['key']))
    return best
