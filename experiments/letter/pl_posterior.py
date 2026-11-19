"""Doan Van Tai — CARD_PL implementation, finite-history pilot and locked CLI.

The existing CTMC, fluid rollout, full-state posterior and strict pair_sum are
reused unchanged. Uniformization samples the *exact* exp(Q*delta) transition:
Poisson(gamma*delta) embedded jumps, with no time step or Poisson-tail cutoff.
Only pilot uses pilot seeds. No command implicitly invokes truth or scoring.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
import math
import multiprocessing
import os
from pathlib import Path
import resource
import signal
import subprocess
import time

import numpy as np
import scipy

from experiments.explore_ctmc import ctmc
from experiments.letter import e3_agediff as age
from experiments.letter import r2_o1_check as r2

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/letter/pl_posterior"
CARD = OUT / "CARD_PL.md"
EXCLUDED = "Za7p5_u3-2_lA31-4_x1-3_k2"
R2_PILOT = "Za3_u1_lA7_x-1_k1-20"
H_GRID = (1, 3, 10, 30, 100)
AGES = (1, 3)
L_GRID = (30, 100, 300, 1000)
SEEDS = tuple(range(5))
K = 50
CPU_CAP = 4 * 3600
REGIME_CAP_CPU_SECONDS = 3600
WORKERS = 9
ARITH = 1e-9
VARIANTS = ("M0", "hybrid_true_s", "hybrid_mm1")
RECEIPT = OUT / "truth_receipt.json"


def stamp():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_once(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = value if isinstance(value, str) else json.dumps(
        value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8") as stream:
        stream.write(text)


def event(name, **fields):
    print(json.dumps(dict(event=name, **fields), ensure_ascii=False, allow_nan=False), flush=True)


def environment():
    return dict(python=os.sys.version, numpy=np.__version__, scipy=scipy.__version__,
                numeric_env={k: os.environ.get(k) for k in (
                    "NPY_DISABLE_CPU_FEATURES", "OPENBLAS_CORETYPE", "OMP_NUM_THREADS",
                    "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")})


def require_environment():
    env = environment()["numeric_env"]
    if any(env[k] != "1" for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")):
        raise RuntimeError("source experiments/explore_ctmc/env.sh before running")
    if env["OPENBLAS_CORETYPE"] != "Haswell" or not env["NPY_DISABLE_CPU_FEATURES"]:
        raise RuntimeError("required deterministic numeric environment is not active")


def matched_raws():
    paths = sorted((ROOT / "results/letter/w1b/raw").glob("*.json"))
    if len(paths) != 93:
        raise ValueError("expected the unchanged 93-regime W1b universe")
    raws = []
    for path in paths:
        raw = json.loads(path.read_text())
        if raw["id"] != path.stem or raw["status"] != "COMPLETED":
            raise ValueError("invalid W1b raw: " + str(path))
        if raw["id"] != EXCLUDED:
            raws.append(raw)
    if len(raws) != 92:
        raise ValueError("expected exactly 92 matched regimes")
    return raws


def saved_tint(raw):
    return next(e for e in raw["evaluations"] if e["age_label"] == "Tint_1")


def regime_amplitude(raw):
    saved = F(str(saved_tint(raw)["a"]))
    if "a" in raw["case"] and F(raw["case"]["a"]) != saved:
        raise ValueError("W1b amplitude mismatch")
    return saved


def nominal_saved_30(raw):
    row = min(saved_tint(raw)["h"], key=lambda r: abs(r["h_Tint"] - 30))
    if not math.isclose(row["h_Tint"], 30, rel_tol=.01):
        raise ValueError("W1b lacks its nominal 30 T_int coordinate")
    return row


def seed_for(index, age_multiple, replicate, pilot=False):
    if age_multiple not in AGES or replicate not in SEEDS or not 0 <= index < 92:
        raise ValueError("seed coordinate outside CARD_PL")
    return (7490000 if pilot else 7400000) + 1000 * index + 100 * (age_multiple == 3) + replicate


def pilot_selection(raws):
    # Heaviest means max N over the two paths, ties broken by sum N then id.
    heavy = max(raws, key=lambda r: (max(saved_tint(r)["N"].values()),
                                     sum(saved_tint(r)["N"].values()), r["id"]))
    selected = [next(r for r in raws if r["id"] == R2_PILOT), heavy]
    truth_seeds = {seed_for(i, a, s) for i in range(92) for a in AGES for s in SEEDS}
    by_id = {r["id"]: i for i, r in enumerate(raws)}
    pilot_seeds = {seed_for(by_id[r["id"]], a, s, True)
                   for r in selected for a in AGES for s in SEEDS}
    if len({r["id"] for r in selected}) != 2 or pilot_seeds & truth_seeds:
        raise ValueError("pilot selection duplicates a regime or overlaps a truth seed")
    return selected


def finite_prefix_steps(length, delta):
    ratio = float(length) / float(delta)
    nearest = round(ratio)
    return nearest if abs(ratio - nearest) <= 1e-10 * max(1., abs(ratio)) else math.floor(ratio)


def reflect_walk(steps, initial, maximum):
    """Exact blocked +/-1 embedded queue, vectorized between boundary changes."""
    steps = np.asarray(steps, dtype=np.int64)
    if maximum < 1 or not 0 <= initial <= maximum or np.any(abs(steps) > 1):
        raise ValueError("invalid reflected-walk inputs")
    result = np.empty(len(steps), dtype=np.int64)
    pos, orient, start = 0, 1, int(initial)
    while pos < len(steps):
        walk = start + np.cumsum(orient * steps[pos:])
        reflected = walk - np.minimum.accumulate(np.minimum(walk, 0))
        crossing = np.flatnonzero(reflected > maximum)
        size = int(crossing[0]) if crossing.size else len(walk)
        result[pos:pos + size] = reflected[:size] if orient == 1 else maximum - reflected[:size]
        pos += size
        if crossing.size:
            result[pos] = maximum if orient == 1 else 0
            pos += 1
            orient, start = -orient, 0
    return result


def uniformized_events(chain, uniforms, initial_state):
    """Untruncated uniformization of the original generator, not a new plant."""
    gamma = float(chain.load) + float(chain.a) + ctmc.MU + 1 / float(chain.kappa)
    uniforms = np.asarray(uniforms)
    flip = uniforms < (1 / float(chain.kappa)) / gamma
    cumulative = np.cumsum(flip, dtype=np.int64)
    before_mode = (int(initial_state) % 2 + cumulative - flip) % 2
    after_mode = (int(initial_state) % 2 + cumulative) % 2
    loads = float(chain.load) + np.where(before_mode, float(chain.a), -float(chain.a))
    boundary = ((1 / float(chain.kappa)) + loads) / gamma
    steps = np.zeros(len(uniforms), dtype=np.int64)
    steps[(~flip) & (uniforms < boundary)] = 1
    steps[(uniforms >= boundary) & (uniforms < boundary + ctmc.MU / gamma)] = -1
    backlog = reflect_walk(steps, int(initial_state) // 2, chain.N)
    return 2 * backlog + after_mode


def sample_history(chain, delta, steps, rng, chunk_events=200000):
    """Z_0..Z_steps at polling delta, kernel exactly exp(Q*delta).

    Independent Poisson counts in polling intervals and independent embedded
    events give exp(Q delta) = exp(-gamma delta) sum (gamma delta)^j R^j/j!.
    No tail is truncated; self events enforce the original finite-N blocking.
    """
    if delta <= 0 or steps < 10:
        raise ValueError("history must contain at least one lag-10 pair")
    gamma = float(chain.load) + float(chain.a) + ctmc.MU + 1 / float(chain.kappa)
    counts = rng.poisson(gamma * float(delta), int(steps))
    endpoints = np.cumsum(counts, dtype=np.int64)
    total = int(endpoints[-1])
    z = np.empty(steps + 1, dtype=np.int64)
    current = int(rng.choice(chain.n, p=chain.pi))
    z[0] = current
    zeros = int(np.searchsorted(endpoints, 0, side="right"))
    z[1:zeros + 1] = current
    begin, filled = 0, zeros
    while begin < total:
        size = min(chunk_events, total - begin)
        states = uniformized_events(chain, rng.random(size), current)
        end = begin + size
        next_filled = int(np.searchsorted(endpoints, end, side="right"))
        if next_filled > filled:
            z[filled + 1:next_filled + 1] = states[endpoints[filled:next_filled] - begin - 1]
        current, begin, filled = int(states[-1]), end, next_filled
    if filled != steps:
        raise ArithmeticError("polling endpoints not completely filled")
    return z, dict(method="exact_exponential_uniformization_no_tail_cutoff",
                   gamma=gamma, delta=float(delta), polling_steps=int(steps),
                   embedded_events=total, starting_state=int(z[0]), final_state=int(z[-1]))


def knn_posterior(old_states, new_states, values, n_states, k=K):
    """Mode-matched backlog k-NN, including *all* boundary-distance ties.

    Sums/counts are aggregated by old backlog. Missing mode uses all pairs;
    an undersized pool uses every pair in that pool. No current-state query or
    future sample enters the neighbor selection.
    """
    y, x = np.asarray(old_states, dtype=int), np.asarray(new_states, dtype=int)
    v = np.asarray(values, dtype=float)
    v = v[None, :] if v.ndim == 1 else v
    if len(y) != len(x) or not len(y) or n_states % 2 or k < 1 or v.shape[1] != n_states:
        raise ValueError("invalid k-NN inputs")
    if np.any(y < 0) or np.any(y >= n_states) or np.any(x < 0) or np.any(x >= n_states):
        raise ValueError("history contains a state outside this chain")
    levels = n_states // 2
    query = np.arange(levels)
    result = np.empty((len(v), n_states))
    selected = np.empty(n_states, dtype=int)
    missing = []
    for mode in (0, 1):
        mask = y % 2 == mode
        missing_mode = not mask.any()
        if missing_mode:
            mask = np.ones(len(y), dtype=bool)
            missing.append(mode)
        pool_y, pool_x = y[mask] // 2, x[mask]
        if missing_mode or len(pool_y) <= k:
            result[:, mode::2] = v[:, pool_x].mean(axis=1)[:, None]
            selected[mode::2] = len(pool_y)
            continue
        count = np.bincount(pool_y, minlength=levels)
        prefix = np.r_[0, np.cumsum(count)]
        low, high = np.full(levels, -1), np.full(levels, levels - 1)
        while np.any(high - low > 1):
            mid = (low + high) // 2
            left = np.maximum(0, query - mid)
            right = np.minimum(levels - 1, query + mid)
            enough = prefix[right + 1] - prefix[left] >= k
            high = np.where(enough, mid, high)
            low = np.where(enough, low, mid)
        left, right = np.maximum(0, query - high), np.minimum(levels - 1, query + high)
        denom = prefix[right + 1] - prefix[left]
        selected[mode::2] = denom
        for j in range(len(v)):
            sums = np.bincount(pool_y, weights=v[j, pool_x], minlength=levels)
            accum = np.r_[0., np.cumsum(sums)]
            result[j, mode::2] = (accum[right + 1] - accum[left]) / denom
    return result, dict(missing_modes=missing, pairs=len(y), k=k,
                        min_selected=int(selected.min()), max_selected=int(selected.max()))


def pair(chains, ua, va, ub, vb):
    return ctmc.pair_sum(chains["Ast"].pi, ua, va, chains["Bst"].pi, ub, vb, 0.)


def policy_metrics(chains, fresh_a, fresh_b, old_a, old_b, gap_a, gap_b,
                   true_old_a, true_old_b, h, r_stay, s):
    """Separated-path G_S; the evaluation posterior is always the true one."""
    oracle = pair(chains, gap_a, gap_a, gap_b, gap_b)[1]
    cref = float(h) * r_stay + oracle
    if not cref > 0:
        raise ArithmeticError("nonpositive C_ref")
    fn, vn, tn = pair(chains, fresh_a, gap_a, fresh_b, gap_b)
    fo, vo, to = pair(chains, old_a, true_old_a, old_b, true_old_b)
    pct = lambda cost: 100 * cost / cref
    rn, ro = pct(vn - oracle), pct(vo - oracle)
    return dict(G_S_packet_s=vo - vn, G_S_pct_C_ref=pct(vo - vn), C_ref=cref,
                regret_new_pct_C_ref=rn, regret_old_pct_C_ref=ro,
                both_side_regret_pct_C_ref=max(rn, ro),
                excess_cost_new_packet_s=vn - oracle, excess_cost_old_packet_s=vo - oracle,
                share_switch_new=fn, share_switch_old=fo,
                share_long_run_action_new=fn if s < 0 else 1 - fn,
                share_long_run_action_old=fo if s < 0 else 1 - fo,
                long_run_action="Switch" if s < 0 else "Stay", tie_mass_new=tn, tie_mass_old=to)


def control_comparison(metrics, saved):
    expected = saved["G_S"] * saved["Cref"] / 100
    observed = metrics["G_S_packet_s"]
    error = abs(observed - expected)
    tolerance = max(ARITH * abs(expected), ARITH * saved["Cref"])
    return dict(h=saved["h"], expected_packet_s=expected, observed_packet_s=observed,
                absolute_error_packet_s=error, tolerance_packet_s=tolerance,
                relative_error=error / max(abs(expected), 1e-300), passed=bool(error <= tolerance))


def saturated_fluid(raw, chains):
    la, lb, u, k, _ = map(F, raw["case"]["parameters"])
    amplitude = regime_amplitude(raw)
    da = ctmc.m0_gap(la, u, k, chains["Ast"].N, [math.inf], "A", a=amplitude)[0]
    db = ctmc.m0_gap(lb, u, k, chains["Bst"].N, [math.inf], "B", a=amplitude)[0]
    hbar = max(float(np.max(ctmc.m0_vhat(load, k, n, [math.inf], a=amplitude, return_T=True)[1]))
               for load, n in ((la, chains["Ast"].N), (la + u, chains["Ast"].N),
                               (lb, chains["Bst"].N), (lb + u, chains["Bst"].N)))
    return da, db, hbar, r2.max_pair_abs(da, db)


def limiting_share(chains, rates_a, rates_b, remainder_a, remainder_b):
    """Mode slopes, with exact-zero slopes resolved by saturated fluid gap."""
    wa, wb = chains["Ast"].pi, chains["Bst"].pi
    total = 0.
    zero_mass = 0.
    for ma in (0, 1):
        for mb in (0, 1):
            slope = float(rates_a[ma] + rates_b[mb])
            mass = float(wa[ma::2].sum() * wb[mb::2].sum())
            if slope < 0:
                total += mass
            elif slope == 0:
                zero_mass += mass
                total += ctmc.pair_sum(wa[ma::2], remainder_a[ma::2], remainder_a[ma::2] * 0,
                                      wb[mb::2], remainder_b[mb::2], remainder_b[mb::2] * 0, 0)[0]
    return float(total), zero_mass


def t4_prediction(raw, chains, age_multiple=1):
    la, lb, u, k, _ = map(F, raw["case"]["parameters"])
    amplitude = regime_amplitude(raw)
    tint, s = raw["T_int"], raw["s"]
    nc = r2.nowcast(la, lb, u, k, amplitude, age_multiple * tint)
    if not nc["eligible"]:
        return dict(eligible=False, w_star=None, classification="INELIGIBLE", reason=nc["reason"])
    da, db, hbar, maximum = saturated_fluid(raw, chains)
    ra, rb = np.asarray(nc["rate_A"]), np.asarray(nc["rate_B"])
    tau = age_multiple * tint
    transition = np.array([[1 + math.exp(-2 * tau / float(k)), 1 - math.exp(-2 * tau / float(k))],
                           [1 - math.exp(-2 * tau / float(k)), 1 + math.exp(-2 * tau / float(k))]]) / 2
    oa, ob = transition @ ra, transition @ rb
    fresh_share, zero_new = limiting_share(chains, ra, rb, da, db)
    # Only zero-rate modes need the full-state fluid posterior in the prediction.
    if np.any(np.add.outer(oa, ob) == 0):
        da_old = age.posterior_full(chains["Ast"], da, tau)
        db_old = age.posterior_full(chains["Bst"], db, tau)
    else:
        da_old, db_old = da, db
    old_share, zero_old = limiting_share(chains, oa, ob, da_old, db_old)
    rates = np.add.outer(ra, rb)
    mode_mass = np.outer(chains["Ast"].pi.reshape(-1, 2).sum(axis=0),
                         chains["Bst"].pi.reshape(-1, 2).sum(axis=0))
    plus = float(mode_mass[rates > 0].sum())
    minus = float(mode_mass[rates < 0].sum())
    support = mode_mass > 0
    eta = float(np.min(np.abs(rates[support])))
    mixed = plus > 1e-9 and minus > 1e-9
    h_eval = 300 * tint if mixed else 1.1 * max(hbar, maximum / eta) if eta > 0 else None
    return dict(eligible=True, w_star=nc["w_star"], rate_A=ra.tolist(), rate_B=rb.tolist(),
                old_rate_A=oa.tolist(), old_rate_B=ob.tolist(), positive_mass=plus, negative_mass=minus,
                classification="mixed_sign" if mixed else "same_sign", eta=eta, M=maximum, h_bar=hbar,
                h_evaluate=h_eval, h_evaluate_T_int=h_eval / tint if h_eval is not None else None,
                zero_rate_mass_new=zero_new, zero_rate_mass_old=zero_old,
                F_new_inf=fresh_share, F_old_inf=old_share, sigma=s * (old_share - fresh_share),
                evaluation_status="PLANNED" if h_eval is not None else "NO_FINITE_M_OVER_ETA",
                zero_tie_rule="use saturated fluid gap at h_bar; strict <0, ties Stay")


def gain_bias_values(chain, horizons, tolerance=1e-12):
    """Reuse Chain.V until its gain-bias remainder is uniformly negligible.

    The Markov semigroup contracts sup norm. After a computed remainder w at
    t, every later horizon has |P_h g| <= ||w||_inf. This omission is explicitly
    bounded (floating-point error is separate); never claim an exact tail zero.
    """
    values, errors, details = [], [], []
    for h in map(float, horizons):
        target = tolerance * max(1., h * abs(chain.r))
        t = min(h, max(chain.T_int, .01))
        while True:
            v = chain.V([t])[0]
            remainder = t * chain.r + chain.g - v
            bound = float(np.max(abs(remainder)))
            if t >= h or bound <= target:
                break
            t = min(h, 2 * t)
        omitted = 0. if t >= h else bound
        values.append(v if t >= h else h * chain.r + chain.g)
        errors.append(omitted)
        details.append(dict(h=h, computed_until=t, remainder_sup_norm=bound,
                            omitted_tail_bound=omitted, tolerance=target))
    return np.asarray(values), errors, details


def prepare(raw, horizons):
    la, lb, u, k, c = map(F, raw["case"]["parameters"])
    result = age.prepare_regime(la, lb, u, k, horizons, c=c, a=regime_amplitude(raw))
    if result["NA"] != saved_tint(raw)["N"]["A"] or result["NB"] != saved_tint(raw)["N"]["B"]:
        raise ValueError("unchanged engine did not reproduce W1b N")
    if not math.isclose(result["T_int"], raw["T_int"], rel_tol=1e-12):
        raise ValueError("unchanged engine did not reproduce W1b T_int")
    return result


def evaluate_q1(raw, index, pilot=False):
    """Pilot times h=1 plus a W1b control; truth covers the entire fixed grid."""
    start, wall = time.process_time(), time.perf_counter()
    tint = raw["T_int"]
    h_grid = (1,) if pilot else H_GRID
    target = [F(str(tint)) * h for h in h_grid]
    saved = saved_tint(raw)["h"]
    controls = [min(saved, key=lambda r: abs(r["h_Tint"] - 1))] if pilot else saved
    horizons = sorted(set(target + [F(r["h"]) for r in controls]))
    t = time.process_time()
    p = prepare(raw, horizons)
    prepare_cpu = time.process_time() - t
    chains = {name: p[name] for name in ("Ast", "Asw", "Bst", "Bsw")}
    h_lookup = {h: i for i, h in enumerate(horizons)}
    rows, replay, history_info = [], [], []
    timers = dict(prepare_cpu_seconds=prepare_cpu, posterior_cpu_seconds=0.,
                  simulation_cpu_seconds=0., knn_cpu_seconds=0., pair_cpu_seconds=0.)
    for age_multiple in AGES:
        tau = age_multiple * tint
        t = time.process_time()
        old = {}
        for side in ("A", "B"):
            old[side] = age.posterior_full(chains[side + "st"],
                np.column_stack([p["d" + side].T, p["dh" + side].T]), tau)
        timers["posterior_cpu_seconds"] += time.process_time() - t
        n_h = len(horizons)
        def metrics(j, oa, ob, shift=0.):
            return policy_metrics(chains, p["dhA"][j] + shift, p["dhB"][j], oa + shift, ob,
                                  p["dA"][j], p["dB"][j], old["A"][:, j], old["B"][:, j],
                                  float(horizons[j]), p["r_stay"], p["s"])
        if age_multiple == 1:
            for saved_row in controls:
                j = h_lookup[F(saved_row["h"])]
                m = metrics(j, old["A"][:, n_h + j], old["B"][:, n_h + j])
                comparison = control_comparison(m, saved_row)
                replay.append(comparison)
                if not comparison["passed"]:
                    raise ArithmeticError("H-PL1 BUG: " + json.dumps(comparison))
        t = time.process_time()
        for mult, h in zip(h_grid, target):
            j = h_lookup[h]
            for kernel in ("true_kernel", "plugin"):
                oa, ob = ((old["A"][:, n_h + j], old["B"][:, n_h + j]) if kernel == "true_kernel"
                          else (p["dhA"][j], p["dhB"][j]))
                for variant, slope in zip(VARIANTS, (0., p["s"], p["s_mm1"])):
                    rows.append(dict(regime=raw["id"], tau_T_int=age_multiple, h_T_int=mult,
                        h=float(h), tau=tau, L_T_int=None, replicate=None, seed=None,
                        kernel=kernel, variant=variant, **metrics(j, oa, ob, float(h) * slope)))
        timers["pair_cpu_seconds"] += time.process_time() - t
        delta = tau / 10
        max_steps = finite_prefix_steps(max(L_GRID) * tint, delta)
        for replicate in SEEDS:
            seed = seed_for(index, age_multiple, replicate, pilot)
            streams = np.random.SeedSequence(seed).spawn(2)
            histories = {}
            t = time.process_time()
            for side, stream in zip(("A", "B"), streams):
                histories[side], info = sample_history(chains[side + "st"], delta, max_steps,
                                                       np.random.default_rng(stream))
                history_info.append(dict(path=side, seed=seed, seed_spawn_key=list(stream.spawn_key),
                                         replicate=replicate, tau_T_int=age_multiple, **info))
            timers["simulation_cpu_seconds"] += time.process_time() - t
            for length in L_GRID:
                steps = finite_prefix_steps(length * tint, delta)
                learned, diagnostics = {}, {}
                t = time.process_time()
                for side in ("A", "B"):
                    z = histories[side][:steps + 1]
                    learned[side], diagnostics[side] = knn_posterior(z[:-10], z[10:],
                        p["dh" + side][[h_lookup[h] for h in target]], chains[side + "st"].n)
                timers["knn_cpu_seconds"] += time.process_time() - t
                t = time.process_time()
                for loc, (mult, h) in enumerate(zip(h_grid, target)):
                    j = h_lookup[h]
                    for variant, slope in zip(VARIANTS, (0., p["s"], p["s_mm1"])):
                        rows.append(dict(regime=raw["id"], tau_T_int=age_multiple, h_T_int=mult,
                            h=float(h), tau=tau, L_T_int=length, replicate=replicate, seed=seed,
                            kernel="learned", variant=variant, prefix_polling_steps=steps,
                            diagnostics=diagnostics, **metrics(j, learned["A"][loc], learned["B"][loc],
                                                             float(h) * slope)))
                timers["pair_cpu_seconds"] += time.process_time() - t
    return dict(owner="Doan Van Tai", regime=raw["id"], kind="PILOT" if pilot else "TRUTH",
                created_utc=stamp(), regime_index_zero_based=index,
                N=saved_tint(raw)["N"], T_int=tint, rows=rows, controls=replay,
                histories=history_info, timing=timers, cpu_seconds=time.process_time() - start,
                wall_seconds=time.perf_counter() - wall,
                max_chain_stationary_residual=max(ch.residual for ch in chains.values()),
                h_grid=list(h_grid), L_grid=list(L_GRID), seeds=list(SEEDS))


def q2_evaluate(raw, age_multiple, prediction):
    if not prediction["eligible"] or prediction["h_evaluate"] is None:
        return dict(regime=raw["id"], tau_T_int=age_multiple, status="NOT_EVALUABLE")
    start = time.process_time()
    _, chains = r2.chains_for(raw)
    h, tau = prediction["h_evaluate"], age_multiple * raw["T_int"]
    vals, errors, propagation = {}, {}, {}
    for name, chain in chains.items():
        value, error, detail = gain_bias_values(chain, [h])
        vals[name], errors[name], propagation[name] = value[0], error[0], detail[0]
    ga, gb = vals["Asw"] - vals["Ast"], vals["Bsw"] - vals["Bst"]
    error_gap = sum(errors.values())
    la, lb, u, k, _ = map(F, raw["case"]["parameters"])
    a = regime_amplitude(raw)
    da = ctmc.m0_gap(la, u, k, chains["Ast"].N, [h], "A", a=a)[0]
    db = ctmc.m0_gap(lb, u, k, chains["Bst"].N, [h], "B", a=a)[0]
    r_a = np.tile(prediction["rate_A"], chains["Ast"].N + 1)
    r_b = np.tile(prediction["rate_B"], chains["Bst"].N + 1)
    post = {}
    for side, gap, fluid, rate in (("A", ga, da, r_a), ("B", gb, db, r_b)):
        # Rate posterior is computed analytically on the autonomous two-mode
        # chain. This avoids roundoff changing an exact zero-rate tie.
        post[side] = age.posterior_full(chains[side + "st"], np.column_stack([gap, fluid]), tau)
    out = []
    for twin in ("T4", "T1"):
        if twin == "T4":
            ua, ub = da + h * r_a, db + h * r_b
            oa = post["A"][:, 1] + h * np.tile(prediction["old_rate_A"], chains["Ast"].N + 1)
            ob = post["B"][:, 1] + h * np.tile(prediction["old_rate_B"], chains["Bst"].N + 1)
        else:
            ua, ub = da + h * raw["s"], db
            oa, ob = post["A"][:, 1] + h * raw["s"], post["B"][:, 1]
        m = policy_metrics(chains, ua, ub, oa, ob, ga, gb, post["A"][:, 0], post["B"][:, 0],
                           h, chains["Ast"].r + chains["Bst"].r, raw["s"])
        sigma = prediction["sigma"] if twin == "T4" else 0.
        out.append(dict(regime=raw["id"], tau_T_int=age_multiple, twin=twin, h=h,
                        h_T_int=h / raw["T_int"], classification=prediction["classification"],
                        sigma=sigma, slope_measured=m["G_S_packet_s"] / h,
                        relative_slope_error=abs(m["G_S_packet_s"] / h - sigma) / abs(sigma) if sigma else None,
                        cost_gap_tail_bound=error_gap, G_S_tail_bound=2 * error_gap,
                        floating_point_error_in_tail_bound=False, **m))
    return dict(regime=raw["id"], tau_T_int=age_multiple, status="COMPLETED", rows=out,
                propagation=propagation, cpu_seconds=time.process_time() - start)


def pilot():
    require_environment()
    if (OUT / "lock.json").exists():
        raise RuntimeError("pilot is refused after lock")
    start = time.process_time()
    raws = matched_raws()
    selected = pilot_selection(raws)
    by_id = {r["id"]: i for i, r in enumerate(raws)}
    results = []
    for raw in selected:
        path = OUT / "pilot" / (raw["id"] + ".json")
        if path.exists():
            raise FileExistsError("pilot output already exists; do not silently reuse or overwrite")
        event("pilot_start", regime=raw["id"], N=saved_tint(raw)["N"])
        result = evaluate_q1(raw, by_id[raw["id"]], pilot=True)
        _, ch = r2.chains_for(raw)
        t4p = t4_prediction(raw, ch)
        q2 = q2_evaluate(raw, 1, t4p)
        result["q2_pilot"] = q2
        result["cpu_seconds_including_q2"] = result["cpu_seconds"] + q2.get("cpu_seconds", 0.)
        write_once(path, result)
        results.append(result)
        event("pilot_complete", regime=raw["id"], timing=result["timing"],
              cpu_seconds=result["cpu_seconds_including_q2"], controls_passed=all(c["passed"] for c in result["controls"]))
    # A finite-h pilot at 1 T_int is explicitly a timing sample. Scale the
    # expensive engine and posterior work by state size, generator rate and
    # horizon; scale history events by the actual Poisson workload. Use the
    # worse coefficient of the two pilots, not a light-regime constant mean.
    work = [work_metadata(r) for r in raws]
    lookup = {r["id"]: r for r in work}
    coefficients = {}
    for component, key in (("prepare_cpu_seconds", "pilot_prepare_work"),
                           ("posterior_cpu_seconds", "pilot_posterior_work"),
                           ("simulation_cpu_seconds", "simulation_work"),
                           ("knn_cpu_seconds", "pilot_knn_work"),
                           ("pair_cpu_seconds", "pilot_pair_work")):
        coefficients[component] = max(r["timing"][component] / max(lookup[r["regime"]][key], 1.) for r in results)
    totals = dict(prepare_cpu_seconds=sum(w["truth_prepare_work"] for w in work) * coefficients["prepare_cpu_seconds"],
                  posterior_cpu_seconds=sum(w["truth_posterior_work"] for w in work) * coefficients["posterior_cpu_seconds"],
                  simulation_cpu_seconds=sum(w["simulation_work"] for w in work) * coefficients["simulation_cpu_seconds"],
                  knn_cpu_seconds=sum(w["truth_knn_work"] for w in work) * coefficients["knn_cpu_seconds"],
                  pair_cpu_seconds=sum(w["truth_pair_work"] for w in work) * coefficients["pair_cpu_seconds"])
    # Q2 is eligible only at lighter loads, but budget it using all 92 regimes
    # and 300 T_int engine work, with the heavy pilot's observed engine rate.
    totals["q2_conservative_cpu_seconds"] = sum(w["q2_work_upper"] for w in work) * coefficients["prepare_cpu_seconds"]
    nominal = sum(totals.values())
    reserved = 1.25 * nominal + 180.
    pilot_cpu = time.process_time() - start
    report = dict(owner="Doan Van Tai", created_utc=stamp(), environment=environment(),
        regimes=[r["regime"] for r in results], heaviest_rule="max(max(N_A,N_B)), then sum N, then id",
        heaviest_regime=selected[1]["id"], pilot_h_T_int=[1], truth_h_T_int=list(H_GRID),
        pilot_sampling="all 2 ages x 5 pilot seeds x 4 prefixes at h=1; independent A/B streams",
        controls_passed=sum(sum(c["passed"] for c in r["controls"]) for r in results),
        controls_total=sum(len(r["controls"]) for r in results),
        components=totals, calibration_coefficients=coefficients,
        projected_truth_cpu_seconds=nominal, projected_truth_cpu_hours=nominal / 3600,
        projected_truth_with_reserve_cpu_seconds=reserved,
        projected_truth_with_reserve_cpu_hours=reserved / 3600,
        pilot_cpu_seconds=pilot_cpu, local_budget_cpu_seconds=CPU_CAP,
        decision="STOP_LOCAL_BUDGET_USE_GCP" if reserved + pilot_cpu > CPU_CAP else "WITHIN_LOCAL_PROJECTION",
        projection_caveat="Two-regime, workload-scaled timing projection, not a confidence interval or guarantee. Q2 upper charges all 92 regimes at direct 300 T_int work although gain-bias stopping and ineligibility reduce it. 25% +180s reserve.",
        q1_expected_learned_rows=92 * 2 * 5 * 4 * 5 * 3,
        pilot_outputs={str((OUT / "pilot" / (r["regime"] + ".json")).relative_to(ROOT)):
                       sha(OUT / "pilot" / (r["regime"] + ".json")) for r in results}, work=work)
    write_once(OUT / "pilot.json", report)
    event("pilot_projection", **{k: report[k] for k in (
        "pilot_cpu_seconds", "projected_truth_cpu_hours", "projected_truth_with_reserve_cpu_hours", "decision")})


def work_metadata(raw):
    ev, tint = saved_tint(raw), raw["T_int"]
    k, a = float(F(ev["parameters"][3])), float(ev["a"])
    rate_work = sum((2 * (ch["N"] + 1)) * (float(F(ch["load"])) + a + ctmc.MU + 1 / k)
                    for ch in ev["chains"].values())
    state_total = sum(2 * (n + 1) for n in ev["N"].values())
    stay_rates = sum(float(F(ev["chains"][name]["load"])) + a + ctmc.MU + 1 / k
                     for name in ("A_stay", "B_stay"))
    pair_work = state_total * math.log2(max(2, state_total))
    return dict(id=raw["id"], N=ev["N"], T_int=tint,
        pilot_prepare_work=rate_work * tint, truth_prepare_work=rate_work * 100 * tint,
        pilot_posterior_work=rate_work * tint * 4 * 5,
        truth_posterior_work=rate_work * tint * 4 * 2 * (5 + len(ev["h"]) + 1),
        simulation_work=stay_rates * 1000 * tint * 2 * 5,
        pilot_knn_work=state_total * 4 * 2 * 5,
        truth_knn_work=state_total * 4 * 2 * 5 * 5,
        pilot_pair_work=pair_work * 2 * (2 * 3 + 5 * 4 * 3),
        truth_pair_work=pair_work * (2 * 5 * (2 * 3 + 5 * 4 * 3) + len(ev["h"])),
        q2_work_upper=rate_work * 300 * tint * 2)


def projected_q1_seconds(work_row, coefficients):
    return (work_row["truth_prepare_work"] * coefficients["prepare_cpu_seconds"]
            + work_row["truth_posterior_work"] * coefficients["posterior_cpu_seconds"]
            + work_row["simulation_work"] * coefficients["simulation_cpu_seconds"]
            + work_row["truth_knn_work"] * coefficients["knn_cpu_seconds"]
            + work_row["truth_pair_work"] * coefficients["pair_cpu_seconds"])


def truth_population(pilot_report, cap=REGIME_CAP_CPU_SECONDS):
    coefficients = pilot_report["calibration_coefficients"]
    costs = {w["id"]: projected_q1_seconds(w, coefficients) for w in pilot_report["work"]}
    return sorted(k for k, v in costs.items() if v <= cap), costs


def predict():
    require_environment()
    if (OUT / "lock.json").exists() or (OUT / "truth_started.json").exists():
        raise RuntimeError("predictions cannot be changed after lock/truth")
    pilot_report = json.loads((OUT / "pilot.json").read_text())
    if pilot_report["controls_passed"] != pilot_report["controls_total"]:
        raise ArithmeticError("pilot control failure")
    start = time.process_time()
    raws = matched_raws()
    records = []
    for i, raw in enumerate(raws):
        _, ch = r2.chains_for(raw)
        t4 = {str(a): t4_prediction(raw, ch, a) for a in AGES}
        row = nominal_saved_30(raw)
        record = dict(regime=raw["id"], regime_index_zero_based=i,
            parameters=raw["case"]["parameters"], a=str(regime_amplitude(raw)), N=saved_tint(raw)["N"],
            T_int=raw["T_int"], s=raw["s"], s_mm1=raw["s_mm1"],
            saved_nominal_30=dict(h=row["h"], h_T_int=row["h_Tint"], G_S_pct_C_ref=row["G_S"],
                true_hybrid_both_side_regret_pct_C_ref=max(row["regret"]["hybrid_new"], row["regret"]["hybrid_old"])),
            in_saved_harm_population=bool(row["G_S"] < -.1),
            T4=t4, truth_seeds={str(a): [seed_for(i, a, r) for r in SEEDS] for a in AGES})
        records.append(record)
        event("prediction", regime=raw["id"], T4_class=t4["1"]["classification"],
              sigma=t4["1"].get("sigma"))
    population, costs = truth_population(pilot_report)
    for record in records:
        record["projected_q1_cpu_seconds"] = costs[record["regime"]]
        record["in_truth_population"] = record["regime"] in population
    records_all = records
    records = [r for r in records if r["in_truth_population"]]
    harm = [r["regime"] for r in records if r["in_saved_harm_population"]]
    hybrid = [r["regime"] for r in records if r["saved_nominal_30"]["true_hybrid_both_side_regret_pct_C_ref"] <= .5]
    groups = {name: [r["regime"] for r in records if r["T4"]["1"]["classification"] == name]
              for name in ("mixed_sign", "same_sign", "INELIGIBLE")}
    obj = dict(owner="Doan Van Tai", created_utc=stamp(), kind="PREDICTIONS_BEFORE_PL_TRUTH",
        card_sha256=sha(CARD), code_sha256=sha(__file__), pilot_sha256=sha(OUT / "pilot.json"),
        universe=92, excluded=[EXCLUDED], truth_population=population,
        truth_population_rule=f"pre-truth amendment A1: projected Q1 CPU <= {REGIME_CAP_CPU_SECONDS} s per regime from pilot.json coefficients (cost only, no outcome)",
        not_run_compute=sorted(set(costs) - set(population)), all_regimes=records_all, h_T_int=list(H_GRID), tau_T_int=list(AGES),
        L_T_int=list(L_GRID), seeds=list(SEEDS), k=K, regimes=records,
        n_true=len(harm), harm_population=harm, true_hybrid_saved_pass_population=hybrid,
        populations=groups, primary_age_T_int=1,
        population_provenance="n_true and pre-truth harm IDs are from existing W1b nominal h=30 T_int rows (actual rounded coordinates recorded per regime). PL truth uses exactly h=30 T_int. Scoring recomputes its exact-grid n_true and reports any membership difference; never substitutes the rounded row for an exact-grid outcome.",
        scientific_thresholds=dict(harm_pct_C_ref=-.1, harm_fraction=.8, min_n_true=10,
            hybrid_both_side_pct_C_ref=.5, hybrid_regime_allowance=2,
            slope_relative_error=.05, slope_regime_fraction=.9, min_T4_population=3,
            same_sign_abs_G_S_over_C_ref=1e-9),
        implementation=dict(seed_index="zero-based sorted matched-regime id (excluded case removed)",
            independent_paths="np.random.SeedSequence(card_seed).spawn(2), A then B",
            history="observations at 0..floor(L/delta); all overlapping lag-10 pairs in each prefix",
            sampling="untruncated uniformization, exactly exp(Q*delta), original finite-N generator",
            estimator="mode-matched equal-weight k=50 including all equal-distance boundary pairs",
            fallback="fewer than k: mean of all same-mode pairs; no same-mode pairs: mean of all pairs",
            ties="strict <0 -> Switch, otherwise Stay; no decision epsilon",
            fresh_rule="unchanged exact current fluid gap on both telemetry sides; only stale learns",
            both_side="max(fresh regret, stale regret), relative to fresh true-model oracle C_ref",
            T4_zero_rate="saturated fluid gap at h_bar, old fluid posterior at the true requested tau",
            T4_long_h="existing Chain.V gain-bias formula; bounded negligible tail omission, no direct huge-h exponential",
            tail_tolerance=1e-12, pilot_not_reused_as_truth=True),
        forecasts=dict(F1="n_true approximately 72", F2="Switch-optimal harm persists at all L",
            F3="Stay-optimal harm lost more often at small L", F4="20-40 eligible T4, mostly mixed-sign"),
        truth_status="NOT_RUN", prepare_cpu_seconds=time.process_time() - start,
        environment=environment())
    write_once(OUT / "predictions.json", obj)
    event("predictions_written", n_true=obj["n_true"], T4_counts={k: len(v) for k, v in groups.items()},
          cpu_seconds=obj["prepare_cpu_seconds"])


def source_paths():
    paths = [CARD, Path(__file__).resolve(), ROOT / "tests/test_pl_posterior.py",
             OUT / "predictions.json", OUT / "pilot.json", ROOT / "experiments/letter/e3_agediff.py",
             ROOT / "experiments/letter/r2_o1_check.py", ROOT / "experiments/explore_ctmc/ctmc.py",
             ROOT / "experiments/explore_ctmc/env.sh", ctmc.LOCKS_L72]
    gate = json.loads(ctmc.LOCKS_L72.read_text())
    paths.append(ctmc.LOCKS_L72.parent / gate["card"])
    paths.extend(sorted((ROOT / "results/letter/w1b/raw").glob("*.json")))
    paths.extend(sorted((OUT / "pilot").glob("*.json")))
    paths.append(ROOT / "results/letter/r2_o1/raw" / (R2_PILOT + ".json"))
    return sorted(set(p.resolve() for p in paths))


def lock():
    require_environment()
    if (OUT / "truth_started.json").exists():
        raise RuntimeError("truth already attempted")
    prediction = json.loads((OUT / "predictions.json").read_text())
    if prediction["code_sha256"] != sha(__file__) or prediction["card_sha256"] != sha(CARD):
        raise ValueError("code/card changed since predictions")
    record = dict(owner="Doan Van Tai", created_utc=stamp(), kind="PL_PRE_TRUTH_LOCK_NOT_COMMITTED",
        sha256={str(p.relative_to(ROOT)): sha(p) for p in source_paths()},
        environment=environment(), truth_status="NOT_RUN", no_retry_no_resume=True,
        local_budget_cpu_seconds=CPU_CAP,
        authorization="User authorized steps 1-4 only. Claude commits this lock and separately invokes truth.")
    write_once(OUT / "lock.json", record)
    event("lock_written", files=len(record["sha256"]), lock_sha256=sha(OUT / "lock.json"))


def verify_lock(require_committed=False):
    record = json.loads((OUT / "lock.json").read_text())
    expected_paths = {str(p.relative_to(ROOT)) for p in source_paths()}
    if set(record["sha256"]) != expected_paths:
        raise ValueError("lock input set changed")
    for path, digest in record["sha256"].items():
        if sha(ROOT / path) != digest:
            raise ValueError("locked file changed: " + path)
    if environment() != record["environment"]:
        raise ValueError("numeric environment/package versions changed since lock")
    if require_committed:
        committed = subprocess.run(["git", "show", "HEAD:results/letter/pl_posterior/lock.json"],
                                   cwd=ROOT, capture_output=True, check=True).stdout
        if committed != (OUT / "lock.json").read_bytes():
            raise RuntimeError("Claude must commit the identical lock before truth")
    return record


def cpu_guard(seconds):
    def stop(signum, frame):
        raise TimeoutError("PL CPU budget reached; no retry or resume")
    signal.signal(signal.SIGXCPU, stop)
    used = time.process_time()
    soft = max(1, math.ceil(used + seconds))
    resource.setrlimit(resource.RLIMIT_CPU, (soft, soft + 5))


def truth_worker(task):
    raw, index, t4, cap = task
    cpu_guard(cap)
    start = time.process_time()
    event("truth_regime_start", regime=raw["id"], cpu_cap_seconds=cap)
    result = evaluate_q1(raw, index)
    result["Q2"] = [q2_evaluate(raw, a, t4[str(a)]) for a in AGES]
    result["worker_cpu_seconds"] = time.process_time() - start
    path = OUT / "raw" / (raw["id"] + ".json")
    write_once(path, result)
    return dict(regime=raw["id"], path=str(path.relative_to(ROOT)), sha256=sha(path),
                cpu_seconds=result["worker_cpu_seconds"])


def truth(cpu_budget_seconds=CPU_CAP):
    """One-shot raw-only invocation. Scoring is a separate post-raw command."""
    require_environment()
    verify_lock(require_committed=True)
    plan = json.loads((OUT / "pilot.json").read_text())
    population, costs = truth_population(plan)
    needed = 1.25 * sum(costs[k] for k in population) + 180.
    if needed > cpu_budget_seconds:
        raise RuntimeError(f"STOP_BUDGET: projection {needed:.1f}s > explicit budget {cpu_budget_seconds}s; move to GCP, no local truth")
    # Exclusive start marker survives success, failure, interruption or SIGKILL.
    # No invocation is permitted to reuse a raw directory or resume a prefix.
    if RECEIPT.exists() or (OUT / "raw").exists():
        raise FileExistsError("existing truth artifacts: retry/resume refused")
    write_once(OUT / "truth_started.json", dict(utc=stamp(), lock_sha256=sha(OUT / "lock.json"),
        cpu_budget_seconds=cpu_budget_seconds, execution="one-shot, raw before score"))
    start = time.process_time()
    wall = time.perf_counter()
    outputs = []
    try:
        predictions = json.loads((OUT / "predictions.json").read_text())
        if predictions["truth_population"] != population:
            raise ValueError("truth population differs from the locked predictions")
        raws = matched_raws()
        index = {r["id"]: i for i, r in enumerate(raws)}
        by_id = {r["id"]: r for r in raws}
        plan_rows = {r["regime"]: r for r in predictions["regimes"]}
        jobs = sorted(population, key=lambda k: -costs[k])
        tasks = [(by_id[k], index[k], plan_rows[k]["T4"], max(600., 4 * costs[k] + 600.)) for k in jobs]
        context = multiprocessing.get_context("fork")
        with context.Pool(WORKERS, maxtasksperchild=1) as pool:
            for item in pool.imap_unordered(truth_worker, tasks):
                outputs.append(item)
                event("truth_regime_complete", regime=item["regime"], worker_cpu_seconds=item["cpu_seconds"],
                      completed=len(outputs), total=len(tasks), wall_seconds=time.perf_counter() - wall)
        verify_lock(require_committed=True)
    except BaseException as exc:
        write_once(RECEIPT, dict(status="INCOMPLETE", utc=stamp(), error_type=type(exc).__name__,
            error=str(exc), completed_regimes=len(outputs), raw=outputs,
            parent_cpu_seconds=time.process_time() - start, wall_seconds=time.perf_counter() - wall,
            no_retry_no_resume=True))
        raise
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    write_once(RECEIPT, dict(status="COMPLETED_RAW_UNSCORED", utc=stamp(), completed_regimes=len(outputs),
        population=len(population), raw=sorted(outputs, key=lambda o: o["path"]),
        parent_cpu_seconds=time.process_time() - start,
        children_cpu_seconds=children.ru_utime + children.ru_stime,
        wall_seconds=time.perf_counter() - wall, lock_sha256=sha(OUT / "lock.json")))
    event("truth_raw_complete", regimes=len(outputs), cpu_seconds=time.process_time() - start,
          next_step="commit raw before the separate score command")


def score():
    verify_lock(require_committed=True)
    receipt = json.loads(RECEIPT.read_text())
    if receipt["status"] != "COMPLETED_RAW_UNSCORED" or receipt["completed_regimes"] != receipt["population"]:
        raise ValueError("incomplete truth cannot be scored")
    raws = []
    for item in receipt["raw"]:
        path = ROOT / item["path"]
        if sha(path) != item["sha256"]:
            raise ValueError("raw checksum mismatch")
        committed = subprocess.run(["git", "show", "HEAD:" + item["path"]],
                                   cwd=ROOT, capture_output=True, check=True).stdout
        if committed != path.read_bytes():
            raise ValueError("commit identical raw before scoring")
        raws.append(json.loads(path.read_text()))
    verdict = score_records(raws, json.loads((OUT / "predictions.json").read_text()))
    write_once(OUT / "scores.json", dict(owner="Doan Van Tai", utc=stamp(), **verdict))
    event("score_complete", **verdict["tests"])


def score_records(raws, prediction):
    tests = {}
    comparisons = [c for r in raws for c in r["controls"]]
    control_ok = bool(comparisons) and all(c["passed"] for c in comparisons)
    tests["H-PL1"] = dict(verdict="PASS" if control_ok else "BUG_STOP", total=len(comparisons),
                         passed=sum(c["passed"] for c in comparisons))
    if not control_ok:
        return dict(tests=tests, remaining_tests="NOT_SCORED")
    primary = [row for r in raws for row in r["rows"] if row["tau_T_int"] == 1 and row["h_T_int"] == 30]
    baselines = {r["regime"]: r for r in primary if r["kernel"] == "true_kernel" and r["variant"] == "M0"}
    harm = [key for key, row in baselines.items() if row["G_S_pct_C_ref"] < -.1]
    learned = [r for r in primary if r["kernel"] == "learned" and r["L_T_int"] == 100]
    retained = []
    for name in harm:
        rows = [r for r in learned if r["regime"] == name and r["variant"] == "M0"]
        if len(rows) != 5 or {r["replicate"] for r in rows} != set(SEEDS):
            raise ValueError("missing/duplicate learned seeds")
        if np.median([r["G_S_pct_C_ref"] for r in rows]) < -.1:
            retained.append(name)
    ntrue = len(harm)
    tests["H-PL2"] = dict(verdict="NOT_EVALUABLE" if ntrue < 10 else
        "PASS" if len(retained) >= .8 * ntrue else "FAIL", n_true=ntrue, retained=len(retained),
        required=.8 * ntrue, regimes=retained)
    hybrid_true = [r for r in primary if r["kernel"] == "true_kernel" and r["variant"] == "hybrid_true_s"]
    nbaseline = sum(r["both_side_regret_pct_C_ref"] <= .5 for r in hybrid_true)
    passed = []
    for raw in raws:
        rows = [r for r in learned if r["regime"] == raw["regime"] and r["variant"] == "hybrid_true_s"]
        if len(rows) != 5 or {r["replicate"] for r in rows} != set(SEEDS):
            raise ValueError("missing/duplicate hybrid seeds")
        if all(r["both_side_regret_pct_C_ref"] <= .5 for r in rows):
            passed.append(raw["regime"])
    tests["H-PL3"] = dict(verdict="PASS" if len(passed) >= nbaseline - 2 else "FAIL",
                          true_kernel_pass=nbaseline, learned_pass=len(passed), required=nbaseline - 2)
    q2 = [row for r in raws for q in r["Q2"] if q["tau_T_int"] == 1
          for row in q.get("rows", []) if row["twin"] == "T4"]
    for label, classification in (("H-T4a", "mixed_sign"), ("H-T4b", "same_sign")):
        group = [r for r in q2 if r["classification"] == classification and
                 (classification != "mixed_sign" or abs(r["sigma"]) > 1e-9)]
        hits = sum((r["relative_slope_error"] <= .05 if classification == "mixed_sign" else
                    abs(r["G_S_packet_s"]) <= 1e-9 * r["C_ref"]) for r in group)
        required = .9 * len(group) if classification == "mixed_sign" else len(group)
        tests[label] = dict(verdict="NOT_EVALUABLE" if len(group) < 3 else
            "PASS" if hits >= required else "FAIL", eligible=len(group), passed=hits, required=required)
    return dict(tests=tests, exact_grid_harm_population=harm,
        predicted_saved_grid_n_true=prediction["n_true"],
        population_difference_from_saved_W1b=dict(added=sorted(set(harm) - set(prediction["harm_population"])),
            removed=sorted(set(prediction["harm_population"]) - set(harm))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("pilot", "predict", "lock", "verify-lock", "truth", "score"))
    parser.add_argument("--cpu-budget-seconds", type=int, default=CPU_CAP,
                        help="runtime cap; above the card's local 4h is for Claude's GCP invocation only")
    args = parser.parse_args()
    if args.command == "verify-lock":
        result = verify_lock()
        event("lock_verified", files=len(result["sha256"]), truth_started=(OUT / "truth_started.json").exists())
    elif args.command == "truth":
        truth(args.cpu_budget_seconds)
    else:
        globals()[args.command]()


if __name__ == "__main__":
    main()
