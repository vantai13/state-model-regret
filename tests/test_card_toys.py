"""Doan Van Tai — E8, sister bounds and mode-persistence toy arithmetic."""
from fractions import Fraction as F

from experiments.A00_engine.factorial_core import aggregate
from experiments.A00_engine.precision import enclose
from experiments.A03_card.toy_checks import E8, persistence_rows, check_ledger_bound
from tests.test_engine_core import E7


def test_E8_harm_route_is_not_mechanism_support():
    r = aggregate(*E8())
    assert (r['G']['G_S'], r['G']['Gamma'], r['G']['F'], r['G']['V']) == (F(-1, 4), F(1, 4), F(-7, 8), F(5, 8))
    assert r['G']['G_S_M1'] == 0 and r['p_sw'] == 1


def test_Eabs_error_golden_and_numeric_enclosure():
    A, B = E7
    r = aggregate(A, B)
    assert r['E_abs_e_M'] == F(9, 8)
    assert r['G']['G_M_S1'] <= r['E_abs_e_M']
    e = enclose(A, B, r)
    assert e['intervals']['E_abs_e_M'][0] <= F(9, 8) <= e['intervals']['E_abs_e_M'][1]


def test_4000_ledgers_statewise_bound_and_independent_sum():
    r = check_ledger_bound()
    assert r['cases'] == 4000 and r['violations'] == r['independent_abs_error_mismatches'] == 0


def test_persistence_and_A_side_conjecture():
    rows = persistence_rows()
    assert len(rows) == 16
    lookup = {(r['toy'], r['keep'], r['mode']): r for r in rows}
    b = lookup['B_bursty', F(3, 4), 'off']
    assert (b['Delta'], b['Delta_hat'], b['e_M']) == (F(-57, 8), F(-37, 8), F(5, 2))
    assert lookup['B_bursty', F(1, 2), 'off']['e_M'] == b['e_M']
    for row in rows:
        if row['toy'] == 'B_bursty':
            assert row['e_M'] >= 0
        else:
            assert row['e_M'] <= 0
        if row['keep'] == 1:
            assert row['e_M'] == 0
        assert row['oracle'] == row['S1M0']
