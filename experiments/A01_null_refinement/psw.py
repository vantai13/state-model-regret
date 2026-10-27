"""Doan Van Tai — Part 0: only public sign intervals leave this API.

Rebuilds D through the current adapter. Reproduces the design screen's exact
float64-first arithmetic/error convention. No M0, costs, or aggregate calls.
The native idle kernel is shared, so this is not an independent kernel proof.
"""
import math
from fractions import Fraction as F

import numpy as np

from experiments.A00_engine.cells_adapter import load_cell, queue_law
from experiments.A00_engine.guard import guard
from smr.gap_screen import backward, probability_interval
from smr.stationary import r2_keep


def _component(c, w, ref, part, extended):
    native, mass, support, errorD = part
    dt, H = F(1, 120 * ref), c['H_coarse'] * ref
    values = [(r + u - 10) * dt for r in c['rates' + w] for u in (F(0), c['u'])]
    values.append(c['y' + w])
    den = math.lcm(*(v.denominator for v in values))
    unit = F(math.gcd(*(int(v * den) for v in values)), den)
    factor = native / unit
    if factor.denominator != 1:
        raise ValueError('unaligned lattice')
    indices = np.arange(len(mass), dtype=np.int64) * int(factor)
    stay = tuple(int((r + (c['u'] if w == 'A' else 0) - 10) * dt / unit) for r in c['rates' + w])
    switch = tuple(int((r + (c['u'] if w == 'B' else 0) - 10) * dt / unit) for r in c['rates' + w])
    minimal = switch if w == 'A' else stay
    zero = np.column_stack([(indices + a >= 0) & (indices + a + (H - 1) * min(0, *minimal) >= 0)
                            for a in minimal])
    if np.all(zero[support]):
        return np.zeros(mass.shape, dtype=np.longdouble), mass, 0., float(errorD), zero.ravel()
    keep, ke = r2_keep(dt, c['kappa'])
    a, ea, _ = backward(indices, stay, H, keep, ke, extended)
    b, eb, _ = backward(indices, switch, H, keep, ke, extended)
    scale = np.longdouble(str((unit * dt).numerator)) / np.longdouble(str((unit * dt).denominator))
    delta = (b.astype(np.longdouble) - a.astype(np.longdouble)) * scale
    error = (ea + eb) * float(scale) + float(16 * np.finfo(np.longdouble).eps * scale * (np.max(a) + np.max(b)))
    if not np.all(delta[zero] == 0):
        raise ArithmeticError('conservation certificate failed')
    return delta, mass, error, float(errorD), zero.ravel()


def reproduce_psw(cid, ref, *, allow_grid=False):
    guard(cid, purpose='A01', allow_grid=allow_grid)
    c = load_cell(cid)
    parts = {w: queue_law(c, w, ref) for w in 'AB'}
    for extended in (False, True):
        a, pa, ea, da, za = _component(c, 'A', ref, parts['A'], extended)
        b, pb, eb, db, zb = _component(c, 'B', ref, parts['B'], extended)
        r = probability_interval(a, b, pa, pb, ea, eb, da + db, za, zb)
        if r['unresolved_mass'] <= .01:
            return {'p_low': r['p_low'], 'p_high': r['p_high']}
    raise ArithmeticError('Part 0 unresolved mass exceeds .01')
