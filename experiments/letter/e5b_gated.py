"""E5b: confidence-gated replay ordering (card results/letter/e5/CARD_E5b.md).

Claude, 17/11/2026, author delegation. Same replay as E5 (ev_te.trajectory with common random
numbers); for each record prefix the Switch-minus-Stay cost-rate difference is summarized by
B batch means, so the record itself says whether its ordering is reliable.
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
from experiments.letter.e5_replay import training, BURN

OUT = T.ROOT / 'results/letter/e5/e5b'
SEED, R, B, Z = 5200001, 200, 10, 2.58
LS = (10, 30, 100, 300)


def record(task):
    spec, rep = task
    ti, dt, _ = training(spec['id'])
    model = T.make_model(spec)
    burn = math.ceil(BURN * ti / dt)
    steps = math.ceil(max(LS) * ti / dt)
    cpu = time.process_time()
    rates, _, _, _ = T.trajectory(model, dt, burn, steps, T.seed_for(SEED, spec['id'], rep))
    d = rates[:, 1] - rates[:, 0]
    out = []
    for L in LS:
        n = math.ceil(L * ti / dt)
        k = n // B
        bm = d[:k * B].reshape(B, k).mean(axis=1)
        out.append((float(bm.mean()), float(bm.std(ddof=1) / math.sqrt(B))))
    return spec['id'], rep, np.array(out), time.process_time() - cpu


def run(workers):
    specs = E.selected_specs(T.OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    if any(OUT.glob('*.npz')):
        raise FileExistsError('E5b raw exists; one run only')
    T.native()
    tasks = [(s, rep) for s in specs for rep in range(R)]
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers, mp_context=get_context('spawn')) as pool:
        res = list(pool.map(record, tasks))
    for s in specs:
        rows = sorted((r for r in res if r[0] == s['id']), key=lambda r: r[1])
        np.savez(OUT / f"{s['id']}.npz", diff_mean_se=np.stack([r[2] for r in rows]), L_Tint=np.array(LS))
        ti, dt, ra = training(s['id'])
        T.write_json(OUT / f"{s['id']}.json", dict(regime=s['id'], seed=SEED, R=len(rows), B=B, z=Z, L_Tint=list(LS),
                                                   T_int=ti, dt=dt, training_r_a=ra, CPU=sum(r[3] for r in rows)))
    T.write_json(OUT / 'run_summary.json', dict(seed=SEED, R=R, B=B, z=Z, L_Tint=list(LS), CPU=sum(r[3] for r in res),
                                                wall=time.perf_counter() - start, workers=workers))
    print('done', time.perf_counter() - start)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--workers', type=int, default=8)
    run(p.parse_args().workers)
