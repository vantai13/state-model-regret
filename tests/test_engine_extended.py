"""Doan Van Tai — asymmetric ledgers, diagnostics, validation and exercises."""
from dataclasses import replace
from fractions import Fraction as F

import pytest

from experiments.A00_engine.factorial_core import Side, aggregate
from tests.test_engine_core import canonical, side, E7


def test_E2_and_E5_asymmetric_ledgers():
    A = side([F(1, 2)] * 2, [0, 1], [1, 0], [10, 10])
    B = side([1], [-1], [-F(1, 2)])
    # The exact E2/E5 ledgers are represented with a constant B offset.
    E2 = aggregate(side([F(1, 2)] * 2, [0, 4], [0, 3], [10, 10]),
                   side([1], [-3], [-1]))
    assert [E2['L'][k] for k in ('00', '01', '10', '11')] == [10, 9, F(17, 2), F(17, 2)]
    assert (E2['G']['G_S'], E2['G']['G_M'], E2['G']['Gamma']) == (F(3, 2), 1, -1)
    E5 = aggregate(side([F(1, 2)] * 2, [0, 3], [F(3, 2), 0], [10, 10]),
                   side([1], [-1], [-F(1, 2)]))
    assert [E5['L'][k] for k in ('00', '01', '10', '11')] == [10, 10, 11, F(19, 2)]
    assert (E5['G']['G_S'], E5['G']['Gamma']) == (-1, F(3, 2))


def test_I_delta_and_weighted_quantiles_L15_E7():
    r = aggregate(*canonical()[:2])
    assert r['E_abs_I_delta'] == F(1, 4)
    assert r['quantiles_abs_I_delta'] == {'1/2': 0, '9/10': F(1, 2), '99/100': F(1, 2)}
    e = aggregate(*E7)
    assert e['E_abs_I_delta'] == F(9, 8)
    assert e['quantiles_abs_delta'] == {'1/2': 1, '9/10': 3, '99/100': 3}


def test_E7_modified_prediction_exercise():
    A, B = E7
    r = aggregate(A, replace(B, dh=(F(-2), F(-2, 5))))
    assert r['L']['10'] == -1 and r['G']['G_M_S1'] == 0
    assert r['G']['Gamma'] == 0
    assert (r['G']['F'], r['G']['V']) == (F(3, 8), F(3, 8))


def test_WD_is_not_necessarily_zero_control():
    r = aggregate(side([1], [0], [0]), side([1], [-1], [0]))
    assert r['G']['G_S_M1'] == 0 and r['G']['G_M'] == 1


def test_side_rejects_invalid_input_and_unknown_queue():
    with pytest.raises(ValueError):
        side([1], [-1], [0]).check('A')
    with pytest.raises(ValueError):
        side([F(1, 2)], [1], [1]).check('A')
    with pytest.raises(ValueError):
        side([1], [1], [1]).check('C')
    with pytest.raises(ValueError):
        Side((F(1),), (), (), (), ()).check('A')
