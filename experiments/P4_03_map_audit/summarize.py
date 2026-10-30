"""Read-only reporting of complete or interrupted registered audit artifacts.

Never calls a physical engine; incomplete zones never receive a full-zone rate.
"""
import argparse
import csv
import json
from pathlib import Path
import statistics as st

from .common import ROOT,HERE,OUT,METRICS,write_once


def summarize():
    plan=json.loads((ROOT/HERE/'cases.json').read_text())
    parts={}
    for name in ('partA/summary.json','benchmark_summary.json','full_summary.json'):
        path=ROOT/OUT/name
        if path.exists():parts[name]=json.loads(path.read_text())
    physical=[];raw=[]
    for path in sorted((ROOT/OUT/'native').glob('*/comparison.json')):
        physical.append(json.loads(path.read_text()))
    for path in sorted((ROOT/OUT/'native').glob('*/level_*.json')):
        r=json.loads(path.read_text())
        raw.append(dict(id=r.get('id'),K=r.get('K'),ref=r.get('ref'),status=r.get('status'),
                        arithmetic_pass=r.get('arithmetic_pass'),validity_errors=json.dumps(r.get('validity_errors')),
                        CF_computed=r.get('CF_computed'),call_cpu_seconds=r.get('call_cpu_seconds'),
                        error=r.get('error','')))
    aliases=[r for p in physical for r in p['aliases']]
    zones={}
    for zone in ('A','AB'):
        planned=[a for a in plan['aliases'] if zone in a['zones']]
        observed=[r for r in aliases if zone in r.get('zones',[]) and 'shift_pp' in r]
        metric='G_S' if zone=='A' else 'Gamma';unknown='unresolved_A_GS' if zone=='A' else 'unresolved_AB_Gamma'
        shifts={m:[r['shift_pp'][m] for r in observed] for m in METRICS}
        zones[zone]=dict(planned_rows=len(planned),planned_distinct=len({a['native_id'] for a in planned}),
                        observed_rows=len(observed),observed_distinct=len({r['native_id'] for r in observed}),
                        complete=len(observed)==len(planned),
                        class_flips=sum(r['class_flipped'] for r in observed),
                        pilot_A_to_other=sum(r['pilot_class']=='A' and r['native_class']!='A' for r in observed),
                        criterion_unresolved=sum(r[unknown] for r in observed),
                        unresolved_observed_fraction=(sum(r[unknown] for r in observed)/len(observed) if observed else None),
                        unresolved_is_full_zone_estimate=len(observed)==len(planned),
                        metric=metric,shifts={m:dict(n=len(v),median=st.median(v) if v else None,
                                  max_absolute=max(map(abs,v)) if v else None,
                                  negative=sum(x<0 for x in v),negative_fraction=sum(x<0 for x in v)/len(v) if v else None)
                                                   for m,v in shifts.items()})
    hold=any(v.get('status')!='PASS' for v in parts.values()) or any(p['status']!='PASS' for p in physical)
    full=parts.get('full_summary.json',{}).get('status')=='PASS' and len(physical)==len(plan['cases'])
    status='HOLD' if hold else 'PASS_LIMITED_MISSING_HISTORICAL_PROBES' if full else 'INCOMPLETE'
    summary=dict(responsible='Doan Van Tai',technical_recommendation=status,author_audit_label='NOT_CONFIRMED',
                 prereg_commit='ae174d0',parts={k:{q:v.get(q) for q in ('status','rows','passed','planned','completed','cpu_seconds','wall_seconds') if q in v} for k,v in parts.items()},
                 planned_native_distinct=len(plan['cases']),observed_native_distinct=len(physical),
                 native_level_files=len(raw),native_completed_levels=sum(r['status']=='COMPLETED' for r in raw),
                 observed_class_flips=sum(r.get('class_flipped',False) for r in aliases),
                 failed_native_cases=[p['native_id'] for p in physical if p['status']!='PASS'],zones=zones,
                 completed_native_cpu_seconds=sum(r['call_cpu_seconds'] or 0 for r in raw),
                 predictions_evaluable=full,CF_outcomes=0,G_level='G1',
                 historical_K2='UNVERIFIED: missing original six IDs',historical_K6='UNVERIFIED: missing original eight probe file',
                 use_for_L45='BLOCKED' if not full or hold else 'native labels only, scoped limitations retained',
                 limitations=['Empirical refinement differences are not certified total error bounds',
                              'Raw validity guard can be stricter than lean confirmation adapter',
                              'Partial-zone proportions must not be read as full-zone estimates',
                              'Resource failures are not proof of a numerical or physical bug'])
    flattened=[]
    for r in aliases:
        flat={k:r.get(k) for k in ('id','native_id','status','pilot_class','native_class','native_class_R6','class_flipped',
                                  'unresolved_A_GS','unresolved_AB_Gamma')}
        flat['zones']='|'.join(r.get('zones',[]));flat['reasons']='|'.join(r.get('reasons',[]))
        for kind in ('z_pctC','d_pp','shift_pp'):
            for m in METRICS:flat[kind+'_'+m]=r.get(kind,{}).get(m)
        flattened.append(flat)
    return summary,flattened,raw


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise FileExistsError('report output exists; preserve it')
    summary,points,raw=summarize();a.out.mkdir(parents=True)
    write_once(a.out/'summary.json',summary)
    for name,rows in [('audit_points.csv',points),('class_flips.csv',[r for r in points if r['class_flipped']]),('native_rows.csv',raw)]:
        fields=list(rows[0]) if rows else list(points[0]) if points else ['id','native_id','status']
        with (a.out/name).open('x',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
