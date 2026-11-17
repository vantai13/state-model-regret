"""Doan Van Tai — independent V7-1 AUC rescore from the saved cell table.

Only the standard library is used. Never imports the V7-1 analysis module.
Counts positive/negative comparisons using binary searches, not rank sums.
"""
import argparse
from bisect import bisect_left, bisect_right
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/"results/letter/v7_1"


def mann_whitney(labels, scores):
    if len(labels) != len(scores) or any(y not in (0, 1) for y in labels):
        raise ValueError("aligned binary labels required")
    if not all(math.isfinite(x) for x in scores):
        raise ValueError("finite scores required")
    negatives = sorted(x for y,x in zip(labels, scores) if y == 0)
    positives = [x for y,x in zip(labels, scores) if y == 1]
    if not positives or not negatives:
        return None
    # Integer twice-wins makes ties exact; divide once at the end.
    twice_wins = sum(bisect_left(negatives,x)+bisect_right(negatives,x) for x in positives)
    return twice_wins/(2*len(negatives)*len(positives))


def rescore(out=OUT):
    start, wall = time.process_time(), time.perf_counter()
    with (out/"cells.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    summary = json.loads((out/"summary.json").read_text())
    if Counter(r["dataset"] for r in rows) != {"CTMC":3255, "GEANT":612}:
        raise ValueError("incomplete population")
    comparisons = []
    for row in rows:
        label = int(max(float(row["regret_fresh_pct"]), float(row["regret_stale_pct"])) <= .5)
        if label != int(row["Y"]):
            raise ArithmeticError("Y differs from the saved both-side definition")
        h, s = float(row["h_s"]), abs(float(row["s_hat"]))
        for predictor, expected in (("P1", h/float(row["T_int_s"])),
                                    ("P2", h*s/float(row["Q90"])),
                                    ("P3", h*s/float(row["M_hat"]))):
            if not math.isclose(float(row[predictor]), expected, rel_tol=1e-14, abs_tol=0.):
                raise ArithmeticError(f"{predictor} formula mismatch")
    datasets = {}
    for name in ("CTMC", "GEANT"):
        group = [r for r in rows if r["dataset"] == name]
        labels = [int(r["Y"]) for r in group]
        values = {}
        for predictor in ("P1", "P2", "P3"):
            actual = mann_whitney(labels, [float(r[predictor]) for r in group])
            saved = summary["datasets"][name]["auc"][predictor]["value"]
            delta = abs(actual-saved)
            if delta > 1e-12:
                raise ArithmeticError(f"{name}/{predictor} AUC mismatch {delta}")
            comparisons.append(dict(dataset=name, predictor=predictor, recomputed=actual,
                                    saved=saved, absolute_difference=delta))
            values[predictor] = actual
        selected = [r for r in group if float(r["P2"]) >= 1.]
        hit = sum(int(r["Y"]) for r in selected)
        saved = summary["datasets"][name]["precision_P2_ge_1"]
        if (hit, len(selected)) != (saved["true_positive"], saved["selected"]):
            raise ArithmeticError("precision count mismatch")
        datasets[name] = dict(auc=values, Y1=sum(labels), cells=len(group),
                              precision_P2_ge_1=dict(hits=hit, selected=len(selected),
                                                    value=hit/len(selected) if selected else None))
    per_seed = {}
    for seed in ("3000001", "5000001"):
        group = [r for r in rows if r["seed"] == seed]
        values = {p:mann_whitney([int(r["Y"]) for r in group], [float(r[p]) for r in group])
                  for p in ("P1", "P2", "P3")}
        for p, value in values.items():
            delta = abs(value-summary["geant_by_seed"][seed]["auc"][p])
            if delta > 1e-12:
                raise ArithmeticError("per-seed AUC mismatch")
            comparisons.append(dict(dataset="GEANT:"+seed, predictor=p, recomputed=value,
                                    saved=summary["geant_by_seed"][seed]["auc"][p], absolute_difference=delta))
        per_seed[seed] = values
    verdict = "HOLDS" if all(d["auc"]["P2"] > d["auc"]["P1"] for d in datasets.values()) else "DOES_NOT_HOLD"
    if verdict != summary["verdict"]:
        raise ArithmeticError("card verdict mismatch")
    result = dict(owner="Doan Van Tai", status="PASS", verdict=verdict, datasets=datasets,
                  geant_by_seed=per_seed, comparisons=comparisons,
                  max_absolute_auc_difference=max(c["absolute_difference"] for c in comparisons),
                  tolerance=1e-12, method="standard-library binary searches of negatives; integer twice-wins for exact ties",
                  cells_sha256=hashlib.sha256((out/"cells.csv").read_bytes()).hexdigest(),
                  summary_sha256=hashlib.sha256((out/"summary.json").read_bytes()).hexdigest(),
                  scorer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  cpu_s=time.process_time()-start, wall_s=time.perf_counter()-wall)
    with (out/"rescore.json").open("x") as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    rescore(args.out)
