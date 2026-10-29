"""Fail-closed preflight. Future closure schemas are design interfaces, not approvals."""
import json
from fractions import Fraction as F
from pathlib import Path

from experiments.R3R_05_contract.freeze import verify_lock
from .common import NUMERICS_TAG, digest, git, sha, verified_card, check_committed, verify_tool_hashes

NUMERIC_SPEC = 'notes/design/numerics_v1_3_1.json'
NUMERIC_RECEIPT = 'notes/phases/contract_v1_3_1.lock.json'


def verify_numerics():
    verify_lock()
    verified_card()
    if git('cat-file','-t',NUMERICS_TAG).decode().strip() != 'tag':
        raise ValueError('annotated numerics v1.3.1 tag required')
    commit = git('rev-parse',NUMERICS_TAG+'^{commit}').decode().strip()
    git('merge-base','--is-ancestor',commit,'HEAD')
    receipt = json.loads(Path(NUMERIC_RECEIPT).read_text())
    spec_blob = git('show',f'{commit}:{NUMERIC_SPEC}')
    spec = json.loads(spec_blob)
    if receipt.get('tag_object')!=git('rev-parse',NUMERICS_TAG).decode().strip() or receipt.get('commit')!=commit:
        raise ValueError('numerics tag/receipt mismatch')
    paths = spec.get('freeze_paths')
    if not isinstance(paths,list) or len(paths)!=len(set(paths)) or NUMERIC_SPEC not in paths or len(paths)<3:
        raise ValueError('numerics frozen manifest must include spec, audit evidence and code')
    expected = {p:sha(git('show',f'{commit}:{p}')) for p in paths}
    if expected!=receipt.get('source_sha256') or any(digest(p)!=h for p,h in expected.items()):
        raise ValueError('numerics exact manifest/blob mismatch')
    validate_numerics_spec(spec)
    return spec


def validate_numerics_spec(spec):
    required = ('K_star','ref_star','dt_star','S1_route','quadrature_tail_policy',
                'p95_bundle_cpu_seconds','fixed_validation_cpu_seconds','r_coverage_report')
    if spec.get('status')!='CLOSED_WITH_DECLARED_SCOPE' or any(spec.get(k) in (None,'',False) for k in required):
        raise ValueError('numerical levels/method/timing/coverage remain deferred')
    K,ref=spec['K_star'],spec['ref_star']
    if any(isinstance(x,bool) or not isinstance(x,int) or x<2 or x%2 for x in (K,ref)) or F(spec['dt_star'])!=F(1,120*ref):
        raise ValueError('invalid global levels/dt; both coarse-axis neighbours required')
    if F(str(spec['p95_bundle_cpu_seconds']))<=0 or F(str(spec['fixed_validation_cpu_seconds']))<0:
        raise ValueError('invalid measured timing')
    coverage=spec.get('coverage',{})
    for key in ('kappa_3_h_16','rational_rate_resolution_1_1000','interior_lattice_feasibility'):
        if coverage.get(key) is not True:
            raise ValueError('missing numerics coverage: '+key)


def verify_hashes(paths):
    """Require the exact allowlisted manifest, never accept a partial manifest."""
    required={'prereg','frame','inventory','card_receipt','scorer','sampler','numerics_receipt'}
    if set(paths)!=required:
        raise ValueError('execution receipt must cover the exact artifact set')
    for role,record in paths.items():
        if set(record)!={'path','sha256'} or digest(record['path'])!=record['sha256']:
            raise ValueError('artifact hash mismatch: '+role)
        check_committed(record['path'])


def verify_execution_receipt(path):
    card=verified_card()
    verify_numerics()
    receipt=json.loads(Path(path).read_text())
    check_committed(path)
    verify_hashes(receipt['artifacts'])
    files={k:Path(v['path']) for k,v in receipt['artifacts'].items()}
    # Exact source identity in addition to hashes: no alternative scorer/sampler.
    for key,wanted in (('card_receipt','notes/phases/PHASE_3R_hypothesis_cards.lock.json'),
                       ('scorer','experiments/R3R_06_cards/verdict.py'),
                       ('sampler','experiments/R3R_07_confirmation/sampler.py'),
                       ('numerics_receipt',NUMERIC_RECEIPT)):
        if files[key].resolve()!=Path(wanted).resolve():
            raise ValueError('unexpected artifact path: '+key)
    prereg=json.loads(files['prereg'].read_text())
    verify_tool_hashes(prereg['tool_sha256'])
    frame=json.loads(files['frame'].read_text())
    inventory=json.loads(files['inventory'].read_text())
    if frame['prereg_sha256']!=digest(files['prereg']):
        raise ValueError('frame belongs to a different prereg')
    if prereg['inventory']['sha256']!=digest(files['inventory']):
        raise ValueError('prereg inventory binding mismatch')
    from .frame import validate_rows
    validate_rows(frame['rows'],card,prereg['n']['scored'],prereg['n']['bnd'],inventory,purpose='COMMITTED_CONFIRMATION')
    gate=json.loads(Path(receipt['gate_path']).read_text())
    if digest(receipt['gate_path'])!=receipt['gate_sha256']:
        raise ValueError('Gate3R hash mismatch')
    check_committed(receipt['gate_path'])
    validate_gate(gate)
    return receipt


def validate_gate(gate):
    if gate.get('decision') not in ('GO','GO_WITH_DECLARED_SCOPE') or gate.get('phase4_allowed') is not True:
        raise ValueError('Gate3R does not authorize Phase4')
    for name in ('D22_implementation','D22_audit','P0_V10','L8'):
        if gate.get(name)!='PASS':
            raise ValueError('open execution condition: '+name)
    if gate.get('realism_disposition') not in ('CLEARED','SCOPE_LIMITATION_AUTHORIZED'):
        raise ValueError('realism disposition unresolved')
