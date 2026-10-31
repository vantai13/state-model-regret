"""P-clip: independent finite paths, conditional means and initial-mode boundary."""
from fractions import Fraction as F
import itertools

import numpy as np
import pytest

from experiments.P4_07_clipping import check_clipping as C
from experiments.R3R_08_population_numerics import piecewise as P


def any_reflection(H, increments, q0, m0):
    # Explicit path support, independent of minimum-partial-sum threshold.
    for flips in itertools.product((0,1),repeat=H-1):
        q,m = F(q0),m0
        for k in range(H):
            if k and flips[k-1]:
                m=1-m
            if q+increments[m] < 0:
                return True
            q=max(F(0),q+increments[m])
    return False


@pytest.mark.parametrize('H',range(1,6))
@pytest.mark.parametrize('inc',[(-2,1),(-1,3),(-3,-1),(1,2)])
def test_mode_aware_threshold_matches_all_future_paths(H,inc):
    for mode in (0,1):
        t=C.threshold(H,inc,mode)
        for q in (F(0),F(1,2),t,max(F(0),t-F(1,2)),t+1):
            assert (q<t) is any_reflection(H,inc,q,mode)


def test_lesson_hD_iff_fails_for_initial_ON_single_slot():
    inc=(F(-7,20),F(5,20))
    assert 0 < F(7,20)  # lesson's mode-independent hD cover includes this point
    assert C.threshold(1,inc,1)==0
    assert not any_reflection(1,inc,0,1)
    assert C.threshold(10,inc,0)==F(7,2)
    assert C.threshold(10,inc,1)==F(29,10)  # hD-12dt


@pytest.mark.parametrize('H,inc,p',[(1,(-2,1),F(3,4)),(5,(-2,1),F(3,4)),(8,(-3,2),F(9,10))])
def test_exact_cost_jensen_and_no_clipping_equality(H,inc,p):
    for m in (0,1):
        for q in (0,1,2,H*max(map(abs,inc))):
            actual=C.exact_reference(H,inc,p,q,m)
            mean=C.rational_mean(H,inc,p,q,m)
            assert actual>=mean
            if q>=C.threshold(H,inc,m):
                assert actual==mean


def test_clipping_is_not_sufficient_for_error():
    assert any_reflection(1,(-2,1),0,0)
    assert C.exact_reference(1,(-2,1),F(3,4),0,0)==C.rational_mean(1,(-2,1),F(3,4),0,0)==0


def test_unconditional_mean_fails_even_without_reflection():
    # ModeOFF persists probabilistically: correct conditional expected sum=-3.0625.
    correct=C.exact_reference(4,(-2,1),F(3,4),100,0)
    conditional=C.rational_mean(4,(-2,1),F(3,4),100,0)
    unconditional=4*F(100)+F(sum((-2,1)),2)*sum(range(1,5))
    assert correct==conditional
    assert correct!=unconditional


@pytest.mark.parametrize('q',[0,1,20,70])
def test_native_idle_jensen_and_saturated_busy_tail(q):
    H,inc,p=10,(-7,5),F(3,4)
    true=P.idle(H,inc,p,error_budget_raw=np.longdouble('1e-10'))
    mean=P.mean_idle(H,inc,p)
    for m in (0,1):
        w=P.evaluate(true,np.array([q]),m)[0]
        v=P.evaluate(mean,np.array([q]),m)[0]
        assert w-v>=-true['error']-mean['error']
        if q>=C.threshold(H,inc,m):
            assert w==v==0


def test_per_action_underestimation_does_not_fix_gap_error_sign():
    p,H=F(3,4),4
    stay=C.exact_reference(H,(-3,1),p,0,0)
    mstay=C.rational_mean(H,(-3,1),p,0,0)
    switch=C.exact_reference(H,(-1,3),p,0,0)
    mswitch=C.rational_mean(H,(-1,3),p,0,0)
    assert stay>=mstay and switch>=mswitch
    gap_error=(mswitch-mstay)-(switch-stay)
    assert gap_error!=0
    assert -gap_error==((mstay-mswitch)-(stay-switch))


def test_constant_predictor_has_no_interpretable_spearman():
    rows=[dict(P_clip=1.,S_clip_over_sigma=1.,GM_S1_pctC=float(i),abs_Gamma_pctC=float(i*i)) for i in range(4)]
    result=C.associations(rows,1e-9)
    assert all(r['rho'] is None and r['status']=='DEGENERATE_RANGE' for r in result.values())


def test_lesson_enumeration_normalizes_H_minus_one_transitions():
    rows=C.enumerate_example()
    assert len(rows)==4
    assert all(r['paths']==512 and abs(r['probability_mass']-1)<1e-12 for r in rows)
    assert all(abs(r['M1_minus_M0'])<1e-12 for r in rows if r['outside'])
    assert all(r['M1_minus_M0']>0 for r in rows if not r['outside'])
