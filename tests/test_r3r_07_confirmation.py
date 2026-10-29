"""Doan Van Tai — synthetic/test-seed verification only; never invoke a research engine."""
from copy import deepcopy
from fractions import Fraction as F
import json
import math

import pytest

from experiments.R3R_06_cards import verify_cards as VC
from experiments.R3R_06_cards import stats
from experiments.R3R_07_confirmation import common as C, sampler as S, power as P, score as SC
from experiments.R3R_07_confirmation import gates, frame, run, inventory as I
from experiments.R3R_05_contract.schema import canonical, validate


@pytest.mark.parametrize('mutation',['empty','only_stats','missing','extra','invalid_hash','bad_schema','bad_commit','not_object','duplicate_key','malformed'])
def test_card_receipt_requires_complete_manifest(tmp_path,monkeypatch,mutation):
    rec=json.loads(VC.RECEIPT.read_text())
    if mutation=='empty': rec['sha256']={}
    elif mutation=='only_stats': rec['sha256']={VC.FROZEN[7]:rec['sha256'][VC.FROZEN[7]]}
    elif mutation=='missing': rec['sha256'].pop(VC.FROZEN[1])
    elif mutation=='extra': rec['sha256']['unexpected']='0'*64
    elif mutation=='invalid_hash': rec['sha256'][VC.FROZEN[1]]=None
    elif mutation=='bad_schema': rec['schema_version']=99
    elif mutation=='bad_commit': rec['card_commit']='HEAD'
    elif mutation=='not_object': rec=[]
    raw=json.dumps(rec)
    if mutation=='duplicate_key': raw=raw[:-1]+',"sha256":{}}'
    elif mutation=='malformed': raw='{'
    fake=tmp_path/'receipt.json'; fake.write_text(raw)
    monkeypatch.setattr(VC,'RECEIPT',fake)
    assert VC.verify()['status']=='FAIL'


def test_real_receipt_and_frozen_card_unchanged():
    assert VC.verify()['status']=='PASS'
    assert VC.verify()['files']==10
    assert C.verified_card()['status']=='FROZEN'


def test_half_even_rounding_and_reject_unknown_law():
    assert S.snap(F(2001,2000),F(1,1000))==1
    assert S.snap(F(2003,2000),F(1,1000))==F(1002,1000)
    import numpy as np
    with pytest.raises(ValueError): S.draw(np.random.default_rng(C.TEST_ROOT),'1','2','typo',F(1,1000))


def test_sampler_reproducible_prefix_and_primary_validity():
    card=C.verified_card()
    for name in C.ORDER:
        a,_=S.sample_region(C.TEST_ROOT,name,card['regions'][name],40,set(),purpose='TEST_ONLY_NO_ENGINE')
        b,_=S.sample_region(C.TEST_ROOT,name,card['regions'][name],60,set(),purpose='TEST_ONLY_NO_ENGINE')
        assert a==b[:40]
        for row in b:
            validate(row['regime'],primary=True)
            assert S.inside(row['regime'],card['regions'][name])
            assert all(F(row['regime'][k])%step==0 for k,step in S.STEP.items())


def test_bnd_cut_does_not_shift_SH_and_exact_collision_redraw():
    card=C.verified_card()
    a,_=S.sample_all(C.TEST_ROOT,card,30,15,set(),purpose='TEST_ONLY_NO_ENGINE')
    b,_=S.sample_all(C.TEST_ROOT,card,30,0,set(),purpose='TEST_ONLY_NO_ENGINE')
    for name in ('SH+A','SH-ii'):
        assert [x for x in a if x['origin_region']==name]==[x for x in b if x['origin_region']==name]
    first,_=S.sample_region(C.TEST_ROOT,'MV+A',card['regions']['MV+A'],1,set(),purpose='TEST_ONLY_NO_ENGINE')
    key=canonical(first[0]['regime'])
    second,redraws=S.sample_region(C.TEST_ROOT,'MV+A',card['regions']['MV+A'],2,{key},purpose='TEST_ONLY_NO_ENGINE')
    assert redraws==1 and all(canonical(x['regime'])!=key for x in second)
    with pytest.raises(ValueError,match='cap exceeded'):
        S.sample_region(C.TEST_ROOT,'MV+A',card['regions']['MV+A'],1,{key},purpose='TEST_ONLY_NO_ENGINE',max_redraw=0)


def test_sampler_10000_log_uniform_draws():
    spec=C.verified_card()['regions']['MV+A']
    rows,_=S.sample_region(C.TEST_ROOT,'MV+A',spec,10000,set(),purpose='TEST_ONLY_NO_ENGINE')
    observed=sum(F(r['regime']['kappa'])<F(1,5) for r in rows)/len(rows)
    # Snapped <.2 corresponds to continuous <.1995, not exactly <.2.
    expected=math.log(.1995/.1)/math.log(3)
    assert abs(observed-expected)<.02


def test_origin_membership_at_shared_boundary():
    card=C.verified_card()
    reg=dict(id='boundary',contract_id='contract-v1.3',role='confirmation',lambdaA='7',lambdaB='8',u='1',kappa='3/10',h='12',c_sw='0')
    assert S.inside(reg,card['regions']['MV+A']) and S.inside(reg,card['regions']['MV-BND'])
    rows=[dict(regime=reg,origin_region='MV-BND',purpose='TEST_ONLY_NO_ENGINE')]
    result=SC.score_batch(rows,{'boundary':dict(main=level())})
    assert result['counts']['MV-BND']=={'UNRESOLVED':1}
    assert result['counts']['MV+A']=={}


def test_distance_reports_both_metrics_and_fixed_axes():
    spec=C.verified_card()['regions']['MV+A']
    a=dict(lambdaA='7',lambdaB='8',u='1',kappa='1/10',h='12',c_sw='0')
    b=dict(a,h='25/2')
    d=S.distances(a,[b],spec)
    assert F(d['contract_Linf'])==F(1,2)
    assert d['range_log_Linf']==pytest.approx(math.log(12.5/12)/math.log(16/12))
    assert d['same_pinned_count']==1
    assert S.distances(a,[dict(b,lambdaB='7')],spec)['range_log_Linf_same_pinned'] is None


def test_inventory_parameters_including_R11_sealed_and_namespaces():
    inv=I.build()
    assert [inv['source_record_counts'][k] for k in ('stage1','stage2','stage3','robustK','robustdt')]==[60,108,48,9,9]
    assert sum(r['source']=='v1.2/heldout' for r in inv['records'])==12
    assert {'R09','R10','R11'} <= {r['source_id'] for r in inv['records']}
    r11=next(r for r in inv['records'] if r['source_id']=='R11')
    assert F(r11['coordinates']['u'])==1
    assert any(r['namespace']=='v1.2_incompatible_plant' for r in inv['records'])
    assert len(inv['other_namespaces'])==4


def test_frame_count_hash_purpose_and_collision_guards():
    card=C.verified_card(); inv={'records':[]}
    rows,_=S.sample_all(C.TEST_ROOT,card,30,0,set(),purpose='TEST_ONLY_NO_ENGINE')
    assert sum(frame.validate_rows(rows,card,30,0,inv,purpose='TEST_ONLY_NO_ENGINE').values())==120
    with pytest.raises(ValueError,match='truncated'): frame.validate_rows(rows[:-1],card,30,0,inv,purpose='TEST_ONLY_NO_ENGINE')
    with pytest.raises(ValueError,match='purpose'): frame.validate_rows(rows,card,30,0,inv,purpose='COMMITTED_CONFIRMATION')
    reg=rows[0]['regime']; seen={'records':[{'key':'|'.join(map(str,canonical(reg)))}]}
    with pytest.raises(ValueError,match='collision'): frame.validate_rows(rows,card,30,0,seen,purpose='TEST_ONLY_NO_ENGINE')


def test_exact_power_and_R5_against_independent_binomial():
    assert float(P.pass_power(30,F(7,10),F(1,5)))==pytest.approx(.552840041774)
    for n in (30,40,60):
        expected=sum(F(math.comb(n,k))*F(1,20)**k*F(19,20)**(n-k) for k in range(n//10+1,n+1))
        assert P.r5_failure(n,F(1,20))==expected
        assert P.robust_pass_power(n,F(7,10),F(1,5),0,0)==P.pass_power(n,F(7,10),F(1,5))
    assert P.robust_pass_power(40,F(7,10),F(1,5),F(1,50),F(1,20)) < P.pass_power(40,F(7,10),F(1,5))
    assert stats.k_support(30,F(1,2),F(1,40))==21


def test_allocation_uses_largest_n_then_optional_BND_and_no_silent_small_n():
    with pytest.raises(ValueError): P.select_allocation(100,10,0,numerics_closed=False)
    assert P.select_allocation(1,100,0,numerics_closed=True)['status']=='HOLD_BUDGET'
    # Synthetic timing only: 4*60*10*1.3=3120s; boundary would cost3510s.
    a=P.select_allocation(F(3200,3600),10,0,numerics_closed=True)
    assert (a['n'],a['bnd'])==(60,0)
    b=P.select_allocation(1,10,0,numerics_closed=True)
    assert (b['n'],b['bnd'])==(60,15)


def level(gm='2',gs='-2',cref='100'):
    return dict(Cref=cref,G_M=gm,G_S=gs,G_SM='0',Gamma='0',G_S_M1='0',G_M_S1='0')


def bundle(gm='2',gs='-2'):
    v=level(gm,gs)
    return dict(main=v,coarse_K=v,coarse_dt=v,arithmetic_pass=True)


def test_label_adapter_never_uses_unpaired_pilot_as_ready():
    assert SC.label_result('effect',dict(main=level()))=='UNRESOLVED'
    assert SC.label_result('effect',bundle())=='MEETS'
    assert SC.label_result('effect',bundle(gm='0'))=='FAILS'
    assert SC.label_result('effect',bundle(gm='1'))=='UNRESOLVED'
    assert SC.label_result('effect',dict(main=level(cref='0')))=='UNDEFINED'
    bad=bundle();bad['arithmetic_pass']=False
    assert SC.label_result('effect',bad)=='UNRESOLVED'
    bad=bundle();bad['coarse_dt']=level(gm='1')
    assert SC.label_result('effect',bad)=='UNRESOLVED'


@pytest.mark.parametrize('kplus,kminus,expected',[(24,5,'PASS'),(24,20,'WEAKEN'),(5,5,'FALSIFY'),(15,5,'INCONCLUSIVE')])
def test_synthetic_join_reaches_each_verdict(kplus,kminus,expected):
    rows=[]; results={}
    for name in ('MV+A','MV-ii','SH+A','SH-ii'):
        k=kplus if name.endswith('+A') else kminus
        for i in range(30):
            rid=f'{name}:{i}'
            rows.append(dict(regime={'id':rid},origin_region=name))
            results[rid]=bundle(gm='2' if i<k else '0',gs='-2' if i<k else '0')
    out=SC.score_batch(rows,results)
    assert all(c['verdict']==expected for c in out['cards'].values())
    with pytest.raises(ValueError): SC.score_batch(rows,{k:v for k,v in list(results.items())[:-1]})


def test_controls_exact_zero_and_r5_threshold():
    from experiments.R3R_05_contract.rules import CONTRASTS
    from experiments.R3R_06_cards import verdict as V
    zero=dict.fromkeys(CONTRASTS,'0');SC.require_zero_control(zero)
    SC.require_identical_models(zero)
    with pytest.raises(ValueError): SC.require_zero_control(dict(zero,G_M='0.0000000000000001'))
    with pytest.raises(ValueError): SC.require_identical_models(dict(zero,G_M_S1='0.0000000000000001'))
    assert V.r5(dict(MEETS=27,UNRESOLVED=3)) is None
    assert V.r5(dict(MEETS=26,UNRESOLVED=4))=='UMAX'


def test_runner_refuses_missing_flag_receipt_tag_and_logs(tmp_path,monkeypatch):
    with pytest.raises(ValueError,match='confirmation-run'): run.preflight(confirmation_run=False,receipt=None)
    with pytest.raises(ValueError,match='receipt'): run.preflight(confirmation_run=True,receipt=None)
    assert run.main(['--attempt-log-dir',str(tmp_path)])==2
    record=json.loads(next(tmp_path.glob('*.json')).read_text())
    assert record['status']=='REFUSED' and record['engine_runs']==0
    import subprocess
    monkeypatch.setattr(gates,'verify_lock',lambda:None)
    monkeypatch.setattr(gates,'verified_card',lambda:None)
    def no_tag(*args): raise subprocess.CalledProcessError(128,['git',*args])
    monkeypatch.setattr(gates,'git',no_tag)
    with pytest.raises(subprocess.CalledProcessError): gates.verify_numerics()


def test_runner_rejects_incomplete_hash_set_and_changed_hash(tmp_path):
    with pytest.raises(ValueError,match='exact artifact set'): gates.verify_hashes({})
    path=tmp_path/'one';path.write_text('original')
    names=('prereg','frame','inventory','card_receipt','scorer','sampler','numerics_receipt')
    with pytest.raises(ValueError,match='hash mismatch'):
        gates.verify_hashes({k:dict(path=str(path),sha256='0'*64) for k in names})


def test_numerics_requires_interior_resolution_and_corner_coverage():
    spec=dict(status='CLOSED_WITH_DECLARED_SCOPE',K_star=160,ref_star=2,dt_star='1/240',S1_route='synthetic',
              quadrature_tail_policy='synthetic',p95_bundle_cpu_seconds=10,fixed_validation_cpu_seconds=10,r_coverage_report='synthetic',
              coverage=dict(kappa_3_h_16=True,rational_rate_resolution_1_1000=True,interior_lattice_feasibility=True))
    gates.validate_numerics_spec(spec)
    for name in spec['coverage']:
        missing=deepcopy(spec);missing['coverage'][name]=False
        with pytest.raises(ValueError,match='coverage'): gates.validate_numerics_spec(missing)


@pytest.mark.parametrize('field',['decision','phase4_allowed','D22_implementation','D22_audit','P0_V10','L8','realism_disposition'])
def test_each_execution_gate_is_required(field):
    good=dict(decision='GO_WITH_DECLARED_SCOPE',phase4_allowed=True,D22_implementation='PASS',D22_audit='PASS',
              P0_V10='PASS',L8='PASS',realism_disposition='SCOPE_LIMITATION_AUTHORIZED')
    gates.validate_gate(good)
    bad=deepcopy(good);bad.pop(field)
    with pytest.raises(ValueError): gates.validate_gate(bad)


def test_write_once_and_no_engine_imports(tmp_path):
    C.write_once(tmp_path/'one.json',{'test':True})
    with pytest.raises(FileExistsError): C.write_once(tmp_path/'one.json',{})
    # AST import boundary: test sampler/frame code cannot reach the physical engine.
    import ast
    from pathlib import Path
    for path in Path('experiments/R3R_07_confirmation').glob('*.py'):
        tree=ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node,ast.ImportFrom):
                assert not (node.module or '').startswith(('smr','experiments.A00_engine','experiments.R3R_02_audit'))
