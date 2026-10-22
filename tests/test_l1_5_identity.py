"""Doan Van Tai — eleven lesson tests; the mean-zero checker is independent."""
from fractions import Fraction as F
from itertools import product

from experiments.lessons.l1_3_expected_cost import CANON, expected_cost
from experiments.lessons.l1_4_factorial import choose
from experiments.lessons.l1_5_identity import (
    belief_average, direct_regret, i_delta, i_delta_per_state, regret_identity,
)
from golden_phase1 import (
    CANONICAL_BELIEF, CANONICAL_I_DELTA, DELTA_HAT_10, IDENTITY_REGRETS,
    TIE_REGRET_GOLDEN, X_A, X_B, X_C, X_D,
)

XS = (X_A, X_B, X_C, X_D)
BELIEF = CANONICAL_BELIEF
J = {x: tuple(expected_cost(x, a, CANON) for a in ("Stay", "Switch")) for x in XS}
DELTA = {x: J[x][1]-J[x][0] for x in XS}
DHAT_M0 = DELTA_HAT_10


def test_F5_matches_direct_regret_on_canonical_16_pairs():
    d00, d01 = belief_average(BELIEF, DHAT_M0), belief_average(BELIEF, DELTA)
    for x in XS:
        dhats = {"00": d00, "10": DHAT_M0[x], "01": d01, "11": DELTA[x]}
        got = {cell: regret_identity(DELTA[x], dh) for cell, dh in dhats.items()}
        assert got == IDENTITY_REGRETS[x]
        assert got == {cell: direct_regret(*J[x], dh) for cell, dh in dhats.items()}


def test_F5_tie_term_running_example():
    for delta, predicted, expected in TIE_REGRET_GOLDEN:
        assert regret_identity(delta, predicted) == expected
        assert direct_regret(F(4), F(4)+delta, predicted) == expected


def test_F5_equals_direct_regret_on_grid_including_ties():
    values = [F(k, 2) for k in range(-4, 5)]
    for d, dh in product(values, repeat=2):
        assert regret_identity(d, dh) == direct_regret(F(10), F(10)+d, dh), (d, dh)


def test_consistency_is_not_regret():
    for dh, expected_regret in ((F(1, 4), F(9, 8)), (F(-1, 4), F(7, 8))):
        consistency = sum(BELIEF[x] for x in XS
                          if choose(dh) == ("Switch" if DELTA[x] < 0 else "Stay"))
        regret = sum(BELIEF[x]*regret_identity(DELTA[x], dh) for x in XS)
        assert consistency == F(1, 2) and regret == expected_regret


def test_i_delta_canonical_golden():
    assert i_delta_per_state(BELIEF, DELTA, DHAT_M0) == CANONICAL_I_DELTA


def test_i_delta_equals_belief_mean_error_minus_state_error():
    values = i_delta_per_state(BELIEF, DELTA, DHAT_M0)
    errors = {x: DHAT_M0[x]-DELTA[x] for x in XS}
    for x in XS:
        assert values[x] == belief_average(BELIEF, errors)-errors[x]


def test_mean_i_delta_given_y_is_zero_canonical():
    assert belief_average(BELIEF, i_delta_per_state(BELIEF, DELTA, DHAT_M0)) == 0


def test_mean_zero_holds_for_any_belief_and_any_numbers():
    states = ("s1", "s2", "s3")
    beliefs = ((F(1, 3),)*3, (F(1, 2), F(1, 3), F(1, 6)), (F(7, 10), F(1, 10), F(1, 5)))
    values = [F(k, 2) for k in (-3, 0, 1, 4)]
    for weights in beliefs:
        b = dict(zip(states, weights))
        for d in product(values, repeat=3):
            for m in product(values, repeat=3):
                interaction = i_delta_per_state(b, dict(zip(states, d)), dict(zip(states, m)))
                assert sum(wi * interaction[s] for wi, s in zip(weights, states)) == 0


def test_mean_nonzero_when_belief_does_not_match_D():
    # Specific mismatch with power to detect it; not a universal D != belief claim.
    distribution = dict(zip(XS, (F(3, 8), F(1, 8), F(3, 8), F(1, 8))))
    interaction = i_delta_per_state(BELIEF, DELTA, DHAT_M0)
    assert belief_average(distribution, interaction) != 0


def test_limitation_grouping_by_true_mode_is_not_zero():
    interaction = i_delta_per_state(BELIEF, DELTA, DHAT_M0)
    on = [interaction[x] for x in XS if x[2] == "on"]
    off = [interaction[x] for x in XS if x[2] == "off"]
    assert sum(on)/len(on) == F(1, 4) and sum(off)/len(off) == F(-1, 4)


def test_dispersion_is_the_informative_diagnostic():
    interaction = i_delta_per_state(BELIEF, DELTA, DHAT_M0)
    assert belief_average(BELIEF, {x: abs(v) for x, v in interaction.items()}) == F(1, 4)
