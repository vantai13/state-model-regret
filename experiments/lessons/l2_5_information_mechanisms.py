"""L2.5 Part2: exact teaching examples; not the contract-v1.2 experiment.

Responsible: Doan Van Tai. Enumerate outcomes before comparing with the older
L2.2 helper and frozen L2.3 V1. All arithmetic is rational, no random seed.
"""
import argparse
import csv
from fractions import Fraction as F
from itertools import combinations, product
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACT = ("St", "Sw")
MODES = ("hi", "lo")


def encode(x):
    if isinstance(x, F):
        return str(x)
    if isinstance(x, dict):
        return {k: encode(v) for k, v in x.items()}
    if isinstance(x, (tuple, list)):
        return [encode(v) for v in x]
    return x


def csv_out(path, rows):
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(encode(rows))


def pick(values):
    return min(ACT, key=lambda a: values[a])  # ACT order: exact tie -> Stay


def slot(a, ba, bb):
    """Apply arrivals, then each queue serves min(work,3), dt=1 second."""
    work = (F(ba) + (2 if a == "St" else 0),
            F(bb) + (2 if a == "Sw" else 0))
    residual = tuple(w - min(w, F(3)) for w in work)
    return (*residual, sum(residual))


def queue_case(name, hi, check, events, policies):
    supports = {"hi": hi, "lo": (0, 1)}
    truth, approx = {}, {}
    for m in MODES:
        truth[m], approx[m] = {}, {}
        for a in ACT:
            vals = []
            for ba, bb in product((2, 3), supports[m]):
                qa, qb, c = slot(a, ba, bb)
                vals.append(c)
                events.append(dict(case=name, mode=m, action=a, bA=ba, bB=bb,
                                   probability=F(1, 4), qA=qa, qB=qb, cost=c))
            truth[m][a] = sum(vals) / 4
            approx[m][a] = slot(a, F(5, 2), F(sum(supports[m]), 2))[2]
    forecasts = {"M0": {a: sum(approx[m][a] for m in MODES) / 2 for a in ACT},
                 "M1": {a: sum(truth[m][a] for m in MODES) / 2 for a in ACT}}
    actions = {"00": pick(forecasts["M0"]), "01": pick(forecasts["M1"]),
               "10": {m: pick(approx[m]) for m in MODES},
               "11": {m: pick(truth[m]) for m in MODES}}
    losses = {}
    for cell, rule in actions.items():
        chosen = {m: rule if isinstance(rule, str) else rule[m] for m in MODES}
        losses[cell] = sum(truth[m][chosen[m]] for m in MODES) / 2
        policies.append(dict(case=name, cell=cell, hi=chosen["hi"], lo=chosen["lo"],
                             expected_cost=losses[cell]))
    l = losses
    contrast = dict(GS=l["00"]-l["10"], GM=l["00"]-l["01"], GSM=l["00"]-l["11"],
                    Gam=l["10"]+l["01"]-l["00"]-l["11"],
                    GSgM1=l["01"]-l["11"], GMgS1=l["10"]-l["11"])
    bias = {m: {a: truth[m][a]-approx[m][a] for a in ACT} for m in MODES}
    oracle = sum(min(truth[m].values()) for m in MODES) / 2
    check(name+": Jensen fixed-action lower bound", all(v >= 0 for b in bias.values() for v in b.values()))
    check(name+": true-law information value", contrast["GSgM1"] >= 0)
    check(name+": interaction identity", contrast["Gam"] == contrast["GSgM1"]-contrast["GS"])
    check(name+": nonnegative oracle regret", all(x >= oracle for x in l.values()))
    return dict(J=truth, J0=approx, S0_forecasts=forecasts, actions=actions, L=l,
                con=contrast, Jensen_bias=bias, oracle_cost=oracle,
                regret={c: v-oracle for c, v in l.items()})


def servers(check):
    initial = (0, 3, 3, 3)
    pair_p = [F(0)] * 4
    for pair in combinations(range(4), 2):
        best = min(initial[i] for i in pair)
        ties = [i for i in pair if initial[i] == best]
        for i in ties:
            pair_p[i] += F(1, 6 * len(ties))
    check("d2 without replacement probabilities", pair_p == [F(1, 2)] + [F(1, 6)]*3)
    fixed = {"stale_shortest": [F(1), F(0), F(0), F(0)],
             "random": [F(1, 4)]*4, "stale_d2": pair_p}
    expected = {"stale_shortest": (8, 3, 3, 3), "random": (2, 5, 5, 5),
                "stale_d2": (4, F(13, 3), F(13, 3), F(13, 3)),
                "fresh_shortest": (5, 4, 4, 4)}
    rows, distributions = [], []
    for policy in expected:
        dist = {initial: F(1)}
        for _ in range(8):
            following = {}
            for q, mass in dist.items():
                if policy == "fresh_shortest":
                    # Illustrative toy tie rule only, not M00's random tie.
                    idx = min(range(4), key=lambda i: q[i])
                    p = [F(i == idx) for i in range(4)]
                else:
                    p = fixed[policy]
                for i, prob in enumerate(p):
                    if not prob:
                        continue
                    dest = tuple(v + (j == i) for j, v in enumerate(q))
                    following[dest] = following.get(dest, F(0)) + mass*prob
            dist = following
        eq = tuple(sum(m*q[i] for q, m in dist.items()) for i in range(4))
        emax = sum(m*max(q) for q, m in dist.items())
        check(policy+": probability mass", sum(dist.values()) == 1)
        check(policy+": expected loads", eq == expected[policy])
        check(policy+": conservation 17 jobs", all(sum(q) == 17 for q in dist))
        check(policy+": max of mean <= mean of max", max(eq) <= emax)
        rows.append(dict(policy=policy, **{f"Eq{i+1}": eq[i] for i in range(4)},
                         max_Eq=max(eq), E_max_q=emax, terminal_states=len(dist)))
        for q, mass in sorted(dist.items()):
            distributions.append(dict(policy=policy, **{f"q{i+1}": q[i] for i in range(4)}, probability=mass))
    return rows, distributions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT/"results/lessons/l2_5/part2")
    out = parser.parse_args().output
    out.mkdir(parents=True, exist_ok=True)
    checks = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    events, policies = [], []
    cases = {name: queue_case(name, hi, check, events, policies)
             for name, hi in [("V1", (1, 6)), ("hi_2_5", (2, 5))]}
    # Read-only comparisons after independently enumerating costs and decisions.
    from l2_2_voi_mapping import toy_table
    frozen = json.loads((ROOT/"results/lessons/l2_3/p11_toy.json").read_text())["v1"]
    for name, hi in [("V1", (1, 6)), ("hi_2_5", (2, 5))]:
        reference = toy_table((2, 3), hi, (0, 1))
        for field in ("J", "J0", "actions", "L", "con"):
            check(name+": L2.2 helper "+field, cases[name][field] == reference[field])
            if name == "V1":
                # Frozen JSON encoded some exact zeros as integers.
                def normal(x):
                    if isinstance(x, dict): return {k: normal(v) for k, v in x.items()}
                    return str(x)
                check("V1: frozen L2.3 "+field, normal(encode(cases[name][field])) == normal(frozen[field]))
    check("V1 negative GS", cases["V1"]["con"]["GS"] == F(-1, 4))
    check("hi_2_5 all four costs", set(cases["hi_2_5"]["L"].values()) == {F(5, 4)})
    check("hi_2_5 true tie -> Stay", cases["hi_2_5"]["actions"]["11"]["hi"] == "St")
    check("hi_2_5 model still biased", cases["hi_2_5"]["Jensen_bias"]["hi"]["St"] == F(1, 2))
    server_rows, distributions = servers(check)
    summary = [dict(case=n, **{f"L{k}": v for k, v in c["L"].items()}, **c["con"]) for n,c in cases.items()]
    config = dict(responsible="Doan Van Tai", arithmetic="fractions.Fraction", seed=None,
                  scope="exposed teaching verification, not contract-v1.2 or M00 replication",
                  queue=dict(capacity=3, managed_load=2, q0=[0,0], dt_seconds=1, horizon_slots=1,
                             A=[2,3], B_hi_cases=[[1,6],[2,5]], B_lo=[0,1],
                             prior_hi="1/2", outcome_probability="1/4 conditional on mode",
                             unit="packet*s", tie="Stay", S0="cost average over conditional mean rollouts"),
                  servers=dict(q0=[0,3,3,3], jobs=8, service=0, stale_board="fixed",
                               d2="uniform unordered pair without replacement; random tie",
                               fresh_tie="lowest server index", unit="jobs, not response time"))
    for filename, value in [("config.json",config), ("toy_results.json",dict(status="PASS",cases=cases,
                           checks=checks,check_count=len(checks),servers=server_rows,
                           source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))]:
        (out/filename).write_text(json.dumps(encode(value),ensure_ascii=False,indent=2)+"\n")
    for name, rows in [("cost_events.csv",events),("policies.csv",policies),("summary.csv",summary),
                       ("server_summary.csv",server_rows),("server_distribution.csv",distributions)]:
        csv_out(out/name, rows)
    print(json.dumps(encode(dict(status="PASS",checks=len(checks),summary=summary,servers=server_rows)),ensure_ascii=False))


if __name__ == "__main__":
    main()
