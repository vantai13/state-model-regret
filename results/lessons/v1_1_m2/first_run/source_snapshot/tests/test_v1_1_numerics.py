"""Doan Van Tai — N1/N2 exact references and mutants, no new grid."""
from fractions import Fraction as F
from itertools import product
import pytest

from smr.idle_gap import gap_from_idle,precision_summary,resolve_sign
from smr.single_observation import statistics
from smr.dominance import classify_state
from experiments.lessons.v1_1_numerics import conservation_cases,subtract_mean,subtract_truth
from tests.test_dominance_v1_1 import _small_plants,_paths,_prob,_cost,_m0_cost
from experiments.lessons.l1_3_expected_cost import CANON,expected_cost
from experiments.lessons.l1_6_belief import m0_cost
from tests.golden_phase1 import CANONICAL_BELIEF


def test_truth_structural_ties_and_subtraction_mutant():
    bad=0
    for state,plant in conservation_cases(300):
        assert classify_state(*state,plant)['label']=='conservation'
        assert gap_from_idle(state,plant,'M1')==0
        bad+=subtract_truth(state,plant)<0
    assert bad>0,'subtraction mutant must actually violate strict tie decisions'


def test_mean_structural_ties_and_subtraction_mutant():
    bad=0
    for state,plant in conservation_cases(468):
        assert gap_from_idle(state,plant,'M0')==0
        bad+=subtract_mean(state,plant)<0
    assert bad>0


def test_idle_gaps_match_exact_enumeration_and_mean_paths():
    targets={k:0 for k in ('SD1','SD2','WD1','WD2','none')}
    for p,x in _small_plants():
        flags=classify_state(*x,p)
        keys=[k for k in targets if flags.get(k,False) or (k=='none' and flags['label']=='none')]
        if not any(targets[k]<5 for k in keys): continue
        for k in keys: targets[k]+=1
        P=lambda s:{m:{n:s if m==n else 1-s for n in ('off','on')} for m in ('off','on')}
        plant=dict(p,PA=P(p['keepA']),PB=P(p['keepB']),dt=F(1))
        expected=sum(_prob(a,p['keepA'])*_prob(b,p['keepB'])*
                     (_cost(x,a,b,p,'Switch')-_cost(x,a,b,p,'Stay'))
                     for a,b in product(_paths(x[1],p['H']),_paths(x[3],p['H'])))
        assert gap_from_idle(x,plant)==expected
        assert gap_from_idle(x,plant,'M0')==_m0_cost(x,p,'Switch')-_m0_cost(x,p,'Stay')
        if all(n>=5 for n in targets.values()): break
    assert min(targets.values())>=5


def test_precision_policy_preserves_true_oracle_and_requires_resolution():
    assert resolve_sign(F(-1,10**20))['action']=='Switch'
    assert resolve_sign(F(0))['action']=='Stay'
    assert resolve_sign(-1e-15,error_bound=1e-14)['action'] is None
    assert resolve_sign(0.,exact_zero=True)['action']=='Stay'
    with pytest.raises(ArithmeticError): resolve_sign(-1e-15,exact_zero=True)
    with pytest.raises(ValueError): resolve_sign(-1e-15)
    p=precision_summary([(0.,.9,True),(1e-15,.02,False),(1.,.08,False)],10)
    assert p['escalation_required'] and p['uncertified_band_mass']==.02
    assert not precision_summary([(0.,1.,True)],10)['escalation_required']


def test_N2_canonical_exact_and_tie_exception():
    rows=[(p,expected_cost(x,'Stay',CANON),expected_cost(x,'Switch',CANON),
           m0_cost(x,'Stay',CANON),m0_cost(x,'Switch',CANON)) for x,p in CANONICAL_BELIEF.items()]
    s=statistics(rows)
    assert s['L00']==F(59,8) and s['L01']==F(57,8)
    assert s['G_M']==F(1,4) and s['G_S_given_M1']==F(7,8)
    assert s['E_positive']==F(7,8) and s['E_negative']==F(9,8)
    assert s['model_bias']==F(1,2)
    zero=statistics([(F(1),5,5,6,5)])
    assert zero['a00']!=zero['a01'] and zero['G_M']==0


def test_N2_exact_grid_with_zero_margins():
    for a,b,c,d in product(range(-2,3),repeat=4):
        for p in (F(1,4),F(1,2),F(3,4)):
            s=statistics([(p,5,5+a,5,5+c),(1-p,5,5+b,5,5+d)])
            assert (s['G_S_given_M1']>0)==(min(a,b)<0<max(a,b))
    with pytest.raises(ValueError): statistics([])
