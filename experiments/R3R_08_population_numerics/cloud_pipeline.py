"""Detached GCP preflight + registered population calibration; never creates CF."""
import argparse
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET


def main():
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);a=p.parse_args()
    base=a.base;cfg=json.loads(Path('experiments/R3R_08_population_numerics/prereg.json').read_text())
    env=dict(os.environ,**cfg['worker_environment'],MPLBACKEND='Agg')
    state={'owner':'Doan Van Tai','CF_generated':0,'Phase4':'HOLD'}
    try:
        for name,wanted in cfg['environment']['packages'].items():
            if version(name)!=wanted:raise ValueError('package version mismatch:'+name)
        if platform.python_version()!=cfg['environment']['python']:raise ValueError('Python version mismatch')
        with (base/'editable_install.log').open('x') as log:
            subprocess.run([sys.executable,'-m','pip','install','--no-deps','-e','.'],env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        with (base/'full_suite.log').open('x') as log:
            test=subprocess.run([sys.executable,'-m','pytest','-q','--junitxml='+str(base/'full_suite.xml')],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=900)
        suites=list(ET.parse(base/'full_suite.xml').getroot().iter('testsuite'))
        if test.returncode or sum(int(s.get('tests',0)) for s in suites)!=668 or any(int(s.get(k,0)) for s in suites for k in ('failures','errors','skipped')):
            raise RuntimeError('cloud full suite did not pass668tests')
        (base/'preflight.json').write_text(json.dumps(dict(status='PASS',tests=668,python=platform.python_version(),packages=cfg['environment']['packages'],CF_generated=0),indent=2)+'\n')
        result=subprocess.run([sys.executable,'-m','experiments.R3R_08_population_numerics.run','--prereg','experiments/R3R_08_population_numerics/prereg.json',
                               '--out','results/R3R_population_numerics/20261029_01','--cache',str(base/'cache')],env=env)
        state.update(status='CALIBRATION_CONTROLLER_FINISHED',controller_exit_code=result.returncode)
    except Exception as exc:state.update(status='FAIL_PREFLIGHT_OR_CONTROLLER',error_type=type(exc).__name__,error=str(exc))
    (base/'pipeline_result.json').write_text(json.dumps(state,indent=2)+'\n')


if __name__=='__main__':main()
