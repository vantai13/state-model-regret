"""The 11 L1.2 propositions: golden answers, invariants, negative controls."""
from fractions import Fraction
from itertools import product

from experiments.lessons.l1_2_queue import rollout, step, two_queue_cost
from golden_phase1 import ONE_QUEUE, TWO_QUEUE_CASES


def weighted_idle_diff(idle_sw, idle_st, dt=1):
    horizon = len(idle_sw)
    return dt * sum((horizon - j) * (sw - st)
                    for j, (sw, st) in enumerate(zip(idle_sw, idle_st)))


def test_hand_table_one_queue():
    case = ONE_QUEUE
    assert rollout(case["q0"], case["arrivals"], case["c"]) == (case["backlogs"], case["idles"])


def test_identity_linear_plus_idle():
    q0, c, arrivals = 4, 3, [2, 5, 1, 0, 0, 6]
    backlogs, idles = rollout(q0, arrivals, c)
    assert backlogs[-1] == q0 + sum(a - c for a in arrivals) + sum(idles)


def test_conservation_arrivals_minus_served():
    q0, c, arrivals = 4, 3, [2, 5, 1, 0, 0, 6]
    backlogs, idles = rollout(q0, arrivals, c)
    assert sum(arrivals) - sum(c - i for i in idles) == backlogs[-1] - q0


def test_complementarity_backlog_times_idle_is_zero():
    for q, a, c in product(range(6), range(6), range(1, 5)):
        q_next, idle = step(q, a, c)
        assert q_next >= 0 and idle >= 0
        assert q_next * idle == 0


def test_dl010_question_1_no_idle():
    case = TWO_QUEUE_CASES["dl010_no_idle"]
    stay, idle_st = two_queue_cost(action="Stay", **case["cfg"])
    switch, idle_sw = two_queue_cost(action="Switch", **case["cfg"])
    assert (stay, switch) == case["costs"]
    assert (idle_st, idle_sw) == case["idles"]


def test_dl010_question_2_with_idle():
    case = TWO_QUEUE_CASES["dl010_with_idle"]
    stay, idle_st = two_queue_cost(action="Stay", **case["cfg"])
    switch, idle_sw = two_queue_cost(action="Switch", **case["cfg"])
    assert (stay, switch) == case["costs"]
    assert (idle_st, idle_sw) == case["idles"]
    assert switch - stay == weighted_idle_diff(idle_sw, idle_st) == -6


def test_canonical_x_d_both_branches():
    for name in ("canonical_B_on", "canonical_B_off"):
        case = TWO_QUEUE_CASES[name]
        stay, idle_st = two_queue_cost(action="Stay", **case["cfg"])
        switch, idle_sw = two_queue_cost(action="Switch", **case["cfg"])
        assert (stay, switch) == case["costs"]
        assert switch - stay == weighted_idle_diff(idle_sw, idle_st)


def _grid():
    for qA, qB, cA, cB, u in product((0, 2, 10), (0, 2, 10), (2, 3), (2, 3), (0, 2)):
        for a0, a1, b0, b1 in product((0, 1, 4), repeat=4):
            yield dict(q0=(qA, qB), bA=[a0, a1], bB=[b0, b1], u=u, cA=cA, cB=cB)


def test_identity_cost_difference_on_exhaustive_grid():
    count = 0
    for cfg in _grid():
        stay, idle_st = two_queue_cost(action="Stay", **cfg)
        switch, idle_sw = two_queue_cost(action="Switch", **cfg)
        assert switch - stay == weighted_idle_diff(idle_sw, idle_st), cfg
        count += 1
    assert count == 5832


def test_negative_control_no_idle_means_equal_cost():
    count = 0
    for cfg in _grid():
        stay, idle_st = two_queue_cost(action="Stay", **cfg)
        switch, idle_sw = two_queue_cost(action="Switch", **cfg)
        if sum(idle_st) == sum(idle_sw) == 0:
            assert stay == switch, cfg
            count += 1
    assert count == 2048


def test_zero_action_control():
    for cfg in _grid():
        if cfg["u"] == 0:
            assert two_queue_cost(action="Stay", **cfg) == two_queue_cost(action="Switch", **cfg)


def test_dt_scales_cost_linearly():
    cfg = TWO_QUEUE_CASES["dl010_with_idle"]["cfg"]
    cost, _ = two_queue_cost(action="Stay", dt=1, **cfg)
    scaled, _ = two_queue_cost(action="Stay", dt=Fraction(1, 2), **cfg)
    assert scaled == Fraction(cost, 2)
