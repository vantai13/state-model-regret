"""Doan Van Tai — A01 pre-run tests use synthetic tables, never grid outcomes."""
from fractions import Fraction as F
import random

import numpy as np
import pytest

from experiments.A00_engine.factorial_core import Side, aggregate
from experiments.A01_null_refinement.controls import controlled, enumerated_oracle
from experiments.A01_null_refinement.run import c4_toys, control_row
from experiments.A01_null_refinement.selection import NAMES, choose_all_finer, choose_final, pair_check, diagnostics
from tests.test_engine_core import E7


def illustrative():
    # Compatible factorial ledger; changes .100,.840,.010,.005 as lesson table.
    out = []
    for m, gm, s, v in zip((1, 2, 4, 8, 16), (.8, .8, 0, 0, 0),
                           (1.4, 1.32, 1.28, 1.27, 1.265), (.6, .5, .46, .45, .448)):
        total = gm + s
        out.append(dict(m=m, Cref=100, G_S=total-v, G_M=gm, G_SM=total,
                        Gamma=v-gm, G_S_M1=s, G_M_S1=v))
    return out


def test_illustrative_first_pair_trap_and_complete_suffix():
    levels = illustrative()
    assert [pair_check(a, b)['pair_pass'] for a, b in zip(levels, levels[1:])] == [True, False, True, True]
    assert [pair_check(a, b)['max_change'] for a, b in zip(levels, levels[1:])] == pytest.approx([.1, .84, .01, .005])
    assert choose_all_finer(levels) == 8


def test_common_finest_and_oscillating_hold():
    x = illustrative(); y = illustrative()
    y[2]['G_M'] = .5
    assert choose_final({'M01': x, 'M09': y, 'M22': x}) == (16, {'M01': 8, 'M09': 16, 'M22': 8})
    for i, r in enumerate(y):
        r['G_M'] = (-1)**i
    assert choose_final({'M01': x, 'M09': y, 'M22': x})[0] == 'HOLD'


def test_minimum_reference_errors_and_missing_budget():
    a, b = illustrative()[:2]
    b['Cref'] = 1
    assert not pair_check(a, b)['pair_pass']
    b['Cref'] = 100; b['e_G_S'] = 1
    assert not pair_check(a, b)['pair_pass']
    b['e_G_S'] = 0; b['precision_ok'] = False
    assert not pair_check(a, b)['pair_pass']
    with pytest.raises(ValueError):
        choose_all_finer(illustrative()[:-1])
    with pytest.raises(ValueError):
        choose_final({'M01': illustrative()})


def test_rho_zero_infinite_and_diagnostic_only():
    x = illustrative()
    d = diagnostics(x)
    assert next(r for r in d if r['m'] == 4 and r['contrast'] == 'G_M')['rho_status'] == 'infinite'
    assert next(r for r in d if r['m'] == 16 and r['contrast'] == 'G_M')['rho_status'] == 'undefined_0_over_0'
    assert next(r for r in d if r['m'] == 4 and r['contrast'] == 'G_M_S1')['rho'] == pytest.approx(.4)


def test_changed_information_and_model_controls_E7():
    a, b = E7
    c2, c3 = controlled(a, b, 'C2'), controlled(a, b, 'C3')
    assert c2['exact_identity_pass'] and c3['exact_identity_pass']
    assert c2['G']['G_M'] == F(1, 8)
    assert c3['G']['G_S'] == F(5, 8)
    # C3's 11 need not be the true oracle after replacing its decision model.
    assert c3['L']['11'] != aggregate(a, b)['L']['11']
    assert aggregate(a, b)['G']['V'] == F(1, 4)


def test_independent_oracle_and_tie_actions():
    assert c4_toys()['pass_']
    assert enumerated_oracle(*E7)[0] == aggregate(*E7)['L']['11']


def test_random_WD_direct_zero_2000_cases():
    rng = random.Random(20261101)
    for _ in range(2000):
        n, m = rng.randint(1, 6), rng.randint(1, 6)
        pa = np.array([rng.random() for _ in range(n)], dtype=np.longdouble); pa /= pa.sum()
        pb = np.array([rng.random() for _ in range(m)], dtype=np.longdouble); pb /= pb.sum()
        a = Side(tuple(pa), (np.longdouble(0),)*n, (np.longdouble(0),)*n,
                 tuple(np.longdouble(rng.random()) for _ in range(n)), tuple(range(n)))
        b = Side(tuple(pb), tuple(-np.longdouble(rng.random()) for _ in range(m)),
                 (np.longdouble(0),)*m, (np.longdouble(1),)*m, tuple(range(m)))
        r = aggregate(a, b)
        assert r['E_pos'] == r['G']['G_S_M1'] == 0


def test_E9_is_random_arrival_toy_outside_D7_known_mode_slot0():
    def costs(uA, uB):
        return sum(F(max(0, a + uA - 3) + max(0, b + uB - 3), 4)
                   for a in (3, 4) for b in (1, 6))
    assert costs(2, 0) == 4 and costs(0, 2) == 3
    mean_st = max(0, F(7, 2) + 2 - 3) + max(0, F(7, 2) - 3)
    mean_sw = max(0, F(7, 2) - 3) + max(0, F(7, 2) + 2 - 3)
    assert mean_st == mean_sw == 3
