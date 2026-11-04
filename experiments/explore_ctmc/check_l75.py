"""Doan Van Tai — score results/explore_ctmc/l75/CARD_L7_5.md as locked [EXPLORATION ONLY; AI (Claude) theo ủy quyền;
the card is AI-drafted on the author's order and must be reviewed before it is locked].

  python -m experiments.explore_ctmc.check_l75    # -> results/explore_ctmc/score_l75.json

Inputs: truth units results/explore_ctmc/runs_l75/<stage>/<id>__t<tau>.json (stages sobol, old, xs) and the frozen zero
fit l75/ZEROFIT_tau.csv (single host). Eligibility comes only from parameters and the frozen zero fit, so every unit is
known even when its truth is UNRESOLVED.

Revised 04/11/2026 after the mentor's review, before the lock: L75-1 split by the frozen prior bit (l75/PRIOR_BIT.csv),
L75-3 amplitude filter, L75-4 restricted to the frozen eligible series (l75/L75_4_ELIGIBILITY.csv, n_min 6), L75-2 report
on |z_pred1| >= 0.5.

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
AMP_MIN = 0.01                                         # L75-3 amplitude filter, pp (mentor review §3a)
N_MIN_L754 = 6                                         # L75-4: 8 eligible (family, tau) series (mentor review §3b)
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
    pb = pd.read_csv(out / 'l75' / 'PRIOR_BIT.csv')
    prior = {(r.stage, r.id): bool(r.prior_correct) for r in pb.itertuples()}
    m['prior_correct'] = [prior.get((s, i), True) for s, i in zip(m.stage, m.id)]     # xs rows: unused
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


def s_class(values, tol=TOL_S, amp_min=AMP_MIN):
    """L75-3 class of one truth S series over its grid tau (sorted): 'flat' (max - min < amp_min, cannot fail),
    'pass' (no step drops by more than tol) or 'fail'. A failing series has a drop > tol, hence amplitude > tol >=
    amp_min, so the amplitude filter only removes series that cannot fail (mentor review §3a). Requires amp_min <= tol."""
    v = np.asarray(values, float)
    if not (np.diff(v) >= -tol).all():
        return 'fail'
    return 'flat' if v.max() - v.min() < amp_min else 'pass'


def series(m, keep):
    """Yield (key, group) for every (stage, id, h) series over its grid tau that satisfies keep(group)."""
    for key, g in m.groupby(['stage', 'id', 'h']):
        g = g[g.tau_mult.notna()].sort_values('tau_s')
        if len(g) >= 2 and keep(g):
            yield key, g


def score(m, elig=None):
    res = {}
    main = m[m.stage.isin(['sobol', 'old'])]
    longh = lambda g: g.h_mult.iloc[0] >= 7
    # L75-1a prior correct, h in {7, 15, 30} T_int: truth G_S non-increasing in tau (tolerance TOL_DOSE)
    keep1a = lambda g: longh(g) and bool(g.prior_correct.iloc[0])
    e1a = list(series(main, keep1a))
    done = [g for _, g in e1a if g.done.all()]
    unres = 1 - len(done) / len(e1a) if e1a else 0.0
    hits = [bool((np.diff(g.G_S.values) <= TOL_DOSE).all()) for g in done]
    v = float(np.mean(hits)) if done else None
    p1a = dict(eligible=len(e1a), n=len(done), unresolved_share=unres, value=v, threshold=0.90,
               regimes=len({k[:2] for k, _ in e1a}), verdict=verdict(len(done), unres, v, 0.90))
    # L75-1b prior wrong, h in {7, 15, 30} T_int, tau = 10 T_int, rows with z_pred1 >= 0.1: truth G_S > 0
    e1b = main[(main.h_mult >= 7) & ~main.prior_correct.astype(bool) & np.isclose(main.tau_mult, 10.0) & (main.z_pred1 >= 0.1)]
    d1b = e1b[e1b.done]
    unres = float((~e1b.done).mean()) if len(e1b) else 0.0
    v = float((d1b.G_S > 0).mean()) if len(d1b) else None
    p1b = dict(eligible=len(e1b), n=len(d1b), unresolved_share=unres, value=v, threshold=0.90,
               regimes=int(e1b.id.nunique()), verdict=verdict(len(d1b), unres, v, 0.90))
    old_rule = list(series(main, lambda g: longh(g) and (g.z_pred1 < -0.5).all()))
    od = [g for _, g in old_rule if g.done.all()]
    res['L75-1'] = dict(label='onset (zero-fit báo trước)', parts={'1a prior đúng': p1a, '1b prior sai': p1b},
                        report_only={'quy tắc cũ (z_pred1 < -0,5 ở cả 8 τ)': dict(
                            eligible=len(old_rule), n=len(od),
                            value=float(np.mean([(np.diff(g.G_S.values) <= TOL_DOSE).all() for g in od])) if od else None)},
                        verdict=combine([p1a, p1b]))
    # L75-2 onset at every tau: |G_S - z_pred1| <= 0.1 pp, per tau group x h multiple {7, 15, 30}
    parts, report = {}, {}
    for gname, taus in TAU_GROUPS.items():
        for hm, thr in ((7.0, 0.90), (15.0, 0.95), (30.0, 0.95)):
            e = main[main.tau_mult.isin(taus) & np.isclose(main.h_mult, hm)]
            unres = float((~e.done).mean()) if len(e) else 0.0
            d = e[e.done]
            ok = (d.G_S - d.z_pred1).abs() <= 0.1
            v = float(ok.mean()) if len(d) else None
            big = d.z_pred1.abs() >= 0.5
            parts[f'{gname} h={hm:g}T'] = dict(n=len(d), eligible=len(e), unresolved_share=unres, value=v, threshold=thr,
                                               verdict=verdict(len(d), unres, v, thr),
                                               report_big_z=dict(n=int(big.sum()), value=float(ok[big].mean()) if big.any() else None))
        e = main[main.tau_mult.isin(taus) & np.isclose(main.h_mult, 3.0)]
        d = e[e.done]
        report[f'{gname} h=3T'] = dict(n=len(d), value=float(((d.G_S - d.z_pred1).abs() <= 0.1).mean()) if len(d) else None)
    res['L75-2'] = dict(label='onset', parts=parts, report_only=report, verdict=combine(list(parts.values())))
    # R-a report only: help band (sobol stratum 'band'), truth G_S non-decreasing in tau
    band = main[main.stratum == 'band'] if 'stratum' in main else main.iloc[0:0]
    bd = [g for _, g in series(band, lambda g: True) if g.done.all()]
    res['R-a'] = dict(label='chỉ báo', n=len(bd), value=float(np.mean([(np.diff(g.G_S.values) >= -TOL_DOSE).all() for g in bd])) if bd else None,
                      verdict='REPORT')
    # L75-3 model right: S non-decreasing in tau; denominator = series with amplitude >= AMP_MIN (mentor §3a)
    e3 = list(series(main, lambda g: True))
    done3 = [(k, g) for k, g in e3 if g.done.all()]
    unres = 1 - len(done3) / len(e3) if e3 else 0.0
    cls = {k: s_class(g.S.values) for k, g in done3}
    scored = [k for k, c in cls.items() if c != 'flat']
    v = float(np.mean([cls[k] == 'pass' for k in scored])) if scored else None
    drops = {k: float(-np.diff(g.S.values).max()) for k, g in done3 if cls[k] == 'fail'}
    hm = {k: float(g.h_mult.iloc[0]) for k, g in done3}
    by_h = {}
    for h in sorted(set(hm.values())):
        ks = [k for k in scored if hm[k] == h]
        by_h[f'{h:g}T'] = dict(n=len(ks), flat=sum(1 for k in cls if hm[k] == h and cls[k] == 'flat'),
                               value=float(np.mean([cls[k] == 'pass' for k in ks])) if ks else None)
    res['L75-3'] = dict(label='rủi ro', eligible=len(e3), resolved=len(done3), unresolved_share=unres,
                        flat_trivial_pass=sum(c == 'flat' for c in cls.values()), n=len(scored),
                        regimes=len({k[:2] for k in scored}), value=v, threshold=0.90,
                        verdict=verdict(len(scored), unres, v, 0.90),
                        report_only=dict(by_h=by_h, violations_gt_0p1=sorted(
                            [dict(series=list(k), max_drop=d) for k, d in drops.items() if d > 0.1], key=lambda r: -r['max_drop'])))
    # L75-4 band edge on the frozen eligible x-slice series (mentor §3b): |edge(truth) - edge(z_pred1)| <= TOL_EDGE
    if elig is None:
        elig = pd.read_csv(OUT / 'l75' / 'L75_4_ELIGIBILITY.csv')
    ok_set = {(r.family, float(r.tau_mult)) for r in elig.itertuples() if bool(r.eligible)}
    xs = m[m.stage == 'xs']
    scored4, other4, unres_n = [], [], 0
    for (fam, tm), g in xs.groupby(['family', 'tau_mult']):
        xz = x_edge(g.x.values, g.z_pred1.values)
        near = g[(g.x > 0) & (g.x <= (xz if xz is not None else 0) + 0.25)]
        if (fam, float(tm)) not in ok_set:
            d = g[g.done & (g.x > 0)]
            other4.append(dict(family=fam, tau_mult=tm, x_edge_zf=xz, max_G_S_xpos=float(d.G_S.max()) if len(d) else None,
                               x_edge_truth=x_edge(g[g.done].x.values, g[g.done].G_S.values) if g.done.any() else None))
            continue
        if not near.done.all():
            unres_n += 1
            scored4.append(dict(family=fam, tau_mult=tm, x_edge_zf=xz, x_edge_truth=None, unresolved=True))
            continue
        xt = x_edge(g[g.done].x.values, g[g.done].G_S.values)
        scored4.append(dict(family=fam, tau_mult=tm, x_edge_zf=xz, x_edge_truth=xt, unresolved=False,
                            pass_=xt is not None and abs(xt - xz) <= TOL_EDGE))
    ok4 = [r for r in scored4 if not r['unresolved']]
    unres = unres_n / len(scored4) if scored4 else 0.0
    passing = sum(r['pass_'] for r in ok4)
    need = int(np.ceil(0.9 * len(ok4))) if ok4 else None
    v4 = 'INCONCLUSIVE' if (unres > UNRES_MAX or len(ok4) < N_MIN_L754) else ('PASS' if passing >= need else 'FAIL')
    res['L75-4'] = dict(label='rủi ro', eligible=len(ok_set), scored=len(ok4), passing=passing, need=need,
                        unresolved_share=unres, n_min=N_MIN_L754, series=scored4, report_only=other4, verdict=v4)
    return res


def d22_report(out=OUT):
    """Report only (separate D22 stage): backlog share F / G_S on truth harm rows (G_S < -0.5) by tau multiple, and
    the share of harm rows with F < 0. Never a verdict."""
    rows = []
    for st in ('sobol', 'old'):
        cases = {c['id']: c for c in json.loads((out / 'cases_l75' / f'{st}.json').read_text())}
        for f in sorted((out / 'runs_l75_d22' / st).glob('*.json')):
            d = json.loads(f.read_text())
            if d['status'] != 'COMPLETED':
                rows.append(dict(status=d['status']))
                continue
            tm = T5.tau_grid_map(cases[d['id']], st).get(d['tau'])
            for r in d['h']:
                if 'd22' in r:
                    rows.append(dict(status='COMPLETED', tau_mult=tm, G_S=r['G_S'], F=r['d22']['F'], flags=r.get('flags', [])))
    df = pd.DataFrame(rows)
    if df.empty:
        return dict(label='chỉ báo', units=0)
    done = df[df.status == 'COMPLETED']
    harm = done[(done.G_S < -0.5) & done.tau_mult.notna()]
    by = {f'{t:g}': dict(n=len(g), median_F_over_G_S=float((g.F / g.G_S).median()), share_F_neg=float((g.F < 0).mean()))
          for t, g in harm.groupby('tau_mult')}
    return dict(label='chỉ báo', rows=len(done), unresolved_rows=int((df.status != 'COMPLETED').sum()),
                flagged_rows=int(done.flags.map(len).gt(0).sum()), harm_by_tau=by)


def main():
    m = load()
    res = score(m)
    if (OUT / 'runs_l75_d22').exists():
        res['D22'] = dict(d22_report(), verdict='REPORT')
    units = m.drop_duplicates(['stage', 'id', 'tau']).unit_status.value_counts().to_dict()
    verdicts = {k: v['verdict'] for k, v in res.items() if v['verdict'] != 'REPORT'}
    res['counts'] = dict(unit_status=units, verdicts=verdicts, PASS=sum(v == 'PASS' for v in verdicts.values()),
                         FAIL=sum(v == 'FAIL' for v in verdicts.values()),
                         INCONCLUSIVE=sum(v == 'INCONCLUSIVE' for v in verdicts.values()))
    (OUT / 'score_l75.json').write_text(json.dumps(res, indent=1, default=str) + '\n')
    print(res['counts'])


if __name__ == '__main__':
    main()
