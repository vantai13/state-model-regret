"""Doan Van Tai — A05-T one-way gates, checked before any held-out D or cost.

AI (Claude) viết theo ủy quyền trực tiếp của tác giả cho L3.7; không phải bằng
chứng tác giả tự viết. Read-only Git/content checks. No engine, D or outcome.

Gate order used by run.py: frozen A05-F chain -> committed irreversible decision
(decision.json + DL + exposure in one commit, registered A05-T source hashes)
-> exact opening list -> empty output base. A validity-bug retry would need a new
DL and a new decision record; this gate deliberately has no retry switch.
"""
import hashlib
import json
from pathlib import Path
import subprocess

from experiments.A03_card.provenance import ROOT, _tracked_clean
from experiments.A05_freeze.provenance import DISCRIMINATION

BASE = 'experiments/A05_test/'
DECISION = BASE + 'decision.json'
DECISION_LOG = 'notes/02_decision_log.md'
EXPOSURE = 'notes/00_exposure_register.md'
DL_MARKER = '### DL-059'
EXPOSURE_MARKER = 'A05-T_OPENING_DECLARED'
OUTPUT_BASE = 'results/A05_test'
OPEN = ('R01', 'R02', 'R03', 'R04', 'R05', 'R06', 'R07', 'R08', 'R11', 'R12')
SEALED = ('R09', 'R10')
SCORING_DT, CHECK_DT = '1/240', '1/120'


def _git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sources(repo=ROOT):
    return {str(p.relative_to(repo)): sha(p) for p in sorted(Path(repo).glob(BASE + '*.py'))}


def check_ids(ids):
    """Exact frozen opening list; called before any engine/D work."""
    ids = list(ids)
    if ids != list(OPEN) or set(ids) & set(SEALED):
        raise PermissionError('A05-T may open exactly R01-R08,R11,R12; R09/R10 stay sealed')
    return ids


def require_fresh_output(base):
    base = Path(base)
    if base.exists() and any(base.iterdir()):
        raise PermissionError('A05-T đã chạy: one-shot; output base is not empty')


def require_committed_decision(frozen, repo=ROOT):
    if _git(repo, 'status', '--porcelain'):
        raise PermissionError('A05-T runs only from a clean committed tree')
    decision_commit, raw = _tracked_clean(DECISION, repo)
    decision = json.loads(raw)
    freeze = frozen['freeze_commit']
    if freeze == decision_commit or subprocess.run(
            ['git', '-C', str(repo), 'merge-base', '--is-ancestor', freeze, decision_commit],
            capture_output=True).returncode:
        raise PermissionError('decision must be a strict descendant of the A05-F freeze commit')
    touched = set(_git(repo, 'diff-tree', '--no-commit-id', '--name-only', '-r', decision_commit).splitlines())
    if not {DECISION, DECISION_LOG, EXPOSURE} <= touched:
        raise PermissionError('decision record, DL and exposure entry must share one commit')
    for path, marker in ((DECISION_LOG, DL_MARKER), (EXPOSURE, EXPOSURE_MARKER)):
        _, body = _tracked_clean(path, repo)
        if marker.encode() not in body:
            raise PermissionError(f'{path} lacks the committed A05-T decision marker')
    expected = dict(status='IRREVERSIBLE_A05_T_DECISION', open_ids=list(OPEN), sealed_ids=list(SEALED),
                    scoring_dt_s=SCORING_DT, check_dt_s=CHECK_DT, freeze_commit=freeze,
                    predictions_sha256=frozen['predictions_sha256'],
                    discrimination_sha256=frozen['discrimination_sha256'])
    for key, value in expected.items():
        if decision.get(key) != value:
            raise PermissionError(f'decision field {key} differs from the frozen A05-F record')
    registered = decision.get('source_sha256')
    if registered != sources(repo):
        raise PermissionError('A05-T source differs from the registered decision')
    for path in registered:
        _tracked_clean(path, repo)
    disc = json.loads((Path(repo) / DISCRIMINATION).read_bytes())
    check_ids(disc['outcome_open_ids'])
    if sorted(disc['outcomes_not_needed']) != list(SEALED):
        raise PermissionError('frozen discrimination record changed the sealed cells')
    return dict(decision_commit=decision_commit, decided_at=decision.get('decided_at'),
                provenance=decision.get('provenance'))
