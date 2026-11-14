"""Doan Van Tai — EV-E (descriptive): value of fresh state G_S for several twin classes on the EV-B panel, random-time
decisions [AI (Claude) theo ủy quyền 14/11/2026]. Twins already defined in ctmc.evaluate: fluid M0, true model M1,
stateless static/const, hybrid M0 + h*s, hybrid with the M/M/1 s, KO (true model minus h*s), M0 + best margin."""
import csv
import json
import multiprocessing
from fractions import Fraction as F
from pathlib import Path

from experiments.explore_ctmc import ctmc as C

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / 'results/ext_validity/ev_b/cases.json'
OUT = ROOT / 'results/ext_validity/ev_e_twin_classes.csv'
TWINS = ('M0', 'M1', 'hybrid', 'hybrid_mm1', 'ko', 'margin', 'static')


def one(case):
    lamA, lamB, u, kappa = (F(x) for x in case['parameters'])
    ev = C.evaluate(lamA, lamB, u, kappa, [F(h) for h in case['hs']], disagree=False)
    out = []
    for r, hm in zip(ev['h'], ('1', '3', '10')):
        g = r['regret']
        row = dict(id=case['id'], stratum=case['stratum'], h_mult=hm, s_sign=int(ev['s'] > 0) - int(ev['s'] < 0))
        for t in TWINS:
            row[f'G_S_{t}'] = 0.0 if t == 'static' else g[f'{t}_old'] - g[f'{t}_new']
            row[f'regret_new_{t}'] = g['static'] if t == 'static' else g[f'{t}_new']
        out.append(row)
    return out


if __name__ == '__main__':
    cases = json.loads(CASES.read_text())
    with multiprocessing.get_context('fork').Pool(6) as p:
        rows = [r for rs in p.map(one, cases) for r in rs]
    with OUT.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(rows), 'rows ->', OUT)
