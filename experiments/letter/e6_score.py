"""Score E6 from the committed raw files only (Claude, 17/11/2026), as defined in results/letter/e6/CARD_E6.md.

Cell = seed x regime x tau x h. Per record, the hybrid's regret is the worse of the fresh and stale sides;
the cell value is the mean over the 200 records. The stationary rule's cell value is the mean over the same
records (it does not depend on tau or side). Also reports the alternative aggregation (worse side of the
record-mean) as a sensitivity check.
"""
import glob
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
E6 = ROOT / 'results/letter/e6'


def load():
    cells = []
    for f in sorted(glob.glob(str(E6 / 'raw/*.npz'))):
        z = np.load(f)
        seed, regime = Path(f).stem.split('_', 1)
        hy, st = z['regret_hybrid'], z['regret_static']
        for li, L in enumerate(z['L_Tint']):
            for ti, tau in enumerate(z['tau_mult']):
                for hi, h in enumerate(z['h_mult']):
                    per_rec = hy[:, li, :, ti, hi]
                    cells.append(dict(seed=seed, regime=regime, L=int(L), tau=float(tau), h=int(h),
                                      hybrid=float(per_rec.max(axis=1).mean()),
                                      hybrid_alt=float(per_rec.mean(axis=0).max()),
                                      hybrid_fresh=float(per_rec[:, 0].mean()),
                                      static=float(st[:, li, hi].mean())))
    return cells


def summary(v):
    v = np.asarray(v)
    return dict(n=int(v.size), le_0p5=int((v <= .5).sum()), median=float(np.median(v)), mean=float(np.mean(v)))


def main():
    cells = load()
    out = dict(cells=len(cells), long=dict(), by_h=dict())
    for L in (30, 100, 300):
        c = [x for x in cells if x['L'] == L and x['h'] in (15, 30)]
        out['long'][str(L)] = dict(hybrid=summary([x['hybrid'] for x in c]),
                                   hybrid_alt=summary([x['hybrid_alt'] for x in c]),
                                   static=summary([x['static'] for x in c]),
                                   hybrid_worse_than_static=int(sum(x['hybrid'] > x['static'] + 1e-9 for x in c)))
        out['by_h'][str(L)] = {}
        for h in (1, 2, 4, 7, 15, 30):
            c = [x for x in cells if x['L'] == L and x['h'] == h]
            hy, hf, st = (np.array([x[k] for x in c]) for k in ('hybrid', 'hybrid_fresh', 'static'))
            out['by_h'][str(L)][str(h)] = dict(
                n=len(c), median_hybrid=float(np.median(hy)), median_static=float(np.median(st)),
                mean_hybrid=float(hy.mean()), mean_static=float(st.mean()),
                mean_hybrid_fresh=float(hf.mean()),
                cells_hybrid_worse=int((hy > st + 1e-9).sum()), cells_hybrid_better=int((hy < st - 1e-9).sum()),
                cells_fresh_worse=int((hf > st + 1e-9).sum()), cells_fresh_better=int((hf < st - 1e-9).sum()))
    L100, L300 = out['long']['100']['hybrid'], out['long']['300']['hybrid']
    e63 = {}
    for L in ('30', '100', '300'):
        b = out['by_h'][L]
        e63[L] = dict(never_worse=all(b[h]['median_hybrid'] <= b[h]['median_static'] + 1e-9 for h in b),
                      better_1_to_7=all(b[h]['median_hybrid'] < b[h]['median_static'] - 1e-9 for h in ('1', '2', '4', '7')))
    out['forecasts'] = {
        'E6-1 (L=100: cells <= 0.5% >= 72/204)': dict(value=L100['le_0p5'], held=L100['le_0p5'] >= 72),
        'E6-2 (L=300: cells <= 0.5% >= 110/204)': dict(value=L300['le_0p5'], held=L300['le_0p5'] >= 110),
        'E6-3 (median hybrid never worse than stationary at any h; better at 1-7 Tint)': dict(
            per_L=e63, held=all(v['never_worse'] and v['better_1_to_7'] for v in e63.values()))}
    (E6 / 'score.json').write_text(json.dumps(out, indent=1) + '\n')
    print(json.dumps(dict(long=out['long'], forecasts=out['forecasts']), indent=1))


if __name__ == '__main__':
    main()
