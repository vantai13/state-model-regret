"""Doan Van Tai — EV-D4c POST-HOC analysis (after the score; descriptive, not a verdict) [AI (Claude) theo ủy quyền 15/11/2026].
Per arm and design ratio r = tau/T_int:
- D6 pass share for plug-in twins and median plug-in effect at h10/h30 (where does T12 in its O(1) form fail?);
- nowcast increment-sign share with and without the noise filter, from score_rows.csv.

    python -m experiments.ext_validity.ev_d4c_posthoc        # writes results/ext_validity/ev_d4c/posthoc.json
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

D = Path(__file__).resolve().parents[2] / 'results/ext_validity/ev_d4c'
PLUGIN = ('fluid', 'ratefluid')


def main():
    cases = json.loads((D / 'cases.json').read_text())
    d6 = defaultdict(lambda: dict(ok=0, n=0, G10=[], G30=[], growth=[]))
    for c in cases:
        g = {m: json.loads((D / 'test' / f"{c['id']}_s{c['seed']}_h{m}.json").read_text()) for m in (10, 30)}
        e = g[10]['E_stay']['mean'] / g[30]['E_stay']['mean']
        for tw in PLUGIN:
            a, b = g[10]['twins'][tw], g[30]['twins'][tw]
            growth = b['pct_E_stay'] - e * a['pct_E_stay']
            k = d6[f"{c['arm']}|{c['r']:g}"]
            k['ok'] += abs(growth) <= max(.25, 2 * (b['se_pct'] + e * a['se_pct']))
            k['n'] += 1
            k['G10'].append(a['pct_E_stay'])
            k['G30'].append(b['pct_E_stay'])
            k['growth'].append(growth)
    d6_out = {k: dict(ok=v['ok'], n=v['n'], median_G10_pct=float(np.median(v['G10'])), median_G30_pct=float(np.median(v['G30'])),
                      median_growth_pct=float(np.median(v['growth']))) for k, v in sorted(d6.items())}
    rows = list(csv.DictReader((D / 'score_rows.csv').open()))
    inc = defaultdict(lambda: [0, 0, 0, 0])
    for r in rows:
        k = inc[f"{r['arm']}|{float(r['r']):g}"]
        k[0] += r['inc_ok'] == 'True'
        k[1] += 1
        if r['noise_ok'] == 'True':
            k[2] += r['inc_ok'] == 'True'
            k[3] += 1
    inc_out = {k: dict(inc_ok=v[0], n=v[1], inc_ok_noise=v[2], n_noise=v[3]) for k, v in sorted(inc.items())}
    c_small = sum(v['ok'] for k, v in d6_out.items() if k.startswith('C|') and float(k[2:]) <= 1.2)
    c_small_n = sum(v['n'] for k, v in d6_out.items() if k.startswith('C|') and float(k[2:]) <= 1.2)
    c_large = sum(v['ok'] for k, v in d6_out.items() if k.startswith('C|') and float(k[2:]) >= 2.5)
    c_large_n = sum(v['n'] for k, v in d6_out.items() if k.startswith('C|') and float(k[2:]) >= 2.5)
    res = dict(note='POST-HOC, descriptive; D6 formula of the card per (arm, r); increment sign from score_rows.csv',
               D6_C_r_le_1p2=[c_small, c_small_n], D6_C_r_ge_2p5=[c_large, c_large_n], D6=d6_out, increment_sign=inc_out)
    (D / 'posthoc.json').write_text(json.dumps(res, indent=1) + '\n')
    print(json.dumps({k: v for k, v in res.items() if k.startswith('D6_C')}, indent=1))
    for k, v in inc_out.items():
        if k.startswith('C|'):
            print(k, v, 'D6', d6_out[k]['ok'], '/', d6_out[k]['n'])


if __name__ == '__main__':
    main()
