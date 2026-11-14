"""Doan Van Tai — EV-D4 post-stop diagnostic, TRAIN ONLY (no test seed, no D) [AI (Claude) theo ủy quyền 14/11/2026].
Question: does replaying a single 15-min file in a loop (as in EV-D2/D3) shorten the backlog integral time T_int compared
with the 4 h continuous series? Same 20 regimes at tau = 30 s, same seeds, same path_keys/shared phase; only the series
changes: two single 15-min segments (10:00 and 12:00) of the same mod-10 DITL extraction.

    python -m experiments.ext_validity.ev_d4_loopdiag build /home/ubuntu/mawi/ditl10    # VM, writes the two series + cases
    python -m experiments.ext_validity.packet train --cases results/ext_validity/ev_d4/diag_loop15/cases.json --out results/ext_validity/ev_d4/diag_loop15/train --workers 12
    python -m experiments.ext_validity.ev_d4_loopdiag summary
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
D4 = ROOT / 'results/ext_validity/ev_d4'
OUT = D4 / 'diag_loop15'
SEGMENTS = ('202304121000', '202304121200')


def build(src):
    OUT.mkdir(parents=True, exist_ok=True)
    cases = []
    base = [c for c in json.loads((D4 / 'cases.json').read_text()) if c['tau'] == 30.0]
    for seg in SEGMENTS:
        meta = json.loads((Path(src) / f'{seg}.json').read_text())
        counts = np.fromfile(Path(src) / f'{seg}.bin', dtype='<i4').reshape(-1, 3)[:-1]
        rel = f'results/ext_validity/ev_d4/diag_loop15/series_{seg}.npz'
        with (ROOT / rel).open('xb') as f:
            np.savez_compressed(f, all=counts[:, 0], s0=counts[:, 1], s1=counts[:, 2],
                                metadata=json.dumps(dict(meta, note='single 15-min file, last bin dropped'), sort_keys=True))
        for c in base:
            cases.append(dict(c, id=c['id'].replace('_tau30', f'_loop{seg[-4:]}'), params=dict(c['params'], series=rel)))
    (OUT / 'cases.json').write_text(json.dumps(cases, indent=1) + '\n')
    print(len(cases), 'cases')


def summary():
    full = {c['id'].split('_')[0]: json.loads((D4 / 'train' / f"{c['id']}_s{c['seed']}.json").read_text())['T_int']
            for c in json.loads((D4 / 'cases.json').read_text()) if c['tau'] == 30.0}
    rows = {}
    for c in json.loads((OUT / 'cases.json').read_text()):
        t = json.loads((OUT / 'train' / f"{c['id']}_s{c['seed']}.json").read_text())
        reg, seg = c['id'].split('_')
        rows.setdefault(reg, dict(full_4h=full[reg]))[seg] = t['T_int']
    for seg in SEGMENTS:
        k = 'loop' + seg[-4:]
        r = np.array([v[k] / v['full_4h'] for v in rows.values()])
        print(k, 'T_int ratio loop/4h: median %.3f min %.3f max %.3f' % (np.median(r), r.min(), r.max()))
    (OUT / 'summary.json').write_text(json.dumps(rows, indent=1) + '\n')


if __name__ == '__main__':
    build(sys.argv[2]) if sys.argv[1] == 'build' else summary()
