"""Independent E4 rescore from saved decisions and costs; no simulator imports.

Doan Van Tai. AI-assisted implementation of LETTER_E4_rescore_brief.md.
Only numpy and the standard library are used. Existing files are read-only.
"""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import unittest

import numpy as np


RTOL, ATOL = 1e-12, 1e-9
BRIEF = "notes/ops/codex/LETTER_E4_rescore_brief.md"
BRIEF_COMMIT = "4b6ad702"
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "results/letter/e4"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def mean(values):
    return math.fsum(float(x) for x in values) / len(values)


def stderr(values):
    return float(np.std(values, ddof=1) / math.sqrt(len(values)))


def close(a, b):
    return math.isfinite(a) and math.isfinite(b) and math.isclose(
        a, b, rel_tol=RTOL, abs_tol=ATOL
    )


def summarize(reference, stay, costs, ties):
    """Use paired instance differences for G_S and regret standard errors."""
    cref = mean(reference)
    if not math.isfinite(cref) or cref <= 0:
        raise ValueError("C_ref must be finite and positive for this E4 card")
    row = {"C_ref": cref, "E_stay": mean(stay)}
    for side in ("fresh", "stale"):
        values = costs.get(side)
        for field in (f"L_{side}", f"L_{side}_se", f"regret_{side}_pct",
                      f"regret_{side}_se_pct", f"tie_{side}"):
            row[field] = None
        if values is not None:
            row[f"L_{side}"] = mean(values)
            row[f"L_{side}_se"] = stderr(values)
            row[f"regret_{side}_pct"] = 100 * mean(values - reference) / cref
            row[f"regret_{side}_se_pct"] = 100 * stderr(values - reference) / cref
            row[f"tie_{side}"] = mean(ties[side])
    for field in ("G_S", "G_S_se", "G_S_pct", "G_S_se_pct"):
        row[field] = None
    if all(side in costs for side in ("fresh", "stale")):
        delta = costs["stale"] - costs["fresh"]
        row.update(G_S=mean(delta), G_S_se=stderr(delta),
                   G_S_pct=100 * mean(delta) / cref,
                   G_S_se_pct=100 * stderr(delta) / cref)
    return row


class Checks:
    def __init__(self):
        self.count = 0
        self.failures = []

    def check(self, condition, context, **detail):
        self.count += 1
        if not condition:
            self.failures.append({"context": context, **detail})


def read_manifest(path):
    entries = {}
    for line in path.read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        name = name.lstrip("*")
        if len(digest) != 64 or name in entries or Path(name).is_absolute() or ".." in Path(name).parts:
            raise ValueError(f"Invalid/duplicate checksum entry: {line}")
        int(digest, 16)
        entries[name] = digest
    return entries


def compare_tables(name, expected, locked, keys):
    """Compare every field, including missing values and nonnumeric fields."""
    if isinstance(locked, Path):
        with locked.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            fields = list(reader.fieldnames or [])
            actual = list(reader)
    else:
        actual = locked
        fields = list(actual[0]) if actual else []
    result = {"name": name, "recomputed_rows": len(expected), "locked_rows": len(actual),
              "rows_compared": 0, "fields_compared": 0, "fields": {}, "mismatches": []}

    def index(rows, source):
        indexed = {}
        for row in rows:
            key = tuple(str(row.get(k, "")) for k in keys)
            # 1 versus 1.0 is the same multiplier in CSV/JSON.
            key = tuple(float(x) if k in ("tau_mult", "h_mult") else x for k, x in zip(keys, key))
            if key in indexed:
                result["mismatches"].append({"cause": "duplicate key", "source": source, "key": key})
            indexed[key] = row
        return indexed

    eindex, aindex = index(expected, "independent"), index(actual, "locked")
    if expected and set(fields) != set(expected[0]):
        result["mismatches"].append({"cause": "field set", "independent": sorted(expected[0]), "locked": fields})
    for key in sorted(set(eindex) | set(aindex), key=str):
        if key not in eindex or key not in aindex:
            result["mismatches"].append({"cause": "missing row", "key": key, "missing_from": "independent" if key not in eindex else "locked"})
            continue
        result["rows_compared"] += 1
        erow, arow = eindex[key], aindex[key]
        for field in sorted(set(erow) | set(arow)):
            ev, av = erow.get(field), arow.get(field)
            stat = result["fields"].setdefault(field, {"compared": 0, "numeric": 0,
                    "missing_pairs": 0, "max_abs_diff": 0.0, "max_rel_diff": 0.0,
                    "mismatches": 0, "max_abs_at": None})
            stat["compared"] += 1
            result["fields_compared"] += 1
            if ev is None:
                matched = av is None or av == ""
                stat["missing_pairs"] += int(matched)
            elif isinstance(ev, bool):
                matched = (av == str(ev)) if isinstance(av, str) else type(av) is bool and av == ev
            elif isinstance(ev, (float, int)):
                try:
                    number = float(av)
                    matched = close(float(ev), number)
                    diff = abs(float(ev) - number)
                    if math.isfinite(diff):
                        stat["numeric"] += 1
                        if diff > stat["max_abs_diff"]:
                            stat["max_abs_diff"], stat["max_abs_at"] = diff, key
                        relative = diff / max(abs(float(ev)), abs(number)) if ev or number else 0.0
                        stat["max_rel_diff"] = max(stat["max_rel_diff"], relative)
                except (TypeError, ValueError):
                    matched = False
            else:
                matched = ev == av
            if not matched:
                stat["mismatches"] += 1
                result["mismatches"].append({"key": key, "field": field, "independent": ev, "locked": av,
                                             "cause": "field value"})
    result["status"] = "MATCH" if not result["mismatches"] else "MISMATCH"
    return result


def inspect_raw(data, card, training, checks, manifest_path):
    manifest = read_manifest(manifest_path)
    paths = sorted((data / "raw").glob("*.npz"))
    json_paths = sorted((data / "raw").glob("*.json"))
    actual_names = {str(p.relative_to(data)) for p in paths + json_paths}
    checks.check(set(manifest) == actual_names, "manifest covers exactly all raw JSON/NPZ",
                 missing=sorted(actual_names - set(manifest)), extra=sorted(set(manifest) - actual_names))
    hashes = {}
    matched_manifest = 0
    for name, digest in manifest.items():
        path = data / name
        hashes[str(path)] = sha256(path)
        matched_manifest += int(hashes[str(path)] == digest)
        checks.check(hashes[str(path)] == digest, "VM manifest SHA256", path=name)
    checks.check(len(paths) == 170 and len(json_paths) == 170, "170 NPZ + 170 JSON",
                 npz=len(paths), json=len(json_paths))
    groups = {}
    matched_json = 0
    for path in paths:
        meta = load_json(path.with_suffix(".json"))
        digest = sha256(path)
        matched_json += int(digest == meta["npz_sha256"])
        checks.check(digest == meta["npz_sha256"], "JSON npz_sha256", path=path.name)
        checks.check(meta["pilot"] is False, "pilot false", path=path.name)
        checks.check(meta["seed"] == 3000001, "truth seed", path=path.name)
        checks.check(meta["onset_theta"] == card["onset_theta"], "onset theta", path=path.name)
        checks.check(path.stem == f"{meta['regime']}_chunk{meta['chunk']:02d}", "filename metadata", path=path.name)
        checks.check(meta["N"] == 50 and meta["K"] == 128 and meta["R_eval"] == 256 and meta["R_dec"] == 128,
                     "chunk configuration", path=path.name)
        with np.load(path, allow_pickle=False) as archive:
            arrays = {k: archive[k] for k in archive.files}
        groups.setdefault(meta["regime"], []).append((meta, arrays))
    expected_regimes = {x["regime"] for x in training["regimes"]}
    checks.check(len(groups) == 17 and set(groups) == expected_regimes, "17 training/truth regimes")
    details = {"vm_manifest": str(manifest_path.relative_to(ROOT)), "npz_files": len(paths),
               "json_files": len(json_paths), "manifest_files_matched": matched_manifest,
               "manifest_files_total": len(manifest), "json_npz_hashes_matched": matched_json,
               "regimes": [], "seed": 3000001, "pilot": False, "onset_theta": card["onset_theta"]}
    return groups, hashes, details


def recompute(groups, checks, details):
    cells, regimes, tie_counts = [], [], {}
    for regime, chunks in sorted(groups.items()):
        chunks.sort(key=lambda item: item[0]["chunk"])
        meta0, base = chunks[0]
        checks.check([m["chunk"] for m, _ in chunks] == list(range(10)), "ten unique chunks", regime=regime)
        pipelines = base["pipelines"].tolist()
        sides = base["sides"].tolist()
        checks.check(len(pipelines) == 20 and len(set(pipelines)) == 20 and sides == ["fresh", "stale"],
                     "pipeline/side axes", regime=regime)
        checks.check(base["tau_mult"].tolist() == [0.3, 1.0, 3.0] and base["h_mult"].tolist() == [1, 2, 4, 7, 15, 30],
                     "age/horizon grid", regime=regime)
        for meta, arrays in chunks:
            for key in ("pipelines", "sides", "tau_mult", "h_mult", "tau", "h", "available"):
                checks.check(np.array_equal(arrays[key], base[key]), "consistent chunk axes", regime=regime, chunk=meta["chunk"], field=key)
            checks.check(meta["T_int"] == meta0["T_int"] and meta["dt"] == meta0["dt"], "consistent T_int/dt", regime=regime, chunk=meta["chunk"])
            checks.check(meta["pipelines"] == pipelines, "metadata pipeline axis", regime=regime, chunk=meta["chunk"])
            checks.check(arrays["V"].shape == (50, base["V"].shape[1], 6) and arrays["decisions"].shape == (50, 20, 2, 3, 6)
                         and arrays["tie_flags"].shape == arrays["decisions"].shape and arrays["available"].shape == (20, 2),
                         "array shapes", regime=regime, chunk=meta["chunk"])
            checks.check(bool(np.isfinite(arrays["V"]).all()) and bool((arrays["V"] >= 0).all()), "finite nonnegative costs", regime=regime, chunk=meta["chunk"])
            checks.check(arrays["decisions"].dtype.kind in "iu" and arrays["tie_flags"].dtype.kind == "b" and arrays["available"].dtype.kind == "b", "decision/tie dtypes", regime=regime, chunk=meta["chunk"])
        values, decisions, ties, ids = [np.concatenate([a[k] for _, a in chunks]) for k in ("V", "decisions", "tie_flags", "instance_id")]
        checks.check(len(ids) == 500 and len(np.unique(ids)) == 500 and set(ids.tolist()) == set(range(500)), "500 unique instance IDs", regime=regime)
        order = np.argsort(ids)
        values, decisions, ties = values[order], decisions[order], ties[order]
        available = base["available"]
        for p, pipeline in enumerate(pipelines):
            for s, side in enumerate(sides):
                selected = decisions[:, p, s]
                valid = bool(((selected >= 0) & (selected < values.shape[1])).all()) if available[p, s] else bool((selected == -1).all())
                checks.check(valid, "valid actions or unavailable sentinel", regime=regime, pipeline=pipeline, side=side)
                if available[p, s] and not valid:
                    raise ValueError(f"Invalid action index: {regime}/{pipeline}/{side}")
                tally = tie_counts.setdefault((pipeline, side), [0, 0])
                if available[p, s]:
                    tally[0] += int(ties[:, p, s].sum())
                    tally[1] += int(ties[:, p, s].size)
        refp, freshs = pipelines.index("M1_new"), sides.index("fresh")
        checks.check(bool(available[refp, freshs]) and not bool(available[refp, sides.index("stale")]), "M1_new fresh only", regime=regime)
        checks.check(bool((decisions[:, refp, freshs] == decisions[:, refp, freshs, :1, :]).all()), "C_ref decision independent of tau", regime=regime)
        for t, tau_mult in enumerate(base["tau_mult"]):
            for h, h_mult in enumerate(base["h_mult"]):
                reference = values[np.arange(len(ids)), decisions[:, refp, freshs, 0, h], h]
                for p, pipeline in enumerate(pipelines):
                    costs, cell_ties = {}, {}
                    for s, side in enumerate(sides):
                        if available[p, s]:
                            costs[side] = values[np.arange(len(ids)), decisions[:, p, s, t, h], h]
                            cell_ties[side] = ties[:, p, s, t, h]
                    cells.append({"regime": regime, "tau_mult": float(tau_mult), "h_mult": int(h_mult),
                                  "tau": float(base["tau"][t]), "h": float(base["h"][h]), "N": len(ids),
                                  "pipeline": pipeline, **summarize(reference, values[:, 0, h], costs, cell_ties)})
        regimes.append({"regime": regime, "chunks": len(chunks), "N": len(ids),
                        "complete": len(chunks) == 10 and len(ids) == 500,
                        "CPU": math.fsum(meta["CPU"] for meta, _ in chunks), "seed": meta0["seed"], "pilot": meta0["pilot"]})
        details["regimes"].append({"regime": regime, "chunks": len(chunks), "instances": len(ids),
                                   "unique_instance_ids": len(np.unique(ids)), "actions": values.shape[1], "T_int": meta0["T_int"]})
    return cells, regimes, tie_counts


def reductions(cells):
    indexed = {(r["regime"], r["tau_mult"], r["h_mult"], r["pipeline"]): r for r in cells}
    result = []
    for row in cells:
        if row["pipeline"] != "M0":
            continue
        key = (row["regime"], row["tau_mult"], row["h_mult"])
        for level in ("i", "ii"):
            hybrid, tie, reversed_row = [indexed[(*key, p)] for p in (f"Hybrid-{level}", f"M0-tie-{level}", "Hybrid-reversed")]
            for side in ("fresh", "stale"):
                field = f"L_{side}"
                gain, tie_gain = row[field] - hybrid[field], row[field] - tie[field]
                result.append({"regime": key[0], "tau_mult": key[1], "h_mult": key[2], "level": level,
                               "side": side, "M0_loss": row[field], "hybrid_loss": hybrid[field], "tie_loss": tie[field],
                               "hybrid_reduction": gain, "tie_reduction": tie_gain,
                               "reduction_fraction": tie_gain / gain if gain != 0 else None,
                               "reversed_minus_hybrid": reversed_row[field] - hybrid[field], "denominator_positive": gain > 0})
    return result


def training_checks(training, checks):
    rows = []
    checks.check(training["test_seed_used"] is False and training["seed"] == 1, "E4-3 training only")
    for item in training["regimes"]:
        ref, candidate = [int(np.argmin(np.asarray(item["rhat"][k], dtype=float))) for k in ("i", "ii")]
        agrees = ref == candidate
        checks.check(item["ii"]["reference_best"] == ref and item["ii"]["candidate_best"] == candidate
                     and item["ii"]["best_action_agrees"] == agrees, "training argmin vs saved flags", regime=item["regime"])
        rows.append({"regime": item["regime"], "reference_best": ref, "candidate_best": candidate, "agrees": agrees})
    passed = sum(r["agrees"] for r in rows)
    checks.check(passed == training["summary"]["ii"]["best_action_agrees"] and len(rows) == training["regime_count"] == 17,
                 "training summary recomputed", passed=passed, denominator=len(rows))
    return rows


def score(cells, regimes, card, train_rows, checks):
    result, diagnostics = {}, {}
    for test, pipeline, gs in (("E4-1", "Hybrid-i", True), ("E4-2", "Hybrid-i", False), ("E4-4", "Hybrid-ii", False)):
        rule = card["tests"][test]
        checks.check(rule["horizon_rule"] == "each", "card horizon rule", test=test)
        selected = [r for r in cells if r["pipeline"] == pipeline and r["h_mult"] in rule["h_multipliers"]]
        flags = [abs(r["G_S_pct"]) <= rule["abs_GS_pct_max"] if gs else
                 max(r["regret_fresh_pct"], r["regret_stale_pct"]) <= rule["regret_pct_max"] for r in selected]
        checks.check(len(selected) == 153, "153 test units", test=test, count=len(selected))
        passed = sum(flags)
        fraction = passed / len(selected)
        result[test] = {"complete": all(r["complete"] for r in regimes) and len(regimes) == 17,
                        "denominator": len(selected), "fraction": fraction, "normalization_defined": True,
                        "passed": passed, "threshold": rule["pass_fraction_min"], "units": "each",
                        "verdict": "PASS" if fraction >= rule["pass_fraction_min"] else "FAIL"}
        factors = {}
        for factor in ("h_mult", "tau_mult", "regime"):
            factors[factor] = []
            for value in sorted({r[factor] for r in selected}):
                chosen = [f for r, f in zip(selected, flags) if r[factor] == value]
                factors[factor].append({"value": value, "passed": sum(chosen), "denominator": len(chosen)})
        diagnostics[test] = {"by_factor": factors, "failed_units": [
            {k: r[k] for k in ("regime", "tau_mult", "h_mult", "G_S_pct", "regret_fresh_pct", "regret_stale_pct")}
            for r, flag in zip(selected, flags) if not flag]}
    passed = sum(r["agrees"] for r in train_rows)
    fraction = passed / len(train_rows)
    threshold = card["tests"]["E4-3"]["best_action_agreement_min"]
    result["E4-3"] = {"denominator": len(train_rows), "fraction": fraction, "passed": passed,
                      "threshold": threshold, "training_only": True, "verdict": "PASS" if fraction >= threshold else "FAIL"}
    for test in ("E4-5", "E4-6"):
        checks.check(card["tests"][test]["descriptive"] is True, "descriptive only", test=test)
        result[test] = {"tables": ["cells.csv", "reductions.csv"], "verdict": "DESCRIPTIVE"}
    return result, diagnostics


def compare_score(independent, locked, checks):
    comparisons = []
    for test, row in sorted(independent.items()):
        saved = locked["tests"][test]
        scalar = {k: v for k, v in row.items() if k != "tables"}
        target = {k: v for k, v in saved.items() if k != "tables"}
        comparisons.append(compare_tables(test, [{"test": test, **scalar}], [{"test": test, **target}], ("test",)))
        if "tables" in row:
            checks.check(row["tables"] == saved.get("tables"), "descriptive table paths", test=test)
    checks.check(set(independent) == set(locked["tests"]), "score test set")
    return comparisons


def baseline_summary(cells):
    result = []
    for pipeline in ("M0", "M0-tie-i", "Hybrid-i", "Hybrid-ii"):
        rows = [r for r in cells if r["pipeline"] == pipeline and r["h_mult"] in (7, 15, 30)]
        result.append({"pipeline": pipeline, "units": len(rows),
                       "median_abs_GS_pct": float(np.median([abs(r["G_S_pct"]) for r in rows])),
                       "median_regret_fresh_pct": float(np.median([r["regret_fresh_pct"] for r in rows])),
                       "median_regret_stale_pct": float(np.median([r["regret_stale_pct"] for r in rows])),
                       "GS_le_0_25_count": sum(abs(r["G_S_pct"]) <= 0.25 for r in rows),
                       "both_regrets_le_0_5_count": sum(max(r["regret_fresh_pct"], r["regret_stale_pct"]) <= 0.5 for r in rows)})
    return result


def audit():
    checks = Checks()
    card = load_json(DATA / "CARD_E4.json")
    training = load_json(DATA / "training_checks.json")
    locked = load_json(DATA / "score.json")
    lock = load_json(DATA / "lock.json")
    notes = []
    manifest_path = DATA / "e4_raw_sha256.txt"
    if not manifest_path.exists():
        manifest_path = DATA / "raw_sha256_vm.txt"
        notes.append("Tên manifest trong brief là e4_raw_sha256.txt; artifact VM đã commit thực tế là raw_sha256_vm.txt (340 mục).")
    paths = [ROOT / BRIEF, DATA / "CARD_E4.json", DATA / "training_checks.json", DATA / "score.json",
             DATA / "lock.json", DATA / "cells.csv", DATA / "reductions.csv", DATA / "regimes.csv", manifest_path]
    paths += [ROOT / p for p in lock["sha256"]]
    before = {str(p): sha256(p) for p in paths}
    committed_brief = subprocess.check_output(["git", "show", f"{BRIEF_COMMIT}:{BRIEF}"], cwd=ROOT)
    checks.check((ROOT / BRIEF).read_bytes() == committed_brief, "brief equals committed 4b6ad702")
    lock_matches = 0
    for name, digest in lock["sha256"].items():
        matched = before[str(ROOT / name)] == digest
        lock_matches += int(matched)
        checks.check(matched, "pre-truth lock SHA256", path=name)
    checks.check(sha256(DATA / "CARD_E4.json") == locked["card_sha256"], "score card SHA256")
    expected_rules = {"E4-1": {"abs_GS_pct_max": 0.25, "pass_fraction_min": 0.9, "h_multipliers": [7, 15, 30], "horizon_rule": "each", "pipeline": "hybrid level i"},
                      "E4-2": {"regret_pct_max": 0.5, "pass_fraction_min": 0.9, "h_multipliers": [7, 15, 30], "horizon_rule": "each", "pipeline": "hybrid level i, both sides"},
                      "E4-3": {"best_action_agreement_min": 0.9},
                      "E4-4": {"regret_pct_max": 0.5, "pass_fraction_min": 0.8, "h_multipliers": [7, 15, 30], "horizon_rule": "each", "pipeline": "hybrid level ii, both sides"}}
    rule_differences = [{"test": test, "field": field, "brief": value, "card": card["tests"][test].get(field)}
                        for test, rule in expected_rules.items() for field, value in rule.items() if card["tests"][test].get(field) != value]
    checks.check(not rule_differences, "card versus brief thresholds", differences=rule_differences)
    groups, hashes, raw = inspect_raw(DATA, card, training, checks, manifest_path)
    before.update(hashes)
    cells, regimes, raw_ties = recompute(groups, checks, raw)
    reduction_rows = reductions(cells)
    tables = {"cells.csv": compare_tables("cells.csv", cells, DATA / "cells.csv", ("regime", "pipeline", "tau_mult", "h_mult")),
              "reductions.csv": compare_tables("reductions.csv", reduction_rows, DATA / "reductions.csv", ("regime", "tau_mult", "h_mult", "level", "side")),
              "regimes.csv": compare_tables("regimes.csv", regimes, DATA / "regimes.csv", ("regime",))}
    train_rows = training_checks(training, checks)
    independent, diagnostics = score(cells, regimes, card, train_rows, checks)
    score_comparisons = compare_score(independent, locked, checks)
    checks.check(locked["complete_regimes"] == len(regimes) and locked["descriptive_only"] is False, "score top-level metadata")
    with (DATA / "cells.csv").open(newline="") as handle:
        saved_cells = list(csv.DictReader(handle))
    tie_rows = []
    for (pipeline, side), (count, total) in sorted(raw_ties.items()):
        rows = [r for r in saved_cells if r["pipeline"] == pipeline and r[f"tie_{side}"] != ""]
        denominator = sum(int(r["N"]) for r in rows)
        saved_share = math.fsum(float(r[f"tie_{side}"]) * int(r["N"]) for r in rows) / denominator if denominator else None
        raw_share = count / total if total else None
        matched = denominator == total and (raw_share is None and saved_share is None or raw_share is not None and saved_share is not None and close(raw_share, saved_share))
        checks.check(matched, "pooled tie share from raw vs cells.csv", pipeline=pipeline, side=side)
        tie_rows.append({"pipeline": pipeline, "side": side, "ties": count, "denominator": total,
                         "share": raw_share, "locked_share": saved_share,
                         "abs_diff": abs(raw_share - saved_share) if total and denominator else None,
                         "status": "MATCH" if matched else "MISMATCH"})
    negative = [{"regime": r["regime"], "pipeline": r["pipeline"], "tau_mult": r["tau_mult"],
                 "h_mult": r["h_mult"], "side": side, "regret_pct": r[f"regret_{side}_pct"]}
                for r in cells for side in ("fresh", "stale") if r[f"regret_{side}_pct"] is not None and r[f"regret_{side}_pct"] < 0]
    notes += ["G_S = mean(V_stale - V_fresh): âm nghĩa là telemetry fresh gây hại; quy ước khớp cells.csv, không đảo dấu.",
              f"reduction_fraction = tie_reduction/hybrid_reduction khi mẫu số khác 0, kể cả âm; denominator_positive là cờ riêng. Có {sum(r['hybrid_reduction'] < 0 for r in reduction_rows)} dòng mẫu số âm, {sum(r['hybrid_reduction'] == 0 for r in reduction_rows)} dòng mẫu số 0. Tỷ số với mẫu số âm không diễn giải là phần lợi ích thu được. Bản check-only đầu của rescore bỏ trống 264 tỷ số mẫu số âm; đã sửa giả định này và thêm analytic test, không sửa locked CSV.",
              "SE dùng sample sd(ddof=1)/sqrt(500); SE của G_S và regret dùng chênh lệch ghép cặp trên cùng instance/CRN, không cộng SE hai phía.",
              "Giữ nguyên regret âm do M1_new dùng rollout quyết định độc lập; không clip về 0. M1_new không có stale: các ô trống được giữ là null.",
              "Dùng tau/h thực trong NPZ (đã làm tròn theo dt), và h_mult cho eligibility của card.",
              "onset_theta=0.5 chỉ descriptive theo addendum trước truth; không dùng các pipeline Onset trong E4-1..E4-4.",
              "153 units dùng chung instances giữa age/horizon: đây là tỷ lệ trong panel, không phải 153 independent trials hoặc population CI.",
              "E4-3 là training-only đã biết trước truth. Rescore kiểm arithmetic của saved costs/decisions; không xác nhận simulator hoặc rollout estimator là ground truth chính xác."]
    if "No card:" in locked.get("note", ""):
        notes.append("score.json có note chung 'No card: no E4 pass/fail verdicts.'; đây là mô tả trường hợp không có card, không phản ánh lượt này (card SHA hợp lệ, descriptive_only=false).")
    changed = [str(Path(p).relative_to(ROOT)) for p, digest in before.items() if sha256(Path(p)) != digest]
    checks.check(not changed, "all audited existing files unchanged during rescore", changed=changed)
    matches = not checks.failures and all(t["status"] == "MATCH" for t in tables.values()) and all(t["status"] == "MATCH" for t in score_comparisons)
    return {"schema": "letter-e4-independent-rescore-v1", "responsible": "Doan Van Tai",
            "implementation": "Independent AI-assisted implementation from the brief; no scorer/simulator module imported or copied.",
            "status": "MATCH" if matches else "MISMATCH", "brief_commit": BRIEF_COMMIT,
            "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "script_sha256": sha256(Path(__file__)), "numpy_version": np.__version__,
            "tolerance": {"relative": RTOL, "absolute": ATOL, "rule": "abs(a-b) <= max(atol, rtol*max(abs(a),abs(b)))"},
            "integrity": {"status": "PASS" if not checks.failures else "FAIL", "checks": checks.count,
                          "failures": checks.failures, "lock_files_matched": lock_matches, "lock_files_total": len(lock["sha256"]),
                          "audited_files_unchanged": len(before) - len(changed), "audited_files_total": len(before), "raw": raw},
            "card_brief_differences": rule_differences, "tables": tables, "independent_tests": independent,
            "locked_tests": locked["tests"], "score_comparisons": score_comparisons,
            "ties": tie_rows, "training_best_actions": train_rows, "diagnostics_saved_data_only": diagnostics,
            "baseline_comparison_descriptive": baseline_summary(cells),
            "negative_regret": {"cell_side_count": len(negative), "minimum_pct": min((r["regret_pct"] for r in negative), default=None), "rows": negative},
            "conventions_and_limitations": notes,
            "input_sha256": {str(Path(p).relative_to(ROOT)): digest for p, digest in sorted(before.items())}}


def markdown(report):
    integrity = report["integrity"]
    raw = integrity["raw"]
    lines = ["# E4 — rescore độc lập", "", "Người phụ trách: Doan Van Tai. Triển khai AI-assisted từ brief; không import scorer/simulator.",
             "", f"**Kết quả đối chiếu: {report['status']}**. Brief `{BRIEF_COMMIT}`, HEAD `{report['git_head']}`.",
             "", f"VM manifest: {raw['manifest_files_matched']}/{raw['manifest_files_total']} SHA256; JSON→NPZ: {raw['json_npz_hashes_matched']}/{raw['npz_files']}; lock: {integrity['lock_files_matched']}/{integrity['lock_files_total']}.",
             f"17 regimes × 10 chunks × 50 = 8.500 instances; mỗi regime 500 ID duy nhất. Seed 3000001, pilot=false, onset_theta={raw['onset_theta']}.",
             f"Kiểm integrity: {integrity['checks']} checks, {len(integrity['failures'])} lỗi; {integrity['audited_files_unchanged']}/{integrity['audited_files_total']} file input/source giữ nguyên SHA trong lượt rescore.",
             "", "| Test | Rescore độc lập | Locked | Ngưỡng share | Verdict độc lập / locked |", "|---|---:|---:|---:|---|"]
    for test in ("E4-1", "E4-2", "E4-3", "E4-4"):
        a, b = report["independent_tests"][test], report["locked_tests"][test]
        lines.append(f"| {test} | {a['passed']}/{a['denominator']} ({100*a['fraction']:.6f}%) | {b['passed']}/{b['denominator']} | {100*a['threshold']:.0f}% | {a['verdict']} / {b['verdict']} |")
    lines += ["", "E4-1: Hybrid-i |G_S|≤0,25%C_ref; E4-2: Hybrid-i regret≤0,5%C_ref ở cả hai phía; E4-4: Hybrid-ii cùng điều kiện regret. E4-3: agreement best action trên training.",
              "", "| Bảng | Số dòng đối chiếu | Số fields | Sai khác |", "|---|---:|---:|---|"]
    for name, table in report["tables"].items():
        lines.append(f"| {name} | {table['rows_compared']} | {table['fields_compared']} | {len(table['mismatches'])} ({table['status']}) |")
    lines += ["", "So sánh từng field: rtol=1e-12, atol=1e-9 (math.isclose; max hai tolerance). Ô trống và fields phân loại kiểm riêng.",
              "", "Cost/SE ở đơn vị Mb·time; fields pct ở %C_ref (sai khác là percentage points).", 
              "", "| Bảng | Field | Max abs difference | Max relative difference | Mismatch |", "|---|---|---:|---:|---:|"]
    for name, table in report["tables"].items():
        for field, stat in table["fields"].items():
            lines.append(f"| {name} | {field} | {stat['max_abs_diff']:.12g} | {stat['max_rel_diff']:.12g} | {stat['mismatches']} |")
    lines += ["", "Tie shares tính trực tiếp từ raw tie_flags, đối chiếu cả từng cell và pooled theo pipeline/side.",
              "", "| Pipeline | Side | Ties / denominator | Raw share | Locked share |", "|---|---|---:|---:|---:|"]
    for row in report["ties"]:
        fmt = lambda x: "N/A" if x is None else f"{100*x:.6f}%"
        lines.append(f"| {row['pipeline']} | {row['side']} | {row['ties']}/{row['denominator']} | {fmt(row['share'])} | {fmt(row['locked_share'])} |")
    lines += ["", "Phân tích mô tả trên saved data; không đổi threshold, không truth run mới.",
              "", "| Test | h/T_int=7 | h/T_int=15 | h/T_int=30 |", "|---|---:|---:|---:|"]
    for test, diag in report["diagnostics_saved_data_only"].items():
        counts = [f"{r['passed']}/{r['denominator']}" for r in diag["by_factor"]["h_mult"]]
        lines.append(f"| {test} | " + " | ".join(counts) + " |")
    lines += ["", "| Pipeline (153 units) | Median abs(G_S) %C_ref | Median regret fresh %C_ref | Median regret stale %C_ref | abs(G_S)≤0,25 | Both regrets≤0,5 |", "|---|---:|---:|---:|---:|---:|"]
    for row in report["baseline_comparison_descriptive"]:
        lines.append(f"| {row['pipeline']} | {row['median_abs_GS_pct']:.6f} | {row['median_regret_fresh_pct']:.6f} | {row['median_regret_stale_pct']:.6f} | {row['GS_le_0_25_count']}/153 | {row['both_regrets_le_0_5_count']}/153 |")
    disagree = [r["regime"] for r in report["training_best_actions"] if not r["agrees"]]
    lines += ["", "E4-3: best action (ii) khác (i) tại " + ", ".join(f"`{x}`" for x in disagree) + ".",
              f"Regret âm: {report['negative_regret']['cell_side_count']} cell-side values; nhỏ nhất {report['negative_regret']['minimum_pct']:.12g}%C_ref; giữ nguyên dấu.", ""]
    lines += [f"- {note}" for note in report["conventions_and_limitations"]]
    problems = integrity["failures"] + [m for table in report["tables"].values() for m in table["mismatches"]] + [m for table in report["score_comparisons"] for m in table["mismatches"]]
    if problems:
        lines += ["", "Chi tiết sai khác:", "", "```json", json.dumps(problems, ensure_ascii=False, indent=2), "```"]
    lines += ["", "Lệnh đã dùng:", "", "```bash", "source .venv/bin/activate && source experiments/explore_ctmc/env.sh",
              "PYTHONDONTWRITEBYTECODE=1 python experiments/letter/e4_rescore.py --self-test",
              "PYTHONDONTWRITEBYTECODE=1 python experiments/letter/e4_rescore.py", "```", "",
              "Source: `experiments/letter/e4_rescore.py`. Outputs: `results/letter/e4/rescore_independent.json` và `.md`.",
              "Không tạo CSV/log/biểu đồ/config mới; stdout hiển thị tóm tắt, JSON lưu số liệu, SHA và toàn bộ sai khác. Không commit, SSH hoặc sửa artifact cũ."]
    return "\n".join(lines) + "\n"


class SelfTests(unittest.TestCase):
    def test_paper_sign_and_paired_se(self):
        ref = np.array([2., 2., 2., 2.])
        fresh = np.array([1., 3., 5., 7.])
        stale = fresh - 1
        row = summarize(ref, ref, {"fresh": fresh, "stale": stale}, {"fresh": np.zeros(4), "stale": np.ones(4)})
        self.assertEqual(row["G_S"], -1)
        self.assertEqual(row["G_S_pct"], -50)
        self.assertEqual(row["G_S_se"], 0)
        self.assertAlmostEqual(row["L_fresh_se"], math.sqrt(5 / 3))
        self.assertEqual(row["tie_stale"], 1)

    def test_negative_regret_and_reference(self):
        ref = np.array([2., 4., 6., 8.])
        r = summarize(ref, ref, {"fresh": ref - 1}, {"fresh": np.zeros(4)})
        self.assertEqual(r["regret_fresh_pct"], -20)
        self.assertEqual(r["regret_fresh_se_pct"], 0)
        r = summarize(ref, ref, {"fresh": ref}, {"fresh": np.zeros(4)})
        self.assertEqual(r["regret_fresh_pct"], 0)
        self.assertEqual(r["regret_fresh_se_pct"], 0)
        self.assertIsNone(r["L_stale"])
        self.assertIsNone(r["G_S"])

    def test_pairing_matters(self):
        x = np.array([1., 2., 4., 8.])
        y = x[::-1]
        r = summarize(x, x, {"fresh": y}, {"fresh": np.zeros(4)})
        self.assertEqual(r["regret_fresh_pct"], 0)
        self.assertGreater(r["regret_fresh_se_pct"], 0)

    def test_tolerance_and_nonfinite(self):
        self.assertTrue(close(0, 0.9e-9))
        self.assertFalse(close(0, 1.1e-9))
        self.assertTrue(close(1e6, 1e6 + 0.9e-6))
        self.assertFalse(close(1e6, 1e6 + 1.1e-6))
        self.assertFalse(close(float("nan"), float("nan")))

    def test_table_reports_mutation_missing_duplicate(self):
        rows = [{"key": "a", "x": 1., "empty": None, "flag": True}]
        saved = [{"key": "a", "x": "1", "empty": "", "flag": "True"}]
        self.assertEqual(compare_tables("toy", rows, saved, ("key",))["status"], "MATCH")
        saved[0]["x"] = "2"
        self.assertEqual(compare_tables("toy", rows, saved, ("key",))["status"], "MISMATCH")
        self.assertEqual(compare_tables("toy", rows, saved * 2, ("key",))["status"], "MISMATCH")
        self.assertEqual(compare_tables("toy", rows, [], ("key",))["status"], "MISMATCH")

    def test_both_sides_threshold_and_count(self):
        cells = [{"pipeline": p, "regime": f"R{n // 9}", "tau_mult": (0.3, 1., 3.)[n % 3],
                  "h_mult": (7, 15, 30)[n // 3 % 3], "G_S_pct": 0.25,
                  "regret_fresh_pct": -1., "regret_stale_pct": 0.5}
                 for p in ("Hybrid-i", "Hybrid-ii") for n in range(153)]
        card = {"tests": {"E4-1": {"horizon_rule": "each", "h_multipliers": [7, 15, 30], "abs_GS_pct_max": 0.25, "pass_fraction_min": 0.9},
                          "E4-2": {"horizon_rule": "each", "h_multipliers": [7, 15, 30], "regret_pct_max": 0.5, "pass_fraction_min": 0.9},
                          "E4-4": {"horizon_rule": "each", "h_multipliers": [7, 15, 30], "regret_pct_max": 0.5, "pass_fraction_min": 0.8},
                          "E4-3": {"best_action_agreement_min": 0.9}, "E4-5": {"descriptive": True}, "E4-6": {"descriptive": True}}}
        result, _ = score(cells, [{"complete": True}] * 17, card, [{"agrees": True}] * 17, Checks())
        self.assertEqual(result["E4-1"]["passed"], 153)
        self.assertEqual(result["E4-2"]["passed"], 153)
        cells[0]["regret_stale_pct"] = 0.500001
        result, _ = score(cells, [{"complete": True}] * 17, card, [{"agrees": True}] * 17, Checks())
        self.assertEqual(result["E4-2"]["passed"], 152)

    def test_zero_cref_rejected(self):
        with self.assertRaises(ValueError):
            summarize(np.zeros(4), np.zeros(4), {}, {})

    def test_reduction_signed_and_zero_denominators(self):
        cells = [{"regime": "toy", "tau_mult": 1., "h_mult": 7,
                  "pipeline": pipeline, "L_fresh": loss, "L_stale": loss}
                 for pipeline, loss in (("M0", 1.), ("Hybrid-i", 3.), ("Hybrid-ii", 1.),
                                        ("M0-tie-i", 2.), ("M0-tie-ii", 1.), ("Hybrid-reversed", 4.))]
        rows = reductions(cells)
        self.assertEqual(rows[0]["hybrid_reduction"], -2)
        self.assertEqual(rows[0]["reduction_fraction"], 0.5)
        self.assertFalse(rows[0]["denominator_positive"])
        self.assertIsNone(rows[2]["reduction_fraction"])

    def test_manifest_validation(self):
        import tempfile
        with tempfile.TemporaryDirectory(prefix="e4-rescore-test-", dir="/tmp") as tmp:
            path = Path(tmp) / "manifest.txt"
            line = "a" * 64 + "  raw/a.npz\n"
            path.write_text(line)
            self.assertEqual(len(read_manifest(path)), 1)
            path.write_text(line + line)
            with self.assertRaises(ValueError):
                read_manifest(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="analytic and mutation checks, no E4 inputs or outputs")
    parser.add_argument("--check-only", action="store_true", help="audit without writing/overwriting reports")
    args = parser.parse_args()
    if args.self_test:
        run = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SelfTests))
        return 0 if run.wasSuccessful() else 1
    outputs = [DATA / "rescore_independent.json", DATA / "rescore_independent.md"]
    if not args.check_only and any(p.exists() for p in outputs):
        parser.error("Refusing to modify an existing output; use --check-only")
    report = audit()
    json_text = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    md_text = markdown(report)
    if not args.check_only:
        for path, text in zip(outputs, (json_text, md_text)):
            with path.open("x", encoding="utf-8") as handle:
                handle.write(text)
    summary = {"status": report["status"], "integrity": report["integrity"]["status"],
               "tables": {k: {field: v[field] for field in ("status", "rows_compared", "fields_compared")} for k, v in report["tables"].items()},
               "tests": {k: report["independent_tests"][k] for k in ("E4-1", "E4-2", "E4-3", "E4-4")},
               "outputs": [] if args.check_only else [str(p.relative_to(ROOT)) for p in outputs]}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "MATCH" else 1


if __name__ == "__main__":
    sys.exit(main())
