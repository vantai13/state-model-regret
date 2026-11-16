"""Doan Van Tai — EV-TE Arm R-DT post-hoc diagnostics (Claude, 16/11/2026). POST-HOC, exploratory.

The card verdict (BOUNDARY, commit 387aa638) is unchanged. This script asks two follow-up questions:
1. Why does the residual T_int grow with the window? Day-to-day level changes (diagnostic: dispersion of daily
   mean bottleneck load; autocorrelation of the residual bottleneck load at 1 h, 6 h, 1 d, 3 d lags).
2. Which forecast would make hour-scale decisions reach h/T_int >= 4? Residuals around adaptive forecasts:
   trailing means over 1 h, 3 h, 6 h and 24 h (previous bins only), and the time-of-day profile rescaled by the
   previous day's level. Same replay, estimator and windows as the card.
"""
import json
import time

import numpy as np

from experiments.ext_validity import ev_te as S
from experiments.ext_validity import ev_te_detrend as D
from experiments.ext_validity import ev_te_trace as R

OUT = D.OUT / 'posthoc'


def trailing_mean(rates, valid, w):
    """Mean of the previous w valid bins (excluding the current bin), per OD; NaN where none."""
    x = np.where(valid[:, None], rates, 0.)
    n = valid.astype(float)[:, None] * np.ones((1, rates.shape[1]))
    cx = np.vstack([np.zeros((1, x.shape[1])), np.cumsum(x, axis=0)])
    cn = np.vstack([np.zeros((1, n.shape[1])), np.cumsum(n, axis=0)])
    idx = np.arange(len(rates))
    lo = np.maximum(idx - w, 0)
    s, c = cx[idx] - cx[lo], cn[idx] - cn[lo]
    out = np.full_like(rates, np.nan)
    np.divide(s, c, out=out, where=c > 0)
    return out


def acf_at(series, lags):
    z = np.asarray(series, float) - np.mean(series)
    v = np.mean(z * z)
    return {str(l): float(np.mean(z[:-l] * z[l:]) / v) if v > 0 and l < len(z) else None for l in lags}


def main():
    clock = time.process_time()
    net, times, rates, valid, train, _ = R.load_trace()
    ids = [d['id'] for d in net['demands']]
    tv = valid & train
    dbar = rates[tv].mean(axis=0)
    prof, slot, wkend = D.profile(rates, times, tv)
    variants = {'additive_profile': D.residual(rates, prof, slot, wkend, dbar, 'additive')}
    for name, w in (('trailing_1h', 12), ('trailing_3h', 36), ('trailing_6h', 72), ('trailing_24h', 288)):
        m = trailing_mean(rates, valid, w)
        variants[name] = np.where(np.isnan(m), np.nan, np.maximum(rates - m + dbar, 0.))
    # profile rescaled by the previous day's level (per OD): P(t) * mean(d over previous 288 bins) / mean(P over them)
    p = prof[wkend, slot]
    lvl = trailing_mean(rates, valid, 288) / np.where(trailing_mean(p, valid, 288) > 0, trailing_mean(p, valid, 288), np.nan)
    variants['profile_x_yesterday'] = np.where(np.isnan(lvl), np.nan, np.maximum(rates - p * lvl + dbar, 0.))
    out = {}
    for rho in (.8, .9):
        prepared = S.prepare_network(net, rho, dict(zip(ids, dbar)))
        managed = prepared['managed_sets'][0]
        links = [e['id'] for e in prepared['links']]
        incidence, _ = R.route_arrays(prepared, managed)
        b = links.index(prepared['bottleneck'])
        for name, dem in [('raw', rates)] + list(variants.items()):
            ok = valid & ~np.isnan(dem).any(axis=1)
            scaled = np.where(ok[:, None], dem, np.nan) * prepared['alpha'] * 60
            r = D.analyze(scaled, train, ok, prepared, managed)
            load = (scaled[train] @ incidence[0][b])
            seg = R.longest_valid(ok[train])
            days = [load[seg][i:i + 288].mean() for i in range(0, seg.stop - seg.start - 287, 288)]
            out[f'{name}|{rho}'] = dict(
                P_Q_positive=r['P_Q_positive'],
                T_backlog={k: r['backlog'][k]['summary'] for k in ('1d', '2d', '4d', 'longest')},
                T_load={k: r['bottleneck_load'][k]['summary'] for k in ('1d', 'longest')},
                acf_load=acf_at(load[seg], (12, 72, 288, 864)),
                daily_mean_load_cv=float(np.std(days) / np.mean(days)) if days else None)
            s = out[f'{name}|{rho}']
            print(f"{name:20s} rho={rho} P(Q>0)={s['P_Q_positive']:.3f} T_backlog 1d={s['T_backlog']['1d']['median']} "
                  f"longest={s['T_backlog']['longest']['median']} | acf(1h,6h,1d,3d)={[round(v, 2) if v is not None else None for v in s['acf_load'].values()]} "
                  f"dayCV={s['daily_mean_load_cv']}", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'posthoc.json').write_text(json.dumps(dict(note=__doc__, CPU_seconds=time.process_time() - clock, results=out),
                                                 indent=1, default=float) + '\n')


if __name__ == '__main__':
    main()
