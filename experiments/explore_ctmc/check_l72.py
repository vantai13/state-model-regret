"""Doan Van Tai — score results/explore_ctmc/l72/CARD_L7_2.md exactly as locked [EXPLORATION ONLY; AI (Claude) theo
ủy quyền; the card itself is AI-drafted on the author's request].

  python -m experiments.explore_ctmc.check_l72    # -> results/explore_ctmc/score_l72.json

Inputs: truth rows results/explore_ctmc/runs_l72/<stage>/<id>.json; frozen zero-fit numbers l72/ZEROFIT_{a3,a7p5}.csv
and l72/compare_amplitudes.json (x*_zf). Parameter conditions (h/T_int, delta, N, |z_inf|) are read from the frozen
zero-fit rows, so every (case, h) is known even when its truth is UNRESOLVED.

Readings fixed here before any truth (the card is silent on them; the strictest reading is used):
  R1  Combining parts (L72-1 bins, L72-8 a/b): FAIL if any part FAILs, PASS if all PASS, otherwise INCONCLUSIVE.
  R2  UNRESOLVED rule (card §5): unit = distinct case among those eligible by parameter conditions; a missing truth file
      or a case whose row lacks the D22 block although N <= 3000 counts as UNRESOLVED.
  R3  L72-2: unit = series (u, lamA, kappa); the 10-row minimum is replaced by the card's own "< 4 series ->
      INCONCLUSIVE"; with m >= 4 scored series it passes when (#passing series) / m >= 5/6. The truth sign change is
      computed over COMPLETED points only, by the same rule as zf_report.x_star.
  R4  L72-4: each amplitude's p must itself survive the UNRESOLVED and n >= 10 rules, otherwise INCONCLUSIVE.
  R5  L72-8(a): majority class rate = max(q, 1 - q) with q the S > M rate; accuracies use the 197-quantile single
      threshold of analyze.best_threshold; P and h/T_int taken from the truth row.
  R6  L72-Z: "cũ − mới" is the difference of the two medians.
"""
from fractions import Fraction as F
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'
TAGS = ('a3', 'a7p5')
SETS = ('asym', 'sobol', 'xs')
N_MIN, UNRES_MAX = 10, 0.10


def best_threshold(values, labels):
    best = (0.0, None)
    for t in np.unique(np.quantile(values, np.linspace(0.01, 0.99, 197))):
        acc = max(((values < t) == labels).mean(), ((values >= t) == labels).mean())
        if acc > best[0]:
            best = (float(acc), float(t))
    return best


def load(tag):
    z = pd.read_csv(OUT / 'l72' / f'ZEROFIT_{tag}.csv', dtype={'h': str})
    z = z[z.status == 'COMPLETED'].copy()
    z['set'] = z.stage.str.rsplit('_', n=1).str[1]
    z['N_max'] = z[['N_A', 'N_B']].max(axis=1)
    recs, status = [], {}
    for st in SETS:
        for f in sorted((OUT / 'runs_l72' / f'zf_{tag}_{st}').glob('*.json')):
            d = json.loads(f.read_text())
            status[(d['stage'] if 'stage' in d else f'zf_{tag}_{st}', d['id'])] = d['status']
            if d['status'] != 'COMPLETED':
                continue
            for r in d['h']:
                sh = r['shares']
                long_switch = d['s'] < 0
                rec = dict(stage=f'zf_{tag}_{st}', id=d['id'], h=r['h'], G_S=r['G_S'], S=r['S'], M=r['M'],
                           reg_static=r['regret']['static'], reg_ko_new=r['regret']['ko_new'],
                           reg_M0_new=r['regret']['M0_new'], h_kappa_t=r['h_kappa'], h_Tint_t=r['h_Tint'],
                           ok_old=sh['M0_old'] if long_switch else 1 - sh['M0_old'],
                           ok_new=sh['M0_new'] if long_switch else 1 - sh['M0_new'])
                if 'd22' in r:
                    rec['F'] = r['d22']['F']
                recs.append(rec)
    t = pd.DataFrame(recs)
    m = z.merge(t, on=['stage', 'id', 'h'], how='left') if len(t) else z.assign(G_S=np.nan)
    m['case_status'] = [status.get((s, i), 'MISSING') for s, i in zip(m.stage, m.id)]
    if 'F' not in m:
        m['F'] = np.nan
    m['done'] = (m.case_status == 'COMPLETED') & m.G_S.notna() & ~((m.N_max <= 3000) & m.set.isin(['asym', 'sobol']) & m.F.isna())
    return m


def gate(elig, truth_mask, hit, thr, cmp='ge'):
    """Card §5: UNRESOLVED share over eligible distinct cases, then n >= 10 rows, then the threshold."""
    cases = elig.drop_duplicates(['stage', 'id'])
    unres = float((~elig.groupby(['stage', 'id']).done.all()).mean()) if len(cases) else 0.0
    rows = elig[elig.done]
    sel = rows[truth_mask(rows)]
    n = len(sel)
    out = dict(n=n, eligible_cases=len(cases), unresolved_share=unres)
    if unres > UNRES_MAX or n < N_MIN:
        return dict(out, value=None, verdict='INCONCLUSIVE')
    v = float(hit(sel).mean())
    ok = v >= thr if cmp == 'ge' else v <= thr
    return dict(out, value=v, threshold=thr, verdict='PASS' if ok else 'FAIL')


def combine(parts):
    vs = [p['verdict'] for p in parts]
    return 'FAIL' if 'FAIL' in vs else ('PASS' if all(v == 'PASS' for v in vs) else 'INCONCLUSIVE')


def x_cross(df, col):
    g = df[df.x > 0].sort_values('x')
    xs, zs = g.x.values, g[col].values
    for i in range(1, len(xs)):
        if zs[i - 1] > 0 >= zs[i]:
            return float(xs[i - 1] + (xs[i] - xs[i - 1]) * zs[i - 1] / (zs[i - 1] - zs[i]))
    return None


def score(tag, m, xstar):
    always = lambda r: np.ones(len(r), dtype=bool)
    AS = m[m.set.isin(['asym', 'sobol'])]
    res = {}
    bins = {}
    for (lo, hi), thr in (((2, 4), None), ((4, 7), 0.90), ((7, 15), 0.95), ((15, 40), 0.95)):
        e = AS[(AS.h_Tint > lo) & (AS.h_Tint <= hi)]
        hit = lambda r: (r.G_S - r.z_pred1).abs() <= 0.1
        if thr is None:
            rows = e[e.done]
            bins['(2;4] report'] = dict(n=len(rows), value=float(hit(rows).mean()) if len(rows) else None)
        else:
            bins[f'({lo};{hi}]'] = gate(e, always, hit, thr)
    res['L72-1'] = dict(label='onset', parts=bins, verdict=combine([v for k, v in bins.items() if 'report' not in k]))

    xs = m[m.set == 'xs']
    unres = float((~xs.groupby(['stage', 'id']).done.all()).mean()) if len(xs) else 1.0
    series = []
    for r in xstar:
        g = xs[(np.isclose(xs.u, r['u'])) & (np.isclose(xs.lamA, r['lamA'])) & (np.isclose(xs.kappa, r['kappa']))]
        xz = r['x_star']
        if xz is not None:
            near = g[(g.x >= xz - 0.1) & (g.x <= xz + 0.1)]
            if (~near.done).any():
                series.append(dict(series=[r['u'], r['lamA'], r['kappa']], x_star_zf=xz, excluded=True))
                continue
        xt = x_cross(g[g.done], 'G_S')
        ok = (xt is None and xz is None) or (xt is not None and xz is not None and abs(xt - xz) <= 0.05)
        series.append(dict(series=[r['u'], r['lamA'], r['kappa']], x_star_zf=xz, x_edge_truth=xt, excluded=False, pass_=ok))
    scored = [s for s in series if not s['excluded']]
    if unres > UNRES_MAX or len(scored) < 4:
        v2 = 'INCONCLUSIVE'
    else:
        v2 = 'PASS' if sum(s['pass_'] for s in scored) / len(scored) >= 5 / 6 else 'FAIL'
    res['L72-2'] = dict(label='rủi ro', unresolved_share=unres, scored=len(scored),
                        passing=sum(s['pass_'] for s in scored), series=series, verdict=v2)

    e = AS[(AS.delta != 0) & (AS.h_Tint > 7)]
    res['L72-3'] = dict(label='onset', **gate(e, always, lambda r: r.reg_static <= 0.1, 0.90))
    e = m[(m.set == 'sobol') & (m.delta != 0) & (m.h_Tint > 1) & (m.h_Tint <= 4)]
    res['L72-4_part'] = gate(e, always, lambda r: r.G_S > 0.1, -1.0)       # value only; verdict across amplitudes
    D = AS[AS.N_max <= 3000]
    e = D[D.h_Tint <= 1]
    res['L72-5'] = dict(label='rủi ro', **gate(e, lambda r: r.G_S < -0.5, lambda r: r.F < 0, 0.70))
    e = D[(D.h_Tint > 7) & (D.z_inf.abs() >= 0.5)]
    res['L72-6'] = dict(label='onset', **gate(e, lambda r: r.G_S < -0.5,
                                               lambda r: (r.F / r.G_S - r.z_F_inf / r.z_inf).abs() <= 0.1, 0.80))
    e = AS[AS.h_Tint > 4]
    res['L72-7'] = dict(label='rủi ro', **gate(e, lambda r: r.G_S < -0.5, lambda r: r.reg_ko_new >= 1.5 * r.reg_M0_new, 0.90))

    so = m[m.set == 'sobol']
    unres_a = float((~so.groupby(['stage', 'id']).done.all()).mean()) if len(so) else 1.0
    rel = so[so.done & ((so.S + so.M) >= 0.5)]
    if unres_a > UNRES_MAX or len(rel) < N_MIN:
        pa = dict(verdict='INCONCLUSIVE', n=len(rel), unresolved_share=unres_a)
    else:
        y = (rel.S > rel.M).values
        q = float(y.mean())
        accP = best_threshold((rel.h_kappa_t * rel.delta.abs()).values, y)
        accT = best_threshold(rel.h_Tint_t.values, y)
        ok = accP[0] >= max(q, 1 - q) + 0.05 and accP[0] >= accT[0]
        pa = dict(n=len(rel), unresolved_share=unres_a, majority=max(q, 1 - q), acc_P=accP, acc_h_Tint=accT,
                  verdict='PASS' if ok else 'FAIL')
    asy = m[m.set == 'asym']
    unres_b = float((~asy.groupby(['stage', 'id']).done.all()).mean()) if len(asy) else 1.0
    zz = asy[asy.done & (asy.z_inf.abs() >= 0.5)]
    if unres_b > UNRES_MAX or len(zz) < N_MIN:
        pb = dict(verdict='INCONCLUSIVE', n=len(zz), unresolved_share=unres_b)
    else:
        relerr = (zz.G_S - zz.z_inf).abs() / zz.z_inf.abs()
        rT, rK = spearmanr(relerr, zz.h_Tint_t)[0], spearmanr(relerr, zz.h_kappa_t)[0]
        pb = dict(n=len(zz), unresolved_share=unres_b, spearman_h_Tint=float(rT), spearman_h_kappa=float(rK),
                  verdict='PASS' if rT <= rK - 0.1 else 'FAIL')
    res['L72-8'] = dict(label='rủi ro', parts=dict(a=pa, b=pb), verdict=combine([pa, pb]))

    e = AS[(AS.delta != 0) & (AS.h_Tint >= 4)]
    rows = e[e.done & (e.G_S < -0.1)]
    if len(rows) < N_MIN:
        res['L72-Z'] = dict(label='zero-fit', n=len(rows), verdict='INCONCLUSIVE')
    else:
        mo, mn = float(rows.ok_old.median()), float(rows.ok_new.median())
        res['L72-Z'] = dict(label='zero-fit (không tính là bằng chứng)', n=len(rows), median_old=mo, median_new=mn,
                            verdict='PASS' if (mo >= 0.75 and mo - mn >= 0.05) else 'FAIL')
    return res


def main():
    out, data = {}, {}
    xstar = json.loads((OUT / 'l72' / 'compare_amplitudes.json').read_text())
    for tag in TAGS:
        data[tag] = load(tag)
        out[tag] = score(tag, data[tag], xstar[tag]['x_star'])
    p3, p75 = out['a3'].pop('L72-4_part'), out['a7p5'].pop('L72-4_part')
    if 'INCONCLUSIVE' in (p3['verdict'], p75['verdict']):
        v4 = 'INCONCLUSIVE'
    else:
        v4 = 'PASS' if p75['value'] <= p3['value'] - 0.05 else 'FAIL'
    out['cross_amplitude'] = {'L72-4': dict(label='rủi ro', p_3=p3, p_7p5=p75, verdict=v4)}
    counts = {}
    for tag in TAGS:
        status = data[tag].drop_duplicates(['stage', 'id']).case_status.value_counts().to_dict()
        risky = {k: v['verdict'] for k, v in out[tag].items() if k != 'L72-Z'}
        counts[tag] = dict(case_status=status, verdicts=risky,
                           PASS=sum(v == 'PASS' for v in risky.values()), FAIL=sum(v == 'FAIL' for v in risky.values()),
                           INCONCLUSIVE=sum(v == 'INCONCLUSIVE' for v in risky.values()))
    out['counts'] = counts
    (OUT / 'score_l72.json').write_text(json.dumps(out, indent=1, default=str) + '\n')
    for tag in TAGS:
        print(tag, counts[tag])
    print('L72-4 (cross-amplitude):', v4, 'p_3 =', p3.get('value'), 'p_7.5 =', p75.get('value'))


if __name__ == '__main__':
    main()
