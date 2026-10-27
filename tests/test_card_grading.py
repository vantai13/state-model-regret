"""Doan Van Tai — synthetic boundary/logic tests, never grid outcomes."""
from fractions import Fraction as F

import pytest

from experiments.A03_card.grading import (
    Interval as I, STANDS as S, FAILS as N, UNKNOWN as U, EXCLUDED as X,
    ratio, judge, combine, point_claim, grade_cell, carry_rule, refinement,
)


@pytest.mark.parametrize('op,expected', [('<=', S), ('>=', S), ('<', N), ('>', N)])
def test_closed_and_open_thresholds(op, expected):
    assert judge(I('.005', '.005'), op, '.005') == expected


def test_signed_ratio_needs_all_four_corners():
    assert ratio(I(-2, -1), I(1, 2)) == I(-2, F(-1, 2))
    assert ratio(I(-1, 1), I(1, 2)) == I(-1, 1)
    assert ratio(I('.42', '.48'), I('99.75', '100.25')) == I(F(42, 100)/F(10025, 100), F(48, 100)/F(9975, 100))
    with pytest.raises(ZeroDivisionError):
        ratio(I(1, 2), I(0, 1))


def test_three_state_logic_and_excluded_denominators():
    assert combine([S, S, S, U]) == U
    assert combine([S, S, S, U], 'any') == S
    assert combine([N, U]) == N
    assert combine([N, U], 'any') == U
    assert combine([X, X]) == combine([], 'all') == combine([], 'any') == U
    assert combine([N, X], 'any') == U


def test_threshold_crossing_is_not_a_failure():
    assert judge(I('.42', '.48'), '<=', '.5') == S
    assert judge(I('.46', '.52'), '<=', '.5') == U
    assert judge(I('.51', '.52'), '<=', '.5') == N


def row(ref=2, GS=1, GM=0, Gamma=1, C=100, V=1, FV=None):
    L10 = C + Gamma + GM
    values = dict(L00=L10+GS, L01=L10+GS-GM, L10=L10, L11=C, C_ref=C,
                  G_S=GS, G_M=GM, G_SM=GS+Gamma+GM, Gamma=Gamma, G_S_M1=Gamma+GS,
                  G_M_S1=Gamma+GM, F=GS-V if FV is None else FV, V=V)
    return dict(intervals={k: [v, v] for k, v in values.items()},
                refinement=ref, dt_s=str(F(1, ref)),
                reference_context=dict(refinement=ref, dt_s=str(F(1, ref))),
                status='BOUNDED', numeric_budget_met=True, unresolved_mass={'oracle': 0, 'M0': 0, 'D22': 0})


def test_PC5_branches_and_conjunction_separately():
    K = combine([point_claim('P5_K', row(GM=F(1, 2))) for _ in range(4)])
    Q = combine([point_claim('P5_Q', row(GM=g)) for g in (0, 0, 1, 0)], 'any')
    assert (K, Q, combine([K, Q])) == (S, S, S)
    assert point_claim('P5_K', row(GM=F(51, 100))) == N
    assert point_claim('P3', row(Gamma=F(1, 2))) == N  # strict >
    assert point_claim('P2', row(GS=1, GM=0)) == S    # closed >=


def test_zero_or_uncertain_Cref_and_absolute_P6():
    assert point_claim('P5_K', row(C=0)) == X
    r = row()
    r['intervals']['C_ref'] = [-1, 1]
    assert point_claim('P2', r) == U
    assert point_claim('P6', row(C=0, V=1, FV=0)) == S
    zero = row(C=0)
    zero['numeric_budget_met'] = False
    assert grade_cell('P5_K', zero)['verdict'] == X


def test_hold_dt_failure_missing_and_mixed_references():
    coarse, fine = row(1), row(2)
    assert grade_cell('P2', fine, coarse)['verdict'] == S
    assert grade_cell('P2', fine)['verdict'] == U
    fine['unresolved_mass']['M0'] = '.0100001'
    assert grade_cell('P2', fine, coarse)['verdict'] == U
    fine = row(2, GS=2)
    assert refinement(coarse, fine) == N
    assert grade_cell('P2', fine, coarse)['verdict'] == U
    fine = row(2)
    fine['reference_context']['refinement'] = 1
    with pytest.raises(ValueError):
        grade_cell('P2', fine, coarse)
    fine = row(2)
    del fine['unresolved_mass']['D22']
    assert grade_cell('P2', fine, coarse)['verdict'] == U


def test_labels_can_be_dt_sensitive_inside_refinement_tolerance():
    coarse, fine = row(1, GM=F(49, 100)), row(2, GM=F(51, 100))
    # Difference .02 < .25; label still changes across the .5 equivalence boundary.
    result = grade_cell('P5_K', fine, coarse)
    assert result == dict(verdict=N, reason='graded_at_final_dt', sensitive_to_dt=True)


def test_carry_has_no_posthoc_choice_for_unresolved_rule():
    assert carry_rule(S) and carry_rule(U) and carry_rule(X)
    assert not carry_rule(N)
