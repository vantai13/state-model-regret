"""Doan Van Tai — S3 sample/pilot/lock; run-shard is Claude/GCP-only handoff.

Old S1-A source files are never edited. The wrapper temporarily supplies new
seeds to the unchanged Sobol sampler and finite-record estimator. Resource
eligibility uses the unchanged initial screen AND the frozen S1-A pilot cost
screen, before outcomes. The independent pilot cannot alter eligibility.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
import datetime
import json
import math
import multiprocessing
import os
from pathlib import Path
import re
import time

from . import integrity as io

SEEDS = dict(sample=630951401, run_record=630951402,
             pilot_sample=630951403, pilot_record=630951404)
N = 600
S1 = io.ROOT / "results/letter/sweep/ctmc/v2"
OLD_RUNNER = io.ROOT / "experiments/letter/sweep_ctmc.py"
BRIEF = Path("/home/vantai/state-model-regret-papers/letter_smr/briefs/sweep/BRIEF_S3_CTMC.md")


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def legacy():
    from experiments.letter import sweep_ctmc
    return sweep_ctmc


@contextmanager
def supplied_seeds(s, sample_seed=None):
    original = s.SEEDS
    s.SEEDS = dict(original, sample=SEEDS["sample"] if sample_seed is None else sample_seed,
                   pilot_record=SEEDS["pilot_record"], run_record=SEEDS["run_record"])
    try:
        yield
    finally:
        s.SEEDS = original


def old_sources():
    s = legacy()
    names = ["experiments/letter/sweep_ctmc.py", "experiments/letter/sweep_ctmc_gcp.sh",
             *s.DEPENDENCIES, "tests/test_sweep_ctmc.py",
             "results/letter/sweep/ctmc/s2/analyze_s2.py",
             "results/letter/sweep/ctmc/report.md",
             "results/letter/sweep/ctmc/s2/S3_CANDIDATES.md",
             "results/letter/sweep/ctmc/v2/sample.json",
             "results/letter/sweep/ctmc/v2/pilot.json"]
    names.extend(str(p.relative_to(io.ROOT)) for p in sorted((S1 / "runs").glob("shard_*/receipt.json")))
    return {name: io.sha(io.ROOT / name) for name in names}


def audit_seeds():
    """Search every pre-existing repo text file for the proposed seed values.

    Ignore Git objects, environments, caches and the new S3 scope. Symlinks
    are not followed. Only seed collisions and aggregate sizes are exposed;
    no scientific outcome is used for selection.
    """
    if len(set(SEEDS.values())) != len(SEEDS):
        raise ValueError("new seeds overlap")
    pattern = re.compile(rb"(?<![0-9])(?:" + b"|".join(str(v).encode() for v in SEEDS.values()) + rb")(?![0-9])")
    suffixes = {".py", ".sh", ".json", ".jsonl", ".csv", ".md", ".txt", ".yaml", ".yml", ".toml"}
    skip = {".git", ".venv", "venv", "__pycache__", ".cache", ".pytest_cache", "node_modules"}
    collisions, count, size = [], 0, 0
    for directory, dirs, files in os.walk(io.ROOT, followlinks=False):
        base = Path(directory)
        dirs[:] = sorted(d for d in dirs if d not in skip and not (base / d).is_symlink()
                         and (base / d) not in (io.CODE, io.OUT))
        for name in sorted(files):
            path = base / name
            if path.suffix not in suffixes or path.is_symlink():
                continue
            count += 1
            overlap = b""
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    size += len(block)
                    if pattern.search(overlap + block):
                        collisions.append(str(path.relative_to(io.ROOT)))
                    overlap = block[-32:]
    # Also check every recorded seed coordinate in S1-A and its timing pilots.
    old_seeds = set(legacy().SEEDS.values())
    for path in [S1 / "pilot.json", *sorted((S1 / "runs").glob("shard_*/receipt.json"))]:
        d = io.read(path)
        old_seeds.add(d["seed_record"])
    if collisions or set(SEEDS.values()) & old_seeds:
        raise ValueError("new seed already appears in pre-existing files: " + str(collisions))
    result = dict(owner="Doan Van Tai", seeds=SEEDS, pairwise_distinct=True,
                  preexisting_literal_collisions=[], old_S1A_seeds=sorted(old_seeds),
                  preexisting_text_files_scanned=count, bytes_scanned=size,
                  scope="all regular repository text files; new S3 scope, Git objects, environments and cache directories excluded; no symlink traversal",
                  limitation="checks recorded literals plus S1-A seed metadata; does not prove noncollision with arbitrary undocumented computed seeds",
                  created_utc=stamp())
    io.write(io.OUT / "sample/seeds.json", result)
    return result


def generate(count, seed, prefix):
    s = legacy()
    with supplied_seeds(s, seed):
        original = s.sobol_regimes(count)
    return [s.x.Regime(f"{prefix}_{i:04d}", r.A, r.B, r.u, r.stratum)
            for i, r in enumerate(original, 1)]


def projected_cost(meta, calibration):
    return calibration["safety_factor"] * sum(
        calibration["coefficients"][k] * meta["work"][k]
        + calibration["pilot_intercepts_seconds"][k] * calibration["full_grid_intercept_factors"][k]
        for k in calibration["coefficients"])


def screened(regime, calibration):
    s = legacy()
    row = s.screen_regime(regime, s.CPU_CAP)
    row["initial_screen_status"] = row["status"]
    row["projected_cpu_seconds"] = None
    if row["status"] == "ELIGIBLE":
        cost = projected_cost(row, calibration)
        row["projected_cpu_seconds"] = cost
        if cost > s.CPU_CAP:
            row.update(status="REJECTED", reason="S1A_PILOT_PROJECTED_CPU_CAP")
    return row


def config():
    s = legacy()
    return dict(namespace=io.NAMESPACE, owner="Doan Van Tai", kind="CONFIRMATORY_PREPARATION",
                N=N, seeds=SEEDS, c=0., h_T_int=list(s.H_GRID), tau_T_int=list(s.AGES),
                rules=list(s.RULES), record_T_int=s.RECORD_T_INT,
                cpu_cap_seconds=s.CPU_CAP, max_N=s.MAX_N,
                max_pair_states=s.MAX_PAIR_STATES, max_count_bins=s.MAX_COUNT_BINS,
                selection="first 600 eligible in new scrambled Sobol order; unchanged S1-A initial + frozen pilot resource screens; no outcome inputs",
                primary=dict(h_T_int=1., side="fresh", level="hat", d_star=.28),
                secondary=[dict(h_T_int=.7, d_star=.32), dict(h_T_int=1.5, d_star=.21)],
                test_thresholds=dict(T1_coverage=.1, T2_delta_pp=.1, T3_lower_ci_pp=-.05,
                                     minimum_region_regimes=5, confidence=.95),
                missing_data="INVALID remains in N; no imputation; unknown D/missing paired outcomes make corresponding mean tests NOT_EVALUABLE",
                gcp=dict(machine="n2-highcpu-32", shards=2, workers_per_shard=15,
                         shard_wall_cap_seconds=21600, retry=False, resume=False,
                         poweroff="Claude driver only"),
                initial_coefficients=s.INITIAL_COEFFICIENTS,
                S1A_projection=io.read(S1 / "pilot.json")["projection"],
                old_input_sha256=old_sources(), card_sha256=io.sha(io.CARD),
                brief_sha256=io.sha(BRIEF), created_utc=stamp(), environment=s.x.environment())


def sample():
    s = legacy()
    s.x.require_environment()
    if (io.OUT / "lock.json").exists():
        raise FileExistsError("S3 is already locked")
    start, wall = time.process_time(), time.perf_counter()
    audit_seeds()
    cfg = config()
    io.write(io.OUT / "sample/config.json", cfg)
    # Sobol powers of two have identical prefixes. A larger net is only used
    # if 1024 candidates cannot supply the fixed first N eligible regimes.
    count, index, rows, selected = 1024, 0, [], []
    while len(selected) < N:
        candidates = generate(count, SEEDS["sample"], "S3")
        while index < count and len(selected) < N:
            row = screened(candidates[index], cfg["S1A_projection"])
            row["sobol_index_zero_based"] = index
            rows.append(row)
            index += 1
            if row["status"] == "ELIGIBLE":
                selected.append(row)
        count *= 2
    io.write(io.OUT / "sample/sample.json", dict(
        namespace=io.NAMESPACE, selected=selected, screened=rows,
        selected_count=len(selected), screened_count=len(rows),
        rejected_by_reason=dict(Counter(r["reason"] for r in rows if r["reason"])),
        finite_h_truth_computed=False, cpu_seconds=time.process_time()-start,
        wall_seconds=time.perf_counter()-wall))
    io.csv_write(io.OUT / "sample/sample.csv", [dict(
        id=r["id"], sobol_index_zero_based=r["sobol_index_zero_based"], status=r["status"],
        reason=r["reason"], projected_cpu_seconds=r["projected_cpu_seconds"],
        initial_projected_cpu_seconds=r.get("initial_projected_cpu_seconds"),
        T_int=r.get("T_int"), state_pair=r.get("state_pair")) for r in rows])
    projection = make_projection(selected)
    io.write(io.OUT / "sample/projection.json", projection)
    print(json.dumps(dict(N=len(selected), screened=len(rows), projection=projection), allow_nan=False))


def make_projection(selected):
    """Both frozen S1-A pilot envelope and actual GCP receipt timings."""
    import numpy as np
    from scipy.optimize import nnls
    receipts = sorted((S1 / "runs").glob("shard_*/receipt.json"))
    old = [m for p in receipts for m in io.read(p)["measured"]]
    if len(old) != 1000 or any(m["status"] != "COMPLETED" for m in old):
        raise ValueError("expected all 1000 S1-A receipt timings")
    components, fitted = tuple(legacy().INITIAL_COEFFICIENTS), {}
    for k in components:
        work = np.array([m["work"][k] for m in old])
        timing = np.array([m["timing"][k] for m in old])
        scale = max(float(work.max()), 1.)
        fit = nnls(np.column_stack([np.ones(len(old)), work / scale]), timing)[0]
        fitted[k] = dict(intercept=float(fit[0]), slope=float(fit[1] / scale))
    def predict(r):
        return sum(v["intercept"] + v["slope"] * r["work"][k] for k, v in fitted.items())
    estimates = [dict(id=r["id"], s1a_pilot_envelope_cpu_seconds=r["projected_cpu_seconds"],
                      s1a_gcp_receipt_fit_cpu_seconds=predict(r)) for r in selected]
    tables = {}
    for field in ("s1a_pilot_envelope_cpu_seconds", "s1a_gcp_receipt_fit_cpu_seconds"):
        hours = sum(r[field] for r in estimates) / 3600
        shards = [sum(r[field] for r in estimates if (int(r["id"].split("_")[-1])-1) % 2 == j) / 3600
                  for j in range(2)]
        tables[field] = dict(cpu_hours=hours, ideal_wall_hours_30_workers=hours / 30,
                             ideal_shard_makespan_hours=max(shards) / 15,
                             shard_makespan_hours_at_90pct=max(shards) / (15 * .9),
                             shard_cpu_hours=shards)
    return dict(method="nonnegative affine per-component fit to actual 1000 S1-A GCP receipt work/timings; frozen S1-A pilot envelope separately",
                coefficients=fitted, source_receipts={str(p.relative_to(io.ROOT)):io.sha(p) for p in receipts},
                S1A_measured_cpu_hours=sum(r["cpu_seconds"] for r in old)/3600,
                estimates=tables, per_regime=estimates,
                caveat="parameter/work-based extrapolation, not a guarantee or confidence interval; new pilot never changes sample, model or screen")


def load_sample():
    cfg = io.read(io.OUT / "sample/config.json")
    report = io.read(io.OUT / "sample/sample.json")
    if cfg["old_input_sha256"] != old_sources() or cfg["card_sha256"] != io.sha(io.CARD):
        raise ValueError("sample source/card changed")
    if cfg["seeds"] != SEEDS or report["selected_count"] != N:
        raise ValueError("wrong S3 sample/seeds")
    selected = [r for r in report["screened"] if r["status"] == "ELIGIBLE"][:N]
    if report["selected"] != selected or len({r["id"] for r in selected}) != N:
        raise ValueError("sample is not first N eligible")
    return cfg, report


def pilot():
    """At most three new pilot-seed regimes; only timings enter the receipt."""
    s = legacy()
    s.x.require_environment()
    cfg, report = load_sample()
    pool = [screened(r, cfg["S1A_projection"]) for r in generate(64, SEEDS["pilot_sample"], "S3P")]
    chosen = sorted((r for r in pool if r["status"] == "ELIGIBLE"),
                    key=lambda r: (-r["projected_cpu_seconds"], r["id"]))[:3]
    def physical(r):
        return {k:v for k,v in r["regime"].items() if k not in ("id", "stratum")}
    if len(chosen) != 3 or any(physical(p) == physical(r) for p in chosen for r in report["selected"]):
        raise ValueError("pilot must have three eligible physical regimes outside S3")
    io.write(io.OUT / "pilot/plan.json", dict(
        purpose="RESOURCE_ONLY_NOT_S3", seeds={k:SEEDS[k] for k in ("pilot_sample", "pilot_record")},
        candidate_count=64, selection="three largest frozen S1-A projected CPU costs among eligible pilot-seed candidates",
        candidates=pool, selected=chosen, h_T_int=list(s.PILOT_H), tau_T_int=list(s.PILOT_AGES),
        source_sha256=source_hashes(), created_utc=stamp(), outcome_use="none; timings only; cannot change eligibility"))
    start = time.perf_counter()
    measured = [evaluate_one((r, "pilot", str(io.OUT / "pilot/raw"), s.CPU_CAP)) for r in chosen]
    io.write(io.OUT / "pilot/receipt.json", dict(
        purpose="RESOURCE_ONLY_NOT_S3", measured=measured,
        statuses=dict(Counter(r["status"] for r in measured)),
        cpu_seconds=sum(r["cpu_seconds"] for r in measured), wall_seconds=time.perf_counter()-start,
        outcome_use="not scored; not included in sample or S3 score", S3_truth_status="NOT_RUN"))
    print(json.dumps(dict(pilot_statuses=dict(Counter(r["status"] for r in measured)),
                          cpu_seconds=sum(r["cpu_seconds"] for r in measured))))


def source_hashes():
    return {str(p.relative_to(io.ROOT)):io.sha(p) for p in sorted(io.CODE.rglob("*"))
            if p.is_file() and p.suffix in (".py", ".sh", ".md")}


def create_lock():
    cfg, sample_report = load_sample()
    if (io.OUT / "runs").exists() or (io.OUT / "score").exists():
        raise ValueError("cannot lock after S3 run/score artifacts")
    pilot_plan = io.read(io.OUT / "pilot/plan.json")
    receipt = io.read(io.OUT / "pilot/receipt.json")
    if pilot_plan["source_sha256"] != source_hashes():
        raise ValueError("code changed since resource pilot; do not silently relock")
    files = dict(cfg["old_input_sha256"], **source_hashes())
    for p in [io.CARD, *sorted((io.OUT / "sample").rglob("*.json")),
              io.OUT / "sample/sample.csv", io.OUT / "pilot/plan.json", io.OUT / "pilot/receipt.json"]:
        files[str(p.relative_to(io.ROOT))] = io.sha(p)
    for m in receipt["measured"]:
        p = io.OUT / "pilot/raw" / (m["id"] + ".json")
        if io.sha(p) != m["sha256"]:
            raise ValueError("resource pilot raw hash mismatch")
        files[str(p.relative_to(io.ROOT))] = m["sha256"]
    io.write(io.LOCK, dict(namespace=io.NAMESPACE, owner="Doan Van Tai", state="LOCKED_BEFORE_TRUTH",
                           seeds=SEEDS, N=N, card_sha256=io.sha(io.CARD), files=files,
                           created_utc=stamp(), truth_status_at_lock="NOT_RUN"))
    print(json.dumps(io.verify_lock()))


def evaluate_one(task):
    meta, purpose, destination, cap = task
    s = legacy()
    target = Path(destination) / (meta["id"] + ".json")
    if target.exists():
        raise FileExistsError(target)
    start, wall = time.process_time(), time.perf_counter()
    result = dict(namespace=io.NAMESPACE, owner="Doan Van Tai",
                  kind="CONFIRMATORY" if purpose == "run" else "RESOURCE_ONLY_NOT_S3",
                  purpose=purpose, id=meta["id"], regime=meta["regime"],
                  source_sha256=io.sha(__file__), old_runner_sha256=io.sha(OLD_RUNNER),
                  status="INCOMPLETE", rows=[], features=[])
    try:
        with s.x.cpu_limit(cap):
            t = time.process_time()
            p = s.x.prepare(s.x.Regime.from_record(meta["regime"]),
                            Ns={side:meta["truncation"][side]["N"] for side in ("A", "B")})
            prepare_cpu = time.process_time() - t
            t = time.process_time()
            with supplied_seeds(s):
                estimator = s.estimate_s(p, purpose)
            telemetry_cpu = time.process_time() - t
            hs, ages = (s.PILOT_H, s.PILOT_AGES) if purpose == "pilot" else (s.H_GRID, s.AGES)
            evaluation = s.evaluate(p, [h*p["T_int"] for h in hs],
                                    [age*p["T_int"] for age in ages], estimator["s_hat"])
            result.update(status="COMPLETED", estimator=estimator, T_int=p["T_int"],
                          h_T_int=list(hs), tau_T_int=list(ages),
                          work=s.work_proxy(p, hs, ages), truncation=p["truncation"],
                          rows=evaluation["rows"], features=evaluation["features"],
                          timing=dict(**evaluation["timing"], prepare=prepare_cpu, telemetry=telemetry_cpu))
    except TimeoutError as exc:
        result.update(status="CPU_CAP", error=repr(exc))
    except Exception as exc:
        result.update(status="ERROR", error=repr(exc))
    result.update(cpu_seconds=time.process_time()-start, wall_seconds=time.perf_counter()-wall)
    io.write(target, result)
    return dict(id=result["id"], status=result["status"], cpu_seconds=result["cpu_seconds"],
                wall_seconds=result["wall_seconds"], timing=result.get("timing"), work=result.get("work"),
                sha256=io.sha(target))


def run_shard(shard, workers, expected_lock_sha):
    # Verify everything before importing CTMC code or reading selected inputs.
    verified = io.verify_lock(expected_sha=expected_lock_sha)
    if shard not in ("0/2", "1/2") or workers != 15:
        raise ValueError("S3 requires exactly 2 shards x 15 workers")
    s = legacy()
    s.x.require_environment()
    cfg, report = load_sample()
    selected = s.shard_rows(report["selected"], shard)
    destination = io.OUT / "runs" / ("shard_" + shard.replace("/", "_of_"))
    destination.mkdir(parents=True, exist_ok=False)  # one-shot reservation
    start = dict(namespace=io.NAMESPACE, owner="Doan Van Tai", shard=shard, workers=workers,
                 ids=[r["id"] for r in selected], lock_sha256=verified["lock_sha256"],
                 sample_sha256=io.sha(io.OUT / "sample/sample.json"),
                 seed_record=SEEDS["run_record"], created_utc=stamp(), retry=False, resume=False)
    io.write(destination / "started.json", start)
    wall = time.perf_counter()
    tasks = [(r, "run", str(destination / "raw"), cfg["cpu_cap_seconds"]) for r in selected]
    with multiprocessing.get_context("spawn").Pool(workers) as pool:
        measured = list(pool.imap_unordered(evaluate_one, tasks, chunksize=1))
    io.write(destination / "receipt.json", dict(
        **start, measured=sorted(measured, key=lambda r:r["id"]),
        statuses=dict(Counter(r["status"] for r in measured)),
        cpu_seconds=sum(r["cpu_seconds"] for r in measured), wall_seconds=time.perf_counter()-wall))
    io.verify_lock(expected_sha=verified["lock_sha256"])
    if any(r["status"] != "COMPLETED" for r in measured):
        raise RuntimeError("S3 shard incomplete; preserve artifacts, no retry/resume")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("sample", "pilot", "lock"):
        sub.add_parser(name)
    verify = sub.add_parser("verify-lock")
    verify.add_argument("--expected-sha")
    run = sub.add_parser("run-shard", help="Claude/GCP only; never a local preparation step")
    run.add_argument("--shard", required=True, choices=("0/2", "1/2"))
    run.add_argument("--workers", type=int, default=15)
    run.add_argument("--expected-lock-sha", required=True)
    args = parser.parse_args(argv)
    if args.command == "verify-lock":
        print(json.dumps(io.verify_lock(expected_sha=args.expected_sha)))
    elif args.command == "run-shard":
        run_shard(args.shard, args.workers, args.expected_lock_sha)
    else:
        {"sample":sample, "pilot":pilot, "lock":create_lock}[args.command]()


if __name__ == "__main__":
    main()
