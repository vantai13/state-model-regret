"""Doan Van Tai — R2-O1 exploratory scope check; unchanged W1b CTMC engine.

No commits, no network, exclusive creation of results. Commands: prepare,
pilot, run, score. Finite-h truth is obtained ONLY from e3_agediff.prepare_regime.
P_dis uses the actual joint law, including for deliberately wrong stale kernels.
Its optional stationary-tail omission is enclosed in a reported interval.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import io
import json
import math
import os
from pathlib import Path
import resource
import signal
import sys
import time

import numpy as np

from experiments.explore_ctmc import ctmc
from experiments.letter import e3_agediff as age

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/letter/r2_o1"
BRIEF = Path("/home/vantai/state-model-regret-papers/letter_smr/briefs/R2_O1_CHECK_BRIEF.md")
GRID = [1, 3, 10, 30, 100, 300]
TAIL_OMISSION = 1e-10
PDIS_WIDTH = 1e-9
ARITH = 1e-9
CPU_CAP = 7200
SOURCE_PATHS = [Path(__file__).resolve(), ROOT / "experiments/letter/e3_agediff.py",
                ROOT / "experiments/explore_ctmc/ctmc.py",
                ROOT / "experiments/explore_ctmc/env.sh", BRIEF]
D = {
    "D1": "T1, T2: G_S=0 (|G_S|<=1e-9*C_ref), P_dis=0 for h>M_hat/|s_hat|.",
    "D2": "T1, T2: |G_S|<=P_dis*max_x|V1-V0+c| at every grid h.",
    "D3": "T3: same as D1, including plug-in and exp(Q0*3*tau).",
    "D4": "T0: |G_S| grows approximately linearly; G_S/h -> s*DeltaF_inf.",
    "D5": "T4: mixed-sign s_nc gives nonvanishing P_dis and G_S/h -> s*(F_old_inf-F_new_inf); constant sign as D1.",
    "D6": "If a negative T4 slope is predicted, T4 harm grows with h there.",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def write_once(path, obj):
    path = Path(path)
    text = obj if isinstance(obj, str) else json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        f.write(text)


def saved_cases():
    raws = [json.loads(p.read_text()) for p in sorted((ROOT / "results/letter/w1b/raw").glob("*.json"))]
    if len(raws) != 93:
        raise ValueError("W1b universe must contain exactly 93 regimes")
    selected, groups = [], []
    for sign in (-1, 1):
        group = [r for r in raws if sign * r["s"] > 0]
        indices = np.rint(np.linspace(0, len(group) - 1, 6)).astype(int).tolist()
        groups.append(dict(sign=sign, available=len(group), indices_zero_based=indices))
        selected.extend(group[i] for i in indices)
    return sorted(selected, key=lambda r: r["id"]), groups


def chains_for(raw):
    ev = raw["evaluations"][0]
    la, lb, u, k, c = map(F, ev["parameters"])
    a, na, nb = F(str(ev["a"])), ev["N"]["A"], ev["N"]["B"]
    if c != 0:
        raise ValueError("brief fixes c=0")
    chains = dict(Ast=ctmc.chain(la+u, k, na, a), Asw=ctmc.chain(la, k, na, a),
                  Bst=ctmc.chain(lb, k, nb, a), Bsw=ctmc.chain(lb+u, k, nb, a))
    return (la, lb, u, k, c, a, na, nb), chains


def pair(chains, ua, va, ub, vb):
    return ctmc.pair_sum(chains["Ast"].pi, ua, va, chains["Bst"].pi, ub, vb, 0)


def max_pair_abs(a, b):
    return max(abs(float(np.min(a) + np.min(b))), abs(float(np.max(a) + np.max(b))))


def nowcast(la, lb, u, kappa, amplitude, tau):
    """Mode-only rate and exact two-mode posterior; no finite-h costs."""
    w = next((v for v in (F(1), F(1, 2), F(1, 4), F(1, 8), F(1, 16))
              if max(la+u, lb+u) + amplitude*v < F(19, 20)*ctmc.MU), None)
    if w is None:
        return dict(eligible=False, w_star=None, reason="no allowed w satisfies strict max load < 0.95*mu")
    rates_a = [ctmc.mm1_mean(la+m*amplitude*w) - ctmc.mm1_mean(la+u+m*amplitude*w) for m in (-1, 1)]
    rates_b = [ctmc.mm1_mean(lb+u+m*amplitude*w) - ctmc.mm1_mean(lb+m*amplitude*w) for m in (-1, 1)]
    decay = math.exp(-2*float(tau)/float(kappa))
    transition = np.array([[1+decay, 1-decay], [1-decay, 1+decay]])/2
    sn = np.add.outer(rates_a, rates_b)
    so = np.add.outer(transition @ rates_a, transition @ rates_b)
    an, ao = sn < 0, so < 0
    dis = sum(transition[ya, xa]*transition[yb, xb]*(an[xa, xb] != ao[ya, yb])/4
              for ya in range(2) for yb in range(2) for xa in range(2) for xb in range(2))
    # W is reported only as an interpretation of the selected w, not a new input.
    lo, hi = 0., 64.
    for _ in range(80):
        mid = (lo+hi)/2
        weight = -math.expm1(-2*mid)/(2*mid) if mid else 1.
        if weight > float(w):
            lo = mid
        else:
            hi = mid
    return dict(eligible=True, w_star=float(w), W_over_kappa=(lo+hi)/2,
                rate_A=rates_a, rate_B=rates_b, slope_by_modes=sn.tolist(),
                stale_rate_by_modes=so.tolist(), F_new_inf=float(an.mean()), F_old_inf=float(ao.mean()),
                delta_F_inf=float(ao.mean()-an.mean()), P_dis_inf=float(dis),
                mixed_sign=bool(np.min(sn) < 0 < np.max(sn)), zero_slope_modes=int(np.sum(sn == 0)),
                max_nowcast_load=float(max(la+u, lb+u)+amplitude*w))


def prepare():
    start = time.process_time()
    raws, groups = saved_cases()
    records = []
    for raw in raws:
        (la, lb, u, k, c, a, na, nb), ch = chains_for(raw)
        tau = max(v.T_int for v in ch.values())
        r_stay = ch["Ast"].r + ch["Bst"].r
        s = ch["Asw"].r + ch["Bsw"].r - r_stay
        smm1 = ctmc.mm1_mean(la)+ctmc.mm1_mean(lb+u)-ctmc.mm1_mean(la+u)-ctmc.mm1_mean(lb)
        da = ctmc.m0_gap(la, u, k, na, [math.inf], "A", a=a)[0]
        db = ctmc.m0_gap(lb, u, k, nb, [math.inf], "B", a=a)[0]
        mhat = max_pair_abs(da, db)
        hbar = max(float(np.max(ctmc.m0_vhat(load, k, n, [math.inf], a=a, return_T=True)[1]))
                   for load, n in ((la, na), (la+u, na), (lb, nb), (lb+u, nb)))
        oa, ob = age.posterior_full(ch["Ast"], da, tau), age.posterior_full(ch["Bst"], db, tau)
        fn = pair(ch, da, da*0, db, db*0)[0]
        fo = pair(ch, oa, oa*0, ob, ob*0)[0]
        nc = nowcast(la, lb, u, k, a, tau)
        if nc["eligible"]:
            nc["slope_predicted"] = s*nc["delta_F_inf"]
        path = ROOT / "results/letter/w1b/raw" / (raw["id"]+".json")
        records.append(dict(regime=raw["id"], parameters=[str(v) for v in (la, lb, u, k, c)], a=str(a),
            N_A=na, N_B=nb, T_int=tau, tau=tau, s=s, s_mm1=smm1, M_hat=mhat, h_bar=hbar,
            threshold_T1=mhat/abs(s), threshold_T2=mhat/abs(smm1),
            T0=dict(F_new_inf=fn, F_old_inf=fo, slope_predicted=s*(fo-fn)), T4=nc,
            saved_source=str(path.relative_to(ROOT)), saved_sha256=sha(path), saved_h=raw["case"]["hs"],
            saved_prepare_cpu=raw["prepare_cpu_seconds"], saved_h_max=max(float(F(h)) for h in raw["case"]["hs"]),
            kernel_work=(ch["Ast"].n**2+ch["Bst"].n**2)*tau,
            truth_work=sum(v.n*(float(v.load)+float(a)+ctmc.MU+1/float(k)) for v in ch.values())*tau))
        print(json.dumps(dict(event="prediction", regime=raw["id"], w=nc["w_star"],
                              slope_T4=nc.get("slope_predicted"), threshold_T1_Tint=mhat/abs(s)/tau)), flush=True)
    # A cheap single pilot is calibrated against each regime's saved timing and
    # matrix-work size, not extrapolated as a constant cost per regime.
    pilot = min(records, key=lambda r: r["kernel_work"])["regime"]
    obj = dict(owner="Doan Van Tai", created_utc=stamp(), kind="EXPLORATION_NOT_PAPER_RESULT",
        predictions=D, proposed_grid=GRID, selection=groups, regimes=records, pilot=pilot,
        arithmetic_relative_tolerance=ARITH, p_dis_tail_omission_per_path=TAIL_OMISSION,
        p_dis_shortcut_max_interval_width=PDIS_WIDTH, cpu_cap_seconds=CPU_CAP,
        finite_grid_reading="D4-D6 have no supplied convergence tolerance: report errors and trends, do not invent PASS for a limit. D1/D3 with no eligible h are NOT_EVALUABLE.",
        reduction_rule="After one-regime pilot remove largest h/T_int first until projected aggregate CPU <= 2h including pilot and reserve; stop if even {1} cannot fit. Pilot extra levels are kept separately, never selected by outcome.",
        P_scope_notes=["K must be a normalized nonnegative probability kernel.",
          "Paper Prop.2 includes max(h_bar,M_hat/abs(s_hat)); both thresholds are recorded.",
          "Here individual fluid action differences have fixed opposite signs and include zero at the empty low-mode state; the saturated max bounds all h.",
          "No nonzero slope is inferred merely from a mixed-sign state-dependent rate; delta_F_inf is calculated before truth."],
        exposure="All 93 W1b s/metadata already exist; selected raw schema and old readouts were inspected. T0 replay is reuse/reproduction. All new finite-h costs follow this file. No external literature search.",
        sources={str(p):sha(p) for p in SOURCE_PATHS}, prepare_cpu_seconds=time.process_time()-start)
    write_once(OUT / "predictions_before.json", obj)
    print(json.dumps(dict(event="predictions_written", pilot=pilot, cpu=obj["prepare_cpu_seconds"])), flush=True)


def load_prediction():
    pred = json.loads((OUT / "predictions_before.json").read_text())
    for path, digest in pred["sources"].items():
        if sha(path) != digest:
            raise ValueError("source changed after predictions: "+path)
    for reg in pred["regimes"]:
        if sha(ROOT / reg["saved_source"]) != reg["saved_sha256"]:
            raise ValueError("saved W1b raw changed")
    return pred


def marginal_disagreement_interval(f_new, f_old):
    return max(0., abs(f_new-f_old)), min(1., f_new+f_old, 2-f_new-f_old)


class JointLaw:
    """Reusable marginal joint laws pi(y) exp(Q*tau)[y,x]. No model changes."""
    def __init__(self, chains, tau):
        self.chains, self.tau = chains, tau
        self.data = None
        self.cpu = 0.

    def build(self):
        if self.data is not None:
            return self.data
        t = time.process_time()
        out = []
        for name in ("Ast", "Bst"):
            ch = self.chains[name]
            keep = int(np.searchsorted(np.cumsum(ch.pi), 1-TAIL_OMISSION))+1
            keep = min(ch.n, keep)
            # The full original Q is used; only terminal x columns are omitted.
            # No killed/shortened chain, row renormalization or state projection.
            J = np.empty((ch.n, keep))
            for lo in range(0, keep, 128):
                hi = min(keep, lo+128)
                rhs = np.zeros((ch.n, hi-lo))
                rhs[np.arange(lo, hi), np.arange(hi-lo)] = 1.
                J[:, lo:hi] = ch.pi[:, None]*age.posterior_full(ch, rhs, self.tau)
            dropped = float(np.sum(ch.pi[keep:]))
            err_col = float(np.max(np.abs(J.sum(axis=0)-ch.pi[:keep])))
            if J.min() < -1e-12 or err_col > 1e-9:
                raise ArithmeticError("joint-law positivity/stationary marginal check failed")
            out.append((J, dropped, err_col))
            print(json.dumps(dict(event="joint_path", path=name, n=ch.n, kept=keep,
                                  dropped_mass=dropped, marginal_error=err_col,
                                  cpu=time.process_time()-t)), flush=True)
        self.data = out
        self.cpu = time.process_time()-t
        return out

    def disagreement(self, new_a, new_b, old_a, old_b, fn, fo):
        lo, hi = marginal_disagreement_interval(fn, fo)
        if hi-lo <= PDIS_WIDTH:
            return dict(P_dis=(lo+hi)/2, P_dis_lower=lo, P_dis_upper=hi,
                        P_dis_method="marginal_probability_enclosure", joint_marginal_error=0.)
        (ja, drop_a, err_a), (jb, drop_b, err_b) = self.build()
        val, lower, upper = disagreement_from_joints(ja, jb, new_a, new_b, old_a, old_b,
                                                    fn, fo, drop_a+drop_b)
        return dict(P_dis=val, P_dis_lower=lower, P_dis_upper=upper,
                    P_dis_method="full_semigroup_joint_tail_enclosure",
                    joint_marginal_error=max(err_a, err_b))


def disagreement_from_joints(ja, jb, new_a, new_b, old_a, old_b, fn, fo, omitted=0.):
    """Both-switch probability from a 2D prefix CDF; avoids the 4D joint.

    ja/ jb include all old y rows and optionally a terminal current x prefix.
    An omitted current stationary mass <= omitted brackets the event, rather
    than changing either classifier or its switching shares.
    """
    nx_a, nx_b = ja.shape[1], jb.shape[1]
    order_y = np.argsort(old_b, kind="stable")
    order_x = np.argsort(new_b[:nx_b], kind="stable")
    cdf = np.zeros((jb.shape[0]+1, nx_b+1))
    cdf[1:, 1:] = jb[np.ix_(order_y, order_x)]
    np.cumsum(cdf, axis=0, out=cdf)
    np.cumsum(cdf, axis=1, out=cdf)
    cut_x = np.searchsorted(new_b[:nx_b][order_x], -new_a[:nx_a], side="left")
    cut_y = np.searchsorted(old_b[order_y], -old_a, side="left")
    both = 0.
    for i in range(0, ja.shape[0], 128):
        sl = slice(i, i+128)
        both += float(np.sum(ja[sl]*cdf[cut_y[sl, None], cut_x[None, :]]))
    lower = max(0., fn+fo-2*(both+omitted))
    upper = min(1., fn+fo-2*both)
    # Rounding is reported via marginals; this is not an interval-arithmetic
    # certificate of scipy's exponential. Remove a last-ulp empty enclosure.
    if lower > upper and lower-upper < 1e-12:
        lower = upper = max(0., min(1., (lower+upper)/2))
    if lower > upper:
        raise ArithmeticError("empty disagreement enclosure")
    return (lower+upper)/2, lower, upper


def evaluate_record(reg, grid, label):
    start, wall = time.process_time(), time.perf_counter()
    hs_main = [F(str(reg["T_int"]))*mult for mult in grid]
    hs = sorted(set(hs_main + [F(h) for h in reg["saved_h"]]))
    la, lb, u, k, c = map(F, reg["parameters"])
    a = F(reg["a"])
    print(json.dumps(dict(event="truth_start", regime=reg["regime"], grid=grid, max_h=float(max(hs)), utc=stamp())), flush=True)
    t = time.process_time()
    p = age.prepare_regime(la, lb, u, k, hs, c=c, a=a)
    truth_cpu = time.process_time()-t
    if p["NA"] != reg["N_A"] or p["NB"] != reg["N_B"]:
        raise ValueError("W1b truncation mismatch")
    ch = {name:p[name] for name in ("Ast", "Asw", "Bst", "Bsw")}
    H, tau = len(hs), reg["tau"]
    t = time.process_time()
    # Match W1b's column layout for the correct posterior; costs use actual tau.
    post = {}
    wrong = {}
    for side, stay in (("A", p["Ast"]), ("B", p["Bst"])):
        vec = np.column_stack([p["d"+side].T, p["dh"+side].T, p["b"+side]])
        post[side] = age.posterior_full(stay, vec, tau)
        wrong[side] = age.posterior_full(stay, p["dh"+side][:H].T, 3*tau).T
    post_cpu = time.process_time()-t
    joint = JointLaw(ch, tau)
    nc = reg["T4"]
    rate_a = np.tile(nc["rate_A"], p["NA"]+1) if nc["eligible"] else None
    rate_b = np.tile(nc["rate_B"], p["NB"]+1) if nc["eligible"] else None
    rate_ao = age.posterior_full(p["Ast"], rate_a, tau) if nc["eligible"] else None
    rate_bo = age.posterior_full(p["Bst"], rate_b, tau) if nc["eligible"] else None
    raw_old = json.loads((ROOT/reg["saved_source"]).read_text())
    saved = next(ev for ev in raw_old["evaluations"] if ev["age_label"] == "Tint_1")
    saved_rows = {F(r["h"]):r for r in saved["h"]}
    rows, replay = [], []
    for i, hfrac in enumerate(hs):
        h = float(hfrac)
        da, db, ma, mb = p["dA"][i], p["dB"][i], p["dhA"][i], p["dhB"][i]
        doa, dob = post["A"][:, i], post["B"][:, i]
        moa, mob = post["A"][:, H+i], post["B"][:, H+i]
        cref = h*p["r_stay"] + pair(ch, da, da, db, db)[1]
        t0new = pair(ch, ma, da, mb, db)
        t0old = pair(ch, moa, doa, mob, dob)
        if hfrac in saved_rows:
            value = 100*(t0old[1]-t0new[1])/cref
            expected = saved_rows[hfrac]["G_S"]
            err = abs(value-expected)/max(abs(expected), 1e-300)
            replay.append(dict(h=str(hfrac), observed=value, expected=expected,
                               relative_error=err, passed=bool(err <= ARITH)))
        if hfrac not in hs_main:
            rows.append(dict(regime=reg["regime"], twin="T0", kernel="posterior_tau", grid_kind="W1B_REPLAY",
                h=h, h_T_int=h/reg["T_int"], G_S_abs=t0old[1]-t0new[1], G_S_pct_C_ref=100*(t0old[1]-t0new[1])/cref,
                C_ref=cref, P_dis=None, P_dis_lower=None, P_dis_upper=None, M_hat=reg["M_hat"], s_hat=0.,
                threshold=None, h_bar=reg["h_bar"], max_abs_true_gap=max_pair_abs(da, db), w_star=None,
                slope_predicted=reg["T0"]["slope_predicted"], slope_measured=(t0old[1]-t0new[1])/h,
                F_new=t0new[0], F_old=t0old[0], s_true=p["s"], flags="REPLAY_ONLY_NO_PDIS"))
            continue
        twins = [("T0", "posterior_tau", ma, mb, moa, mob, 0., None),
          ("T1", "posterior_tau", ma+h*p["s"], mb, moa+h*p["s"], mob, p["s"], reg["threshold_T1"]),
          ("T2", "posterior_tau", ma+h*p["s_mm1"], mb, moa+h*p["s_mm1"], mob, p["s_mm1"], reg["threshold_T2"]),
          ("T3_plugin", "plugin", ma+h*p["s"], mb, ma+h*p["s"], mb, p["s"], reg["threshold_T1"]),
          ("T3_3tau", "posterior_3tau", ma+h*p["s"], mb, wrong["A"][i]+h*p["s"], wrong["B"][i], p["s"], reg["threshold_T1"])]
        if nc["eligible"]:
            twins.append(("T4", "posterior_tau", ma+h*rate_a, mb+h*rate_b,
                          moa+h*rate_ao, mob+h*rate_bo, None, None))
        for twin, kernel, ua, ub, oa, ob, shat, threshold in twins:
            fn, vn, _ = pair(ch, ua, da, ub, db)
            # Deliberately wrong decision kernel never changes the true cost posterior.
            fo, vo, _ = pair(ch, oa, doa, ob, dob)
            gs = vo-vn
            dis = joint.disagreement(ua, ub, oa, ob, fn, fo)
            maxgap = max_pair_abs(da, db)
            flags = []
            if cref <= 0 or not math.isfinite(gs):
                flags.append("INVALID_COST")
            if abs(gs) > dis["P_dis_upper"]*maxgap+ARITH*cref:
                flags.append("DISAGREEMENT_BOUND_VIOLATION")
            if max_pair_abs(ma, mb) > reg["M_hat"]*(1+1e-12):
                flags.append("FLUID_GLOBAL_BOUND_VIOLATION")
            slope = reg["T0"]["slope_predicted"] if twin == "T0" else nc.get("slope_predicted") if twin == "T4" else None
            row = dict(regime=reg["regime"], twin=twin, kernel=kernel, grid_kind="MAIN" if label != "pilot_extra" else "PILOT_EXTRA",
                h=h, h_T_int=h/reg["T_int"], G_S_abs=gs, G_S_pct_C_ref=100*gs/cref, C_ref=cref,
                **dis, M_hat=reg["M_hat"], s_hat=shat, threshold=threshold, h_bar=reg["h_bar"],
                above_threshold=bool(threshold is not None and h > threshold),
                above_paper_threshold=bool(threshold is not None and h > max(reg["h_bar"], threshold)),
                max_abs_true_gap=maxgap, w_star=nc["w_star"] if twin == "T4" else None,
                slope_predicted=slope, slope_measured=gs/h if slope is not None else None,
                slope_absolute_error=abs(gs/h-slope) if slope is not None else None,
                slope_relative_error=abs(gs/h-slope)/abs(slope) if slope else None,
                F_new=fn, F_old=fo, s_true=p["s"], flags=";".join(flags))
            rows.append(row)
        print(json.dumps(dict(event="h_complete", regime=reg["regime"], h_T_int=h/reg["T_int"],
                              cpu=time.process_time()-start)), flush=True)
    return dict(regime=reg["regime"], created_utc=stamp(), grid=grid, rows=rows, replay=replay,
        prediction_sha256=sha(OUT/"predictions_before.json"), truth_cpu_seconds=truth_cpu,
        posterior_cpu_seconds=post_cpu, joint_cpu_seconds=joint.cpu,
        cpu_seconds=time.process_time()-start, wall_seconds=time.perf_counter()-wall,
        chain_residual_max=max(v.residual for v in ch.values()),
        note="Finite CTMC and floating-point expm; P_dis interval covers omitted stationary terminal mass, not floating-point error.")


def cpu_guard(seconds):
    def stop(signum, frame):
        raise TimeoutError("R2-O1 CPU budget reached")
    signal.signal(signal.SIGXCPU, stop)
    used = resource.getrusage(resource.RUSAGE_SELF).ru_utime + resource.getrusage(resource.RUSAGE_SELF).ru_stime
    limit = max(1, math.ceil(used+seconds))
    resource.setrlimit(resource.RLIMIT_CPU, (limit, limit+5))


def pilot():
    pred = load_prediction()
    cpu_guard(CPU_CAP-pred["prepare_cpu_seconds"]-180)
    reg = next(r for r in pred["regimes"] if r["regime"] == pred["pilot"])
    result = evaluate_record(reg, GRID, "pilot")
    write_once(OUT / "raw" / (reg["regime"]+".json"), result)
    # Saved timing accounts for expensive N, loads, kappa and horizon per regime.
    # Joint semigroup cost is horizon-independent once needed, conservative N^2*tau.
    coefficient = result["truth_cpu_seconds"] / (reg["saved_prepare_cpu"]*max(300*reg["T_int"], reg["saved_h_max"])/reg["saved_h_max"])
    jrate = result["joint_cpu_seconds"]/reg["kernel_work"]
    projections = []
    for grid in (GRID, GRID[:-1], GRID[:-2], GRID[:-3], GRID[:-4], GRID[:1]):
        truth = sum(r["saved_prepare_cpu"]*max(max(grid)*r["T_int"], r["saved_h_max"])/r["saved_h_max"]*coefficient
                    for r in pred["regimes"] if r["regime"] != pred["pilot"])
        joint = sum(r["kernel_work"]*jrate for r in pred["regimes"] if r["regime"] != pred["pilot"])
        post = sum(r["truth_work"]/reg["truth_work"]*result["posterior_cpu_seconds"]
                   for r in pred["regimes"] if r["regime"] != pred["pilot"])
        projected = pred["prepare_cpu_seconds"]+result["cpu_seconds"] + 1.25*(truth+joint+post)+180
        projections.append(dict(grid=grid, projected_total_cpu_seconds=projected,
                                remaining_truth=truth, remaining_joint=joint, remaining_posterior=post))
    chosen = next((r for r in projections if r["projected_total_cpu_seconds"] <= CPU_CAP), None)
    rec = dict(created_utc=stamp(), pilot=pred["pilot"], cpu_seconds=result["cpu_seconds"],
        timing={k:result[k] for k in ("truth_cpu_seconds", "joint_cpu_seconds", "posterior_cpu_seconds")},
        projections=projections, selected_grid=chosen["grid"] if chosen else [],
        decision="RUN_REDUCED_GRID" if chosen and chosen["grid"] != GRID else "RUN_FULL_GRID" if chosen else "STOP_BUDGET",
        caveat="One light pilot only; metadata-scaled CPU projection is not a guarantee. 25% reserve plus 180 CPU-s; original full-grid pilot remains visible.")
    write_once(OUT/"pilot.json", rec)
    print(json.dumps(rec), flush=True)


def run():
    pred = load_prediction()
    plan = json.loads((OUT/"pilot.json").read_text())
    if not plan["selected_grid"]:
        print("STOP_BUDGET: no truth invocation beyond pilot")
        return
    start = time.process_time()
    prior = pred["prepare_cpu_seconds"]+plan["cpu_seconds"]
    cpu_guard(CPU_CAP-prior-90)
    receipts = []
    try:
        # Descending workload prevents a cheap-prefix completion being mistaken for full feasibility.
        for reg in sorted(pred["regimes"], key=lambda r:r["truth_work"], reverse=True):
            if reg["regime"] == pred["pilot"]:
                continue
            result = evaluate_record(reg, plan["selected_grid"], "main")
            write_once(OUT/"raw"/(reg["regime"]+".json"), result)
            receipts.append(dict(regime=reg["regime"], cpu_seconds=result["cpu_seconds"]))
            print(json.dumps(dict(event="regime_complete", **receipts[-1], remaining_cpu=CPU_CAP-prior-(time.process_time()-start))), flush=True)
    except BaseException as exc:
        write_once(OUT/"run_failure.json", dict(utc=stamp(), error_type=type(exc).__name__, error=str(exc),
                   cpu_seconds=time.process_time()-start, completed=receipts, rerun_permitted=False))
        raise
    write_once(OUT/"run_receipt.json", dict(created_utc=stamp(), cpu_seconds=time.process_time()-start,
        prior_cpu_seconds=prior, receipts=receipts, seed=None, mode="deterministic finite CTMC, no simulation"))


def score():
    pred = load_prediction()
    plan = json.loads((OUT/"pilot.json").read_text()) if (OUT/"pilot.json").exists() else {}
    grid = plan.get("selected_grid", [])
    raws = [json.loads(p.read_text()) for p in sorted((OUT/"raw").glob("*.json"))]
    rows, replays = [], []
    for raw in raws:
        if raw["prediction_sha256"] != sha(OUT/"predictions_before.json"):
            raise ValueError("prediction mismatch")
        replays.extend(dict(regime=raw["regime"], **r) for r in raw["replay"])
        for original in raw["rows"]:
            row = dict(original)
            if row["grid_kind"] == "MAIN" and not any(math.isclose(row["h_T_int"], h, rel_tol=1e-13) for h in grid):
                row["grid_kind"] = "PILOT_EXTRA"
            rows.append(row)
    fields = list(dict.fromkeys(k for row in rows for k in row))
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    write_once(OUT/"rows.csv", buf.getvalue())
    write_once(OUT/"reproduction.json", replays)
    main = [r for r in rows if r["grid_kind"] == "MAIN"]
    hybrids = [r for r in main if r["twin"] in ("T1", "T2")]
    d1 = [r for r in hybrids if r["above_threshold"]]
    d3 = [r for r in main if r["twin"].startswith("T3") and r["above_threshold"]]
    def collapse(seq):
        if not seq:
            return dict(verdict="NOT_EVALUABLE", eligible=0, passed=0)
        passed = sum(abs(r["G_S_abs"]) <= ARITH*r["C_ref"] and r["P_dis_upper"] <= PDIS_WIDTH for r in seq)
        return dict(verdict="PASS" if passed == len(seq) else "FAIL", eligible=len(seq), passed=passed)
    certified, unresolved, failed = 0, 0, 0
    for row in hybrids:
        lhs, mag = abs(row["G_S_abs"]), row["max_abs_true_gap"]
        if lhs <= row["P_dis_lower"]*mag + ARITH*row["C_ref"]:
            certified += 1
        elif lhs > row["P_dis_upper"]*mag + ARITH*row["C_ref"]:
            failed += 1
        else:
            unresolved += 1
    trends = []
    for reg in pred["regimes"]:
        for twin in ("T0", "T4"):
            subset = sorted([r for r in main if r["regime"] == reg["regime"] and r["twin"] == twin], key=lambda r:r["h"])
            if not subset:
                continue
            last = subset[-1]
            secant = (last["G_S_abs"]-subset[-2]["G_S_abs"])/(last["h"]-subset[-2]["h"]) if len(subset)>1 else None
            trends.append(dict(regime=reg["regime"], twin=twin, last_h_T_int=last["h_T_int"],
                slope_predicted=last["slope_predicted"], slope_measured=last["slope_measured"],
                relative_error=last["slope_relative_error"], last_secant=secant, G_S_abs=last["G_S_abs"],
                G_S_pct_C_ref=last["G_S_pct_C_ref"], P_dis=last["P_dis"],
                P_dis_lower=last["P_dis_lower"], P_dis_upper=last["P_dis_upper"],
                P_dis_predicted_inf=reg["T4"].get("P_dis_inf") if twin=="T4" else None))
    eligible_nc = [r for r in pred["regimes"] if r["T4"]["eligible"]]
    negative_nc = [r["regime"] for r in eligible_nc if r["T4"]["slope_predicted"] < 0]
    observed_harm = [r["regime"] for r in trends if r["twin"] == "T4" and r["slope_predicted"] < 0 and r["G_S_abs"] < 0 and r["last_secant"] is not None and r["last_secant"] < 0]
    verdicts = dict(D1=collapse(d1), D2=dict(verdict="FAIL" if failed else "PASS" if certified and not unresolved else "NOT_EVALUABLE",
        eligible=len(hybrids), certified=certified, unresolved=unresolved, failed=failed), D3=collapse(d3),
        D4=dict(verdict="FINITE_GRID_EVIDENCE_ONLY", regimes=sum(r["twin"]=="T0" for r in trends)),
        D5=dict(verdict="FINITE_GRID_EVIDENCE_ONLY", eligible_regimes=len(eligible_nc), skipped_regimes=12-len(eligible_nc),
                mixed_sign=sum(r["T4"]["mixed_sign"] for r in eligible_nc)),
        D6=dict(verdict="FINITE_GRID_EVIDENCE_ONLY" if negative_nc else "NOT_EVALUABLE", predicted_negative=negative_nc, observed_growing_harm=observed_harm))
    measured_cpu = pred["prepare_cpu_seconds"]+sum(r["cpu_seconds"] for r in raws)
    if (OUT/"run_failure.json").exists():
        fail = json.loads((OUT/"run_failure.json").read_text())
        # Failure command includes its completed raws; count it once.
        measured_cpu = pred["prepare_cpu_seconds"]+plan.get("cpu_seconds", 0)+fail["cpu_seconds"]
    elif (OUT/"run_receipt.json").exists():
        receipt = json.loads((OUT/"run_receipt.json").read_text())
        measured_cpu = receipt["prior_cpu_seconds"]+receipt["cpu_seconds"]
    summary = dict(created_utc=stamp(), verdicts=verdicts, plan=plan,
        completed_regimes=len(raws), expected_regimes=12, main_rows=len(main), total_rows=len(rows),
        measured_scientific_cpu_seconds=measured_cpu, measured_scientific_cpu_hours=measured_cpu/3600,
        reproduction_passed=sum(r["passed"] for r in replays), reproduction_total=len(replays),
        reproduction_max_relative_error=max((r["relative_error"] for r in replays), default=None),
        flags=[{k:r.get(k) for k in ("regime", "twin", "h_T_int", "flags")} for r in rows if r.get("flags") and r["grid_kind"]!="W1B_REPLAY"],
        trends=trends, prediction_sha256=sha(OUT/"predictions_before.json"),
        raw_sha256={p.name:sha(p) for p in sorted((OUT/"raw").glob("*.json"))})
    write_once(OUT/"summary.json", summary)
    lines = ["# R2-O1 — exploration phạm vi mệnh đề (P)", "", "Người phụ trách: **Doan Van Tai**. Không phải kết quả paper; không đổi verdict cũ.", "",
        f"Hoàn tất {len(raws)}/12 regime. Lưới chính sau pilot: `{grid}`; pilot giữ nguyên mọi mức ban đầu. Rows chính {len(main)}, tổng {len(rows)} (bao gồm replay/pilot riêng).",
        f"CPU scientific đo được: {measured_cpu:.6f} s = {measured_cpu/3600:.6f} CPU-h; ngân sách 7200 s. Command/tests/rescore overhead ghi riêng trong logs.", "",
        "| Dự đoán | Kết quả | Bằng chứng |", "|---|---|---|"]
    for name, rec in verdicts.items():
        lines.append(f"| {name} | {rec['verdict']} | `{json.dumps({k:v for k,v in rec.items() if k!='verdict'}, ensure_ascii=False)}` |")
    lines += ["", "D4–D6 nói về giới hạn nhưng brief không cho tolerance hội tụ. Bảng dưới báo sai số và xu hướng hữu hạn, không tự đặt ngưỡng PASS cho một giới hạn.", "",
        "| Regime | Twin | h/T_int cuối | slope dự đoán | G_S/h đo | sai số tương đối | secant cuối | G_S packet·s | G_S %C_ref | P_dis |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in trends:
        fmt = lambda v: "n/a" if v is None else f"{v:.9g}"
        lines.append("| "+" | ".join([r["regime"],r["twin"]]+[fmt(r[k]) for k in ("last_h_T_int","slope_predicted","slope_measured","relative_error","last_secant","G_S_abs","G_S_pct_C_ref","P_dis")])+" |")
    lines += ["", "## Regime, w* và ngưỡng trước truth", "",
        "| Regime | s thật | w* | T4 slope dự đoán | M_hat/|s| / T_int | M_hat/|s_MM1| / T_int | h_bar/T_int |",
        "|---|---:|---:|---:|---:|---:|---:|"]
    for r in pred["regimes"]:
        lines.append(f"| {r['regime']} | {r['s']:.9g} | {r['T4']['w_star']} | {r['T4'].get('slope_predicted')} | {r['threshold_T1']/r['T_int']:.9g} | {r['threshold_T2']/r['T_int']:.9g} | {r['h_bar']/r['T_int']:.9g} |")
    lines += ["", "## Kiểm chứng và giới hạn số học", "",
        f"- T0/W1b: {summary['reproduction_passed']}/{len(replays)} scalar G_S khớp tolerance tương đối 1e−9; max relative error {summary['reproduction_max_relative_error']}.",
        f"- Flag số học mới: {len(summary['flags'])}; xem `summary.json`. Không gọi deterministic là số học exact hoặc CTMC không cắt cụt.",
        "- P_dis dùng joint thật pi(Y) exp(Q0*tau), kể cả T3 kernel sai; không thay bằng |F_old−F_new|. Khi chỉ dùng marginals, báo cả hai đầu enclosure; nếu chưa đủ hẹp, dùng hai joint marginal path và 2D prefix CDF. Omission tối đa 1e−10 mỗi path, giữ nguyên full Q, không renormalize. Enclosure không bao floating-point error; check marginal/residual lưu raw.",
        "- D2 chấm bằng lower bound P_dis (có tolerance arithmetic 1e−9 C_ref); bất đồng nằm trong enclosure ghi UNRESOLVED. Không dùng upper bound để nhận PASS.",
        "- T3 thay kernel của **quyết định**, chi phí vẫn tính dưới posterior thật ở tuổi tau. Tie strict <0 → Stay; không epsilon.",
        "- 8 regime không có w thỏa điều kiện tải T4 được báo skipped, không thay w hoặc xóa khỏi 12-regime T0–T3 panel.",
        "- Không seed Monte Carlo: toàn bộ chi phí là finite CTMC. Các cells chung regime không phải thử nghiệm độc lập; không CI population.", "",
        "## Phạm vi của (P), không gọi là định lý", "",
        "Với K là probability kernel, |E_K b|≤M. Vì vậy h|s_hat|>M ép cùng dấu ở mọi state, cho coincidence và G_S=0. Cần phân biệt điều kiện đủ cho coincidence **ở mọi state/mọi K** với điều kiện cần để G_S=O(1).",
        "1. s_hat phải độc lập state và khác 0 là điều kiện đủ mạnh. Với s_hat=0, T0 có thể giữ slope khác 0 (xem dữ liệu); do đó chỉ thêm tên ‘stationary cost term’ không đủ. Dự đoán T4 tính trước cho biết khi slope phụ thuộc state có đổi dấu và DeltaF_inf khác 0 thì vẫn có thành phần O(h). Nếu DeltaF_inf=0 thì sign đổi riêng nó không chứng minh O(h).",
        "2. Constancy theo state không cần thiết: s_hat(x) cùng dấu và cách 0 ít nhất eta>0, với |b|≤M, cũng coincidence khi h>M/eta. Với finite support, cùng dấu strict tự cho eta>0. Mode slope bằng 0 cần xét b/tie riêng; không áp tự động D1.",
        "3. Bounded b là điều kiện đủ cho cutoff hữu hạn, không phải điều kiện cần của O(1). Ví dụ b(h,x)=sqrt(h)u(x) trên finite support vẫn o(h), nên nonzero common slope thắng cuối cùng. Ngược lại b(h,x)=h u(x) có thể tạo mixed-sign slope và bất đồng lâu dài; không thể bỏ mọi kiểm soát relative growth của remainder.",
        "4. Stationary-rate sign đúng với s thật không cần để G_S=0: hai rule có thể cùng chọn action sai. Cần sign đúng khi bàn regret, không khi chỉ bàn coincidence.",
        "5. K không cần đúng với posterior thật để áp cutoff; cần normalized, nonnegative. Signed hoặc không chuẩn hóa không còn là posterior kernel và không được bao trong từ ‘mọi K’.",
        "6. Uniformity over all states là yêu cầu của cutoff mọi state, không cần cho bounded expected G_S: cancellation DeltaF=0 (chẳng hạn plug-in dưới stationary X,Y) cũng cho G_S=O(1) nhờ gain–bias trên finite CTMC, dù P_dis có thể dương. Một hướng đủ khác là P_dis=O(1/h) khi max|true gap|=O(h).",
        "7. M_hat ở saturation không tự động là sup b cho một twin bất kỳ. Ở fluid model cụ thể này, từng path gap có dấu cố định và bounded bởi saturated path gap; empty low-mode cho gap 0, nên maximum network gap saturation là uniform bound. Code kiểm max gap tại các h thực chạy. Prop.2 của letter vẫn được ghi đúng max(h_bar,M_hat/|s_hat|).",
        "8. Finite irreducibility/bounded f bảo đảm gain–bias bounded trong mô hình này; không suy ra cùng bound cho infinite-buffer hoặc traffic thật. Phần đại số cutoff của (P) không cần CTMC, còn ‘horizon-linear true gap’ và phạm vi O(1) cần giả định chi phí riêng.", "",
        "## Provenance", "",
        f"Brief `{BRIEF}` SHA256 `{sha(BRIEF)}`. Predictions SHA256 `{sha(OUT/'predictions_before.json')}`.",
        "AI (Codex) triển khai và kiểm theo brief của Claude và ủy quyền tác giả; không phải tác giả tự chứng minh/độc lập human review. Source/W1b input hashes ở predictions; raw hashes ở summary. Không commit, SSH, sửa paper hoặc frozen verdict. Không tìm literature mới.",
        "File: `rows.csv`, `predictions_before.json`, `pilot.json`, `raw/*.json`, `reproduction.json`, `summary.json`; tests/logs/independent audit được ghi riêng khi thực chạy."]
    write_once(OUT/"SUMMARY.md", "\n".join(lines)+"\n")
    print(json.dumps({k:v for k,v in summary.items() if k not in ("trends", "raw_sha256")}, ensure_ascii=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "pilot", "run", "score"))
    args = parser.parse_args()
    globals()[args.command]()


if __name__ == "__main__":
    main()
