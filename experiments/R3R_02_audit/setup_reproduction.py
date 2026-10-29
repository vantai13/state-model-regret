"""Doan Van Tai — rebuild disappeared temporary clone/venv, preserve old receipts."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/lessons/l3r_3'


def main():
    pointer = OUT / 'repro_environment.json'
    old = json.loads(pointer.read_text())
    (OUT / 'repro_environment_before_interruption.json').write_text(json.dumps(old, indent=2) + '\n')
    base = Path(tempfile.mkdtemp(prefix='smr_l3r3_repro_resume_'))
    repo, venv = base / 'repo', base / 'venv'
    subprocess.run(['git', 'clone', '--no-hardlinks', '--no-checkout', str(ROOT), str(repo)], check=True)
    subprocess.run(['git', '-C', str(repo), 'checkout', '--detach', 'explore-v13-pilot'], check=True)
    subprocess.run([sys.executable, '-m', 'venv', str(venv)], check=True)
    requirements = base / 'requirements.txt'; requirements.write_text(old['requirements'])
    with (OUT / 'repro_install_resume.log').open('w') as log:
        subprocess.run([str(venv / 'bin/python'), '-m', 'pip', 'install', '-r', str(requirements)], stdout=log, stderr=subprocess.STDOUT, check=True)
    (base / 'native_tmp').mkdir()
    fresh = dict(old, base=str(base), repo=str(repo), interpreter=str(venv / 'bin/python'),
                 status='READY', temp_disappeared_after_interruption=True,
                 prior_12_completed_jobs_preserved=True)
    pointer.write_text(json.dumps(fresh, indent=2) + '\n')
    print(json.dumps(fresh, indent=2))


if __name__ == '__main__':
    main()
