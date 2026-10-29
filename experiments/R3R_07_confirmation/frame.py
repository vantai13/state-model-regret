"""Generate the production frame only after committed numerics, n and root allocation.

Never called by preparation or unit tests with a confirmation root. A consumed
attempt directory remains on any failure; repairs use a new attempt_id, same root,
explicit deviation and complete preserved history, never overwrite the old list.
"""
import json
from pathlib import Path

from .common import ORDER, TEST_RANGE, check_committed, digest, environment, verified_card, write_once, verify_tool_hashes
from .gates import verify_numerics
from .inventory import reserved_keys, seen_regimes
from .power import select_allocation
from .sampler import sample_all, distances, inside
from experiments.R3R_05_contract.schema import canonical, validate


def validate_rows(rows, card, n, bnd, inventory, *, purpose):
    expected={name:bnd if name.endswith('BND') else n for name in ORDER}
    got=dict.fromkeys(ORDER,0)
    taken=reserved_keys(inventory); ids=set()
    for row in rows:
        reg,name=row['regime'],row['origin_region']
        if name not in got or row.get('purpose')!=purpose:
            raise ValueError('invalid origin/purpose')
        validate(reg,primary=True)
        if not inside(reg,card['regions'][name]):
            raise ValueError('outside origin region')
        key=canonical(reg)
        if key in taken or reg['id'] in ids:
            raise ValueError('exact collision or duplicate ID')
        taken.add(key); ids.add(reg['id']); got[name]+=1
    if got!=expected:
        raise ValueError('truncated/extra frame: counts differ from committed n')
    return got


def generate(prereg_path, attempt_dir):
    card=verified_card(); numerics=verify_numerics()
    prereg_path=Path(prereg_path); check_committed(prereg_path)
    prereg=json.loads(prereg_path.read_text())
    verify_tool_hashes(prereg['tool_sha256'])
    if prereg.get('status')!='LOCKED_BEFORE_SAMPLING' or tuple(prereg['regions_order'])!=ORDER:
        raise ValueError('locked prereg and fixed region order required')
    if Path(attempt_dir).resolve()!=Path(prereg['generation_dir']).resolve():
        raise ValueError('only the committed one-shot generation directory is allowed')
    inv_path=prereg['inventory']['path']; check_committed(inv_path)
    if digest(inv_path)!=prereg['inventory']['sha256']:
        raise ValueError('inventory mismatch')
    if digest('notes/phases/PHASE_3R_hypothesis_cards.lock.json')!=prereg['cards']['receipt_sha256']:
        raise ValueError('card receipt mismatch')
    for name,path in (('sampler','experiments/R3R_07_confirmation/sampler.py'),
                      ('scorer','experiments/R3R_06_cards/verdict.py'),
                      ('numerics_receipt','notes/phases/contract_v1_3_1.lock.json')):
        check_committed(path)
        if prereg[name+'_sha256']!=digest(path):
            raise ValueError(name+' hash mismatch')
    if prereg.get('n_rule_status')!='AUTHOR_ADOPTED':
        raise ValueError('sample-size rule not adopted by author')
    allocation=select_allocation(prereg['budget_cpu_hours'],numerics['p95_bundle_cpu_seconds'],
                                 numerics['fixed_validation_cpu_seconds'],numerics_closed=True)
    if allocation['status']=='HOLD_BUDGET' or allocation['n']!=prereg['n']['scored'] or allocation['bnd']!=prereg['n']['bnd']:
        raise ValueError('n does not follow committed budget rule')
    seed=prereg['seed']; root=seed['root']
    if isinstance(root,bool) or not isinstance(root,int) or root<0 or root in TEST_RANGE or 318300000<=root<=318409999:
        raise ValueError('confirmation root invalid or reserved for tests')
    registry_path=seed['allocation_path']; check_committed(registry_path)
    if digest(registry_path)!=seed['allocation_sha256']:
        raise ValueError('seed allocation receipt mismatch')
    allocation_record=json.loads(Path(registry_path).read_text())
    if allocation_record.get('stage')!='confirmation' or allocation_record.get('root')!=root or allocation_record.get('status')!='COMMITTED_BEFORE_DRAW':
        raise ValueError('confirmation root not allocated before draw')
    inventory=json.loads(Path(inv_path).read_text())
    # A consumed directory is durable evidence that even a failed attempt happened.
    out=Path(attempt_dir); out.mkdir(parents=True,exist_ok=False)
    write_once(out/'attempt.json',dict(status='STARTED',root=root,prereg_sha256=digest(prereg_path),
                                      environment=environment(),engine_runs=0))
    rows,redraws=sample_all(root,card,prereg['n']['scored'],prereg['n']['bnd'],reserved_keys(inventory),purpose='COMMITTED_CONFIRMATION')
    counts=validate_rows(rows,card,prereg['n']['scored'],prereg['n']['bnd'],inventory,purpose='COMMITTED_CONFIRMATION')
    seen=seen_regimes(inventory)
    for row in rows:
        row['distance_to_seen']=distances(row['regime'],seen,card['regions'][row['origin_region']])
    write_once(out/'regimes_cf.json',dict(prereg_sha256=digest(prereg_path),rows=rows))
    write_once(out/'generation_log.json',dict(status='GENERATED_ONCE_NO_ENGINE',counts=counts,redraws=redraws,
                                            frame_sha256=digest(out/'regimes_cf.json')))
    return counts


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--prereg',type=Path,required=True);p.add_argument('--attempt-dir',type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(generate(args.prereg,args.attempt_dir),indent=2))
