"""Finite-grid checks of the drain-time lemma and true-s hybrid bound.

Doan Van Tai. Both readings of the ambiguous P4 decision sentence are retained:
invariance as h grows, and literal equality of fresh/stale decisions. A numerical
grid is evidence on the truncated CTMC state spaces, not a mathematical proof.
"""
import argparse
from fractions import Fraction as F
import math
from pathlib import Path
import time

import numpy as np

from experiments.explore_ctmc import ctmc as C
from experiments.letter.ties_topology import OUT, ROOT, write_csv, write_json

CASES = ROOT / "results/explore_ctmc/cases/asym.json"


def pair_extrema(a, b, c=0.0):
    return float(np.min(a) + np.min(b) + c), float(np.max(a) + np.max(b) + c)


def pair_decision_changes(a, b, reference_a, reference_b, c=0.0):
    """Exhaust every pair in bounded-memory chunks; no probability cutoff."""
    step = max(1, 500_000 // len(b))
    count = 0
    for start in range(0, len(a), step):
        sl = slice(start, start + step)
        x = (a[sl, None] + b[None, :] + c) < 0
        y = (reference_a[sl, None] + reference_b[None, :] + c) < 0
        count += int(np.count_nonzero(x != y))
    return count


def opposite_observation_witness(fa, fb, oa, ob, c=0.0):
    """Look for opposed actions among current states and old observations.

    Current X and age-tau observations Y have different domains. They are not
    equated by repeating a backlog-only decision across modes. A pair of
    opposing extrema is enough to refute equality for every X,Y; at tau=1 an
    irreducible finite chain permits every such old/current state transition.
    """
    fmin, fmax = pair_extrema(fa, fb, c)
    omin, omax = pair_extrema(oa, ob, c)
    if fmin < 0 <= omax:
        fi = [int(np.argmin(fa)), int(np.argmin(fb))]
        oi = [int(np.argmax(oa)), int(np.argmax(ob))]
    elif omin < 0 <= fmax:
        fi = [int(np.argmax(fa)), int(np.argmax(fb))]
        oi = [int(np.argmin(oa)), int(np.argmin(ob))]
    else:
        return None
    fg, og = float(fa[fi[0]] + fb[fi[1]] + c), float(oa[oi[0]] + ob[oi[1]] + c)
    return dict(fresh_state_indices=fi, fresh_states_nm=[[i//2, i%2] for i in fi],
                stale_backlogs=oi, fresh_gap=fg, stale_posterior_mean_gap=og,
                fresh_action="Switch" if fg < 0 else "Stay",
                stale_action="Switch" if og < 0 else "Stay")


def check_regime(case):
    start, wall = time.process_time(), time.perf_counter()
    lamA, lamB, u, kappa, c = (F(x) for x in case["parameters"])
    if c != 0:
        raise ValueError("asym lemma scope requires c=0")
    # Only this small horizon needs true V. Do not exponentiate the true plant
    # at the very large all-state drain/bound horizons: the checks use M0 only.
    reference = C.evaluate(lamA, lamB, u, kappa, [F(1, 100)], c=c,
                           disagree=False, arrays=True)
    arr = reference["_arrays"]
    na, nb = arr["NA"], arr["NB"]
    ast = C.chain(lamA + u, kappa, na)
    bst = C.chain(lamB, kappa, nb)
    specs = dict(A_stay=(lamA+u, na), A_switch=(lamA, na),
                 B_stay=(lamB, nb), B_switch=(lamB+u, nb))
    saturated, drain = {}, {}
    for name, (load, n) in specs.items():
        v, t = C.m0_vhat(load, kappa, n, [math.inf], return_T=True)
        saturated[name], drain[name] = v[0], t
    bar_h = max(float(t.max()) for t in drain.values())
    tint = max(ch["T_int"] for ch in reference["chains"].values())
    beyond = [bar_h, math.nextafter(bar_h, math.inf), 1.25*bar_h, 2*bar_h, 4*bar_h]
    local_grid = [.25*bar_h, .5*bar_h, .75*bar_h]
    path_checks = {}
    for name, (load, n) in specs.items():
        values = C.m0_vhat(load, kappa, n, beyond, return_T=False)
        errors = values - saturated[name]
        local = C.m0_vhat(load, kappa, n, local_grid)
        own_errors = [np.abs(v[t <= h] - saturated[name][t <= h])
                      for h, v, t in zip(local_grid, local, [drain[name]]*len(local_grid))]
        max_error = max(float(np.abs(errors).max()),
                        *(float(e.max()) if len(e) else 0.0 for e in own_errors))
        path_checks[name] = dict(status="PASS" if max_error == 0 else "FAIL",
                                  states=len(drain[name]), max_T=float(drain[name].max()),
                                  max_abs_error=max_error, bitwise_constant=bool(np.all(errors == 0)))

    def shifted(hs):
        da = C.m0_gap(lamA, u, kappa, na, hs, "A")
        db = C.m0_gap(lamB, u, kappa, nb, hs, "B")
        oa = C.posterior_mean(ast, da.T).T
        ob = C.posterior_mean(bst, db.T).T
        return da, db, oa, ob

    da, db, oa, ob = shifted(beyond)
    # Exact cancellation-free plateau representation, before +/- u*h^2/2.
    fa = saturated["A_switch"] - saturated["A_stay"]
    fb = saturated["B_switch"] - saturated["B_stay"]
    pa, pb = C.posterior_mean(ast, fa), C.posterior_mean(bst, fb)
    temporal = []
    representation = []
    for j, h in enumerate(beyond):
        temporal.append(dict(h=h, h_Tint=h/tint,
                             fresh_changed_pairs=pair_decision_changes(da[j], db[j], da[0], db[0]),
                             stale_changed_pairs=pair_decision_changes(oa[j], ob[j], oa[0], ob[0])))
        representation.append(dict(h=h,
                                   fresh_changed_pairs=pair_decision_changes(da[j], db[j], fa, fb),
                                   stale_changed_pairs=pair_decision_changes(oa[j], ob[j], pa, pb)))
    stable = all(r["fresh_changed_pairs"] == r["stale_changed_pairs"] == 0 for r in temporal)
    witnesses = [opposite_observation_witness(da[j], db[j], oa[j], ob[j]) for j in range(len(beyond))]
    fresh_range, stale_range = pair_extrema(fa, fb), pair_extrema(pa, pb)
    mhat = max(abs(x) for bounds in (fresh_range, stale_range) for x in bounds)
    s = reference["s"]
    if s == 0:
        threshold, threshold_ratio = None, None
        hybrid_rows, hybrid_status = [], "NOT_EVALUABLE"
    else:
        threshold = mhat/abs(s)
        threshold_ratio = threshold/tint
        hybrid_grid = [threshold*(1+1e-6), threshold*1.01, threshold*2, threshold*4]
        ha, hb, hao, hbo = shifted(hybrid_grid)
        hybrid_rows = []
        for j, h in enumerate(hybrid_grid):
            fresh_bounds = pair_extrema(ha[j] + h*s, hb[j])
            stale_bounds = pair_extrema(hao[j] + h*s, hbo[j])
            # Uniform optimal stationary action over every finite state and
            # every backlog-only observation; stronger than equality in mass.
            ok = (min(*fresh_bounds, *stale_bounds) >= 0 if s > 0 else
                  max(*fresh_bounds, *stale_bounds) < 0)
            hybrid_rows.append(dict(h=h, h_Tint=h/tint, strictly_above_bound=h > threshold,
                                    fresh_gap_range=list(fresh_bounds), stale_gap_range=list(stale_bounds),
                                    common_action="Stay" if s > 0 else "Switch",
                                    status="PASS" if ok and h > threshold else "FAIL"))
        hybrid_status = "PASS" if all(r["status"] == "PASS" for r in hybrid_rows) else "FAIL"
    direct_a = C.m0_gap(lamA, u, kappa, na, [.01, math.inf], "A")
    direct_b = C.m0_gap(lamB, u, kappa, nb, [.01, math.inf], "B")
    arrays_match = bool(np.array_equal(direct_a, arr["dhA"]) and np.array_equal(direct_b, arr["dhB"]))
    if not arrays_match:
        raise AssertionError("evaluate(arrays=True) and m0_gap differ")
    return dict(regime=case["id"], parameters=case["parameters"], N=dict(A=na, B=nb),
                T_int=tint, bar_h=bar_h, bar_h_Tint=bar_h/tint, s=s, M_hat=mhat,
                coincidence_bound=threshold, coincidence_bound_Tint=threshold_ratio,
                a_vhat_constant=dict(status="PASS" if all(r["status"] == "PASS" for r in path_checks.values()) else "FAIL",
                                     paths=path_checks, horizon_grid=beyond, additional_local_grid=local_grid),
                b_literal_fresh_equals_stale=dict(status="PASS" if all(w is None for w in witnesses) else "FAIL",
                                                   meaning="same action for every current state and every stale observation",
                                                   counterexamples=witnesses),
                b_horizon_invariance=dict(status="PASS" if stable else "FAIL", grid=temporal),
                shifted_vs_unshifted_plateau_decisions=representation,
                plateau_gap_ranges=dict(fresh=list(fresh_range), stale=list(stale_range)),
                c_true_s_hybrid=dict(status=hybrid_status, grid=hybrid_rows),
                evaluate_arrays_replay_match=arrays_match, true_V_horizons=["1/100"],
                cpu_s=time.process_time()-start, wall_s=time.perf_counter()-wall)


def main(argv=None):
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=CASES)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    if (args.out / "lemma_checks.json").exists() or (args.out / "lemma").exists():
        raise FileExistsError("lemma outputs already exist")
    start, wall = time.process_time(), time.perf_counter()
    results = []
    for case in json.loads(args.cases.read_text()):
        result = check_regime(case)
        write_json(args.out / "lemma" / f"{case['id']}.json", result)
        results.append(result)
        print(json.dumps({k:result[k] for k in ("regime", "bar_h_Tint", "coincidence_bound_Tint", "cpu_s")}), flush=True)
    labels = ("a_vhat_constant", "b_literal_fresh_equals_stale", "b_horizon_invariance", "c_true_s_hybrid")
    counts = {label: {status:sum(r[label]["status"] == status for r in results)
                      for status in ("PASS", "FAIL", "NOT_EVALUABLE")} for label in labels}
    rows = [dict(regime=r["regime"], T_int=r["T_int"], bar_h=r["bar_h"], bar_h_Tint=r["bar_h_Tint"],
                 M_hat=r["M_hat"], s=r["s"], coincidence_bound=r["coincidence_bound"],
                 coincidence_bound_Tint=r["coincidence_bound_Tint"],
                 **{k:r[k]["status"] for k in labels}, cpu_s=r["cpu_s"]) for r in results]
    write_csv(args.out / "lemma_checks.csv", rows)
    write_json(args.out / "lemma_checks.json", dict(responsible="Doan Van Tai", cases=len(results), counts=counts,
               scope="numerical finite-grid checks over complete truncated state spaces; not a proof or infinite-buffer certificate",
               posterior="ctmc-v1: age 1, old backlog only, stationary conditional mode law",
               M_hat_definition="max absolute summed unshifted saturated gap over every joint state and every pair of posterior means",
               P4_ambiguity="horizon invariance and fresh/stale coincidence are reported separately without changing the card",
               cpu_s=time.process_time()-start, wall_s=time.perf_counter()-wall, regimes=results))
    print(json.dumps(counts), flush=True)


if __name__ == "__main__":
    main()
