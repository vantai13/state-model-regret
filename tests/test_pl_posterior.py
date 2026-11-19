"""Doan Van Tai — analytic controls and saved-exposure PL regressions only."""
from fractions import Fraction as F
import itertools
import json
import math

import numpy as np
import pytest
from scipy.linalg import expm

from experiments.letter import pl_posterior as pl


@pytest.fixture(scope="module")
def r2_raw():
    return json.loads((pl.ROOT / "results/letter/w1b/raw" / (pl.R2_PILOT + ".json")).read_text())


def test_separated_path_GS_matches_direct_4D_on_small_actual_ctmc():
    a = pl.ctmc.chain(F(7), F(1, 2), 2)
    b = pl.ctmc.chain(F(8), F(1, 2), 3)
    a1 = pl.ctmc.chain(F(13, 2), F(1, 2), 2)
    b1 = pl.ctmc.chain(F(17, 2), F(1, 2), 3)
    h, tau = .7, .11
    ga = a1.V([h])[0] - a.V([h])[0]
    gb = b1.V([h])[0] - b.V([h])[0]
    pa, pb = expm(a.Q.toarray() * tau), expm(b.Q.toarray() * tau)
    ua = np.linspace(-1.4, .8, a.n)
    ub = np.linspace(-.3, .7, b.n)
    # Deliberately use a wrong decision posterior; the costs still use true P.
    oa, ob = ua[::-1] - .17, ub[::-1] + .09
    m = pl.policy_metrics(dict(Ast=a, Bst=b), ua, ub, oa, ob, ga, gb, pa @ ga, pb @ gb,
                          h, a.r + b.r, a1.r + b1.r - a.r - b.r)
    direct = sum(a.pi[ya] * b.pi[yb] * pa[ya, xa] * pb[yb, xb]
                 * (int(oa[ya] + ob[yb] < 0) - int(ua[xa] + ub[xb] < 0)) * (ga[xa] + gb[xb])
                 for ya, yb, xa, xb in itertools.product(range(a.n), range(b.n), range(a.n), range(b.n)))
    assert m["G_S_packet_s"] == pytest.approx(direct, abs=3e-14)
    assert m["both_side_regret_pct_C_ref"] == max(m["regret_new_pct_C_ref"], m["regret_old_pct_C_ref"])


def test_knn_hand_example_includes_all_boundary_ties_and_small_mode_pool():
    y, x = np.array([0, 8, 8, 12, 1]), np.array([2, 4, 6, 8, 10])
    v = np.arange(14, dtype=float)
    got, info = pl.knn_posterior(y, x, v, 14, k=2)
    assert got[0, 4] == 4.  # n=2: all three distance-2 pairs, not only k=2.
    np.testing.assert_equal(got[0, 1::2], 10.)
    assert info["max_selected"] == 3
    assert info["missing_modes"] == []


def test_missing_mode_fallback_means_all_pairs_even_when_more_than_k():
    y = np.tile([0, 2, 4, 6, 8], 12)
    x = np.arange(60) % 10
    v = np.arange(10, dtype=float) ** 2
    got, info = pl.knn_posterior(y, x, v, 10)
    np.testing.assert_allclose(got[0, 1::2], v[x].mean())
    assert info["missing_modes"] == [1]
    assert info["max_selected"] == 60


def test_knn_aggregated_implementation_matches_independent_neighbor_enumeration():
    rng = np.random.default_rng(9182)
    for pairs in (1, 13, 50, 121):
        y, x = rng.integers(0, 30, (2, pairs))
        v = rng.normal(size=(3, 30))
        got, _ = pl.knn_posterior(y, x, v, 30, k=7)
        for state in range(30):
            pool = np.flatnonzero(y % 2 == state % 2)
            if not len(pool):
                chosen = np.arange(pairs)
            elif len(pool) < 7:
                chosen = pool
            else:
                distance = abs(y[pool] // 2 - state // 2)
                radius = np.sort(distance)[6]
                chosen = pool[distance <= radius]
            np.testing.assert_allclose(got[:, state], v[:, x[chosen]].mean(axis=1), atol=1e-14)


@pytest.mark.parametrize("maximum", [1, 2, 9])
def test_two_barrier_reflection_matches_scalar_blocked_queue(maximum):
    rng = np.random.default_rng(12991)
    for initial in range(maximum + 1):
        steps = rng.integers(-1, 2, 700)
        state, expected = initial, []
        for increment in steps:
            state = min(maximum, max(0, state + int(increment)))
            expected.append(state)
        np.testing.assert_array_equal(pl.reflect_walk(steps, initial, maximum), expected)


def test_uniformized_event_operator_is_original_Q_including_blocked_boundaries():
    ch = pl.ctmc.chain(F(7), F(1, 2), 3)
    gamma = float(ch.load) + float(ch.a) + pl.ctmc.MU + 1 / float(ch.kappa)
    matrix = np.zeros((ch.n, ch.n))
    for state in range(ch.n):
        load = float(ch.load) + (float(ch.a) if state % 2 else -float(ch.a))
        cut = sorted(set([0., (1 / float(ch.kappa)) / gamma,
                          (1 / float(ch.kappa) + load) / gamma,
                          (1 / float(ch.kappa) + load + pl.ctmc.MU) / gamma, 1.]))
        for lo, hi in zip(cut, cut[1:]):
            target = pl.uniformized_events(ch, np.array([(lo + hi) / 2]), state)[0]
            matrix[state, target] += hi - lo
    np.testing.assert_allclose(matrix, np.eye(ch.n) + ch.Q.toarray() / gamma, atol=1e-15)
    # This identity establishes the exact polling transition, not an Euler step.
    delta = .37
    mixture = np.zeros_like(matrix)
    power = np.eye(ch.n)
    weight = math.exp(-gamma * delta)
    for j in range(100):
        if j:
            power = power @ matrix
            weight *= gamma * delta / j
        mixture += weight * power
    np.testing.assert_allclose(mixture, expm(ch.Q.toarray() * delta), atol=1e-14)


def test_history_event_chunking_does_not_change_any_polling_state():
    ch = pl.ctmc.chain(F(7), F(1, 2), 3)
    a, info_a = pl.sample_history(ch, .017, 200, np.random.default_rng(7491234), chunk_events=7)
    b, info_b = pl.sample_history(ch, .017, 200, np.random.default_rng(7491234), chunk_events=200000)
    np.testing.assert_array_equal(a, b)
    assert info_a == info_b
    assert len(a) == 201 and np.all((0 <= a) & (a < ch.n))


def test_prefixes_use_only_available_lag_10_pairs():
    tint = 4.630634303080048
    delta = 3 * tint / 10
    assert [pl.finite_prefix_steps(length * tint, delta) + 1 - 10 for length in pl.L_GRID] == [91, 324, 991, 3324]
    assert pl.finite_prefix_steps(1000 * tint, tint / 10) == 10000


def test_seed_namespaces_and_heaviest_pilot_selection():
    raws = pl.matched_raws()
    selected = pl.pilot_selection(raws)
    assert len(raws) == 92
    assert selected[1]["id"] == "A_u1-2_lA9_x1-2_k2"
    assert max(pl.saved_tint(selected[1])["N"].values()) == max(
        max(pl.saved_tint(r)["N"].values()) for r in raws)
    assert pl.seed_for(2, 1, 4) == 7402004
    assert pl.seed_for(2, 3, 4, True) == 7492104
    assert pl.EXCLUDED not in {r["id"] for r in raws}


def test_true_kernel_reproduces_one_W1b_regime(r2_raw):
    saved = pl.saved_tint(r2_raw)["h"]
    horizons = [F(r["h"]) for r in saved]
    p = pl.prepare(r2_raw, horizons)
    ch = {name: p[name] for name in ("Ast", "Asw", "Bst", "Bsw")}
    tau = r2_raw["T_int"]
    post = {side: pl.age.posterior_full(ch[side + "st"],
              np.column_stack([p["d" + side].T, p["dh" + side].T]), tau) for side in ("A", "B")}
    for i, row in enumerate(saved):
        m = pl.policy_metrics(ch, p["dhA"][i], p["dhB"][i], post["A"][:, len(saved) + i],
            post["B"][:, len(saved) + i], p["dA"][i], p["dB"][i], post["A"][:, i], post["B"][:, i],
            float(horizons[i]), p["r_stay"], p["s"])
        assert pl.control_comparison(m, row)["passed"]
        assert m["regret_new_pct_C_ref"] == pytest.approx(row["regret"]["M0_new"], abs=1e-9)
        assert m["regret_old_pct_C_ref"] == pytest.approx(row["regret"]["M0_old"], abs=1e-9)


def test_T4_slope_and_finite_h_reproduce_saved_R2_O1_pilot(r2_raw):
    _, ch = pl.r2.chains_for(r2_raw)
    pred = pl.t4_prediction(r2_raw, ch)
    assert pred["classification"] == "mixed_sign"
    assert pred["sigma"] == pytest.approx(-.21302092437311448, abs=1e-12)
    saved = json.loads((pl.ROOT / "results/letter/r2_o1/raw" / (pl.R2_PILOT + ".json")).read_text())
    old = next(row for row in saved["rows"] if row["twin"] == "T4" and row["h_T_int"] == 300)
    new = next(row for row in pl.q2_evaluate(r2_raw, 1, pred)["rows"] if row["twin"] == "T4")
    assert new["slope_measured"] == pytest.approx(old["slope_measured"], abs=2e-10)
    assert new["G_S_packet_s"] == pytest.approx(old["G_S_abs"], abs=1e-8)
    assert new["G_S_tail_bound"] < 1e-8


def test_gain_bias_tail_enclosure_against_direct_existing_engine():
    ch = pl.ctmc.chain(F(7), F(1, 2), 4)
    horizons = [.1, 20., 200.]
    got, bounds, details = pl.gain_bias_values(ch, horizons)
    direct = ch.V(horizons)
    for i in range(3):
        assert np.max(abs(got[i] - direct[i])) <= bounds[i] + 3e-12
    assert details[-1]["computed_until"] < 200.


def test_zero_slope_limiting_rule_uses_fluid_and_strict_ties():
    ch = pl.ctmc.chain(F(7), F(1, 2), 2)
    remainder = np.array([-1., -1., 0., 0., 1., 1.])
    share, zero = pl.limiting_share(dict(Ast=ch, Bst=ch), [0., 0.], [0., 0.],
                                   remainder, remainder * 0)
    assert share == pytest.approx(float(ch.pi[:2].sum()))
    assert zero == pytest.approx(1.)
    assert share < 1.  # Exact zero remainder chooses Stay.


def test_control_failure_stops_all_scientific_scoring():
    result = pl.score_records([dict(controls=[dict(passed=False)])], {})
    assert result["tests"]["H-PL1"]["verdict"] == "BUG_STOP"
    assert result["remaining_tests"] == "NOT_SCORED"


def test_truth_refuses_uncommitted_lock_before_any_marker(monkeypatch, tmp_path):
    monkeypatch.setattr(pl, "OUT", tmp_path)
    monkeypatch.setattr(pl, "require_environment", lambda: None)
    def reject(require_committed=False):
        assert require_committed
        raise RuntimeError("uncommitted lock")
    monkeypatch.setattr(pl, "verify_lock", reject)
    with pytest.raises(RuntimeError, match="uncommitted"):
        pl.truth()
    assert not list(tmp_path.iterdir())


def test_lock_detects_modified_input_without_running_truth(monkeypatch, tmp_path):
    monkeypatch.setattr(pl, "OUT", tmp_path)
    monkeypatch.setattr(pl, "ROOT", tmp_path)
    code = tmp_path / "input.py"
    code.write_text("before\n")
    pl.write_once(tmp_path / "lock.json", dict(sha256={"input.py": pl.sha(code)}, environment=pl.environment()))
    monkeypatch.setattr(pl, "source_paths", lambda: [code])
    assert pl.verify_lock()["sha256"]["input.py"] == pl.sha(code)
    code.write_text("after\n")
    with pytest.raises(ValueError, match="locked file changed"):
        pl.verify_lock()


def test_amplitude_falls_back_to_saved_evaluation_and_checks_consistency():
    raws = pl.matched_raws()
    missing = [r for r in raws if "a" not in r["case"]]
    present = [r for r in raws if "a" in r["case"]]
    assert missing and present
    assert all(pl.regime_amplitude(r) == pl.F(str(pl.saved_tint(r)["a"])) for r in raws)
    bad = dict(present[0], case=dict(present[0]["case"], a="99"))
    with pytest.raises(ValueError, match="amplitude mismatch"):
        pl.regime_amplitude(bad)


def test_truth_population_uses_pilot_projection_per_regime_only():
    report = dict(calibration_coefficients=dict(prepare_cpu_seconds=1., posterior_cpu_seconds=0.,
                  simulation_cpu_seconds=0., knn_cpu_seconds=0., pair_cpu_seconds=0.),
                  work=[dict(id="b", truth_prepare_work=10., truth_posterior_work=0., simulation_work=0.,
                             truth_knn_work=0., truth_pair_work=0.),
                        dict(id="a", truth_prepare_work=5000., truth_posterior_work=0., simulation_work=0.,
                             truth_knn_work=0., truth_pair_work=0.)])
    population, costs = pl.truth_population(report)
    assert population == ["b"] and costs == {"b": 10., "a": 5000.}
    assert pl.truth_population(report, cap=6000)[0] == ["a", "b"]
