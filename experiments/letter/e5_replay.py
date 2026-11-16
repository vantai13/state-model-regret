"""E5: long-run action ordering from a finite replayed demand record on GEANT.

Claude, 17/11/2026, under the author's delegation; card in results/letter/e5/CARD_E5.md.
One recorded demand path of length L (all OD mode processes) is replayed through every
action with common random numbers (ev_te.trajectory). The ordering estimate is the
argmin of the time-average total backlog over the first L; it is compared with the
long training simulation in results/ext_validity/ev_te/train/<regime>.json.
"""
import argparse
import json
import math
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context

import numpy as np

from experiments.ext_validity import ev_te as T
from experiments.letter import e4_geant as E

OUT = T.ROOT / 'results/letter/e5'
SEED, PILOT_SEED = 5100001, 5199999
R = 200
LS = (1, 3, 10, 30, 100, 300)
BURN = 50


def training(spec_id):
    tr = T.read_json(T.OUT / 'train' / f'{spec_id}.json')
    if tr['excluded'] or tr['seed'] != 1:
        raise ValueError('invalid training provenance')
    ra = [x['mean'] for x in tr['r_a']]
    return tr['T_int'], tr['dt'], ra


def record(task):
    spec, rep, seed = task
    ti, dt, _ = training(spec['id'])
    model = T.make_model(spec)
    burn = math.ceil(BURN * ti / dt)
    steps = math.ceil(max(LS) * ti / dt)
    cpu = time.process_time()
    rates, _, _, _ = T.trajectory(model, dt, burn, steps, T.seed_for(seed, spec['id'], rep))
    csum = np.cumsum(rates, axis=0)
    idx = [math.ceil(L * ti / dt) - 1 for L in LS]
    means = np.array([csum[i] / (i + 1) for i in idx])
    return spec['id'], rep, means, time.process_time() - cpu


def run(workers, pilot=False):
    specs = E.selected_specs(T.OUT)
    if pilot:
        by_ti = sorted(specs, key=lambda s: training(s['id'])[0])
        specs, reps, seed, out = [by_ti[0], by_ti[-1]], 2, PILOT_SEED, OUT / 'pilot'
    else:
        reps, seed, out = R, SEED, OUT / 'raw'
    out.mkdir(parents=True, exist_ok=True)
    if any(out.glob('*.npz')):
        raise FileExistsError(f'{out} already has raw files; one run only')
    T.native()
    tasks = [(s, rep, seed) for s in specs for rep in range(reps)]
    tasks.sort(key=lambda t: -training(t[0]['id'])[0])
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers, mp_context=get_context('spawn')) as pool:
        results = list(pool.map(record, tasks))
    for s in specs:
        rows = sorted((r for r in results if r[0] == s['id']), key=lambda r: r[1])
        means = np.stack([r[2] for r in rows])
        np.savez(out / f"{s['id']}.npz", means=means, L_Tint=np.array(LS), reps=np.array([r[1] for r in rows]))
        ti, dt, ra = training(s['id'])
        T.write_json(out / f"{s['id']}.json", dict(regime=s['id'], seed=seed, R=len(rows), L_Tint=list(LS),
                                                   burn_Tint=BURN, T_int=ti, dt=dt, training_r_a=ra,
                                                   CPU=sum(r[3] for r in rows)))
    summary = dict(seed=seed, pilot=pilot, regimes=[s['id'] for s in specs], R=reps, L_Tint=list(LS),
                   CPU=sum(r[3] for r in results), wall=time.perf_counter() - start, workers=workers)
    T.write_json(out / 'run_summary.json', summary)
    print(json.dumps(summary))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--workers', type=int, default=8)
    p.add_argument('--pilot', action='store_true')
    a = p.parse_args()
    run(a.workers, a.pilot)
