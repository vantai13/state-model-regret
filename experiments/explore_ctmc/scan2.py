"""Doan Van Tai — run ctmc-v2 Stage 0 zero-fit cases, one write-once JSON per case
[EXPLORATION ONLY; AI (Claude) theo ủy quyền].

  python -m experiments.explore_ctmc.scan2 STAGE [--workers N] [--cap CPU_S] [--shard I N]

Stage 0 has only the zero-fit mode: stationary laws, T_int, T_relax, the §3d approximation, M0 decisions on old,
backlog-only and full state at each h and at h = inf, KO at h = inf, first-order z, and a CPU estimate for the future
truth run. No V at finite h, no true gaps. One forked process per case under RLIMIT_CPU; a case that dies or hits the
cap is written by the parent as UNRESOLVED, never retried silently.
"""
import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import argparse
from fractions import Fraction as F
import json
import multiprocessing
from pathlib import Path
import resource
import signal
import socket
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'
CASES = OUT / 'cases_l73'
DEST = OUT / 'm0_l73'


class CpuCap(Exception):
    pass


def _cap(signum, frame):
    raise CpuCap('per-case CPU cap reached')


def est_truth_cpu(NA, NB, Tf, Ts, hmax, peak=6.0, load=9.0, mu=10.0):
    """Rough CPU-s of one future truth case: the ctmc-v1 estimate (design.est_cpu, calibrated on probe T3) with 4
    states per level and the generator norm 2 (lam_max + mu + 1/T_f + 1/T_s)."""
    norm = 2 * (load + peak + mu + 1 / float(Tf) + 1 / float(Ts))
    return 1.5e-6 * (NA + NB) * 4 * float(hmax) * norm / 52


def run_case(job):
    case, path, cap = job
    if path.exists():
        return
    signal.signal(signal.SIGXCPU, _cap)
    resource.setrlimit(resource.RLIMIT_CPU, (cap, cap + 60))
    from experiments.explore_ctmc import ctmc2
    t = time.process_time()
    p = [F(x) for x in case['parameters']]
    lamA, lamB, u, Tf, Ts, af, as_, c = p
    try:
        if case.get('d22', True) and max(case['N'].values()) <= ctmc2.D22_NMAX:
            out = ctmc2.evaluate_d22_m0(lamA, lamB, u, Tf, Ts, af, as_, case['hs'], c=c)
        else:
            out = ctmc2.evaluate_m0(lamA, lamB, u, Tf, Ts, af, as_, case['hs'], c=c)
        out['est_truth_cpu'] = est_truth_cpu(out['N']['A'], out['N']['B'], Tf, Ts, max(F(h) for h in case['hs']))
        out['status'] = 'COMPLETED'
    except CpuCap as exc:
        out = dict(parameters=case['parameters'], status='UNRESOLVED', error=str(exc))
    except Exception as exc:
        out = dict(parameters=case['parameters'], status='ERROR', error=f'{type(exc).__name__}: {exc}')
    out.update(id=case['id'], hs=case['hs'], mode='zf2', cpu=time.process_time() - t, host=socket.gethostname(),
               tags=case.get('tags', {}), f_nominal=case.get('f'))
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(out, default=float) + '\n')
    tmp.rename(path)


def run_robust(jobs, workers):
    ctx = multiprocessing.get_context('fork')
    pending, active = list(jobs), {}
    while pending or active:
        while pending and len(active) < workers:
            job = pending.pop(0)
            if job[1].exists():
                yield job[1].name, 'SKIP', 0.0
                continue
            proc = ctx.Process(target=run_case, args=(job,))
            proc.start()
            active[proc] = job
        time.sleep(0.2)
        for proc in [q for q in active if not q.is_alive()]:
            case, path, cap = active.pop(proc)
            proc.join()
            if path.exists():
                d = json.loads(path.read_text())
                yield path.name, d['status'], d.get('cpu') or 0.0
                continue
            sig = -proc.exitcode if proc.exitcode is not None and proc.exitcode < 0 else None
            status = 'UNRESOLVED' if sig in (signal.SIGKILL, signal.SIGXCPU) else 'ERROR'
            out = dict(id=case['id'], parameters=case['parameters'], hs=case['hs'], mode='zf2', status=status,
                       cpu=None, host=socket.gethostname(), tags=case.get('tags', {}),
                       error=f'worker died with signal {sig} (exitcode {proc.exitcode}) without writing its row')
            tmp = path.with_suffix('.tmp')
            tmp.write_text(json.dumps(out) + '\n')
            tmp.rename(path)
            yield path.name, status, 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('stage')
    ap.add_argument('--workers', type=int, default=os.cpu_count())
    ap.add_argument('--cap', type=int, default=900)
    ap.add_argument('--shard', nargs=2, type=int, default=[0, 1])
    a = ap.parse_args()
    from experiments.explore_ctmc import ctmc2
    cases = json.loads((CASES / f'{a.stage}.json').read_text())
    leaked = [c['id'] for c in cases if tuple(F(x) for x in c['parameters'][:7]) in ctmc2.CONTROL_REGIMES.values()]
    if leaked:
        raise SystemExit(f'control regimes in the case list: {leaked}')
    i, n = a.shard
    mine = [c for j, c in enumerate(cases) if j % n == i]
    folder = DEST / a.stage
    folder.mkdir(parents=True, exist_ok=True)
    jobs = [(c, folder / f"{c['id']}.json", a.cap) for c in mine]
    todo = sorted([j for j in jobs if not j[1].exists()], key=lambda j: -max(j[0]['N'].values()))   # heaviest first
    print(f'{a.stage} [zf2] shard {i}/{n} on {socket.gethostname()}: {len(mine)} cases, {len(todo)} to run, '
          f'{a.workers} workers, cap {a.cap} CPU-s', flush=True)
    start, cpu = time.monotonic(), 0.0
    for k, (name, status, c) in enumerate(run_robust(todo, a.workers), 1):
        cpu += c
        print(f'[{k}/{len(todo)} {time.monotonic() - start:.0f}s cpu {cpu:.0f}s] {status} {name}', flush=True)


if __name__ == '__main__':
    main()
