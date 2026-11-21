"""Doan Van Tai — independent S3 rescore, no scorer/analyzer imports.

Uses policy raw rows (including their D tails), not the scorer's feature
join. Uses standard-library arithmetic/statistics plus Student t quantiles.
Only integrity verification and exclusive file I/O are shared.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import statistics

from scipy.stats import t as student

from . import integrity as io

HORIZONS = (.1, .2, .3, .5, .7, 1., 1.5, 2., 3., 5., 7., 10., 20., 30.)
TAUS = (.3, 1., 3.)


def interval(numbers):
    if len(numbers) < 2:
        return None, None
    center = statistics.fmean(numbers)
    width = float(student.ppf(.975, len(numbers)-1)) * statistics.stdev(numbers) / math.sqrt(len(numbers))
    return center-width, center+width


def describe(rows, total):
    n = len(rows)
    if len({r["regime"] for r in rows}) != n:
        raise ValueError("independent CI has repeated regimes")
    result = dict(n_regimes=n, denominator_regimes=total, share_regimes=n/total)
    for field in ("delta_pp", "delta_abs"):
        values = sorted(r[field] for r in rows)
        def percentile(q):
            if not values:
                return None
            at = (len(values)-1)*q
            lo, hi = math.floor(at), math.ceil(at)
            return values[lo] + (values[hi]-values[lo])*(at-lo)
        left, right = interval(values)
        result.update({field+"_"+k:v for k,v in dict(
            mean=statistics.fmean(values) if n else None,
            median=statistics.median(values) if n else None,
            q10=percentile(.1), q90=percentile(.9), min=min(values) if n else None,
            max=max(values) if n else None, ci95_low=left, ci95_high=right).items()})
    for name in ("baseline_abs", "hybrid_abs", "baseline_pp", "hybrid_pp", "disagreement", "D"):
        result[name+"_mean"] = statistics.fmean(r[name] for r in rows) if n else None
    result["n_delta_le_neg005"] = sum(r["delta_pp"] <= -.05 for r in rows)
    result["n_delta_le_neg01"] = sum(r["delta_pp"] <= -.1 for r in rows)
    result["n_delta_ge_01"] = sum(r["delta_pp"] >= .1 for r in rows)
    return result


def independent_candidate(rows, total, horizon, cutoff):
    accepted, rejected = [], []
    for r in rows:
        (accepted if r["D"] >= cutoff else rejected).append(r)
    ins, outs = describe(accepted, total), describe(rejected, total)
    unknown = total-len(rows)
    if unknown < 0:
        raise ValueError("independent observations exceed N")
    coverage = len(accepted)/total
    tests = ["PASS" if coverage >= .1 else "FAIL"]
    if len(accepted) < 5 or unknown:
        tests.append("NOT_EVALUABLE")
    else:
        tests.append("PASS" if ins["delta_pp_mean"] >= .1 and ins["delta_pp_ci95_low"] > 0 else "FAIL")
    if len(rejected) < 5 or unknown:
        tests.append("NOT_EVALUABLE")
    else:
        tests.append("PASS" if outs["delta_pp_ci95_low"] >= -.05 else "FAIL")
    verdict = "PASS" if tests == ["PASS"]*3 else "FAIL" if "FAIL" in tests else "NOT_EVALUABLE"
    return dict(h_T_int=horizon, d_star=cutoff, N=total, n_valid=len(rows), n_unknown=unknown,
                n_region=len(accepted), n_outside=len(rejected), coverage=coverage,
                T1=tests[0], T2=tests[1], T3=tests[2], S3=verdict, region=ins, outside=outs)


def independent_score(records, total, horizons=HORIZONS, taus=TAUS):
    by_group = {(h, side, rate):[] for h in horizons for side in ("fresh", "stale") for rate in ("hat", "true")}
    ids, statuses, methods, invalid, fallback = set(), Counter(), Counter(), 0, 0
    for record in records:
        rid = record["id"]
        if rid in ids:
            raise ValueError("duplicate independent raw ID")
        ids.add(rid)
        statuses[record["status"]] += 1
        estimator = record.get("estimator", {})
        invalid += estimator.get("status") == "INVALID_ESTIMATOR"
        fallback += bool(estimator.get("fallback"))
        if estimator:
            methods[estimator.get("method") or "INVALID_ESTIMATOR"] += 1
        if record["status"] != "COMPLETED":
            continue
        lookup = {}
        for p in record["rows"]:
            key = (p["h_T_int"], p["tau_T_int"], p["rule"])
            if key in lookup or p["regime"] != rid:
                raise ValueError("duplicate/wrong independent policy cell")
            lookup[key] = p
        for h in horizons:
            for rate in ("hat", "true"):
                if rate == "hat" and estimator["status"] == "INVALID_ESTIMATOR":
                    continue
                for side in ("fresh", "stale"):
                    ages = []
                    for tau in taus:
                        static = lookup[(h, tau, "Stationary_"+rate)]
                        hybrid = lookup[(h, tau, "Hybrid_"+rate)]
                        if static["status"] != "COMPLETED" or hybrid["status"] != "COMPLETED":
                            raise ValueError("independent unpaired policy")
                        reference = static["C_ref"]
                        if reference <= 0 or reference != hybrid["C_ref"]:
                            raise ValueError("independent paired reference invalid")
                        before, after = static["regret_"+side], hybrid["regret_"+side]
                        difference = before-after
                        s = static["s_hat"] if rate == "hat" else static["s"]
                        switched = hybrid["p_new" if side == "fresh" else "p_old"]
                        age = dict(D=hybrid["D_fresh"]+hybrid["D_stale"],
                                   disagreement=1-switched if s < 0 else switched,
                                   baseline_abs=before, hybrid_abs=after, delta_abs=difference,
                                   baseline_pp=100*before/reference, hybrid_pp=100*after/reference,
                                   delta_pp=100*difference/reference)
                        if not all(math.isfinite(v) for v in age.values()):
                            raise ValueError("independent nonfinite data")
                        ages.append(age)
                    result = {name:statistics.fmean(row[name] for row in ages) for name in ages[0]}
                    result["regime"] = rid
                    by_group[(h, side, rate)].append(result)
    if len(ids) > total:
        raise ValueError("independent raw IDs exceed fixed N")
    candidates = [independent_candidate(by_group[(h, "fresh", "hat")], total, h, cutoff)
                  for h, cutoff in ((1., .28), (.7, .32), (1.5, .21)) if h in horizons]
    return dict(N=total, measured_regimes=len(ids), missing_raw_regimes=total-len(ids),
                statuses=dict(statuses), invalid_estimators=invalid, fallback_regimes=fallback,
                estimator_methods=dict(methods), primary=candidates[0], secondary=candidates[1:],
                stale_candidates=[dict(side="stale", **independent_candidate(by_group[(h, "stale", "hat")], total, h, cutoff))
                                  for h, cutoff in ((1., .28), (.7, .32), (1.5, .21)) if h in horizons],
                by_h=[dict(h_T_int=h, side=side, level=rate, **describe(by_group[(h, side, rate)], total))
                      for h in horizons for side in ("fresh", "stale") for rate in ("hat", "true")])


def compare(expected, observed, path="root"):
    """Compare every independently recomputed count, mean, CI and verdict."""
    if isinstance(observed, dict):
        checks = 0
        for key, value in observed.items():
            if key not in expected:
                raise AssertionError(path+" missing "+key)
            checks += compare(expected[key], value, path+"."+key)
        return checks
    if isinstance(observed, list):
        if len(expected) != len(observed):
            raise AssertionError(path+" list length mismatch")
        return sum(compare(a, b, path+f"[{i}]") for i,(a,b) in enumerate(zip(expected, observed)))
    if isinstance(observed, float):
        if not math.isclose(expected, observed, rel_tol=5e-12, abs_tol=1e-10):
            raise AssertionError(f"{path}: {expected} != {observed}")
    elif expected != observed:
        raise AssertionError(f"{path}: {expected} != {observed}")
    return 1


def independent_inputs(lock_sha):
    cfg = io.read(io.OUT / "sample/config.json")
    planned = {m["id"]:m["regime"] for m in io.read(io.OUT / "sample/sample.json")["selected"]}
    found = set()
    for number in (0, 1):
        directory = io.OUT / "runs" / f"shard_{number}_of_2"
        receipt = io.read(directory / "receipt.json")
        if receipt["lock_sha256"] != lock_sha or set(receipt["ids"]) != {m["id"] for m in receipt["measured"]}:
            raise ValueError("independent receipt mismatch")
        for m in receipt["measured"]:
            rid = m["id"]
            if rid not in planned or rid in found:
                raise ValueError("independent unexpected/duplicate raw")
            found.add(rid)
            path = directory / "raw" / (rid+".json")
            if io.sha(path) != m["sha256"]:
                raise ValueError("independent raw digest failure")
            r = io.read(path)
            if (r["id"] != rid or r["namespace"] != io.NAMESPACE or r["purpose"] != "run"
                    or r["kind"] != "CONFIRMATORY" or r["regime"] != planned[rid]):
                raise ValueError("independent raw is not S3")
            if r["status"] == "COMPLETED" and r["estimator"]["seed_coordinate"] != [cfg["seeds"]["run_record"], int(rid.split("_")[-1])]:
                raise ValueError("independent raw record seed mismatch")
            yield r
    if found != set(planned):
        raise ValueError("independent incomplete panel")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-lock-sha", required=True)
    args = parser.parse_args(argv)
    verification = io.verify_lock(expected_sha=args.expected_lock_sha)
    original = io.read(io.OUT / "score/summary.json")
    if original["lock_sha256"] != verification["lock_sha256"]:
        raise ValueError("scored a different lock")
    independent = independent_score(independent_inputs(verification["lock_sha256"]), total=600)
    checks = compare(original, independent)
    io.write(io.OUT / "score/independent_rescore.json", dict(status="PASS", checks=checks,
             lock_sha256=verification["lock_sha256"], independent_results=independent,
             independence="no imports from score_s3 or analyze_s2; raw policy D tails, standard-library arithmetic"))
    print(json.dumps(dict(status="PASS", checks=checks)))


if __name__ == "__main__":
    main()
