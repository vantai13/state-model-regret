"""Doan Van Tai — mechanism-regime exploration v2: where does the dominant source of decision value switch
between current state (S = G_S|M1), model fidelity (M = G_M|S1) and their interaction (Gamma)?
[EXPLORATION ONLY, branch explore/mechanism-regime-v2; AI (Claude) theo ủy quyền]

Frozen native engine + L4.4 margin baseline (experiments.P4_04_baseline.evaluate), contract v1.3 namespace:
mu = 10, a = 6 (a/mu = .6, never scanned: amplitude stays held-out), tau = 1 s, c_sw = 0.
Every case must satisfy h/kappa <= 160 (keeps the frozen L4.9 panel, ratios 320/640, untouched) and is
refused if it equals an R09/R10 sealed key, a CF-v2 key or an L4.9 panel key. Every regime is discovery.
Cases come from results/explore_mech/cases/<stage>.json (written by design.py); one write-once JSON per
case; reruns skip finished cases; --shard i n runs cases with index % n == i (one shard per machine).

  python -m experiments.explore_mech.scan STAGE [--workers N] [--level K REF] [--shard I N] [--reverse]
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
import socket
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_mech'
CACHE = Path(os.environ.get('SMR_EXPLORE_CACHE', Path.home() / '.cache/smr_explore_mech'))
MAX_RATIO = 160
KEEP = ('Cref', 'Sbar', 'G_S', 'G_M', 'G_SM', 'Gamma', 'G_S_M1', 'G_M_S1', 'P_flip', 'losses', 'cost_error',
        'contrast_error', 'normalized_error', 'uncertain_action_mass', 'validity_errors', 'arithmetic_pass',
        'zero_action_certificate', 'Stay', 'Stay_error')


def key(params):
    lamA, lamB, kappa, eta, h, c = params
    return tuple(str(F(x)) for x in (lamA, lamB, 2 * F(eta), kappa, h, c))


def forbidden_keys():
    sealed = json.loads((ROOT / 'experiments/P4_03_map_audit/sealed_scope.json').read_text())['sealed']
    keys = {tuple(str(F(x)) for x in s['coordinates']) for s in sealed}
    cf = json.loads((ROOT / 'results/lessons/l3r_7/lean_close/cf_generation/attempt01/regimes_cf.json').read_text())['rows']
    keys |= {tuple(str(F(r['regime'][k])) for k in ('lambdaA', 'lambdaB', 'u', 'kappa', 'h', 'c_sw')) for r in cf}
    panel = json.loads((ROOT / 'experiments/P4_09_stationary/protocol.json').read_text())['future_panel']
    keys |= {key(p['parameters']) for p in panel}
    return keys


def admissible(params):
    lamA, lamB, kappa, eta, h, c = (F(x) for x in params)
    u = 2 * eta
    return (min(lamA, lamB) >= 6 and max(lamA, lamB) + u < 10 and u > 0 and kappa > 0 and h > 0 and c == 0
            and h / kappa <= MAX_RATIO and (h * 120).denominator == 1)


def actions(A, B):
    """Mechanism read-out of the four cells (added after sobol4; rows of earlier stages lack it): for current
    (S1) and old (S0) states, the population share where the true gap d = dA + dB and the mean-rollout gap
    h = hA + hB say Switch (< 0), the share where they disagree, and the population means of d and h. The mean
    model uses the engine's certified-zero rule. Pairs are processed in row blocks to bound memory."""
    import numpy as np
    out = {}
    for kind in ('current', 'old'):
        a, b = A[kind], B[kind]
        acc = dict(true_switch=0, mean_switch=0, disagree=0, E_true_gap=0, E_mean_gap=0)
        for s in range(0, len(a['w']), 512):
            sl = slice(s, s + 512)
            w = a['w'][sl, None] * b['w'][None, :]
            d = a['d'][sl, None] + b['d'][None, :]
            cert = (a['zero_h'][sl, None] & b['zero_h'][None, :]) | (a['sat_h'][sl, None] & b['sat_h'][None, :])
            h = np.where(cert, 0, a['h'][sl, None] + b['h'][None, :])
            acc['true_switch'] += (w * (d < 0)).sum()
            acc['mean_switch'] += (w * (h < 0)).sum()
            acc['disagree'] += (w * ((d < 0) != (h < 0))).sum()
            acc['E_true_gap'] += (w * d).sum()
            acc['E_mean_gap'] += (w * h).sum()
        out[kind] = {k: str(v) for k, v in acc.items()}
    return out


def run_case(args):
    case, level, path = args
    if path.exists():
        return path, 'SKIP'
    resource.setrlimit(resource.RLIMIT_CPU, (3600, 3605))
    from experiments.P4_04_baseline.evaluate import evaluate_level
    from experiments.R3R_08_population_numerics import population
    sides, raw = [], []
    original = population.side

    def record(*a, **k):
        result = original(*a, **k)
        sides.append({n: str(result[n]) for n in ('mean', 'mean_error') if n in result})
        if len(raw) < 2:
            raw.append(result)
        return result
    population.side = record
    try:
        row = evaluate_level(case, level, CACHE)
        out = {k: row.get(k) for k in KEEP}
        out.update(id=case['id'], parameters=case['parameters'], level=list(level), status='COMPLETED',
                   cpu=row.get('call_cpu_seconds'), baseline_sanity_pass=row.get('baseline_sanity_pass'),
                   baseline=[{k: b[k] for k in ('rho', 'L00', 'L10')} for b in row.get('baseline', [])],
                   sides=sides[:2], actions=actions(*raw), error=row.get('error'))
    except Exception as exc:
        out = dict(id=case['id'], parameters=case['parameters'], level=list(level), status='UNRESOLVED',
                   error=f'{type(exc).__name__}: {exc}')
    finally:
        population.side = original
    out['host'] = socket.gethostname()
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(out) + '\n')
    tmp.rename(path)
    return path, out['status']


def main():
    p = argparse.ArgumentParser()
    p.add_argument('stage')
    p.add_argument('--workers', type=int, default=os.cpu_count())
    p.add_argument('--level', nargs=2, type=int, default=[160, 2])
    p.add_argument('--shard', nargs=2, type=int, default=[0, 1])
    p.add_argument('--reverse', action='store_true', help='run this shard last-first (to steal leftover work)')
    a = p.parse_args()
    level = tuple(a.level)
    cases = json.loads((OUT / 'cases' / f'{a.stage}.json').read_text())
    bad = forbidden_keys()
    refused = [c['id'] for c in cases if key(c['parameters']) in bad or not admissible(c['parameters'])]
    if refused:
        raise SystemExit(f'{len(refused)} cases refused (sealed/CF/panel/inadmissible): {refused[:5]}')
    i, n = a.shard
    mine = [c for j, c in enumerate(cases) if j % n == i]
    out = OUT / a.stage / f'level_{level[0]}_{level[1]}'
    out.mkdir(parents=True, exist_ok=True)
    jobs = [(c, level, out / f"{c['id']}.json") for c in mine]
    todo = [j for j in jobs if not j[2].exists()]
    if a.reverse:
        todo.reverse()
    print(f'{a.stage} shard {i}/{n} on {socket.gethostname()}: {len(mine)} cases, {len(todo)} to run, '
          f'{a.workers} workers', flush=True)
    # The frozen code compiles its C++ helpers lazily into /tmp; workers racing on the first compile load a
    # half-written .so ("file too short"). Build them once here, before forking.
    from experiments.R3R_08_population_numerics import dyadic, piecewise
    from experiments.R3R_10_interval_evaluation import evaluator
    piecewise.library()
    dyadic.library()
    evaluator.library()
    start = time.monotonic()
    with multiprocessing.get_context('fork').Pool(a.workers, maxtasksperchild=4) as pool:
        for k, (path, status) in enumerate(pool.imap_unordered(run_case, todo), 1):
            print(f'[{k}/{len(todo)} {time.monotonic() - start:.0f}s] {status} {path.name}', flush=True)


if __name__ == '__main__':
    main()
