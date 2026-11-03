"""Doan Van Tai — freeze the D22 zero-fit numbers from the M0-only pass [EXPLORATION ONLY; AI (Claude) theo ủy quyền].

  python -m experiments.explore_ctmc.freeze_d22    # -> results/explore_ctmc/PREDICTIONS_d22_numbers.csv
Fails if any D22 case of the scored stages lacks a COMPLETED M0-only row.
"""
from fractions import Fraction as F
import csv
import json
from pathlib import Path

from experiments.explore_ctmc.check_d22 import STAGES

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'


def main():
    rows, missing = [], []
    for stage in STAGES:
        for c in json.loads((OUT / 'cases' / f'{stage}.json').read_text()):
            f = OUT / 'm0_d22' / stage / f"{c['id']}.json"
            d = json.loads(f.read_text()) if f.exists() else None
            if not d or d['status'] != 'COMPLETED':
                missing.append((stage, c['id']))
                continue
            for r in d['h'][:-1]:
                rows.append(dict(stage=stage, id=d['id'], h=r['h'], h_Tint=float(F(r['h'])) / d['T_int_max'],
                                 z_inf=d['z_inf'], z_F_inf=d['z_F_inf'], z_V_inf=d['z_V_inf'], F_old=d['h'][-1]['F_old'],
                                 F_cb=d['h'][-1]['F_cb'], F_new=d['h'][-1]['F_new'], host=d['host']))
    if missing:
        raise SystemExit(f'{len(missing)} D22 cases without an M0-only row: {missing[:5]}')
    with (OUT / 'PREDICTIONS_d22_numbers.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(rows), 'rows frozen from', len({(r['stage'], r['id']) for r in rows}), 'cases')


if __name__ == '__main__':
    main()
