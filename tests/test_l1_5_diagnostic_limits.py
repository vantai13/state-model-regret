"""Doan Van Tai — the diagnostic can detect faults but cannot certify belief."""
from fractions import Fraction as F

from experiments.lessons.l1_5_identity import i_delta, i_delta_per_state
from golden_phase1 import CANONICAL_BELIEF, DELTA_HAT_10, EXPECTED_COSTS, X_A, X_B, X_C, X_D

XS = (X_A, X_B, X_C, X_D)
DELTA = {x: costs[1]-costs[0] for x, costs in EXPECTED_COSTS.items()}


def test_different_beliefs_between_cells_trigger_nonzero_mean():
    b00 = dict(zip(XS, (F(3, 8), F(1, 8), F(3, 8), F(1, 8))))
    b01 = CANONICAL_BELIEF
    d00 = sum(b00[x]*DELTA_HAT_10[x] for x in XS)
    d01 = sum(b01[x]*DELTA[x] for x in XS)
    interactions = {x: i_delta(d00, DELTA_HAT_10[x], d01, DELTA[x]) for x in XS}
    assert sum(CANONICAL_BELIEF[x]*interactions[x] for x in XS) == F(7, 8)


def test_zero_mean_does_not_certify_correct_belief():
    distribution = dict(zip(XS, (F(1, 4), F(1, 4), F(3, 8), F(1, 8))))
    assert distribution != CANONICAL_BELIEF
    interactions = i_delta_per_state(CANONICAL_BELIEF, DELTA, DELTA_HAT_10)
    assert any(v != 0 for v in interactions.values())
    assert sum(distribution[x]*interactions[x] for x in XS) == 0
