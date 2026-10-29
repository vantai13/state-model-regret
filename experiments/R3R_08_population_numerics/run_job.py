"""One serial resource controller per job; CPU accounting is not shared by threads."""
import argparse
import json
import os
from pathlib import Path
import sys
from experiments.R3R_07_numerics.run import verify_prereg
from experiments.R3R_07_numerics.budget import bounded_call


def main():
    p=argparse.ArgumentParser()
    for name in ('prereg','out','cache'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--job',required=True);p.add_argument('--stage',required=True);a=p.parse_args()
    cfg=verify_prereg(a.prereg);limits=cfg['limits']
    resources=bounded_call([sys.executable,'-m','experiments.R3R_08_population_numerics.worker',
        '--prereg',str(a.prereg),'--job',a.job,'--stage',a.stage,'--out',str(a.out),'--cache',str(a.cache)],a.out,
        wall_seconds=limits['job_wall_seconds'],cpu_seconds=limits['job_cpu_seconds'],rss_bytes=limits['rss_bytes'],
        env=dict(os.environ,**cfg['worker_environment']))
    result=a.out/'result.json';data=json.loads(result.read_text()) if result.exists() else {}
    row=dict(id=a.job,stage=a.stage,resources=resources,
             status='COMPLETED' if resources['exit_code']==0 and data.get('status')=='COMPLETED' else 'UNRESOLVED')
    with (a.out/'receipt.json').open('x') as f:json.dump(row,f,indent=2)
    return 0


if __name__=='__main__':main()
