"""Single registered coefficient-solver benchmark; no automatic model adoption."""
import argparse
import json
import os
from pathlib import Path
import sys

from experiments.R3R_07_numerics.run import verify_prereg
from experiments.R3R_07_numerics.budget import bounded_call
from experiments.R3R_07_confirmation.common import digest,git,write_once


def main():
    p=argparse.ArgumentParser();p.add_argument('--prereg',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();cfg=verify_prereg(a.prereg)
    if len(cfg['stationary_jobs'])!=1 or cfg['legacy_jobs'] or cfg['conditional_global_jobs']:
        raise ValueError('candidate benchmark requires the one predeclared marginal only')
    out=a.out;out.mkdir(parents=True,exist_ok=False)
    write_once(out/'attempt.json',dict(source_commit=git('rev-parse','HEAD').decode().strip(),prereg_sha256=digest(a.prereg),CF_runs=0))
    job=cfg['stationary_jobs'][0];dest=out/job['id'];limits=cfg['limits']
    r=bounded_call([sys.executable,'-m','experiments.R3R_07_fast_stationary.worker','--prereg',str(a.prereg),'--job',job['id'],'--out',str(dest)],dest,
                   wall_seconds=limits['job_wall_seconds'],cpu_seconds=limits['job_cpu_seconds'],rss_bytes=limits['rss_bytes'],
                   env=dict(os.environ,**cfg['worker_environment']))
    data=json.loads((dest/'result.json').read_text()) if (dest/'result.json').exists() else None
    complete=data is not None and data['status']=='COMPLETED' and r['exit_code']==0
    summary=dict(owner='Doan Van Tai',status='CANDIDATE_PROBE_COMPLETED_NOT_ADOPTED' if complete else 'CANDIDATE_UNRESOLVED',
                 resources=r,result=data,CF_generated=0,Phase4='HOLD',source_scope='one stationary marginal; no global audit')
    write_once(out/'summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='result'},indent=2))


if __name__=='__main__':main()
