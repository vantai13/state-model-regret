"""Doan Van Tai — independent synthetic tests; no new grid D/outcomes."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path

import pytest

from experiments.A00_engine.factorial_core import Side
from experiments.A00_engine.evaluate import evaluate_sides
from experiments.A04_discovery.provenance import validate_config, verify_gate, validate_run_inputs, sha
from experiments.A04_discovery.validity import ledger_checks, physical_checks, pair
from experiments.A04_discovery.run import point_label, flatten, r04_diagnostic
from experiments.A04_discovery.score_card import score, claim_intervals
from experiments.A04_discovery.discovery import cheap_kill
from experiments.A03_card.grading import STANDS, FAILS, UNKNOWN
from tests.test_card_grading import row


def test_scope_rejects_heldout_and_changed_dt():
    cfg = json.loads(Path('experiments/A04_discovery/config.json').read_text())
    grid = json.loads(Path('notes/design/grid_v1_2.json').read_text())
    validate_config(cfg, grid)
    for key, value in [('main_ids', cfg['main_ids'] + ['R01']), ('pair_refinements', [2, 4]),
                       ('primary_dt_s', '1/480'), ('heldout_allowed', True)]:
        mutant = dict(cfg, **{key: value})
        with pytest.raises(PermissionError):
            validate_config(mutant, grid)


def test_gate_accepts_honest_waiver_not_fake_supervisor():
    gate = dict(v9_status='WAIVED_BY_AUTHOR', decision='DL-054', heldout_authorized=False)
    verify_gate(gate)
    for bad in ('WAIT', 'GVHD_APPROVED'):
        with pytest.raises(PermissionError):
            verify_gate(dict(gate, v9_status=bad))


def test_ledger_detects_oracle_and_model_bound_corruption():
    A = Side((F(1),), (F(1),), (F(2),), (F(10),), (0,))
    B = Side((F(1),), (F(-2),), (F(-1),), (F(10),), (0,))
    r = evaluate_sides(A, B, refinement=2, dt=F(1, 240))
    assert all(ledger_checks(r).values())
    bad = deepcopy(r); bad['L']['11'] += 10
    assert not ledger_checks(bad)['oracle_within_bounds']
    bad = deepcopy(r); bad['G']['G_M_S1'] += 10
    assert not ledger_checks(bad)['model_error_bound_pass']
    bad = deepcopy(r); bad['G']['V'] += 10
    assert not ledger_checks(bad)['identities_pass']


def test_physical_checks_use_real_bounds_and_component_signs():
    A = Side((1,), (1,), (1,), (10,), (0,))
    B = Side((1,), (-1,), (-1,), (10,), (0,))
    d = dict(W0={'St': (0,), 'Sw': (0,)}, W1={'St': (1,), 'Sw': (1,)},
             mean_idle_error=0., true_idle_error={'St': 0., 'Sw': 0.})
    assert physical_checks([A, B], [d, d])['jensen_within_bounds']
    bad = deepcopy(d); bad['W0']['Sw'] = (2,)
    assert not physical_checks([A, B], [bad, d])['jensen_within_bounds']


def test_pair_flags_are_retained_and_fv_is_diagnostic_only():
    c, f = row(1), row(2)
    f['G'] = {'F': 0, 'V': 1}; c['G'] = {'F': 0, 'V': 1}
    assert not pair(c, f)['pair_flag']
    f['G']['F'] = 99  # no six-contrast change: descriptive field only
    assert not pair(c, f)['pair_flag']
    f['intervals']['G_M'] = [1, 1]
    assert pair(c, f)['pair_flag']


def test_primary_and_equal_threshold_sensitivity_are_not_card_labels():
    assert point_label(.5, 100, .005) == 'equivalent_point'
    assert point_label(.6, 100, .005) == 'practical_positive'
    assert point_label(.6, 100, .01) == 'between_thresholds'
    assert point_label(1, 100, .01) == 'practical_positive'
    assert point_label(1, 100, .02) == 'between_thresholds'


def test_cheap_kill_all_cells_strict_upper_and_hold():
    def r(ref, value):
        x = row(ref, GS=0, GM=0, Gamma=0)
        x['intervals']['R00'] = [value, value]
        return x
    coarse = {'a': r(1, F(9, 10)), 'b': r(1, F(1, 2))}
    fine = {'a': r(2, F(9, 10)), 'b': r(2, F(1, 2))}
    assert cheap_kill(['a', 'b'], fine, coarse)['status'] == 'NARROW_BASELINE_GAIN'
    fine['a']['intervals']['R00'] = [1, 1]
    assert cheap_kill(['a', 'b'], fine, coarse)['status'] == 'NOT_CHEAP_KILLED'
    fine['a']['status'] = 'HOLD_PRECISION'
    assert cheap_kill(['a', 'b'], fine, coarse)['status'] == 'UNRESOLVED'
    assert cheap_kill([], fine, coarse)['status'] == 'UNRESOLVED'


def test_score_adapter_threshold_crossing_and_p6_parts():
    spec = {'predictions': {'P2': {'ids': ['p'], 'quantifier': 'all'},
          'P3': {'ids': ['p'], 'quantifier': 'all'}, 'P6': {'ids': ['p'], 'quantifier': 'all'},
          'P5': {'K_ids': ['k'], 'Q_ids': ['q']}}}
    fine = {'p': row(2, GS=1, V=1), 'k': row(2, GM=F(49, 100)), 'q': row(2, GM=1)}
    coarse = {'p': row(1, GS=1, V=1), 'k': row(1, GM=F(49, 100)), 'q': row(1, GM=1)}
    fine['k']['intervals']['G_M'] = [F(46, 100), F(52, 100)]
    grades, summary, detail = score(spec, dict(fine=fine, coarse=coarse))
    assert grades['P5']['verdict'] == UNKNOWN and grades['carry_to_A05_F']['carry']
    assert len([r for r in detail if r['prediction'] == 'P6']) == 2
    assert all(r['verdict'] == STANDS for r in detail if r['prediction'] == 'P6')
    assert next(r for r in summary if r['prediction'] == 'P5')['denominator_unit'] == 'branches'


def test_output_hash_gate_rejects_tamper_and_invalidity(tmp_path):
    (tmp_path / 'cells.csv').write_text('synthetic\n')
    status = dict(hard_failures=[], completed_levels=92)
    (tmp_path / 'validity_status.json').write_text(json.dumps(status))
    hashes = {p.name: sha(p) for p in tmp_path.iterdir()}
    (tmp_path / 'output_hashes.json').write_text(json.dumps(hashes))
    validate_run_inputs(tmp_path)
    (tmp_path / 'cells.csv').write_text('tampered\n')
    with pytest.raises(PermissionError):
        validate_run_inputs(tmp_path)


def test_r04_state_repair_identity_on_independent_rational_ledger():
    A = Side((F(1, 2), F(1, 2)), (F(1), F(3)), (F(2), F(4)), (F(10), F(20)), (0, 1))
    B = Side((F(1),), (F(-2),), (F(-1),), (F(10),), (0,))
    r = evaluate_sides(A, B, refinement=2, dt=F(1, 240))
    details = [dict(W1={'St': (F(1),)*len(s.p)}, W0={'St': (F(0),)*len(s.p)}) for s in (A, B)]
    d = r04_diagnostic(A, B, details, r)
    assert d['identity_residual'] == 0
    assert d['eligible_A05_feature'] is False


def test_flatten_keeps_cell_horizon_and_point_vs_interval_fields():
    A = Side((F(1),), (F(1),), (F(2),), (F(10),), (0,))
    B = Side((F(1),), (F(-2),), (F(-1),), (F(10),), (0,))
    r = evaluate_sides(A, B, refinement=2, dt=F(1, 240))
    record = dict(id='toy', kappa='1', eta='1/2', h='2', H_coarse=240,
                  yA='1', yB='1', lambdaA='7', label_2='candidate')
    out = flatten(record, 2, r, {}, {}, {'pair_flag': False}, 0)
    assert out['H'] == 480 and out['dt_s'] == '1/240'
    assert 'G_M_low' in out and 'G_M_verdict_010' in out and 'unresolved_D22' in out


def test_three_plots_on_synthetic_rows_only(tmp_path, monkeypatch):
    from experiments.A04_discovery import plots
    from experiments.A01_null_refinement.run import csv_write
    A = Side((F(1),), (F(1),), (F(2),), (F(10),), (0,))
    B = Side((F(1),), (F(-2),), (F(-1),), (F(10),), (0,))
    r = evaluate_sides(A, B, refinement=2, dt=F(1, 240))
    rows = []
    for i, group in enumerate(('core', 'spoke_A50', 'spoke_h2'), 1):
        record = dict(id=f'M{i:02}', group=group, kappa='1', alphaB='1/2', eta='1/2',
                      h='2' if i == 3 else '8', H_coarse=240 if i == 3 else 960,
                      yA='1', yB='1', lambdaA='7', label_2='candidate')
        rows.append(flatten(record, 2, r, {}, {}, {'pair_flag': False}, 0))
    csv_write(tmp_path / 'cells.csv', rows)
    monkeypatch.setattr(plots, 'require_score_commit', lambda out: 'SYNTHETIC-CHECKPOINT')
    assert plots.generate(tmp_path) == 'SYNTHETIC-CHECKPOINT'
    assert len(list((tmp_path / 'figures').iterdir())) == 6
