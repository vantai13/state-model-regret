"""Doan Van Tai — tests for idelta2 [AI (Claude) theo ủy quyền 14/11/2026]. Pilot points and synthetic data only."""
import csv
import json
import math
from fractions import Fraction as F

import numpy as np
import pytest

from experiments.explore_ctmc import idelta2 as D2


def _pilot():
    return [p for p in json.loads(D2.POINTS.read_text())['points'] if p['set'] == 'pilot']


def test_fluid_cell_gamma_matches_engine_and_constant_bias_identity():
    r = D2.fluid_cell(_pilot()[0], F(2))
    assert abs(r['Gamma'] - r['Gamma_engine']) <= 1e-9
    assert r['EabsI_pct'] >= 0 and 0 <= r['kappa_add'] <= 1


def test_points_avoid_sealed_axes_and_named_cells():
    pts = json.loads(D2.POINTS.read_text())
    assert '4' not in pts['h'] and all(F(p['kappa']) != F(3, 5) for p in pts['points'])
    assert len({(p['kappa'], p['lamA'], p['eta'], p['yA'], p['yB']) for p in pts['points']}) == D2.N_PILOT + D2.N_PANEL
    assert sum(p['set'] == 'pilot' for p in pts['points']) == D2.N_PILOT


def test_fresh_cases_are_new():
    seen = D2.seen_all()
    cases = json.loads(D2.CASES.read_text())
    assert len(cases) == 3 * D2.N_PER
    assert not any(tuple(F(x) for x in c['parameters'][:4]) in seen for c in cases)


def test_additivity_from_dose_synthetic(tmp_path):
    path = tmp_path / 'd.csv'
    rows = []
    for side, vals in (('A', [(1.0, .5), (3.0, .5)]), ('B', [(-1.0, .25), (-1.0, .75)])):
        for n, (e, pi) in enumerate(vals):
            rows.append(['X', '1', side, 0, n, e, 0, 0, 0, 0, 0, pi])
    with open(path, 'w', newline='') as f:
        csv.writer(f).writerows(rows)
    b, var = 2.0 - 1.0, 1.0           # A: mean 2, var 1; B: constant -1
    assert abs(D2.additivity_from_dose(path, '1') - abs(b) / math.sqrt(b * b + var)) <= 1e-12


def test_readouts_on_synthetic_tables():
    mk = lambda g, ga, ei, k: dict(Gamma=g, Gamma_add=ga, EabsI=ei, kappa_add=k)
    table = {'r1': [mk(.1, 0, 3, .1), mk(.2, .01, 2, .2), mk(1, .5, .5, .9), mk(2, 1.8, .1, 1)],
             'r2': [mk(.1, 0, 3, .1), mk(.01, 0, 2, .2), mk(1, .5, .5, .9), mk(2, .4, .1, 1)]}
    r = D2.ctmc_readout(table)
    assert r['n_elig_lo'] == 1 and r['n_elig_hi'] == 2 and r['n_elig_both'] == 1
    assert abs(r['median_ratio_lo'] - .05) < 1e-12 and abs(r['median_ratio_hi'] - .55) < 1e-12
    assert r['frac_ratio_up'] == 1 and r['frac_EabsI_down'] == 1 and r['frac_kadd_up'] == 1


def test_lock_refuses_changed_file(tmp_path, monkeypatch):
    f = tmp_path / 'x.txt'
    f.write_text('a')
    lock = tmp_path / 'lock.json'
    lock.write_text(json.dumps(dict(files={str(f): D2.sha(f)})))
    monkeypatch.setattr(D2, 'LOCK', lock)       # absolute paths: ROOT / abs_path == abs_path
    assert D2.check_lock()['files']
    f.write_text('b')
    with pytest.raises(PermissionError):
        D2.check_lock()
