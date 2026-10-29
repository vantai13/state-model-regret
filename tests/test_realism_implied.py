"""Doan Van Tai — exact/limit checks on generic design-only realism formulas."""
import ast
import inspect
import math

import pytest

from experiments.R3R_04_realism import implied as I


def test_no_outcome_engine_or_io_imports():
    module = ast.parse(inspect.getsource(I))
    assert [n.names[0].name for n in ast.walk(module) if isinstance(n, ast.Import)] == ['math']
    assert not any(isinstance(n, ast.ImportFrom) for n in ast.walk(module))
    assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ('open', 'eval', 'exec', '__import__') for n in ast.walk(module))


def test_fluid_known_answers_and_buffer_proxy():
    q = I.fluid_queue(8, 6, 10, .1)
    assert q['p_busy'] == .75 and q['atom_zero'] == .25
    assert q['theta_per_packet'] == 1.25
    assert q['virtual_delay_time_mean_s'] == .06
    assert I.delay_exceedance(q, 10, .1) == pytest.approx(.75 * math.exp(-1.25))
    q95 = I.fluid_queue(9.5, 6, 10, .1)
    assert q95['virtual_delay_time_mean_s'] / q['virtual_delay_time_mean_s'] == pytest.approx(5.5)


def test_small_window_numerical_stability_and_large_window_limit():
    assert I.window_cv(8, 6, .1, 1e-16) == pytest.approx(.75, rel=1e-12)
    assert I.window_cv(8, 6, .1, 1e8) == pytest.approx(.75 * math.sqrt(.1 / 1e8), rel=1e-8)
    assert I.window_cv(8, 6, .1, .1) == pytest.approx(.75 * math.sqrt((1 + math.exp(-2)) / 2))


def test_anchor_keeps_h_ratio_and_maps_every_time_once():
    a = I.implied(7, 8, 1, .3, 8, tau_anchor_s=1)
    b = I.implied(7, 8, 1, .3, 8, tau_anchor_s=.01)
    for key in ('rho_A_pre', 'rho_A_post', 'rho_B_pre', 'rho_B_post', 'phi', 'kappa', 'h_over_tau'):
        assert a[key] == b[key]
    assert b['h_physical_s'] == a['h_physical_s'] / 100
    assert b['T_mode_s'] == a['T_mode_s'] / 100
    assert b['B_pre']['virtual_delay_time_mean_s'] == pytest.approx(a['B_pre']['virtual_delay_time_mean_s'] / 100)
    assert b['B_pre']['CV_windows']['0.1'] < a['B_pre']['CV_windows']['0.1']


def test_joint_time_traffic_scaling_of_recurrence_and_cost():
    rates = [2, 14, 14, 2, 2, 14]
    baseline = I.endpoint_path(1.5, rates, 1, 10, .1)
    k, s = 1000., .01
    scaled = I.endpoint_path(1.5 * k * s, [r * k for r in rates], k, 10 * k, .1 * s)
    assert scaled == pytest.approx([q * k * s for q in baseline])
    cost0, cost1 = .1 * sum(baseline) + 4, .1 * s * sum(scaled) + 4 * k * s * s
    assert cost1 == pytest.approx(cost0 * k * s * s)
    assert I.window_cv(8000, 6000, .003, .001) == pytest.approx(I.window_cv(8, 6, .3, .1))


def test_eta_label_and_physical_headroom_ratio_are_distinct():
    x = I.implied(7, 6, 1.5, .3, 8)
    assert x['eta_label_pilot'] == .75 and x['phi'] == .375


def test_ctmc_event_count_is_not_slotted_boundary_count():
    x = I.mode_diagnostics(.1)
    assert x['ctmc_expected_events_in_age'] == 10
    assert x['slotted_expected_boundary_flips_in_age'] < 10
    assert x['mode_correlation_over_age'] == pytest.approx(math.exp(-20))
    assert I.mode_diagnostics(.1, ref=2)['slotted_expected_boundary_flips_in_age'] > x['slotted_expected_boundary_flips_in_age']


def test_post_switch_proxy_is_explicit_and_no_fabricated_actuation():
    x = I.implied(7, 8, 1.5, .1, 16)
    assert x['rho_B_post'] == .95
    assert 'not actual transient' in x['B_post']['scope']
    assert x['actuation_mode_correlation'] is None and x['mode_oracle_structural_flag']


@pytest.mark.parametrize('args', [(10, 6, 10, .1), (5, 6, 10, .1), (8, 6, 10, 0)])
def test_invalid_stationary_inputs_rejected(args):
    with pytest.raises(ValueError): I.fluid_queue(*args)


def test_always_empty_and_zero_threshold_boundary():
    x = I.fluid_queue(5, 2, 10, .1)
    assert x['p_busy'] == x['virtual_delay_time_mean_s'] == 0
    assert I.delay_exceedance(x, 10, 0) == 0
    assert I.delay_exceedance(I.fluid_queue(8, 6, 10, .1), 10, 0) == .75
