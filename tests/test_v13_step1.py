"""Doan Van Tai — v1.3 step-1 measures against brute-force enumeration on synthetic tables only.

No test calls the engine on a grid cell.
"""
import csv
import itertools
import json

import numpy as np
import pytest

from experiments.A00_engine.factorial_core import Side
from experiments.V13_step1 import regime as R
from experiments.V13_step1 import run


def side(p, d, dh, which, zero_dh=None, err=0.0):
    n = len(p)
    return Side(tuple(p), tuple(d), tuple(dh), tuple([0.0] * n), tuple(range(n)),
                dict(d=err, dh=err, zero_dh=tuple(zero_dh or [x == 0 for x in dh])))


def random_pair(rng, nA=6, nB=7):
    pA = rng.dirichlet(np.ones(nA)); pB = rng.dirichlet(np.ones(nB))
    dA = rng.uniform(0, 3, nA); dB = -rng.uniform(0, 3, nB)
    hA = np.where(rng.random(nA) < .3, 0.0, rng.uniform(0, 4, nA))
    hB = np.where(rng.random(nB) < .3, 0.0, -rng.uniform(0, 4, nB))
    return side(pA, dA, hA, 'A'), side(pB, dB, hB, 'B')


def brute(A, B):
    gm = 0.0; lens = {}; pairs = []
    for (pa, da, ha), (pb, db, hb) in itertools.product(zip(A.p, A.d, A.dh), zip(B.p, B.d, B.dh)):
        w, delta, hat = pa * pb, da + db, ha + hb
        gm += w * delta * (int(hat < 0) - int(delta < 0))
        pairs.append((w, delta, hat - delta))
    return gm, pairs


@pytest.mark.parametrize('seed', range(12))
def test_gm_s1_and_boundary_lens_match_enumeration(seed):
    rng = np.random.default_rng(seed)
    A, B = random_pair(rng)
    gm, pairs = brute(A, B)
    assert R.gm_s1(A, B) == pytest.approx(gm, abs=1e-12)
    for eps in (0.05, 0.4, 2.0):
        total = sum(w * e * e for w, delta, e in pairs if 0 < abs(delta) <= eps and e * delta < 0)
        window = sum(w for w, delta, _ in pairs if 0 < abs(delta) <= eps)
        lens, mass = R.boundary_lens(A, B, eps)
        assert lens == pytest.approx(total / (2 * eps), abs=1e-12)
        assert mass == pytest.approx(window, abs=1e-12)


def test_ties_stay_and_exaggeration_has_no_boundary_error():
    # Δ̂ = 2Δ exactly: errors vanish at the boundary and no state flips.
    A = side([.5, .5], [1.0, 2.0], [2.0, 4.0], 'A')
    B = side([.5, .5], [-1.0, -3.0], [-2.0, -6.0], 'B')
    assert R.gm_s1(A, B) == 0
    assert R.boundary_lens(A, B, 0.5)[0] == 0
    # exact tie Δ̂ = 0 with Δ < 0: M0 stays, oracle switches -> regret |Δ|.
    A = side([1.0], [1.0], [0.0], 'A'); B = side([1.0], [-1.5], [0.0], 'B')
    assert R.gm_s1(A, B) == pytest.approx(0.5)


def test_fluid_idle_masses_use_certificates_and_bounds():
    A = side([.2, .3, .5], [1, 1, 1], [0.0, 1e-13, 2.0], 'A', zero_dh=[True, False, False], err=1e-12)
    f = R.fluid_idle(A, 'A')
    assert f['I'] == pytest.approx(.5) and f['zero_mass'] == pytest.approx(.2)
    assert f['unresolved_mass'] == pytest.approx(.3) and not f['all_zero']
    B = side([.4, .6], [-1, -1], [0.0, 0.0], 'B')
    assert R.fluid_idle(B, 'B') == dict(I=0.0, zero_mass=1.0, unresolved_mass=0.0, all_zero=True)


def test_labels_and_predicted_reversal_rules():
    assert R.side_label(0, 0) == 'both_zero'
    assert R.side_label(.05, .20) == 'one_sided_B'
    assert R.side_label(.051, .9) == 'two_sided'
    assert R.side_label(.3, .01) == 'one_sided_A'
    assert R.predicted_reversal('0.3', 'one_sided_B') and R.predicted_reversal('0.7', 'one_sided_A')
    assert not R.predicted_reversal('0.7', 'one_sided_B') and not R.predicted_reversal('0.3', 'two_sided')
    assert R.observed_regime(1.0, 0.0) == 'blind'
    assert R.observed_regime(1.0, -0.5) == 'reverse' and R.observed_regime(-1.0, -2.0) == 'same'


def _cell(name, regime, pred=False, IA=.3, IB=.3, a0=False, b0=False, gm=1.0, lb=1.0, lm=1.0):
    return dict(cell=name, observed_regime=regime, predicted_reversal=pred, I_A=IA, I_B=IB,
                A_all_zero=a0, B_all_zero=b0, G_M_S1=gm, stakes=1.0, lens_boundary=lb, lens_mean=lm,
                **{f'lens_boundary_{e}': lb for e in R.EPS_SENSITIVITY})


def test_score_thresholds_on_synthetic_cells():
    same = [_cell(f'S{i}', 'same', gm=i, lb=i + .1 * (i % 2), lm=(7 * i) % 5) for i in range(1, 9)]
    cells = same + [_cell('B1', 'blind', IA=0, IB=0, a0=True, b0=True), _cell('R1', 'reverse', pred=True)]
    s = R.score(cells)
    assert (s['P_a']['verdict'], s['P_b']['verdict'], s['P_c']['verdict']) == ('PASS', 'PASS', 'PASS')
    many_false = cells + [_cell(f'F{i}', 'same', pred=True) for i in range(3)]
    assert R.score(many_false)['P_b']['verdict'] == 'FAIL'
    missed = [dict(c, predicted_reversal=False) if c['cell'] == 'R1' else c for c in cells]
    assert R.score(missed)['P_b']['verdict'] == 'FAIL'
    cancelling_blind = [dict(c, A_all_zero=False) if c['cell'] == 'B1' else c for c in cells]
    assert R.score(cancelling_blind)['P_a']['verdict'] == 'FAIL'
    no_gain = [dict(c, lens_mean=c['lens_boundary']) for c in cells]
    assert R.score(no_gain)['P_c']['verdict'] == 'FAIL'


def test_mean_lens_reproduces_reviewer_script_on_exposed_row():
    row = next(r for r in csv.DictReader(open('results/A04/20261027_01/main_final.csv')) if r['cell'] == 'M01')
    stakes = float(row['E_pos']) + float(row['E_neg'])
    assert R.mean_bias_lens(float(row['E_delta']), stakes, float(row['bias'])) == pytest.approx(0.3763, abs=1e-4)


def test_runner_refuses_non_main_cells_before_engine(monkeypatch):
    monkeypatch.setattr(run, 'side_table', lambda *a, **k: pytest.fail('engine reached'))
    monkeypatch.setattr(run, 'load_cell', lambda *a, **k: pytest.fail('cell loaded'))
    for cid in ('R01', 'R09', 'N01', 'P02'):
        with pytest.raises(PermissionError):
            run.cell_task((cid, 1.0))


def test_runner_has_no_threshold_or_cell_options(monkeypatch):
    monkeypatch.setattr(run, 'preflight', lambda: pytest.fail('preflight reached'))
    for option in (['--cells', 'R01'], ['--eps', '0.5'], ['--threshold', '0.1']):
        with pytest.raises(SystemExit):
            run.main(option)
