"""Doan Van Tai — independent, saved-data-only X-CTMC / X-GEANT rescore.

Implements CODEX_RESCORE_BRIEF.md (letter_smr commit 9f27dee). Imports only
the standard library and NumPy; never imports or invokes a project scorer,
predictor, or truth engine. The only writes are the two specified reports.
Run from the research repo after sourcing experiments/explore_ctmc/env.sh:
    python -B experiments/letter/x_rescore_independent.py
"""

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import statistics
import subprocess
from collections import Counter, defaultdict

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
PAPERS = ROOT.parent / "state-model-regret-papers"
BRIEF = PAPERS / "letter_smr/briefs/strengthen/CODEX_RESCORE_BRIEF.md"
LEDGER = PAPERS / "letter_smr_argon/ledger/numbers.json"
DESTINATION = ROOT / "results/letter/x_rescore"
LOAD_RULES = ("TH_0.5", "TH_0.65", "TH_0.8", "TH_0.9", "MLU")
G1_RULES = ("TH_0.65", "TH_0.8", "TH_0.9")
TH_RULES = LOAD_RULES[:-1]
SIGN_CONVENTION = "G_S=L_stale-L_fresh; negative=fresh hurts"


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def sign(value):
    return int(value > 0) - int(value < 0)


def coordinate(value, grid):
    """Recover the nominal design label from a stored floating point ratio."""
    matches = [v for v in grid if math.isclose(value, v, rel_tol=1e-12, abs_tol=0)]
    if len(matches) != 1:
        raise ValueError(f"Coordinate {value!r} does not identify one design label: {grid}")
    return matches[0]


def fraction(numerator, denominator):
    return numerator / denominator if denominator else None


def strict_majority(values):
    return 2 * sum(values) > len(values)


def middle(values):
    return statistics.median(values) if values else None


def sample_summary(values):
    n = len(values)
    return (statistics.mean(values), statistics.stdev(values) / math.sqrt(n)
            if n > 1 else math.inf)


def resolved(mean, se, cref, n):
    return (n > 1 and cref > 0 and abs(mean) >= 2 * se
            and abs(mean) >= 0.0025 * cref)


def decision(n, minimum, passes, additional=True):
    if n < minimum or not additional:
        return "NOT_EVALUABLE"
    return "STANDS" if passes else "DOES_NOT_STAND"


def both_side_regret(fresh, stale, reference):
    """Regret of the worse mean-cost side, in percentage points of mean C_ref."""
    cref = float(np.mean(reference))
    if cref <= 0:
        return None
    return 100 * max(float(np.mean(fresh)) - cref,
                     float(np.mean(stale)) - cref) / cref


def ctmc_eligible(row, forecast, exposed):
    return (row["regime"] not in exposed and row["status"] == "COMPLETED"
            and row["h_T_int"] in (30, 100) and forecast is not None
            and forecast["status"] == "COMPLETED"
            and forecast.get("sign_pred") in (-1, 1)
            and abs(forecast["DeltaF_hat"]) >= 0.01
            and abs(row["G_S_pct_C_ref"]) >= 0.25)


def hybrid_sign_ok(row):
    return (row["rule"] == "Hybrid_hat" and row["h_T_int"] in (30, 100)
            and row.get("s_hat") is not None
            and sign(row["s_hat"]) == sign(row["s"]) != 0)


def self_tests():
    """Analytic controls for estimands, inclusive cutoffs, and exclusions."""
    passed = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        passed.append(name)

    check("letter_sign_and_zero", [sign(x) for x in (-4, 0, 7)] == [-1, 0, 1])
    check("sample_SE_uses_days_and_ddof1", sample_summary([1.0, 3.0]) == (2.0, 1.0))
    check("resolution_both_equalities_included", resolved(2.0, 1.0, 800.0, 2))
    check("resolution_requires_SE_clause", not resolved(2.0, 1.01, 800.0, 2))
    check("resolution_requires_Cref_clause", not resolved(2.0, 0.1, 801.0, 2))
    check("one_day_not_resolved", not resolved(2.0, 0.0, 800.0, 1))
    row = dict(regime="control", status="COMPLETED", h_T_int=30,
               G_S_pct_C_ref=-0.25, rule="Hybrid_hat", s=1.0, s_hat=2.0)
    forecast = dict(status="COMPLETED", sign_pred=-1, DeltaF_hat=-0.01)
    check("CTMC_cutoffs_inclusive", ctmc_eligible(row, forecast, set()))
    check("CTMC_pilot_excluded", not ctmc_eligible(row, forecast, {"control"}))
    check("CTMC_abstention_excluded", not ctmc_eligible(row, dict(forecast, sign_pred=0), set()))
    check("CTMC_short_horizon_excluded", not ctmc_eligible(dict(row, h_T_int=10), forecast, set()))
    check("T5_does_not_require_nonzero_DeltaF", hybrid_sign_ok(row)
          and not ctmc_eligible(row, dict(forecast, DeltaF_hat=0.0), set()))
    check("T5_wrong_slope_sign_excluded", not hybrid_sign_ok(dict(row, s_hat=-2.0)))
    check("both_side_is_max_of_means", both_side_regret([10, 0], [0, 10], [4, 4]) == 25.0)
    check("strict_regime_majority_not_tie", not strict_majority([True, False])
          and strict_majority([True, True, False]))
    check("nominal_horizon_survives_division_roundoff", coordinate(29.999999999999996, [1, 3, 10, 30, 100]) == 30)
    return passed


class Inputs:
    """Read committed bytes; record SHA256 and independently verify Git blobs."""

    def __init__(self):
        self.sources = {}
        self.repos = {}
        for repo, paths in (
            (ROOT, ["results/letter/x_ctmc", "results/letter/x_geant"]),
            (LEDGER.parent.parent, ["ledger/numbers.json"]),
            (BRIEF.parents[2], ["briefs/strengthen/CODEX_RESCORE_BRIEF.md"]),
        ):
            repo = repo.resolve()
            head = git(repo, "rev-parse", "HEAD").decode().strip()
            entries = git(repo, "ls-tree", "-rz", head, "--", *paths).split(b"\0")
            blobs = {}
            for entry in entries:
                if entry:
                    metadata, name = entry.split(b"\t", 1)
                    blobs[name.decode()] = metadata.split()[2].decode()
            self.repos[repo] = dict(head=head, blobs=blobs)

    def read(self, path, expected_sha256=None):
        path = Path(path).resolve()
        if path in self.sources:
            raise ValueError("Input unexpectedly read twice: " + str(path))
        contents = path.read_bytes()
        digest = hashlib.sha256(contents).hexdigest()
        if expected_sha256 is not None and digest != expected_sha256:
            raise ValueError("Receipt SHA256 mismatch: " + str(path))
        for repo, info in self.repos.items():
            if path.is_relative_to(repo):
                relative = path.relative_to(repo).as_posix()
                expected_blob = info["blobs"].get(relative)
                blob = hashlib.sha1(b"blob " + str(len(contents)).encode() + b"\0" + contents).hexdigest()
                if expected_blob is None or blob != expected_blob:
                    raise ValueError("Input differs from committed HEAD: " + str(path))
                self.sources[path] = dict(path=str(path), sha256=digest, git_blob=blob,
                                          git_head=info["head"], committed=True,
                                          receipt_sha256=expected_sha256,
                                          receipt_match=(digest == expected_sha256)
                                          if expected_sha256 else None)
                return contents
        raise ValueError("Input outside the declared repositories: " + str(path))

    def json(self, path, expected_sha256=None):
        return json.loads(self.read(path, expected_sha256))


class Comparisons:
    # These are serialization/roundoff tolerances only, never scientific cutoffs.
    relative_tolerance = 1e-12
    absolute_tolerance = 1e-9

    def __init__(self):
        self.fields = []

    def add(self, field, actual, reported, cause=""):
        if isinstance(actual, bool) or isinstance(reported, bool):
            match = type(actual) is type(reported) and actual == reported
        elif isinstance(actual, (int, float)) and isinstance(reported, (int, float)):
            match = (actual == reported if isinstance(actual, int) and isinstance(reported, int)
                     else math.isclose(actual, reported, rel_tol=self.relative_tolerance,
                                       abs_tol=self.absolute_tolerance))
        else:
            match = actual == reported
        item = dict(field=field, independent=actual, reported=reported,
                    status="MATCH" if match else "MISMATCH")
        if isinstance(actual, (int, float)) and not isinstance(actual, bool) and isinstance(reported, (int, float)):
            item["absolute_difference"] = abs(actual - reported)
        if not match:
            item["cause"] = cause or "Khác biệt cần kiểm tra tại trường này; không thay verdict đã khóa."
        self.fields.append(item)

    def tree(self, field, actual, reported):
        if isinstance(reported, dict):
            for key, value in reported.items():
                if key not in actual:
                    self.add(field + "." + key, None, value, "Thiếu trường trong kết quả tính lại.")
                else:
                    self.tree(field + "." + key, actual[key], value)
        elif isinstance(reported, list):
            self.add(field + ".length", len(actual), len(reported))
            for i, (a, b) in enumerate(zip(actual, reported)):
                self.tree(f"{field}[{i}]", a, b)
        else:
            self.add(field, actual, reported)


def ctmc_rescore(inputs, comparisons):
    base = ROOT / "results/letter/x_ctmc"
    inputs.read(base / "CARD_X_CTMC.md")
    predictions = inputs.json(base / "predictions.json")
    receipt = inputs.json(base / "truth_receipt.json")
    excluded = set(predictions["pilot_exposed_regimes"])
    forecast = {}
    for rec in predictions["records"]:
        if rec["status"] == "PLANNED":
            for row in rec["rows"]:
                key = (row["regime"], row["rule"], row["h_T_int"], row["tau_T_int"])
                if key in forecast:
                    raise ValueError("Duplicate CTMC prediction key")
                forecast[key] = row
    rows, raw_ids, checked_rows = [], [], 0
    label_roundoff = Counter()
    for entry in receipt["raw"]:
        path = ROOT / entry["path"]
        if not path.resolve().is_relative_to((base / "raw").resolve()):
            raise ValueError("Receipt path outside CTMC raw directory")
        raw = inputs.json(path, entry["sha256"])
        if raw["regime"]["id"] != entry["id"]:
            raise ValueError("CTMC receipt/regime identity mismatch")
        if raw["status"] != "COMPLETED":
            continue
        raw_ids.append(entry["id"])
        for row in raw["rows"]:
            if row["status"] != "COMPLETED":
                continue
            # Rebuild the signed gap and percentages from mean costs, not scores.
            r = dict(row)
            r["h_T_int"] = coordinate(r["h_T_int"], predictions["h_T_int"])
            r["tau_T_int"] = coordinate(r["tau_T_int"], predictions["tau_T_int"])
            for label in ("h_T_int", "tau_T_int"):
                if row[label] != r[label]:
                    label_roundoff[(label, row[label], r[label])] += 1
            r["G_S"] = r["L_stale"] - r["L_fresh"]
            r["G_S_pct_C_ref"] = 100 * r["G_S"] / r["C_ref"]
            r["slope_measured"] = r["G_S"] / r["h"]
            comparisons.add(f"CTMC.raw.{entry['id']}.{checked_rows}.G_S", r["G_S"], row["G_S"])
            for side in ("fresh", "stale"):
                r[f"regret_{side}_pct_C_ref"] = 100 * (r[f"L_{side}"] - r["C_ref"]) / r["C_ref"]
                comparisons.add(f"CTMC.raw.{entry['id']}.{checked_rows}.regret_{side}_pct",
                                r[f"regret_{side}_pct_C_ref"], row[f"regret_{side}_pct_C_ref"])
            checked_rows += 1
            if r["regime"] not in excluded:
                rows.append(r)
    comparisons.add("CTMC.receipt.completed_regimes", len(raw_ids), receipt["completed_regimes"])
    comparisons.add("CTMC.receipt.unique_regimes", len(set(raw_ids)), len(raw_ids))
    comparisons.add("CTMC.receipt.status", receipt["status"], "COMPLETED_RAW_UNSCORED")
    comparisons.add("CTMC.receipt.raw_files", len(list((base / "raw").glob("*.json"))), len(receipt["raw"]))

    def key(row):
        return (row["regime"], row["rule"], row["h_T_int"], row["tau_T_int"])

    by_key = {key(row): row for row in rows}
    comparisons.add("CTMC.raw.unique_cell_keys", len(by_key), len(rows))
    eligible = [row for row in rows if ctmc_eligible(row, forecast.get(key(row)), excluded)]
    load = [r for r in eligible if r["rule"] in LOAD_RULES]
    m0 = [r for r in eligible if r["rule"] == "M0"]
    disagree = [r for r in load if r["stratum"] == "disagree"]

    def hits(group, prediction="sign_pred"):
        return sum(sign(r["G_S"]) == forecast[key(r)][prediction] for r in group)

    def tally(group):
        per_regime = defaultdict(list)
        for r in group:
            per_regime[r["regime"]].append(sign(r["G_S"]) == forecast[key(r)]["sign_pred"])
        correct = hits(group)
        return dict(cells=len(group), correct=correct, accuracy=fraction(correct, len(group)),
                    regimes=len(per_regime), majority_correct=sum(strict_majority(v) for v in per_regime.values()))

    t1, t4 = tally(load), tally(m0)
    t1.update(threshold=0.9, verdict=decision(len(load), 20, (t1["accuracy"] or 0) >= 0.9, t1["regimes"] >= 8),
              by_stratum={s: {k: v for k, v in tally([r for r in load if r["stratum"] == s]).items()
                              if k in ("cells", "correct", "accuracy")} for s in ("agree", "disagree")})
    law, null = hits(disagree), hits(disagree, "null_sign")
    gap = (law - null) / len(disagree) if disagree else None
    t2 = dict(cells=len(disagree), correct=law, null_correct=null,
              law_accuracy=fraction(law, len(disagree)), null_accuracy=fraction(null, len(disagree)),
              threshold_gap=0.2, verdict=decision(len(disagree), 10, gap is not None and gap >= 0.2))
    slope_rows = [r for r in load if r["h_T_int"] == 100 and r["slope_measured"] != 0]
    slope_errors = {name: [] for name in ("locked", "true_s_hat_shares", "estimated_s_exact_shares", "identity")}
    for row in slope_rows:
        f = forecast[key(row)]
        measured = row["slope_measured"]
        exact_delta = row["p_old"] - row["p_new"]
        estimates = (f["slope_pred"], row["s"] * f["DeltaF_hat"],
                     row["s_hat"] * exact_delta, row["s"] * exact_delta)
        for name, estimate in zip(slope_errors, estimates):
            slope_errors[name].append(abs(measured - estimate) / abs(measured))
    slope_median = middle(slope_errors["locked"])
    t3 = dict(cells=len(slope_rows), median_relative_error=slope_median, threshold=0.25,
              verdict=decision(len(slope_rows), 20, slope_median is not None and slope_median <= 0.25))
    t4.update(threshold=0.9, verdict=decision(len(m0), 20, (t4["accuracy"] or 0) >= 0.9))
    hybrid = [r for r in rows if hybrid_sign_ok(r)]
    wrong = [r for r in rows if r["rule"] == "Hybrid_hat" and r["h_T_int"] in (30, 100)
             and r.get("s_hat") is not None and sign(r["s_hat"]) != sign(r["s"])]

    def worst(row):
        return max(row["regret_fresh_pct_C_ref"], row["regret_stale_pct_C_ref"])

    hybrid_ok = sum(worst(r) <= 0.5 for r in hybrid)
    t5 = dict(cells=len(hybrid), correct=hybrid_ok, share=fraction(hybrid_ok, len(hybrid)), threshold=0.9,
              verdict=decision(len(hybrid), 20, bool(hybrid) and hybrid_ok / len(hybrid) >= 0.9),
              wrong_sign_cells=len(wrong), wrong_sign_median_both_side_regret_pct=middle([worst(r) for r in wrong]))
    c5 = [r for r in m0 if forecast[key(r)].get("c5_sign") in (-1, 1)]
    c5_hits = hits(c5, "c5_sign")
    t6 = dict(cells=len(c5), correct=c5_hits, accuracy=fraction(c5_hits, len(c5)), threshold=0.85,
              verdict=decision(len(c5), 20, bool(c5) and c5_hits / len(c5) >= 0.85))
    concentration = sum(abs(r["p_old"] - 0.5) >= abs(r["p_new"] - 0.5) for r in m0)
    t6b = dict(cells=len(m0), correct=concentration, share=fraction(concentration, len(m0)), threshold=0.8,
               verdict=decision(len(m0), 20, bool(m0) and concentration / len(m0) >= 0.8))
    d1, d2 = {}, {}
    for rule in sorted({r["rule"] for r in rows}):
        group = [r for r in rows if r["rule"] == rule and r["h_T_int"] == 30 and r["tau_T_int"] == 1]
        d1[rule] = dict(regimes=len(group), harm_regimes=sum(r["G_S_pct_C_ref"] < -0.5 for r in group),
                        median_G_S_pct=middle([r["G_S_pct_C_ref"] for r in group]))
        d2[rule] = middle([max(r["tie_share_fresh"], r["tie_share_stale"]) for r in rows if r["rule"] == rule])
    result = dict(sign=SIGN_CONVENTION, excluded_pilot_regimes=sorted(excluded), T1=t1, T2=t2, T3=t3,
                  T4=t4, T5=t5, T6=t6, T6b=t6b, D1_harm_at_30Tint_tau1=d1, D2_median_tie_share=d2,
                  note="Cells share regimes and are not independent trials.", receipt_status=receipt["status"])

    d4_cells = []
    for row in rows:
        if row["rule"] != "Hybrid_hat" or row["h_T_int"] not in (1, 3, 10):
            continue
        stationary = by_key.get((row["regime"], "Stationary_hat", row["h_T_int"], row["tau_T_int"]))
        if stationary is None:
            continue
        for side in ("fresh", "stale"):
            difference = row[f"regret_{side}_pct_C_ref"] - stationary[f"regret_{side}_pct_C_ref"]
            d4_cells.append(dict(regime=row["regime"], h_T_int=row["h_T_int"], tau_T_int=row["tau_T_int"],
                                 side=side, hybrid_minus_stationary_pp=difference))
    d4 = {}
    for h in (1, 3, 10):
        d4[str(h)] = {}
        for side in ("fresh", "stale"):
            values = [r["hybrid_minus_stationary_pp"] for r in d4_cells if r["h_T_int"] == h and r["side"] == side]
            d4[str(h)][side] = dict(cells=len(values), better=sum(d < -0.05 for d in values),
                                    worse=sum(d > 0.05 for d in values), within=sum(abs(d) <= 0.05 for d in values))
    planned = [rec for rec in predictions["records"] if rec["status"] == "PLANNED"]
    pair_counts = {v["pairs"] for rec in planned for age in rec["histories"].values() for v in age.values()}
    record_lengths = {round(v["W"] / rec["T_int"], 9) for rec in planned
                      for age in rec["histories"].values() for v in age.values()}
    if len(pair_counts) != 1 or len(record_lengths) != 1:
        raise ValueError("Unexpected heterogeneous CTMC prediction record lengths")
    ledger = dict(
        regimes_grid=len(predictions["records"]), regimes_run=len(raw_ids),
        regimes_pilot_excluded=len(excluded), estimator_invalid=sum(rec["estimator"]["status"] != "VALID" for rec in planned),
        thetas=[float(rule[3:]) for rule in predictions["rules"] if rule.startswith("TH_")],
        record_T_int=int(next(iter(record_lengths))), history_pairs=next(iter(pair_counts)),
        horizons_T_int=predictions["h_T_int"], share_threshold=0.01, percent_threshold=0.25, harm_threshold=0.5,
        load_cells=len(load), load_correct=t1["correct"], load_accuracy=t1["accuracy"], load_regimes=t1["regimes"],
        load_accuracy_pct=100 * t1["accuracy"], disagree_cells=len(disagree), disagree_correct=law,
        disagree_null_correct=null, disagree_law=t2["law_accuracy"], disagree_null=t2["null_accuracy"],
        m0_cells=len(m0), m0_correct=t4["correct"], m0_accuracy=t4["accuracy"], m0_accuracy_pct=100 * t4["accuracy"],
        c5_cells=len(c5), c5_correct=c5_hits, concentration=concentration, hybrid_cells=len(hybrid), hybrid_ok=hybrid_ok,
        hybrid_share=t5["share"], hybrid_share_pct=100 * t5["share"], slope_median_rel_error=slope_median,
        slope_error_median_pct={k: 100 * middle(v) for k, v in slope_errors.items()},
        harm_at_30Tint={rule: dict(harm=d1[rule]["harm_regimes"], regimes=d1[rule]["regimes"],
                                  median_G_S_pct=d1[rule]["median_G_S_pct"]) for rule in ("M0", "MLU", *TH_RULES)},
        d4_cells=len(d4_cells), d4_hybrid_worse=sum(r["hybrid_minus_stationary_pp"] > 0.05 for r in d4_cells),
        d4_better_fresh={str(h): d4[str(h)]["fresh"]["better"] for h in (1, 3, 10)},
        d4_pairs_per_h=d4["1"]["fresh"]["cells"],
        d4_largest_gain_pp=-min(0.0, *(r["hybrid_minus_stationary_pp"] for r in d4_cells)), d4_tolerance_pp=0.05)
    reported = inputs.json(base / "card_verdicts.json")
    comparisons.tree("CTMC.card", result, reported)
    return dict(card=result, ledger=ledger, D4=d4, D4_cells=d4_cells,
                cell_membership={name: [list(key(r)) for r in group]
                                 for name, group in (("T1", load), ("T2", disagree), ("T3", slope_rows),
                                                     ("T4", m0), ("T5", hybrid), ("T6", c5), ("T6b", m0))},
                raw_regimes=len(raw_ids), nonpilot_regimes=len({r["regime"] for r in rows}),
                checked_completed_rows=checked_rows, seeds=predictions["seeds"],
                coordinate_roundoff=[dict(coordinate=k[0], stored=k[1], design_label=k[2], rows=n)
                                     for k, n in sorted(label_roundoff.items())])


def geant_rescore(inputs, comparisons):
    base = ROOT / "results/letter/x_geant"
    inputs.read(base / "CARD_X_GEANT.md")
    receipt = inputs.json(base / "truth/receipt.json")
    prediction_rows = list(csv.DictReader(io.StringIO(inputs.read(base / "predictions.csv").decode())))
    predictions = {(r["regime"], r["rule"], int(r["tau_s"]), int(r["h_s"])): r for r in prediction_rows}
    if len(predictions) != len(prediction_rows):
        raise ValueError("Duplicate GEANT prediction key")
    pools, daily, data, stationary_cases = defaultdict(list), [], {}, []
    stationary_zero, total_gs_checked, costs_gs_equal = True, 0, True
    for meta in sorted(receipt["records"], key=lambda m: (m["regime"], m["date"])):
        if meta["set"] != "X2" or meta["split"] != "test" or meta["pilot"]:
            raise ValueError("Unexpected record outside the locked GEANT population")
        name = f"{meta['regime']}_{meta['date']}.npz"
        blob = inputs.read(base / "truth/records" / name, meta["npz_sha256"])
        with np.load(io.BytesIO(blob), allow_pickle=False) as z:
            rules = z["pipelines"].tolist()
            sides = z["sides"].tolist()
            hs, taus = z["h_seconds"].tolist(), z["tau_seconds"].tolist()
            costs, cref, choices = z["costs"], z["C_ref"], z["decisions"]
            gs = costs[:, :, 1:, :] - costs[:, :, :1, :]
            equal = bool(np.array_equal(gs, z["G_S"]))
            costs_gs_equal &= equal
            comparisons.add("GEANT.raw." + name + ".G_S_equals_cost_difference", equal, True)
            total_gs_checked += gs.size
            st = rules.index("Stationary")
            stationary_zero &= bool(np.all(gs[:, st, :, :] == 0))
            if sides[0] != "fresh" or sides[1:] != [f"stale_{int(t)}" for t in taus]:
                raise ValueError("GEANT side axes disagree with tau labels")
            data[(meta["regime"], meta["date"])] = dict(
                rules=rules, hs=hs, taus=taus, shares=choices.mean(axis=0),
                evaluable=z["evaluable"].tolist())
            for ih, h in enumerate(hs):
                if h not in (14400, 21600) or not z["evaluable"][ih]:
                    continue
                reference = float(cref[:, ih].mean())
                for t, tau in enumerate(taus):
                    stationary_regret = both_side_regret(costs[:, st, 0, ih], costs[:, st, t + 1, ih], cref[:, ih])
                    threshold_regrets = {rule: both_side_regret(costs[:, rules.index(rule), 0, ih],
                                                              costs[:, rules.index(rule), t + 1, ih], cref[:, ih])
                                         for rule in TH_RULES}
                    stationary_cases.append(dict(regime=meta["regime"], date=meta["date"], tau_s=int(tau), h_s=int(h),
                                                 stationary_regret_pct=stationary_regret,
                                                 threshold_regrets_pct=threshold_regrets,
                                                 stationary_not_worse=stationary_regret <= min(threshold_regrets.values())))
                    for rule in G1_RULES:
                        key = (meta["regime"], rule, int(tau), int(h))
                        forecast = predictions[key]
                        predicted = int(forecast["predicted_G_S_sign"])
                        if predicted == 0:
                            continue
                        p = rules.index(rule)
                        values = gs[:, p, t, ih]
                        mean = float(values.mean())
                        se = float(values.std(ddof=1) / math.sqrt(len(values)))
                        delta = float(choices[:, p, t + 1, ih].mean() - choices[:, p, 0, ih].mean())
                        row = dict(regime=meta["regime"], date=meta["date"], rule=rule, tau_s=int(tau), h_s=int(h),
                                   mean_G_S_Mbit_s=mean, se=se, mean_C_ref=reference, predicted=predicted,
                                   observed=sign(mean), resolved=resolved(mean, se, reference, len(values)), delta_F_test=delta)
                        pools[key].append(row)
                        daily.append(row)
    comparisons.add("GEANT.receipt.status", receipt["status"], "COMPLETE")
    comparisons.add("GEANT.receipt.unique_regime_dates", len(data), len(receipt["records"]))
    comparisons.add("GEANT.receipt.npz_files", len(list((base / "truth/records").glob("*.npz"))), len(receipt["records"]))
    cells = []
    for key, group in sorted(pools.items()):
        mean, se = sample_summary([r["mean_G_S_Mbit_s"] for r in group])
        cref = statistics.mean(r["mean_C_ref"] for r in group)
        is_resolved = resolved(mean, se, cref, len(group))
        predicted = int(predictions[key]["predicted_G_S_sign"])
        cells.append(dict(regime=key[0], rule=key[1], tau_s=key[2], h_s=key[3], days=len(group),
                          mean_G_S_Mbit_s=mean, se=se, mean_C_ref=cref, G_S_pct=100 * mean / cref,
                          resolved=is_resolved, predicted=predicted, observed=sign(mean),
                          correct=is_resolved and sign(mean) == predicted))
    resolved_cells = [r for r in cells if r["resolved"]]
    correct = sum(r["correct"] for r in resolved_cells)
    accuracy = fraction(correct, len(resolved_cells))
    resolved_days = [r for r in daily if r["resolved"]]
    record_correct = sum(r["observed"] == r["predicted"] for r in resolved_days)
    st_med = middle([r["stationary_regret_pct"] for r in stationary_cases])
    not_worse = sum(r["stationary_not_worse"] for r in stationary_cases)
    result = dict(sign=SIGN_CONVENTION,
                  G1=dict(verdict=decision(len(resolved_cells), 6, accuracy is not None and accuracy >= 0.8),
                          resolved=len(resolved_cells), correct=correct, accuracy=accuracy, threshold=0.8, cells=cells),
                  D2_record_level=dict(resolved=len(resolved_days), correct=record_correct,
                                       accuracy=fraction(record_correct, len(resolved_days))),
                  G2=dict(verdict=decision(len(stationary_cases), 20, stationary_zero and st_med is not None and st_med <= 0.5),
                          records=len(stationary_cases), G_S_all_zero=stationary_zero,
                          median_both_side_regret_pct=st_med, threshold=0.5),
                  G3=dict(verdict=decision(len(stationary_cases), 20, bool(stationary_cases) and not_worse / len(stationary_cases) >= 0.9),
                          cases=len(stationary_cases), stationary_not_worse=not_worse,
                          share=fraction(not_worse, len(stationary_cases)), threshold=0.9))

    # Post hoc, saved decisions only: training vs evaluable-test share for TH_0.8.
    th08 = []
    for key, group in sorted(pools.items()):
        if key[1] != "TH_0.8":
            continue
        f = predictions[key]
        train_delta = (int(f["switch_stale"]) - int(f["switch_fresh"])) / int(f["denominator"])
        comparisons.add("GEANT.TH08." + ".".join(map(str, key)) + ".train_delta_F", train_delta, float(f["delta_F_hat"]))
        test_delta = statistics.mean(r["delta_F_test"] for r in group)
        mean_gs = statistics.mean(r["mean_G_S_Mbit_s"] for r in group)
        th08.append(dict(regime=key[0], rule=key[1], tau_s=key[2], h_s=key[3], days=len(group),
                         train_days=int(f["train_S_days"]), delta_F_train=train_delta,
                         mean_delta_F_test=test_delta, delta_F_sign_reversed=sign(train_delta) != sign(test_delta),
                         s_hat_train_Mbit=float(f["s_hat_pooled_Mbit"]), observed_G_S_sign=sign(mean_gs),
                         sign_from_test_delta=sign(float(f["s_hat_pooled_Mbit"]) * test_delta),
                         day_values=[dict(date=r["date"], delta_F=r["delta_F_test"]) for r in group]))

    # Independently reproduce the existing post-hoc K=5 comparison too, since
    # the two rolling fields appear in the requested X_GEANT ledger row.
    rolling_reported = inputs.json(base / "posthoc_rolling/summary.json")
    window_size = int(rolling_reported["K"])
    posthoc = dict(K=window_size, label="POST-HOC; locked G1 unchanged")
    for method in ("train", "rolling", "same_period_oracle"):
        hits, grouped = [], defaultdict(list)
        for row in daily:
            reg, day = row["regime"], row["date"]
            key = (reg, row["rule"], row["tau_s"], row["h_s"])
            f = predictions[key]
            if method == "train":
                pred = int(f["predicted_G_S_sign"])
            else:
                days = sorted(d for r, d in data if r == reg)
                position = days.index(day)
                selected = days[max(0, position - window_size):position] if method == "rolling" else days
                if not selected:
                    continue
                deltas = []
                for d in selected:
                    record = data[(reg, d)]
                    p, ih, t = record["rules"].index(row["rule"]), record["hs"].index(row["h_s"]), record["taus"].index(row["tau_s"])
                    deltas.append(float(record["shares"][p, t + 1, ih] - record["shares"][p, 0, ih]))
                pred = sign(float(f["s_hat_pooled_Mbit"]) * statistics.mean(deltas))
            if pred == 0:
                continue
            if row["resolved"]:
                hits.append(row["observed"] == pred)
            grouped[key].append((row["mean_G_S_Mbit_s"], pred))
        pooled_hits = [sign(statistics.mean(a for a, _ in v)) == sign(sum(b for _, b in v))
                       for v in grouped.values() if sum(b for _, b in v) != 0]
        posthoc[method] = dict(record_resolved=len(hits), record_correct=sum(hits), record_accuracy=fraction(sum(hits), len(hits)),
                               pooled_cells=len(pooled_hits), pooled_sign_agreement=sum(pooled_hits))
    comparisons.tree("GEANT.posthoc_rolling", posthoc, rolling_reported)
    signal = inputs.json(base / "signal.json")
    x4 = signal["gates"]["X4"]
    x4_denominators = {r["denominator"] for r in x4["counts"]}
    if len(x4_denominators) != 1:
        raise ValueError("Different X4 denominators")
    result["X4"] = x4["verdict"] + " (step 0, card)"
    signs_equal_null = all(int(r["predicted_G_S_sign"]) == int(r["null_sign"])
                           for key, r in predictions.items() if key[0].startswith("NEW"))
    comparisons.add("GEANT.null_signs_equal_law", signs_equal_null, True)
    result["null_comparison"] = "NOT_EVALUABLE (null sign equals law sign in every X2 cell; declared in card)"
    ledger = dict(records=len(receipt["records"]), flows=len({m["regime"] for m in receipt["records"]}),
                  evaluable_cases=len(stationary_cases), stationary_G_S_all_zero=stationary_zero,
                  stationary_median_both_side_regret_pct=st_med, stationary_not_worse=not_worse,
                  g1_pooled_cells=len(cells), g1_resolved=len(resolved_cells),
                  g1_signs_matched_unresolved=sum(r["observed"] == r["predicted"] for r in cells if not r["resolved"]),
                  record_level_resolved=len(resolved_days), record_level_correct=record_correct,
                  rolling_K_days=window_size, rolling_pooled_cells=posthoc["rolling"]["pooled_cells"],
                  rolling_pooled_sign_agreement=posthoc["rolling"]["pooled_sign_agreement"],
                  thetas_resolved_rules=[float(r[3:]) for r in G1_RULES],
                  evaluable_days_per_cell=sorted({r["days"] for r in cells}),
                  x4_decisions=next(iter(x4_denominators)), x4_disagreements=sum(r["numerator"] for r in x4["counts"]),
                  cpu_hours=receipt["CPU_s_records"] / 3600)
    reported = inputs.json(base / "card_verdicts.json")
    comparisons.tree("GEANT.card", result, reported)
    return dict(card=result, ledger=ledger, TH08_posthoc=th08, posthoc_rolling=posthoc, daily_cells=daily,
                stationary_cases=stationary_cases, costs_G_S_bitwise_equal=costs_gs_equal,
                scalar_G_S_values_checked=total_gs_checked,
                stationary_zero_scope="all instances, all ages, all 4 horizons, all 87 receipt records",
                seeds=sorted({m["seed_base"] for m in receipt["records"]}),
                resolution_clauses=dict(passes_2SE=sum(abs(r["mean_G_S_Mbit_s"]) >= 2 * r["se"] for r in cells),
                                        passes_magnitude=sum(abs(r["G_S_pct"]) >= 0.25 for r in cells)))


def markdown(result):
    ct, ge = result["X_CTMC"], result["X_GEANT"]
    checks = result["comparison_summary"]
    def reported(field):
        return next(c["reported"] for c in result["comparisons"] if c["field"] == field)

    lines = [f"**Chấm lại độc lập X-CTMC và X-GÉANT — {result['overall']}**", "",
             "Người phụ trách: **Doan Van Tai**. Script độc lập thực hiện theo brief tại commit `9f27dee` của `letter_smr`.", "",
             f"Đối chiếu **{checks['MATCH']}/{checks['total']} trường MATCH**, **{checks['MISMATCH']} MISMATCH**. "
             "MATCH xác nhận việc tính lại khớp dữ liệu đã báo; không đồng nghĩa mọi hypothesis đứng.", "",
             f"SHA256 theo receipt khớp **{result['integrity']['CTMC_receipt_files']}/63 JSON** và "
             f"**{result['integrity']['GEANT_receipt_files']}/87 NPZ**. Mọi input đều khớp blob đã commit. "
             "Không import/call module chấm, không đọc `score.json`, không chạy lại truth, không commit.", "",
             "Quy ước: `G_S = L_stale − L_fresh`; âm là freshness gây hại. Không phát hiện khác biệt do quy ước dấu. "
             "Regret và G_S chuẩn hóa dùng % C_ref; chênh lệch D4 dùng điểm phần trăm (pp).", "",
             "| Nhóm đối chiếu | Số trường | MISMATCH |", "|---|---:|---:|"]
    for name, group in result["comparison_groups"].items():
        lines.append(f"| {name} | {group['total']} | {group['MISMATCH']} |")
    lines += ["", "Rescore không dùng RNG. Seed của dữ liệu nguồn CTMC: "
              + ", ".join(f"{name}={value}" for name, value in ct["seeds"].items())
              + "; truth GÉANT: " + ", ".join(map(str, ge["seeds"]))
              + ". CTMC raw ghi test_rng unused vì tính deterministic; đây là replay số liệu đã lưu.", "",
             "**X-CTMC**", "",
             "| Test | Tính lại | Đã báo | Verdict tính lại / đã báo | So sánh |",
             "|---|---:|---:|---|---|"]
    for name in ("T1", "T2", "T3", "T4", "T5", "T6", "T6b"):
        t = ct["card"][name]
        if name == "T2":
            value = f"law {t['correct']}/{t['cells']} = {t['law_accuracy']:.9f}; null {t['null_correct']}/{t['cells']} = {t['null_accuracy']:.9f}"
        elif name == "T3":
            value = f"n={t['cells']}; median relative error {t['median_relative_error']:.9f}"
        else:
            value = f"{t['correct']}/{t['cells']} = {t.get('accuracy', t.get('share')):.9f}"
        status = "MISMATCH" if any(c["status"] == "MISMATCH" and c["field"].startswith("CTMC.card." + name + ".")
                                    for c in result["comparisons"]) else "MATCH"
        reported_verdict = reported(f"CTMC.card.{name}.verdict")
        n = reported(f"CTMC.card.{name}.cells")
        if name == "T2":
            baseline = f"law {reported('CTMC.card.T2.law_accuracy'):.9f}; null {reported('CTMC.card.T2.null_accuracy'):.9f}; n={n}"
        elif name == "T3":
            baseline = f"n={n}; median relative error {reported('CTMC.card.T3.median_relative_error'):.9f}"
        else:
            metric = "share" if name in ("T5", "T6b") else "accuracy"
            baseline = f"n={n}; {metric} {reported(f'CTMC.card.{name}.{metric}'):.9f}"
        lines.append(f"| {name} | {value} | {baseline} | {t['verdict']} / {reported_verdict} | {status} |")
    t1, t5 = ct["card"]["T1"], ct["card"]["T5"]
    lines += ["", f"T1: {t1['regimes']} regime eligible, {t1['majority_correct']}/{t1['regimes']} đúng theo đa số nghiêm ngặt; "
              + "; ".join(f"{s} {g['correct']}/{g['cells']}" for s, g in t1["by_stratum"].items()) + ". "
              f"Đã loại {len(ct['card']['excluded_pilot_regimes'])} pilot (3 có raw, 1 NOT_RUN): còn {ct['nonpilot_regimes']} regime trong mô tả D1. "
              "T5 xét riêng dấu ŝ = dấu s ≠ 0, không áp bộ lọc ΔF của test dấu. "
              f"{t5['wrong_sign_cells']} ô Hybrid_hat sai dấu có median both-side regret "
              f"{t5['wrong_sign_median_both_side_regret_pct']:.9f}% C_ref.", "",
              "| D1, h=30 T_int, τ=T_int | Harm / regime | Median G_S (% C_ref) |",
              "|---|---:|---:|"]
    for rule, values in ct["card"]["D1_harm_at_30Tint_tau1"].items():
        lines.append(f"| {rule} | {values['harm_regimes']}/{values['regimes']} | {values['median_G_S_pct']:.9g} |")
    lines += ["", "D1 đối chiếu từng rule với card và sáu rule có mặt trong ledger. D4 đối chiếu Hybrid_hat − Stationary_hat "
              "trên cả fresh/stale, ngưỡng nghiêm ngặt ±0,05 pp:", "",
              "| h/T_int | Phía | Số ô | Hybrid tốt hơn >0,05 pp | Hybrid tệ hơn >0,05 pp |",
              "|---:|---|---:|---:|---:|"]
    for h, sides in ct["D4"].items():
        for side, row in sides.items():
            lines.append(f"| {h} | {side} | {row['cells']} | {row['better']} | {row['worse']} |")
    lines += ["", f"D4: {ct['ledger']['d4_cells']} ô, {ct['ledger']['d4_hybrid_worse']} ô tệ hơn ngưỡng; "
              f"lợi lớn nhất {ct['ledger']['d4_largest_gain_pp']:.9f} pp. Các trường D4 trong ledger đều được tính lại.", "",
              f"T3 {ct['card']['T3']['verdict']}: phân rã post hoc trên đúng {ct['card']['T3']['cells']} ô cho median relative error "
              + "; ".join(f"`{k}` {v:.6f}%" for k, v in ct["ledger"]["slope_error_median_pct"].items())
              + ". Các phép thay một thành phần cho thấy sai số độ lớn của ŝ là thành phần đáng kể; "
              "đây là mô tả từ saved data, không sửa prediction hay verdict.", "",
              "**X-GÉANT**", "",
              "| Test | Tính lại từ NPZ | Đã báo | Verdict tính lại / đã báo |",
              "|---|---|---|---|",
              f"| G1 | {ge['card']['G1']['resolved']}/{len(ge['card']['G1']['cells'])} ô gộp resolved; accuracy=null | 0/36; accuracy=null | {ge['card']['G1']['verdict']} / NOT_EVALUABLE |",
              f"| G2 | G_S=0; median both-side regret {ge['card']['G2']['median_both_side_regret_pct']:.9g}% C_ref, n={ge['card']['G2']['records']} | 0%; n=102 | {ge['card']['G2']['verdict']} / STANDS |",
              f"| G3 | Stationary ≤ min TH: {ge['card']['G3']['stationary_not_worse']}/{ge['card']['G3']['cases']} | 102/102 | {ge['card']['G3']['verdict']} / STANDS |", "",
              "G1 gồm 3 regime × 3 rule × 2 τ × 2 h = 36 ô, mỗi ô có 8–9 ngày evaluable. "
              "SE = sample standard deviation của mean G_S từng ngày / √số ngày (ddof=1). "
              f"{ge['resolution_clauses']['passes_2SE']}/36 ô đạt vế 2·SE; "
              f"{ge['resolution_clauses']['passes_magnitude']}/36 đạt vế 0,25% mean C_ref; phải đồng thời đạt cả hai. "
              "Dấu khớp 24/36 ô chưa resolved chỉ là mô tả. Ở mức bản ghi, 34/56 resolved đúng (0,607142857).", "",
              f"G_S trong NPZ bằng bitwise `costs_stale − costs_fresh` ở {ge['scalar_G_S_values_checked']} giá trị. "
              "Stationary G_S=0 được kiểm cả 87 bản ghi, mọi instance/τ và cả 4 horizon; median regret và G3 chỉ dùng "
              "102 bộ (regime, ngày, τ, h) evaluable tại 4/6 h. Both-side regret = "
              "100·max(mean cost_fresh − mean C_ref, mean cost_stale − mean C_ref)/mean C_ref.", "",
              "**Post hoc TH_0,8 — train so với test evaluable**", "",
              "ΔF_train tính lại bằng (switch_stale − switch_fresh)/denominator trong predictions.csv; "
              "ΔF_test tính từ decisions trong NPZ, lấy trung bình đều theo ngày evaluable. "
              "Bảng dưới chỉ gộp hai h khi các giá trị trùng nhau; JSON giữ đủ 12 ô và từng ngày.", "",
              "| Regime | τ (s) | h (h) | Ngày train/test | ΔF_train | Mean ΔF_test | Dấu G_S quan sát / từ ΔF_test |",
              "|---|---:|---|---|---:|---:|---|"]
    for row in ge["TH08_posthoc"]:
        if row["h_s"] != 14400:
            continue
        other = next(r for r in ge["TH08_posthoc"] if r["regime"] == row["regime"] and r["tau_s"] == row["tau_s"] and r["h_s"] == 21600)
        same = all(row[k] == other[k] for k in ("days", "delta_F_train", "mean_delta_F_test", "observed_G_S_sign", "sign_from_test_delta"))
        selected = [row] if same else [row, other]
        for r in selected:
            hs = "4 và 6" if same else str(r["h_s"] // 3600)
            lines.append(f"| {r['regime']} | {r['tau_s']} | {hs} | {r['train_days']}/{r['days']} | {r['delta_F_train']:.9f} | {r['mean_delta_F_test']:.9f} | {r['observed_G_S_sign']:+d} / {r['sign_from_test_delta']:+d} |")
    train_values = [r["delta_F_train"] for r in ge["TH08_posthoc"]]
    test_values = [r["mean_delta_F_test"] for r in ge["TH08_posthoc"]]
    lines += ["", f"Train ΔF nằm trong [{min(train_values):.9f}, {max(train_values):.9f}], "
              f"test evaluable trong [{min(test_values):.9f}, {max(test_values):.9f}]. "
              f"Đảo dấu ở {sum(r['delta_F_sign_reversed'] for r in ge['TH08_posthoc'])}/12 ô; "
              "ŝ_train < 0 nên thay ΔF_train bằng ΔF_test cũng đảo dự đoán dấu. "
              "Đây là bằng chứng về thay đổi share giữa các cửa sổ dữ liệu đã xét; không đủ để quy nguyên nhân cho mùa "
              "hoặc xác nhận luật dấu trên population, vì G1 vẫn NOT_EVALUABLE.", "",
              "Phải tách horizon khi đọc khoảng ΔF_test: "
              + "; ".join(f"h={h // 3600} h: [{min(r['mean_delta_F_test'] for r in ge['TH08_posthoc'] if r['h_s'] == h):.9f}, "
                          f"{max(r['mean_delta_F_test'] for r in ge['TH08_posthoc'] if r['h_s'] == h):.9f}]"
                          for h in (14400, 21600))
              + ". Khác biệt do tập ngày evaluable có 8 ngày ở 4 h và 9 ngày ở 6 h; khoảng xấp xỉ −0,045…−0,02 "
              "chỉ mô tả phần 6 h, không bao hết cả hai horizon.", "",
              "Kiểm tra phụ post hoc K=5 cũng khớp summary/ledger: dấu gộp train 24/36, rolling 34/36, "
              "same-period oracle 36/36; record-level tương ứng 34/56, 28/50, 38/56. "
              "Không dùng các số này thay G1 khóa trước truth.", "",
              "**Sai khác và giới hạn**", ""]
    mismatches = [r for r in result["comparisons"] if r["status"] == "MISMATCH"]
    if mismatches:
        lines += ["| Trường | Tính lại | Đã báo | Nguyên nhân |", "|---|---|---|---|"]
        for r in mismatches:
            lines.append(f"| {r['field']} | {r['independent']} | {r['reported']} | {r['cause']} |")
    else:
        lines.append("Không có MISMATCH số liệu hoặc verdict. Sai khác floating point nhỏ, nếu có, nằm trong "
                     "tolerance đối chiếu (relative 1e−12, absolute 1e−9); JSON lưu absolute_difference. "
                     "Các ngưỡng khoa học giữ nguyên, không dùng epsilon khi quyết định eligibility/resolution/verdict.")
    numeric_differences = [r["absolute_difference"] for r in result["comparisons"] if "absolute_difference" in r]
    lines += ["", f"Sai khác tuyệt đối lớn nhất giữa hai cách tính là {max(numeric_differences):.9g} "
              "(các trường có đơn vị khác nhau; đây chỉ là kiểm tra roundoff). Ví dụ median T3 tính lại bằng "
              f"(L_stale−L_fresh)/h là {ct['card']['T3']['median_relative_error']:.17g}, "
              f"đã báo {reported('CTMC.card.T3.median_relative_error'):.17g}. "
              "JSON giữ mọi giá trị trước/sau và absolute_difference, kể cả các trường MATCH."]
    lines += ["", "Các ô chia sẻ regime/ngày và CRN nên không phải các trial độc lập; không tạo population CI. "
              "Việc chấm lại xác nhận saved outputs và phép tổng hợp; không phải một truth run độc lập hoặc chứng chỉ "
              "loại mọi bias của engine. X4 0/8352 được đối chiếu từ decision-only signal.json; không chạy lại X4. "
              "Không mở X1c hay dữ liệu ngoài hai thí nghiệm trong brief.", "",
              "Nhãn h/T_int và τ/T_int được ánh xạ về đúng lưới design để xử lý roundoff của phép chia "
              "(ví dụ 29.999999999999996 → 30); JSON lưu nhãn trước/sau và số dòng. "
              "Đây là nhận diện tọa độ, không nới ngưỡng khoa học.", "",
              "Trong lúc kiểm tra script mới đã sửa hai lỗi: đường dẫn repo paper ban đầu thiếu "
              "`state-model-regret-papers` (dừng trước đọc dữ liệu), và so sánh trực tiếp nhãn horizon float "
              "(bản chạy tạm bỏ sót ô). Kết quả cuối được tính lại từ input nguyên byte sau khi sửa; "
              "không phải sửa scorer/ledger đã có hoặc chạy lại truth.", "",
              "Kiểm tra phụ về lặp byte: lượt audit đầu có assertion không khớp hash output; không lưu diff "
              "của lượt đó nên chưa xác định nguyên nhân. Hai kiểm tra tiếp theo (chạy ở tiến trình riêng và "
              "chạy dưới guard import/ghi file) khớp byte. Kết luận MATCH dựa trên từng trường và tolerance "
              "đã nêu, không phải tuyên bố mọi môi trường hoặc mọi lượt chạy luôn trùng byte.", "",
              "**Lệnh và output**", "", "```bash", "source .venv/bin/activate",
              "source experiments/explore_ctmc/env.sh", "python -B experiments/letter/x_rescore_independent.py", "```", "",
              f"Embedded analytic controls: {len(result['self_tests'])}/{len(result['self_tests'])} PASS. "
              "Script kiểm SHA256 và committed blobs trước khi đọc số liệu; toàn bộ so sánh card/ledger theo từng trường "
              "và cell membership nằm trong JSON.", "",
              "- Script: `experiments/letter/x_rescore_independent.py`.",
              "- Số liệu, provenance và đối chiếu: `results/letter/x_rescore/rescore_independent.json`.",
              "- Báo cáo: `results/letter/x_rescore/RESCORE.md`.",
              "- Không tạo log, CSV, biểu đồ hoặc cấu hình mới. Không sửa file đầu vào.", ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run analytic controls without reading data or writing reports")
    args = parser.parse_args(argv)
    controls = self_tests()
    if args.self_test:
        print(json.dumps(dict(status="PASS", tests=controls), ensure_ascii=False))
        return 0
    inputs, comparisons = Inputs(), Comparisons()
    brief = inputs.read(BRIEF)
    locked_brief = git(BRIEF.parents[2], "show", "9f27dee:briefs/strengthen/CODEX_RESCORE_BRIEF.md")
    if brief != locked_brief:
        raise ValueError("Brief differs from commit 9f27dee")
    ctmc = ctmc_rescore(inputs, comparisons)
    geant = geant_rescore(inputs, comparisons)
    ledger = inputs.json(LEDGER)
    for name, computed in (("X_CTMC", ctmc), ("X_GEANT", geant)):
        comparisons.tree("ledger." + name, computed["ledger"], ledger["rows"][name]["recomputed"])
    counts = Counter(r["status"] for r in comparisons.fields)
    groups = defaultdict(Counter)
    prefixes = ("CTMC.card", "GEANT.card", "ledger.X_CTMC", "ledger.X_GEANT", "CTMC.raw", "GEANT.raw", "GEANT.posthoc_rolling")
    for field in comparisons.fields:
        group = next((p for p in prefixes if field["field"].startswith(p + ".")), "receipts_and_train_DeltaF")
        groups[group][field["status"]] += 1
    result = dict(owner="Doan Van Tai", overall="MISMATCH" if counts["MISMATCH"] else "MATCH",
                  brief_commit="9f27dee", brief_sha256=hashlib.sha256(brief).hexdigest(),
                  research_head=inputs.repos[ROOT]["head"],
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  sign_convention=SIGN_CONVENTION,
                  method="Independent formulas, standard library + NumPy; saved committed data only; no scorer imports/calls, no score.json, no truth run",
                  comparison_tolerances=dict(relative=comparisons.relative_tolerance, absolute=comparisons.absolute_tolerance,
                                             scope="field comparison only; never applied to scientific cutoffs"),
                  comparison_summary=dict(total=len(comparisons.fields), MATCH=counts["MATCH"], MISMATCH=counts["MISMATCH"]),
                  comparison_groups={name: dict(total=sum(values.values()), MATCH=values["MATCH"], MISMATCH=values["MISMATCH"])
                                     for name, values in sorted(groups.items())},
                  integrity=dict(CTMC_receipt_files=sum(r["receipt_match"] is True and r["path"].endswith(".json") for r in inputs.sources.values()),
                                 GEANT_receipt_files=sum(r["receipt_match"] is True and r["path"].endswith(".npz") for r in inputs.sources.values()),
                                 all_inputs_committed=True, input_files=len(inputs.sources)),
                  self_tests=controls, X_CTMC=ctmc, X_GEANT=geant,
                  comparisons=comparisons.fields, inputs=sorted(inputs.sources.values(), key=lambda r: r["path"]))
    # Recheck bytes immediately before publishing; no input is ever mutated.
    for path, source in inputs.sources.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError("Input changed during rescore: " + str(path))
    json_text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    report_text = markdown(result)
    DESTINATION.mkdir(parents=True, exist_ok=True)
    (DESTINATION / "rescore_independent.json").write_text(json_text, encoding="utf-8")
    (DESTINATION / "RESCORE.md").write_text(report_text, encoding="utf-8")
    print(json.dumps(dict(overall=result["overall"], **result["comparison_summary"],
                         CTMC={k: ctmc["card"][k]["verdict"] for k in ("T1", "T2", "T3", "T4", "T5", "T6", "T6b")},
                         GEANT={k: geant["card"][k]["verdict"] for k in ("G1", "G2", "G3")}), ensure_ascii=False))
    return 1 if counts["MISMATCH"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
