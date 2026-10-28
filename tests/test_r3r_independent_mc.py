"""Specification-only tests on invented small systems; no engine import."""
import importlib.util
from pathlib import Path
import sys
import unittest

import numpy as np


SOURCE = Path(__file__).resolve().parents[1] / "experiments/R3R_02_audit/independent_mc.py"
SPEC = importlib.util.spec_from_file_location("r3r_independent_mc_test_module", SOURCE)
mc = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mc
SPEC.loader.exec_module(mc)


class IndependentPhysicalTests(unittest.TestCase):
    def test_one_slot_endpoint_initial_mode_and_switch_cost(self):
        dt = 1 / 120
        dataset = mc.sample_fixed_state(0, 1, 0, 0, lambda_a=6, lambda_b=6,
                                       u=1, kappa=0.1, h=dt, n=3,
                                       seed=318300001, c_sw=0.7)
        np.testing.assert_allclose(dataset.CStay, 3 * dt * dt, atol=1e-16, rtol=0)
        np.testing.assert_allclose(dataset.CSwitch, 2 * dt * dt + 0.7, atol=1e-16, rtol=0)

    def test_refinement_one_slot(self):
        dt = 1 / 240
        dataset = mc.sample_fixed_state(0, 0, 2, 0, lambda_a=6, lambda_b=6,
                                       u=1, kappa=0.03, h=dt, n=2,
                                       seed=318300002, ref=2)
        np.testing.assert_allclose(dataset.CStay, dt * (2 - 10 * dt), atol=1e-16, rtol=0)
        np.testing.assert_allclose(dataset.CSwitch-dataset.CStay, dt*dt, atol=1e-16, rtol=0)

    def test_run_occupancy_matches_slot_recurrence_with_reflection(self):
        dt, h = 1 / 120, 0.1
        q0 = np.array([0.0, 0.01, 0.1, 2.0])
        modes = np.array([0, 0, 1, 1])
        stay, switch = mc.simulate_future(q0, modes, 6, 1, 0, 1e300,
                                           h=h, seed=318300003)
        for actual, managed in ((stay, 1), (switch, 0)):
            q = q0.copy()
            expected = np.zeros(len(q))
            for _ in range(12):
                q = np.maximum(0, q + (6 + 6*(2*modes-1) + managed - 10) * dt)
                expected += dt * q
            np.testing.assert_allclose(actual, expected, rtol=1e-13, atol=1e-15)

    def test_age_transition_after_one_slot(self):
        dt, kappa, n = 1/120, 0.017, 10000
        q, mode = mc.simulate_age(np.zeros(n), np.ones(n), 6, 0, kappa,
                                  tau=dt, seed=318300004)
        np.testing.assert_allclose(q, 2*dt, atol=1e-16, rtol=0)
        keep = (1 + np.exp(-2*dt/kappa))/2
        self.assertLess(abs(mode.mean()-keep), 0.02)

    def test_three_slot_expectation_matches_exhaustive_mode_tree(self):
        dt, kappa = 1/120, 0.017
        keep = (1+np.exp(-2*dt/kappa))/2
        expected = 0.0
        for second in (0, 1):
            for third in (0, 1):
                probability = (keep if second == 1 else 1-keep) * (keep if third == second else 1-keep)
                costs = []
                for managed in (0, 1):
                    q, cost = 0.01, 0.0
                    for mode in (1, second, third):
                        q = max(0, q + (6+6*(2*mode-1)+managed-10)*dt)
                        cost += dt*q
                    costs.append(cost)
                expected += probability*(costs[1]-costs[0])
        n = 10000
        c0, c1 = mc.simulate_future(np.full(n, 0.01), np.ones(n), 6, 0, 1, kappa,
                                    h=3*dt, seed=318300005)
        gap = c1-c0
        self.assertLess(abs(gap.mean()-expected), 5*gap.std(ddof=1)/np.sqrt(n)+1e-14)

    def test_same_actions_share_identical_future(self):
        stay, switch = mc.simulate_future([0, 0.1, 1], [1, 0, 1], 6, 1, 1, 0.1,
                                           h=0.1, seed=318300006)
        np.testing.assert_array_equal(stay, switch)

    def test_far_state_no_idle_gap_is_symbolic_raw_noise_is_retained(self):
        from fractions import Fraction
        n, h = 128, 0.1
        q = np.full(n, 1e9)
        raw0, raw1 = mc.simulate_future(q, np.arange(n)%2, 6, 1, 0, 0.017,
                                       h=h, seed=318300010)
        raw_gap = raw1-raw0
        gap, certified, metadata = mc._side_gap_no_idle(
            q, raw_gap, lambda_bg=6, managed_stay=1, managed_switch=0, mu=10, h=h, ref=1)
        expected = float(-Fraction(1,120)**2*12*13/2)
        self.assertTrue(np.all(certified))
        np.testing.assert_array_equal(gap, np.full(n, expected))
        self.assertEqual(float(gap.max()-gap.min()), 0)
        self.assertTrue(np.any(raw_gap != gap))
        self.assertGreater(raw_gap.std(), 0)
        self.assertGreater(metadata["certified_raw_subtraction_max_abs_roundoff"], 0)
        # Native action costs themselves have not been rewritten.
        np.testing.assert_array_equal(raw_gap, raw1-raw0)

    def test_exact_no_idle_threshold_has_no_tolerance(self):
        from fractions import Fraction
        exact_threshold = Fraction(10,120)  # one-slot max drain, lambda6, min managed0
        boundary = float(exact_threshold)
        if Fraction.from_float(boundary) < exact_threshold:
            boundary = np.nextafter(boundary, np.inf)
        q = np.array([np.nextafter(boundary,-np.inf), boundary])
        raw = np.array([0.0, 0.0])
        gap, certificate, metadata = mc._side_gap_no_idle(
            q, raw, lambda_bg=6, managed_stay=1, managed_switch=0,
            mu=10, h=1/120, ref=1)
        np.testing.assert_array_equal(certificate, [False,True])
        self.assertEqual(gap[0],raw[0])
        self.assertEqual(gap[1],float(-Fraction(1,120)**2))
        self.assertFalse(metadata["epsilon_or_clamping"])


class IndependentStationaryTests(unittest.TestCase):
    def test_exact_empty_queue(self):
        law = mc.stationary_law(6, 0, 0.05, mu=13)
        np.testing.assert_array_equal(law.joint, [[0.5, 0.5]])
        self.assertEqual(law.diagnostics["stationary_cap_coupling_tv_bound"], 0)

    def test_iid_modes_are_independent_of_stationary_backlog(self):
        law = mc.stationary_law(6, 0, 0, truncation_tv_target=1e-8)
        np.testing.assert_allclose(law.joint[:, 0], law.joint[:, 1], rtol=1e-8, atol=1e-15)
        self.assertLess(law.diagnostics["residual_l1"], 1e-12)
        self.assertTrue(law.diagnostics["truncation_target_met"])
        self.assertGreater(law.joint[0].sum(), 0)

    def test_conditional_mode_at_atom_is_not_unconditional(self):
        law = mc.stationary_law(6, 1, 0.05, truncation_tv_target=1e-8)
        conditional, diagnostics = law.conditional_mode(0)
        self.assertGreater(conditional[0], 0.5)
        np.testing.assert_allclose(law.joint.sum(axis=0), [0.5, 0.5], atol=1e-11)
        self.assertLess(diagnostics["conditional_mode_cap_error_bound"], 1e-5)
        with self.assertRaisesRegex(ValueError, "lattice"):
            law.conditional_mode(law.quantum/2)
        result = mc.sample_side_conditional(law, 0, managed_stay=1, managed_switch=0,
                                           h=1/120, tau=0, n=10000, seed=318300007)
        self.assertLess(abs(result["old_mode"].mean()-conditional[1]), 0.02)
        np.testing.assert_array_equal(result["old_mode"], result["x_mode"])

    def test_cap_refinement_and_stationary_balance(self):
        one = mc.stationary_law(6, 0, 0, truncation_tv_target=1e-7)
        two = mc.stationary_law(6, 0, 0, cap_packets=1.5*one.diagnostics["cap_packets"])
        comparison = mc.compare_stationary_laws(one, two)
        self.assertLess(comparison["total_variation"], 1e-7)
        increments = np.array(one.diagnostics["increments_lattice"])*one.quantum
        q = one.q[:, None]
        q_next = np.clip(q+increments, 0, one.diagnostics["cap_packets"])
        self.assertAlmostEqual(float(np.sum(one.joint*(q_next-q))), 0, places=12)

    def test_nonstationary_or_too_large_lattice_raises(self):
        with self.assertRaisesRegex(ValueError, "stationarity"):
            mc.stationary_law(9, 1, 0.1)
        with self.assertRaises(MemoryError):
            mc.stationary_law(6, 1, 0.05, max_states=2)


class IndependentPopulationTests(unittest.TestCase):
    def test_discrete_nodes_and_pairing_moments(self):
        a = mc.stationary_law(6, 1, 0, truncation_tv_target=1e-7)
        b = mc.stationary_law(6, 0, 0, truncation_tv_target=1e-7)
        nodes = [[0, 0], [a.quantum, b.quantum]]
        data = mc.sample_population(a, b, u=1, h=1/120, tau=0, n=20,
                                   seed=318300008, y_nodes=nodes, node_weights=[0.5, 0.5])
        self.assertEqual(data.y.shape, (20, 2))
        self.assertEqual(data.x.shape, (20, 4))
        np.testing.assert_array_equal(data.y[:, 0], data.x[:, 0])
        np.testing.assert_array_equal(data.y[:, 1], data.x[:, 2])
        self.assertIn("discrete", data.metadata["observation_law"])
        actions = {"00": np.zeros(20), "10": np.ones(20),
                   "01": np.ones(20), "11": np.zeros(20), "cb0": np.zeros(20)}
        score = mc.score_policies(data, actions)
        self.assertAlmostEqual(score["mean"]["GS"], np.mean(data.CStay-data.CSwitch))
        self.assertAlmostEqual(score["mean"]["Gamma"], -2*score["mean"]["GS"])
        self.assertAlmostEqual(score["mean"]["GS"], score["mean"]["F"]+score["mean"]["V"])
        index = score["metric_names"].index("GS")
        expected_se = np.std(data.CStay-data.CSwitch, ddof=1)/np.sqrt(20)
        self.assertAlmostEqual(score["se"]["GS"], expected_se)
        self.assertAlmostEqual(score["cross_sum"][index,index], np.sum((data.CStay-data.CSwitch)**2))

    def test_seed_repeat_and_all_same_actions_zero_contrasts(self):
        a = mc.stationary_law(6, 1, 0, truncation_tv_target=1e-7)
        b = mc.stationary_law(6, 0, 0, truncation_tv_target=1e-7)
        kwargs = dict(u=1, h=0.1, tau=0.1, n=20, seed=318300009)
        one, two = mc.sample_population(a,b,**kwargs), mc.sample_population(a,b,**kwargs)
        np.testing.assert_array_equal(one.x, two.x)
        np.testing.assert_array_equal(one.CStay, two.CStay)
        np.testing.assert_array_equal(one.CSwitch, two.CSwitch)
        score = mc.score_policies(one, np.zeros((20,4)))
        for name in ("GS", "GM", "GSM", "Gamma", "GS_given_M1", "GM_given_S1"):
            self.assertEqual(score["mean"][name], 0)
            self.assertEqual(score["se"][name], 0)

    def test_population_truncation_allowance_scope_and_units(self):
        a = mc.stationary_law(6, 1, 0, truncation_tv_target=1e-7)
        b = mc.stationary_law(6, 0, 0, truncation_tv_target=1e-7)
        bound = mc.population_cost_truncation_bound(a,b,u=1,h=0.1,tau=0.1)
        self.assertLessEqual(bound["full_stationary_episode_coupling_bound"], 2e-7)
        self.assertGreater(bound["per_policy_loss_absolute_bias_bound"], 0)
        self.assertAlmostEqual(bound["contrast_absolute_bias_bounds"]["Gamma"],
                               4*bound["per_policy_loss_absolute_bias_bound"])


if __name__ == "__main__":
    unittest.main()
