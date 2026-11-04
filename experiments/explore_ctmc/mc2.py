"""Doan Van Tai — Monte Carlo control (c) for ctmc-v2: end-to-end with common random numbers
[EXPLORATION ONLY; AI (Claude) theo ủy quyền].

Uniformization at a fixed total rate, untruncated queues, two independent on-off modulators per path. The only
evaluator outputs used are the decision functions (index lookups). Stay runs from an empty queue for a burn-in
>= 30 T_int, Y is read at t0 - tau, X at t0, each pipeline acts on its own information, and both actions are run from
X with the same event times, uniforms and mode paths, so the contrasts have paired errors.
"""
from fractions import Fraction as F

import numpy as np

from experiments.explore_ctmc import ctmc2

MU = ctmc2.MU


def _arr(load, m, af, as_):
    return float(load) + np.where(m & 1, af, -af) + np.where(m & 2, as_, -as_)


def advance(n, m, load, Tf, Ts, af, as_, T, rng, mu=MU):
    af, as_ = float(af), float(as_)
    lam_max = float(load) + af + as_
    qf, qs = 1 / float(Tf), 1 / float(Ts)
    Lam = lam_max + mu + qf + qs
    t = np.zeros(n.size)
    active = np.arange(n.size)
    while active.size:
        t[active] += rng.exponential(1 / Lam, active.size)
        go = active[t[active] < T]
        U = rng.random(go.size) * Lam
        n[go] += U < _arr(load, m[go], af, as_)
        n[go] -= (U >= lam_max) & (U < lam_max + mu) & (n[go] > 0)
        m[go] ^= ((U >= lam_max + mu) & (U < lam_max + mu + qf)).astype(m.dtype)
        m[go] ^= (2 * ((U >= lam_max + mu + qf) & (U < Lam))).astype(m.dtype)
        active = go


def costs(n0, m0, load_stay, load_switch, Tf, Ts, af, as_, h, rng, mu=MU):
    af, as_ = float(af), float(as_)
    lam_max = max(float(load_stay), float(load_switch)) + af + as_
    qf, qs = 1 / float(Tf), 1 / float(Ts)
    Lam = lam_max + mu + qf + qs
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
        mg = m[go]
        nS[go] += U < _arr(load_stay, mg, af, as_)
        nW[go] += U < _arr(load_switch, mg, af, as_)
        serve = (U >= lam_max) & (U < lam_max + mu)
        nS[go] -= serve & (nS[go] > 0)
        nW[go] -= serve & (nW[go] > 0)
        m[go] ^= ((U >= lam_max + mu) & (U < lam_max + mu + qf)).astype(m.dtype)
        m[go] ^= (2 * ((U >= lam_max + mu + qf) & (U < Lam))).astype(m.dtype)
        peak = max(peak, int(nS[go].max(initial=0)), int(nW[go].max(initial=0)))
        active = go
    return cS, cW, peak


def end_to_end(regime, h, episodes, seed, burn_factor=30):
    lamA, lamB, u, Tf, Ts, af, as_ = regime
    exact = ctmc2.evaluate(lamA, lamB, u, Tf, Ts, af, as_, [h], arrays=True, disagree=False)
    arr = exact.pop('_arrays')
    row = exact['h'][0]
    rng = np.random.default_rng(seed)
    T_burn = burn_factor * max(exact['chains']['A_stay']['T_int'], exact['chains']['B_stay']['T_int'], 1.0)
    side = {}
    for name, stay, switch, N in (('A', lamA + u, lamA, arr['NA']), ('B', lamB, lamB + u, arr['NB'])):
        n = np.zeros(episodes, dtype=np.int64)
        m = rng.integers(0, 4, episodes).astype(np.int64)
        advance(n, m, stay, Tf, Ts, af, as_, T_burn, rng)
        y = n.copy()
        advance(n, m, stay, Tf, Ts, af, as_, ctmc2.TAU, rng)
        if max(y.max(), n.max()) > N:
            raise ArithmeticError(f'path {name}: simulated backlog above truncation N={N}')
        cS, cW, peak = costs(n, m, stay, switch, Tf, Ts, af, as_, h, rng)
        side[name] = dict(y=y, x=4 * n + m, cS=cS, cW=cW, peak=peak)
    A_, B_ = side['A'], side['B']
    a11 = arr['dA'][0][A_['x']] + arr['dB'][0][B_['x']] < 0
    a10 = arr['dhA'][0][A_['x']] + arr['dhB'][0][B_['x']] < 0
    a01 = arr['dAo'][0][A_['y']] + arr['dBo'][0][B_['y']] < 0
    a00 = arr['dhAo'][0][A_['y']] + arr['dhBo'][0][B_['y']] < 0
    CS = A_['cS'] + B_['cS']
    D = A_['cW'] + B_['cW'] - CS
    a = {k: v.astype(float) for k, v in dict(a00=a00, a01=a01, a10=a10, a11=a11).items()}
    samples = dict(L00=CS + a['a00'] * D, L01=CS + a['a01'] * D, L10=CS + a['a10'] * D, L11=CS + a['a11'] * D,
                   G_S=(a['a00'] - a['a10']) * D, G_M=(a['a00'] - a['a01']) * D, G_SM=(a['a00'] - a['a11']) * D,
                   Gamma=(a['a10'] + a['a01'] - a['a00'] - a['a11']) * D, S=(a['a01'] - a['a11']) * D,
                   M=(a['a10'] - a['a11']) * D)
    Cref = row['Cref']
    exact_abs = {k: row[k] for k in ('L00', 'L01', 'L10', 'L11')}
    exact_abs.update({k: row[k] * Cref / 100 for k in ('G_S', 'G_M', 'G_SM', 'Gamma', 'S', 'M')})
    checks = {}
    for k, v in samples.items():
        mean, se = float(v.mean()), float(v.std(ddof=1) / np.sqrt(v.size))
        z = (mean - exact_abs[k]) / se if se > 0 else (0.0 if mean == exact_abs[k] else np.inf)
        checks[k] = dict(mc=mean, se=se, exact=exact_abs[k], z=z, pass_=bool(abs(z) <= 3.5))
    return dict(parameters=exact['parameters'], h=str(h), episodes=episodes, seed=seed, T_burn=T_burn,
                peak_backlog=max(A_['peak'], B_['peak']), N=exact['N'], checks=checks,
                PASS=all(c['pass_'] for c in checks.values()))
