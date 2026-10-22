"""Doan Van Tai — extra exact cases for multi-step costs and D12 aggregation."""
from fractions import Fraction as F

from experiments.lessons.l1_2_queue import two_queue_cost
from experiments.lessons.l1_3_expected_cost import CANON, expected_cost, futures, generate_episodes
from golden_phase1 import H3_BRANCH_COSTS, H3_EXPECTED_COSTS, TAU2_EPISODES, X_D


def test_three_slot_costs_match_explicit_branch_table():
    th = dict(CANON, H=3)
    branches = list(futures(X_D, th))
    assert len(branches) == 4 and all(pr == F(1, 4) for _, pr in branches)
    for bB, _ in branches:
        tail = tuple("on" if b == 5 else "off" for b in bB[1:])
        assert bB[0] == 0  # Current mode is fixed.
        costs = tuple(two_queue_cost(X_D[:2], [1]*3, bB, 2, 3, 3, a)[0] for a in ("Stay", "Switch"))
        assert costs == H3_BRANCH_COSTS[tail]
    assert tuple(expected_cost(X_D, a, th) for a in ("Stay", "Switch")) == H3_EXPECTED_COSTS


def test_zero_age_preserves_backlog_and_declared_prior():
    assert generate_episodes((2, 0), 0, CANON, F(3, 4)) == {
        (2, 0, "on"): F(3, 4), (2, 0, "off"): F(1, 4)}


def test_two_slot_age_aggregates_paths_with_unequal_prior():
    th = dict(CANON, p_onon=F(3, 4), p_offoff=F(1, 4))
    episodes = generate_episodes((2, 0), 2, th, F(3, 4))
    assert episodes == TAU2_EPISODES
    assert sum(episodes.values()) == 1
