"""Doan Van Tai — known-answer normalization/ambiguity/finite-budget tests."""
from fractions import Fraction as F
import pytest
from experiments.R3R_05_contract.rules import (
    CONTRASTS,ratio_of_expectations,relative,conditional_weights,compare_levels,
    classify_threshold,escalation_levels,unresolved_bounds,numerical_coverage)


def test_ratio_of_expectations_is_not_average_of_snapshot_ratios():
    w=[F(1,2)]*2;g=[F(1,10)]*2;c=[1,19]
    assert ratio_of_expectations(w,g,c)==F(1,100)
    assert sum(p*x/y for p,x,y in zip(w,g,c))==F(1,19)
    assert ratio_of_expectations(w,g,[F(1,10),19])==F(2,191)


def test_population_conditional_example_has_known_correct_ratios():
    w=[F(1,2),F(3,10),F(1,5)];g=[0,F(4,5),0];c=[2,10,20]
    assert ratio_of_expectations(w,g,c)==F(3,100)
    conditional=conditional_weights(w,[False,True,True])
    assert conditional==[0,F(3,5),F(2,5)]
    assert ratio_of_expectations(conditional,g,c)==F(6,175)
    assert ratio_of_expectations(conditional_weights(w,[False,True,False]),g,c)==F(2,25)


def test_zero_denominators_remain_undefined():
    assert relative(0,0) is None and relative(1,0) is None
    with pytest.raises(ValueError):relative(1,-1)
    with pytest.raises(ValueError):conditional_weights([1,0],[False,True])


def test_same_absolute_gain_has_different_scales_without_or_rule():
    assert relative(2,400)==F(1,200)
    assert relative(2,5)==F(2,5)
    assert classify_threshold(relative(2,400),0)=='DOES_NOT_MEET'


def levels(g,cref=100):return dict(Cref=F(cref),**{k:F(g) for k in CONTRASTS})


def test_all_contrasts_and_denominator_drift_are_checked():
    assert compare_levels(levels('1'),levels('1.2'))['ready']
    assert not compare_levels(levels('1'),levels('1.3'))['ready']
    assert not compare_levels(levels('1'),levels('1',90))['ready']
    changed=levels('1');changed['Gamma']=F(2)
    assert not compare_levels(changed,levels('1'))['ready']


def test_small_joint_refinement_difference_can_hide_axis_cancellation():
    main=levels('1');coarseK=levels('1.4');coarse_dt=levels('.6')
    assert not compare_levels(main,coarseK)['ready']
    assert not compare_levels(main,coarse_dt)['ready']
    assert numerical_coverage(80,2)==dict(main=(80,2),coarse_K=(40,2),coarse_dt=(80,1))


def test_near_effect_and_harm_thresholds_escalate_then_unresolved():
    assert classify_threshold(F('0.0098'),F('.002'),remaining_steps=1)=='ESCALATE'
    assert classify_threshold(F('0.0098'),F('.002'))=='UNRESOLVED'
    assert classify_threshold(F('-0.0098'),F('.002'),kind='harm')=='UNRESOLVED'
    assert classify_threshold(F('0.012'),F('.001'))=='MEETS'
    assert classify_threshold(F('-0.012'),F('.001'),kind='harm')=='MEETS'


def test_equivalence_boundary_and_uncertified_zero_difference():
    assert classify_threshold(F('.0049'),F('.0002'),kind='equivalence')=='UNRESOLVED'
    assert classify_threshold(F('.003'),F('.001'),kind='equivalence')=='MEETS'
    assert classify_threshold(F('.01'),0)=='UNRESOLVED'
    assert classify_threshold(F('.01'),0,certified_exact=True)=='MEETS'
    assert classify_threshold(None,0)=='UNDEFINED'


def test_fixed_budget_cannot_restart_for_near_threshold():
    assert escalation_levels(80,2)==[(80,2),(160,2),(160,4)]
    with pytest.raises(ValueError):escalation_levels(40,1)


def test_unresolved_stratum_retains_full_denominator_and_strict_ten_percent():
    x=unresolved_bounds(7,2,1)
    assert x['status']=='APPLY_PREREG_TO_BOTH_EXTREMES'
    assert (x['rate_low'],x['rate_high'],x['unresolved_rate'])==(F(7,10),F(8,10),F(1,10))
    assert unresolved_bounds(7,1,2)['status']=='INCONCLUSIVE'
    assert unresolved_bounds(0,0,0)['status']=='INCONCLUSIVE'


def test_refinement_gap_is_not_an_error_certificate():
    # e(n)=.6/sqrt(n) gives adjacent gap below .25 but residual error above .25.
    import math
    gap=.6-.6/math.sqrt(2);remaining=.6/math.sqrt(2)
    assert gap<.25<remaining
