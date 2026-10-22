"""Doan Van Tai — cover non-additive patterns and the zero-margin control."""
from fractions import Fraction as F
from itertools import product

from experiments.lessons.l1_4_factorial import cell_costs, contrasts, gamma_coefficient


def test_property_b_all_patterns_include_coefficient_two():
    seen = set()
    for delta in (-2, 2):
        stay, switch = 20, 20+delta
        best, margin = min(stay, switch), abs(delta)
        for i00, i10, i01 in product((0, 1), repeat=3):
            indicators = dict(zip(("00", "10", "01", "11"), (i00, i10, i01, 0)))
            # Non-tied predicted gaps selected to implement each given pattern.
            gaps = {cell: -delta if wrong else delta for cell, wrong in indicators.items()}
            table = cell_costs(stay, switch, gaps)
            assert table == {cell: best+margin*i for cell, i in indicators.items()}
            c = contrasts(table["00"], table["10"], table["01"], table["11"])
            coefficient = i10+i01-i00
            assert c["Gamma"] == coefficient*margin
            assert F(c["Gamma"])/margin in {-1, 0, 1, 2}
            assert gamma_coefficient(i00, i10, i01) == coefficient
            seen.add(F(c["Gamma"])/margin)
    assert seen == {-1, 0, 1, 2}


def test_zero_margin_gives_zero_cost_contrasts():
    table = cell_costs(F(7, 3), F(7, 3), {"00": -1, "10": 0, "01": 1, "11": 0})
    assert set(table.values()) == {F(7, 3)}
    assert set(contrasts(table["00"], table["10"], table["01"], table["11"]).values()) == {0}
