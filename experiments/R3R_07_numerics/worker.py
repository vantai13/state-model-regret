"""Single numerical job; resource limits precede NumPy/engine imports."""
import argparse
from datetime import datetime,timezone
from fractions import Fraction as F
import json
from pathlib import Path
import resource
import time


def checkpoint(out,phase,**details):
    record=dict(utc=datetime.now(timezone.utc).isoformat(),phase=phase,**details)
    with (out/'progress.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')


def registered_stage0_job(config,job_id):
    jobs={j['id']:j for j in config['legacy_jobs']+config['stationary_jobs']}
    if job_id not in jobs:
        raise ValueError('job not authorized for stage0; global calibration needs a separate audit activation')
    return jobs[job_id]


def trace_spectral(out):
    """Observe calls without changing roots, tolerances or returned arrays."""
    import smr.stationary_spectral as SS
    original_roots=SS.np.roots
    def roots(coefficients):
        checkpoint(out,'numpy_roots_started',degree=len(coefficients)-1)
        result=original_roots(coefficients)
        checkpoint(out,'numpy_roots_completed',roots=len(result))
        return result
    SS.np.roots=roots
    original_lu=SS.mp.lu_solve
    def lu(matrix,rhs,*a,**kw):
        checkpoint(out,'mpmath_lu_started',rows=matrix.rows)
        result=original_lu(matrix,rhs,*a,**kw)
        checkpoint(out,'mpmath_lu_completed',rows=matrix.rows)
        return result
    SS.mp.lu_solve=lu


def stationary(job,out):
    trace_spectral(out)
    from smr.cells import law_for,lattice
    lam,u,kappa=map(F,(job['lambda'],job['managed'],job['kappa']))
    ref=job['ref']
    unit,steps=lattice((lam-6,lam+6),u,F(1,120*ref))
    checkpoint(out,'law_started',unit=str(unit),increments=list(steps))
    unit,law=law_for(lam,u,kappa,ref)
    qs=[law.quantile(F(a,10)) for a in (5,9)]
    posterior=[law.posterior(q) for q in (0,*qs)]
    return dict(id=job['id'],kind='stationary_only',unit=str(unit),increments=list(steps),
                degree=max(steps)-min(steps),certificate=law.certificate,
                law_error_upper=str(law.error),quantiles=qs,posterior_errors=[x[1] for x in posterior],
                stable_terms=len(law.terms),joint_costs_or_contrasts_computed=False)


def population(job,out):
    trace_spectral(out)
    from experiments.R3R_02_audit import pilot_population as P
    import numpy as np
    checkpoint(out,'population_started',id=job['id'],ref=job['spec'][6],K=job['spec'][7])
    row,pairs=P.evaluate(job['spec'])
    np.savez_compressed(out/'pairs.npz',pairs=np.asarray(pairs,dtype=str))
    return dict(id=job['id'],kind=job['kind'],row=row,pairs=len(pairs))


def main(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('--prereg',type=Path,required=True)
    ap.add_argument('--job',required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args(argv)
    from .run import verify_prereg
    config=verify_prereg(a.prereg)
    job=registered_stage0_job(config,a.job)
    limits=config['limits'];cpu=limits['job_cpu_seconds']
    resource.setrlimit(resource.RLIMIT_CPU,(cpu,cpu+5))
    resource.setrlimit(resource.RLIMIT_AS,(limits['address_space_bytes'],limits['address_space_bytes']))
    start=time.monotonic();out=a.out
    checkpoint(out,'worker_started',job=a.job)
    try:
        result=stationary(job,out) if job['kind']=='stationary_only' else population(job,out)
        result['status']='COMPLETED'
    except Exception as exc:
        result=dict(id=a.job,status='ERROR',error_type=type(exc).__name__,error=str(exc))
    result.update(wall_seconds=time.monotonic()-start,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                  process_cpu_seconds=time.process_time())
    with (out/'result.json').open('x') as f:json.dump(result,f,indent=2,allow_nan=True)
    checkpoint(out,'worker_finished',status=result['status'])
    return 0 if result['status']=='COMPLETED' else 1


if __name__=='__main__':raise SystemExit(main())
