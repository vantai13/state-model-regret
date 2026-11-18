"""Doan Van Tai — V7-3 synthetic controls and explicitly TRAIN-only checks."""
import ast
import copy
import csv
from datetime import datetime, timedelta
import io
import json
from pathlib import Path
import shutil
import tarfile
import time

import numpy as np
import pytest

from experiments.letter import e4_geant as E
from experiments.letter import v7_3_day as A
from experiments.letter import v7_3_cong as G
from experiments.letter import v7_3_test as Run
from experiments.letter import v7_3_test_common as C
from experiments.letter import v7_3_score as Score
from experiments.letter import v7_3_rescore as Rescore

# Register without modifying existing pytest configuration (new files only).
pytestmark = pytest.mark.filterwarnings('ignore:Unknown pytest.mark.slow:pytest.PytestUnknownMarkWarning')


@pytest.fixture
def params():
    return C.read_json(C.ROOT/C.PARAMS)


@pytest.fixture(params=[1.,np.float64(1.),np.array(1.),np.array([1.]),np.array([[1.]])],
                ids=['python-float','numpy-scalar','0d','1d-size1','2d-size1'])
def scalar_capacity(request):
    return request.param


def synthetic(params,n=4):
    hs = np.array(params['hours'])*3600
    value = np.empty((n,2,4))
    value[:,0,:] = (100+20*np.arange(n))[:,None]*hs
    value[:,1,:] = value[:,0,:]-20*hs
    m0 = np.ones((n,2,4))
    old = np.ones((n,2,2,4))
    old[:,:,1,:] = 0
    decisions = np.ones((n,3,2,2,4),dtype=np.int16)
    decisions[:,0,0] = 0
    flags = np.zeros_like(decisions,dtype=bool)
    flags[:,0,0] = True
    selected = E.costs_for_decisions(value,decisions)
    reference = np.ones((n,4),dtype=np.int16)
    cref = E.costs_for_decisions(value,reference)
    raw = dict(V=value,paired_evaluation=np.repeat(value[:,None],2,axis=1),
        reference_decision_rollouts=np.repeat(value[:,None],2,axis=1),
        C_ref=cref,reference_decision=reference,reference_tie_flags=np.zeros((n,4),dtype=bool),
        decisions=decisions,tie_flags=flags,costs=selected,
        regret=selected-cref[:,None,None,None,:],G_S=selected[:,:,1]-selected[:,:,0],
        M0_predicted_fresh=m0,M0_predicted_stale=old,h_seconds=hs,
        tau_seconds=np.array(params['tau_seconds']),backlog_trace=np.zeros((16,2)),
        input_utilization=np.full((24,2,1),.5))
    label = dict(regime='DAY1',date='2005-05-05',stratum='S')
    return raw,label


def test_known_metrics_and_independent_recalculation(params):
    raw,label = synthetic(params)
    rows = Score.case_rows(raw,label,params)
    independent = Rescore.recompute(raw,label,params)
    assert Rescore.compare(rows,independent)==[]
    r = next(r for r in rows if r['h_hours']==6 and r['tau_s']==300)
    assert r['C_ref_Mbit']==110
    assert r['M0_G_S_Mbit']==-20
    assert r['M0_se_G_S_Mbit']==0
    assert r['M0_fresh_R_pct']==pytest.approx(100*20/110)
    assert r['M0_stale_R_pct']==0
    assert r['M0_both_R_pct']==r['M0_fresh_R_pct']
    assert r['M0_fresh_F_switch']==0 and r['M0_stale_F_switch']==1
    assert r['M0_fresh_tie_share']==1 and r['M0_stale_tie_share']==0
    assert r['M0_G_S_ms']==pytest.approx(-20/params['capacity_Mbps']*1000)
    assert r['H1_clause']=='RESOLVED_AGREE'


def test_paired_instance_standard_error_is_not_rollout_standard_error(params):
    raw,label = synthetic(params)
    # Vary instance effects while preserving the decision/reference distinction.
    raw['paired_evaluation'][:, :,1,:] -= np.arange(4)[:,None,None]*raw['h_seconds']
    raw['V'] = raw['paired_evaluation'].mean(axis=1)
    raw['C_ref'] = E.costs_for_decisions(raw['V'],raw['reference_decision'])
    raw['costs'] = E.costs_for_decisions(raw['V'],raw['decisions'])
    raw['regret'] = raw['costs']-raw['C_ref'][:,None,None,None,:]
    raw['G_S'] = raw['costs'][:,:,1]-raw['costs'][:,:,0]
    row = Score.case_rows(raw,label,params)[0]
    assert row['M0_se_G_S_Mbit']==pytest.approx(np.std([20,21,22,23],ddof=1)/2)
    assert Rescore.compare(Score.case_rows(raw,label,params),Rescore.recompute(raw,label,params))==[]


def test_random_tie_is_expected_cost_and_switch_variant(params):
    raw,label = synthetic(params)
    row = Score.case_rows(raw,label,params)[0]
    assert row['M0_random_tie_fresh_R_Mbit']==10
    assert row['M0_random_tie_G_S_Mbit']==-10
    assert row['M0_random_tie_fresh_F_switch']==.5
    assert row['M0_switch_tie_G_S_Mbit']==0
    assert row['M0_switch_tie_fresh_R_Mbit']==0
    assert row['Hybrid_S_both_R_Mbit']==0


def test_small_regret_on_large_common_cost_rescores_at_locked_tolerance(params):
    raw,label = synthetic(params,n=32)
    rng = np.random.default_rng(7007312)
    value = np.empty((32,2,4))
    value[:,0] = rng.uniform(1e12,1e13,(32,4))
    value[:,1] = value[:,0]-rng.uniform(.1,10.,(32,4))
    raw['paired_evaluation'] = np.repeat(value[:,None],2,axis=1)
    raw['V'] = raw['paired_evaluation'].mean(axis=1)
    raw['C_ref'] = E.costs_for_decisions(raw['V'],raw['reference_decision'])
    raw['costs'] = E.costs_for_decisions(raw['V'],raw['decisions'])
    raw['regret'] = raw['costs']-raw['C_ref'][:,None,None,None,:]
    raw['G_S'] = raw['costs'][:,:,1]-raw['costs'][:,:,0]
    assert Rescore.compare(Score.case_rows(raw,label,params),Rescore.recompute(raw,label,params))==[]


@pytest.mark.parametrize('load,label',[(.999,'S'),(1.,'O'),(1.001,'O')])
def test_strict_stratum_rule(load,label,scalar_capacity):
    inc = np.array([[[1.]],[[.5]]])
    got = Run.strata(np.full((24,1),load),inc,scalar_capacity)
    assert got['stratum']==label
    assert got['max_utilization_by_action']==[load,.5*load]


def test_strata_include_every_link_and_both_actions():
    inc = np.array([[[.2],[.3]],[[.1],[1.]]])
    assert Run.strata(np.ones((24,1)),inc,1.)['stratum']=='O'


@pytest.mark.parametrize('offset,evaluable',[(-1e-9,False),(0.,True),(1e-9,True)])
def test_evaluable_threshold_including_equality(params,offset,evaluable):
    raw,label = synthetic(params)
    # Keep all raw identities consistent with a constant, zero-regret record.
    v = np.full_like(raw['V'],params['evaluable_threshold_Mbit']+offset)*raw['h_seconds']
    raw['V'] = v
    raw['paired_evaluation'] = np.repeat(v[:,None],2,axis=1)
    # Reference costs intentionally remain non-tied and keep Switch as choice.
    raw['C_ref'] = E.costs_for_decisions(v,raw['reference_decision'])
    raw['costs'] = E.costs_for_decisions(v,raw['decisions'])
    raw['regret'] = raw['costs']-raw['C_ref'][:,None,None,None,:]
    raw['G_S'] = raw['costs'][:,:,1]-raw['costs'][:,:,0]
    rows = Score.case_rows(raw,label,params)
    assert all(r['evaluable']==evaluable for r in rows)
    if not evaluable:
        assert all(r['M0_both_R_pct'] is None for r in rows)
        assert all(v is None for r in rows for k,v in r.items() if k.endswith('_ms'))
    assert all(r['M0_both_R_Mbit']==0 for r in rows)
    assert Rescore.compare(rows,Rescore.recompute(raw,label,params))==[]


def test_h1_resolution_clauses_and_exact_two_se(params):
    raw,label = synthetic(params)
    base = Score.case_rows(raw,label,params)
    assert base[0]['H1_resolved']
    # Equal action proportions can still have a nonzero paired cost difference.
    raw['M0_predicted_fresh'][:2,1] = 0
    raw['M0_predicted_fresh'][:2,0] = 1
    raw['M0_predicted_fresh'][2:,0] = 0
    raw['M0_predicted_stale'][:2,:,0] = 0
    raw['M0_predicted_stale'][:2,:,1] = 1
    raw['M0_predicted_stale'][2:,:,0] = 1
    raw['M0_predicted_stale'][2:,:,1] = 0
    raw['decisions'][:,0,0] = np.array([1,1,0,0])[:,None,None]
    raw['decisions'][:,0,1] = np.array([0,0,1,1])[:,None,None]
    raw['tie_flags'][:,0] = False
    raw['costs'] = E.costs_for_decisions(raw['V'],raw['decisions'])
    raw['regret'] = raw['costs']-raw['C_ref'][:,None,None,None,:]
    raw['G_S'] = raw['costs'][:,:,1]-raw['costs'][:,:,0]
    assert all(r['H1_clause'] in ('F_EQUAL','OUTSIDE_POPULATION') for r in Score.case_rows(raw,label,params))
    # [1,1,1,5] has mean=2 and SE=1: equality at 2*SE is unresolved.
    raw,label = synthetic(params)
    raw['paired_evaluation'][:,:,1,:] = (raw['paired_evaluation'][:,:,0,:]
        -np.array([1,1,1,5])[:,None,None]*raw['h_seconds'])
    raw['V'] = raw['paired_evaluation'].mean(axis=1)
    raw['C_ref'] = E.costs_for_decisions(raw['V'],raw['reference_decision'])
    raw['costs'] = E.costs_for_decisions(raw['V'],raw['decisions'])
    raw['regret'] = raw['costs']-raw['C_ref'][:,None,None,None,:]
    raw['G_S'] = raw['costs'][:,:,1]-raw['costs'][:,:,0]
    result = Score.case_rows(raw,label,params)
    assert result[0]['M0_G_S_Mbit']==-2
    assert result[0]['M0_se_G_S_Mbit']==1
    assert not any(r['H1_resolved'] for r in result)
    assert result[-1]['H1_clause']=='GS_WITHIN_2SE'


def test_negative_signed_regret_preserves_separate_reference_stream(params):
    raw,label = synthetic(params)
    raw['reference_decision_rollouts'][:,:,0,:] = 0
    raw['reference_decision'][:] = 0
    raw['C_ref'] = E.costs_for_decisions(raw['V'],raw['reference_decision'])
    raw['regret'] = raw['costs']-raw['C_ref'][:,None,None,None,:]
    row = Score.case_rows(raw,label,params)[0]
    assert row['Hybrid_both_R_pct']<0
    assert row['M0_stale_R_Mbit']==-20
    assert Rescore.compare(Score.case_rows(raw,label,params),Rescore.recompute(raw,label,params))==[]


@pytest.mark.parametrize('name,minimum',[('H1',20),('H2',20),('H3',10)])
def test_minimums_and_verdict_boundaries(params,name,minimum):
    raw,label = synthetic(params)
    row = next(r for r in Score.case_rows(raw,label,params) if r['h_hours']==2)
    assert Score.hypothesis([row]*(minimum-1),name,params)['verdict']=='NOT_EVALUABLE'
    assert Score.hypothesis([row]*minimum,name,params)['verdict']=='PASS'
    assert Rescore.trial([row]*minimum,name,params)==Score.hypothesis([row]*minimum,name,params)
    fail = dict(row,H1_agrees=False,Hybrid_both_R_pct=30.,H1_clause='RESOLVED_DISAGREE',
                H2_clause='REGRET_GT_0.5',H3_clause='HYBRID_NOT_LOWER')
    assert Score.hypothesis([fail]*minimum,name,params)['verdict']=='FAIL'


def test_thresholds_are_inclusive_and_h3_improvement_is_strict(params):
    raw,label = synthetic(params)
    row = next(r for r in Score.case_rows(raw,label,params) if r['h_hours']==2)
    assert Score.hypothesis([row]*16+[dict(row,H1_agrees=False)]*4,'H1',params)['verdict']=='PASS'
    assert Score.hypothesis([dict(row,Hybrid_both_R_pct=.5)]*16+
                            [dict(row,Hybrid_both_R_pct=.50001)]*4,'H2',params)['verdict']=='PASS'
    assert Score.hypothesis([row]*9+[dict(row,Hybrid_both_R_pct=row['M0_both_R_pct'])],'H3',params)['verdict']=='PASS'
    assert Score.hypothesis([row]*8+[dict(row,Hybrid_both_R_pct=row['M0_both_R_pct'])]*2,'H3',params)['verdict']=='FAIL'


def test_lock_full_dependency_closure_and_tamper(tmp_path):
    root,sndlib = tmp_path/'repo',tmp_path/'sndlib'
    root.mkdir()
    sndlib.mkdir()
    # Real source closure, a small train-only data archive, no test payloads.
    for rel in C.source_paths():
        dest = root/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(C.ROOT/rel,dest)
    for rel in [C.PARAMS,C.BRIEF,C.BASE/'CARD_V7_3.md',Path('experiments/letter/v7_3_test_gcp.sh')]:
        (root/rel).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(C.ROOT/rel,root/rel)
    p = C.read_json(root/C.PARAMS)
    train = root/p['training_dir']
    train.mkdir(parents=True)
    for name in ('configuration.json','configuration.npz','protocol.json','summary.json'):
        (train/name).write_bytes(b'train-only fixture')
    (sndlib/'sndlib-networks-native').mkdir()
    (sndlib/'sndlib-networks-native/geant.txt').write_bytes(b'topology fixture')
    (sndlib/'v7_3_train.npz').write_bytes(b'train cache fixture')
    with tarfile.open(sndlib/C.ARCHIVE,'w:gz') as tar:
        data = b'train-only 2005-05-05 fixture'
        member = tarfile.TarInfo('tm-20050505-0000.txt')
        member.size = len(data)
        tar.addfile(member,io.BytesIO(data))
    manifest = dict(sha256=C.sha256(sndlib/C.ARCHIVE),
        topology_sha256=C.sha256(sndlib/'sndlib-networks-native/geant.txt'),
        train_cache_sha256=C.sha256(sndlib/'v7_3_train.npz'),
        canonical_member_sha256=C.canonical_members(sndlib/C.ARCHIVE))
    (root/C.BASE/'data_manifest.json').write_text(json.dumps(manifest))
    out = root/'out'
    locked = C.create_lock(out,root=root,sndlib=sndlib)
    C.verify_lock(out,root=root,sndlib=sndlib)
    for rel in ('experiments/ext_validity/packet.py','experiments/letter/e4_rhat.py',
                'experiments/letter/v7_3_cong.py','experiments/letter/v7_3_rescore.py'):
        assert rel in locked['sha256']
    path = root/'experiments/letter/v7_3_sim.py'
    path.write_text(path.read_text()+'\n# tamper\n')
    with pytest.raises(ValueError,match='lock mismatch'):
        C.verify_lock(out,root=root,sndlib=sndlib)
    with pytest.raises(FileExistsError):
        C.create_lock(out,root=root,sndlib=sndlib)


def test_loader_and_record_refuse_test_access_without_lock(monkeypatch):
    def forbidden(*args,**kwargs):
        pytest.fail('data/engine access preceded gate')
    monkeypatch.setattr(Run.D,'topology',forbidden)
    monkeypatch.setattr(Run.S,'warm_instances',forbidden)
    with pytest.raises(ValueError,match='verified lock'):
        Run.load_days(['2005-06-15'],{'start_slot':41})
    with pytest.raises(ValueError,match='date gate'):
        Run.compute_record({}, {},dict(train_dates=['2005-05-05']),
                           '2005-06-15','DAY1',0.,training_only=True)
    with pytest.raises(ValueError,match='verified lock'):
        Run.prepare_inputs({},Path('unused'))
    with pytest.raises(ValueError,match='date gate'):
        Run.write_record({}, {},dict(train_dates=['2005-05-05']),{},Path('unused'),
                         'DAY1','2005-06-15',{},training_only=True)


def test_record_writer_accepts_scalar_capacity(tmp_path,params,scalar_capacity):
    date,regime = '2005-05-05','DAY1'
    training = dict(dates=np.array([date]),days=np.full((1,24,1),6.),
                    warm=np.zeros((1,8,1)))
    arrays = dict(incidence=np.array([[[[2.]],[[1.]]]]),capacity=10*scalar_capacity,
                  profiles=np.full((2,24,1),6.))
    config = dict(train_dates=[date],regimes=[dict(id=regime)])
    p = dict(params,N_test=2,K=2,R_dec=2,R_eval=3,test_seed=A.PILOT_SEED)
    label = Run.strata(training['days'][0],arrays['incidence'][0],arrays['capacity'])
    result = Run.write_record(training,arrays,config,p,tmp_path,regime,date,label,
                              training_only=True)
    path = tmp_path/'records'/f'{regime}_{date}.npz'
    meta = C.read_json(path.with_suffix('.json'))
    assert result['npz_sha256']==meta['npz_sha256']==C.sha256(path)
    assert meta['training_only'] is True and meta['stratum']=='O'
    with np.load(path,allow_pickle=False) as raw:
        assert raw['V'].shape==(2,2,4)
        np.testing.assert_allclose(raw['input_utilization'][...,0],[[1.2,.6]]*24)


def test_no_overwrite_atomic_writer(tmp_path):
    path = tmp_path/'record.json'
    C.write_json(path,{'first':True})
    with pytest.raises(FileExistsError):
        C.write_json(path,{'first':False})
    assert C.read_json(path)=={'first':True}
    assert len(list(tmp_path.iterdir()))==1


def test_rescorer_does_not_import_runner_or_scorer():
    tree = ast.parse(Path(Rescore.__file__).read_text())
    for node in ast.walk(tree):
        if isinstance(node,(ast.Import,ast.ImportFrom)):
            assert all(x.name not in ('v7_3_score','v7_3_test') for x in node.names)


def test_synthetic_score_rescore_files_and_tamper(tmp_path,params,monkeypatch):
    raw,label = synthetic(params)
    params = dict(params,N_test=4,R_dec=2,R_eval=2,regimes=['DAY1'])
    (tmp_path/C.PARAMS).parent.mkdir(parents=True)
    (tmp_path/C.PARAMS).write_text(json.dumps(params))
    out = tmp_path/'out'
    token = C.VerifiedLock('synthetic-lock','fixture')
    monkeypatch.setattr(C,'ROOT',tmp_path)
    monkeypatch.setattr(C,'verify_lock',lambda *a,**k:token)
    (tmp_path/C.BASE/'data_manifest.json').write_text(json.dumps(dict(test_dates=[label['date']])))
    inputs = dict(records=[label],dates=[label['date']],requested_dates=[label['date']],
                  exclusions=[],lock_sha256=token.digest)
    C.write_json(out/'inputs.json',inputs)
    C.write_json(out/'run_summary.json',dict(status='COMPLETE',records=[label]))
    path = out/'records'/f'{label["regime"]}_{label["date"]}.npz'
    E.write_npz(path,raw)
    C.write_json(path.with_suffix('.json'),dict(label,npz_sha256=C.sha256(path)))
    summary = Score.score(out)
    assert summary['tests']['H1']['verdict']=='NOT_EVALUABLE'
    assert Rescore.rescore(out)['status']=='MATCH'
    # Alter a verdict then a numeric case metric: both must be discovered.
    saved = out/'score/summary.json'
    altered = C.read_json(saved)
    altered['tests']['H1']['verdict']='PASS'
    saved.write_text(json.dumps(altered))
    (out/'rescore.json').unlink()
    assert Rescore.rescore(out)['status']=='MISMATCH'
    # Entire-day omission must fail against the locked calendar as well.
    inputs['requested_dates']=[]
    (out/'inputs.json').write_text(json.dumps(inputs))
    with pytest.raises(ValueError,match='calendar'):
        Score.score(out)
    (out/'rescore.json').unlink()
    assert any('calendar' in m for m in Rescore.rescore(out)['mismatches'])
    inputs['requested_dates']=[label['date']]
    (out/'inputs.json').write_text(json.dumps(inputs))
    saved.write_text(json.dumps(summary))
    csv_path = out/'score/cases.csv'
    with csv_path.open(newline='') as f:
        case_data = list(csv.DictReader(f))
    case_data[0]['M0_G_S_Mbit']='-999'
    with csv_path.open('w',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=list(case_data[0]))
        writer.writeheader()
        writer.writerows(case_data)
    (out/'rescore.json').unlink()
    result = Rescore.rescore(out)
    assert result['status']=='MISMATCH'
    assert any('M0_G_S_Mbit' in m for m in result['mismatches'])


@pytest.mark.parametrize('rate',[-100.,0.,100.])
def test_independent_randomized_metrics_and_all_forecasts(params,rate):
    p = copy.deepcopy(params)
    p['s_hat_pooled_Mbit'] = {g:rate for g in p['regimes']}
    rng = np.random.default_rng(7400301)
    rows,other,labels,dates = [],[],[],[]
    for record in range(9):
        raw,label = synthetic(p,n=32)
        label = dict(label,regime=p['regimes'][record%3],date=f'2005-05-{5+record:02d}',
                     stratum='S' if record<6 else 'O')
        raw['input_utilization'][:] = .5 if record<6 else 1.
        dates.append(label['date'])
        labels.append(label)
        # Include exact ties, unequal states, independent decision/eval streams,
        # near-zero effects on a large common cost, and both s_hat signs.
        raw['paired_evaluation'] = rng.uniform(1e7,1e8,(32,4,2,4))
        raw['V'] = raw['paired_evaluation'].mean(axis=1)
        raw['reference_decision_rollouts'] = rng.uniform(1e7,1e8,(32,3,2,4))
        rv = raw['reference_decision_rollouts'].mean(axis=1)
        raw['reference_decision'] = rv.argmin(axis=1)
        raw['reference_tie_flags'] = rv[:,0]==rv[:,1]
        raw['C_ref'] = E.costs_for_decisions(raw['V'],raw['reference_decision'])
        raw['M0_predicted_fresh'] = rng.integers(0,3,(32,2,4)).astype(float)
        raw['M0_predicted_stale'] = rng.integers(0,3,(32,2,2,4)).astype(float)
        for side in range(2):
            for t in range(2):
                costs = raw['M0_predicted_fresh'] if side==0 else raw['M0_predicted_stale'][:,t]
                dc,fl = E.pick(costs)
                hc,hf = E.pick(E.hybrid_costs(costs,[0,rate],raw['h_seconds']))
                raw['decisions'][:,0,side,t],raw['tie_flags'][:,0,side,t] = dc,fl
                raw['decisions'][:,1,side,t],raw['tie_flags'][:,1,side,t] = hc,hf
                raw['decisions'][:,2,side,t] = int(rate<0)
                raw['tie_flags'][:,2,side,t] = rate==0
        raw['costs'] = E.costs_for_decisions(raw['V'],raw['decisions'])
        raw['regret'] = raw['costs']-raw['C_ref'][:,None,None,None,:]
        raw['G_S'] = raw['costs'][:,:,1]-raw['costs'][:,:,0]
        scored = Score.case_rows(raw,label,p)
        rescored = Rescore.recompute(raw,label,p)
        assert Rescore.compare(scored,rescored)==[]
        rows.extend(scored)
        other.extend(rescored)
    inputs = dict(dates=dates,records=labels,exclusions=[])
    assert Rescore.compare(Score.summarize(rows,inputs,p),Rescore.rebuild_summary(other,inputs,p))==[]


def test_f5_checks_each_pipeline_share_without_requiring_same_cases(params):
    raw,label = synthetic(params)
    base = next(r for r in Score.case_rows(raw,label,params) if r['h_hours']==2)
    rows = []
    for j in range(5):
        row = dict(base,stratum='O',confirmatory_population=False,
                   M0_both_R_pct=0.,Hybrid_both_R_pct=0.,Stationary_both_R_pct=0.)
        if j<3:
            row[Score.PIPES[j]+'_both_R_pct']=1.
        rows.append(row)
    inputs = dict(dates=[label['date']],records=[dict(label,stratum='O')],exclusions=[])
    f5 = Score.summarize(rows,inputs,params)['forecasts']['F5']
    assert f5['joint_numerator']==2 and f5['denominator']==5
    assert f5['verdict']=='HELD'
    assert all(x['fraction']==.8 for x in f5['by_pipeline'].values())


@pytest.mark.slow
def test_native_loader_on_train_date_equals_training_cache():
    training,_,config = A.load(G.OUT)
    got,excluded = Run.load_days(['2005-05-05'],config,training_only=True)
    assert excluded==[]
    j = np.flatnonzero(training['dates']=='2005-05-05')[0]
    for field in ('days','warm'):
        np.testing.assert_array_equal(got[field][0],training[field][j])
    assert got['dates'].tolist()==['2005-05-05']


@pytest.mark.slow
def test_pre_pool_train_dry_run_writes_real_inputs(tmp_path,params,monkeypatch):
    def forbidden(*args,**kwargs):
        pytest.fail('pre-pool train dry run accessed an engine, pool or lock')
    for name in ('compute_record','ProcessPoolExecutor','checked_token'):
        monkeypatch.setattr(Run,name,forbidden)
    monkeypatch.setattr(Run.S,'warm_instances',forbidden)
    monkeypatch.setattr(Run.S,'variable',forbidden)
    cached,expected_arrays,expected_config = A.load(G.OUT)
    original_load = Run.load_days
    def train_load(dates,config,**kwargs):
        assert kwargs['training_only'] is True
        assert set(dates)<=set(expected_config['train_dates'])
        return original_load(dates,config,**kwargs)
    monkeypatch.setattr(Run,'load_days',train_load)
    training,arrays,config,tasks,labels = Run.prepare_inputs(params,tmp_path,
                                                            training_only=True)
    assert config==expected_config
    assert arrays['capacity'].shape==(1,)
    for key in cached:
        np.testing.assert_array_equal(training[key],cached[key])
    for key in expected_arrays:
        np.testing.assert_array_equal(arrays[key],expected_arrays[key])
    inputs = C.read_json(tmp_path/'inputs.json')
    assert inputs['training_only'] is True and inputs['lock_sha256'] is None
    assert inputs['requested_dates']==inputs['dates']==cached['dates'].tolist()
    assert inputs['exclusions']==[]
    assert len(tasks)==len(labels)==len(inputs['records'])==len(cached['dates'])*len(params['regimes'])
    for record in inputs['records']:
        g,j = params['regimes'].index(record['regime']),inputs['dates'].index(record['date'])
        utilization = np.einsum('sd,aed->sae',cached['days'][j],expected_arrays['incidence'][g],
                               optimize=True)/expected_arrays['capacity'].item()
        maximum = utilization.max(axis=(0,2)).tolist()
        assert record['max_utilization_by_action']==maximum
        assert record['stratum']==('S' if all(x<1 for x in maximum) else 'O')
        assert labels[record['regime'],record['date']]==dict(
            max_utilization_by_action=maximum,stratum=record['stratum'])
    assert [p.name for p in tmp_path.iterdir()]==['inputs.json']
    # Even the validation bypass rejects test dates before opening traffic data.
    monkeypatch.setattr(Run.D,'topology',forbidden)
    monkeypatch.setattr(Run,'load_days',original_load)
    with pytest.raises(ValueError,match='date gate'):
        Run.prepare_inputs(params,tmp_path/'rejected',training_only=True,dates=['2005-06-15'])
    assert not (tmp_path/'rejected').exists()


@pytest.mark.slow
def test_real_congested_train_record_score_rescore_json(tmp_path,params):
    training,arrays,config = A.load(G.OUT)
    date,regime = '2005-05-06','DAY1'
    j = int(np.flatnonzero(training['dates']==date)[0])
    assert arrays['capacity'].shape==(1,)
    p = dict(params,N_test=2,test_seed=A.PILOT_SEED)
    assert (p['K'],p['R_dec'],p['R_eval'])==(64,64,128)
    label = Run.strata(training['days'][j],arrays['incidence'][0],arrays['capacity'])
    result = Run.write_record(training,arrays,config,p,tmp_path,regime,date,label,
                              training_only=True)
    path = tmp_path/'records'/f'{regime}_{date}.npz'
    # write_record uses C.write_json, then both scorers consume round-tripped data.
    meta = C.read_json(path.with_suffix('.json'))
    assert meta['training_only'] is True and meta['seed_base']==A.PILOT_SEED
    assert (meta['N'],meta['K'],meta['R_dec'],meta['R_eval'])==(2,64,64,128)
    assert result['npz_sha256']==meta['npz_sha256']==C.sha256(path)
    assert all(meta[key]==value for key,value in label.items())
    with np.load(path,allow_pickle=False) as f:
        raw = {key:f[key] for key in f.files}
    utilization = np.einsum('sd,aed->sae',training['days'][j],arrays['incidence'][0],
                           optimize=True)/arrays['capacity'].item()
    np.testing.assert_array_equal(raw['input_utilization'],utilization)
    scored = Score.case_rows(raw,meta,p)
    rescored = Rescore.recompute(raw,meta,p)
    mismatches = Rescore.compare(scored,rescored)
    assert mismatches==[]
    assert len(scored)==8
    C.write_json(tmp_path/'integration_result.json',dict(
        owner='Doan Van Tai',training_only=True,date=date,regime=regime,
        N=meta['N'],K=meta['K'],R_dec=meta['R_dec'],R_eval=meta['R_eval'],
        seed_base=meta['seed_base'],stratum=meta['stratum'],
        capacity_shape=list(arrays['capacity'].shape),json_roundtrip=True,
        cases_compared=len(scored),mismatches=mismatches,
        status='MATCH',CPU_s=meta['CPU_s'],wall_s=meta['wall_s']))


@pytest.mark.slow
def test_congested_train_pilot_bitwise_equivalence(tmp_path):
    training,arrays,config = A.load(G.OUT)
    learned = C.read_json(G.OUT/'summary.json')['regimes'][0]['s_hat_Mbit']
    started = time.perf_counter()
    raw,meta = Run.compute_record(training,arrays,config,'2005-05-05','DAY1',learned,
        n=2,k=64,r_dec=64,r_eval=128,seed=A.PILOT_SEED,training_only=True)
    path = G.OUT/'pilot/DAY1_2005-05-05.npz'
    with np.load(path,allow_pickle=False) as saved:
        for name in saved.files:
            assert raw[name].dtype==saved[name].dtype,name
            assert raw[name].shape==saved[name].shape,name
            assert raw[name].tobytes()==saved[name].tobytes(),name
        count = len(saved.files)
    assert raw['M0_predicted_fresh'].shape==(2,2,4)
    assert raw['M0_predicted_stale'].shape==(2,2,2,4)
    assert meta['tint_seed']==Run.T.seed_for(A.PILOT_SEED,'tint|DAY1|2005-05-05')
    # Keep new validation artifacts away from all existing pilot files.
    validation = tmp_path
    evidence = dict(meta,legacy_arrays_bitwise_equal=count,
        test_wall_s=time.perf_counter()-started,
        projection=dict(records=150,N=32,workers=30,
            CPU_s=meta['CPU_s']*16*150,
            ideal_wall_s=meta['CPU_s']*16*150/30,
            method='linear N scaling from one TRAIN DAY1 N2 full-K/R record; trace overhead also scaled conservatively'))
    C.write_json(validation/'pilot_equivalence.json',evidence)
