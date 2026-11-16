"""Rebuild EV-TE test states and audit predicted costs, without truth rollouts.

Run ``python -m experiments.letter.ties_topology pilot`` before ``run``.
The pilot times all 61 regimes (three of the original 500 instances each).
Posterior streams remain per-instance, exactly as ev_te.run_one/choose_twins.
"""
from concurrent.futures import ProcessPoolExecutor, as_completed
import argparse
import csv
import hashlib
import json
from multiprocessing import get_context
from pathlib import Path
import time

import numpy as np

from experiments.ext_validity import ev_te as T

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/letter/w1a"
PIPES = ("M0_new", "M0_old", "P_old", "CE_old")
N, K, PILOT_N = 500, 128, 3


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write("\n")


def write_csv(path, rows):
    with Path(path).open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def state_hash(fresh, stale):
    h = hashlib.sha256()
    for pair in (fresh, *stale):
        for a in pair:
            a = np.ascontiguousarray(a)
            h.update(str((a.shape, a.dtype.str)).encode())
            h.update(a.tobytes())
    return h.hexdigest()


def rebuild_instances(model, training, regime, n=N):
    """Use the truth-run state stream, including all four ages/checkpoints."""
    return T.instances(model, training["T_int"], training["dt"], n,
                       T.seed_for(T.TEST_SEED, regime, 0))


def predicted_costs(model, fresh, stale, training, regime, index, tau_indices=(0, 1, 2, 3)):
    """One original decision instance: tau, pipeline, horizon, action.

    Keep the complete original horizon grid inside the kernel, even if only
    selected horizons will be exported, so checkpoint arithmetic is unchanged.
    """
    taus, hs = T.grid(training["T_int"], training["dt"])
    dt = training["dt"]
    seed = T.seed_for(T.TEST_SEED, regime, 100 + index)
    f = tuple(x[index:index+1] for x in fresh)
    out = np.empty((len(tau_indices), 4, len(hs), len(model.weights)))
    fresh_cost = T.twin_costs(model, *f, dt, hs)[0].T
    for j, t in enumerate(tau_indices):
        sm, sq = (x[index:index+1] for x in stale[t])
        pm, pq = T.posterior(model, sm, sq, dt, taus[t], K,
                             T.seed_for(seed, "posterior", t))
        old = T.twin_costs(model, pm, pq, dt, hs).reshape(1, K, len(model.weights), len(hs)).mean(axis=1)[0]
        conditional_m = sm * np.exp(-2 * model.kappa * taus[t] * dt)
        ce_q = pq.reshape(1, K, -1).mean(axis=1)
        out[j, 0] = fresh_cost
        out[j, 1] = old.T
        out[j, 2] = T.twin_costs(model, sm, sq, dt, hs)[0].T
        out[j, 3] = T.twin_costs(model, conditional_m, ce_q, dt, hs)[0].T
    return out


def tie_masks(costs, relative=1e-9):
    """Primary tie = every action equal; also expose ties among minimizers.

    Relative spread uses max_a |cost_a|, with no absolute tolerance or floor.
    Zero cost vectors satisfy both exact and relative definitions.
    """
    costs = np.asarray(costs, dtype=float)
    if costs.ndim < 1 or costs.shape[-1] < 2 or not np.isfinite(costs).all():
        raise ValueError("finite vectors with at least two actions required")
    lo, hi = costs.min(axis=-1), costs.max(axis=-1)
    scale = np.abs(costs).max(axis=-1)
    exact = hi == lo
    near = hi - lo <= relative * scale
    minima = np.sum(costs == lo[..., None], axis=-1) >= 2
    second = np.partition(costs, 1, axis=-1)[..., 1]
    near_minima = second - lo <= relative * scale
    return dict(exact=exact, relative=near, zero=np.all(costs == 0, axis=-1),
                minimum_exact=minima, minimum_relative=near_minima)


def load_regimes():
    specs = T.read_json(T.OUT / "regimes.json")
    validity = {}
    with (T.OUT / "predictions.csv").open() as f:
        for row in csv.DictReader(f):
            v = row["stationary_rate_valid"] == "True"
            if row["regime"] in validity and validity[row["regime"]] != v:
                raise ValueError("inconsistent stationary-rate eligibility")
            validity[row["regime"]] = v
    tasks = []
    for spec in specs:
        path = T.OUT / "raw" / f"{spec['id']}.json"
        if not path.exists():
            continue
        meta = T.read_json(path)
        training = T.read_json(T.OUT / "train" / f"{spec['id']}.json")
        taus, hs = T.grid(training["T_int"], training["dt"])
        if (training["excluded"] or meta["seed"] != T.TEST_SEED or meta["N"] != N or
                meta["K"] != K or meta["h_steps"] != hs or meta["tau_steps"] != taus):
            raise ValueError(f"unexpected truth configuration: {spec['id']}")
        with np.load(path.with_suffix(".npz"), allow_pickle=False) as raw:
            if raw["pipeline_V"].shape != (N, 4, 6, 6):
                raise ValueError("saved instance count/shape mismatch")
        tasks.append((spec, training, validity[spec["id"]]))
    if len(tasks) != 61:
        raise ValueError(f"expected 61 run regimes, found {len(tasks)}")
    return tasks


def pilot_one(task):
    spec, training, confirmatory, out = task
    start, wall = time.process_time(), time.perf_counter()
    model = T.make_model(spec)
    T.native()
    a = time.process_time()
    fresh, stale = rebuild_instances(model, training, spec["id"])
    rebuild_cpu = time.process_time() - a
    a = time.process_time()
    second = rebuild_instances(model, training, spec["id"])
    hash1, hash2 = state_hash(fresh, stale), state_hash(*second)
    if hash1 != hash2:
        raise AssertionError("state rebuild not bitwise deterministic")
    repeat_cpu = time.process_time() - a
    a = time.process_time()
    costs = np.stack([predicted_costs(model, fresh, stale, training, spec["id"], i) for i in range(PILOT_N)])
    cost_cpu = time.process_time() - a
    # Independent entry point in the locked source; same first-instance choices.
    a = time.process_time()
    original = T.choose_twins(model, tuple(x[:1] for x in fresh),
                             [tuple(x[:1] for x in pair) for pair in stale],
                             training["T_int"], training["dt"], K,
                             T.seed_for(T.TEST_SEED, spec["id"], 100))
    matched = np.array_equal(costs[0].argmin(axis=-1), original[0])
    if not matched:
        raise AssertionError("predicted decisions differ from choose_twins")
    validation_cpu = time.process_time() - a
    folder = out / "pilot"
    folder.mkdir(parents=True, exist_ok=True)
    data = dict(fresh_m=fresh[0], fresh_q=fresh[1], costs=costs)
    for j, (m, q) in enumerate(stale):
        data[f"stale_m{j}"], data[f"stale_q{j}"] = m, q
    with (folder / f"{spec['id']}.npz").open("xb") as f:
        np.savez_compressed(f, **data)
    result = dict(regime=spec["id"], topology=spec["topology"], confirmatory=confirmatory,
                  N=N, K=K, timed_instances=PILOT_N, state_sha256=hash1,
                  repeated_state_sha256=hash2, bitwise_rebuild=True,
                  saved_truth_instance_count=N, choose_twins_first_instance_match=bool(matched),
                  rebuild_cpu_s=rebuild_cpu, repeat_cpu_s=repeat_cpu,
                  predicted_cost_cpu_s=cost_cpu, validation_cpu_s=validation_cpu,
                  projected_full_cpu_s=rebuild_cpu + N / PILOT_N * cost_cpu,
                  cpu_s=time.process_time()-start, wall_s=time.perf_counter()-wall)
    write_json(folder / f"{spec['id']}.json", result)
    return result


def run_one(task):
    spec, training, confirmatory, out, scope = task
    start, wall = time.process_time(), time.perf_counter()
    model = T.make_model(spec)
    tau_indices = (0, 1, 2, 3) if scope == "full" else (1, 3)
    h_indices = tuple(range(6)) if scope == "full" else (3, 5)
    with np.load(out / "pilot" / f"{spec['id']}.npz", allow_pickle=False) as saved:
        fresh = saved["fresh_m"], saved["fresh_q"]
        stale = [(saved[f"stale_m{t}"], saved[f"stale_q{t}"]) for t in range(4)]
        costs = np.empty((N, len(tau_indices), 4, len(h_indices), len(model.weights)))
        costs[:PILOT_N] = saved["costs"][:, tau_indices][:, :, :, h_indices]
    for i in range(PILOT_N, N):
        costs[i] = predicted_costs(model, fresh, stale, training, spec["id"], i, tau_indices)[:, :, h_indices]
    masks = tie_masks(costs)
    rows = []
    for t, ti in enumerate(tau_indices):
        for p, name in enumerate(PIPES):
            for h, hi in enumerate(h_indices):
                row = dict(regime=spec["id"], topology=spec["topology"], confirmatory=confirmatory,
                           tau_mult=T.TAUS[ti], h_mult=T.HS[hi],
                           tau=training["tau_steps"][ti]*training["dt"],
                           h=training["h_steps"][hi]*training["dt"], pipeline=name,
                           N=N, K=K, actions=len(model.weights))
                for label, mask in masks.items():
                    count = int(mask[:, t, p, h].sum())
                    row[f"{label}_count"], row[f"{label}_share"] = count, count/N
                rows.append(row)
    folder = out / "topology"
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / f"{spec['id']}.npz").open("xb") as f:
        np.savez_compressed(f, predicted_costs=costs, tau_indices=tau_indices, h_indices=h_indices,
                            pipelines=np.array(PIPES))
    result = dict(regime=spec["id"], cpu_s=time.process_time()-start,
                  wall_s=time.perf_counter()-wall, reused_pilot_instances=PILOT_N, rows=rows)
    write_json(folder / f"{spec['id']}.json", result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("pilot", "run"))
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    if not 1 <= args.workers <= 8:
        parser.error("workers must be between 1 and 8")
    tasks = load_regimes()
    start, wall = time.process_time(), time.perf_counter()
    if args.command == "pilot":
        target = args.out / "topology_pilot.json"
        if target.exists() or (args.out / "pilot").exists():
            raise FileExistsError("pilot outputs already exist")
        jobs = [(*task, args.out) for task in tasks]
        work = pilot_one
    else:
        target = args.out / "topology_summary.json"
        if target.exists() or (args.out / "topology").exists():
            raise FileExistsError("topology outputs already exist")
        pilot = T.read_json(args.out / "topology_pilot.json")
        scope = pilot["selected_scope"]
        jobs = [(*task, args.out, scope) for task in tasks]
        work = run_one
    results = []
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=get_context("spawn")) as pool:
        for future in as_completed([pool.submit(work, job) for job in jobs]):
            result = future.result()
            results.append(result)
            print(json.dumps(dict(command=args.command, completed=len(results),
                                  regime=result["regime"], cpu_s=result["cpu_s"])), flush=True)
    results.sort(key=lambda r: r["regime"])
    base = dict(responsible="Doan Van Tai", seed=T.TEST_SEED, N=N, K=K,
                regimes=len(results), workers=args.workers,
                parent_cpu_s=time.process_time()-start,
                worker_cpu_s=sum(r["cpu_s"] for r in results), wall_s=time.perf_counter()-wall)
    if args.command == "pilot":
        projection = sum(r["projected_full_cpu_s"] for r in results)
        # Exactly the brief's two-hour, eight-worker projection gate.
        base.update(regime_timings=results, projected_full_cpu_s=projection,
                    projected_wall_s_on_8_workers=projection/8,
                    projection_is_estimate_not_guarantee=True,
                    selected_scope="reduced" if projection/8 > 2*3600 else "full",
                    selection_rule="full unless projected total CPU / 8 exceeds 7200 seconds")
    else:
        rows = [row for result in results for row in result["rows"]]
        write_csv(args.out / "topology_ties.csv", rows)
        base.update(scope=scope, cells=len(rows),
                    tau_mult=list(T.TAUS) if scope == "full" else [.3, 3.],
                    h_mult=list(T.HS) if scope == "full" else [7, 30],
                    primary_tie="all actions equal", relative_tolerance=1e-9,
                    relative_scale="max absolute predicted action cost; no absolute floor",
                    determinism="61/61 complete state rebuilds bitwise equal; N=500 equals saved truth; first-instance argmin equals locked choose_twins")
    write_json(target, base)
    print(json.dumps({k:v for k,v in base.items() if k != "regime_timings"}), flush=True)


if __name__ == "__main__":
    main()
