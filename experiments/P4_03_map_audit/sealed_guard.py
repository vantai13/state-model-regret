"""Additional mandatory R09/R10 guard, before any native call.

The originally registered scope is preserved. One coordinate is SEALED_BLOCKED;
it cannot silently enter discovery or be relabelled as a failed numerical result.
"""
import json
import subprocess
import sys

from .common import ROOT,HERE,sha,git,require
from . import resource_resume as R

LEDGER=HERE/'sealed_scope.json'


def guard_case(case,keys):
    require(tuple(case['key']) not in keys,'SEALED_R09_R10: refuse before engine import')


def eligible_plan(plan,keys):
    return dict(plan,cases=[c for c in plan['cases'] if tuple(c['key']) not in keys])


def worker_command(command):
    if (isinstance(command,list) and len(command)>3 and
            command[1:4]==['-m','experiments.P4_03_map_audit.resource_resume','worker']):
        command=list(command);command[2]='experiments.P4_03_map_audit.sealed_guard'
    return command


def main():
    ledger=json.loads((ROOT/LEDGER).read_text())
    require(git('show','HEAD:'+str(LEDGER))==(ROOT/LEDGER).read_bytes(),'sealed scope guard must be committed')
    for path,h in ledger['source_sha256'].items():require(sha(ROOT/path)==h,'sealed guard source changed:'+path)
    R.verify_extension()
    keys={tuple(x['coordinates']) for x in ledger['sealed']}
    plan=R.original.read_plan()
    step=sys.argv[1]
    if step=='worker':
        cid=sys.argv[sys.argv.index('--case')+1]
        guard_case(next(c for c in plan['cases'] if c['id']==cid),keys)
    if step=='benchmark':
        cfg=json.loads((ROOT/HERE/'prereg.json').read_text())
        for c in plan['cases']:
            if c['id'] in cfg['benchmark_ids']:guard_case(c,keys)
    old_read=R.original.read_plan
    if step=='full':R.original.read_plan=lambda:eligible_plan(plan,keys)
    saved=subprocess.run
    def route(command,*args,**kwargs):return saved(worker_command(command),*args,**kwargs)
    subprocess.run=route
    try:return R.main()
    finally:
        subprocess.run=saved
        R.original.read_plan=old_read


if __name__=='__main__':raise SystemExit(main())
