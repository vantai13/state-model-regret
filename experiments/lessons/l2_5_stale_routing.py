"""L2.5 Part1: deterministic admission examples, not a replication of P04.

Responsible: Doan Van Tai. No changes to the locked queueing contract or grid.
"""
import csv
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/lessons/l2_5"


def simulate(period=None, requests=10, round_robin=False):
    actual, advertised = [6, 4], [6, 4]
    last_update, trace = 0, []
    for n in range(requests):
        updated = not round_robin and n % period == 0
        if updated:
            advertised, last_update = actual.copy(), n
        before = actual.copy()
        if round_robin:
            chosen = n % 2
        elif max(advertised) < 1:
            chosen = None
        else:
            chosen = int(advertised[1] > advertised[0])  # tie -> A
        if chosen is None:
            outcome = "routing_failure"
        elif actual[chosen] < 1:
            outcome = "setup_failure"
        else:
            outcome = "accepted"
            actual[chosen] -= 1
        trace.append(dict(request=n+1, updated=int(updated), snapshot_step=last_update,
                          advertised_A=advertised[0], advertised_B=advertised[1],
                          before_A=before[0], before_B=before[1],
                          chosen="-" if chosen is None else "AB"[chosen], outcome=outcome,
                          after_A=actual[0], after_B=actual[1]))
    routing = sum(r["outcome"] == "routing_failure" for r in trace)
    setup = sum(r["outcome"] == "setup_failure" for r in trace)
    return dict(period=period, policy="round_robin" if round_robin else "snapshot_widest",
                requests=requests, accepted=requests-routing-setup,
                attempts_A=sum(r["chosen"] == "A" for r in trace),
                attempts_B=sum(r["chosen"] == "B" for r in trace),
                routing_failures=routing, setup_failures=setup, blocked=routing+setup,
                blocked_fraction=str(F(routing+setup, requests)),
                remaining_A=actual[0], remaining_B=actual[1]), trace


def trigger_example(hold_down):
    advertised, last = F(10), F(0)
    rows = []
    for t, available in [(F(0), F(10)), (F(1), F(6)), (F(5), F(6))]:
        relative_error = abs(available-advertised) / advertised
        fires = relative_error > F(1, 5) and t-last >= hold_down
        if fires:
            advertised, last = available, t
        rows.append(dict(time=str(t), actual_available=str(available),
                         advertised_available=str(advertised), hold_down=str(hold_down),
                         trigger_threshold="1/5", update=int(fires),
                         relative_error_after=str(abs(available-advertised)/advertised)))
    return rows


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    checks = []
    summaries, traces = [], []
    for period in range(1, 11):
        summary, rows = simulate(period=period)
        summary["case"] = f"T{period}"
        summaries.append(summary)
        for r in rows:
            assert min(r["after_A"], r["after_B"]) >= 0
            expected_drop = int(r["outcome"] == "accepted")
            assert r["before_A"] + r["before_B"] - r["after_A"] - r["after_B"] == expected_drop
            assert r["advertised_A"] == rows[r["snapshot_step"]]["before_A"]
            assert r["advertised_B"] == rows[r["snapshot_step"]]["before_B"]
        assert summary["accepted"] + summary["blocked"] == 10
        assert summary["accepted"] == 10-summary["remaining_A"]-summary["remaining_B"]
        checks.append(f"T{period}: mass, admissions, immutable snapshot, nonnegative resources")
        traces.extend(dict(case=summary["case"], **r) for r in rows)
    round_robin, rows = simulate(round_robin=True)
    round_robin["case"] = "round_robin"
    summaries.append(round_robin)
    traces.extend(dict(case="round_robin", **r) for r in rows)
    by_case = {s["case"]: s for s in summaries}
    expected = {"T1": (10, 0), "T5": (9, 1), "T6": (10, 0), "T10": (6, 4), "round_robin": (9, 1)}
    for name, golden in expected.items():
        assert (by_case[name]["accepted"], by_case[name]["blocked"]) == golden
        checks.append(name + ": hand-derived accepted/blocked pair")
    assert round_robin["attempts_A"] == round_robin["attempts_B"] == 5
    checks.append("round-robin alternates exactly five requests per link")
    assert by_case["T5"]["blocked"] > by_case["T6"]["blocked"]
    checks.append("finite-horizon counterexample to global monotonicity in T")

    long_summary, long_trace = simulate(period=10, requests=40)
    route_sequence = [r["chosen"] for r in long_trace if r["chosen"] != "-"]
    switches = sum(a != b for a, b in zip(route_sequence, route_sequence[1:]))
    assert switches == 1 and long_summary["accepted"] == 10
    assert long_summary["remaining_A"] == long_summary["remaining_B"] == 0
    assert all(r["outcome"] == "routing_failure" for r in long_trace[20:])
    checks.append("no-departure toy exhausts resources; does not establish sustained oscillation")

    trigger_rows = trigger_example(F(0)) + trigger_example(F(5))
    assert trigger_rows[1]["relative_error_after"] == "0"
    assert trigger_rows[4]["relative_error_after"] == "2/5"
    assert trigger_rows[4]["update"] == 0
    checks.append("hold-down permits residual error2/5 above trigger1/5")
    age = []
    for period in [1, 5, 10]:
        # An explicitly uniform phase grid; not a claim about arrivals in P04.
        phases = [F(period*(2*k+1), 200) for k in range(100)]
        mean = sum(phases)/len(phases)
        assert mean == F(period, 2)
        age.append(dict(period=period, mean_age=str(mean),
                        quarter_phase_age=str(F(period, 4)), three_quarter_phase_age=str(F(3*period, 4))))
        checks.append(f"T{period}: midpoint-uniform phase mean T/2")

    config = dict(responsible="Doan Van Tai", initial_available=[6, 4], demand_per_request=1,
                  requests=10, arrivals="one request per step; refresh at0,T,2T before request n+1",
                  periods=list(range(1, 11)), tie="A", departures=False,
                  units="capacity in arbitrary bandwidth units; period in request steps",
                  seed=None, stochastic=False,
                  objective="blocked count/fraction; not packet*s regret",
                  scope="illustration supplied in L2.5 Part1; not P04 replication or locked-contract plant")
    (OUT / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n")
    result = dict(status="PASS", responsible="Doan Van Tai", source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  check_count=len(checks), checks=checks, summaries=summaries,
                  extended_horizon=dict(**long_summary, route_switches=switches),
                  ideal_uniform_phase_examples=age,
                  trigger_counterexample=dict(threshold="1/5", hold_down=5, residual_at_time1="2/5"),
                  no_replicated_paper_measurements=True, no_phase3_grid_results=True)
    (OUT / "toy_results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    for name, data in [("summary.csv", summaries), ("trace.csv", traces), ("trigger_trace.csv", trigger_rows),
                       ("extended_trace.csv", long_trace)]:
        with (OUT / name).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(data[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(data)
    print(json.dumps({"status":"PASS", "checks":len(checks), "requests_per_comparison":10,
                      "blocked":{name:by_case[name]["blocked"] for name in expected},
                      "monotonicity_counterexample":"T5 blocks1; T6 blocks0",
                      "trigger_residual":"2/5 > 1/5 during hold-down",
                      "scope":"deterministic lesson illustration; no replicated P04 or Phase3 measurements"}, ensure_ascii=False), flush=True)
    return result


if __name__ == "__main__":
    run()
