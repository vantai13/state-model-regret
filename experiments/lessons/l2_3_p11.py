"""Exact P11 illustration and corrections. Responsible: Doan Van Tai; AI-assisted.

Finite illustrative beliefs, not structural uncertainty added to contract v1.2.
Run as python3 -m experiments.lessons.l2_3_p11.
"""
import argparse
import csv
import hashlib
import json
from fractions import Fraction as F
from itertools import product
from pathlib import Path

from .l2_2_voi_mapping import ACTIONS, MODES, serializable, toy_table


def p11_toy(prior):
    if not prior or sum(p for _, p in prior) != 1 or any(p < 0 for _, p in prior):
        raise ValueError("prior must be nonempty and normalized with nonnegative weights")
    true_costs = (F(3), F(5, 2))
    costs = (sum(p * (2 + d) for d, p in prior), F(5, 2))
    action = min(range(2), key=costs.__getitem__)
    learned = sum(p * min(2 + d, F(5, 2)) for d, p in prior)
    return dict(prior=prior, action=ACTIONS[action], expected_stay=costs[0],
                expected_switch=costs[1], baseline_cost=costs[action],
                learned_cost=learned, EVPI_delta=costs[action] - learned,
                true_cost=true_costs[action], true_regret=true_costs[action] - min(true_costs))


def value_of_disclosure(J, weights, signal):
    """Bayes value of a finite signal, preserving any dependence with the state."""
    base = min(sum(weights[x] * J[x][a] for x in weights) for a in ACTIONS)
    groups = {}
    for x in weights:
        groups.setdefault(signal[x], []).append(x)
    # Group mass times conditional expectation cancels the normalization.
    informed = sum(min(sum(weights[x] * J[x][a] for x in xs) for a in ACTIONS)
                   for xs in groups.values())
    return dict(baseline=base, informed=informed, value=base - informed)


def run(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    checks = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    specs = [
        ("minus1_plus1", [(F(-1), F(1, 2)), (F(1), F(1, 2))], "St", F(1, 4), F(1, 2)),
        ("zero_plus2", [(F(0), F(1, 2)), (F(2), F(1, 2))], "Sw", F(1, 4), F(0)),
        ("point0", [(F(0), F(1))], "St", F(0), F(1, 2)),
        ("point1", [(F(1), F(1))], "Sw", F(0), F(0)),
    ]
    rows = []
    for label, prior, action, voi, regret in specs:
        row = p11_toy(prior)
        check(label + ": golden", (row["action"], row["EVPI_delta"], row["true_regret"]) == (action, voi, regret))
        a = ACTIONS.index(row["action"])
        direct = sum(p * ((2 + d if a == 0 else F(5, 2)) - min(2 + d, F(5, 2))) for d, p in prior)
        check(label + ": direct expected improvement", direct == row["EVPI_delta"] >= 0)
        rows.append(dict(id=label, **row))
    check("known-state model gain", F(3) - F(5, 2) == F(1, 2))
    v1 = toy_table([2, 3], [1, 6], [0, 1])
    fixed_costs = [sum(v1["J"][m][a] for m in MODES) / 2 for a in ACTIONS]
    same_info_gains = [v1["L"]["00"] - c for c in fixed_costs]
    check("S0 true-law model upper bound", max(same_info_gains) == v1["con"]["GM"] == 0)
    full_costs = [sum(v1["J"][m][a] for m, a in zip(MODES, policy)) / 2
                  for policy in product(ACTIONS, repeat=2)]
    full_info_gains = [v1["L"]["10"] - c for c in full_costs]
    check("S1 true-law model upper bound", max(full_info_gains) == v1["con"]["GMgS1"] == F(1, 4))
    check("state oracle does not bound no-op", v1["con"]["GS"] == F(-1, 4) < 0)
    check("V1 true-cost table", v1["J"] == {"hi": {"St": F(3), "Sw": F(5, 2)}, "lo": {"St": F(3, 2), "Sw": 0}})
    check("V1 M0 table", v1["J0"] == {"hi": {"St": F(2), "Sw": F(5, 2)}, "lo": {"St": F(3, 2), "Sw": 0}})
    check("V1 2x2", v1["L"] == {"00": F(5, 4), "10": F(3, 2), "01": F(5, 4), "11": F(5, 4)})
    v2 = toy_table([0, 5], [0, 2], [3, 6])
    discrepancy = {m: tuple(v2["J"][m][a] - v2["J0"][m][a] for a in ACTIONS) for m in MODES}
    check("V2 state-dependent discrepancy", discrepancy == {"hi": (F(1, 2), F(3, 2)), "lo": (F(1, 2), F(1))})
    disclosure = value_of_disclosure(v2["J"], v2["true"], discrepancy)
    check("V2 known law but valuable state disclosure", disclosure == {"baseline": F(11, 4), "informed": F(5, 2), "value": F(1, 4)})
    assert len(checks) == 17
    config = dict(author="Doan Van Tai", arithmetic="fractions.Fraction", seed=None,
                  dt_seconds=1, horizon_slots=1, capacity=3, managed_load=2,
                  q0=[0, 0], unit="packet*s", actual_delta="1",
                  status="exposed verification; not grid v1.2")
    summary = dict(status="PASS", checks=checks, check_count=len(checks),
                   rows=rows, v1=v1, v2=v2, discrepancy=discrepancy,
                   hidden_state_disclosure=disclosure,
                   same_info_gains=same_info_gains, full_info_gains=full_info_gains,
                   config=config, source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (output / "p11_toy.json").write_text(json.dumps(serializable(summary), indent=2) + "\n")
    (output / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    fields = ["id", "action", "baseline_cost", "learned_cost", "EVPI_delta", "true_cost", "true_regret"]
    with (output / "p11_toy.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(serializable(rows))
    print(f"L2.3 PASS: {len(checks)} exact checks; 4 priors; RNG=none; unit=packet*s")
    for row in rows:
        print(row["id"], row["action"], "VOI", row["EVPI_delta"], "true regret", row["true_regret"])
    print("V2 disclosure:", serializable(disclosure))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="results/lessons/l2_3")
    run(parser.parse_args().output)
