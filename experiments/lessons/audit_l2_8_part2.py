"""Audit retained Part2 artifacts; no claim of full search replay. Doan Van Tai."""
import csv
from decimal import Decimal as D, getcontext, localcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

from openpyxl import load_workbook

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"results/lessons/l2_8/part2"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    getcontext().prec=65
    protected=json.loads((OUT/"protected_before.json").read_text())
    assert len(protected["files"])==1186
    for p,h in protected["files"].items():
        assert sha(ROOT/p)==h,p
    # Preserve the entire historical PC table/prefix while appending evidence.
    prior="notes/literature/prior_boundary.md"
    old=subprocess.check_output(["git","show",protected["baseline_commit"]+":"+prior])
    assert (ROOT/prior).read_bytes().startswith(old)

    ledger=json.loads((OUT/"search_calls.json").read_text())
    calls=ledger["calls"]
    assert len(calls)==20 and len({c["call_id"] for c in calls})==20
    assert sum(c["screened_records"] for c in calls)==169
    assert {a:sum(c["screened_records"] for c in calls if c["call_id"].startswith(a+"_"))
            for a in ["A1","A2","A3"]}==dict(A1=44,A2=45,A3=60)
    assert all(0<=c["screened_records"]<=c["returned_records"]<=20 for c in calls)
    selected={p for c in calls for p in c["selected_new_for_reading"]}
    assert selected=={"NDT26","WM26","AIS22"}
    approval=json.loads((OUT/"author_approval.json").read_text())
    assert approval["approval"]=="Duyệt cả 3" and len(approval["sources"])==3
    assert not ledger["rank_level_raw_retained"] and not ledger["stopping_rule_met"]
    assert ledger["candidate_total_unique"] is None

    # Read generated CSV, aggregate its conditional branch, compare with independent
    # Poisson truncated-first-moment formulas (no Monte Carlo).
    with (OUT/"cooper_example1.csv").open() as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==18
    assert len({(r["first_high"],r["second_high"],r["second_low"]) for r in rows})==18
    with localcontext() as ctx:
        ctx.prec=65
        q=(-D(1)).exp(); tol=D("1e-45")
        total=sum(D(r["probability"]) for r in rows)
        no=sum(D(r["probability"])*D(r["initial_policy_revenue"]) for r in rows)
        yes=sum(D(r["probability"])*D(r["resolving_revenue"]) for r in rows)
        assert abs(total-1)<tol
        assert abs(no-(20-40*q*q))<tol
        assert abs(no-yes-(8*q-18*q*q))<tol and no>yes
        branch=[r for r in rows if r["first_high"]=="0"]
        bmass=sum(D(r["probability"]) for r in branch)
        assert abs(bmass-q)<tol
        for key,target in [("initial_policy_revenue",20-30*q),("resolving_revenue",12*(1-q))]:
            assert abs(sum(D(r["probability"])*D(r[key]) for r in branch)/bmass-target)<tol
    with (OUT/"v1_diagnostic.csv").open() as f:
        diag=list(csv.DictReader(f))
    assert len(diag)==2
    for r in diag:
        p,a,b,g=map(F,(r["predicted_improvement"],r["old_underestimate"],
                       r["new_underestimate"],r["true_improvement"]))
        assert p+a-b==g and g>=-F(r["one_sided_epsilon"])
    assert sum(F(r["true_improvement"]) for r in diag)/2==F(-1,4)
    math=json.loads((OUT/"math_checks.json").read_text())
    assert abs(D(math["loss_from_resolving"])-(no-yes))<D("1e-45")

    access=json.loads((OUT/"source_access.json").read_text())
    assert len(access["sources"])==6
    for s in access["sources"]:
        pdf=Path(s["local_pdf"])
        assert pdf.read_bytes().startswith(b"%PDF-") and sha(pdf)==s["sha256"]
        assert not pdf.resolve().is_relative_to(ROOT)
        info=subprocess.check_output(["pdfinfo",str(pdf)],text=True)
        assert int(re.search(r"^Pages:\s+(\d+)",info,re.M)[1])==s["pdf_pages"]
        for im in s["rendered_and_viewed"]:
            assert sha(Path(im["path"]))==im["sha256"]
        if "historical_AI_T_note" in s:
            n=s["historical_AI_T_note"];assert sha(Path(n["path"]))==n["sha256"]
        assert s["author_L_self"]=="Not established"

    backup=Path.home()/"papers/state-model-regret/archive/2026-10-26_before_l2_8_part2"
    oldbook=load_workbook(backup/"paper_comparison.xlsx")
    newbook=load_workbook(ROOT/"papers/paper_comparison.xlsx")
    notes=lambda b:{r[0]:list(r) for r in b["Ghi_chu_doc"].iter_rows(min_row=2,values_only=True)}
    levels=lambda b:{r[0]:r[11] for r in b["Danh_sach"].iter_rows(min_row=2,values_only=True)}
    before,after=notes(oldbook),notes(newbook)
    assert len(before)==13 and len(after)==19
    assert all(after[k]==v for k,v in before.items())
    a,b=levels(oldbook),levels(newbook);assert all(b[k]==v for k,v in a.items())
    assert all(b[k]=="Chưa có xác nhận" for k in selected|{"R01","R02","R04"})
    oldbook.close();newbook.close()
    cat=json.loads((ROOT/"papers/data/catalog.json").read_text())["papers"]
    oldcat=json.loads((backup/"catalog.json").read_text())["papers"]
    assert cat[6:]==oldcat and {c["id"] for c in cat[:6]}==selected|{"R01","R02","R04"}
    sums=(ROOT/"results/lessons/part_a/SHA256SUMS").read_text().splitlines()
    assert len(sums)==52
    baseline=subprocess.check_output(["git","show",protected["baseline_commit"]+":results/lessons/part_a/SHA256SUMS"],text=True)
    assert [s.split("  ",1)[1] for s in sums]==[s.split("  ",1)[1] for s in baseline.splitlines()]
    for line in sums:
        h,p=line.split("  ",1);assert sha(ROOT/p)==h,p
    assert not subprocess.check_output(["git","ls-files","*.pdf"]).strip()
    links=0
    docs=[ROOT/"README.md",ROOT/"AGENTS.md",ROOT/"papers/README.md",OUT/"report.md",
          *list((ROOT/"notes/literature").rglob("*.md"))]
    for doc in docs:
        for link in re.findall(r"\]\(([^)]+)\)",doc.read_text()):
            if "://" in link or link.startswith(("#","mailto:")):continue
            target=unquote(link.split("#",1)[0].strip("<>"))
            assert (doc.parent/target).exists(),(str(doc),link)
            links+=1
    result=dict(artifact_status="PASS",responsible="Doan Van Tai",
                primary_targeted_sources=6,approved_new_sources=3,
                call_checkpoint_rows=len(calls),screening_events=169,
                rank_level_search_audit="NOT_VERIFIABLE_RAW_PAYLOAD_NOT_RETAINED",
                saturation_rule_met=False,cooper_aggregate_cases=18,
                cooper_loss_revenue_units=str(no-yes),V1_GS="-1/4",
                old_author_progress_preserved=13,old_notes_preserved=13,catalog_papers=19,
                protected_files_unchanged=1186,historical_PC_prefix_unchanged=True,
                legacy_manifest_files=52,local_links_checked=links,
                grid_run=False,heldout_outcomes_used=False,H1_or_null_selected=False,
                contract_changed=False,human_L_self="OPEN",L2_9="OPEN",
                whole_L2_8_status="PARTIAL_SEARCH_PROVENANCE_AND_FORMAL_GATE_OPEN")
    (OUT/"verification.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False))


if __name__=="__main__":main()
