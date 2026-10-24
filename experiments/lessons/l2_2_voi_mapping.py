"""L2.2 — kiểm ánh xạ contrast ↔ EVPPI / VSS trên toy một slot (E1, exact).

Scientific purpose: kiểm rằng G_S|M1 = EVPPI(x|y) và G_M|S1 = E_b[VSS(x)] là
identity dưới G1–G5, và chúng vỡ (hoặc không vỡ) đúng như lý thuyết dự đoán khi
một giả định bị phá. Không chạm plant hay lưới v1.2.

Người phụ trách: Doan Van Tai. AI-assisted adaptation of the supplied L2.2
lesson code, with artifact output and an independent conditional-VSS checker.
"""
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
from collections import Counter
import argparse
import csv
import hashlib
import json
import sys
from time import perf_counter

C, U = 3, 2                      # capacity, managed load: packet/slot
ACTIONS = ("St", "Sw")
MODES = ("hi", "lo")

def cost(a, bA, bB):
    """Truth plant: một slot, hai queue rỗng, cost = backlog cuối slot."""
    if a == "St":
        return max(0, bA + U - C) + max(0, bB - C)
    return max(0, bA - C) + max(0, bB + U - C)

def mean(xs):
    return sum(F(v) for v in xs) / len(xs)

def argmin(costs, tie="St"):
    """D16: Switch chỉ khi rẻ hơn hẳn; hòa -> `tie` (mặc định Stay)."""
    if costs["Sw"] < costs["St"]:
        return "Sw"
    if costs["Sw"] > costs["St"]:
        return "St"
    return tie

def vss_known_x(A, Bm, J_m, tie="St"):
    """VSS cổ điển của bài toán ĐÃ BIẾT x, tính từ định nghĩa (thay w bằng E[w|x]),
    độc lập với cách pipeline cài M0 — để I2 không thành tautology."""
    a_ev = argmin({a: cost(a, mean(A), mean(Bm)) for a in ACTIONS}, tie)
    return J_m[a_ev] - min(J_m.values())

def toy_table(A, Bhi, Blo, prior_hi=F(1, 2), belief_hi=None, tie="St",
              mean_state=False, m0_ignores_mode=False):
    true = {"hi": prior_hi, "lo": 1 - prior_hi}                  # luật thật của x
    b = true if belief_hi is None else {"hi": belief_hi, "lo": 1 - belief_hi}  # G1
    B = {"hi": Bhi, "lo": Blo}
    E = lambda w, f: sum(w[m] * f(m) for m in MODES)

    J = {m: {a: mean([cost(a, x, y) for x in A for y in B[m]]) for a in ACTIONS} for m in MODES}  # M1 (G3)
    mB_all = E(true, lambda m: mean(B[m]))
    J0 = {m: {a: cost(a, mean(A), mB_all if m0_ignores_mode else mean(B[m])) for a in ACTIONS}
          for m in MODES}                                   # M0 (G5); mutant d bỏ điều kiện theo mode

    a11 = {m: argmin(J[m], tie) for m in MODES}
    a10 = {m: argmin(J0[m], tie) for m in MODES}
    a01 = argmin({a: E(b, lambda m: J[m][a]) for a in ACTIONS}, tie)
    if mean_state:   # mutant b: rollout từ "mean-state" (trộn nền B qua mode), trái D10
        mB = E(b, lambda m: mean(B[m]))
        a00 = argmin({a: cost(a, mean(A), mB) for a in ACTIONS}, tie)
    else:            # D10: trung bình cost của mean rollout theo belief
        a00 = argmin({a: E(b, lambda m: J0[m][a]) for a in ACTIONS}, tie)

    L = {"00": E(true, lambda m: J[m][a00]), "01": E(true, lambda m: J[m][a01]),   # G4: chấm dưới luật thật
         "10": E(true, lambda m: J[m][a10[m]]), "11": E(true, lambda m: J[m][a11[m]])}
    con = {"GS": L["00"] - L["10"], "GM": L["00"] - L["01"], "GSM": L["00"] - L["11"],
           "Gam": L["10"] + L["01"] - L["00"] - L["11"],
           "GSgM1": L["01"] - L["11"], "GMgS1": L["10"] - L["11"]}

    # Đại lượng cổ điển, tính dưới luật thật
    EJ = {a: E(true, lambda m: J[m][a]) for a in ACTIONS}
    evppi = min(EJ.values()) - E(true, lambda m: min(J[m].values()))
    vss_x = {m: vss_known_x(A, B[m], J[m], tie) for m in MODES}
    d = {m: J[m]["Sw"] - J[m]["St"] for m in MODES}
    dplus = E(true, lambda m: max(0, d[m]))
    dminus = E(true, lambda m: max(0, -d[m]))
    scen = [(true[m] / (len(A) * len(B[m])), x, y) for m in MODES for x in A for y in B[m]]
    ws = sum(p * min(cost("St", x, y), cost("Sw", x, y)) for p, x, y in scen)
    rp = min(EJ.values())
    cev = {a: cost(a, mean(A), mB_all) for a in ACTIONS}
    eev = EJ[argmin(cev, tie)]
    return dict(J=J, J0=J0, true=true, belief=b,
                actions={"00": a00, "01": a01, "10": a10, "11": a11},
                EVPPI_subjective=min(E(b, lambda m: J[m][a]) for a in ACTIONS) - E(b, lambda m: min(J[m].values())),
                EVSS_taut=E(true, lambda m: J[m][a10[m]] - min(J[m].values())),
                L=L, con=con, EVPPI=evppi, EVSS=E(true, lambda m: vss_x[m]),
                Dplus=dplus, Dminus=dminus, WS=ws, RP=rp, EV=min(cev.values()), EEV=eev)

def invariants(t):
    c = t["con"]
    return {
        "I1": c["GSgM1"] == t["EVPPI"],
        "I2": c["GMgS1"] == t["EVSS"],
        "I3": c["Gam"] == c["GSgM1"] - c["GS"] == c["GMgS1"] - c["GM"],
        "I4": t["WS"] <= t["RP"] <= t["EEV"],
        "I5": all(t["L"]["11"] <= v for v in t["L"].values()),
        "I6": c["GSgM1"] == min(t["Dplus"], t["Dminus"]),
    }

GOLDEN = {  # tính tay ở Part 1–2
    "V1": (([2, 3], [1, 6], [0, 1]), dict(GS=F(-1, 4), GM=0, Gam=F(1, 4), GSgM1=0, GMgS1=F(1, 4))),
    "V2": (([0, 5], [0, 2], [3, 6]), dict(GS=F(1, 2), GM=F(1, 4), Gam=F(-1, 4), GSgM1=F(1, 4), GMgS1=0)),
}


def serializable(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serializable(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [serializable(v) for v in value]
    return value


def enumerate_toys():
    pairs = tuple(combinations(range(8), 2))
    yield from product(pairs, repeat=3)


def run(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    config = dict(author="Doan Van Tai", arithmetic="fractions.Fraction",
                  capacity=3, managed_load=2, q0=[0, 0], dt_seconds=1,
                  horizon_slots=1, unit="packet*s", prior_hi="1/2", seed=None,
                  family="three independent unordered distinct pairs from 0..7",
                  tie="St", role="exposed verification toy; not grid v1.2")
    (output / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    golden = {}
    for name, (args, want) in GOLDEN.items():
        got = toy_table(*args)
        if not all(got["con"][k] == v for k, v in want.items()):
            raise AssertionError((name, got))
        golden[name] = got
    golden["V4"] = toy_table([1, 2], [0, 1], [1, 3])
    assert golden["V4"]["EV"] == F(1, 4) > golden["V4"]["WS"] == F(1, 8)
    failures = Counter({f"I{i}": 0 for i in range(1, 7)})
    counts = Counter()
    rows = 0
    start = perf_counter()
    with (output / "cases.csv").open("w", newline="") as stream:
        writer = None
        for A, Bh, Bl in enumerate_toys():
            args = (A, Bh, Bl)
            base = toy_table(*args)
            wrong = toy_table(*args, belief_hi=F(3, 4))
            mean_state = toy_table(*args, mean_state=True)
            tie_sw = toy_table(*args, tie="Sw")
            ignores_mode = toy_table(*args, m0_ignores_mode=True)
            checks = invariants(base)
            failures.update({k: int(not v) for k, v in checks.items()})
            diagnostics = {
                "wrong_prior_i1": wrong["con"]["GSgM1"] != wrong["EVPPI"],
                "wrong_prior_up": wrong["con"]["GSgM1"] > wrong["EVPPI"],
                "wrong_prior_down": wrong["con"]["GSgM1"] < wrong["EVPPI"],
                "mean_state_L00_changed": mean_state["L"]["00"] != base["L"]["00"],
                "tie_sw_i1_fail": not invariants(tie_sw)["I1"],
                "ignores_mode_i2": not invariants(ignores_mode)["I2"],
                "tautological_i2_fail": ignores_mode["con"]["GMgS1"] != ignores_mode["EVSS_taut"],
                "GS_negative": base["con"]["GS"] < 0,
                "Gamma_positive": base["con"]["Gam"] > 0,
                "Gamma_negative": base["con"]["Gam"] < 0,
                "Gamma_zero": base["con"]["Gam"] == 0,
                "M0_better_global_EV": base["L"]["00"] < base["EEV"],
                "M0_worse_global_EV": base["L"]["00"] > base["EEV"],
                "EV_above_WS": base["EV"] > base["WS"],
                "EV_above_RP": base["EV"] > base["RP"],
                "subjective_objective_differ": wrong["EVPPI_subjective"] != wrong["EVPPI"],
            }
            counts.update({k: int(v) for k, v in diagnostics.items()})
            row = {"A0": A[0], "A1": A[1], "Bh0": Bh[0], "Bh1": Bh[1],
                   "Bl0": Bl[0], "Bl1": Bl[1]}
            row.update({"L" + k: str(v) for k, v in base["L"].items()})
            row.update({k: str(v) for k, v in base["con"].items()})
            row.update({k: str(base[k]) for k in ("EVPPI", "EVSS", "WS", "RP", "EV", "EEV", "Dplus", "Dminus")})
            row.update({k: int(v) for k, v in checks.items()})
            row.update({k: int(v) for k, v in diagnostics.items()})
            if writer is None:
                writer = csv.DictWriter(stream, fieldnames=list(row))
                writer.writeheader()
            writer.writerow(row)
            rows += 1
    # Source counts were exposed. Assertions check replication, not prediction skill.
    expected = dict(wrong_prior_i1=410, wrong_prior_up=410, wrong_prior_down=0,
                    mean_state_L00_changed=3528, tie_sw_i1_fail=0,
                    ignores_mode_i2=5730, tautological_i2_fail=0,
                    GS_negative=2048, Gamma_positive=2698, Gamma_negative=1436,
                    Gamma_zero=17818, M0_better_global_EV=2434,
                    M0_worse_global_EV=1094, EV_above_WS=137, EV_above_RP=0,
                    subjective_objective_differ=1940)
    assert rows == 21952
    assert not any(failures.values()), failures
    assert dict(counts) == expected, dict(counts)
    summary = dict(status="PASS", cases=rows, failures=dict(failures),
                   counts=dict(counts), expected_counts_exposed=True,
                   golden=golden, config=config,
                   source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (output / "voi_mapping.json").write_text(json.dumps(serializable(summary), indent=2) + "\n")
    print(f"L2.2 PASS: {rows} toys; invariant failures={dict(failures)}", flush=True)
    print(json.dumps(dict(counts), sort_keys=True), flush=True)
    print(f"Python {sys.version.split()[0]}; elapsed={perf_counter()-start:.3f}s; output={output}", flush=True)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="results/lessons/l2_2")
    run(parser.parse_args().output)

