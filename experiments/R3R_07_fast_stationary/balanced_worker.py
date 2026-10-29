"""Isolated replacement of interval product grouping; frozen variants retained."""
def main():
    import json,os,platform,sys
    from importlib.metadata import version
    from pathlib import Path
    from experiments.R3R_07_numerics import worker as base
    cfg=json.loads(Path(sys.argv[sys.argv.index('--prereg')+1]).read_text())
    original_stationary=base.stationary
    def recorded_stationary(job,out):
        packages={k:version(k) for k in cfg['execution_platform']['packages']}
        observed=dict(python=platform.python_version(),packages=packages,
                      platform=platform.platform(),logical_cpus=os.cpu_count())
        expected=cfg['execution_platform']
        observed['matches_preregistered_versions']=observed['python']==expected['python'] and packages==expected['packages']
        with (out/'environment.json').open('x') as f:json.dump(observed,f,indent=2)
        if not observed['matches_preregistered_versions']:raise RuntimeError('numerical environment differs from preregistration')
        return original_stationary(job,out)
    base.stationary=recorded_stationary
    from . import algebraic_certificate as original
    from .balanced_certificate import balanced_algebraic_certificate
    from .sparse_worker import main as run
    original.algebraic_certificate=balanced_algebraic_certificate
    return run()


if __name__=='__main__':main()
