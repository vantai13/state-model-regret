"""DL-134 probe: fixed points, signed-G_S readiness, pre-declared decision. No engine calls."""
import copy
import json
from fractions import Fraction as F

import pytest

from experiments.P6_band import probe as B
from experiments.P6_band import select_dii as S

ROOT = S.Path(__file__).resolve().parents[1]


def saved(path):
    rows = {lv: json.loads((ROOT/path/f'level_{lv[0]}_{lv[1]}.json').read_text()) for lv in B.LEVELS}
    for lv, r in rows.items():
        r.setdefault('resources', {})['cpu_seconds'] = 1.0
    return rows


def test_contract_constants_are_the_frozen_ones():
    from experiments.R3R_05_contract.rules import TOL_NUM, EPS_E
    from experiments.R3R_14_lean_close.checks import ARITH_MAX
    assert (B.TOL_NUM, B.EPS_E, B.ARITH_MAX) == (TOL_NUM, EPS_E, ARITH_MAX)


def test_probe_points_fixed_offpanel_and_nondiscriminating():
    points = B.probe_points(S.load_rows(ROOT), B.load_panel(ROOT))
    assert tuple(p['scan_id'] for p in points) == B.EXPECTED_PROBES
    assert [p['numerics_class'] for p in points] == [['8', '1/10'], ['16', '1/10'], ['16', '1/5']]
    for p in points:
        a, b, k, eta, h, c = map(F, p['parameters'])
        assert c == F(1, 16) and eta == F(3, 4)          # u = 3/2 at all three bases


@pytest.mark.parametrize('anchor,sign', [('P43_0021', -1), ('P43_0018', +1)])
def test_exposed_anchors_of_both_signs_are_ready(anchor, sign):
    rows = saved(f'results/lessons/l4_3/a1_sv/native/{anchor}')
    assert B.gs_readiness(rows) == []
    z = F(rows[B.MAIN]['G_S'])/F(rows[B.MAIN]['Cref'])
    assert z*sign > B.EPS_E                               # a NEGATIVE G_S must stay ready
    summary = B.numerics_summary(rows)
    assert summary['ready']
    assert set(summary) == {'ready', 'reasons', 'd_pp', 'width_pp', 'R1_delta_pp',
                            'uncertain_action_mass', 'cpu_seconds'}      # no z, no G_S: sealed


def test_long_horizon_exposed_row_fails_on_width():
    rows = saved('results/phase5_v1_1/panel/P5_03')       # h=32, kappa=1/20: known wide L00
    assert any(r.startswith('width') for r in B.gs_readiness(rows))


def synthetic(gs_fine, gs_coarse, width=F(1, 10**6)):
    base = dict(Cref='10', normalized_error={'G_S': str(width)})
    rows = {lv: dict(base, G_S=str(gs_coarse)) for lv in B.LEVELS[1:]}
    rows[B.MAIN] = dict(base, G_S=str(gs_fine))
    return rows


def test_R1_width_and_sign_flip_reasons():
    assert B.gs_readiness(synthetic(F(-2, 10), F(-2, 10))) == []
    assert 'R1_K' in B.gs_readiness(synthetic(F(-2, 10), F(-1, 10)))
    flips = B.gs_readiness(synthetic(F(-1, 10), F(1, 10)))
    assert 'sign_flip_K' in flips and 'sign_flip_dt' in flips
    assert any(r.startswith('width') for r in B.gs_readiness(synthetic(0, 0, width=F(1, 1000))))


def fake(panel_classes, ready, cpu3):
    points = [dict(id=f'P{i}', numerics_class=list(c)) for i, c in enumerate(panel_classes)]
    results = {p['id']: dict(ready=ready[i], d_pp=0.01, cpu_seconds={'a': cpu3[i]})
               for i, p in enumerate(points)}
    return points, results


def panel(n_per_class):
    rows, i = [], 0
    for cls, n in n_per_class.items():
        for _ in range(n):
            i += 1
            common = dict(base_id=f'B{i:03d}', h=cls[0], kappa=cls[1], z_K640='-2')
            rows += [dict(common, role='D', id=f'B{i:03d}C05'), dict(common, role='twin', id=f'B{i:03d}C00')]
    rows.append(dict(role='A-', id='B999C00', base_id='B999', h='8', kappa='1/10', z_K640='-5'))
    return rows


CLASSES = {('8', '1/10'): 3, ('16', '1/10'): 7, ('16', '1/5'): 3}


@pytest.mark.parametrize('ready,cpu3,status,plan', [
    ((True, True, True), (60, 60, 60), 'PASS', 'ALL_MEMBERS'),
    ((False, True, True), (60, 60, 60), 'PASS_REDUCED', 'ALL_MEMBERS'),
    ((True, False, True), (60, 60, 60), 'STOP_NUMERICS', None),
    ((True, True, True), (200, 200, 200), 'PASS', 'DROP_TWINS'),
    ((True, True, True), (400, 400, 400), 'HOLD_BUDGET', None),
])
def test_predeclared_decision(ready, cpu3, status, plan):
    points, results = fake(list(CLASSES), ready, cpu3)
    out = B.decide(points, results, panel(CLASSES))
    assert out['status'] == status and out.get('plan') == plan


def test_readiness_threshold_edges_and_normalizer():
    rows = synthetic(0, 0, width=B.ARITH_MAX)
    assert B.gs_readiness(rows) == []
    rows[B.MAIN]['normalized_error'] = {'G_S': str(B.ARITH_MAX+F(1,10**9))}
    assert B.gs_readiness(rows)
    rows[B.MAIN]['Cref'] = '0'
    assert any(r.startswith('nonpositive_Cref') for r in B.gs_readiness(rows))


def test_no_negative_contrast_gate_mutant():
    rows = saved('results/lessons/l4_3/a1_sv/native/P43_0021')
    assert B.gs_readiness(rows) == []
    assert F(rows[B.MAIN]['G_S'])/F(rows[B.MAIN]['Cref']) < -B.TOL_NUM


def test_sealed_summary_has_no_signed_outcome_keys():
    rows = saved('results/lessons/l4_3/a1_sv/native/P43_0021')
    report = B.numerics_summary(rows)
    def visit(value):
        if isinstance(value,dict):
            assert not {'G_S','z','z_pct','losses','label'} & value.keys()
            for v in value.values():visit(v)
    visit(report)


def test_reservation_requires_parent_fd(tmp_path):
    from pathlib import Path
    with pytest.raises(RuntimeError, match='PARENT_RESERVATION_REQUIRED'):
        B.reservation(ROOT, {}, B.MAIN, None, tmp_path/'row.json')


def test_compute_budget_stop_never_calls_engine(tmp_path):
    points=B.probe_points(S.load_rows(ROOT),B.load_panel(ROOT))
    result=B.compute(ROOT,points,B.load_panel(ROOT),out=tmp_path,
                     used_cpu=lambda:B.PROBE_CAP,
                     call=lambda *a,**kw:pytest.fail('budget-exhausted call'))
    assert result['status']=='RESOURCE_CPU' and result['numerics']=={}


def test_launcher_rejects_wrong_identity_before_overwriting(tmp_path,monkeypatch):
    from experiments.P5_panel import run as V1
    class FakeProcess:
        pid=999999999
        def __init__(self,cmd,**kwargs):
            kwargs['stdout'].write(json.dumps(dict(id='WRONG',K=640,ref=4,
                parameters=['bad'],status='COMPLETED',CF_computed=False)).encode())
        def poll(self):return 0
        def wait(self):return 0
    monkeypatch.setattr(B.subprocess,'Popen',FakeProcess)
    monkeypatch.setattr(V1,'reap_group',lambda proc:None)
    point=dict(id='P6B_FAKE',parameters=['7','8','1/10','1/2','8','1/16'])
    path=tmp_path/'wrong.json'
    result=B.launch(point,B.MAIN,path,cpu_limit=10)
    assert result['status']=='EXECUTION_ERROR'
    assert json.loads(path.read_text())['status']=='EXECUTION_ERROR'
    with pytest.raises(FileExistsError):B.launch(point,B.MAIN,path,cpu_limit=10)


def test_worker_without_reservation_cannot_evaluate(tmp_path,monkeypatch):
    from experiments.P5_panel import run as V1
    point=dict(id='P6B_FAKE',parameters=['7','8','1/10','1/2','8','1/16'])
    monkeypatch.setattr(B,'preflight',lambda root:(V1,[point],[]))
    monkeypatch.setattr(B.resource,'setrlimit',lambda *args:None)
    monkeypatch.setattr(V1,'evaluate',lambda *a:pytest.fail('unauthorized worker evaluated'))
    with pytest.raises(RuntimeError,match='PARENT_RESERVATION_REQUIRED'):
        B.worker('probe',point['id'],640,4,None,10)
