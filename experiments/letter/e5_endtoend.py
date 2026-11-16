"""Post-hoc end-to-end expected regret for E5/E5b policies (Claude, 17/11/2026, after the E5/E5b scores).

Approximation: at h >= 7 T_int the hybrid with an estimated ordering is taken to act like Hybrid-i
(correct ordering) or Hybrid-reversed (wrong ordering); the saved +-50% magnitude variants support this.
Regret per cell = worse of the fresh and stale sides, from the E4/E4b cells.csv.
"""
import csv
import json

import numpy as np

from experiments.ext_validity import ev_te as T

OUT = T.ROOT / 'results/letter/e5'


def main():
    e5 = json.loads((OUT / 'score.json').read_text())['per_regime']
    gate = {}
    for f in sorted((OUT / 'e5b').glob('G*.json')):
        m = json.loads(f.read_text()); a = np.load(f.with_suffix('.npz'))['diff_mean_se']
        ra = np.array(m['training_r_a']); truth = np.sign(ra[1] - ra[0])
        conf = np.abs(a[:, :, 0]) > m['z'] * a[:, :, 1]; right = np.sign(a[:, :, 0]) == truth
        gate[m['regime']] = {L: (float((conf[:, j] & right[:, j]).mean()), float((conf[:, j] & ~right[:, j]).mean()))
                             for j, L in enumerate(m['L_Tint'])}
    lidx = {30: 3, 100: 4, 300: 5}
    reg = lambda c: max(float(c['regret_fresh_pct']), float(c['regret_stale_pct']))
    res = {}
    for L in (30, 100, 300):
        for name, hs in (('h7', ('7',)), ('h15_30', ('15', '30'))):
            pol = {'ungated_replay': [], 'gated_fallback_M0': [], 'true_ordering': [], 'M0': []}
            for run in ('e4', 'e4b'):
                cells = list(csv.DictReader(open(T.ROOT / f'results/letter/{run}/cells.csv')))
                key = {(c['regime'], c['tau_mult'], c['h_mult'], c['pipeline']): c for c in cells}
                for r in e5:
                    p = e5[r]['p'][lidx[L]]; cr, cw = gate[r][L]
                    for tau in ('0.3', '1.0', '3.0'):
                        for h in hs:
                            Ri, Rr, R0 = (reg(key[(r, tau, h, q)]) for q in ('Hybrid-i', 'Hybrid-reversed', 'M0'))
                            pol['ungated_replay'].append(p * Ri + (1 - p) * Rr)
                            pol['gated_fallback_M0'].append(cr * Ri + cw * Rr + (1 - cr - cw) * R0)
                            pol['true_ordering'].append(Ri); pol['M0'].append(R0)
            res[f'L{L}_{name}'] = {k: dict(n=len(v), le_0p5=int((np.array(v) <= .5).sum()), median=float(np.median(v)),
                                           mean=float(np.mean(v))) for k, v in pol.items()}
    (OUT / 'endtoend_posthoc.json').write_text(json.dumps(res, indent=1) + '\n')
    print(json.dumps(res['L100_h15_30'], indent=1))


if __name__ == '__main__':
    main()
