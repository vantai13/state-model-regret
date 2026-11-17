"""Doan Van Tai — tests for the V7-3 congested capacity rule (Claude, 17/11/2026)."""
import numpy as np

from experiments.letter.v7_3_cong import congested_capacity


def test_busiest_link_mean_utilization_equals_rho():
    rng = np.random.default_rng(1)
    days = rng.uniform(1, 5, size=(4, 24, 3))           # days x slots x OD
    stay = np.array([[1, 1, 0], [0, 1, 1], [1, 0, 0]])  # links x OD
    cap = congested_capacity(days, stay, busiest=1, rho=0.9)
    load = np.einsum('nsd,ed->nse', days, stay)
    assert abs(load[:, :, 1].mean() / cap - 0.9) < 1e-12


def test_rule_scales_inversely_with_rho():
    days = np.ones((2, 24, 2))
    stay = np.array([[1, 1]])
    assert abs(congested_capacity(days, stay, 0, rho=0.5) - 2 * congested_capacity(days, stay, 0, rho=1.0)) < 1e-12
