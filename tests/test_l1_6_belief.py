"""Doan Van Tai — sixteen collected tests from L1.6 Part D (including priors)."""
from fractions import Fraction as F
from itertools import product

import pytest

from experiments.lessons.l1_3_expected_cost import CANON, expected_cost, generate_episodes
from experiments.lessons.l1_4_factorial import contrasts
from experiments.lessons.l1_5_identity import i_delta
from experiments.lessons.l1_6_belief import (
    belief, cost_with_current_backlog, factorial_end_to_end, m0_cost, predict,
)
from golden_phase1 import (
    BELIEF_TAU2, BELIEF_TWO_OBS_EMPTY, BELIEF_TWO_OBS_UP, CANONICAL_BELIEF,
    FACTORIAL_CONTRASTS, FACTORIAL_MEANS, M0_COSTS, X_A, X_B, X_C, X_D,
)

XS = (X_A, X_B, X_C, X_D)
P34 = dict(CANON, p_onon=F(3,4), p_offoff=F(3,4))


def C(L):
    return contrasts(L["00"], L["10"], L["01"], L["11"])


def test_belief_canonical_one_observation():
    b = belief([(-1,(2,0))], CANON, F(1,2))
    assert b == CANONICAL_BELIEF
    assert b == generate_episodes((2,0), 1, CANON, F(1,2))


def test_belief_canonical_older_observation_tau2():
    assert belief([(-2,(2,0))], CANON, F(1,2)) == BELIEF_TAU2


def test_belief_two_observations_eliminates_and_renormalises():
    history = [(-2,(2,0)),(-1,(2,2))]
    assert belief(history, P34, F(1,2)) == BELIEF_TWO_OBS_UP
    assert belief(history, P34, F(1,4)) == BELIEF_TWO_OBS_UP
    assert belief([(-2,(2,0)),(-1,(2,0))], P34, F(1,2)) == BELIEF_TWO_OBS_EMPTY


def test_belief_is_joint_not_product_of_marginals():
    b = belief([(-2,(2,0)),(-1,(2,2))], P34, F(1,2))
    p_q4 = sum(p for x,p in b.items() if x[1] == 4)
    p_on = sum(p for x,p in b.items() if x[2] == "on")
    assert p_q4*p_on == F(15,32) != b[(2,4,"on")] == F(9,16)


def test_impossible_observation_raises():
    with pytest.raises(ValueError):
        belief([(-2,(2,0)),(-1,(2,1))], P34, F(1,2))


def test_m0_golden_canonical():
    for x, costs in M0_COSTS.items():
        assert tuple(m0_cost(x,a,CANON) for a in ("Stay","Switch")) == costs


def test_m0_exact_when_no_queue_can_empty():
    for x in ((10,10,"on"),(10,10,"off")):
        for a in ("Stay","Switch"):
            assert m0_cost(x,a,CANON) == expected_cost(x,a,CANON)


def _grid(prior_D):
    for ron,(p,s),yA,yB,u in product((3,4,5,6),
            ((F(1,2),F(1,2)),(F(3,4),F(3,4)),(F(3,4),F(1,2))), (0,2,4),(0,1,2,3),(1,2)):
        th = dict(CANON, rate_on=ron, p_onon=p, p_offoff=s, u=u)
        yield th,(yA,yB),generate_episodes((yA,yB),1,th,prior_D)


def test_property_7h_m0_never_above_m1_on_grid():
    for th,_,D in _grid(F(1,2)):
        for x in D:
            for a in ("Stay","Switch"):
                assert m0_cost(x,a,th) <= expected_cost(x,a,th)


def test_predict_averages_predictions_not_states():
    b = belief([(-1,(2,0))],CANON,F(1,2))
    assert tuple(predict(b,a,"M0",CANON) for a in ("Stay","Switch")) == (F(27,4),F(7))
    assert tuple(predict(b,a,"M1",CANON) for a in ("Stay","Switch")) == (F(59,8),F(57,8))


def test_end_to_end_canonical_matches_L14():
    D = generate_episodes((2,0),1,CANON,F(1,2))
    L,_,_ = factorial_end_to_end([(-1,(2,0))],CANON,F(1,2),D)
    assert L == FACTORIAL_MEANS and C(L) == FACTORIAL_CONTRASTS


@pytest.mark.parametrize("prior_D",[F(1,4),F(1,2),F(3,4)])
def test_property_7c_bayes_decision_on_grid(prior_D):
    for th,y,D in _grid(prior_D):
        L,_,b = factorial_end_to_end([(-1,y)],th,prior_D,D)
        best = min(sum(p*expected_cost(x,a,th) for x,p in D.items()) for a in ("Stay","Switch"))
        assert L["01"] == best
        assert C(L)["G_M"] >= 0 and C(L)["G_S|M1"] >= 0
        d00 = predict(b,"Switch","M0",th)-predict(b,"Stay","M0",th)
        d01 = predict(b,"Switch","M1",th)-predict(b,"Stay","M1",th)
        mean = sum(p*i_delta(d00,m0_cost(x,"Switch",th)-m0_cost(x,"Stay",th),d01,
                            expected_cost(x,"Switch",th)-expected_cost(x,"Stay",th)) for x,p in D.items())
        assert mean == 0


def test_the_7c_check_can_fail_when_prior_is_wrong():
    negatives = 0
    for prior_D in (F(1,4),F(3,4)):
        for th,y,D in _grid(prior_D):
            L,_,_ = factorial_end_to_end([(-1,y)],th,F(1,2),D)
            negatives += C(L)["G_M"] < 0
    assert negatives == 5


def test_tau0_cell_splits_G_S():
    D = generate_episodes((2,0),1,CANON,F(1,2))
    for model in ("M0","M1"):
        assert cost_with_current_backlog(D,CANON,model) == 7


def test_persistence_variants_golden():
    for th,prior,gs,gm in ((P34,F(1,2),F(31,32),F(0)),(P34,F(1,4),F(45,64),F(0)),
            (dict(CANON,p_onon=F(11,20),p_offoff=F(11,20)),F(1,2),F(979,800),F(13,40))):
        D = generate_episodes((2,0),1,th,prior)
        L,_,_ = factorial_end_to_end([(-1,(2,0))],th,prior,D)
        assert (C(L)["G_S"],C(L)["G_M"]) == (gs,gm)
