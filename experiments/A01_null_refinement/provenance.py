"""Doan Van Tai — two-commit A01 prereg receipt, checked before any run."""
import hashlib
import json
import subprocess
from pathlib import Path

from experiments.A03_card.provenance import ROOT, _git, _tracked_clean, verify_receipt

PREREG = 'experiments/A01_null_refinement/prereg.md'
LOCK = 'experiments/A01_null_refinement/prereg.lock.json'


def sources(repo=ROOT):
    paths = [*Path(repo).glob('src/smr/**/*.py'), *Path(repo).glob('src/smr/native/*.cpp'),
             *Path(repo).glob('experiments/A00_engine/*.py'),
             *Path(repo).glob('experiments/A01_null_refinement/*.py'),
             *Path(repo).glob('experiments/A03_card/*.py'),
             Path(repo) / 'experiments/A01_null_refinement/config.json']
    return {str(p.relative_to(repo)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def verify(repo=ROOT):
    card = verify_receipt(repo)
    pc, body = _tracked_clean(PREREG, repo)
    lc, raw = _tracked_clean(LOCK, repo)
    lock = json.loads(raw)
    if lock['prereg_commit'] != pc or lock['prereg_sha256'] != hashlib.sha256(body).hexdigest():
        raise PermissionError('A01 prereg changed after registration')
    if pc == lc:
        raise PermissionError('A01 prereg and receipt need distinct commits')
    for before, after in ((card['prediction_card_commit'], pc), (pc, lc)):
        if subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor', before, after],
                          capture_output=True).returncode:
            raise PermissionError('A01/card commit ordering failed')
    actual = sources(repo)
    if actual != lock['source_sha256']:
        raise PermissionError('A01 engine/config differs from registered sources')
    for path in actual:
        _tracked_clean(path, repo)
    return dict(**card, prereg_commit=pc, prereg_sha256=lock['prereg_sha256'],
                prereg_receipt_commit=lc, code_commit=_git(repo, 'rev-parse', 'HEAD').decode().strip(),
                source_sha256=actual)
