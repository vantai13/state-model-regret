"""Write-once descriptive summary; select rho only after every case passed."""
import csv
from fractions import Fraction as F
from statistics import median

from .common import ROOT,HERE,OUT,LEVELS,RHOS,load,plan,sha,require,write_once,verify_prereg,compare_bundle
from .analysis import select_rho,describe,reading,baseline


def table(path,rows):
    if not rows:return
    with path.open('x',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(rows)


def stats(values):
    defined=[v for v in values if v is not None]
    return dict(N=len(values),defined=len(defined),median=median(defined) if defined else None,
                minimum=min(defined) if defined else None,maximum=max(defined) if defined else None)


def main():
    verify_prereg()
    destination=ROOT/OUT/'summary'
    require(not destination.exists(),'summary already exists; never overwrite')
    cases=plan()['cases'];observed={};ledger=[];raw=[];metrics=[];levels={}
    for case in cases:
        folder=ROOT/OUT/'native'/case['id']
        comparison=folder/'comparison.json'
        if comparison.exists():
            observed[case['id']]=load(comparison.relative_to(ROOT))
        rows={}
        for lv in LEVELS:
            path=folder/f'level_{lv[0]}_{lv[1]}.json'
            if not path.exists():continue
            row=load(path.relative_to(ROOT));rows[lv]=row
            raw.append(dict(id=case['id'],aliases='|'.join(case['aliases']),region='|'.join(case['regions']),
                            K=lv[0],ref=lv[1],status=row['status'],
                            raw_arithmetic_pass=row.get('arithmetic_pass'),validity_errors=str(row.get('validity_errors')),
                            CF_computed=row.get('CF_computed'),baseline_sanity_pass=row.get('baseline_sanity_pass'),
                            cpu_seconds=row.get('call_cpu_seconds'),baseline_added_cpu_seconds=row.get('baseline_added_cpu_seconds')))
            for b in row.get('baseline',[]):
                metrics.append(dict(id=case['id'],region='|'.join(case['regions']),K=lv[0],ref=lv[1],
                                    rho=b['rho'],Cref=row['Cref'],Stay=row['Stay'],
                                    L00_original=row['losses']['00'],L10_original=row['losses']['10'],
                                    L00_margin=b['L00'],L10_margin=b['L10'],GS_theta=b['GS_theta'],
                                    deltaL10=b['deltaL10'],R_M=b['R_M'],theta=b['theta'],theta_error=b['theta_error']))
        levels[case['id']]=rows
        saved=observed.get(case['id'])
        if saved and saved['status']=='PASS':
            require(compare_bundle(case,rows)==saved,'passing comparison changed')
        ledger.append(dict(id=case['id'],aliases='|'.join(case['aliases']),regions='|'.join(case['regions']),
                           status=saved['status'] if saved else 'NOT_RUN',reasons='|'.join(saved.get('reasons',[])) if saved else ''))
    full_path=ROOT/OUT/'full_summary.json'
    complete=(full_path.exists() and load(full_path.relative_to(ROOT))['status']=='PASS' and
              len(observed)==len(cases) and all(r['status']=='PASS' for r in observed.values()))
    summary=dict(responsible='Doan Van Tai',status='PASS_DISCOVERY_DESCRIPTIVE' if complete else 'HOLD_OR_PARTIAL',
                 planned=90,observed_cases=len(observed),level_rows=len(raw),
                 passed_cases=sum(r['status']=='PASS' for r in observed.values()),
                 hold_cases=[k for k,r in observed.items() if r['status']!='PASS'],
                 selection_allowed=complete,CF_outcomes=0,G_level='G1',card_v2_verdict_unchanged=True,
                 predictions_provenance='AI soạn theo ủy quyền trực tiếp; không independent author forecast',
                 forecasts='NOT_EVALUABLE' if not complete else {},regions={})
    descriptions=[]
    if complete:
        selected={};selection={}
        for region,target in [('MV+A','00'),('SH+A','10')]:
            group=[c for c in cases if region in c['regions']]
            rows=[levels[c['id']][LEVELS[0]] for c in group]
            rho,scores=select_rho(rows,target);selected[region]=rho
            ds=[dict(region=region,**describe(row,rho,target)) for row in rows]
            descriptions+=ds
            by_level={str(lv):select_rho([levels[c['id']][lv] for c in group],target)[0] for lv in LEVELS}
            ranking=sorted(scores,key=lambda r:(scores[r],F(r)))
            selection[region]=dict(rho_star=rho,target=target,normalized_mean_regret_scores={r:str(v) for r,v in scores.items()},
                                   selected_by_level=by_level,runner_up_gap=str(scores[ranking[1]]-scores[ranking[0]]))
            summary['regions'][region]=dict(N=len(group),rho_star=rho,reading_preview=reading(region,ds),
                  statistics={key:stats([r[key] for r in ds]) for key in
                              ('R_M','GS_theta_pctC','deltaL10','deltaL10_pctC','Stay_headroom_pctC','Stay_minus_L00_pctC','L10_minus_Stay_pctC')},
                  rho_best={r:sum(F(d['rho_best'])==F(r) for d in ds) for r in RHOS},
                  sensitivity=selection[region])
            if region=='MV+A':
                vals=[F(d['R_M_exact']) for d in ds if d['R_M_exact'] is not None]
                summary['forecasts']['MV_median_recovery_ge_half']=bool(vals and median(vals)>=F(1,2))
            else:
                reductions=[]
                for row in rows:
                    gs0=F(row['G_S'])
                    if gs0<0:
                        gs1=F(baseline(row,'1/100')['GS_theta'])
                        reductions.append(1-max(F(0),-gs1)/abs(gs0))
                summary['forecasts']['SH_rho1_harm_reduction_lt_half']=bool(reductions and median(reductions)<F(1,2))
                summary['forecasts']['SH_rho1_harm_reduction']=dict(N=len(reductions),median=None if not reductions else float(median(reductions)))
                summary['forecasts']['SH_selected_median_absGS_ge_point5pct']=summary['regions'][region]['reading_preview']['median_abs_GS_theta_pctC']>=.5
        write_once(ROOT/HERE/'rho_freeze.json',dict(responsible='Doan Van Tai',status='FROZEN_BY_PREDECLARED_SELECTION_RULE',
                    author_choice_sha256=sha(ROOT/HERE/'author_choices.json'),prereg_sha256=sha(ROOT/HERE/'prereg.json'),
                    rho_by_region=selected,selection=selection,not_CF_verdict=True,
                    native_comparison_sha256={str(ROOT/OUT/'native'/c['id']/'comparison.json'):sha(ROOT/OUT/'native'/c['id']/'comparison.json') for c in cases}))
    destination.mkdir(parents=True)
    write_once(destination/'summary.json',summary)
    table(destination/'case_ledger.csv',ledger)
    table(destination/'native_rows.csv',raw)
    table(destination/'baseline_grid.csv',metrics)
    table(destination/'selected_baseline.csv',descriptions)
    write_once(destination/'manifest.json',dict(script_sha256=sha(__file__),
               outputs_sha256={p.name:sha(p) for p in destination.iterdir()}))
    print({k:summary[k] for k in ('status','planned','observed_cases','level_rows','passed_cases','hold_cases','selection_allowed')},flush=True)
    if complete:
        for r,s in summary['regions'].items():print(r,s['rho_star'],s['reading_preview'],flush=True)


if __name__=='__main__':main()
