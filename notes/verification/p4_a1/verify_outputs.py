"""Doan Van Tai: read-only independent arithmetic/rescore of saved A1 results.

No engine, box membership/counts, CF outcomes or new rho selection on partial runs.
Run from repository root after registered schedules finish.
"""
from collections import Counter
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
from statistics import median
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from experiments.P4_A1.config import verify_run

METRICS = ('G_S','G_M','G_SM','Gamma','G_S_M1','G_M_S1')
SOURCES = {}


def read(path):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT/path
    blob = path.read_bytes()
    SOURCES[str(path.relative_to(ROOT))] = hashlib.sha256(blob).hexdigest()
    return json.loads(blob)


def independent_row_checks(row, case, level):
    assert row['id'] == case['id'] and row['parameters'] == case['parameters']
    assert (row['K'],row['ref']) == level and row['CF_computed'] is False
    if row['status'] != 'COMPLETED':
        return
    L = {k:F(v) for k,v in row['losses'].items()}; C = F(row['Cref'])
    assert C == L['11'] and C > 0
    expected = dict(G_S=L['00']-L['10'],G_M=L['00']-L['01'],G_SM=L['00']-L['11'],
                    Gamma=L['10']+L['01']-L['00']-L['11'],
                    G_S_M1=L['01']-L['11'],G_M_S1=L['10']-L['11'])
    assert all(abs(F(row[m])-expected[m])/C <= F(1,10**11) for m in METRICS)
    for b in row['baseline']:
        assert abs(F(b['GS_theta'])-(F(b['L00'])-F(b['L10'])))/C <= F(1,10**11)
        if F(b['rho']) == 0:
            assert b['L00'] == row['losses']['00'] and b['L10'] == row['losses']['10']


def extra_delta00_diagnostic(levels, main):
    """Additional reporting only: deltaL00 was not in the supplied baseline readiness fields."""
    fine=levels[main]; cf=F(fine['Cref']); worst=F(0); width=F(0)
    for i,b in enumerate(fine['baseline']):
        for lv in ((main[0]//2,main[1]),(main[0],main[1]//2)):
            co=levels[lv]; v=F(co['baseline'][i]['deltaL00']); cc=F(co['Cref']); f=F(b['deltaL00'])
            worst=max(worst,abs(f-v)/cf,abs(f/cf-v/cc))
        for row in levels.values():
            width=max(width,F(row['baseline'][i]['deltaL00_error'])/F(row['Cref']))
    return dict(refinement_ratio=float(worst),arithmetic_width_ratio=float(width),
                would_meet_existing_tolerances=worst<=F(1,400) and width<=F(1,4000),
                role='post-run diagnostic, not an amended selection/readiness rule')


def verify_one(run):
    cfg=verify_run(run); out=ROOT/cfg['output']; main=tuple(cfg['levels'][0])
    full=read(out/'full_summary.json') if (out/'full_summary.json').exists() else dict(
        status='NOT_RUN_UPSTREAM_HOLD',completed=0,results=[],stop_reasons=['No registered full-stage summary'])
    records={}; levels_by_id={}; ledger=[]; rawflags=Counter(); delta00=[]
    for c in cfg['cases']:
        folder=out/'native'/c['id']; p=folder/'comparison.json'
        if not p.exists():
            ledger.append(dict(id=c['id'],supports=c['supports'],status='NOT_RUN'));continue
        rec=read(p); assert rec['native_id']==c['id']
        records[c['id']]=rec
        ledger.append(dict(id=c['id'],supports=c['supports'],status=rec['status']))
        rows={}
        for lv in (main,(main[0]//2,main[1]),(main[0],main[1]//2)):
            rp=folder/f'level_{lv[0]}_{lv[1]}.json'
            if not rp.exists():continue
            r=read(rp); independent_row_checks(r,c,lv); rows[lv]=r
            for flag in r.get('validity_errors',[]):rawflags[flag]+=1
        levels_by_id[c['id']]=rows
        if len(rows)==3 and all(r['status']=='COMPLETED' for r in rows.values()):
            delta00.append(dict(id=c['id'],**extra_delta00_diagnostic(rows,main)))
    by_support={s:dict(Counter(l['status'] for l in ledger if s in l['supports'])) for s in cfg['supports']}
    nr_reasons=Counter(reason.split(':')[0] for r in records.values() if r['status']=='NOT_READY'
                       for reason in r.get('readiness_reasons',[]))
    report=dict(status=full['status'],planned=len(cfg['cases']),observed_distinct_including_benchmark=len(records),
                full_stage_completed=full['completed'],by_support=by_support,
                not_ready_reason_events=dict(nr_reasons),
                stop_reasons=full['stop_reasons'],raw_flags_all_levels=dict(rawflags),
                deltaL00_additional_diagnostic=dict(cases=len(delta00),not_meeting=sum(not d['would_meet_existing_tolerances'] for d in delta00),
                    max_refinement_ratio=max((d['refinement_ratio'] for d in delta00),default=None),
                    max_width_ratio=max((d['arithmetic_width_ratio'] for d in delta00),default=None)),
                independent_rho_rescore='NOT_SELECTED_ON_PARTIAL_OR_HOLD')
    assert len(full['results'])==full['completed']
    assert {r['native_id'] for r in full['results']} <= records.keys()
    control=read(out/'control_summary.json')
    report['unique_evaluation_cpu_seconds_including_control']=sum(r.get('cpu_seconds',0) for r in records.values())+control.get('cpu_seconds',0)
    if full['status']=='PASS':
        assert len(records)==len(cfg['cases'])
        saved=read(out/'summary/summary.json'); rescored={}
        for support,spec in cfg['supports'].items():
            if not spec.get('target'):continue
            ids=[c['id'] for c in cfg['cases'] if support in c['supports'] and records[c['id']]['status']=='PASS']
            rows=[levels_by_id[cid][main] for cid in ids]
            scores={rho:sum((F(r['baseline'][i]['L'+spec['target']])-F(r['losses']['11']))/F(r['Cref']) for r in rows)/len(rows)
                    for i,rho in enumerate(cfg['rho'])}
            rho=min(scores,key=lambda x:(scores[x],F(x)))
            assert rho==saved['supports'][support]['rho_star']
            i=cfg['rho'].index(rho); bs=[r['baseline'][i] for r in rows]
            before=median(100*F(r['G_S'])/F(r['Cref']) for r in rows)
            after=median(100*F(b['GS_theta'])/F(r['Cref']) for r,b in zip(rows,bs))
            if support=='MV+A':
                recovery=[(F(r['losses']['00'])-F(b['L00']))/F(r['G_M']) for r,b in zip(rows,bs) if F(r['G_M'])>0]
                narrow=bool(recovery) and median(recovery)>=F(1,2)
                detail=dict(median_recovery=float(median(recovery)) if recovery else None,
                            undefined=len(rows)-len(recovery))
            elif support=='SH+A':
                med_abs=median(abs(100*F(b['GS_theta'])/F(r['Cref'])) for r,b in zip(rows,bs))
                change=median(F(b['deltaL10']) for b in bs);narrow=med_abs<F(1,2) and change<0
                detail=dict(median_abs_GS_theta_pctC=float(med_abs),median_deltaL10=float(change))
            else:
                change=median(F(b['deltaL00']) for b in bs)
                narrow=after<F(cfg['reading']['SV']['median_GS_theta_pctC_below']) and change<0
                detail=dict(median_deltaL00=float(change))
            assert narrow==saved['supports'][support]['reading']['descriptive_narrow']
            rescored[support]=dict(N_ready=len(rows),rho_star=rho,median_GS_original_pctC=float(before),
                                   median_GS_theta_pctC=float(after),descriptive_narrow=narrow,**detail)
        report['independent_rho_rescore']=rescored
    if run=='SUB_PROBE' and full['status']=='PASS':
        ready=sum(not r['native_readiness_reasons'] for r in records.values())
        mx=max(r['cpu_seconds'] for r in records.values())
        report['predeclared_native_decision']=dict(native_ready=ready,N=5,max_bundle_cpu_seconds=mx,
             decision='PROPOSE_KEEP_KAPPA_GE_1_20_FOR_FURTHER_COVERAGE' if ready>=4 and mx<=600 else 'PROPOSE_NARROW_KAPPA_GE_1_10',
             note='No assertion about SUB effects or global coverage')
    return report


if __name__=='__main__':
    reports={run:verify_one(run) for run in ('L44_A1','L43_A1_SV','SUB_PROBE')}
    report=dict(responsible='Doan Van Tai',checks='PASS',runs=reports,new_CF_outcomes=0,new_sealed_outcomes=0,
                new_box_counts=0,source_sha256=SOURCES)
    dest=ROOT/'results/lessons/p4_a1/verification.json'
    assert not dest.exists(), 'write once'
    dest.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='source_sha256'},indent=2,ensure_ascii=False))
