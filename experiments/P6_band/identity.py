"""Doan Van Tai — M0 lattice mean identity with an explicit error budget.

The predictor's own builders run at every queue index in their nonzero support.
This removes K-bin sampling error; stationary/profile/rounding errors remain
enclosed. No finite-horizon M1 cost is constructed. See DL-131.
"""
from contextlib import contextmanager
from fractions import Fraction as F
import math

import numpy as np

from experiments.R3R_08_population_numerics import quadrature
from experiments.R3R_08_population_numerics import piecewise as P
from experiments.P6_band import predictor

NEGLIGIBLE = P.LD('1e-20')


def gamma(n):
    """Conservative floating-point accumulation bound, using epsilon >= unit roundoff."""
    value = P.LD(n)*P.EPS
    if value >= 1:
        raise ArithmeticError('roundoff budget exhausted')
    return value/(1-value)


def outward(value):
    return math.nextafter(float(value), math.inf)


@contextmanager
def lattice_quadrature(record):
    original = quadrature.build

    def build(law, K, cap):
        q = np.arange(cap+1, dtype=np.int64)
        point, perr = law.point(q)
        keep = point.sum(axis=1, dtype=P.LD) > NEGLIGIBLE
        c, ce = law.cdf([cap])
        dropped = point[~keep].sum(axis=0, dtype=P.LD)
        mass = np.vstack([point[keep], P.LD('.5')-c[0]+dropped])
        # Includes point errors even at dropped nodes, the tail, and mass sums.
        rounding = gamma(4*len(q)+16)*(1+abs(mass).sum(dtype=P.LD))
        l1 = np.nextafter((perr.sum(dtype=P.LD)+ce.sum(dtype=P.LD)+rounding)
                          *(1+gamma(8)), P.LD('inf'))
        if np.any(mass < 0) or abs(mass.sum(dtype=P.LD)-1) > l1:
            raise ArithmeticError('lattice complete-mass guard failed')
        record.append(dict(cap=int(cap), nodes=int(keep.sum()),
                           dropped=dropped.sum(dtype=P.LD)))
        return dict(indices=np.r_[q[keep], -1].astype(np.int64), mass=mass,
                    l1_error=l1, cap=cap)

    quadrature.build = build
    try:
        yield
    finally:
        quadrature.build = original


def exact_identity(a, b, kappa, u, h, cache, *, ref=4):
    """Enclose E[g_old]-E[g_new]; 'exact' means lattice sum, not exact arithmetic."""
    a, b, kappa, u, h = map(F, (a, b, kappa, u, h))
    if min(a,b) < 6 or max(a+u,b+u) >= 10 or u <= 0 or kappa <= 0 or h <= 0:
        raise ValueError('outside stable plant')
    laws = {load: cache.get(load, kappa, ref)[:2] for load in (a+u,b)}
    dt = F(1,120*ref)
    # Reflection is 1-Lipschitz: changing rate by u changes slot-j queue by
    # at most j*u*dt. Summing gives u*h*(h+dt)/2, also after conditional aging.
    magnitude = P.number(u*h*(h+dt)/2)*(1+gamma(8))
    records, parts, report = [], [], []
    with lattice_quadrature(records):
        for lam,pre,post,load in ((a,u,F(0),a+u),(b,F(0),u,b)):
            fresh = predictor.mean_side(lam,pre,post,kappa,h,ref,2,*laws[load])
            stale = predictor.stale_mean_side(lam,pre,post,kappa,h,ref,2,*laws[load])
            values = {}
            for name,side in (('fresh',fresh),('stale',stale)):
                product = side['w']*side['h']
                mean = product.sum(dtype=P.LD)
                rounding = gamma(2*len(product)+16)*abs(product).sum(dtype=P.LD)
                profile_error = (side['w']*side['eh']).sum(dtype=P.LD)
                profile_error *= 1+gamma(2*len(product)+16)
                mass_error = side['w_error']*magnitude
                dropped_error = records[-2 if name=='fresh' else -1]['dropped']*magnitude
                error = profile_error+mass_error+dropped_error+rounding
                values[name] = mean
                parts.append((mean,error))
                values[name+'_profile_error'] = outward(profile_error)
                values[name+'_mass_error'] = outward(mass_error)
                values[name+'_dropped_error'] = outward(dropped_error)
                values[name+'_rounding_error'] = outward(rounding)
            report.append({k:float(v) for k,v in values.items()})
    new = parts[0][0]+parts[2][0]
    old = parts[1][0]+parts[3][0]
    drift = old-new
    rounding = gamma(8)*sum(abs(v) for v,e in parts)
    bound = np.nextafter((sum(e for v,e in parts)+rounding)*(1+gamma(64)),P.LD('inf'))
    return dict(mean_new=float(new),mean_old=float(old),drift=float(drift),bound=outward(bound),
                passed=bool(abs(drift)<=bound),dropped_mass=outward(sum(r['dropped'] for r in records)),
                magnitude_bound=outward(magnitude),sides=report,
                grids=[{k:(outward(v) if k=='dropped' else v) for k,v in r.items()} for r in records])
