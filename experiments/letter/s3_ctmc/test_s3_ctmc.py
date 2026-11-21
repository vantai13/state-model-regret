"""Doan Van Tai — S3 controls, synthetic verdicts and saved S1-A regression.

No test invokes S3 truth. Files are confined to pytest's explicit S3 basetemp.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess

import numpy as np
import pytest

from experiments.letter import sweep_ctmc as old
from experiments.letter.s3_ctmc import integrity as io
from experiments.letter.s3_ctmc import runner
from experiments.letter.s3_ctmc import score_s3 as scorer
from experiments.letter.s3_ctmc import rescore_s3 as independent


def fake_record(index, d=.4, delta=.2, hs=(1., .7, 1.5)):
    rid = f"FAKE_{index:04d}"
    policies, features = [], []
    ds = d if isinstance(d, list) else [d]*3
    for h in hs:
        for age, bound in zip(scorer.AGES, ds):
            common = dict(regime=rid, h_T_int=h, tau_T_int=age, C_ref=100., status="COMPLETED", s=1., s_hat=1.)
            for rate in ("true", "hat"):
                policies.extend([
                    dict(**common, rule="Stationary_"+rate, regret_fresh=2., regret_stale=2.,
                         L_fresh=102., L_stale=102., p_new=0., p_old=0.),
                    dict(**common, rule="Hybrid_"+rate, regret_fresh=2.-delta, regret_stale=2.-delta,
                         L_fresh=102.-delta, L_stale=102.-delta, p_new=.005, p_old=.005,
                         D_fresh=.02, D_stale=bound-.02)])
                for side in ("fresh", "stale"):
                    features.append(dict(**common, side=side, level=rate, D=bound,
                                         D_fresh=.02, D_stale=bound-.02, hybrid_static_disagreement=.005))
    return dict(id=rid, status="COMPLETED", rows=policies, features=features,
                estimator=dict(status="VALID", method="MMPP/M/1", fallback=False))


def panel(n_inside=6, n_outside=14, inside=.2, outside=.02):
    return [fake_record(i+1, .4 if i < n_inside else .1,
                        inside if i < n_inside else outside) for i in range(n_inside+n_outside)]


def test_known_T1_T2_T3_and_independent_complete_report():
    data = panel()
    summary, age, collapsed = scorer.score_records(data, 20, h_grid=(1., .7, 1.5))
    p = summary["primary"]
    assert (p["T1"], p["T2"], p["T3"], p["S3"]) == ("PASS",)*4
    assert p["n_region"] == 6 and p["n_outside"] == 14 and p["coverage"] == .3
    assert p["region"]["delta_pp_mean"] == pytest.approx(.2)
    assert p["region"]["baseline_pp_mean"] == 2.
    assert p["region"]["hybrid_pp_mean"] == pytest.approx(1.8)
    assert p["region"]["delta_abs_mean"] == pytest.approx(.2)
    assert len(age) == 20*3*3*2*2 and len(collapsed) == 20*3*2*2
    assert independent.compare(summary, independent.independent_score(data, 20, horizons=(1., .7, 1.5))) > 0


@pytest.mark.parametrize("n_in,n_out,din,dout,key,verdict", [
    (5, 95, .2, .02, "T1", "FAIL"),
    (6, 14, -.1, .02, "T2", "FAIL"),
    (6, 14, .05, .02, "T2", "FAIL"),
    (6, 14, .2, -.1, "T3", "FAIL"),
    (4, 16, .2, .02, "T2", "NOT_EVALUABLE"),
    (16, 4, .2, .02, "T3", "NOT_EVALUABLE"),
    (0, 20, .2, .02, "T2", "NOT_EVALUABLE"),
    (20, 0, .2, .02, "T3", "NOT_EVALUABLE"),
])
def test_known_failures_and_small_regions(n_in, n_out, din, dout, key, verdict):
    data = panel(n_in, n_out, din, dout)
    result = scorer.score_records(data, n_in+n_out, h_grid=(1.,))[0]
    assert result["primary"][key] == verdict
    assert result["primary"]["S3"] != "PASS"
    independent.compare(result, independent.independent_score(data, n_in+n_out, horizons=(1.,)))


@pytest.mark.parametrize("where,key", [("inside", "T2"), ("outside", "T3")])
def test_CI_clause_can_fail_despite_favorable_mean(where, key):
    data = panel()
    varied = [-1., 1., 1., -1., 1., 1.] if where == "inside" else [-1., 1.]*7
    for j, delta in enumerate(varied):
        i = j if where == "inside" else j+6
        data[i] = fake_record(i+1, .4 if where == "inside" else .1, delta)
    p = scorer.score_records(data, 20, h_grid=(1.,))[0]["primary"]
    assert p[key] == "FAIL"
    assert p["region" if where == "inside" else "outside"]["delta_pp_mean"] >= -.05


def test_student_interval_uses_regimes_and_matches_hand_answer():
    lo, hi = scorer.ci([0., 2.])
    assert lo == pytest.approx(1.-12.706204736432095, abs=1e-9)
    assert hi == pytest.approx(1.+12.706204736432095, abs=1e-9)
    assert scorer.ci([2.]) == (None, None)
    assert scorer.ci([2.]*5) == (2., 2.)


def test_D_is_mean_of_two_tail_terms_not_disagreement_or_max_age():
    record = fake_record(1, [.1, .2, .6])
    _, rows = scorer.collapse_record(record, h_grid=(1.,))
    for row in rows:
        assert row["D"] == pytest.approx(.3)
        assert row["D"] != row["disagreement"]
        assert row["D"] != .6


def test_D_threshold_is_inclusive_and_no_threshold_refit():
    data = panel()
    for i in range(6):
        data[i] = fake_record(i+1, .28)
    p = scorer.score_records(data, 20, h_grid=(1.,))[0]["primary"]
    assert p["n_region"] == 6 and p["d_star"] == .28


def test_invalid_kept_in_N_and_not_zero_imputed():
    data = panel()
    record = data[-1]
    record["estimator"].update(status="INVALID_ESTIMATOR", method=None, fallback=True)
    for r in record["rows"]:
        if r["rule"].endswith("_hat"):
            r["status"] = "INVALID_ESTIMATOR"
    record["features"] = [r for r in record["features"] if r["level"] != "hat"]
    result = scorer.score_records(data, 20, h_grid=(1.,))[0]
    assert result["N"] == 20 and result["invalid_estimators"] == 1
    assert result["fallback_regimes"] == 1
    assert result["primary"]["coverage"] == .3
    assert result["primary"]["n_unknown"] == 1
    assert result["primary"]["T2"] == result["primary"]["T3"] == "NOT_EVALUABLE"
    independent.compare(result, independent.independent_score(data, 20, horizons=(1.,)))


def test_cpu_capped_and_absent_raw_never_pass_full_N():
    data = panel()
    data[-1] = dict(id=data[-1]["id"], status="CPU_CAP", rows=[], features=[])
    result = scorer.score_records(data[:-1], 20, h_grid=(1.,))[0]
    assert result["missing_raw_regimes"] == 1 and result["primary"]["T3"] == "NOT_EVALUABLE"
    result = scorer.score_records(data, 20, h_grid=(1.,))[0]
    assert result["statuses"]["CPU_CAP"] == 1 and result["primary"]["S3"] != "PASS"


@pytest.mark.parametrize("fault", ["duplicate_policy", "duplicate_feature", "C_ref", "D", "regret", "fresh_age", "disagreement"])
def test_corrupt_raw_is_rejected(fault):
    record = fake_record(1)
    if fault == "duplicate_policy": record["rows"].append(record["rows"][0])
    elif fault == "duplicate_feature": record["features"].append(record["features"][0])
    elif fault == "C_ref": record["rows"][0]["C_ref"] = 0.
    elif fault == "D": record["features"][0]["D"] += .1
    elif fault == "regret": record["rows"][0]["regret_fresh"] += .2
    elif fault == "fresh_age":
        record["rows"][0]["regret_fresh"] += .2
        record["rows"][0]["L_fresh"] += .2
    elif fault == "disagreement": record["features"][0]["hybrid_static_disagreement"] = .7
    with pytest.raises(ValueError): scorer.collapse_record(record, h_grid=(1.,))


def test_duplicate_raw_is_rejected():
    with pytest.raises(ValueError, match="duplicate raw"):
        scorer.score_records([fake_record(1), fake_record(1)], 2, h_grid=(1.,))


def test_independent_comparator_catches_wrong_sign_CI_count_and_verdict():
    summary = scorer.score_records(panel(), 20, h_grid=(1.,))[0]
    other = independent.independent_score(panel(), 20, horizons=(1.,))
    for key in ("delta_pp_mean", "delta_pp_ci95_low", "n_regimes"):
        bad = copy.deepcopy(other)
        bad["primary"]["region"][key] += 1
        with pytest.raises(AssertionError): independent.compare(summary, bad)
    other["primary"]["T3"] = "FAIL"
    with pytest.raises(AssertionError): independent.compare(summary, other)


def test_seeded_sampler_reuses_old_formula_restores_seeds_and_has_same_prefix(monkeypatch):
    old_seeds = old.SEEDS.copy()
    monkeypatch.setattr(old.x, "prepare", lambda *a, **k:pytest.fail("sampler requested stationary/finite-h values"))
    generated = runner.generate(16, runner.SEEDS["sample"], "S3")
    assert old.SEEDS == old_seeds
    assert [r.record() for r in generated] == [r.record() for r in runner.generate(32, runner.SEEDS["sample"], "S3")[:16]]
    assert generated[0].record()["A"] != old.sobol_regimes(16)[0].record()["A"]
    assert generated[0].record()["A"] != runner.generate(16, runner.SEEDS["pilot_sample"], "S3P")[0].record()["A"]
    assert len(set(runner.SEEDS.values())) == 4
    assert set(runner.SEEDS.values()).isdisjoint(old.SEEDS.values())


def test_frozen_resource_screen_uses_no_finite_h_truth(monkeypatch):
    monkeypatch.setattr(old.x.Chain, "V", lambda *a, **k:pytest.fail("screen requested truth"))
    calibration = io.read(runner.S1 / "pilot.json")["projection"]
    regime = runner.generate(16, runner.SEEDS["sample"], "S3")[0]
    row = runner.screened(regime, calibration)
    if row["initial_screen_status"] == "ELIGIBLE":
        assert row["projected_cpu_seconds"] == runner.projected_cost(row, calibration)
    assert row["status"] in ("ELIGIBLE", "REJECTED")


def test_actual_sample_is_first_600_in_sobol_order_and_cost_screen():
    cfg, sample = runner.load_sample()
    assert sample["selected_count"] == cfg["N"] == 600
    assert sample["finite_h_truth_computed"] is False
    expected = runner.generate(1024, runner.SEEDS["sample"], "S3")
    assert [r["regime"] for r in sample["screened"]] == [r.record() for r in expected[:sample["screened_count"]]]
    assert sample["selected"][-1] == sample["screened"][-1]
    for row in sample["selected"]:
        assert row["status"] == row["initial_screen_status"] == "ELIGIBLE"
        assert row["projected_cpu_seconds"] <= cfg["cpu_cap_seconds"]


def test_shards_cover_actual_600_without_overlap():
    rows = runner.load_sample()[1]["selected"]
    groups = [old.shard_rows(rows, f"{i}/2") for i in (0, 1)]
    a, b = [{r["id"] for r in group} for group in groups]
    assert not a & b and len(a | b) == 600


@pytest.mark.parametrize("purpose", ["pilot", "run"])
def test_worker_supplies_new_record_seed_and_unchanged_grids_without_truth(monkeypatch, tmp_path, purpose):
    meta = runner.load_sample()[1]["selected"][0]
    monkeypatch.setattr(old.x, "prepare", lambda *a, **k:dict(T_int=2., truncation={}))
    seeds_before = old.SEEDS.copy()
    def estimator(p, actual_purpose):
        assert actual_purpose == purpose
        assert old.SEEDS[purpose+"_record"] == runner.SEEDS[purpose+"_record"]
        return dict(status="VALID", s_hat=.1)
    def evaluate(p, hs, ages, shat):
        expected_h, expected_age = (old.PILOT_H, old.PILOT_AGES) if purpose == "pilot" else (old.H_GRID, old.AGES)
        assert hs == [2*h for h in expected_h] and ages == [2*t for t in expected_age]
        assert shat == .1
        return dict(rows=[], features=[], timing={})
    monkeypatch.setattr(old, "estimate_s", estimator)
    monkeypatch.setattr(old, "evaluate", evaluate)
    monkeypatch.setattr(old, "work_proxy", lambda *a, **k:{})
    result = runner.evaluate_one((meta, purpose, str(tmp_path), 30.))
    assert result["status"] == "COMPLETED" and old.SEEDS == seeds_before
    with pytest.raises(FileExistsError):
        runner.evaluate_one((meta, purpose, str(tmp_path), 30.))


def test_production_loader_rejects_pilot_raw(monkeypatch, tmp_path):
    monkeypatch.setattr(io, "OUT", tmp_path)
    rid = "S3_0001"
    io.write(tmp_path/"sample/config.json", dict(seeds=runner.SEEDS))
    io.write(tmp_path/"sample/sample.json", dict(selected=[dict(id=rid, regime={})]))
    directory = tmp_path/"runs/shard_0_of_2"
    raw = directory/"raw"/(rid+".json")
    io.write(raw, dict(id=rid, namespace=io.NAMESPACE, kind="RESOURCE_ONLY_NOT_S3", purpose="pilot", regime={}))
    io.write(directory/"receipt.json", dict(ids=[rid], lock_sha256="test-lock",
             seed_record=runner.SEEDS["run_record"], measured=[dict(id=rid, sha256=io.sha(raw))]))
    with pytest.raises(ValueError, match="not the frozen S3"):
        next(scorer.s3_records("test-lock"))


def test_wrong_lock_stops_before_legacy_engine(monkeypatch):
    def fail(**kwargs): raise ValueError("synthetic lock mismatch")
    monkeypatch.setattr(io, "verify_lock", fail)
    monkeypatch.setattr(runner, "legacy", lambda:pytest.fail("engine imported before lock verification"))
    with pytest.raises(ValueError, match="lock mismatch"):
        runner.run_shard("0/2", 15, "wrong")


def test_lock_detects_mutation_and_external_hash_pin(tmp_path):
    source = tmp_path / "input.txt"
    source.write_text("original")
    lock = tmp_path / "lock.json"
    io.write(lock, dict(namespace=io.NAMESPACE, state="LOCKED_BEFORE_TRUTH", files={"input.txt":io.sha(source)}))
    pin = io.sha(lock)
    assert io.verify_lock(lock, pin, tmp_path)["status"] == "PASS"
    with pytest.raises(ValueError, match="launch pin"): io.verify_lock(lock, "0"*64, tmp_path)
    source.write_text("changed")
    with pytest.raises(ValueError, match="input changed"): io.verify_lock(lock, pin, tmp_path)


def test_exclusive_json_and_csv_outputs(tmp_path):
    for path, writer, data in ((tmp_path/"a.json", io.write, {"a":1}),
                                (tmp_path/"b.csv", io.csv_write, [{"a":1}])):
        writer(path, data)
        original = path.read_bytes()
        with pytest.raises(FileExistsError): writer(path, data)
        assert path.read_bytes() == original


def test_gcp_script_syntax_and_invalid_shard_no_run_marker():
    script = io.CODE / "s3_gcp.sh"
    assert subprocess.run(["bash", "-n", str(script)], capture_output=True).returncode == 0
    result = subprocess.run(["bash", str(script), "bad"], capture_output=True, text=True)
    assert result.returncode == 2 and "SHARD must" in result.stderr


def saved_records(even_only=False):
    for path in sorted((runner.S1/"runs").glob("shard_*/receipt.json")):
        receipt = io.read(path)
        for m in receipt["measured"]:
            if even_only and int(m["id"].split("_")[-1]) % 2:
                continue
            raw = path.parent / "raw" / (m["id"]+".json")
            assert io.sha(raw) == m["sha256"]
            yield io.read(raw)


@pytest.fixture(scope="module")
def s1a_even_score(tmp_path_factory):
    summary, age, collapsed = scorer.score_records(saved_records(even_only=True), 501)
    other = independent.independent_score(saved_records(even_only=True), 501)
    checks = independent.compare(summary, other)
    destination = tmp_path_factory.mktemp("s1a_regression") / "regression.json"
    io.write(destination, dict(kind="TEST_ONLY_NOT_S3", N=501, independent_checks=checks, summary=summary))
    print(json.dumps(dict(test="S1A_even_raw_regression", N=501,
                          region=summary["primary"]["n_region"],
                          delta_pp=summary["primary"]["region"]["delta_pp_mean"], checks=checks,
                          output=str(destination))))
    return summary, collapsed


def test_raw_S1A_even_reproduces_S2_99_over_501_and_delta_2110655(s1a_even_score):
    summary, _ = s1a_even_score
    primary = summary["primary"]
    assert primary["N"] == 501 and primary["n_region"] == 99
    region = primary["region"]
    assert region["delta_pp_mean"] == pytest.approx(2.110655, abs=5e-7)
    assert region["baseline_pp_mean"] == pytest.approx(2.427720, abs=5e-7)
    assert region["hybrid_pp_mean"] == pytest.approx(.317065, abs=5e-7)
    assert region["delta_pp_ci95_low"] == pytest.approx(1.284329, abs=5e-7)
    assert region["delta_pp_ci95_high"] == pytest.approx(2.936981, abs=5e-7)
    assert region["delta_abs_mean"] == pytest.approx(5.588285, abs=5e-7)
    assert [s["n_region"] for s in summary["secondary"]] == [109, 93]


def test_D_hat_matches_actual_analyze_S2_on_three_S1A_regimes(s1a_even_score):
    # Call the existing analyzer in memory; never its main/output writer.
    path = io.ROOT / "results/letter/sweep/ctmc/s2/analyze_s2.py"
    spec = importlib.util.spec_from_file_location("s3_test_existing_s2_analyzer", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _, expected = module.load_pairs()
    ids = {"S1A_0002", "S1A_0004", "S1A_0006"}
    reference = expected[expected.regime.isin(ids) & expected.level.eq("hat")]
    lookup = {(r.regime, r.h_T_int, r.side):r for r in reference.itertuples()}
    compared = 0
    for r in s1a_even_score[1]:
        if r["regime"] in ids and r["level"] == "hat":
            before = lookup[(r["regime"], r["h_T_int"], r["side"])]
            assert r["D"] == pytest.approx(before.D, abs=1e-12)
            assert r["delta_pp"] == pytest.approx(before.delta_pp, abs=1e-10)
            compared += 1
    assert compared == 3*14*2
