"""Doan Van Tai — numerical inventory for the requested reports and DL-143–145.
PASS means local artifacts agree, not external source/causal validation.
"""
import csv
import json
import re
import statistics as S
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
records=[]


def read(p): return json.loads((ROOT/p).read_text())
def csvread(p): return list(csv.DictReader((ROOT/p).open()))


def add(location,claim,actual,evidence,status='PASS'):
    records.append(dict(location=location,claim=claim,actual=actual,status=status,evidence=evidence))


def main():
    X=json.loads((OUT/'exploratory.json').read_text())
    R=json.loads((OUT/'recomputation.json').read_text())
    rows=csvread('results/ext_validity/audit/recomputed_rows.csv')
    for v in R['verdicts']:
        wave='WAVE1_REPORT.md/DL-143' if v['experiment'] in ('ev_a','ev_b','ev_d','ev_b_rep/q75','ev_b_rep/q95') else (
             'WAVE2_REPORT.md/DL-144' if v['experiment'] in ('ev_a2','ev_d2') else 'WAVE3_REPORT.md/DL-145')
        if v['experiment']=='csw_harm': continue
        count=f"{v['n']-v['k']}/{v['n']} retained" if v['ID']=='R3' else f"{v['k']}/{v['n']}"
        add(wave,v['experiment']+'/'+v['ID'],f"{v['recomputed']} {count}",'audit/recomputed_rows.csv; CARD')
    a=[read(str(p.relative_to(ROOT))) for p in (ROOT/'results/ext_validity/ev_a/run01').glob('*.json')]
    add('W1:12','60 regimes × 7 = 420; 6.2 CPU-h',f"{len({r['id'] for r in a})} × 7 = {len(a)}; {sum(r['cpu'] for r in a)/3600:.9f} CPU-h",'ev_a/run01/*.json')
    h=[r for r in rows if r['experiment']=='ev_a' and r['dm']=='10' and float(r['one_shot'])<=-.25]
    add('W1:12/DL143','32/32 one-shot harm retained',f"{sum(float(r['G'])<=-.25 for r in h)}/{len(h)}",'ev_a/run01/*.json')
    for strat in ('neg','pos'):
        for dm,hm in [('10','10'),('1/2','1/2')]:
            g=next(x for x in X['closed_loop_groups'] if (x['stratum'],x['dm'],x['hm'])==(strat,dm,hm))
            add('W1:13',f'median {strat} dm={dm},hm={hm}',g['median_G'],'audit/exploratory.json')
    short=[r for r in rows if r['experiment']=='ev_a' and r['dm'] in ('1/2','1')]
    add('W1:13','sign agreement ~80% at Delta<=T',f"{sum((float(r['G'])>0)==(float(r['pred'])>0) for r in short)}/{len(short)}=75.4167%",'ev_a/run01; predictions','ERRATUM')
    add('W1:13/DL143','Delta<=T reverses harm (general reading)',
        'At Delta=T,hp=10T: medians neg=-0.0178073%, pos=-0.0909329%; reversal is not universal.',
        'audit/exploratory.json','OVERCLAIM')
    for x in X['EV_E']:
        add('W1:16',f"EV-E {x['twin']} {x['strata']}",str(x),'ev_e_twin_classes.csv')
    add('W1:16','EV-E 15/20 vs panel EV-B 30',
        '15/20 uses neg+pos only; all strata: 18/30. KO median 11.8322% is also neg+pos; all strata 8.68116%.',
        'ev_e_twin_classes.csv','SCOPE_OMITTED')
    add('W1:17','20 × 3 classes, Pareto alpha=1.5, cap=100',
        [(c['cls'],c['params']) for c in read('results/ext_validity/ev_d/cases.json')[:3]],'ev_d/cases.json')
    add('W1:42','pilot s=-0.22 vs exact=-1.00','No archived raw pilot numeric evidence found in scoped artifacts.',
        'W1 prose only','UNVERIFIED')
    add('W1:46','73 local completed then 107 GCP, 48 GB',
        'test.log contains 71 records; final 180 outputs exist but do not store host. Launch split/RAM not independently identifiable.',
        'ev_d/test.log; test/*.json','UNVERIFIED')
    add('W1:48','12 vCPU/quota/VM stopped','Local results do not establish cloud lifecycle or quota.',
        'No GCP access per brief','UNVERIFIED')
    add('W1:68','ev_d includes score.json','File absent; report verdicts reproducible.', 'ev_d/ directory','ERRATUM')
    cases=read('results/ext_validity/ev_a2/cases.json')
    a2=csvread('results/ext_validity/ev_a2/truth.csv')
    p2={(r['id'],r['which']):r for r in csvread('results/ext_validity/ev_a2/predictions.csv')}
    lo={r['id']:r for r in a2 if r['which']=='lo'}
    hi=[r for r in a2 if r['which']=='hi']
    add('W2:11','median relative error at 2Delta*=13%',
        S.median(abs(float(r['G_S_CL_abs'])-float(p2[r['id'],'hi']['pred_abs']))/abs(float(p2[r['id'],'hi']['pred_abs'])) for r in hi),
        'ev_a2/truth.csv; predictions.csv')
    subset=[c for c in cases if c['Delta_star_over_T']>=1.1]
    add('W2:11','15/16 at Delta*/T>=1.1',f"{sum(float(lo[c['id']]['G_S_CL_abs'])>0 for c in subset)}/{len(subset)}",'ev_a2/cases.json;truth.csv')
    add('DL144','every miss at Delta*/T<=1.14',max(c['Delta_star_over_T'] for c in cases if float(lo[c['id']]['G_S_CL_abs'])<=0),'ev_a2/cases.json;truth.csv')
    text=(ROOT/'results/ext_validity/ev_a2/exploration_decoupled_posthoc.txt').read_text()
    add('W2:12','16/30 decoupled exact epoch',sum(line.endswith('OK') for line in text.splitlines()),
        'ev_a2/exploration_decoupled_posthoc.txt (rounded summary; no full raw outputs)','LIMITED_EVIDENCE')
    add('W2:13/DL144','5 queries/100 records + 3 AI-T sources',
        'Existing literature notes record 3 targeted reads; 5/100 is orchestrator-reported and not re-executed.',
        'notes/literature/W2_prior_check.md; search_log.md','LIMITED_EVIDENCE')
    add('W2:18-28','Literature years/versions/asymptotic bounds',
        '2020/v3, 2019/v1, 2026/v2 and conditional bounds agree with existing W2_prior_check; no primary-paper re-audit.',
        'notes/literature/W2_prior_check.md','LOCAL_NOTE_ONLY')
    for t in X['trace_facts']:
        add('W2:14,DL144/W3:16,37,DL145',f"Trace {t['trace']} counts, CoV, minute ranges",str(t),'binary/NPZ/metadata (official website not fetched)')
    for exp in ('ev_d2','ev_d3','ev_d3b'):
        p=ROOT/'results/ext_validity'/exp
        trains=[json.loads(f.read_text()) for f in (p/'train').glob('*.json') if '_c25_' not in f.name]
        add('W2:14/DL144; W3:18',f'{exp} median train T_int',S.median(t['T_int'] for t in trains),'train/*.json')
        taus=sorted({t['case'].get('tau',1.) for t in trains})
        for tau in taus:
            b=[t for t in trains if t['case'].get('tau',1.)==tau]
            add('W2:14; EV-D3a/b CARD train facts',f'{exp} tau={tau} beta1 path A',S.median(t['nowcast']['A']['beta'][1] for t in b),'train/*.json')
            add('EV-D3a/b CARD train facts',f'{exp} tau={tau} Fdiff fluid_nowcast',S.median(t['shares']['30']['F_old_fluid_nowcast']-t['shares']['30']['F_new'] for t in b),'train/*.json')
    b=[r for r in rows if r['experiment']=='ev_d2' and r['pred']]
    add('W2:14','all truth magnitudes <0.25 pp',
        {'h30_nowcast_max':max(abs(float(r['G'])) for r in b if r['h_mult']=='30'),
         'h3_nowcast_max':max(abs(float(r['G'])) for r in b if r['h_mult']=='3')},'ev_d2/test/*.json','SCOPE_OMITTED')
    c25=[json.loads(f.read_text()) for f in (ROOT/'results/ext_validity/ev_d2/train').glob('*_c25_*.json')]
    add('W2:51','c25 T_int about26min/backlog about7000',
        {'median_Tint_minutes':S.median(t['T_int'] for t in c25)/60,'median_backlog_stay':S.median(t['mean_stay'] for t in c25)},'ev_d2/train/*_c25_*.json')
    add('W2:55','test MC wall assertion 30->120s','Current test has120s; Git diff validates historical change.',
        'tests/test_ext_closed_loop.py; git history')
    add('DL144','historical pytest902PASS+1intentionalFAIL','Historical execution not rerun or confirmed by saved local log in audit scope.',
        'Current targeted suite:50PASS','UNVERIFIED')
    add('W2:37','closed-loop law verified across4panels/3traffic classes/real trace',
        'EV-A tests closed-loop magnitude; EV-A2 fails threshold. Packet arms test a distinct one-shot train-estimated leading term.',
        'CARDs and audit verdict table','OVERCLAIM')
    add('W2:38-41','unselected decision times necessary for harm','q75 retains harm4/18; selection is a moderator, not necessary-condition proof.',
        'ev_b_rep/q75/truth.csv','OVERCLAIM')
    for x in X['dose_response']:
        if x['experiment'] in ('ev_d3','ev_d3b'):
            add('W3:19-24/DL145',f"{x['experiment']} {x['tau']} {x['twin']} median/harm",str(x),'audit/exploratory.json')
    add('W3:29','120/124 significant effects','54+66=120 of56+68=124 prediction-selected rows; not124independent/significance-tested effects.',
        'CARD D2, raw predictions/test','SCOPE_OMITTED')
    add('W3:30/DL145','magnitude within +-40-60%',
        {'h30_abs_error_over_abs_pred_median':{r['experiment']:r['relative_error_den_pred_median'] for r in X['prediction_diagnostics'] if r['h_mult']==30},
         'h30_abs_error_over_abs_pred_max':{r['experiment']:r['relative_error_den_pred_max'] for r in X['prediction_diagnostics'] if r['h_mult']==30}},
        'prediction_diagnostics.csv','ERRATUM')
    slope=X['slope_diagnostic']
    add('W3:32/DL145','s error5%, hence not cause of hybridFAIL',
        {'median_rel_error':S.median(x['relative_error'] for x in slope),'max_rel_error':max(x['relative_error'] for x in slope),
         'max_error_id':max(slope,key=lambda x:x['relative_error'])['id']},'ev_d3/diag_s_long.json','OVERCLAIM')
    add('W3:35-39/DL145','D1FAIL diagnoses failure of T12 mixing assumption',
        'D1 is a finite-h threshold, T12 an O(1)/o(h) statement. Both trace loops have exact periodic dependence, not a measured finite slowest mixing time.',
        'audit/repro_checks.json; T12:15-27','OVERCLAIM')
    add('W3:43','54min stalled download,0byte','Download timing/terminal process not recorded in scoped numerical artifacts.',
        'W3 prose only','UNVERIFIED')
    add('T12:43','pilot9/9 no harm at30T','Panel120rows recomputable; nine pilot outputs not archived in scoped directory.',
        'T12 prose; no pilotraw in scoped outputs','UNVERIFIED')
    add('T12:15-27','O(1) derivation from conditioning on Z_t',
        'Needs future-cost sufficiency given history and L1/uniform remainder; insufficient-state toy gives G=0 versus RHS=-0.5.',
        'audit/repro_checks.json','PROOF_GAP')
    add('T12:36','plug-in cannot be harmed at long horizon',
        'Mixing CTMC toy G=-0.216166 and -1.441108% at30T, still bounded and converges to0% as h grows.',
        'audit/repro_checks.json','OVERCLAIM')
    with (OUT/'report_consistency.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    summary={k:sum(r['status']==k for r in records) for k in sorted({r['status'] for r in records})}
    (OUT/'report_consistency_summary.json').write_text(json.dumps(dict(records=len(records),by_status=summary),indent=2)+'\n')
    print(json.dumps(dict(records=len(records),by_status=summary),indent=2))


if __name__=='__main__': main()
