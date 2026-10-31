"""Synthetic/algebraic design checks only, never screen real discovery boxes."""
from copy import deepcopy
from fractions import Fraction as F
from math import comb
import json

import pytest

from experiments.P4_05_candidates import screen as S
from experiments.P4_05_candidates.identity_checks import fixtures
from experiments.R3R_06_cards import stats,verdict
from experiments.R3R_07_confirmation import power


def rules():
    return json.loads((S.ROOT/S.HERE/'screening_rules.json').read_text())


def row(i,*,meets=True,unresolved=False,undefined=False,region=0):
    return dict(id=f'TEST_{region}_{i}',key=['7','7','1',str(F(1,10)+F(i,10000)),str(2+region),'0'],
                Cref='0' if undefined else '10',G_S='1' if meets else '0',Gamma='-1' if meets else '0',
                d_normalized={'G_S':'0','Gamma':'0'},r1_ready=not unresolved,
                arithmetic_ready=True,CF_computed=False,source_kind='SYNTHETIC_TEST')


def test_n60_exact_thresholds_and_supplied_no_unresolved_power():
    assert stats.k_support(60,F(1,2),F(1,40))==39
    assert stats.k_reject(60,F(1,2),F(1,40))==21
    for p,two,one in [(F(3,5),.256,.257),(F(13,20),.558,.559),(F(7,10),.836,.838),
                      (F(3,4),.968,.970),(F(4,5),.996,.998)]:
        assert float(power.pass_power(60,p,F(1,5)))==pytest.approx(two,abs=.0006)
        assert float(verdict.plus_power(60,p))==pytest.approx(one,abs=.0006)
        assert power.robust_pass_power(60,p,F(1,5),0,0)==power.pass_power(60,p,F(1,5))


def test_robust_region_matches_independent_multinomial_and_actual_R4_R5():
    n=10;p=F(3,4);r=F(1,20);observed=F(0)
    for u in range(n+1):
        for m in range(n-u+1):
            f=n-u-m
            mass=F(comb(n,u)*comb(n-u,m))*r**u*((1-r)*p)**m*((1-r)*(1-p))**f
            score=verdict.gamma_verdict(dict(MEETS=m,FAILS=f,UNRESOLVED=u),
                                        pi0=F(1,2),alpha=F(1,40),n_min=1)
            if score['verdict']=='PASS':observed+=mass
    assert observed==power.robust_region_power(n,p,r,plus=True)


def test_R5_failure_is_direct_binomial_upper_tail():
    for r in (F(1,20),F(2,25)):
        expected=sum(F(comb(60,k))*r**k*(1-r)**(60-k) for k in range(7,61))
        assert power.r5_failure(60,r)==expected


def test_exact_identity_counterexamples_limit_double_dissociation_and_AB():
    examples=fixtures();both=examples['SV_and_MV_both_hold']
    assert both['GS']/both['Cref']>=F(1,100) and both['GM']/both['Cref']>=F(1,100)
    ab=examples['AB_without_SUB']
    assert ab['GS']/ab['Cref']>=F(1,100) and ab['GM']/ab['Cref']>=F(1,100)
    assert ab['Gamma']>0  # AB alone does not force substitution


def test_SUB_implication_and_forced_negative_control_exact_algebra():
    for r00 in range(5):
        for r01 in range(r00+1):
            for r10 in range(5):
                gs,gm,gamma=F(r00-r10),F(r00-r01),F(r10+r01-r00)
                assert gamma>=-min(gs,gm)
                if gamma<=-1:assert gs>=1 and gm>=1
                if gs<0:assert gamma>0
                if gm<F(1,100):assert gamma>F(-1,100)


def test_empty_and_full_boxes_preserve_counts():
    data=[row(i) for i in range(10)]
    empty=S.screen_box(data,{'h':['50','60']},rules(),set(),'SUB')
    full=S.screen_box(data,{},rules(),set(),'SUB')
    assert empty['decision']=='EMPTY' and empty['regions']['plus']['n']==0
    assert full['regions']['plus']['n']==10 and full['regions']['plus']['counts']['MEETS']==10
    assert full['decision']=='PASS_SCREEN'


def test_haircut_and_unresolved_enter_once_with_separate_rate():
    data=[row(i,meets=i<14,unresolved=i==19) for i in range(20)]
    result=S.screen_box(data,{},rules(),set(),'SUB');s=result['regions']['plus']
    assert s['p_cond']==F(14,19) and s['r_hat']==F(1,20)
    assert result['p_plus_plan']==F(14,19)-F(1,10)
    assert result['power']==power.robust_region_power(60,result['p_plus_plan'],F(1,20),plus=True)


def test_SV_minus_unresolved_is_measured_separately():
    plus=[row(i) for i in range(20)]
    minus=[row(i,meets=False,unresolved=i==19,region=1) for i in range(20)]
    result=S.screen_box(plus,{},rules(),set(),'SV',minus_rows=minus,minus_box={})
    assert result['regions']['plus']['r_hat']==0
    assert result['regions']['minus']['r_hat']==F(1,20)
    assert result['p_minus_plan']==F(1,5) and result['p_minus_observed_conditional']==0
    assert result['power']==power.robust_pass_power(60,F(9,10),F(1,5),0,F(1,20))


def test_no_resolved_or_undefined_never_imputes_success_or_zero():
    noresolved=S.screen_box([row(0,unresolved=True)],{},rules(),set(),'SUB')
    undefined=S.screen_box([row(0,undefined=True)],{},rules(),set(),'SUB')
    assert noresolved['decision']=='NO_RESOLVED' and noresolved['power'] is None
    assert undefined['decision']=='UNDEFINED_BLOCKED' and undefined['power'] is None


def test_SUB_uses_negative_gamma_boundary_and_R6():
    a=row(0);a['Gamma']='-1/10'
    assert S.native_label(a,'SUB')=='UNRESOLVED'
    a['Gamma']='-11/100';assert S.native_label(a,'SUB')=='MEETS'
    a['Gamma']='-9/100';assert S.native_label(a,'SUB')=='FAILS'
    a['Gamma']='1';assert S.native_label(a,'SUB')=='FAILS'


def test_CF_box_and_rows_are_refused_and_flags_are_literal():
    a=row(0);key=tuple(a['key'])
    with pytest.raises(RuntimeError,match='CF_COLLISION'):S.screen_box([a],{},rules(),{key},'SUB')
    with pytest.raises(RuntimeError,match='CF_COLLISION'):S.screen_box([],{},rules(),{key},'SUB')
    a['CF_computed']=0
    with pytest.raises(RuntimeError,match='literal False'):S.screen_box([a],{},rules(),set(),'SUB')


def test_duplicate_canonical_keys_pilot_rows_and_sealed_keys_refused():
    a=row(0);b=deepcopy(a);b['key'][0]='7.0'
    with pytest.raises(ValueError,match='duplicate normalized'):S.screen_box([a,b],{},rules(),set(),'SUB')
    a['source_kind']='PILOT'
    with pytest.raises(RuntimeError,match='pilot forbidden'):S.screen_box([a],{},rules(),set(),'SUB')
    a=row(0);a['key']=['15/2','8','1','3/5','4','0']
    with pytest.raises(RuntimeError,match='SEALED_R09_R10'):S.screen_box([a],{},rules(),set(),'SUB')


def test_three_boxes_count_empty_failures_and_do_not_double_count_result_files(tmp_path):
    for i in range(3):
        p=S.reserve_trial(tmp_path,'SUB',f'TESTBOX{i}',{})
        p.with_suffix('.result.json').write_text(json.dumps(dict(decision='EMPTY' if i==0 else 'FAIL_SCREEN')))
    with pytest.raises(RuntimeError,match='MAX_THREE_BOXES'):S.reserve_trial(tmp_path,'SUB','FOURTH',{})
    assert len(list((tmp_path/'SUB').glob('trial_[0-9][0-9].json')))==3


def test_no_real_boxes_or_engine_calls_in_current_preflight():
    status=S.preflight()
    assert status['status']=='BLOCKED_PART_B' and status['real_boxes_evaluated']==0
    assert not status['p_hat_computed'] and status['engine_calls']==0
    assert any('L4_3' in r for r in status['reasons']) and any('L4_4' in r for r in status['reasons'])


def test_real_entrypoint_refuses_before_reading_candidate_data():
    with pytest.raises(RuntimeError,match='PART_B_BLOCKED'):
        S.screen_registered('SUB','NONEXISTENT_BOX_FILE','NONEXISTENT_NATIVE_MANIFEST')


def test_registered_pipeline_with_mocked_readiness_and_synthetic_files(tmp_path,monkeypatch):
    """Exercise complete plumbing in tmp_path; never a real box or native run."""
    frozen_sealed=(S.ROOT/'experiments/P4_03_map_audit/sealed_scope.json').read_text()
    rr=rules()
    (tmp_path/S.HERE).mkdir(parents=True)
    p=tmp_path/'experiments/P4_03_map_audit/sealed_scope.json';p.parent.mkdir(parents=True);p.write_text(frozen_sealed)
    (tmp_path/S.HERE/'screening_rules.json').write_text(json.dumps(rr))
    data=[dict(row(i),source_kind='DISCOVERY_NATIVE') for i in range(10)]
    (tmp_path/'fixture_rows.json').write_text(json.dumps(data))
    (tmp_path/'fixture_manifest.json').write_text(json.dumps(dict(source_kind='DISCOVERY_NATIVE_BUNDLE_V1',
        source_sha256={'fixture_rows.json':S.sha(tmp_path/'fixture_rows.json')},rows={'plus':'fixture_rows.json'})))
    (tmp_path/S.HERE/'candidate_readiness.json').write_text(json.dumps(dict(candidates={'SUB':dict(native_manifest='fixture_manifest.json')})))
    (tmp_path/'fixture_box.json').write_text(json.dumps(dict(candidate='SUB',id='SYNTHETIC_BOX',
        status='REGISTERED_BEFORE_BOX_COUNTS',plus={})))
    monkeypatch.setattr(S,'ROOT',tmp_path)
    monkeypatch.setattr(S,'preflight',lambda:dict(status='READY',reasons=[]))
    monkeypatch.setattr(S,'rules_adopted',lambda:True)
    monkeypatch.setattr(S,'cf_keys',lambda:set())
    monkeypatch.setattr(S,'committed_json',lambda path:json.loads((tmp_path/path).read_text()))
    result=S.screen_registered('SUB','fixture_box.json','fixture_manifest.json')
    assert result['decision']=='PASS_SCREEN' and result['regions']['plus']['n']==10
    assert (tmp_path/S.OUT/'box_trials/SUB/trial_01.json').exists()
    assert (tmp_path/S.OUT/'box_trials/SUB/trial_01.result.json').exists()
