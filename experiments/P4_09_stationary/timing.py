"""Doan Van Tai — bounded non-held-out timing; uses unchanged native evaluator."""
import argparse
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import sys
import time

from experiments.P4_03_map_audit.common import ROOT,canonical
from .discovery import PROTOCOL,forbidden,references,exposure_audit,write_json

OUT=ROOT/'results/lessons/l4_9_v2/timing'


def case_for(index):
    protocol=json.loads(PROTOCOL.read_text());case=protocol['timing'][index]
    if 'source' in case:
        source=ROOT/case['source'];raw=json.loads(source.read_text())
        parameters=raw['parameters'];cache=source.parents[2]/'native_cache';level=(raw['K'],raw['ref'])
    else:
        parameters=case['parameters'];cache=ROOT/'results/lessons/l4_9_v2/native_cache';level=tuple(case['main'])
        # Only root checkpoints reused; h32 true cost profiles are never copied.
        base=ROOT/'results/lessons/l4_4/a3/native/P44_005/level_640_4.json';old=json.loads(base.read_text())
        folder=base.parents[2]/'native_cache/stationary';target=cache/'stationary';target.mkdir(parents=True,exist_ok=True)
        for side in ('A','B'):
            key=old['source_components'][side]['law_key']
            for ext in ('.json','.sha256'):
                src=folder/(key+ext);dst=target/(key+ext)
                if dst.exists() and dst.read_bytes()!=src.read_bytes():raise ValueError('stationary reuse changed bytes')
                if not dst.exists():shutil.copyfile(src,dst)
    key=canonical(parameters)
    if key in forbidden() or F(parameters[4])/F(parameters[2])>160:
        raise ValueError('benchmark is sealed/CF/extrapolation')
    if any(key==canonical(c['parameters']) for c in protocol['future_panel']):raise ValueError('benchmark held-out collision')
    return protocol,case,parameters,cache,level


def worker(index):
    protocol,case,parameters,cache,level=case_for(index)
    from experiments.P4_A1.config import verify_run
    verify_run('L43_A1_SV')
    resource.setrlimit(resource.RLIMIT_CPU,(protocol['limits']['timing_CPU_seconds_per_case'],protocol['limits']['timing_CPU_seconds_per_case']+1))
    from experiments.R3R_14_lean_close import engine
    engine.configure()
    print(json.dumps(dict(id=case['id'],parameters=parameters,level=level,cache_mode=case['cache_mode'])),flush=True)
    result=engine.evaluate_level(case['id'],parameters,*level,cache)
    engine.write_once(OUT/case['id']/'row.json',result)
    print(json.dumps(dict(status='COMPLETED',native_CPU=result['call_cpu_seconds'])),flush=True)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--worker',type=int);args=p.parse_args(argv)
    if args.worker is not None:return worker(args.worker)
    if OUT.exists():raise FileExistsError('timing output exists; no automatic retry')
    protocol=json.loads(PROTOCOL.read_text());training,_,_=references();audit=exposure_audit(protocol,training)
    OUT.mkdir(parents=True);write_json(OUT/'exposure_before_calls.json',audit)
    results=[]
    for i,case in enumerate(protocol['timing']):
        folder=OUT/case['id'];folder.mkdir()
        before=resource.getrusage(resource.RUSAGE_CHILDREN);begin=time.monotonic()
        with (folder/'worker.log').open('w') as log:
            child=subprocess.Popen([sys.executable,'-m','experiments.P4_09_stationary.timing','--worker',str(i)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            try:code=child.wait(timeout=protocol['limits']['timing_wall_seconds_per_case'])
            except subprocess.TimeoutExpired:
                os.killpg(child.pid,signal.SIGKILL);code=child.wait()
        after=resource.getrusage(resource.RUSAGE_CHILDREN)
        complete=(folder/'row.json').exists() and code==0
        r=dict(id=case['id'],status='COMPLETED' if complete else 'RESOURCE_OR_EXECUTION_STOP',
               returncode=code,CPU_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
               wall_seconds=time.monotonic()-begin,cache_mode=case['cache_mode'],heldout=False)
        if complete:
            row=json.loads((folder/'row.json').read_text());r['native_call_CPU_seconds']=row['call_cpu_seconds']
        results.append(r);write_json(OUT/'summary.json',dict(cases=results,new_heldout_outcomes=0,
                                                        h32_full_cost_measured=complete if i==3 else None))
        print(json.dumps(r),flush=True)


if __name__=='__main__':main()
