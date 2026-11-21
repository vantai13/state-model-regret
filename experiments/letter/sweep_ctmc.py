"""Doan Van Tai — S1-A exploratory heterogeneous CTMC sweep.

Only sample/pilot are authorized locally.  ``run`` is the handoff for Claude.
Plant, fluid, posterior, strict ties and truncation reuse unchanged X-CTMC.
Results are numerical solutions of a tail-controlled truncated CTMC, not
symbolically exact or measurements of a production network.  No truth guard
is bypassed.  Sobol cells/ages/horizons are not independent statistical trials.

Usage (source .venv/bin/activate and experiments/explore_ctmc/env.sh first):
    python3 -B -m experiments.letter.sweep_ctmc sample
    python3 -B -m experiments.letter.sweep_ctmc pilot --workers 2
    python3 -B -m experiments.letter.sweep_ctmc summarize --source pilot
    # Claude/GCP only, after reviewing the pilot:
    python3 -B -m experiments.letter.sweep_ctmc run --workers 15 --shard 0/2

Every published file is exclusive-create.  Failed/partial outputs survive.
Delivered handoff uses --out results/letter/sweep/ctmc/v2; the parent directory
retains the initial cost calibration and its unmodified pilot artifacts.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
import multiprocessing
from pathlib import Path
import time

import numpy as np
from scipy.optimize import nnls
from scipy.stats import qmc

from experiments.letter import mmpp, shat2, x_ctmc as x
from experiments.letter.w2_eval import absolute_tail_mass

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/letter/sweep/ctmc"
NAMESPACE = "s1a-ctmc-exploratory-v1"
SEEDS = dict(sample=8100001, pilot_selection=8100002, pilot_record=8100003,
             run_record=8100004)
H_GRID = (.1, .2, .3, .5, .7, 1., 1.5, 2., 3., 5., 7., 10., 20., 30.)
AGES = (.3, 1., 3.)
# Timing-only local subset selected from parameter costs before any new truth.
# Full run retains all 14 horizons and three ages specified by the brief.
PILOT_H = (.1, 1.)
PILOT_AGES = (.3,)
RULES = ("M0", "Stationary_true", "Stationary_hat", "Hybrid_true",
         "Hybrid_hat", "MLU", "TH_0.8", "Oracle")
RECORD_T_INT = 300.
CPU_CAP = 3600.
MAX_N = 4096
MAX_PAIR_STATES = 16000000
MAX_COUNT_BINS = 10000000
NUM_TOL = 1e-9  # arithmetic check, never a decision/effect threshold
# Initial cost-only screen, before new outcomes. Values/posterior constants
# conservatively round the old X-CTMC pilot's timing coefficients upward.
# These are heuristics; new pilot maxima calibrate the final projection.
INITIAL_COEFFICIENTS = dict(values=4e-8, posterior=4e-7, pairs=2e-6,
                            telemetry=5e-7, prepare=5e-6)
DEPENDENCIES = ("experiments/letter/x_ctmc.py", "experiments/letter/mmpp.py",
                "experiments/letter/shat2.py", "experiments/letter/w2_eval.py",
                "experiments/letter/pl_posterior.py",
                "experiments/letter/e3_agediff.py", "experiments/letter/shat.py",
                "experiments/letter/r2_o1_check.py",
                "experiments/explore_ctmc/ctmc.py",
                "experiments/explore_ctmc/env.sh")


def dump(path, value):
    x.write_once(path, value)


def read(path):
    return json.loads(Path(path).read_text())


def csv_once(path, rows):
    rows = list(rows)
    if not rows:
        raise ValueError("refuse an empty CSV without a schema")
    keys = list(dict.fromkeys(key for row in rows for key in row))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, sort_keys=True, allow_nan=False)
                             if isinstance(v, (list, dict)) else v
                             for k, v in row.items()})


def hashes():
    return {name: x.sha(ROOT / name) for name in DEPENDENCIES}


def validate_output(out):
    out = Path(out).resolve()
    if not out.is_relative_to(OUT.resolve()):
        raise ValueError("outputs must be under results/letter/sweep/ctmc")
    return out


def sobol_regimes(count=1024):
    """One scrambled 9-D Sobol net; no replacement of screened candidates."""
    if count < 1 or count & (count - 1):
        raise ValueError("Sobol candidate count must be a positive power of two")
    points = qmc.Sobol(9, scramble=True, seed=SEEDS["sample"]).random_base2(
        count.bit_length() - 1)
    regimes = []
    for i, z in enumerate(points):
        mu = 5. * 4. ** z[:2]
        loads = (.3 + .62 * z[2:4]) * mu
        amplitude = .9 * z[4:6] * loads
        kappa = .02 * 250. ** z[6:8]
        u = (.05 + .9 * z[8]) * float(np.min(.97 * mu - loads))
        paths = [x.PathSpec(*map(float, (loads[j], mu[j], amplitude[j], kappa[j])))
                 for j in (0, 1)]
        r = x.Regime(f"S1A_{i+1:04d}", *paths, float(u))
        label = x.parameter_comparison(r)["stratum"]
        regimes.append(x.Regime(r.id, r.A, r.B, r.u, label))
    return regimes


def truncation_for(regime):
    out = {}
    for side in ("A", "B"):
        path = getattr(regime, side)
        loads = dict(stay=path.load + (regime.u if side == "A" else 0.),
                     switch=path.load + (regime.u if side == "B" else 0.))
        selections = {a: mmpp.choose_N(load, path.kappa, path.alpha, path.mu, x.TAIL)
                      for a, load in loads.items()}
        out[side] = dict(N=max(v[0] for v in selections.values()),
                         actions={a: dict(selector_N=v[0], selector_tail=v[1], method=v[2])
                                  for a, v in selections.items()})
    return out


def work_proxy(p, horizons=H_GRID, ages=AGES):
    """Sparse work estimates; depends on parameters/stationarity, never regret."""
    ch, tint = p["chains"], p["T_int"]
    n_h, n_age = len(horizons), len(ages)
    sparse = sum(c.n * c.gamma for c in ch.values())
    stay = sum(ch[s+"st"].n * ch[s+"st"].gamma for s in ("A", "B"))
    return dict(values=sparse * max(horizons) * tint,
                posterior=stay * sum(ages) * tint * (2 * n_h + 1),
                pairs=sum(ch[s+"st"].n * math.log2(ch[s+"st"].n)
                          for s in ("A", "B")) * n_h * n_age,
                telemetry=2 * math.floor(RECORD_T_INT * tint / shat2.BIN_WIDTH)
                          + RECORD_T_INT * tint * sum(1 / getattr(p["regime"], s).kappa
                                                     for s in ("A", "B")),
                prepare=sum(c.n for c in ch.values()))


def projected_seconds(work, coefficients):
    return float(sum(work[k] * coefficients[k] for k in work))


def screen_regime(regime, cpu_cap=CPU_CAP):
    row = dict(id=regime.id, regime=regime.record(), status="REJECTED",
               reason=None, model_valid=False, numerical_valid=False)
    start = time.process_time()
    try:
        if x.heldout_collision(regime):
            row["reason"] = "HELDOUT_COLLISION"
            return row
        for path in (regime.A, regime.B):
            if not (0 <= path.alpha <= path.load and path.load + regime.u < path.mu
                    and path.kappa > 0):
                row["reason"] = "UNSTABLE_OR_INVALID_PARAMETERS"
                return row
        row["model_valid"] = True
        trunc = truncation_for(regime)
        n_a, n_b = (2 * (trunc[s]["N"] + 1) for s in ("A", "B"))
        row.update(truncation=trunc, state_pair=n_a * n_b)
        if any(v["N"] > MAX_N for v in trunc.values()) or n_a*n_b > MAX_PAIR_STATES:
            row["reason"] = "TRUNCATION_RESOURCE_CAP"
            return row
        # Chosen Ns already certify both actions; reuse unchanged X-CTMC.
        p = x.prepare(regime, Ns={s: trunc[s]["N"] for s in ("A", "B")})
        work = work_proxy(p)
        bins = math.floor(RECORD_T_INT * p["T_int"] / shat2.BIN_WIDTH)
        cost = projected_seconds(work, INITIAL_COEFFICIENTS)
        row.update(numerical_valid=True, T_int=p["T_int"], count_bins_per_path=bins,
                   work=work, initial_projected_cpu_seconds=cost,
                   chains={k: dict(states=c.n, residual=c.residual) for k, c in p["chains"].items()})
        if bins > MAX_COUNT_BINS:
            row["reason"] = "TELEMETRY_RESOURCE_CAP"
        elif cost > cpu_cap:
            row["reason"] = "PROJECTED_CPU_CAP"
        else:
            row.update(status="ELIGIBLE", reason=None)
    except (ValueError, ArithmeticError, RuntimeError, np.linalg.LinAlgError) as exc:
        row.update(reason="NUMERICAL_PREPARATION_ERROR", error=repr(exc))
    finally:
        row["screen_cpu_seconds"] = time.process_time() - start
    return row


def sample(out=OUT, count=1024, cpu_cap=CPU_CAP):
    out = validate_output(out)
    x.require_environment()
    if cpu_cap <= 0:
        raise ValueError("CPU cap must be positive")
    start, wall = time.process_time(), time.perf_counter()
    # Parameters/config are written before stationary metadata and any pilot.
    regimes = sobol_regimes(count)
    config = dict(namespace=NAMESPACE, owner="Doan Van Tai", kind="EXPLORATORY",
                  seed=SEEDS["sample"], candidate_count=count, c=0.,
                  h_T_int=list(H_GRID), tau_T_int=list(AGES), rules=list(RULES),
                  record_T_int=RECORD_T_INT, cpu_cap_seconds=cpu_cap,
                  max_N=MAX_N, max_pair_states=MAX_PAIR_STATES, max_count_bins=MAX_COUNT_BINS,
                  axes=dict(mu="log [5,20] per path", base_rho="[.3,.92] per path",
                            alpha_over_base_load="[0,.9] per path", kappa_seconds="log [.02,5] per path",
                            managed_rate="[.05,.95]*min(.97*mu-base_load)"),
                  initial_coefficients=INITIAL_COEFFICIENTS,
                  selection="parameter/truncation/resource cost only; no replacement",
                  source_sha256=x.sha(__file__), input_sha256=hashes(),
                  created_utc=x.stamp(), environment=x.environment())
    dump(out / "sample_config.json", config)
    dump(out / "candidates.json", [r.record() for r in regimes])
    rows = []
    for i, regime in enumerate(regimes):
        rows.append(screen_regime(regime, cpu_cap))
        if (i+1) % 128 == 0:
            x.event("sample_progress", screened=i+1, total=count)
    reasons = Counter(r["reason"] for r in rows if r["reason"])
    report = dict(config=config, candidates=rows, candidate_count=len(rows),
                  model_valid=sum(r["model_valid"] for r in rows),
                  numerical_valid=sum(r["numerical_valid"] for r in rows),
                  eligible=sum(r["status"] == "ELIGIBLE" for r in rows),
                  rejected_by_reason=dict(reasons), cpu_seconds=time.process_time()-start,
                  wall_seconds=time.perf_counter()-wall, finite_h_truth_computed=False)
    dump(out / "sample.json", report)
    csv_once(out / "sample.csv", ({k:v for k,v in r.items() if k != "regime"} for r in rows))
    x.event("sample_complete", **{k:report[k] for k in ("candidate_count", "model_valid", "numerical_valid",
                                                        "eligible", "rejected_by_reason", "cpu_seconds")})
    return report


def load_sample(out):
    report = read(Path(out) / "sample.json")
    if report["config"]["namespace"] != NAMESPACE:
        raise ValueError("wrong sample namespace")
    if report["config"]["input_sha256"] != hashes():
        raise ValueError("an existing CTMC input changed since sample")
    if read(Path(out) / "sample_config.json") != report["config"]:
        raise ValueError("sample configuration mismatch")
    if read(Path(out) / "candidates.json") != [r["regime"] for r in report["candidates"]]:
        raise ValueError("sample candidate records mismatch")
    return report


def pilot_selection(rows):
    eligible = [r for r in rows if r["status"] == "ELIGIBLE"]
    if len(eligible) < 10:
        raise ValueError("pilot requires at least ten eligible regimes")
    heavy = sorted(eligible, key=lambda r: (-r["initial_projected_cpu_seconds"], r["id"]))[:5]
    heavy_ids = {r["id"] for r in heavy}
    rest = sorted((r for r in eligible if r["id"] not in heavy_ids), key=lambda r: r["id"])
    chosen = np.random.default_rng(SEEDS["pilot_selection"]).choice(len(rest), 5, replace=False)
    return [(r, "heaviest_proxy") for r in heavy] + [(rest[int(i)], "random") for i in chosen]


def shard_rows(rows, shard):
    try:
        i, n = map(int, shard.split("/"))
    except (ValueError, AttributeError) as exc:
        raise ValueError("shard must be zero-based i/n") from exc
    if n < 1 or not 0 <= i < n:
        raise ValueError("shard must satisfy 0 <= i < n")
    # Fixed global candidate index, independent of eligibility/shard count.
    return [r for r in rows if (int(r["id"].rsplit("_", 1)[1])-1) % n == i]


def estimate_path(path, stay_load, shift, tint, rng):
    """W2's literal count moments; mu-specific validation, no disk writes.

    x.estimate_path cannot be called because it creates files under x_ctmc/.
    Reuse its count generator and FFT covariance primitives instead.  No
    telemetry bin decimation, finite-bin correction or parameter clipping.
    """
    W, delta = RECORD_T_INT * tint, shat2.BIN_WIDTH
    n = math.floor(W / delta)
    if not 2 <= n <= MAX_COUNT_BINS:
        raise ValueError("telemetry bin count outside resource/domain limits")
    counts = np.empty(n, dtype="<i4")
    record = shat2.simulate_counts(stay_load, path.alpha, path.kappa, W, rng, counts, delta)
    mean = float(np.sum(counts, dtype=float) / n)
    ss = 0.
    for begin in range(0, n, shat2.CHUNK_BINS):
        centered = np.asarray(counts[begin:begin+shat2.CHUNK_BINS], dtype=float) - mean
        ss += float(centered @ centered)
    lam, variance = mean/delta, ss/n/delta**2
    raw = variance - lam/delta
    alpha2 = max(0., raw)
    cov = shat2.autocovariances(counts, delta, max(1, math.ceil(50*path.kappa/delta)))
    nonpositive = np.flatnonzero(cov[1:] <= 0)
    stop = int(nonpositive[0]+1) if len(nonpositive) else None
    used = stop-1 if stop is not None else len(cov)-1
    khat = float(2*np.sum(cov[1:used+1])*delta/alpha2) if alpha2 > 0 else None
    alpha = math.sqrt(alpha2)
    errors = []
    if khat is None or not math.isfinite(khat) or khat <= 0:
        errors.append("undefined or nonpositive kappa_hat")
    if not (0 <= alpha <= min(lam, lam+shift) and max(lam, lam+shift) < path.mu):
        errors.append("estimated MMPP action parameters outside stable nonnegative domain")
    record.update(lambda_hat=lam, alpha_hat=alpha, alpha_squared_raw=raw,
                  kappa_hat=khat, stay_load_hat=lam, switch_load_hat=lam+shift,
                  rate_variance=variance, variance_ddof=0, first_nonpositive_lag=stop,
                  positive_lags_summed=used, max_lag_bins=len(cov)-1,
                  lag_cap_reached=stop is None, autocovariances=cov[:used+2].tolist(),
                  kappa_guess=path.kappa, kappa_guess_source="design kappa; computational lag cap only",
                  autocovariance_normalization="global mean, denominator n-k",
                  status="INVALID" if errors else "VALID", errors=errors,
                  mu=path.mu, count_storage="transient int32 array; seed/count SHA retained")
    return record


def estimate_s(p, purpose):
    if purpose not in ("pilot", "run"):
        raise ValueError("purpose must be pilot or run")
    index = int(p["regime"].id.rsplit("_", 1)[-1])
    seed = SEEDS[purpose+"_record"]
    streams = np.random.SeedSequence([seed, index]).spawn(2)
    telemetry, means, errors = {}, {}, []
    for j, side in enumerate(("A", "B")):
        path = getattr(p["regime"], side)
        shift = -p["regime"].u if side == "A" else p["regime"].u
        est = estimate_path(path, p["chains"][side+"st"].load, shift,
                            p["T_int"], np.random.default_rng(streams[j]))
        telemetry[side] = est
        if est["status"] != "VALID":
            errors.append(dict(path=side, errors=est["errors"]))
            continue
        for action in ("stay", "switch"):
            try:
                load = est[action+"_load_hat"]
                N, tail, method = mmpp.choose_N(load, est["kappa_hat"], est["alpha_hat"], path.mu, x.TAIL)
                if N > MAX_N:
                    raise ValueError("estimated MMPP truncation exceeds resource cap")
                value = mmpp.stationary_mean(load, est["kappa_hat"], est["alpha_hat"], path.mu, N=N)
                if tail > x.TAIL:
                    raise ArithmeticError("estimated MMPP tail certificate failed")
                means[side+"_"+action] = dict(**value.record(), selector_method=method)
            except (ValueError, ArithmeticError, RuntimeError, np.linalg.LinAlgError) as exc:
                errors.append(dict(path=side, action=action, error=repr(exc)))
    mm1, mm1_errors = {}, []
    for side in ("A", "B"):
        path = getattr(p["regime"], side)
        for action in ("stay", "switch"):
            load = telemetry[side][action+"_load_hat"]
            if not math.isfinite(load) or not 0 <= load < path.mu:
                mm1_errors.append(side+"_"+action+": M/M/1 estimated load outside [0,mu)")
            else:
                mm1[side+"_"+action] = load / (path.mu-load)
    def slope(v):
        return float(v["A_switch"]+v["B_switch"]-v["A_stay"]-v["B_stay"])
    mmpp_s = None if errors else slope({k:v["r"] for k,v in means.items()})
    mm1_s = None if mm1_errors else slope(mm1)
    chosen = mmpp_s if mmpp_s is not None else mm1_s
    return dict(status="VALID" if chosen is not None else "INVALID_ESTIMATOR", s_hat=chosen,
                method="MMPP/M/1" if mmpp_s is not None else "M/M/1" if mm1_s is not None else None,
                fallback=mmpp_s is None, fallback_reason=errors if errors else None,
                s_hat_mmpp=mmpp_s, s_hat_mm1=mm1_s, telemetry=telemetry,
                stationary_estimates=means, mm1_estimates=mm1, mm1_errors=mm1_errors,
                record_T_int=RECORD_T_INT, seed_coordinate=[seed, index], purpose=purpose)


def abs_gap_quantiles(wa, a, wb, b, quantiles=(.1, .5, .9, .99)):
    """Weighted discrete |a+b| quantiles, sorted CDF and 54 bisections.

    No state-pair tensor or probability cutoff; support location is numerical
    to about double precision. Exact CDF includes equality at both endpoints.
    """
    order = np.argsort(b, kind="stable")
    b, wb = b[order], wb[order]
    prefix = np.r_[0., np.cumsum(wb)]
    mass = float(wa.sum() * wb.sum())
    def cdf(v):
        left = np.searchsorted(b, -v-a, side="left")
        right = np.searchsorted(b, v-a, side="right")
        return float(wa @ (prefix[right]-prefix[left])) / mass
    upper = max(abs(float(np.min(a)+np.min(b))), abs(float(np.max(a)+np.max(b))))
    zero = cdf(0.)
    result = {}
    for q in quantiles:
        if not 0 < q < 1:
            raise ValueError("quantiles must be strictly between zero and one")
        lo, hi = 0., upper
        if zero >= q:
            hi = 0.
        else:
            for _ in range(54):
                mid = .5*(lo+hi)
                if cdf(mid) >= q:
                    hi = mid
                else:
                    lo = mid
        result[f"q{int(100*q):02d}"] = float(hi)
    return result


def regime_features(p, s_hat):
    r = p["regime"]
    rmin = min(p["r_stay"], p["r_switch"])
    features = dict(s=p["s"], s_hat=s_hat, r_min=rmin,
                    abs_s_over_r_min=abs(p["s"])/rmin, T_int=p["T_int"],
                    r_stay=p["r_stay"], r_switch=p["r_switch"], managed_rate=r.u, c=0.)
    for side in ("A", "B"):
        path = getattr(r, side)
        features.update({f"{side}_{key}": value for key, value in dict(
            mu=path.mu, base_rho=path.load/path.mu, alpha=path.alpha,
            alpha_over_base_load=path.alpha/path.load, kappa=path.kappa,
            kappa_over_T_int=path.kappa/p["T_int"],
            rho_stay=p["chains"][side+"st"].load/path.mu,
            rho_switch=p["chains"][side+"sw"].load/path.mu).items()})
    for level, s in (("true", p["s"]), ("hat", s_hat)):
        if s is None:
            features[f"static_{level}_chosen_path_busy_decision"] = None
            features[f"static_{level}_chosen_path_busy_stationary_action"] = None
            continue
        side, action = ("B", "sw") if s < 0 else ("A", "st")
        features[f"static_{level}_chosen_path"] = side
        features[f"static_{level}_chosen_path_busy_decision"] = 1-float(p["chains"][side+"st"].pi[:2].sum())
        features[f"static_{level}_chosen_path_busy_stationary_action"] = 1-float(p["chains"][side+action].pi[:2].sum())
    return features


def evaluate(p, horizons, ages, s_hat, rules=RULES, observation="full"):
    """Extend X-CTMC aggregation with true static/oracle, D and features.

    The old evaluate does not expose its value arrays. Reuse the path/decision
    and policy primitives here to avoid evaluating exp(Qh) a second time just
    to attach D(h), conditional benefits and fluid-gap quantiles.
    """
    start = time.process_time()
    ch = p["chains"]
    wa, wb = ch["Ast"].pi, ch["Bst"].pi
    t = time.process_time()
    values = {k:c.V(horizons) for k,c in ch.items()}
    gap = {s:values[s+"sw"]-values[s+"st"] for s in ("A", "B")}
    timing = dict(values=time.process_time()-t, posterior=0., pairs=0.)
    oracle_values = [x.pair_sum(wa, gap["A"][i], gap["A"][i], wb,
                              gap["B"][i], gap["B"][i], 0.) for i in range(len(horizons))]
    rows, features = [], []
    for tau in ages:
        t = time.process_time()
        decisions = x.decision_vectors(p, horizons, tau, s_hat, observation)
        old_gap = {s:x.posterior(ch[s+"st"], gap[s].T, tau, observation).T for s in ("A", "B")}
        timing["posterior"] += time.process_time()-t
        oa, ob = ((wa.reshape(-1, 2).sum(axis=1), wb.reshape(-1, 2).sum(axis=1))
                  if observation == "backlog" else (wa, wb))
        t = time.process_time()
        for i, h in enumerate(horizons):
            oracle_mass, oracle, oracle_tie = oracle_values[i]
            scale, cref = h*p["r_stay"], h*p["r_stay"]+oracle
            if cref <= 0:
                raise ArithmeticError("nonpositive C_ref")
            unconditional = float(wa @ gap["A"][i] + wb @ gap["B"][i])
            common = dict(regime=p["regime"].id, h=float(h), tau=float(tau),
                          h_T_int=round(float(h/p["T_int"]), 12),
                          tau_T_int=round(float(tau/p["T_int"]), 12),
                          C_ref=cref, cost_unit="packet*s", status="COMPLETED")
            cell = {}
            for rule in rules:
                is_static = rule.startswith("Stationary_")
                if rule == "Stationary_true":
                    action = int(p["s"] < 0)
                    fn = fo = float(action)
                    vn = vo = action*unconditional
                    tn = to = float(p["s"] == 0)
                elif rule == "Oracle":
                    # Reference oracle observes X at decision time on both
                    # sides. It is not the Bayes oracle restricted to stale Y.
                    fn = fo = oracle_mass
                    vn = vo = oracle
                    tn = to = oracle_tie
                else:
                    fresh = x.rule_inputs(p, decisions, rule, "fresh", i, h)
                    stale = x.rule_inputs(p, decisions, rule, "stale", i, h)
                    if fresh is None or stale is None:
                        row = dict(**common, rule=rule)
                        row["status"] = "INVALID_ESTIMATOR"
                        rows.append(row)
                        cell[rule] = row
                        continue
                    fn, vn, tn = x.policy_sum(wa, wb, fresh, gap["A"][i], gap["B"][i])
                    fo, vo, to = x.policy_sum(oa, ob, stale, old_gap["A"][i], old_gap["B"][i])
                    for inputs, side in ((fresh, "fresh"), (stale, "stale")):
                        action = x.constant_action(inputs)
                        if action is not None:
                            if side == "fresh":
                                fn, vn = float(action), action*unconditional
                            else:
                                fo, vo = float(action), action*unconditional
                row = dict(**common, rule=rule, L_fresh=scale+vn, L_stale=scale+vo,
                           regret_fresh=vn-oracle, regret_stale=vo-oracle,
                           regret_fresh_pct_C_ref=100*(vn-oracle)/cref,
                           regret_stale_pct_C_ref=100*(vo-oracle)/cref,
                           G_S=vo-vn, G_S_pct_C_ref=100*(vo-vn)/cref,
                           p_new=fn, p_old=fo, tie_share_fresh=tn, tie_share_stale=to,
                           s=p["s"], s_hat=s_hat, reference_oracle=rule == "Oracle")
                if is_static and row["G_S"] != 0.:
                    raise ArithmeticError("constant policy has nonzero G_S")
                if min(row["regret_fresh"], row["regret_stale"]) < -NUM_TOL*max(1., scale):
                    raise ArithmeticError("policy beats reference oracle beyond arithmetic tolerance")
                cell[rule] = row
                rows.append(row)
            quantiles = {side:abs_gap_quantiles(weights_a, decisions[side]["A"][i],
                                               weights_b, decisions[side]["B"][i])
                         for side, weights_a, weights_b in (("fresh", wa, wb), ("stale", oa, ob))}
            for level, s in (("true", p["s"]), ("hat", s_hat)):
                if s is None:
                    continue
                hybrid, static = cell.get("Hybrid_"+level), cell.get("Stationary_"+level)
                if hybrid is None or static is None or hybrid["status"] != "COMPLETED":
                    continue
                tails = {side:absolute_tail_mass(weights_a, decisions[side]["A"][i],
                                                 weights_b, decisions[side]["B"][i], h*abs(s))
                         for side, weights_a, weights_b in (("fresh", wa, wb), ("stale", oa, ob))}
                for side, share in (("fresh", "p_new"), ("stale", "p_old")):
                    disagree = 1-hybrid[share] if s < 0 else hybrid[share]
                    if not -NUM_TOL <= disagree <= tails[side]+NUM_TOL:
                        raise ArithmeticError("hybrid/static disagreement exceeds its D term")
                    benefit = static["regret_"+side]-hybrid["regret_"+side]
                    feature = dict(**common, level=level, side=side, **regime_features(p, s_hat),
                                   D_fresh=tails["fresh"], D_stale=tails["stale"],
                                   D=tails["fresh"]+tails["stale"], D_threshold=h*abs(s),
                                   D_applicable=s != 0, hybrid_static_disagreement=float(disagree),
                                   static_regret=static["regret_"+side], hybrid_regret=hybrid["regret_"+side],
                                   static_regret_pct_C_ref=static["regret_"+side+"_pct_C_ref"],
                                   hybrid_regret_pct_C_ref=hybrid["regret_"+side+"_pct_C_ref"],
                                   benefit_static_minus_hybrid=benefit,
                                   benefit_pp_C_ref=100*benefit/cref,
                                   benefit_when_disagree=None if disagree <= 0 else benefit/disagree,
                                   feature_provenance="model/stationary/finite arrival record; benefit is target")
                    feature.update({"abs_fluid_gap_"+key:value for key,value in quantiles[side].items()})
                    features.append(feature)
                    hybrid["hybrid_static_disagreement_"+side] = float(disagree)
                hybrid.update(D_fresh=tails["fresh"], D_stale=tails["stale"],
                              D=tails["fresh"]+tails["stale"], D_applicable=s != 0)
        timing["pairs"] += time.process_time()-t
    return dict(rows=rows, features=features, timing=timing,
                cpu_seconds=time.process_time()-start, observation=observation)


def evaluate_one(task):
    meta, purpose, destination, cap = task
    target = Path(destination) / (meta["id"]+".json")
    if target.exists():
        raise FileExistsError(target)
    start, wall = time.process_time(), time.perf_counter()
    result = dict(namespace=NAMESPACE, owner="Doan Van Tai", kind="EXPLORATORY", purpose=purpose,
                  id=meta["id"], regime=meta["regime"], source_sha256=x.sha(__file__),
                  status="INCOMPLETE", rows=[], features=[])
    x.event("regime_start", purpose=purpose, regime=meta["id"])
    try:
        with x.cpu_limit(cap):
            t = time.process_time()
            regime = x.Regime.from_record(meta["regime"])
            p = x.prepare(regime, Ns={s:meta["truncation"][s]["N"] for s in ("A", "B")})
            prepare_cpu = time.process_time()-t
            t = time.process_time()
            estimator = estimate_s(p, purpose)
            telemetry_cpu = time.process_time()-t
            h_grid, ages = (PILOT_H, PILOT_AGES) if purpose == "pilot" else (H_GRID, AGES)
            evaluation = evaluate(p, [h*p["T_int"] for h in h_grid],
                                  [age*p["T_int"] for age in ages], estimator["s_hat"])
            result.update(status="COMPLETED", estimator=estimator, T_int=p["T_int"],
                          h_T_int=list(h_grid), tau_T_int=list(ages), work=work_proxy(p, h_grid, ages),
                          truncation=p["truncation"], regime_features=regime_features(p, estimator["s_hat"]),
                          rows=evaluation["rows"], features=evaluation["features"],
                          timing=dict(**evaluation["timing"], prepare=prepare_cpu, telemetry=telemetry_cpu))
    except TimeoutError as exc:
        result.update(status="CPU_CAP", error=repr(exc))
    except Exception as exc:
        result.update(status="ERROR", error=repr(exc))
    result.update(cpu_seconds=time.process_time()-start, wall_seconds=time.perf_counter()-wall)
    dump(target, result)
    x.event("regime_complete", purpose=purpose, regime=meta["id"], status=result["status"],
            cpu_seconds=result["cpu_seconds"], wall_seconds=result["wall_seconds"])
    return dict(id=result["id"], status=result["status"], cpu_seconds=result["cpu_seconds"],
                wall_seconds=result["wall_seconds"], timing=result.get("timing"),
                work=result.get("work"),
                estimator_method=result.get("estimator", {}).get("method"),
                rows=len(result["rows"]), features=len(result["features"]), sha256=x.sha(target))


def process_tasks(tasks, workers):
    if workers < 1:
        raise ValueError("workers must be positive")
    if workers == 1:
        return [evaluate_one(t) for t in tasks]
    # Spawn avoids inherited RNG/process CPU clocks and BLAS fork state.
    with multiprocessing.get_context("spawn").Pool(workers) as pool:
        return list(pool.imap_unordered(evaluate_one, tasks, chunksize=1))


def project(rows, measurements, cpu_cap):
    lookup = {r["id"]:r for r in rows}
    completed = [r for r in measurements if r["status"] == "COMPLETED"]
    if not completed:
        raise ValueError("no completed pilot; projection unavailable")
    # Post-pilot cost diagnosis: a maximum time/work ratio mistakes small-
    # regime fixed overhead for a sparse operation's marginal cost. Fit a
    # nonnegative slope, then raise the intercept to envelope EVERY measured
    # pilot. This uses timings/work only, never the scientific outcomes.
    coefficients, intercepts = {}, {}
    for k in INITIAL_COEFFICIENTS:
        work = np.array([(r.get("work") or lookup[r["id"]]["work"])[k] for r in completed])
        observed = np.array([r["timing"][k] for r in completed])
        scale = max(float(work.max()), 1.)
        fitted = nnls(np.column_stack([np.ones(len(work)), work/scale]), observed)[0]
        coefficients[k] = float(fitted[1]/scale)
        intercepts[k] = float(np.maximum(0., observed-coefficients[k]*work).max())
    intercept_factors = dict(values=len(H_GRID)/len(PILOT_H),
                             posterior=len(H_GRID)*len(AGES)/(len(PILOT_H)*len(PILOT_AGES)),
                             pairs=len(H_GRID)*len(AGES)/(len(PILOT_H)*len(PILOT_AGES)),
                             telemetry=1., prepare=1.)
    # Safety factor is cost-only. Actual complete pilot CPU also lower-bounds
    # its projected cost. No scientific label influences final eligibility.
    final = []
    pilot_by_id = {r["id"]:r for r in measurements}
    censored = [lookup[r["id"]]["initial_projected_cpu_seconds"] for r in measurements
                if r["status"] == "CPU_CAP"]
    for meta in rows:
        row = dict(id=meta["id"], sample_status=meta["status"], reason=meta["reason"],
                   status="NOT_RUN", projected_cpu_seconds=None)
        if meta["status"] == "ELIGIBLE":
            cost = 1.5*sum(coefficients[k]*meta["work"][k] + intercepts[k]*intercept_factors[k]
                           for k in coefficients)
            observed = pilot_by_id.get(meta["id"], {})
            cost = max(cost, observed.get("cpu_seconds", 0.))
            reason = ("PILOT_CPU_CAP_LOWER_BOUND" if any(meta["initial_projected_cpu_seconds"] >= v for v in censored)
                      else "PROJECTED_CPU_CAP" if cost > cpu_cap else None)
            row.update(status="ELIGIBLE" if reason is None else "NOT_RUN", reason=reason,
                       projected_cpu_seconds=cost)
        final.append(row)
    total = sum(r["projected_cpu_seconds"] for r in final if r["status"] == "ELIGIBLE")
    return dict(coefficients=coefficients, pilot_intercepts_seconds=intercepts,
                full_grid_intercept_factors=intercept_factors,
                method="NNLS slope per component; intercept raised to cover all ten timings; no outcome inputs",
                safety_factor=1.5, cpu_cap_seconds=cpu_cap,
                rows=final, eligible=sum(r["status"] == "ELIGIBLE" for r in final),
                not_run_by_reason=dict(Counter(r["reason"] for r in final if r["reason"])),
                projected_cpu_hours=total/3600., projected_wall_hours_15_workers=total/(3600*15),
                projected_wall_hours_15_workers_90pct=total/(3600*15*.9),
                caveat="affine timing envelope * parameter work/grid scaling * 1.5; extrapolation, not a guarantee or confidence interval")


def pilot(out=OUT, workers=2):
    out = validate_output(out)
    x.require_environment()
    report = load_sample(out)
    chosen = pilot_selection(report["candidates"])
    plan = dict(namespace=NAMESPACE, kind="EXPLORATORY", created_utc=x.stamp(),
                sample_sha256=x.sha(out/"sample.json"), source_sha256=x.sha(__file__),
                input_sha256=hashes(), h_T_int=list(PILOT_H), tau_T_int=list(PILOT_AGES),
                full_h_T_int=list(H_GRID), full_tau_T_int=list(AGES),
                selections=[dict(id=r["id"], selection=why) for r,why in chosen],
                workers=workers, seed_record=SEEDS["pilot_record"],
                selection="five largest initial cost proxies + five random without replacement",
                projection_safety_factor=1.5,
                projection_model="nonnegative affine slope; intercept envelopes every pilot; component/grid scaling",
                pilot_scope="timing subset, chosen after parameter-only sample cost screen; not full-map outcomes")
    dump(out/"pilot_plan.json", plan)
    wall = time.perf_counter()
    results = process_tasks([(r, "pilot", str(out/"pilot"), report["config"]["cpu_cap_seconds"])
                             for r,why in chosen], workers)
    results.sort(key=lambda r:r["id"])
    if x.sha(__file__) != plan["source_sha256"] or hashes() != plan["input_sha256"]:
        raise ValueError("source/input changed during pilot; preserve raw outputs")
    projection = project(report["candidates"], results, report["config"]["cpu_cap_seconds"])
    receipt = dict(**plan, measured=results, statuses=dict(Counter(r["status"] for r in results)),
                   pilot_cpu_seconds=sum(r["cpu_seconds"] for r in results),
                   pilot_wall_seconds=time.perf_counter()-wall, projection=projection,
                   environment=x.environment(), full_run_status="NOT_RUN")
    dump(out/"pilot.json", receipt)
    csv_once(out/"projection.csv", projection["rows"])
    x.event("pilot_complete", statuses=receipt["statuses"], cpu_seconds=receipt["pilot_cpu_seconds"],
            wall_seconds=receipt["pilot_wall_seconds"], eligible=projection["eligible"],
            projected_cpu_hours=projection["projected_cpu_hours"],
            projected_wall_hours_15_workers=projection["projected_wall_hours_15_workers"])
    return receipt


def run(out=OUT, workers=15, shard="0/1"):
    out = validate_output(out)
    x.require_environment()
    report, pilot_report = load_sample(out), read(out/"pilot.json")
    if pilot_report["source_sha256"] != x.sha(__file__) or pilot_report["input_sha256"] != hashes():
        raise ValueError("source/input differs from reviewed pilot")
    if pilot_report["sample_sha256"] != x.sha(out/"sample.json"):
        raise ValueError("pilot and sample do not match")
    for row in pilot_report["measured"]:
        if x.sha(out/"pilot"/(row["id"]+".json")) != row["sha256"]:
            raise ValueError("pilot raw checksum mismatch")
    selected_ids = {r["id"] for r in pilot_report["projection"]["rows"] if r["status"] == "ELIGIBLE"}
    selected = shard_rows([r for r in report["candidates"] if r["id"] in selected_ids], shard)
    tag = shard.replace("/", "_of_")
    destination = out/"runs"/("shard_"+tag)
    start = dict(namespace=NAMESPACE, shard=shard, workers=workers, ids=[r["id"] for r in selected],
                 source_sha256=x.sha(__file__), input_sha256=hashes(),
                 sample_sha256=x.sha(out/"sample.json"), pilot_sha256=x.sha(out/"pilot.json"),
                 seed_record=SEEDS["run_record"], kind="EXPLORATORY", created_utc=x.stamp())
    dump(destination/"started.json", start)
    wall = time.perf_counter()
    measured = process_tasks([(r, "run", str(destination/"raw"), report["config"]["cpu_cap_seconds"])
                              for r in selected], workers)
    receipt = dict(**start, measured=sorted(measured, key=lambda r:r["id"]),
                   statuses=dict(Counter(r["status"] for r in measured)),
                   cpu_seconds=sum(r["cpu_seconds"] for r in measured), wall_seconds=time.perf_counter()-wall)
    dump(destination/"receipt.json", receipt)
    if hashes() != start["input_sha256"] or x.sha(__file__) != start["source_sha256"]:
        raise ValueError("inputs changed during run")
    x.event("shard_complete", shard=shard, statuses=receipt["statuses"])
    if any(r["status"] != "COMPLETED" for r in measured):
        raise RuntimeError("shard includes CPU_CAP/ERROR/INCOMPLETE; see receipt")
    return receipt


def describe(values, prefix):
    a = np.asarray(values, dtype=float)
    return {prefix+"_"+k:float(v) for k,v in dict(mean=a.mean(), min=a.min(), q10=np.quantile(a,.1),
                                                median=np.median(a), q90=np.quantile(a,.9), max=a.max()).items()}


def summarize(out=OUT, source="pilot"):
    out = validate_output(out)
    if source not in ("pilot", "run"):
        raise ValueError("source must be pilot or run")
    report = load_sample(out)
    if source == "pilot":
        receipt = read(out/"pilot.json")
        paths = [out/"pilot"/(r["id"]+".json") for r in receipt["measured"]]
        checksums = {r["id"]:r["sha256"] for r in receipt["measured"]}
    else:
        paths, checksums = [], {}
        for receipt_path in sorted((out/"runs").glob("shard_*/receipt.json")):
            receipt = read(receipt_path)
            for row in receipt["measured"]:
                if row["id"] in checksums:
                    raise ValueError("duplicate regimes across shards")
                checksums[row["id"]] = row["sha256"]
                paths.append(receipt_path.parent/"raw"/(row["id"]+".json"))
    if not paths:
        raise ValueError("no completed receipts to summarize")
    records = []
    for path in paths:
        record = read(path)
        if x.sha(path) != checksums[record["id"]]:
            raise ValueError("raw checksum mismatch")
        records.append(record)
    raw_rows = [row for r in records for row in r["rows"]]
    feature_rows = [dict(**row, estimator_method=r["estimator"]["method"])
                    for r in records if r["status"] == "COMPLETED" for row in r["features"]]
    if not feature_rows:
        raise ValueError("no scientific rows; failed records retained, no empty scientific summary")
    destination = out/(source+"_summary")
    groups, by_h_groups = defaultdict(list), defaultdict(list)
    for row in feature_rows:
        groups[(row["h_T_int"], row["tau_T_int"], row["side"], row["level"])].append(row)
        by_h_groups[(row["regime"], row["h_T_int"], row["side"], row["level"])].append(row)
    age_rows = []
    for key, cells in sorted(groups.items()):
        h, tau, side, level = key
        values = [r["benefit_pp_C_ref"] for r in cells]
        row = dict(h_T_int=h, tau_T_int=tau, side=side, level=level, regimes=len(cells),
                   baseline_mean_regret_pct_C_ref=float(np.mean([r["static_regret_pct_C_ref"] for r in cells])),
                   hybrid_mean_regret_pct_C_ref=float(np.mean([r["hybrid_regret_pct_C_ref"] for r in cells])),
                   **describe(values, "benefit_pp_C_ref"),
                   **describe([r["hybrid_static_disagreement"] for r in cells], "disagreement"))
        age_rows.append(row)
    regime_averages = defaultdict(list)
    for (regime,h,side,level), cells in by_h_groups.items():
        regime_averages[(h,side,level)].append(dict(
            benefit=float(np.mean([r["benefit_pp_C_ref"] for r in cells])),
            baseline=float(np.mean([r["static_regret_pct_C_ref"] for r in cells])),
            hybrid=float(np.mean([r["hybrid_regret_pct_C_ref"] for r in cells])),
            disagreement=float(np.mean([r["hybrid_static_disagreement"] for r in cells]))))
    h_rows = []
    for (h,side,level), cells in sorted(regime_averages.items()):
        h_rows.append(dict(h_T_int=h, side=side, level=level, regimes=len(cells),
                           baseline_mean_regret_pct_C_ref=float(np.mean([r["baseline"] for r in cells])),
                           hybrid_mean_regret_pct_C_ref=float(np.mean([r["hybrid"] for r in cells])),
                           **describe([r["benefit"] for r in cells], "benefit_pp_C_ref"),
                           **describe([r["disagreement"] for r in cells], "disagreement")))
    eligible = read(out/"pilot.json")["projection"]["eligible"]
    summary = dict(namespace=NAMESPACE, kind="EXPLORATORY", source=source,
                   sample_candidates=report["candidate_count"], planned_eligible=eligible,
                   measured_regimes=len(records), statuses=dict(Counter(r["status"] for r in records)),
                   rows=len(raw_rows), feature_rows=len(feature_rows),
                   estimator_methods=dict(Counter(r.get("estimator", {}).get("method") or "INVALID"
                                                  for r in records if r["status"] == "COMPLETED")),
                   invalid_policy_rows=sum(r["status"] != "COMPLETED" for r in raw_rows),
                   coverage="PILOT_ONLY" if source == "pilot" else "FULL" if len(records) == eligible else "PARTIAL",
                   statistics="descriptive finite panel; ages averaged within regime for by_h; no iid/population CI",
                   pilot_warning="five heaviest + five random is not a representative population sample" if source == "pilot" else None,
                   by_h=h_rows, by_h_and_age=age_rows, raw_sha256=checksums,
                   feature_columns_are_targets=["C_ref", "static_regret", "hybrid_regret", "static_regret_pct_C_ref",
                       "hybrid_regret_pct_C_ref", "benefit_static_minus_hybrid", "benefit_pp_C_ref", "benefit_when_disagree"],
                   feature_warning="Do not fit S2 predictors to target/outcome columns or use target columns for selection.")
    dump(destination/"summary.json", summary)
    csv_once(destination/"by_h.csv", h_rows)
    csv_once(destination/"by_h_and_age.csv", age_rows)
    csv_once(destination/"features_benefit.csv", feature_rows)
    csv_once(destination/"policies.csv", raw_rows)
    x.event("summary_complete", source=source, measured_regimes=len(records),
            rows=len(raw_rows), feature_rows=len(feature_rows), coverage=summary["coverage"])
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("sample", "pilot", "run", "summarize"):
        p = sub.add_parser(name)
        p.add_argument("--out", type=Path, default=OUT)
        if name == "sample":
            p.add_argument("--count", type=int, default=1024)
            p.add_argument("--cpu-cap", type=float, default=CPU_CAP)
        elif name in ("pilot", "run"):
            p.add_argument("--workers", type=int, default=2 if name == "pilot" else 15)
            if name == "run":
                p.add_argument("--shard", default="0/1")
        else:
            p.add_argument("--source", choices=("pilot", "run"), default="run")
    args = vars(parser.parse_args(argv))
    command = args.pop("command")
    return globals()[command](**args)


if __name__ == "__main__":
    main()
