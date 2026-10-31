"""Doan Van Tai — A2 eight-point R3 probe; no A1/frozen source modifications.

Source supplied by the user (AI Claude); guards strengthened before freeze.
Only numerical readiness is scored: no rho selection or regional medians.
"""
import argparse
from fractions import Fraction as F
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

from experiments.P4_03_map_audit.common import ROOT,sha,require,write_once
from experiments.P4_A1.config import load,committed,check_author,guard_case,verify_run
from experiments.P4_A1.checks import row_readiness,baseline_readiness
from .guards import validate_decisions,validate_row,reproduction,require_run_complete,METRICS

RUN=Path('experiments/P4_A2/runs/L44_PROBE')
A1_PREREG=Path('experiments/P4_A1/runs/L44_A1/prereg.json')
A1_OUT=Path('results/lessons/l4_4/a1')
DIAGNOSIS=Path('results/lessons/p4_a2/l44_diagnosis.json')
LADDER=(((640,4),(320,4),(640,2)),((1280,4),(640,4),(1280,2)),((1280,8),(640,8),(1280,4)))
CONTROL=dict(id='A2_CONTROL_U0',parameters=['7','6','1/10','0','8','0'],key=['7','6','0','1/10','8','0'])


def all_levels():
    return list(dict.fromkeys(lv for step in LADDER for lv in step))


def fingerprint():
    return sha(ROOT/RUN/'prereg.json')


def expected_targets(a1,diag):
    failing=diag['summary']['failing_pairs_per_point']
    require(len(failing)==8,'target set must contain all eight A1 failures')
    targets=[]
    for cid,rhos in sorted(failing.items()):
        case=next(c for c in a1['cases'] if c['id']==cid)
        guard_case(case,a1)
        require(len(rhos)==1 and rhos[0] in a1['rho'],'unexpected target rho')
        targets.append(dict(id=cid,parameters=case['parameters'],key=case['key'],target_rho=rhos))
    return targets


def freeze():
    design=load(RUN/'design.json');choice=check_author(RUN/'author_choices.json')
    from experiments.P4_A1.freeze import require_filled
    require_filled(choice['decisions'],'decisions');validate_decisions(choice['decisions'])
    require(design['run_id']=='L44_PROBE','wrong design id')
    out=ROOT/design['output']
    require(not any((out/n).exists() for n in ('native','controls','control_summary.json','run_summary.json')),
            'plant outputs already exist; never refreeze')
    a1=verify_run('L44_A1');targets=expected_targets(a1,load(DIAGNOSIS))
    sources={str(p) for p in RUN.parents[1].glob('*.py')}
    sources.update(('tests/test_p4_a2.py',str(RUN/'design.json'),str(RUN/'author_choices.json'),
                    str(RUN/'amendment.md'),str(DIAGNOSIS),'experiments/P4_A1/checks.py',
                    'experiments/P4_A1/evaluate.py','experiments/P4_A1/config.py',
                    'experiments/P4_04_baseline/margin.py'))
    if choice.get('delegation_path'):sources.add(choice['delegation_path'])
    for path in sources:committed(path)
    diag=load(DIAGNOSIS)
    history={str(A1_PREREG),str(A1_OUT/'full_summary.json'),'notes/phases/L4_4_A1_completion.json',
             'results/lessons/p4_a1/environment.json',*diag['inputs_sha256']}
    for path in history:committed(path)
    cfg=dict(status='FROZEN_BEFORE_PLANT',run_id='L44_PROBE',responsible='Doan Van Tai',
             output=design['output'],ladder=[[list(lv) for lv in step] for step in LADDER],rho=a1['rho'],
             targets=targets,control=CONTROL,decisions=choice['decisions'],resources=design['resources'],
             author_choices=str(RUN/'author_choices.json'),CF_computed=False,
             source_sha256={p:sha(ROOT/p) for p in sorted(sources)},
             preserved_history_sha256={p:sha(ROOT/p) for p in sorted(history)},
             replay_scope='All saved numerical/error/baseline fields plus reparsed significant bits; exclude runtime metadata',
             cpu_accounting='Unique level evaluation CPU incl control; cap checked before/after each point; process cap separately')
    write_once(ROOT/RUN/'prereg.json',cfg)
    print(json.dumps(dict(targets=[(t['id'],t['target_rho']) for t in targets],levels=all_levels()),default=str))


def verify():
    path=RUN/'prereg.json';require((ROOT/path).exists(),'A2_PREREG_NOT_FROZEN');committed(path)
    cfg=load(path)
    require(cfg['status']=='FROZEN_BEFORE_PLANT' and cfg['run_id']=='L44_PROBE','prereg status/id')
    for name,digest in cfg['source_sha256'].items():
        require(sha(ROOT/name)==digest,'source changed: '+name);committed(name)
    for name,digest in cfg['preserved_history_sha256'].items():
        require(sha(ROOT/name)==digest,'HISTORY_CHANGED: '+name)
    choice=check_author(cfg['author_choices']);validate_decisions(cfg['decisions'])
    require(choice['decisions']==cfg['decisions'],'decision mismatch')
    design=load(RUN/'design.json')
    require(cfg['resources']==design['resources'] and cfg['output']==design['output'],'design mismatch')
    a1=verify_run('L44_A1')
    require(cfg['targets']==expected_targets(a1,load(DIAGNOSIS)),'incomplete or foreign target set')
    require(cfg['rho']==a1['rho'] and cfg['ladder']==[[list(lv) for lv in s] for s in LADDER], 'rho/ladder changed')
    require(cfg['control']==CONTROL,'control changed')
    return cfg


def folder_of(cfg,cid,control=False):
    return ROOT/cfg['output']/('controls' if control else 'native')/cid


def case_of(cfg,cid):
    if cid==cfg['control']['id']:return cfg['control'],True
    return next(t for t in cfg['targets'] if t['id']==cid),False


def check_case(case,cfg,control):
    if control:guard_case(case,cfg,control=True)
    else:
        a1=load(A1_PREREG);registered=next(c for c in a1['cases'] if c['id']==case['id'])
        require(registered['parameters']==case['parameters'] and registered['key']==case['key'],'foreign A1 target')
        guard_case(registered,a1)


def point_files(cfg,case,control):
    folder=folder_of(cfg,case['id'],control)
    levels=[tuple(cfg['ladder'][-1][0])] if control else all_levels()
    return [(lv,folder/f'level_{lv[0]}_{lv[1]}.json') for lv in levels]


def point_receipt(cfg,case,control,status,reasons=()):
    files=[p for _,p in point_files(cfg,case,control) if p.exists()]
    cpu=math.fsum(load(p.relative_to(ROOT)).get('call_cpu_seconds',0) for p in files)
    rec=dict(id=case['id'],status=status,reasons=list(reasons),a2_prereg_sha256=fingerprint(),cpu_seconds=cpu,
             rows_sha256={str(p.relative_to(ROOT)):sha(p) for p in files})
    write_once(folder_of(cfg,case['id'],control)/'point_summary.json',rec)
    return rec


def verify_point(cfg,case,control=False):
    folder=folder_of(cfg,case['id'],control);rec=load((folder/'point_summary.json').relative_to(ROOT))
    require(rec.get('status')=='COMPLETED' and rec.get('id')==case['id'] and
            rec.get('a2_prereg_sha256')==fingerprint(),'POINT_NOT_VALID_COMPLETE')
    wanted={str(p.relative_to(ROOT)) for _,p in point_files(cfg,case,control)}
    require(set(rec['rows_sha256'])==wanted,'POINT_LEVEL_SET_INCOMPLETE')
    rows={}
    for lv,p in point_files(cfg,case,control):
        require(sha(p)==rec['rows_sha256'][str(p.relative_to(ROOT))],'POINT_ROW_HASH_CHANGED')
        row=load(p.relative_to(ROOT));validate_row(row,case,lv,fingerprint(),cfg['rho']);rows[lv]=row
        if not control and lv in LADDER[0]:
            old=load(A1_OUT/'native'/case['id']/p.name);rep=reproduction(old,row)
            require(rep['reparsed_significant_bits_equal'],'REPRODUCTION_MISMATCH')
            saved=load((folder/f'reproduction_{lv[0]}_{lv[1]}.json').relative_to(ROOT))
            require(saved==rep,'REPRODUCTION_RECEIPT_CHANGED')
    if control:
        row=next(iter(rows.values()))
        require(row['zero_action_certificate'] is True and all(F(row[m])==0 for m in METRICS), 'CONTROL_NOT_EXACT_ZERO')
    require(rec['cpu_seconds']==math.fsum(r['call_cpu_seconds'] for r in rows.values()),'POINT_CPU_RECEIPT_CHANGED')
    return rows


def verify_control(cfg):
    rec=load(Path(cfg['output'])/'control_summary.json')
    require(rec.get('status')=='PASS' and rec.get('a2_prereg_sha256')==fingerprint(),'CONTROL_NOT_PASS')
    rows=verify_point(cfg,cfg['control'],True)
    require(rec['level']==list(LADDER[-1][0]) and rec['cpu_seconds']==next(iter(rows.values()))['call_cpu_seconds'],
            'CONTROL_RECEIPT_CHANGED')
    return rec


def worker(cid):
    cfg=verify();case,control=case_of(cfg,cid);check_case(case,cfg,control)
    if not control:verify_control(cfg)
    folder=folder_of(cfg,cid,control);folder.mkdir(parents=True,exist_ok=True)
    existing=folder/'point_summary.json'
    if existing.exists():
        verify_point(cfg,case,control);print(cid,'cached COMPLETED',flush=True);return 0
    lim=cfg['resources']
    resource.setrlimit(resource.RLIMIT_CPU,(lim['case_cpu_seconds'],lim['case_cpu_seconds']+5))
    resource.setrlimit(resource.RLIMIT_AS,(lim['address_space_bytes'],lim['address_space_bytes']))
    # Every scientific/identity/source guard above runs before the engine import.
    from experiments.P4_A1.evaluate import evaluate_level
    ignore=ROOT/cfg['output']/'.gitignore'
    if not ignore.exists():ignore.write_text('native_cache/\n')
    for lv,path in point_files(cfg,case,control):
        if path.exists():row=load(path.relative_to(ROOT))
        else:
            begin=time.process_time()
            try:
                row=evaluate_level(case,lv,ROOT/cfg['output']/'native_cache',cfg['rho']);row['status']='COMPLETED'
            except Exception as exc:
                row=dict(id=cid,K=lv[0],ref=lv[1],status='HOLD_EXECUTION',error=f'{type(exc).__name__}: {exc}',
                         call_cpu_seconds=time.process_time()-begin)
            row.update(parameters=case['parameters'],a2_prereg_sha256=fingerprint(),CF_computed=False)
            write_once(path,row)
        try:validate_row(row,case,lv,fingerprint(),cfg['rho'],complete=False)
        except (KeyError,ValueError,RuntimeError) as exc:
            point_receipt(cfg,case,control,'HOLD_GUARD',[str(exc)]);return 1
        if row['status']!='COMPLETED' or row.get('a1_bug_reasons'):
            why=row.get('a1_bug_reasons') or [row.get('error','execution failure')]
            point_receipt(cfg,case,control,'BUG' if row.get('a1_bug_reasons') else 'HOLD_EXECUTION',why)
            print(cid,lv,'STOP',why,flush=True);return 1
        validate_row(row,case,lv,fingerprint(),cfg['rho'])
        if not control and lv in LADDER[0]:
            old=load(A1_OUT/'native'/cid/path.name);rep=reproduction(old,row)
            rp=folder/f'reproduction_{lv[0]}_{lv[1]}.json'
            if rp.exists():require(load(rp.relative_to(ROOT))==rep,'replay receipt changed')
            else:write_once(rp,rep)
            if not rep['reparsed_significant_bits_equal']:
                point_receipt(cfg,case,control,'REPRODUCTION_MISMATCH',rep['unequal_fields']+rep['bit_mismatch_fields'])
                print(cid,lv,'STOP REPRODUCTION_MISMATCH',rep,flush=True);return 1
        print(cid,list(lv),'COMPLETED',flush=True)
    if control:
        require(row['zero_action_certificate'] is True and all(F(row[m])==0 for m in METRICS),'CONTROL_NOT_EXACT_ZERO')
    rec=point_receipt(cfg,case,control,'COMPLETED')
    if control:
        write_once(ROOT/cfg['output']/'control_summary.json',dict(status='PASS',level=list(LADDER[-1][0]),
                   cpu_seconds=rec['cpu_seconds'],a2_prereg_sha256=fingerprint()))
    return 0


def launch(cid,cfg):
    case,control=case_of(cfg,cid);check_case(case,cfg,control)
    if (folder_of(cfg,cid,control)/'point_summary.json').exists():
        verify_point(cfg,case,control);return 0
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
    command=[sys.executable,'-m','experiments.P4_A2.probe','worker','--case',cid]
    try:
        p=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,timeout=cfg['resources']['case_wall_seconds'])
        log,code=p.stdout+p.stderr,p.returncode
    except subprocess.TimeoutExpired as exc:log,code=str(exc),'TIMEOUT'
    logs=ROOT/cfg['output']/'logs';logs.mkdir(parents=True,exist_ok=True)
    n=len(list(logs.glob(f'{cid}_*.log')))
    with (logs/f'{cid}_{n+1:02d}.log').open('x') as f:f.write(log)
    if code==0:verify_point(cfg,case,control)
    return code


def unique_cpu(cfg):
    out=ROOT/cfg['output'];files=[*out.glob('native/*/level_*.json'),*out.glob('controls/*/level_*.json')]
    return math.fsum(load(p.relative_to(ROOT)).get('call_cpu_seconds',0) for p in sorted(files))


def run(stage):
    cfg=verify();out=ROOT/cfg['output'];out.mkdir(parents=True,exist_ok=True)
    if stage=='control':
        path=out/'control_summary.json'
        if path.exists():verify_control(cfg)
        else:
            code=launch(cfg['control']['id'],cfg)
            if code!=0:
                if not path.exists():write_once(path,dict(status='HOLD_EXECUTION_OR_BUG',exit_code=code,a2_prereg_sha256=fingerprint()))
                print('control HOLD',code,flush=True);return 1
            verify_control(cfg)
        print(load(path.relative_to(ROOT)),flush=True);return 0
    verify_control(cfg)
    summary_path=out/'run_summary.json';ids=[t['id'] for t in cfg['targets']]
    if summary_path.exists():
        require_run_complete(load(summary_path.relative_to(ROOT)),fingerprint(),ids)
        for t in cfg['targets']:verify_point(cfg,t)
        print('run already complete and reproduced');return 0
    done=[];reason=None;cap=cfg['decisions']['cpu_cap_hours']*3600
    for target in cfg['targets']:
        if unique_cpu(cfg)>=cap:reason='CPU_CAP_BEFORE_NEXT_POINT';break
        try:code=launch(target['id'],cfg)
        except (KeyError,ValueError,RuntimeError) as exc:code='HOLD_GUARD:'+str(exc)
        cpu=unique_cpu(cfg)
        print(target['id'],'exit',code,'cumulative evaluation CPU-s incl control',round(cpu,3),flush=True)
        if code!=0:reason=f'POINT_STOP:{target["id"]}:{code}';break
        done.append(target['id'])
        if cpu>cap:reason='CPU_CAP_AFTER_POINT';break
    rec=dict(status='PASS' if not reason and done==ids else 'HOLD',completed_ids=done,
             planned_ids=ids,stop_reason=reason,cpu_seconds=unique_cpu(cfg),a2_prereg_sha256=fingerprint())
    write_once(summary_path,rec);return 0 if rec['status']=='PASS' else 1


def rho_of(reason):
    if reason.startswith('baseline_arithmetic:'):return reason.rsplit(':',1)[1]
    if reason.startswith('baseline_R1:'):return reason.split(':')[1]
    return None


def step_status(levels,main,rhos):
    row_reasons=row_readiness(levels,main);base_reasons,refinement=baseline_readiness(levels,main,rhos)
    failing=sorted({rho_of(r) for r in base_reasons if rho_of(r)},key=F)
    from .diagnose_l44 import pair_record
    named=dict(main=levels[main],K=levels[(main[0]//2,main[1])],dt=levels[(main[0],main[1]//2)])
    diagnostics=[pair_record(named,i) for i in range(len(rhos))]
    return dict(main=list(main),point_ready=not row_reasons and not base_reasons,
                row_reasons=row_reasons,baseline_reasons=base_reasons,failing_rho=failing,
                L00_refinement={r['rho']:r['normalized_difference']['L00'] for r in refinement},
                per_rho_diagnostics=[{k:float(v) if isinstance(v,F) else v for k,v in r.items()} for r in diagnostics])


def classify(n_ready,n,decisions):
    require(type(n_ready) is int and type(n) is int and 0<=n_ready<=n,'invalid ready count')
    if n_ready>=decisions['ladder_resolves_if_at_least']:return 'LADDER_RESOLVES'
    if n_ready<=decisions['ladder_fails_if_at_most']:return decisions['branch_if_ladder_fails']
    return 'INCONCLUSIVE_AUTHOR_DECIDES_WITH_NEW_DL'


def build_decision(cfg):
    out=Path(cfg['output']);ids=[t['id'] for t in cfg['targets']]
    summary=load(out/'run_summary.json')
    require_run_complete(summary,fingerprint(),ids);verify_control(cfg)
    cpu=unique_cpu(cfg)
    require(summary['cpu_seconds']==cpu and cpu<=cfg['decisions']['cpu_cap_hours']*3600,'RUN_CPU_RECEIPT_OR_CAP_INVALID')
    points=[]
    for target in cfg['targets']:
        levels=verify_point(cfg,target)
        steps=[step_status(levels,tuple(step[0]),cfg['rho']) for step in cfg['ladder']]
        first=next((i for i,s in enumerate(steps) if s['point_ready']),None)
        points.append(dict(id=target['id'],target_rho=target['target_rho'],ready_at_step=first,steps=steps,
                           target_L00_refinement_by_step=[{rho:s['L00_refinement'][rho] for rho in target['target_rho']} for s in steps]))
    n_ready=sum(p['ready_at_step'] is not None for p in points)
    return dict(run_id='L44_PROBE',n_targets=len(points),n_ready_within_ladder=n_ready,
                branch=classify(n_ready,len(points),cfg['decisions']),points=points,
                prereg_sha256=fingerprint(),rho_selection_computed=False,regional_medians_computed=False,
                replay_rows_confirmed=3*len(points),CF_outcomes=0,
                limitation='Operational ladder result only; neither H_res nor H_cliff is proved as a physical mechanism')


def decide():
    cfg=verify();decision=build_decision(cfg);path=ROOT/cfg['output']/'decision.json'
    if path.exists():require(load(path.relative_to(ROOT))==decision,'DECISION_CHANGED: never overwrite')
    else:write_once(path,decision)
    print('n_ready_within_ladder',decision['n_ready_within_ladder'],'/',decision['n_targets'],'->',decision['branch'])
    for p in decision['points']:
        print(p['id'],'ready_at_step',p['ready_at_step'],'target L00 refinement by step:',
              [{k:round(v*100,3) for k,v in d.items()} for d in p['target_L00_refinement_by_step']])


def main():
    p=argparse.ArgumentParser();p.add_argument('step',choices=['freeze','control','run','decide','worker']);p.add_argument('--case')
    args=p.parse_args()
    if args.step=='freeze':return freeze()
    if args.step=='worker':return worker(args.case)
    if args.step=='decide':return decide()
    return run(args.step)


if __name__=='__main__':raise SystemExit(main())
