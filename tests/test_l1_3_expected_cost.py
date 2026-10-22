"""Doan Van Tai — the nine L1.3 propositions from the supplied lesson."""
from fractions import Fraction as F

from experiments.lessons.l1_2_queue import two_queue_cost
from experiments.lessons.l1_3_expected_cost import (
    CANON, expected_cost, futures, generate_episodes, mode_paths, oracle, p_idle,
)
from golden_phase1 import ASYMMETRIC_EXPECTED_COSTS, EXPECTED_COSTS, X_A, X_B, X_C, X_D


def test_mode_path_probabilities_sum_to_one():
    for initial in ("on", "off"):
        for p, s in ((F(1, 2), F(1, 2)), (F(3, 4), F(1, 4)), (F(1), F(0))):
            assert sum(pr for _, pr in mode_paths(initial, 3, p, s)) == 1


def test_episodes_generated_from_plant_D12():
    assert generate_episodes((2, 0), 1, CANON, F(1, 2)) == {
        X_A: F(1, 4), X_B: F(1, 4), X_C: F(1, 4), X_D: F(1, 4)}


def test_expected_costs_match_hand_calculation():
    # Golden answers supplied in the lesson, not a record of completed author exercises.
    for state, (stay, switch) in EXPECTED_COSTS.items():
        assert expected_cost(state, "Stay", CANON) == stay
        assert expected_cost(state, "Switch", CANON) == switch


def test_oracle_rule_on_means_stay_off_means_switch():
    for state in EXPECTED_COSTS:
        assert oracle(state, CANON)[0] == ("Stay" if state[2] == "on" else "Switch")


def test_delta_equals_expected_weighted_idle_difference():
    horizon = CANON["H"]
    for state in EXPECTED_COSTS:
        rhs = F(0)
        for bB, pr in futures(state, CANON):
            args = (state[:2], [CANON["bA"]] * horizon, bB, CANON["u"], CANON["cA"], CANON["cB"])
            _, idle_stay = two_queue_cost(*args, "Stay")
            _, idle_switch = two_queue_cost(*args, "Switch")
            rhs += pr * sum((horizon-j)*(sw-st) for j, (sw, st) in enumerate(zip(idle_switch, idle_stay)))
        assert oracle(state, CANON)[1] == rhs


def test_zero_action_gives_zero_delta():
    for state in EXPECTED_COSTS:
        assert oracle(state, dict(CANON, u=0)) == ("Stay", 0)


def test_non_degenerate_every_state():
    for state in EXPECTED_COSTS:
        assert p_idle(state, "Stay", CANON) > 0 or p_idle(state, "Switch", CANON) > 0
        assert oracle(state, CANON)[1] != 0


def test_oracle_cost_and_fixed_rule_regrets():
    episodes = generate_episodes((2, 0), 1, CANON, F(1, 2))
    l_star = sum(pr * min(expected_cost(x, action, CANON) for action in ("Stay", "Switch"))
                 for x, pr in episodes.items())
    l_stay = sum(pr * expected_cost(x, "Stay", CANON) for x, pr in episodes.items())
    l_switch = sum(pr * expected_cost(x, "Switch", CANON) for x, pr in episodes.items())
    assert l_star == F(25, 4)
    assert l_stay - l_star == F(9, 8)
    assert l_switch - l_star == F(7, 8)


def test_asymmetric_chain_weights_branches_by_probability():
    th = dict(CANON, p_onon=F(3, 4), p_offoff=F(1, 4))
    assert expected_cost(X_B, "Stay", th) == ASYMMETRIC_EXPECTED_COSTS[0]
    assert expected_cost(X_B, "Switch", th) == ASYMMETRIC_EXPECTED_COSTS[1]
