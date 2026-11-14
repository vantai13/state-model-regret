"""Doan Van Tai — tests for the I_Delta exploration module [AI (Claude) theo ủy quyền 14/11/2026].
Small synthetic chains/regimes only; no regime of the design list is evaluated here."""
from fractions import Fraction as F

import numpy as np
from scipy.sparse.linalg import expm_multiply

from experiments.explore_ctmc import ctmc as C
from experiments.explore_ctmc import idelta as D


def test_boundary_identity_small_chain():
    ch = C.chain(7, F(1, 2), 60)
    hs = [F(1, 2), F(3)]
    V = ch.V(hs)
    Vf = D.vfree(ch.load, ch.kappa, ch.N, hs)
    I0, BN = D.boundary_terms(ch, hs)
    assert np.abs(V - Vf - C.MU * I0 + BN).max() <= 1e-9 * max(1, np.abs(V).max())


def test_I0_matches_quadrature():
    ch = C.chain(8, 1, 50)
    h = 2.0
    I0, _ = D.boundary_terms(ch, [h])
    f0 = (np.repeat(np.arange(ch.N + 1), 2) == 0).astype(float)

    def simpson(points):
        s = np.linspace(0, h, points)
        w = (h - s)[:, None] * np.array([expm_multiply(ch.Q * t, f0) for t in s])   # P(n_t = 0 | x) per start x
        return (s[1] - s[0]) / 3 * (w[0] + w[-1] + 4 * w[1:-1:2].sum(axis=0) + 2 * w[2:-1:2].sum(axis=0))
    coarse, fine = simpson(201), simpson(401)
    # Simpson error falls ~16x per halving; the exact value must sit within the Richardson error estimate
    assert np.all(np.abs(I0[0] - fine) <= 2 * np.abs(fine - coarse) / 15 + 1e-13)
    assert np.abs(I0[0] - fine).max() <= 1e-6


def test_hit_prob_bounds_and_monotone():
    ch = C.chain(7, 1, 60)
    P = D.hit_prob(ch, [F(1), F(4)])
    assert P.min() >= -1e-12 and P.max() <= 1 + 1e-12
    assert np.allclose(P[:, :2], 1.0)
    for m in (0, 1):
        assert np.all(np.diff(P[0].reshape(-1, 2)[:, m]) <= 1e-12)
    assert np.all(P[1] >= P[0] - 1e-12)


def test_abs_stats_matches_brute_force():
    rng = np.random.default_rng(1)
    wA, wB = rng.random(40), rng.random(30)
    wA, wB = wA / wA.sum(), wB / wB.sum()
    a, b = rng.normal(size=40), rng.normal(size=30)
    a, b = a - wA @ a, b - wB @ b
    s = D.abs_stats(wA, a, wB, b, cref=10.0)
    tot = a[:, None] + b[None, :]
    W = wA[:, None] * wB[None, :]
    assert abs(s['EabsI'] - (W * np.abs(tot)).sum()) <= 1e-12
    for d in D.DELTAS:
        assert abs(s[f'P_gt_{d}pct'] - W[np.abs(tot) > d * 10 / 100].sum()) <= 1e-12
    flat, ww = np.abs(tot).ravel(), W.ravel()
    order = np.argsort(flat)
    cum = np.cumsum(ww[order])
    for q in D.QUANTS:
        ref = flat[order][np.searchsorted(cum, q - 1e-15)]
        assert abs(s[f'q{q}'] - ref) <= 1e-9


def test_first_quiet():
    ok = np.array([False, True, False, True, True])
    assert D.first_quiet(None, ok) == 3
    assert D.first_quiet(None, np.array([True, True])) == 0
    assert D.first_quiet(None, np.array([True, False])) is None


def test_select_regimes_rule():
    ids = [c['id'] for c in D.select_regimes()]
    assert ids == ['TN0003', 'TN0000', 'TN0004', 'TB0007', 'TB0001', 'TB0003', 'TP0079', 'TP0003', 'TP0004']


def test_run_regime_small_controls_and_example():
    case = dict(id='T_small', parameters=['7', '7', '1', '1/2', '0'], hs=['1/2', '1', '2', '4'], x=0.0,
                tags=dict(stratum='test'))
    out, _ = D.run_regime(case)
    assert out['status'] == 'COMPLETED'
    for r in out['rows']:
        c = r['controls']
        assert c['identity_resid'] <= 1e-9 and c['tower_A'] <= 1e-9 and c['tower_B'] <= 1e-9
        assert c['posterior_A'] <= 1e-9 and c['posterior_B'] <= 1e-9 and c['Gamma_match_pp'] <= 1e-9
        assert c['shift_A'] <= 1e-9 and c['shift_B'] <= 1e-9
        assert abs(r['I']['EI']) <= 1e-9 * r['Cref']
        assert r['I']['EabsI'] >= 0
    ex = out['rows'][1]['example']
    for k in ('B_empty', 'B_backlog'):
        e = ex[k]
        assert abs(e['I'] - (e['d11'] - e['d10'] - e['d01'] + e['d00'])) <= 1e-12


def test_fluid_reference_point_outside_clip_is_exact_zero():
    from experiments.P4_07_clipping.check_clipping import exact_reference, rational_mean, threshold
    dt, H = F(1, 20), 10
    keep = (1 + np.exp(-2 * float(dt / F(3, 10)))) / 2
    St, Sw = (F(-9) * dt, F(3) * dt), (F(-7) * dt, F(5) * dt)
    for m in (0, 1):
        t = max(threshold(H, St, m), threshold(H, Sw, m))
        e = lambda q: ((rational_mean(H, Sw, keep, q, m) - rational_mean(H, St, keep, q, m))
                       - (exact_reference(H, Sw, keep, q, m) - exact_reference(H, St, keep, q, m)))
        assert e(t) == 0 and e(t + 1) == 0
        assert e(F(0)) != 0 or m == 1
