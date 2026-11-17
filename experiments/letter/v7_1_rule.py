"""Doan Van Tai — the fixed V7-1 post-hoc gap-scale analysis.

No truth evaluator is called: regenerate only the old M0 predictors from their
original inputs, verify saved quantities/decisions, and read saved regrets.
Run ``pilot`` before ``run``; both commands refuse to overwrite artifacts.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time

import numpy as np
from scipy.stats import rankdata, spearmanr

from experiments.explore_ctmc import ctmc
from experiments.letter.e3_agediff import posterior_full
from experiments.letter import e4_geant as E

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/letter/v7_1"
PREDICTORS = ("P1", "P2", "P3")
BOOTSTRAP_SEED = 20261118
DRAWS = 2000
REL_TOL = 1e-9
LOCAL_CAP_S = 1200


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    payload = json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle:
        handle.write(payload)


def write_csv(path, rows):
    if not rows:
        raise ValueError("empty table")
    with Path(path).open("x", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def check_relative(name, actual, saved):
    """No absolute tolerance that could hide errors in a saved tiny quantity."""
    actual, saved = float(actual), float(saved)
    if not math.isfinite(actual) or not math.isfinite(saved):
        raise ArithmeticError(f"nonfinite check: {name}")
    relative = abs(actual - saved) / abs(saved) if saved else (0. if actual == 0 else math.inf)
    if relative > REL_TOL:
        raise ArithmeticError(f"{name}: {actual!r} != {saved!r}; relative={relative}")
    return dict(name=name, actual=actual, saved=saved, relative_error=relative)


def auc(y, score):
    """P(score_positive > score_negative) + half the probability of a tie."""
    y, score = np.asarray(y), np.asarray(score, dtype=float)
    if y.ndim != 1 or score.shape != y.shape or not np.isfinite(score).all():
        raise ValueError("finite aligned vectors required")
    if not np.isin(y, (0, 1)).all():
        raise ValueError("binary Y required")
    positive = int(y.sum())
    negative = len(y) - positive
    if positive == 0 or negative == 0:
        return None
    ranks = rankdata(score, method="average")
    return float((ranks[y == 1].sum() - positive * (positive + 1) / 2)
                 / (positive * negative))


def pair_abs_cdf(x, w_x, z, w_z, threshold):
    """Stationary P(|x(X_A)+z(X_B)| <= threshold), without a dense product."""
    order = np.argsort(z, kind="stable")
    z = np.asarray(z)[order]
    cumulative = np.r_[0., np.cumsum(np.asarray(w_z)[order])]
    lo = np.searchsorted(z, -threshold - np.asarray(x), side="left")
    hi = np.searchsorted(z, threshold - np.asarray(x), side="right")
    return float(np.asarray(w_x) @ (cumulative[hi] - cumulative[lo]))


def law_quantile(components, probability=.9):
    """Generalized inverse CDF; components are (mass, A-gap, pi_A, B-gap, pi_B).

    Equal mass to fresh/stale and equal ages on each side. A fresh component
    therefore has mass 1/2, and each of the five old components has mass 1/10.
    Floating bisection returns the upper endpoint containing the target mass.
    """
    prepared = []
    upper = 0.
    for mass, x, wx, z, wz in components:
        if mass < 0 or np.min(wx) < 0 or np.min(wz) < 0:
            raise ValueError("probability weights must be nonnegative")
        order = np.argsort(z, kind="stable")
        prepared.append((mass, np.asarray(x), np.asarray(wx), np.asarray(z)[order],
                         np.r_[0., np.cumsum(np.asarray(wz)[order])]))
        upper = max(upper, abs(float(np.min(x) + np.min(z))),
                    abs(float(np.max(x) + np.max(z))))
    if not math.isclose(sum(c[0] for c in components), 1., abs_tol=1e-14):
        raise ValueError("mixture weights must sum to one")

    def cdf(t):
        result = 0.
        for mass, x, wx, z, cumulative in prepared:
            lo = np.searchsorted(z, -t-x, side="left")
            hi = np.searchsorted(z, t-x, side="right")
            result += mass * float(wx @ (cumulative[hi] - cumulative[lo]))
        return result

    if cdf(0.) >= probability:
        return 0.
    lower = 0.
    for _ in range(80):
        middle = (lower + upper) / 2
        if middle == lower or middle == upper:
            break
        if cdf(middle) >= probability:
            upper = middle
        else:
            lower = middle
    return upper


def ctmc_work(raw):
    ev = raw["evaluations"][0]
    kappa = float(F(ev["parameters"][3]))
    return sum(2*(ch["N"]+1)*(float(F(ch["load"]))+ev["a"]+10+1/kappa)
               for name, ch in ev["chains"].items() if name.endswith("stay")) * max(
                   e["tau"] for e in raw["evaluations"])


def extract_ctmc(raw, progress=False):
    """Uncorrected saturation gap on every truncated state and exact full-old law."""
    start, wall = time.process_time(), time.perf_counter()
    ev = raw["evaluations"][0]
    la, lb, u, k, cost = map(F, ev["parameters"])
    if cost != 0 or len(raw["evaluations"]) != 5:
        raise ValueError("unexpected W1b configuration")
    a = F(str(ev["a"]))
    na, nb = ev["N"]["A"], ev["N"]["B"]
    chains = dict(A_stay=ctmc.chain(la+u, k, na, a),
                  A_switch=ctmc.chain(la, k, na, a),
                  B_stay=ctmc.chain(lb, k, nb, a),
                  B_switch=ctmc.chain(lb+u, k, nb, a))
    checks = []
    for name, ch in chains.items():
        for variable in ("r", "T_int", "var"):
            checks.append(check_relative(f"{name}.{variable}", getattr(ch, variable),
                                         ev["chains"][name][variable]))
    ti = max(ch.T_int for ch in chains.values())
    # Use the original subtraction grouping for a byte-compatible true s.
    s = (chains["A_switch"].r+chains["B_switch"].r) - (chains["A_stay"].r+chains["B_stay"].r)
    checks += [check_relative("T_int", ti, raw["T_int"]),
               check_relative("s", s, raw["s"])]
    da = ctmc.m0_gap(la, u, k, na, [math.inf], "A", a=a)[0]
    db = ctmc.m0_gap(lb, u, k, nb, [math.inf], "B", a=a)[0]
    wa, wb = chains["A_stay"].pi, chains["B_stay"].pi
    zero_a, zero_b = np.zeros_like(da), np.zeros_like(db)
    fresh_mass = ctmc.pair_sum(wa, da, zero_a, wb, db, zero_b, 0)[0]
    checks.append(check_relative("saturation.F_new", fresh_mass, ev["asymptotic"]["F_new"]))
    maximum = max(abs(float(da.min()+db.min())), abs(float(da.max()+db.max())))
    components = [(0.5, da, wa, db, wb)]
    old_vectors = {}
    pa, pb, previous_tau = da.copy(), db.copy(), 0.
    for age in sorted(raw["evaluations"], key=lambda x: x["tau"]):
        tau = age["tau"]
        pa = posterior_full(chains["A_stay"], pa, tau-previous_tau)
        pb = posterior_full(chains["B_stay"], pb, tau-previous_tau)
        previous_tau = tau
        mass = ctmc.pair_sum(wa, pa, zero_a, wb, pb, zero_b, 0)[0]
        checks.append(check_relative(f"{age['age_label']}.saturation.F_old", mass,
                                     age["asymptotic"]["F_old"]))
        components.append((0.5/len(raw["evaluations"]), pa, wa, pb, wb))
        old_vectors[age["age_label"]] = (pa, pb)
        if progress:
            print(json.dumps(dict(event="ctmc_age", regime=raw["id"],
                                  age=age["age_label"], cpu_s=time.process_time()-start)), flush=True)
    q90 = law_quantile(components)
    if q90 <= 0 or maximum <= 0 or s == 0:
        raise ValueError("undefined fixed gap-scale predictor")
    scale = dict(dataset="CTMC", regime=raw["id"], seed="none", family=raw["family"],
                 M_hat=maximum, Q90=q90, s_hat=s, T_int_s=ti, h_star_s=q90/abs(s),
                 h_star_Tint=q90/abs(s)/ti, horizon="saturation_inf",
                 gap_units="packet*s", rate_units="packet", source=f"results/letter/w1b/raw/{raw['id']}.json",
                 max_relative_error=max(c["relative_error"] for c in checks))
    arrays = dict(gap_A=da, gap_B=db, pi_A=wa, pi_B=wb)
    for label, (oa, ob) in old_vectors.items():
        arrays[f"old_A_{label}"] = oa
        arrays[f"old_B_{label}"] = ob
    return dict(scale=scale, checks=checks, cpu_s=time.process_time()-start,
                wall_s=time.perf_counter()-wall), arrays


def extract_geant_chunk(spec, training, sub, chunk):
    """Recreate ONLY M0 costs; original per-instance posterior seeds are essential.

    V in the old NPZ is plant MC cost and is NEVER treated as a fluid gap.
    The returned fresh_gap[n,h] and stale_gap[n,tau,h] have no h*s correction.
    """
    start, wall = time.process_time(), time.perf_counter()
    old_path = ROOT / "results/letter" / sub / "raw" / f"{spec['id']}_chunk{chunk:02d}.npz"
    meta = json.loads(old_path.with_suffix(".json").read_text())
    if meta["npz_sha256"] != sha(old_path) or meta["pilot"]:
        raise ValueError("saved raw hash/pilot mismatch")
    seed, n, k = meta["seed"], meta["N"], meta["K"]
    model = E.T.make_model(spec)
    if len(model.weights) != 2:
        raise ValueError("card requires a scalar Switch - Stay gap")
    levels, _ = E.rate_levels(model, training)
    ti, dt = training["T_int"], training["dt"]
    taus, hs = E.e4_grid(ti, dt)
    checks = [check_relative("T_int", ti, meta["T_int"]),
              check_relative("dt", dt, meta["dt"])]
    fresh, all_stale = E.T.instances(model, ti, dt, n,
                                    E.stream_seed(seed, spec["id"], chunk, "instances"))
    stale = [all_stale[t] for t in E.TAU_INDEX]
    # The native kernel is per-instance deterministic; batching keeps all scalars.
    fresh_cost = E.T.twin_costs(model, *fresh, dt, hs)
    old_cost = np.empty((n, 2, len(taus), len(hs)))
    for i in range(n):
        root = E.stream_seed(seed, spec["id"], chunk, f"instance={i}")
        for t, (state, age) in enumerate(zip(stale, taus)):
            sm, sq = (x[i:i+1] for x in state)
            pm, pq = E.T.posterior(model, sm, sq, dt, age, k, E.T.seed_for(root, "posterior", t))
            old_cost[i, :, t] = E.T.twin_costs(model, pm, pq, dt, hs).reshape(1, k, 2, len(hs)).mean(axis=1)[0]
    with np.load(old_path, allow_pickle=False) as saved:
        np.testing.assert_array_equal(saved["h"], np.array(hs)*dt)
        np.testing.assert_array_equal(saved["tau"], np.array(taus)*dt)
        np.testing.assert_array_equal(saved["instance_id"], chunk*E.CHUNK_SIZE+np.arange(n))
        names = list(saved["pipelines"])
        matched = 0
        for label in ("M0", "Hybrid-i"):
            ix = names.index(label)
            fc = fresh_cost if label == "M0" else E.hybrid_costs(fresh_cost, levels["i"], np.array(hs)*dt)
            decisions, flags = E.pick(fc)
            np.testing.assert_array_equal(np.repeat(decisions[:, None, :], len(taus), axis=1),
                                          saved["decisions"][:, ix, 0])
            np.testing.assert_array_equal(np.repeat(flags[:, None, :], len(taus), axis=1),
                                          saved["tie_flags"][:, ix, 0])
            for t in range(len(taus)):
                oc = old_cost[:, :, t]
                if label == "Hybrid-i":
                    oc = E.hybrid_costs(oc, levels["i"], np.array(hs)*dt)
                decisions, flags = E.pick(oc)
                np.testing.assert_array_equal(decisions, saved["decisions"][:, ix, 1, t])
                np.testing.assert_array_equal(flags, saved["tie_flags"][:, ix, 1, t])
            matched += 2*n*len(taus)*len(hs)
    arrays = dict(fresh_gap=fresh_cost[:, 1]-fresh_cost[:, 0],
                  stale_gap=old_cost[:, 1]-old_cost[:, 0], h=np.array(hs)*dt,
                  tau=np.array(taus)*dt, instance_id=chunk*E.CHUNK_SIZE+np.arange(n))
    return dict(regime=spec["id"], seed=seed, dataset="GEANT", sub=sub, chunk=chunk,
                checks=checks, exact_decisions_checked=matched, exact_tie_flags_checked=matched,
                source=str(old_path.relative_to(ROOT)), source_sha256=sha(old_path),
                cpu_s=time.process_time()-start, wall_s=time.perf_counter()-wall), arrays


def save_extraction(out, prefix, result, arrays):
    write_json(out / "extracted" / f"{prefix}.json", result)
    destination = out / "extracted" / f"{prefix}.npz"
    with destination.open("xb") as handle:
        np.savez_compressed(handle, **arrays)


def geant_inputs():
    specs = E.selected_specs()
    training = {s["id"]: json.loads((E.EV/"train"/f"{s['id']}.json").read_text()) for s in specs}
    return specs, training


def pilot(out=OUT):
    if (out/"pilot.json").exists():
        raise FileExistsError("pilot already exists")
    (out/"extracted").mkdir(parents=True, exist_ok=True)
    inputs = [json.loads(p.read_text()) for p in sorted((ROOT/"results/letter/w1b/raw").glob("*.json"))]
    raw = max(inputs, key=ctmc_work)
    first, arrays = extract_ctmc(raw, progress=True)
    save_extraction(out, "CTMC_"+raw["id"], first, arrays)
    specs, training = geant_inputs()
    # The largest saved E4 CPU chunk includes the slowest workload, not a light pilot.
    metadata = [json.loads(p.read_text()) for sub in ("e4", "e4b")
                for p in (ROOT/"results/letter"/sub/"raw").glob("*.json")]
    largest = max(metadata, key=lambda x: x["CPU"])
    sub = "e4" if largest["seed"] == 3000001 else "e4b"
    spec = next(s for s in specs if s["id"] == largest["regime"])
    second, arrays = extract_geant_chunk(spec, training[spec["id"]], sub, largest["chunk"])
    save_extraction(out, f"GEANT_{sub}_{spec['id']}_{largest['chunk']:02d}", second, arrays)
    factor = sum(ctmc_work(r) for r in inputs)/ctmc_work(raw)
    # Conservative: charge the worst observed M0 chunk to all 340 GEANT chunks.
    projected = first["wall_s"]*factor + second["wall_s"]*len(metadata)
    record = dict(owner="Doan Van Tai", status="GO" if projected <= LOCAL_CAP_S else "STOP_FOR_GCP",
                  ctmc=first, geant=second, ctmc_work_factor=factor,
                  geant_chunk_count=len(metadata), projected_total_local_wall_s=projected,
                  projection="CTMC sparse-generator work ratio plus worst GEANT chunk times all 340 chunks; no parallel speedup assumed",
                  cap_s=LOCAL_CAP_S, cpu_s=first["cpu_s"]+second["cpu_s"],
                  wall_s=first["wall_s"]+second["wall_s"])
    write_json(out/"pilot.json", record)
    print(json.dumps({k:record[k] for k in ("status", "projected_total_local_wall_s", "cpu_s", "wall_s")}), flush=True)
    return record


def read_extraction(out, prefix):
    target = out/"extracted"/f"{prefix}.json"
    if not target.exists():
        return None
    if not target.with_suffix(".npz").exists():
        raise ValueError(f"incomplete extraction {prefix}")
    return json.loads(target.read_text())


def geant_scale(out, spec, training, sub):
    fresh, stale, timings = [], [], []
    for chunk in range(10):
        prefix = f"GEANT_{sub}_{spec['id']}_{chunk:02d}"
        record = read_extraction(out, prefix)
        if record is None:
            record, arrays = extract_geant_chunk(spec, training, sub, chunk)
            save_extraction(out, prefix, record, arrays)
        with np.load(out/"extracted"/f"{prefix}.npz", allow_pickle=False) as arrays:
            fresh.append(arrays["fresh_gap"][:, -1])
            stale.append(arrays["stale_gap"][:, :, -1])
            h_max = float(arrays["h"][-1])
        timings.append(record)
    fresh, stale = np.concatenate(fresh), np.concatenate(stale)
    # Fresh replicated per age: both sides receive exactly 1/2 of the pooled mass.
    pooled = np.r_[np.repeat(np.abs(fresh), 3), np.abs(stale).ravel()]
    q90 = float(np.quantile(pooled, .9, method="inverted_cdf"))
    maximum = float(np.max(np.abs(fresh)))
    levels, _ = E.rate_levels(E.T.make_model(spec), training)
    s = float(levels["i"][1]-levels["i"][0])
    if min(q90, maximum) <= 0 or s == 0:
        raise ValueError("undefined fixed gap-scale predictor")
    seed = 3000001 if sub == "e4" else 5000001
    scale = dict(dataset="GEANT", regime=spec["id"], seed=str(seed), family="GEANT",
                 M_hat=maximum, Q90=q90, s_hat=s, T_int_s=training["T_int"],
                 h_star_s=q90/abs(s), h_star_Tint=q90/abs(s)/training["T_int"],
                 horizon=h_max, gap_units="Mb*s", rate_units="Mb",
                 source=f"results/letter/{sub}/raw/{spec['id']}_chunk00..09.npz (seeds/decisions; M0 costs reconstructed)",
                 max_relative_error=max(c["relative_error"] for r in timings for c in r["checks"]))
    return scale


def add_predictors(row, scale):
    row.update(M_hat=scale["M_hat"], Q90=scale["Q90"], s_hat=scale["s_hat"],
               T_int_s=scale["T_int_s"], h_star_s=scale["h_star_s"],
               h_star_Tint=scale["h_star_Tint"], P1=row["h_s"]/scale["T_int_s"],
               P2=row["h_s"]*abs(scale["s_hat"])/scale["Q90"],
               P3=row["h_s"]*abs(scale["s_hat"])/scale["M_hat"])
    return row


def load_cells(scales):
    index = {(r["dataset"], r["regime"], r["seed"]):r for r in scales}
    rows = []
    for path in sorted((ROOT/"results/letter/w1b/raw").glob("*.json")):
        raw = json.loads(path.read_text())
        scale = index["CTMC", raw["id"], "none"]
        for ev in raw["evaluations"]:
            for i, h in enumerate(ev["h"]):
                hybrid = h["hybrid_levels"]["true_s"]
                new, old = hybrid["regret_new"], hybrid["regret_old"]
                row = dict(dataset="CTMC", regime=raw["id"], seed="none", family=raw["family"],
                           age=ev["age_label"], tau_s=ev["tau"], h_s=float(F(h["h"])),
                           regret_fresh_pct=new, regret_stale_pct=old, Y=int(max(new, old) <= .5),
                           C_ref=h["Cref"], source=str(path.relative_to(ROOT)),
                           source_row=f"evaluations[{ev['age_label']}].h[{i}]", raw_flags="|".join(h["flags"]))
                rows.append(add_predictors(row, scale))
    for sub, seed in (("e4", "3000001"), ("e4b", "5000001")):
        path = ROOT/"results/letter"/sub/"cells.csv"
        with path.open() as handle:
            for i, c in enumerate(csv.DictReader(handle)):
                if c["pipeline"] != "Hybrid-i":
                    continue
                scale = index["GEANT", c["regime"], seed]
                new, old = float(c["regret_fresh_pct"]), float(c["regret_stale_pct"])
                row = dict(dataset="GEANT", regime=c["regime"], seed=seed, family="GEANT",
                           age=c["tau_mult"], tau_s=float(c["tau"]), h_s=float(c["h"]),
                           regret_fresh_pct=new, regret_stale_pct=old, Y=int(max(new, old) <= .5),
                           C_ref=float(c["C_ref"]), source=str(path.relative_to(ROOT)),
                           source_row=f"CSV data row {i+1}", raw_flags="")
                rows.append(add_predictors(row, scale))
    if Counter(r["dataset"] for r in rows) != {"CTMC":3255, "GEANT":612}:
        raise ValueError("fixed population is incomplete")
    return rows


def bootstrap_auc(rows, draws=DRAWS, seed=BOOTSTRAP_SEED):
    regimes = sorted({r["regime"] for r in rows})
    groups = {name:np.array([i for i, r in enumerate(rows) if r["regime"] == name]) for name in regimes}
    y = np.array([r["Y"] for r in rows])
    scores = {p:np.array([r[p] for r in rows]) for p in PREDICTORS}
    estimates = {p:auc(y, s) for p,s in scores.items()}
    rng = np.random.default_rng(seed)
    boot = {p:[] for p in PREDICTORS}
    difference = []
    for _ in range(draws):
        selected = rng.integers(0, len(regimes), len(regimes))
        ix = np.concatenate([groups[regimes[j]] for j in selected])
        values = {p:auc(y[ix], s[ix]) for p,s in scores.items()}
        if values["P1"] is None:
            continue
        for p in PREDICTORS:
            boot[p].append(values[p])
        difference.append(values["P2"]-values["P1"])
    interval = lambda x: [float(t) for t in np.quantile(x, [.025, .975])] if x else None
    return dict(regimes=len(regimes), cells=len(rows), Y1=int(y.sum()), Y0=int(len(y)-y.sum()),
                auc={p:dict(value=estimates[p], ci95=interval(boot[p])) for p in PREDICTORS},
                auc_difference_P2_minus_P1=dict(value=estimates["P2"]-estimates["P1"], ci95=interval(difference)),
                bootstrap=dict(seed=seed, draws_requested=draws, draws_valid=len(difference),
                               draws_single_class=draws-len(difference), unit="regime; both GEANT seeds travel together",
                               interval="paired cluster percentile 95%; descriptive post-hoc interval"))


def precision(rows):
    selected = [r for r in rows if r["P2"] >= 1]
    positive = sum(r["Y"] for r in selected)
    return dict(threshold=1, selected=len(selected), true_positive=positive,
                false_positive=len(selected)-positive, value=positive/len(selected) if selected else None)


def onset_rows(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row["dataset"], row["regime"], row["seed"]].append(row)
    result = []
    for (dataset, regime, seed), group in sorted(groups.items()):
        horizons = sorted({r["h_s"] for r in group})
        holds = [all(r["Y"] for r in group if r["h_s"] == h) for h in horizons]
        eligible = [i for i in range(len(horizons)) if all(holds[i:])]
        first = horizons[eligible[0]] if eligible else None
        scale = group[0]
        result.append(dict(dataset=dataset, regime=regime, seed=seed, onset_s=first,
                           censoring="right" if first is None else ("left_at_first_saved" if eligible[0] == 0 else "saved_grid"),
                           last_saved_h_s=horizons[-1], T_int_s=scale["T_int_s"],
                           h_star_s=scale["h_star_s"], h_star_Tint=scale["h_star_Tint"]))
    return result


def correlations(onsets):
    groups = defaultdict(list)
    for row in onsets:
        groups[row["dataset"]+":"+row["seed"]].append(row)
    result = {}
    for label, group in groups.items():
        finite = [r for r in group if r["onset_s"] is not None]
        correlations_ = {}
        for key in ("T_int_s", "h_star_s"):
            a = [r["onset_s"] for r in finite]
            b = [r[key] for r in finite]
            rho = float(spearmanr(a,b).statistic) if len(a)>1 and len(set(a))>1 and len(set(b))>1 else None
            correlations_[key] = rho
        result[label] = dict(regimes=len(group), evaluable=len(finite),
                             right_censored=sum(r["censoring"] == "right" for r in group),
                             left_at_first_saved=sum(r["censoring"] == "left_at_first_saved" for r in group),
                             spearman=correlations_, definition="first saved h with Y=1 at every age and every later h; right-censored excluded, retained in table")
    return result


def binned_figure(out, rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    # Fixed, shared logarithmic bins; all cells retained, including under/overflow.
    edges = np.array([0, .1, .25, .5, 1, 2, 4, 8, 16, 32, 64, math.inf])
    bins = []
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.25), sharey=True, layout="constrained")
    for axis, predictor in zip(axes, ("P1", "P2")):
        for dataset, marker in (("CTMC", "o"), ("GEANT", "s")):
            group = [r for r in rows if r["dataset"] == dataset]
            x, y = [], []
            for lo, hi in zip(edges[:-1], edges[1:]):
                cell = [r for r in group if lo <= r[predictor] < hi]
                if not cell:
                    continue
                location = float(np.median([r[predictor] for r in cell]))
                share = sum(r["Y"] for r in cell)/len(cell)
                bins.append(dict(dataset=dataset, predictor=predictor, lower=float(lo),
                                 upper=float(hi) if math.isfinite(hi) else "inf", cells=len(cell),
                                 Y1=sum(r["Y"] for r in cell), predictor_median=location, Y1_share=share))
                x.append(location); y.append(share)
            axis.plot(x, y, marker=marker, ms=4, label=dataset)
        axis.set_xscale("log")
        axis.set_ylim(-.03, 1.03)
        axis.set_xlabel(r"$h/T_{\rm int}$" if predictor == "P1" else r"$h|\hat{s}|/Q_{90}$")
        axis.grid(alpha=.2)
        axis.axvline(1, lw=.6, color="gray", ls="--")
        axis.legend(frameon=False)
    axes[0].set_ylabel(r"Share with both-side regret $\leq 0.5\%$ of $C_{\rm ref}$")
    fig.suptitle("V7-1 candidate — post-hoc, correlated cells", fontsize=10)
    fig.savefig(out/"fig_rule.pdf")
    fig.savefig(out/"fig_rule.png", dpi=180)
    plt.close(fig)
    write_csv(out/"figure_bins.csv", bins)


def summarize(out, rows, scales, compute):
    datasets = {}
    for name in ("CTMC", "GEANT"):
        group = [r for r in rows if r["dataset"] == name]
        stats = bootstrap_auc(group)
        stats["precision_P2_ge_1"] = precision(group)
        stats["test"] = "HOLDS" if stats["auc"]["P2"]["value"] > stats["auc"]["P1"]["value"] else "DOES_NOT_HOLD"
        p1, p2, p3 = (stats["auc"][p]["value"] for p in PREDICTORS)
        stats["forecast_P3_between"] = dict(holds=min(p1,p2) <= p3 <= max(p1,p2), inclusive=True)
        ss = [s for s in scales if s["dataset"] == name]
        stats["h_star_range_s"] = [min(s["h_star_s"] for s in ss), max(s["h_star_s"] for s in ss)]
        stats["h_star_range_Tint"] = [min(s["h_star_Tint"] for s in ss), max(s["h_star_Tint"] for s in ss)]
        stats["failed_Y_by_regime"] = dict(sorted(Counter(r["regime"] for r in group if not r["Y"]).items()))
        datasets[name] = stats
    onsets = onset_rows(rows)
    write_csv(out/"regime_onsets.csv", onsets)
    per_seed = {}
    for seed in ("3000001", "5000001"):
        group = [r for r in rows if r["seed"] == seed]
        per_seed[seed] = dict(cells=len(group), Y1=sum(r["Y"] for r in group),
                              auc={p:auc([r["Y"] for r in group], [r[p] for r in group]) for p in PREDICTORS},
                              precision_P2_ge_1=precision(group))
    precision_ = datasets["GEANT"]["precision_P2_ge_1"]["value"]
    return dict(owner="Doan Van Tai", status="COMPLETE", analysis="post-hoc with a prewritten fixed card",
                verdict="HOLDS" if all(d["test"] == "HOLDS" for d in datasets.values()) else "DOES_NOT_HOLD",
                datasets=datasets, geant_by_seed=per_seed, regime_level=correlations(onsets),
                forecast_geant_precision_at_least_0p9=dict(value=precision_, holds=precision_ is not None and precision_ >= .9),
                outcome="max(regret_fresh_pct, regret_stale_pct) <= 0.5; signed saved percentages of C_ref; no SE allowance",
                auc_orientation="larger predictor predicts Y=1; Mann-Whitney with exact ties counting 1/2",
                quantile="generalized inverse CDF (inverted_cdf); equal fresh/stale mass and equal saved ages on each side",
                compute=compute, deviations=["M0 fluid gaps absent from E4/E4b NPZ: reconstructed from exact original instance/posterior seeds; V is never used as fluid cost.",
                                             "v7_1_rescore.py is created as explicitly required by brief item 6, although omitted from the initial new-file list."],
                limitations=["Post-hoc finite-panel analysis; cluster CIs do not create a fresh confirmation experiment.",
                             "CTMC is truncated; GEANT maximum is empirical over 500 fresh instances per regime and seed.",
                             "GEANT uses the largest saved horizon (30 T_int), not a proved saturation time.",
                             "Seconds use the existing simulator time convention (GEANT fast switching rate 1/s); this is not a measured operational timescale.",
                             "Regime-onset correlations use the saved horizon grid; right-censored onsets are reported, never imputed."])


def report(out, summary, scales):
    lines = ["# V7-1 — gap-scale rule (post-hoc)", "", "Người phụ trách: **Doan Van Tai**.", "",
             f"Verdict card: **{summary['verdict']}**. Tiêu chí là AUC(P2)>AUC(P1) ở cả hai dataset; CI là mô tả, không thay tiêu chí.", "",
             "| Dataset | Cells / Y=1 | AUC P1 (95% CI) | AUC P2 (95% CI) | AUC P3 (95% CI) | P2−P1 (95% CI) |",
             "|---|---:|---:|---:|---:|---:|"]
    fmt = lambda d: f"{d['value']:.9f} [{d['ci95'][0]:.9f}, {d['ci95'][1]:.9f}]"
    for name, d in summary["datasets"].items():
        lines.append(f"| {name} | {d['cells']} / {d['Y1']} | {fmt(d['auc']['P1'])} | {fmt(d['auc']['P2'])} | {fmt(d['auc']['P3'])} | {fmt(d['auc_difference_P2_minus_P1'])} |")
    lines += ["", "Nguồn mọi AUC/CI: `cells.csv` (P1/P2/P3/Y); `summary.json.datasets`. Bootstrap paired theo regime, 2.000 draws, seed 20261118; hai seed GÉANT được lấy cùng nhau. Không bootstrap các cell như trial độc lập.", "",
              "## Extraction, arrays và đơn vị", "",
              "- CTMC: `results/letter/w1b/raw/*.json`, 93 regimes × 5 ages × 7 saved horizons = 3.255 cells, level `true_s`. Dùng `ctmc.m0_gap(..., h=inf)` cho `gap_A`, `gap_B`, chưa có h·s; hai finite-horizon certified shifts triệt tiêu trong tổng network gap. `pi_A`, `pi_B` là stationary Stay laws. `old_A_*`, `old_B_*` là `exp(Q_Stay*tau)` nhân gap, full old (backlog,mode), dùng `posterior_full` ở các chênh tuổi tăng dần. Joint stationary law của hai queue là tích hai pi; conditional expectation được lấy trước absolute value. M̂ xét **mọi** truncated states. Q90 của |gap_A+gap_B| dùng mass fresh 1/2, mỗi stale age 1/10. Units gap=packet·s, s=packet (backlog-cost rate), h/T_int/h*=s.",
              "- GÉANT: kiểm đủ 340 NPZ + metadata ở `results/letter/e4/raw/` và `e4b/raw/`, seeds 3000001/5000001. NPZ chỉ có `V[instance,action,h]` là plant MC cost, `decisions[instance,pipeline,side,tau,h]`, `tie_flags` và grids/IDs; **không có per-instance M0 fluid costs/gaps**. Không thay `V` vào Δ̂. Tái tạo `instances`, posterior K=128 theo đúng E4 per-instance seeds, gọi `twin_costs` và mean cost như E4. `fresh_gap[n,h]=fresh_cost[:,Switch,:]-fresh_cost[:,Stay,:]`; `stale_gap[n,tau,h]=mean_posterior_cost_Switch-mean_posterior_cost_Stay`. Lưu dưới `extracted/GEANT_*.npz`. M̂=max |fresh_gap[:,-1]|; Q90 pool fresh 3 lần và 3 stale ages một lần (equal sides/ages), N=500/seed/regime. Dùng largest saved horizon h=30T_int theo card fallback, không tuyên bố đã saturation. Training s=`r_a[1].mean-r_a[0].mean` (level i), T_int/dt từ `results/ext_validity/ev_te/train/*.json`. Units gap=Mb·s, s=Mb, time=s theo simulator fast rate 1/s; không phải đo calibration thực tế.",
              "- `extraction_checks.json`: mọi r/T_int/variance/s/F_new/F_old tính lại ở CTMC phải khớp saved với relative error≤1e−9 (zero đòi đúng zero). GÉANT đối chiếu bitwise M0 và Hybrid-i decisions + tie flags ở mọi age/horizon, cả hai phía; nguồn NPZ SHA được kiểm trước khi đọc. Gap scales là đại lượng mới nên không có saved gap scalar để đối chiếu trực tiếp; không tuyên bố scalar-gap replay khi raw không chứa nó.",
              "- Quantile là inverse empirical/weighted CDF (`inverted_cdf`), dùng thống nhất hai dataset; không nội suy probability giữa atom. Scales và per-regime h* ở `regime_scales.csv`, mỗi số có source column; mỗi cell có source + source_row.", "",
              "## Forecasts và h*", ""]
    for name, d in summary["datasets"].items():
        p = d["precision_P2_ge_1"]
        lines += [f"- {name}: forecast AUC(P3) nằm giữa P1/P2: **{d['forecast_P3_between']['holds']}**. Precision P2≥1 = {p['true_positive']}/{p['selected']} = {p['value']:.9f}; false positives={p['false_positive']}.",
                  f"- {name}: h*=Q90/|s| ∈ [{d['h_star_range_s'][0]:.9g}, {d['h_star_range_s'][1]:.9g}] s, tương đương [{d['h_star_range_Tint'][0]:.9g}, {d['h_star_range_Tint'][1]:.9g}] T_int. Nguồn: toàn bộ rows cùng dataset trong `regime_scales.csv`."]
    lines += [f"- Forecast precision≥0,9 trên GÉANT: **{summary['forecast_geant_precision_at_least_0p9']['holds']}**.", "",
              "Nguồn forecast và per-seed counts/AUC: `summary.json.forecast_*`, `summary.json.geant_by_seed` (cùng cell table, không thí nghiệm mới).", "",
              "## Regime-level Spearman", "",
              "Onset là saved h đầu tiên mà mọi age có Y=1 ở h đó và mọi h sau. Mỗi GÉANT seed báo riêng để không coi hai seed của cùng regime là hai regime độc lập. Không có onset được ghi right-censored, không điền horizon kế tiếp.", "",
              "| Dataset:seed | Evaluable / regimes | Right-censored | Left at first h | rho(onset,T_int) | rho(onset,h*) |",
              "|---|---:|---:|---:|---:|---:|"]
    for label, d in summary["regime_level"].items():
        lines.append(f"| {label} | {d['evaluable']}/{d['regimes']} | {d['right_censored']} | {d['left_at_first_saved']} | {d['spearman']['T_int_s']} | {d['spearman']['h_star_s']} |")
    lines += ["", "Nguồn: `regime_onsets.csv`; không có p-value/population claim từ panel này.", "",
              "## Phân tích nguyên nhân và giới hạn", "",
              "Cả ba predictor đều tuyến tính theo h trong mỗi regime: chênh AUC chỉ do thứ tự giữa regimes, không do thêm thông tin truth theo horizon. Dùng gap/s để dự báo regret/C_ref còn thiếu độ lớn denominator C_ref, information loss của stale state và sai số rate/truncated/finite-sample. Một gap thường gặp nhỏ không chứng minh regret chuẩn hóa nhỏ; M̂ từ đuôi mọi truncated state còn có thể rất lớn dù stationary mass ở đuôi nhỏ.",
              "`summary.json.datasets.*.failed_Y_by_regime` giữ đủ các regime gây failure; không loại near-empty regimes hay tune quantile/cutoff để cứu card. Kiểm tra cùng saved dữ liệu bằng P3 là alternative đã khai trong card, không thêm predictor sau outcome. `subgroups.csv` báo từng CTMC family và từng GÉANT seed, kể cả nhóm kết quả không thuận. Không khởi động simulation mới để cải thiện verdict.", ""]
    if summary["verdict"] == "HOLDS":
        lines.append("Inclusion rule: đủ điều kiện đề xuất Table II theo h|s|/Q90. Figure hiện tại chỉ candidate; chưa sửa paper.")
    else:
        lines.append("Inclusion rule: Table II giữ theo T_int; phải nói rõ gap/s không cải thiện dự báo trên cả hai dataset được xét. Không sửa paper trong brief này.")
    lines += ["", "## Compute và kiểm chứng", "", f"Compute (source `summary.json.compute`): `{json.dumps(summary['compute'], ensure_ascii=False)}`.",
              "Pilot gồm regime CTMC lớn nhất và E4/E4b chunk có saved CPU lớn nhất; `pilot.json` ghi projection trước full extraction. Pilot được reuse nguyên artifact. `input_manifest.json` ghi SHA256 code/card/brief và mọi input đã đọc; xác minh lại sau run. Independent rescore ở `experiments/letter/v7_1_rescore.py`, không import scorer, đọc per-cell table và phải khớp mọi AUC≤1e−12; kết quả riêng `rescore.json`.", "",
              "## Deviations", "", *["- "+s for s in summary["deviations"]], "",
              "Không commit, không SSH, không sửa card/file cũ/paper, không chạm V7-2/V7-3. Các test/log thực thi được ghi riêng trong thư mục này."]
    with (out/"REPORT_V7_1.md").open("x") as handle:
        handle.write("\n".join(lines)+"\n")


def input_paths():
    paths = [Path(__file__), Path(__file__).with_name("v7_1_rescore.py"),
             ROOT/"tests/test_letter_v7_1.py", ROOT/"notes/ops/codex/V7_1_brief.md",
             OUT/"CARD_V7_1.md", Path(ctmc.__file__), Path(E.__file__),
             Path(__file__).with_name("e3_agediff.py"), Path(E.T.__file__),
             Path(__file__).with_name("e4_rhat.py"), E.EV/"regimes.json", E.EV/"score.json"]
    paths += sorted((ROOT/"results/letter/w1b/raw").glob("*.json"))
    specs, _ = geant_inputs()
    paths += [E.EV/"train"/f"{s['id']}.json" for s in specs]
    for sub in ("e4", "e4b"):
        paths += [ROOT/"results/letter"/sub/"cells.csv"]
        paths += sorted((ROOT/"results/letter"/sub/"raw").glob("*"))
    return paths


def run(out=OUT, compute_location="local"):
    pilot_record = json.loads((out/"pilot.json").read_text())
    if compute_location not in ("local", "gcp"):
        raise ValueError("unknown compute location")
    if pilot_record["status"] != "GO" and compute_location == "local":
        raise RuntimeError("pilot projection exceeds 20 minutes: stop for Claude/GCP")
    if (out/"summary.json").exists() or (out/"input_manifest.json").exists():
        raise FileExistsError("analysis already started; no automatic rerun")
    start, wall = time.process_time(), time.perf_counter()
    paths = input_paths()
    manifest = {str(p.relative_to(ROOT)):sha(p) for p in paths}
    write_json(out/"input_manifest.json", dict(owner="Doan Van Tai", sha256=manifest,
                                              git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()))
    scales = []
    for path in sorted((ROOT/"results/letter/w1b/raw").glob("*.json")):
        raw = json.loads(path.read_text())
        prefix = "CTMC_"+raw["id"]
        record = read_extraction(out, prefix)
        if record is None:
            record, arrays = extract_ctmc(raw)
            save_extraction(out, prefix, record, arrays)
        scales.append(record["scale"])
        print(json.dumps(dict(event="scale", dataset="CTMC", regime=raw["id"], cpu_s=record["cpu_s"])), flush=True)
        if compute_location == "local" and time.perf_counter()-wall+pilot_record["wall_s"] > LOCAL_CAP_S:
            raise RuntimeError("local 20-minute extraction budget reached; retain partial artifacts for GCP")
    specs, training = geant_inputs()
    for sub in ("e4", "e4b"):
        for spec in specs:
            scales.append(geant_scale(out, spec, training[spec["id"]], sub))
            print(json.dumps(dict(event="scale", dataset="GEANT", sub=sub, regime=spec["id"])), flush=True)
            if compute_location == "local" and time.perf_counter()-wall+pilot_record["wall_s"] > LOCAL_CAP_S:
                raise RuntimeError("local 20-minute extraction budget reached; retain partial artifacts for GCP")
    rows = load_cells(scales)
    write_csv(out/"regime_scales.csv", scales)
    write_csv(out/"cells.csv", rows)
    extracted = [json.loads(p.read_text()) for p in sorted((out/"extracted").glob("*.json"))]
    checks = dict(ctmc_relative_checks=[dict(regime=e["scale"]["regime"], **c) for e in extracted if "scale" in e for c in e["checks"]],
                  geant_chunks=[e for e in extracted if "scale" not in e],
                  ctmc_regimes=sum("scale" in e for e in extracted),
                  geant_chunk_count=sum("scale" not in e for e in extracted))
    write_json(out/"extraction_checks.json", checks)
    compute = dict(extraction_cpu_s=sum(e["cpu_s"] for e in extracted),
                   extraction_wall_sum_s=sum(e["wall_s"] for e in extracted),
                   analysis_process_cpu_s_before_bootstrap=time.process_time()-start,
                   compute_location=compute_location, local_cap_s=LOCAL_CAP_S,
                   pilot_projected_total_wall_s=pilot_record["projected_total_local_wall_s"])
    summary = summarize(out, rows, scales, compute)
    subgroups = []
    for dataset, factor, values in (("CTMC", "family", sorted({r["family"] for r in rows if r["dataset"] == "CTMC"})),
                                     ("GEANT", "seed", ["3000001", "5000001"])):
        for value in values:
            group = [r for r in rows if r["dataset"] == dataset and r[factor] == value]
            subgroups.append(dict(dataset=dataset, factor=factor, value=value, cells=len(group),
                                  Y1=sum(r["Y"] for r in group),
                                  **{f"auc_{p}":auc([r["Y"] for r in group], [r[p] for r in group]) for p in PREDICTORS}))
    write_csv(out/"subgroups.csv", subgroups)
    binned_figure(out, rows)
    changed = [name for name, digest in manifest.items() if sha(ROOT/name) != digest]
    if changed:
        raise RuntimeError(f"input changed during analysis: {changed}")
    summary["input_hash_verification"] = dict(files=len(manifest), changed=changed, status="PASS")
    compute["main_cpu_s_including_score_and_figures"] = time.process_time()-start
    compute["main_wall_s_including_score_and_figures"] = time.perf_counter()-wall
    compute["total_local_wall_s_including_pilot"] = time.perf_counter()-wall+pilot_record["wall_s"]
    write_json(out/"summary.json", summary)
    report(out, summary, scales)
    print(json.dumps(dict(status=summary["status"], verdict=summary["verdict"], compute=compute)), flush=True)


def report_pilot(out=OUT):
    """Report the mandated resource stop without scoring a convenient subset."""
    record = json.loads((out/"pilot.json").read_text())
    if record["status"] != "STOP_FOR_GCP":
        raise ValueError("resource-stop report requires a STOP_FOR_GCP pilot")
    brief = ROOT/"notes/ops/codex/V7_1_brief.md"
    card = OUT/"CARD_V7_1.md"
    for p in (brief,card):
        committed = subprocess.check_output(["git", "show", "HEAD:"+str(p.relative_to(ROOT))], cwd=ROOT)
        if committed != p.read_bytes():
            raise RuntimeError("brief/card differs from HEAD")
    metadata = [json.loads(p.read_text()) for sub in ("e4", "e4b")
                for p in (ROOT/"results/letter"/sub/"raw").glob("*.json")]
    source_meta = json.loads((ROOT/record["geant"]["source"]).with_suffix(".json").read_text())
    # Secondary scheduling estimate only, never an outcome/model criterion.
    cpu_ratio = sum(m["CPU"] for m in metadata)/source_meta["CPU"]
    secondary = (record["ctmc"]["wall_s"]*record["ctmc_work_factor"]
                 + record["geant"]["wall_s"]*cpu_ratio)
    ctmc_scale = dict(record["ctmc"]["scale"], scope="PILOT_ONLY_1_OF_93_REGIMES")
    write_csv(out/"regime_scales.csv", [ctmc_scale])
    checks = dict(ctmc=record["ctmc"]["checks"],
                  ctmc_max_relative_error=ctmc_scale["max_relative_error"],
                  geant=record["geant"], status="PILOT_CHECKS_PASS_NOT_FULL_ANALYSIS")
    write_json(out/"extraction_checks.json", checks)
    manifest = {str(p.relative_to(ROOT)):sha(p) for p in input_paths()}
    write_json(out/"input_manifest.json", dict(owner="Doan Van Tai", sha256=manifest,
                                              scope="snapshot after pilot, before any full-population score; not a pre-pilot lock",
                                              git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()))
    summary = dict(owner="Doan Van Tai", status="PILOT_ONLY_STOP_FOR_GCP", verdict="NOT_EVALUABLE",
                   reason="projected local compute exceeds the brief's fixed 1200-second cap; stop after pilot",
                   datasets={name:dict(expected_regimes=nreg, expected_cells=ncell, scored_cells=0,
                                       auc={p:dict(value=None, ci95=None) for p in PREDICTORS},
                                       auc_difference_P2_minus_P1=dict(value=None, ci95=None),
                                       precision_P2_ge_1=None, regime_spearman=None, h_star_range_s=None,
                                       h_star_range_Tint=None, test="NOT_EVALUABLE")
                             for name,nreg,ncell in (("CTMC",93,3255),("GEANT",17,612))},
                   forecasts=dict(P3_between="NOT_EVALUABLE", geant_precision_at_least_0p9="NOT_EVALUABLE"),
                   pilot_ctmc_scale=ctmc_scale,
                   pilot_coverage=dict(ctmc_regimes=1, ctmc_total=93, geant_chunks=1,
                                       geant_total=340, geant_fresh_instances=50, geant_required_per_regime_seed=500),
                   compute=dict(pilot_cpu_s=record["cpu_s"], pilot_wall_s=record["wall_s"],
                                projected_conservative_wall_s=record["projected_total_local_wall_s"],
                                projected_secondary_saved_CPU_scaled_wall_s=secondary,
                                secondary_saved_CPU_ratio=cpu_ratio, local_cap_s=LOCAL_CAP_S,
                                secondary_projection="original E4/E4b saved full-job CPU ratios, calibrated to the measured heaviest M0-only chunk; approximate, not a CI or guarantee"),
                   bootstrap_plan=dict(draws=DRAWS, seed=BOOTSTRAP_SEED, unit="regime with GEANT seeds together", status="NOT_RUN"),
                   rescore=dict(status="NOT_RUN", reason="no full per-cell table; no AUC generated to compare"),
                   figure=dict(status="NOT_CREATED", reason="full-population P1/P2/Y bins unavailable; do not plot a selected pilot as the card population"),
                   input_hash_verification=dict(files=len(manifest), status="PASS",
                                                changed=[name for name,digest in manifest.items() if sha(ROOT/name) != digest]),
                   deviations=["E4/E4b raw has plant V/decisions/tie_flags, not M0 gaps; reconstructing the original predictor inputs is required and was piloted.",
                               "Created experiments/letter/v7_1_rescore.py as expressly required in item 6 despite its omission from the initial new-file list.",
                               "Stopped after pilot as required by the compute rule; full AUC/CI, precision, Spearman, h* ranges, figure and independent data rescore remain unrun."],
                   inclusion="Card not evaluable: no authorization to replace Table II; paper unchanged.")
    if summary["input_hash_verification"]["changed"]:
        raise RuntimeError("input changed during pilot report")
    write_json(out/"summary.json", summary)
    text = f"""# V7-1 — resource-stop pilot report

Người phụ trách: **Doan Van Tai**.

Verdict card: **NOT_EVALUABLE**. Chưa kiểm định dự đoán AUC(P2)>AUC(P1) trên cả hai dataset; không gán FAIL cho hypothesis từ một compute stop. Giữ nguyên card tại HEAD, threshold và inclusion rule; chưa sửa Table II/paper.

## Đã triển khai và chạy

Đã tạo `experiments/letter/v7_1_rule.py`, `experiments/letter/v7_1_rescore.py`, `tests/test_letter_v7_1.py`. Có code extraction, P1–P3/Y, AUC Mann–Whitney (ties=1/2), cluster-bootstrap 2.000 draws/seed 20261118, precision, per-regime onset Spearman, h*, candidate figure và rescore độc lập dùng standard-library bisect. **Full analysis chưa chạy**; triển khai không đồng nghĩa kết quả khoa học đã được xác nhận.

Command đã chạy:

```bash
source .venv/bin/activate && source experiments/explore_ctmc/env.sh
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider tests/test_letter_v7_1.py --basetemp=/tmp/v7_1_pytest_preflight
PYTHONDONTWRITEBYTECODE=1 python -u -m experiments.letter.v7_1_rule pilot
PYTHONDONTWRITEBYTECODE=1 python -m experiments.letter.v7_1_rule report-pilot
```

Preflight: 12 tests PASS, 2.58 s (`pytest_preflight.log`). Kiểm tra cuối sau bổ sung resource-stop guards được ghi riêng ở `pytest_final.log`; không dùng log này để suy full analysis PASS.

## Compute và lý do dừng

- CTMC pilot: regime lớn nhất `{ctmc_scale['regime']}` (N_A=3159, N_B=9518), đủ 5 saved ages; CPU {record['ctmc']['cpu_s']:.9f} s, wall {record['ctmc']['wall_s']:.9f} s.
- GÉANT pilot: `{record['geant']['source']}`, seed {record['geant']['seed']}, chunk {record['geant']['chunk']}, N=50/K=128, đủ 3 ages × 6 horizons. Đây là chunk có saved CPU lớn nhất trong 340 chunks. CPU {record['geant']['cpu_s']:.9f} s, wall {record['geant']['wall_s']:.9f} s.
- Pilot tổng: **{record['cpu_s']:.9f} CPU-s / {record['wall_s']:.9f} wall-s** ({record['wall_s']/60:.6f} phút), nguồn `pilot.json`.
- Projection bảo thủ = CTMC pilot wall × sparse-generator work ratio {record['ctmc_work_factor']:.9f} + GÉANT worst-chunk wall × 340 = **{record['projected_total_local_wall_s']:.6f} s ({record['projected_total_local_wall_s']/60:.6f} phút)**. Đây là bound scheduling bảo thủ, không actual full-run duration.
- Cross-check scheduling dùng tỷ số CPU full-job đã lưu của toàn bộ chunks / chunk pilot = {cpu_ratio:.9f}, nhân M0-only chunk wall thực đo: **{secondary:.6f} s ({secondary/60:.6f} phút)** cho toàn bộ, vẫn vượt **1.200 s / 20 phút**. Ước lượng này không CI hoặc guarantee. Nguồn metadata `results/letter/e4/raw/*.json`, `e4b/raw/*.json`; script và các số trong `summary.json.compute`.

Theo brief: dừng sau pilot để Claude chuyển GCP. Không chạy phần population còn lại, không SSH, không commit.

## Arrays, nguồn và đơn vị

**CTMC:** `results/letter/w1b/raw/*.json` có regrets và saturation decision probabilities, không có gap arrays. Tái tạo `ctmc.m0_gap(...,[inf])` trên đúng truncated state spaces. Artifact `extracted/CTMC_{ctmc_scale['regime']}.npz`: `gap_A`, `gap_B` (uncorrected Switch−Stay network gap là tổng hai thành phần), `pi_A`, `pi_B`; `old_A_<age>`, `old_B_<age>` là conditional expectation full old (backlog,mode), dùng `posterior_full=exp(Q_Stay*tau)` ở chênh tuổi tăng dần. Joint law của hai queue là tích hai pi. Absolute value được lấy **sau** conditional expectation. M̂ xét mọi truncated states; Q90=weighted inverse CDF của |gap_A+gap_B|, mass fresh=1/2, mỗi stale age=1/10. Fresh lặp theo age và pooling hai sides có cùng weighting. Gap units packet·s, s units packet/backlog-cost rate; h/T_int/h* tính bằng giây của simulator. Không gọi CTMC truncated là infinite-state exact.

**GÉANT:** NPZ E4/E4b lưu `V[50,2,6]` (plant Monte Carlo cost), `decisions[50,20,2,3,6]`, `tie_flags`, `h`, `tau`, grids và instance IDs; **V không phải M0 fluid gap**. Tái tạo đúng E4 `instances`, per-instance/posterior seeds, K=128, gọi `twin_costs`, mean posterior cost rồi trừ Switch−Stay; không gọi M1 decision/evaluation truth. Artifact `extracted/GEANT_e4_{record['geant']['regime']}_{record['geant']['chunk']:02d}.npz`: `fresh_gap[50,6]`, `stale_gap[50,3,6]`, `h`, `tau`, `instance_id`. Chưa đủ 10 chunks/500 fresh instances để tính **regime** M̂/Q90. Full-analysis code sẽ dùng largest saved h=30T_int, empirical max fresh, Q90 pool fresh ba lần và stale ba ages một lần (equal side mass; inverse CDF, không linear interpolation). ŝ=training `r_a[1].mean-r_a[0].mean`, T_int/dt từ `results/ext_validity/ev_te/train/*.json`; units gap=Mb·s, ŝ=Mb. Seconds dùng convention fast switching rate 1/s, không phải calibration theo deployment thật.

Pilot replay: **20/20 CTMC scalar comparisons PASS**, max relative error **{ctmc_scale['max_relative_error']:.12g}**, threshold ≤1e−9. Các scalar kiểm r/T_int/variance của bốn chains, s/T_int toàn regime, fresh F_new và năm stale F_old (nguồn `evaluations[*].asymptotic` trong W1b raw). Gap scale mới không có saved scalar để so trực tiếp; không tuyên bố đã có raw scalar-gap replay. GÉANT: **{record['geant']['exact_decisions_checked']:,} decisions + {record['geant']['exact_tie_flags_checked']:,} tie flags khớp bitwise**, M0 và Hybrid-i, fresh/stale, mọi age/horizon; grids/instance IDs cũng khớp, NPZ SHA khớp metadata. Xem `extraction_checks.json`, JSON/NPZ trong `extracted/` và test gap extraction trên một regime cũ khác.

## Kết quả hiện có và chưa có

| Đại lượng | CTMC pilot duy nhất | Population đầy đủ |
|---|---:|---|
| M̂ (packet·s) | {ctmc_scale['M_hat']:.12g} | Chưa tính |
| Q90 (packet·s) | {ctmc_scale['Q90']:.12g} | Chưa tính |
| s (packet) | {ctmc_scale['s_hat']:.12g} | Chưa tổng hợp |
| T_int (s) | {ctmc_scale['T_int_s']:.12g} | Chưa tổng hợp |
| h*=Q90/|s| (s) | **{ctmc_scale['h_star_s']:.12g}** | **Range chưa xác định** |
| h*/T_int | **{ctmc_scale['h_star_Tint']:.12g}** | **Range chưa xác định** |
| AUC P1/P2/P3, CIs và P2−P1 | Không chấm pilot subset | **NOT_RUN** |
| Precision P2≥1 / regime Spearman | Không chấm pilot subset | **NOT_RUN** |

Nguồn toàn bộ số scale: `extracted/CTMC_{ctmc_scale['regime']}.json:scale`, `regime_scales.csv` (scope `PILOT_ONLY_1_OF_93_REGIMES`). Không xem đây là h* range của 93 regimes hoặc 2-seed GÉANT. `summary.json` để null cho metrics chưa đo, không điền 0.

Forecast AUC(P3) nằm giữa P1/P2 và precision≥0,9 trên GÉANT: **NOT_EVALUABLE**. Không tạo `cells.csv`, `regime_onsets.csv`, `fig_rule.pdf/png`, `figure_bins.csv` hoặc `rescore.json` vì chưa có full-population scale table; không tạo figure từ một pilot rồi trình bày như population card. Rescore script đã có và toy AUC đã kiểm; **independent rescore trên dataset chưa chạy**. Bootstrap giữ regime block, hai GÉANT seeds đi cùng; Spearman dự kiến báo từng seed, onset cần mọi age và mọi saved h sau đều pass, giữ right-censoring.

## Nguyên nhân, giới hạn và handoff

Compute bottleneck là phải tái tạo posterior M0 predictor do fluid gaps không được lưu, cộng sparse semigroup ở CTMC state space lớn. Dùng V của plant thay gap hoặc bỏ regimes/ages/horizons sẽ đổi đại lượng và population, nên không làm. Đã dùng cách nhẹ: chỉ tính gap vector (không truth V), tiến dần giữa CTMC ages, batch fresh fluid costs, và reuse pilot artifacts. Cross-check scheduling vẫn vượt cap; không tiếp tục local hoặc tune criterion để cứu tính khả thi.

Claude có thể chuyển code, nguyên `pilot.json`/`extracted/`, dữ liệu nguồn và card sang GCP. Full command hỗ trợ `run --compute-location gcp`; dùng **output directory mới** và copy pilot/extracted vào đó để giữ báo cáo pilot này, ví dụ `results/letter/v7_1/full/`. Chạy full analysis, sau đó `python -m experiments.letter.v7_1_rescore --out <full-output>`; phải khớp AUC≤1e−12. Đây là hướng dẫn handoff, **không phải lệnh đã chạy hay yêu cầu bật VM**. Thực hiện trên GCP do Claude phụ trách theo brief.

## Files và deviations

- `summary.json`, `REPORT_V7_1.md`: trạng thái stop, counts, timings, metrics chưa chạy và forecast chưa chấm.
- `pilot.json`, `pilot.log`, `extraction_checks.json`, `regime_scales.csv`, `extracted/*.json/npz`: pilot thật, arrays, replay checks và units/source.
- `input_manifest.json`: SHA256 snapshot sau pilot, trước full score; **không gọi đây là lock trước pilot**. Brief/card đã đối chiếu byte với HEAD. Full code tiếp tục snapshot và verify tất cả inputs quanh analysis.
- Tests/log: `tests/test_letter_v7_1.py`, `pytest_preflight.log`, `pytest_final.log` sau kiểm tra cuối.
- Deviations cần báo: fluid gaps vắng trong E4/E4b raw nên phải tái tạo đúng original predictor inputs; tạo thêm `v7_1_rescore.py` đúng mục 6 dù initial allowlist bỏ sót. Việc dừng sau pilot là nhánh được brief yêu cầu khi vượt 20 phút.

Không sửa file có từ đầu/card/paper, không chạm V7-2/V7-3, không commit, không SSH. Card vẫn là post-hoc finite-panel analysis; không novelty/Understanding/author-self claim.
"""
    with (out/"REPORT_V7_1.md").open("x") as handle:
        handle.write(text)
    print(json.dumps(dict(status=summary["status"], verdict=summary["verdict"],
                          compute=summary["compute"])), flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("pilot", "run", "report-pilot"))
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--compute-location", choices=("local", "gcp"), default="local",
                        help="explicit GCP handoff only; never bypass the local 20-minute cap")
    args = parser.parse_args()
    if args.command == "run":
        run(args.out, compute_location=args.compute_location)
    else:
        {"pilot":pilot, "report-pilot":report_pilot}[args.command](args.out)


if __name__ == "__main__":
    main()
