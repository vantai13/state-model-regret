"""Doan Van Tai — registered, write-once L4.3 replay/native audit (AI theo ủy quyền).

Native stages refuse incomplete/uncommitted scope, failed Part A, any CF collision,
or modified frozen source. A HOLD stops scheduling additional physical cases.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED
from fractions import Fraction as F
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

from .common import ROOT,HERE,OUT,CF,LEVELS,METRICS,sha,git,require,write_once,cf_keys,forbid_cf,verify_prereg,compare,canonical


def read_plan():return json.loads((ROOT/HERE/'cases.json').read_text())


def replay():
    config=verify_prereg()
    clean=Path(config['clean_worktree'])
    if not clean.exists():
        subprocess.run(['git','worktree','add','--detach',str(clean),config['map_commit']],cwd=ROOT,check=True)
    require(subprocess.check_output(['git','rev-parse','HEAD'],cwd=clean,text=True).strip()==config['map_commit'],'wrong clean tag')
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=clean).strip(),'tag worktree not clean')
    target=ROOT/OUT/'partA';target.mkdir(parents=True,exist_ok=True)
    recount=target/'recount'
    if not recount.exists():
        command=[str(ROOT/'.venv/bin/python'),'-m','experiments.P4_01_recount.recount_map','--out',str(recount)]
        p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
        write_once(target/'recount_command.json',dict(command=command,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
        require(p.returncode==0,'identity recount failed')
    specs=json.loads((ROOT/HERE/'bit_specs.json').read_text())['rows']
    forbidden=cf_keys()
    for item in specs:
        s=item['spec'];age=F(s[9]);parameters=[s[1],s[2],str(F(s[3])/age),s[4],str(F(s[5])/age),s[8]]
        forbid_cf(parameters,forbidden)
    env=dict(os.environ,PYTHONPATH=str(clean/'src')+os.pathsep+str(clean),
             OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
    def job(i):
        item=specs[i];path=target/(item['id']+'.json')
        if path.exists():return json.loads(path.read_text())
        command=[str(ROOT/'.venv/bin/python'),str(ROOT/HERE/'replay_worker.py'),'--spec',str(ROOT/HERE/'bit_specs.json'),
                 '--index',str(i),'--output',str(path),'--clean',str(clean)]
        try:p=subprocess.run(command,cwd=clean,env=env,capture_output=True,text=True,timeout=1200)
        except subprocess.TimeoutExpired:
            if not path.exists():write_once(path,dict(id=item['id'],status='HOLD_TIMEOUT'))
            return json.loads(path.read_text())
        (target/(item['id']+'.log')).write_text(p.stdout+p.stderr)
        if not path.exists():write_once(path,dict(id=item['id'],status='HOLD_EXECUTION_ERROR',exit_code=p.returncode,error=p.stderr))
        result=json.loads(path.read_text());print(item['id'],result['status'],flush=True)
        return result
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(job,range(len(specs))))
    summary=dict(status='PASS' if all(r['status']=='PASS' for r in results) else 'HOLD',rows=len(results),
                 passed=sum(r['status']=='PASS' for r in results),comparisons=9*len(results),results=results,
                 original_K2='UNVERIFIED: original six IDs unavailable; six supplemental map1 rows are independent selections',
                 K6='UNVERIFIED: native_probe_summary.csv unavailable',
                 clean_worktree=str(clean),tag=config['map_commit'],recount=json.loads((recount/'recount.json').read_text())['checks'])
    path=target/'summary.json'
    if path.exists():require(json.loads(path.read_text())==summary,'Part A summary changed on resume')
    else:write_once(path,summary)
    print(json.dumps({k:summary[k] for k in ('status','rows','passed','comparisons')},indent=2))
    return summary['status']!='PASS'


def worker(case_id):
    config=verify_prereg();plan=read_plan();case=next(c for c in plan['cases'] if c['id']==case_id)
    partA=json.loads((ROOT/OUT/'partA/summary.json').read_text())
    require(partA['status']=='PASS','PART_A_HOLD: refuse worker before engine import')
    for stage in ('benchmark','full'):
        previous=ROOT/OUT/(stage+'_summary.json')
        if previous.exists():require(json.loads(previous.read_text())['status']=='PASS','previous audit HOLD: no new calls')
    if case_id not in config['benchmark_ids']:
        path=OUT/'budget.json'
        require(git('show','HEAD:'+str(path))==(ROOT/path).read_bytes(),'full worker requires committed budget')
        require(json.loads((ROOT/path).read_text())['status']=='AUTHORIZED_BY_PREREG_RULE','budget not authorized')
    forbid_cf(case['parameters'],cf_keys())
    require(canonical(case['parameters'])==tuple(case['key']),'case canonical key mismatch')
    inventory=json.loads((ROOT/'results/lessons/l3r_7/lean_close/collision_inventory_v3.json').read_text())
    seen={r['key'] for r in inventory['records'] if r['namespace']=='v1.3_fixed_plant'}
    require('|'.join(case['key']) in seen,'not an already exposed/reserved discovery coordinate')
    resource.setrlimit(resource.RLIMIT_CPU,(1800,1805))
    resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,3*1024**3))
    # All guards above run BEFORE this physical-engine import/configure.
    from experiments.R3R_14_lean_close import engine
    engine.configure()
    folder=ROOT/OUT/'native'/case_id;folder.mkdir(parents=True,exist_ok=True)
    fingerprint=sha(ROOT/HERE/'prereg.json');rows={}
    for K,ref in LEVELS:
        path=folder/f'level_{K}_{ref}.json'
        if path.exists():
            row=json.loads(path.read_text())
            require(row.get('audit_prereg_sha256')==fingerprint,'stale resumed row')
            require(row.get('parameters')==case['parameters'] and row.get('id')==case_id,'resumed row identity changed')
        else:
            try:
                row=engine.evaluate_level(case_id,case['parameters'],K,ref,ROOT/OUT/'native_cache')
                row['status']='COMPLETED'
            except Exception as exc:
                row=dict(id=case_id,K=K,ref=ref,status='UNRESOLVED_EXECUTION_ERROR',error=f'{type(exc).__name__}: {exc}')
            row.update(parameters=case['parameters'],audit_prereg_sha256=fingerprint)
            write_once(path,row)
        rows[(K,ref)]=row
    results=[compare(a,case,rows) for a in plan['aliases'] if a['native_id']==case_id]
    record=dict(native_id=case_id,status='HOLD' if any(r['status']=='HOLD' for r in results) else 'PASS',
                aliases=results,cpu_seconds=sum(r.get('call_cpu_seconds',0) for r in rows.values()))
    output=folder/'comparison.json'
    if output.exists():require(json.loads(output.read_text())==record,'comparison changed on resume')
    else:write_once(output,record)
    return record['status']!='PASS'


def run_native(stage):
    config=verify_prereg()
    partA=json.loads((ROOT/OUT/'partA/summary.json').read_text())
    require(partA['status']=='PASS','PART_A_HOLD: native audit not allowed')
    if stage=='benchmark':ids=config['benchmark_ids'];workers=1
    else:
        budget_path=OUT/'budget.json';budget=json.loads((ROOT/budget_path).read_text())
        require(git('show','HEAD:'+str(budget_path))==(ROOT/budget_path).read_bytes(),'budget must be committed before full run')
        require(budget['status']=='AUTHORIZED_BY_PREREG_RULE','budget not authorized')
        ids=[c['id'] for c in read_plan()['cases']];workers=2
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
    def call(cid):
        path=ROOT/OUT/'native'/cid/'comparison.json'
        cmd=[str(ROOT/'.venv/bin/python'),'-m','experiments.P4_03_map_audit.run','worker','--case',cid]
        try:p=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True,timeout=2400)
        except subprocess.TimeoutExpired:
            return dict(native_id=cid,status='HOLD_RESOURCE_TIMEOUT')
        logs=ROOT/OUT/'native'/cid/'worker.log';logs.parent.mkdir(parents=True,exist_ok=True)
        if logs.exists():logs=logs.with_name(f'worker_resume_{time.time_ns()}.log')
        with logs.open('x') as f:f.write(p.stdout+p.stderr)
        if path.exists():
            record=json.loads(path.read_text())
            if p.returncode==0 and record['status']=='PASS' or p.returncode==1 and record['status']=='HOLD':
                return record
        return dict(native_id=cid,status='HOLD_EXECUTION_ERROR',exit_code=p.returncode,error=p.stderr)
    # Stop scheduling as soon as any case returns HOLD; finish and keep in-flight cases.
    pending_ids=iter(ids);finished=[];stop=False
    started=time.monotonic()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pending={}
        def schedule():
            for cid in pending_ids:
                future=pool.submit(call,cid);pending[future]=cid;return
        for _ in range(workers):schedule()
        while pending:
            done,_=wait(pending,return_when=FIRST_COMPLETED)
            for future in done:
                cid=pending.pop(future);result=future.result();finished.append(result)
                print(f'{stage} {cid} {result["status"]} cpu={result.get("cpu_seconds",0):.2f}',flush=True)
                if result['status']!='PASS':stop=True
            cpu=sum(r.get('cpu_seconds',0) for r in finished)
            if cpu>config['resource_cap_cpu_hours']*3600:stop=True
            if not stop:
                while len(pending)<workers:
                    before=len(pending);schedule()
                    if len(pending)==before:break
    summary=dict(stage=stage,status='HOLD' if stop else 'PASS',planned=len(ids),completed=len(finished),
                 cpu_seconds=sum(r.get('cpu_seconds',0) for r in finished),wall_seconds=time.monotonic()-started,
                 results=finished,stopped_without_scheduling_more=stop)
    write_once(ROOT/OUT/(stage+'_summary.json'),summary)
    print(json.dumps({k:summary[k] for k in ('stage','status','planned','completed','cpu_seconds','wall_seconds')},indent=2))
    return summary['status']!='PASS'


def main():
    p=argparse.ArgumentParser();p.add_argument('step',choices=['replay','benchmark','full','worker']);p.add_argument('--case')
    a=p.parse_args()
    if a.step=='replay':return replay()
    if a.step=='worker':return worker(a.case)
    return run_native(a.step)


if __name__=='__main__':raise SystemExit(main())
