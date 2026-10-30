"""Run the complete selected known-coordinate validation set, no CF or freeze."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
import time

from experiments.R3R_07_numerics.run import verify_prereg
from experiments.R3R_07_confirmation.common import digest,git,write_once
from .prepare import require_ready


def can_launch(spent, active_limits, next_limit, total):
    return spent+sum(n+10 for n in active_limits)+next_limit+10<=total


def main():
    parser = argparse.ArgumentParser()
    for name in ('prereg','out','cache'):
        parser.add_argument('--'+name,type=Path,required=True)
    args = parser.parse_args()
    cfg = verify_prereg(args.prereg)
    audit_path = Path(cfg['calibration_audit']['path'])
    if digest(audit_path)!=cfg['calibration_audit']['sha256']:
        raise ValueError('parent global audit changed')
    audit = json.loads(audit_path.read_text())
    if require_ready(audit)!=cfg['selected_levels']:
        raise ValueError('selected levels do not match the verified global audit')
    args.out.mkdir(parents=True,exist_ok=False)
    write_once(args.out/'attempt.json',dict(owner='Doan Van Tai',
        utc=datetime.now(timezone.utc).isoformat(),source_commit=git('rev-parse','HEAD').decode().strip(),
        prereg_sha256=digest(args.prereg),CF_generated=0))
    mem = {s.split(':')[0]:int(s.split()[1])*1024 for s in Path('/proc/meminfo').read_text().splitlines() if ':' in s}
    pool = min(6*1024**3,mem['MemAvailable']-3*1024**3)-512*1024**2
    peak = audit['measured_peak_rss_MiB']*1024**2
    workers = min(cfg['max_workers'],max(0,int(pool/(1.25*peak+32*1024**2))))
    queue,active,receipts = list(cfg['validation_jobs']),[],[]
    okay = workers>0
    if not okay:queue=[]
    while queue or active:
        spent = cfg['carried_cpu_reserve_seconds']+sum(r['resources']['cpu_seconds'] for r in receipts)
        while queue and len(active)<workers:
            job = queue[0]
            if not can_launch(spent,[item[4]['cpu_seconds'] for item in active],job['cpu_seconds'],cfg['limits']['total_cpu_seconds']):
                if active:break  # drain outstanding calls, then try less concurrency
                okay=False;queue=[];break
            queue.pop(0)
            dest=args.out/job['id']
            log=(args.out/(job['id']+'_controller.log')).open('x')
            proc=subprocess.Popen([sys.executable,'-m','experiments.R3R_12_validation.run_job',
                '--prereg',str(args.prereg),'--out',str(dest),'--cache',str(args.cache),'--job',job['id']],
                stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            active.append((proc,log,dest,job['id'],job))
        for item in list(active):
            proc,log,dest,rid,job=item
            if proc.poll() is None:continue
            log.close();active.remove(item)
            if not (dest/'receipt.json').exists():okay=False;queue=[];continue
            row=json.loads((dest/'receipt.json').read_text());receipts.append(row)
            if row['status']!='COMPLETED':okay=False;queue=[]
            print(json.dumps(dict(id=rid,status=row['status'],cpu_seconds=row['resources']['cpu_seconds'])),flush=True)
        state=dict(utc=datetime.now(timezone.utc).isoformat(),completed=len(receipts),
            active=[item[3] for item in active],queued=len(queue),CF_generated=0)
        tmp=args.out/'progress.tmp';tmp.write_text(json.dumps(state));tmp.replace(args.out/'progress.json')
        if active:time.sleep(.3)
    result=dict(owner='Doan Van Tai',status='PASS_SELECTED_VALIDATIONS' if okay and len(receipts)==len(cfg['validation_jobs']) else 'HOLD_SELECTED_VALIDATIONS',
        receipts=receipts,cpu_seconds=sum(r['resources']['cpu_seconds'] for r in receipts),
        carried_cpu_reserve_seconds=cfg['carried_cpu_reserve_seconds'],workers=workers,
        selected_levels=cfg['selected_levels'],CF_generated=0,n=None,confirmation_root=None,Phase4='HOLD')
    write_once(args.out/'summary.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='receipts'},indent=2))


if __name__ == '__main__':
    main()
