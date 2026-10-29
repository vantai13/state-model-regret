"""Doan Van Tai — shared-anchor feasibility, independent of research outcomes.

Each constraint supplies an allowed tau interval and its predeclared relaxed
interval. Conversion from empirical ranges must be established separately; null
inputs must never be replaced by an illustrative anchor.
"""
import itertools
import math


def intersects(intervals):
    if not intervals: return False
    for lo, hi in intervals:
        if not math.isfinite(lo) or not math.isfinite(hi) or lo < 0 or hi < lo:
            raise ValueError('invalid tau interval')
    return max(i[0] for i in intervals) <= min(i[1] for i in intervals)


def classify(tau_range, constraints, *, k=1):
    missing = [c['name'] for c in constraints if c.get('allowed_tau_s') is None]
    if tau_range is None: missing.insert(0, 'tau_eff_s')
    if missing: return {'label': 'UNSOURCED', 'missing': missing, 'relaxed': []}
    if not constraints: raise ValueError('nonempty empirical constraints required')
    intervals = [c['allowed_tau_s'] for c in constraints]
    if intersects([tau_range, *intervals]):
        return {'label': 'IN', 'missing': [], 'relaxed': []}
    for count in range(1, min(k, len(constraints)) + 1):
        for chosen in itertools.combinations(range(len(constraints)), count):
            candidate = [tau_range]
            for i, c in enumerate(constraints):
                candidate.append(c.get('relaxed_tau_s', c['allowed_tau_s']) if i in chosen else c['allowed_tau_s'])
            if intersects(candidate):
                return {'label': 'EDGE', 'missing': [], 'relaxed': [constraints[i]['name'] for i in chosen]}
    return {'label': 'OUT', 'missing': [], 'relaxed': []}
