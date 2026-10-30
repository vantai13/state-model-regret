"""Registered L4.4 control/benchmark/full runner. No CF, sealed or new A/AB cases."""
import argparse
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from fractions import Fraction as F
import os
import resource
import subprocess
import sys
import time

from .common import (ROOT,HERE,OUT,LEVELS,load,plan,sha,git,require,write_once,
                     verify_prereg,guard_case,validate_row,compare_bundle)


def budget_receipt():
    path=OUT/'budget.json'
    require((ROOT/path).exists(),'full run needs budget receipt')
    require(git('show','HEAD:'+str(path))==(ROOT/path).read_bytes(),'budget must be committed before full')
    receipt=load(path)
    require(receipt['status']=='AUTHORIZED_BY_PREREG_RULE','budget exceeds cap or benchmark failed')
    return receipt


def worker(cid):
    cfg=verify_prereg()
    control=cid==cfg['control']['id']
    case=cfg['control'] if control else next(c for c in plan()['cases'] if c['id']==cid)
    guard_case(case,control=control)
    for stage in ('benchmark','full'):
        path=ROOT/OUT/(stage+'_summary.json')
        if path.exists():require(load(path.relative_to(ROOT))['status']=='PASS','previous HOLD: no new physical calls')
    if not control:
        require(load(OUT/'control_summary.json')['status']=='PASS','zero-action control not passed')
        if cid not in cfg['benchmark_ids']:
            budget_receipt()
    resource.setrlimit(resource.RLIMIT_CPU,(cfg['case_cpu_seconds'],cfg['case_cpu_seconds']+5))
    resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,3*1024**3))
    # Guards and committed source/approval checks run before physical imports.
    from .evaluate import evaluate_level
    folder=ROOT/OUT/('controls' if control else 'native')/cid
    folder.mkdir(parents=True,exist_ok=True)
    fingerprint=sha(ROOT/HERE/'prereg.json')
    rows={}
    requested=LEVELS[:1] if control else LEVELS
    for level in requested:
        path=folder/f'level_{level[0]}_{level[1]}.json'
        if path.exists():
            row=load(path.relative_to(ROOT))
            validate_row(row,case,level,fingerprint)
        else:
            try:
                row=evaluate_level(case,level,ROOT/OUT/'native_cache')
                row['status']='COMPLETED' if row['baseline_sanity_pass'] else 'HOLD_SANITY'
            except Exception as exc:
                row=dict(id=cid,K=level[0],ref=level[1],status='HOLD_EXECUTION_OR_SANITY',
                         error=f'{type(exc).__name__}: {exc}',CF_computed=False)
            row.update(parameters=case['parameters'],audit_prereg_sha256=fingerprint)
            write_once(path,row)
        rows[level]=row
        if row['status']!='COMPLETED':
            record=dict(native_id=cid,status='HOLD',reasons=[row.get('error',row['status'])])
            write_once(folder/'comparison.json',record)
            print(cid,'HOLD',record['reasons'],flush=True)
            return 1
    if control:
        row=rows[LEVELS[0]]
        ok=row.get('zero_action_certificate') is True and row['baseline_sanity']['zero_action_real'] is True
        record=dict(native_id=cid,status='PASS' if ok else 'HOLD',cpu_seconds=row['call_cpu_seconds'],
                    reasons=[] if ok else ['zero control not certified'])
    else:
        record=compare_bundle(case,rows)
    target=folder/'comparison.json'
    if target.exists():require(load(target.relative_to(ROOT))==record,'comparison changed on resume')
    else:write_once(target,record)
    print(cid,record['status'],'cpu',record.get('cpu_seconds'),record.get('reasons'),flush=True)
    return record['status']!='PASS'


def launch(cid,cfg):
    control=cid==cfg['control']['id']
    folder=ROOT/OUT/('controls' if control else 'native')/cid
    target=folder/'comparison.json'
    if target.exists():
        saved=load(target.relative_to(ROOT))
        if saved['status']=='PASS':
            case=cfg['control'] if control else next(c for c in plan()['cases'] if c['id']==cid)
            guard_case(case,control=control)
            rows={lv:load((folder/f'level_{lv[0]}_{lv[1]}.json').relative_to(ROOT))
                  for lv in (LEVELS[:1] if control else LEVELS)}
            for lv,row in rows.items():validate_row(row,case,lv,sha(ROOT/HERE/'prereg.json'))
            if not control:require(compare_bundle(case,rows)==saved,'cached comparison changed')
        return saved
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
    cmd=[str(ROOT/'.venv/bin/python'),'-m','experiments.P4_04_baseline.run','worker','--case',cid]
    try:
        proc=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True,timeout=cfg['case_wall_seconds'])
        log=proc.stdout+proc.stderr
        failure=dict(native_id=cid,status='HOLD_EXECUTION',exit_code=proc.returncode,error=proc.stderr)
    except subprocess.TimeoutExpired as exc:
        log=str(exc);failure=dict(native_id=cid,status='HOLD_RESOURCE_TIMEOUT')
    folder.mkdir(parents=True,exist_ok=True)
    # Preserve separate attempt logs after an interruption; never replace a log.
    attempts=list(folder.glob('worker_*.log'))
    with (folder/f'worker_{len(attempts)+1:02d}.log').open('x') as stream:stream.write(log)
    if not target.exists():write_once(target,failure)
    return load(target.relative_to(ROOT))


def control(cfg):
    summary=ROOT/OUT/'control_summary.json'
    if summary.exists():
        result=load(summary.relative_to(ROOT))
    else:
        result=launch(cfg['control']['id'],cfg)
        write_once(summary,result)
    print(result,flush=True)
    return result['status']!='PASS'


def run_stage(stage,cfg):
    require(load(OUT/'control_summary.json')['status']=='PASS','control HOLD')
    if stage=='full':budget_receipt()
    target=ROOT/OUT/(stage+'_summary.json')
    if target.exists():
        result=load(target.relative_to(ROOT));print(result['status'],flush=True)
        return result['status']!='PASS'
    cases=plan()['cases']
    ids=cfg['benchmark_ids'] if stage=='benchmark' else [c['id'] for c in cases]
    begin=time.monotonic();results=[];stopped=False
    if stage=='benchmark':
        for cid in ids:
            result=launch(cid,cfg);results.append(result)
            print('benchmark',cid,result['status'],result.get('cpu_seconds'),flush=True)
            if result['status']!='PASS':stopped=True;break
    else:
        pending_ids=iter(ids)
        with ThreadPoolExecutor(max_workers=cfg['workers']) as pool:
            active={}
            def schedule():
                cid=next(pending_ids,None)
                if cid is not None:active[pool.submit(launch,cid,cfg)]=cid
            for _ in range(cfg['workers']):schedule()
            while active:
                done,_=wait(active,return_when=FIRST_COMPLETED)
                for future in done:
                    cid=active.pop(future);result=future.result();results.append(result)
                    print('full',cid,result['status'],result.get('cpu_seconds'),flush=True)
                    if result['status']!='PASS':stopped=True
                if sum(r.get('cpu_seconds',0) for r in results)>cfg['cpu_cap_hours']*3600:
                    stopped=True
                if not stopped:
                    while len(active)<cfg['workers']:
                        before=len(active);schedule()
                        if len(active)==before:break
    ok=not stopped and len(results)==len(ids) and all(r['status']=='PASS' for r in results)
    result=dict(stage=stage,status='PASS' if ok else 'HOLD',planned=len(ids),completed=len(results),
                cpu_seconds=sum(r.get('cpu_seconds',0) for r in results),wall_seconds=time.monotonic()-begin,
                results=results,stopped_without_scheduling_more=stopped,
                note='full CPU counts every registered case once, including reused benchmark cases; wall excludes their earlier runs')
    write_once(target,result)
    print({k:result[k] for k in ('stage','status','planned','completed','cpu_seconds','wall_seconds')},flush=True)
    return not ok


def budget(cfg):
    bench=load(OUT/'benchmark_summary.json')
    require(bench['status']=='PASS' and bench['completed']==4,'four passing benchmark cases required')
    cases={c['id']:c for c in plan()['cases']}
    estimate={}
    for region in ('MV+A','SH+A'):
        measured=[r['cpu_seconds'] for r in bench['results'] if region in cases[r['native_id']]['regions']]
        count=sum(region in c['regions'] for c in cases.values())
        estimate[region]=dict(max_bundle_cpu_seconds=max(measured),N=count,
                              conservative_cpu_seconds=1.5*max(measured)*count)
    total=sum(x['conservative_cpu_seconds'] for x in estimate.values())+load(OUT/'control_summary.json')['cpu_seconds']
    receipt=dict(status='AUTHORIZED_BY_PREREG_RULE' if total<=cfg['cpu_cap_hours']*3600 else 'HOLD_BUDGET',
                 rule='1.5*max benchmark bundle per region*N, including benchmark once, plus control',
                 regions=estimate,estimated_cpu_seconds=total,estimated_cpu_hours=total/3600,
                 cap_cpu_hours=cfg['cpu_cap_hours'],prereg_sha256=sha(ROOT/HERE/'prereg.json'))
    write_once(ROOT/OUT/'budget.json',receipt)
    print(receipt,flush=True)
    return receipt['status']!='AUTHORIZED_BY_PREREG_RULE'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('step',choices=['control','benchmark','budget','full','worker'])
    parser.add_argument('--case')
    args=parser.parse_args();cfg=verify_prereg()
    if args.step=='worker':return worker(args.case)
    if args.step=='control':return control(cfg)
    if args.step=='budget':return budget(cfg)
    return run_stage(args.step,cfg)


if __name__=='__main__':raise SystemExit(main())
