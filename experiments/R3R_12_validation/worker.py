"""Only the committed selected-level validation allowlist; no sampler or CF."""
import argparse
from fractions import Fraction as F
import json
from pathlib import Path
import resource
import time

from experiments.R3R_07_numerics.run import verify_prereg
from experiments.R3R_07_confirmation.score import require_identical_models, require_zero_control
from experiments.R3R_11_native_population.worker import configure_engine
from experiments.R3R_08_population_numerics import population


def cpu():
    child = resource.getrusage(resource.RUSAGE_CHILDREN)
    return time.process_time()+child.ru_utime+child.ru_stime


def main():
    parser = argparse.ArgumentParser()
    for name in ('prereg','out','cache'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--job',required=True)
    args = parser.parse_args()
    cfg = verify_prereg(args.prereg)
    jobs = {j['id']:j for j in cfg['validation_jobs']}
    if len(jobs) != len(cfg['validation_jobs']) or args.job not in jobs:
        raise ValueError('not a unique registered validation job')
    job = jobs[args.job]
    resource.setrlimit(resource.RLIMIT_CPU,(job['cpu_seconds'],job['cpu_seconds']+5))
    resource.setrlimit(resource.RLIMIT_AS,(cfg['limits']['address_space_bytes'],cfg['limits']['address_space_bytes']))
    configure_engine()
    start = cpu()
    try:
        p = job['parameters']
        spec = [job['source_id'],*p[:5],job['ref'],job['K'],p[5]]
        row = population.evaluate(spec,args.cache,identical_models=job['role']=='identical')
        if job['role'] == 'identical':
            require_identical_models(row)
        if job['role'] == 'zero':
            require_zero_control({key:row[key] for key in population.CONTRASTS})
        if not row['arithmetic_pass'] or row['validity_errors']:
            raise ArithmeticError('selected validation arithmetic/validity did not pass')
        result = dict(owner='Doan Van Tai',status='COMPLETED',job=job,row=row,
                      cpu_seconds=cpu()-start,CF_generated=0)
    except Exception as exc:
        result = dict(owner='Doan Van Tai',status='ERROR',job=job,
                      error_type=type(exc).__name__,error=str(exc),CF_generated=0)
    with (args.out/'result.json').open('x') as stream:
        stream.write(json.dumps(result,indent=2)+'\n')
    return 0 if result['status']=='COMPLETED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
