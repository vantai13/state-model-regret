import json
import statistics
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent


def load():
    receipt = json.loads((OUT / "truth_receipt.json").read_text())
    predictions = json.loads((OUT / "predictions.json").read_text())
    raws = [json.loads((OUT / "raw" / (name + ".json")).read_text()) for name in predictions["truth_population"]]
    return receipt, predictions, raws


def rows_of(raws, **match):
    return [r for raw in raws for r in raw["rows"] if all(r.get(k) == v for k, v in match.items())]


def verdicts(raws):
    out = {}
    controls = [c for raw in raws for c in raw["controls"]]
    out["H-PL1"] = dict(passed=sum(bool(c["passed"]) for c in controls), total=len(controls))
    truth_m0 = {r["regime"]: r for r in rows_of(raws, tau_T_int=1, h_T_int=30, kernel="true_kernel", variant="M0")}
    harm = sorted(k for k, r in truth_m0.items() if r["G_S_pct_C_ref"] < -0.1)
    out["n_true"] = len(harm)
    by_length = {}
    for length in (30, 100, 300, 1000):
        kept = 0
        for name in harm:
            values = [r["G_S_pct_C_ref"] for r in rows_of(raws, regime=name, tau_T_int=1, h_T_int=30,
                                                          kernel="learned", variant="M0", L_T_int=length)]
            assert len(values) == 5
            kept += statistics.median(values) < -0.1
        by_length[length] = kept
    out["H-PL2_retained_by_L"] = by_length
    out["H-PL2"] = "NOT_EVALUABLE" if len(harm) < 10 else ("PASS" if by_length[100] >= 0.8 * len(harm) else "FAIL")
    hybrid_true = rows_of(raws, tau_T_int=1, h_T_int=30, kernel="true_kernel", variant="hybrid_true_s")
    base = sum(r["both_side_regret_pct_C_ref"] <= 0.5 for r in hybrid_true)
    learned_pass = 0
    for raw in raws:
        values = [r["both_side_regret_pct_C_ref"] for r in rows_of([raw], tau_T_int=1, h_T_int=30,
                                                                   kernel="learned", variant="hybrid_true_s", L_T_int=100)]
        assert len(values) == 5
        learned_pass += all(v <= 0.5 for v in values)
    out["H-PL3"] = dict(true_kernel=base, learned=learned_pass,
                        verdict="PASS" if learned_pass >= base - 2 else "FAIL")
    q2 = [row for raw in raws for q in raw["Q2"] if q["tau_T_int"] == 1 for row in q.get("rows", []) if row["twin"] == "T4"]
    mixed = [r for r in q2 if r["classification"] == "mixed_sign" and abs(r["sigma"]) > 1e-9]
    hits = sum(abs(r["slope_measured"] - r["sigma"]) / abs(r["sigma"]) <= 0.05 for r in mixed)
    out["H-T4a"] = dict(eligible=len(mixed), passed=hits,
                        verdict="NOT_EVALUABLE" if len(mixed) < 3 else ("PASS" if hits >= 0.9 * len(mixed) else "FAIL"))
    same = [r for r in q2 if r["classification"] == "same_sign"]
    zero = sum(abs(r["G_S_packet_s"]) <= 1e-9 * r["C_ref"] for r in same)
    out["H-T4b"] = dict(eligible=len(same), passed=zero,
                        verdict="NOT_EVALUABLE" if len(same) < 3 else ("PASS" if zero == len(same) else "FAIL"))
    mixed_zero_sigma = [r for r in q2 if r["classification"] == "mixed_sign" and abs(r["sigma"]) <= 1e-9]
    out["T4_mixed_sigma_zero"] = len(mixed_zero_sigma)
    out["T4_harm_mixed"] = sum(r["G_S_pct_C_ref"] < -0.1 for r in mixed)
    return out


def descriptive(raws):
    out = {}
    for variant in ("M0", "hybrid_true_s"):
        for kernel, length in (("true_kernel", None), ("plugin", None), ("learned", 100)):
            values = []
            for raw in raws:
                rows = rows_of([raw], tau_T_int=1, h_T_int=30, kernel=kernel, variant=variant)
                if length is not None:
                    rows = [r for r in rows if r["L_T_int"] == length]
                key = "G_S_pct_C_ref" if variant == "M0" else "both_side_regret_pct_C_ref"
                values.append(statistics.median([r[key] for r in rows]))
            out[f"{variant}/{kernel}/median_over_regimes"] = statistics.median(values)
    return out


if __name__ == "__main__":
    receipt, predictions, raws = load()
    result = dict(receipt_status=receipt["status"], population=len(raws), verdicts=verdicts(raws),
                  descriptive=descriptive(raws))
    scores = OUT / "scores.json"
    if scores.exists():
        locked = json.loads(scores.read_text())["tests"]
        mine = result["verdicts"]
        comparison = {
            "H-PL1": locked["H-PL1"]["passed"] == mine["H-PL1"]["passed"],
            "H-PL2": locked["H-PL2"]["verdict"] == mine["H-PL2"] and locked["H-PL2"]["retained"] == mine["H-PL2_retained_by_L"][100]
                     and locked["H-PL2"]["n_true"] == mine["n_true"],
            "H-PL3": locked["H-PL3"]["verdict"] == mine["H-PL3"]["verdict"] and locked["H-PL3"]["learned_pass"] == mine["H-PL3"]["learned"],
            "H-T4a": locked["H-T4a"]["verdict"] == mine["H-T4a"]["verdict"] and locked["H-T4a"]["passed"] == mine["H-T4a"]["passed"],
            "H-T4b": locked["H-T4b"]["verdict"] == mine["H-T4b"]["verdict"] and locked["H-T4b"]["passed"] == mine["H-T4b"]["passed"],
        }
        result["comparison_with_locked_scorer"] = comparison
        result["MATCH"] = all(comparison.values())
    text = json.dumps(result, indent=2)
    (OUT / "rescore_independent.json").write_text(text + "\n")
    print(text)
    sys.exit(0 if result.get("MATCH", True) else 1)
