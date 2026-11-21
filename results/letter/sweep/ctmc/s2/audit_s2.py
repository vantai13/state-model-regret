"""Independent S2 rescore from committed raw; does not import analyze_s2.

Doan Van Tai. No CTMC evaluator or simulation; all writes are exclusive.
"""
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import time

from scipy.stats import t

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
BASE = OUT.parent
CHECKS = Counter()
ERRORS = defaultdict(float)


def read(path):
    return json.loads(Path(path).read_text())


def rows(name):
    with (OUT / name).open(newline="") as stream:
        yield from csv.DictReader(stream)


def close(got, expected, label, atol=1e-9):
    if expected is None:
        assert got in (None, ""), (label, got)
    else:
        error = abs(float(got) - expected)
        ERRORS[label] = max(ERRORS[label], error)
        assert error <= atol + 1e-10 * max(abs(expected), abs(float(got))), (label, got, expected)
    CHECKS[label] += 1


def key(row):
    return float(row["h_T_int"]), row["side"], row["level"]


def quantile(data, p):
    values = sorted(data)
    z = (len(values) - 1) * p
    lo, hi = math.floor(z), math.ceil(z)
    return values[lo] + (values[hi] - values[lo]) * (z - lo)


def summary_check(row, data, denominator):
    n = len(data)
    assert int(row["n_regimes"]) == n
    assert int(row["denominator_regimes"]) == denominator
    close(row["share_regimes"], n / denominator, "regime_share")
    for field in ["delta_abs", "delta_pp"]:
        values = [r[field] for r in data]
        mean = statistics.fmean(values) if n else None
        low = high = None
        if n > 1:
            half = float(t.ppf(.975, n - 1)) * statistics.stdev(values) / math.sqrt(n)
            low, high = mean - half, mean + half
        measures = {"mean": mean, "median": statistics.median(values) if n else None,
                    "q10": quantile(values, .1) if n else None,
                    "q90": quantile(values, .9) if n else None,
                    "min": min(values) if n else None, "max": max(values) if n else None,
                    "ci95_low": low, "ci95_high": high}
        for label, expected in measures.items():
            close(row[field + "_" + label], expected, "summary_" + field + "_" + label)
    for field in ["baseline_pp", "hybrid_pp", "baseline_abs", "hybrid_abs", "disagreement"]:
        close(row[field + "_mean"], statistics.fmean(r[field] for r in data) if n else None,
              "summary_" + field)
    delta = [r["delta_pp"] for r in data]
    for field, expected in {
        "n_delta_ge_01": sum(v >= .1 for v in delta),
        "n_delta_le_neg005": sum(v <= -.05 for v in delta),
        "n_delta_le_neg01": sum(v <= -.1 for v in delta),
        "n_abs_delta_lt_005": sum(abs(v) < .05 for v in delta),
    }.items():
        assert int(row[field]) == expected, (field, row[field], expected)
        CHECKS[field] += 1
    verdict = "NOT_EVALUABLE" if not n else "PASS" if n / denominator >= .1 and statistics.fmean(delta) >= .1 else "FAIL"
    assert row["numeric_gate"] == verdict
    CHECKS["numeric_gate"] += 1


def main():
    start, wall = time.process_time(), time.perf_counter()
    if (OUT / "audit.json").exists():
        raise FileExistsError(OUT / "audit.json")
    initial = read(OUT / "input_audit.json")
    for name, sha in initial["sha256"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == sha, name
        CHECKS["protected_file_unchanged"] += 1
    expected_age, expected_regime = {}, {}
    for path in sorted((BASE / "v2/runs").glob("shard_*/raw/*.json")):
        record = read(path)
        assert record["status"] == "COMPLETED"
        policies = {(r["h_T_int"], r["tau_T_int"], r["rule"]): r for r in record["rows"]}
        by_regime = defaultdict(list)
        for feature in record["features"]:
            h, tau = feature["h_T_int"], feature["tau_T_int"]
            side, level = feature["side"], feature["level"]
            static = policies[h, tau, "Stationary_" + level]
            hybrid = policies[h, tau, "Hybrid_" + level]
            assert static["C_ref"] == hybrid["C_ref"] == feature["C_ref"]
            cref = static["C_ref"]
            absolute = static["regret_" + side] - hybrid["regret_" + side]
            gain = 100 * absolute / cref
            close(feature["benefit_pp_C_ref"], gain, "raw_feature_delta")
            close(feature["D"], feature["D_fresh"] + feature["D_stale"], "raw_D_identity")
            rate = feature["s"] if level == "true" else feature["s_hat"]
            switch = rate < 0
            p = hybrid["p_new" if side == "fresh" else "p_old"]
            disagreement = 1 - p if switch else p
            close(feature["hybrid_static_disagreement"], disagreement, "raw_disagreement")
            f = record["regime_features"]
            chosen = f["B_rho_switch"] if switch else f["A_rho_stay"]
            other = f["A_rho_switch"] if switch else f["B_rho_stay"]
            values = dict(C_ref=cref, delta_abs=absolute, delta_pp=gain,
                          baseline_abs=static["regret_" + side], hybrid_abs=hybrid["regret_" + side],
                          baseline_pp=100 * static["regret_" + side] / cref,
                          hybrid_pp=100 * hybrid["regret_" + side] / cref,
                          D=feature["D"], D_side=feature["D_" + side], disagreement=disagreement,
                          abs_s_over_r_min=abs(f["s"]) / f["r_min"],
                          kappa_min_over_T_int=min(f["A_kappa_over_T_int"], f["B_kappa_over_T_int"]),
                          kappa_max_over_T_int=max(f["A_kappa_over_T_int"], f["B_kappa_over_T_int"]),
                          A_kappa_over_T_int=f["A_kappa_over_T_int"], B_kappa_over_T_int=f["B_kappa_over_T_int"],
                          load_imbalance=abs(f["A_base_rho"] - f["B_base_rho"]),
                          load_level=max(f["A_base_rho"], f["B_base_rho"]),
                          load_balance_other_minus_chosen=other - chosen,
                          abs_shat_over_abs_s=abs(f["s_hat"] / f["s"]) if f["s"] else None,
                          static_action="Switch" if switch else "Stay",
                          estimator_method=record["estimator"]["method"],
                          rate_sign="same_sign" if (f["s"] > 0) - (f["s"] < 0) ==
                          (f["s_hat"] > 0) - (f["s_hat"] < 0) else "different_sign")
            identity = (record["id"], h, tau, side, level)
            assert identity not in expected_age
            expected_age[identity] = values
            by_regime[h, side, level].append(values)
        for group, data in by_regime.items():
            assert len(data) == 3
            values = {}
            for field in data[0]:
                sample = [r[field] for r in data]
                values[field] = sample[0] if isinstance(sample[0], str) or sample[0] is None else statistics.fmean(sample)
            values["regime"] = record["id"]
            expected_regime[record["id"], *group] = values
    assert len(expected_age) == 168000 and len(expected_regime) == 56000
    for row in rows("paired_by_age.csv"):
        identity = (row["regime"], float(row["h_T_int"]), float(row["tau_T_int"]), row["side"], row["level"])
        expected = expected_age[identity]
        for field, value in expected.items():
            if isinstance(value, str):
                assert row[field] == value
            else:
                close(row[field], value, "paired_age_" + field)
        CHECKS["paired_age_rows"] += 1
    assert CHECKS["paired_age_rows"] == len(expected_age)
    groups, age_groups = defaultdict(list), defaultdict(list)
    for identity, record in expected_age.items():
        age_groups[identity[1], identity[3], identity[4], identity[2]].append(record)
    for row in rows("paired_regime_h.csv"):
        identity = row["regime"], *key(row)
        expected = expected_regime[identity]
        for field, value in expected.items():
            if isinstance(value, str):
                assert row[field] == value
            else:
                close(row[field], value, "paired_regime_" + field)
        groups[key(row)].append(expected)
        CHECKS["paired_regime_rows"] += 1
    assert CHECKS["paired_regime_rows"] == len(expected_regime)
    for row in rows("by_h.csv"):
        data = groups[key(row)]
        summary_check(row, data, 1000)
    for row in rows("by_h_and_age.csv"):
        data = age_groups[*key(row), float(row["tau_T_int"])]
        summary_check(row, data, 1000)
    del expected_age, age_groups
    bins = list(rows("bins_by_h.csv"))
    for row in bins:
        feature, label = row["feature"], row["bin"]
        if label.startswith("["):
            low, high = map(float, label[1:-1].split(","))
            data = [r for r in groups[key(row)] if r[feature] is not None and low <= r[feature] < high]
        else:
            data = [r for r in groups[key(row)] if r[feature] == label]
        summary_check(row, data, 1000)
    for row in rows("hypotheses_AB.csv"):
        h, side, level = key(row)
        if row["hypothesis"] == "H-A":
            assert h <= 3 and side == "fresh"
            data = [r for r in groups[key(row)] if r["abs_s_over_r_min"] <= .1 and r["static_action"] == "Stay"]
            hit = sum(r["delta_pp"] >= .1 for r in data)
            expected = "NOT_EVALUABLE" if not data else "PASS_MAJORITY" if hit / len(data) > .5 else "FAIL_MAJORITY"
        else:
            data = [r for r in groups[key(row)] if r["abs_s_over_r_min"] >= .3 or h >= 10]
            hit = sum(abs(r["delta_pp"]) < .05 for r in data)
            expected = "NOT_EVALUABLE" if not data else "ALL_MATCH" if hit == len(data) else "COUNTEREXAMPLES"
        summary_check(row, data, 1000)
        assert row["hypothesis_verdict"] == expected
        close(row["share_matching"], hit / len(data) if data else None, "hypothesis_AB_share")
    thresholds, grid_scores = {}, {}
    config = read(OUT / "analysis_config.json")
    for group, data in groups.items():
        train = [r for r in data if int(r["regime"].split("_")[-1]) % 2]
        scores = []
        for d in config["H_C"]["threshold_grid"]:
            selected = [r for r in train if r["D"] >= d]
            tp = sum(r["delta_pp"] >= .1 for r in selected)
            n_positive = sum(r["delta_pp"] >= .1 for r in train)
            f1 = 2 * tp / (len(selected) + n_positive) if len(selected) + n_positive else 0.
            scores.append((f1, d, len(selected), tp, n_positive))
            grid_scores[group, d] = scores[-1]
        best = min((r for r in scores if r[2] / len(train) >= .1), key=lambda r: (-r[0], r[1]))
        thresholds[group] = best[1]
    for row in rows("hc_threshold_selection.csv"):
        d = float(row["d_star"])
        score = grid_scores[key(row), d]
        close(row["f1"], score[0], "HC_training_f1")
        assert int(row["n_selected"]) == score[2]
        assert row["selected"] == str(d == thresholds[key(row)])
        CHECKS["HC_grid_rows"] += 1
    for row in rows("hypothesis_C.csv"):
        assert float(row["d_star"]) == thresholds[key(row)]
        parity = 1 if row["split"] == "train_odd" else 0
        data = [r for r in groups[key(row)] if int(r["regime"].split("_")[-1]) % 2 == parity]
        selected = [r for r in data if r["D"] >= float(row["d_star"])]
        summary_check(row, selected, len(data))
        tp = sum(r["delta_pp"] >= .1 for r in selected)
        positives = sum(r["delta_pp"] >= .1 for r in data)
        assert int(row["true_positive"]) == tp
        close(row["precision"], tp / len(selected) if selected else None, "HC_precision")
        close(row["recall"], tp / positives if positives else None, "HC_recall")
    for row in rows("gates_by_h.csv"):
        candidates = [r for r in bins if key(r) == key(row)]
        passing = [r for r in candidates if r["numeric_gate"] == "PASS"]
        assert int(row["n_passing_feature_bins"]) == len(passing)
        overall_mean = statistics.fmean(r["delta_pp"] for r in groups[key(row)])
        population = "PASS" if overall_mean >= .1 else "FAIL"
        assert row["population_numeric_gate"] == population
        assert row["feature_region_numeric_gate"] == ("PASS" if passing or population == "PASS" else "FAIL")
        assert row["harm_clause"] == "NOT_DECIDED"
        CHECKS["gates_by_h"] += 1
    for row in rows("harm_regime_h.csv"):
        record = expected_regime[row["regime"], *key(row)]
        assert record["delta_pp"] <= -.05
        close(row["delta_pp"], record["delta_pp"], "harm_delta")
    expected_harm = sum(r["delta_pp"] <= -.05 for r in expected_regime.values())
    assert sum(1 for _ in rows("harm_regime_h.csv")) == expected_harm
    legacy = [read(p) for p in sorted((OUT / "pytest_validation").glob("test_matches_saved*/equivalence.json"))
              if not p.parent.is_symlink()]
    assert len(legacy) == 2
    assert {r["id"] for r in legacy} == {"XCTMC_001", "XCTMC_002"}
    for r in legacy:
        assert max(r["max_absolute_errors"].values()) <= 2e-10
    result = dict(owner="Doan Van Tai", kind="EXPLORATORY_POST_HOC_INDEPENDENT_RESCORE",
                  status="PASS", no_import_of_analysis_or_evaluator=True,
                  checks=dict(CHECKS), max_absolute_error=dict(ERRORS), legacy_equivalence=legacy,
                  raw_commit=initial["raw_commit"], cpu_seconds=time.process_time() - start,
                  wall_seconds=time.perf_counter() - wall)
    with (OUT / "audit.json").open("x") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
    print(json.dumps({"status": "PASS", "checks": sum(CHECKS.values()),
                      "paired_age_rows": CHECKS["paired_age_rows"],
                      "regime_h_rows": CHECKS["paired_regime_rows"],
                      "legacy": legacy, "cpu_seconds": result["cpu_seconds"],
                      "wall_seconds": result["wall_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
