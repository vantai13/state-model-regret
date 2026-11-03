"""Doan Van Tai — run ctmc-v1 cases, one write-once JSON per case [EXPLORATION ONLY; AI (Claude) theo ủy quyền].

  python -m experiments.explore_ctmc.scan STAGE [--mode full|m0] [--workers N] [--shard I N] [--cap CPU_S]

--mode m0 computes only mean-rollout and stationary quantities (allowed before the predictions are locked).
--mode full computes the truth and refuses to start unless results/explore_ctmc/locks.json lists the sha256 of
every prediction file the stage needs and the files on disk still match (bridge for every full stage; asymptote
as well when any case has h/kappa > 160 or h/T_int >= 10). Cases equal to a sealed/CF/panel key of the fluid
namespace, to a V3 control regime or to an exposed timing probe are refused. A case that exceeds the per-case CPU
cap is written as UNRESOLVED and reported, never retried silently.
"""
import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import argparse
from fractions import Fraction as F
import hashlib
import json
import multiprocessing
from pathlib import Path
import resource
import signal
import socket
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'
LOCKS = OUT / 'locks.json'


class CpuCap(Exception):
    pass


def _cap(signum, frame):
    raise CpuCap('per-case CPU cap reached')


def fluid_forbidden():
    from experiments.explore_mech.scan import forbidden_keys
    return forbidden_keys()


def controls_and_probes():
    ids = json.loads((OUT / 'controls/v3_ids.json').read_text())
    keys = {tuple(str(F(x)) for x in v[:4]) + (str(F(v[4])),) for v in ids['V3'].values()}
    for lamA, lamB, u, kappa, hs in ids['exposed_timing_probes'].values():
        keys |= {(str(F(lamA)), str(F(lamB)), str(F(u)), str(F(kappa)), str(F(h))) for h in hs}
    return keys


def case_keys(case):
    lamA, lamB, u, kappa, c = (str(F(x)) for x in case['parameters'])
    return [(lamA, lamB, u, kappa, str(F(h)), c) for h in case['hs']]


def check_locks(stage_cases):
    need = {'PREDICTIONS_bridge.md', 'check_bridge.py'}
    if any(c.get('long') for c in stage_cases):
        need |= {'PREDICTIONS_asymptote.md', 'check_asymptote.py', 'PREDICTIONS_asymptote_numbers.csv'}
    if any(c.get('csw') for c in stage_cases):
        need |= {'PREDICTIONS_csw.md', 'check_csw.py', 'PREDICTIONS_csw_numbers.csv'}
    if not LOCKS.exists():
        raise SystemExit('full mode refused: no locks.json (predictions not locked)')
    locks = json.loads(LOCKS.read_text())['files']
    for name in need:
        path = (ROOT / 'experiments/explore_ctmc' / name) if name.endswith('.py') else (OUT / name)
        if name not in locks or hashlib.sha256(path.read_bytes()).hexdigest() != locks[name]:
            raise SystemExit(f'full mode refused: {name} missing from locks or changed since it was locked')
    return locks


def run_case(job):
    case, mode, path, cap = job
    if path.exists():
        return path.name, 'SKIP', 0.0
    signal.signal(signal.SIGXCPU, _cap)
    resource.setrlimit(resource.RLIMIT_CPU, (cap, cap + 60))
    from experiments.explore_ctmc import ctmc
    t = time.process_time()
    lamA, lamB, u, kappa, c = (F(x) for x in case['parameters'])
    try:
        if mode == 'm0':
            out = ctmc.evaluate_m0(lamA, lamB, u, kappa, case['hs'], c=c, allow_csw=case.get('csw', False))
        else:
            out = ctmc.evaluate(lamA, lamB, u, kappa, case['hs'], c, disagree=case.get('disagree', True),
                                allow_csw=case.get('csw', False))
            for r in out['h']:      # V6 and V11 on every row
                flags = [k for k in ('S', 'M', 'G_M') if r[k] < -1e-9]
                r['flags'] = flags
            out['V11_static_sign_ok'] = (out['s'] < 0) == (lamB < lamA) if lamA != lamB else None
        out['status'] = 'COMPLETED'
    except CpuCap as exc:
        out = dict(parameters=case['parameters'], status='UNRESOLVED', error=str(exc))
    except Exception as exc:
        out = dict(parameters=case['parameters'], status='ERROR', error=f'{type(exc).__name__}: {exc}')
    out.update(id=case['id'], hs=[str(F(h)) for h in case['hs']], mode=mode, cpu=time.process_time() - t,
               host=socket.gethostname(), tags=case.get('tags', {}))
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(out, default=float) + '\n')
    tmp.rename(path)
    return path.name, out['status'], out['cpu']


def main():
    p = argparse.ArgumentParser()
    p.add_argument('stage')
    p.add_argument('--mode', choices=('full', 'm0'), default='full')
    p.add_argument('--workers', type=int, default=os.cpu_count())
    p.add_argument('--shard', nargs=2, type=int, default=[0, 1])
    p.add_argument('--cap', type=int, default=3600)
    p.add_argument('--reverse', action='store_true')
    a = p.parse_args()
    cases = json.loads((OUT / 'cases' / f'{a.stage}.json').read_text())
    bad, ctrl = fluid_forbidden(), controls_and_probes()
    refused = [c['id'] for c in cases if any(k in bad or k[:5] in ctrl for k in case_keys(c))]
    if refused:
        raise SystemExit(f'{len(refused)} cases refused (sealed/CF/panel/control/probe): {refused[:5]}')
    if a.mode == 'full':
        check_locks(cases)
    i, n = a.shard
    mine = [c for j, c in enumerate(cases) if j % n == i]
    folder = OUT / ('m0' if a.mode == 'm0' else 'runs') / a.stage
    folder.mkdir(parents=True, exist_ok=True)
    jobs = [(c, a.mode, folder / f"{c['id']}.json", a.cap) for c in mine]
    todo = [j for j in jobs if not j[2].exists()]
    if a.reverse:
        todo.reverse()
    print(f'{a.stage} [{a.mode}] shard {i}/{n} on {socket.gethostname()}: {len(mine)} cases, {len(todo)} to run, '
          f'{a.workers} workers', flush=True)
    start, cpu = time.monotonic(), 0.0
    with multiprocessing.get_context('fork').Pool(a.workers, maxtasksperchild=1) as pool:
        for k, (name, status, c) in enumerate(pool.imap_unordered(run_case, todo), 1):
            cpu += c
            print(f'[{k}/{len(todo)} {time.monotonic() - start:.0f}s cpu {cpu:.0f}s] {status} {name}', flush=True)


if __name__ == '__main__':
    main()
