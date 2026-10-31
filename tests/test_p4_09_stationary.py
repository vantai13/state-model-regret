"""L4.9 mathematical counterexamples, noncircular predictor and prospective scores."""
from fractions import Fraction as F
from pathlib import Path
import json

import numpy as np
import pytest

from experiments.P4_09_stationary import predictor as P
from experiments.P4_09_stationary import score as S
from experiments.P4_09_stationary.discovery import exposure_audit,references
from experiments.P4_07_clipping.check_clipping import exact_reference


@pytest.mark.parametrize('H',[1,2,4,8])
def test_unbounded_initial_backlog_defeats_uniform_oracle_action(H):
    # Positive-probability states in the two-mode queue support, however large H.
    A_st,A_sw,B_st,B_sw=(-8,4),(-9,3),(-8,4),(-7,5)
    def gap(qa,qb):
        return (exact_reference(H,A_sw,F(3,4),qa,0)+exact_reference(H,B_sw,F(3,4),qb,0)
                -exact_reference(H,A_st,F(3,4),qa,0)-exact_reference(H,B_st,F(3,4),qb,0))
    assert gap(9*H,0)<=-H
    assert gap(0,9*H)>=H


def test_global_action_variation_does_not_prove_information_value():
    # If Y already identifies X, each posterior is one point: S10=0.
    posteriors=[[-1],[1]]
    assert sum(min(sum(max(x,0) for x in g),sum(max(-x,0) for x in g)) for g in posteriors)==0


def fake_side(h):
    return dict(h=np.asarray(h,dtype=np.longdouble),eh=np.zeros(len(h),dtype=np.longdouble),
                zero=np.asarray([x==0 for x in h]),sat=np.zeros(len(h),dtype=bool),
                w=np.full(len(h),np.longdouble(1)/len(h)))


def test_tie_is_Stay_not_a_third_action():
    A,B=fake_side([0,-1]),fake_side([0])
    result=P.action_mismatch(A,B,1)
    assert result['P_mis']==.5 and result['M0_tie_mass']==.5
    assert result['M0_ambiguous_mass']==0
    assert P.action_mismatch(A,B,-1)['P_mis']==.5


def test_mean_profile_path_cannot_call_finite_horizon_M1(monkeypatch):
    def forbidden(*a,**kw):raise AssertionError('finite-h M1 accessed')
    monkeypatch.setattr(P.P,'idle',forbidden)
    monkeypatch.setattr(P.profiles,'get',forbidden)
    monkeypatch.setattr(P.quadrature,'build',lambda law,K,cap:dict(
        indices=np.array([0,1,20,-1]),mass=np.array([[.25,0],[.1,.1],[.1,.1],[.1,.25]],dtype=np.longdouble),l1_error=np.longdouble(0)))
    side=P.mean_side(F(7),F(0),F(2),F(3,10),F(1,2),1,4,F(1,120),object())
    assert abs(side['w'].sum()-1)<1e-15
    assert side['h'].shape==(8,)


class FakeLaw:
    def __init__(self,mean,error=0):self.mean=np.longdouble(mean);self.mean_error=np.longdouble(error)


class FakeCache:
    def __init__(self,error=0):self.error=error
    def get(self,load,k,ref):
        moments={F(7):1,F(8):2,F(9):4}
        return F(1),FakeLaw(moments[load],self.error),'fixture','fixture'


def test_predictor_known_answer_uses_stationary_denominator(monkeypatch):
    monkeypatch.setattr(P,'mean_side',lambda *args:fake_side([0,-1]))
    result=P.predict(['7','8','1/10','1/2','16','0'],FakeCache())
    assert result['r_Stay']==4 and result['r_Switch']==5 and result['s']==1
    assert result['GM_pred_pctC']==18.75  # .75 mismatch, normalized by stationary4


def test_stationary_symmetry_is_not_finite_horizon_outcome(monkeypatch):
    monkeypatch.setattr(P,'mean_side',lambda *args:fake_side([0,-1]))
    result=P.predict(['7','7','1/10','1/2','16','0'],FakeCache())
    assert result['GM_pred_pctC']==0 and result['stationary_symmetry_zero'] is True


def test_uncertain_stationary_sign_not_forced_to_plus_or_minus():
    result=P.predict(['7','8','1/10','1/2','16','0'],FakeCache(error=10))
    assert result['status']=='NOT_READY_STATIONARY_SIGN'


def test_1NN_physical_key_exclusion_and_stable_tie_break():
    target='7|8|1|1/10|16|0'
    rows=[dict(key=target,value=999),dict(key='7|8|1|1/10|8|0',value=1),dict(key='7|8|1|1/10|32|0',value=2)]
    assert P.nearest(target,rows)['value']==999
    assert P.nearest(target,rows,leave_out=True)['value'] in (1,2)
    assert P.nearest(target,list(reversed(rows)),leave_out=True)==P.nearest(target,rows,leave_out=True)


@pytest.mark.parametrize('labels,expected',[
    (['MEETS']*11+['DOES_NOT_MEET'],'PASS'),
    (['MEETS']*10+['DOES_NOT_MEET']*2,'FAIL'),
    (['MEETS']*10+['DOES_NOT_MEET','UNRESOLVED'],'INCONCLUSIVE'),
    (['MEETS']*11+['UNRESOLVED'],'PASS'),
    (['MEETS']*10+['UNRESOLVED']*2,'INCONCLUSIVE'),
    (['MEETS']*11,'INCONCLUSIVE'),
])
def test_HL1_finite_panel_no_90_80_gap(labels,expected):
    assert S.state_verdict(labels)['verdict']==expected


def test_HL2_three_level_robustness_and_incomplete_panel():
    truth=np.arange(12,dtype=float);nn=truth+1
    assert S.model_verdict(truth,nn,[truth]*3,all_ready=True)['verdict']=='PASS'
    assert S.model_verdict(truth,nn,[truth,truth,truth+5],all_ready=True)['verdict']=='INCONCLUSIVE'
    assert S.model_verdict(truth,nn,[truth]*3,all_ready=False)['verdict']=='INCONCLUSIVE'
    assert S.model_verdict(truth,nn,[truth,truth,truth[:11]],all_ready=True)['verdict']=='INCONCLUSIVE'


def test_zero_null_error_and_constant_prediction_do_not_demonstrate_advantage():
    x=np.arange(12,dtype=float)
    assert S.model_metrics(x,x,x)['passes'] is False
    assert S.model_metrics(np.zeros(12),x+1,x)['Spearman'] is None


def test_future_panel_extrapolates_and_timing_is_disjoint():
    protocol=json.loads(Path('experiments/P4_09_stationary/protocol.json').read_text())
    training,_,_=references()
    audit=exposure_audit(protocol,training)
    assert len(audit['future_panel'])==12
    assert {r['h_over_kappa'] for r in audit['future_panel']}=={'320','640'}
    assert audit['timing_h32_new_coordinate'] is True
    assert audit['max_registered_ratio']=='160'
