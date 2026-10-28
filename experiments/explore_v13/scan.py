"""Doan Van Tai — run a declared list of NEW regimes through the population pilot [EXPLORATION].

AI (Claude) theo ủy quyền. Usage: python -m experiments.explore_v13.scan STAGE --workers 6
Stages are fixed in STAGES; outputs go to results/explore_v13/<stage>/ and are never overwritten.
"""
import argparse
import csv
from fractions import Fraction as F
import itertools
import json
import multiprocessing
from pathlib import Path
import time

import numpy as np

from experiments.explore_v13.population import evaluate

ROOT = Path(__file__).resolve().parents[2]
PAIR_COLS = ('rid', 'ia', 'ib', 'w', 'ED', 'EDh', 'EdA', 'EdB', 'EhA', 'EhB', 'flip', 'reverse', 'blind', 'm_rel')


def grid(lamA, lamB, kappa, eta, h, prefix, ref=1, K=40, c_sw=('0',)):
    specs = []
    for i, (a, b, k, e, hh, c) in enumerate(itertools.product(lamA, lamB, kappa, eta, h, c_sw)):
        u = 2 * F(e)
        if F(a) + u >= 10 or F(b) + u >= 10:
            continue
        specs.append((f'{prefix}{i:03d}', a, b, k, e, hh, ref, K, c))
    return specs


# (lamA, lamB, kappa, eta, h): X2065, X2064, X2063, X2062, X2029, X2035, X2071, X2041, X2027
ROBUST = [('15/2', '8', '1/10', '3/4', '16'), ('15/2', '8', '1/10', '3/4', '12'), ('15/2', '8', '1/10', '3/4', '8'),
          ('15/2', '8', '1/10', '1/2', '16'), ('7', '8', '1/10', '3/4', '16'), ('7', '8', '3/10', '3/4', '16'),
          ('15/2', '8', '3/10', '3/4', '16'), ('15/2', '6', '1/10', '3/4', '16'), ('7', '8', '1/10', '3/4', '8')]


STAGES = {
    # Stage 1: 4 factors (A load, mode memory, rerouted load, horizon); B load fixed at 8.
    'stage1': lambda: grid(['6', '13/2', '7', '15/2', '8'], ['8'], ['3/10', '1', '3'], ['1/2', '3/4'], ['2', '8'], 'X1'),
    # Stage 2 (chosen after stage 1): where could G_M under stale state grow? Higher A load,
    # varied B headroom, shorter mode memory, longer horizons.
    'stage2': lambda: grid(['7', '15/2', '8'], ['6', '7', '8'], ['1/10', '3/10'], ['1/2', '3/4'], ['8', '12', '16'], 'X2'),
    # Stage 3: a switching cost known to all pipelines (outside D13, which fixes c_sw=0):
    # tests whether M0's same-sign exaggeration becomes harmful once the threshold is nonzero.
    'stage3': lambda: grid(['13/2', '7', '15/2', '8'], ['8'], ['3/10', '1', '3'], ['1/2', '3/4'], ['8'], 'X3',
                           c_sw=('1', '4')),
    # Robustness of the stage-2 regimes that drive the picture: finer quadrature (K=80, ref 1)
    # and finer time step (ref 2 = dt 1/240 s, K=40). Same coordinates, new ids.
    'robustK': lambda: [(f'XRK{i}', *c, 1, 80, '0') for i, c in enumerate(ROBUST)],
    'robustdt': lambda: [(f'XRD{i}', *c, 2, 40, '0') for i, c in enumerate(ROBUST)],
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=sorted(STAGES))
    parser.add_argument('--workers', type=int, default=6)
    args = parser.parse_args()
    out = ROOT / 'results/explore_v13' / args.stage
    out.mkdir(parents=True, exist_ok=False)
    specs = STAGES[args.stage]()
    (out / 'specs.json').write_text(json.dumps([list(map(str, s)) for s in specs], indent=1))
    start = time.monotonic()
    rows, pairs = [], []
    with multiprocessing.get_context('fork').Pool(args.workers) as pool:
        for o, p in pool.imap_unordered(evaluate, specs, chunksize=1):
            rows.append(o)
            pairs.extend(p)
            print(f"[{args.stage}] {o['id']} lamA={o['lambdaA']} kappa={o['kappa']} eta={o['eta']} h={o['h']} "
                  f"GS={o['G_S_pctC']:+.2f}%C GM={o['G_M_pctC']:.2f}%C Gam={o['Gamma_pctC']:+.2f}%C "
                  f"Pflip={o['P_flip']:.3f} ({len(rows)}/{len(specs)})", flush=True)
    rows.sort(key=lambda r: r['id'])
    with (out / 'regimes.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    arr = {c: np.array([p[i] for p in pairs]) for i, c in enumerate(PAIR_COLS)}
    np.savez_compressed(out / 'pairs.npz', **arr)
    (out / 'status.json').write_text(json.dumps(dict(regimes=len(rows), pairs=len(pairs),
                                                     wall_s=time.monotonic() - start), indent=1))
    print(f'[{args.stage}] done {len(rows)} regimes in {time.monotonic() - start:.0f}s', flush=True)


if __name__ == '__main__':
    main()
