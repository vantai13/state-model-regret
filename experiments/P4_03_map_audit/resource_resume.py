"""Resource-only L4.3 amendment. Original failed attempt remains immutable.

Uses the original native controller/worker with a new output root. Child command
routing changes only the orchestration entrypoint; engine/compare/criteria stay frozen.
"""
import argparse
from fractions import Fraction as F
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

from . import run as original
from .common import ROOT,HERE,OUT,CF,sha,git,require,write_once,verify_prereg,forbid_cf,cf_keys

EXT=HERE/'resource_amendment.json'
NEWOUT=OUT/'resource_v2'


def verify_extension():
    cfg=json.loads((ROOT/EXT).read_text())
    require(git('show','HEAD:'+str(EXT))==(ROOT/EXT).read_bytes(),'resource amendment not committed')
    require(cfg['status']=='RESOURCE_ONLY_NO_CRITERION_CHANGE','wrong extension status')
    verify_prereg()
    for path,h in cfg['source_sha256'].items():require(sha(ROOT/path)==h,'extension source changed:'+path)
    for path,h in cfg['preserved_failure_sha256'].items():require(sha(ROOT/path)==h,'historical failure changed:'+path)
    before=(ROOT/HERE/'replay_worker.py').read_text()
    after=(ROOT/HERE/'extended_replay_worker.py').read_text()
    require(before.replace('resource.setrlimit(resource.RLIMIT_CPU,(900,905))',
                           'resource.setrlimit(resource.RLIMIT_CPU,(1800,1805))')==after,
            'extended pilot worker changed more than resource limit')
    return cfg


def replay():
    cfg=verify_extension()
    original_summary=json.loads((ROOT/OUT/'partA/summary.json').read_text())
    specs=json.loads((ROOT/HERE/'bit_specs.json').read_text())['rows']
    index=next(i for i,s in enumerate(specs) if s['id']=='XPR0D')
    spec=specs[index]['spec'];age=F(spec[9])
    parameters=[spec[1],spec[2],str(F(spec[3])/age),spec[4],str(F(spec[5])/age),spec[8]]
    forbid_cf(parameters,cf_keys())
    failed=json.loads((ROOT/OUT/'partA/XPR0D.json').read_text())
    require(failed.get('exit_code')==-24,'only the confirmed SIGXCPU failure may be retried')
    folder=ROOT/NEWOUT/'partA';folder.mkdir(parents=True,exist_ok=True)
    target=folder/'XPR0D.json'
    if not target.exists():
        clean=json.loads((ROOT/HERE/'prereg.json').read_text())['clean_worktree']
        env=dict(os.environ,PYTHONPATH=str(Path(clean)/'src')+os.pathsep+clean,
                 OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
        cmd=[str(ROOT/'.venv/bin/python'),str(ROOT/HERE/'extended_replay_worker.py'),'--spec',str(ROOT/HERE/'bit_specs.json'),
             '--index',str(index),'--output',str(target),'--clean',clean]
        try:p=subprocess.run(cmd,cwd=clean,env=env,capture_output=True,text=True,timeout=2400)
        except subprocess.TimeoutExpired:
            write_once(target,dict(id='XPR0D',status='HOLD_RESOURCE_TIMEOUT_2400S'))
        else:
            with (folder/'XPR0D.log').open('x') as f:f.write(p.stdout+p.stderr)
            if not target.exists():write_once(target,dict(id='XPR0D',status='HOLD_EXECUTION_ERROR',exit_code=p.returncode,error=p.stderr))
    resolved=[];receipts={}
    for item in specs:
        path=target if item['id']=='XPR0D' else ROOT/OUT/'partA'/(item['id']+'.json')
        r=json.loads(path.read_text())
        if r['status']=='PASS':
            require(r['id']==item['id'] and r['expected']==item['expected'],'replay receipt identity/expected changed')
            require(all(struct.pack('!d',float(r['actual'][k]))==struct.pack('!d',float(v))
                        for k,v in item['expected'].items()),'stored replay fields fail exact check')
        resolved.append(r);receipts[str(path.relative_to(ROOT))]=sha(path)
    ok=all(r['status']=='PASS' for r in resolved)
    summary=dict(status='PASS' if ok else 'HOLD',rows=len(resolved),passed=sum(r['status']=='PASS' for r in resolved),
                 actual_comparisons=sum(len(r.get('matches',{})) for r in resolved),results=resolved,
                 original_attempt_status=original_summary['status'],original_SIGXCPU_preserved=True,
                 amendment=str(EXT),amendment_sha256=sha(ROOT/EXT),row_receipts_sha256=receipts,
                 original_K2=original_summary['original_K2'],K6=original_summary['K6'],recount=original_summary['recount'])
    write_once(folder/'summary.json',summary)
    print(json.dumps({k:summary[k] for k in ('status','rows','passed','actual_comparisons')},indent=2),flush=True)
    return not ok


def main():
    p=argparse.ArgumentParser();p.add_argument('step',choices=['replay','benchmark','full','worker','budget']);p.add_argument('--case')
    a=p.parse_args();verify_extension()
    if a.step=='replay':return replay()
    summary=json.loads((ROOT/NEWOUT/'partA/summary.json').read_text())
    require(summary['status']=='PASS','resource retry has not resolved Part A')
    for path,h in summary['row_receipts_sha256'].items():require(sha(ROOT/path)==h,'resolved Part A receipt changed')
    if a.step=='budget':
        from . import budget
        budget.OUT=NEWOUT;return budget.main()
    original.OUT=NEWOUT
    if a.step=='worker':return original.worker(a.case)
    # Preserve the frozen controller logic while routing child workers to this
    # explicitly versioned output-root wrapper. No engine argument is changed.
    saved=subprocess.run
    def route(command,*args,**kwargs):
        if isinstance(command,list) and len(command)>3 and command[1:4]==['-m','experiments.P4_03_map_audit.run','worker']:
            command=list(command);command[2]='experiments.P4_03_map_audit.resource_resume'
        return saved(command,*args,**kwargs)
    subprocess.run=route
    try:return original.run_native(a.step)
    finally:subprocess.run=saved


if __name__=='__main__':raise SystemExit(main())
