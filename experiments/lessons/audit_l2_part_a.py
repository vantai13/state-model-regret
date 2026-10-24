"""Independently replay finite toy artifacts, without importing the lesson scorer.

Responsible: Doan Van Tai; AI-assisted. This is an artifact audit, not a human
independent scientific review. Run after both lesson CLIs and report creation.
"""
from collections import Counter
import csv
from fractions import Fraction as F
from functools import lru_cache
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def terminal(a, b, action):
    # One-slot mass balance, independently written from the lesson helper.
    load = (2, 0) if action == 0 else (0, 2)
    arrivals = (a, b)
    return sum(max(F(0), arrivals[k] + load[k] - 3) for k in (0, 1))


@lru_cache(None)
def costs(A, B):
    J = tuple(sum(terminal(a, b, action) for a, b in product(A, B)) / 4 for action in (0, 1))
    J0 = tuple(terminal(F(sum(A), 2), F(sum(B), 2), action) for action in (0, 1))
    WS = sum(min(terminal(a, b, 0), terminal(a, b, 1)) for a, b in product(A, B)) / 4
    return J, J0, WS


def reference(A, Bh, Bl):
    jh, mh, wh = costs(A, Bh)
    jl, ml, wl = costs(A, Bl)
    J, M = (jh, jl), (mh, ml)
    avg = lambda pairs: tuple((pairs[0][a] + pairs[1][a]) / 2 for a in (0, 1))
    choose = lambda pair: 1 if pair[1] < pair[0] else 0
    EJ = avg(J)
    a00, a01 = choose(avg(M)), choose(EJ)
    L00, L01 = EJ[a00], EJ[a01]
    L10 = sum(J[m][choose(M[m])] for m in (0, 1)) / 2
    L11 = sum(min(J[m]) for m in (0, 1)) / 2
    delta = (jh[1] - jh[0], jl[1] - jl[0])
    P = sum(max(F(0), d) for d in delta) / 2
    N = sum(max(F(0), -d) for d in delta) / 2
    ev_inputs = (F(sum(A), 2), F(sum(Bh) + sum(Bl), 4))
    ev_costs = tuple(terminal(*ev_inputs, a) for a in (0, 1))
    EEV = EJ[choose(ev_costs)]
    row = dict(L00=L00, L01=L01, L10=L10, L11=L11,
               GS=L00-L10, GM=L00-L01, GSM=L00-L11,
               Gam=L10+L01-L00-L11, GSgM1=L01-L11, GMgS1=L10-L11,
               EVPPI=min(EJ)-L11, EVSS=L10-L11, WS=(wh+wl)/2,
               RP=min(EJ), EV=min(ev_costs), EEV=EEV, Dplus=P, Dminus=N)
    wrong_EJ = tuple((3*jh[a] + jl[a])/4 for a in (0, 1))
    wrong_gain = EJ[choose(wrong_EJ)] - L11
    subjective = min(wrong_EJ) - (3*min(jh)+min(jl))/4
    ignored_mode_gain = EEV-L11
    diag = dict(wrong_prior_i1=wrong_gain != row["EVPPI"],
                wrong_prior_up=wrong_gain > row["EVPPI"],
                wrong_prior_down=wrong_gain < row["EVPPI"],
                mean_state_L00_changed=EEV != L00, tie_sw_i1_fail=False,
                ignores_mode_i2=ignored_mode_gain != row["EVSS"],
                tautological_i2_fail=False, GS_negative=L00 < L10,
                Gamma_positive=row["Gam"] > 0, Gamma_negative=row["Gam"] < 0,
                Gamma_zero=row["Gam"] == 0, M0_better_global_EV=L00 < EEV,
                M0_worse_global_EV=L00 > EEV, EV_above_WS=row["EV"] > row["WS"],
                EV_above_RP=row["EV"] > row["RP"],
                subjective_objective_differ=subjective != row["EVPPI"])
    return row, diag


def run():
    out = ROOT / "results/lessons/part_a"
    summary = json.loads((ROOT / "results/lessons/l2_2/voi_mapping.json").read_text())
    pairs = tuple(combinations(range(8), 2))
    expected_inputs = set(product(pairs, repeat=3))
    seen, counts = set(), Counter()
    with (ROOT / "results/lessons/l2_2/cases.csv").open(newline="") as stream:
        for row in csv.DictReader(stream):
            key = tuple(tuple(int(row[p+str(i)]) for i in (0, 1)) for p in ("A", "Bh", "Bl"))
            assert key not in seen, ("duplicate", key)
            seen.add(key)
            expected, diag = reference(*key)
            for k, v in expected.items():
                assert F(row[k]) == v, (key, k, row[k], v)
            for k, v in diag.items():
                assert int(row[k]) == int(v), (key, k)
            counts.update({k: int(v) for k, v in diag.items()})
            assert all(row[f"I{i}"] == "1" for i in range(1, 7))
    assert seen == expected_inputs
    assert len(seen) == summary["cases"] == 21952
    assert dict(counts) == summary["counts"]
    p11 = json.loads((ROOT / "results/lessons/l2_3/p11_toy.json").read_text())
    expected_p11 = [("St", "1/4", "1/2"), ("Sw", "1/4", "0"),
                    ("St", "0", "1/2"), ("Sw", "0", "0")]
    assert [(r["action"], r["EVPI_delta"], r["true_regret"]) for r in p11["rows"]] == expected_p11
    with (ROOT / "results/lessons/l2_3/p11_toy.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert [(r["action"], r["EVPI_delta"], r["true_regret"]) for r in rows] == expected_p11
    assert p11["check_count"] == 17 == len(set(p11["checks"]))
    assert p11["hidden_state_disclosure"] == {"baseline": "11/4", "informed": "5/2", "value": "1/4"}
    for script, result in [("l2_2_voi_mapping.py", summary), ("l2_3_p11.py", p11)]:
        assert hashlib.sha256((ROOT / "experiments/lessons" / script).read_bytes()).hexdigest() == result["source_sha256"]
    docs = list((ROOT / "notes/literature").rglob("*.md"))
    docs += [ROOT / "notes/theory/T03_primary_reading_start.md", out / "report.md",
             ROOT / "notes/lessons/L2_part_a_review.md"]
    checked_links = 0
    for path in docs:
        assert path.is_file(), path
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if target.startswith(("http:", "https:", "mailto:", "#")):
                continue
            local = target.split("#", 1)[0]
            if (path.parent / local).resolve() == out / "artifact_audit.json":
                continue  # Written below only after all checks succeed.
            assert (path.parent / local).resolve().exists(), (str(path), target)
            checked_links += 1
    assert not list((ROOT / "notes/literature").rglob("*.pdf"))
    result = dict(status="PASS", independent_csv_rows=len(seen),
                  l2_3_checks=p11["check_count"], local_links_checked=checked_links,
                  source_hashes_match=True, no_pdfs_in_literature_repo=True,
                  scope="artifact/finite-toy audit; not human independent review")
    (out / "artifact_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result


if __name__ == "__main__":
    run()
