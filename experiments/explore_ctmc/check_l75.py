"""Doan Van Tai — score results/explore_ctmc/l75/CARD_L7_5.md as locked [EXPLORATION ONLY; AI (Claude) theo ủy quyền;
the card is AI-drafted on the author's order and must be reviewed before it is locked].

  python -m experiments.explore_ctmc.check_l75    # -> results/explore_ctmc/score_l75.json

Inputs: truth units results/explore_ctmc/runs_l75/<stage>/<id>__t<tau>.json (stages sobol, old, xs) and the frozen zero
fit l75/ZEROFIT_tau.csv (single host). Eligibility comes only from parameters and the frozen zero fit, so every unit is
known even when its truth is UNRESOLVED.

Readings fixed before any truth (strictest where the card is silent):
  R1  h and tau are grouped by the NEAREST grid multiple (tau.H_GRID, tau.TAU_GRID / XS_TAU) of h/T_int and tau/T_int, not
      by interval edges: the 3-digit rounding puts 7 T_int at 6.998 or 7.002.
  R2  UNRESOLVED (card §5): unit = (regime, tau). A series (regime, h) over tau is unresolved if any of its units is. A
      prediction or part is INCONCLUSIVE when more than 10% of its eligible units (L75-2) or series (L75-1, -3, -4) are
      unresolved, or when fewer than N_MIN remain.
  R3  Series predictions (L75-1, L75-3) use the 8 grid tau of a regime sorted by tau, mapped exactly from the case list
      (tau.tau_grid_map); the extra reference tau = 1 s is ignored, but a grid tau that rounds to 1 s (TB0001) is kept.
  R4  L75-4 edge: first sign change + -> - over x > 0 (rule of zf_report.x_star, linear interpolation) of truth G_S and of
      zero-fit z_pred1 at the same (family, tau). A series with no zero-fit edge is excluded (reported); a series with a
      zero-fit edge but no truth edge FAILS.
  R5  Parts combine as in check_l73: any FAIL -> FAIL, all PASS -> PASS, otherwise INCONCLUSIVE.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from experiments.explore_ctmc import tau as T5

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'
N_MIN, UNRES_MAX = 10, 0.10
TOL_DOSE, TOL_S, TOL_EDGE = 0.05, 0.01, 0.01          # pp, pp, x units (card §6)
TAU_GROUPS = {'tau<=0.03': (0.003, 0.01, 0.03), 'tau 0.1-0.3': (0.1, 0.3), 'tau>=1': (1.0, 3.0, 10.0)}


def nearest(v, grid):
    """Nearest grid multiple on a log scale, element-wise."""
    g = np.array([float(x) for x in grid])
    v = np.atleast_1d(np.asarray(v, float))
    return g[np.abs(np.log(v[:, None] / g[None, :])).argmin(axis=1)]


def load(out=OUT):
    z = pd.read_csv(out / 'l75' / 'ZEROFIT_tau.csv', dtype={'h': str, 'tau': str})
    z = z[(z.status == 'COMPLETED') & (z.h != 'inf')].copy()
    z['h_mult'] = nearest(z.h_Tint.values, T5.H_GRID)
    z.loc[z.stage == 'xs', 'h_mult'] = 10.0
    gmap = {}
    for st in ('sobol', 'old', 'xs'):
        for c in json.loads((out / 'cases_l75' / f'{st}.json').read_text()):
            gmap.update({(st, c['id'], t): m for t, m in T5.tau_grid_map(c, st).items()})
    z['tau_mult'] = [gmap.get((s, i, t), np.nan) for s, i, t in zip(z.stage, z.id, z.tau)]      # R3: exact grid map
    recs, status = [], {}
    for st in ('sobol', 'old', 'xs'):
        for f in sorted((out / 'runs_l75' / st).glob('*.json')):
            d = json.loads(f.read_text())
            status[(st, d['id'], d['tau'])] = d['status']
            if d['status'] != 'COMPLETED':
                continue
            for r in d['h']:
                recs.append(dict(stage=st, id=d['id'], tau=d['tau'], h=r['h'], G_S=r['G_S'], S=r['S'],
                                 F=r['d22']['F'] if 'd22' in r else np.nan))
    t = pd.DataFrame(recs, columns=['stage', 'id', 'tau', 'h', 'G_S', 'S', 'F'])
    m = z.merge(t, on=['stage', 'id', 'tau', 'h'], how='left')
    m['unit_status'] = [status.get((s, i, ta), 'MISSING') for s, i, ta in zip(m.stage, m.id, m.tau)]
    m['done'] = (m.unit_status == 'COMPLETED') & m.G_S.notna()
    return m


def verdict(n, unres, value, thr):
    if unres > UNRES_MAX or n < N_MIN:
        return 'INCONCLUSIVE'
    return 'REPORT' if thr is None else ('PASS' if value >= thr else 'FAIL')


def combine(parts):
    vs = [p['verdict'] for p in parts]
    return 'FAIL' if 'FAIL' in vs else ('PASS' if all(v == 'PASS' for v in vs) else 'INCONCLUSIVE')


def series_score(m, keep, hit):
    """keep(g) -> bool on a zero-fit series (regime, h) over its grid tau; hit(g) -> bool on the truth series."""
    out = dict(eligible=0, unresolved=0, n=0, hits=0)
    for _, g in m.groupby(['stage', 'id', 'h']):
        g = g[g.tau_mult.notna()].sort_values('tau_s')
        if len(g) < 2 or not keep(g):
            continue
        out['eligible'] += 1
        if not g.done.all():
            out['unresolved'] += 1
            continue
        out['n'] += 1
        out['hits'] += bool(hit(g))
    unres = out['unresolved'] / out['eligible'] if out['eligible'] else 0.0
    value = out['hits'] / out['n'] if out['n'] else None
    return dict(out, unresolved_share=unres, value=value)


def x_edge(x, y):
    o = np.argsort(x)
    x, y = np.asarray(x)[o], np.asarray(y)[o]
    pos = x > 0
    x, y = x[pos], y[pos]
    for i in range(1, len(x)):
        if y[i - 1] > 0 >= y[i]:
            return float(x[i - 1] + (x[i] - x[i - 1]) * y[i - 1] / (y[i - 1] - y[i]))
    return None


def score(m):
    res = {}
    main = m[m.stage.isin(['sobol', 'old'])]
    # L75-1 dose-response: h >= 7 T_int, harm at every grid tau in the zero fit; truth G_S non-increasing in tau
    keep1 = lambda g: g.h_mult.iloc[0] >= 7 and (g.z_pred1 < -0.5).all()
    hit1 = lambda g: (np.diff(g.G_S.values) <= TOL_DOSE).all()
    s1 = series_score(main, keep1, hit1)
    res['L75-1'] = dict(label='onset (zero-fit 87/87)', threshold=0.90, **s1, verdict=verdict(s1['n'], s1['unresolved_share'], s1['value'], 0.90))
    # L75-2 onset at every tau: |G_S - z_pred1| <= 0.1 pp, per tau group x h multiple {7, 15, 30}
    parts = {}
    for gname, taus in TAU_GROUPS.items():
        for hm, thr in ((7.0, 0.90), (15.0, 0.95), (30.0, 0.95)):
            e = main[main.tau_mult.isin(taus) & np.isclose(main.h_mult, hm)]
            unres = float((~e.done).mean()) if len(e) else 0.0
            d = e[e.done]
            v = float(((d.G_S - d.z_pred1).abs() <= 0.1).mean()) if len(d) else None
            parts[f'{gname} h={hm:g}T'] = dict(n=len(d), eligible=len(e), unresolved_share=unres, value=v, threshold=thr,
                                               verdict=verdict(len(d), unres, v, thr))
    report = {}
    for gname, taus in TAU_GROUPS.items():
        e = main[main.tau_mult.isin(taus) & np.isclose(main.h_mult, 3.0)]
        d = e[e.done]
        report[f'{gname} h=3T'] = dict(n=len(d), value=float(((d.G_S - d.z_pred1).abs() <= 0.1).mean()) if len(d) else None)
    res['L75-2'] = dict(label='onset', parts=parts, report_only=report, verdict=combine(list(parts.values())))
    # R-a report only: help band (sobol stratum 'band'), truth G_S non-decreasing in tau, every h; never a verdict
    band = main[main.stratum == 'band'] if 'stratum' in main else main.iloc[0:0]
    ra = series_score(band, lambda g: True, lambda g: (np.diff(g.G_S.values) >= -TOL_DOSE).all())
    res['R-a'] = dict(label='chỉ báo', **ra, verdict='REPORT')
    # L75-3 model right: S non-decreasing in tau (tolerance TOL_S), every (regime, h) series
    s3 = series_score(main, lambda g: True, lambda g: (np.diff(g.S.values) >= -TOL_S).all())
    res['L75-3'] = dict(label='rủi ro', threshold=0.90, **s3, verdict=verdict(s3['n'], s3['unresolved_share'], s3['value'], 0.90))
    # L75-4 band edge on the x slice: truth edge vs zero-fit z_pred1 edge at the same (family, tau)
    xs = m[m.stage == 'xs']
    series, excluded, unres_n = [], [], 0
    for (fam, tm), g in xs.groupby(['family', 'tau_mult']):
        xz = x_edge(g.x.values, g.z_pred1.values)
        if xz is None:
            excluded.append(dict(family=fam, tau_mult=tm))
            continue
        near = g[(g.x > 0) & (g.x <= xz + 0.25)]           # the points that decide the truth edge
        if not near.done.all():
            unres_n += 1
            series.append(dict(family=fam, tau_mult=tm, x_edge_zf=xz, x_edge_truth=None, unresolved=True))
            continue
        xt = x_edge(g[g.done].x.values, g[g.done].G_S.values)
        series.append(dict(family=fam, tau_mult=tm, x_edge_zf=xz, x_edge_truth=xt, unresolved=False,
                           pass_=xt is not None and abs(xt - xz) <= TOL_EDGE))
    scored = [s for s in series if not s['unresolved']]
    unres = unres_n / len(series) if series else 0.0
    passing = sum(s['pass_'] for s in scored)
    need = int(np.ceil(0.9 * len(scored))) if scored else None
    v4 = 'INCONCLUSIVE' if (unres > UNRES_MAX or len(scored) < 10) else ('PASS' if passing >= need else 'FAIL')
    res['L75-4'] = dict(label='rủi ro', scored=len(scored), passing=passing, need=need, unresolved_share=unres,
                        excluded_no_zf_edge=excluded, series=series, verdict=v4)
    return res


def main():
    m = load()
    res = score(m)
    units = m.drop_duplicates(['stage', 'id', 'tau']).unit_status.value_counts().to_dict()
    verdicts = {k: v['verdict'] for k, v in res.items() if v['verdict'] != 'REPORT'}
    res['counts'] = dict(unit_status=units, verdicts=verdicts, PASS=sum(v == 'PASS' for v in verdicts.values()),
                         FAIL=sum(v == 'FAIL' for v in verdicts.values()),
                         INCONCLUSIVE=sum(v == 'INCONCLUSIVE' for v in verdicts.values()))
    (OUT / 'score_l75.json').write_text(json.dumps(res, indent=1, default=str) + '\n')
    print(res['counts'])


if __name__ == '__main__':
    main()
