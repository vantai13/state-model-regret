"""Durable finite global calibration. This module never freezes or samples CF."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
from experiments.R3R_07_numerics.run import verify_prereg
from experiments.R3R_07_confirmation.common import git,digest,write_once
from .checks import check,planning_seconds


def main():
    p=argparse.ArgumentParser();p.add_argument('--prereg',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--cache',type=Path,required=True);a=p.parse_args();cfg=verify_prereg(a.prereg)
    a.out.mkdir(parents=True,exist_ok=False)
    write_once(a.out/'attempt.json',dict(owner='Doan Van Tai',source_commit=git('rev-parse','HEAD').decode().strip(),
        prereg_sha256=digest(a.prereg),utc=datetime.now(timezone.utc).isoformat(),CF_generated=0))
    receipts=[];bundles={};all_pass=True;workers=1
    def group(ids,stage,count):
        nonlocal all_pass
        queue=list(ids);active=[]
        while queue or active:
            spent=sum(r['resources']['cpu_seconds'] for r in receipts)
            while queue and len(active)<count:
                if spent+(len(active)+1)*(cfg['limits']['job_cpu_seconds']+10)>cfg['limits']['total_cpu_seconds']:
                    all_pass=False;queue=[];break
                rid=queue.pop(0);out=a.out/stage/rid;out.parent.mkdir(parents=True,exist_ok=True)
                log=(a.out/(stage+'_'+rid+'_controller.log')).open('x')
                proc=subprocess.Popen([sys.executable,'-m','experiments.R3R_08_population_numerics.run_job',
                    '--prereg',str(a.prereg),'--job',rid,'--stage',stage,'--out',str(out),'--cache',str(a.cache)],
                    stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                active.append((proc,log,out,rid))
            for item in list(active):
                proc,log,out,rid=item
                if proc.poll() is None:continue
                log.close();active.remove(item)
                receipt=out/'receipt.json'
                if not receipt.exists():
                    all_pass=False;queue=[];continue
                row=json.loads(receipt.read_text());receipts.append(row)
                if row['status']!='COMPLETED':all_pass=False;queue=[]
                else:
                    data=json.loads((out/'result.json').read_text())
                    if data['kind']=='global_calibration':bundles.setdefault(rid,{}).update(data['levels'])
                print(json.dumps(dict(stage=stage,id=rid,status=row['status'],cpu_seconds=row['resources']['cpu_seconds'])),flush=True)
                payload=dict(utc=datetime.now(timezone.utc).isoformat(),completed=len(receipts),active=[r for _,_,_,r in active],
                             queued=len(queue),cpu_seconds=sum(r['resources']['cpu_seconds'] for r in receipts),CF_generated=0)
                tmp=a.out/'progress.tmp';tmp.write_text(json.dumps(payload));tmp.replace(a.out/'progress.json')
            if active:time.sleep(.2)
        return all_pass
    group([j['id'] for j in cfg['legacy_jobs']+cfg['marginals']],'marginal',1)
    if all_pass:group(cfg['stage0_cases'],'base',1)
    if all_pass:
        peak=max(r['resources']['sampled_peak_rss_bytes'] for r in receipts)
        memory={s.split(':')[0]:int(s.split()[1])*1024 for s in Path('/proc/meminfo').read_text().splitlines() if ':' in s}
        available=min(6*1024**3,memory['MemAvailable']-3*1024**3)-512*1024**2
        workers=min(cfg['max_workers'],max(0,int(available/(1.25*peak+32*1024**2))))
        if workers<1:all_pass=False
        else:
            rest=[j['id'] for j in cfg['cases'] if j['id'] not in cfg['stage0_cases']]
            group(rest[:2],'base',min(2,workers))
            if all_pass:
                peak=max(r['resources']['sampled_peak_rss_bytes'] for r in receipts)
                workers=min(workers,max(1,int(available/(1.25*peak+32*1024**2))))
                group(rest[2:],'base',workers)
    selected=None;history=[]
    if all_pass:
        for stage,K,ref in cfg['candidates']:
            if stage!='base':group([j['id'] for j in cfg['cases']],stage,workers)
            if not all_pass:break
            checks={j['id']:check(bundles[j['id']],K,ref) for j in cfg['cases']}
            history.append(dict(stage=stage,K=K,ref=ref,checks=checks,ready=sum(v['ready'] for v in checks.values()),total=len(checks)))
            if all(v['ready'] for v in checks.values()):selected=(K,ref);break
    timing=[]
    if selected:
        timing=[dict(id=j['id'],**planning_seconds(bundles[j['id']],*selected)) for j in cfg['cases']]
    summary=dict(owner='Doan Van Tai',status='CALIBRATION_READY_REQUIRES_CLOSURE_AUDIT' if selected else 'HOLD_NUMERICAL_AUDIT',
                 selected_levels=list(selected) if selected else None,history=history,receipts=receipts,timing=timing,
                 cpu_seconds=sum(r['resources']['cpu_seconds'] for r in receipts),workers_final=workers,
                 CF_generated=0,confirmation_root=None,n=None,tag_created=False,Phase4='HOLD')
    write_once(a.out/'summary.json',summary)
    write_once(a.out/'levels.json',bundles)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('history','receipts','timing')},indent=2),flush=True)


if __name__=='__main__':main()
