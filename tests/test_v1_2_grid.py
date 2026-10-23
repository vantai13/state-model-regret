"""Doan Van Tai — invariants of the accepted grid v1.2 and one from-scratch recomputation."""
import json
from fractions import Fraction as F
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GRID = json.loads((ROOT / 'notes/design/grid_v1_2.json').read_text())
CAP = 2e11


def mid(c, level):
    return (c[f'p_{level}'][0] + c[f'p_{level}'][1]) / 2


def test_status_and_counts():
    assert GRID['status'] == 'ACCEPTED'
    assert [c['id'] for c in GRID['main']] == [f'M{i:02}' for i in range(1, 39)]
    assert len(GRID['heldout']) == 12 and not GRID['heldout_failures']
    groups = [c['group'] for c in GRID['main']]
    assert groups.count('core') == 22 and groups.count('spoke_A50') == 8 and groups.count('spoke_h2') == 8


@pytest.mark.parametrize('part', ['main', 'heldout'])
def test_every_cell_contested_stable_candidate_and_within_budget(part):
    for c in GRID[part]:
        assert c['in_band_all_levels'], c['id']
        assert all(.1 <= c[f'p_{l}'][0] and c[f'p_{l}'][1] <= .9 for l in (1, 2, 4)), c['id']
        assert c['label_1'] == c['label_2'] == 'candidate', c['id']
        assert c['updates_16'] <= CAP and c['within_budget_dt16'], c['id']
        assert max(c[f'unresolved_{l}'] for l in (1, 2, 4)) <= .01
        assert all(abs(mid(c, 1) - a['target']) <= .15 for a in c['anchors']), c['id']


def test_only_expected_main_failures():
    fails = {(f['slice'], f['target'], f['bracketing']) for f in GRID['main_failures']}
    assert fails == {('V09', .3, 'floor'), ('V10', .3, 'floor')}


def test_derived_coordinates_and_ladder():
    for c in GRID['main'] + GRID['heldout']:
        lam, eta = F(c['lambdaA']), F(c['eta'])
        assert lam >= 6 and (lam + 2 * eta) / 10 <= F(95, 100) and (lam * 4).denominator == 1
        assert F(c['psi']) == (lam - 8) / 10 and F(c['delta']) == (lam + 2 * eta - 8) / 10


def test_calibration_rule_with_exact_ties():
    cal = [c['id'] for c in GRID['calibration']]
    assert cal == ['M01', 'M09', 'M22']
    flagged = [c['id'] for c in GRID['main'] if c['calibration']]
    assert flagged == cal and all(c['group'] == 'core' for c in GRID['main'] if c['calibration'])
    kappas = {c['kappa'] for c in GRID['main'] if c['calibration']}
    assert kappas == {'3/10', '1', '3'}


def test_controls_and_probes_keep_expected_labels():
    labels = {c['id']: (c['label_1'], c['label_2']) for c in GRID['controls']}
    expected = {'N01': 'SD-cell', 'N02': 'SD-cell', 'N03': 'conservation-cell', 'N04': 'conservation-cell',
                'W01': 'WD-cell', 'S01': 'WD-cell'}
    assert labels == {k: (v, v) for k, v in expected.items()}
    assert {p['id']: p['label_1'] for p in GRID['probes']} == {'P01': 'conservation-cell', 'P02': 'WD-cell'}


def test_one_main_cell_recomputes_exactly():
    from experiments.lessons.run_v1_2 import main_slices
    from experiments.explore.reformulate_grid import task
    cell = next(c for c in GRID['main'] if c['id'] == 'M31')
    s = next(s for s in main_slices() if s['slice'] == cell['slice'])
    row = task((s, F(cell['lambdaA']), (1,), False))
    assert row['status'] == 'OK'
    assert [row['p_low_1'], row['p_high_1']] == cell['p_1']
