"""Independent, read-only numerical replay; does not import p2_tier2.

Doan Van Tai. Run: python3 results/letter/p2_tier2/verify_saved.py [OUTPUT_DIR]
No truth evaluator; all raw inputs stay in the directories allowed by the brief.
The optional one-regime quadrature checks only fluid costs and pi, within item 6.
"""
from collections import Counter, defaultdict
import csv
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
CHECKS = []
START = time.process_time()


def load(path):
    return json.loads(Path(path).read_text())


def expect(label, actual, expected):
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        ok = math.isclose(actual, expected, rel_tol=2e-9, abs_tol=2e-9)
    else:
        ok = actual == expected
    CHECKS.append(dict(name=label, actual=actual, expected=expected, passed=bool(ok)))
    if not ok:
        raise AssertionError(f"{label}: {actual!r} != {expected!r}")


def quantile(values, q):
    a = sorted(float(v) for v in values)
    pos = (len(a) - 1) * q
    i = int(pos)
    return a[i] if i == len(a) - 1 else a[i] + (pos - i) * (a[i + 1] - a[i])


def distribution(label, saved, values, signed=False):
    values = list(values)
    expect(label + " n", len(values), saved["n"])
    for field, q in (("median", .5), ("q25", .25), ("q75", .75), ("q90", .9)):
        expect(label + " " + field, quantile(values, q), saved[field])
    expect(label + " mean", math.fsum(values) / len(values), saved["mean"])
    if signed:
        for field, predicate in (("negative", lambda x: x < 0), ("zero", lambda x: x == 0),
                                 ("positive", lambda x: x > 0), ("abs_le_0p1", lambda x: abs(x) <= .1)):
            expect(label + " " + field, sum(predicate(v) for v in values), saved[field])


ct_raw = [load(p) for p in sorted((ROOT / "results/letter/w1b/raw").glob("*.json"))]
ct_index = {d["id"]: d for d in ct_raw}
with (ROOT / "results/letter/w1b/summary.csv").open() as stream:
    ct_summary = [r for r in csv.DictReader(stream) if r["level"] == "true_s"]
availability = {(r["id"], r["age_label"], F(r["h"])): r["baseline_available"] == "True" for r in ct_summary}

# Fig.3: independently select each nearest raw row; compute every distribution.
f3 = load(OUT / "fig3_iqr.json")
for population, table in f3["tables"].items():
    for entry in table:
        gs, both = [], []
        for d in ct_raw:
            age = next(a for a in d["evaluations"] if a["age_label"] == "Tint_1")
            r = min(age["h"], key=lambda x: abs(math.log(x["h_Tint"] / entry["h_Tint"])))
            if population == "ledger92" and not availability[d["id"], "Tint_1", F(r["h"])]:
                continue
            pipe = entry["pipeline"]
            if pipe == "M0":
                gs.append(r["G_S"])
                both.append(max(r["regret"]["M0_new"], r["regret"]["M0_old"]))
            elif pipe == "Hybrid":
                h = r["hybrid_levels"]["true_s"]
                gs.append(h["G_S"])
                both.append(max(h["regret_new"], h["regret_old"]))
            else:
                gs.append(0.)
                both.append(r["regret"]["static"])
        label = f"Fig3 {population} {entry['pipeline']} {entry['h_Tint']}"
        distribution(label + " GS", entry["GS"], gs, signed=True)
        distribution(label + " regret", entry["both_side_regret"], both)

# Fig.4 and all GEANT paired SE: reconstruct from the same saved instances.
geant = []
f4 = load(OUT / "fig4a_signed.json")
for directory, seed in (("e4", 3000001), ("e4b", 5000001)):
    training = {r["regime"]: r["rhat"]["i"] for r in load(ROOT / f"results/letter/{directory}/training_checks.json")["regimes"]}
    for regime, rates in training.items():
        pieces = []
        for path in sorted((ROOT / f"results/letter/{directory}/raw").glob(regime + "_chunk*.npz")):
            with np.load(path) as z:
                pieces.append({k: z[k] for k in ("V", "decisions", "h_mult", "tau_mult", "pipelines")})
        v = np.concatenate([p["V"] for p in pieces])
        decisions = np.concatenate([p["decisions"] for p in pieces])
        names = pieces[0]["pipelines"].tolist()
        for ti, tau in enumerate(pieces[0]["tau_mult"]):
            for hi, h in enumerate(pieces[0]["h_mult"]):
                # Gather by explicit Python per-instance loop, separately from
                # the vectorized production replay.
                cref = math.fsum(v[i, decisions[i, names.index("M1_new"), 0, 0, hi], hi] for i in range(500)) / 500
                static = np.array([v[i, int(np.argmin(rates)), hi] for i in range(500)])
                costs = {}
                for pipe, name in (("M0", "M0"), ("Hybrid", "Hybrid-i")):
                    costs[pipe] = np.array([[v[i, decisions[i, names.index(name), side, ti, hi], hi]
                                             for side in range(2)] for i in range(500)])
                worst = max(range(2), key=lambda side: math.fsum(costs["Hybrid"][:, side]))
                differences = 100 / cref * (costs["Hybrid"][:, worst] - static)
                se = float(np.std(differences, ddof=1) / math.sqrt(500))
                row = dict(dataset=directory, seed=seed, regime=regime, tau=float(tau), h=int(h),
                           stationary=100 / cref * (math.fsum(static) / 500 - cref), paired_se=se)
                for pipe in ("M0", "Hybrid"):
                    means = [math.fsum(costs[pipe][:, side]) / 500 for side in range(2)]
                    # Strict signed counts use the saved paired arithmetic, to
                    # avoid changing a 1-ulp zero through a different reduction.
                    csvrow = next(r for r in f4["observations"]
                                  if r["dataset"] == directory and r["regime"] == regime and r["h_target"] == int(h)) if tau == 1 else None
                    row[pipe] = dict(GS=100 / cref * (means[1] - means[0]),
                                     both=100 / cref * (max(means) - cref))
                    if tau == 1:
                        expect(f"Fig4 raw GS {directory} {regime} {h} {pipe}", row[pipe]["GS"], csvrow["pipelines"][pipe]["GS"])
                geant.append(row)

for entry in f4["tables"]:
    pop = [r for r in geant if r["tau"] == 1 and r["h"] == entry["h_Tint"]
           and (entry["dataset"] == "both_seeds" or r["dataset"] == entry["dataset"])]
    if entry["pipeline"] == "Stationary":
        values = [0.] * len(pop)
    else:
        values = [r[entry["pipeline"]]["GS"] for r in pop]
    distribution(f"Fig4 {entry['dataset']} {entry['h_Tint']} {entry['pipeline']}", entry["GS"], values)
    # Strict sign counts are independently available in cells.csv; their GS
    # reduction is the one used by the original experiment.
    if entry["pipeline"] != "Stationary":
        csv_values = []
        for directory in ("e4", "e4b"):
            if entry["dataset"] not in (directory, "both_seeds"):
                continue
            with (ROOT / f"results/letter/{directory}/cells.csv").open() as stream:
                csv_values.extend(float(r["G_S_pct"]) for r in csv.DictReader(stream)
                                  if float(r["tau_mult"]) == 1 and int(r["h_mult"]) == entry["h_Tint"]
                                  and r["pipeline"] == ("M0" if entry["pipeline"] == "M0" else "Hybrid-i"))
        for field, predicate in (("negative", lambda x: x < 0), ("positive", lambda x: x > 0), ("abs_le_0p1", lambda x: abs(x) <= .1)):
            expect(f"Fig4 strict {entry['dataset']} {entry['h_Tint']} {entry['pipeline']} {field}",
                   sum(predicate(v) for v in csv_values), entry["GS"][field])

# E6: independent record loop; no exchange of max and mean.
e6 = load(OUT / "e6_replay.json")
cells, signs = [], defaultdict(list)
for path in sorted((ROOT / "results/letter/e6/raw").glob("*.npz")):
    seed, regime = path.stem.split("_", 1)
    with np.load(path) as z:
        for li, L in enumerate(z["L_Tint"]):
            if L not in (100, 300):
                continue
            if seed == "3000001":
                tr = next(r for r in load(ROOT / "results/letter/e4/training_checks.json")["regimes"] if r["regime"] == regime)["rhat"]["i"]
                for rates in z["record_rates"][:, li]:
                    signs[int(L)].append(np.sign(rates[1] - rates[0]) != np.sign(tr[1] - tr[0]))
            for ti, tau in enumerate(z["tau_mult"]):
                for hi, h in enumerate(z["h_mult"]):
                    hy = math.fsum(max(z["regret_hybrid"][rep, li, 0, ti, hi], z["regret_hybrid"][rep, li, 1, ti, hi]) for rep in range(200)) / 200
                    st = math.fsum(z["regret_static"][:, li, hi]) / 200
                    m = next(r for r in geant if r["seed"] == int(seed) and r["regime"] == regime and r["tau"] == tau and r["h"] == h)
                    cells.append(dict(L=int(L), h=int(h), M0=m["M0"]["both"], Hybrid=hy, Stationary=st))
for entry in e6["tables"]:
    values = [r[entry["pipeline"]] for r in cells if r["L"] == entry["L_Tint"] and r["h"] == entry["h_Tint"]]
    distribution(f"E6 {entry['L_Tint']} {entry['h_Tint']} {entry['pipeline']}", entry["regret"], values)
for entry in e6["long_h15_h30"]:
    values = [r[entry["pipeline"]] for r in cells if r["L"] == entry["L_Tint"] and r["h"] in (15, 30)]
    distribution(f"E6 long {entry['L_Tint']} {entry['pipeline']}", entry["regret"], values)
for entry in e6["sign_error"]:
    expect(f"E6 sign {entry['L_Tint']} n", len(signs[entry["L_Tint"]]), entry["n_unique_records"])
    expect(f"E6 sign {entry['L_Tint']} wrong", int(sum(signs[entry["L_Tint"]])), entry["wrong"])

# Paired comparisons, including validation of every stored GEANT paired SE.
paired = load(OUT / "paired_by_h.json")
for row in paired["observations"]:
    p = row["paired"]
    if row["dataset"] in ("e4", "e4b"):
        raw = next(r for r in geant if r["dataset"] == row["dataset"] and r["regime"] == row["regime"]
                   and r["tau"] == row["tau_Tint"] and r["h"] == row["h_target"])
        expect(f"paired SE {row['dataset']} {row['regime']} {row['tau_Tint']} {row['h_target']}", raw["paired_se"], p["paired_se_pp"])
    tolerance = 1e-9 * max(abs(p["hybrid"]), abs(p["stationary"]))
    delta = p["hybrid"] - p["stationary"]
    equal = abs(delta) <= tolerance or (p["paired_se_pp"] is not None and abs(delta) <= 2 * p["paired_se_pp"])
    label = "equal" if equal else "better" if delta < 0 else "worse"
    expect("paired classification", label, p["comparison"])
for entry in paired["tables"]:
    pop = [r for r in paired["observations"] if (r["dataset"] == entry["dataset"]
           or (entry["dataset"] == "GEANT_both_seeds" and r["dataset"] in ("e4", "e4b")))
           and r["h_target"] == entry["h_Tint"] and (entry["age_scope"] == "all_saved_ages"
           or (r.get("age_label") == "Tint_1" if r["dataset"] == "CTMC" else r["tau_Tint"] == 1))]
    counts = Counter(r["paired"]["comparison"] for r in pop)
    for label in ("better", "equal", "worse"):
        expect("paired table " + label, counts[label], entry[label])
    distribution("paired delta table", entry["delta"], [r["paired"]["delta_pp"] for r in pop])

# C2/C3/M2 subgroup replays directly from the original summary and raw ties.
splits = load(OUT / "optimal_sign_splits.json")
for entry in splits["tables"][:3]:
    sg = None if entry["group"] == "ALL" else -1 if entry["group"].startswith("Switch") else 1
    pop = [r for r in ct_summary if sg is None or (float(r["s_true"]) > 0) - (float(r["s_true"]) < 0) == sg]
    harm = [r for r in pop if r["baseline_available"] == "True" and float(r["tau_Tint"]) >= 1 and float(r["h_Tint"]) >= 3]
    regret = [r for r in pop if float(r["tau_Tint"]) >= 1 and float(r["h_Tint"]) >= 1]
    expect("split harm denominator", len(harm), entry["harm_n"])
    expect("split harmed", sum(float(r["G_S_M0_age"]) < -.1 for r in harm), entry["harmful"])
    distribution("split fresh", entry["fresh_regret"], [float(r["M0_new"]) for r in regret])
    distribution("split stale", entry["stale_regret"], [float(r["M0_old"]) for r in regret])
    tie_fresh, tie_stale = [], []
    for d in ct_raw:
        if sg is not None and int(np.sign(d["s"])) != sg:
            continue
        a = next(a for a in d["evaluations"] if a["age_label"] == "Tint_1")
        r = min(a["h"], key=lambda x: abs(math.log(x["h_Tint"] / 30)))
        tie_fresh.append(r["tie_mass"]["c10"])
        tie_stale.append(r["tie_mass"]["c00"])
    distribution("split fresh ties", entry["fresh_tie"], tie_fresh)
    distribution("split stale ties", entry["stale_tie"], tie_stale)

# Primitives: all signs/components and saved finite-age shares checked separately.
primitive = load(OUT / "primitive_signs.json")
for row in primitive["observations"]:
    expect("m0 additive expectation", row["components"]["A"] + row["components"]["B"], row["m0"])
    expect("m0 sign", int(np.sign(row["m0"])), row["sign_m0"])
    expect("s sign", int(np.sign(ct_index[row["regime"]]["s"])), row["sign_s"])
    for target in (1, 3):
        a = next(a for a in ct_index[row["regime"]]["evaluations"] if a["age_label"] == f"Tint_{target}")
        r = min(a["h"], key=lambda x: abs(math.log(x["h_Tint"] / 30)))
        good = r["shares"]["M0_old"] if row["s"] < 0 else 1 - r["shares"]["M0_old"]
        expect("primitive saved good-action share", good, row["stale"][str(target)]["long_run_action_share"])
for entry in primitive["tables"]:
    pop = [r for r in primitive["observations"] if entry["group"] == "ALL"
           or (r["s"] < 0 if entry["group"].startswith("Switch") else r["s"] > 0)]
    expect("primitive sign agreement", sum(r["sign_m0"] == r["sign_s"] for r in pop), entry["sign_agree"])

# V-C: regenerate counts from cases.csv, including prose factorization.
with (ROOT / "results/letter/v7_3/test_congested/score_dev1/cases.csv").open() as stream:
    cases = list(csv.DictReader(stream))
denom = load(OUT / "vc_denominators.json")
for entry in denom["by_flow"]:
    pop = [r for r in cases if r["regime"] == entry["regime"]]
    for s in ("S", "O"):
        group = [r for r in pop if r["stratum"] == s]
        expect("V-C strata days", len({r["date"] for r in group}), entry[s + "_days"])
        expect("V-C evaluable flow", sum(r["evaluable"] == "True" for r in group), entry[s + "_evaluable"])
o_counts = [sum(r["evaluable"] == "True" and r["stratum"] == "O" and r["regime"] == flow for r in cases)
            for flow in ("DAY1", "DAY2", "DAY3")]
prose_counts = [int(s) for s in re.search(r"per-flow ([0-9+]+)", denom["factorizations"]["408"]).group(1).split("+")]
expect("V-C 408 factorization per flow", prose_counts, o_counts)
primary = [r for r in cases if r["regime"] in ("DAY1", "DAY2") and r["stratum"] == "S" and int(r["h_hours"]) in (2, 4, 6)]
evaluable = [r for r in primary if r["evaluable"] == "True"]
expect("V-C 348", len(primary), 348)
expect("V-C 76", len(evaluable), 76)
expect("V-C 408", sum(o_counts), 408)
expect("V-C 1216", len({(r["regime"], r["date"], r["h_hours"]) for r in evaluable}) * 32, 1216)

hashes = load(OUT / "input_sha256.json")
for label, digest in hashes.items():
    path = Path(label) if Path(label).is_absolute() else ROOT / label
    expect("input hash " + label, hashlib.sha256(path.read_bytes()).hexdigest(), digest)
result = dict(status="PASS", checks=len(CHECKS), cpu_s=time.process_time() - START,
              methods="Independent selection and Python-loop raw-cost gathering; manual sorted linear quantiles; original CSV sign checks; no import of production replay; no truth calls",
              primitive_limit="m0 arithmetic/signs and saved shares independently checked; full primitive recomputation is reproducible via the production command",
              source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), details=CHECKS)
with (OUT / "independent_verification.json").open("x") as stream:
    json.dump(result, stream, indent=2, allow_nan=False)
    stream.write("\n")
print(json.dumps({k: v for k, v in result.items() if k != "details"}))
