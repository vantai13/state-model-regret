"""L2.7 Part A: exact teaching examples; no plant/grid simulation.

Responsible: Doan Van Tai. Fractions, no randomness or fitted parameters.
"""
from __future__ import annotations

import csv
import hashlib
import json
from fractions import Fraction as F
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/lessons/l2_7/part_a"


def oracle(costs):
    """Two equally likely futures; choose once, ties choose Stay."""
    means = [sum(row, F(0)) / 2 for row in costs]
    action = min(range(2), key=lambda a: means[a])
    rp = means[action]
    ws = sum((min(costs[a][w] for a in range(2)) for w in range(2)), F(0)) / 2
    return dict(action=["Stay", "Switch"][action], expected=means,
                RP=rp, WS=ws, future_EVPI=rp - ws)


def factorial(values):
    """Order 00,10,01,11; Gamma is negative of the cost interaction."""
    a, b, c, d = map(F, values)
    gs, gm = a - b, a - c
    gs1, gm1 = c - d, b - d
    predicted00 = b + c - d
    return dict(L00=a, L10=b, L01=c, L11=d, GS=gs, GM=gm, GSM=a-d,
                GSgivenM1=gs1, GMgivenS1=gm1, Gamma=gs1-gs,
                averaged_state_effect=(gs+gs1)/2,
                averaged_model_effect=(gm+gm1)/2,
                cost_interaction=d-b-c+a,
                additive_prediction_L00=predicted00,
                additive_prediction_error=predicted00-a)


def serial(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {k: serial(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [serial(v) for v in value]
    return value


def write_csv(name, rows):
    with (OUT / name).open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(serial(rows))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    checks = []

    def check(label, condition):
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    examples = {}
    oracle_rows = []
    for name, costs in [("lesson", ((2, 6), (4, 3))),
                        ("exercise", ((2, 6), (6, 3)))]:
        result = oracle(costs)
        examples[name] = dict(costs=costs, **result)
        for a, choice in enumerate(["Stay", "Switch"]):
            expected = result["expected"][a]
            avoidable = expected - result["RP"]
            hindsight = expected - result["WS"]
            check(f"{name}/{choice}: hindsight decomposition",
                  hindsight == avoidable + result["future_EVPI"])
            oracle_rows.append(dict(case=name, controller=choice, expected_cost=expected,
                                    RP=result["RP"], WS=result["WS"],
                                    avoidable_regret=avoidable, hindsight_gap=hindsight,
                                    future_EVPI=result["future_EVPI"]))
    check("lesson golden", examples["lesson"]["action"] == "Switch" and
          (examples["lesson"]["RP"], examples["lesson"]["WS"],
           examples["lesson"]["future_EVPI"]) == (F(7,2), F(5,2), F(1)))
    check("exercise golden", examples["exercise"]["action"] == "Stay" and
          (examples["exercise"]["RP"], examples["exercise"]["WS"],
           examples["exercise"]["future_EVPI"]) == (F(4), F(5,2), F(3,2)))

    frozen = ROOT / "results/lessons/l2_3/p11_toy.json"
    old = json.loads(frozen.read_text())["v1"]
    v1 = factorial([old["L"][key] for key in ["00", "10", "01", "11"]])
    regret = {key: F(old["L"][key]) - F(old["L"]["11"]) for key in old["L"]}
    check("V1 cost versus regret", regret == {"00": F(0), "10": F(1,4),
                                              "01": F(0), "11": F(0)})
    check("V1 contrasts match frozen evidence", all(v1[new] == F(old["con"][prev])
          for new, prev in [("GS","GS"),("GM","GM"),("GSM","GSM"),
                            ("Gamma","Gam"),("GSgivenM1","GSgM1"),
                            ("GMgivenS1","GMgS1")]))
    check("V1 additive error", v1["additive_prediction_L00"] == F(3,2)
          and v1["additive_prediction_error"] == F(1,4))
    check("V1 averaged effects", (v1["averaged_state_effect"],
          v1["averaged_model_effect"]) == (F(-1,8), F(1,8)))

    tables = {"V1": v1, "additive_exercise": factorial([4,3,2,1]),
              "same_OAT_Gamma0": factorial([F(3,2),F(3,2),F(5,4),F(5,4)]),
              "same_OAT_Gamma_negative": factorial([F(7,4),F(3,2),F(5,4),F(5,4)])}
    check("additive exercise", tables["additive_exercise"]["Gamma"] == 0
          and tables["additive_exercise"]["additive_prediction_error"] == 0)
    check("same three observed corners do not identify Gamma",
          len({tuple(t[k] for k in ["L10","L01","L11"]) for t in tables.values()
               if t is not tables["additive_exercise"]}) == 1 and
          {tables[k]["Gamma"] for k in ["V1","same_OAT_Gamma0",
              "same_OAT_Gamma_negative"]} == {F(1,4),F(0),F(-1,4)})

    factorial_sweep, oracle_sweep = [], []
    for i, values in enumerate(product(range(4), repeat=4)):
        t = factorial(values)
        assert t["Gamma"] == t["GMgivenS1"] - t["GM"]
        assert t["Gamma"] == t["GSM"] - t["GS"] - t["GM"]
        assert t["Gamma"] == -t["cost_interaction"] == t["additive_prediction_error"]
        factorial_sweep.append(dict(case=i, **t))
        costs = (values[:2], values[2:])
        o = oracle(costs)
        assert o["WS"] <= o["RP"] and o["future_EVPI"] >= 0
        for mean in o["expected"]:
            assert mean - o["WS"] == (mean - o["RP"]) + o["future_EVPI"]
        oracle_sweep.append(dict(case=i, stay_w1=values[0], stay_w2=values[1],
                                 switch_w1=values[2], switch_w2=values[3],
                                 action=o["action"], RP=o["RP"], WS=o["WS"],
                                 future_EVPI=o["future_EVPI"]))
    check("256 factorial tables: identities and sign convention", len(factorial_sweep)==256)
    check("256 two-future problems: oracle ordering and decomposition", len(oracle_sweep)==256)
    write_csv("oracle_examples.csv", oracle_rows)
    write_csv("factorial_examples.csv", [dict(case=k, **v) for k,v in tables.items()])
    write_csv("factorial_sweep.csv", factorial_sweep)
    write_csv("oracle_sweep.csv", oracle_sweep)
    config = dict(responsible="Doan Van Tai", arithmetic="fractions.Fraction",
                  seed=None, units="arbitrary cost units; V1 inherited packet*s",
                  oracle_futures=["w1","w2"], probabilities=["1/2","1/2"],
                  tie_rule="Stay", factorial_order=["00","10","01","11"],
                  exhaustive_values=[0,1,2,3], exhaustive_cases_per_sweep=256,
                  scope="exposed teaching examples; no grid v1.2, paper replication or null selection")
    (OUT / "config.json").write_text(json.dumps(config,ensure_ascii=False,indent=2)+"\n")
    payload=dict(status="PASS", check_count=len(checks), checks=checks,
                 oracle_examples=examples, factorial_examples=tables, V1_regret=regret,
                 exhaustive_cases=dict(factorial=256,oracle=256),
                 input=dict(path=str(frozen.relative_to(ROOT)),
                            sha256=hashlib.sha256(frozen.read_bytes()).hexdigest()),
                 source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT / "toy_results.json").write_text(json.dumps(serial(payload),ensure_ascii=False,indent=2)+"\n")
    print(f"PASS {len(checks)} checks; 256 factorial + 256 oracle problems; exact Fraction")
    for name,o in examples.items():
        print(f"{name}: {o['action']}, RP={o['RP']}, WS={o['WS']}, future EVPI={o['future_EVPI']}")
    print(f"V1: Gamma={v1['Gamma']}, L00={v1['L00']}, R00={regret['00']}; additive Gamma=0")


if __name__ == "__main__":
    main()
