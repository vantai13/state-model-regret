"""Doan Van Tai — check every preexisting file and the allowed new paths."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'results/letter/x5c_alarm'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def run():
    baseline = json.loads((OUT / 'preexisting_inventory.json').read_text())
    changed, missing = [], []
    for name, info in baseline['files'].items():
        p = ROOT / name
        if not p.is_file():
            missing.append(name)
        elif digest(p) != info['sha256']:
            changed.append(name)
    current = set()
    for directory, dirs, names in os.walk(ROOT, followlinks=False):
        dirs[:] = [d for d in dirs if d != '.git' and not (Path(directory) / d).is_symlink()]
        current.update(str((Path(directory) / n).relative_to(ROOT)) for n in names
                       if (Path(directory) / n).is_file() and not (Path(directory) / n).is_symlink())
    created = sorted(current - baseline['files'].keys())
    permitted = {'experiments/letter/x5c_alarm.py', 'experiments/letter/x5c_card.py',
                 'experiments/letter/x5c_gcp.sh', 'tests/test_x5c_alarm.py'}
    outside = [p for p in created if p not in permitted and not p.startswith('results/letter/x5c_alarm/')]
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, env=env, text=True).strip()
    unstaged = subprocess.run(['git', 'diff', '--exit-code'], cwd=ROOT, env=env, capture_output=True, text=True)
    staged = subprocess.run(['git', 'diff', '--cached', '--exit-code'], cwd=ROOT, env=env, capture_output=True, text=True)
    result = dict(owner='Doan Van Tai', status='PASS' if not (changed or missing or outside
        or head != baseline['HEAD'] or unstaged.returncode or staged.returncode) else 'FAIL',
        preexisting_files_checked=len(baseline['files']), changed=changed, missing=missing,
        new_files_outside_allowed=outside, new_files=created, HEAD_before=baseline['HEAD'], HEAD_after=head,
        git_diff_exit=unstaged.returncode, git_cached_diff_exit=staged.returncode,
        scope='All preexisting regular repository files, including .venv; excludes .git and symlink targets.')
    with (OUT / 'workspace_audit.json').open('x') as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'new_files'}, sort_keys=True))
    assert result['status'] == 'PASS'


if __name__ == '__main__':
    run()
