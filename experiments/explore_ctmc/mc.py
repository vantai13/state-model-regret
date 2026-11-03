"""Doan Van Tai — Monte Carlo controls for ctmc-v1: V3 end-to-end and V8 Gillespie V(h, x)
[EXPLORATION ONLY; AI (Claude) theo ủy quyền].

Simulation uses uniformization at a fixed total rate, untruncated queues and no evaluator output except the four
decision functions (index lookups). V3: Stay runs from an empty queue for a burn-in >= 30 T_int, the old backlog
Y is read at t0 - tau, the state X at t0, every pipeline acts on its own information, and both actions are run
from X with common random numbers (same event times, uniforms and mode path), so contrasts have paired errors.
"""
from fractions import Fraction as F

import numpy as np

from experiments.explore_ctmc import ctmc


def _windows(load_hi, kappa, a, mu):
    lam_max = float(load_hi) + a
    q = 1 / float(kappa)
    return lam_max, q, lam_max + mu + q


def advance(n, m, load, kappa, T, rng, a=ctmc.A, mu=ctmc.MU):
    """Run (n, m) in place to time T under one constant load (arrival window [0, arr), service window at
    [lam_max, lam_max + mu), mode flip after it, dummy otherwise)."""
    lam_max, q, Lam = _windows(load, kappa, a, mu)
    t = np.zeros(n.size)
    active = np.arange(n.size)
    while active.size:
        t[active] += rng.exponential(1 / Lam, active.size)
        go = active[t[active] < T]
        U = rng.random(go.size) * Lam
        arr = float(load) + np.where(m[go] == 1, a, -a)
        n[go] += (U < arr)
        n[go] -= (U >= lam_max) & (U < lam_max + mu) & (n[go] > 0)
        m[go] ^= ((U >= lam_max + mu) & (U < lam_max + mu + q)).astype(m.dtype)
        active = go


def costs(n0, m0, load_stay, load_switch, kappa, h, rng, a=ctmc.A, mu=ctmc.MU):
    """Cumulative backlog to h under both loads from the same start, common random numbers."""
    lam_max, q, Lam = _windows(max(load_stay, load_switch), kappa, a, mu)
    nS, nW, m = n0.copy(), n0.copy(), m0.copy()
    cS, cW = np.zeros(n0.size), np.zeros(n0.size)
    t = np.zeros(n0.size)
    active = np.arange(n0.size)
    h = float(h)
    peak = int(max(nS.max(), 0))
    while active.size:
        tn = t[active] + rng.exponential(1 / Lam, active.size)
        seg = np.minimum(tn, h) - t[active]
        cS[active] += nS[active] * seg
        cW[active] += nW[active] * seg
        t[active] = tn
        go = active[tn < h]
        U = rng.random(go.size) * Lam
        sig = np.where(m[go] == 1, a, -a)
        nS[go] += (U < float(load_stay) + sig)
        nW[go] += (U < float(load_switch) + sig)
        serve = (U >= lam_max) & (U < lam_max + mu)
        nS[go] -= serve & (nS[go] > 0)
        nW[go] -= serve & (nW[go] > 0)
        m[go] ^= ((U >= lam_max + mu) & (U < lam_max + mu + q)).astype(m.dtype)
        peak = max(peak, int(nS[go].max(initial=0)), int(nW[go].max(initial=0)))
        active = go
    return cS, cW, peak


def end_to_end(lamA, lamB, u, kappa, h, episodes, seed, burn_factor=30, d22=False):
    """V3: Monte Carlo estimates of the four losses and six contrasts against the exact evaluator. With d22=True
    also the two backlog-only pipelines (Y, Q) and the split F, V, F1, V1 (control V3-D22)."""
    if d22:
        exact = ctmc.evaluate_d22(lamA, lamB, u, kappa, [h], arrays=True)
        arr = exact.pop('_arrays_d22')
    else:
        exact = ctmc.evaluate(lamA, lamB, u, kappa, [h], arrays=True, disagree=False)
        arr = exact.pop('_arrays')
    row = exact['h'][0]
    rng = np.random.default_rng(seed)
    T_burn = burn_factor * max(exact['chains']['A_stay']['T_int'], exact['chains']['B_stay']['T_int'], 1.0)
    side = {}
    for name, stay, switch, N in (('A', lamA + u, lamA, arr['NA']), ('B', lamB, lamB + u, arr['NB'])):
        n = np.zeros(episodes, dtype=np.int64)
        m = rng.integers(0, 2, episodes).astype(np.int64)
        advance(n, m, stay, kappa, T_burn, rng)
        y = n.copy()
        advance(n, m, stay, kappa, ctmc.TAU, rng)
        if max(y.max(), n.max()) > N:
            raise ArithmeticError(f'path {name}: simulated backlog above truncation N={N}')
        cS, cW, peak = costs(n, m, stay, switch, kappa, h, rng)
        side[name] = dict(y=y, x=2 * n + m, cS=cS, cW=cW, peak=peak)
    A_, B_ = side['A'], side['B']
    c = float(F(exact['parameters'][4]))
    a11 = arr['dA'][0][A_['x']] + arr['dB'][0][B_['x']] + c < 0
    a10 = arr['dhA'][0][A_['x']] + arr['dhB'][0][B_['x']] + c < 0
    a01 = arr['dAo'][0][A_['y']] + arr['dBo'][0][B_['y']] + c < 0
    a00 = arr['dhAo'][0][A_['y']] + arr['dhBo'][0][B_['y']] + c < 0
    CS = A_['cS'] + B_['cS']
    D = A_['cW'] + B_['cW'] + c - CS
    a = {k: v.astype(float) for k, v in dict(a00=a00, a01=a01, a10=a10, a11=a11).items()}
    samples = dict(L00=CS + a['a00'] * D, L01=CS + a['a01'] * D, L10=CS + a['a10'] * D, L11=CS + a['a11'] * D,
                   G_S=(a['a00'] - a['a10']) * D, G_M=(a['a00'] - a['a01']) * D, G_SM=(a['a00'] - a['a11']) * D,
                   Gamma=(a['a10'] + a['a01'] - a['a00'] - a['a11']) * D, S=(a['a01'] - a['a11']) * D,
                   M=(a['a10'] - a['a11']) * D)
    Cref = row['Cref']
    exact_abs = {k: row[k] for k in ('L00', 'L01', 'L10', 'L11')}
    exact_abs.update({k: row[k] * Cref / 100 for k in ('G_S', 'G_M', 'G_SM', 'Gamma', 'S', 'M')})
    if d22:
        nA, nB = A_['x'] // 2, B_['x'] // 2
        acb0 = (arr['gA'][A_['y'], nA] + arr['gB'][B_['y'], nB] + c < 0).astype(float)
        acb1 = (arr['vA'][A_['y'], nA] + arr['vB'][B_['y'], nB] + c < 0).astype(float)
        samples.update(L_cb0=CS + acb0 * D, L_cb1=CS + acb1 * D, F=(a['a00'] - acb0) * D, V=(acb0 - a['a10']) * D,
                       F1=(a['a01'] - acb1) * D, V1=(acb1 - a['a11']) * D)
        dd = row['d22']
        exact_abs.update(L_cb0=dd['L_cb0'], L_cb1=dd['L_cb1'], **{k: dd[k] * Cref / 100 for k in ('F', 'V', 'F1', 'V1')})
    checks = {}
    for k, v in samples.items():
        mean, se = float(v.mean()), float(v.std(ddof=1) / np.sqrt(v.size))
        z = (mean - exact_abs[k]) / se if se > 0 else (0.0 if mean == exact_abs[k] else np.inf)
        checks[k] = dict(mc=mean, se=se, exact=exact_abs[k], z=z, pass_=bool(abs(z) <= 3.5))
    return dict(parameters=exact['parameters'], h=str(h), episodes=episodes, seed=seed, T_burn=T_burn,
                peak_backlog=max(A_['peak'], B_['peak']), N=exact['N'], checks=checks,
                PASS=all(c['pass_'] for c in checks.values()), exact=exact)


def gillespie_V(load, kappa, N, state, h, episodes, seed):
    """V8: Monte Carlo V(h, x) from one fixed state under one load; returns (mean, se, exact)."""
    rng = np.random.default_rng(seed)
    n0 = np.full(episodes, state[0], dtype=np.int64)
    m0 = np.full(episodes, state[1], dtype=np.int64)
    cS, _, _ = costs(n0, m0, load, load, kappa, h, rng)
    exact = ctmc.Chain(load, kappa, N).V([h])[0][2 * state[0] + state[1]]
    return float(cS.mean()), float(cS.std(ddof=1) / np.sqrt(episodes)), float(exact)
