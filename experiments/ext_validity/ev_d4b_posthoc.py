"""Doan Van Tai — EV-D4b POST-HOC analysis (after the score; descriptive, not a verdict) [AI (Claude) theo ủy quyền 15/11/2026].
Where does the sign law fail? Per tau: level sign at h30, sign of the h10 -> h30 increment vs the predicted increment,
observed/predicted increment ratio, the intercept share |B|/|G30| of the line through (10T, G10), (30T, G30), and the
same with the share difference measured on the TEST seed. Plug-in medians by tau and h.

    python -m experiments.ext_validity.ev_d4b_posthoc        # writes results/ext_validity/ev_d4b/posthoc.json
"""
import csv
import json
from pathlib import Path

import numpy as np

D = Path(__file__).resolve().parents[2] / 'results/ext_validity/ev_d4b'
TAUS = (1, 10, 30, 60, 120, 300)


def main():
    cases = json.loads((D / 'cases.json').read_text())
    P = {(r['id'], int(r['h_mult']), r['twin']): float(r['pred_abs']) for r in csv.DictReader((D / 'predictions.csv').open())}
    rows, plug = [], {}
    for c in cases:
        tr = json.loads((D / 'train' / f"{c['id']}_s{c['seed']}.json").read_text())
        g = {m: json.loads((D / 'test' / f"{c['id']}_s{c['seed']}_h{m}.json").read_text()) for m in (10, 30)}
        for m in (10, 30):
            for t in ('fluid', 'ratefluid', 'ratefluid_nowcast_hybrid_train'):
                plug.setdefault(f'tau{c["tau"]:g}|{t}|h{m}', []).append(g[m]['twins'][t]['pct_E_stay'])
        for t, fn in (('fluid_nowcast', 'F_new'), ('ratefluid_nowcast', 'F_new_rate')):
            p30 = 100 * P[(c['id'], 30, t)] / g[30]['E_stay']['mean']
            if abs(p30) < 0.25:
                continue
            Ga = {m: g[m]['twins'][t]['G_S'] for m in (10, 30)}
            inc_obs, inc_pred = Ga[30] - Ga[10], P[(c['id'], 30, t)] - P[(c['id'], 10, t)]
            dtr = tr['shares']['30'][f'F_old_{t}'] - tr['shares']['30'][fn]
            dte = g[30][f'F_old_{t}'] - g[30][fn]
            rows.append(dict(id=c['id'], twin=t, tau=c['tau'], stratum=c['stratum'], pred30=p30, G30=g[30]['twins'][t]['pct_E_stay'],
                             G10=g[10]['twins'][t]['pct_E_stay'], level_ok=bool((g[30]['twins'][t]['pct_E_stay'] > 0) == (p30 > 0)),
                             inc_ok=bool((inc_obs > 0) == (inc_pred > 0)), inc_ratio=inc_obs / inc_pred if inc_pred else None,
                             B_share=abs(Ga[10] - inc_obs / 2) / max(abs(Ga[30]), 1e-12),
                             test_F_sign_ok=bool((g[30]['twins'][t]['pct_E_stay'] > 0) == (p30 * (dte / dtr if dtr else 0) > 0))))
    by = {}
    for tau in TAUS:
        q = [r for r in rows if r['tau'] == tau]
        by[str(tau)] = dict(n=len(q), level_sign=sum(r['level_ok'] for r in q), increment_sign=sum(r['inc_ok'] for r in q),
                            median_increment_ratio=float(np.median([r['inc_ratio'] for r in q if r['inc_ratio'] is not None])),
                            median_B_share=float(np.median([r['B_share'] for r in q])),
                            median_G10=float(np.median([r['G10'] for r in q])), median_G30=float(np.median([r['G30'] for r in q])))
    res = dict(note='POST-HOC, descriptive; rows = h30 nowcast rows with |pred| >= 0.25 pp (the D2 set)', n=len(rows),
               level_sign=sum(r['level_ok'] for r in rows), increment_sign=sum(r['inc_ok'] for r in rows),
               level_sign_with_test_F=sum(r['test_F_sign_ok'] for r in rows),
               by_tau=by, by_stratum={s: [sum(r['level_ok'] for r in rows if r['stratum'] == s), sum(r['stratum'] == s for r in rows)]
                                      for s in ('neg', 'band', 'pos')},
               median_T_int=float(np.median([json.loads((D / 'train' / f"{c['id']}_s{c['seed']}.json").read_text())['T_int'] for c in cases])),
               plugin_and_hybrid_medians={k: float(np.median(v)) for k, v in plug.items()}, rows=rows)
    (D / 'posthoc.json').write_text(json.dumps(res, indent=1) + '\n')
    print(json.dumps({k: v for k, v in res.items() if k not in ('rows', 'plugin_and_hybrid_medians')}, indent=1))


if __name__ == '__main__':
    main()
