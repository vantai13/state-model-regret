"""Doan Van Tai — synthetic provenance fixtures; no real research attestation."""
import hashlib
import json
from pathlib import Path

from experiments.A03_card.provenance import CARD, LOCK


def make_card(repo, status='FROZEN'):
    info = dict(status=status, already_implied_readback='AUTHOR_ATTESTED', engine_readback='AUTHOR_ATTESTED')
    for key, path, content in (
            ('claims_sha256', 'notes/literature/claims.md', 'Synthetic fixture claims\n'),
            ('grid_sha256', 'notes/design/grid_v1_2.json', 'Synthetic fixture grid hash input\n'),
            ('author_attestation_sha256', 'results/lessons/l3_3/author_attestation.json', 'Synthetic fixture attestation, not a real person\n')):
        target = Path(repo) / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        info[key] = hashlib.sha256(target.read_bytes()).hexdigest()
    path = Path(repo) / CARD
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('# Synthetic card fixture\n<!-- A03_METADATA\n' + json.dumps(info) + '\n-->\n')
    return path


def make_lock(repo, card_commit):
    path = Path(repo) / LOCK
    path.write_text(json.dumps(dict(card_path=CARD, card_commit=card_commit,
                                    sha256=hashlib.sha256((Path(repo) / CARD).read_bytes()).hexdigest(),
                                    tag='fixture-a03'), indent=2) + '\n')
    return path
