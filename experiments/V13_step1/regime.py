"""Doan Van Tai — v1.3 step-1 [DISCOVERY] measures on engine Side tables (pure functions).

AI (Claude) viết theo ủy quyền (DL-062). No engine, grid or file access here, so every
function can be checked against brute-force enumeration on synthetic tables.
Definitions and thresholds follow experiments/V13_step1/predictions.md.
"""
from fractions import Fraction
import math

import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm, spearmanr

LD = np.longdouble
ONE_SIDED_LOW, ONE_SIDED_HIGH = 0.05, 0.20
EPS_PRIMARY, EPS_SENSITIVITY = 0.1, (0.05, 0.2)
SPEARMAN_MIN, SPEARMAN_GAIN = 0.6, 0.2
MAX_FALSE_REVERSAL = 2


def _ld(x):
    if isinstance(x, Fraction):
        return LD(x.numerator) / LD(x.denominator)
    return LD(x)


def col(values):
    return np.array([_ld(x) for x in values], dtype=LD)


def fluid_idle(side, which):
    """Mass of states whose conditional mean (fluid) path idles within h, certified by bounds."""
    p, dh = col(side.p), col(side.dh)
    bounds = side.bounds or {}
    err = LD(float(bounds.get('dh', 0.0)))
    zero = np.array(bounds.get('zero_dh', [False] * len(p)), dtype=bool) | (dh == 0)
    idle = (dh > err) if which == 'A' else (dh < -err)
    unresolved = ~(zero | idle)
    return dict(I=float(p[idle].sum()), zero_mass=float(p[zero].sum()),
                unresolved_mass=float(p[unresolved].sum()), all_zero=bool(zero.all()))


def true_idle(side, which):
    """Same as fluid_idle for the true component d (stochastic paths); diagnostic only."""
    p, d = col(side.p), col(side.d)
    err = LD(float((side.bounds or {}).get('d', 0.0)))
    idle = (d > err) if which == 'A' else (d < -err)
    return float(p[idle].sum())


def cut_value(kA, vA, pA, kB, vB, pB):
    """Σ_a p_a Σ_{b: kA+kB<0} p_b (vA+vB); strict inequality, so ties stay (D16)."""
    order = np.argsort(kB, kind='stable')
    keys, vals, probs = kB[order], vB[order], pB[order]
    cp = np.concatenate([[LD(0)], np.cumsum(probs)])
    cpv = np.concatenate([[LD(0)], np.cumsum(probs * vals)])
    idx = np.searchsorted(keys, -kA, side='left')
    return (pA * (vA * cp[idx] + cpv[idx])).sum()


def gm_s1(A, B):
    """G_M|S1 = E[Δ 1(Δ̂<0)] − E[Δ 1(Δ<0)] (state known, M0 vs M1)."""
    pA, dA, hA = col(A.p), col(A.d), col(A.dh)
    pB, dB, hB = col(B.p), col(B.d), col(B.dh)
    return float(cut_value(hA, dA, pA, hB, dB, pB) - cut_value(dA, dA, pA, dB, dB, pB))


def boundary_lens(A, B, eps):
    """Σ p e_M² / (2ε) over pairs with 0<|Δ|≤ε and e_M·Δ<0; also the window mass."""
    pA, dA, eA = col(A.p), col(A.d), col(A.dh) - col(A.d)
    pB, dB, eB = col(B.p), col(B.d), col(B.dh) - col(B.d)
    order = np.argsort(dB, kind='stable')
    dB, eB, pB = dB[order], eB[order], pB[order]
    eps = LD(eps)
    total = window = LD(0)
    for pa, da, ea in zip(pA, dA, eA):
        lo = np.searchsorted(dB, -eps - da, side='left')
        hi = np.searchsorted(dB, eps - da, side='right')
        if hi <= lo:
            continue
        delta = da + dB[lo:hi]
        e = ea + eB[lo:hi]
        w = pa * pB[lo:hi]
        inside = (delta != 0) & (np.abs(delta) <= eps)
        across = inside & (e * delta < 0)
        total += (w[across] * e[across] ** 2).sum()
        window += w[inside].sum()
    return float(total / (2 * eps)), float(window)


def folded_mean(mu, s):
    return mu * (2 * norm.cdf(mu / s) - 1) + 2 * s * norm.pdf(mu / s)


def mean_bias_lens(mu, stakes, bias):
    """Reviewer's constant-bias Gaussian lens (lens_check.py), ported unchanged in logic."""
    f = lambda s: folded_mean(mu, s) - stakes
    if f(1e-9) > 0:
        return float('nan')
    s = brentq(f, 1e-9, 1e6)
    lo, hi = sorted([0.0, -bias])
    al, be = (lo - mu) / s, (hi - mu) / s
    return abs(mu * (norm.cdf(be) - norm.cdf(al)) + s * (norm.pdf(al) - norm.pdf(be)))


def side_label(IA, IB):
    if IA == 0 and IB == 0:
        return 'both_zero'
    if IA <= ONE_SIDED_LOW and IB >= ONE_SIDED_HIGH:
        return 'one_sided_B'
    if IB <= ONE_SIDED_LOW and IA >= ONE_SIDED_HIGH:
        return 'one_sided_A'
    return 'two_sided'


def predicted_reversal(target, label):
    return (target == '0.3' and label == 'one_sided_B') or (target == '0.7' and label == 'one_sided_A')


def observed_regime(E_delta, E_delta_hat):
    if E_delta_hat == 0:
        return 'blind'
    return 'same' if (E_delta > 0) == (E_delta_hat > 0) else 'reverse'


def rho(x, y):
    r = spearmanr(x, y).correlation
    return None if r is None or math.isnan(r) else float(r)


def score(cells):
    """cells: list of per-cell dicts produced by run.py. Returns the three verdicts."""
    blind = [c for c in cells if c['observed_regime'] == 'blind']
    nonblind = [c for c in cells if c['observed_regime'] != 'blind']
    a_blind = all(c['A_all_zero'] and c['B_all_zero'] for c in blind)
    a_nonblind = all(c['I_A'] + c['I_B'] > 0 for c in nonblind)
    reversal = sorted(c['cell'] for c in cells if c['observed_regime'] == 'reverse')
    predicted = sorted(c['cell'] for c in cells if c['predicted_reversal'])
    hits = [x for x in reversal if x in predicted]
    false = [x for x in predicted if x not in reversal]
    b_pass = len(hits) == len(reversal) and len(false) <= MAX_FALSE_REVERSAL
    same = [c for c in cells if c['observed_regime'] == 'same']
    target = [c['G_M_S1'] / c['stakes'] for c in same]
    r_b = rho(target, [c['lens_boundary'] / c['stakes'] for c in same])
    r_m = rho(target, [c['lens_mean'] / c['stakes'] for c in same])
    sens = {str(e): rho(target, [c[f'lens_boundary_{e}'] / c['stakes'] for c in same]) for e in EPS_SENSITIVITY}
    c_pass = r_b is not None and r_m is not None and r_b >= SPEARMAN_MIN and r_b >= r_m + SPEARMAN_GAIN
    return dict(
        P_a=dict(verdict='PASS' if a_blind and a_nonblind else 'FAIL', blind_cells=[c['cell'] for c in blind],
                 blind_both_sides_certified_zero=a_blind, nonblind_all_have_fluid_idle=a_nonblind),
        P_b=dict(verdict='PASS' if b_pass else 'FAIL', observed_reversal=reversal, predicted_reversal=predicted,
                 hits=hits, false_positives=false, max_false_allowed=MAX_FALSE_REVERSAL),
        P_c=dict(verdict='PASS' if c_pass else 'FAIL', n_same_sign=len(same), spearman_boundary=r_b,
                 spearman_mean_lens=r_m, required_min=SPEARMAN_MIN, required_gain=SPEARMAN_GAIN,
                 sensitivity_spearman_boundary=sens),
        label='DISCOVERY')
