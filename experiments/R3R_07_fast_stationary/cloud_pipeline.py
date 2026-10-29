"""Durable GCP-only preflight and two preregistered marginal profiles, never CF."""
import argparse
from datetime import datetime,timezone
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET


def save(path,data):
    with path.open('x') as f:json.dump(data,f,indent=2);f.write('\n')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    out=parser.parse_args().out
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',
             NUMEXPR_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',MPLBACKEND='Agg')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    save(out/'pipeline_attempt.json',dict(owner='Doan Van Tai',source_commit=commit,
         utc=datetime.now(timezone.utc).isoformat(),CF_generated=0,cloud_workers=2,
         scientific_scope='two registered stationary marginals; not joint outcomes'))
    try:
        with (out/'editable_install.log').open('x') as log:
            subprocess.run([sys.executable,'-m','pip','install','--no-deps','-e','.'],
                           env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        with (out/'full_suite.log').open('x') as log:
            test=subprocess.run([sys.executable,'-m','pytest','-q','--junitxml='+str(out/'full_suite.xml')],
                                env=env,stdout=log,stderr=subprocess.STDOUT,timeout=600)
        suites=list(ET.parse(out/'full_suite.xml').getroot().iter('testsuite'))
        assert test.returncode==0 and sum(int(s.get('tests',0)) for s in suites)==633
        assert all(int(s.get(k,0))==0 for s in suites for k in ('failures','errors','skipped'))
        from experiments.R3R_07_numerics.run import verify_prereg
        from experiments.R3R_07_confirmation.common import digest
        configs=[Path(f'experiments/R3R_07_fast_stationary/prereg_balanced_candidate_{n:02}.json') for n in (6,7)]
        for path in configs:
            cfg=verify_prereg(path);expected=cfg['execution_platform']
            assert platform.python_version()==expected['python']
            assert {p:version(p) for p in expected['packages']}==expected['packages']
        medium=json.loads(Path('results/R3R_numerics/20261029_candidate_05/summary.json').read_text())
        reference=json.loads(Path('results/R3R_numerics/20261029_02/CAL_RATE_100_A/result.json').read_text())
        assert medium['result']['status']=='COMPLETED' and medium['result']['quantiles']==reference['quantiles']
        assert float(medium['result']['law_error_upper'])<=1e-10 and max(medium['result']['posterior_errors'])<=1e-8
        packages=json.loads(configs[0].read_text())['execution_platform']['packages']
        save(out/'preflight.json',dict(status='PASS',source_commit=commit,tests=633,
             python=platform.python_version(),packages={p:version(p) for p in packages},
             platform=platform.platform(),cpu_count=os.cpu_count(),
             meminfo=Path('/proc/meminfo').read_text(),
             config_sha256={str(p):digest(p) for p in configs},medium_quantiles=medium['result']['quantiles'],
             CF_generated=0,Phase4='HOLD'))
        with (out/'pip_freeze.txt').open('x') as f:
            subprocess.run([sys.executable,'-m','pip','freeze'],stdout=f,check=True,timeout=60)
        children=[]
        for n,path in zip((6,7),configs):
            destination=Path(f'results/R3R_numerics/20261029_candidate_{n:02}')
            log=(out/f'probe_{n:02}.log').open('x')
            process=subprocess.Popen([sys.executable,'-m','experiments.R3R_07_fast_stationary.balanced_run',
                                      '--prereg',str(path),'--out',str(destination)],env=env,
                                     stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            children.append((process,log,n,str(destination)))
        save(out/'jobs_started.json',dict(source_commit=commit,utc=datetime.now(timezone.utc).isoformat(),
             jobs=[dict(pid=p.pid,candidate=n,raw=dest) for p,_,n,dest in children],CF_generated=0))
        records=[]
        for process,log,n,dest in children:
            code=process.wait();log.close()
            path=Path(dest)/'summary.json'
            records.append(dict(candidate=n,controller_exit_code=code,summary=str(path),
                                summary_sha256=digest(path) if path.exists() else None))
        save(out/'pipeline_result.json',dict(status='CONTROLLERS_FINISHED_REVIEW_RESULTS',records=records,
             CF_generated=0,Phase4='HOLD',numerical_adoption=False))
    except Exception as exc:
        save(out/'pipeline_result.json',dict(status='FAIL_PREFLIGHT_OR_ORCHESTRATION',
             error_type=type(exc).__name__,error=str(exc),CF_generated=0,Phase4='HOLD'))
        raise


if __name__=='__main__':main()
