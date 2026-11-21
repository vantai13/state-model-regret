"""Doan Van Tai — independent saved-data S1-A audit; standard library only.

Usage: python3 -B results/letter/sweep/ctmc/rescore_audit.py
Exclusive-create verification.json. Does not import a CTMC evaluator/scorer.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
CURRENT = OUT / "v2"


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def main():
    initial = read(OUT / "initial_existing_inputs.json")
    sample = read(CURRENT / "sample.json")
    pilot = read(CURRENT / "pilot.json")
    summary = read(CURRENT / "pilot_summary/summary.json")
    checks, max_error = Counter(), defaultdict(float)

    def close(a, b, name):
        error = abs(a-b)
        max_error[name] = max(max_error[name], error)
        assert error <= 1e-9 * max(1., abs(a), abs(b)), (name, a, b, error)
        checks[name] += 1

    fields = ("regime", "T_int", "truncation", "estimator", "regime_features", "rows", "features")
    comparisons, features, ids = [], [], []
    for measured in pilot["measured"]:
        rid = measured["id"]
        path = CURRENT / "pilot" / (rid+".json")
        record, old = read(path), read(OUT / "pilot" / (rid+".json"))
        ids.append(rid)
        assert sha(path) == measured["sha256"]
        assert record["status"] == "COMPLETED"
        left, right = ({k:row[k] for k in fields} for row in (old, record))
        assert left == right, ("scientific_data_changed", rid)
        comparisons.append(dict(id=rid, identical=True, scientific_sha256=digest(right)))
        assert len(record["rows"]) == 16 and len(record["features"]) == 8
        assert record["h_T_int"] == [.1, 1.] and record["tau_T_int"] == [.3]
        for est in record["estimator"]["telemetry"].values():
            close(est["W"], 300*record["T_int"], "record_length")
        cells = defaultdict(dict)
        for row in record["rows"]:
            assert row["status"] == "COMPLETED"
            cells[(row["h_T_int"], row["tau_T_int"])][row["rule"]] = row
            close(row["G_S"], row["L_stale"]-row["L_fresh"], "G_S_identity")
            for side in ("fresh", "stale"):
                close(row["regret_"+side], row["L_"+side]-row["C_ref"], "regret_identity")
                close(row["regret_"+side+"_pct_C_ref"],
                      100*row["regret_"+side]/row["C_ref"], "regret_normalization")
                assert row["regret_"+side] >= -1e-9 * max(1., row["C_ref"])
            if row["rule"].startswith("Stationary_") or row["rule"] == "Oracle":
                assert row["G_S"] == 0.
            if row["rule"] == "Oracle":
                close(row["L_fresh"], row["C_ref"], "oracle_identity")
        for row in record["features"]:
            features.append(row)
            cell = cells[(row["h_T_int"], row["tau_T_int"])]
            level, side = row["level"], row["side"]
            rate = row["s"] if level == "true" else row["s_hat"]
            share = "p_new" if side == "fresh" else "p_old"
            hybrid, static = cell["Hybrid_"+level], cell["Stationary_"+level]
            close(row["benefit_static_minus_hybrid"],
                  static["regret_"+side]-hybrid["regret_"+side], "benefit_identity")
            close(row["benefit_pp_C_ref"], static["regret_"+side+"_pct_C_ref"] -
                  hybrid["regret_"+side+"_pct_C_ref"], "benefit_normalization")
            disagree = 1-hybrid[share] if rate < 0 else hybrid[share]
            close(row["hybrid_static_disagreement"], disagree, "disagreement_identity")
            close(row["D"], row["D_fresh"]+row["D_stale"], "D_identity")
            close(row["D_threshold"], row["h"]*abs(rate), "D_threshold")
            assert -1e-9 <= disagree <= row["D_"+side]+1e-9
            assert all(-1e-9 <= row["D_"+s] <= 1+1e-9 for s in ("fresh", "stale"))
            qs = [row["abs_fluid_gap_"+q] for q in ("q10", "q50", "q90", "q99")]
            assert 0 <= qs[0] <= qs[1] <= qs[2] <= qs[3]
    assert len(set(ids)) == 10 and len(features) == 80
    groups = defaultdict(list)
    for row in features:
        groups[(row["h_T_int"], row["side"], row["level"])].append(row)
    for row in summary["by_h"]:
        group = groups[(row["h_T_int"], row["side"], row["level"])]
        for label, key in (("baseline", "static_regret_pct_C_ref"), ("hybrid", "hybrid_regret_pct_C_ref")):
            close(row[label+"_mean_regret_pct_C_ref"],
                  statistics.mean(r[key] for r in group), "summary_"+label)
        values = [r["benefit_pp_C_ref"] for r in group]
        close(row["benefit_pp_C_ref_mean"], statistics.mean(values), "summary_benefit")
        deciles = statistics.quantiles(values, n=10, method="inclusive")
        close(row["benefit_pp_C_ref_q10"], deciles[0], "summary_q10")
        close(row["benefit_pp_C_ref_q90"], deciles[-1], "summary_q90")
        close(row["disagreement_mean"], statistics.mean(r["hybrid_static_disagreement"]
                                                       for r in group), "summary_disagreement")
    projection = pilot["projection"]
    metadata = {r["id"]:r for r in sample["candidates"]}
    total, shards = 0., defaultdict(lambda:dict(regimes=0, cpu_seconds=0.))
    for record in pilot["measured"]:
        for k, observed in record["timing"].items():
            predicted = projection["coefficients"][k]*record["work"][k] + projection["pilot_intercepts_seconds"][k]
            assert predicted+1e-10 >= observed
            checks["affine_pilot_envelope"] += 1
    for row in projection["rows"]:
        if row["status"] != "ELIGIBLE":
            continue
        meta = metadata[row["id"]]
        cost = projection["safety_factor"] * sum(
            projection["coefficients"][k]*meta["work"][k] + projection["pilot_intercepts_seconds"][k] *
            projection["full_grid_intercept_factors"][k] for k in projection["coefficients"])
        observed = next((v["cpu_seconds"] for v in pilot["measured"] if v["id"] == row["id"]), 0.)
        close(row["projected_cpu_seconds"], max(cost, observed), "cost_projection")
        total += row["projected_cpu_seconds"]
        tag = str((int(row["id"].split("_")[-1])-1) % 2)+"/2"
        shards[tag]["regimes"] += 1
        shards[tag]["cpu_seconds"] += row["projected_cpu_seconds"]
    close(projection["projected_cpu_hours"], total/3600., "total_projection")
    for row in shards.values():
        row.update(cpu_hours=row["cpu_seconds"]/3600,
                   wall_hours_15=row["cpu_seconds"]/3600/15,
                   wall_hours_15_90pct=row["cpu_seconds"]/3600/15/.9)
    changed = [name for name, value in initial["sha256"].items()
               if not (ROOT/name).is_file() or sha(ROOT/name) != value]
    assert not changed, changed
    head_now = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
    assert not list(CURRENT.glob("runs/**/raw/*.json"))
    assert pilot["source_sha256"] == sha(ROOT/"experiments/letter/sweep_ctmc.py")
    invalid = subprocess.run(["bash", "experiments/letter/sweep_ctmc_gcp.sh", "invalid"],
                             cwd=ROOT, capture_output=True, text=True)
    assert invalid.returncode == 2
    legacy = [read(p) for p in sorted((OUT/"pytest_final").glob("test_matches_saved*/equivalence.json"))
              if not p.parent.is_symlink()]
    assert len(legacy) == 2
    result = dict(owner="Doan Van Tai", status="PASS", kind="EXPLORATORY_TECHNICAL_VERIFICATION",
                  created_utc=datetime.now(timezone.utc).isoformat(), checks=dict(checks),
                  max_absolute_error=dict(max_error), scientific_pilot1_vs_v2=comparisons,
                  legacy_equivalence=legacy, existing_tracked_files_checked=len(initial["sha256"]),
                  existing_tracked_files_changed=changed, initial_head=initial["head"], current_head=head_now,
                  head_unchanged=head_now == initial["head"],
                  concurrent_head_note="HEAD can advance in concurrent jobs. This task ran no commit; source/input hashes are checked directly.",
                  new_full_run_rows=0, raw_pilot_rows=160, feature_rows=80, shards=dict(shards),
                  source_sha256={name:sha(ROOT/name) for name in ("experiments/letter/sweep_ctmc.py",
                      "tests/test_sweep_ctmc.py", "experiments/letter/sweep_ctmc_gcp.sh")},
                  shell_invalid_shard_rc=invalid.returncode, all_pilot_raw_checksums_verified=True,
                  independent_rescore="standard library only; no import of sweep or CTMC scorer")
    with (OUT/"verification.json").open("x") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
    print(json.dumps(dict(status="PASS", checks=sum(checks.values()),
                         scientific_identical_regimes=len(comparisons),
                         tracked_unchanged=len(initial["sha256"]),
                         head_unchanged=result["head_unchanged"], shards=dict(shards), legacy=legacy), indent=2))


if __name__ == "__main__":
    main()
