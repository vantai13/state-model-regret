"""Doan Van Tai — grid provenance guard, checked before any D/cost work.

Commit checks establish ordering and clean content, not scientific card quality.
Paths are explicit defaults for the next lessons; no cards created here.
"""
import json
import subprocess
from pathlib import Path

from experiments.A00_engine.cells_adapter import ROOT, GRID_PATH
from experiments.A03_card.provenance import CARD, LOCK, verify_receipt

FREEZE = 'notes/lessons/A05_F_preregistration.md'


def _git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()


def _committed(path, repo):
    # HEAD:path rejects removed files and files only present on another branch.
    try:
        body = _git(repo, 'show', f'HEAD:{path}')
        commit = _git(repo, 'log', '-1', '--format=%H', 'HEAD', '--', path)
        dirty = _git(repo, 'status', '--porcelain', '--', path)
    except subprocess.CalledProcessError as exc:
        raise PermissionError(f'{path} chưa có trong HEAD') from exc
    if not body or not commit or dirty:
        raise PermissionError(f'{path} chưa commit, trống hoặc đang sửa')
    return commit


def guard(cell_id, *, allow_grid=False, allow_heldout=False, purpose=None,
          repo=ROOT, grid_path=GRID_PATH, card_path=CARD, freeze_path=FREEZE, lock_path=LOCK):
    grid = json.loads(Path(grid_path).read_text())
    ids = {r['id'] for k in ('main', 'heldout', 'controls', 'probes') for r in grid[k]}
    if cell_id not in ids:
        return {'scope': 'toy', 'prediction_card_commit': None, 'freeze_commit': None}
    if not allow_grid or purpose not in ('A01', 'A04', 'A05-T'):
        raise PermissionError('grid evaluation needs explicit allow_grid and runner purpose')
    heldout = {r['id'] for r in grid['heldout']}
    if cell_id in heldout and (not allow_heldout or purpose != 'A05-T'):
        raise PermissionError('held-out: only A05-T after committed A05-F')
    if purpose == 'A05-T' and cell_id not in heldout:
        raise PermissionError('A05-T is reserved for declared held-out cells')
    if purpose == 'A01':
        calibration = {r['id'] for r in grid['calibration']}
        nonmain = {r['id'] for k in ('controls', 'probes') for r in grid[k]}
        if cell_id not in calibration | nonmain:
            raise PermissionError('A01 cannot calibrate on non-calibration main cells')
    receipt = verify_receipt(repo, card_path=card_path, lock_path=lock_path)
    card = receipt['prediction_card_commit']
    freeze = None
    if cell_id in heldout:
        freeze = _committed(freeze_path, repo)
        if subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor', card, freeze],
                          capture_output=True).returncode != 0:
            raise PermissionError('prediction card changed after A05-F; freeze must be renewed')
    return {'scope': 'grid', **receipt, 'freeze_commit': freeze,
            'code_commit': _git(repo, 'rev-parse', 'HEAD'), 'purpose': purpose}
