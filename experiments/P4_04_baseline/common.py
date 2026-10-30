"""Fail-closed L4.4 prereg, discovery, sealed and CF guards; no engine imports."""
from fractions import Fraction as F
import json
from pathlib import Path

from experiments.P4_03_map_audit.common import (ROOT, sha, git, require, write_once,
                                                canonical, cf_keys, forbid_cf)

HERE = Path('experiments/P4_04_baseline')
OUT = Path('results/lessons/l4_4')
LEVELS = ((640,4),(320,4),(640,2))
RHOS = ('0','1/200','1/100','1/50','1/20')
INVENTORY = Path('results/lessons/l3r_7/lean_close/collision_inventory_v3.json')
SEALED = Path('experiments/P4_03_map_audit/sealed_scope.json')


def load(path):
    return json.loads((ROOT / path).read_text())


def plan():
    return load(HERE / 'cases.json')


def guard_case(case, *, control=False):
    require(canonical(case['parameters']) == tuple(case['key']), 'wrong canonical parameters')
    forbid_cf(case['parameters'], cf_keys())
    keys = {tuple(r['coordinates']) for r in load(SEALED)['sealed']}
    require(tuple(case['key']) not in keys, 'SEALED_R09_R10: refuse before engine import')
    if control:
        require(F(case['parameters'][3]) == 0, 'control must have u=0')
    else:
        inventory = load(INVENTORY)
        seen = {r['key'] for r in inventory['records'] if r['namespace'] == 'v1.3_fixed_plant'}
        require('|'.join(case['key']) in seen, 'not registered exposed discovery')
        require(case in plan()['cases'], 'unregistered baseline coordinate')
        require(set(case['regions']) <= {'MV+A','SH+A'}, 'A/AB are deferred')


def verify_prereg():
    path = HERE / 'prereg.json'
    require((ROOT / path).exists(), 'BASELINE_PREREG_NOT_FROZEN')
    cfg = load(path)
    require(cfg['status'] == 'FROZEN_BEFORE_PLANT_BASELINE', 'prereg status')
    for name in [str(path), *cfg['source_sha256']]:
        require(git('show', 'HEAD:' + name) == (ROOT / name).read_bytes(), 'uncommitted source: '+name)
    for name, digest in cfg['source_sha256'].items():
        require(sha(ROOT / name) == digest, 'source changed: '+name)
    choice = load(HERE / 'author_choices.json')
    require(choice['status'] == 'ADOPTED_BY_AUTHOR_CHOICE', 'AUTHOR_SPEC_NOT_ADOPTED')
    require('**ADOPTED_BY_AUTHOR_CHOICE**' in (ROOT / HERE / 'spec.md').read_text(), 'draft spec')
    # Keeps the original physical sources, cards, CF list and all four receipts.
    from experiments.P4_03_map_audit.common import verify_prereg as verify_frozen
    verify_frozen()
    return cfg


def validate_row(row, case, level, fingerprint):
    require(row.get('id') == case['id'] and row.get('parameters') == case['parameters'], 'wrong baseline identity')
    require((row.get('K'), row.get('ref')) == tuple(level), 'wrong numerical level')
    require(row.get('audit_prereg_sha256') == fingerprint, 'stale baseline receipt')
    require(row.get('status') == 'COMPLETED' and row.get('CF_computed') is False, 'incomplete/CF row')
    require(row.get('baseline_sanity_pass') is True, 'baseline sanity failed')
    require(tuple(r['rho'] for r in row['baseline']) == RHOS, 'rho grid changed')


def compare_bundle(case, levels):
    from experiments.R3R_14_lean_close.checks import level_ready, ARITH_MAX
    from experiments.R3R_05_contract.rules import TOL_NUM
    reasons=[]
    fingerprint=sha(ROOT / HERE / 'prereg.json')
    for lv in LEVELS:
        try:
            validate_row(levels[lv], case, lv, fingerprint)
        except (KeyError, RuntimeError) as exc:
            reasons.append(str(exc))
    if reasons:
        return dict(native_id=case['id'], status='HOLD', reasons=reasons)
    ready, why = level_ready(levels, LEVELS[0])
    if not ready:
        reasons += why
    fields = dict(L00='error00',L10='error10',GS_theta='GS_theta_error',deltaL10='deltaL10_error')
    refinement=[]
    main=levels[LEVELS[0]];cf=F(main['Cref'])
    for lv,row in levels.items():
        for baseline in row['baseline']:
            if max(F(baseline[e]) / F(row['Cref']) for e in fields.values()) > ARITH_MAX:
                reasons.append(f'baseline_arithmetic:{lv}:{baseline["rho"]}')
    for index,rho in enumerate(RHOS):
        fine=main['baseline'][index]
        ds={}
        for field in fields:
            gf=F(fine[field])
            differences=[]
            for lv in LEVELS[1:]:
                coarse=levels[lv];gc=F(coarse['baseline'][index][field]);cc=F(coarse['Cref'])
                differences.append(max(abs(gf-gc)/cf,abs(gf/cf-gc/cc)))
            measured=max(differences)
            ds[field]=float(measured)
            if measured > TOL_NUM:
                reasons.append(f'baseline_R1:{rho}:{field}')
        refinement.append(dict(rho=rho,normalized_difference=ds))
    return dict(native_id=case['id'], aliases=case['aliases'], regions=case['regions'],
                status='HOLD' if reasons else 'PASS', reasons=reasons,
                native_R1_ready=bool(ready),baseline_refinement=refinement,
                raw_flags=[dict(level=list(lv),arithmetic_pass=r['arithmetic_pass'],
                                validity_errors=r['validity_errors']) for lv,r in levels.items()],
                cpu_seconds=sum(r['call_cpu_seconds'] for r in levels.values()))
