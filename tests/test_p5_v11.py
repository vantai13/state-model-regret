"""Phase 5 v1.1 (declared design revision): fake engine + saved rows only, no native panel call.

Each test guards one way the v1.1 verdict could be wrong or could quietly become a rescue.
"""
import copy
import json
from fractions import Fraction as F

import pytest

from experiments.P5_panel import run as V1
from experiments.P5_v11 import run as R
from experiments.P4_09_stationary.score import state_verdict

PANEL = R.panel10()
LEVELS = R.LEVELS


def saved(kind, lv):
    return copy.deepcopy(V1.saved_levels('P43_0379' if kind == 'DNM' else 'P44_025')[lv])


def seen(pid):
    return {lv: V1.load(V1.row_path(V1.OUT, pid, lv)) for lv in LEVELS}


def with_state_value(row, z):          # move L00 and L01 together: same-route gaps and definitions kept
    shift = F(z) * F(row['Cref']) - F(row['G_S_M1'])
    for k in ('00', '01'):
        row['losses'][k] = str(F(row['losses'][k]) + shift)
    L = {k: F(v) for k, v in row['losses'].items()}
    row.update({k: str(v) for k, v in dict(G_S=L['00'] - L['10'], G_M=L['00'] - L['01'], G_SM=L['00'] - L['11'],
               Gamma=L['10'] + L['01'] - L['00'] - L['11'], G_S_M1=L['01'] - L['11'], G_M_S1=L['10'] - L['11']).items()})


def noisy_L00(row):                    # the P5_02 pattern: only the S0xM0 route is imprecise
    for k in ('G_S', 'G_M', 'G_SM', 'Gamma'):
        row['normalized_error'][k] = '0.02'


def rows_of(kind, mutate=None):
    rows = {lv: saved(kind, lv) for lv in LEVELS}
    for r in rows.values():
        mutate and mutate(r)
    return rows


def fake(plan, calls, cpu=10):
    def call(point, lv, path, *, cpu_limit, **kw):
        calls.append((point['id'], lv))
        kind, mutate = plan.get(point['id'], ('MEETS', None))
        row = saved(kind, lv)
        row.update(id=point['id'], K=lv[0], ref=lv[1], parameters=point['parameters'], status='COMPLETED',
                   resources=dict(child_cpu_seconds=min(cpu,cpu_limit), wall_seconds=1., cpu_limit=cpu_limit, stop_error=None))
        if cpu > cpu_limit:
            row['status'] = 'RESOURCE_CPU'
        mutate and mutate(row)
        V1.write_once(path, row)
        return row
    return call


def run(out, plan=None, budget=28000, calls=None):
    calls = [] if calls is None else calls
    return R.run_panel(PANEL, call=fake(plan or {}, calls), out=out, budget=budget, controller_clock=lambda: 0.), calls


def test_V1_seen_points_U_under_v1_MEETS_under_v11_and_cref_choice(monkeypatch):
    for pid in R.SEEN:
        out = R.label(seen(pid))
        assert out['strict_v1_label'] == 'UNRESOLVED' and out['label'] == 'MEETS' and out['ready_HL2']
    monkeypatch.setattr(R, 'CREF_DELTA_GATES', True)            # the alternative author choice
    assert R.label(seen('P5_01'))['label'] == 'UNRESOLVED' and R.label(seen('P5_02'))['label'] == 'MEETS'


def test_V2_symmetry_noisy_L00_no_longer_blocks_a_FAIL():
    rows = rows_of('MEETS', lambda r: (with_state_value(r, F(3, 100)), noisy_L00(r)))
    out = R.label(rows)
    assert out['label'] == 'DOES_NOT_MEET' and out['strict_v1_label'] == 'UNRESOLVED'


def test_V3_noise_in_the_hypothesis_contrast_still_gives_U():
    out = R.label(rows_of('MEETS', lambda r: r['normalized_error'].update(G_S_M1='0.001')))
    assert out['label'] == 'UNRESOLVED' and any('arithmetic_width' in x for x in out['readiness_reasons'])


def test_V4_refinement_drift_of_the_contrast_gives_U():
    rows = rows_of('MEETS')
    with_state_value(rows[(640, 2)], F(1, 100))                 # coarse dt level moves z by 1 pp
    out = R.label(rows)
    assert out['label'] == 'UNRESOLVED' and 'R1_dt:G_S_M1' in out['readiness_reasons']


def test_V5_boundary_zone_unchanged():
    assert R.label(rows_of('MEETS', lambda r: with_state_value(r, R.THRESHOLD)))['label'] == 'UNRESOLVED'


def test_V6_order_and_N10_verdicts(tmp_path):
    _, calls = run(tmp_path)
    assert calls == [(p['id'], lv) for p in PANEL for lv in LEVELS] and calls[0][0] == 'P5_03'
    for labels, verdict in ((['MEETS'] * 9 + ['DOES_NOT_MEET'], 'PASS'), (['MEETS'] * 9 + ['UNRESOLVED'], 'PASS'),
                            (['MEETS'] * 8 + ['DOES_NOT_MEET', 'UNRESOLVED'], 'INCONCLUSIVE'),
                            (['MEETS'] * 8 + ['DOES_NOT_MEET'] * 2, 'FAIL')):
        assert state_verdict(labels, planned=10)['verdict'] == verdict


def test_V7_stops_and_strict_no_resume(tmp_path):
    u = ('MEETS', lambda r: with_state_value(r, R.THRESHOLD))
    result, _ = run(tmp_path / 'u', {'P5_04': u, 'P5_06': u})
    assert result['stop_reason'] == 'SECOND_U' and result['H_L1_v11']['verdict'] == 'INCONCLUSIVE'
    bug = ('MEETS', lambda r: r.update(Gamma=str(F(r['Gamma']) + F(r['Cref']) / 10)))
    result, _ = run(tmp_path / 'b', {'P5_05': bug})
    assert result['stop_reason'].startswith('BUG')
    with pytest.raises(RuntimeError, match='ALREADY_SCORED'):                 # never a second scoring
        R.run_panel(PANEL, call=fake({}, []), out=tmp_path / 'b', budget=28000, controller_clock=lambda: 0.)
    (tmp_path / 'c' / 'panel').mkdir(parents=True)                           # an interrupted attempt
    with pytest.raises(FileExistsError):                                     # is never resumed
        R.run_panel(PANEL, call=fake({}, []), out=tmp_path / 'c', budget=28000, controller_clock=lambda: 0.)


def test_V8_full_panel_scores_both_and_reports_sensitivity(tmp_path):
    result, _ = run(tmp_path, {'P5_08': ('DNM', None), 'P5_10': ('MEETS', noisy_L00)})
    assert result['stop_reason'] is None and result['H_L1_v11']['verdict'] == 'PASS'
    assert result['P5_08_label'] == 'DOES_NOT_MEET' and result['without_P5_08_descriptive']['MEETS'] == 9
    assert result['strict_v1_rule_sensitivity']['UNRESOLVED'] == 1          # P5_10 would be U under v1
    assert result['seen_points_v11_rule_descriptive'] == {'P5_01': 'MEETS', 'P5_02': 'MEETS'}
    assert result['H_L2_v11_exploratory']['reason'] == 'FIXED_PREDICTIONS_THREE_LEVEL_SENSITIVITY'


def test_V9_HL2_needs_ten_ready(tmp_path):
    result, _ = run(tmp_path, {'P5_07': ('MEETS', lambda r: r['normalized_error'].update(G_M_S1='0.001'))})
    assert result['H_L2_v11_exploratory']['reason'] == 'NEED_COMPLETE_READY_PANEL_AND_THREE_LEVELS'


def test_V10_rescore_and_tamper(tmp_path, monkeypatch):
    run(tmp_path, {'P5_09': ('DNM', None)})
    before={str(p):p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    monkeypatch.setattr(R,'launch',lambda *a,**kw:pytest.fail('rescore called engine'))
    assert R.rescore(tmp_path)
    assert before=={str(p):p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    doc = json.loads((tmp_path / 'summary.json').read_text())
    doc['points']['P5_09']['label'] = 'MEETS'
    (tmp_path / 'summary.json').write_text(json.dumps(doc))
    assert not R.rescore(tmp_path)


def test_V11_v1_is_untouched_and_still_rescores():
    for name in V1.SOURCES:
        assert (R.ROOT / name).read_bytes() == R.git('show', R.V1_RUNNER + ':' + name)
    assert V1.rescore()


@pytest.mark.parametrize('budget', [0, 1, 95])
def test_remaining_budget_covers_partial_point_and_no_retry(tmp_path, budget):
    result, calls = run(tmp_path, budget=budget)
    assert result['cpu_seconds'] <= budget
    assert result['stop_reason'] == 'BUDGET' or result['stop_reason'] == 'EXECUTION:RESOURCE_CPU'
    assert result['H_L1_v11']['verdict'] == 'INCONCLUSIVE'
    assert R.rescore(tmp_path)
    if budget <= V1.RESERVE:
        assert calls == []


def test_two_DNM_do_not_stop(tmp_path):
    result,calls=run(tmp_path, {'P5_03':('DNM',None),'P5_04':('DNM',None)})
    assert len(calls)==30 and result['stop_reason'] is None
    assert result['H_L1_v11']['verdict']=='FAIL' and R.rescore(tmp_path)


@pytest.mark.parametrize('field', ['calls','stop_reason','cpu_seconds','budget_CPU_seconds','cref_delta_gates'])
def test_rescore_verifies_call_ledger_stop_and_budget(tmp_path,field):
    run(tmp_path)
    path=tmp_path/'summary.json'
    doc=V1.load(path)
    if field=='calls': doc['calls'][0]['child_cpu_seconds']+=1
    elif field=='stop_reason': doc['stop_reason']='SECOND_U'
    elif field=='cpu_seconds': doc['cpu_seconds']=doc['budget_CPU_seconds']+1
    elif field=='budget_CPU_seconds': doc['budget_CPU_seconds']=1
    else: doc['cref_delta_gates']=True
    path.write_text(json.dumps(doc))
    assert not R.rescore(tmp_path)


def test_rescore_derives_points_from_raw_instead_of_trusting_summary(tmp_path):
    run(tmp_path)
    path=tmp_path/'summary.json';doc=V1.load(path)
    doc['points'].pop('P5_12')
    doc.update(R.score(doc['points'],PANEL))
    path.write_text(json.dumps(doc))
    assert not R.rescore(tmp_path)


def test_rescore_rejects_extra_missing_or_wrong_identity_rows(tmp_path):
    run(tmp_path)
    extra=R.row_path(tmp_path,'P5_01',R.MAIN)
    V1.write_once(extra,{})
    assert not R.rescore(tmp_path)
    extra.unlink()
    path=R.row_path(tmp_path,'P5_04',R.MAIN)
    row=V1.load(path);row['id']='WRONG';path.write_text(json.dumps(row))
    assert not R.rescore(tmp_path)
    path.unlink()
    assert not R.rescore(tmp_path)


def test_resource_and_unsaved_failures_replay_without_engine(tmp_path,monkeypatch):
    result,_=run(tmp_path/'resource',{'P5_04':('MEETS',lambda r:r.update(status='RESOURCE_WALL'))})
    assert result['stop_reason']=='EXECUTION:RESOURCE_WALL' and R.rescore(tmp_path/'resource')
    def interrupted(point,lv,path,**kw):
        path.parent.mkdir(parents=True,exist_ok=True);path.touch(exist_ok=False)
        raise KeyboardInterrupt('simulated after outcome before save')
    result=R.run_panel(PANEL,call=interrupted,out=tmp_path/'interrupt',budget=100,controller_clock=lambda:0.)
    assert result['stop_reason']=='EXECUTION:KeyboardInterrupt'
    monkeypatch.setattr(R,'launch',lambda *a,**kw:pytest.fail('rescore called native'))
    assert R.rescore(tmp_path/'interrupt')
    with pytest.raises(RuntimeError,match='ALREADY_SCORED'):
        R.run_panel(PANEL,call=interrupted,out=tmp_path/'interrupt')


@pytest.mark.parametrize('lv', LEVELS)
def test_nonpositive_denominator_is_not_accepted(lv):
    rows=rows_of('MEETS');rows[lv]['Cref']='0'
    assert R.scoped_readiness(rows,'G_S_M1')==[f'nonpositive_Cref:{lv}']


def test_worker_guards_precede_native(monkeypatch):
    monkeypatch.setattr(R.resource,'setrlimit',lambda *a:None)
    monkeypatch.setattr(R,'preflight',lambda **kw:(_ for _ in ()).throw(RuntimeError('GUARD_STOP')))
    monkeypatch.setattr(V1,'evaluate',lambda *a:pytest.fail('guard bypassed'))
    with pytest.raises(RuntimeError,match='GUARD_STOP'):
        R.worker('P5_03',R.MAIN,'panel',10,0)


def test_all_66_N10_label_counts_match_independent_rule():
    for m in range(11):
        for f in range(11-m):
            u=10-m-f
            labels=['MEETS']*m+['DOES_NOT_MEET']*f+['UNRESOLVED']*u
            expected='INCONCLUSIVE' if u>=2 else 'PASS' if m>=9 else 'FAIL' if m+u<=8 else 'INCONCLUSIVE'
            assert state_verdict(labels,planned=10)['verdict']==expected


def test_missing_gate_is_rejected(tmp_path,monkeypatch):
    note=tmp_path/'notes/02_decision_log.md';note.parent.mkdir();note.write_text('HOLD: no marker')
    monkeypatch.setattr(R,'ROOT',tmp_path)
    monkeypatch.setattr(R,'git',lambda *a:note.read_bytes())
    with pytest.raises(RuntimeError,match='V11_GATE_DECLARATION_REQUIRED'):
        R.gate_record()


def test_standalone_worker_needs_parent_reservation(tmp_path,monkeypatch):
    monkeypatch.setattr(R.resource,'setrlimit',lambda *a:None)
    monkeypatch.setattr(R,'preflight',lambda **kw:dict(panel=PANEL))
    monkeypatch.setattr(R,'OUT',tmp_path)
    monkeypatch.setattr(V1,'evaluate',lambda *a:pytest.fail('standalone native call'))
    with pytest.raises(RuntimeError,match='INVALID_PARENT_RESERVATION'):
        R.worker('P5_03',R.MAIN,'panel',10,0)


def test_launch_accounts_orphan_descendant_CPU(tmp_path,monkeypatch):
    import subprocess,sys
    monkeypatch.setattr(R,'preflight',lambda **kw:{})
    original=subprocess.Popen
    code="import subprocess,sys,time;subprocess.Popen([sys.executable,'-c','while True: pass']);time.sleep(20)"
    monkeypatch.setattr(R.subprocess,'Popen',lambda command,**kw:original([sys.executable,'-c',code],**kw))
    path=tmp_path/'row.json'
    row=R.launch(PANEL[0],R.MAIN,path,cpu_limit=.35,wall_limit=5)
    assert row['status']=='RESOURCE_CPU' and row['resources']['child_cpu_seconds']>=.25
    with pytest.raises(FileExistsError):
        R.launch(PANEL[0],R.MAIN,path,cpu_limit=.35,wall_limit=5)
