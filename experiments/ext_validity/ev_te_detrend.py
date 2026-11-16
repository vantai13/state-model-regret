"""Doan Van Tai — EV-TE Arm R-DT: backlog integral time of the unpredictable part of real Abilene traffic.

Exploratory. Specification: results/ext_validity/ev_te/arm_r_detrend/CARD.md, committed (ecb0f9a3) before any
detrended number was computed. Written by Claude on 16/11/2026 because Codex hit its usage limit; it reuses
ev_te_trace (loader, replay, routing), ev_te (network preparation, T_int estimator) unchanged.
Units as Arm R: rates Mb/min after scaling, queues Mb, time in minutes, 5-min bins.
"""
import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np

from experiments.ext_validity import ev_te as S
from experiments.ext_validity import ev_te_trace as R

OUT = S.OUT / 'arm_r_detrend'
BIN = R.BIN                      # minutes
SLOTS = 288                      # 5-min slots per day
WINDOWS = {'1d': 288, '2d': 576, '4d': 1152}
H_MIN = (5, 15, 30, 60)
ARM_R_V2_TINT = {('R1', .8): 283.733817565, ('R1', .9): 438.891423818}   # CARD reproduction targets


def profile(rates, times, mask):
    """Per-OD mean by (weekday/weekend, 5-min slot of day) over `mask` bins, then a centered circular 5-slot average."""
    slot = np.array([t.hour * 12 + t.minute // 5 for t in times])
    wkend = np.array([t.weekday() >= 5 for t in times], dtype=int)
    prof = np.full((2, SLOTS, rates.shape[1]), np.nan)
    for w in (0, 1):
        for s in range(SLOTS):
            sel = mask & (wkend == w) & (slot == s)
            if sel.any():
                prof[w, s] = np.nanmean(rates[sel], axis=0)
        fill = np.nanmean(prof[w], axis=0)          # an empty slot (never expected) gets the day-type mean
        prof[w] = np.where(np.isnan(prof[w]), fill, prof[w])
    smooth = np.stack([np.mean([np.roll(prof[w], -k, axis=0) for k in range(-2, 3)], axis=0) for w in (0, 1)])
    return smooth, slot, wkend


def residual(rates, prof, slot, wkend, dbar, kind):
    """Additive: d - P + dbar, clipped at 0. Multiplicative: dbar * d / max(P, 0.01 dbar) (0 where dbar = 0)."""
    p = prof[wkend, slot]
    if kind == 'additive':
        out = np.maximum(rates - p + dbar, 0.)
    elif kind == 'multiplicative':
        den = np.maximum(p, .01 * dbar)
        out = np.zeros_like(rates)
        np.divide(dbar * rates, den, out=out, where=den > 0)
    else:
        raise ValueError(kind)
    out[np.isnan(rates)] = np.nan
    return out


def windows(valid, length):
    """All non-overlapping contiguous valid windows of `length` bins, left-aligned within each valid run."""
    padded = np.r_[False, valid, False].astype(int)
    starts, ends = np.flatnonzero(np.diff(padded) == 1), np.flatnonzero(np.diff(padded) == -1)
    out = []
    for s, e in zip(starts, ends):
        out += [slice(int(s + i * length), int(s + (i + 1) * length)) for i in range((e - s) // length)]
    return out


def tint_minutes(series):
    value, censored, error = S.estimate_tint(np.asarray(series, float), BIN)
    return dict(T_int=value, censored=bool(censored), error=error)


def summarize(vals):
    ok = [v['T_int'] for v in vals if v['T_int'] is not None and not v['censored']]
    return dict(n=len(vals), n_uncensored=len(ok), n_censored=sum(v['censored'] for v in vals),
                median=float(np.median(ok)) if ok else None, min=min(ok) if ok else None, max=max(ok) if ok else None)


def analyze(scaled_all, train, valid, prepared, managed):
    """Replay under Stay on training bins (as Arm R train) and measure T_int on windows of the backlog and load."""
    incidence, cap = R.route_arrays(prepared, managed)
    cap = cap * 60
    maxima = np.max([np.nanmax(scaled_all @ route.T, axis=0) for route in incidence], axis=0)
    active = maxima > cap
    relevant = np.any(incidence[:, active] != 0, axis=(0, 1))
    inc, cp, rr = incidence[:, active][:, :, relevant], cap[active], scaled_all[:, relevant]
    vt = valid[train]
    q = R.replay_stay(rr[train], inc[0], cp, vt)
    total = q.sum(axis=1)
    p_pos = float(np.mean(total[vt] > 0))
    links = [e['id'] for e in prepared['links']]
    b = links.index(prepared['bottleneck'])
    load = scaled_all[train] @ incidence[0][b]
    res = dict(active_links=int(active.sum()), P_Q_positive=p_pos)
    segs = {name: windows(vt, n) for name, n in WINDOWS.items()}
    segs['longest'] = [R.longest_valid(vt)]
    for what, series in (('backlog', total), ('bottleneck_load', load)):
        per = {}
        for name, ws in segs.items():
            vals = []
            for w in ws:
                try:
                    vals.append(tint_minutes(series[w]))
                except ValueError as error:      # zero variance (no backlog in the window)
                    vals.append(dict(T_int=None, censored=True, error=str(error)))
            per[name] = dict(summary=summarize(vals), windows=[dict(start=w.start, stop=w.stop, **v) for w, v in zip(ws, vals)])
        res[what] = per
    return res


def reading_rule(results):
    """CARD reading rule, applied mechanically to the primary variant (additive, R1, both rho, longest segment)."""
    checks = {}
    for rho in (.8, .9):
        raw = results[f'raw|R1|{rho}']['backlog']['longest']['summary']['median']
        target = ARM_R_V2_TINT[('R1', rho)]
        checks[f'raw_reproduction_{rho}'] = dict(value=raw, target=target,
                                                ok=raw is not None and abs(raw - target) / target <= .01)
    if not all(c['ok'] for c in checks.values()):
        return 'PIPELINE_MISMATCH', checks
    tl, t1 = {}, {}
    for rho in (.8, .9):
        r = results[f'additive|R1|{rho}']
        if r['P_Q_positive'] < .01:
            return 'NOT_EVALUABLE', dict(checks, reason=f'P(Q>0) < 1% at rho {rho}')
        tl[rho] = r['backlog']['longest']['summary']['median']
        t1[rho] = r['backlog']['1d']['summary']['median']
    checks.update(T_longest=tl, T_1d_median=t1)
    if any(v is None for v in tl.values()):
        return 'NOT_EVALUABLE', dict(checks, reason='censored longest segment')
    growth = {rho: (tl[rho] / t1[rho] if t1[rho] else None) for rho in tl}
    checks['longest_over_1d'] = growth
    if any(v >= 60 for v in tl.values()) or any(g is not None and g > 2 for g in growth.values()):
        return 'BOUNDARY', checks
    if all(v <= 15 for v in tl.values()) and all(g is not None and .5 <= g <= 2 for g in growth.values()):
        return 'REACHABLE', checks
    return 'INTERMEDIATE', checks


def run(out=OUT):
    S.new(out / 'results.json', out / 'summary.csv')
    clock = time.process_time()
    net, times, rates, valid, train, parsing = R.load_trace()
    ids = [d['id'] for d in net['demands']]
    means = rates[valid & train].mean(axis=0)
    prof, slot, wkend = profile(rates, times, valid & train)
    variants = dict(raw=rates,
                    additive=residual(rates, prof, slot, wkend, means, 'additive'),
                    multiplicative=residual(rates, prof, slot, wkend, means, 'multiplicative'))
    results, rows = {}, []
    for rho in (.8, .9):
        prepared = S.prepare_network(net, rho, dict(zip(ids, means)))
        for set_i in (1, 4):
            managed = prepared['managed_sets'][set_i - 1]
            for kind, demand in variants.items():
                r = analyze(demand * prepared['alpha'] * 60, train, valid, prepared, managed)
                key = f'{kind}|R{set_i}|{rho}'
                results[key] = dict(variant=kind, set=f'R{set_i}', rho=rho, managed=managed, alpha=prepared['alpha'], **r)
                for what in ('backlog', 'bottleneck_load'):
                    for name in ('1d', '2d', '4d', 'longest'):
                        sm = r[what][name]['summary']
                        rows.append(dict(variant=kind, set=f'R{set_i}', rho=rho, series=what, window=name,
                                         P_Q_positive=r['P_Q_positive'], **sm))
    outcome, checks = reading_rule(results)
    implied = {k: {str(h): (h / v['backlog']['longest']['summary']['median']
                            if v['backlog']['longest']['summary']['median'] else None) for h in H_MIN}
               for k, v in results.items()}
    meta = dict(card='results/ext_validity/ev_te/arm_r_detrend/CARD.md (ecb0f9a3)', outcome=outcome, checks=checks,
                implied_h_over_T_int=implied, profile='288 slots x weekday/weekend, 5-slot circular MA, train valid bins',
                train_valid_bins=int((valid & train).sum()), CPU_seconds=time.process_time() - clock,
                parsing={k: v for k, v in parsing.items() if not isinstance(v, list)})
    out.mkdir(parents=True, exist_ok=True)
    (out / 'results.json').open('x').write(json.dumps(dict(meta=meta, results=results), indent=1, default=float) + '\n')
    with (out / 'summary.csv').open('x', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(json.dumps(dict(outcome=outcome, checks=checks, CPU_seconds=meta['CPU_seconds']), indent=1, default=float))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('run',))
    p.parse_args(argv)
    run()


if __name__ == '__main__':
    main()
