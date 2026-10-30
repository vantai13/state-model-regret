"""Preflight and detached recovery of the unchanged registered calibration."""
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--prereg', type=Path, required=True)
    args = parser.parse_args()
    args.base.mkdir(parents=True, exist_ok=False)
    cfg = json.loads(args.prereg.read_text())
    env = dict(os.environ, **cfg['worker_environment'], MPLBACKEND='Agg')
    state = dict(owner='Doan Van Tai', CF_generated=0, Phase4='HOLD')
    try:
        if platform.python_version() != cfg['environment']['python']:
            raise ValueError('Python version mismatch')
        for name, wanted in cfg['environment']['packages'].items():
            if version(name) != wanted:
                raise ValueError('package mismatch: ' + name)
        with (args.base / 'full_suite.log').open('x') as log:
            test = subprocess.run([sys.executable, '-m', 'pytest', '-q',
                '--junitxml=' + str(args.base / 'full_suite.xml')],
                env=env, stdout=log, stderr=subprocess.STDOUT, timeout=900)
        suites = list(ET.parse(args.base / 'full_suite.xml').getroot().iter('testsuite'))
        if (test.returncode or sum(int(s.get('tests', 0)) for s in suites) != cfg['full_tests_required']
                or any(int(s.get(k, 0)) for s in suites for k in ('failures', 'errors', 'skipped'))):
            raise RuntimeError('full preflight count/failures mismatch')
        (args.base / 'preflight.json').write_text(json.dumps(dict(status='PASS',
            tests=cfg['full_tests_required'], python=platform.python_version(),
            packages=cfg['environment']['packages'], CF_generated=0), indent=2) + '\n')
        result = subprocess.run([sys.executable, '-m', 'experiments.R3R_09_numerics_resume.run',
            '--prereg', str(args.prereg)], env=env)
        state.update(status='CALIBRATION_CONTROLLER_FINISHED', controller_exit_code=result.returncode)
    except Exception as exc:
        state.update(status='FAIL_PREFLIGHT_OR_CONTROLLER', error_type=type(exc).__name__, error=str(exc))
    (args.base / 'pipeline_result.json').write_text(json.dumps(state, indent=2) + '\n')
    return 0 if state.get('controller_exit_code') == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
