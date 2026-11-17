"""Doan Van Tai — V7-2 saved-artifact audit and train-only timing pilot.

No test runner, scientific scoring, VM operation, or existing-file write.
Run with Python -B. All outputs are exclusive new files under v7_2/.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import resource
import subprocess
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/letter/v7_2"
SERIES = ROOT / "results/ext_validity/ev_d4/series_ditl4h_mod10.npz"
BRIEF = ROOT / "notes/ops/codex/V7_2_brief.md"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write_new(path, value):
    payload = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        stream.write(payload)


def stats(values):
    values = np.asarray(values, dtype=float)
    if not len(values) or not np.isfinite(values).all():
        raise ValueError("need nonempty finite observations")
    return dict(n=len(values), min=float(values.min()), median=float(np.median(values)),
                max=float(values.max()), sum=float(values.sum()))


def window_plan(duration, train=3600.0, max_age=300.0, step=300.0):
    """Metadata arithmetic only; stale observations must also follow training."""
    if not all(math.isfinite(x) for x in (duration, train, max_age, step)):
        raise ValueError("nonfinite window parameter")
    if min(duration, train, step) <= 0 or max_age < 0:
        raise ValueError("invalid window parameter")
    first = train + max_age
    holds = {}
    for hours in (1, 2, 4):
        h = hours * 3600.0
        n = max(0, math.floor((duration - first - h) / step) + 1)
        holds[str(hours)] = dict(hold_s=h, first_anchor_s=first,
                                last_eligible_anchor_s=first+(n-1)*step if n else None,
                                anchor_count=n, ready=n > 0,
                                minimum_record_s=first+h,
                                record_s_for_12_common_anchors=first+11*step+h)
    return dict(duration_s=duration, train_s=train, max_age_s=max_age,
                step_s=step, holds=holds)


def verify_entries(base, entries):
    problems = []
    for name, expected in entries.items():
        path = base / name
        actual = digest(path) if path.is_file() else None
        if actual != expected:
            problems.append(dict(path=str(path.relative_to(ROOT)), expected=expected, actual=actual))
    return dict(checked=len(entries), mismatches=problems, passed=not problems)


def audit_saved():
    committed = subprocess.check_output(["git", "show", "HEAD:notes/ops/codex/V7_2_brief.md"], cwd=ROOT)
    if committed != BRIEF.read_bytes():
        raise ValueError("brief differs from HEAD")
    inputs = {str(BRIEF.relative_to(ROOT)): digest(BRIEF)}
    datasets, raw_rows = {}, []
    for name in ("ev_d4b", "ev_d4c"):
        directory = ROOT / "results/ext_validity" / name
        cases = read(directory / "cases.json")
        manifest = read(directory / "raw_manifest.json")
        lock = read(directory / "lock.json")
        raw_checks = verify_entries(directory / "test", manifest["sha256"])
        lock_checks = verify_entries(ROOT, lock["sha256"])
        train_checks = None
        if (directory / "train_manifest.json").exists():
            tm = read(directory / "train_manifest.json")
            train_checks = verify_entries(directory, tm["sha256"])
        arms = {}
        for path in sorted((directory / "test").glob("*.json")):
            raw = read(path)
            case = raw["case"]
            arm = case.get("arm", "B")
            row = dict(dataset=name, arm=arm, file=str(path.relative_to(ROOT)),
                       id=case["id"], h_mult=raw["h_mult"], h_s=raw["h"],
                       tau_s=raw["tau"], T_int_s=raw["T_int"],
                       n_inst=raw["n_inst"], CPU_s=raw["CPU"], wall_s=raw["wall"],
                       CPU_per_instance_h_s=raw["CPU"]/(raw["n_inst"]*raw["h"]),
                       mean_parameter_load=(max(case["lamA"], case["lamB"])+case["u"])/10,
                       virtual_run_s=case.get("warmup", 1000.)+raw["tau"]
                           +(raw["n_inst"]-1)*raw["spacing"]+raw["h"],
                       case_signature_valid=digest_bytes(case)==raw["case_sha256"])
            raw_rows.append(row)
            arms.setdefault(arm, []).append(row)
        summary = {}
        for arm, rows in arms.items():
            summary[arm] = dict(n_files=len(rows),
                T_int_s=stats([r["T_int_s"] for r in rows]),
                h_s=stats([r["h_s"] for r in rows]),
                tau_s=stats([r["tau_s"] for r in rows]),
                CPU_s=stats([r["CPU_s"] for r in rows]),
                wall_per_job_s=stats([r["wall_s"] for r in rows]),
                CPU_per_instance_h_s=stats([r["CPU_per_instance_h_s"] for r in rows]),
                virtual_run_s=stats([r["virtual_run_s"] for r in rows]),
                load=stats([r["mean_parameter_load"] for r in rows]))
        first = read(next((directory / "test").glob("*.json")))
        train_paths = sorted((directory / "train").glob("*.json"))
        probes = sorted((directory / "train_probe").glob("*.json"))
        with (directory / "predictions.csv").open(newline="") as stream:
            prediction_count = sum(1 for _ in csv.DictReader(stream))
        datasets[name] = dict(cases=len(cases), train_files=len(train_paths), probe_files=len(probes),
            prediction_rows=prediction_count, manifest_files=manifest["n"],
            raw_checks=raw_checks, lock_checks=lock_checks, train_checks=train_checks,
            actual_test_files=sum(len(v) for v in arms.values()), arms=summary,
            train_CPU_s=stats([read(p)["CPU"] for p in train_paths]),
            raw_keys=sorted(first), twin_names=list(first["twins"]),
            per_instance_costs_saved=False, posterior_samples_saved=False,
            stochastic_reference_saved=False,
            case_signatures_pass=all(r["case_signature_valid"] for r in raw_rows if r["dataset"]==name))
        for filename in ("cases.json", "cases_all.json", "lock.json", "raw_manifest.json",
                         "train_manifest.json", "CARD.md", "REPORT_EV_D4B.md", "REPORT_EV_D4C.md", "pipeline.log"):
            path = directory / filename
            if path.exists():
                inputs[str(path.relative_to(ROOT))] = digest(path)
        inputs.update({p: digest(ROOT/p) for p in lock["sha256"]})
    with np.load(SERIES, allow_pickle=False) as data:
        meta = json.loads(str(data["metadata"].item()))
        lengths = {k: len(data[k]) for k in ("s0", "s1")}
    sidecar = SERIES.with_suffix(".json")
    inputs[str(sidecar.relative_to(ROOT))] = digest(sidecar)
    result = dict(owner="Doan Van Tai", audit_type="saved outputs and metadata only; no new test outcome",
        git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        brief_matches_HEAD=True, datasets=datasets,
        trace=dict(path=str(SERIES.relative_to(ROOT)), sha256=digest(SERIES), bytes=SERIES.stat().st_size,
                   metadata=meta, array_lengths=lengths, sidecar_matches_embedded=read(sidecar)==meta,
                   window_plan=window_plan(lengths["s0"]*meta["bin"])),
        input_sha256=inputs, VM_access="NOT_USED: required series is already local",
        new_test_outcomes_computed=0)
    with (OUT/"raw_inventory.csv").open("x", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(raw_rows[0]))
        writer.writeheader()
        writer.writerows(raw_rows)
    write_new(OUT/"audit.json", result)
    print(json.dumps(dict(datasets={k:dict(raw=v["actual_test_files"],
        lock_pass=v["lock_checks"]["passed"], raw_pass=v["raw_checks"]["passed"],
        arms=v["arms"]) for k,v in datasets.items()}, window_plan=result["trace"]["window_plan"]), indent=2))


def digest_bytes(case):
    return hashlib.sha256(json.dumps(case, sort_keys=True).encode()).hexdigest()


def train_arrivals(counts, mean_train, lam, dt, rng):
    """One forward pass over the supplied training prefix; no modulo/phase."""
    counts = np.asarray(counts, dtype=float)
    if counts.ndim != 1 or not len(counts) or not np.isfinite(counts).all() or np.any(counts < 0):
        raise ValueError("invalid train prefix")
    if not np.isfinite([mean_train, lam, dt]).all() or min(mean_train, dt) <= 0 or lam < 0:
        raise ValueError("invalid training calibration")
    n = rng.poisson(lam*counts/mean_train*dt)
    return np.sort(np.repeat(np.arange(len(counts))*dt, n) + rng.random(int(n.sum()))*dt)


def timing_pilot():
    # Importing packet.py has no scientific side effect. Never call its train,
    # simulate, futures, job, background, or case/score CLI entry points here.
    from experiments.ext_validity import packet as P
    with np.load(SERIES, allow_pickle=False) as data:
        dt = json.loads(str(data["metadata"].item()))["bin"]
        train = [np.array(data[k][:int(3600/dt)], dtype=float) for k in ("s0", "s1")]
    means = [float(x.mean()) for x in train]
    # Parameters fixed from design metadata, ranked by total offered mean load.
    cases = read(ROOT/"results/ext_validity/ev_d4b/cases.json")
    case = sorted(cases, key=lambda c: (-(c["lamA"]+c["lamB"]+c["u"]), c["id"]))[0]
    measurements = []
    for duration, seed in ((60., 8722001), (120., 8722002), (300., 8722003)):
        rng = np.random.default_rng(seed)
        count = 16
        clock, wall = time.process_time(), time.perf_counter()
        backgrounds, services, flows, flow_services = [[], []], [[], []], [], []
        events = 0
        for _ in range(count):
            for j, key in enumerate(("lamA", "lamB")):
                at = train_arrivals(train[j][:int(duration/dt)], means[j], case[key], dt, rng)
                backgrounds[j].append(at)
                services[j].append(rng.exponential(1/P.MU, len(at)))
                events += len(at)
            flow = P.poisson(case["u"], duration, rng)
            flows.append(flow)
            flow_services.append(rng.exponential(1/P.MU, len(flow)))
            events += len(flow)
        sampling_cpu = time.process_time()-clock
        kernel_clock = time.process_time()
        for j in (0, 1):
            for action in (0, 1):
                lengths = [len(a)+(len(f) if j==action else 0) for a,f in zip(backgrounds[j], flows)]
                at = np.full((count, max(lengths)), np.inf)
                sv = np.zeros_like(at)
                for i in range(count):
                    t, s = backgrounds[j][i], services[j][i]
                    if j == action:
                        t, s = np.r_[t, flows[i]], np.r_[s, flow_services[i]]
                    order = np.argsort(t, kind="stable")
                    at[i, :len(t)], sv[i, :len(t)] = t[order], s[order]
                # q=0 synthetic initial state; training-prefix intensities only.
                # Discard costs immediately: no decision, s-hat, G_S, or regret.
                cost = P.lindley_cost(np.zeros(count, dtype=int), at, sv,
                                       np.empty((count, 0)), duration)
                if not np.isfinite(cost).all():
                    raise ArithmeticError("nonfinite training-kernel output")
        cpu = time.process_time()-clock
        measurements.append(dict(train_prefix_s=[0., duration], rollout_count=count, seed=seed,
            initial_queue=[0, 0], generated_events=events, sampling_CPU_s=sampling_cpu,
            kernel_CPU_s=time.process_time()-kernel_clock, CPU_s=cpu,
            wall_s=time.perf_counter()-wall, CPU_per_paired_rollout_h_s=cpu/(count*duration),
            finite_check=True))
    result = dict(owner="Doan Van Tai", type="training-prefix kernel timing; NOT a test or precision pilot",
        trace_sha256=digest(SERIES), calibration_interval_s=[0., 3600.], physics_interval_s=[0., 300.],
        parameter_case_id=case["id"], parameters={k:case[k] for k in ("lamA", "lamB", "u")},
        training_mean_counts_per_bin=means, measurements=measurements,
        peak_process_memory_MiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.,
        environment=dict(python=platform.python_version(), numpy=np.__version__, platform=platform.platform()),
        extrapolation_caveat="Short q=0 prefixes do not measure long-horizon memory, posterior accuracy, or reference precision.",
        new_test_outcomes_computed=0, test_entry_points_called=[], subprocesses=0)
    write_new(OUT/"pilot.json", result)
    print(json.dumps(result, indent=2))


def estimate():
    """Planning arithmetic; proposed sizes are not a locked scientific card."""
    audit, pilot = read(OUT/"audit.json"), read(OUT/"pilot.json")
    rate = pilot["measurements"][-1]["CPU_per_paired_rollout_h_s"]
    rates = [m["CPU_per_paired_rollout_h_s"] for m in pilot["measurements"]]
    for study, arm in (("ev_d4b", "B"), ("ev_d4c", "C")):
        rates.append(audit["datasets"][study]["arms"][arm]["CPU_per_instance_h_s"]["max"])
    worst_measured_rate = max(rates)
    g, anchors, reps, k, rdec, reval, rtrain = 20, 12, 8, 128, 128, 256, 32
    taus = [1, 10, 30, 60, 120, 300]
    n = anchors*reps
    posterior_work = g*n*k*sum(taus)
    training_work = g*rtrain*3600
    instance_work = g*reps*7200
    scenarios = {}
    for label, horizons in (("1_2h_available", [3600, 7200]),
                             ("1_2_4h_requires_longer_data", [3600, 7200, 14400])):
        nested_work = g*n*(rdec+reval)*max(horizons)
        separate_work = g*n*(rdec+reval)*sum(horizons)
        fixed = posterior_work+training_work+instance_work
        central = (nested_work+fixed)*rate
        conservative = (separate_work+fixed)*worst_measured_rate*2
        scenarios[label] = dict(holds_s=horizons, N_per_regime=n,
            cost_rollout_s_nested=nested_work, cost_rollout_s_separate=separate_work,
            posterior_rollout_s=posterior_work, training_rollout_s=training_work,
            instance_history_rollout_s=instance_work,
            central_CPU_s=central, central_CPU_hours=central/3600,
            separate_horizons_with_2x_contingency_CPU_s=conservative,
            separate_horizons_with_2x_contingency_CPU_hours=conservative/3600,
            ideal_12_worker_wall_hours=central/(3600*12),
            planning_12_worker_65pct_utilization_wall_hours=[central/(3600*12*.65),
                                                           conservative/(3600*12*.65)])
    # Memory is a rough array-volume calculation, not a measured peak at 4 h.
    params = pilot["parameters"]
    expected_events_4h = 14400*(params["lamA"]+params["lamB"]+params["u"])
    memory = {str(batch): expected_events_4h*batch*8*12/2**30 for batch in (8, 16, 256)}
    result = dict(owner="Doan Van Tai", status="DESIGN_DRAFT_NOT_LOCKED",
        parameters=dict(regimes=g, anchors=anchors, history_replicates=reps, K=k,
                        R_dec=rdec, R_eval=reval, R_train=rtrain, taus_s=taus),
        central_throughput_CPU_per_paired_rollout_s=rate,
        worst_observed_throughput_CPU_per_paired_rollout_s=worst_measured_rate,
        scenarios=scenarios,
        rough_4h_array_volume_GiB_12_arrays_by_batch=memory,
        assumptions=["Reuse the same CRN trajectory for nested horizons in the central scenario.",
                     "Separate-horizon scenario plus an explicit 2x planning contingency is not a runtime bound or CI.",
                     "12 workers and 65% utilization are planning assumptions, not a VM recommendation or measurement.",
                     "K/R/N are proposals; this timing pilot measures neither posterior nor reference precision.",
                     "Small train-prefix q=0 costs can understate long-horizon sorting, queue and memory costs.",
                     "Posterior and history propagation are conservatively charged as paired action-cost rollouts.",
                     "All 1/2/4 h scenarios remain data-blocked until a sufficiently long continuous record is verified."],
        source_sha256={"audit.json":digest(OUT/"audit.json"), "pilot.json":digest(OUT/"pilot.json")},
        new_test_outcomes_computed=0)
    write_new(OUT/"compute_estimate.json", result)
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("audit", "pilot", "estimate"))
    args = parser.parse_args()
    {"audit": audit_saved, "pilot": timing_pilot, "estimate": estimate}[args.command]()


if __name__ == "__main__":
    main()
