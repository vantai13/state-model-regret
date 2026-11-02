"""L5.1: discovery fixtures/fake engine only; no native panel outcomes.

Each case targets a verdict-changing wiring, stop, accounting or replay error.
The subprocess CPU test burns CPU in an unrelated synthetic child, not native.
"""
import copy
import hashlib
import json
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path

import pytest

from experiments.P5_panel import run as R

PANEL, LEVELS = R.check_frozen()


def saved(kind, level):
    return R.saved_levels('P43_0379' if kind == 'DNM' else 'P44_025')[level]


def with_state_value(row, z):
    """Move both old-state losses equally; keep same-route gaps and cost definitions."""
    c = F(row['Cref'])
    shift = F(z)*c-F(row['G_S_M1'])
    row['losses']['00'] = str(F(row['losses']['00'])+shift)
    row['losses']['01'] = str(F(row['losses']['01'])+shift)
    L = {k: F(v) for k, v in row['losses'].items()}
    row.update({k: str(v) for k, v in dict(
        G_S=L['00']-L['10'], G_M=L['00']-L['01'], G_SM=L['00']-L['11'],
        Gamma=L['10']+L['01']-L['00']-L['11'], G_S_M1=L['01']-L['11'], G_M_S1=L['10']-L['11']).items()})


def fake(plan, calls, cpu=10):
    def call(point, lv, path, *, cpu_limit, **kwargs):
        calls.append((point['id'], lv, cpu_limit))
        kind = plan.get(point['id'], 'MEETS')
        if kind == 'INTERRUPT':
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch(exist_ok=False)  # native may have returned before parent could save
            raise KeyboardInterrupt('simulated after outcome / before save')
        row = copy.deepcopy(saved(kind, lv))
        row.update(id=point['id'], K=lv[0], ref=lv[1], parameters=point['parameters'], status='COMPLETED')
        if kind == 'U':
            with_state_value(row, R.THRESHOLD)
        if kind == 'BUG':
            row['Gamma'] = str(F(row['Gamma'])+F(row['Cref'])/10)
        if kind == 'CRASH':
            row['status'] = 'EXECUTION_ERROR'
        if cpu > cpu_limit:
            row['status'] = 'RESOURCE_CPU'
        row['resources'] = dict(child_cpu_seconds=min(cpu, cpu_limit), wall_seconds=1., cpu_limit=cpu_limit, stop_error=None)
        R.write_once(path, row)
        return row
    return call


def run(out, plan=None, budget=R.BUDGET, calls=None):
    calls = [] if calls is None else calls
    result = R.run_panel(PANEL, LEVELS, call=fake(plan or {}, calls), out=out, budget=budget, controller_clock=lambda: 0.)
    return result, calls


def test_T1_native_api_has_no_status_or_parameters(monkeypatch, tmp_path):
    from experiments.R3R_14_lean_close import engine
    point = PANEL[0]
    row = copy.deepcopy(saved('MEETS', R.MAIN))
    for key in ('status', 'parameters'):
        row.pop(key, None)
    row.update(id=point['id'], K=640, ref=4)
    monkeypatch.setattr(engine, 'configure', lambda: None)
    def evaluate(*args):
        assert args == (point['id'], point['parameters'], 640, 4, tmp_path)
        return row
    monkeypatch.setattr(engine, 'evaluate_level', evaluate)
    got = R.evaluate(point, R.MAIN, tmp_path)
    assert got['status'] == 'COMPLETED' and got['parameters'] == point['parameters']
    assert 'status' not in row and 'parameters' not in row


def test_native_wrong_identity_is_not_masked(monkeypatch, tmp_path):
    from experiments.R3R_14_lean_close import engine
    monkeypatch.setattr(engine, 'configure', lambda: None)
    monkeypatch.setattr(engine, 'evaluate_level', lambda *args: dict(id='WRONG', K=640, ref=4, CF_computed=False))
    with pytest.raises(RuntimeError, match='ENGINE_ROW_IDENTITY'):
        R.evaluate(PANEL[0], R.MAIN, tmp_path)


def test_T2_order_and_completed_verdict(tmp_path):
    result, calls = run(tmp_path)
    assert [(pid, lv) for pid, lv, _ in calls] == [(p['id'], lv) for p in PANEL for lv in LEVELS]
    assert result['H_L1']['verdict'] == 'PASS' and result['stop_reason'] is None


def test_T3_strict_no_second_batch_even_if_a_saved_row_is_missing(tmp_path):
    run(tmp_path)
    R.row_path(tmp_path, 'P5_07', (320, 4)).unlink()
    calls = []
    with pytest.raises(RuntimeError, match='ALREADY_SCORED'):
        run(tmp_path, calls=calls)
    assert not calls
    with pytest.raises(FileExistsError):
        R.write_once(R.row_path(tmp_path, 'P5_01', R.MAIN), {})


def test_T4_second_U_stops_and_marks_unrun_points(tmp_path):
    result, calls = run(tmp_path, {'P5_02': 'U', 'P5_05': 'U'})
    assert result['stop_reason'] == 'SECOND_U' and len(calls) == 15
    assert result['H_L1']['verdict'] == 'INCONCLUSIVE'
    assert result['labels_by_id']['P5_06'] == 'NOT_RUN'
    assert R.rescore(tmp_path)


def test_second_DNM_does_not_stop(tmp_path):
    result, calls = run(tmp_path, {'P5_02': 'DNM', 'P5_03': 'DNM'})
    assert len(calls) == 36 and result['stop_reason'] is None
    assert result['H_L1']['verdict'] == 'FAIL'


def test_T5_algebra_bug_stops_before_next_level(tmp_path):
    result, calls = run(tmp_path, {'P5_04': 'BUG'})
    assert result['stop_reason'].startswith('BUG:') and len(calls) == 10
    assert result['H_L1']['verdict'] == 'INCONCLUSIVE' and R.rescore(tmp_path)


@pytest.mark.parametrize('budget', [0, 1, 95])
def test_T6_remaining_budget_caps_call_instead_of_overshooting(tmp_path, budget):
    result, calls = run(tmp_path, budget=budget)
    assert result['cpu_seconds'] <= budget
    assert result['stop_reason'] == 'BUDGET' or 'RESOURCE_CPU' in result['stop_reason']
    assert result['H_L1']['verdict'] == 'INCONCLUSIVE' and R.rescore(tmp_path)
    if budget <= R.RESERVE:
        assert not calls
    else:
        assert calls[-1][2] == 4  # 95 minus 90 consumed minus 1 reserved, not a 10s overrun


def test_T7_known_anchors_and_boundary_and_not_ready():
    assert R.label(R.saved_levels('P43_0379'))['label'] == 'DOES_NOT_MEET'
    assert R.label(R.saved_levels('P44_025'))['label'] == 'MEETS'
    rows = R.saved_levels('P44_025')
    for row in rows.values():
        with_state_value(row, R.THRESHOLD)
    got = R.label(rows)
    assert got['ready'] and got['label'] == 'UNRESOLVED'
    rows = R.saved_levels('P44_025')
    for row in rows.values():
        row['normalized_error'] = {key: '0.01' for key in row['normalized_error']}
    got = R.label(rows)
    assert not got['ready'] and got['label'] == 'UNRESOLVED'


@pytest.mark.parametrize('z, delta, expected', [
    ('0.003', '0.0005', 'MEETS'),
    ('0.004', '0.0012', 'UNRESOLVED'),
    ('0.0062', '0.0005', 'DOES_NOT_MEET'),
    ('0.0047', '0.0002', 'MEETS'),
    ('0.0047', '0.0004', 'UNRESOLVED'),
])
def test_threshold_examples_with_real_refinement_distance(z, delta, expected):
    rows = R.saved_levels('P44_025')
    for lv, row in rows.items():
        with_state_value(row, F(z) if lv == R.MAIN else F(z)-F(delta))
    result = R.label(rows)
    assert result['ready'] and result['label'] == expected


def test_cost_basis_catches_coherent_but_wrong_zero_contrasts():
    row = saved('DNM', R.MAIN)
    for key in ('G_S', 'G_M', 'G_SM', 'Gamma', 'G_S_M1', 'G_M_S1'):
        row[key] = '0'
    assert any(reason.startswith('COST_DEFINITION') for reason in R.bug_reasons(row))


def test_same_route_violation_is_a_bug_not_a_negative_result():
    row = saved('MEETS', R.MAIN)
    row['losses']['10'] = str(F(row['Cref']) * F(9, 10))
    assert any('same_route:10<11' in reason for reason in R.bug_reasons(row))


def test_negative_estimate_is_preserved_not_clamped():
    rows = R.saved_levels('P44_025')
    for row in rows.values():
        with_state_value(row, F(-1, 10**7))
    got = R.label(rows)
    assert got['label'] == 'MEETS' and F(got['S_abs']) < 0 and F(got['z']) < 0


@pytest.mark.parametrize('labels, expected', [
    (['MEETS']*11+['DOES_NOT_MEET'], 'PASS'),
    (['MEETS']*11+['UNRESOLVED'], 'PASS'),
    (['MEETS']*10+['DOES_NOT_MEET', 'UNRESOLVED'], 'INCONCLUSIVE'),
    (['MEETS']*10+['DOES_NOT_MEET']*2, 'FAIL'),
])
def test_T8_frozen_verdict(labels, expected):
    points = {p['id']: dict(label=v, ready=True, M_pct_by_level=['1', '1', '1']) for p, v in zip(PANEL, labels)}
    assert R.score(points, PANEL)['H_L1']['verdict'] == expected


def test_T9_HL2_requires_all_twelve_ready(tmp_path):
    result, _ = run(tmp_path, {'P5_03': 'CRASH'})
    assert result['H_L2_exploratory']['reason'] == 'NEED_COMPLETE_READY_PANEL_AND_THREE_LEVELS'
    assert R.rescore(tmp_path)


def test_T10_unsaved_interruption_never_runs_again(tmp_path):
    result, calls = run(tmp_path, {'P5_02': 'INTERRUPT'})
    assert result['H_L1']['verdict'] == 'INCONCLUSIVE' and len(calls) == 4
    assert R.row_path(tmp_path, 'P5_02', R.MAIN).exists()
    assert R.rescore(tmp_path)
    new_calls = []
    with pytest.raises(RuntimeError, match='ALREADY_SCORED'):
        run(tmp_path, calls=new_calls)
    assert not new_calls


def test_P5_08_descriptive_only(tmp_path):
    result, _ = run(tmp_path, {'P5_08': 'DNM'})
    assert result['P5_08_label'] == 'DOES_NOT_MEET'
    assert result['without_P5_08_descriptive']['MEETS'] == 11
    assert 'verdict' not in result['without_P5_08_descriptive']


def test_T11_read_only_rescore_and_tamper_detection(tmp_path, monkeypatch):
    run(tmp_path, {'P5_10': 'DNM'})
    before = {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    monkeypatch.setattr(R, 'launch', lambda *args, **kwargs: pytest.fail('rescore called engine'))
    assert R.rescore(tmp_path)
    assert before == {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    summary = R.load(tmp_path/'summary.json')
    summary['points']['P5_10']['label'] = 'MEETS'
    (tmp_path/'summary.json').write_text(json.dumps(summary))
    assert not R.rescore(tmp_path)


def test_rescore_detects_extra_unregistered_rows(tmp_path):
    run(tmp_path)
    R.write_once(tmp_path/'panel/P5_13/level_640_4.json', {})
    assert not R.rescore(tmp_path)


def test_guard_failure_precedes_engine_import(monkeypatch):
    monkeypatch.setattr(R.resource, 'setrlimit', lambda *args: None)
    monkeypatch.setattr(R, 'preflight', lambda **kwargs: (_ for _ in ()).throw(RuntimeError('FROZEN_CHANGED')))
    monkeypatch.setattr(R, 'evaluate', lambda *args: pytest.fail('guard did not stop evaluation'))
    with pytest.raises(RuntimeError, match='FROZEN_CHANGED'):
        R.worker('P5_01', R.MAIN, 'panel', 10)


def test_standalone_worker_cannot_bypass_parent_reservation(monkeypatch):
    monkeypatch.setattr(R.resource, 'setrlimit', lambda *args: None)
    monkeypatch.setattr(R, 'preflight', lambda **kwargs: dict(panel=PANEL, levels=LEVELS))
    monkeypatch.setattr(R, 'evaluate', lambda *args: pytest.fail('standalone native call'))
    with pytest.raises(RuntimeError, match='PARENT_RESERVATION_REQUIRED'):
        R.worker('P5_01', R.MAIN, 'panel', 10)


def test_gate_refuses_HOLD_without_native_call(tmp_path, monkeypatch):
    note = tmp_path/'notes/02_decision_log.md'
    note.parent.mkdir()
    text = '<!-- P5_GATE4 {"status":"HOLD","policy":"STRICT_NO_RETRY"} -->'
    note.write_text(text)
    monkeypatch.setattr(R, 'ROOT', tmp_path)
    monkeypatch.setattr(R, 'git', lambda *args: text.encode())
    with pytest.raises(RuntimeError, match='GATE4_NOT_GO'):
        R.gate_record()


def test_subprocess_descendant_cpu_cap_and_no_repeat(tmp_path, monkeypatch):
    monkeypatch.setattr(R, 'preflight', lambda **kwargs: {})
    original = subprocess.Popen
    code = "import subprocess,sys,time;subprocess.Popen([sys.executable,'-c','while True: pass']);time.sleep(20)"
    monkeypatch.setattr(R.subprocess, 'Popen', lambda command, **kwargs: original([sys.executable, '-c', code], **kwargs))
    point, path = PANEL[0], tmp_path/'row.json'
    row = R.launch(point, R.MAIN, path, cpu_limit=.35, wall_limit=5)
    assert row['status'] == 'RESOURCE_CPU'
    assert row['resources']['child_cpu_seconds'] >= .25  # includes the orphaned busy child
    with pytest.raises(FileExistsError):
        R.launch(point, R.MAIN, path, cpu_limit=.35, wall_limit=5)
