"""Cooper (2002) Example 1: analytic replay, not Phase 3. Doan Van Tai."""
import csv
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/lessons/l2_8/part2"


def replay(precision):
    with localcontext() as ctx:
        ctx.prec = precision
        q = (-D(1)).exp()
        poisson = [(0, q), (1, q), (2, 1-2*q)]  # 2 means 2 or more, exactly.
        low = [(0, q), (1, 1-q)]               # 1 means one or more.
        rows = []
        for (n1, p1), (n2, p2), (l2, p3) in product(poisson, poisson, low):
            old = 10*min(n1+n2, 2)
            new = 10*min(n1, 2)
            if n1 == 0:
                new += 10*min(n2, 1) + 2*l2
            elif n1 == 1:
                new += 10*min(n2, 1)
            rows.append(dict(first_high=n1, second_high=n2, second_low=l2,
                             probability=p1*p2*p3, initial_policy_revenue=old,
                             resolving_revenue=new))
        old = sum(r["probability"]*r["initial_policy_revenue"] for r in rows)
        new = sum(r["probability"]*r["resolving_revenue"] for r in rows)
        tol = D(10)**(-precision+5)
        assert abs(sum(r["probability"] for r in rows)-1) < tol
        assert abs(old-(20-40*q*q)) < tol
        assert abs(new-(20-8*q-22*q*q)) < tol
        assert abs(old-new-(8*q-18*q*q)) < tol and old > new
        return rows, dict(initial_policy_revenue=old, resolving_revenue=new,
                          loss_from_resolving=old-new,
                          conditional_old=20-30*q, conditional_resolving=12*(1-q))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows, profit = replay(50)
    _, high = replay(70)
    assert all(abs(v-high[k]) < D("1e-45") for k,v in profit.items())
    with (OUT/"cooper_example1.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader(); w.writerows(rows)

    frozen = json.loads((ROOT/"results/lessons/l2_3/p11_toy.json").read_text())["v1"]
    diagnostics=[]
    for mode in ("hi", "lo"):
        a0 = frozen["actions"]["00"]
        a1 = frozen["actions"]["10"][mode]
        j = {a:F(v) for a,v in frozen["J"][mode].items()}
        pred = {a:F(v) for a,v in frozen["J0"][mode].items()}
        delta = {a:j[a]-pred[a] for a in j}
        gain = j[a0]-j[a1]
        predicted = pred[a0]-pred[a1]
        assert predicted >= 0 and all(d >= 0 for d in delta.values())
        assert gain == predicted+delta[a0]-delta[a1]
        eps = max(delta.values())
        assert gain >= -eps  # certified one-sided errors only
        diagnostics.append(dict(mode=mode, old_action=a0, new_action=a1,
                                predicted_improvement=str(predicted),
                                old_underestimate=str(delta[a0]), new_underestimate=str(delta[a1]),
                                true_improvement=str(gain), one_sided_epsilon=str(eps)))
    gs = sum(F(r["true_improvement"]) for r in diagnostics)/2
    assert gs == F(-1,4) == F(frozen["con"]["GS"])
    with (OUT/"v1_diagnostic.csv").open("w", newline="") as f:
        w=csv.DictWriter(f, fieldnames=list(diagnostics[0]), lineterminator="\n")
        w.writeheader(); w.writerows(diagnostics)

    config = dict(responsible="Doan Van Tai", source="R02 §5 Example 1, printed726/PDF7",
                  prices=[10,2], capacity=2, poisson_rates_per_unit=[1,1],
                  horizon=2, resolving_time=1, unit="revenue units",
                  initial_allocation=[2,0], aggregate_cases=18,
                  arithmetic="Decimal 50 digits; independent precision replay 70 digits",
                  seed=None, monte_carlo=False, tail_truncation=False,
                  scope="exact probability aggregation of the cited example; no four-cell RM or grid replication")
    result=dict(status="PASS", responsible="Doan Van Tai", **{k:str(v) for k,v in profit.items()},
                aggregate_cases=len(rows), precision_replay_digits=[50,70],
                V1_GS=str(gs), V1_mode_rows=len(diagnostics), grid_run=False,
                paper_simulations_replicated=False, H1_selected=False)
    for name,data in [("config.json",config),("math_checks.json",result)]:
        (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False))


if __name__ == "__main__":
    main()
