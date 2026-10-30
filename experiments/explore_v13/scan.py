"""Doan Van Tai — run a declared list of NEW regimes through the population pilot [EXPLORATION].

AI (Claude) theo ủy quyền. Usage: python -m experiments.explore_v13.scan STAGE --workers 6 [--resume]
Stages are fixed in STAGES; outputs go to results/explore_v13/<stage>/ and are never overwritten.
Each finished regime is checkpointed in <stage>/partial/; --resume continues an interrupted stage
(same specs only) and the final files are assembled in spec order once every regime is done.
"""
import argparse
import csv
from fractions import Fraction as F
import itertools
import json
import multiprocessing
import os
from pathlib import Path
import pickle
import shutil
import time

import numpy as np

from experiments.explore_v13.population import evaluate, make_regime

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


def grid_plant(pairs, kappa, eta, h, ages, amps, prefix):
    """Like grid() but over (lamA, lamB) pairs and the plant extensions age / amp (exploration only);
    a combination the two-mode family rejects (stability, OFF rate, ON overload, dt grid) is skipped."""
    specs = []
    for i, ((a, b), k, e, hh, ag, am) in enumerate(itertools.product(pairs, kappa, eta, h, ages, amps)):
        try:
            make_regime(a, b, k, e, hh, 'check', ag, am)
        except ValueError:
            continue
        specs.append((f'{prefix}{i:03d}', a, b, k, e, hh, 1, 40, '0', ag, am))
    return specs


PLANT_ROBUST = [(('15/2', '8', '1/10', '3/4', '2'), '4', '6'), (('13/2', '7', '3/10', '3/4', '2'), '4', '6'),
                (('13/2', '7', '1/10', '3/4', '8'), '2', '6'), (('13/2', '8', '1/10', '3/4', '8'), '4', '6'),
                (('15/2', '8', '1/10', '3/4', '8'), '1', '4'), (('13/2', '7', '1', '3/4', '2'), '1', '4')]
JOINT_ROBUST = [('6', '15/2', '1/5', '7/8', '2'), ('13/2', '8', '1/5', '7/8', '3'), ('6', '15/2', '3/10', '7/8', '3')]
MAP_PAIRS = [('13/2', '7'), ('15/2', '8'), ('13/2', '8')]


def inside_frozen_cards(a, b, k, e, hh, c='0'):
    """True if the regime falls in any Phase 3R card box (MV/SH: plus, minus, BND), frozen at 1414d92.

    MV family: lamB=8, lamA in [7,15/2], u in [1,3/2], kappa in [1/10,3], h in [12,16], c_sw=0.
    SH family: lamB in [6,7], lamA in [7,8], u in [1,3/2], kappa in [1/10,3], h in [8,16], c_sw=0.
    These regimes are reserved for the one-shot confirmation; exploration must not look at them.
    """
    a, b, k, u, hh, c = F(a), F(b), F(k), 2 * F(e), F(hh), F(c)
    common = c == 0 and 1 <= u <= F(3, 2) and F(1, 10) <= k <= 3
    mv = common and b == 8 and 7 <= a <= F(15, 2) and 12 <= hh <= 16
    sh = common and 6 <= b <= 7 and 7 <= a <= 8 and 8 <= hh <= 16
    return mv or sh


def inside_frozen_cards_scaled(a, b, k, e, hh, c='0', age='1', amp='6'):
    """Card-box test up to the fluid plant's time scaling. Multiplying age, kappa (mode time constant,
    seconds) and h by the same factor leaves every % Cbar contrast unchanged (rates fixed; backlog and
    cost scale), so (age, kappa, h) is the age-1 regime (1, kappa/age, h/age). The cards are written at
    age 1 on the +/-6 plant; another amplitude is a different plant and is never inside a card box.
    Errata 30/10/2026: the map3age stage was filtered on raw coordinates, which let 10 regimes through."""
    if F(amp) != 6:
        return False
    return inside_frozen_cards(a, b, F(k) / F(age), e, F(hh) / F(age), c)


def outside(specs):
    return [s for s in specs
            if not inside_frozen_cards_scaled(*s[1:6], *(s[8:11] if len(s) > 8 else ('0',)))]


MAP_ROBUST = [('15/2', '8', '1/10', '3/4', '2'), ('13/2', '7', '3/10', '3/4', '2'), ('13/2', '7', '1/10', '3/4', '8'),
              ('13/2', '7', '1/10', '3/4', '4'), ('13/2', '7', '1/10', '3/4', '2'), ('15/2', '8', '1/10', '3/4', '8'),
              ('13/2', '7', '1/10', '1/2', '8'), ('13/2', '7', '3', '3/4', '8')]


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
    # Regime map (branch explore/v13-regime-map): search for state-dominant / neither regions,
    # strictly outside the frozen confirmation boxes. Wider loads, small rerouted load, short h.
    'map1': lambda: outside(grid(['13/2', '15/2', '17/2'], ['6', '7', '8', '17/2'], ['1/10', '3/10', '1', '3'],
                                 ['1/4', '1/2', '3/4'], ['2', '4', '8'], 'XM1')),
    # Robustness of map1 representatives: state-dom XM1222/XM1051, substitution XM1044/XM1043/XM1042,
    # model-dom XM1224/XM1041, neither (kappa 3) and a harm cell.
    'map1robustK': lambda: [(f'XMRK{i}', *c, 1, 80, '0') for i, c in enumerate(MAP_ROBUST)],
    'map1robustdt': lambda: [(f'XMRD{i}', *c, 2, 40, '0') for i, c in enumerate(MAP_ROBUST)],
    # map2: refine around the state-dominant (short h) and substitution (small kappa, lamA<7) regions.
    'map3age': lambda: outside(grid_plant(MAP_PAIRS, ['1/10', '3/10', '1'], ['1/2', '3/4'], ['2', '4', '8'],
                                          ['1/4', '1/2', '2', '4'], ['6'], 'XA')),
    'map4amp': lambda: outside(grid_plant(MAP_PAIRS, ['1/10', '3/10', '1'], ['1/2', '3/4'], ['2', '4', '8'],
                                          ['1'], ['4', '5', '7'], 'XB')),
    'plantrobust': lambda: [(f'XPR{i}{tag}', *c, ref, K, '0', ag, am) for i, (c, ag, am) in enumerate(PLANT_ROBUST)
                            for tag, ref, K in (('K', 1, 80), ('D', 2, 40))],
    'jointrobust': lambda: [(f'XJR{i}{tag}', *c, ref, K, '0', '1', '6') for i, c in enumerate(JOINT_ROBUST)
                            for tag, ref, K in (('K', 1, 80), ('D', 2, 40))],
    'map2': lambda: outside(
        grid(['6', '13/2'], ['7', '15/2', '8'], ['1/5', '3/10', '1/2', '7/10', '1'], ['1/2', '3/4', '7/8'],
             ['1', '2', '3', '4'], 'XM2S')
        + grid(['6', '25/4', '13/2', '27/4'], ['13/2', '7', '15/2'], ['1/20', '1/10', '3/20'],
               ['5/8', '3/4', '7/8'], ['4', '8'], 'XM2X')),
    'robustK': lambda: [(f'XRK{i}', *c, 1, 80, '0') for i, c in enumerate(ROBUST)],
    'robustdt': lambda: [(f'XRD{i}', *c, 2, 40, '0') for i, c in enumerate(ROBUST)],
}


def with_plant_columns(o):
    """Rows checkpointed before the age/amp extension lack those columns; they were computed on the
    inherited plant (age 1 s, +/-6) with arithmetic shown bitwise equal to the extended code."""
    if 'age' in o:
        return o
    out = {}
    for k, v in o.items():
        out[k] = v
        if k == 'c_sw':
            out['age'], out['amp'] = 1.0, 6.0
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=sorted(STAGES))
    parser.add_argument('--workers', type=int, default=6)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    out = ROOT / 'results/explore_v13' / args.stage
    specs = STAGES[args.stage]()
    spec_text = json.dumps([list(map(str, s)) for s in specs], indent=1)
    if args.resume:
        if (out / 'status.json').exists():
            raise SystemExit(f'{args.stage} already complete')
        if (out / 'specs.json').read_text() != spec_text:
            raise SystemExit(f'{args.stage}: specs differ from the interrupted run')
    else:
        out.mkdir(parents=True, exist_ok=False)
        (out / 'specs.json').write_text(spec_text)
    part = out / 'partial'
    part.mkdir(exist_ok=True)
    done = {q.stem for q in part.glob('*.pkl')}
    # slow regimes (old observation, long h, small kappa = fast mode switching) first, so the pool does not end
    # on one straggler
    todo = sorted((s for s in specs if s[0] not in done),
                  key=lambda s: (-(F(s[9]) if len(s) > 9 else 1), -F(s[5]), F(s[3])))
    start = time.monotonic()
    with multiprocessing.get_context('fork').Pool(args.workers) as pool:
        for n, (o, p) in enumerate(pool.imap_unordered(evaluate, todo, chunksize=1), len(done) + 1):
            tmp = part / f"{o['id']}.tmp"
            tmp.write_bytes(pickle.dumps((o, p)))
            os.replace(tmp, part / f"{o['id']}.pkl")
            print(f"[{args.stage}] {o['id']} lamA={o['lambdaA']} kappa={o['kappa']} eta={o['eta']} h={o['h']} "
                  f"GS={o['G_S_pctC']:+.2f}%C GM={o['G_M_pctC']:.2f}%C Gam={o['Gamma_pctC']:+.2f}%C "
                  f"Pflip={o['P_flip']:.3f} ({n}/{len(specs)}, {time.monotonic() - start:.0f}s)", flush=True)
    rows, pairs = [], []
    for s in specs:
        o, p = pickle.loads((part / f'{s[0]}.pkl').read_bytes())
        rows.append(with_plant_columns(o))
        pairs.extend(p)
    with (out / 'regimes.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    arr = {c: np.array([p[i] for p in pairs]) for i, c in enumerate(PAIR_COLS)}
    np.savez_compressed(out / 'pairs.npz', **arr)
    wall = time.monotonic() - start
    (out / 'status.json').write_text(json.dumps(dict(regimes=len(rows), pairs=len(pairs), wall_s=wall,
                                                     resumed_with=len(done)), indent=1))
    shutil.rmtree(part)
    print(f'[{args.stage}] done {len(rows)} regimes in {wall:.0f}s (resumed with {len(done)})', flush=True)


if __name__ == '__main__':
    main()
