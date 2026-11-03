"""Doan Van Tai — guard scientific interpretations of centered moments."""
import numpy as np
import pytest

from tools.analyze_phase6_covariance import centered_moments


def test_zero_truth_information_value_can_have_alignment_and_fresh_information_gain():
    # Truth Stay at both states; misspecified gaps -4,+2 select old Switch,
    # and fresh Switch only at the cheaper state. S|M1=0, yet G_S=1.5.
    w, gap = [.5, .5], [1, 3]
    old = centered_moments(w, gap, [1, 1], 2)
    new = centered_moments(w, gap, [1, 0], 2)
    assert np.all(np.asarray(gap) > 0)
    assert old['covariance'] - new['covariance'] == pytest.approx(.5)
    assert 2 * (old['share'] - new['share']) + old['covariance'] - new['covariance'] == pytest.approx(1.5)


def test_conditional_mean_mismatch_requires_an_explicit_bridge():
    old = centered_moments([.5, .5], [2, 4], [1, 0], 2)
    new = centered_moments([.5, .5], [1, 3], [0, 1], 2)
    direct = old['common_centered'] - new['common_centered']
    cov = old['covariance'] - new['covariance']
    bridge = old['share'] * (old['mean_gap'] - 2) - new['share'] * (new['mean_gap'] - 2)
    assert direct != pytest.approx(cov)
    assert direct == pytest.approx(cov + bridge)


def test_bounded_transient_does_not_force_bias_dominance_when_frequency_difference_vanishes():
    # Delta_h=h+(-1,+1), alpha=h: uniformly bounded transient, Delta_F=0.
    for horizon in (2, 20, 200):
        old = centered_moments([.5, .5], [horizon-1, horizon+1], [1, 0], horizon)
        new = centered_moments([.5, .5], [horizon-1, horizon+1], [0, 1], horizon)
        assert old['share'] == new['share']
        assert old['common_centered'] - new['common_centered'] == pytest.approx(-1)


def test_nonunit_weights_are_rejected_instead_of_renormalized():
    with pytest.raises(AssertionError, match='NONUNIT_PROBABILITY_MASS'):
        centered_moments([.4, .5], [1, 3], [1, 0], 2)
