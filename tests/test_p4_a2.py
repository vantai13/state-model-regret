"""A2 tests: chỉ đọc artifact đã commit + hàm thuần. Không gọi engine."""
from fractions import Fraction as F
import json
import os

import pytest

from experiments.P4_03_map_audit.common import ROOT
from experiments.P4_A2 import diagnose_l44 as D
from experiments.P4_A2 import probe as P

A1 = 'results/lessons/l4_4/a1'


def rd(path):
    return json.loads((ROOT / path).read_text())


def a1_points():
    for cid in sorted(os.listdir(ROOT / A1 / 'native')):
        rows = {lv: rd(f'{A1}/native/{cid}/level_{lv[0]}_{lv[1]}.json') for lv in ((640, 4), (320, 4), (640, 2))}
        yield cid, rd(f'{A1}/native/{cid}/comparison.json'), rows


def test_diagnosis_one_failing_rho_per_point_only_old_route_cell():
    failing = {}
    for cid, cmp, rows in a1_points():
        named = {'main': rows[(640, 4)], 'K': rows[(320, 4)], 'dt': rows[(640, 2)]}
        recs = [D.pair_record(named, i) for i in range(5)]
        bad = [r for r in recs if r['failure']]
        assert bool(bad) == (cmp['status'] == 'NOT_READY')
        for r in bad:
            assert set(r['fields_over_tol']) <= {'L00', 'GS_theta'}       # không bao giờ L10 / deltaL10
        if bad:
            failing[cid] = [r['rho'] for r in bad]
            assert rows[(640, 4)]['parameters'][:2] == ['7', '6']            # cùng một góc lambdaA=7, lambdaB=6
    assert len(failing) == 8 and all(len(v) == 1 for v in failing.values())


def test_step0_of_ladder_reproduces_A1_readiness_exactly():
    rhos = rd('experiments/P4_A1/runs/L44_A1/prereg.json')['rho']
    for cid, cmp, rows in a1_points():
        s = P.step_status(rows, (640, 4), rhos)
        assert s['point_ready'] == (cmp['status'] == 'PASS')
        assert s['row_reasons'] + s['baseline_reasons'] == cmp['readiness_reasons']


def test_rho_parsing():
    assert P.rho_of('baseline_arithmetic:(640, 4):1/100') == '1/100'
    assert P.rho_of('baseline_R1:1/50:GS_theta') == '1/50'
    assert P.rho_of('R1_dt:cref=0.003') is None


def test_classification_thresholds():
    d = dict(ladder_resolves_if_at_least=7, ladder_fails_if_at_most=4, branch_if_ladder_fails='B2_NARROW')
    assert P.classify(8, 8, d) == 'LADDER_RESOLVES' and P.classify(7, 8, d) == 'LADDER_RESOLVES'
    assert P.classify(5, 8, d).startswith('INCONCLUSIVE') and P.classify(6, 8, d).startswith('INCONCLUSIVE')
    assert P.classify(4, 8, d) == 'B2_NARROW' and P.classify(0, 8, d) == 'B2_NARROW'


def test_ladder_is_the_frozen_scorer_ladder_with_contract_neighbours():
    from experiments.R3R_14_lean_close.frame_v2 import escalation_plan
    assert [step[0] for step in P.LADDER] == escalation_plan(640, 4)
    for main, k_nb, dt_nb in P.LADDER:
        assert k_nb == (main[0] // 2, main[1]) and dt_nb == (main[0], main[1] // 2)
    assert P.all_levels()[:3] == [(640, 4), (320, 4), (640, 2)] and len(P.all_levels()) == 7


def test_draft_cannot_freeze(tmp_path):
    from experiments.P4_A1.config import check_author, load
    draft=load(P.RUN / 'author_choices.json');draft['status']='DRAFT_AWAITING_AUTHOR'
    path=tmp_path/'draft.json';path.write_text(json.dumps(draft))
    with pytest.raises(RuntimeError, match='AUTHOR_NOT_ADOPTED'):
        check_author(path)


def test_control_is_exact_zero_action_and_not_cf():
    from experiments.P4_03_map_audit.common import canonical, cf_keys
    c = P.CONTROL
    assert F(c['parameters'][3]) == 0 and canonical(c['parameters']) == tuple(c['key'])
    assert tuple(c['key']) not in cf_keys()


@pytest.mark.parametrize('field', ['losses','cost_error','normalized_error','baseline_L10','baseline_error10'])
def test_replay_detects_corruption_beyond_supplied_L00_only_comparison(field):
    from copy import deepcopy
    from experiments.P4_A2.guards import reproduction
    old=rd(f'{A1}/native/P44_000/level_640_4.json');new=deepcopy(old)
    if field.startswith('baseline_'):
        key=field[len('baseline_'):];new['baseline'][0][key]=str(F(new['baseline'][0][key])+F(1,10**6))
    else:
        key='G_S' if field=='normalized_error' else '10'
        new[field][key]=str(F(new[field][key])+F(1,10**6))
    r=reproduction(old,new)
    assert not r['saved_numerical_fields_equal'] and not r['reparsed_significant_bits_equal']


def test_replay_ignores_timing_but_checks_saved_significant_bits():
    from copy import deepcopy
    from experiments.P4_A2.guards import reproduction
    old=rd(f'{A1}/native/P44_000/level_640_4.json');new=deepcopy(old)
    new['call_cpu_seconds']=999999;new['wall_seconds']=999999
    assert reproduction(old,new)['reparsed_significant_bits_equal']


@pytest.mark.parametrize('field,bad', [('K',1280),('ref',8),('parameters',[]),('CF_computed',0),
                                       ('a2_prereg_sha256','foreign'),('a1_bug_reasons',['synthetic_bug'])])
def test_resume_or_decision_rejects_poisoned_row_metadata(field,bad):
    from copy import deepcopy
    from experiments.P4_A2.guards import validate_row
    row=deepcopy(rd(f'{A1}/native/P44_000/level_640_4.json'))
    row['a2_prereg_sha256']='fixture';case={'id':row['id'],'parameters':row['parameters']}
    row[field]=bad
    with pytest.raises(RuntimeError):validate_row(row,case,(640,4),'fixture',[b['rho'] for b in row['baseline']])


@pytest.mark.parametrize('status,ids', [('HOLD',list(range(8))),('PASS',list(range(7)))])
def test_decide_refuses_stopped_or_partial_run_before_loading_any_physics(monkeypatch,status,ids):
    cfg={'output':'fixture','targets':[{'id':i} for i in range(8)]}
    monkeypatch.setattr(P,'fingerprint',lambda:'fp')
    monkeypatch.setattr(P,'load',lambda _:dict(status=status,completed_ids=ids,a2_prereg_sha256='fp'))
    def forbidden(*a):raise AssertionError('must reject before control/raw rows')
    monkeypatch.setattr(P,'verify_control',forbidden)
    with pytest.raises(RuntimeError,match='RUN_NOT_PASS|RUN_TARGET_SET_INCOMPLETE'):P.build_decision(cfg)


@pytest.mark.parametrize('patch', [dict(ladder_resolves_if_at_least=9),dict(ladder_fails_if_at_most=7),
                                   dict(branch_if_ladder_fails='unregistered'),dict(cpu_cap_hours=0)])
def test_invalid_predeclared_thresholds_or_budget_are_rejected(patch):
    from experiments.P4_A2.guards import validate_decisions
    d=dict(ladder_resolves_if_at_least=7,ladder_fails_if_at_most=4,
           branch_if_ladder_fails='B1_CLAIM_LEVEL_ROBUSTNESS',cpu_cap_hours=3)
    d.update(patch)
    with pytest.raises(RuntimeError):validate_decisions(d)


def test_failed_control_is_nonzero_and_cannot_be_reported_as_pass(tmp_path,monkeypatch):
    cfg={'output':'fixture','control':{'id':'CONTROL'}}
    monkeypatch.setattr(P,'ROOT',tmp_path);monkeypatch.setattr(P,'verify',lambda:cfg)
    monkeypatch.setattr(P,'fingerprint',lambda:'fp');monkeypatch.setattr(P,'launch',lambda *a:1)
    assert P.run('control')==1
    r=json.loads((tmp_path/'fixture/control_summary.json').read_text())
    assert r['status']=='HOLD_EXECUTION_OR_BUG'


def test_changed_cached_row_hash_blocks_reuse_before_readiness(tmp_path,monkeypatch):
    cfg={'output':'fixture','ladder':[[list(lv) for lv in step] for step in P.LADDER]};case={'id':'FIXTURE'}
    monkeypatch.setattr(P,'ROOT',tmp_path);monkeypatch.setattr(P,'fingerprint',lambda:'fp')
    monkeypatch.setattr(P,'load',lambda p:json.loads((tmp_path/p).read_text()))
    files=P.point_files(cfg,case,False);folder=files[0][1].parent;folder.mkdir(parents=True)
    for _,p in files:p.write_text('{}')
    receipt=dict(id=case['id'],status='COMPLETED',a2_prereg_sha256='fp',
                 rows_sha256={str(p.relative_to(tmp_path)):'wrong' for _,p in files})
    (folder/'point_summary.json').write_text(json.dumps(receipt))
    with pytest.raises(RuntimeError,match='POINT_ROW_HASH_CHANGED'):P.verify_point(cfg,case)


def test_full_plumbing_and_resume_in_tmp_without_research_engine(tmp_path,monkeypatch):
    """Synthetic plumbing only: copied fixture values are not numerical probe results."""
    from copy import deepcopy
    from experiments.P4_A1 import evaluate as E
    a1=rd('experiments/P4_A1/runs/L44_A1/prereg.json')
    bad=[cid for cid,cmp,rows in a1_points() if cmp['status']=='NOT_READY']
    targets=[dict(id=c['id'],parameters=c['parameters'],key=c['key'],target_rho=['0']) for c in a1['cases'] if c['id'] in bad]
    cfg=dict(output='fixture_probe',targets=targets,control=P.CONTROL,rho=a1['rho'],
             ladder=[[list(lv) for lv in step] for step in P.LADDER],
             resources=dict(case_cpu_seconds=3600,address_space_bytes=3*1024**3),
             decisions=dict(ladder_resolves_if_at_least=7,ladder_fails_if_at_most=4,
                            branch_if_ladder_fails='B1_CLAIM_LEVEL_ROBUSTNESS',cpu_cap_hours=3))
    templates={}
    for t in targets:
        for lv in P.LADDER[0]:
            relative=f'{A1}/native/{t["id"]}/level_{lv[0]}_{lv[1]}.json'
            r=rd(relative);templates[t['id'],lv]=r
            p=tmp_path/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(r))
    control=rd(f'{A1}/controls/A1_CONTROL_U0/level_640_4.json')
    monkeypatch.setattr(P,'ROOT',tmp_path);monkeypatch.setattr(P,'verify',lambda:cfg)
    monkeypatch.setattr(P,'fingerprint',lambda:'fixture')
    monkeypatch.setattr(P,'load',lambda p:json.loads((tmp_path/p).read_text()))
    monkeypatch.setattr(P,'check_case',lambda *a:None)
    monkeypatch.setattr(P.resource,'setrlimit',lambda *a:None)
    calls=[]
    def fake(case,lv,cache,rhos):
        calls.append((case['id'],lv))
        r=deepcopy(control if case['id']==P.CONTROL['id'] else templates[case['id'],lv if lv in P.LADDER[0] else (640,4)])
        r.update(id=case['id'],K=lv[0],ref=lv[1],dt=str(F(1,120*lv[1])),call_cpu_seconds=1.)
        return r
    monkeypatch.setattr(E,'evaluate_level',fake)
    monkeypatch.setattr(P,'launch',lambda cid,c:P.worker(cid))
    assert P.run('control')==0 and P.run('run')==0
    assert len(calls)==57
    assert P.run('run')==0 and len(calls)==57  # resume never evaluates a completed level again
    decision=P.build_decision(cfg)
    assert decision['n_targets']==8 and decision['replay_rows_confirmed']==24
    P.decide()
    assert json.loads((tmp_path/'fixture_probe/decision.json').read_text())==decision
