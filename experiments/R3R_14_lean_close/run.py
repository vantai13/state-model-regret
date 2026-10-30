"""Doan Van Tai — lean L3R.7 closure runner (DL-095). AI (Claude) theo ủy quyền.

Every computation is a registered calibration spec from prereg.json; outputs are write-once JSON under
results/lessons/l3r_7/lean_close/<step>/ and an existing file is a checkpoint (skipped on rerun).
Never samples, never touches CF, R09 or R10.

  python -m experiments.R3R_14_lean_close.run verify
  python -m experiments.R3R_14_lean_close.run replay
  python -m experiments.R3R_14_lean_close.run represent
  python -m experiments.R3R_14_lean_close.run calibrate --level 160 4 [--level 80 4 ...]
  python -m experiments.R3R_14_lean_close.run timing --level 160 4
"""
import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import argparse
from fractions import Fraction as F
import hashlib
import json
import multiprocessing
from pathlib import Path
import resource
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
PREREG = Path(__file__).with_name('prereg.json')
OUT = ROOT / 'results/lessons/l3r_7/lean_close'
CACHE = Path.home() / '.cache/smr_lean_close'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_prereg():
    cfg = json.loads(PREREG.read_text())
    bad = [p for p, h in cfg['source_sha256'].items() if not (ROOT / p).exists() or sha(ROOT / p) != h]
    if bad:
        raise SystemExit(f'source hash mismatch, refusing to run: {bad[:5]}')
    return cfg


def r_tag(r):
    return str(F(r)).replace('/', '_')


def _job(args):
    """Child process: limits, evaluate, write once. Returns (path, status)."""
    case_id, parameters, K, ref, path, cache, limits = args
    if Path(path).exists():
        return path, 'SKIPPED_EXISTS'
    resource.setrlimit(resource.RLIMIT_CPU, (limits['job_cpu_seconds'], limits['job_cpu_seconds'] + 5))
    resource.setrlimit(resource.RLIMIT_AS, (limits['address_space_bytes'], limits['address_space_bytes']))
    from experiments.R3R_14_lean_close import engine
    engine.configure()
    try:
        row = engine.evaluate_level(case_id, parameters, K, ref, cache)
        status = 'COMPLETED'
    except Exception as exc:          # recorded, never silently dropped
        row, status = dict(id=case_id, K=K, ref=ref, error=f'{type(exc).__name__}: {exc}'), 'UNRESOLVED'
    row['status'] = status
    row['parameters'] = parameters
    engine.write_once(path, row)
    return path, status


def run_jobs(jobs, cfg, workers):
    limits = cfg['limits']
    todo = [(*j, limits) for j in jobs if not Path(j[4]).exists()]
    print(f'{len(jobs)} jobs, {len(todo)} to run, {workers} workers', flush=True)
    start = time.monotonic()
    with multiprocessing.get_context('fork').Pool(workers, maxtasksperchild=1) as pool:
        for i, (path, status) in enumerate(pool.imap_unordered(_job, todo), 1):
            print(f'[{i}/{len(todo)} {time.monotonic() - start:.0f}s] {status} {Path(path).relative_to(OUT)}', flush=True)


def case_table(cfg):
    """Registered calibration v2 cases: id -> parameters (needs the chosen r for rounded/interior cases)."""
    cases = {c['id']: c['parameters'] for c in cfg['calibration']['coarse_cases']}
    sel = OUT / 'representation_selection.json'
    if sel.exists():
        from experiments.R3R_14_lean_close.engine import round_rates
        r = json.loads(sel.read_text())['selected_r']
        if r is not None:
            for c in cfg['representation']['cases']:
                cases[c['id'] + '_R'] = round_rates(c['parameters'], r)
            for d in cfg['calibration']['r_interior_designs']:
                lo = [F(x) for x in d['lower_corner']]
                rr = F(r)
                params = [str(lo[0] + rr), str(lo[1] + (rr if d['shift_lambdaB'] else 0)), d['kappa'],
                          str((lo[2] + rr) / 2), d['h'], '0']
                cases[d['id']] = params
    return cases


def main():
    p = argparse.ArgumentParser()
    p.add_argument('step', choices=['verify', 'replay', 'represent', 'calibrate', 'timing'])
    p.add_argument('--level', nargs=2, type=int, action='append')
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--only', nargs='*')
    a = p.parse_args()
    cfg = load_prereg()
    workers = min(a.workers, cfg['limits']['max_workers'])
    if a.step == 'verify':
        print(f'prereg OK: {len(cfg["source_sha256"])} source files match')
        return
    if a.step == 'replay':
        jobs = [(c['id'], c['parameters'], c['level'][0], c['level'][1],
                 OUT / 'replay' / c['id'] / f'level_{c["level"][0]}_{c["level"][1]}.json', CACHE, )
                for c in cfg['environment_replay']['cases']]
        run_jobs(jobs, cfg, workers)
    elif a.step == 'represent':
        from experiments.R3R_14_lean_close.engine import round_rates
        K, ref = cfg['representation']['level']
        jobs = [(c['id'] + '_R', round_rates(c['parameters'], r), K, ref,
                 OUT / 'represent' / r_tag(r) / c['id'] / f'level_{K}_{ref}.json', CACHE)
                for r in cfg['representation']['candidates_r'] for c in cfg['representation']['cases']]
        run_jobs(jobs, cfg, workers)
    elif a.step == 'calibrate':
        cases = case_table(cfg)
        if a.only:
            cases = {k: v for k, v in cases.items() if k in set(a.only)}
        jobs = [(cid, params, K, ref, OUT / 'calibration' / cid / f'level_{K}_{ref}.json', CACHE)
                for K, ref in a.level for cid, params in sorted(cases.items())]
        run_jobs(jobs, cfg, workers)
    elif a.step == 'timing':
        (K, ref), = a.level
        cases = case_table(cfg)
        ids = cfg['timing']['cases_corner'] + [c['id'] + '_R' for c in cfg['representation']['cases']] \
            + [d['id'] for d in cfg['calibration']['r_interior_designs']]
        todo = [(cid, cases[cid], K, ref, OUT / 'timing' / cid / 'bundle.json', cfg['limits'])
                for cid in ids if not (OUT / 'timing' / cid / 'bundle.json').exists()]
        print(f'{len(ids)} bundles, {len(todo)} to time', flush=True)
        with multiprocessing.get_context('fork').Pool(min(workers, cfg['timing']['workers']), maxtasksperchild=1) as pool:
            for path, status in pool.imap_unordered(_bundle, todo):
                print(status, Path(path).relative_to(OUT), flush=True)


def _bundle(args):
    """Child process: main + coarse-K + coarse-dt in one fresh (cold) cache; CPU of the whole bundle."""
    case_id, parameters, K, ref, path, limits = args
    cpu_limit = 3 * limits['job_cpu_seconds']
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit + 5))
    resource.setrlimit(resource.RLIMIT_AS, (limits['address_space_bytes'], limits['address_space_bytes']))
    from experiments.R3R_14_lean_close import engine
    engine.configure()
    statuses, cpu, begin = {}, 0.0, time.monotonic()
    with tempfile.TemporaryDirectory(prefix='lean_timing_') as cold:
        for lv in ((K, ref), (K // 2, ref), (K, ref // 2)):
            try:
                row = engine.evaluate_level(case_id, parameters, lv[0], lv[1], Path(cold))
                cpu += row['call_cpu_seconds']
                statuses[f'{lv[0]}:{lv[1]}'] = 'COMPLETED'
            except Exception as exc:
                statuses[f'{lv[0]}:{lv[1]}'] = f'UNRESOLVED {type(exc).__name__}: {exc}'
    status = 'COMPLETED' if all(s == 'COMPLETED' for s in statuses.values()) else 'UNRESOLVED'
    engine.write_once(path, dict(id=case_id, parameters=parameters, level=[K, ref], cold_cache=True,
                                 bundle_cpu_seconds=cpu, bundle_wall_seconds=time.monotonic() - begin,
                                 statuses=statuses, status=status))
    return path, status


if __name__ == '__main__':
    main()
