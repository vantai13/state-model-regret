"""Doan Van Tai — L3R.6 card receipt: create once, then verify (fail closed).

L3R.7 must call `verify()` before writing a frame, drawing a sample or opening any engine.
Checks: the freeze commit is an ancestor of HEAD, every frozen file is byte-identical to its
blob at the freeze commit and to the recorded SHA-256, and the contract tag still points to
the contract commit. A changed card means a new version + DL, never an edited receipt.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RECEIPT = Path('notes/phases/PHASE_3R_hypothesis_cards.lock.json')
FROZEN = ('notes/phases/PHASE_3R_hypothesis_cards.md', 'notes/phases/PHASE_3R_forking_paths.md',
          'notes/01_claim_boundary_v1_3.md', 'results/lessons/l3r_6/forking_paths.jsonl',
          'results/lessons/l3r_6/card_checks.json', 'results/lessons/l3r_6/author_choices.json',
          'experiments/R3R_06_cards/verdict.py', 'experiments/R3R_06_cards/stats.py',
          'experiments/R3R_06_cards/regions.py', 'experiments/R3R_06_cards/check_cards.py')


def _git(*a, check=True):
    return subprocess.run(['git', *a], capture_output=True, check=check)


def sha_bytes(b): return hashlib.sha256(b).hexdigest()


def create(card_commit):
    if RECEIPT.exists(): raise SystemExit('receipt exists; a new card version needs a new receipt path and DL')
    files = {p: sha_bytes(_git('show', f'{card_commit}:{p}').stdout) for p in FROZEN}
    for p, h in files.items():
        if sha_bytes(Path(p).read_bytes()) != h: raise SystemExit(f'working copy differs from freeze commit: {p}')
    checks = json.loads(Path('results/lessons/l3r_6/card_checks.json').read_text())
    if not checks['all_ok'] or checks['card_sha256'] != files[FROZEN[0]]:
        raise SystemExit('card checks missing/failed or run on another card text')
    rec = dict(schema_version=1, card_set_id='L3R6', version=1, owner='Doan Van Tai',
               created_utc=datetime.now(timezone.utc).isoformat(),
               card_commit=_git('rev-parse', card_commit).stdout.decode().strip(),
               contract_tag='contract-v1.3', contract_commit='3d2359b32d7bd24f9e9072d5b5b8131bd33fffa0',
               sha256=files, checks_all_ok=True, primaries=['Hyp-MV', 'Hyp-SH'], secondary=None,
               provenance='AI (Claude) drafted; author selected allocation D, regions and rule package verbatim (DL-073)',
               scope='before any L3R.7 frame/sample and before any CF outcome; not evidence; G1 unchanged')
    RECEIPT.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + '\n')
    return rec


def verify():
    rec = json.loads(RECEIPT.read_text())
    errors = []
    if _git('merge-base', '--is-ancestor', rec['card_commit'], 'HEAD', check=False).returncode:
        errors.append('card commit is not an ancestor of HEAD')
    tag = _git('rev-list', '-n1', rec['contract_tag'], check=False).stdout.decode().strip()
    if tag != rec['contract_commit']: errors.append('contract tag moved or missing')
    for p, h in rec['sha256'].items():
        blob = _git('show', f"{rec['card_commit']}:{p}", check=False)
        if blob.returncode or sha_bytes(blob.stdout) != h: errors.append(f'freeze blob mismatch: {p}')
        if not Path(p).exists() or sha_bytes(Path(p).read_bytes()) != h: errors.append(f'working copy changed: {p}')
    return dict(status='PASS' if not errors else 'FAIL', errors=errors, card_commit=rec['card_commit'],
                files=len(rec['sha256']))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--create', metavar='CARD_COMMIT')
    a = ap.parse_args(argv)
    if a.create: create(a.create)
    r = verify()
    print(json.dumps(r, indent=1))
    return 0 if r['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
