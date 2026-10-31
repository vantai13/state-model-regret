"""Prereg loading and fail-closed guards for A1 runs (no engine import here).

A run is runnable only if: its prereg.json is committed with status FROZEN_BEFORE_PLANT, every
listed source hash matches and is committed, the author choice file is ADOPTED_BY_AUTHOR with the
provenance fields non-empty (explicit delegation is recorded separately), every preserved historical HOLD artifact is byte-unchanged, and the
frozen engine/card/CF receipts still verify (reuses the L4.3 verifier, which checks them).
"""
from fractions import Fraction as F
import json
from pathlib import Path

from experiments.P4_03_map_audit.common import ROOT, sha, git, require, canonical, cf_keys, forbid_cf

PKG = Path('experiments/P4_A1')
RUNS = PKG / 'runs'
INVENTORY = Path('results/lessons/l3r_7/lean_close/collision_inventory_v3.json')
SEALED = Path('experiments/P4_03_map_audit/sealed_scope.json')
AUTHOR_FIELDS = ('decision_verbatim', 'prediction_verbatim', 'why_not_posthoc_in_author_words')


def load(path):
    return json.loads((ROOT / path).read_text())


def committed(path):
    path = Path(path)
    require(git('show', 'HEAD:' + str(path)) == (ROOT / path).read_bytes(), 'uncommitted: ' + str(path))


def check_author(choice_path):
    choice = load(choice_path)
    status = choice.get('status')
    require(status in ('ADOPTED_BY_AUTHOR', 'ADOPTED_BY_AUTHOR_DELEGATION'),
            'AUTHOR_NOT_ADOPTED: ' + str(choice_path))
    if status == 'ADOPTED_BY_AUTHOR_DELEGATION':
        require(choice.get('author_self_written') is False and choice.get('drafted_by') == 'AI',
                'DELEGATION_PROVENANCE_REQUIRED')
        evidence = Path(choice['delegation_path'])
        committed(evidence)
        require(load(evidence).get('user_instruction_verbatim') == choice.get('delegation_verbatim')
                and len(choice.get('delegation_verbatim', '')) >= 20, 'DELEGATION_EVIDENCE_MISMATCH')
    for field in AUTHOR_FIELDS:
        text = str(choice.get(field, '')).strip()
        require(len(text) >= 20 and not text.startswith('<'), 'AUTHOR_FIELD_EMPTY: ' + field)
    return choice


def verify_run(run_id):
    path = RUNS / run_id / 'prereg.json'
    require((ROOT / path).exists(), 'A1_PREREG_NOT_FROZEN: ' + run_id)
    committed(path)
    cfg = load(path)
    require(cfg['status'] == 'FROZEN_BEFORE_PLANT' and cfg['run_id'] == run_id, 'prereg status/run id')
    for name, digest in cfg['source_sha256'].items():
        require(sha(ROOT / name) == digest, 'source changed: ' + name)
        committed(name)
    for name, digest in cfg['preserved_history_sha256'].items():
        require(sha(ROOT / name) == digest, 'HISTORY_CHANGED (never edit old HOLD artifacts): ' + name)
    check_author(cfg['author_choices'])
    from experiments.P4_03_map_audit.common import verify_prereg as verify_frozen
    verify_frozen()                         # frozen engine sources, cards, CF list, L4.1 integrity
    return cfg


def all_cases(cfg):
    return [dict(c, supports=c['supports']) for c in cfg['cases']]


def guard_case(case, cfg, *, control=False):
    require(canonical(case['parameters']) == tuple(case['key']), 'wrong canonical parameters')
    forbid_cf(case['parameters'], cf_keys())
    sealed = {tuple(r['coordinates']) for r in load(SEALED)['sealed']}
    require(tuple(case['key']) not in sealed, 'SEALED_R09_R10: refuse before engine import')
    if control:
        require(case == cfg['control'], 'unregistered control identity')
        require(F(case['parameters'][3]) == 0, 'control must have u=0')
        return
    seen = {r['key'] for r in load(INVENTORY)['records'] if r['namespace'] == 'v1.3_fixed_plant'}
    require('|'.join(case['key']) in seen, 'not an exposed discovery coordinate')
    require(case in cfg['cases'], 'unregistered coordinate or mismatched case identity')
