"""Report-only annotation of frozen audit outputs; no physical calls or rescoring changes."""
import argparse
import csv
from fractions import Fraction as F
import json
from pathlib import Path

from . import summarize as S
from .common import ROOT,HERE,OUT,METRICS,sha,write_once,require
from .resource_resume import NEWOUT,verify_extension


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise FileExistsError('final report outputs already exist')
    verify_extension()
    S.OUT=NEWOUT
    summary,points,raw=S.summarize()
    ledger=json.loads((ROOT/HERE/'sealed_scope.json').read_text())
    summary.update(resource_amendment_commit='35e902e',sealed_guard_commit='1db060f',
                   original_scope_distinct=666,allowed_scope_distinct=665,sealed_blocked=ledger['blocked'],
                   original_partA=json.loads((ROOT/OUT/'partA/summary.json').read_text())['status'],
                   original_partA_actual_bit_checks=117,resource_resolved_partA_bit_checks=126,
                   raw_native_arithmetic_pass_count=sum(r['arithmetic_pass'] is True for r in raw),
                   raw_native_validity_empty_count=sum(r['validity_errors']=='[]' for r in raw),
                   raw_native_CF_false_count=sum(r['CF_computed'] is False for r in raw),
                   report_note='Point class/R6 interval classifications are not usable when R1/status fails; all L4.5 use blocked by audit HOLD',
                   full_run='NOT_RUN_AFTER_BENCHMARK_HOLD',budget='NOT_CLOSED: benchmark stopped at case3 of4',
                   MC='NOT_RUN: R1 convergence already failed; no pilot/native shift exceeded.25pp; no new SUB card selected')
    for r in points:
        r['native_class_for_use']=r['native_class_R6'] if r['status']=='PASS' else 'UNRESOLVED_VALIDITY'
        r['eligible_for_L45']=False  # global audit HOLD, even the two individually passing cases
    for zone,z in summary['zones'].items():
        rs=[r for r in points if zone in r['zones'].split('|')]
        z['R6_fraction_note']='observed-only diagnostic; excludes neither validity failures nor uncomputed scope from reporting'
        z['unusable_validity_rows']=sum(r['status']!='PASS' for r in rs)
        z['unknown_for_use_observed']=sum(r['status']!='PASS' or r['native_class_R6']=='UNRESOLVED' for r in rs)
    plan=json.loads((ROOT/HERE/'cases.json').read_text())
    aliases={r['id']:r for r in plan['aliases']}
    matrix=[];r1_diagnostics=[]
    for r in points:
        alias=aliases[r['id']]
        for m in METRICS:
            matrix.append(dict(id=r['id'],native_id=r['native_id'],metric=m,pilot_pctC=alias['pilot_pctC'][m],
                               native_pctC=r['z_pctC_'+m],shift_pp=r['shift_pp_'+m],
                               native_refinement_d_pp=r['d_pp_'+m],status=r['status']))
        folder=ROOT/NEWOUT/'native'/r['native_id']
        fine=json.loads((folder/'level_640_4.json').read_text())
        for suffix,axis in [('320_4','K'),('640_2','dt')]:
            coarse=json.loads((folder/f'level_{suffix}.json').read_text())
            delta=abs(F(fine['Cref'])-F(coarse['Cref']))/F(fine['Cref'])
            r1_diagnostics.append(dict(id=r['id'],axis=axis,Cref_fine=fine['Cref'],Cref_coarse=coarse['Cref'],
                                      Cref_relative_difference_percent=float(100*delta),
                                      Cref_R1_pass=delta<=F(1,400)))
    # These assertions check the observed receipts, not a hypothesis outcome.
    require(len(raw)==9 and len(points)==3,'unexpected completed audit scope')
    require(summary['technical_recommendation']=='HOLD','registered HOLD not reflected')
    failed=[r for r in r1_diagnostics if not r['Cref_R1_pass']]
    require(len(failed)==1 and failed[0]['id']=='XM2X000' and failed[0]['axis']=='dt','R1 failure diagnosis disagrees')
    a.out.mkdir(parents=True)
    write_once(a.out/'summary.json',summary)
    for name,rows in [('audit_points.csv',points),('class_flips.csv',[r for r in points if r['class_flipped']]),
                      ('native_rows.csv',raw),('pilot_native_metrics.csv',matrix),('R1_reference_cost.csv',r1_diagnostics),
                      ('sealed_blocked.csv',[dict(native_id=b['native_id'],aliases='|'.join(b['aliases']),status=b['status']) for b in ledger['blocked']])]:
        with (a.out/name).open('x',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    write_once(a.out/'manifest.json',dict(responsible='Doan Van Tai',scope='report only; no physical calls',
               script_sha256=sha(Path(__file__)),outputs_sha256={p.name:sha(p) for p in a.out.iterdir()},
               native_source_root=str(NEWOUT),initial_prereg_commit='ae174d0',resource_amendment_commit='35e902e',sealed_guard_commit='1db060f'))
    print(json.dumps({k:summary[k] for k in ('technical_recommendation','observed_native_distinct','native_level_files',
                      'observed_class_flips','failed_native_cases','completed_native_cpu_seconds','full_run')},indent=2))


if __name__=='__main__':main()
