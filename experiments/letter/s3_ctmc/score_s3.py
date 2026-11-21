"""Doan Van Tai — locked S3 T1/T2/T3; raw-data-only, no CTMC evaluator.

D_hat follows S2 H-C: mean_tau(D_fresh + D_stale), NOT the actual policy
disagreement share. Regrets are paired before normalization, then three ages
are averaged within each regime. Student t uses regimes, never age cells.
INVALID stays in the fixed denominator. Unknown membership/outcomes cannot
certify region means and produce NOT_EVALUABLE, without zero imputation.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math

import numpy as np
from scipy.stats import t

from . import integrity as io

H_GRID = (.1, .2, .3, .5, .7, 1., 1.5, 2., 3., 5., 7., 10., 20., 30.)
AGES = (.3, 1., 3.)
CANDIDATES = ((1., .28), (.7, .32), (1.5, .21))


def ci(values):
    a = np.asarray(values, dtype=float)
    if not np.isfinite(a).all():
        raise ValueError("nonfinite paired outcomes")
    if len(a) < 2:
        return None, None
    half = float(t.ppf(.975, len(a)-1) * np.std(a, ddof=1) / math.sqrt(len(a)))
    return float(np.mean(a)-half), float(np.mean(a)+half)


def stats(rows, denominator):
    if len({r["regime"] for r in rows}) != len(rows):
        raise ValueError("CI requires one observation per regime")
    result = dict(n_regimes=len(rows), denominator_regimes=denominator,
                  share_regimes=len(rows)/denominator if denominator else None)
    for column in ("delta_pp", "delta_abs"):
        a = np.array([r[column] for r in rows], dtype=float)
        lo, hi = ci(a)
        result.update({column + "_" + k:v for k,v in dict(
            mean=float(a.mean()) if len(a) else None,
            median=float(np.median(a)) if len(a) else None,
            q10=float(np.quantile(a, .1)) if len(a) else None,
            q90=float(np.quantile(a, .9)) if len(a) else None,
            min=float(a.min()) if len(a) else None,
            max=float(a.max()) if len(a) else None,
            ci95_low=lo, ci95_high=hi).items()})
    for col in ("baseline_abs", "hybrid_abs", "baseline_pp", "hybrid_pp", "disagreement", "D"):
        result[col + "_mean"] = float(np.mean([r[col] for r in rows])) if rows else None
    result.update(n_delta_le_neg005=sum(r["delta_pp"] <= -.05 for r in rows),
                  n_delta_le_neg01=sum(r["delta_pp"] <= -.1 for r in rows),
                  n_delta_ge_01=sum(r["delta_pp"] >= .1 for r in rows))
    return result


def collapse_record(record, h_grid=H_GRID, ages=AGES):
    """Return paired age data and one row per regime/h/side/rate."""
    if record["status"] != "COMPLETED":
        return [], []
    rid = record["id"]
    policies, features = {}, {}
    for row in record["rows"]:
        if row["regime"] != rid:
            raise ValueError("policy regime mismatch")
        key = row["h_T_int"], row["tau_T_int"], row["rule"]
        if key in policies:
            raise ValueError("duplicate policy cell")
        policies[key] = row
    for row in record["features"]:
        if row["regime"] != rid:
            raise ValueError("feature regime mismatch")
        key = row["h_T_int"], row["tau_T_int"], row["side"], row["level"]
        if key in features:
            raise ValueError("duplicate feature cell")
        features[key] = row
    paired, collapsed = [], []
    for h in h_grid:
        for level in ("hat", "true"):
            invalid = level == "hat" and record["estimator"]["status"] == "INVALID_ESTIMATOR"
            if invalid:
                for age in ages:
                    for rule in ("Stationary_hat", "Hybrid_hat"):
                        if policies[(h, age, rule)]["status"] != "INVALID_ESTIMATOR":
                            raise ValueError("invalid estimator/policy status mismatch")
                continue
            for side, share in (("fresh", "p_new"), ("stale", "p_old")):
                group = []
                for age in ages:
                    base, hybrid = (policies[(h, age, rule + "_" + level)] for rule in ("Stationary", "Hybrid"))
                    feature = features[(h, age, side, level)]
                    if base["status"] != "COMPLETED" or hybrid["status"] != "COMPLETED":
                        raise ValueError("valid estimator has missing policy outcome")
                    cref = base["C_ref"]
                    if not math.isfinite(cref) or cref <= 0 or hybrid["C_ref"] != cref or feature["C_ref"] != cref:
                        raise ValueError("invalid paired C_ref")
                    baseline, corrected = base["regret_"+side], hybrid["regret_"+side]
                    absolute = baseline - corrected
                    if not math.isclose(absolute, base["L_"+side]-hybrid["L_"+side], abs_tol=2e-10, rel_tol=1e-9):
                        raise ValueError("regret/L cancellation mismatch")
                    d = feature["D_fresh"] + feature["D_stale"]
                    if not math.isclose(d, feature["D"], abs_tol=1e-12, rel_tol=1e-12):
                        raise ValueError("D differs from two-sided tail sum")
                    rate = base["s_hat"] if level == "hat" else base["s"]
                    disagreement = 1-hybrid[share] if rate < 0 else hybrid[share]
                    if not math.isclose(disagreement, feature["hybrid_static_disagreement"], abs_tol=1e-12):
                        raise ValueError("policy disagreement mismatch")
                    row = dict(regime=rid, h_T_int=h, tau_T_int=age, side=side, level=level,
                               C_ref=cref, D=d, disagreement=disagreement,
                               baseline_abs=baseline, hybrid_abs=corrected, delta_abs=absolute,
                               baseline_pp=100*baseline/cref, hybrid_pp=100*corrected/cref,
                               delta_pp=100*absolute/cref)
                    if not all(math.isfinite(v) for v in row.values() if isinstance(v, (float, int))):
                        raise ValueError("nonfinite scientific input")
                    group.append(row)
                if side == "fresh" and len({r["delta_pp"] for r in group}) != 1:
                    raise ValueError("fresh outcome depends on age")
                paired.extend(group)
                collapsed.append(dict(regime=rid, h_T_int=h, side=side, level=level,
                                      n_tau=len(ages), **{k:float(np.mean([r[k] for r in group])) for k in
                                      ("D", "disagreement", "C_ref", "baseline_abs", "hybrid_abs", "delta_abs",
                                       "baseline_pp", "hybrid_pp", "delta_pp")}))
    return paired, collapsed


def candidate(rows, denominator, h, threshold):
    inside = [r for r in rows if r["D"] >= threshold]
    outside = [r for r in rows if r["D"] < threshold]
    missing = denominator-len(rows)
    if missing < 0:
        raise ValueError("observations exceed fixed denominator")
    a, b = stats(inside, denominator), stats(outside, denominator)
    t1 = "PASS" if len(inside)/denominator >= .1 else "FAIL"
    t2 = "NOT_EVALUABLE" if len(inside) < 5 or missing else (
        "PASS" if a["delta_pp_mean"] >= .1 and a["delta_pp_ci95_low"] > 0 else "FAIL")
    t3 = "NOT_EVALUABLE" if len(outside) < 5 or missing else (
        "PASS" if b["delta_pp_ci95_low"] >= -.05 else "FAIL")
    verdicts = [t1, t2, t3]
    overall = "PASS" if all(v == "PASS" for v in verdicts) else (
        "FAIL" if "FAIL" in verdicts else "NOT_EVALUABLE")
    return dict(h_T_int=h, d_star=threshold, N=denominator, n_valid=len(rows),
                n_unknown=missing, n_region=len(inside), n_outside=len(outside),
                coverage=len(inside)/denominator, T1=t1, T2=t2, T3=t3, S3=overall,
                region=a, outside=b)


def score_records(records, denominator, h_grid=H_GRID, ages=AGES):
    if denominator < 1:
        raise ValueError("positive fixed denominator required")
    ids, groups, age_rows, collapsed = set(), defaultdict(list), [], []
    methods, statuses, invalid, fallback = Counter(), Counter(), 0, 0
    for record in records:
        if record["id"] in ids:
            raise ValueError("duplicate raw regime")
        ids.add(record["id"])
        statuses[record["status"]] += 1
        estimator = record.get("estimator", {})
        invalid += estimator.get("status") == "INVALID_ESTIMATOR"
        fallback += bool(estimator.get("fallback"))
        if estimator:
            methods[estimator.get("method") or "INVALID_ESTIMATOR"] += 1
        a, c = collapse_record(record, h_grid, ages)
        age_rows.extend(a)
        collapsed.extend(c)
        for row in c:
            groups[(row["h_T_int"], row["side"], row["level"])].append(row)
    if len(ids) > denominator:
        raise ValueError("too many raw regimes")
    candidates = [candidate(groups[(h, "fresh", "hat")], denominator, h, threshold)
                  for h, threshold in CANDIDATES if h in h_grid]
    by_h = [dict(h_T_int=h, side=side, level=level, **stats(groups[(h, side, level)], denominator))
            for h in h_grid for side in ("fresh", "stale") for level in ("hat", "true")]
    stale = [dict(side="stale", **candidate(groups[(h, "stale", "hat")], denominator, h, threshold))
             for h, threshold in CANDIDATES if h in h_grid]
    return dict(owner="Doan Van Tai", namespace=io.NAMESPACE, N=denominator,
                measured_regimes=len(ids), missing_raw_regimes=denominator-len(ids),
                statuses=dict(statuses), invalid_estimators=invalid, fallback_regimes=fallback,
                estimator_methods=dict(methods), primary=candidates[0],
                secondary=candidates[1:], stale_candidates=stale, by_h=by_h,
                units=dict(delta_pp="percentage points of paired C_ref", delta_abs="packet*s"),
                D_definition="mean over tau/T_int {0.3,1,3} of D_fresh_hat + D_stale_hat; two-sided tail bound, not actual disagreement",
                CI="two-sided 95% Student t; one age-averaged observation per regime; descriptive finite Sobol panel, no population guarantee",
                invalid_handling="retained in N; unknown region/outcomes unclassified, no zero imputation; affected mean tests NOT_EVALUABLE"), age_rows, collapsed


def s3_records(lock_sha):
    """Validated raw receipts, never pilot files. Streaming avoids GB retention."""
    cfg = io.read(io.OUT / "sample/config.json")
    sample = io.read(io.OUT / "sample/sample.json")
    expected = {r["id"]:r for r in sample["selected"]}
    seen = set()
    for shard in ("0_of_2", "1_of_2"):
        directory = io.OUT / "runs" / ("shard_" + shard)
        receipt = io.read(directory / "receipt.json")
        if receipt["lock_sha256"] != lock_sha or receipt["seed_record"] != cfg["seeds"]["run_record"]:
            raise ValueError("receipt lock/seed mismatch")
        if set(receipt["ids"]) != {r["id"] for r in receipt["measured"]}:
            raise ValueError("receipt did not finish the planned IDs")
        for measured in receipt["measured"]:
            rid = measured["id"]
            if rid in seen or rid not in expected:
                raise ValueError("raw ID duplicate/outside frozen sample")
            seen.add(rid)
            path = directory / "raw" / (rid + ".json")
            if io.sha(path) != measured["sha256"]:
                raise ValueError("raw hash mismatch")
            record = io.read(path)
            if (record["id"] != rid or record["namespace"] != io.NAMESPACE
                    or record["kind"] != "CONFIRMATORY" or record["purpose"] != "run"
                    or record["regime"] != expected[rid]["regime"]):
                raise ValueError("raw is not the frozen S3 truth record")
            if record["status"] == "COMPLETED":
                coordinate = [cfg["seeds"]["run_record"], int(rid.rsplit("_", 1)[1])]
                if record["estimator"]["seed_coordinate"] != coordinate:
                    raise ValueError("wrong raw arrival-record seed")
            yield record
    if seen != set(expected):
        raise ValueError("missing frozen S3 sample IDs; no partial scientific verdict")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-lock-sha", required=True)
    args = parser.parse_args(argv)
    verified = io.verify_lock(expected_sha=args.expected_lock_sha)
    destination = io.OUT / "score"
    if destination.exists():
        raise FileExistsError(destination)
    summary, age, paired = score_records(s3_records(verified["lock_sha256"]), denominator=600)
    summary["lock_sha256"] = verified["lock_sha256"]
    destination.mkdir(exist_ok=False)
    io.write(destination / "summary.json", summary)
    if age:
        io.csv_write(destination / "paired_by_age.csv", age)
        io.csv_write(destination / "paired_regime_h.csv", paired)
    io.csv_write(destination / "by_h.csv", summary["by_h"])
    print(json.dumps(summary["primary"], ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
