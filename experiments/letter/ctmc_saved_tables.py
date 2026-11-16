"""Doan Van Tai — descriptive tables from existing CTMC JSONs only.

Each saved case/horizon is a row; keep overlaps between design sources, flags,
and zero-sign mismatches visible. No evaluator is imported or called here.
"""
import argparse
from collections import Counter, defaultdict
import csv
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/letter/w1a"
PIPES = ("M0_new", "M0_old", "hybrid_new", "hybrid_old",
         "hybrid_mm1_new", "hybrid_mm1_old", "static")
BINS = ("<1", "1-4", "4-7", "7-15", ">=15")


def horizon_bin(value):
    if value < 1:
        return BINS[0]
    if value < 4:
        return BINS[1]
    if value < 7:
        return BINS[2]
    if value < 15:
        return BINS[3]
    return BINS[4]


def sign(value):
    return int(value > 0) - int(value < 0)


def sign_kind(s, s_mm1):
    a, b = sign(s), sign(s_mm1)
    if a == b:
        return "agree"
    if a*b == -1:
        return "opposite_nonzero"
    return "true_zero_mm1_nonzero" if a == 0 else "true_nonzero_mm1_zero"


def median(values):
    return float(np.median(values)) if len(values) else None


def q90(values):
    return float(np.quantile(values, .9, method="linear")) if len(values) else None


def aggregate(rows, source, bin_name):
    n = len(rows)
    mismatch = [r for r in rows if r["sign_kind"] != "agree"]
    opposite = [r for r in rows if r["sign_kind"] == "opposite_nonzero"]
    result = dict(source=source, h_Tint_bin=bin_name, rows=n,
                  cases=len({r["input_file"] for r in rows}),
                  M0_new_tie_mass_median=median([r["M0_new_tie_mass"] for r in rows]),
                  M0_new_tie_mass_q90=q90([r["M0_new_tie_mass"] for r in rows]),
                  GS_below_minus_0p1_count=sum(r["G_S"] < -.1 for r in rows),
                  GS_below_minus_0p1_share=sum(r["G_S"] < -.1 for r in rows)/n if n else None,
                  flagged_rows=sum(bool(r["flags"]) for r in rows),
                  sign_agreement_count=n-len(mismatch), sign_agreement_share=(n-len(mismatch))/n if n else None,
                  sign_mismatch_rows=len(mismatch), opposite_nonzero_rows=len(opposite),
                  true_zero_mm1_nonzero_rows=sum(r["sign_kind"] == "true_zero_mm1_nonzero" for r in rows),
                  true_nonzero_mm1_zero_rows=sum(r["sign_kind"] == "true_nonzero_mm1_zero" for r in rows))
    for pipe in PIPES:
        result[f"regret_{pipe}_median_pct_Cref"] = median([r[f"regret_{pipe}"] for r in rows])
    for pipe in ("hybrid_mm1_new", "hybrid_mm1_old"):
        for label, subset in (("sign_mismatch", mismatch), ("opposite_nonzero", opposite)):
            values = [r[f"regret_{pipe}"] for r in subset]
            result[f"{label}_{pipe}_median_pct_Cref"] = median(values)
            result[f"{label}_{pipe}_q90_pct_Cref"] = q90(values)
    return result


def load_saved(root=ROOT):
    paths = sorted([*(root / "results/explore_ctmc/runs").glob("*/*.json"),
                    *(root / "results/explore_ctmc/runs_l72").glob("*/*.json")])
    rows, manifest, excluded, cases = [], {}, [], []
    for path in paths:
        payload = path.read_bytes()
        rel = str(path.relative_to(root))
        manifest[rel] = hashlib.sha256(payload).hexdigest()
        d = json.loads(payload)
        source = "/".join(path.parts[-3:-1])
        if d.get("status") != "COMPLETED":
            excluded.append(dict(input_file=rel, source=source, status=d.get("status"),
                                 reason=d.get("error", "not COMPLETED"), rows=len(d.get("h", []))))
            continue
        cases.append(dict(input_file=rel, source=source, s=d["s"], s_mm1=d["s_mm1"],
                          sign_kind=sign_kind(d["s"], d["s_mm1"])))
        for i, row in enumerate(d.get("h", [])):
            required = all(p in row.get("regret", {}) for p in PIPES)
            if not required or "c10" not in row.get("tie_mass", {}) or "G_S" not in row:
                raise ValueError(f"completed row missing required data: {rel}:{i}")
            key = [str(F(str(d.get("a", 6)))), *(str(F(x)) for x in d["parameters"]),
                   str(F(row["h"])), str(F(str(d.get("tau", 1))))]
            data = dict(input_file=rel, row_index=i, source=source, regime=d.get("id", path.stem),
                        physical_key="|".join(key), h=row["h"], h_Tint=row["h_Tint"],
                        h_Tint_bin=horizon_bin(row["h_Tint"]), M0_new_tie_mass=row["tie_mass"]["c10"],
                        G_S=row["G_S"], flags=json.dumps(row.get("flags", []), separators=(",", ":")) if row.get("flags") else "",
                        s=d["s"], s_mm1=d["s_mm1"], sign_kind=cases[-1]["sign_kind"])
            data.update({f"regret_{p}":row["regret"][p] for p in PIPES})
            nums = [data["h_Tint"], data["M0_new_tie_mass"], data["G_S"], data["s"], data["s_mm1"],
                    *(data[f"regret_{p}"] for p in PIPES)]
            if not np.isfinite(nums).all():
                raise ValueError(f"nonfinite saved values: {rel}:{i}")
            rows.append(data)
    return rows, cases, excluded, manifest


def write_csv(path, rows):
    with Path(path).open("x", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    if (args.out / "ctmc_saved_tables.json").exists():
        raise FileExistsError("saved-data outputs already exist")
    start, wall = time.process_time(), time.perf_counter()
    rows, cases, excluded, manifest = load_saved()
    groups = defaultdict(list)
    for row in rows:
        groups[row["source"], row["h_Tint_bin"]].append(row)
    sources = sorted({r["source"] for r in rows})
    tables = [aggregate(groups[source, b], source, b) for source in sources for b in BINS]
    pooled = [aggregate([r for r in rows if r["h_Tint_bin"] == b], "ALL_SOURCES_POOLED", b) for b in BINS]
    sign_cases = []
    for source in [*sources, "ALL_SOURCES_POOLED"]:
        group = [r for r in cases if r["source"] == source] if source != "ALL_SOURCES_POOLED" else cases
        counts = Counter(r["sign_kind"] for r in group)
        sign_cases.append(dict(source=source, cases=len(group),
                               sign_agreement_cases=counts["agree"],
                               sign_agreement_share=counts["agree"]/len(group),
                               opposite_nonzero_cases=counts["opposite_nonzero"],
                               true_zero_mm1_nonzero_cases=counts["true_zero_mm1_nonzero"],
                               true_nonzero_mm1_zero_cases=counts["true_nonzero_mm1_zero"]))
    unique = Counter(r["physical_key"] for r in rows)
    intra = Counter((r["source"], r["physical_key"]) for r in rows)
    mismatch = [r for r in rows if r["sign_kind"] != "agree"]
    write_csv(args.out / "ctmc_saved_rows.csv", rows)
    write_csv(args.out / "ctmc_saved_tables.csv", tables)
    write_csv(args.out / "ctmc_saved_pooled.csv", pooled)
    write_csv(args.out / "ctmc_sign_by_source.csv", sign_cases)
    # Keep a header even if no mismatch occurs in another saved-data snapshot.
    with (args.out / "ctmc_sign_mismatch_rows.csv").open("x", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(mismatch)
    result = dict(responsible="Doan Van Tai", input_files=len(manifest), completed_files=len(cases),
                  excluded_files=len(excluded), saved_horizon_rows=len(rows),
                  source_file_counts=dict(Counter(r["source"] for r in cases)),
                  unique_physical_horizon_keys=len(unique),
                  repeated_physical_horizon_rows=sum(v-1 for v in unique.values()),
                  repeated_rows_within_source=sum(v-1 for v in intra.values()),
                  units=dict(regret="percent of row C_ref", G_S="percent of row C_ref", tie_mass="stationary probability mass"),
                  tie_definition="saved tie_mass.c10: tolerance 1e-12*(h*r_stay+1), not an exact-tie counter",
                  weighting="one saved case/horizon row; design-source overlaps retained, not independent samples",
                  bins="[0,1), [1,4), [4,7), [7,15), [15,infinity); saved h_Tint used without rounding",
                  sign_definition="strict sign(s_mm1)==sign(s); zero/nonzero mismatch separately from opposite nonzero signs; no epsilon",
                  tables=tables, pooled_tables=pooled, sign_by_source=sign_cases,
                  excluded=excluded, cpu_s=time.process_time()-start, wall_s=time.perf_counter()-wall)
    for name, content in (("ctmc_saved_tables.json", result), ("ctmc_saved_input_hashes.json", manifest)):
        with (args.out / name).open("x") as f:
            json.dump(content, f, indent=2, allow_nan=False)
            f.write("\n")
    print(json.dumps({k:result[k] for k in ("input_files", "completed_files", "excluded_files", "saved_horizon_rows", "unique_physical_horizon_keys", "cpu_s", "wall_s")}), flush=True)


if __name__ == "__main__":
    main()
