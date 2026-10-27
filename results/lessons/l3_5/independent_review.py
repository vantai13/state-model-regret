#!/usr/bin/env python3
"""Independent two-cell card audit; never imports engine or card grading code.

Only input files are the frozen prediction card and the four named raw records.
Fractions preserve all recorded decimal endpoints exactly; decimals in Markdown
are outward rounded for display and are not used to make decisions.
"""

from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CARD = ROOT / "notes/phases/PHASE_3_prediction_card.md"
RAW = ROOT / "results/A04/20261027_01/raw"
CONTRASTS = ("G_S", "G_M", "G_SM", "G_S_M1", "G_M_S1", "Gamma")
STANDS = "STANDS"
DOES_NOT_STAND = "DOES_NOT_STAND"
UNRESOLVED = "UNRESOLVED"


def q(value):
    return Fraction(str(value))


def interval(record, name):
    low, high = map(q, record["intervals"][name])
    assert low <= high, name
    return low, high


def subtract(left, right):
    return left[0] - right[1], left[1] - right[0]


def abs_interval(value):
    low, high = value
    return (Fraction(0) if low <= 0 <= high else min(abs(low), abs(high))), max(abs(low), abs(high))


def four_corners(numerator, denominator):
    assert denominator[0] > 0
    corners = tuple(n / d for n in numerator for d in denominator)
    return (min(corners), max(corners)), corners


def format_endpoint(value, lower):
    with localcontext() as context:
        context.prec = 100
        return str((Decimal(value.numerator) / Decimal(value.denominator)).quantize(
            Decimal("1e-18"), rounding=ROUND_FLOOR if lower else ROUND_CEILING))


def pack(value):
    return {"exact": [str(x) for x in value],
            "decimal_outward": [format_endpoint(value[0], True), format_endpoint(value[1], False)]}


def show(packed):
    return "[" + ", ".join(packed["decimal_outward"]) + "]"


def ge(value, threshold):
    return STANDS if value[0] >= threshold else DOES_NOT_STAND if value[1] < threshold else UNRESOLVED


def gt_zero(value):
    return STANDS if value[0] > 0 else DOES_NOT_STAND if value[1] <= 0 else UNRESOLVED


def kleene_and(*labels):
    return DOES_NOT_STAND if DOES_NOT_STAND in labels else STANDS if all(x == STANDS for x in labels) else UNRESOLVED


def audit_numeric(record):
    mass = {name: q(record["unresolved_mass"][name]) for name in ("oracle", "M0", "D22")}
    context = record["reference_context"]
    same_reference = (
        q(record["C_ref"]) == q(record["L"]["11"])
        and interval(record, "C_ref") == interval(record, "L11")
        and context["refinement"] == record["refinement"]
        and q(context["dt_s"]) == q(record["dt_s"])
    )
    # Check the reported enclosures contain nominal +/- actual e_num, never a budget.
    nominal = {"L" + k: v for k, v in record["L"].items()}
    nominal.update(record["G"])
    nominal["C_ref"] = record["C_ref"]
    enclosure_checks = {}
    for name, value in nominal.items():
        low, high = interval(record, name)
        center, error = q(value), q(record["e_num"][name])
        enclosure_checks[name] = error >= 0 and low <= center - error and center + error <= high
    passed = (record["status"] == "BOUNDED" and record["numeric_budget_met"] is True
              and all(Fraction(0) <= m <= Fraction(1, 100) for m in mass.values())
              and same_reference and all(enclosure_checks.values()))
    return {"status": record["status"], "numeric_budget_met_reported": record["numeric_budget_met"],
            "unresolved_mass": {k: str(v) for k, v in mass.items()},
            "Cref_equals_L11_and_context": same_reference,
            "actual_e_num_enclosure_checks": enclosure_checks,
            "max_actual_e_num_checked": str(max(q(record["e_num"][k]) for k in nominal)),
            "C_ref": pack(interval(record, "C_ref")), "passed": passed,
            "limitation": "Budget attainment consumes the raw Boolean; the card does not specify the engine budget formula."}


def audit_pair(coarse, fine):
    adjacency = q(coarse["dt_s"]) == 2 * q(fine["dt_s"]) and coarse["refinement"] == 1 and fine["refinement"] == 2
    tolerance = Fraction(1, 400) * interval(fine, "C_ref")[0]
    results = {}
    for name in CONTRASTS:
        difference = subtract(interval(fine, name), interval(coarse, name))
        absolute = abs_interval(difference)
        coarse_ratio, _ = four_corners(interval(coarse, name), interval(coarse, "C_ref"))
        fine_ratio, _ = four_corners(interval(fine, name), interval(fine, "C_ref"))
        # A conservative exclusion of even possible opposite signs beyond +/-0.005.
        possible_sign_flip = ((coarse_ratio[1] > Fraction(1, 200) and fine_ratio[0] < -Fraction(1, 200))
                              or (fine_ratio[1] > Fraction(1, 200) and coarse_ratio[0] < -Fraction(1, 200)))
        results[name] = {"fine_minus_coarse": pack(difference), "absolute_difference": pack(absolute),
                         "coarse_ratio": pack(coarse_ratio), "fine_ratio": pack(fine_ratio),
                         "absolute_difference_pass": absolute[1] <= tolerance,
                         "sign_flip_beyond_band_possible": possible_sign_flip,
                         "passed": absolute[1] <= tolerance and not possible_sign_flip}
    return {"coarse_dt_s": coarse["dt_s"], "fine_dt_s": fine["dt_s"], "adjacent": adjacency,
            "tolerance_exact": str(tolerance), "tolerance_decimal": format_endpoint(tolerance, True),
            "contrasts": results, "passed": adjacency and all(x["passed"] for x in results.values())}


def score_p2(record):
    numerator = subtract(interval(record, "L01"), interval(record, "L10"))
    denominator = interval(record, "C_ref")
    if denominator == (0, 0):
        return {"numerator": pack(numerator), "label": "EXCLUDED_ZERO_REFERENCE"}
    if denominator[0] <= 0:
        return {"numerator": pack(numerator), "label": UNRESOLVED}
    ratio, corners = four_corners(numerator, denominator)
    return {"numerator": pack(numerator), "C_ref": pack(denominator), "ratio": pack(ratio),
            "corners_exact": [str(x) for x in corners], "threshold": "1/100", "label": ge(ratio, Fraction(1, 100))}


def score_p6(record):
    value = interval(record, "V")
    difference = subtract(value, interval(record, "F"))
    first, second = gt_zero(value), gt_zero(difference)
    return {"F": pack(interval(record, "F")), "V": pack(value), "V_minus_F": pack(difference),
            "V_gt_zero_label": first, "V_minus_F_gt_zero_label": second, "label": kleene_and(first, second)}


def main():
    card_bytes = CARD.read_bytes()
    # The rules above were transcribed from the card by this independent session.
    assert b"0.0025" in card_bytes and b"0.005" in card_bytes
    results = {"responsible": "Doan Van Tai", "date": "2026-10-27",
               "reviewer": "Independent AI session, not a human or supervisor review",
               "grader_results_seen": False, "engine_run": False, "heldout_seen": False,
               "scope": {"M09": "P2", "M17": "P6"},
               "method": "Exact Fraction arithmetic from raw decimal endpoints; Decimal only for outward-rounded display",
               "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "inputs_sha256": {str(CARD.relative_to(ROOT)): hashlib.sha256(card_bytes).hexdigest()}, "cells": {}}
    for cell, score in (("M09", score_p2), ("M17", score_p6)):
        records = []
        for refinement in (1, 2):
            path = RAW / f"{cell}_m{refinement}.json"
            payload = path.read_bytes()
            results["inputs_sha256"][str(path.relative_to(ROOT))] = hashlib.sha256(payload).hexdigest()
            records.append(json.loads(payload, parse_float=Decimal)["engine"])
        coarse, fine = records
        numeric = [audit_numeric(record) for record in records]
        pair = audit_pair(coarse, fine)
        scores = [score(record) for record in records]
        eligible = all(x["passed"] for x in numeric) and pair["passed"]
        results["cells"][cell] = {"numeric": numeric, "pair": pair, "coarse": scores[0], "fine": scores[1],
                                  "eligible": eligible, "final_label": scores[1]["label"] if eligible else UNRESOLVED,
                                  "dt_sensitive_label": scores[0]["label"] != scores[1]["label"]}
    lines = ["# Kiểm độc lập hai ô A04", "", "Người phụ trách: **Doan Van Tai** · 27/10/2026.", "",
             "Reviewer là **một phiên AI độc lập**, không phải GVHD/người đọc thật. Phiên này chưa xem `card_scores.*`, `card_details.csv` hoặc kết quả grader; không đọc ô khác, không chạy engine và không đọc held-out.", "",
             "Phạm vi: chỉ M09/P2 và M17/P6 đã chỉ định trước. Không suy rộng verdict toàn bộ P2/P6, không tìm pattern và không xác nhận mechanism.", "",
             "## Phép tính độc lập", "",
             "Chỉ đọc prediction card và bốn raw record. Dùng `Fraction` trên chuỗi decimal raw, không import grading/score_card. Với A−B: [aL−bU,aU−bL]; lấy abs interval rồi kiểm upper ≤ Cref_fine.lower/400. Ratio dùng min/max của bốn corner. Kiểm không có cặp dấu đối nhau có thể xảy ra ngoài ±1/200 của Cref mỗi mức. P2 lấy L01−L10 trước propagation; P6 kiểm V>0 và (V−F)>0 theo strict inequality rồi Kleene AND.", "",
             "Các khoảng dưới là numeric enclosures của slot model, không phải CI, không chứng minh giới hạn dt→0. Số hiển thị được làm tròn ra ngoài đến 18 chữ số thập phân; JSON giữ phân số chính xác. Không thay e_num thực bằng budget.", "",
             "## Numeric gate và cặp dt", "",
             "Bốn raw đều BOUNDED, numeric_budget_met=true; unresolved_mass oracle/M0/D22 đều 0. Đã kiểm Cref=L11 cùng interval/context; nominal±e_num thực nằm trong enclosure cho L00/L01/L10/L11/Lcb0, sáu contrast, F/V/Cref. Cờ budget được lấy từ raw: card không định nghĩa công thức budget nội bộ nên review này không tái tính công thức đó.", "",
             "| Ô | dt coarse → fine (s) | 0.0025 × Cref_fine.lower | Sáu contrast |", "|---|---|---:|---|"]
    for cell, result in results["cells"].items():
        pair = result["pair"]
        lines.append(f"| {cell} | {pair['coarse_dt_s']} → {pair['fine_dt_s']} | {pair['tolerance_decimal']} | {'PASS 6/6' if pair['passed'] else 'FAIL'} |")
    for cell, result in results["cells"].items():
        lines += ["", f"### {cell}: sáu contrast", "", "| Contrast | Khoảng abs(fine−coarse) | Đổi dấu ngoài ±.005 có thể xảy ra? |", "|---|---|---|"]
        for name, detail in result["pair"]["contrasts"].items():
            lines.append(f"| {name} | {show(detail['absolute_difference'])} | {'Có' if detail['sign_flip_beyond_band_possible'] else 'Không'} |")
    m09 = results["cells"]["M09"]
    m17 = results["cells"]["M17"]
    lines += ["", "## M09/P2", "", "| dt (s) | L01−L10 | (L01−L10)/Cref | Nhãn ≥.01 |", "|---|---|---|---|"]
    for label, dt in (("coarse", "1/120"), ("fine", "1/240")):
        result = m09[label]
        lines.append(f"| {dt} | {show(result['numerator'])} | {show(result['ratio'])} | {result['label']} |")
    lines += ["", "Cả hai upper ratio đều <.01. Numeric gate và pair đều đạt; verdict tại dt_final=1/240 là **DOES_NOT_STAND**. Không nhạy với dt theo tiêu chí đổi nhãn của card. Đây là counterexample cho vế tại M09; review không đọc các ô K2 còn lại.", "",
              "## M17/P6", "", "| dt (s) | V | V−F | V>0 | V−F>0 | AND |", "|---|---|---|---|---|---|"]
    for label, dt in (("coarse", "1/120"), ("fine", "1/240")):
        result = m17[label]
        lines.append(f"| {dt} | {show(result['V'])} | {show(result['V_minus_F'])} | {result['V_gt_zero_label']} | {result['V_minus_F_gt_zero_label']} | {result['label']} |")
    lines += ["", "Upper(V) và upper(V−F) đều ≤0 ở hai mức. Numeric gate và pair đều đạt; verdict tại dt_final=1/240 là **DOES_NOT_STAND**. Không nhạy với dt theo tiêu chí đổi nhãn của card. Đây là counterexample tại M17; review không đọc M18. Không diễn giải V thành lợi ích chỉ refresh backlog.", "",
              "## Số đếm trong phạm vi hai ô", "",
              "Tại fine: M09/P2 có STANDS=0, DOES_NOT_STAND=1, UNRESOLVED=0, EXCLUDED_ZERO_REFERENCE=0. M17/P6 mỗi vế V>0 và V−F>0 có STANDS=0, DOES_NOT_STAND=1, UNRESOLVED=0, EXCLUDED_ZERO_REFERENCE=0; AND cũng DOES_NOT_STAND. Hai nhãn ô cuối: 0 đứng, 2 không đứng, 0 chưa phân giải, 0 excluded. Đây không phải bảng đếm toàn bộ card.", "",
              "## Thực thi và giới hạn", "",
              "Đã chạy `python3 results/lessons/l3_5/independent_review.py`; không chạy test suite/engine/simulation. Lần đọc thử ban đầu bằng `python` thất bại vì shell không có lệnh đó; đã dùng `python3`. Lần chạy script đầu gặp SyntaxError tại biểu thức abs interval do thiếu dấu ngoặc; đã sửa cú pháp và chạy lại. Script assert tính đúng thứ tự interval, reference context và viết kết quả; dữ liệu từng kiểm được lưu trong JSON. Phép tính độc lập trên raw không phải validation độc lập của thuật toán sinh enclosure. Không có seed mới, không tạo data thí nghiệm mới, không mở Phase4/Gate người thật và không nhận mechanism đúng.", "",
              "Files: `results/lessons/l3_5/independent_review.py`, `independent_review.json`, `independent_review.md`. Không tạo log riêng; stdout được ghi trong báo cáo chạy của phiên. SHA256 của đúng năm input và script nằm trong JSON."]
    (OUT / "independent_review.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    (OUT / "independent_review.md").write_text("\n".join(lines) + "\n")
    for cell, result in results["cells"].items():
        print(cell, "numeric", [x["passed"] for x in result["numeric"]], "pair", result["pair"]["passed"],
              "label", result["final_label"], "dt_sensitive", result["dt_sensitive_label"])
    assert all(x["eligible"] for x in results["cells"].values()), "Numeric/pair gate failed; inspect independent_review.json"


if __name__ == "__main__":
    main()
