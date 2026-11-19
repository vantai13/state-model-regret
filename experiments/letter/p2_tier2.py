"""Doan Van Tai — P2-TIER2, descriptive replay of saved, exposed letter data.

No truth evaluator, new rollout, fitting, threshold selection or verdict change.
Only item 6 recomputes primitives: Stay stationary probabilities and fluid gaps.
Run with the virtualenv and experiments/explore_ctmc/env.sh sourced.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import sys
import time

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/letter/p2_tier2"
PAPER = Path("/home/vantai/state-model-regret-papers")
BRIEF = PAPER / "letter_smr/briefs/P2_TIER2_BRIEF.md"
LEDGER = PAPER / "letter_smr_argon/ledger"
CTMC_H = (1 / 3, 1, 3, 10, 30)
GEANT_H = (1, 2, 4, 7, 15, 30)
PIPES = ("M0", "Hybrid", "Stationary")
CHECKS = []


def sign(value):
    return int(value > 0) - int(value < 0)


def check(name, actual, expected=True, *, rtol=1e-10, atol=1e-10):
    if isinstance(actual, (float, np.floating)) and isinstance(expected, (int, float)):
        passed = math.isclose(actual, expected, rel_tol=rtol, abs_tol=atol)
    else:
        passed = actual == expected
    CHECKS.append(dict(name=name, passed=bool(passed), actual=actual, expected=expected))
    if not passed:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")


def stats(values):
    a = np.asarray(values, dtype=float)
    if not len(a):
        return dict(n=0, median=None, q25=None, q75=None, q90=None, mean=None,
                    minimum=None, maximum=None)
    if not np.isfinite(a).all():
        raise ArithmeticError("nonfinite saved or derived statistic")
    q25, med, q75, q90 = np.quantile(a, [.25, .5, .75, .9], method="linear")
    return dict(n=len(a), median=float(med), q25=float(q25), q75=float(q75),
                q90=float(q90), mean=float(a.mean()), minimum=float(a.min()),
                maximum=float(a.max()))


def signed_stats(values):
    a = np.asarray(values, dtype=float)
    return dict(stats(a), negative=int((a < 0).sum()), zero=int((a == 0).sum()),
                positive=int((a > 0).sum()), abs_le_0p1=int((np.abs(a) <= .1).sum()),
                below_minus_0p1=int((a < -.1).sum()), above_plus_0p1=int((a > .1).sum()))


def paired_row(hybrid, stationary, paired_se=None):
    delta = float(hybrid - stationary)
    tol = 1e-9 * max(abs(hybrid), abs(stationary))
    relative_equal = abs(delta) <= tol
    se_equal = paired_se is not None and abs(delta) <= 2 * paired_se
    label = "equal" if relative_equal or se_equal else "better" if delta < 0 else "worse"
    return dict(delta_pp=delta, hybrid=hybrid, stationary=stationary,
                relative_tolerance_pp=tol, paired_se_pp=paired_se,
                equal_relative=bool(relative_equal), equal_2se=bool(se_equal), comparison=label)


def stderr(values):
    a = np.asarray(values, dtype=float)
    return float(a.std(ddof=1) / math.sqrt(len(a)))


class Inputs:
    """Record the bytes actually read, and verify them again before publishing."""

    def __init__(self):
        self.hashes = {}

    def path(self, path):
        p = Path(path)
        return p if p.is_absolute() else ROOT / p

    def label(self, path):
        p = self.path(path)
        return str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)

    def register(self, path):
        p = self.path(path)
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        key = self.label(p)
        if key in self.hashes and self.hashes[key] != digest:
            raise RuntimeError(f"input changed during replay: {key}")
        self.hashes[key] = digest
        return p

    def text(self, path):
        return self.register(path).read_text()

    def js(self, path):
        return json.loads(self.text(path))

    def csv(self, path):
        return list(csv.DictReader(self.text(path).splitlines()))

    def npz(self, path):
        p = self.register(path)
        with np.load(p, allow_pickle=False) as z:
            return {k: z[k] for k in z.files}

    def verify(self):
        for p, digest in list(self.hashes.items()):
            check(f"input bytes unchanged: {p}", hashlib.sha256(self.path(p).read_bytes()).hexdigest(), digest)


def ct_observations(inputs):
    raws = [inputs.js(p) for p in sorted((ROOT / "results/letter/w1b/raw").glob("*.json"))]
    check("W1b completed regime count", len(raws), 93)
    summary = [r for r in inputs.csv("results/letter/w1b/summary.csv") if r["level"] == "true_s"]
    lookup = {(r["id"], r["age_label"], Fraction(r["h"])): r for r in summary}
    rows = []
    for d in raws:
        check(f"W1b completed {d['id']}", d["status"], "COMPLETED")
        for age in d["evaluations"]:
            for target in CTMC_H:
                h = min(age["h"], key=lambda r: abs(math.log(r["h_Tint"] / target)))
                distance = abs(math.log(h["h_Tint"] / target))
                if distance >= .02:
                    raise ValueError(f"no matched CTMC horizon: {d['id']} {target}")
                saved = lookup[d["id"], age["age_label"], Fraction(h["h"])]
                check(f"raw/summary GS {d['id']} {age['age_label']} {target}",
                      h["G_S"], float(saved["G_S_M0_age"]))
                reg = h["regret"]
                hybrid = h["hybrid_levels"]["true_s"]
                pipes = {}
                for pipe, gs, fresh, stale in (
                    ("M0", h["G_S"], reg["M0_new"], reg["M0_old"]),
                    ("Hybrid", hybrid["G_S"], hybrid["regret_new"], hybrid["regret_old"]),
                    ("Stationary", 0., reg["static"], reg["static"]),
                ):
                    pipes[pipe] = dict(GS=gs, fresh=fresh, stale=stale, both=max(fresh, stale))
                rows.append(dict(regime=d["id"], family=d["family"], s=d["s"],
                                 age_label=age["age_label"], tau_Tint=age["tau_Tint"],
                                 h_target=target, h_actual_Tint=h["h_Tint"], h=h["h"],
                                 baseline_available=saved["baseline_available"] == "True",
                                 flags=h["flags"], C_ref=h["Cref"], pipelines=pipes))
    check("CTMC selected observations", len(rows), 93 * 5 * 5)
    return raws, summary, rows


def fig3_table(ctrows, ledger):
    fresh = [r for r in ctrows if r["age_label"] == "Tint_1"]
    tables = {}
    for label, population in (("full93", fresh),
                              ("ledger92", [r for r in fresh if r["baseline_available"]])):
        table = []
        for h in CTMC_H:
            pop = [r for r in population if r["h_target"] == h]
            check(f"Fig3 {label} n h={h}", len(pop), 93 if label == "full93" else 92)
            for pipe in PIPES:
                gs = signed_stats([r["pipelines"][pipe]["GS"] for r in pop])
                both = stats([r["pipelines"][pipe]["both"] for r in pop])
                table.append(dict(h_Tint=h, pipeline=pipe, GS=gs, both_side_regret=both))
                if label == "ledger92":
                    if pipe != "Stationary":
                        key = "M0" if pipe == "M0" else "true_s"
                        old = ledger["F3"]["recomputed"][key][str(h)]
                        check(f"F3 {pipe} n {h}", len(pop), old["n"])
                        check(f"F3 {pipe} median GS {h}", gs["median"], old["median_GS"])
                    else:
                        old = ledger["F1_R13"]["recomputed"]["fig3_stationary"][str(h)]
                        check(f"F1_R13 stationary count {h}",
                              sum(r["pipelines"][pipe]["both"] <= .5 for r in pop), old["le_0p5"])
        tables[label] = table
    return dict(status="POST_HOC_EXPOSED", units="percent C_ref", quantile_method="linear",
                ledger_ids=["C1", "F3", "F1_R13"], new_statistics=["full93", "all IQR and regret distributions"],
                selection="age_label=Tint_1; one nearest actual h per target; abs(log(actual/target))<0.02",
                exception="F3 uses baseline_available and 92 regimes; the brief asks for all 93 saved W1b regimes",
                flagged_selected_observations=sum(bool(r["flags"]) for r in fresh),
                excluded_from_ledger92=sorted({r["regime"] for r in fresh if not r["baseline_available"]}),
                tables=tables, observations=fresh)


def geant_observations(inputs):
    rows, training_rates = [], {}
    errors = []
    for directory, seed in (("e4", 3000001), ("e4b", 5000001)):
        base = ROOT / "results/letter" / directory
        training = inputs.js(base / "training_checks.json")
        training_rates[seed] = {r["regime"]: r["rhat"]["i"] for r in training["regimes"]}
        csv_rows = {(r["regime"], float(r["tau_mult"]), int(r["h_mult"]), r["pipeline"]): r
                    for r in inputs.csv(base / "cells.csv")}
        for regime, rates in sorted(training_rates[seed].items()):
            paths = sorted((base / "raw").glob(f"{regime}_chunk*.npz"))
            check(f"{directory} {regime} chunks", len(paths), 10)
            pieces = []
            for p in paths:
                meta = inputs.js(p.with_suffix(".json"))
                z = inputs.npz(p)
                check(f"{directory}/{p.name} SHA", inputs.hashes[inputs.label(p)], meta["npz_sha256"])
                check(f"{directory}/{p.name} seed", meta["seed"], seed)
                check(f"{directory}/{p.name} nonpilot", meta["pilot"], False)
                pieces.append(z)
            z = dict(pieces[0])
            for key in ("V", "decisions", "tie_flags", "instance_id"):
                z[key] = np.concatenate([p[key] for p in pieces], axis=0)
            check(f"{directory} {regime} instance ids", z["instance_id"].tolist(), list(range(500)))
            names = z["pipelines"].tolist()
            hi_index = np.arange(len(z["h_mult"]))
            ref_choices = z["decisions"][:, names.index("M1_new"), 0, 0, :]
            ref = z["V"][np.arange(500)[:, None], ref_choices, hi_index].mean(axis=0)
            static_action = int(np.argmin(rates))
            static_costs = z["V"][:, static_action, :]
            for ti, tau in enumerate(z["tau_mult"]):
                by_pipe = {}
                for pipe, name in (("M0", "M0"), ("Hybrid", "Hybrid-i"), ("Stationary", None)):
                    if name is None:
                        costs = np.repeat(static_costs[:, None, :], 2, axis=1)
                    else:
                        choices = z["decisions"][:, names.index(name), :, ti, :]
                        costs = z["V"][np.arange(500)[:, None, None], choices, hi_index]
                    by_pipe[pipe] = costs
                for hi, h in enumerate(z["h_mult"]):
                    if not ref[hi] > 0:
                        raise ValueError("nonpositive GÉANT reference")
                    pipes = {}
                    for pipe, costs in by_pipe.items():
                        mean_sides = costs[:, :, hi].mean(axis=0)
                        regrets = 100 * (mean_sides - ref[hi]) / ref[hi]
                        gs = 100 * (mean_sides[1] - mean_sides[0]) / ref[hi]
                        pipes[pipe] = dict(GS=float(gs), fresh=float(regrets[0]), stale=float(regrets[1]),
                                           both=float(regrets.max()))
                        if pipe != "Stationary":
                            old = csv_rows[regime, float(tau), int(h), "M0" if pipe == "M0" else "Hybrid-i"]
                            for key, old_key in (("GS", "G_S_pct"), ("fresh", "regret_fresh_pct"),
                                                 ("stale", "regret_stale_pct")):
                                error = abs(pipes[pipe][key] - float(old[old_key]))
                                errors.append(error)
                                check(f"{directory} raw/CSV {regime} {tau} {h} {pipe} {key}",
                                      pipes[pipe][key], float(old[old_key]), atol=2e-9)
                    # Both-side regret = max of side means. Pair the selected worse
                    # hybrid side against the stationary cost on the same instance.
                    hybrid_sides = by_pipe["Hybrid"][:, :, hi]
                    worst_side = int(np.argmax(hybrid_sides.mean(axis=0)))
                    differences = 100 * (hybrid_sides[:, worst_side] - static_costs[:, hi]) / ref[hi]
                    comparison = paired_row(pipes["Hybrid"]["both"], pipes["Stationary"]["both"], stderr(differences))
                    rows.append(dict(dataset=directory, seed=seed, regime=regime, tau_Tint=float(tau),
                                     h_target=int(h), C_ref=float(ref[hi]), static_action=static_action,
                                     pipelines=pipes, paired=comparison, hybrid_worst_side=worst_side))
    check("GÉANT cells", len(rows), 2 * 17 * 3 * 6)
    return rows, training_rates, max(errors)


def fig4_table(rows, ledger):
    table = []
    for group in ("e4", "e4b", "both_seeds"):
        for h in GEANT_H:
            pop = [r for r in rows if r["tau_Tint"] == 1 and r["h_target"] == h
                   and (group == "both_seeds" or r["dataset"] == group)]
            for pipe in PIPES:
                table.append(dict(dataset=group, h_Tint=h, pipeline=pipe,
                                  GS=signed_stats([r["pipelines"][pipe]["GS"] for r in pop])))
            if group == "e4":
                old = ledger["F1_R13"]["recomputed"]["fig4_stationary"][str(h)]
                check(f"F1_R13 GÉANT stationary count {h}",
                      sum(r["pipelines"]["Stationary"]["both"] <= .5 for r in pop), old["le_0p5"])
    return dict(status="POST_HOC_EXPOSED", units="percent C_ref", tau_Tint=1,
                ledger_ids=["G0", "F1_R13"], new_statistics="signed distributions, IQR and counts",
                sign_counts="negative/zero/positive are strict; abs<=0.1 overlaps strict signs; band partition also saved",
                stationary="level-(i) training-rate argmin; same action on fresh and stale, hence GS=0",
                tables=table, observations=[r for r in rows if r["tau_Tint"] == 1])


def e6_replay(inputs, geant_rows, training_rates, ledger):
    lookup = {(r["seed"], r["regime"], r["tau_Tint"], r["h_target"]): r for r in geant_rows}
    rows, signs, record_rates = [], [], {}
    roundoff = []
    for p in sorted((ROOT / "results/letter/e6/raw").glob("*.npz")):
        seed_s, regime = p.stem.split("_", 1)
        seed = int(seed_s)
        check(f"E6 full-run seed {p.name}", seed in (3000001, 5000001))
        z = inputs.npz(p)
        check(f"E6 record count {p.name}", z["regret_hybrid"].shape[0], 200)
        for key in ("hybrid", "static"):
            derived = 100 * (z[f"cost_{key}"] - z["C_ref"]) / z["C_ref"]
            check(f"E6 {p.name} {key} cost/regret exact", np.array_equal(derived, z[f"regret_{key}"]))
        true_gap = training_rates[seed][regime][1] - training_rates[seed][regime][0]
        for li, L in enumerate(z["L_Tint"]):
            if L not in (100, 300):
                continue
            rates = z["record_rates"][:, li, :]
            record_rates[seed, regime, int(L)] = rates
            estimated_sign = np.sign(rates[:, 1] - rates[:, 0]).astype(int)
            for rep, estimated in enumerate(estimated_sign):
                signs.append(dict(seed=seed, regime=regime, L_Tint=int(L), record=int(rep),
                                  s_reference=float(true_gap), estimated_s=float(rates[rep, 1] - rates[rep, 0]),
                                  wrong=bool(estimated != sign(true_gap)), estimated_sign=int(estimated)))
            # Do not exchange mean_record and max_side.
            hybrid = z["regret_hybrid"][:, li].max(axis=1).mean(axis=0)
            stationary = z["regret_static"][:, li].mean(axis=0)
            for ti, tau in enumerate(z["tau_mult"]):
                for hi, h in enumerate(z["h_mult"]):
                    m0 = lookup[seed, regime, float(tau), int(h)]["pipelines"]["M0"]["both"]
                    check(f"E6/E4 reference {p.name} {h}",
                          float(z["C_ref"][hi]), lookup[seed, regime, float(tau), int(h)]["C_ref"])
                    row = dict(seed=seed, regime=regime, L_Tint=int(L), tau_Tint=float(tau),
                               h_target=int(h), M0=m0, Hybrid=float(hybrid[ti, hi]),
                               Stationary=float(stationary[hi]))
                    row["paired"] = paired_row(row["Hybrid"], row["Stationary"])
                    rows.append(row)
                    roundoff.extend(z["regret_hybrid"][:, li, :, ti, hi].ravel().tolist())
    for regime in training_rates[3000001]:
        for L in (100, 300):
            check(f"E6 same records across seeds {regime} L{L}",
                  np.array_equal(record_rates[3000001, regime, L], record_rates[5000001, regime, L]))
    check("E6 selected cell count", len(rows), 2 * 17 * 2 * 3 * 6)
    tables = []
    for L in (100, 300):
        for h in GEANT_H:
            pop = [r for r in rows if r["L_Tint"] == L and r["h_target"] == h]
            for pipe in PIPES:
                tables.append(dict(L_Tint=L, h_Tint=h, pipeline=pipe, regret=stats([r[pipe] for r in pop])))
    long = []
    expected_p90 = {100: {"Stationary": 28.845, "Hybrid": 28.786},
                    300: {"Stationary": 12.895, "Hybrid": 13.076}}
    score = inputs.js("results/letter/e6/score.json")
    for L in (100, 300):
        pop = [r for r in rows if r["L_Tint"] == L and r["h_target"] in (15, 30)]
        for pipe in PIPES:
            values = [r[pipe] for r in pop]
            result = dict(L_Tint=L, pipeline=pipe, regret=stats(values))
            long.append(result)
            if pipe != "M0":
                check(f"E6 prior P90 L{L} {pipe}", round(result["regret"]["q90"], 3), expected_p90[L][pipe])
                key = "hybrid" if pipe == "Hybrid" else "static"
                old = ledger["G20_R11"]["recomputed"]["by_L"][str(L)][key]
                for field in ("n", "median", "mean"):
                    check(f"G20_R11 L{L} {pipe} {field}", result["regret"][field], old[field])
                check(f"E6 saved score L{L} {pipe} median", result["regret"]["median"],
                      score["long"][str(L)][key]["median"])
            else:
                check(f"G20_R11 fluid median L{L}", result["regret"]["median"],
                      ledger["G20_R11"]["recomputed"]["fluid"]["median"])
    sign_tables = []
    for L in (100, 300):
        pop = [r for r in signs if r["L_Tint"] == L and r["seed"] == 3000001]
        by_regime = []
        for regime in sorted({r["regime"] for r in pop}):
            subset = [r for r in pop if r["regime"] == regime]
            by_regime.append(dict(regime=regime, n=len(subset), wrong=sum(r["wrong"] for r in subset)))
        wrong = sum(r["wrong"] for r in pop)
        sign_tables.append(dict(L_Tint=L, n_unique_records=len(pop), wrong=wrong,
                                wrong_fraction=wrong / len(pop), seed_appearances=2 * len(pop),
                                wrong_seed_appearances=2 * wrong, by_regime=by_regime))
    return dict(status="POST_HOC_EXPOSED", units="percent C_ref", ledger_ids=["G20_R11", "G22_R11"],
                new_statistics="IQR, P90, per-horizon distributions and sign-error counts",
                aggregation="mean_record(max(fresh regret, stale regret)) for hybrid; stationary mean_record; M0 max side means",
                ages_Tint=[.3, 1, 3], records_per_cell=200, cells_per_horizon_per_L=102,
                sign_reference="sign(rhat_i[Switch]-rhat_i[Stay]) from saved E4 training_checks; finite training reference",
                record_reuse="17*200=3400 unique records per L, reused exactly by both plant seeds, all ages and horizons",
                negative_saved_hybrid_regret_values=sum(v < 0 for v in roundoff),
                minimum_saved_hybrid_regret=min(roundoff), no_negative_clipping=True,
                tables=tables, long_h15_h30=long, sign_error=sign_tables, observations=rows, sign_records=signs)


def paired_tables(ctrows, geantrows, e6, ledger):
    details, tables = [], []

    def add(dataset, scope, h, pop):
        counts = Counter(r["paired"]["comparison"] for r in pop)
        differences = [r["paired"]["delta_pp"] for r in pop]
        table = dict(dataset=dataset, age_scope=scope, h_Tint=h, n=len(pop),
                     better=counts["better"], equal=counts["equal"], worse=counts["worse"],
                     delta=stats(differences), equal_relative=sum(r["paired"]["equal_relative"] for r in pop),
                     equal_2se_only=sum(r["paired"]["equal_2se"] and not r["paired"]["equal_relative"] for r in pop))
        tables.append(table)
        check(f"paired partition {dataset} {scope} {h}", sum(counts.values()), len(pop))

    for r in ctrows:
        details.append(dict(dataset="CTMC", regime=r["regime"], h_target=r["h_target"],
                            tau_Tint=r["tau_Tint"], age_label=r["age_label"],
                            paired=paired_row(r["pipelines"]["Hybrid"]["both"], r["pipelines"]["Stationary"]["both"])))
    for h in CTMC_H:
        for scope in ("tau=Tint", "all_saved_ages"):
            pop = [r for r in details if r["dataset"] == "CTMC" and r["h_target"] == h
                   and (scope == "all_saved_ages" or r["age_label"] == "Tint_1")]
            add("CTMC", scope, h, pop)
    details.extend(dict(dataset=r["dataset"], seed=r["seed"], regime=r["regime"],
                        h_target=r["h_target"], tau_Tint=r["tau_Tint"], paired=r["paired"]) for r in geantrows)
    for group in ("e4", "e4b", "GEANT_both_seeds"):
        for h in GEANT_H:
            for scope in ("tau=Tint", "all_saved_ages"):
                pop = [r for r in details if r["dataset"] in ("e4", "e4b") and r["h_target"] == h
                       and (group == "GEANT_both_seeds" or r["dataset"] == group)
                       and (scope == "all_saved_ages" or r["tau_Tint"] == 1)]
                add(group, scope, h, pop)
    for L in (100, 300):
        dataset = f"E6_L{L}"
        details.extend(dict(dataset=dataset, seed=r["seed"], regime=r["regime"],
                            h_target=r["h_target"], tau_Tint=r["tau_Tint"], paired=r["paired"])
                       for r in e6["observations"] if r["L_Tint"] == L)
        for h in GEANT_H:
            for scope in ("tau=Tint", "all_saved_ages"):
                pop = [r for r in details if r["dataset"] == dataset and r["h_target"] == h
                       and (scope == "all_saved_ages" or r["tau_Tint"] == 1)]
                add(dataset, scope, h, pop)
                if scope == "all_saved_ages":
                    old = ledger["G22_R11"]["recomputed"]["by_L"][str(L)][str(h)]
                    row = tables[-1]
                    check(f"G22_R11 delta mean L{L} h{h}", row["delta"]["mean"], old["paired_difference_mean"])
                    check(f"G22_R11 delta median L{L} h{h}", row["delta"]["median"], old["paired_difference_median"])
    return dict(status="POST_HOC_EXPOSED", units="percentage points C_ref (hybrid minus stationary)",
                ledger_ids=["G22_R11", "F3", "F1_R13"], new_statistics="paired comparison partitions by horizon",
                equality_rule="abs(delta)<=1e-9*max(abs(R_hybrid),abs(R_stationary)); no absolute floor; GEANT additionally abs(delta)<=2*paired_SE",
                GEANT_se="same 500 instance costs: choose hybrid side with larger sample mean; subtract fixed stationary-action cost; sample sd/sqrt(500), normalize by C_ref",
                caution="GEANT SE is descriptive after selecting the worse mean side; no hypothesis test or population CI",
                tables=tables, observations=details)


def sign_splits(raws, summary, ledger):
    harm = [r for r in summary if r["baseline_available"] == "True"
            and float(r["tau_Tint"]) >= 1 and float(r["h_Tint"]) >= 3]
    regret = [r for r in summary if float(r["tau_Tint"]) >= 1 and float(r["h_Tint"]) >= 1]
    ties = []
    for d in raws:
        age = next(a for a in d["evaluations"] if a["age_label"] == "Tint_1")
        h = min(age["h"], key=lambda r: abs(math.log(r["h_Tint"] / 30)))
        ties.append(dict(regime=d["id"], s=d["s"], h_actual_Tint=h["h_Tint"],
                         fresh=h["tie_mass"]["c10"], stale=h["tie_mass"]["c00"]))
    tables = []
    for label, sg in (("ALL", None), ("Switch-optimal (s<0)", -1), ("Stay-optimal (s>0)", 1), ("s=0", 0)):
        hp = [r for r in harm if sg is None or sign(float(r["s_true"])) == sg]
        rp = [r for r in regret if sg is None or sign(float(r["s_true"])) == sg]
        tp = [r for r in ties if sg is None or sign(r["s"]) == sg]
        harmed = sum(float(r["G_S_M0_age"]) < -.1 for r in hp)
        tables.append(dict(group=label, regimes=len({r["id"] for r in summary if sg is None or sign(float(r["s_true"])) == sg}),
                           harm_n=len(hp), harmful=harmed, harm_fraction=harmed / len(hp) if hp else None,
                           harm_GS=stats([float(r["G_S_M0_age"]) for r in hp]),
                           regret_n=len(rp), fresh_regret=stats([float(r["M0_new"]) for r in rp]),
                           stale_regret=stats([float(r["M0_old"]) for r in rp]),
                           tie_n=len(tp), fresh_tie=stats([r["fresh"] for r in tp]), stale_tie=stats([r["stale"] for r in tp])))
    allrow = tables[0]
    for field, value in (("n", allrow["harm_n"]), ("harmful", allrow["harmful"]),
                         ("fraction", allrow["harm_fraction"]), ("median_GS", allrow["harm_GS"]["median"])):
        check(f"C2_AGE {field}", value, ledger["C2_AGE"]["recomputed"][field])
    for field, value in (("n", allrow["regret_n"]), ("fresh", allrow["fresh_regret"]["median"]),
                         ("stale", allrow["stale_regret"]["median"])):
        check(f"C3 {field}", value, ledger["C3"]["recomputed"][field])
    for field, value in (("n", allrow["tie_n"]), ("fresh_tie_share", allrow["fresh_tie"]["median"]),
                         ("stale_tie_share", allrow["stale_tie"]["median"])):
        check(f"M2 {field}", value, ledger["M2"]["recomputed"][field])
    return dict(status="POST_HOC_EXPOSED", ledger_ids=["C2_AGE", "C3", "M2"],
                new_statistics="s<0/s>0 subgroup counts, harm, regret and tie distributions",
                harm_selection="true_s, baseline_available, actual tau/Tint>=1, actual h/Tint>=3; GS< -0.1%",
                regret_selection="true_s, actual tau/Tint>=1, actual h/Tint>=1; no baseline filter; repeated fresh across ages retained",
                tie_selection="all 93 regimes, Tint_1, nearest actual h/Tint to 30; saved exact tie_mass c10/c00",
                tables=tables, tie_observations=ties,
                harm_observations=[dict(regime=r["id"], s=float(r["s_true"]), age_label=r["age_label"],
                                        h=r["h"], GS=float(r["G_S_M0_age"])) for r in harm],
                regret_observations=[dict(regime=r["id"], s=float(r["s_true"]), age_label=r["age_label"],
                                          h=r["h"], fresh=float(r["M0_new"]), stale=float(r["M0_old"])) for r in regret])


def primitive_diagnostic(inputs, raws):
    """Only stationary pi under Stay and fluid gaps; never construct Chain or V."""
    from scipy.sparse.linalg import splu
    from experiments.explore_ctmc.ctmc import generator, m0_gap, m0_vhat

    inputs.register("experiments/explore_ctmc/ctmc.py")
    start = time.process_time()

    def timeout(signum, frame):
        raise TimeoutError("item 6 reached its 3600 CPU-second cap")

    old = signal.signal(signal.SIGPROF, timeout)
    signal.setitimer(signal.ITIMER_PROF, 3600)
    cache, rows = {}, []
    try:
        for d in raws:
            t0 = time.process_time()
            la, lb, u, k, c = (Fraction(x) for x in d["case"]["parameters"])
            age1 = next(a for a in d["evaluations"] if a["age_label"] == "Tint_1")
            amplitude = Fraction(str(age1["a"]))
            if float(c) != 0:
                raise ValueError("unexpected nonzero switching cost in W1b")
            parts, pis, residuals, drain = {}, {}, {}, []
            for path, load, lower, side in (("A", la + u, la, "A"), ("B", lb, lb, "B")):
                N = int(age1["N"][path])
                key = (load, k, N, amplitude)
                if key not in cache:
                    Q = generator(load, k, N, a=amplitude, mu=age1["mu"])
                    QT = Q.T.tocsc()
                    x = splu(QT[1:, 1:].tocsc()).solve(-QT[1:, 0].toarray().ravel())
                    pi = np.r_[1., x]
                    pi /= pi.sum()
                    residual = float(np.max(np.abs(pi @ Q)))
                    if pi.min() < -1e-12 or residual > 1e-9:
                        raise ArithmeticError("invalid stationary probabilities")
                    cache[key] = pi, residual
                pi, residual = cache[key]
                gap = m0_gap(lower, u, k, N, [math.inf], side, a=amplitude)[0]
                parts[path] = float(pi @ gap)
                pis[path] = hashlib.sha256(pi.tobytes()).hexdigest()
                residuals[path] = residual
                for action_load in (lower, lower + u):
                    _, T = m0_vhat(action_load, k, N, [math.inf], a=amplitude, return_T=True)
                    drain.append(float(T.max()))
            m0 = parts["A"] + parts["B"] + float(c)
            record = dict(regime=d["id"], family=d["family"], parameters=d["case"]["parameters"],
                          amplitude=float(amplitude), N=age1["N"], s=d["s"], m0=m0,
                          sign_m0=sign(m0), sign_s=sign(d["s"]), signs_agree=sign(m0) == sign(d["s"]),
                          components=parts, pi_sha256=pis, stationary_residual=residuals,
                          maximum_drain_time_on_truncated_support=max(drain), cpu_s=time.process_time() - t0,
                          stale={})
            for label, age_target in (("Tint_1", 1), ("Tint_3", 3)):
                age = next(a for a in d["evaluations"] if a["age_label"] == label)
                h = min(age["h"], key=lambda r: abs(math.log(r["h_Tint"] / 30)))
                # a_inf is Switch iff stored s<0; dep_static already includes
                # strict tie-to-Stay behavior for either optimal-action group.
                infinite_good = age["asymptotic"]["F_old"] if d["s"] < 0 else 1 - age["asymptotic"]["F_old"]
                record["stale"][str(age_target)] = dict(
                    long_run_action_share=1 - h["dep_static"]["M0_old"],
                    fresh_long_run_action_share=1 - h["dep_static"]["M0_new"],
                    h_actual_Tint=h["h_Tint"], limiting_fluid_gap_share=infinite_good,
                    observed_h_beyond_all_support_drain=float(Fraction(h["h"])) >= max(drain))
            rows.append(record)
    finally:
        signal.setitimer(signal.ITIMER_PROF, 0)
        signal.signal(signal.SIGPROF, old)
    table = []
    for group, sg in (("ALL", None), ("Switch-optimal (s<0)", -1), ("Stay-optimal (s>0)", 1)):
        pop = [r for r in rows if sg is None or r["sign_s"] == sg]
        table.append(dict(group=group, n=len(pop), sign_agree=sum(r["signs_agree"] for r in pop),
                          sign_disagree=sum(not r["signs_agree"] for r in pop),
                          m0=stats([r["m0"] for r in pop]),
                          stale_tau1=stats([r["stale"]["1"]["long_run_action_share"] for r in pop]),
                          stale_tau3=stats([r["stale"]["3"]["long_run_action_share"] for r in pop]),
                          limiting_tau1=stats([r["stale"]["1"]["limiting_fluid_gap_share"] for r in pop]),
                          limiting_tau3=stats([r["stale"]["3"]["limiting_fluid_gap_share"] for r in pop])))
    confusion = Counter((r["sign_s"], r["sign_m0"]) for r in rows)
    return dict(status="POST_HOC_TRUE_PI_DIAGNOSTIC", ledger_ids=["M1", "M2"],
                new_statistics="m0, primitive signs and tau=3 long-run-action diagnostics",
                definition="m0=E_piStayA[fluid gap_A(infinity)]+E_piStayB[fluid gap_B(infinity)]+c",
                gap_units="packet seconds", s_units="packets (stationary mean backlog difference)",
                cap_cpu_s=3600, cpu_s=time.process_time() - start,
                method="saved N and amplitude; existing CTMC generator and fluid routines; direct sparse stationary solve only; no Chain, Poisson bias, V, true-cost rollout or new actual cost",
                raw_arrays_available=False, finite_support_caveat="infinity is saturated fluid cost on the saved truncated CTMC support; no uniform finite drain bound on unbounded states",
                caveat="uses true Stay stationary law pi0; exposed diagnostic, not out-of-sample prediction; compare m0 with stored s, do not recompute s",
                stale_share_selection="nearest h approximately 30 Tint at each requested age; additionally report exact h->infinity fluid-decision shares from saved asymptotic",
                tables=table, confusion=[dict(sign_s=a, sign_m0=b, n=n) for (a, b), n in sorted(confusion.items())],
                observations=rows)


def denominators(inputs, ledger):
    rows = inputs.csv("results/letter/v7_3/test_congested/score_dev1/cases.csv")
    card = inputs.js("results/letter/v7_3/card_v7_3_params.json")
    inputs.register("results/letter/v7_3/CARD_V7_3.md")
    inputs.register("results/letter/v7_3/DEVIATION_V7_3_01.md")
    keys = [(r["regime"], r["date"], int(r["h_hours"]), int(r["tau_s"])) for r in rows]
    check("V7-3 unique case keys", len(set(keys)), len(rows))
    expected_regimes = set(card["regimes"])
    dates = sorted({r["date"] for r in rows})
    check("V7-3 usable days", len(dates), 49)
    check("V7-3 all case count", len(rows), 49 * 3 * 4 * 2)
    by_flow = []
    for regime in sorted(expected_regimes):
        pop = [r for r in rows if r["regime"] == regime]
        record = dict(regime=regime, days=len({r["date"] for r in pop}), S_days=0, O_days=0)
        for stratum in ("S", "O"):
            sub = [r for r in pop if r["stratum"] == stratum]
            record[f"{stratum}_days"] = len({r["date"] for r in sub})
            record[f"{stratum}_cases"] = len(sub)
            record[f"{stratum}_evaluable"] = sum(r["evaluable"] == "True" for r in sub)
        by_flow.append(record)
    s_primary = [r for r in rows if r["regime"] in card["confirmatory_regimes"]
                 and r["stratum"] == "S" and int(r["h_hours"]) in card["test_horizons_hours"]]
    confirmatory = [r for r in s_primary if r["evaluable"] == "True"]
    overload = [r for r in rows if r["stratum"] == "O"]
    o_eval = [r for r in overload if r["evaluable"] == "True"]
    fresh_keys = {(r["regime"], r["date"], int(r["h_hours"])) for r in confirmatory}
    n_instances = card["N_test"]
    check("V73_DENOM primary total", len(s_primary), ledger["V73_DENOM"]["recomputed"]["stable_DAY1_DAY2_2_6h"]["cases"])
    check("V73_DENOM primary evaluable", len(confirmatory), 76)
    check("V73_DENOM overload total", len(overload), 480)
    check("V73_DENOM overload evaluable", len(o_eval), 408)
    check("V73_ATTRIB unique record-horizons", len(fresh_keys), 38)
    check("V73_ATTRIB unique fresh decisions", len(fresh_keys) * n_instances,
          ledger["V73_ATTRIB"]["recomputed"]["by_side"]["fresh"]["unique_decisions"])
    check("V73_STRATA primary cases", len(confirmatory), ledger["V73_STRATA"]["recomputed"]["confirmatory"]["cases"])
    per_h = []
    for h in card["hours"]:
        sub = [r for r in confirmatory if int(r["h_hours"]) == h]
        fresh = {(r["regime"], r["date"], int(r["h_hours"])) for r in sub}
        per_h.append(dict(h_hours=h, primary_cases=len(sub), unique_record_horizons=len(fresh),
                          unique_fresh_decisions=len(fresh) * n_instances,
                          stale_decisions=len(sub) * n_instances))
    per_day = []
    for regime, date in sorted({(r["regime"], r["date"]) for r in confirmatory}):
        sub = [r for r in confirmatory if r["regime"] == regime and r["date"] == date]
        per_day.append(dict(regime=regime, date=date, cases=len(sub),
                            horizons_hours=sorted({int(r["h_hours"]) for r in sub})))
    return dict(status="SAVED_AMENDED_ANALYSIS", ledger_ids=["V73_SETUP", "V73_STRATA", "V73_DENOM", "V73_ATTRIB"],
                new_statistics="factorized denominator and per-flow/per-horizon/per-day tables; headline counts already in ledger",
                days=49, excluded_day="2005-06-27", original_run="INCOMPLETE; DEVIATION_V7_3_01 retained",
                by_flow=by_flow, horizons_hours=card["hours"], primary_horizons_hours=card["test_horizons_hours"],
                ages_seconds=card["tau_seconds"], instances_per_record=n_instances,
                numbers=dict(primary_stable_candidates=len(s_primary), primary_stable_evaluable=len(confirmatory),
                             overload_candidates=len(overload), overload_evaluable=len(o_eval),
                             unique_fresh_record_horizons=len(fresh_keys), unique_fresh_decisions=len(fresh_keys) * n_instances,
                             stale_decisions=len(confirmatory) * n_instances, all_cases=len(rows)),
                factorizations={"348": "29 S days * 2 flows (DAY1/DAY2) * 3 horizons (2,4,6h) * 2 ages",
                                "480": "20 O days * 3 flows * 4 horizons (1,2,4,6h) * 2 ages",
                                "408": "O cases surviving C_ref/h evaluability; per-flow "
                                       + "+".join(str(r["O_evaluable"]) for r in by_flow)
                                       + ", not a full fixed-day rectangle",
                                "76": "primary S cases surviving C_ref/h gate: 16 at 2h + 28 at 4h + 32 at 6h",
                                "1216": "38 unique flow-day-horizon tuples * 32 instances; fresh counted once across two ages"},
                gate=dict(mean_backlog_Mbit=card["evaluable_threshold_Mbit"], rule=card["evaluable_rule"]),
                DAY3_role="predeclared near-zero training-slope control; descriptive, outside H1-H3 population",
                h1_role="predeclared descriptive sensitivity; outside H1-H3 horizons 2,4,6h",
                per_horizon=per_h, primary_by_day=per_day)


def make_figures(out, inputs, fig3, fig4):
    os.environ["MPLCONFIGDIR"] = str(out / "mplconfig")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    p = inputs.register(PAPER / "letter_smr/figures/fig4_geant.pdf")
    box = re.search(rb"/MediaBox\s*\[([^]]+)\]", p.read_bytes())
    if box is None:
        raise ValueError("reference PDF MediaBox not found")
    bounds = [float(x) for x in box.group(1).split()]
    width_pt = bounds[2] - bounds[0]
    width = width_pt / 72
    colors = {"M0": "#b33c32", "Hybrid": "#246a9d", "Stationary": "#4c8050"}
    plt.rcParams.update({"font.size": 7, "axes.labelsize": 7, "axes.titlesize": 7,
                         "xtick.labelsize": 6, "ytick.labelsize": 6, "legend.fontsize": 6,
                         "pdf.fonttype": 42, "savefig.bbox": None})
    fig, ax = plt.subplots(figsize=(width, 2.9))
    offsets = {"M0": -.24, "Hybrid": 0, "Stationary": .24}
    for pi, pipe in enumerate(PIPES):
        for si, dataset in enumerate(("e4", "e4b")):
            for hi, h in enumerate(GEANT_H):
                vals = [r["pipelines"][pipe]["GS"] for r in fig4["observations"]
                        if r["dataset"] == dataset and r["h_target"] == h]
                x = hi + offsets[pipe] + (-.045 if si == 0 else .045)
                # Fixed index spacing, not random resampling or jitter draws.
                ax.scatter(x + np.linspace(-.025, .025, len(vals)), vals, s=7,
                           marker="o" if si == 0 else "^", color=colors[pipe], alpha=.42,
                           linewidths=0, zorder=3)
                med, q1, q3 = np.quantile(vals, [.5, .25, .75])
                ax.plot([x, x], [q1, q3], color=colors[pipe], lw=1.6)
                ax.plot([x - .035, x + .035], [med, med], color="black", lw=.65)
    ax.axhline(0, color="black", lw=.6)
    ax.set_xticks(range(6), [str(h) for h in GEANT_H])
    ax.set_xlabel(r"$h/T_{\rm int}$")
    ax.set_ylabel(r"Signed $G_S$ (% $C_{\rm ref}$)")
    ax.set_title(r"GÉANT: 17 regimes, two seeds; $\tau=T_{\rm int}$")
    ax.grid(axis="y", alpha=.2)
    handles = [Line2D([0], [0], color=colors[p], lw=2, label=p) for p in PIPES]
    handles.extend(Line2D([0], [0], marker=m, ls="", color="gray", markersize=3, label=s)
                   for m, s in (("o", "seed 3000001"), ("^", "seed 5000001")))
    ax.legend(handles=handles, loc="best", framealpha=.8)
    fig.subplots_adjust(left=.20, right=.98, bottom=.17, top=.91)
    fig.savefig(out / "fig4a_signed_candidate.pdf", metadata={"Author": "Doan Van Tai", "Title": "Post-hoc signed G_S candidate"})
    fig.savefig(out / "fig4a_signed_candidate.png", dpi=180)
    plt.close(fig)
    fig, axes = plt.subplots(2, 1, figsize=(width, 3.55), sharex=True)
    for pipe in PIPES:
        selected = [r for r in fig3["tables"]["full93"] if r["pipeline"] == pipe]
        for ax, key in zip(axes, ("GS", "both_side_regret")):
            med = np.array([r[key]["median"] for r in selected])
            q1 = np.array([r[key]["q25"] for r in selected])
            q3 = np.array([r[key]["q75"] for r in selected])
            x = np.arange(5) + offsets[pipe] * .5
            ax.errorbar(x, med, yerr=[med - q1, q3 - med], fmt="o-", markersize=2.6,
                        capsize=2, lw=.8, color=colors[pipe], label=pipe)
    axes[0].axhline(0, color="black", lw=.6)
    axes[0].set_ylabel(r"Signed $G_S$ (% $C_{\rm ref}$)")
    axes[1].set_ylabel(r"Both-side regret (% $C_{\rm ref}$)")
    axes[0].set_title(r"CTMC: 93 saved regimes; $\tau=T_{\rm int}$")
    axes[0].legend(ncol=3, frameon=False, loc="best")
    for ax in axes:
        ax.grid(axis="y", alpha=.2)
    axes[1].set_xticks(range(5), ["1/3", "1", "3", "10", "30"])
    axes[1].set_xlabel(r"$h/T_{\rm int}$ (nearest saved horizon)")
    fig.subplots_adjust(left=.20, right=.98, bottom=.12, top=.93, hspace=.16)
    fig.savefig(out / "fig3_iqr_candidate.pdf", metadata={"Author": "Doan Van Tai", "Title": "Post-hoc CTMC median and IQR candidate"})
    fig.savefig(out / "fig3_iqr_candidate.png", dpi=180)
    plt.close(fig)
    return dict(width_points=width_pt, reference_pdf=str(p), signed_figure_height_inches=2.9,
                fig3_height_inches=3.55, axes_scale="linear, no clipping",
                signed_figure="strip of every regime/seed, per-seed median and IQR; strict signed GS",
                fig3_figure="full93, median and IQR; ledger92 reconciliation in JSON")


def fmt(value):
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def mdtable(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |",
                      "| " + " | ".join("---" for _ in headers) + " |",
                      *("| " + " | ".join(fmt(v) for v in row) + " |" for row in rows)])


def write_summary(out, f3, f4, e6, paired, splits, primitive, denom, meta):
    sections = ["# P2-TIER2 — phân tích mô tả hậu kiểm\n",
                "Người phụ trách: **Doan Van Tai**. Triển khai và phân tích có AI hỗ trợ theo brief P2-TIER2 ngày 19/11/2026. "
                "Toàn bộ kết quả dưới đây là **post-hoc, exposed**; không phải kiểm định mới, không đổi verdict hoặc ngưỡng đã khóa. "
                "Các ô dùng chung regime, instances, records, tuổi hoặc horizon; mẫu số không phải các phép thử độc lập. "
                "Không suy population CI. Quantile dùng nội suy tuyến tính. Regret và GS tính bằng % C_ref; chênh lệch tính bằng percentage points (pp).\n",
                "## 1. Fig. 4(a) có dấu — GÉANT\n",
                "**MỚI:** phân phối có dấu và IQR; hai seed 3000001/5000001, 17 regime/seed/h, τ=T_int. "
                "Bảng dưới gộp hai seed để mô tả (n=34), không coi là 34 regime độc lập. "
                "JSON giữ thêm từng seed và mọi điểm. Stationary dùng argmin rate level-(i) đã lưu và có GS=0 chính xác. "
                "ID đối chiếu: G0, F1_R13.\n"]
    sections.append(mdtable(["h/T_int", "Pipeline", "n", "Median", "Q25", "Q75", "Âm / 0 / dương", "|GS|≤0.1%"],
                            [[r["h_Tint"], r["pipeline"], r["GS"]["n"], r["GS"]["median"], r["GS"]["q25"], r["GS"]["q75"],
                              f"{r['GS']['negative']}/{r['GS']['zero']}/{r['GS']['positive']}", r["GS"]["abs_le_0p1"]]
                             for r in f4["tables"] if r["dataset"] == "both_seeds"]))
    sections.extend(["\nÂm/dương là dấu nghiêm ngặt, kể cả sai số rất nhỏ; |GS|≤0.1% chồng lấp với số âm/dương. "
                     "JSON có phân hoạch không chồng lấp <-0.1 / [-0.1,0.1] / >0.1.\n",
                     "File: `fig4a_signed.json`, `fig4a_signed_candidate.pdf` và `.png`. Hình giữ dấu, không cắt outlier, "
                     f"rộng {meta['figure_geometry']['width_points']:.3f} pt đúng MediaBox của hình tham chiếu; không sửa hình paper.\n",
                     "## 2. Fig. 3 có IQR — CTMC\n",
                     "**MỚI:** IQR/median regret và tập full93 đúng brief. Có 93 W1b raw hoàn tất, nhưng F3 trong ledger "
                     "lọc `baseline_available`, còn 92 regime. File mới cung cấp cả `full93` và `ledger92`; F3/F1_R13 "
                     "được đối chiếu trên ledger92, không âm thầm đổi số cũ. Regime chỉ thiếu baseline cũ: "
                     f"`{f3['excluded_from_ledger92'][0]}`; kết quả age-only W1b của regime này đã lưu đầy đủ. "
                     "Chọn horizon gần nhất trong abs(log(actual/target))<0.02, không dùng giá trị h làm tròn để lọc các claim C2/C3.\n"])
    sections.append(mdtable(["h/T_int", "Pipeline", "GS median [Q25,Q75]", "Both-side regret median [Q25,Q75]"],
                            [[r["h_Tint"], r["pipeline"],
                              f"{fmt(r['GS']['median'])} [{fmt(r['GS']['q25'])}, {fmt(r['GS']['q75'])}]",
                              f"{fmt(r['both_side_regret']['median'])} [{fmt(r['both_side_regret']['q25'])}, {fmt(r['both_side_regret']['q75'])}]"]
                             for r in f3["tables"]["full93"]]))
    sections.extend(["\nFile: `fig3_iqr.json`, `fig3_iqr_candidate.pdf` và `.png`. ID: C1/F3/F1_R13; full93 là MỚI, không thay figure paper.\n",
                     "## 3. Replay E6 — finite-record rates\n",
                     "Mỗi ô: mean_record(max(regret_fresh,regret_stale)) cho Hybrid; stationary mean_record cùng records. "
                     "M0 dùng max của hai side means đã lưu E4/E4b. Mỗi h,L có 102 ô = 2 seeds×17 regimes×3 ages, mỗi ô 200 records; "
                     "M0 lặp theo L vì không dùng rate estimate. **MỚI:** Q25/Q75/Q90 và sign-error breakdown. "
                     "Median/mean trùng G20_R11/G22_R11 đã kiểm lại. Giữ regret âm đã lưu, không clip. "
                     f"Có {e6['negative_saved_hybrid_regret_values']} lượt giá trị Hybrid âm trong các record×side×age×h×seed ở L=100/300, "
                     f"minimum {e6['minimum_saved_hybrid_regret']:.9f}% C_ref. Đây là các lượt lặp, không phải số record độc lập; "
                     "C_ref dùng saved M1_new decisions, không thay bằng pointwise min của V. Không suy từ ước lượng âm rằng regret thật âm hoặc có bug.\n"])
    sections.append(mdtable(["L/T_int", "h/T_int", "Pipeline", "Median", "Q25", "Q75", "P90"],
                            [[r["L_Tint"], r["h_Tint"], r["pipeline"], *(r["regret"][k] for k in ("median", "q25", "q75", "q90"))]
                             for r in e6["tables"]]))
    sections.append("\nĐối chiếu P90 đã có trong brief, gộp h∈{15,30} (204 ô/L), **không phải** P90 của mọi record riêng lẻ:\n")
    sections.append(mdtable(["L/T_int", "Pipeline", "Median", "P90 (% C_ref)"],
                            [[r["L_Tint"], r["pipeline"], r["regret"]["median"], r["regret"]["q90"]]
                             for r in e6["long_h15_h30"]]))
    sections.append("\nTỷ lệ dấu sai so với sign(rhat_i[Switch]−rhat_i[Stay]) từ training E4 đã lưu, không phải dấu từ một truth run mới:\n")
    sections.append(mdtable(["L/T_int", "Sai / unique records", "Tỷ lệ", "Số lượt khi lặp hai plant seed"],
                            [[r["L_Tint"], f"{r['wrong']}/{r['n_unique_records']}", r["wrong_fraction"], r["seed_appearances"]]
                             for r in e6["sign_error"]]))
    sections.extend(["\n17/17 regime dùng cùng record_rates ở hai seed: 3400 unique records/L; 6800 là số lượt xuất hiện. "
                     "File `e6_replay.json` giữ bảng theo regime, record và cell.\n",
                     "## 4. So cặp Hybrid − Stationary theo h\n",
                     "**MỚI:** số tốt hơn/bằng/tệ hơn. Δ<0 nghĩa Hybrid ít regret hơn. Bằng nếu "
                     "|Δ|≤1e−9 max(|R_H|,|R_S|), không có absolute floor; với GÉANT thêm |Δ|≤2 paired SE. "
                     "Paired SE lấy từ chênh chi phí trên cùng 500 instances, sau khi chọn side Hybrid có mean cost lớn hơn, "
                     "rồi chuẩn hóa C_ref. Đây chỉ là độ phân giải mô tả sau chọn worse side, không phải kiểm định. "
                     "Vì relative tolerance không có floor, chênh cực nhỏ khi một regret gần 0 vẫn có thể phân loại tốt/tệ; xem Δ đầy đủ trong JSON. "
                     "CTMC/GÉANT trong bảng dùng τ=T_int; E6 dùng cả 3 tuổi như G22_R11. JSON có cả τ=T_int và all_saved_ages cho mọi nguồn, cùng từng seed GÉANT.\n"])
    chosen = [r for r in paired["tables"] if (r["dataset"] in ("CTMC", "e4", "e4b", "GEANT_both_seeds") and r["age_scope"] == "tau=Tint")
              or (r["dataset"].startswith("E6_") and r["age_scope"] == "all_saved_ages")]
    sections.append(mdtable(["Nguồn", "h/T_int", "n", "Tốt hơn / bằng / tệ hơn", "Median Δ (pp)", "Mean Δ (pp)", "Bằng chỉ nhờ 2SE"],
                            [[r["dataset"], r["h_Tint"], r["n"], f"{r['better']}/{r['equal']}/{r['worse']}",
                              r["delta"]["median"], r["delta"]["mean"], r["equal_2se_only"]] for r in chosen]))
    sections.extend(["\nFile `paired_by_h.json`; ID G22_R11 đối chiếu mean và median Δ E6 theo từng h,L. "
                     "Median chênh lệch cặp không phải chênh của hai median.\n",
                     "## 5. Tách Switch-optimal và Stay-optimal\n",
                     "**MỚI:** bảng subgroup; tổng C2_AGE/C3/M2 giữ đúng ledger. s là rate gap dài hạn, "
                     "không phải optimal action tại mọi state/h hữu hạn. C2_AGE giữ baseline_available và τ/T_int≥1, h/T_int≥3, "
                     "harm nếu GS<−0.1%; C3 giữ τ/T_int≥1, h/T_int≥1, không thêm baseline filter. "
                     "Các dòng seconds_1 được giữ nếu actual ratio thỏa điều kiện. Tie M2: 93 regime, τ=T_int, h≈30T_int, "
                     "median exact tie_mass fresh/stale.\n"])
    sections.append(mdtable(["Nhóm", "Regime", "C2: harm/n", "Tỷ lệ", "C2 median GS", "C3 n", "C3 median fresh / stale", "M2 n", "Tie fresh / stale"],
                            [[r["group"], r["regimes"], f"{r['harmful']}/{r['harm_n']}", r["harm_fraction"],
                              r["harm_GS"]["median"], r["regret_n"],
                              f"{fmt(r['fresh_regret']['median'])}/{fmt(r['stale_regret']['median'])}", r["tie_n"],
                              f"{fmt(r['fresh_tie']['median'])}/{fmt(r['stale_tie']['median'])}"] for r in splits["tables"]]))
    sections.extend(["\nTie là probability share [0,1], không phải % C_ref. Median tổng không là trung bình có trọng số của median nhóm. "
                     "File `optimal_sign_splits.json`.\n",
                     "## 6. Dấu từ primitives: m₀ và π₀\n",
                     "**MỚI — chẩn đoán dùng π₀ thật, không phải dự báo ngoài mẫu.** Raw W1b không có mảng π/gap. "
                     "Đã dùng generator và fluid functions CTMC hiện có với N/amplitude đã lưu; giải π dưới Stay trên hai path. "
                     "m₀=Eπ_A[gap_A(∞)]+Eπ_B[gap_B(∞)]+c, đơn vị packet·s; s dùng nguyên từ raw, đơn vị packet. "
                     "Không gọi Chain, Poisson bias, V, evaluator, chi phí thật hay rollout mới. "
                     "∞ chỉ cách lấy fluid gap sau drain; không khẳng định h̄ đồng nhất trên không gian trạng thái không chặn. "
                     f"CPU mục này {primitive['cpu_s']:.6f}s, cap 3600 CPU-s.\n"])
    sections.append(mdtable(["Nhóm", "n", "Dấu m₀ khớp / khác dấu s", "Median m₀ (packet·s)", "Median stale good-action τ=T_int", "τ=3T_int"],
                            [[r["group"], r["n"], f"{r['sign_agree']}/{r['sign_disagree']}", r["m0"]["median"],
                              r["stale_tau1"]["median"], r["stale_tau3"]["median"]] for r in primitive["tables"]]))
    sections.append("\nConfusion matrix (dấu nghiêm ngặt, không epsilon):\n")
    sections.append(mdtable(["sign(s)", "sign(m₀)", "n"], [[r["sign_s"], r["sign_m0"], r["n"]] for r in primitive["confusion"]]))
    sections.extend(["\nStale good-action share trong bảng dùng h gần 30T_int của từng regime/tuổi, không thay bằng m₀ sign. "
                     "JSON có cả h thực, limiting fluid-decision share từ saved asymptotic, residual π và SHA từng π. "
                     "M₀ trung bình chỉ mô tả cực hạn khi stale mất thông tin; tại tuổi hữu hạn cần phân phối conditional gap. "
                     "File `primitive_signs.json`; M1/M2 là provenance cho shares/ties đã lưu, m₀ chưa có ledger.\n",
                     "## 7. Mẫu số V-C\n",
                     "Các số headline đã có V73_DENOM/V73_STRATA/V73_ATTRIB; **MỚI:** phép phân rã và bảng chi tiết dưới đây. "
                     "Theo cases.csv và card: N=32 instances/record; 2 tuổi 300/900s; h={1,2,4,6}h; H1–H3 chỉ DAY1/DAY2, "
                     "stratum S, evaluable, h={2,4,6}h. 49 usable test weekdays sau loại 2005-06-27; original run vẫn INCOMPLETE, "
                     "đây là amended analysis DEVIATION_V7_3_01.\n"])
    sections.append(mdtable(["Flow", "S ngày", "O ngày", "S cases/evaluable", "O cases/evaluable"],
                            [[r["regime"], r["S_days"], r["O_days"], f"{r['S_cases']}/{r['S_evaluable']}",
                              f"{r['O_cases']}/{r['O_evaluable']}"] for r in denom["by_flow"]]))
    sections.append("\n" + mdtable(["Số", "Tái dựng"], list(denom["factorizations"].items())))
    sections.append("\n" + mdtable(["h (h)", "Primary cases", "Unique fresh record-horizons", "Fresh decisions", "Stale decisions"],
                                   [[r["h_hours"], r["primary_cases"], r["unique_record_horizons"], r["unique_fresh_decisions"], r["stale_decisions"]]
                                    for r in denom["per_horizon"]]))
    sections.extend(["\n76 cases thuộc 8 calendar days, 16 flow-days; số horizon qua evaluability gate khác nhau giữa ngày. "
                     "1216=38×32 đếm fresh một lần qua hai tuổi; stale=76×32=2432; tổng fresh+stale=3648. "
                     "408 là số O evaluable qua từng horizon, không phải 51 ngày độc lập; 480=20×3×4×2. "
                     "DAY3 là control training slope gần 0, mô tả; 1h là sensitivity đã khai báo, ngoài population H1–H3. "
                     "File `vc_denominators.json` có per-flow/per-horizon/per-day; không mở thêm outcomes.\n",
                     "## Kiểm chứng, thời gian và tái tạo\n",
                     f"{len(CHECKS)} checks PASS tại thời điểm lập báo cáo: raw/CSV, SHA chunks, ledger, quantile/count và file đầu vào bất biến. "
                     f"CPU phân tích (kể cả primitives và vẽ hình): {meta['cpu_s']:.6f}s; wall {meta['wall_s']:.6f}s.\n",
                     mdtable(["Bước", "CPU-s", "Wall-s"], [[k, v["cpu_s"], v["wall_s"]] for k, v in meta["timings"].items()]),
                     "\nLệnh chạy thực tế (log riêng trong thư mục kết quả):\n\n```bash\n"
                     "cd /home/vantai/state-model-regret\nsource .venv/bin/activate\nsource experiments/explore_ctmc/env.sh\n"
                     "PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.letter.p2_tier2 --self-test\n"
                     "PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.letter.p2_tier2\n```\n",
                     "Tái tạo vào thư mục mới, không ghi đè kết quả đã có:\n\n```bash\n"
                     "PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.letter.p2_tier2 --out results/letter/p2_tier2/reproduction_01\n```\n",
                     "Mọi số của từng mục tái tạo cùng lệnh trên, từ `experiments/letter/p2_tier2.py`. "
                     "`input_sha256.json` ghi từng file thực đọc (gồm brief, ledger và source); `validation.json` ghi actual/expected; "
                     "`run_metadata.json` ghi environment, argv, source SHA, timing và provenance. Không tải/đọc paper mới.\n",
                     "Kiểm chéo độc lập (không import script phân tích): "
                     "`PYTHONDONTWRITEBYTECODE=1 python3 results/letter/p2_tier2/verify_saved.py`. "
                     "Kết quả và actual/expected ở `independent_verification.json`; log `independent_final.log`. "
                     "Verifier tính lại quantile bằng sort/nội suy riêng, gather raw cost bằng vòng lặp và kiểm riêng paired SE/mẫu số.\n",
                     "Lịch sử thực thi: " + ("; ".join(meta["prior_failed_attempts"]) if meta["prior_failed_attempts"] else "không có lượt lỗi trong thư mục output này") + ". "
                     "Giữ nguyên log lỗi; sửa adapter tên trường ledger, không sửa dữ liệu/công thức hay chạy truth. "
                     f"Tổng CPU primitives ghi nhận trong các lượt ở thư mục này: {meta['all_attempts_primitive_cpu_s']:.6f}s, dưới cap 3600s.\n",
                     ("Đính chính cách diễn giải: bản xuất `run02_snapshot/` giữ nguyên cả source và kết quả trước khi sửa "
                      "dòng phân rã 408 (đã ghi sai 136+136+136). Bản hiện hành sinh trực tiếp từ đếm theo flow: "
                      + "+".join(str(r["O_evaluable"]) for r in denom["by_flow"]) + "=408. Không thay số tổng, metric hoặc outcome.\n")
                     if meta["has_narrative_correction_snapshot"] else "",
                     "## Ngoại lệ và giới hạn\n",
                     "- Đã hoàn thành cả 7 phân tích. Khác biệt 93/92 được giữ ở hai bảng; không sửa ledger hoặc paper.\n"
                     "- E6 sign-error dùng ordering level-(i) training làm reference; records lặp qua hai seed/tuổi/horizon.\n"
                     "- GÉANT paired SE là SE mô tả của cost difference trên cùng instances, sau chọn worse side; không CI cho population.\n"
                     "- Relative equality không có absolute floor; các sign/count cực gần 0 không được diễn giải thành effect có độ lớn thực tiễn.\n"
                     "- m₀ dùng π₀ thật và support truncation đã lưu; không chứng minh prediction, deployment realism hay novelty.\n"
                     "- Không truth rollout mới; không thay threshold, card, verdict; không commit/SSH; không sửa file có trước.\n"])
    (out / "SUMMARY.md").write_text("\n\n".join(sections))


def write_json(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def self_test():
    # Analytic examples: quantiles, sign at zero, paired cancellation versus
    # unpaired SE, and the noncommuting E6 aggregation order.
    check("linear Q25", stats([0., 10., 20., 30.])["q25"], 7.5)
    check("linear P90", stats([0., 10., 20., 30.])["q90"], 27.)
    check("strict sign zero", sign(0.), 0)
    check("relative tolerance", paired_row(1., 1. + 5e-10)["comparison"], "equal")
    check("no absolute floor", paired_row(1e-14, 0.)["comparison"], "worse")
    check("paired SE equality", paired_row(2., 1., .6)["comparison"], "equal")
    check("CRN paired cancellation", stderr(np.array([1., 2., 9.]) - np.array([1., 2., 9.])), 0.)
    a = np.array([[10., 0.], [0., 10.]])
    check("E6 mean of recordwise worse sides", float(a.max(axis=1).mean()), 10.)
    check("E6 alternative differs", float(a.mean(axis=0).max()), 5.)
    s = signed_stats([-.2, -.05, 0., .05, .2])
    check("signed near-zero overlaps", s["abs_le_0p1"], 3)
    check("disjoint sign bands", s["below_minus_0p1"] + s["abs_le_0p1"] + s["above_plus_0p1"], 5)
    print(json.dumps(dict(self_tests=len(CHECKS), status="PASS")))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    out = args.out.resolve()
    if not out.is_relative_to(OUT.resolve()):
        raise ValueError("all outputs must stay in results/letter/p2_tier2/")
    out.mkdir(parents=True, exist_ok=True)
    if (out / "SUMMARY.md").exists() or (out / "run_metadata.json").exists():
        raise FileExistsError("use a new --out subdirectory; existing results are immutable")
    inputs = Inputs()
    inputs.register(__file__)
    inputs.register(BRIEF)
    inputs.register(LEDGER / "numbers_ledger.md")
    ledger = inputs.js(LEDGER / "numbers.json")["rows"]
    start, wall = time.process_time(), time.perf_counter()
    timings = {}

    def stage(name, callback):
        t0, w0 = time.process_time(), time.perf_counter()
        result = callback()
        timings[name] = dict(cpu_s=time.process_time() - t0, wall_s=time.perf_counter() - w0)
        print(json.dumps(dict(stage=name, **timings[name]), ensure_ascii=False), flush=True)
        return result

    raws, summary, ctrows = stage("CTMC_saved_selection", lambda: ct_observations(inputs))
    f3 = stage("2_Fig3_IQR", lambda: fig3_table(ctrows, ledger))
    geantrows, rates, max_csv_error = stage("GEANT_raw_replay", lambda: geant_observations(inputs))
    f4 = stage("1_Fig4_signed", lambda: fig4_table(geantrows, ledger))
    e6 = stage("3_E6_replay", lambda: e6_replay(inputs, geantrows, rates, ledger))
    paired = stage("4_paired_comparisons", lambda: paired_tables(ctrows, geantrows, e6, ledger))
    splits = stage("5_optimal_sign_splits", lambda: sign_splits(raws, summary, ledger))
    primitive = stage("6_primitive_signs", lambda: primitive_diagnostic(inputs, raws))
    denom = stage("7_VC_denominators", lambda: denominators(inputs, ledger))
    geometry = stage("candidate_figures", lambda: make_figures(out, inputs, f3, f4))
    stage("input_integrity", inputs.verify)
    failed, completed = [], []
    previous_primitive_cpu = 0.
    for logfile in sorted(out.glob("run_*.log")):
        log = logfile.read_text()
        is_failed = "Traceback (most recent call last)" in log
        is_completed = '"status": "COMPLETE"' in log
        if is_failed:
            failed.append(f"{logfile.name}: " + log.strip().splitlines()[-1])
        if is_completed:
            completed.append(logfile.name)
        if is_failed or is_completed:
            for line in log.splitlines():
                if line.startswith('{"stage": "6_primitive_signs"'):
                    previous_primitive_cpu += json.loads(line)["cpu_s"]
    meta = dict(responsible="Doan Van Tai", status="POST_HOC_EXPOSED", brief=str(BRIEF),
                AI_provenance="Codex implementation under direct author instruction to execute P2_TIER2_BRIEF.md; not author-self or independent human review",
                timestamp_UTC=datetime.now(timezone.utc).isoformat(), argv=sys.argv,
                cwd=str(ROOT), python=sys.version, numpy=np.__version__,
                environment={k: os.environ.get(k) for k in ("OPENBLAS_CORETYPE", "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "NPY_DISABLE_CPU_FEATURES", "PYTHONDONTWRITEBYTECODE")},
                code_sha256=inputs.hashes[inputs.label(__file__)], input_files=len(inputs.hashes),
                source_data_roots=[f"results/letter/{x}" for x in ("w1b", "w2", "e4", "e4b", "e6", "v7_1", "v7_3")],
                actual_result_roots_used=["w1b", "e4", "e4b", "e6", "v7_3"],
                no_new_truth=True, no_existing_files_modified=True,
                max_GEANT_raw_CSV_difference_pp=max_csv_error, figure_geometry=geometry,
                prior_failed_attempts=failed, prior_completed_attempts=completed,
                has_narrative_correction_snapshot=(out / "run02_snapshot").is_dir(),
                all_attempts_primitive_cpu_s=previous_primitive_cpu + primitive["cpu_s"],
                timings=timings, cpu_s=time.process_time() - start, wall_s=time.perf_counter() - wall)
    for filename, content in (("fig3_iqr.json", f3), ("fig4a_signed.json", f4), ("e6_replay.json", e6),
                              ("paired_by_h.json", paired), ("optimal_sign_splits.json", splits),
                              ("primitive_signs.json", primitive), ("vc_denominators.json", denom),
                              ("input_sha256.json", inputs.hashes),
                              ("validation.json", dict(status="PASS", n_checks=len(CHECKS), checks=CHECKS)),
                              ("run_metadata.json", meta)):
        write_json(out / filename, content)
    write_summary(out, f3, f4, e6, paired, splits, primitive, denom, meta)
    print(json.dumps(dict(status="COMPLETE", checks=len(CHECKS), cpu_s=meta["cpu_s"],
                          primitive_cpu_s=primitive["cpu_s"], output=str(out)), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
