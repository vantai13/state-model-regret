"""Doan Van Tai — EV-D3 (realistic telemetry age tau on two real MAWI traces) panel, predictions from the TRAIN seed only, and scoring [AI (Claude) theo ủy quyền 14/11/2026].
Simulator: packet.py (Codex; reviewed, CRN s-estimate by Claude). 20 regimes x 3 arrival classes = 60 cases.

    python -m experiments.ext_validity.ev_d_panel design
    python -m experiments.ext_validity.packet train --cases results/ext_validity/ev_d/cases.json --out results/ext_validity/ev_d/train --workers N
    python -m experiments.ext_validity.ev_d_panel predict          # from train JSON only (no D, no test)
    python -m experiments.ext_validity.packet test ... --out results/ext_validity/ev_d/test
    python -m experiments.ext_validity.ev_d_panel score
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/ext_validity/ev_d3'
CASES, PRED = OUT / 'cases.json', OUT / 'predictions.csv'
SEED = 20261201
STRATA = dict(neg=(-1.5, -0.1, 8), band=(0.02, 0.35, 4), pos=(0.4, 1.5, 8))
NOWCAST = (('fluid_nowcast', 'F_old_fluid_nowcast', 'F_new'), ('ratefluid_nowcast', 'F_old_ratefluid_nowcast', 'F_new_rate'))


def design():
    from scipy.stats import qmc
    if CASES.exists():
        raise FileExistsError(CASES)
    cases, i = [], 0
    for k, (name, (lo, hi, n)) in enumerate(STRATA.items()):
        acc = 0
        for pu, pa, px in qmc.Sobol(3, scramble=True, seed=SEED + k).random(1024):
            if acc >= n:
                break
            u = 0.25 * (1 + int(pu * 12))
            lamA = 6 + 0.25 * int(pa * max(1, int((10 - u - 6) * 4)))
            x = round(lo + (hi - lo) * px, 2)
            lamB = round(lamA + x * u, 4)
            if not (lamB >= 6 and max(lamA, lamB) + u < 9.75):
                continue
            base = dict(lamA=lamA, lamB=lamB, u=u, seed=9000 + i, n_inst=10000, spacing_mult=3, train_T=100000.,
                        sample_dt=0.2, h_mult=[10, 30], batches=40)
            # realistic telemetry ages (SNMP-like polling) on two real traces, real time (c = 1)
            for trace in ('20250311',):   # EV-D3a: trace 1 only (trace 2 download throttled; replication EV-D3b later)
                for tau in (30, 300):
                    p = dict(series=f'results/ext_validity/ev_d3/series_{trace}.npz', key='s0', bin=0.01)
                    cases.append(dict(base, id=f'R{name[0].upper()}{acc:02d}_t{trace[2:6]}_tau{tau}', cls='trace_cox',
                                      params=p, stratum=name, trace=trace, tau=float(tau)))
            acc += 1
            i += 1
    OUT.mkdir(parents=True, exist_ok=True)
    CASES.write_text(json.dumps(cases, indent=1) + '\n')
    print(len(cases), 'cases')


def predict():
    if PRED.exists():
        raise FileExistsError(PRED)
    rows = []
    for c in json.loads(CASES.read_text()):
        t = json.loads((OUT / 'train' / f"{c['id']}_s{c['seed']}.json").read_text())
        for m in c['h_mult']:
            sh, h = t['shares'][str(m)], m * t['T_int']
            for name, fo, fn in NOWCAST:
                rows.append(dict(id=c['id'], cls=c['cls'], stratum=c['stratum'], h_mult=m, twin=name,
                                 pred_abs=h * t['s_train'] * (sh[fo] - sh[fn]), s_train=t['s_train'], T_int=t['T_int']))
    with PRED.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows({k: (repr(v) if isinstance(v, float) else v) for k, v in r.items()} for r in rows)
    print(len(rows), 'prediction rows')


def score():
    P = {(r['id'], int(r['h_mult']), r['twin']): float(r['pred_abs']) for r in csv.DictReader(PRED.open())}
    cases = json.loads(CASES.read_text())
    rec = []
    for c in cases:
        for m in c['h_mult']:
            f = OUT / 'test' / f"{c['id']}_s{c['seed']}_h{m}.json"
            if not f.exists():
                continue
            g = json.loads(f.read_text())
            Es = g['E_stay']['mean']
            for twin, tw in g['twins'].items():
                pr = P.get((c['id'], m, twin))
                rec.append(dict(id=c['id'], cls=c['cls'], stratum=c['stratum'], h_mult=m, twin=twin, G=tw['pct_E_stay'],
                                se=tw['se_pct'], pred=None if pr is None else 100 * pr / Es))
    n_exp = sum(len(c['h_mult']) for c in cases)   # Claude (EV-D3): two h levels
    n_got = len({(r['id'], r['h_mult']) for r in rec})
    r30 = [r for r in rec if r['h_mult'] == 30]
    plug = [r for r in r30 if r['twin'] in ('fluid', 'ratefluid')]
    D1 = sum(r['G'] >= -max(0.25, 2 * r['se']) for r in plug) / len(plug)
    nc = [r for r in r30 if r['pred'] is not None]
    sig = [r for r in nc if abs(r['pred']) >= 0.25]
    D2 = sum((r['G'] > 0) == (r['pred'] > 0) for r in sig) / len(sig) if sig else None
    D3 = sum(abs(r['G'] - r['pred']) <= max(0.15, 0.3 * abs(r['pred'])) + 2 * r['se'] for r in nc) / len(nc)
    hyb = [r for r in rec if r['twin'] == 'ratefluid_nowcast_hybrid_train' and r['h_mult'] >= 10]
    D4 = sum(r['G'] >= -max(0.1, 2 * r['se']) for r in hyb) / len(hyb)
    v = lambda x, t: 'PASS' if x is not None and x >= t else ('NOT_EVALUABLE' if x is None else 'FAIL')
    inc = n_got < 0.9 * n_exp
    res = dict(completed=n_got, of=n_exp,
               D1=dict(n=len(plug), share=D1, threshold=0.9, verdict='INCONCLUSIVE' if inc else v(D1, 0.9)),
               D2=dict(n=len(sig), share=D2, threshold=0.85, verdict='INCONCLUSIVE' if inc else (v(D2, 0.85) if len(sig) >= 5 else 'NOT_EVALUABLE')),
               D3=dict(n=len(nc), share=D3, threshold=0.8, verdict='INCONCLUSIVE' if inc else v(D3, 0.8)),
               D4=dict(n=len(hyb), share=D4, threshold=0.9, verdict='INCONCLUSIVE' if inc else v(D4, 0.9)))
    by = {}
    for cls in ('tau30', 'tau300'):
        for twin in ('fluid', 'ratefluid', 'fluid_nowcast', 'ratefluid_nowcast', 'ratefluid_nowcast_hybrid_train'):
            g = [r['G'] for r in r30 if r['id'].endswith('_' + cls) and r['twin'] == twin]
            by[f'{cls}|{twin}'] = dict(n=len(g), median=float(np.median(g)) if g else None, harm=sum(x <= -0.25 for x in g))
    res['descriptive_30T'] = by
    (OUT / 'score.json').write_text(json.dumps(res, indent=1) + '\n')
    print(json.dumps({k: v for k, v in res.items() if k != 'descriptive_30T'}, indent=1))


if __name__ == '__main__':
    dict(design=design, predict=predict, score=score)[sys.argv[1]]()
