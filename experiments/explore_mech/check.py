"""Doan Van Tai — score the pre-written predictions (PREDICTIONS_x.md P1-P5, PREDICTIONS_collapse.md C1-C4)
against the slice rows [EXPLORATION ONLY; AI (Claude) theo ủy quyền]. Thresholds are copied from those files
and must not be edited after the slice rows exist.

  python -m experiments.explore_mech.check   -> results/explore_mech/checks.json (+ printed table)
"""
import json
import math

import numpy as np
import pandas as pd

from experiments.explore_mech.analyze import load
from experiments.explore_mech.scan import OUT


def frame(stage):
    rows, unresolved = load([stage])
    d = pd.DataFrame(rows)
    if len(d):
        d['delta'] = d.lamB - d.lamA
    return d, unresolved


def crossing(xs, ys, level, log=False):
    """first x where ys crosses `level` (either direction), linear (or log-linear) interpolation; None if none"""
    for (x0, y0), (x1, y1) in zip(zip(xs, ys), list(zip(xs, ys))[1:]):
        if (y0 - level) * (y1 - level) <= 0 and y0 != y1:
            t = (level - y0) / (y1 - y0)
            return 10 ** (math.log10(x0) + t * (math.log10(x1) - math.log10(x0))) if log else x0 + t * (x1 - x0)
    return None


def check_x(h, x):
    out = {}
    both = pd.concat([h, x])
    big = both[(both.h_kappa >= 50 - 1e-9) & (both.delta.abs() >= .5)]
    bad = big[((big.delta < 0) & (big.sw_true_cur < .9)) | ((big.delta > 0) & (big.sw_true_cur > .1))]
    out['P1'] = dict(n=len(big), violations=bad[['id', 'delta', 'h_kappa', 'sw_true_cur']].to_dict('records'),
                     pass_=len(bad) == 0)
    xs, cuts, viol = {}, {}, []
    for (u, hk), g in x.groupby(['u', 'h_kappa']):
        g = g.sort_values('x')
        cut = crossing(list(g.x), list(g.sw_mean_old), .5)
        cuts[f'u={u:g},h/k={hk:g}'] = cut
        lo, hi = g[(g.x >= 0) & (g.x <= .25)], g[g.x >= .75]
        viol += list(lo[lo.sw_mean_old < .9].id) + list(hi[hi.sw_mean_old > .1].id)
        xs[(u, hk)] = cut
    order = all(xs.get((2.0, hk)) is not None and xs.get((1.0, hk)) is not None and xs[(2.0, hk)] <= xs[(1.0, hk)] + 1 / 16
                for hk in sorted(set(x.h_kappa)))
    inrange = all(c is not None and .3 <= c <= .6 for c in cuts.values())
    out['P2'] = dict(crossings=cuts, plateau_violations=viol, order_u2_le_u1=order, crossings_in_range=inrange,
                     pass_=not viol and order and inrange)
    viol3 = []
    for (u, hk), g in x.groupby(['u', 'h_kappa']):
        cut, step = xs[(u, hk)], 1 / (8 * u)
        if cut is None:
            continue
        neg = g[g.Gamma < 0]
        viol3 += [dict(id=r.id, x=r.x, why='Gamma<0 outside (0, x*)') for r in neg.itertuples()
                  if not (0 < r.x < cut + step)]
        out_band = g[((g.x < 0) | (g.x > cut + step)) & (g.delta.abs() >= .5)]
        viol3 += [dict(id=r.id, x=r.x, why='G_S>=0 outside band') for r in out_band.itertuples() if r.G_S >= 0]
    out['P3'] = dict(violations=viol3, pass_=not viol3)
    z = both[both.delta == 0]
    bad4 = z[(z.G_S < -.1) | (z.Gamma < -.1 * (z.S + z.M))]
    out['P4'] = dict(n=len(z), violations=list(bad4.id), pass_=len(z) > 0 and len(bad4) == 0)
    onset = {}
    for (kappa, dl), g in h[h.delta != 0].groupby(['kappa', 'delta']):
        g = g.sort_values('h_kappa')
        final = np.sign(g.G_S.iloc[-1])
        same = list(np.sign(g.G_S) == final)
        k = len(same)
        while k > 0 and same[k - 1]:
            k -= 1
        onset[(kappa, dl)] = float(g.h_kappa.iloc[k]) if k < len(g) else None
    ok5 = []
    for kappa in sorted(set(h.kappa)):
        o = lambda dl: onset.get((kappa, dl))
        ok5.append(None not in (o(-.25), o(-.5)) and o(-.25) >= o(-.5))
        ok5.append(None not in (o(.25), o(.5), o(1.0)) and o(.25) >= max(o(.5), o(1.0)))
    out['P5'] = dict(onset={f'kappa={k:g},delta={dl:g}': v for (k, dl), v in onset.items()}, pass_=all(ok5),
                     n_hslice=len(h))
    return out


def check_collapse(p):
    out, series = {}, {}
    for (dl, u, kappa), g in p[p.delta != 0].groupby(['delta', 'u', 'kappa']):
        g = g.sort_values('h_kappa')
        g = g[g.S + g.M >= .5]
        P = list(g.h_kappa * abs(dl))
        cut = crossing(P, list(g.R), .5, log=True)
        series[(dl, u, kappa)] = cut
    out['C1'] = dict(crossings={f'delta={k[0]:g},u={k[1]:g},kappa={k[2]:g}': v for k, v in series.items()},
                     pass_=all(5 <= v <= 30 for v in series.values() if v is not None),
                     n_with_crossing=sum(v is not None for v in series.values()), n_series=len(series))
    ratios, ok = {}, []
    for (u, kappa) in sorted({(k[1], k[2]) for k in series}):
        pts = [(abs(dl), v) for (dl, uu, kk), v in series.items() if (uu, kk) == (u, kappa) and v is not None]
        if len({a for a, _ in pts}) < 2:
            continue
        Pr = max(v for _, v in pts) / min(v for _, v in pts)
        Hr = max(v / a for a, v in pts) / min(v / a for a, v in pts)
        ratios[f'u={u:g},kappa={kappa:g}'] = dict(P_ratio=Pr, hk_ratio=Hr, n=len(pts))
        ok.append(Pr <= 2.5 and Hr >= 2.5)
    out['C2'] = dict(ratios=ratios, pass_=bool(ok) and all(ok))
    z = p[p.delta == 0]
    bad = z[(z.M > .3) | ((z.S + z.M >= .5) & (z.R < .9))]
    out['C3'] = dict(n=len(z), violations=bad[['id', 'M', 'R', 'h_kappa']].to_dict('records'), pass_=len(z) > 0 and len(bad) == 0)
    return out


def main():
    res = {}
    h, uh = frame('hslice')
    x, ux = frame('xslice')
    p, up = frame('pslice')
    res['unresolved'] = dict(hslice=uh, xslice=ux, pslice=up)
    res['rows'] = dict(hslice=len(h), xslice=len(x), pslice=len(p))
    if len(h) and len(x):
        res.update(check_x(h, x))
    if len(p):
        res.update(check_collapse(p))
    (OUT / 'checks.json').write_text(json.dumps(res, indent=1, default=str) + '\n')
    for k, v in res.items():
        print(k, v.get('pass_', '') if isinstance(v, dict) else '', '' if isinstance(v, dict) and 'pass_' in v else v)


if __name__ == '__main__':
    main()
