"""Doan Van Tai — exploration: where do state value, model value (beyond a margin baseline) and interaction
actually matter? [EXPLORATION ONLY, branch explore/p4-regions; AI (Claude) theo ủy quyền]

Native engine (frozen R3R_08 + native evaluator) with the L4.4 margin baseline, amplitude a = 6 only, tau = 1 s,
c_sw = 0, so kappa and h read as kappa/tau and h/tau. Refuses R09/R10 and CF-v2 keys. Every regime becomes
discovery data. One write-once JSON per case; reruns skip finished cases.

  python -m experiments.explore_p4.scan STAGE [--workers 8] [--level K REF]
"""
import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import argparse
from fractions import Fraction as F
import itertools
import json
import multiprocessing
from pathlib import Path
import resource
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_p4'
CACHE = Path.home() / '.cache/smr_explore_p4'
KEEP = ('Cref', 'Sbar', 'G_S', 'G_M', 'G_SM', 'Gamma', 'G_S_M1', 'G_M_S1', 'P_flip', 'losses', 'normalized_error',
        'validity_errors', 'arithmetic_pass', 'Stay')


def key(params):
    lamA, lamB, kappa, eta, h, c = params
    return tuple(str(F(x)) for x in (lamA, lamB, 2 * F(eta), kappa, h, c))


def forbidden_keys():
    sealed = json.loads((ROOT / 'experiments/P4_03_map_audit/sealed_scope.json').read_text())['sealed']
    keys = {tuple(str(F(x)) for x in s['coordinates']) for s in sealed}
    cf = json.loads((ROOT / 'results/lessons/l3r_7/lean_close/cf_generation/attempt01/regimes_cf.json').read_text())['rows']
    keys |= {tuple(str(F(r['regime'][k])) for k in ('lambdaA', 'lambdaB', 'u', 'kappa', 'h', 'c_sw')) for r in cf}
    return keys


def grid(prefix, lamA, lamB, u, kappa, h):
    cases = []
    for i, (a, b, uu, k, hh) in enumerate(itertools.product(lamA, lamB, u, kappa, h)):
        if F(a) < 6 or F(b) < 6 or F(a) + F(uu) >= 10 or F(b) + F(uu) >= 10:
            continue
        cases.append(dict(id=f'{prefix}{i:04d}', parameters=[a, b, k, str(F(uu) / 2), hh, '0']))
    return cases


STAGES = {
    'timing': lambda: [dict(id=f'T{i}', parameters=p) for i, p in enumerate([
        ['8', '9', '3/100', '1/4', '32', '0'], ['7', '8', '1/10', '3/4', '32', '0'],
        ['6', '7', '10', '1/4', '32', '0'], ['7', '8', '1', '3/4', '8', '0']])],
    'wide': lambda: grid('W', ['6', '7', '8'], ['6', '7', '8', '9'], ['1/2', '1', '3/2'],
                         ['3/100', '1/10', '3/10', '1', '3', '10'], ['2', '8', '32']),
    'short': lambda: grid('S', ['6', '13/2', '7'], ['6', '7', '8'], ['1', '3/2', '7/4'],
                          ['3/100', '1/10', '1/5', '3/10', '1/2', '1'], ['1/4', '1/2', '1', '2']),
    'top': lambda: [dict(id=i, parameters=p) for i, p in json.loads((OUT / 'top_cases.json').read_text())],
}


def run_case(args):
    case, level, path = args
    if path.exists():
        return path, 'SKIP'
    resource.setrlimit(resource.RLIMIT_CPU, (3600, 3605))
    from experiments.P4_04_baseline.evaluate import evaluate_level
    try:
        row = evaluate_level(case, level, CACHE)
        out = {k: row.get(k) for k in KEEP}
        out.update(id=case['id'], parameters=case['parameters'], level=list(level), status='COMPLETED',
                   cpu=row.get('call_cpu_seconds'), baseline_sanity_pass=row.get('baseline_sanity_pass'),
                   baseline=[{k: b[k] for k in ('rho', 'L00', 'L10')} for b in row.get('baseline', [])],
                   error=row.get('error'))
    except Exception as exc:
        out = dict(id=case['id'], parameters=case['parameters'], level=list(level), status='UNRESOLVED',
                   error=f'{type(exc).__name__}: {exc}')
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(out) + '\n')
    tmp.rename(path)
    return path, out['status']


def main():
    p = argparse.ArgumentParser()
    p.add_argument('stage', choices=sorted(STAGES))
    p.add_argument('--workers', type=int, default=8)
    p.add_argument('--level', nargs=2, type=int, default=[160, 2])
    a = p.parse_args()
    level = tuple(a.level)
    bad = forbidden_keys()
    cases = [c for c in STAGES[a.stage]() if key(c['parameters']) not in bad]
    out = OUT / a.stage / f'level_{level[0]}_{level[1]}'
    out.mkdir(parents=True, exist_ok=True)
    jobs = [(c, level, out / f"{c['id']}.json") for c in cases]
    todo = [j for j in jobs if not j[2].exists()]
    print(f'{a.stage}: {len(cases)} cases ({len(STAGES[a.stage]()) - len(cases)} forbidden), {len(todo)} to run', flush=True)
    start = time.monotonic()
    with multiprocessing.get_context('fork').Pool(a.workers, maxtasksperchild=4) as pool:
        for i, (path, status) in enumerate(pool.imap_unordered(run_case, todo), 1):
            print(f'[{i}/{len(todo)} {time.monotonic() - start:.0f}s] {status} {path.name}', flush=True)


if __name__ == '__main__':
    main()
