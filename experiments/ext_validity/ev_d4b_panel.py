"""Doan Van Tai — EV-D4b: telemetry-age dose response on the 4 h continuous MAWI DITL trace, LOW-LOAD regimes
[AI (Claude) theo ủy quyền 14/11/2026]. New card after EV-D4 stopped (results/ext_validity/ev_d4/REPORT_EV_D4.md).

Same series (ev_d4/series_ditl4h_mod10.npz, paths = disjoint 10 % flow subsets, one shared real-time phase), same six
telemetry ages and the same D1-D6 as EV-D4. Only the regime range changes: max(lamA, lamB) + u <= 7.75 (load <= 0.775),
chosen from EV-D4 attempt-2 TRAIN T_int (no outcome existed), so that 30*T_int fits in half the 4 h series.
Fresh Sobol seed and fresh case seeds. The EV-D4 feasibility rule is applied after train by `select`.

    python -m experiments.ext_validity.ev_d4b_panel design          # cases_all.json
    python -m experiments.ext_validity.packet train --cases results/ext_validity/ev_d4b/cases_all.json --out results/ext_validity/ev_d4b/train --workers N
    python -m experiments.ext_validity.ev_d4b_panel select          # cases.json = regimes passing the rule at every tau
    python -m experiments.ext_validity.ev_d4b_panel predict         # train JSON only
    python -m experiments.ext_validity.ev_d4b_panel run N           # test seed; resumable, fixed seeds per (case, h)
    python -m experiments.ext_validity.ev_d4b_panel manifest        # sha256 of every raw test file, BEFORE score
    python -m experiments.ext_validity.ev_d4b_panel score
"""
import csv
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

from experiments.ext_validity import ev_d4_panel as D4

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/ext_validity/ev_d4b'
ALL, CASES, PRED = OUT / 'cases_all.json', OUT / 'cases.json', OUT / 'predictions.csv'
SERIES = 'results/ext_validity/ev_d4/series_ditl4h_mod10.npz'
SEED = 20261231
LOADCAP = 7.75
TINT_MAX = 7200 / 30
MIN_REGIMES = 10


def design():
    from scipy.stats import qmc
    if ALL.exists():
        raise FileExistsError(ALL)
    cases, i = [], 0
    for k, (name, (lo, hi, n)) in enumerate(D4.STRATA.items()):
        acc = 0
        for pu, pa, px in qmc.Sobol(3, scramble=True, seed=SEED + k).random(4096):
            if acc >= n:
                break
            u = 0.25 * (1 + int(pu * 7))                       # 0.25 .. 1.75
            lamA = 6 + 0.25 * int(pa * max(1, int((LOADCAP - u - 6) * 4) + 1))
            x = round(lo + (hi - lo) * px, 2)
            lamB = round(lamA + x * u, 4)
            if not (lamB >= 6 and max(lamA, lamB) + u <= LOADCAP):
                continue
            base = dict(lamA=lamA, lamB=lamB, u=u, seed=14000 + i, n_inst=10000, spacing_mult=3, train_T=100000.,
                        sample_dt=0.2, h_mult=[10, 30], batches=40)
            p = dict(series=SERIES, key='s0', path_keys=['s0', 's1'], bin=0.01)
            for tau in D4.TAUS:
                cases.append(dict(base, id=f'M{name[0].upper()}{acc:02d}_tau{tau}', cls='trace_cox', params=p,
                                  stratum=name, trace='ditl4h', tau=float(tau)))
            acc += 1
            i += 1
        if acc < n:
            raise RuntimeError(f'stratum {name}: only {acc} regimes under the load cap')
    OUT.mkdir(parents=True, exist_ok=True)
    ALL.write_text(json.dumps(cases, indent=1) + '\n')
    print(len(cases), 'cases')


def select():
    if CASES.exists():
        raise FileExistsError(CASES)
    cases = json.loads(ALL.read_text())
    bad = set()
    for c in cases:
        t = json.loads((OUT / 'train' / f"{c['id']}_s{c['seed']}.json").read_text())
        if t['T_int_censored'] or t['T_int'] > TINT_MAX:
            bad.add(c['id'].split('_')[0])
    kept = [c for c in cases if c['id'].split('_')[0] not in bad]
    regimes = len({c['id'].split('_')[0] for c in kept})
    (OUT / 'selection.json').write_text(json.dumps(dict(excluded=sorted(bad), kept_regimes=regimes,
                                                        rule=f'T_int <= {TINT_MAX} s and not censored at every tau'), indent=1) + '\n')
    print('excluded', sorted(bad), 'kept regimes', regimes)
    if regimes < MIN_REGIMES:
        raise SystemExit(f'STOP: only {regimes} regimes pass the rule (< {MIN_REGIMES}); no test')
    CASES.write_text(json.dumps(kept, indent=1) + '\n')


def _bind():
    D4.OUT, D4.CASES, D4.PRED = OUT, CASES, PRED


def predict():
    _bind()
    D4.predict()


def run(workers):
    from concurrent.futures import ProcessPoolExecutor
    from multiprocessing import get_context
    from experiments.ext_validity import packet as P
    (OUT / 'test').mkdir(parents=True, exist_ok=True)
    tasks = []
    for c in json.loads(CASES.read_text()):
        tr = json.loads((OUT / 'train' / f"{c['id']}_s{c['seed']}.json").read_text())
        assert tr['case_sha256'] == P.signature(c)
        for m in c['h_mult']:
            out = OUT / 'test' / f"{c['id']}_s{c['seed']}_h{m}.json"
            if not out.exists():
                tasks.append(('test', c, tr, m, out, False))
    tasks.sort(key=lambda t: -t[3] * t[2]['T_int'])
    print(len(tasks), 'tasks', flush=True)
    with ProcessPoolExecutor(max_workers=workers, mp_context=get_context('spawn')) as pool:
        for r in pool.map(P.job, tasks):
            print(json.dumps(r), flush=True)
    print('RUN_DONE', flush=True)


def manifest():
    files = sorted((OUT / 'test').glob('*.json'))
    m = dict(created=time.strftime('%Y-%m-%dT%H:%M:%S%z'), n=len(files),
             sha256={f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in files})
    (OUT / 'raw_manifest.json').write_text(json.dumps(m, indent=1) + '\n')
    print(m['n'], 'raw files hashed at', m['created'])


def score():
    _bind()
    D4.score()


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'run':
        run(int(sys.argv[2]))
    else:
        dict(design=design, select=select, predict=predict, manifest=manifest, score=score)[cmd]()
