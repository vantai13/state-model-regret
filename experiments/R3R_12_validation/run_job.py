"""Serial resource accounting per selected validation call."""
import argparse
import json
import os
from pathlib import Path
import sys

from experiments.R3R_07_numerics.run import verify_prereg
from experiments.R3R_07_numerics.budget import bounded_call


def main():
    parser = argparse.ArgumentParser()
    for name in ('prereg','out','cache'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--job',required=True)
    args = parser.parse_args()
    cfg = verify_prereg(args.prereg)
    job = next(j for j in cfg['validation_jobs'] if j['id']==args.job)
    resource = bounded_call([sys.executable,'-m','experiments.R3R_12_validation.worker',
        '--prereg',str(args.prereg),'--job',args.job,'--out',str(args.out),'--cache',str(args.cache)],
        args.out,wall_seconds=job['wall_seconds'],cpu_seconds=job['cpu_seconds'],
        rss_bytes=cfg['limits']['rss_bytes'],env=dict(os.environ,**cfg['worker_environment']))
    path = args.out/'result.json'
    result = json.loads(path.read_text()) if path.exists() else {}
    row = result.get('row',{})
    valid = result.get('job')==job and row.get('id')==job['source_id'] and row.get('K')==job['K'] and row.get('ref')==job['ref']
    record = dict(id=args.job,role=job['role'],resources=resource,payload_valid=valid,
        status='COMPLETED' if resource['exit_code']==0 and result.get('status')=='COMPLETED' and valid else 'UNRESOLVED')
    with (args.out/'receipt.json').open('x') as stream:
        stream.write(json.dumps(record,indent=2)+'\n')


if __name__ == '__main__':
    main()
