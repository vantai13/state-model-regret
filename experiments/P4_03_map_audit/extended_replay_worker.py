"""Invoked with cwd/PYTHONPATH set to the clean tag worktree; no main engine import."""
import argparse
import json
from pathlib import Path
import resource
import struct
import sys
import time


def main():
    p=argparse.ArgumentParser();p.add_argument('--spec',required=True);p.add_argument('--index',type=int,required=True)
    p.add_argument('--output',required=True);p.add_argument('--clean',required=True)
    a=p.parse_args()
    item=json.loads(Path(a.spec).read_text())['rows'][a.index]
    resource.setrlimit(resource.RLIMIT_CPU,(1800,1805))
    resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,3*1024**3))
    from experiments.explore_v13 import population
    if not Path(population.__file__).resolve().is_relative_to(Path(a.clean).resolve()):
        raise RuntimeError('pilot module not loaded from clean tag worktree')
    start=time.process_time()
    row,_=population.evaluate(item['spec'])
    matches={k:struct.pack('!d',float(row[k]))==struct.pack('!d',float(v)) for k,v in item['expected'].items()}
    result=dict(id=item['id'],batch=item['batch'],reason=item['reason'],matches=matches,
                actual={k:repr(float(row[k])) for k in item['expected']},expected=item['expected'],
                status='PASS' if all(matches.values()) else 'HOLD_BIT_MISMATCH',
                cpu_seconds=time.process_time()-start,python=sys.version,pilot_module=str(population.__file__))
    with Path(a.output).open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(id=item['id'],status=result['status'],cpu_seconds=result['cpu_seconds'])),flush=True)
    return not all(matches.values())


if __name__=='__main__':raise SystemExit(main())
