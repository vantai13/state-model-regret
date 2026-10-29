"""Doan Van Tai — immutable annotated contract tag and fail-closed receipt checks."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess

SPEC='experiments/R3R_05_contract/contract_spec.json'
LOCK='notes/phases/contract_v1_3.lock.json'
TAG='contract-v1.3'


def git(repo,*args,raw=False):
    data=subprocess.check_output(['git','-C',str(repo),*args])
    return data if raw else data.decode().strip()


def sha(data):return hashlib.sha256(data).hexdigest()


def check_snapshot(repo,commit,paths):
    hashes={}
    for rel in paths:
        actual=(Path(repo)/rel).read_bytes();original=git(repo,'show',f'{commit}:{rel}',raw=True)
        if actual!=original:raise ValueError(f'Frozen input changed: {rel}; version/DL required')
        hashes[rel]=sha(actual)
    return hashes


def create_lock(repo=Path('.')):
    repo=Path(repo)
    if (repo/LOCK).exists():raise ValueError('Receipt exists; verify it, never overwrite freeze history')
    if git(repo,'cat-file','-t',TAG)!='tag':raise ValueError('annotated contract tag required')
    commit=git(repo,'rev-parse',TAG+'^{commit}')
    subprocess.run(['git','-C',str(repo),'merge-base','--is-ancestor',commit,'HEAD'],check=True)
    spec=json.loads(git(repo,'show',f'{commit}:{SPEC}'))
    paths=spec['freeze_paths'];hashes=check_snapshot(repo,commit,paths)
    candidate=json.loads((repo/'results/lessons/l3r_5/candidate_verification.json').read_text())
    if candidate['status']!='PASS' or candidate['frozen_file_hashes']!=hashes:
        raise ValueError('successful candidate checks must match tagged source bytes')
    receipt=dict(owner='Doan Van Tai',created_utc=datetime.now(timezone.utc).isoformat(),
                 tag=TAG,tag_object=git(repo,'rev-parse',TAG),commit=commit,
                 source_sha256=hashes,status='LOCKED_WITH_DEFERRED',
                 phase4_execution='HOLD',numerical_levels='DEFERRED',realism='HOLD_UNSOURCED')
    (repo/LOCK).write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt


def verify_lock(repo=Path('.')):
    repo=Path(repo);receipt=json.loads((repo/LOCK).read_text())
    if receipt['tag']!=TAG or git(repo,'cat-file','-t',TAG)!='tag':raise ValueError('annotated tag identity mismatch')
    if git(repo,'rev-parse',TAG)!=receipt['tag_object']:raise ValueError('contract tag moved')
    commit=git(repo,'rev-parse',TAG+'^{commit}')
    if commit!=receipt['commit']:raise ValueError('contract commit mismatch')
    subprocess.run(['git','-C',str(repo),'merge-base','--is-ancestor',commit,'HEAD'],check=True)
    frozen_spec=json.loads(git(repo,'show',f'{commit}:{SPEC}'))
    hashes=check_snapshot(repo,commit,frozen_spec['freeze_paths'])
    if hashes!=receipt['source_sha256']:raise ValueError('receipt does not cover exact frozen path/hash set')
    return receipt


def readiness(spec,*,tag_verified=False):
    card=[] if tag_verified else ['annotated contract tag/receipt not verified']
    numeric=spec['numerics'];sampling=list(card)
    for field in ['K_star','ref_star','dt_star','S1_route','quadrature_tail_policy']:
        if numeric[field] is None:sampling.append('numerics DEFERRED: '+field)
    if spec['audit_L3R3']!='PASS':sampling.append('numerical audit/coverage closure HOLD')
    sampling.append('L3R.7 frame/strata/sample-size/seed/collision prereg not created in L3R.5')
    phase4=list(sampling)
    if spec['D22']['audit']!='PASS':phase4.append('committed D22 implementation/audit DEFERRED')
    if spec['P0_V10']!='PASS':phase4.append('P0-V10 real reader OPEN')
    if spec['L8']!='PASS':phase4.append('L8 real reader OPEN')
    phase4+=['Gate3R/prereg not frozen','realism disposition remains HOLD_UNSOURCED']
    return dict(hypothesis_freeze=dict(allowed=not card,reasons=card),
                CF_sampling=dict(allowed=False,reasons=sampling),
                Phase4=dict(allowed=False,reasons=phase4),
                scope='Current v1.3 snapshot only; closure requires versioned v1.3.1 evidence, not editing status flags')


def main():
    p=argparse.ArgumentParser();p.add_argument('--create-lock',action='store_true');args=p.parse_args()
    receipt=create_lock() if args.create_lock else verify_lock()
    spec=json.loads(Path(SPEC).read_text())
    print(json.dumps(dict(status='PASS',tag=receipt['tag'],tag_commit=receipt['commit'],
                          frozen_inputs=len(receipt['source_sha256']),readiness=readiness(spec,tag_verified=True)),indent=2))


if __name__=='__main__':main()
