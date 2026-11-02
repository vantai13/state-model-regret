"""Parameter-only P6 predictor: saved exposed shares, numerical invariants, no M1 costs."""
import ast
import csv
from fractions import Fraction as F
from pathlib import Path
import resource
import time

import numpy as np
import pytest

from experiments.P6_band import predictor as R
from experiments.P6_band import window as W
from experiments.P6_band import identity as I
from experiments.P4_09_stationary import predictor as OLD

ROOT=W.ROOT
_cache=None
_memo={}


@pytest.fixture(autouse=True)
def no_truth(monkeypatch):
    def forbidden(*a,**kw):raise AssertionError('finite-h M1 cost accessed')
    monkeypatch.setattr(R.profiles,'get',forbidden)
    monkeypatch.setattr(R.P,'idle',forbidden)


@pytest.fixture
def sides(tmp_path_factory,no_truth):
    global _cache
    if _cache is None:_cache=R.StationaryCache(ROOT,tmp_path_factory.mktemp('p6_mean_laws'))
    def build(params,ref=4,K=320):
        k=tuple(map(F,params))+(ref,K)
        if k not in _memo:_memo[k]=R.build_sides(*map(F,params),_cache,ref=ref,K=K)
        return _memo[k]
    return build


def fake_side(values,zero=None,sat=None):
    n=len(values)
    return dict(h=np.array(values,dtype=R.P.LD),w=np.full(n,R.P.LD(1)/n),
                eh=np.zeros(n,dtype=R.P.LD),zero=np.array(zero or [False]*n),
                sat=np.array(sat or [False]*n))


@pytest.mark.parametrize('a,b', [('6','13/2'),('13/2','6')])
def test_T1_fresh_mismatch_matches_frozen_predictor_at_zero(sides,a,b):
    sd=sides((a,b,'1/20','1','16'))
    pred=R.predict(sd,F(0))
    pm=OLD.action_mismatch(*sd['fresh'],sd['r_switch']-sd['r_stay'])['P_mis']
    mismatch=1-pred['F_new'] if pred['truth_switch'] else pred['F_new']
    assert abs(pm-mismatch)<1e-12


@pytest.mark.parametrize('rid', ['H0015','H0143'])
def test_T2_saved_exposed_M0_shares(sides,rid):
    with (ROOT/'results/explore_mech/hslice/metrics.csv').open() as f:
        row=next(r for r in csv.DictReader(f) if r['id']==rid)
    sd=sides((row['lamA'],row['lamB'],'1/10','3/2','16'),ref=2,K=160)
    assert abs(R.switch_share(*sd['fresh'],0)-float(row['sw_mean_cur']))<=1e-9
    assert abs(R.switch_share(*sd['stale'],0)-float(row['sw_mean_old']))<=1e-9


def test_quadrature_mean_descriptive_and_T7_variance_at_main(sides):
    sd=sides(('13/2','6','1/10','3/2','16'))
    d=R.distribution_checks(sd)
    assert np.isfinite(d['mean_drift'])
    assert d['variance_old']<=d['variance_new']+1e-9
    print('T3_T7',d)


def test_cold_first_production_base_and_numeric_invariants(tmp_path):
    cache=R.StationaryCache(ROOT,tmp_path/'cold');cache.index.clear()
    start=W.cpu();wall=time.monotonic()
    sd=R.build_sides(*next(W.bases()),cache)
    d=R.distribution_checks(sd)
    assert np.isfinite(d['mean_drift'])
    assert d['variance_old']<=d['variance_new']+1e-9
    print('COLD_FIRST_BASE_CPU',W.cpu()-start,'WALL',time.monotonic()-wall,'diagnostics',d)


def test_T4_cost_monotonic_certificates_and_ties():
    a=fake_side([-10,2,-2],zero=[True,False,False],sat=[False,True,False])
    b=fake_side([0],zero=[True],sat=[True])
    shares=[R.switch_share(a,b,c) for c in map(F,('0','1','2','3'))]
    assert shares==sorted(shares,reverse=True)
    assert shares==[float(F(1,3)),float(F(1,3)),0,0]
    assert R.switch_share(fake_side([-1]),fake_side([0]),1)==0


@pytest.mark.parametrize('u', [F(1),F(3,2),F(2)])
def test_T5_exact_H0_boundaries(u):
    edge=R.THETA0-R.THETA1*u
    assert R.h0_sign(0,u)=='-'
    assert R.h0_sign(edge,u)=='-'
    assert R.h0_sign(edge-F(1,1000000),u)=='+'


def test_T6_ast_no_true_profile_or_evaluator_calls():
    tree=ast.parse(Path(R.__file__).read_text())
    for node in ast.walk(tree):
        if isinstance(node,ast.ImportFrom):
            assert (node.module or '').split('.')[-1]!='population'
            assert all(alias.name not in ('population','idle') for alias in node.names)
        if isinstance(node,ast.Import):
            assert all(alias.name.split('.')[-1]!='population' for alias in node.names)
        if isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name):
            assert (node.value.id,node.attr) not in [('profiles','get'),('P','idle')]
    # The numeric tests above run with forbidden cost functions patched to raise.


def test_signed_predictor_formula_known_toy():
    fresh=(fake_side([-3,1]),fake_side([0]))
    stale=(fake_side([-1]),fake_side([0]))
    sd=dict(a=F(7),b=F(13,2),u=F(1),h=F(10),kappa=F(1,10),x=F(-1,2),
            r_stay=2.,r_switch=1.,fresh=fresh,stale=stale)
    for c,gain in [(0,-5),(1,F(9,2)),(2,4),(4,0)]:
        p=R.predict(sd,c)
        assert p['status']=='PREDICTED'
        assert abs(p['z_H1']-100*float(gain)/p['Cref_H1'])<1e-12


def test_unresolved_stationary_stake_not_forced_to_sign():
    sd=dict(h=F(1),r_switch=1.,r_stay=1.,s_error=.01)
    assert R.predict(sd,0)['status']=='STATIONARY_STAKE_UNRESOLVED'
    assert R.predict(sd,F(1,1000))['status']=='STATIONARY_STAKE_UNRESOLVED'
    with pytest.raises(ValueError):R.predict(sd,-1)


def test_engine_eta_conversion_and_collision():
    base=(F(7),F(13,2),F(1,10),F(3,2),F(8))
    assert W.parameters(base,F(1,4))==['7','13/2','1/10','3/4','8','1/4']
    p=dict(status='PREDICTED',truth_switch=True,H1='+',H0='-',c_over_stake=.1,z_H1=2.)
    q=dict(status='PREDICTED',H1='-',H0='-')
    blocked={W.key(W.parameters(base,F(1,4)))}
    flags=W.flags(base,F(1,4),p,q,p,p,blocked)
    assert not flags['W6'] and not flags['all']


def test_margin_flags_do_not_relax_near_crossing():
    base=(F(7),F(13,2),F(1,10),F(1),F(8))
    p=dict(status='PREDICTED',truth_switch=True,H1='+',H0='-',c_over_stake=.25,z_H1=1.)
    zero=dict(status='PREDICTED',H1='-',H0='-')
    out=W.flags(base,F(1,4),p,zero,p,p,set())
    assert out['group']=='Di' and out['all']
    assert not W.flags(base,F(1,4),dict(p,c_over_stake=.251),zero,p,p,set())['W3']
    assert not W.flags(base,F(1,4),dict(p,z_H1=.999),zero,p,p,set())['W4']
    assert not W.flags(base,F(1,4),p,zero,dict(p,H1='-'),p,set())['W7']
    assert not W.flags(base,F(1,4),p,dict(zero,H1='+'),p,p,set())['W8']


def test_witness_diversity_and_both_controls():
    rows=[]
    for i in range(10):
        for c in range(3):
            rows.append(dict(id=f'{i}-{c}',base_id=f'B{i}',all=True,group='Di' if i<7 else 'Dii',H1='+' if i<7 else '-'))
    rows.extend([dict(id='A+',base_id='A1',all=True,group='A',H1='+'),
                 dict(id='A-',base_id='A2',all=True,group='A',H1='-')])
    result=W.witness(rows)
    assert len(result['D'])==10 and result['Di']==7 and result['D_bases']==10
    assert result['controls_both_signs']
    same=[dict(r,base_id='ONLY') for r in rows if r['group']=='Di']
    assert not W.witness(same)['W9_met']


def test_declared_grid_count_and_domains():
    points=list(W.bases())
    assert len(points)==51 and sum(b<a for a,b,k,u,h in points)==33
    assert len(set(points))==51 and all(h/k*abs(b-a)>=30 for a,b,k,u,h in points)


def test_scan_serializes_predictions_and_flags_without_truth(tmp_path,monkeypatch):
    """Exercise the full CSV boundary on tiny synthetic M0 distributions."""
    monkeypatch.setattr(W,'collision_keys',lambda:set())
    original=R.distribution_checks
    monkeypatch.setattr(R,'distribution_checks',lambda sd:dict(original(sd),mean_drift=.008187))
    def build(a,b,k,u,h,cache,**kw):
        return dict(a=a,b=b,kappa=k,u=u,h=h,x=(b-a)/u,
                    r_stay=2.,r_switch=1. if b<a else 3.,
                    fresh=(fake_side([-3,1]),fake_side([0])),
                    stale=(fake_side([-1]),fake_side([0])))
    result=W.compute(tmp_path,builder=build,identity_checker=lambda *a,**kw:dict(passed=True,drift=0.,bound=.0001))
    with (tmp_path/'scan.csv').open() as stream:
        rows=list(csv.DictReader(stream))
    assert len(rows)==result['rows']==51*len(W.COSTS)
    assert len({r['id'] for r in rows})==len(rows)
    assert all(r['status']=='PREDICTED' and r['W6']=='True' for r in rows)
    assert set(r['c'] for r in rows)==set(map(str,W.COSTS))
    assert all(float(r['mean_drift'])>W.MEAN_TOL for r in rows)
    assert set(result['identities'])==set(W.IDENTITY_BASES)


class SwappedPosterior:
    def __init__(self,law):self.law=law
    def __getattr__(self,name):return getattr(self.law,name)
    def posterior(self,q):
        p,e=self.law.posterior(q)
        return 1-p,e


class MutantCache:
    def __init__(self,cache):self.cache=cache
    def get(self,load,kappa,ref):
        unit,law,*rest=self.cache.get(load,kappa,ref)
        return (unit,SwappedPosterior(law),*rest)


@pytest.mark.parametrize('kappa', [F(1,5),F(1,10)],ids=['B017','B011'])
def test_lattice_identity_detects_swapped_posterior(tmp_path,kappa):
    cache=R.StationaryCache(ROOT,tmp_path/'identity_laws')
    args=(F(7),F(13,2),kappa,F(3,2),F(16))
    good=I.exact_identity(*args,cache)
    bad=I.exact_identity(*args,MutantCache(cache))
    print('IDENTITY_MUTATION',str(kappa),{'good':good,'bad':bad})
    assert good['passed'] and abs(good['drift'])<=good['bound']
    assert not bad['passed'] and abs(bad['drift'])>100*bad['bound']


def test_strata_cover_every_nonempty_grid_cell():
    first={}
    for i,(a,b,k,u,h) in enumerate(W.bases(),1):first.setdefault((k,u,h),f'B{i:03d}')
    assert set(first.values())==set(W.IDENTITY_BASES)
    assert len(first)==7  # k=.2/u=1/h=8 has no admissible point in this grid.


def test_failed_identity_blocks_before_predictions(tmp_path,monkeypatch):
    monkeypatch.setattr(W,'collision_keys',lambda:set())
    monkeypatch.setattr(R,'distribution_checks',lambda sd:dict(mean_drift=0.))
    result=W.compute(tmp_path,builder=lambda *a,**kw:{},
                     identity_checker=lambda *a,**kw:dict(passed=False,drift=.1,bound=.0001))
    assert result['status']=='BLOCKED_EXACT_IDENTITY' and result['rows']==0
    assert result['diagnostic_failure']['base_id']=='B001'
    assert not (tmp_path/'scan.csv').exists()


@pytest.mark.parametrize('z,stable',[(.99,False),(1.01,True),(-2.,False)])
def test_final_K640_check_vetoes_weak_or_reversed_prediction(monkeypatch,z,stable):
    row=dict(id='D1',base_id='B001',lambdaA='7',lambdaB='13/2',kappa='1/10',
             u='1',h='8',c='1/2',H1='+',z_H1=1.2)
    calls=[]
    def builder(*a,**kw):calls.append(kw['K']);return {}
    monkeypatch.setattr(R,'predict',lambda *a:dict(status='PREDICTED',H1='+' if z>0 else '-',z_H1=z))
    failure,checks=W.validate_witness([row],dict(D=['D1'],A=[]),None,{'B001':dict(passed=True)},
        builder=builder,identity_checker=lambda *a,**kw:pytest.fail('sampled identity recomputed'))
    assert failure is None and calls==[640] and checks[0]['K_stable']==stable


def test_window_stop_rules_do_not_relax_Di_requirement():
    w=dict(W9_met=False,controls_both_signs=True)
    assert W.candidate_status({'all':{'Di':0,'Dii':3}},w)=='HOLD_ONLY_DII'
    assert W.candidate_status({'all':{'Di':0,'Dii':0}},w)=='STOP_NO_WINDOW'
    assert W.candidate_status({'all':{'Di':1,'Dii':30}},w)=='HOLD_INSUFFICIENT_DI_OR_DIVERSITY'


def test_lattice_patch_restored_after_error():
    original=R.quadrature.build
    with pytest.raises(RuntimeError):
        with I.lattice_quadrature([]):raise RuntimeError('test interruption')
    assert R.quadrature.build is original
