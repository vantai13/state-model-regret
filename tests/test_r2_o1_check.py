"""Doan Van Tai — independent small analytic controls for the R2-O1 adapter."""
from fractions import Fraction as F
import itertools

import numpy as np
import pytest
from scipy.linalg import expm

from experiments.letter import r2_o1_check as r


def test_two_dimensional_prefix_matches_four_dimensional_joint_enumeration():
    pa = np.array([[.8, .2], [.3, .7]])
    pb = np.array([[.5, .3, .2], [.2, .7, .1], [.1, .2, .7]])
    wa = np.array([.6, .4])
    wb = np.array([.2, .5, .3])
    ja, jb = wa[:, None]*pa, wb[:, None]*pb
    new_a, new_b = np.array([-.5, 1.]), np.array([-.4, .5, -1.])
    old_a, old_b = np.array([.2, -.8]), np.array([.8, -.1, 1.])
    fn = sum(ja[:, xa].sum()*jb[:, xb].sum()*(new_a[xa]+new_b[xb]<0)
             for xa in range(2) for xb in range(3))
    fo = sum(wa[ya]*wb[yb]*(old_a[ya]+old_b[yb]<0) for ya in range(2) for yb in range(3))
    expected = sum(ja[ya, xa]*jb[yb, xb]*((new_a[xa]+new_b[xb]<0) != (old_a[ya]+old_b[yb]<0))
                   for ya, xa, yb, xb in itertools.product(range(2), range(2), range(3), range(3)))
    got, lo, hi = r.disagreement_from_joints(ja, jb, new_a, new_b, old_a, old_b, fn, fo)
    assert got == pytest.approx(expected, abs=1e-14)
    assert lo == hi
    # An omitted terminal state is enclosed, never renormalized.
    omitted = jb[:, -1].sum()
    got, lo, hi = r.disagreement_from_joints(ja, jb[:, :-1], new_a, new_b, old_a, old_b, fn, fo, omitted)
    assert lo-1e-14 <= expected <= hi+1e-14


def test_actual_joint_not_difference_of_switching_shares():
    p = np.array([[.7, .3], [.3, .7]])
    joint = .5*p
    a, b = np.array([-1., 1.]), np.zeros(1)
    value, _, _ = r.disagreement_from_joints(joint, np.ones((1, 1)), a, b, a, b, .5, .5)
    assert value == pytest.approx(.3)
    assert value > abs(.5-.5)


def test_wrong_stale_kernel_does_not_change_the_true_cost_posterior():
    p_true = np.array([[.75, .25], [.25, .75]])
    pi = np.array([.5, .5])
    gap = np.array([-2., 4.])
    predictor = np.array([-1., 2.])
    old_plugin = predictor < 0
    actual = pi @ (old_plugin*(p_true @ gap))
    incorrect = pi @ (old_plugin*gap)
    brute = sum(pi[y]*p_true[y, x]*old_plugin[y]*gap[x] for y in range(2) for x in range(2))
    assert actual == brute
    assert actual != incorrect


def test_probability_kernel_cutoff_and_strict_tie_boundary():
    remainder = np.array([-3., 1., 3.])
    kernels = [np.eye(3), np.full((3, 3), 1/3), np.array([[0., 1., 0.]]*3)]
    for slope in (-2., 2.):
        h = 3/abs(slope)+1e-5
        fresh = h*slope+remainder < 0
        for kernel in kernels:
            assert np.all(fresh == (slope < 0))
            assert np.all((h*slope+kernel @ remainder < 0) == (slope < 0))
    # At equality a negative common slope can still yield Stay at a tie.
    assert not (-3.+3. < 0)


def test_p_dis_bound_with_signed_costs_against_brute_force():
    rng = np.random.default_rng(912)
    for _ in range(50):
        law = rng.random((4, 4)); law /= law.sum()
        fresh, old = rng.integers(0, 2, 4), rng.integers(0, 2, 4)
        delta = rng.normal(size=4)
        gs = sum(law[y, x]*(old[y]-fresh[x])*delta[x] for y in range(4) for x in range(4))
        dis = sum(law[y, x]*(old[y] != fresh[x]) for y in range(4) for x in range(4))
        assert abs(gs) <= dis*max(abs(delta))+1e-15


def test_nowcast_cutoff_and_mode_posterior_use_requested_amplitude():
    nc = r.nowcast(F(7), F(6), F(1), F(1, 20), F(3), 4.)
    assert nc["eligible"] and nc["w_star"] == .25
    assert nc["max_nowcast_load"] < 9.5
    assert r.nowcast(F(9), F(17, 2), F(1, 2), F(1, 2), F(6), 5.)["eligible"] is False
    rate = np.add.outer(nc["rate_A"], nc["rate_B"])
    assert nc["F_new_inf"] == np.mean(rate < 0)


def test_joint_law_uses_original_semigroup_and_preserves_stationary_marginals():
    ch = r.ctmc.chain(F(7), F(1, 2), 6)
    joint = r.JointLaw(dict(Ast=ch, Bst=ch), .05)
    data = joint.build()
    for j, dropped, err in data:
        expected = ch.pi[:, None]*expm(ch.Q.toarray()*.05)[:, :j.shape[1]]
        np.testing.assert_allclose(j, expected, rtol=1e-12, atol=1e-14)
        assert dropped <= r.TAIL_OMISSION+1e-14
        assert err < 1e-12


def test_selection_is_exactly_evenly_spaced_within_each_sign_group():
    selected, groups = r.saved_cases()
    assert len(selected) == 12
    assert sum(raw["s"]<0 for raw in selected) == 6
    assert sum(raw["s"]>0 for raw in selected) == 6
    assert groups[0]["indices_zero_based"] == [0, 8, 16, 25, 33, 41]
    assert groups[1]["indices_zero_based"] == [0, 10, 20, 30, 40, 50]
