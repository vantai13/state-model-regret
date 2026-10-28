"""Doan Van Tai — exact interval MAE comparison, independent of any model fit.

Only paired loss-difference endpoints are needed: |p0-y|-|p1-y| is monotone
in y. Individual absolute-loss minima additionally need the prediction kink.
No input/output, engine, held-out loading or numerical-budget assumptions here.
"""
from fractions import Fraction as F


def q(value):
    return value if isinstance(value, F) else F(str(value))


def distance(prediction, interval):
    p = q(prediction)
    lo, hi = map(q, interval)
    if lo > hi:
        raise ValueError('reversed interval')
    return (F(0) if lo <= p <= hi else min(abs(p-lo), abs(p-hi)), max(abs(p-lo), abs(p-hi)))


def paired_difference(p0, p1, interval):
    p0, p1 = q(p0), q(p1)
    lo, hi = map(q, interval)
    if lo > hi:
        raise ValueError('reversed interval')
    endpoints = [abs(p0-y)-abs(p1-y) for y in (lo, hi)]
    return min(endpoints), max(endpoints)


def compare(y_intervals, predictions0, predictions1, *, margin, max_missing=0):
    """Equal-weight scalar entries; flatten a registered multi-contrast metric first.

    None entries mark missing quantities, not silently omitted cells. The caller
    must count/reject unavailable cells before flattening the frozen metric.
    """
    m = q(margin)
    if m <= 0 or not (len(y_intervals) == len(predictions0) == len(predictions1)):
        raise ValueError('positive margin and equal-length arrays required')
    p0, p1 = list(map(q, predictions0)), list(map(q, predictions1))
    n = len(p0)
    if n == 0:
        return dict(verdict='INCONCLUSIVE', reason='empty_domain', n=0)
    D = sum(abs(a-b) for a,b in zip(p0,p1))/n
    if D < m:
        return dict(verdict='DO_NOT_OPEN', reason='D_below_margin', D=D, n=n)
    missing = sum(x is None for x in y_intervals)
    if missing > max_missing or missing == n:
        return dict(verdict='INCONCLUSIVE', reason='missing_budget', D=D, n=n, missing=missing)
    triples = [(iv,a,b) for iv,a,b in zip(y_intervals,p0,p1) if iv is not None]
    active_D = sum(abs(a-b) for _,a,b in triples)/len(triples)
    if active_D < m:
        return dict(verdict='INCONCLUSIVE', reason='active_D_below_margin', D=D,
                    active_D=active_D, n=n, missing=missing)
    bands = [paired_difference(a,b,iv) for iv,a,b in triples]
    lo, hi = (sum(b[k] for b in bands)/len(bands) for k in (0,1))
    if lo >= m:
        state = 'SUPPORT'
    elif hi <= 0:
        state = 'FALSIFY'
    elif lo > 0 and hi < m:
        state = 'WEAKEN'
    else:
        state = 'INCONCLUSIVE'
    mae = []
    for model in (1,2):
        errors = [distance(t[model],t[0]) for t in triples]
        mae.append(tuple(sum(e[k] for e in errors)/len(errors) for k in (0,1)))
    return dict(verdict=state, reason='registered_interval_rule', D=D, active_D=active_D,
                d_interval=(lo,hi), MAE0=mae[0], MAE1=mae[1], n=n, eligible=len(triples), missing=missing)
