"""Doan Van Tai — serial resource controller, native evaluator version.

Derived from R3R_08; same bounds and payload checks."""
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
    resources=bounded_call([sys.executable,'-m','experiments.R3R_11_native_population.worker',
        '--prereg',str(a.prereg),'--job',a.job,'--stage',a.stage,'--out',str(a.out),'--cache',str(a.cache)],a.out,
        wall_seconds=limits['job_wall_seconds'],cpu_seconds=limits['job_cpu_seconds'],rss_bytes=limits['rss_bytes'],
        env=dict(os.environ,**cfg['worker_environment']))
    result=a.out/'result.json';data=json.loads(result.read_text()) if result.exists() else {}
    expected='global_calibration' if a.stage!='marginal' else next(j['kind'] for j in cfg['legacy_jobs']+cfg['marginals'] if j['id']==a.job)
    payload_valid=data.get('kind')==expected
    if expected=='global_calibration':payload_valid &= len(data.get('levels',{}))==len(cfg['stage_levels'][a.stage])>0
    row=dict(id=a.job,stage=a.stage,resources=resources,
             payload_valid=payload_valid,status='COMPLETED' if resources['exit_code']==0 and data.get('status')=='COMPLETED' and payload_valid else 'UNRESOLVED')
    with (a.out/'receipt.json').open('x') as f:json.dump(row,f,indent=2)
    return 0


if __name__=='__main__':main()
