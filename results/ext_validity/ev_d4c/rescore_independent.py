"""Independent CARD/raw-input rescore for Doan Van Tai; standard library only.

No panel implementation is read or imported. Existing files are read-only;
the result is created exclusively, so an existing result cannot be overwritten.
Run from the repository root with the environment specified in the brief.
"""

import csv
import hashlib
import json
import math
from pathlib import Path
import statistics


ROOT = Path(__file__).resolve().parent
GROUPS = {"low": (0.1, 0.3, 0.5), "band": (0.8, 1.0, 1.2), "high": (2.5, 5.0)}
MISMATCHES = []
COMPARED = {"manifest": 0, "score": 0, "rows": 0}


def read_json(path):
    return json.loads(path.read_text())


def compare(path, actual, reference, category):
    """Compare all leaves, with strictly relative 1e-12 float tolerance."""
    if isinstance(actual, dict) and isinstance(reference, dict):
        for key in sorted(actual.keys() | reference.keys()):
            if key not in actual or key not in reference:
                COMPARED[category] += 1
                MISMATCHES.append({"field": path + "." + key,
                                   "recomputed": actual.get(key),
                                   "reference": reference.get(key), "error": "missing key"})
            else:
                compare(path + "." + key, actual[key], reference[key], category)
        return
    COMPARED[category] += 1
    if isinstance(actual, float) and isinstance(reference, (int, float)):
        equal = math.isclose(actual, reference, rel_tol=1e-12, abs_tol=0.0)
    else:
        equal = type(actual) is type(reference) and actual == reference
    if not equal:
        MISMATCHES.append({"field": path, "recomputed": actual, "reference": reference})


def sign(x):
    return (x > 0) - (x < 0)


def summarize(rows):
    n = len(rows)
    noise = [r for r in rows if r["noise_ok"]]
    ratios = [r["inc_ratio"] for r in rows if r["inc_ratio"] is not None]
    return {
        "n": n,
        "inc_share": sum(r["inc_ok"] for r in rows) / n if n else None,
        "level_share": sum(r["level_ok"] for r in rows) / n if n else None,
        "median_inc_ratio": statistics.median(ratios) if ratios else None,
        "n_inc_ratio": len(ratios),
        "n_regimes": len({r["regime"] for r in rows}),
        "n_noise": len(noise),
        "inc_share_noise": sum(r["inc_ok"] for r in noise) / len(noise) if noise else None,
        "status": "OK" if n >= 10 else "NOT_EVALUABLE",
    }


def main():
    # Manifest validation is deliberately first, before parsing any test output.
    manifest = read_json(ROOT / "raw_manifest.json")
    files = {p.name: p for p in (ROOT / "test").glob("*.json")}
    expected_hashes = manifest["sha256"]
    compare("manifest.count", len(files), manifest["n"], "manifest")
    compare("manifest.entry_count", len(expected_hashes), manifest["n"], "manifest")
    compare("manifest.names", sorted(files), sorted(expected_hashes), "manifest")
    hashes = {name: hashlib.sha256(p.read_bytes()).hexdigest() for name, p in files.items()}
    for name in sorted(files.keys() & expected_hashes.keys()):
        compare("manifest.sha256." + name, hashes[name], expected_hashes[name], "manifest")
    manifest_result = {"expected_count": manifest["n"], "manifest_entries": len(expected_hashes),
                       "actual_count": len(files), "sha256_checked": len(hashes),
                       "missing": sorted(expected_hashes.keys() - files.keys()),
                       "extra": sorted(files.keys() - expected_hashes.keys()),
                       "mismatches": list(MISMATCHES), "passed": not MISMATCHES}

    cases = read_json(ROOT / "cases.json")
    selection = read_json(ROOT / "selection.json")
    with (ROOT / "predictions.csv").open(newline="") as f:
        predictions_list = list(csv.DictReader(f))
    predictions = {(r["id"], int(r["h_mult"]), r["twin"]): float(r["pred_abs"])
                   for r in predictions_list}
    if len(predictions) != len(predictions_list):
        raise ValueError("Duplicate prediction keys")
    outputs = {}
    for name in sorted(files):
        out = read_json(files[name])
        key = (out["case"]["id"], int(out["h_mult"]))
        if key in outputs:
            raise ValueError("Duplicate test key: " + str(key))
        outputs[key] = out

    rows = []
    d6 = {a: [] for a in "CLH"}
    for case in cases:
        cid, arm = case["id"], case["arm"]
        if (cid, 10) not in outputs or (cid, 30) not in outputs:
            continue
        o10, o30 = outputs[cid, 10], outputs[cid, 30]
        e10, e30 = o10["E_stay"]["mean"], o30["E_stay"]["mean"]
        for twin in ("fluid_nowcast", "ratefluid_nowcast"):
            p10, p30 = predictions[cid, 10, twin], predictions[cid, 30, twin]
            pred_pct = 100 * p30 / e30
            if abs(pred_pct) < 0.25:
                continue
            t10, t30 = o10["twins"][twin], o30["twins"][twin]
            dg, dp = t30["G_S"] - t10["G_S"], p30 - p10
            rows.append({"arm": arm, "regime": case["regime"], "r": case["r"],
                         "tau": case["tau"], "twin": twin, "pred30": pred_pct,
                         "G30": t30["pct_E_stay"], "G10_abs": t10["G_S"],
                         "G30_abs": t30["G_S"], "pred10_abs": p10, "pred30_abs": p30,
                         "inc_ok": sign(dg) == sign(dp),
                         "level_ok": sign(t30["pct_E_stay"]) == sign(pred_pct),
                         "inc_ratio": dg / dp if dp else None,
                         "noise_ok": abs(dg) > 2 * (t10["se"] + t30["se"])})
        # D6 uses all paired plug-in rows, without the nowcast prediction filter.
        for twin in ("fluid", "ratefluid"):
            t10, t30 = o10["twins"][twin], o30["twins"][twin]
            scaled10 = t10["pct_E_stay"] * e10 / e30
            limit = max(0.25, 2 * (t30["se_pct"] + t10["se_pct"] * e10 / e30))
            d6[arm].append(abs(t30["pct_E_stay"] - scaled10) <= limit)

    score = {"arms": {}}
    for arm in "CLH":
        arm_cases = [c for c in cases if c["arm"] == arm]
        expected = len(arm_cases) * 2
        completed = sum((c["id"], h) in outputs for c in arm_cases for h in (10, 30))
        subset = [r for r in rows if r["arm"] == arm]
        score["arms"][arm] = {
            "arm_status": selection["arms"][arm]["arm_status"],
            "completed": completed, "of": expected,
            "inconclusive": completed < 0.9 * expected,
            "groups": {g: summarize([r for r in subset if r["r"] in values])
                       for g, values in GROUPS.items()},
            "by_r": {str(value): summarize([r for r in subset if r["r"] == value])
                     for value in sorted({c["r"] for c in arm_cases})}}
        ds = sum(d6[arm]) / len(d6[arm]) if d6[arm] else None
        score["D6-" + arm] = {"n": len(d6[arm]), "share": ds, "threshold": 0.90,
                               "exploratory": arm != "C",
                               "verdict": "NOT_EVALUABLE" if ds is None else
                               ("INCONCLUSIVE" if score["arms"][arm]["inconclusive"] else
                                "PASS" if ds >= 0.90 else "FAIL")}

    low = score["arms"]["C"]["groups"]["low"]
    band = score["arms"]["C"]["groups"]["band"]

    def verdict(group, passed):
        if score["arms"]["C"]["inconclusive"]:
            return "INCONCLUSIVE"
        if group["status"] != "OK":
            return "NOT_EVALUABLE"
        return "PASS" if passed else "FAIL"

    score["H1"] = {"verdict": verdict(low, low["inc_share"] is not None and low["inc_share"] >= 0.8),
                   "n": low["n"], "inc_share": low["inc_share"],
                   "median_inc_ratio": low["median_inc_ratio"], "threshold": 0.8}
    score["H2"] = {"verdict": verdict(band, band["inc_share"] is not None and
                                    band["inc_share"] <= 0.65 and
                                    band["median_inc_ratio"] is not None and band["median_inc_ratio"] < 0.5),
                   "n": band["n"], "inc_share": band["inc_share"],
                   "median_inc_ratio": band["median_inc_ratio"], "max_inc_share": 0.65,
                   "median_inc_ratio_strictly_below": 0.5}
    labels = {}
    for arm in "LH":
        group = score["arms"][arm]["groups"]["band"]
        labels[arm] = ("INCONCLUSIVE" if score["arms"][arm]["inconclusive"] else
                       "NOT_EVALUABLE" if group["status"] != "OK" else
                       "WORKS" if group["inc_share"] >= 0.8 else
                       "FAILS" if group["inc_share"] <= 0.65 else "MIXED")
        score["arms"][arm]["band_label"] = labels[arm]
    h3 = "UNRESOLVED"
    if score["H2"]["verdict"] == "PASS":
        if labels["L"] == "WORKS":
            h3 = "LOOPING"
        elif labels["L"] == "FAILS" and labels["H"] == "WORKS":
            h3 = "LOAD"
        elif labels["L"] == labels["H"] == "FAILS":
            h3 = "TRACE_OR_OTHER"
    score["H3"] = {"verdict": h3, "L_band": labels["L"], "H_band": labels["H"]}

    # References are opened only after the independent computation is complete.
    compare("score", score, read_json(ROOT / "score.json"), "score")
    with (ROOT / "score_rows.csv").open(newline="") as f:
        reference_rows = list(csv.DictReader(f))
    compare("rows.count", len(rows), len(reference_rows), "rows")

    def row_key(r):
        return (r["arm"], r["regime"], float(r["r"]), r["twin"])

    computed_map = {row_key(r): r for r in rows}
    reference_map = {row_key(r): r for r in reference_rows}
    compare("rows.unique_computed", len(computed_map), len(rows), "rows")
    compare("rows.unique_reference", len(reference_map), len(reference_rows), "rows")
    compare("rows.keys", sorted(computed_map), sorted(reference_map), "rows")
    for key in sorted(computed_map.keys() & reference_map.keys()):
        ref = {}
        for field, value in reference_map[key].items():
            if field in ("inc_ok", "level_ok", "noise_ok"):
                if value not in ("True", "False"):
                    raise ValueError("Invalid boolean: " + value)
                ref[field] = value == "True"
            elif field in ("arm", "regime", "twin"):
                ref[field] = value
            else:
                ref[field] = float(value) if value else None
        compare("rows." + str(key), computed_map[key], ref, "rows")

    result = {
        "responsible": "Doan Van Tai", "recomputed": score,
        "rows": rows, "row_count": len(rows),
        "d6_pass_counts": {a: sum(d6[a]) for a in "CLH"},
        "manifest_check": manifest_result, "mismatches": MISMATCHES,
        "compared_fields": sum(COMPARED.values()), "compared_fields_by_category": COMPARED,
        "relative_tolerance": 1e-12, "absolute_tolerance": 0.0,
        "readings": [
            "D6: CARD references EV-D4b without restating the formula; use the explicit formula in the brief, without reading panel code.",
            "D6 denominator is every paired fluid/ratefluid plug-in row; the 0.25 pp prediction filter applies only to nowcast rows.",
            "Shares and medians pool twins and regimes as rows, without regime averaging; noise filtering is secondary only.",
            "Count completed outputs as present expected case/h pairs; there is no test status field required by the brief.",
            "A zero predicted increment has undefined ratio (null, excluded from median); sign(0)=0. No such retained row here.",
            "NOT_EVALUABLE applies at n<10; INCONCLUSIVE takes precedence for hypothesis verdicts when an arm has <90% outputs. Neither occurs here.",
            "H3 follows the reading table literally: H2 PASS and L WORKS implies LOOPING regardless of H; this is the card label, not independent causal proof."
        ],
    }
    with (ROOT / "rescore_independent.json").open("x") as f:
        json.dump(result, f, indent=2, allow_nan=False)
        f.write("\n")
    print(json.dumps({"match": not MISMATCHES, "compared_fields": result["compared_fields"],
                      "row_count": len(rows), "manifest_check": manifest_result,
                      "verdicts": {k: v["verdict"] for k, v in score.items() if k != "arms"},
                      "mismatches": MISMATCHES}, indent=2))
    return 0 if not MISMATCHES else 1


if __name__ == "__main__":
    raise SystemExit(main())
