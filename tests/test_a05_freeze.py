"""Doan Van Tai — design-only inputs, matched fit and future scorer guards."""
import ast
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys

import numpy as np
import pytest
from scipy.integrate import quad

from experiments.A05_freeze import features
from experiments.A05_freeze.ledger import gaussian
from experiments.A05_freeze.model import fit_model,predict_model,standardize
from experiments.A05_freeze.predict import discrimination
from experiments.A05_freeze.score_test import score,score_group
from experiments.A05_freeze import provenance
from tests.test_card_grading import row
from tests.test_engine_guard import isolated_repo,commit


def cfg():return json.loads(Path('experiments/A05_freeze/config.json').read_text())


def test_whitelist_target_input_and_forbidden_outcome_columns():
    # Public grid metadata is sanitized on main rows only; no held-out features.
    raw=json.loads(Path('notes/design/grid_v1_2.json').read_text())['main'][0]
    poison=dict(raw,p_sw='DO NOT READ',Cref='DO NOT READ',E_delta='DO NOT READ')
    a,b=features.sanitize(raw),features.sanitize(poison)
    assert a==b and set(a)==features.FIELDS
    assert features.values(a)==features.values(b)
    with pytest.raises(ValueError):features.values(dict(a,p_sw=.7))
    with pytest.raises(PermissionError):features.load_design('heldout')


@pytest.mark.parametrize('k,h',[(.3,2.),(1.,8.),(3.,8.),(10.,.00001)])
def test_telegraph_memory_time_matches_independent_integral(k,h):
    expected=quad(lambda t:2*36*(h-t)*np.exp(-2*t/k),0,h,epsabs=1e-12)[0]
    assert features.telegraph_variance(h,k)==pytest.approx(expected,rel=1e-10,abs=1e-15)


def test_equal_budget_feature_shapes_and_no_engine_imports():
    records=features.load_design('main')
    assert len(records)==38
    for model in ('H0','H1'):
        assert len(features.CANDIDATES[model])==2
        for c in features.CANDIDATES[model]:
            X=features.tensor(records,model,c)
            assert X.shape==(38,4,3) and np.isfinite(X).all()
            assert np.all(X[:,:,0]==1) and 4*X.shape[-1]==12
    for name in ('features.py','fit.py','model.py','ledger.py'):
        tree=ast.parse(Path('experiments/A05_freeze',name).read_text())
        imports=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):imports.extend(n.name for n in node.names)
            elif isinstance(node,ast.ImportFrom):imports.append(node.module or '')
        assert not any(m.startswith(('smr','experiments.A00_engine')) for m in imports)
    calls=[n for n in ast.walk(ast.parse(Path('experiments/A05_freeze/fit.py').read_text()))
           if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='load_design']
    assert len(calls)==1 and calls[0].args[0].value=='main'


def test_scaling_fit_only_and_matched_small_synthetic_recovery():
    X=np.ones((12,4,3));X[:,:,1]=np.repeat([-1,1],6)[:,None]
    X[:,:,2]=np.linspace(-.8,.8,12)[:,None]
    standardized,scale=standardize(X)
    beta=np.zeros((4,3));beta[0]=[.01,.005,.003];beta[2]=[.002,.001,0]
    beta[1,0]=beta[3,0]=-3
    from experiments.A05_freeze.model import forward
    y=forward(standardized,beta,cfg())
    fit=fit_model(X,y,cfg())
    assert fit['k']==12 and len(fit['starts'])==2
    assert np.mean((predict_model(X,fit,cfg())-y)**2)<1e-7
    huge=X.copy();huge[:,:,2]+=10000
    _,same=standardize(huge,scale)
    assert same==scale


def predictions():
    return {f'R{i:02}':{m:{'contrasts':{g:('0' if m=='H0' else '.02') for g in
                  ('G_S','G_M','G_SM','Gamma','G_S_M1','G_M_S1')}} for m in ('H0','H1')} for i in range(1,13)}


def synthetic_outcomes(ids):
    data={'fine':{},'coarse':{}}
    for cid in ids:
        for name,ref in (('fine',2),('coarse',1)):
            r=row(ref,GS=.1,GM=0,Gamma=0)
            r['dt_s']=str(F(1,120*ref));r['reference_context']['dt_s']=r['dt_s']
            r['intervals']['R00']=[.1,.1]
            data[name][cid]=r
    return data


def test_discrimination_closed_groups_use_no_outcomes_and_keep_rule_cells():
    p=predictions()
    for r in p.values():r['H1']['contrasts']=dict(r['H0']['contrasts'])
    d=discrimination(p,cfg())
    assert d['outcome_open_ids']==['R03','R04','R05','R06','R07','R08']
    result=score({},p,d,cfg())
    assert result['primary_verdict']=='DO_NOT_OPEN'
    assert result['K5']['heldout_K']['verdict']=='UNRESOLVED'


def test_future_score_uses_all_branches_and_counts_unavailable_cells():
    p=predictions();d=discrimination(p,cfg());data=synthetic_outcomes(d['outcome_open_ids'])
    result=score(data,p,d,cfg())
    assert result['K5']['full_rule_verdict']=='STANDS'
    assert result['C1']['heldout']['verdict']=='STANDS'
    assert result['K5']['heldout_K']['cells']['R03']['headroom_label']=='STANDS_HEADROOM_LIMITED'
    assert result['combined_success_rate'] is None
    ids=cfg()['test_groups']['interpolation']
    for cid in ids[:3]:data['fine'].pop(cid)
    result=score_group(ids,data,p,cfg(),'interpolation',d['groups']['interpolation']['D'])
    assert result['verdict']=='INCONCLUSIVE' and len(result['unavailable'])==3


def test_frozen_hash_guard_before_any_true_input_read(monkeypatch):
    import experiments.A05_freeze.score_test as scorer
    def denied():raise PermissionError('synthetic hash mismatch')
    monkeypatch.setattr(scorer,'verify_frozen',denied)
    monkeypatch.setattr(scorer,'read',lambda p:pytest.fail('true input read before hash guard'))
    monkeypatch.setattr(sys,'argv',['score_test','--input','MUST_NOT_OPEN.json'])
    with pytest.raises(PermissionError,match='hash mismatch'):scorer.main()


def test_freeze_rejects_dirty_and_committed_tampering(isolated_repo,monkeypatch):
    repo=isolated_repo
    checkpoint={'prediction_commit':'synthetic'}
    monkeypatch.setattr(provenance,'verify_prediction_checkpoint',lambda r:checkpoint)
    monkeypatch.setattr(provenance,'ancestor',lambda *a,**kw:None)
    artifact=repo/'record.json';artifact.write_text('{"synthetic":true}\n')
    for name in (provenance.FREEZE_LOCK,provenance.CANONICAL):(repo/name).parent.mkdir(parents=True,exist_ok=True)
    (repo/provenance.CANONICAL).write_text('Synthetic freeze; not research evidence\n')
    (repo/provenance.FREEZE_LOCK).write_text(json.dumps({'status':'FROZEN_A05_F','checkpoint':checkpoint,
                                                      'artifact_sha256':{'record.json':provenance.sha(artifact)}}))
    commit(repo,'synthetic frozen receipt')
    provenance.verify_frozen(repo)
    artifact.write_text('tampered\n')
    with pytest.raises(PermissionError):provenance.verify_frozen(repo)
    commit(repo,'synthetic tampering committed')
    with pytest.raises(PermissionError,match='artifact changed'):provenance.verify_frozen(repo)
