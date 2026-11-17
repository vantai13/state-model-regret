"""Saved-data checks used in the letter after the external reviews (Claude, 17/11/2026; post hoc).

Recomputes, from committed raw outputs only:
  * stationary rule (no telemetry) versus the corrected twin with fresh telemetry, CTMC (W1b raw,
    same true s for both) and GEANT (E4/E4b raw per-action costs, same level-(i) rates for both);
  * share of the hybrid's fresh-side cost reduction over M0 that comes from strict-preference states;
  * M0 with ties broken at random versus ties to Stay (cells.csv).
Writes results/letter/review_checks/summary.json.
"""
import csv
import glob
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/letter/review_checks'


def ctmc_stationary(exclude=()):
    grid = (1 / 3, 1, 3, 10, 30)
    rows = {g: dict(static=[], hybrid_new=[], hybrid_old=[]) for g in grid}
    for f in sorted(glob.glob(str(ROOT / 'results/letter/w1b/raw/*.json'))):
        raw = json.loads(Path(f).read_text())
        if raw['id'] in exclude:
            continue
        ev = [e for e in raw['evaluations'] if e['age_label'] == 'Tint_1'][0]
        for g in grid:
            r = min(ev['h'], key=lambda x: abs(np.log(x['h_Tint'] / g)))
            if abs(np.log(r['h_Tint'] / g)) < 0.02:
                for k in rows[g]:
                    rows[g][k].append(r['regret'][k])
    return {f'{g:.4g}': {k: dict(n=len(v), mean=float(np.mean(v)), median=float(np.median(v))) for k, v in d.items()}
            for g, d in rows.items()}


def geant(run):
    out = {}
    for f in sorted(glob.glob(str(ROOT / f'results/letter/{run}/raw/*_chunk00.npz'))):
        reg = Path(f).name.rsplit('_chunk', 1)[0]
        tr = json.loads((ROOT / f'results/ext_validity/ev_te/train/{reg}.json').read_text())
        best = int(np.argmin([x['mean'] for x in tr['r_a']]))
        zs = [np.load(q) for q in sorted(glob.glob(str(ROOT / f'results/letter/{run}/raw/{reg}_chunk*.npz')))]
        V = np.concatenate([z['V'] for z in zs]); D = np.concatenate([z['decisions'] for z in zs])
        T = np.concatenate([z['tie_flags'] for z in zs])
        P = list(zs[0]['pipelines']); H = [int(x) for x in zs[0]['h_mult']]; TA = list(zs[0]['tau_mult'])
        n = np.arange(len(V)); m0, hy, m1, t = P.index('M0'), P.index('Hybrid-i'), P.index('M1_new'), TA.index(1.0)
        per_h = {}
        for j, h in enumerate(H):
            cref = V[n, D[:, m1, 0, t, j], j].mean()
            reg_ = lambda a: 100 * (V[n, a, j].mean() - cref) / cref
            static = 100 * (V[:, best, j].mean() - cref) / cref
            red = V[n, D[:, m0, 0, t, j], j] - V[n, D[:, hy, 0, t, j], j]
            tie = T[:, m0, 0, t, j]
            per_h[h] = dict(static=float(static), hybrid_fresh=float(reg_(D[:, hy, 0, t, j])),
                            red_strict=float(red[~tie].sum()), red_tie=float(red[tie].sum()))
        out[reg] = per_h
    summ = {}
    for h in (1, 2, 4, 7, 15, 30):
        v = [out[r][h] for r in out]
        st = np.array([x['static'] for x in v]); hf = np.array([x['hybrid_fresh'] for x in v])
        rs = sum(x['red_strict'] for x in v); rt = sum(x['red_tie'] for x in v)
        summ[str(h)] = dict(regimes=len(v), hybrid_worse=int((hf > st + 1e-9).sum()), hybrid_better=int((hf < st - 1e-9).sum()),
                            mean_static=float(st.mean()), mean_hybrid_fresh=float(hf.mean()),
                            strict_share_of_fresh_gain=float(rs / (rs + rt)) if rs + rt else None)
    return summ


def tie_random(run):
    rows = list(csv.DictReader(open(ROOT / f'results/letter/{run}/cells.csv')))
    res = {}
    for p in ('M0', 'M0-tie-rand', 'M0-tie-i'):
        v = np.array([float(r['G_S_pct']) for r in rows if r['pipeline'] == p and r['h_mult'] == '30' and r['tau_mult'] == '1.0'])
        res[p] = dict(median_abs_GS=float(np.median(np.abs(v))), median_GS=float(np.median(v)),
                      harm_regimes=int((v < -0.25).sum()), regimes=len(v))
    return res


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    res = dict(note='post hoc, saved data only; tau = T_int; GEANT regret is the fresh side for the hybrid',
               ctmc_stationary_vs_hybrid=ctmc_stationary(),
               ctmc_stationary_vs_hybrid_fig3_92=ctmc_stationary(exclude=('Za7p5_u3-2_lA31-4_x1-3_k2',)),
               geant_stationary_vs_hybrid={run: geant(run) for run in ('e4', 'e4b')},
               geant_tie_random={run: tie_random(run) for run in ('e4', 'e4b')})
    (OUT / 'summary.json').write_text(json.dumps(res, indent=1) + '\n')
    print(json.dumps(res['geant_stationary_vs_hybrid']['e4']['2'], indent=1))


if __name__ == '__main__':
    main()
