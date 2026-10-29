"""Allowlisted calibration only. No random sampling, held-out cells or CF."""
import argparse
from datetime import datetime,timezone
from fractions import Fraction as F
import json
from pathlib import Path
import resource
import time


def cpu():
    child=resource.getrusage(resource.RUSAGE_CHILDREN)
    return time.process_time()+child.ru_utime+child.ru_stime


def main():
    p=argparse.ArgumentParser();p.add_argument('--prereg',type=Path,required=True);p.add_argument('--job',required=True)
    p.add_argument('--stage',required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--cache',type=Path,required=True)
    a=p.parse_args()
    from experiments.R3R_07_numerics.run import verify_prereg
    cfg=verify_prereg(a.prereg);limits=cfg['limits']
    resource.setrlimit(resource.RLIMIT_CPU,(limits['job_cpu_seconds'],limits['job_cpu_seconds']+5))
    resource.setrlimit(resource.RLIMIT_AS,(limits['address_space_bytes'],limits['address_space_bytes']))
    jobs={j['id']:j for j in cfg['legacy_jobs']+cfg['marginals']+cfg['cases']}
    if a.job not in jobs or a.stage not in cfg['stage_levels']:raise ValueError('unregistered computation')
    job=jobs[a.job];start=cpu();wall=time.monotonic();a.out.mkdir(parents=True,exist_ok=True)
    def progress(phase,**values):
        with (a.out/'progress.jsonl').open('a') as log:log.write(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(),phase=phase,**values))+'\n')
    try:
        from . import law_cache
        from . import population
        import numpy as np
        if job['kind']=='legacy_anchor':
            from experiments.R3R_02_audit import pilot_population as old
            from experiments.R3R_07_numerics.run import compare_anchor
            row,pairs=old.evaluate(job['spec'])
            np.savez_compressed(a.out/'pairs.npz',pairs=np.asarray(pairs,dtype=str))
            result=dict(status='COMPLETED',kind=job['kind'],row=row)
            comparison=compare_anchor(job,result,a.out)
            (a.out/'anchor_comparison.json').write_text(json.dumps(comparison,indent=2)+'\n')
            if comparison['status']!='PASS':raise ArithmeticError('legacy anchor replay mismatch; see comparison')
            result['comparison']=comparison
        elif job['kind']=='stationary_only':
            unit,law,key=law_cache.get(F(job['lambda']),F(job['managed']),F(job['kappa']),job['ref'],a.cache/'stationary',progress)
            qs=law.quantiles(np.array(['.5','.9'],dtype=np.longdouble),law.law.plan['cutoff'])
            below,eb=law.cdf(qs-1);above,ea=law.cdf(qs)
            alphas=np.array(['.5','.9'],dtype=np.longdouble)
            if not np.all((below.sum(axis=1)+eb.sum(axis=1)<alphas)&(above.sum(axis=1)-ea.sum(axis=1)>=alphas)):
                raise ArithmeticError('quantile not certified')
            posterior,errors=law.posterior(np.r_[0,qs])
            if 'expected_quantiles' in job and list(map(int,qs))!=job['expected_quantiles']:raise ArithmeticError('known quantiles mismatch')
            result=dict(status='COMPLETED',kind=job['kind'],unit=str(unit),quantiles=list(map(int,qs)),
                        posterior_errors=list(map(float,errors)),law_error=str(law.law.error),moment_error=str(law.mean_error),cache_key=key)
        else:
            levels={}
            for K,ref in cfg['stage_levels'][a.stage]:
                spec=[job['id'],*job['parameters'][:5],ref,K,job['parameters'][5]]
                begin=cpu();row=population.evaluate(spec,a.cache,progress)
                row['cpu_seconds']=cpu()-begin;levels[f'{K}:{ref}']=row
                with (a.out/f'level_{K}_{ref}.json').open('x') as f:json.dump(row,f,indent=2)
                # Cross-quadrature inequalities can fail as an estimator error
                # and must enter finite K/ref refinement. Same-measure algebra
                # cannot be repaired by K and is a hard validity stop.
                hard=[v for v in row['validity_errors'] if v in ('negative_nonnegative_contrast:G_M','negative_nonnegative_contrast:G_M_S1','model_gain_flip_identity')]
                if hard:raise ArithmeticError('population hard validity check failed: '+','.join(hard))
                if job.get('role')=='zero_control' and any(F(row[key])!=0 for key in population.CONTRASTS):raise ArithmeticError('zero control not exactly zero')
            result=dict(status='COMPLETED',kind=job['kind'],levels=levels)
        result.update(id=job['id'],stage=a.stage,CPU_seconds=cpu()-start,wall_seconds=time.monotonic()-wall,
                      peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,CF_generated=0)
    except Exception as exc:
        result=dict(status='ERROR',id=job['id'],stage=a.stage,error_type=type(exc).__name__,error=str(exc),
                    CPU_seconds=cpu()-start,wall_seconds=time.monotonic()-wall,CF_generated=0)
    with (a.out/'result.json').open('x') as f:json.dump(result,f,indent=2)
    progress('worker_finished',status=result['status'])
    return 0 if result['status']=='COMPLETED' else 1


if __name__=='__main__':raise SystemExit(main())
