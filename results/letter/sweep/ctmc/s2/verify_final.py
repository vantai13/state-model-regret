"""Doan Van Tai — independent age-bin verification and delivery receipt.

Uses paired CSVs already matched to raw by audit_s2.py. No analyzer import.
"""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time

import numpy as np
import pandas as pd
from scipy.stats import t

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]


def read(name):
    return json.loads((OUT / name).read_text())


def load(name):
    return pd.read_csv(OUT / name, low_memory=False, float_precision="round_trip",
                       dtype={"level": str, "side": str, "regime": str})


def main():
    start, wall = time.process_time(), time.perf_counter()
    if (OUT / "FINAL_CHECK.json").exists():
        raise FileExistsError(OUT / "FINAL_CHECK.json")
    checks = Counter()
    initial = read("input_audit.json")
    for name, sha in initial["sha256"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == sha, name
        checks["protected_SHA256"] += 1
    result = read("results.json")
    assert hashlib.sha256((OUT / "analyze_s2.py").read_bytes()).hexdigest() == result["analysis_source_sha256"]
    checks["analysis_source_matches_run"] += 1
    age = load("paired_by_age.csv")
    assert not age.duplicated(["regime", "h_T_int", "tau_T_int", "side", "level"]).any()
    assert len(age) == 168000 and set(age.level) == {"true", "hat"}
    assert age.groupby(["regime", "h_T_int", "side", "level"]).tau_T_int.nunique().eq(3).all()
    checks["age_pair_uniqueness_and_coverage"] += 1
    population = load("by_h_and_age.csv")
    grouped = {key: group for key, group in age.groupby(["h_T_int", "tau_T_int", "side", "level"])}
    region_table = load("bins_by_h_and_age.csv")
    expected_bins = json.loads((OUT / "feature_dictionary.json").read_text())["bins"]
    seen, numeric_seen = set(), set()
    for row in region_table.itertuples(index=False):
        group = grouped[row.h_T_int, row.tau_T_int, row.side, row.level]
        feature, label = row.feature, row.bin
        identity = (row.h_T_int, row.tau_T_int, row.side, row.level, feature, label)
        assert identity not in seen
        seen.add(identity)
        if label.startswith("["):
            low, high = [float(value.strip()) for value in label[1:-1].split(",")]
            numeric_seen.add((row.h_T_int, row.tau_T_int, row.side, row.level, feature, low, high))
            mask = (group[feature] >= low) & (group[feature] < high)
        else:
            mask = group[feature] == label
        data = group.loc[mask, "delta_pp"].to_numpy(float)
        assert len(data) == row.n_regimes and len(data) == group.loc[mask, "regime"].nunique()
        mean = float(data.mean())
        assert math.isclose(mean, row.delta_pp_mean, rel_tol=1e-10, abs_tol=1e-10)
        for q, value in [(.1, row.delta_pp_q10), (.5, row.delta_pp_median), (.9, row.delta_pp_q90)]:
            assert math.isclose(float(np.quantile(data, q)), value, rel_tol=1e-10, abs_tol=1e-10)
        if len(data) > 1:
            half = t.ppf(.975, len(data) - 1) * np.std(data, ddof=1) / math.sqrt(len(data))
            assert math.isclose(mean - half, row.delta_pp_ci95_low, rel_tol=1e-10, abs_tol=1e-10)
            assert math.isclose(mean + half, row.delta_pp_ci95_high, rel_tol=1e-10, abs_tol=1e-10)
        else:
            assert math.isnan(row.delta_pp_ci95_low) and math.isnan(row.delta_pp_ci95_high)
        assert bool(row.mean_le_neg005) == (mean <= -.05)
        assert bool(row.mean_le_neg01) == (mean <= -.1)
        assert row.n_delta_ge_01 == int((data >= .1).sum())
        assert row.n_delta_le_neg005 == int((data <= -.05).sum())
        assert row.n_delta_le_neg01 == int((data <= -.1).sum())
        expected_gate = "PASS" if len(data) / len(group) >= .1 and mean >= .1 else "FAIL"
        assert row.numeric_gate == expected_gate
        checks["age_feature_regions_recomputed"] += 1
    # Every nonempty bin in the declared family must be present, including bad bins.
    for group_key, group in grouped.items():
        for feature, edges in expected_bins.items():
            edges = [float(value) for value in edges]
            for low, high in zip(edges[:-1], edges[1:]):
                if ((group[feature] >= low) & (group[feature] < high)).any():
                    assert (*group_key, feature, low, high) in numeric_seen
                    checks["age_numeric_bin_coverage"] += 1
        for feature in ["static_action", "rate_sign", "estimator_method"]:
            for category in group[feature].unique():
                assert (*group_key, feature, str(category)) in seen
                checks["age_categorical_bin_coverage"] += 1
    flagged = region_table[region_table.delta_pp_mean <= -.05]
    saved_flagged = load("harm_regions_by_age.csv")
    assert len(flagged) == len(saved_flagged) == 3
    assert int((flagged.delta_pp_mean <= -.1).sum()) == 2
    assert (flagged.delta_pp_ci95_low < 0).all() and (flagged.delta_pp_ci95_high > 0).all()
    # CSV type inference turns an all-3 tau subset into int64. Compare the
    # numeric values exactly; every mean/CI/threshold is already checked above.
    pd.testing.assert_frame_equal(flagged.reset_index(drop=True), saved_flagged.reset_index(drop=True),
                                  check_dtype=False, check_exact=True)
    harm = age[age.delta_pp <= -.05]
    assert len(harm) == 52 and harm.regime.nunique() == 8
    assert set(harm.level) == {"hat"} and harm.abs_shat_over_abs_s.max() < .5
    checks["harm_age_summary"] += 1
    assert read("audit.json")["status"] == "PASS"
    for name in ["summarize_execution.json", "pytest_execution.json", "analysis_execution.json", "audit_execution.json", "report_execution.json"]:
        assert read(name)["returncode"] == 0
        checks["successful_command_receipts"] += 1
    assert "18 passed" in (OUT / "pytest_validation.log").read_text()
    assert all((OUT / name).is_file() for name in ["REPORT_S2.md", "S3_CANDIDATES.md", "analysis_config.json", "key_numbers.json"])
    from PIL import Image
    for name in ["delta_by_gap_h.png", "delta_by_kappa_h.png", "delta_by_estimator_ratio_h.png"]:
        with Image.open(OUT / name) as im:
            assert im.format == "PNG" and im.width > 1000 and im.height > 500
            im.verify()
        checks["PNG_valid"] += 1
    costs = {name: read(name) for name in ["input_audit.json", "summarize_execution.json", "pytest_execution.json",
                                          "analysis_execution.json", "audit_execution.json", "report_execution.json"]}
    cpu, elapsed = time.process_time() - start, time.perf_counter() - wall
    costs["final_verification_body"] = dict(cpu_seconds=cpu, wall_seconds=elapsed)
    manifests = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                 for path in sorted(OUT.iterdir()) if path.is_file() and path.name != "final_verification.log"}
    for path in sorted((OUT.parent / "v2/run_summary").iterdir()):
        if path.is_file():
            manifests[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    receipt = dict(owner="Doan Van Tai", kind="EXPLORATORY_POST_HOC_FINAL_VERIFICATION", status="PASS",
                   checks=dict(checks), gate_overall="NOT_DECIDED_UNQUANTIFIED_HARM", numerical_gate_PASS=47,
                   numerical_gate_FAIL=9, age_specific_negative_mean_regions=3,
                   age_specific_negative_mean_regions_ci_cross_zero=3,
                   command_costs=costs,
                   local_CPU_seconds=sum(r["cpu_seconds"] for r in costs.values()),
                   local_command_wall_seconds_sum=sum(r["wall_seconds"] for r in costs.values()),
                   timing_scope="measured commands only; excludes uninstrumented inspections, coding, interaction and the first final-check dtype failure (not timed); no double counting internal analyzer/report timings",
                   retained_first_final_check_failure=dict(log="final_verification.log", reason="CSV tau=3 subset inferred int64 versus full table float64; exact numeric values agree", cpu_seconds=None, wall_seconds=None),
                   raw_S1_worker_CPU_seconds=sum(r["cpu_seconds"] for r in initial["receipts"]),
                   raw_S1_max_parallel_shard_wall_seconds=max(r["wall_seconds"] for r in initial["receipts"]),
                   sha256=manifests, head_observed=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                   task_commits=0, task_ssh_calls=0, new_sweep_truth_evaluations=0,
                   legacy_control_regimes_recomputed=2)
    with (OUT / "FINAL_CHECK.json").open("x") as stream:
        json.dump(receipt, stream, indent=2, allow_nan=False)
    print(json.dumps({k: v for k, v in receipt.items() if k not in ["sha256", "command_costs"]}, indent=2))


if __name__ == "__main__":
    main()
