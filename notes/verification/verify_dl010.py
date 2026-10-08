"""Doan Van Tai — kiểm hữu hạn DL-010, không dùng seed/network simulation.

Chạy từ gốc repo: python notes/verification/verify_dl010.py
Kết quả kiểm đại số không thay bài tính tay hoặc người đọc độc lập.
"""

import json
from fractions import Fraction as F
from itertools import product


def rollout(q0, arrivals, capacity=(3, 3), u=2, switch=False):
    q = list(q0)
    cost = 0
    idle = []
    managed = (0, u) if switch else (u, 0)
    for background in arrivals:
        z = [q[l] + background[l] + managed[l] - capacity[l] for l in range(2)]
        idle.append(sum(max(0, -v) for v in z))
        q = [max(0, v) for v in z]
        cost += sum(q)
    return cost, idle


def mode_paths(initial, horizon=3):
    transition = ((F(3, 4), F(1, 4)), (F(1, 2), F(1, 2)))
    for tail in product((0, 1), repeat=horizon - 1):
        modes = (initial,) + tail
        probability = F(1)
        for prev, curr in zip(modes, modes[1:]):
            probability *= transition[prev][curr]
        yield tuple(4 * mode for mode in modes), probability


def verify():
    examples = []
    for q0, arrivals, expected in [
        ((10, 10), ((2, 1), (2, 1)), (37, 37)),
        ((10, 0), ((2, 0), (2, 0)), (23, 17)),
    ]:
        costs = tuple(rollout(q0, arrivals, switch=a)[0] for a in (False, True))
        assert costs == expected
        examples.append({"q0": q0, "stay": costs[0], "switch": costs[1]})

    pairs = no_idle = 0
    for q0 in product((0, 2, 10), repeat=2):
        for capacity in product((2, 3), repeat=2):
            for u in (0, 2):
                for flat in product((0, 1, 4), repeat=4):
                    arrivals = (flat[:2], flat[2:])
                    stay, idle_stay = rollout(q0, arrivals, capacity, u)
                    switch, idle_switch = rollout(q0, arrivals, capacity, u, True)
                    weighted_idle = sum((2 - j) * (b - a) for j, (a, b) in enumerate(zip(idle_stay, idle_switch)))
                    assert switch - stay == weighted_idle
                    pairs += 1
                    if not any(idle_stay + idle_switch):
                        assert switch == stay
                        # Any of the four pipelines' actions has the same true cost.
                        for actions in product((False, True), repeat=4):
                            costs = [switch if a else stay for a in actions]
                            assert costs == [stay] * 4
                            assert costs[1] + costs[2] - costs[0] - costs[3] == 0
                        no_idle += 1

    jensen = 0
    strict = 0
    for q0 in product((0, 2, 10), repeat=2):
        for initial in product((0, 1), repeat=2):
            paths = []
            for (a, pa), (b, pb) in product(mode_paths(initial[0]), mode_paths(initial[1])):
                paths.append((tuple(zip(a, b)), pa * pb))
            assert sum(p for _, p in paths) == 1
            means = tuple(tuple(sum(p * arrivals[k][l] for arrivals, p in paths) for l in range(2)) for k in range(3))
            for action in (False, True):
                mean_cost = rollout(q0, means, switch=action)[0]
                exact_cost = sum(p * rollout(q0, arrivals, switch=action)[0] for arrivals, p in paths)
                assert mean_cost <= exact_cost
                jensen += 1
                strict += mean_cost < exact_cost

    return {
        "method": "finite enumeration; exact integers/Fractions; horizon 2 (conservation), 3 (Markov/Jensen)",
        "examples": examples,
        "conservation_action_pairs": pairs,
        "no_idle_pairs": no_idle,
        "negative_control_action_assignments_per_pair": 16,
        "jensen_state_action_cases": jensen,
        "jensen_strict_cases": strict,
        "violations": 0,
        "scope": "declared toy grids only; not independent review, author understanding or network evidence",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
