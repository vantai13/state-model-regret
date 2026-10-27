"""Doan Van Tai — decision discontinuities and numerical impact bounds."""
import random
from fractions import Fraction as F

import numpy as np

from experiments.A00_engine.factorial_core import Side, aggregate
from experiments.A00_engine.precision import cut_with_bound, enclose
from experiments.A00_engine.evaluate import evaluate_sides
from tests.test_engine_core import side, E7


def test_2000_perturbed_cut_trials():
    rng = random.Random(20261029)
    for _ in range(2000):
        n, m = rng.randint(1, 5), rng.randint(1, 5)
        ak, bk = ([F(rng.randint(-10, 10), 4) for _ in range(k)] for k in (n, m))
        av, bv = ([F(rng.randint(-20, 20), 4) for _ in range(k)] for k in (n, m))
        ap, bp = [F(1, n)] * n, [F(1, m)] * m
        error = F(rng.randint(0, 5), 10)
        value, unresolved, impact, arithmetic = cut_with_bound(ak, av, ap, bk, bv, bp, float(error))
        da = [F(rng.randint(-10, 10), 20) * error for _ in ak]
        db = [F(rng.randint(-10, 10), 20) * error for _ in bk]
        truth = sum(ap[i] * bp[j] * (av[i] + bv[j]) for i in range(n) for j in range(m)
                    if ak[i] + da[i] + bk[j] + db[j] < 0)
        assert abs(value - float(truth)) <= impact + arithmetic
        assert 0 <= unresolved <= 1 + 1e-15


def test_unresolved_S0_returns_both_actions_and_HOLD():
    A = Side((np.longdouble(1),), (np.longdouble(2),), (np.longdouble(1),),
             (np.longdouble(10),), (0,), {'dh': .1})
    B = Side((np.longdouble(1),), (np.longdouble(-5),), (np.longdouble(-1),),
             (np.longdouble(10),), (0,), {'dh': .1})
    r = evaluate_sides(A, B, refinement=1, dt=F(1))
    assert r['a00'] is None and len(r['L00_alternatives']) == 2
    assert r['status'] == 'HOLD_PRECISION'
    assert r['intervals']['L00'][0] <= 17 <= r['intervals']['L00'][1]
    assert r['intervals']['L00'][0] <= 20 <= r['intervals']['L00'][1]


def test_small_negative_oracle_is_not_clamped():
    A, B = side([1], [0], [0], [10]), side([1], ['-1/1000000000000'], [-2], [10])
    r = aggregate(A, B)
    assert r['a01'] == 1 and r['p_sw'] == 1
    assert r['G']['G_M_S1'] == 0


def test_E7_interval_contains_exact_values_and_reports_three_bands():
    A, B = E7
    result = aggregate(A, B)
    bounds = enclose(A, B, result)
    for key in ('G_S', 'G_M', 'Gamma', 'F', 'V', 'E_abs_I_delta'):
        exact = result.get(key, result['G'].get(key))
        assert bounds['intervals'][key][0] <= exact <= bounds['intervals'][key][1]
    assert set(bounds['unresolved_mass']) == {'oracle', 'M0', 'D22'}


def test_joint_value_probability_and_D22_enclosures():
    # Independent perturbed input tables: probabilities, values and decisions.
    rng = random.Random(20261030)
    for _ in range(40):
        sides, perturbed = [], []
        for sign in (1, -1):
            values = [sign * F(rng.randint(1, 12), 2) for _ in range(2)]
            hats = [sign * F(rng.randint(1, 12), 2) for _ in range(2)]
            p = (F(1, 2), F(1, 2))
            sides.append(Side(p, tuple(values), tuple(hats), (F(20), F(20)), (0, 0),
                              dict(d=1/32, dh=1/32, jst=1/32, D_l1=1/64)))
            p2 = (F(1, 2) + F(1, 128), F(1, 2) - F(1, 128))
            perturbed.append(Side(p2, tuple(x + F(1, 64) for x in values),
                                  tuple(x - F(1, 64) for x in hats),
                                  (F(20) + F(1, 64), F(20) - F(1, 64)), (0, 0)))
        result = aggregate(*sides)
        bounds = enclose(*sides, result)
        truth = aggregate(*perturbed)
        for key in bounds['e_num']:
            if key.startswith('L'):
                value = truth['L'][key[1:]]
            elif key.startswith('R'):
                value = truth['R'][key[1:]]
            else:
                value = truth.get(key, truth['G'].get(key))
            lo, hi = bounds['intervals'][key]
            assert lo <= value <= hi, (key, value, (lo, hi))
        for name in ('abs_delta', 'abs_I_delta'):
            for q, value in truth['quantiles_' + name].items():
                lo, hi = bounds['quantile_intervals'][name][q]
                assert lo <= value <= hi
