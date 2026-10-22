"""Doan Van Tai — extra history/off-rate checks against an evaluator reference."""
from fractions import Fraction as F

import pytest

from experiments.lessons.l1_3_expected_cost import CANON
from experiments.lessons.l1_6_belief import belief, m0_cost, predict
from experiments.lessons.l1_6_reference import history_reference


def test_longer_history_nonzero_off_rate_matches_evaluator():
    th = dict(CANON,rate_on=4,rate_off=1,p_onon=F(3,4),p_offoff=F(1,2),H=3)
    history = [(-3,(2,0)),(-2,(2,1)),(-1,(2,0))]
    D,evidence,_ = history_reference(history,th,F(1,4))
    expected = {(2,1,"on"):F(3,8),(2,1,"off"):F(1,8),
                (2,0,"on"):F(1,4),(2,0,"off"):F(1,4)}
    assert D == expected and evidence == F(1,16)
    assert belief(history,th,F(1,4)) == D


def test_three_slot_m0_conditions_nonzero_off_rate():
    # P_on = 0,1/2,5/8; background means 1,5/2,23/8.
    # Switch B backlog=0,3/2,27/8 -> cost39/8. A remains empty.
    th = dict(CANON,rate_on=4,rate_off=1,p_onon=F(3,4),p_offoff=F(1,2),H=3)
    assert m0_cost((0,0,"off"),"Stay",th) == 0
    assert m0_cost((0,0,"off"),"Switch",th) == F(39,8)


def test_history_schema_and_unknown_model_are_rejected():
    for history in ([],[(1,(2,0))],[(-1,(2,0)),(-2,(2,0))],
                    [(-1,(2,0)),(-1,(2,2))],[(-1,(-1,0))]):
        with pytest.raises(ValueError):
            belief(history,CANON,F(1,2))
    with pytest.raises(ValueError):
        predict({(2,0,"off"):F(1)},"Stay","m1",CANON)
