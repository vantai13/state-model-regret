"""Exact illustrative checks for L2.4; no grid/plant experiment.

Responsible: Doan Van Tai. Examples use declared artificial costs, not paper data.
"""
import csv
from fractions import Fraction as F
import hashlib
from itertools import product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/lessons/l2_4"


def action(costs):
    return int(costs[1] < costs[0])  # exact tie -> Stay


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    failures = legacy_failures = count = 0
    for jt, js, pt, ps in product(range(5), repeat=4):
        true, predicted = (jt, js), (pt, ps)
        delta = js - jt
        direct = true[action(predicted)] - min(true)
        identity = abs(delta) * int(action(predicted) != action(true))
        failures += direct != identity
        legacy_failures += direct != abs(delta) * int(delta * (ps - pt) < 0)
        count += 1
    assert count == 625 and failures == 0 and legacy_failures == 50

    true = (F(12), F(9))
    delay_rows = []
    for name, prediction in [("Twin1", (F(10), F(11))), ("Twin2", (F(16), F(13)))]:
        mae = sum(abs(a-b) for a, b in zip(true, prediction)) / 2
        regret = true[action(prediction)] - min(true)
        delay_rows.append(dict(twin=name, predicted_A=str(prediction[0]), predicted_B=str(prediction[1]),
                               mae=str(mae), action="B" if action(prediction) else "A", regret=str(regret), unit="ms"))
    assert [(r["mae"], r["regret"]) for r in delay_rows] == [("2", "3"), ("4", "0")]

    gaps = [-10, -1, 1, 10]
    actual = [int(d < 0) for d in gaps]  # positive class = beneficial Switch
    classification = []
    for name, chosen in [("X", [1, 0, 1, 0]), ("Y", [0, 1, 0, 1])]:
        tp = sum(a == p == 1 for a, p in zip(actual, chosen))
        fp = sum(a == 0 and p == 1 for a, p in zip(actual, chosen))
        fn = sum(a == 1 and p == 0 for a, p in zip(actual, chosen))
        tn = sum(a == p == 0 for a, p in zip(actual, chosen))
        precision, recall = F(tp, tp+fp), F(tp, tp+fn)
        total = sum(abs(d) for d, a, p in zip(gaps, actual, chosen) if a != p)
        classification.append(dict(twin=name, tp=tp, fp=fp, fn=fn, tn=tn,
                                   precision=str(precision), recall=str(recall),
                                   total_regret=str(total), mean_regret=str(F(total, len(gaps))), unit="packet*s"))
    assert all(r["precision"] == r["recall"] == "1/2" for r in classification)
    assert [r["mean_regret"] for r in classification] == ["1/2", "5"]
    result = dict(status="PASS", responsible="Doan Van Tai", scope="exact illustrative arithmetic; no Phase3 grid results",
                  seed=None, deterministic=True, source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  tie_cases=count, correct_identity_violations=failures,
                  strict_gap_product_failures=legacy_failures,
                  predicted_tie_counterexample=dict(true=[12, 9], predicted=[10, 10], regret=3, unit="ms"),
                  delay_examples=delay_rows, confusion_examples=classification, regret_ratio="10")
    (OUT / "metric_examples.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    for filename, rows in [("delay_examples.csv", delay_rows), ("confusion_examples.csv", classification)]:
        with (OUT / filename).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result


if __name__ == "__main__":
    run()
