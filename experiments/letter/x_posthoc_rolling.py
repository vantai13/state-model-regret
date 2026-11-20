"""Doan Van Tai — POST-HOC improvement check for X-GEANT G1 (Claude, 20/11/2026; Codex out of quota).

Locked G1 = NOT_EVALUABLE is unchanged. Operator-available alternative: predict DeltaF for test day d from the
decisions (no outcomes) of the previous K stable test days of the same regime; sign = sign(s_hat_train * DeltaF_roll).
Compared with the locked train-day prediction at record level (resolved: |G_S| >= 2 SE over instances and >= 0.25% C_ref)
and at pooled-cell level (sign of the mean over evaluable days). Any gain needs a new card on new flows.
"""
import csv, json, math, statistics
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
G = ROOT / 'results/letter/x_geant'
RULES = ('TH_0.65', 'TH_0.8', 'TH_0.9')


def main(K=5):
    pred = {(r['regime'], r['rule'], int(r['tau_s']), int(r['h_s'])): (int(r['predicted_G_S_sign']), float(r['s_hat_pooled_Mbit']))
            for r in csv.DictReader(open(G / 'predictions.csv'))}
    recs = sorted(json.loads((G / 'truth/receipt.json').read_text())['records'], key=lambda m: (m['regime'], m['date']))
    data = {}
    for m in recs:
        z = np.load(G / f"truth/records/{m['regime']}_{m['date']}.npz")
        data[(m['regime'], m['date'])] = {k: z[k] for k in ('decisions', 'G_S', 'C_ref', 'evaluable', 'h_seconds', 'tau_seconds', 'pipelines')}
    out = dict(K=K, label='POST-HOC; locked G1 unchanged')
    for method in ('train', 'rolling', 'same_period_oracle'):
        rec_hits, cells = [], {}
        for reg in sorted({k[0] for k in data}):
            days = sorted(d for r, d in data if r == reg)
            for i, day in enumerate(days):
                z = data[(reg, day)]
                pipes = [str(x) for x in z['pipelines']]
                for ih, h in enumerate(z['h_seconds']):
                    if int(h) not in (14400, 21600) or not bool(z['evaluable'][ih]):
                        continue
                    for t, tau in enumerate(z['tau_seconds']):
                        for rule in RULES:
                            p = pipes.index(rule)
                            sign_train, s_hat = pred[(reg, rule, int(tau), int(h))]
                            if method == 'train':
                                ps = sign_train
                            else:
                                window = days[max(0, i - K):i] if method == 'rolling' else days
                                if not window:
                                    continue
                                d = [data[(reg, w)]['decisions'][:, p, :, ih] for w in window]
                                dF = float(np.mean([x[:, t + 1].mean() - x[:, 0].mean() for x in d]))
                                ps = int(np.sign(s_hat * dF))
                            if ps == 0:
                                continue
                            g = z['G_S'][:, p, t, ih]
                            cref = float(z['C_ref'][:, ih].mean())
                            se = float(g.std(ddof=1) / math.sqrt(len(g)))
                            mean = float(g.mean())
                            if abs(mean) >= 2 * se and abs(mean) >= 0.0025 * cref:
                                rec_hits.append(int(np.sign(mean)) == ps)
                            cells.setdefault((reg, rule, int(tau), int(h)), []).append((mean, ps))
        pooled = [int(np.sign(np.mean([a for a, _ in v]))) == int(np.sign(sum(b for _, b in v))) for v in cells.values()
                  if sum(b for _, b in v) != 0]
        out[method] = dict(record_resolved=len(rec_hits), record_correct=sum(rec_hits),
                           record_accuracy=(sum(rec_hits) / len(rec_hits)) if rec_hits else None,
                           pooled_cells=len(pooled), pooled_sign_agreement=sum(pooled))
    (G / 'posthoc_rolling/summary.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
