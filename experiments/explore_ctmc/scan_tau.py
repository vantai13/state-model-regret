"""Doan Van Tai — run the L7.5 telemetry-age units, one write-once JSON per (regime, tau)
[EXPLORATION ONLY; AI (Claude) theo ủy quyền].

  python -m experiments.explore_ctmc.scan_tau STAGE [--mode zf|l75] [--workers N] [--cap CPU_S]

STAGE is sobol, old or xs (results/explore_ctmc/cases_l75/STAGE.json).
  zf   zero fit only (tau.evaluate_m0; D22 parts when the unit's d22 flag is set): never calls V.
  l75  truth (tau.evaluate), refused unless locks_l75.json holds every locked file unchanged, the stage is locked,
       and the host is dt4n-research-01. No --shard, no --ids: every unit of the stage once, on one host.
One forked process per unit under RLIMIT_CPU (scan2.run_robust); a unit that dies or hits the cap is written by the
parent as UNRESOLVED and is never retried silently.
"""
import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import resource
import signal
import socket
import time

from experiments.explore_ctmc import scan2

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'
CASES = OUT / 'cases_l75'
TRUTH_HOST = 'dt4n-research-01'
STAGES = ('sobol', 'old', 'xs')
LOCKS_L75 = OUT / 'locks_l75.json'


def unit_name(case, tau):
    return f"{case['id']}__t{str(F(tau)).replace('/', '-')}.json"


def check_l75_locks(stage):
    if not LOCKS_L75.exists():
        raise SystemExit('l75 truth refused: no locks_l75.json (card not locked)')
    locks = json.loads(LOCKS_L75.read_text())
    for rel, sha in locks['files'].items():
        if hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() != sha:
            raise SystemExit(f'l75 truth refused: {rel} changed since the lock')
    if stage not in locks.get('truth_stages', []) or f'results/explore_ctmc/cases_l75/{stage}.json' not in locks['files']:
        raise SystemExit(f'l75 truth refused: {stage} is not a locked truth stage')
    if socket.gethostname() != TRUTH_HOST:
        raise SystemExit(f'l75 truth refused: single-host rule, truth runs only on {TRUTH_HOST}')
    return locks


def run_unit(job):
    """scan2.run_robust calls this as run_case(job) with job = (case, path, cap, mode); the unit's tau is in case."""
    case, path, cap, mode = job
    if path.exists():
        return
    signal.signal(signal.SIGXCPU, scan2._cap)
    resource.setrlimit(resource.RLIMIT_CPU, (cap, cap + 60))
    from experiments.explore_ctmc import tau as T5
    t0 = time.process_time()
    lamA, lamB, u, kappa = (F(x) for x in case['parameters'][:4])
    tau, unit = F(case['tau']), case['unit']
    try:
        if mode == 'l75':
            kw = dict(d22=True) if unit['d22'] else dict(disagree=False)
            out = T5.evaluate(lamA, lamB, u, kappa, case['hs'], tau, **kw)
            for r in out['h']:
                r['flags'] = [k for k in ('S', 'M', 'G_M') if r[k] < -1e-9] + \
                    ([k for k in ('F1', 'V1') if r['d22'][k] < -1e-9] if 'd22' in r else [])
        else:
            out = T5.evaluate_m0(lamA, lamB, u, kappa, case['hs'], tau, d22=unit['d22'])
        out['status'] = 'COMPLETED'
    except scan2.CpuCap as exc:
        out = dict(parameters=case['parameters'], status='UNRESOLVED', error=str(exc))
    except Exception as exc:
        out = dict(parameters=case['parameters'], status='ERROR', error=f'{type(exc).__name__}: {exc}')
    out.update(id=case['id'], hs=case['hs'], tau=str(tau), d22_unit=unit['d22'], est_truth=unit['est_truth'], mode=mode,
               cpu=time.process_time() - t0, host=socket.gethostname(), tags=case.get('tags', {}))
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(out, default=str) + '\n')
    tmp.rename(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('stage', choices=STAGES)
    ap.add_argument('--mode', choices=('zf', 'l75'), default='zf')
    ap.add_argument('--workers', type=int, default=os.cpu_count())
    ap.add_argument('--cap', type=int, default=900)
    a = ap.parse_args()
    from experiments.explore_ctmc import tau as T5
    cases = json.loads((CASES / f'{a.stage}.json').read_text())
    leaked = [c['id'] for c in cases if T5.is_control(c['parameters'])]
    if leaked:
        raise SystemExit(f'control regimes in the case list: {leaked}')
    if a.mode == 'l75':
        check_l75_locks(a.stage)
    folder = OUT / ('runs_l75' if a.mode == 'l75' else 'm0_l75') / a.stage
    folder.mkdir(parents=True, exist_ok=True)
    jobs = []
    for c in cases:
        for un in c['units']:
            jobs.append((dict(c, tau=un['tau'], unit=un), folder / unit_name(c, un['tau']), a.cap, a.mode))
    todo = sorted([j for j in jobs if not j[1].exists()], key=lambda j: -j[0]['unit']['est_truth'])     # heaviest first
    print(f'{a.stage} [{a.mode}] on {socket.gethostname()}: {len(jobs)} units, {len(todo)} to run, {a.workers} workers, '
          f'cap {a.cap} CPU-s', flush=True)
    scan2.run_case = run_unit                     # run_robust forks scan2.run_case(job)
    start, cpu = time.monotonic(), 0.0
    for k, (name, status, c) in enumerate(scan2.run_robust(todo, a.workers), 1):
        cpu += c
        print(f'[{k}/{len(todo)} {time.monotonic() - start:.0f}s cpu {cpu:.0f}s] {status} {name}', flush=True)


if __name__ == '__main__':
    main()
