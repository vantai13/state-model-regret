"""Doan Van Tai — the twelve L1.4 golden/invariant tests from the lesson."""
from fractions import Fraction as F
from itertools import product

from experiments.lessons.l1_3_expected_cost import CANON, expected_cost
from experiments.lessons.l1_4_factorial import (
    additive_cells, cell_costs, choose, contrasts, gamma_coefficient, table_from_additive,
)
from golden_phase1 import (
    DELTA_HAT_10, FACTORIAL_ASYMMETRIC, FACTORIAL_CONTRASTS, FACTORIAL_MEANS,
    FACTORIAL_ROWS, X_A, X_B, X_C, X_D,
)


def C(table):
    return contrasts(table["00"], table["10"], table["01"], table["11"])


def test_20_18_complements_when_errors_large():
    c = C(table_from_additive(20, 18, 3, 3))
    assert (c["G_S"], c["G_M"], c["G_SM"], c["Gamma"]) == (0, 0, 2, 2)


def test_20_18_substitutes_when_errors_medium():
    c = C(table_from_additive(20, 18, F(3, 2), F(3, 2)))
    assert (c["G_S"], c["G_M"], c["G_SM"], c["Gamma"]) == (2, 2, 2, -2)


def test_tie_rule_is_part_of_definition():
    table = table_from_additive(20, 18, F(3, 2), F(1, 2))
    assert table["00"] == 20 and C(table)["Gamma"] == -2
    switch_on_tie = dict(table, **{"00": 18})
    assert C(switch_on_tie)["Gamma"] == 0


def test_gamma_is_a_step_function_of_error_size():
    expected = {0: 0, 1: 0, 2: -2, 3: -2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2}
    for k, gamma in expected.items():
        e = F(k, 2)
        assert C(table_from_additive(20, 18, e, e))["Gamma"] == gamma


def test_average_can_hide_opposite_signs_EV25():
    large = C(table_from_additive(20, 18, 3, 3))["Gamma"]
    medium = C(table_from_additive(20, 18, F(3, 2), F(3, 2)))["Gamma"]
    assert F(7, 10)*large + F(3, 10)*medium == F(4, 5)
    assert F(1, 2)*large + F(1, 2)*medium == 0


def test_partial_repair_beats_oracle_repair_EV26():
    types = [(F(1), F(3, 2)), (F(3), F(-5, 2))]

    def regret_00(scale):
        return sum((table_from_additive(20, 18, eS*scale, eM)["00"]-18)
                   for eM, eS in types) / F(len(types))

    r00 = regret_00(1)
    assert r00 == 1
    assert r00-regret_00(0) == 0
    assert r00-regret_00(F(1, 2)) == 1 == r00


def _grid():
    halves = [F(k, 2) for k in range(-8, 9)]
    for delta, eS, eM in product((-3, -1, 1, 3), halves, halves):
        yield table_from_additive(F(10), F(10+delta), eS, eM), abs(delta)


def test_property_a_cell_11_is_oracle():
    for table, _ in _grid():
        c = C(table)
        assert c["G_SM"] >= 0 and c["G_S|M1"] >= 0 and c["G_M|S1"] >= 0


def test_property_b_gamma_takes_four_values():
    assert {gamma_coefficient(*p) for p in product((0, 1), repeat=3)} == {-1, 0, 1, 2}
    for table, margin in _grid():
        assert C(table)["Gamma"]/margin in {-1, 0, 1, 2}


def test_property_e_gamma_is_change_in_conditional_gain():
    for table, _ in _grid():
        c = C(table)
        assert c["Gamma"] == c["G_S|M1"]-c["G_S"] == c["G_M|S1"]-c["G_M"]


def _canonical_rows():
    rows = []
    for state in (X_A, X_B, X_C, X_D):
        stay, switch = (expected_cost(state, action, CANON) for action in ("Stay", "Switch"))
        rows.append(cell_costs(stay, switch, {"00": F(1, 4), "01": F(-1, 4),
                                              "10": DELTA_HAT_10[state], "11": switch-stay}))
    return rows


def test_canonical_table_golden():
    rows = _canonical_rows()
    assert rows == [FACTORIAL_ROWS[x] for x in (X_A, X_B, X_C, X_D)]
    means = {cell: sum(r[cell] for r in rows)/4 for cell in rows[0]}
    assert means == FACTORIAL_MEANS
    assert C(means) == FACTORIAL_CONTRASTS
    assert [C(r)["Gamma"] for r in rows] == [2, F(-3, 2), F(3, 2), -3]


def test_contrast_of_mean_equals_mean_of_contrasts():
    rows = _canonical_rows()
    means = {cell: sum(r[cell] for r in rows)/4 for cell in rows[0]}
    for name in C(means):
        assert C(means)[name] == sum(C(r)[name] for r in rows)/4


def test_asymmetric_errors_distinguish_state_from_model():
    c = C(table_from_additive(20, 18, 3, F(1, 2)))
    assert {name: c[name] for name in FACTORIAL_ASYMMETRIC} == FACTORIAL_ASYMMETRIC
