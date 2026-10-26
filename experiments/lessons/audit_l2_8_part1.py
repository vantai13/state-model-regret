"""Verify L2.8 Part1 audit ledger and preservation. Responsible: Doan Van Tai."""
import csv
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"results/lessons/l2_8/part1"


def main():
    data=json.loads((OUT/"search_records.json").read_text())
    with (OUT/"screening.csv").open() as f:rows=list(csv.DictReader(f))
    counts={p:len(data[p]["records"]) for p in ["query1","query2","forward"]}
    assert counts==dict(query1=20,query2=15,forward=20) and len(rows)==55
    for p in counts:
        assert [int(r["rank"]) for r in rows if r["pass_name"]==p]==list(range(1,counts[p]+1))
    assert data["forward"]["offset"]==0 and data["forward"]["next"]==20 and data["forward"]["calls"]==2
    assert all(not data[p]["errors"] for p in ["query1","query2"])
    proposals={r["identifier"] for r in rows if r["decision"].startswith("Tier2")}
    assert proposals=={"10.1287/moor.2025.0898","2308.13166","2211.01961"}
    protected=json.loads((OUT/"protected_before.json").read_text())
    for p,h in protected["files"].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    provenance=json.loads((OUT/"archive_provenance.json").read_text())
    for p in provenance:assert hashlib.sha256(Path(p["path"]).read_bytes()).hexdigest()==p["sha256"]
    math=json.loads((OUT/"math_checks.json").read_text())
    assert sum((F(max(0,b-10),2) for b in [2,14]),F(0))==F(math["jensen"]["expected_backlog"])==2
    assert max(0,F(2+14,2)-10)==F(math["jensen"]["mean_rollout_backlog"])==0
    assert len(math["identity_cases"])==9
    for c in math["identity_cases"]:
        gs,known,gamma=map(F,(c["GS"],c["GSgivenM1"],c["Gamma"]))
        assert gs<0<=known and gamma==known-gs>0
    sums=(ROOT/"results/lessons/part_a/SHA256SUMS").read_text().splitlines();assert len(sums)==52
    for line in sums:
        h,p=line.split("  ",1);assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    result=dict(artifact_status="PASS",responsible="Doan Van Tai",session="A4 bounded screening only",
                query_records=counts,total_screen_records=55,unique_identifiers=len({r["identifier"] for r in rows}),
                new_Tier2_proposals=len(proposals),approved_new_PDFs=0,primary_abstracts=3,
                full_primary_read_this_session=False,protected_files_unchanged=len(protected["files"]),
                math_identity_cases=9,jensen_expected=2,jensen_mean_rollout=0,
                stopping_rule_met=False,forward_exhausted=False,A1_A2_A3="NOT_RUN",
                whole_L2_8_status="OPEN_PART2_AND_REMAINING_SESSIONS",workbook_changed=False,grid_run=False)
    (OUT/"verification.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False))


if __name__=="__main__":main()
