"""Doan Van Tai — tests for idelta3 [AI (Claude) theo ủy quyền 14/11/2026]. Synthetic data, a small synthetic regime
and one exposed pilot point only."""
import json
from fractions import Fraction as F

import numpy as np

from experiments.explore_ctmc import idelta as D1
from experiments.explore_ctmc import idelta2 as D2
from experiments.explore_ctmc import idelta3 as D3


def test_e_abs_pair_brute_force():
    rng = np.random.default_rng(3)
    wa, wb = rng.random(25), rng.random(17)
    wa, wb = wa / wa.sum(), wb / wb.sum()
    a, b = rng.normal(size=25), rng.normal(size=17)
    ref = (wa[:, None] * wb[None, :] * np.abs(a[:, None] + b[None, :])).sum()
    assert abs(D3.e_abs_pair(wa, a, wb, b) - ref) <= 1e-12


def test_light_regime_matches_round1_counterfactual():
    case = dict(id='T_small3', parameters=['7', '7', '1', '1/2', '0'], hs=['1/2', '1', '2', '4'], x=0.0,
                tags=dict(stratum='test'))
    light = D3.light_regime(case)
    full, _ = D1.run_regime(case)
    for a, b in zip(light['rows'], full['rows']):
        assert abs(a['Gamma_self'] - a['Gamma']) <= 1e-9
        assert abs(a['Gamma_add'] - b['Gamma_cf']['add']) <= 1e-9
        assert a['T_fresh'] is None or a['T_fresh'] >= 0
        assert 0 <= a['kappa_add'] <= 1


def test_fluid_point_gamma_matches_engine():
    p = [q for q in json.loads(D2.POINTS.read_text())['points'] if q['set'] == 'pilot'][0]
    out = D3.fluid_point(p, hs=(F(2),))
    r = out['rows'][0]
    assert abs(r['Gamma'] - r['Gamma_engine']) <= 1e-9 and r['T_fresh'] >= 0


def test_round3_panel_is_new():
    seen = D2.seen_all() | {tuple(F(x) for x in c['parameters'][:4]) for c in json.loads(D2.CASES.read_text())}
    cases = json.loads(D3.CASES.read_text())
    assert len(cases) == sum(D3.COUNTS.values())
    assert not any(tuple(F(x) for x in c['parameters'][:4]) in seen for c in cases)
    old = {(p['kappa'], p['lamA'], p['eta'], p['yA'], p['yB']) for p in json.loads(D2.POINTS.read_text())['points']}
    new = [(p['kappa'], p['lamA'], p['eta'], p['yA'], p['yB']) for p in json.loads(D3.POINTS.read_text())['points']]
    assert len(set(new)) == D3.N_FLUID and not set(new) & old
    pts = json.loads(D3.POINTS.read_text())
    assert '4' not in pts['h'] and all(F(p['kappa']) != F(3, 5) for p in pts['points'])


def test_ctmc_readout_split():
    mk = lambda g, ga, t, k: dict(Gamma=g, Gamma_add=ga, T_fresh=t, kappa_add=k)
    regs = [dict(status='COMPLETED', stratum=s, rows=[None, None, None, mk(1, ga, t, .99)])
            for s, ga, t in (('neg', 1.2, .1), ('pos', 1.0, .2), ('band', .1, 2.0), ('band', .2, 1.5))]
    r = D3.ctmc_readout(regs, 3, cut=1.0, var='T_fresh')
    assert r['split']['n_le'] == 2 and r['split']['n_gt'] == 2
    assert abs(r['split']['median_rho_le'] - 1.1) < 1e-12 and abs(r['split']['median_rho_gt'] - .15) < 1e-12
    assert r['band']['n'] == 2 and r['spearman_T_fresh_rho'] < 0
