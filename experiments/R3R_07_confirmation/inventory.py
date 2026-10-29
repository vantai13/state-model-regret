"""Read design coordinates only; preserve non-v1.3 namespaces explicitly."""
import json
from pathlib import Path
from fractions import Fraction as F

from experiments.R3R_05_contract.schema import IDENTITY, canonical, exact, from_pilot
from .common import git, sha, write_once, verified_card

PILOT = 'a7435e9a3cb0d1625479c942041ec6748444014a'


def build():
    verified_card()
    if git('rev-list', '-n1', 'explore-v13-pilot').decode().strip() != PILOT:
        raise ValueError('pilot tag moved')
    records, sources, other = [], {}, []
    def add(reg, source, rid, namespace='v1.3_fixed_plant', note='', reservation_type='observed_or_design_reserved'):
        records.append(dict(source=source, source_id=rid, namespace=namespace, note=note,
                            reservation_type=reservation_type,
                            coordinates={k: str(v) for k,v in zip(IDENTITY,canonical(reg))},
                            key='|'.join(map(str,canonical(reg)))))
    for stage in ('stage1','stage2','stage3','robustK','robustdt'):
        path = f'results/explore_v13/{stage}/specs.json'
        blob = git('show', f'{PILOT}:{path}')
        sources[f'{PILOT}:{path}'] = sha(blob)
        for spec in json.loads(blob):
            add(from_pilot(spec), stage, spec[0])
    path = 'notes/design/grid_v1_2.json'
    blob = Path(path).read_bytes()
    sources[path] = sha(blob)
    grid = json.loads(blob)
    for role in ('main','heldout','controls','probes'):
        for cell in grid[role]:
            u = exact(cell['u']) if 'u' in cell else 2*exact(cell['eta'])
            amp = F(6)
            if 'lambdaA' in cell:
                lam = exact(cell['lambdaA'])
            else:
                off, on = map(exact, cell['ratesA'])
                amp = (on-off)/2
                lam = (off+on)/2-u
            reg = dict(lambdaA=str(lam),lambdaB='8',u=str(u),kappa=cell['kappa'],h=cell['h'],c_sw='0')
            namespace = 'v1.3_fixed_plant' if amp == 6 and lam >= 6 else 'v1.2_incompatible_plant'
            add(reg, f'v1.2/{role}', cell['id'], namespace,
                'parameter projection only; snapshot outcomes are not population outcomes; u=2eta; '
                f'A amplitude={amp}; incompatible namespace is not a valid v1.3 regime')
    path = 'experiments/R3R_02_audit/regimes.json'
    blob = Path(path).read_bytes(); sources[path] = sha(blob)
    for reg in json.loads(blob)['audit_regimes']:
        add(reg, 'L3R.3/audit', reg['id'])
        # Conservatively reserve zero-action variants; this does not attest that
        # every variant was actually executed by T4.
        add(dict(reg,u='0'), 'L3R.3/conservative_zero_variants', reg['id']+':u0',
            reservation_type='conservative_unattested_execution')
    # Formula/finite-state verification has no joint (lambdaA,lambdaB,u,kappa,h,c_sw).
    # Do not invent such a key or treat a stationary-only queue as a full regime.
    for path, namespace, explanation in (
        ('experiments/R3R_04_realism/generic_prereg.json','single_queue_continuous_fluid',
         'three single queues, no routing action/u or decision horizon h; not joint v1.3 keys'),
        ('experiments/lessons/l3r_2_spec.json','finite_abstract_T07',
         'finite algebraic laws/toys, not fixed-plant joint regimes'),
        ('experiments/R3R_02_audit/pilot_tests_original.py','synthetic_side_tables',
         'synthetic arrays; no physical joint-regime identity'),
        ('experiments/R3R_04_realism/check_stationary.py','stationary_marginal_only',
         'X2041/X2012/X1009 already reserved above; marginal laws do not define new joint regimes')):
        blob = Path(path).read_bytes(); sources[path] = sha(blob)
        other.append(dict(path=path,namespace=namespace,handling=explanation))
    counts = {}
    for row in records:
        counts[row['source']] = counts.get(row['source'],0)+1
    keys = {r['key'] for r in records if r['namespace']=='v1.3_fixed_plant'}
    return dict(owner='Doan Van Tai',status='PARAMETER_ONLY_INVENTORY_V1',pilot_commit=PILOT,
                identity=list(IDENTITY),sources=sources,records=records,source_record_counts=counts,
                distinct_v13_keys=len(keys),other_namespaces=other,
                limitations=['local registered sources only; unseen external work is not certified',
                             'sealed R09/R10 coordinates reserved; no sealed outcome computed/read',
                             'all projected keys may conservatively be reserved, even incompatible controls'])


def reserved_keys(inventory):
    return {tuple(F(v) for v in row['key'].split('|')) for row in inventory['records']}


def seen_regimes(inventory):
    unique = {}
    for row in inventory['records']:
        if row['namespace']=='v1.3_fixed_plant' and row['reservation_type']!='conservative_unattested_execution':
            unique[row['key']] = row['coordinates']
    return list(unique.values())


if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(); result=build(); write_once(a.out,result)
    print(json.dumps(dict(status=result['status'],source_record_counts=result['source_record_counts'],
                          distinct_v13_keys=result['distinct_v13_keys']),indent=2))
