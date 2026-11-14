"""Doan Van Tai — tests for ce_knockout [AI (Claude) theo ủy quyền 14/11/2026]. Synthetic regime only."""
from fractions import Fraction as F

import numpy as np

from experiments.explore_ctmc import ctmc as C
from experiments.explore_ctmc import ce_knockout as K


def test_fluid_gap_reproduces_engine_at_lattice():
    lam, u, kappa, N = F(7), F(1), F(1, 2), 40
    hs = [F(1, 2), F(2), F(9)]
    ref = C.m0_gap(lam, u, kappa, N, [float(h) for h in hs], 'B')
    n = np.repeat(np.arange(N + 1), 2).astype(float)
    sig = np.tile([-1.0, 1.0], N + 1)
    got = K.fluid_gap(lam, u, kappa, n, sig, hs, 'B')
    assert np.abs(got - ref).max() <= 1e-12 * max(1.0, np.abs(ref).max())
    refA = C.m0_gap(lam, u, kappa, N, [float(h) for h in hs], 'A')
    assert np.abs(K.fluid_gap(lam, u, kappa, n, sig, hs, 'A') - refA).max() <= 1e-12 * max(1.0, np.abs(refA).max())


def test_plug_backlog_lattice_and_linear():
    v = np.arange(12, dtype=float) ** 2          # index 2n + m, n = 0..5
    V = v.reshape(-1, 2)
    nb, p1 = np.array([0.0, 3.0, 2.5]), np.array([0.25, 1.0, 0.5])
    got = K.plug_backlog(v, nb, p1)
    assert got[0] == 0.75 * V[0, 0] + 0.25 * V[0, 1]
    assert got[1] == V[3, 1]
    assert abs(got[2] - 0.5 * (0.5 * (V[2, 0] + V[3, 0])) - 0.5 * (0.5 * (V[2, 1] + V[3, 1]))) <= 1e-12


def test_posterior_moments_tower():
    ch = C.chain(F(8), F(1, 2), 120)
    nb, p1 = K.posterior_moments(ch)
    p = ch.pi.reshape(-1, 2).sum(axis=1)
    assert abs(float(p @ nb) - ch.r) <= 1e-9 * max(1.0, ch.r)          # stationary under Stay: E E[n|y] = r
    assert abs(float(p @ p1) - float(ch.pi.reshape(-1, 2)[:, 1].sum())) <= 1e-12
    assert p1.min() >= 0 and p1.max() <= 1


def test_regime_controls_and_identities():
    case = dict(id='T_ce', parameters=['7', '15/2', '1', '1/2', '0'], hs=['1/2', '1', '2', '4'], x=0.5,
                tags=dict(stratum='test'))
    out = K.regime(case)
    for r in out['rows']:
        c = r['controls']
        assert c['L_match_pp'] <= 1e-7 and c['tower_rel'] <= 1e-10
        assert c['bayes_M1_pp'] >= -1e-9                                # L01 is Bayes-optimal among S0 rules
        assert abs(r['G_S_PB'] - (r['G_S'] + r['P_M0'])) <= 1e-9
        assert abs(r['E_K_pct'] - (r['E_Jhat_pct'] - r['E_J_pct'])) <= 1e-9
        assert r['Eabs_K_pct'] >= 0 and r['Eabs_Jhat_pct'] >= 0


def test_nk_arm_identity():
    case = dict(id='T_ce2', parameters=['7', '15/2', '1', '1/2', '0'], hs=['1/2', '2'], x=0.5, tags=dict(stratum='test'))
    for r in K.regime(case)['rows']:
        assert abs(r['G_S_NK'] - (r['G_S'] + r['P_NK'])) <= 1e-9
        assert r['err_B_pct'] >= 0 and r['err_PB_pct'] >= 0


def test_ce_panel_is_new():
    import json
    from experiments.explore_ctmc import idelta2 as D2
    seen = D2.seen_all()
    for path in K.CALIB_SETS:
        seen |= {tuple(F(x) for x in c['parameters'][:4]) for c in json.loads(path.read_text())}
    cases = json.loads(K.CASES.read_text())
    assert len(cases) == sum(K.COUNTS.values())
    keys = [tuple(F(x) for x in c['parameters'][:4]) for c in cases]
    assert len(set(keys)) == len(keys) and not set(keys) & seen
