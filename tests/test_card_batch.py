"""Doan Van Tai — verify branch counts, no cherry-picking, all synthetic rows."""
from experiments.A03_card.grade_card import grade_main
from experiments.A03_card.grading import STANDS as S, FAILS as N, UNKNOWN as U
from tests.test_card_grading import row


SPEC = {'predictions': {'P2': {'ids': ['t2'], 'quantifier': 'all'},
                        'P3': {'ids': ['t3'], 'quantifier': 'all'},
                        'P6': {'ids': ['t6'], 'quantifier': 'all'},
                        'P5': {'K_ids': ['k1', 'k2'], 'Q_ids': ['q1', 'q2']}}}


def test_batch_separates_branches_and_carries_unknown_without_selection():
    fine = {'k1': row(2, GM=0), 'k2': row(2, GM=0), 'q1': row(2, GM=1)}
    coarse = {k: row(1, GM=1 if k == 'q1' else 0) for k in fine}
    result = grade_main(SPEC, fine, coarse)
    assert result['P5']['K']['verdict'] == result['P5']['Q']['verdict'] == result['P5']['verdict'] == S
    assert result['P5']['Q']['counts'][S] == 1 and result['P5']['Q']['counts'][U] == 1
    assert result['P2']['verdict'] == U and result['carry_to_A05_F']['carry']
    fine.pop('q1')
    result = grade_main(SPEC, fine, coarse)
    assert result['P5']['verdict'] == U and result['carry_to_A05_F']['carry']


def test_refuted_main_rule_does_not_open_heldout_to_rescue_it():
    fine, coarse = {'k1': row(2, GM=1)}, {'k1': row(1, GM=1)}
    result = grade_main(SPEC, fine, coarse)
    assert result['P5']['K']['verdict'] == result['P5']['verdict'] == N
    assert result['carry_to_A05_F']['carry'] is False
