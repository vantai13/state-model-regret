#!/usr/bin/env python3
"""Independent, saved-data-only rescore of CARD_X4B (Doan Van Tai).

No experiment/scoring modules are imported. Inputs are committed NPZ/JSON/CSV
under results/letter/x4b, plus the card named by the brief. In particular, the
stored costs, regrets, gains, evaluability flags and verdicts are checks, never
inputs to the recomputed outcomes. No simulation, fitting or truth run occurs.

Run from any directory:
    python -B experiments/letter/x4b_rescore_independent.py --self-test
    python -B experiments/letter/x4b_rescore_independent.py
    python -B experiments/letter/x4b_rescore_independent.py --check-only
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import subprocess
import sys
import unittest

import numpy as np


OWNER = "Doan Van Tai"
INPUT = "results/letter/x4b"
OUTPUT = "results/letter/x_rescore"
C0_MBPS = 12544.525174  # Literal pre-truth capacity in CARD_X4B, not a refit.
HORIZONS = (300, 600, 900, 1200, 1800, 3600, 7200)
AGES = (300, 900)
RULES = ("M0", "Hybrid", "Stationary")
SIDES = ("fresh", "stale_300", "stale_900")
SIGN = "G_S=L_stale-L_fresh; negative=fresh hurts"
SUM_SCOPE = (
    "Sum of instance regrets over evaluable record,h; fresh occurs once per h."
)
# Only field/array comparisons use these tolerances. Card gates use their exact
# thresholds, without an added epsilon. Signed MC regrets are never clipped.
RTOL = 1e-12
ATOL = 1e-9


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class CommittedInputs:
    """Check every byte read against HEAD, without reading experiment sources."""

    def __init__(self, repo: Path):
        self.repo = repo
        self.head = self.git("rev-parse", "HEAD").decode().strip()
        self.branch = self.git("branch", "--show-current").decode().strip()
        require(self.branch == "letter", f"Expected branch letter, got {self.branch}")
        self.blobs = {}
        for entry in self.git("ls-tree", "-rz", self.head, "--", INPUT).split(b"\0"):
            if entry:
                header, path = entry.split(b"\t", 1)
                mode, kind, oid = header.decode().split()
                require(kind == "blob" and mode != "120000", "Symlink/non-blob input")
                self.blobs[path.decode()] = oid
        self.sha256: dict[str, str] = {}

    def git(self, *args: str) -> bytes:
        return subprocess.check_output(["git", "-C", str(self.repo), *args])

    def read(self, relative: str) -> bytes:
        path = PurePosixPath(relative)
        require(not path.is_absolute() and ".." not in path.parts, "Unsafe input path")
        require(
            path.suffix in {".npz", ".json", ".csv"} or str(path) == "CARD_X4B.md",
            f"Input type outside brief: {relative}",
        )
        name = f"{INPUT}/{path}"
        require(name in self.blobs, f"Input not committed at HEAD: {name}")
        local = self.repo / name
        require(not local.is_symlink(), f"Symlink input: {name}")
        data = local.read_bytes()
        oid = self.blobs[name]
        algorithm = "sha1" if len(oid) == 40 else "sha256"
        blob = hashlib.new(algorithm, f"blob {len(data)}\0".encode() + data).hexdigest()
        require(blob == oid, f"Working file differs from committed blob: {name}")
        sha = digest(data)
        require(name not in self.sha256 or self.sha256[name] == sha, f"Input changed: {name}")
        self.sha256[name] = sha
        return data

    def load_json(self, relative: str):
        return json.loads(self.read(relative))

    def check_sha(self, relative: str, expected: str) -> None:
        require(digest(self.read(relative)) == expected, f"SHA256 mismatch: {relative}")


class ArrayChecks:
    def __init__(self):
        self.groups = {}

    def check(self, name: str, actual, saved, record: str) -> None:
        actual, saved = np.asarray(actual), np.asarray(saved)
        require(actual.shape == saved.shape, f"{record}: shape mismatch for {name}")
        if actual.dtype.kind in "f" or saved.dtype.kind in "f":
            require(np.isfinite(actual).all() and np.isfinite(saved).all(), f"Nonfinite {name}")
            equal = np.isclose(actual, saved, rtol=RTOL, atol=ATOL)
            maximum = float(np.max(np.abs(actual - saved))) if actual.size else 0.0
        else:
            equal = actual == saved
            maximum = 0.0
        group = self.groups.setdefault(name, {
            "records_checked": 0, "values_checked": 0, "mismatched_values": 0,
            "max_absolute_difference": 0.0, "mismatch_records": [],
        })
        group["records_checked"] += 1
        group["values_checked"] += int(actual.size)
        group["mismatched_values"] += int(np.count_nonzero(~equal))
        group["max_absolute_difference"] = max(group["max_absolute_difference"], maximum)
        if not bool(np.all(equal)):
            group["mismatch_records"].append(record)


def compare_fields(actual, saved) -> dict:
    """Compare all keys, list lengths, types and scalar leaves recursively."""
    result = {
        "status": "MATCH", "fields_checked": 0, "fields_matched": 0,
        "mismatches": [], "by_section": {}, "rounding_differences": 0,
        "max_absolute_numeric_difference": 0.0, "max_difference_path": None,
        "relative_tolerance": RTOL, "absolute_tolerance": ATOL,
    }

    def walk(a, b, path: str):
        if isinstance(a, dict) and isinstance(b, dict):
            if set(a) != set(b):
                result["mismatches"].append({
                    "path": path, "reason": "field_set",
                    "only_recomputed": sorted(set(a) - set(b)),
                    "only_original": sorted(set(b) - set(a)),
                })
            for key in sorted(set(a) & set(b)):
                walk(a[key], b[key], f"{path}.{key}" if path else key)
            return
        if isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                result["mismatches"].append({
                    "path": path, "reason": "list_length",
                    "recomputed": len(a), "original": len(b),
                })
            for index, (aa, bb) in enumerate(zip(a, b)):
                walk(aa, bb, f"{path}[{index}]")
            return
        result["fields_checked"] += 1
        section = path.split(".")[0].split("[")[0]
        tally = result["by_section"].setdefault(section, {"checked": 0, "matched": 0})
        tally["checked"] += 1
        numeric = type(a) in (int, float) and type(b) in (int, float)
        if numeric and (isinstance(a, float) or isinstance(b, float)):
            error = abs(a - b)
            equal = math.isfinite(a) and math.isfinite(b) and error <= ATOL + RTOL * abs(b)
            result["rounding_differences"] += int(equal and a != b)
            if error > result["max_absolute_numeric_difference"]:
                result["max_absolute_numeric_difference"] = error
                result["max_difference_path"] = path
        else:
            equal = type(a) is type(b) and a == b
        if equal:
            result["fields_matched"] += 1
            tally["matched"] += 1
        else:
            result["mismatches"].append({
                "path": path, "reason": "value_or_type",
                "recomputed": a, "original": b,
            })

    walk(actual, saved, "")
    if result["mismatches"]:
        result["status"] = "MISMATCH"
    return result


def standard_error(values) -> float:
    values = np.asarray(values, dtype=float)
    return float(values.std(ddof=1) / math.sqrt(values.size)) if values.size > 1 else 0.0


def percent(value: float, reference: float):
    return 100.0 * value / reference if reference > 0.0 else None


def paired_reading(mean: float, se: float) -> str:
    if mean < 0.0 and abs(mean) >= 2.0 * se:
        return "GAIN"
    if mean > 0.0 and mean >= 2.0 * se:
        return "LOSS"
    return "UNRESOLVED"


def b2_verdict(cases: int, not_worse: int) -> str:
    if cases < 20:
        return "NOT_EVALUABLE"
    return "STANDS" if not_worse / cases >= 0.95 else "DOES_NOT_STAND"


def b3_cell(key, day_values: list[tuple[float, float]], predicted: int) -> dict:
    gains = np.array([value[0] for value in day_values])
    reference = float(np.mean([value[1] for value in day_values]))
    mean = float(gains.mean())
    se = standard_error(gains)
    gain_pct = percent(mean, reference)
    resolved = bool(
        len(gains) >= 2 and reference > 0.0
        and abs(mean) >= 2.0 * se and abs(gain_pct) >= 0.25
    )
    observed = int(np.sign(mean))
    regime, tau, h = key
    return {
        "regime": regime, "rule": "M0", "tau_s": tau, "h_s": h,
        "days": len(day_values), "mean_G_S_Mbit_s": mean,
        "SE_over_days_Mbit_s": se, "mean_C_ref_Mbit_s": reference,
        "G_S_pct": gain_pct, "resolved": resolved, "predicted": predicted,
        "observed": observed, "abstention": predicted == 0,
        "correct": bool(resolved and predicted != 0 and predicted == observed),
    }


def strict_summary(rows: list[dict]) -> dict:
    total = float(sum(row["regret_sum_Mbit_s"] for row in rows))
    tie = float(sum(row["tie_regret_sum_Mbit_s"] for row in rows))
    strict = float(sum(row["strict_regret_sum_Mbit_s"] for row in rows))
    share = strict / total if total != 0.0 else None
    return {
        "cases": len(rows), "instances": sum(row["instances"] for row in rows),
        "tie_instances": sum(row["tie_instances"] for row in rows),
        "strict_instances": sum(row["strict_instances"] for row in rows),
        "regret_sum_Mbit_s": total, "tie_regret_sum_Mbit_s": tie,
        "strict_regret_sum_Mbit_s": strict, "strict_regret_share": share,
        "strict_regret_pct": 100.0 * share if share is not None else None,
        "sum_scope": SUM_SCOPE, "signed_MC_estimates_preserved": True,
    }


def rebuild_record(raw, metadata: dict, checks: ArrayChecks):
    """Rebuild all rules, reference decisions and costs from raw saved arrays."""
    record = f"{metadata['regime']}_{metadata['date']}"
    n, nh = 32, len(HORIZONS)
    for name, expected in {
        "h_seconds": HORIZONS, "tau_seconds": AGES,
        "pipelines": RULES, "sides": SIDES,
    }.items():
        require(tuple(raw[name].tolist()) == tuple(expected), f"{record}: unexpected {name}")
    for name, shape in {
        "paired_evaluation": (n, 128, 2, nh),
        "reference_decision_rollouts": (n, 64, 2, nh),
        "M0_predicted_fresh": (n, 2, nh),
        "M0_predicted_stale": (n, 2, 2, nh),
        "s_hat_Mbit": (1,),
    }.items():
        require(raw[name].shape == shape, f"{record}: invalid {name} shape")
        require(np.isfinite(raw[name]).all(), f"{record}: nonfinite {name}")

    slope = float(raw["s_hat_Mbit"][0])
    fluid = np.concatenate((raw["M0_predicted_fresh"][:, None], raw["M0_predicted_stale"]), axis=1)
    gap = fluid[:, :, 1] - fluid[:, :, 0]
    hybrid_gap = gap + np.asarray(HORIZONS) * slope
    decisions = np.stack((
        gap < 0, hybrid_gap < 0, np.full(gap.shape, slope < 0, dtype=bool),
    ), axis=1).astype(np.int16)
    ties = np.stack((
        gap == 0, hybrid_gap == 0, np.full(gap.shape, slope == 0, dtype=bool),
    ), axis=1)
    reference_means = raw["reference_decision_rollouts"].mean(axis=1)
    reference_decision = reference_means.argmin(axis=1)  # Exact ties choose Stay.
    reference_ties = reference_means[:, 0] == reference_means[:, 1]
    values = raw["paired_evaluation"].mean(axis=1)
    instance = np.arange(n)[:, None]
    horizon = np.arange(nh)[None, :]
    reference = values[instance, reference_decision, horizon]
    costs = values[instance[:, None, None], decisions, horizon[:, None, None]]
    regret = costs - reference[:, None, None]
    gain = costs[:, :, 1:] - costs[:, :, :1]
    paired = costs[:, 1] - costs[:, 2]
    mean_reference = reference.mean(axis=0)
    evaluable = mean_reference / np.asarray(HORIZONS) >= 0.001 * C0_MBPS
    rebuilt = {
        "decisions": decisions, "tie_flags": ties,
        "reference_decision": reference_decision, "reference_tie_flags": reference_ties,
        "V": values, "C_ref": reference, "costs": costs, "regret": regret,
        "G_S": gain, "paired_Hybrid_minus_Stationary": paired,
        "mean_reference_backlog_Mbit": mean_reference / np.asarray(HORIZONS),
        "evaluable": evaluable,
    }
    for name, array in rebuilt.items():
        checks.check(name, array, raw[name], record)
    return rebuilt, mean_reference, slope


def recompute(reader: CommittedInputs) -> dict:
    # Existing receipt/manifest/card locks are verified; no new lock is made.
    card_lock = reader.load_json("lock_card.json")
    reader.check_sha("CARD_X4B.md", card_lock["sha256"]["card"])
    reader.check_sha("lock.json", card_lock["sha256"]["lock"])
    lock = reader.load_json("lock.json")
    lock_sha = digest(reader.read("lock.json"))
    require(lock["evaluability_capacity_Mbps"] == C0_MBPS, "Capacity differs from card")
    require(lock["evaluability_min_mean_backlog_Mbit"] == 0.001 * C0_MBPS, "Wrong gate")
    for name in ("CARD_X4B.md", "predictions.json", "predictions.csv", "protocol.json"):
        reader.check_sha(name, lock["sha256"][f"output:{name}"])
    protocol = reader.load_json("protocol.json")
    receipt = reader.load_json("truth/receipt.json")
    started = reader.load_json("truth/started.json")
    manifest = reader.load_json("truth/raw_manifest.json")
    require(receipt["status"] == "COMPLETE" and receipt["measurements_finalized"], "Truth incomplete")
    require(receipt["lock_sha256"] == lock_sha == started["lock_sha256"], "Truth lock mismatch")
    require(started["card_lock_sha256"] == digest(reader.read("lock_card.json")), "Card lock mismatch")
    require(started["one_shot"] and not started["retry"] and not started["resume"], "Unexpected run policy")
    require(started["seed"] == lock["seed_test"] == protocol["seeds"]["test"] == 7412001, "Unexpected seed")
    for relative, sha in manifest["sha256"].items():
        reader.check_sha(relative, sha)

    records = sorted(receipt["records"], key=lambda r: (r["regime"], r["date"]))
    keys = [(r["regime"], r["date"]) for r in records]
    planned = [(r["regime"], r["date"]) for r in started["records"]]
    require(len(records) == receipt["planned_records"] == lock["test_S_records"] == 60, "Record count mismatch")
    require(len(set(keys)) == len(keys) and sorted(keys) == sorted(planned), "Record coverage mismatch")
    expected_files = {f"truth/records/{regime}_{date}.{ext}" for regime, date in keys for ext in ("json", "npz")}
    committed_files = {
        name[len(INPUT) + 1:] for name in reader.blobs if name.startswith(f"{INPUT}/truth/records/")
    }
    require(expected_files == committed_files, "Committed raw coverage differs from receipt")
    require(set(manifest["sha256"]) == expected_files | {"truth/started.json"}, "Manifest coverage mismatch")

    predictions = reader.load_json("predictions.json")
    require(predictions["training_only"] and not predictions["test_outcomes_read"], "Prediction provenance mismatch")
    require(predictions["seed_train"] == protocol["seeds"]["train"] == 7402001, "Training seed mismatch")
    prediction_checks = ArrayChecks()
    predicted = {}
    slopes = {}
    for row in predictions["rows"]:
        key = (row["regime"], row["rule"], row["tau_s"], row["h_s"])
        require(key not in predicted, "Duplicate train prediction")
        delta = (row["switch_stale"] - row["switch_fresh"]) / row["denominator"]
        slope_prediction = row["s_hat_pooled_Mbit"] * delta
        predicted[key] = int(np.sign(slope_prediction))
        slopes.setdefault(row["regime"], row["s_hat_pooled_Mbit"])
        prediction_checks.check("delta_F_hat", delta, row["delta_F_hat"], str(key))
        prediction_checks.check("slope_pred_Mbit", slope_prediction, row["slope_pred_Mbit"], str(key))
        prediction_checks.check("predicted_G_S_sign", predicted[key], row["predicted_G_S_sign"], str(key))
        prediction_checks.check("pooled_slope", slopes[row["regime"]], row["s_hat_pooled_Mbit"], str(key))
    csv_predictions = list(csv.DictReader(io.StringIO(reader.read("predictions.csv").decode())))
    require(len(csv_predictions) == len(predictions["rows"]) == 126, "Train prediction count mismatch")
    csv_seen = set()
    for row in csv_predictions:
        key = (row["regime"], row["rule"], int(row["tau_s"]), int(row["h_s"]))
        require(key in predicted and key not in csv_seen, "CSV prediction coverage mismatch")
        csv_seen.add(key)
        prediction_checks.check("CSV_predicted_sign", predicted[key], int(row["predicted_G_S_sign"]), str(key))

    checks = ArrayChecks()
    b1_rows, b2_rows, b3b_rows = [], [], []
    days = defaultdict(list)
    record_audit = []
    evaluable_by_regime_h = Counter()
    disagreement_by_h = {str(h): {"numerator": 0, "denominator": 0} for h in HORIZONS}
    for meta in records:
        name = f"{meta['regime']}_{meta['date']}"
        require(meta["stage"] == "truth" and meta["split"] == "test" and meta["stratum"] == "S" and not meta["pilot"], f"Wrong scope: {name}")
        require((meta["N"], meta["K"], meta["R_dec"], meta["R_eval"]) == (32, 64, 64, 128), f"Wrong configuration: {name}")
        require(meta["seed_base"] == 7412001 and meta["evaluability_capacity_Mbps"] == C0_MBPS, f"Wrong seed/capacity: {name}")
        npz_name = f"truth/records/{name}.npz"
        data = reader.read(npz_name)
        require(digest(data) == meta["npz_sha256"] == manifest["sha256"][npz_name], f"Receipt SHA256 mismatch: {name}")
        require(reader.load_json(f"truth/records/{name}.json") == meta, f"Metadata differs from receipt: {name}")
        with np.load(io.BytesIO(data), allow_pickle=False) as raw:
            rebuilt, reference, slope = rebuild_record(raw, meta, checks)
        checks.check("train_slope", slope, slopes[meta["regime"]], name)
        decisions, regret = rebuilt["decisions"], rebuilt["regret"]
        paired, evaluable = rebuilt["paired_Hybrid_minus_Stationary"], rebuilt["evaluable"]
        common = {"regime": meta["regime"], "set": meta["set"], "date": meta["date"]}
        record_audit.append({
            **common, "npz_sha256": digest(data), "receipt_sha256_match": True,
            "evaluable_h_s": [h for i, h in enumerate(HORIZONS) if evaluable[i]],
        })
        for hi, h in enumerate(HORIZONS):
            cref = float(reference[hi])
            is_evaluable = bool(evaluable[hi])
            if is_evaluable:
                evaluable_by_regime_h[(meta["regime"], h)] += 1
            disagreement = decisions[:, 1, :, hi] != decisions[:, 2, :, hi]
            disagreement_by_h[str(h)]["numerator"] += int(disagreement.sum())
            disagreement_by_h[str(h)]["denominator"] += int(disagreement.size)
            if h <= 1800:
                for si, side in enumerate(SIDES):
                    numerator = int(disagreement[:, si].sum())
                    if numerator / 32 >= 0.01:  # B1 has no evaluability exclusion.
                        mean = float(paired[:, si, hi].mean())
                        se = standard_error(paired[:, si, hi])
                        b1_rows.append({
                            **common, "side": side, "h_s": h, "evaluable": is_evaluable,
                            "C_ref_Mbit_s": cref,
                            "paired_Hybrid_minus_Stationary_Mbit_s": mean,
                            "paired_Hybrid_minus_Stationary_SE_Mbit_s": se,
                            "paired_Hybrid_minus_Stationary_pct": percent(mean, cref),
                            "disagreement_numerator": numerator, "instances": 32,
                            "disagreement_share": numerator / 32, "reading": paired_reading(mean, se),
                        })
                if is_evaluable:
                    for ti, tau in enumerate(AGES):
                        both = []
                        for ri in (1, 2):
                            fresh = float(regret[:, ri, 0, hi].mean())
                            stale = float(regret[:, ri, ti + 1, hi].mean())
                            both.append(percent(max(fresh, stale), cref))
                        difference = both[0] - both[1]
                        b2_rows.append({
                            "regime": meta["regime"], "date": meta["date"], "tau_s": tau,
                            "h_s": h, "side": f"fresh+stale_{tau}",
                            "Hybrid_both_side_regret_pct": both[0],
                            "Stationary_both_side_regret_pct": both[1],
                            "difference_percentage_points": difference,
                            "not_worse": bool(difference <= 0.05),
                        })
            if h in (3600, 7200) and is_evaluable:
                for ti, tau in enumerate(AGES):
                    gs = float(rebuilt["G_S"][:, 0, ti, hi].mean())
                    days[(meta["regime"], tau, h)].append((gs, cref))
                fresh_regret = regret[:, 0, 0, hi]
                tie = rebuilt["tie_flags"][:, 0, 0, hi]
                total = float(fresh_regret.sum())
                tie_sum = float(fresh_regret[tie].sum())
                strict_sum = float(fresh_regret[~tie].sum())
                b3b_rows.append({
                    **common, "side": "fresh", "h_s": h, "evaluable": True,
                    "C_ref_Mbit_s": cref, "instances": 32,
                    "tie_instances": int(tie.sum()), "strict_instances": int((~tie).sum()),
                    "regret_Mbit_s": total / 32, "tie_regret_Mbit_s": tie_sum / 32,
                    "strict_regret_Mbit_s": strict_sum / 32,
                    "regret_sum_Mbit_s": total, "tie_regret_sum_Mbit_s": tie_sum,
                    "strict_regret_sum_Mbit_s": strict_sum,
                    "strict_regret_share": strict_sum / total if total != 0.0 else None,
                })

    b1_rows.sort(key=lambda r: (r["regime"], r["date"], r["h_s"], r["side"]))
    b2_rows.sort(key=lambda r: (r["regime"], r["date"], r["tau_s"], r["h_s"]))
    b3b_rows.sort(key=lambda r: (r["regime"], r["date"], r["h_s"]))
    cells = [b3_cell(key, values, predicted[(key[0], "M0", key[1], key[2])]) for key, values in sorted(days.items())]
    resolved = sum(cell["resolved"] for cell in cells)
    correct = sum(cell["correct"] for cell in cells)
    accuracy = correct / resolved if resolved else None
    not_worse = sum(row["not_worse"] for row in b2_rows)
    counts = {label: sum(row["reading"] == label for row in b1_rows) for label in ("GAIN", "LOSS", "UNRESOLVED")}
    score_bytes = reader.read("score.json")  # Provenance hash only, never outcome input.
    card = {
        "owner": OWNER, "lock_sha256": lock_sha, "sign": SIGN,
        "B1": {
            "kind": "EXPLORATORY_NOT_PASS_FAIL", "cases": len(b1_rows),
            "counts": counts, "rows": b1_rows, "SE_unit": "paired instances within record,side,h",
        },
        "B2": {
            "unit": "record,tau,h; both-side=max(fresh regret,stale_tau regret), as X-GEANT",
            "cases": len(b2_rows), "not_worse": not_worse,
            "share": not_worse / len(b2_rows) if b2_rows else None,
            "margin_percentage_points_C_ref": 0.05, "required_share": 0.95,
            "minimum_cases": 20, "verdict": b2_verdict(len(b2_rows), not_worse), "rows": b2_rows,
        },
        "B3a": {
            "resolved": resolved, "correct": correct, "accuracy": accuracy,
            "minimum_resolved": 4, "accuracy_threshold": 0.8, "resolution_pct_C_ref": 0.25,
            "SE_unit": "days within regime,tau,h",
            "verdict": "NOT_EVALUABLE" if resolved < 4 else ("STANDS" if accuracy >= 0.8 else "DOES_NOT_STAND"),
            "cells": cells,
        },
        "B3b": {
            "kind": "DESCRIPTIVE", **strict_summary(b3b_rows),
            "by_h": {str(h): strict_summary([row for row in b3b_rows if row["h_s"] == h]) for h in (3600, 7200)},
            "rows": b3b_rows,
        },
        "counts_are_not_independent_trials": True,
        "descriptive_score_sha256": digest(score_bytes),
    }
    # Target is opened only after all B1/B2/B3 outcomes have been reconstructed.
    target = reader.load_json("card_verdicts.json")
    comparison = compare_fields(card, target)
    raw_mismatches = sum(g["mismatched_values"] for g in checks.groups.values())
    prediction_mismatches = sum(g["mismatched_values"] for g in prediction_checks.groups.values())
    status = "MATCH" if comparison["status"] == "MATCH" and raw_mismatches == prediction_mismatches == 0 else "MISMATCH"
    return {
        "owner": OWNER, "schema": "x4b-independent-rescore-v1", "status": status,
        "method": {
            "outcomes": "paired_evaluation -> mean action costs; reference_decision_rollouts -> reference action; M0 costs + h*s_hat -> all rule decisions; indexed costs -> signed regrets and G_S",
            "reference": "Reference action chosen from R_dec rollouts, evaluated on separate R_eval rollouts; not min(V) or clipped regret.",
            "prediction": "sign(s_hat_pooled_Mbit * (switch_stale-switch_fresh)/denominator), from locked train predictions",
            "B1_scope": "h<=1800 and disagreement>=1%; evaluability is reported, not an exclusion",
            "B2_scope": "evaluable record,tau,h<=1800; max(mean fresh regret,mean stale regret)",
            "B3a_scope": "evaluable days, h in {3600,7200}; SE across daily instance means; both resolution gates required",
            "B3b_scope": "evaluable record,h in {3600,7200}; exact fluid ties; fresh counted once; signed sums preserved",
            "simulations_run": 0, "outcome_modules_imported": [],
        },
        "provenance": {
            "branch": reader.branch, "HEAD": reader.head,
            "raw_commit_reported_by_score": json.loads(score_bytes)["raw_commit"],
            "records_receipt_sha256_checked": len(records),
            "raw_manifest_sha256_checked": len(manifest["sha256"]),
            "all_inputs_match_committed_blobs": True,
            "input_sha256": dict(sorted(reader.sha256.items())),
            "seed_train": 7402001, "seed_truth": 7412001,
            "N": 32, "K": 64, "R_dec": 64, "R_eval": 128,
            "evaluability_capacity_Mbps": C0_MBPS,
            "record_audit": record_audit,
        },
        "validation": {
            "raw_array_checks": checks.groups, "raw_mismatched_values": raw_mismatches,
            "prediction_checks": prediction_checks.groups,
            "prediction_mismatched_values": prediction_mismatches,
        },
        "comparison": comparison, "recomputed_card_verdicts": card,
        "original_card_summary": {
            "B1": {key: target["B1"][key] for key in ("cases", "counts")},
            "B2": {key: target["B2"][key] for key in ("verdict", "cases", "not_worse", "share")},
            "B3a": {key: target["B3a"][key] for key in ("verdict", "resolved", "accuracy")},
            "B3b_strict_regret_pct": target["B3b"]["strict_regret_pct"],
        },
        "diagnostics_saved_data_only": {
            "evaluable_records_by_regime_h": [
                {"regime": regime, "h_s": h, "records": count}
                for (regime, h), count in sorted(evaluable_by_regime_h.items())
            ],
            "Hybrid_Stationary_disagreement_by_h": disagreement_by_h,
            "B2_equal_cases": sum(row["difference_percentage_points"] == 0.0 for row in b2_rows),
            "B2_improved_cases": sum(row["difference_percentage_points"] < 0.0 for row in b2_rows),
            "B3a_below_magnitude_gate": sum(abs(cell["G_S_pct"]) < 0.25 for cell in cells),
            "B3a_below_2SE_gate": sum(abs(cell["mean_G_S_Mbit_s"]) < 2 * cell["SE_over_days_Mbit_s"] for cell in cells),
        },
    }


def render_report(result: dict) -> str:
    card, comp = result["recomputed_card_verdicts"], result["comparison"]
    original = result["original_card_summary"]
    b1, b2, b3a, b3b = (card[key] for key in ("B1", "B2", "B3a", "B3b"))
    checks = result["validation"]["raw_array_checks"]
    values = sum(group["values_checked"] for group in checks.values())
    lines = [
        "# Chấm lại độc lập X4b", "", f"Người phụ trách: **{OWNER}**.", "",
        f"Kết quả đối chiếu: **{result['status']}**. Đã so {comp['fields_checked']} trường vô hướng, "
        f"khớp {comp['fields_matched']}; {len(comp['mismatches'])} sai khác ngoài tolerance.", "",
        "Script chỉ dùng artifact đã commit trong `results/letter/x4b/` và thẻ được brief chỉ định. "
        "Không import module thí nghiệm/chấm gốc. Không chạy lại simulation hoặc truth.", "",
        "| Phép đọc | Tính lại | Kết quả gốc |", "|---|---|---|",
        f"| B1, thăm dò | GAIN {b1['counts']['GAIN']}, LOSS {b1['counts']['LOSS']}, UNRESOLVED {b1['counts']['UNRESOLVED']}; {b1['cases']} ô | GAIN {original['B1']['counts']['GAIN']}, LOSS {original['B1']['counts']['LOSS']}, UNRESOLVED {original['B1']['counts']['UNRESOLVED']}; {original['B1']['cases']} ô |",
        f"| B2 | {b2['verdict']}, {b2['not_worse']}/{b2['cases']} = {100*b2['share']:.1f}% | {original['B2']['verdict']}, {original['B2']['not_worse']}/{original['B2']['cases']} = {100*original['B2']['share']:.1f}% |",
        f"| B3(a) | {b3a['verdict']}; {b3a['resolved']}/{len(b3a['cells'])} ô resolved, accuracy = null | {original['B3a']['verdict']}; {original['B3a']['resolved']} ô resolved, accuracy = null |",
        f"| B3(b), mô tả | strict chiếm {b3b['strict_regret_pct']:.9f}% regret fresh của M0 | {original['B3b_strict_regret_pct']:.9f}% |", "",
        "## Dữ liệu và cách tính", "",
        "60 bản ghi test-S, ba regime NEWB1–NEWB3; N=32, K=64, R_dec=64, R_eval=128; "
        "τ={300,900} s; h={300,600,900,1200,1800,3600,7200} s. "
        "Seed train=7402001, truth=7412001. Giá trị cost/regret có đơn vị Mbit·s.", "",
        "Dựng lại decisions từ cost M0, h·ŝ và luật tĩnh; exact tie chọn Stay. "
        "Reference action lấy từ trung bình R_dec rollouts, rồi đánh giá trên R_eval rollouts riêng. "
        "Lấy trung bình `paired_evaluation` theo rollout để tính cost từng action, index theo decision "
        "để tính cost từng pipeline; regret = cost − C_ref và G_S = L_stale − L_fresh. "
        "Giữ nguyên signed Monte Carlo estimates. Các mảng kết quả lưu sẵn chỉ dùng đối chiếu.", "",
        f"Cổng evaluability: mean(C_ref)/h ≥ 0,001 × {C0_MBPS:.6f} = {0.001*C0_MBPS:.9f} Mbit. "
        "B1 không loại ô theo cổng này. B2 dùng max(mean regret fresh, mean regret stale), "
        "biên 0,05 điểm % C_ref, tối thiểu 20 ô và tỷ lệ đạt ≥95%. "
        "B3(a) tính SE theo ngày, cần đồng thời |mean|≥2SE và |G_S|≥0,25% C_ref; "
        "cần ≥4 ô resolved để chấm accuracy ≥0,80.", "",
        "## B1 và so sánh với baseline", "",
        "Mọi bất đồng nằm ở NEWB3 ngày 19/07/2005. SE dưới đây theo 32 instance trong cùng "
        "bản ghi/phía/h; các ô chia sẻ cùng ngày và instance, không phải các thử nghiệm độc lập.", "",
        "| h (s) | Phía | Bất đồng/32 | Hybrid − Stationary (Mbit·s) | SE (Mbit·s) | Hiệu (điểm % C_ref) | Đọc |",
        "|---:|---|---:|---:|---:|---:|---|",
    ]
    for row in b1["rows"]:
        lines.append(
            f"| {row['h_s']} | {row['side']} | {row['disagreement_numerator']}/32 | "
            f"{row['paired_Hybrid_minus_Stationary_Mbit_s']:.6f} | "
            f"{row['paired_Hybrid_minus_Stationary_SE_Mbit_s']:.6f} | "
            f"{row['paired_Hybrid_minus_Stationary_pct']:.9f} | {row['reading']} |"
        )
    lines += [
        "", "| B2, chỉ các ô có thay đổi | Ngày | τ (s) | h (s) | Hybrid (% C_ref) | Stationary (% C_ref) | Hiệu (điểm %) |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in b2["rows"]:
        if row["difference_percentage_points"] != 0.0:
            lines.append(
                f"| {row['regime']} | {row['date']} | {row['tau_s']} | {row['h_s']} | "
                f"{row['Hybrid_both_side_regret_pct']:.9f} | {row['Stationary_both_side_regret_pct']:.9f} | "
                f"{row['difference_percentage_points']:.9f} |"
            )
    diag = result["diagnostics_saved_data_only"]
    lines += [
        "", f"B2 có {diag['B2_equal_cases']}/{b2['cases']} ô trùng baseline và "
        f"{diag['B2_improved_cases']} ô có regret both-side thấp hơn; không diễn giải tỷ lệ 100% là "
        "Hybrid có lợi ở mọi ô. B1 tại 1800 s vẫn âm nhưng chưa đạt 2SE.", "",
        "## B3 và dự báo trước truth", "",
        "| Regime | τ (s) | h (s) | Ngày evaluable | G_S (% C_ref) | Mean (Mbit·s) | SE theo ngày (Mbit·s) | Dấu train | Resolved |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for cell in b3a["cells"]:
        lines.append(
            f"| {cell['regime']} | {cell['tau_s']} | {cell['h_s']} | {cell['days']} | "
            f"{cell['G_S_pct']:.9f} | {cell['mean_G_S_Mbit_s']:.6f} | "
            f"{cell['SE_over_days_Mbit_s']:.6f} | {cell['predicted']} | {cell['resolved']} |"
        )
    lines += [
        "", f"{diag['B3a_below_magnitude_gate']}/{len(b3a['cells'])} ô không đạt ngưỡng độ lớn "
        f"0,25% C_ref; {diag['B3a_below_2SE_gate']}/{len(b3a['cells'])} ô không đạt 2SE. "
        "Không có accuracy xác định và không thể kết luận luật dấu đã được xác nhận hoặc bị bác.", "",
        "| h (s) | Bản ghi | Instance | Strict / tie | Tổng regret (Mbit·s) | Strict regret (Mbit·s) | Strict (%) |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for h, item in b3b["by_h"].items():
        lines.append(
            f"| {h} | {item['cases']} | {item['instances']} | {item['strict_instances']} / {item['tie_instances']} | "
            f"{item['regret_sum_Mbit_s']:.6f} | {item['strict_regret_sum_Mbit_s']:.6f} | {item['strict_regret_pct']:.9f} |"
        )
    lines += [
        "", f"Tổng fresh đếm một lần cho mỗi (record,h), không nhân đôi theo τ: {b3b['instances']} instance, "
        f"{b3b['strict_instances']} strict/{b3b['tie_instances']} tie. "
        f"Strict regret = {b3b['strict_regret_sum_Mbit_s']:.6f} Mbit·s; tie regret = "
        f"{b3b['tie_regret_sum_Mbit_s']:.6f} Mbit·s; tổng = {b3b['regret_sum_Mbit_s']:.6f} Mbit·s. "
        f"Strict chỉ chiếm {b3b['strict_regret_pct']:.9f}%: có hai bottleneck vẫn chưa loại được "
        "sự chi phối của ties trong regret fresh của M0.", "",
        "Đối chiếu dự báo: F1 sai ở vế đa số UNRESOLVED (thực tế 6 GAIN/3 UNRESOLVED), "
        "vế nghiêng GAIN khi resolved phù hợp; F2 đúng; F3 phù hợp với nhánh NOT_EVALUABLE; "
        "F4 không đứng (strict <30%). Theo luật inclusion của card, strict cũng <10%. "
        "Đây là đọc lại kết quả đã lưu; không thay ngưỡng, chọn subset, fit hoặc thử predictor mới.", "",
        "## Kiểm chứng và tái lập", "",
        f"- SHA256 NPZ theo receipt: {result['provenance']['records_receipt_sha256_checked']}/60; "
        f"raw manifest: {result['provenance']['raw_manifest_sha256_checked']}/121 file.",
        f"- {len(result['provenance']['input_sha256'])} input khớp byte với blob đã commit ở HEAD "
        f"`{result['provenance']['HEAD']}`; raw commit được score ghi nhận: "
        f"`{result['provenance']['raw_commit_reported_by_score']}`.",
        f"- {len(checks)} nhóm đối chiếu raw, {values} giá trị; "
        f"{result['validation']['raw_mismatched_values']} sai khác; prediction mismatches = "
        f"{result['validation']['prediction_mismatched_values']}.",
        f"- So mọi trường của `card_verdicts.json`, kể cả rows/cells/by_h và provenance: "
        f"{comp['fields_matched']}/{comp['fields_checked']}. "
        f"{comp['rounding_differences']} sai khác làm tròn trong tolerance; max absolute = "
        f"{comp['max_absolute_numeric_difference']:.12g}, tại `{comp['max_difference_path']}`.",
        f"- Tolerance chỉ để đối chiếu số: rtol={RTOL:g}, atol={ATOL:g}; không thêm epsilon vào tiêu chí card.",
        f"- Self-test giải tích và ngưỡng: {result['validation']['self_tests']['tests_run']} PASS, "
        f"{result['validation']['self_tests']['failures']} FAIL, {result['validation']['self_tests']['errors']} ERROR; "
        "bao gồm reference action từ tập rollout riêng, exact tie, signed regret âm, "
        "ngưỡng 2SE/evaluability, abstention và phát hiện sai khác lồng nhau.",
        "", "```bash", "python -B experiments/letter/x4b_rescore_independent.py --self-test",
        "python -B experiments/letter/x4b_rescore_independent.py",
        "python -B experiments/letter/x4b_rescore_independent.py --check-only", "```", "",
        "Source: `experiments/letter/x4b_rescore_independent.py`. "
        "Kết quả và toàn bộ trường tính lại: `results/letter/x_rescore/rescore_x4b.json`. "
        "Báo cáo: `results/letter/x_rescore/RESCORE_X4B.md`. "
        "Không tạo CSV, biểu đồ hoặc file log mới; stdout và kiểm tra nằm trong JSON/báo cáo. "
        "Không sửa artifact gốc, không commit.", "",
        "Rescore xác nhận tính tái lập của phép chấm trên raw đã lưu; không kiểm chứng lại simulator "
        "hay suy ra external validity, novelty hoặc độ chính xác của Monte Carlo ngoài các kiểm tra này.",
    ]
    if comp["mismatches"]:
        lines += ["", "Sai khác từng trường:", "", "```json", json.dumps(comp["mismatches"], ensure_ascii=False, indent=2), "```"]
    return "\n".join(lines) + "\n"


def run_self_tests(stream=None) -> dict:
    """Analytic boundary checks; no data files or experiment modules are read."""
    class RescoreTests(unittest.TestCase):
        def test_paired_gain_at_two_se(self):
            self.assertEqual(paired_reading(-4, 2), "GAIN")

        def test_paired_loss_at_two_se(self):
            self.assertEqual(paired_reading(4, 2), "LOSS")

        def test_paired_zero_is_unresolved(self):
            self.assertEqual(paired_reading(0, 0), "UNRESOLVED")

        def test_paired_low_resolution(self):
            self.assertEqual(paired_reading(-3.9, 2), "UNRESOLVED")

        def test_sample_se(self):
            self.assertAlmostEqual(standard_error([1, 3]), 1.0)

        def test_b2_minimum(self):
            self.assertEqual(b2_verdict(19, 19), "NOT_EVALUABLE")

        def test_b2_threshold_inclusive(self):
            self.assertEqual(b2_verdict(20, 19), "STANDS")

        def test_b2_below_threshold(self):
            self.assertEqual(b2_verdict(20, 18), "DOES_NOT_STAND")

        def test_b3_magnitude_threshold_inclusive(self):
            cell = b3_cell(("T", 300, 3600), [(0.25, 100), (0.25, 100)], 1)
            self.assertTrue(cell["resolved"] and cell["correct"])

        def test_b3_requires_magnitude(self):
            cell = b3_cell(("T", 300, 3600), [(0.249, 100)] * 2, 1)
            self.assertFalse(cell["resolved"])

        def test_b3_requires_day_precision(self):
            cell = b3_cell(("T", 300, 3600), [(0, 100), (2, 100)], 1)
            self.assertFalse(cell["resolved"])

        def test_b3_abstention(self):
            cell = b3_cell(("T", 300, 3600), [(-1, 100)] * 2, 0)
            self.assertTrue(cell["resolved"] and cell["abstention"])
            self.assertFalse(cell["correct"])

        def test_b3_one_day_cannot_resolve(self):
            self.assertFalse(b3_cell(("T", 300, 3600), [(1, 100)], 1)["resolved"])

        def test_zero_reference_is_null(self):
            self.assertIsNone(percent(1, 0))

        def test_signed_strict_contributions_preserved(self):
            rows = [{"instances": 2, "tie_instances": 1, "strict_instances": 1,
                     "regret_sum_Mbit_s": 2., "tie_regret_sum_Mbit_s": 3.,
                     "strict_regret_sum_Mbit_s": -1.}]
            summary = strict_summary(rows)
            self.assertEqual(summary["strict_regret_share"], -0.5)
            self.assertEqual(summary["instances"], 2)

        def test_zero_total_share_is_null(self):
            self.assertIsNone(strict_summary([])["strict_regret_share"])

        def test_comparison_finds_missing_fields(self):
            self.assertEqual(compare_fields({"a": 1}, {"b": 1})["status"], "MISMATCH")

        def test_comparison_finds_nested_mismatch(self):
            c = compare_fields({"B1": {"rows": [{"x": 1}]}}, {"B1": {"rows": [{"x": 2}]}})
            self.assertEqual(c["mismatches"][0]["path"], "B1.rows[0].x")

        def test_comparison_checks_types(self):
            self.assertEqual(compare_fields(True, 1)["status"], "MISMATCH")

        def test_comparison_checks_list_length(self):
            self.assertEqual(compare_fields([1], [1, 2])["status"], "MISMATCH")

        def test_comparison_accepts_roundoff(self):
            self.assertEqual(compare_fields(1.0 + 1e-13, 1.0)["status"], "MATCH")

        def test_nan_does_not_match(self):
            self.assertEqual(compare_fields(float("nan"), float("nan"))["status"], "MISMATCH")

        @staticmethod
        def analytic_record():
            # Evaluation prefers Switch (3 vs 10), but the independently drawn
            # reference rollouts prefer Stay. A switch must retain regret -7.
            n, nh = 32, len(HORIZONS)
            fresh = np.zeros((n, 2, nh))
            stale = np.zeros((n, 2, 2, nh))
            stale[:, 0, 1] = -1
            stale[:, 1, 1] = 1
            evaluation = np.empty((n, 128, 2, nh))
            evaluation[:, :, 0] = 10
            evaluation[:, :, 1] = 3
            reference_rollouts = np.zeros((n, 64, 2, nh))
            reference_rollouts[:, :, 1] = 1
            decisions = np.ones((n, 3, 3, nh), dtype=np.int16)
            decisions[:, 0, 0] = 0
            decisions[:, 0, 2] = 0
            ties = np.zeros((n, 3, 3, nh), dtype=bool)
            ties[:, 0, 0] = True
            costs = np.full((n, 3, 3, nh), 3.)
            costs[:, 0, 0] = 10
            costs[:, 0, 2] = 10
            values = np.empty((n, 2, nh))
            values[:, 0] = 10
            values[:, 1] = 3
            gain = np.zeros((n, 3, 2, nh))
            gain[:, 0, 0] = -7
            return {
                "h_seconds": np.array(HORIZONS), "tau_seconds": np.array(AGES),
                "pipelines": np.array(RULES), "sides": np.array(SIDES),
                "M0_predicted_fresh": fresh, "M0_predicted_stale": stale,
                "s_hat_Mbit": np.array([-1.]), "paired_evaluation": evaluation,
                "reference_decision_rollouts": reference_rollouts,
                "decisions": decisions, "tie_flags": ties,
                "reference_decision": np.zeros((n, nh), dtype=np.int16),
                "reference_tie_flags": np.zeros((n, nh), dtype=bool),
                "V": values, "C_ref": np.full((n, nh), 10.),
                "costs": costs, "regret": costs - 10,
                "G_S": gain, "paired_Hybrid_minus_Stationary": np.zeros((n, 3, nh)),
                "mean_reference_backlog_Mbit": 10 / np.array(HORIZONS),
                "evaluable": np.zeros(nh, dtype=bool),
            }

        def test_rebuild_separate_reference_and_negative_regret(self):
            raw = self.analytic_record()
            checks = ArrayChecks()
            rebuilt, _, _ = rebuild_record(raw, {"regime": "T", "date": "synthetic"}, checks)
            self.assertEqual(sum(g["mismatched_values"] for g in checks.groups.values()), 0)
            self.assertTrue(np.all(rebuilt["C_ref"] == 10))
            self.assertTrue(np.all(rebuilt["regret"][:, 1] == -7))
            self.assertTrue(np.all(rebuilt["decisions"][:, 0, 0] == 0))

        def test_rebuild_evaluability_ignores_saved_flag(self):
            raw = self.analytic_record()
            # Exactly representable integer costs just above the gate; saved
            # C_ref and evaluability deliberately remain the old, wrong ones.
            expected_reference = np.ceil(0.001*C0_MBPS*np.array(HORIZONS))
            raw["paired_evaluation"][:, :, 0, :] = expected_reference
            checks = ArrayChecks()
            rebuilt, reference, _ = rebuild_record(raw, {"regime": "T", "date": "gate"}, checks)
            np.testing.assert_array_equal(reference, expected_reference)
            self.assertTrue(rebuilt["evaluable"].all())
            self.assertEqual(checks.groups["evaluable"]["mismatched_values"], len(HORIZONS))

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(RescoreTests)
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return {"status": "PASS" if result.wasSuccessful() else "FAIL", "tests_run": result.testsRun,
            "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run analytic checks without reading data or writing outputs")
    parser.add_argument("--check-only", action="store_true", help="Recompute and compare without writing outputs")
    args = parser.parse_args()
    if args.self_test:
        return 0 if run_self_tests()["status"] == "PASS" else 1
    self_tests = run_self_tests(stream=io.StringIO())
    if self_tests["status"] != "PASS":
        print(json.dumps(self_tests), file=sys.stderr)
        return 1
    repo = Path(__file__).resolve().parents[2]
    try:
        result = recompute(CommittedInputs(repo))
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"INPUT_OR_SCHEMA_FAILURE: {error}", file=sys.stderr)
        return 2
    result["validation"]["self_tests"] = self_tests
    if not args.check_only:
        folder = repo / OUTPUT
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "rescore_x4b.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        (folder / "RESCORE_X4B.md").write_text(render_report(result), encoding="utf-8")
    card = result["recomputed_card_verdicts"]
    print(json.dumps({
        "status": result["status"],
        "fields_checked": result["comparison"]["fields_checked"],
        "field_mismatches": len(result["comparison"]["mismatches"]),
        "receipt_npz_sha256_checked": result["provenance"]["records_receipt_sha256_checked"],
        "raw_array_mismatches": result["validation"]["raw_mismatched_values"],
        "B1": card["B1"]["counts"],
        "B2": {k: card["B2"][k] for k in ("verdict", "cases", "not_worse")},
        "B3a": {k: card["B3a"][k] for k in ("verdict", "resolved")},
        "B3b_strict_regret_pct": card["B3b"]["strict_regret_pct"],
        "outputs_written": not args.check_only,
        "self_tests": self_tests,
    }, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "MATCH" else 1


if __name__ == "__main__":
    raise SystemExit(main())
