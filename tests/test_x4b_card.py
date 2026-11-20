"""Doan Van Tai — synthetic B1/B2/B3 criteria, no real outcomes or scoring."""
import pytest

from experiments.letter import x4b_card as K


def pair(side='fresh', h=900, num=1, n=100, mean=-2., se=1., **kw):
    return dict(regime='synthetic', date='synthetic-day', side=side, h_s=h,
        instances=n, disagreement_numerator=num, disagreement_share=num/n,
        paired_Hybrid_minus_Stationary_Mbit_s=mean, paired_Hybrid_minus_Stationary_SE_Mbit_s=se,
        evaluable=False, **kw)


def row(day, rule='M0', tau=300, h=3600, gs=-10., cref=1000., regret=0., eligible=True, regime='synthetic'):
    return dict(regime=regime, date=str(day), rule=rule, tau_s=tau, h_s=h,
        evaluable=eligible, G_S_Mbit_s=gs, G_S_SE_Mbit_s=1.e9,
        C_ref_Mbit_s=cref, both_side_regret_pct=regret)


def test_b1_local_one_percent_inclusive_two_se_no_evaluability_filter():
    pairs = [pair(), pair(side='stale_300', mean=2.), pair(side='stale_900', mean=-1.99),
             pair(h=1200, mean=0., se=0.), pair(h=1800, num=0), pair(h=3600)]
    b1 = K.evaluate([], {}, pairs)['B1']
    assert b1['kind'] == 'EXPLORATORY_NOT_PASS_FAIL'
    assert b1['cases'] == 4
    assert b1['counts'] == dict(GAIN=1, LOSS=1, UNRESOLVED=2)
    assert all(not r['evaluable'] for r in b1['rows'])


@pytest.mark.parametrize('mean,se,expected', [(-1., 0., 'GAIN'), (1., 0., 'LOSS'), (0., 0., 'UNRESOLVED'),
    (-2., 1., 'GAIN'), (2., 1., 'LOSS'), (-1.99, 1., 'UNRESOLVED')])
def test_b1_both_directions_and_zero_ties(mean, se, expected):
    assert K.b1_reading(mean, se) == expected


def b2_rows(count=20, successes=19):
    rows = []
    for d in range(count):
        rows += [row(d, 'Stationary', h=1800, regret=1.),
                 row(d, 'Hybrid', h=1800, regret=1.05 if d < successes else 1.051)]
    return rows


def test_b2_inclusive_005_percentage_point_margin_and_95_percent_share():
    b2 = K.evaluate(b2_rows(), {})['B2']
    assert b2['verdict'] == 'STANDS'
    assert (b2['cases'], b2['not_worse'], b2['share']) == (20, 19, .95)
    assert K.evaluate(b2_rows(successes=18), {})['B2']['verdict'] == 'DOES_NOT_STAND'
    assert K.evaluate(b2_rows(count=19), {})['B2']['verdict'] == 'NOT_EVALUABLE'


def test_b2_filters_long_h_and_nonevaluable_but_keeps_both_ages():
    rows = b2_rows()
    rows += [row('other-age', r, tau=900, h=300, regret=1.) for r in ('Hybrid', 'Stationary')]
    rows += [row('long', r, h=3600) for r in ('Hybrid', 'Stationary')]
    rows += [row('low-backlog', r, h=900, eligible=False) for r in ('Hybrid', 'Stationary')]
    b2 = K.evaluate(rows, {})['B2']
    assert b2['cases'] == 21 and b2['not_worse'] == 20
    assert 'both-side=max' in b2['unit']


def test_b2_never_uses_a_missing_rule_or_different_normalizer():
    with pytest.raises(ValueError, match='missing Hybrid/Stationary'):
        K.evaluate([row(0, 'Hybrid', h=300)], {})
    with pytest.raises(ValueError, match='common positive C_ref'):
        K.evaluate([row(0, 'Hybrid', h=300), row(0, 'Stationary', h=300, cref=2.)], {})


def b3_rows(cells=5):
    rows, signs = [], {}
    for c in range(cells):
        regime = f'synthetic-{c}'
        signs[(regime, 'M0', 300, 3600)] = -1
        for d in range(3):
            rows.append(row(d, regime=regime))
    return rows, signs


def test_b3a_four_resolved_minimum_080_accuracy_and_se_over_days():
    rows, signs = b3_rows()
    signs[('synthetic-0', 'M0', 300, 3600)] = 1  # 4/5 exact threshold
    b3 = K.evaluate(rows, signs)['B3a']
    assert (b3['verdict'], b3['resolved'], b3['correct'], b3['accuracy']) == ('STANDS', 5, 4, .8)
    assert all(r['SE_over_days_Mbit_s'] == 0 for r in b3['cells'])  # instance SE deliberately huge
    rows, signs = b3_rows(cells=3)
    assert K.evaluate(rows, signs)['B3a']['verdict'] == 'NOT_EVALUABLE'
    rows, signs = b3_rows(cells=4)
    signs[('synthetic-0', 'M0', 300, 3600)] = 1
    assert K.evaluate(rows, signs)['B3a']['verdict'] == 'DOES_NOT_STAND'


def test_b3a_resolution_pct_boundary_day_se_abstention_and_eligibility():
    rows, signs = b3_rows(cells=1)
    for r in rows:
        r['G_S_Mbit_s'] = -2.5  # exactly .25% of C_ref
    assert K.evaluate(rows, signs)['B3a']['resolved'] == 1
    rows[0]['G_S_Mbit_s'] = 20.
    assert K.evaluate(rows, signs)['B3a']['resolved'] == 0
    rows, signs = b3_rows(cells=1)
    signs[('synthetic-0', 'M0', 300, 3600)] = 0
    assert K.evaluate(rows, signs)['B3a']['resolved'] == 0
    for r in rows:
        r['evaluable'] = False
    assert K.evaluate(rows, signs)['B3a']['cells'] == []


def test_b3b_adds_regret_contributions_once_per_fresh_record_h():
    rows = [dict(regime='synthetic', date='day', side='fresh', h_s=h, evaluable=True,
        instances=4, tie_instances=2, strict_instances=2,
        regret_sum_Mbit_s=20., tie_regret_sum_Mbit_s=6., strict_regret_sum_Mbit_s=14.)
        for h in (900, 3600, 7200)]
    b3 = K.evaluate([], {}, tie_strict_rows=rows)['B3b']
    assert b3['kind'] == 'DESCRIPTIVE'
    assert (b3['cases'], b3['instances']) == (2, 8)
    assert (b3['regret_sum_Mbit_s'], b3['tie_regret_sum_Mbit_s'], b3['strict_regret_sum_Mbit_s']) == (40., 12., 28.)
    assert b3['strict_regret_share'] == .7 and b3['strict_regret_pct'] == 70.
    assert K.evaluate([], {})['B3b']['strict_regret_share'] is None
    with pytest.raises(ValueError, match='duplicate scoring unit'):
        K.evaluate([], {}, tie_strict_rows=rows+rows)
