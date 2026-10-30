"""Doan Van Tai — v1.3 POPULATION feasibility pilot [EXPLORATION, branch explore/v13-population].

AI (Claude) viết theo ủy quyền ("tự thiết kế và chạy... xem vùng nào khả thi"). Not a contract,
not a prereg, not confirmation evidence: every regime computed here becomes seen discovery data.
Only NEW regimes (ids 'X...') are used; no v1.2 grid cell, no held-out cell. The engine guard treats
unknown ids as toy scope, so no access level is borrowed.

Population estimand (proposal of the v1.3 draft): for a regime c (lambdaA, lambdaB, kappa, eta, h;
age 1 s, capacity 10, +/-6 ON/OFF background), the stale observation Y=(yA,yB) is drawn from the
stationary pre-decision law (A carries u under the Stay status quo), independently per queue.
For every y the four pipelines decide as in v1.2 (S0 from E_D[.|y], S1 per state; M0 mean rollout,
M1 true law; tie -> Stay) and L_sm(y) is the expected true cost. Population values average over p(y):
    Lbar_sm = sum_y p(y) L_sm(y);  Gbar = contrasts of Lbar (same D19 algebra).
Normalizations: Cbar_ref = Lbar_11 and stakes Sbar = sum_y p(y) E|Delta|(y).
Explanatory numbers: P(flip)=P_y(a00 != a01); E[|E Delta| | flip]; P(wrong ranking)=P_{y,x}(sign
Delta_hat != sign Delta) with ties -> Stay; also the per-y margin/distortion data for the secondary
hypothesis.

p(y) quadrature: the atom q=0 is kept exactly; the remaining mass (truncated at 1-1e-4) is split into
K equal-mass bins represented by their conditional median index. K-convergence is checked.

Feasibility rubric (written before the scan; thresholds of v1.2 reused as reading aids only):
  TE   (bad):  Gbar_M/Cbar < 0.5% and Gbar_M/Sbar < 5% in every regime, and |Gammabar| likewise small:
               population only dilutes; nothing beyond "state value" to characterise.
  ON   (ok):   Gbar_S >= 1% Cbar in a broad set of regimes but Gbar_M >= 1% Cbar (or >= 10% Sbar) in
               few/none: an equivalence story ("simple model suffices") only.
  TOT  (good): both Gbar_S and Gbar_M >= 1% Cbar (or >= 10% Sbar) in identifiable regions, and
               Gammabar non-negligible with a sign that varies across regimes.
  RAT TOT (very good): GOOD plus a simple a-priori rule (design coordinates or the secondary
               margin x distortion hypothesis) ranks regimes by Gbar_M / P(reversal) well
               (Spearman >= 0.7) and the picture is stable under K and dt refinement.
"""
from fractions import Fraction as F
from functools import lru_cache
import math
import time

import numpy as np

from smr.cells import lattice
from smr.stationary import r2_keep
from smr.stationary_spectral import SpectralLaw
from experiments.A00_engine.physical import side_from_law
from experiments.V13_step1.regime import cut_value

LD = np.longdouble
COVERAGE = 1 - 1e-4


def make_regime(lamA, lamB, kappa, eta, h, rid, age=1, amp=6):
    """age = staleness of the observation (s); amp = ON/OFF background amplitude (+/-amp packet/s).
    Defaults are the inherited plant (age 1 s, +/-6); other values are exploration-only extensions."""
    lamA, lamB, kappa, eta, h, age, amp = map(F, (lamA, lamB, kappa, eta, h, age, amp))
    u = 2 * eta
    if lamA - amp < 0 or lamB - amp < 0 or lamA + u >= 10 or lamB + u >= 10:
        raise ValueError('regime outside the stable nonnegative two-mode family')
    if lamA + amp + u <= 10 or lamB + amp <= 10:
        raise ValueError('ON mode must overload each queue (otherwise the stationary law is a point mass)')
    if age <= 0 or (age * 120).denominator != 1:
        raise ValueError('age must be a positive multiple of the coarse dt 1/120 s')
    return dict(id=rid, kappa=kappa, eta=eta, u=u, age=age, amp=amp, ratesA=(lamA - amp, lamA + amp),
                ratesB=(lamB - amp, lamB + amp), h=h, H_coarse=int(h * 120), lambdaA=lamA, lambdaB=lamB)


@lru_cache(None)
def law(rates, u, kappa, ref):
    """smr.cells.law_for with the two mode rates given explicitly (law_for fixes them at lam +/- 6)."""
    dt = F(1, 120 * ref)
    unit, inc = lattice(rates, u, dt)
    return unit, SpectralLaw(inc, *r2_keep(dt, kappa))


def queue_D(cell, which, ref):
    """smr.cells.queue_D with tau = age/dt instead of the fixed 1 s; same arithmetic otherwise.
    At age 1 and +/-6 it must agree bitwise with smr.cells.queue_D (tests/test_explore_v13.py)."""
    rates = tuple(cell['rates' + which]); u = cell['u'] if which == 'A' else F(0); dt = F(1, 120 * ref)
    unit, inc = lattice(rates, u, dt); index = cell['y' + which] / unit
    if index.denominator != 1: raise ValueError('observation outside stationary sublattice')
    tau = cell['age'] / dt
    if tau.denominator != 1: raise ValueError('age is not a multiple of dt')
    index = int(index); tau = int(tau); s, e = r2_keep(dt, cell['kappa'])
    _, lw = law(rates, u, cell['kappa'], ref); prior, bound = lw.posterior(index)
    size = index + tau * max(0, *inc) + 1
    mass = np.zeros((size, 2), dtype=np.longdouble); support = np.zeros((size, 2), dtype=bool)
    mass[index] = 1 - np.longdouble(prior), np.longdouble(prior); support[index] = True
    p = np.longdouble(str(s.numerator)) / np.longdouble(str(s.denominator))
    for _ in range(tau):
        after = np.zeros_like(mass); active = np.zeros_like(support)
        for m, a in enumerate(inc):
            if a < 0:
                after[0] += mass[:min(-a + 1, size), m].sum(dtype=np.longdouble) * np.array([p if m == 0 else 1 - p, p if m == 1 else 1 - p])
                active[0] |= np.any(support[:min(-a + 1, size), m])
                source = mass[-a + 1:, m]; reach = support[-a + 1:, m]; dest = slice(1, size + a)
            elif a > 0:
                source = mass[:-a, m]; reach = support[:-a, m]; dest = slice(a, None)
                assert not np.any(support[-a:, m])
            else: source = mass[:, m]; reach = support[:, m]; dest = slice(None)
            for mode in (0, 1):
                after[dest, mode] += source * (p if m == mode else 1 - p); active[dest, mode] |= reach
        mass, support = after, active
    assert not np.any(support & (mass == 0)), 'positive support underflow'
    total = mass.sum(dtype=np.longdouble); assert abs(total - 1) < 1e-12
    error = bound + float((tau * (8 + 2 * max(map(abs, inc))) + 4 * size) * np.finfo(np.longdouble).eps)
    return unit, mass, support, error


def observation_bins(cell, which, ref, K):
    rates = cell['rates' + which]
    u = cell['u'] if which == 'A' else F(0)
    unit, lw = law(tuple(rates), u, cell['kappa'], ref)
    N = lw.plan['cutoff']
    pmf = lw.mass(N).sum(axis=1)
    cdf = np.cumsum(pmf)
    last = int(np.searchsorted(cdf, COVERAGE)) + 1
    pmf = pmf[:last]
    truncated = float(1 - pmf.sum())
    reps, weights = [0], [pmf[0]]
    rest = pmf[1:]
    if rest.sum() > 0:
        c = np.cumsum(rest) / rest.sum()
        edges = np.searchsorted(c, np.linspace(0, 1, K + 1)[1:-1])
        bounds = [0, *edges.tolist(), len(rest)]
        for lo, hi in zip(bounds[:-1], bounds[1:]):
            if hi <= lo:
                continue
            seg = rest[lo:hi]
            mid = lo + int(np.searchsorted(np.cumsum(seg) / seg.sum(), .5))
            reps.append(1 + mid)
            weights.append(seg.sum())
    w = np.array(weights, dtype=float)
    return unit, reps, w / w.sum(), truncated


def side_rows(cell, which, ref, reps, unit):
    """One DP over the union of posterior supports; per-y weights over the same rows."""
    posts = []
    for idx in reps:
        _, mass, support, _ = queue_D(dict(cell, **{'y' + which: idx * unit}), which, ref)
        posts.append(mass)
    size = max(m.shape[0] for m in posts)
    union = np.zeros((size, 2), dtype=LD)
    for m in posts:
        union[:m.shape[0]] += m
    union /= union.sum()
    dt = F(1, 120 * ref)
    keep, ke = r2_keep(dt, cell['kappa'])
    table, _ = side_from_law(unit, union, rates=cell['rates' + which],
                             u_stay=cell['u'] if which == 'A' else F(0),
                             u_switch=cell['u'] if which == 'B' else F(0), capacity=F(10),
                             H=cell['H_coarse'] * ref, dt=dt, keep=keep, keep_error=ke, extended=True)
    rows_q, rows_m = np.nonzero(union)
    weights = []
    for m in posts:
        full = np.zeros((size, 2), dtype=LD)
        full[:m.shape[0]] = m
        weights.append(full[rows_q, rows_m])
    arr = lambda v: np.array(v, dtype=LD)
    return dict(d=arr(table.d), dh=arr(table.dh), j=arr(table.jst), w=weights)


def pair_values(A, B, ia, ib, c=0):
    """c = switching cost (packet*s) known to every pipeline: Switch iff gap + c < 0 (tie Stay)."""
    wa, wb = A['w'][ia], B['w'][ib]
    sa, sb = wa > 0, wb > 0
    c = LD(float(c))
    pA, dA, hA, jA = wa[sa], A['d'][sa] + c, A['dh'][sa] + c, A['j'][sa]
    pB, dB, hB, jB = wb[sb], B['d'][sb], B['dh'][sb], B['j'][sb]
    EdA, EdB = (pA * dA).sum(), (pB * dB).sum()
    EhA, EhB = (pA * hA).sum(), (pB * hB).sum()
    ED, EDh = EdA + EdB, EhA + EhB
    J = (pA * jA).sum() + (pB * jB).sum()
    T10 = cut_value(hA, dA, pA, hB, dB, pB)
    T11 = cut_value(dA, dA, pA, dB, dB, pB)
    a00, a01 = bool(EDh < 0), bool(ED < 0)
    delta = dA[:, None] + dB[None, :]
    dhat = hA[:, None] + hB[None, :]
    wrong = ((delta < 0) != (dhat < 0)) * (pA[:, None] * pB[None, :])
    L = {'00': J + a00 * ED, '01': J + a01 * ED, '10': J + T10, '11': J + T11}
    return dict(L=L, ED=ED, EDh=EDh, absD=ED - 2 * T11, a00=a00, a01=a01, wrong=wrong.sum(),
                EdA=EdA, EdB=EdB, EhA=EhA, EhB=EhB)


def contrasts(L):
    G_S, G_M, G_SM = L['00'] - L['10'], L['00'] - L['01'], L['00'] - L['11']
    return dict(G_S=G_S, G_M=G_M, G_SM=G_SM, Gamma=G_SM - G_S - G_M,
                G_S_M1=L['01'] - L['11'], G_M_S1=L['10'] - L['11'])


def evaluate(spec):
    rid, lamA, lamB, kappa, eta, h, ref, K, *rest = spec
    c_sw, age, amp = (*map(F, rest), *(F(0), F(1), F(6))[len(rest):])
    t0 = time.monotonic()
    cell = make_regime(lamA, lamB, kappa, eta, h, rid, age, amp)
    uA, repA, wA, trA = observation_bins(cell, 'A', ref, K)
    uB, repB, wB, trB = observation_bins(cell, 'B', ref, K)
    A = side_rows(cell, 'A', ref, repA, uA)
    B = side_rows(cell, 'B', ref, repB, uB)
    Lbar = dict.fromkeys(('00', '01', '10', '11'), 0.0)
    S = P_flip = flip_stakes = wrong = P_rev = 0.0
    pairs = []
    for ia, pa in enumerate(wA):
        for ib, pb in enumerate(wB):
            w = pa * pb
            v = pair_values(A, B, ia, ib, c_sw)
            for k in Lbar:
                Lbar[k] += w * float(v['L'][k])
            S += w * float(v['absD'])
            flip = v['a00'] != v['a01']
            P_flip += w * flip
            flip_stakes += w * flip * abs(float(v['ED']))
            wrong += w * float(v['wrong'])
            reverse = (v['EDh'] != 0) and ((v['EDh'] > 0) != (v['ED'] > 0))
            P_rev += w * reverse
            side_total = float(v['EdA'] + abs(v['EdB']))
            pairs.append((rid, ia, ib, w, float(v['ED']), float(v['EDh']), float(v['EdA']), float(v['EdB']),
                          float(v['EhA']), float(v['EhB']), int(flip), int(reverse), int(v['EDh'] == 0),
                          abs(float(v['ED'])) / side_total if side_total > 0 else float('nan')))
    G = contrasts(Lbar)
    C = Lbar['11']
    out = dict(id=rid, lambdaA=float(F(lamA)), lambdaB=float(F(lamB)), kappa=float(F(kappa)), eta=float(F(eta)),
               h=float(F(h)), c_sw=float(c_sw), age=float(age), amp=float(amp), ref=ref, K=K, nA=len(repA), nB=len(repB), truncated_A=trA, truncated_B=trB,
               Cbar=C, Sbar=S, P_flip=P_flip, E_stakes_given_flip=flip_stakes / P_flip if P_flip > 0 else 0.0,
               P_wrong_ranking=wrong, P_reversal=P_rev, wall_s=time.monotonic() - t0)
    for g, val in G.items():
        out[g] = val
        out[g + '_pctC'] = 100 * val / C if C > 0 else float('nan')
        out[g + '_pctS'] = 100 * val / S if S > 0 else float('nan')
    out['GM_identity_gap'] = G['G_M'] - flip_stakes
    return out, pairs
