"""Score E5 (card results/letter/e5/CARD_E5.md, amended): ordering accuracy and implied regret."""
import csv
import json

import numpy as np

from experiments.ext_validity import ev_te as T

OUT = T.ROOT / 'results/letter/e5'


def accuracy():
    rows = {}
    for f in sorted((OUT / 'raw').glob('G*.json')):
        meta = json.loads(f.read_text())
        means = np.load(f.with_suffix('.npz'))['means']
        best = int(np.argmin(meta['training_r_a']))
        correct = (means.argmin(axis=2) == best)
        ra = np.array(meta['training_r_a'])
        rows[meta['regime']] = dict(p=correct.mean(axis=0).tolist(), L_Tint=meta['L_Tint'], R=meta['R'],
                                    rel_gap=float((ra.max() - ra.min()) / ra.min()), r_min=float(ra.min()),
                                    best=best)
    return rows


def implied(acc, run, hs=('15', '30'), L_index=None):
    cells = list(csv.DictReader(open(T.ROOT / f'results/letter/{run}/cells.csv')))
    key = {(c['regime'], c['tau_mult'], c['h_mult'], c['pipeline']): c for c in cells}
    out = []
    for reg, a in acc.items():
        for tau in ('0.3', '1.0', '3.0'):
            for h in hs:
                ri, rr = key[(reg, tau, h, 'Hybrid-i')], key[(reg, tau, h, 'Hybrid-reversed')]
                Ri = max(float(ri['regret_fresh_pct']), float(ri['regret_stale_pct']))
                Rr = max(float(rr['regret_fresh_pct']), float(rr['regret_stale_pct']))
                p = a['p'][L_index]
                out.append(dict(regime=reg, tau=tau, h=h, p=p, R_i=Ri, R_rev=Rr, expected=p * Ri + (1 - p) * Rr))
    return out


def main():
    acc = accuracy()
    L = list(acc.values())[0]['L_Tint']
    med = [float(np.median([a['p'][k] for a in acc.values()])) for k in range(len(L))]
    allc = [int(sum(a['p'][k] == 1.0 for a in acc.values())) for k in range(len(L))]
    ge95 = [int(sum(a['p'][k] >= .95 for a in acc.values())) for k in range(len(L))]
    imp = {}
    for k, l in enumerate(L):
        cells = implied(acc, 'e4', L_index=k) + implied(acc, 'e4b', L_index=k)
        exp = np.array([c['expected'] for c in cells])
        imp[str(l)] = dict(cells=len(cells), le_0p5=int((exp <= .5).sum()), median=float(np.median(exp)),
                           mean=float(exp.mean()))
    worst = sorted(acc.items(), key=lambda kv: kv[1]['p'][L.index(100)])[:5]
    res = dict(L_Tint=L, median_accuracy=med, regimes_all_correct=allc, regimes_ge_095=ge95,
               implied_long_horizon=imp, per_regime=acc,
               lowest_at_100=[(k, v['p'][L.index(100)], round(v['rel_gap'], 3), round(v['r_min'], 3)) for k, v in worst],
               forecasts=dict(
                   F1_median_increasing=bool(all(np.diff(med) >= -1e-12)),
                   F2_at_100_ge_095=bool(med[L.index(100)] >= .95), F2_at_3_le_08=bool(med[L.index(3)] <= .8),
                   F4_at_100_share_le_0p5=imp['100']['le_0p5'] / imp['100']['cells']))
    dest = OUT / 'score.json'
    if dest.exists():
        raise SystemExit('score.json exists; write-once')
    dest.write_text(json.dumps(res, indent=1) + '\n')
    print(json.dumps({k: v for k, v in res.items() if k != 'per_regime'}, indent=1))


if __name__ == '__main__':
    main()
