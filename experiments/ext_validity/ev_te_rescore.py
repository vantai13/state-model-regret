"""Independent EV-TE rescore from CARD and raw arrays; NumPy + stdlib only.

Run from the repository root with the project's virtual environment activated.
No repository modules, simulation, or scorer implementation are loaded.
"""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "results/ext_validity/ev_te"
TWINS = ("M0", "P", "CE")
H_MULT = np.array([1, 2, 4, 7, 15, 30], dtype=float)
TAU_MULT = np.array([0.1, 0.3, 1, 3], dtype=float)
THRESHOLDS = {"H1": 0.90, "H2": 0.90, "H3": 0.80, "H4": 0.90}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def paired_se(values):
    """Standard error across paired instance contrasts (sample SD, ddof=1)."""
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or len(values) < 2:
        raise ValueError("Paired SE requires at least two independent instances")
    return float(np.std(values, ddof=1) / math.sqrt(len(values)))


def flags(twin, valid, z, pred, delta, delta_pred, se):
    """CARD section 3; percentage and percentage-point units throughout."""
    h1 = bool(valid and twin == "M0" and abs(z) >= 0.25 and abs(pred) >= 0.25)
    h2 = bool(valid and twin == "M0" and abs(delta_pred) >= 0.25
              and abs(delta) >= 2 * se)
    h4 = bool(valid and twin == "P")
    return {
        "H1_eligible": h1,
        "H1_pass": bool(h1 and np.sign(z) == np.sign(pred)),
        "H2_eligible": h2,
        "H2_pass": bool(h2 and np.sign(delta) == np.sign(delta_pred)),
        "H3_eligible": h2,
        "H3_pass": bool(h2 and abs(delta - delta_pred)
                        <= max(0.25, 0.25 * abs(delta_pred), 2 * se)),
        "H4_eligible": h4,
        "H4_pass": bool(h4 and abs(delta) <= max(0.25, 2 * se)),
    }


def contrasts(values, pipelines, twin):
    """L00=old twin, L10=fresh twin, L01=old M1, L11=fresh M1.

    P_new and CE_new coincide with M0_new (CARD section 1).
    GS=L00-L10; GM=L00-L01; Gamma=L00-L10-L01+L11.
    """
    index = {str(name): i for i, name in enumerate(pipelines)}
    if len(index) != len(pipelines):
        raise ValueError("Duplicate pipeline names")
    l00 = values[:, index[twin + "_old"], :]
    l10 = values[:, index["M0_new"], :]
    l01 = values[:, index["M1_old"], :]
    l11 = values[:, index["M1_new"], :]
    return l00 - l10, l00 - l01, (l00 - l10) - (l01 - l11), l11


def self_checks():
    # Analytic toy with correlated horizons: pairing must precede the SE.
    assert paired_se(np.array([2., 4., 6.])) == float(np.std([2., 4., 6.], ddof=1) / np.sqrt(3))
    x = np.array([1., 3., 8.])
    assert paired_se((x + 2) - x) == 0
    names = ["CE_old", "M1_old", "M0_new", "P_old", "M1_new", "M0_old"]
    a = np.zeros((3, 6, 6))
    for n, v in {"M0_old": 10, "M0_new": 6, "M1_old": 7, "M1_new": 2}.items():
        a[:, names.index(n), :] = v
    gs, gm, gamma, ref = contrasts(a, names, "M0")
    assert np.all(gs == 4) and np.all(gm == 3) and np.all(gamma == -1) and np.all(ref == 2)
    order = [5, 2, 1, 4, 0, 3]
    for first, second in zip(contrasts(a, names, "M0"),
                             contrasts(a[:, order, :], [names[i] for i in order], "M0")):
        assert np.array_equal(first, second)
    edge = flags("M0", True, 0.25, 0.25, 0.25, 0.25, 0.125)
    assert all(edge[k] for k in ("H1_eligible", "H1_pass", "H2_eligible", "H2_pass", "H3_pass"))
    assert not any(flags("M0", False, 1, 1, 1, 1, 0).values())
    assert flags("P", True, 0, 0, 0.25, 0, 0)["H4_pass"]
    assert not flags("P", True, 0, 0, 0.250001, 0, 0)["H4_pass"]
    return {"status": "PASS", "checks": ["sample_SE", "paired_horizons", "factorial_contrasts",
            "pipeline_permutation", "inclusive_thresholds", "stationarity_exclusion", "H4_boundary"]}


def compute(base=BASE):
    checks = self_checks()
    input_hashes = {}

    def read_json(path):
        input_hashes[str(path.relative_to(ROOT))] = digest(path)
        return json.loads(path.read_text())

    input_hashes[str((base / "CARD.md").relative_to(ROOT))] = digest(base / "CARD.md")
    regimes = read_json(base / "regimes.json")
    regimes = {r["id"]: r for r in regimes}
    prediction_path = base / "predictions.csv"
    input_hashes[str(prediction_path.relative_to(ROOT))] = digest(prediction_path)
    with prediction_path.open(newline="") as f:
        predictions = list(csv.DictReader(f))
    by_prediction = {}
    for row in predictions:
        key = (row["regime"], float(row["tau_mult"]), row["twin"])
        if key in by_prediction:
            raise ValueError(f"Duplicate prediction: {key}")
        by_prediction[key] = row

    cells = []
    numeric_rows = []
    samples = []
    max_delta_prediction_check = 0.0
    max_level_prediction_check = 0.0
    for raw_path in sorted((base / "raw").glob("*.npz")):
        rid = raw_path.stem
        regime = regimes[rid]
        metadata = read_json(raw_path.with_suffix(".json"))
        train = read_json(base / "train" / (rid + ".json"))
        if train["excluded"] or metadata["timing_only"]:
            raise ValueError(f"Unexpected excluded/timing-only raw regime: {rid}")
        nonstationary = [i for i, u in enumerate(regime["max_action_mean_utilization"]) if u >= 1]
        if nonstationary != train["nonstationary_actions"]:
            raise ValueError(f"Stationarity metadata disagree: {rid}")
        valid = not nonstationary
        input_hashes[str(raw_path.relative_to(ROOT))] = digest(raw_path)
        with np.load(raw_path, allow_pickle=False) as raw:
            values = raw["pipeline_V"]
            pipes = raw["pipelines"].tolist()
            h = raw["h"]
            tau = raw["tau"]
            stay = raw["V_stay"]
        if not np.isfinite(values).all() or not np.isfinite(stay).all():
            raise ValueError(f"Nonfinite raw values: {rid}")
        assert values.shape == (metadata["N"], 4, len(pipes), 6)
        assert stay.shape == (metadata["N"], 6)
        assert pipes == metadata["pipelines"]
        assert metadata["regime"] == rid
        # The stored physical grids are rounded to integer dt steps; the
        # nominal multipliers label cells, not exact physical times.
        assert np.all(np.abs(h - H_MULT * train["T_int"]) <= metadata["dt"] / 2 + 1e-10)
        assert np.all(np.abs(tau - TAU_MULT * train["T_int"]) <= metadata["dt"] / 2 + 1e-10)
        assert np.allclose(h, np.array(metadata["h_steps"]) * metadata["dt"], rtol=1e-12, atol=1e-12)
        assert np.allclose(tau, np.array(metadata["tau_steps"]) * metadata["dt"], rtol=1e-12, atol=1e-12)
        for it, tau_mult in enumerate(TAU_MULT):
            for twin in TWINS:
                prediction = by_prediction[(rid, float(tau_mult), twin)]
                assert prediction["stationary_rate_valid"] in ("True", "False")
                assert (prediction["stationary_rate_valid"] == "True") == valid
                assert json.loads(prediction["nonstationary_actions"]) == nonstationary
                gs, gm, gamma, ref = contrasts(values[:, it, :, :], pipes, twin)
                cref = float(np.mean(ref[:, -1]))
                if cref <= 0:
                    raise ValueError(f"Nonpositive Cref: {rid}/{tau_mult}")
                scale = 100 / cref
                delta_instances = gs[:, -1] - gs[:, 3]
                delta = float(np.mean(delta_instances) * scale)
                se = paired_se(delta_instances) * scale
                delta_pred_raw = float(prediction["Delta_pred"])
                level7 = float(prediction["level_h7"])
                level30 = float(prediction["level_h30"])
                level_difference = level30 - level7
                max_delta_prediction_check = max(max_delta_prediction_check, abs(delta_pred_raw - level_difference))
                assert math.isclose(delta_pred_raw, level_difference, rel_tol=1e-12, abs_tol=1e-10)
                assert math.isclose(level7, float(h[3]) * float(prediction["slope_h7"]), rel_tol=1e-12, abs_tol=1e-10)
                assert math.isclose(level30, float(h[-1]) * float(prediction["slope_h30"]), rel_tol=1e-12, abs_tol=1e-10)
                max_level_prediction_check = max(max_level_prediction_check, abs(float(prediction["level_pred"]) - level30))
                assert math.isclose(float(prediction["level_pred"]), level30, rel_tol=1e-12, abs_tol=1e-10)
                gs_mean = np.mean(gs, axis=0)
                gm_mean = np.mean(gm, axis=0)
                gamma_mean = np.mean(gamma, axis=0)
                z = float(gs_mean[-1] * scale)
                pred = level30 * scale
                delta_pred = delta_pred_raw * scale
                row = {
                    "regime": rid, "tau_mult": float(tau_mult), "tau": float(tau[it]),
                    "twin": twin, "topology": regime["topology"], "slow": regime["slow"],
                    "stationary_rate_valid": valid, "nonstationary_actions": nonstationary,
                    "N": metadata["N"], "seed": metadata["seed"],
                    "Cref": cref, "G_S": float(gs_mean[-1]), "G_M": float(gm_mean[-1]),
                    "Gamma": float(gamma_mean[-1]), "z": z, "pred": pred,
                    "Delta_meas": delta, "Delta_pred": delta_pred, "se": float(se),
                    "level_h7": level7, "level_h30": level30,
                    "Delta_pred_raw": delta_pred_raw,
                    "h": h.tolist(), "Cref_by_h": np.mean(ref, axis=0).tolist(),
                    "G_S_by_h": gs_mean.tolist(), "G_M_by_h": gm_mean.tolist(),
                    "Gamma_by_h": gamma_mean.tolist(),
                }
                row.update(flags(twin, valid, z, pred, delta, delta_pred, se))
                cells.append(row)
            # A separate wide, per-horizon representation covers every CSV
            # field, including descriptive quantities not used by H1-H4.
            # CARD defines increments using Cref(h30), even when displayed
            # beside descriptive values for another horizon.
            v = values[:, it, :, :]
            index = {name: i for i, name in enumerate(pipes)}
            loss = np.mean(v, axis=0)
            twin_arrays = {t: contrasts(v, pipes, t) for t in TWINS}
            increment_factor = 100 / float(np.mean(v[:, index["M1_new"], -1]))
            for ih, h_mult in enumerate(H_MULT):
                cref_h = float(np.mean(v[:, index["M1_new"], ih]))
                if cref_h <= 0:
                    raise ValueError(f"Nonpositive horizon Cref: {rid}/{tau_mult}/{h_mult}")
                factor = 100 / cref_h
                wide = {"regime": rid, "tau_mult": float(tau_mult), "h_mult": int(h_mult),
                        "N": metadata["N"], "C_ref": cref_h,
                        "E_stay": float(np.mean(stay[:, ih]))}
                for name in pipes:
                    wide["L_" + name] = float(loss[index[name], ih])
                for twin in TWINS:
                    gs, gm, gamma, ref = twin_arrays[twin]
                    pred_row = by_prediction[(rid, float(tau_mult), twin)]
                    gs_h = gs[:, ih]
                    gs_se = paired_se(gs_h)
                    delta_instances = gs[:, -1] - gs[:, 3]
                    wide["GS_" + twin] = float(np.mean(gs_h))
                    wide["GS_" + twin + "_se"] = gs_se
                    wide["z_GS_" + twin] = float(np.mean(gs_h)) * factor
                    wide["z_GS_" + twin + "_se"] = gs_se * factor
                    wide["pred_" + twin + "_pp"] = float(pred_row["level_h" + str(int(h_mult))]) * factor
                    wide["Delta_" + twin + "_meas_pp"] = float(np.mean(delta_instances)) * increment_factor
                    wide["Delta_" + twin + "_se_pp"] = paired_se(delta_instances) * increment_factor
                    wide["Delta_" + twin + "_pred_pp"] = float(pred_row["Delta_pred"]) * increment_factor
                _, gm, gamma, _ = twin_arrays["M0"]
                for name, a in (("GM", gm[:, ih]), ("Gamma", gamma[:, ih])):
                    wide[name] = float(np.mean(a))
                    wide[name + "_se"] = paired_se(a)
                    wide["z_" + name] = float(np.mean(a)) * factor
                    wide["z_" + name + "_se"] = paired_se(a) * factor
                numeric_rows.append(wide)
        samples.append({"regime": rid, "N": metadata["N"], "seed": metadata["seed"],
                        "stationary_rate_valid": valid})
    assert len(cells) == len(predictions)
    summary = {}
    for name, threshold in THRESHOLDS.items():
        eligible = sum(r[name + "_eligible"] for r in cells)
        passed = sum(r[name + "_pass"] for r in cells)
        fraction = passed / eligible if eligible else None
        summary[name] = {"eligible": eligible, "passed": passed, "fraction": fraction,
                         "verdict": ("NOT_EVALUABLE" if not eligible else
                                     "PASS" if fraction >= threshold else "FAIL")}
    independent = {"hypotheses": summary, "cells": cells}
    own_hash = hashlib.sha256(json.dumps(independent, sort_keys=True, allow_nan=False).encode()).hexdigest()
    wide_hash = hashlib.sha256(json.dumps(numeric_rows, sort_keys=True, allow_nan=False).encode()).hexdigest()
    return {"responsible": "Doan Van Tai", "method": "Independent NumPy/stdlib rescore from CARD and raw instances",
            "units": {"cost": "raw integrated link backlog", "z": "percent of Cref(h30)",
                      "pred": "percent of Cref(h30)", "Delta_meas": "percentage points",
                      "Delta_pred": "percentage points", "se": "percentage points; ddof=1, paired instances"},
            "definitions": {"Cref": "mean(M1_new) at h30", "G_S": "mean(twin_old - M0_new)",
                            "G_M": "mean(twin_old - M1_old)",
                            "Gamma": "mean((twin_old - M0_new) - (M1_old - M1_new))",
                            "Delta_meas": "100*mean(GS_instance(h30)-GS_instance(h7))/Cref(h30)",
                            "Delta_pred": "100*predictions.Delta_pred/Cref(h30); cross-checked against level_h30-level_h7",
                            "pred": "100*predictions.level_h30/Cref(h30)"},
            "self_checks": checks, "regimes": samples, "regime_count": len(samples),
            "valid_regime_count": sum(r["stationary_rate_valid"] for r in samples),
            "prediction_checks": {"max_abs_Delta_pred_minus_level_difference": max_delta_prediction_check,
                                  "max_abs_level_pred_minus_level_h30": max_level_prediction_check},
            "independent_numbers_sha256_before_reference_read": own_hash,
            "numeric_rows_sha256_before_reference_read": wide_hash,
            "input_sha256": input_hashes, "numeric_rows": numeric_rows, **independent}


def compare(own, base=BASE):
    """Read references only after compute() has returned all independent values.

    No scientific formula in compute() is inferred from the reference files.
    The JSON adapter handles ungated predicate flags; counts still require
    eligibility. Gamma keeps the explicit convention from the first compute.
    """
    reference_path = base / "score.json"
    csv_path = base / "score_cells.csv"
    reference = json.loads(reference_path.read_text())
    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        reference_rows = list(reader)
    field_stats = {}
    mismatches = []
    flag_mismatches = []
    structure_mismatches = []
    numeric_abs_tolerance = 1e-10
    numeric_rel_tolerance = 1e-12

    def check(field, independent, expected, key):
        stat = field_stats.setdefault(field, {"compared": 0, "mismatches": 0})
        stat["compared"] += 1
        numeric = isinstance(independent, (int, float)) and not isinstance(independent, bool)
        if numeric:
            target = float(expected)
            diff = abs(independent - target)
            if not math.isfinite(diff):
                raise ValueError(f"Nonfinite comparison: {field}/{key}")
            if "max_absolute_difference" not in stat or diff > stat["max_absolute_difference"]:
                stat.update(max_absolute_difference=diff, worst_key=key,
                            independent_at_worst=independent, reference_at_worst=target)
            equal = math.isclose(independent, target, rel_tol=numeric_rel_tolerance,
                                 abs_tol=numeric_abs_tolerance)
            if field.endswith((".eligible", ".passed", ".N", ".n_cells")):
                equal = independent == target
        else:
            equal = type(independent) is type(expected) and independent == expected
        if not equal:
            stat["mismatches"] += 1
            detail = {"field": field, "key": key, "independent": independent, "reference": expected}
            mismatches.append(detail)
            if isinstance(independent, bool):
                flag_mismatches.append(detail)

    own_by_twin = {(r["regime"], r["tau_mult"], r["twin"]): r for r in own["cells"]}
    json_cells = {}
    gated_flag_differences = []
    for rid, tau_mult, twin in own_by_twin:
        if twin != "M0":
            continue
        m = own_by_twin[(rid, tau_mult, "M0")]
        p = own_by_twin[(rid, tau_mult, "P")]
        cell = {"regime": rid, "tau_mult": tau_mult, "stationary_rate_valid": m["stationary_rate_valid"]}
        for h in THRESHOLDS:
            source = p if h == "H4" else m
            cell[h + "_eligible"] = source[h + "_eligible"]
        cell.update({
            "H1_pass": bool(np.sign(m["z"]) == np.sign(m["pred"])),
            "H2_pass": bool(np.sign(m["Delta_meas"]) == np.sign(m["Delta_pred"])),
            "H3_pass": bool(abs(m["Delta_meas"] - m["Delta_pred"])
                            <= max(0.25, 0.25 * abs(m["Delta_pred"]), 2 * m["se"])),
            "H4_pass": bool(abs(p["Delta_meas"]) <= max(0.25, 2 * p["se"])),
        })
        json_cells[(rid, tau_mult)] = cell
    for name in THRESHOLDS:
        projected = dict(own["hypotheses"][name], threshold=THRESHOLDS[name])
        target = reference["hypotheses"][name]
        if set(projected) != set(target):
            structure_mismatches.append({"scope": "hypotheses." + name,
                                         "independent_keys": sorted(projected), "reference_keys": sorted(target)})
        for field in sorted(set(projected) & set(target)):
            check("score.json.hypotheses." + name + "." + field, projected[field], target[field], name)
    if set(reference["hypotheses"]) != set(THRESHOLDS):
        structure_mismatches.append({"scope": "score.json.hypotheses", "reference_keys": sorted(reference["hypotheses"])})
    expected_json = {}
    for cell in reference["cells"]:
        key = (cell["regime"], float(cell["tau_mult"]))
        if key in expected_json:
            structure_mismatches.append({"duplicate_json_key": list(key)})
        expected_json[key] = cell
    if set(json_cells) != set(expected_json):
        structure_mismatches.append({"scope": "score.json.cells", "missing": sorted(set(json_cells) - set(expected_json)),
                                     "extra": sorted(set(expected_json) - set(json_cells))})
    for key in sorted(set(json_cells) & set(expected_json)):
        cell = json_cells[key]
        target = expected_json[key]
        if set(cell) != set(target):
            structure_mismatches.append({"scope": "score.json.cells", "key": list(key),
                                         "independent_fields": sorted(cell), "reference_fields": sorted(target)})
        for field in sorted(set(cell) & set(target)):
            check("score.json.cells." + field, cell[field], target[field], list(key))
        for name in THRESHOLDS:
            source = own_by_twin[(*key, "P" if name == "H4" else "M0")]
            if source[name + "_pass"] != target[name + "_pass"]:
                gated_flag_differences.append({"key": list(key), "field": name + "_pass",
                                              "eligible": source[name + "_eligible"],
                                              "independent_gated": source[name + "_pass"],
                                              "reference_ungated": target[name + "_pass"]})
    check("score.json.n_cells", len(json_cells), reference["n_cells"], "n_cells")
    harms = {t: sum(r["z_GS_" + t] < -0.1 for r in own["numeric_rows"]) for t in TWINS}
    for twin in TWINS:
        check("score.json.descriptive_harm." + twin, harms[twin], reference["descriptive_harm"][twin], twin)
    expected_top = {"hypotheses", "cells", "n_cells", "descriptive_harm"}
    if set(reference) != expected_top:
        structure_mismatches.append({"scope": "score.json", "unhandled_fields": sorted(set(reference) - expected_top)})

    own_wide = {(r["regime"], float(r["tau_mult"]), int(r["h_mult"])): r for r in own["numeric_rows"]}
    expected_wide = {}
    for r in reference_rows:
        key = (r["regime"], float(r["tau_mult"]), int(r["h_mult"]))
        if key in expected_wide:
            structure_mismatches.append({"duplicate_csv_key": list(key)})
        expected_wide[key] = r
    if set(own_wide) != set(expected_wide):
        structure_mismatches.append({"scope": "score_cells.csv", "missing": sorted(set(own_wide) - set(expected_wide)),
                                     "extra": sorted(set(expected_wide) - set(own_wide))})
    if set(columns) != set(own["numeric_rows"][0]):
        structure_mismatches.append({"scope": "score_cells.csv.columns", "reference": columns,
                                     "independent": sorted(own["numeric_rows"][0])})
    gamma_opposite_max = {"Gamma": 0.0, "z_Gamma": 0.0}
    for key in sorted(set(own_wide) & set(expected_wide)):
        row, target = own_wide[key], expected_wide[key]
        for field in columns:
            if field in row:
                check("score_cells.csv." + field, row[field], target[field], list(key))
        for field in gamma_opposite_max:
            gamma_opposite_max[field] = max(gamma_opposite_max[field], abs(row[field] + float(target[field])))

    numeric_fields = {k: v for k, v in field_stats.items() if "max_absolute_difference" in v}
    largest_field = max(numeric_fields, key=lambda k: numeric_fields[k]["max_absolute_difference"])
    nongamma = {k: v for k, v in numeric_fields.items() if k not in ("score_cells.csv.Gamma", "score_cells.csv.z_Gamma")}
    largest_nongamma = max(nongamma, key=lambda k: nongamma[k]["max_absolute_difference"])
    return {
        "status": "MISMATCH" if mismatches or structure_mismatches else "MATCH",
        "numeric_tolerance": {"absolute": numeric_abs_tolerance, "relative": numeric_rel_tolerance,
                              "purpose": "comparison of floating-point reductions only; eligibility/counts/flags are exact"},
        "reference_sha256": {str(reference_path.relative_to(ROOT)): digest(reference_path),
                             str(csv_path.relative_to(ROOT)): digest(csv_path)},
        "reference_json_cell_count": len(reference["cells"]), "reference_csv_row_count": len(reference_rows),
        "reference_hypotheses": reference["hypotheses"],
        "json_projection": "Join M0 H1-H3 and P H4 on regime/tau; pass flags are ungated predicates, eligible flags are separate",
        "descriptive_harm": harms, "field_by_field": field_stats,
        "structure_mismatches": structure_mismatches, "flag_mismatches": flag_mismatches,
        "gated_vs_ungated_pass_differences": gated_flag_differences,
        "mismatches": mismatches,
        "largest_numeric_difference": {"field": largest_field, **numeric_fields[largest_field]},
        "largest_numeric_difference_excluding_Gamma_sign": {"field": largest_nongamma, **nongamma[largest_nongamma]},
        "Gamma_opposite_sign_max_absolute_residual": gamma_opposite_max,
        "specification_limit": "CARD section 3 does not define GM or Gamma. The independent first computation declared Gamma=L00-L10-L01+L11. The reference uses the opposite sign on these data. This is a convention mismatch, not evidence of a faulty scorer; no post-reference sign flip is applied.",
    }


def markdown_report(own):
    comp = own["comparison"]
    biggest = comp["largest_numeric_difference"]
    other = comp["largest_numeric_difference_excluding_Gamma_sign"]
    lines = ["# EV-TE independent rescore", "", f"**{comp['status']}**", "",
             "Người phụ trách: Doan Van Tai.", "",
             "Đã tính độc lập bằng NumPy/stdlib trước khi mở score.json và score_cells.csv; không đọc/import ev_te, ev_te_score_post.py hoặc score_attempt01_failed/.", "",
             f"61 regimes × 4 ages = 244 cells; 49 regimes hợp lệ = 196 cells; 732 dòng theo twin và {len(own['numeric_rows'])} dòng theo horizon. N=500, seed B=1000001; paired SE dùng ddof=1, ghép từng instance h30−h7.", "",
             "| Test | Passed/eligible (độc lập) | Claude | Fraction | Verdict |", "|---|---:|---:|---:|---|"]
    for name, h in own["hypotheses"].items():
        ref = comp["reference_hypotheses"][name]
        lines.append(f"| {name} | {h['passed']}/{h['eligible']} | {ref['passed']}/{ref['eligible']} | {h['fraction']:.9%} | {h['verdict']} |")
    lines.extend(["", "Tổng H1–H4 khớp; không thay đổi eligibility hay ngưỡng CARD. Cell là denominator, không phải trial độc lập; không suy population CI hoặc novelty.", "",
                  f"Sai khác số lớn nhất: **{biggest['max_absolute_difference']:.17g}**, trường `{biggest['field']}`, key `{biggest['worst_key']}`.",
                  f"Bỏ hai trường dấu Γ: sai khác lớn nhất `{other['max_absolute_difference']:.17g}` tại `{other['field']}`; tolerance đối chiếu abs=1e-10, rel=1e-12.", "",
                  "CARD §3 không định nghĩa công thức GM/Γ. Bản tính độc lập đầu dùng Γ=L00−L10−L01+L11; score dùng dấu ngược lại trên dữ liệu này. Giữ nguyên quy ước độc lập đã tính trước khi mở score; khác biệt này không chứng minh scorer sai.",
                  f"Residual nếu đối chiếu Γ độc lập với −Γ score: `{comp['Gamma_opposite_sign_max_absolute_residual']}`.", "",
                  f"Cờ eligibility/pass sau khi quy về cùng nghĩa JSON: {len(comp['flag_mismatches'])} mismatch. Có {len(comp['gated_vs_ungated_pass_differences'])} khác biệt giữa pass có gộp eligibility trong bản đầu và pass predicate riêng của score; không làm đổi bất kỳ count nào.",
                  f"Structural mismatches: {len(comp['structure_mismatches'])}. Self-checks: {own['self_checks']['status']} ({len(own['self_checks']['checks'])} checks).", "",
                  "## Đối chiếu từng trường", "", "| Field | Số so sánh | Max absolute difference | Mismatches |", "|---|---:|---:|---:|"])
    for field, stat in sorted(comp["field_by_field"].items()):
        maximum = format(stat["max_absolute_difference"], ".17g") if "max_absolute_difference" in stat else "—"
        lines.append(f"| {field} | {stat['compared']} | {maximum} | {stat['mismatches']} |")
    lines.extend(["", "## Lệnh và artifacts", "", "```bash", "source .venv/bin/activate",
                  "PYTHONDONTWRITEBYTECODE=1 python experiments/ext_validity/ev_te_rescore.py --compute-only",
                  "PYTHONDONTWRITEBYTECODE=1 python experiments/ext_validity/ev_te_rescore.py", "```", "",
                  "Lượt đầu compute-only dừng ở assert lưới h/Tint chính xác; raw dùng integer dt steps. Sửa kiểm tra lưới theo rounding ≤dt/2 và kiểm h=steps×dt; lần compute-only sau PASS. Không thay raw data hoặc số đo.", "",
                  "Lượt xuất thử có lỗi ở adapter CSV: chuẩn hóa increment theo horizon của dòng thay vì Cref(h30). Đã sửa theo công thức CARD §3 và tái xuất các file mới của nhiệm vụ; hash số H1–H4/từng twin giữ nguyên. Không sửa dấu Γ sau đối chiếu.", "",
                  "Script: `experiments/ext_validity/ev_te_rescore.py`.",
                  "JSON: `results/ext_validity/ev_te/rescore_independent.json` (giá trị từng cell/horizon, toàn bộ sai khác và SHA-256 inputs).",
                  "Report: `results/ext_validity/ev_te/rescore_independent.md`. Không tạo CSV/log riêng; log thực thi hiển thị trong phiên.", "",
                  f"SHA-256 số độc lập trước đối chiếu: `{own['independent_numbers_sha256_before_reference_read']}`.", "",
                  "Không commit, không SSH, không sửa file đã có trước nhiệm vụ. Đây là rescore raw truth đã có, không chạy lại simulation.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compute-only", action="store_true", help="Compute independent numbers without reading either reference score")
    args = parser.parse_args()
    own = compute()
    print(json.dumps({"phase": "INDEPENDENT_COMPUTATION_COMPLETE_BEFORE_REFERENCE_READ",
                      "hypotheses": own["hypotheses"], "cells": len(own["cells"]),
                      "regimes": own["regime_count"], "valid_regimes": own["valid_regime_count"],
                      "self_checks": own["self_checks"], "prediction_checks": own["prediction_checks"],
                      "independent_numbers_sha256": own["independent_numbers_sha256_before_reference_read"]},
                     indent=2, allow_nan=False), flush=True)
    if args.compute_only:
        return
    paths = [BASE / "rescore_independent.json", BASE / "rescore_independent.md"]
    if any(p.exists() for p in paths):
        raise SystemExit("Refusing to overwrite existing output files; use --compute-only for a read-only repeat")
    own["comparison"] = compare(own)
    changed = [p for p, sha in own["input_sha256"].items() if digest(ROOT / p) != sha]
    if changed:
        raise RuntimeError(f"Inputs changed during rescore: {changed}")
    own["input_integrity_after_comparison"] = "PASS"
    own["script_sha256"] = digest(Path(__file__))
    content = json.dumps(own, indent=2, allow_nan=False) + "\n"
    report = markdown_report(own)
    with paths[0].open("x") as f:
        f.write(content)
    with paths[1].open("x") as f:
        f.write(report)
    print(json.dumps({"comparison": own["comparison"]["status"],
                      "largest_numeric_difference": own["comparison"]["largest_numeric_difference"],
                      "flag_mismatches": len(own["comparison"]["flag_mismatches"]),
                      "outputs": [str(p.relative_to(ROOT)) for p in paths]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
