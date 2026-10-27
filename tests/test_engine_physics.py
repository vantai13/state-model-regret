"""Doan Van Tai — independent finite-path/Fraction checks on synthetic plants."""
import random
from fractions import Fraction as F
from itertools import product

import numpy as np

from smr.exact import value_backward
from smr.idle_gap import weighted_idle, mean_weighted_idle
from experiments.A00_engine.physical import side_from_law
from experiments.A00_engine.evaluate import evaluate_sides


def canonical_native(ref=1):
    unit, dt = F(1, ref), F(1, ref)
    massA = np.zeros((2 * ref + 1, 2), dtype=np.longdouble)
    massA[2 * ref] = .5
    massB = np.zeros_like(massA)
    massB[0] = massB[2 * ref] = .25
    keep = F(1, 2) if ref == 1 else F(3, 4)
    A, detailA = side_from_law(unit, massA, rates=(F(1), F(1)), u_stay=F(2), u_switch=F(0),
                              capacity=F(3), H=2 * ref, dt=dt, keep=keep)
    B, detailB = side_from_law(unit, massB, rates=(F(0), F(5)), u_stay=F(0), u_switch=F(2),
                              capacity=F(3), H=2 * ref, dt=dt, keep=keep)
    return A, B, detailA, detailB


def test_native_canonical_and_context_reference():
    first = evaluate_sides(*canonical_native()[:2], refinement=1, dt=F(1))
    assert [float(first['L'][k]) for k in ('00', '01', '10', '11')] == [7.375, 7.125, 6.25, 6.25]
    assert (first['G']['F'], first['G']['V']) == (.375, .75)
    assert first['E_abs_I_delta'] == .25
    second = evaluate_sides(*canonical_native(2)[:2], refinement=2, dt=F(1, 2))
    assert first['C_ref'] != second['L']['11']
    assert second['C_ref'] == second['L']['11']
    assert second['reference_context'] == {'refinement': 2, 'dt_s': '1/2'}


def test_D7_known_mode_one_slot_has_no_model_difference():
    mass = np.zeros((2, 2), dtype=np.longdouble)
    mass[1] = [.25, .75]
    s, _ = side_from_law(F(1), mass, rates=(F(0), F(5)), u_stay=F(0), u_switch=F(2),
                          capacity=F(3), H=1, dt=F(1), keep=F(3, 4))
    assert s.d == s.dh


def test_zero_managed_traffic_has_exact_zero_contrasts():
    mass = np.array([[.5, .5]], dtype=np.longdouble)
    s, _ = side_from_law(F(1), mass, rates=(F(0), F(5)), u_stay=F(0), u_switch=F(0),
                          capacity=F(3), H=3, dt=F(1), keep=F(3, 4))
    assert all(s.bounds['zero']) and all(v == 0 for v in s.d + s.dh)
    result = evaluate_sides(s, s, refinement=1, dt=F(1))
    assert all(v == 0 for v in result['G'].values())


def test_float_conservation_is_exact_at_large_backlog():
    for q in (500, 500000):
        mass = np.zeros((q + 1, 2), dtype=np.longdouble)
        mass[q] = [.5, .5]
        for stay, switch in ((F(2), F(0)), (F(0), F(2))):
            s, _ = side_from_law(F(1), mass, rates=(F(1), F(1)), u_stay=stay, u_switch=switch,
                                  capacity=F(3), H=960, dt=F(1, 120), keep=F(3, 4), extended=False)
            assert all(v == 0 for v in s.d + s.dh)
            assert all(s.bounds['zero'])


def test_400_random_physical_plants_against_fraction():
    rng = random.Random(20261028)
    for _ in range(400):
        H, q, mode = rng.randint(1, 3), rng.randint(0, 5), rng.randrange(2)
        rates = (F(rng.randint(0, 2)), F(rng.randint(3, 6)))
        keep = rng.choice((F(1, 2), F(3, 4)))
        u = F(rng.randint(1, 2))
        stay, switch = (u, F(0)) if rng.randrange(2) else (F(0), u)
        mass = np.zeros((q + 1, 2), dtype=np.longdouble)
        mass[q, mode] = 1
        s, detail = side_from_law(F(1), mass, rates=rates, u_stay=stay, u_switch=switch,
                                  capacity=F(3), H=H, dt=F(1), keep=keep)
        P = {m: {n: keep if m == n else 1 - keep for n in (0, 1)} for m in (0, 1)}
        R = dict(enumerate(rates))
        true = {a: weighted_idle(q, mode, R, x, 3, H, P) for a, x in (('St', stay), ('Sw', switch))}
        mean = {a: mean_weighted_idle(q, mode, R, x, 3, H, P) for a, x in (('St', stay), ('Sw', switch))}
        costs = {a: value_backward(x, H, 3, R, P, [q], F(1))[q, mode]
                 for a, x in (('St', stay), ('Sw', switch))}
        assert abs(s.d[0] - float(true['Sw'] - true['St'])) <= s.bounds['d']
        assert abs(s.dh[0] - float(mean['Sw'] - mean['St'])) <= s.bounds['dh']
        assert abs(s.jst[0] - float(costs['St'])) <= s.bounds['jst']
        for a in ('St', 'Sw'):
            assert mean[a] <= true[a]
            assert abs(detail['W1'][a][0] - float(true[a])) <= detail['true_idle_error'][a]


def arrival_toy(A, B, H=1):
    """IID arrival toy for E1/E3/E6: slot-0 arrivals are unknown, unlike D7."""
    costs, idles = {}, {}
    for action in ('St', 'Sw'):
        total = W = F(0)
        paths = list(product(product(A, repeat=H), product(B, repeat=H)))
        for pa, pb in paths:
            qa, qb, C, I = F(2 if H == 2 else 0), F(0), F(0), F(0)
            for k, (a, b) in enumerate(zip(pa, pb)):
                a += 2 if action == 'St' else 0
                b += 2 if action == 'Sw' else 0
                I += (H - k) * (max(0, 3 - qa - a) + max(0, 3 - qb - b))
                qa, qb = max(0, qa + a - 3), max(0, qb + b - 3)
                C += qa + qb
            total += C / len(paths)
            W += I / len(paths)
        costs[action], idles[action] = total, W
    return costs, idles


def test_E1_E3_E6_as_arrival_law_examples_not_D7():
    C, W = arrival_toy((F(1),), (F(0), F(2)), H=2)
    assert (C['St'], C['Sw'], W['St'], W['Sw']) == (4, F(5, 4), 6, F(13, 4))
    for A, B, gap, gap_hat in (((2, 3), (1, 6), F(-1, 2), F(1, 2)),
                                ((1, 5), (F(5, 2),), F(1, 2), F(-1, 2)),
                                ((1, 5), (F(3, 2),), F(-1, 2), F(-3, 2))):
        C, W = arrival_toy(tuple(map(F, A)), tuple(map(F, B)))
        M, _ = arrival_toy((sum(map(F, A)) / len(A),), (sum(map(F, B)) / len(B),))
        assert C['Sw'] - C['St'] == W['Sw'] - W['St'] == gap
        assert M['Sw'] - M['St'] == gap_hat
