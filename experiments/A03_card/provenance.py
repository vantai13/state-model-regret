"""Doan Van Tai — validate A03's two-commit receipt before grid evaluation.

Read-only Git/content checks. No D, engine calls, network writes or author inference.
The receipt proves byte content/order; read-back remains author-attested.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARD = 'notes/phases/PHASE_3_prediction_card.md'
LOCK = 'notes/phases/PHASE_3_prediction_card.lock.json'


def metadata(text):
    blocks = re.findall(r'<!-- A03_METADATA\n(.*?)\n-->', text, re.S)
    if len(blocks) != 1:
        raise PermissionError('A03 metadata block missing or duplicated')
    return json.loads(blocks[0])


def _git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.PIPE)


def _tracked_clean(path, repo):
    try:
        blob = _git(repo, 'show', f'HEAD:{path}')
        dirty = _git(repo, 'status', '--porcelain', '--', path).strip()
        commit = _git(repo, 'log', '-1', '--format=%H', 'HEAD', '--', path).decode().strip()
    except subprocess.CalledProcessError as exc:
        raise PermissionError(f'{path} is not committed in HEAD') from exc
    if dirty or not blob or (Path(repo) / path).read_bytes() != blob:
        raise PermissionError(f'{path} is empty or dirty')
    return commit, blob


def verify_receipt(repo=ROOT, card_path=CARD, lock_path=LOCK):
    card_commit, data = _tracked_clean(card_path, repo)
    info = metadata(data.decode())
    if info.get('status') != 'FROZEN':
        raise PermissionError('A03 card is DRAFT; a committed draft does not unlock A01')
    if any(info.get(k) != 'AUTHOR_ATTESTED' for k in ('already_implied_readback', 'engine_readback')):
        raise PermissionError('A03 read-back record not satisfied')
    lock_commit, raw_lock = _tracked_clean(lock_path, repo)
    lock = json.loads(raw_lock)
    sha = hashlib.sha256(data).hexdigest()
    if lock.get('card_path') != card_path or lock.get('card_commit') != card_commit or lock.get('sha256') != sha:
        raise PermissionError('A03 commit/content differs from the registered receipt')
    if card_commit == lock_commit:
        raise PermissionError('A03 card and receipt must have distinct ordered commits')
    if subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor', card_commit, lock_commit],
                      capture_output=True).returncode:
        raise PermissionError('receipt commit does not follow the card commit')
    for path, expected in (('notes/literature/claims.md', info.get('claims_sha256')),
                           ('notes/design/grid_v1_2.json', info.get('grid_sha256')),
                           ('results/lessons/l3_3/author_attestation.json', info.get('author_attestation_sha256'))):
        if expected is None or not (Path(repo) / path).is_file():
            raise PermissionError(f'missing locked provenance dependency: {path}')
        _, dependency = _tracked_clean(path, repo)
        if hashlib.sha256(dependency).hexdigest() != expected:
            raise PermissionError(f'locked provenance dependency changed: {path}')
    try:
        tag = 'refs/tags/' + lock['tag']
        kind = _git(repo, 'cat-file', '-t', tag).decode().strip()
        target = _git(repo, 'rev-parse', tag + '^{}').decode().strip()
    except (KeyError, subprocess.CalledProcessError) as exc:
        raise PermissionError('registered A03 annotated tag is missing') from exc
    if kind != 'tag' or target != lock_commit:
        raise PermissionError('registered A03 tag does not identify the receipt commit')
    return dict(prediction_card_commit=card_commit, prediction_card_sha256=sha,
                prediction_lock_commit=lock_commit, prediction_tag=lock.get('tag'),
                readback_evidence='AUTHOR_ATTESTED')
