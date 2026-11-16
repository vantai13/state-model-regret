"""Independent E4b rescore of saved costs/decisions, including card tests X1-X3.

Doan Van Tai. AI-assisted implementation of LETTER_E4b_rescore_brief.md.
Reuses only the independent E4 rescorer's arithmetic and comparison helpers.
No simulator or locked scoring module is imported; existing files are read-only.
"""

import argparse
import copy
import csv
import json
import math
from pathlib import Path
import subprocess
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(ROOT))
from experiments.letter import e4_rescore as shared

DATA = ROOT / "results/letter/e4b"
BRIEF = "notes/ops/codex/LETTER_E4b_rescore_brief.md"
BRIEF_COMMIT = "c7d26083a5a7aa315d6944d03ef112cecda81777"
SEED = 5000001
AGES = (0.3, 1.0, 3.0)
HORIZONS = (15, 30)
S8 = (
    "G2_r80_b3_s1", "G2_r80_b6_s0", "G2_r90_b3_s0", "G2_r90_b6_s0",
    "G3_r80_b3_s1", "G3_r80_b6_s0", "G3_r90_b3_s0", "G3_r90_b6_s0",
)
FORBIDDEN = {"e4_geant", "e4_rhat", "e4b_run", "e4b_extra", "ev_te"}


def check_metadata(meta, card, checks, name, seed=SEED):
    checks.check(meta["seed"] == seed, "truth seed", path=name, actual=meta["seed"], expected=seed)
    checks.check(meta["pilot"] is False, "pilot false", path=name)
    checks.check(meta["onset_theta"] == card["onset_theta"] == 0.5, "onset theta", path=name)
    checks.check(meta["N"] == 50 and meta["K"] == 128 and meta["R_eval"] == 256
                 and meta["R_dec"] == 128, "chunk configuration", path=name)
    checks.check(meta["units"] == {"cost": "Mb*time", "queue": "Mb"}, "raw units", path=name)


def inspect_raw(data, card, training, checks, manifest_path, seed=SEED):
    manifest = shared.read_manifest(manifest_path)
    paths = sorted((data / "raw").glob("*.npz"))
    json_paths = sorted((data / "raw").glob("*.json"))
    names = {str(p.relative_to(data)) for p in paths + json_paths}
    checks.check(set(manifest) == names, "VM manifest covers exactly all raw JSON/NPZ",
                 missing=sorted(names - set(manifest)), extra=sorted(set(manifest) - names))
    checks.check(len(paths) == len(json_paths) == 170, "170 NPZ + 170 JSON",
                 npz=len(paths), json=len(json_paths))
    hashes = {str(data / name): shared.sha256(data / name) for name in manifest}
    matched = 0
    for name, digest in manifest.items():
        ok = hashes[str(data / name)] == digest
        matched += int(ok)
        checks.check(ok, "VM manifest SHA256", path=name)
    groups, json_matched = {}, 0
    for path in paths:
        meta = shared.load_json(path.with_suffix(".json"))
        ok = shared.sha256(path) == meta["npz_sha256"]
        json_matched += int(ok)
        checks.check(ok, "JSON to NPZ SHA256", path=path.name)
        check_metadata(meta, card, checks, path.name, seed)
        checks.check(path.stem == f"{meta['regime']}_chunk{meta['chunk']:02d}",
                     "filename metadata", path=path.name)
        with np.load(path, allow_pickle=False) as archive:
            arrays = {key: archive[key] for key in archive.files}
        groups.setdefault(meta["regime"], []).append((meta, arrays))
    expected = {row["regime"] for row in training["regimes"]}
    checks.check(len(groups) == 17 and set(groups) == expected, "17 training/truth regimes")
    details = {"vm_manifest": str(manifest_path.relative_to(ROOT)), "npz_files": len(paths),
               "json_files": len(json_paths), "manifest_files_matched": matched,
               "manifest_files_total": len(manifest), "json_npz_hashes_matched": json_matched,
               "regimes": [], "seed": seed, "pilot": False, "onset_theta": card["onset_theta"]}
    return groups, hashes, details


def rule2(row):
    # The card uses the signed measured regrets, both sides, with an inclusive bound.
    return max(row["regret_fresh_pct"], row["regret_stale_pct"]) <= 0.5


def panel_complete(cells, regimes, train_rows):
    expected = {row["regime"] for row in train_rows}
    keys = {(r["regime"], r["pipeline"], r["tau_mult"], r["h_mult"]) for r in cells}
    needed = {(r, p, t, h) for r in expected for p in ("M0", "Hybrid-i", "Hybrid-ii")
              for t in AGES for h in (7, *HORIZONS)}
    return (len(expected) == len(regimes) == 17 and {r["regime"] for r in regimes} == expected
            and all(r["complete"] and r["N"] == 500 and r["chunks"] == 10 for r in regimes)
            and needed <= keys)


def score(cells, regimes, card, train_rows, checks):
    tests, diagnostics = {}, {}
    complete = panel_complete(cells, regimes, train_rows)
    for test, pipeline in (("E4-1", "Hybrid-i"), ("E4-2", "Hybrid-i"), ("E4-4", "Hybrid-ii")):
        rule = card["tests"][test]
        checks.check(rule["horizon_rule"] == "each", "card horizon rule", test=test)
        rows = [r for r in cells if r["pipeline"] == pipeline and r["h_mult"] in rule["h_multipliers"]]
        flags = [abs(r["G_S_pct"]) <= rule["abs_GS_pct_max"] if test == "E4-1" else
                 max(r["regret_fresh_pct"], r["regret_stale_pct"]) <= rule["regret_pct_max"] for r in rows]
        checks.check(len(rows) == 102, "102 E4b test units", test=test, count=len(rows))
        fraction = sum(flags) / len(rows) if rows else 0.0
        tests[test] = {"complete": complete, "denominator": len(rows), "fraction": fraction,
                       "normalization_defined": True, "passed": sum(flags),
                       "threshold": rule["pass_fraction_min"], "units": "each",
                       "verdict": ("PASS" if fraction >= rule["pass_fraction_min"] else "FAIL")
                       if complete else "NOT_EVALUABLE"}
        factors = {}
        for factor in ("h_mult", "tau_mult", "regime"):
            factors[factor] = [{"value": value, "passed": sum(f for r, f in zip(rows, flags) if r[factor] == value),
                                "denominator": sum(r[factor] == value for r in rows)}
                               for value in sorted({r[factor] for r in rows})]
        diagnostics[test] = {"by_factor": factors, "failed_units": [
            {k: r[k] for k in ("regime", "tau_mult", "h_mult", "G_S_pct", "regret_fresh_pct", "regret_stale_pct")}
            for r, flag in zip(rows, flags) if not flag]}
    passed = sum(row["agrees"] for row in train_rows)
    fraction = passed / len(train_rows)
    threshold = card["tests"]["E4-3"]["best_action_agreement_min"]
    tests["E4-3"] = {"denominator": len(train_rows), "fraction": fraction, "passed": passed,
                     "threshold": threshold, "training_only": True,
                     "verdict": "PASS" if fraction >= threshold else "FAIL"}
    for test in ("E4-5", "E4-6"):
        checks.check(card["tests"][test]["descriptive"] is True, "descriptive only", test=test)
        tests[test] = {"tables": ["cells.csv", "reductions.csv"], "verdict": "DESCRIPTIVE"}
    return tests, diagnostics


def score_extra(cells, regimes, train_rows, checks):
    """Translate CARD_E4B.md definitions directly; never read the extra scorer."""
    names = sorted(row["regime"] for row in train_rows)
    slow, fast = sorted(S8), sorted(set(names) - set(S8))
    checks.check(set(slow) <= set(names) and len(fast) == 9, "X1 fixed S8 and complement")
    checks.check(len(names) == len(set(names)) == 17, "extra unique regimes")
    complete = panel_complete(cells, regimes, train_rows)
    at7 = {name: [r for r in cells if r["regime"] == name and r["pipeline"] == "Hybrid-i"
                  and r["h_mult"] == 7] for name in names}
    checks.check(all(len(rows) == 3 for rows in at7.values()), "X1 three ages per regime")
    fast_pass = sum(len(at7[name]) == 3 and all(rule2(r) for r in at7[name]) for name in fast)
    slow_fail = sum(any(not rule2(r) for r in at7[name]) for name in slow)
    x1 = {"slow_regimes": slow, "fast_regimes": fast, "fast_all_ages_pass": fast_pass,
          "fast_n": len(fast), "slow_some_age_fail": slow_fail, "slow_n": len(slow),
          "holds": fast_pass >= 8 and slow_fail >= 6}
    agreeing = {r["regime"] for r in train_rows if r["agrees"]}
    rows = [r for r in cells if r["pipeline"] == "Hybrid-ii" and r["regime"] in agreeing
            and r["h_mult"] in HORIZONS]
    checks.check(len(agreeing) == 14 and len(rows) == 84, "X2 training eligibility and 84 units")
    fraction = sum(rule2(r) for r in rows) / len(rows) if rows else 0.0
    x2 = {"regimes": len(agreeing), "units": len(rows), "met": sum(rule2(r) for r in rows),
          "fraction": fraction, "threshold": 0.9, "holds": fraction >= 0.9}
    m0 = [r for r in cells if r["pipeline"] == "M0" and r["h_mult"] in HORIZONS]
    h30 = [r["G_S_pct"] for r in m0 if r["h_mult"] == 30]
    checks.check(len(m0) == 102 and len(h30) == 51, "X3 102 units and 51 signed G_S values")
    share = sum(rule2(r) for r in m0) / len(m0) if m0 else 0.0
    median = float(np.median(h30)) if h30 else None
    x3 = {"units": len(m0), "m0_rule2_met": sum(rule2(r) for r in m0), "m0_rule2_share": share,
          "median_GS_pct_h30": median, "holds": share <= 0.1 and median is not None and median <= -25.0}
    result = {"regimes": len(names), "X1": x1, "X2": x2, "X3": x3, "complete": complete}
    for row in (x1, x2, x3):
        row["verdict"] = ("HOLDS" if row["holds"] else "FAIL") if complete else "NOT_EVALUABLE"
    return result


def compare_tree(expected, locked, name):
    """Compare all JSON fields, list positions, missing keys and scalar types."""
    rows, saved = [], []

    def visit(a, b, path):
        if isinstance(a, dict) and isinstance(b, dict):
            for key in sorted(set(a) | set(b)):
                if key not in a or key not in b:
                    rows.append({"path": path + "." + key, "value": key in a})
                    saved.append({"path": path + "." + key, "value": key in b})
                else:
                    visit(a[key], b[key], path + "." + key)
        elif isinstance(a, list) and isinstance(b, list):
            rows.append({"path": path + ".length", "value": len(a)})
            saved.append({"path": path + ".length", "value": len(b)})
            for i, (av, bv) in enumerate(zip(a, b)):
                visit(av, bv, f"{path}[{i}]")
        else:
            # Preserve type checks even for JSON booleans that compare equal to 1.
            rows.extend(({"path": path, "value": a}, {"path": path + ".type", "value": type(a).__name__}))
            saved.extend(({"path": path, "value": b}, {"path": path + ".type", "value": type(b).__name__}))
    visit(expected, locked, name)
    return shared.compare_tables(name, rows, saved, ("path",))


def saved_data_diagnostics(cells, reductions, train_rows):
    baselines = []
    for pipeline in ("M0", "M0-tie-i", "Hybrid-i", "Hybrid-ii"):
        rows = [r for r in cells if r["pipeline"] == pipeline and r["h_mult"] in HORIZONS]
        baselines.append({"pipeline": pipeline, "units": len(rows),
                          "median_GS_pct": float(np.median([r["G_S_pct"] for r in rows])),
                          "median_abs_GS_pct": float(np.median([abs(r["G_S_pct"]) for r in rows])),
                          "median_regret_fresh_pct": float(np.median([r["regret_fresh_pct"] for r in rows])),
                          "median_regret_stale_pct": float(np.median([r["regret_stale_pct"] for r in rows])),
                          "rule2_met": sum(rule2(r) for r in rows)})
    negative = [r[f"regret_{side}_pct"] for r in cells for side in ("fresh", "stale")
                if r[f"regret_{side}_pct"] is not None and r[f"regret_{side}_pct"] < 0]
    agreements = {r["regime"]: r["agrees"] for r in train_rows}
    failure_splits = {}
    for pipeline in ("Hybrid-i", "Hybrid-ii"):
        failed = [r for r in cells if r["pipeline"] == pipeline and r["h_mult"] in HORIZONS and not rule2(r)]
        failure_splits[pipeline] = {"failed_units": len(failed),
                                    "training_agrees": sum(agreements[r["regime"]] for r in failed),
                                    "training_disagrees": sum(not agreements[r["regime"]] for r in failed),
                                    "abs_GS_le_0_25_but_rule2_fails": sum(abs(r["G_S_pct"]) <= 0.25 for r in failed)}
    return {"baselines_102_units": baselines,
            "rule2_failure_training_splits": failure_splits,
            "wrong_training_order_regimes": [r["regime"] for r in train_rows if not r["agrees"]],
            "negative_regret_cell_sides": len(negative), "minimum_regret_pct": min(negative, default=None),
            "negative_reduction_denominators": sum(r["hybrid_reduction"] < 0 for r in reductions),
            "zero_reduction_denominators": sum(r["hybrid_reduction"] == 0 for r in reductions)}


def audit():
    checks = shared.Checks()
    lock = shared.load_json(DATA / "lock.json")
    input_names = ("CARD_E4B.json", "CARD_E4B.md", "lock.json", "raw_sha256_vm.txt", "training_checks.json",
                   "cells.csv", "reductions.csv", "regimes.csv", "score.json", "score_extra.json",
                   "merge.json", "run_start.json", "run_summary.json")
    paths = {DATA / name for name in input_names} | {ROOT / name for name in lock["sha256"]}
    paths |= {ROOT / BRIEF, Path(shared.__file__), Path(__file__), ROOT / "results/letter/e4/training_checks.json"}
    before = {str(p): shared.sha256(p) for p in paths}
    committed = subprocess.check_output(["git", "show", f"{BRIEF_COMMIT}:{BRIEF}"], cwd=ROOT)
    checks.check((ROOT / BRIEF).read_bytes() == committed, "brief equals committed version")
    checks.check(len(lock["sha256"]) == 30, "30 locked files")
    lock_matches = 0
    for name, digest in lock["sha256"].items():
        matched = before[str(ROOT / name)] == digest
        lock_matches += int(matched)
        checks.check(matched, "pre-truth lock SHA256", path=name)
    card, training, locked, extra_locked = [shared.load_json(DATA / name) for name in
                                          ("CARD_E4B.json", "training_checks.json", "score.json", "score_extra.json")]
    checks.check(card["test_seed"] == SEED and card["onset_theta"] == 0.5, "card seed/theta")
    checks.check(shared.sha256(DATA / "CARD_E4B.json") == locked["card_sha256"], "score card SHA256")
    checks.check(before[str(DATA / "training_checks.json")] == before[str(ROOT / "results/letter/e4/training_checks.json")],
                 "E4b training is byte copy of E4 seed-1 training")
    for test, threshold in (("E4-1", 0.9), ("E4-2", 0.9), ("E4-4", 0.8)):
        rule = card["tests"][test]
        checks.check(rule["h_multipliers"] == list(HORIZONS) and rule["pass_fraction_min"] == threshold,
                     "E4b horizon/share thresholds", test=test)
        field, value = ("abs_GS_pct_max", 0.25) if test == "E4-1" else ("regret_pct_max", 0.5)
        checks.check(rule[field] == value, "E4b metric threshold", test=test)
    checks.check(card["tests"]["E4-3"]["best_action_agreement_min"] == 0.9, "E4-3 threshold")
    groups, hashes, raw = inspect_raw(DATA, card, training, checks, DATA / "raw_sha256_vm.txt")
    before.update(hashes)
    cells, regimes, raw_ties = shared.recompute(groups, checks, raw)
    reduction_rows = shared.reductions(cells)
    tables = {name: shared.compare_tables(name, rows, DATA / name, keys) for name, rows, keys in (
        ("cells.csv", cells, ("regime", "pipeline", "tau_mult", "h_mult")),
        ("reductions.csv", reduction_rows, ("regime", "tau_mult", "h_mult", "level", "side")),
        ("regimes.csv", regimes, ("regime",)))}
    train_rows = shared.training_checks(training, checks)
    independent, diagnostics = score(cells, regimes, card, train_rows, checks)
    extra = score_extra(cells, regimes, train_rows, checks)
    score_comparisons = shared.compare_score(independent, locked, checks)
    extra_comparison = compare_tree(extra, extra_locked, "score_extra.json")
    checks.check(locked["complete_regimes"] == 17 and locked["descriptive_only"] is False, "score metadata")
    merge = shared.load_json(DATA / "merge.json")
    checks.check(merge["cell_rows"] == len(cells) == 6120 and merge["complete_regimes"] == 17
                 and merge["expected_regimes"] == 17 and merge["cost_units"] == "Mb*time", "merge metadata")
    tables["merge.json.regimes"] = shared.compare_tables("merge.json.regimes", regimes, merge["regimes"], ("regime",))
    run_start, run_summary = [shared.load_json(DATA / name) for name in ("run_start.json", "run_summary.json")]
    for name, record in (("run_start", run_start), ("run_summary", run_summary)):
        checks.check(record["seed"] == SEED and record["pilot"] is False, "run seed/pilot", record=name)
    checks.check(run_start["chunks"] == list(range(10)) and set(run_start["regimes"]) == set(groups)
                 and run_start["onset_theta"] == 0.5, "run start schedule")
    for name, digest in run_start["source_sha256"].items():
        checks.check(lock["sha256"].get(name) == digest, "run start source lock", path=name)
    raw_meta = sorted((m for chunks in groups.values() for m, _ in chunks), key=lambda m: (m["regime"], m["chunk"]))
    summary_meta = sorted(run_summary["chunks"], key=lambda m: (m["regime"], m["chunk"]))
    checks.check(raw_meta == summary_meta and run_summary["chunks_completed"] == len(raw_meta) == 170,
                 "run summary lists all unchanged raw metadata")
    checks.check(shared.close(run_summary["CPU"], math.fsum(r["CPU"] for r in regimes)), "run CPU sum")
    with (DATA / "cells.csv").open(newline="", encoding="utf-8") as handle:
        saved_cells = list(csv.DictReader(handle))
    ties = []
    for (pipeline, side), (count, total) in sorted(raw_ties.items()):
        rows = [r for r in saved_cells if r["pipeline"] == pipeline and r[f"tie_{side}"] != ""]
        denominator = sum(int(r["N"]) for r in rows)
        saved_share = math.fsum(float(r[f"tie_{side}"]) * int(r["N"]) for r in rows) / denominator if denominator else None
        share = count / total if total else None
        checks.check(denominator == total and (share == saved_share if share is None or saved_share is None
                     else shared.close(share, saved_share)), "pooled raw tie share", pipeline=pipeline, side=side)
        ties.append({"pipeline": pipeline, "side": side, "ties": count, "denominator": total,
                     "share": share, "locked_share": saved_share})
    provenance_differences = [{"path": name, "training_source_sha256": digest,
                               "current_locked_sha256": lock["sha256"].get(name)}
                              for name, digest in training["source_sha256"].items()
                              if lock["sha256"].get(name) != digest]
    diagnostics.update(saved_data_diagnostics(cells, reduction_rows, train_rows))
    notes = [
        "G_S = mean(V_stale - V_fresh); dấu âm nghĩa là fresh telemetry gây hại. Dấu khớp locked CSV.",
        "C_ref là mean chi phí action M1_new/fresh đã lưu; M1_new/stale không available. Giữ regret âm, không clip.",
        "Rule 2 dùng max(regret_fresh_pct, regret_stale_pct) <= 0.5, không dùng absolute regret hoặc SE allowance.",
        "SE = sample sd(ddof=1)/sqrt(500); regret và G_S dùng chênh lệch ghép cặp trên cùng instance.",
        "reduction_fraction = tie_reduction/hybrid_reduction nếu mẫu số khác 0, kể cả âm; denominator_positive là cờ riêng.",
        "Tau/h thực lấy từ NPZ (làm tròn theo dt); eligibility dùng h_mult. Onset theta 0.5 chỉ descriptive.",
        "E4b dùng 102 units ở h/T_int=15,30; không mang 153 units/h=7 của E4 sang verdict. E4-3 chỉ training seed 1.",
        "X1 dùng S8 đã định từ E4, không chọn lại theo E4b. X2 chỉ lấy 14 training argmin agreements; X3 dùng median G_S có dấu.",
        "102 units dùng chung instances giữa ages/horizons, không phải independent trials; không tạo population CI.",
        "Rescore xác nhận arithmetic của saved decisions/costs và verdict, không xác nhận estimator/simulator là exact ground truth.",
        "training_checks.json giữ metadata source lịch sử, có hai SHA khác source lock hiện hành; byte copy E4 và lock E4b được kiểm riêng.",
    ]
    if "No card:" in locked.get("note", ""):
        notes.append("score.json giữ note template 'No card: no E4 pass/fail verdicts.' dù card SHA hợp lệ/descriptive_only=false; đây là note không phù hợp lượt có card.")
    changed = [str(Path(p).relative_to(ROOT)) for p, digest in before.items() if shared.sha256(Path(p)) != digest]
    checks.check(not changed, "all audited existing files unchanged during rescore", changed=changed)
    forbidden = sorted(name for name in sys.modules if name.rsplit(".", 1)[-1] in FORBIDDEN)
    checks.check(not forbidden, "no forbidden scorer/simulator imports", modules=forbidden)
    comparisons = [*tables.values(), *score_comparisons, extra_comparison]
    status = "MATCH" if not checks.failures and all(c["status"] == "MATCH" for c in comparisons) else "MISMATCH"
    return {"schema": "letter-e4b-independent-rescore-v1", "responsible": "Doan Van Tai", "status": status,
            "implementation": "AI-assisted independent rescore; only independent E4 helpers, numpy and standard library imported.",
            "brief_commit": BRIEF_COMMIT, "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "script_sha256": shared.sha256(Path(__file__)), "shared_helper_sha256": shared.sha256(Path(shared.__file__)),
            "numpy_version": np.__version__, "tolerance": {"relative": shared.RTOL, "absolute": shared.ATOL,
             "rule": "abs(a-b) <= max(atol, rtol*max(abs(a),abs(b))); counts/labels/booleans/missing values also compared"},
            "integrity": {"status": "PASS" if not checks.failures else "FAIL", "checks": checks.count,
                          "failures": checks.failures, "lock_files_matched": lock_matches, "lock_files_total": len(lock["sha256"]),
                          "audited_files_total": len(before), "audited_files_unchanged": len(before) - len(changed), "raw": raw},
            "tables": tables, "independent_tests": independent, "locked_tests": locked["tests"],
            "score_comparisons": score_comparisons, "independent_extra": extra, "locked_extra": extra_locked,
            "extra_comparison": extra_comparison, "ties": ties, "training_best_actions": train_rows,
            "training_historical_source_differences": provenance_differences,
            "diagnostics_saved_data_only": diagnostics, "conventions_and_limitations": notes,
            "input_sha256": {str(Path(p).relative_to(ROOT)): digest for p, digest in sorted(before.items())}}


def markdown(report):
    integrity, diag = report["integrity"], report["diagnostics_saved_data_only"]
    raw = integrity["raw"]
    lines = ["# E4b — rescore độc lập", "", "Người phụ trách: Doan Van Tai. Triển khai AI-assisted từ brief đã commit.",
             "", f"**{report['status']}**. Brief `{BRIEF_COMMIT}`; HEAD khi chấm `{report['git_head']}`.",
             f"Seed {SEED}; pilot=false; onset theta=0.5. 17 regimes × 10 chunks × 50 = 8.500 instances; 500 ID duy nhất/regime.",
             f"VM SHA: {raw['manifest_files_matched']}/{raw['manifest_files_total']}; JSON→NPZ: {raw['json_npz_hashes_matched']}/{raw['npz_files']}; lock: {integrity['lock_files_matched']}/{integrity['lock_files_total']}.",
             f"Integrity {integrity['status']}: {integrity['checks']} checks, {len(integrity['failures'])} lỗi; {integrity['audited_files_unchanged']}/{integrity['audited_files_total']} inputs/source giữ SHA.",
             "", "| Test | Rescore độc lập | Locked | Verdict độc lập / locked |", "|---|---:|---:|---|"]
    for test in ("E4-1", "E4-2", "E4-3", "E4-4"):
        a, b = report["independent_tests"][test], report["locked_tests"][test]
        lines.append(f"| {test} | {a['passed']}/{a['denominator']} ({100*a['fraction']:.6f}%) | {b['passed']}/{b['denominator']} | {a['verdict']} / {b['verdict']} |")
    for test in ("X1", "X2", "X3"):
        a, b = report["independent_extra"][test], report["locked_extra"][test]
        if test == "X1":
            fmt = lambda r: f"fast {r['fast_all_ages_pass']}/{r['fast_n']}; slow miss {r['slow_some_age_fail']}/{r['slow_n']}"
        elif test == "X2":
            fmt = lambda r: f"{r['met']}/{r['units']} ({100*r['fraction']:.6f}%)"
        else:
            fmt = lambda r: f"rule2 {r['m0_rule2_met']}/{r['units']}; median G_S {r['median_GS_pct_h30']:.9f}%C_ref"
        lines.append(f"| {test} | {fmt(a)} | {fmt(b)} | {a['verdict']} / {b['verdict']} |")
    lines += ["", "E4-1: |G_S|≤0,25%C_ref, share≥90%; E4-2: both regrets≤0,5%C_ref, share≥90%; E4-4: cùng regret rule, share≥80%. E4-3 training agreement≥90%.",
              "E4-5/E4-6: DESCRIPTIVE ở cả hai scorer. X1 fast≥8/9 và slow miss≥6/8; X2≥90%; X3 rule2≤10% và signed median G_S≤−25%C_ref.",
              "", "| Bảng | Rows | Fields | Mismatches |", "|---|---:|---:|---:|"]
    for name, table in report["tables"].items():
        lines.append(f"| {name} | {table['rows_compared']} | {table['fields_compared']} | {len(table['mismatches'])} |")
    lines += ["", "So sánh từng field: rtol=1e-12, atol=1e-9 theo math.isclose (max hai tolerance); kiểm riêng ô trống, nhãn, boolean. Cost/SE: Mb·time; pct: %C_ref; sai khác pct: percentage points.",
              "", "| Bảng | Field | Max abs diff | Mismatches |", "|---|---|---:|---:|"]
    for name, table in report["tables"].items():
        for field, stat in table["fields"].items():
            lines.append(f"| {name} | {field} | {stat['max_abs_diff']:.12g} | {stat['mismatches']} |")
    lines += ["", "Phân tích mô tả saved data, không đổi verdict/threshold:", "", "| Test | h/T_int=15 | h/T_int=30 |", "|---|---:|---:|"]
    for test in ("E4-1", "E4-2", "E4-4"):
        counts = [f"{r['passed']}/{r['denominator']}" for r in diag[test]["by_factor"]["h_mult"]]
        lines.append(f"| {test} | " + " | ".join(counts) + " |")
    lines += ["", "| Pipeline (102 units) | Median signed G_S %C_ref | Median abs G_S %C_ref | Median regret fresh %C_ref | Median regret stale %C_ref | Rule2 |", "|---|---:|---:|---:|---:|---:|"]
    for row in diag["baselines_102_units"]:
        lines.append(f"| {row['pipeline']} | {row['median_GS_pct']:.6f} | {row['median_abs_GS_pct']:.6f} | {row['median_regret_fresh_pct']:.6f} | {row['median_regret_stale_pct']:.6f} | {row['rule2_met']}/{row['units']} |")
    lines += ["", "Training ordering khác tại: " + ", ".join(diag["wrong_training_order_regimes"]) + ".",
              f"Giữ {diag['negative_regret_cell_sides']} regret âm, min {diag['minimum_regret_pct']:.12g}%C_ref; reduction mẫu số âm {diag['negative_reduction_denominators']}, mẫu số 0 {diag['zero_reduction_denominators']}.", ""]
    split = diag["rule2_failure_training_splits"]
    lines += [f"E4-1 trượt {len(diag['E4-1']['failed_units'])} units; phân bố theo h/regime và từng unit nằm trong JSON.",
              f"Hybrid-i có {split['Hybrid-i']['abs_GS_le_0_25_but_rule2_fails']} units đạt |G_S|≤0,25% nhưng trượt rule 2: chênh lệch fresh/stale nhỏ không đảm bảo regret mỗi phía nhỏ.",
              f"Trong {split['Hybrid-ii']['failed_units']} units trượt Hybrid-ii, {split['Hybrid-ii']['training_disagrees']} thuộc các regime training ordering khác, {split['Hybrid-ii']['training_agrees']} thuộc ordering đúng. Đây là phân rã mô tả, chưa chứng minh cơ chế hoặc instance noise.",
              "Forecast E4-1 holds được giữ; forecast E4-2 holds không đứng; E4-3 FAIL đã biết trước truth; E4-4 forecast chỉ ghi borderline. X1/X2/X3 holds đều đứng.",
              "Không fit/tune hoặc chạy thêm truth để cải thiện verdict; nhiệm vụ này chỉ kiểm chứng lại raw đã lưu.", ""]
    lines += ["- " + note for note in report["conventions_and_limitations"]]
    lines += ["", "Metadata source lịch sử của training (không sửa):", "", "```json",
              json.dumps(report["training_historical_source_differences"], ensure_ascii=False, indent=2), "```"]
    comparisons = [*report["tables"].values(), *report["score_comparisons"], report["extra_comparison"]]
    problems = integrity["failures"] + [m for c in comparisons for m in c["mismatches"]]
    lines += ["", f"Tổng mismatches: {len(problems)}."]
    if problems:
        lines += ["", "```json", json.dumps(problems, ensure_ascii=False, indent=2), "```"]
    lines += ["", "Lệnh thực thi:", "", "```bash", "source .venv/bin/activate && source experiments/explore_ctmc/env.sh",
              "PYTHONDONTWRITEBYTECODE=1 python -m experiments.letter.e4b_rescore --self-test",
              "PYTHONDONTWRITEBYTECODE=1 python -m experiments.letter.e4b_rescore", "```", "",
              "Source mới: `experiments/letter/e4b_rescore.py`. Outputs mới: `results/letter/e4b/rescore_independent.json` và `.md`.",
              "Không tạo CSV/log/biểu đồ/config mới; JSON lưu metrics/checks/SHA/sai khác. Không commit, SSH, truth run hoặc sửa file hiện có."]
    return "\n".join(lines) + "\n"


class SelfTests(unittest.TestCase):
    def setUp(self):
        fast = ("G1_r80_b3_s1", "G1_r80_b6_s0", "G1_r80_b6_s1", "G2_r80_b6_s1", "G2_r90_b3_s1",
                "G2_r90_b6_s1", "G3_r80_b6_s1", "G3_r90_b3_s1", "G3_r90_b6_s1")
        names = sorted((*S8, *fast))
        self.training = [{"regime": r, "agrees": i < 14} for i, r in enumerate(names)]
        self.regimes = [{"regime": r, "complete": True, "N": 500, "chunks": 10} for r in names]
        self.cells = [{"regime": r, "pipeline": p, "tau_mult": t, "h_mult": h,
                       "G_S_pct": -25.0 if p == "M0" else 0.25,
                       "regret_fresh_pct": 1.0 if p == "M0" else -1.0,
                       "regret_stale_pct": 1.0 if p == "M0" else (0.500001 if p == "Hybrid-i" and h == 7 and r in S8 else 0.5)}
                      for r in names for p in ("M0", "Hybrid-i", "Hybrid-ii") for t in AGES for h in (7, *HORIZONS)]
        self.card = {"tests": {"E4-1": {"h_multipliers": [15, 30], "horizon_rule": "each", "abs_GS_pct_max": 0.25, "pass_fraction_min": 0.9},
                               "E4-2": {"h_multipliers": [15, 30], "horizon_rule": "each", "regret_pct_max": 0.5, "pass_fraction_min": 0.9},
                               "E4-4": {"h_multipliers": [15, 30], "horizon_rule": "each", "regret_pct_max": 0.5, "pass_fraction_min": 0.8},
                               "E4-3": {"best_action_agreement_min": 0.9}, "E4-5": {"descriptive": True}, "E4-6": {"descriptive": True}}}

    def extra(self):
        checks = shared.Checks()
        result = score_extra(self.cells, self.regimes, self.training, checks)
        self.assertEqual(checks.failures, [])
        return result

    def test_102_units_exclude_h7_and_include_metric_boundaries(self):
        checks = shared.Checks()
        tests, _ = score(self.cells, self.regimes, self.card, self.training, checks)
        self.assertEqual(checks.failures, [])
        for test in ("E4-1", "E4-2", "E4-4"):
            self.assertEqual((tests[test]["passed"], tests[test]["denominator"], tests[test]["verdict"]), (102, 102, "PASS"))
        row = next(r for r in self.cells if r["pipeline"] == "Hybrid-i" and r["h_mult"] == 15)
        row["regret_stale_pct"] = 0.500001
        tests, _ = score(self.cells, self.regimes, self.card, self.training, shared.Checks())
        self.assertEqual(tests["E4-2"]["passed"], 101)

    def test_x1_counts_regimes_and_all_three_ages(self):
        result = self.extra()
        self.assertEqual((result["X1"]["fast_all_ages_pass"], result["X1"]["slow_some_age_fail"]), (9, 8))
        for i, name in enumerate(result["X1"]["fast_regimes"][:2]):
            row = next(r for r in self.cells if r["regime"] == name and r["pipeline"] == "Hybrid-i" and r["h_mult"] == 7)
            row["regret_fresh_pct"] = 0.500001
            self.assertEqual(self.extra()["X1"]["holds"], i == 0)

    def test_x1_requires_six_slow_regimes_to_miss(self):
        for name in S8[:3]:
            for row in self.cells:
                if row["regime"] == name and row["pipeline"] == "Hybrid-i" and row["h_mult"] == 7:
                    row["regret_stale_pct"] = 0.5
        self.assertFalse(self.extra()["X1"]["holds"])

    def test_x2_training_eligibility_and_90_percent_boundary(self):
        agreeing = {r["regime"] for r in self.training if r["agrees"]}
        chosen = []
        for row in self.cells:
            if row["pipeline"] == "Hybrid-ii" and row["h_mult"] in HORIZONS:
                if row["regime"] in agreeing:
                    chosen.append(row)
                else:
                    row["regret_stale_pct"] = 1000.0
        self.assertEqual(self.extra()["X2"]["met"], 84)
        for row in chosen[:8]:
            row["regret_stale_pct"] = 0.500001
        self.assertTrue(self.extra()["X2"]["holds"])
        chosen[8]["regret_stale_pct"] = 0.500001
        self.assertFalse(self.extra()["X2"]["holds"])

    def test_x3_signed_median_and_share_conjunction(self):
        self.assertTrue(self.extra()["X3"]["holds"])
        m0 = [r for r in self.cells if r["pipeline"] == "M0" and r["h_mult"] in HORIZONS]
        for row in m0[:10]:
            row["regret_fresh_pct"], row["regret_stale_pct"] = -100.0, 0.5
        self.assertTrue(self.extra()["X3"]["holds"])
        m0[10]["regret_fresh_pct"], m0[10]["regret_stale_pct"] = 0.0, 0.0
        self.assertFalse(self.extra()["X3"]["holds"])
        m0[10]["regret_fresh_pct"] = 1.0
        for row in m0:
            if row["h_mult"] == 30:
                row["G_S_pct"] = 25.0
        self.assertFalse(self.extra()["X3"]["holds"])

    def test_incomplete_panel_and_missing_cell_not_evaluable(self):
        self.regimes[0]["complete"] = False
        self.assertEqual({self.extra()[t]["verdict"] for t in ("X1", "X2", "X3")}, {"NOT_EVALUABLE"})
        self.regimes[0]["complete"] = True
        self.cells.pop()
        self.assertFalse(panel_complete(self.cells, self.regimes, self.training))

    def test_json_comparison_detects_field_type_list_and_count_mutations(self):
        original = self.extra()
        self.assertEqual(compare_tree(original, original, "extra")["status"], "MATCH")
        for field, value in (("met", 83), ("holds", 1)):
            mutated = copy.deepcopy(original)
            mutated["X2"][field] = value
            self.assertEqual(compare_tree(original, mutated, "extra")["status"], "MISMATCH")
        mutated = copy.deepcopy(original)
        mutated["X1"]["slow_regimes"][0] = "wrong"
        del mutated["X3"]["units"]
        self.assertEqual(compare_tree(original, mutated, "extra")["status"], "MISMATCH")

    def test_seed_pilot_and_onset_mutations_detected(self):
        meta = {"seed": SEED, "pilot": False, "onset_theta": 0.5, "N": 50, "K": 128, "R_eval": 256,
                "R_dec": 128, "units": {"cost": "Mb*time", "queue": "Mb"}}
        for field, wrong in (("seed", 3000001), ("pilot", True), ("onset_theta", 0.25)):
            checks = shared.Checks()
            check_metadata({**meta, field: wrong}, {"onset_theta": 0.5}, checks, "toy")
            self.assertEqual(len(checks.failures), 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="analytic and mutation tests; no experiment inputs/outputs")
    parser.add_argument("--check-only", action="store_true", help="rescore without writing reports")
    args = parser.parse_args()
    if args.self_test:
        suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(cls) for cls in (shared.SelfTests, SelfTests))
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
    outputs = [DATA / "rescore_independent.json", DATA / "rescore_independent.md"]
    if not args.check_only and any(path.exists() for path in outputs):
        parser.error("Refusing to modify an existing output; use --check-only")
    report = audit()
    texts = [json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", markdown(report)]
    if not args.check_only:
        for path, text in zip(outputs, texts):
            with path.open("x", encoding="utf-8") as handle:
                handle.write(text)
    print(json.dumps({"status": report["status"], "integrity": report["integrity"]["status"],
                      "failures": report["integrity"]["failures"],
                      "tables": {k: {field: v[field] for field in ("status", "rows_compared", "fields_compared")} for k, v in report["tables"].items()},
                      "tests": report["independent_tests"], "extra": report["independent_extra"],
                      "outputs": [] if args.check_only else [str(p.relative_to(ROOT)) for p in outputs]}, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "MATCH" else 1


if __name__ == "__main__":
    sys.exit(main())
