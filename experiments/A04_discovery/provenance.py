"""Doan Van Tai — A04 authorization and immutable run/score ordering."""
import hashlib
import json
import subprocess
from pathlib import Path

from experiments.A03_card.provenance import ROOT, _tracked_clean, _git
from experiments.A01_null_refinement.provenance import verify as verify_a01

BASE = 'experiments/A04_discovery/'
PREREG = BASE + 'prereg.md'
LOCK = BASE + 'prereg.lock.json'
GATE = 'notes/phases/A04_execution_gate.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def validate_config(cfg, grid):
    expected = [f'M{i:02}' for i in range(1, 39)]
    controls = ['N01', 'N02', 'N03', 'N04', 'W01', 'S01', 'P01', 'P02']
    if (cfg['main_ids'] != expected or cfg['controls'] != controls or
            cfg['main_ids'] != [r['id'] for r in grid['main']] or
            set(controls) != {r['id'] for k in ('controls', 'probes') for r in grid[k]} or
            cfg['pair_refinements'] != [1, 2] or cfg['primary_refinement'] != 2 or
            cfg['primary_dt_s'] != '1/240' or cfg['heldout_allowed'] is not False):
        raise PermissionError('A04 must use exactly 38 main + 8 controls at ref1/ref2; held-out forbidden')


def verify_gate(gate):
    if (gate.get('v9_status') != 'WAIVED_BY_AUTHOR' or gate.get('decision') != 'DL-054' or
            gate.get('heldout_authorized') is not False):
        raise PermissionError('A04 gate does not match the registered author waiver')


def sources(repo=ROOT):
    paths = [*Path(repo).glob(BASE + '*.py'), Path(repo) / (BASE + 'config.json'),
             Path(repo) / (BASE + 'exposure_plan.md'), Path(repo) / GATE,
             Path(repo) / 'notes/01_definitions_v1_2.md', Path(repo) / 'notes/design/v1_2_protocol.md',
             Path(repo) / 'results/A01/20261027_03/selection.json']
    return {str(p.relative_to(repo)): sha(p) for p in sorted(paths)}


def verify(repo=ROOT):
    inherited = verify_a01(repo)
    pc, body = _tracked_clean(PREREG, repo)
    lc, raw = _tracked_clean(LOCK, repo)
    lock = json.loads(raw)
    if lock['prereg_commit'] != pc or lock['prereg_sha256'] != hashlib.sha256(body).hexdigest():
        raise PermissionError('A04 prereg changed')
    if pc == lc or subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor', pc, lc],
                                 capture_output=True).returncode:
        raise PermissionError('A04 receipt must follow prereg commit')
    actual = sources(repo)
    if actual != lock['source_sha256']:
        raise PermissionError('A04 code/config/gate/exposure differs from receipt')
    for path in actual:
        _tracked_clean(path, repo)
    cfg = read(Path(repo) / (BASE + 'config.json'))
    validate_config(cfg, read(Path(repo) / 'notes/design/grid_v1_2.json'))
    verify_gate(read(Path(repo) / GATE))
    selection = read(Path(repo) / 'results/A01/20261027_03/selection.json')
    if selection['status'] != 'PASS' or selection['final_dt_s'] != '1/240':
        raise PermissionError('A01 final dt not established')
    return dict(prediction_card_commit=inherited['prediction_card_commit'],
                prediction_card_sha256=inherited['prediction_card_sha256'],
                a01_receipt_commit=inherited['prereg_receipt_commit'],
                a01_source_sha256=inherited['source_sha256'],
                prereg_commit=pc, prereg_sha256=lock['prereg_sha256'],
                receipt_commit=lc, source_sha256=actual,
                code_commit=_git(repo, 'rev-parse', 'HEAD').decode().strip(),
                v9_status='WAIVED_BY_AUTHOR', heldout_allowed=False)


def validate_run_inputs(out):
    """Verify outcome bytes before scoring, and again before discovery."""
    out = Path(out)
    index = read(out / 'output_hashes.json')
    for path, expected in index.items():
        if sha(out / path) != expected:
            raise PermissionError(f'A04 output changed: {path}')
    status = read(out / 'validity_status.json')
    if status['hard_failures'] or status['completed_levels'] != 92:
        raise PermissionError('A04 validity failed/incomplete; do not score or discover')
    return index


def require_score_commit(out, repo=ROOT):
    out = Path(out).resolve()
    receipt = verify(repo)
    inputs = validate_run_inputs(out)
    commits = []
    for name in ('card_scores.csv', 'card_details.csv', 'card_scores.json'):
        commit, _ = _tracked_clean(str((out / name).relative_to(repo)), repo)
        commits.append(commit)
    if len(set(commits)) != 1:
        raise PermissionError('score artifacts must share one committed checkpoint')
    score = read(out / 'card_scores.json')
    if (score['input_sha256'] != inputs or
            score['prediction_card_sha256'] != receipt['prediction_card_sha256']):
        raise PermissionError('score source hashes differ from run/card')
    return commits[0]
