"""Doan Van Tai — EV-D independent FIFO DES (seconds, packets, packet-seconds).

CLI: python -m experiments.ext_validity.packet {train,test} --cases cases.json
     --out DIR [--train TRAIN_DIR --workers N]
Cases: JSON list of {id, cls, lamA, lamB, u, params, seed=1, warmup=1000,
train_T=20000, sample_dt=.1, n_inst=20000, gap=0, batches=40, h_mult=[1,3,10]}.
Rates are numbers; params are shared by independent A/B sources. mmpp2: kappa;
onoff_exp: K,f,T_c,b; onoff_pareto: same plus alpha,cap (>1). Stable means
lamA+u,lamB+u < 10 required. Train uses seed; test uses seed+1000000.
ratefluid uses background counts in [t_info-W,t_info], W=params.rate_window
(default T_r). T_r=T_c*f*(1-f), or kappa/2 for mmpp2. This exponential
relaxation is a deliberate twin mis-specification for Pareto sources.
Nowcast stale pipelines use per-path OLS fit on train-seed stationary instants:
backlog from (1, stale backlog, stale rate), rate from (1, stale rate, stale
backlog). Only predicted backlog is clipped at zero; R² is before clipping.
Train emits stationary means/shares, no branch costs or D. Test is write-once.
--timing-only on test measures the workload without emitting scores.
No scientific run is started on import. No CTMC dependency.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
import hashlib
import json
from pathlib import Path
import re
import time

import numpy as np

MU, TAU = 10., 1.


def pareto_bounds(alpha, cap):
    """Bounded Pareto density x^(-alpha-1): mean 1, upper endpoint cap."""
    if alpha <= 1 or cap <= 1:
        raise ValueError('alpha and cap must exceed 1')
    lo, hi = 0., 1.
    for _ in range(60):
        x = (lo + hi) / 2
        mean = alpha / (alpha - 1) * x * (1 - (x / cap)**(alpha - 1)) / (1 - (x / cap)**alpha)
        lo, hi = (x, hi) if mean < 1 else (lo, x)
    return (lo + hi) / 2, cap


def durations(mean, params, rng, size, residual=False):
    """Exact stationary residual: uniform point in a length-biased interval.

    Exponential residuals remain exponential. For bounded Pareto the length-
    biased density is x^(-alpha), inverted analytically; no approximation.
    """
    if 'alpha' not in params:
        return rng.exponential(mean, size)
    a = params['alpha']
    lo, hi = pareto_bounds(a, params['cap'])
    power = 1 - a if residual else -a
    z = (lo**power + rng.random(size) * (hi**power - lo**power))**(1 / power)
    return mean * z * (rng.random(size) if residual else 1)


def poisson(rate, T, rng):
    return np.sort(rng.uniform(0, T, rng.poisson(rate * T)))


def arrivals(cls, lam, params, T, rng):
    """Sorted stationary arrivals in [0,T]; independent sources per call."""
    if T < 0 or lam < 0 or cls not in ('mmpp2', 'onoff_exp', 'onoff_pareto'):
        raise ValueError('invalid arrival class, rate or duration')
    if cls == 'mmpp2':
        K, f, tc, b, law = 1, .5, 2 * params['kappa'], lam - 6, {}
    else:
        K, f, tc, b = (params[k] for k in ('K', 'f', 'T_c', 'b'))
        law = params if cls == 'onoff_pareto' else {}
    if K != int(K) or K < 1 or not 0 < f < 1 or tc <= 0 or not 0 <= b <= lam:
        raise ValueError('invalid source parameters')
    peak = (lam - b) / (K * f)
    pieces = [poisson(b, T, rng)]
    for _ in range(int(K)):
        on = bool(params['initial_mode']) if 'initial_mode' in params else rng.random() < f
        start = 0.
        end = float(durations((f if on else 1-f) * tc, law, rng, 1, True)[0])
        starts, ends = [], []
        if on:
            starts.append(np.array([0.])); ends.append(np.array([min(end, T)]))
        start, on = end, not on
        while start < T:
            size = max(128, int(2 * (T - start) / tc + 32))
            states = (np.arange(size) % 2 == 0) == on
            ds = durations(f * tc, law, rng, size)
            ds[~states] = durations((1-f) * tc, law, rng, (~states).sum())
            stops = start + np.cumsum(ds)
            begins = np.r_[start, stops[:-1]]
            keep = states & (begins < T)
            starts.append(begins[keep]); ends.append(np.minimum(stops[keep], T))
            start, on = stops[-1], on if size % 2 == 0 else not on
        if starts:
            left, right = np.concatenate(starts), np.concatenate(ends)
            counts = rng.poisson(peak * (right - left))
            pieces.append(np.repeat(left, counts) + rng.random(counts.sum()) * np.repeat(right-left, counts))
    return np.sort(np.concatenate(pieces))


def departures(times, services, initial=0.):
    """Vectorised Lindley recursion, last axis = ordered packets."""
    sums = np.cumsum(services, axis=-1)
    before = sums - services
    return sums + np.maximum(initial, np.maximum.accumulate(times - before, axis=-1))


def backlog(run, ts):
    return np.searchsorted(run[0], ts, side='right') - np.searchsorted(run[1], ts, side='right')


def long_run(case, action, T, rng):
    bg = [arrivals(case['cls'], case[k], case['params'], T, rng) for k in ('lamA', 'lamB')]
    flow = poisson(case['u'], T, rng)
    runs = []
    for j in range(2):
        ts = np.sort(np.r_[bg[j], flow]) if j == action else bg[j]
        runs.append((ts, departures(ts, rng.exponential(1/MU, ts.size))))
    return bg, runs


def long_run_crn(case, T, rng):
    """Claude (review, 14/11): both actions on the SAME background arrivals, managed-flow arrivals and per-packet
    service times (common random numbers), so the stationary difference s = r_Sw - r_St has low variance."""
    bg = [arrivals(case['cls'], case[k], case['params'], T, rng) for k in ('lamA', 'lamB')]
    flow = poisson(case['u'], T, rng)
    sbg = [rng.exponential(1/MU, b.size) for b in bg]
    sfl = rng.exponential(1/MU, flow.size)
    out = []
    for action in (0, 1):
        runs = []
        for j in range(2):
            if j == action:
                ts, sv = np.r_[bg[j], flow], np.r_[sbg[j], sfl]
                order = np.argsort(ts, kind='stable')
                ts, sv = ts[order], sv[order]
            else:
                ts, sv = bg[j], sbg[j]
            runs.append((ts, departures(ts, sv)))
        out.append(runs)
    return bg, out


def fluid_cost(q, load, h):
    """Closed form integral max(0,q+(load-MU)t), including nonnegative drift."""
    drift, q = load-MU, np.asarray(q)
    t = np.minimum(h, q/-drift) if drift < 0 else h
    return q*t + drift*t*t/2


def fluid_parts(q, lam, u, h, side):
    """Shifted per-path gaps; +/-u*h²/2 cancel. Exact saturated ties = 0."""
    q = np.asarray(q)
    correction = lambda load: (MU-load) / 2 * np.maximum(h-q/(MU-load), 0)**2
    v = correction(lam) - correction(lam+u)
    v = np.where(q == 0, u*h*h/2, v)
    return v if side == 0 else -v


def fluid_gap(q, case, h):
    return sum(fluid_parts(q[:, j], case[k], case['u'], h, j) for j, k in enumerate(('lamA', 'lamB')))


def rate_settings(case):
    p = case['params']
    tr = p['kappa']/2 if case['cls'] == 'mmpp2' else p['T_c']*p['f']*(1-p['f'])
    w = p.get('rate_window', tr)
    if not np.isfinite([tr, w]).all() or min(tr, w) <= 0:
        raise ValueError('relaxation time and rate_window must be finite and positive')
    return tr, w


def window_rate(bg, ts, w):
    """Background only, inclusive endpoints; reject incomplete lookback windows."""
    ts = np.asarray(ts)
    if not np.isfinite(w) or w <= 0 or np.any(ts < w):
        raise ValueError('invalid or incomplete rate window')
    return (np.searchsorted(bg, ts, side='right') - np.searchsorted(bg, ts-w, side='left')) / w


def _ratefluid_integrals(q, lam, rho, u, h, tr):
    """Return clipped cost and clipping correction to the uncut integral.

    Stable mean load: if rho<lam the drift increases but remains negative;
    otherwise it decreases. Bisect the zero after the (possibly t=0) peak.
    This implements max(0,q+C(t)), without restarting a queue after emptying.
    """
    d = lam+u-MU
    if d >= 0 or tr <= 0 or h < 0:
        raise ValueError('ratefluid requires stable mean load, positive T_r and h>=0')
    q, b = np.broadcast_arrays(np.asarray(q, dtype=float), np.asarray(rho)-lam)
    level = lambda t: q+d*t-b*tr*np.expm1(-t/tr)
    primitive = lambda t: q*t+d*t*t/2+b*tr*(t+tr*np.expm1(-t/tr))
    end = np.full(q.shape, h, dtype=float)
    cut = level(h) < 0
    lo = np.minimum(h, tr*np.log(np.maximum(b, -d)/(-d)))
    hi = end.copy()
    for _ in range(48):
        mid = (lo+hi)/2
        positive = level(mid) > 0
        lo, hi = np.where(positive, mid, lo), np.where(positive, hi, mid)
    end = np.where(cut, (lo+hi)/2, end)
    end = np.where((q == 0) & (d+b <= 0), 0., end)
    cost = primitive(end)
    return cost, cost-primitive(h)


def ratefluid_cost(q, lam, rho, u, h, tr):
    return _ratefluid_integrals(q, lam, rho, u, h, tr)[0]


def ratefluid_gap(q, rho, case, h):
    tr, _ = rate_settings(case)
    parts = []
    for j, k in enumerate(('lamA', 'lamB')):
        co, off = _ratefluid_integrals(q[:, j], case[k], rho[:, j], 0., h, tr)
        cn, on = _ratefluid_integrals(q[:, j], case[k], rho[:, j], case['u'], h, tr)
        v = np.where((co == 0) & (cn == 0), case['u']*h*h/2, off-on)
        parts.append(v if j == 0 else -v)
    # Uncut +/-u*h²/2 cancel analytically, preserving exact saturated ties.
    return parts[0]+parts[1]


def fit_nowcast(fresh, stale, rate_new, rate_old):
    """Train-only OLS; beta/gamma order matches the module docstring.

    R² is in-sample, not a validation score; None denotes constant targets.
    Rank-deficient designs use numpy's minimum-norm least-squares solution.
    """
    def ols(design, target):
        coef = np.linalg.lstsq(design, target, rcond=None)[0]
        sst = np.sum((target-target.mean())**2)
        r2 = float(1-np.sum((target-design@coef)**2)/sst) if sst > 0 else None
        return coef.tolist(), r2

    fitted = {}
    for j, path in enumerate(('A', 'B')):
        design = np.column_stack([np.ones(len(stale)), stale[:, j], rate_old[:, j]])
        beta, r2_backlog = ols(design, fresh[:, j])
        gamma, r2_rate = ols(design[:, [0, 2, 1]], rate_new[:, j])
        fitted[path] = dict(beta=beta, gamma=gamma, r2_backlog=r2_backlog, r2_rate=r2_rate)
    return fitted


def nowcast_inputs(stale, rate_old, fitted):
    """Apply frozen train coefficients; never refit on test instants."""
    beta = np.array([fitted[p]['beta'] for p in ('A', 'B')])
    gamma = np.array([fitted[p]['gamma'] for p in ('A', 'B')])
    q = np.maximum(0., beta[:, 0]+beta[:, 1]*stale+beta[:, 2]*rate_old)
    rho = gamma[:, 0]+gamma[:, 1]*rate_old+gamma[:, 2]*stale
    return q, rho


def nowcast_gaps(stale, rate_old, case, h, fitted, s_train):
    q, rho = nowcast_inputs(stale, rate_old, fitted)
    rate = ratefluid_gap(q, rho, case, h)
    return dict(fluid_nowcast=fluid_gap(q, case, h), ratefluid_nowcast=rate,
                ratefluid_nowcast_hybrid_train=rate+h*s_train)


def batch_stats(x, batches=40):
    x = np.asarray(x)
    if not 2 <= batches <= len(x) // 2:
        raise ValueError('need >=2 batches and >=2 observations per batch')
    means = np.array([v.mean() for v in np.array_split(x, batches)])
    return dict(mean=float(x.mean()), se=float(means.std(ddof=1) / np.sqrt(batches)))


def tint(x, dt):
    """Unbiased FFT autocovariance; trapezoids to linearly located first zero."""
    z = x - np.mean(x)
    cov = np.fft.irfft(abs(np.fft.rfft(z, n=2*len(z)))**2)[:len(z)//4]
    cov /= np.arange(len(z), len(z)-len(cov), -1)
    if cov[0] <= 0:
        raise ValueError('zero-variance train series')
    r = cov / cov[0]
    hits = np.flatnonzero(r <= 0)
    k = int(hits[0]) if hits.size else len(r)-1
    area = np.sum((r[:k-1] + r[1:k]) / 2) * dt
    area += .5 * r[k-1] * dt * (r[k-1]/(r[k-1]-r[k]) if hits.size else 1)
    return float(area), not bool(hits.size)


def train(case):
    clock = time.process_time()
    rng = np.random.default_rng(case.get('seed', 1))
    warm, T, dt = case.get('warmup', 1000.), case.get('train_T', 20000.), case.get('sample_dt', .1)
    _, w = rate_settings(case)
    warm = max(warm, w)  # Include the complete stale lookback before sampling.
    ts = np.arange(warm + TAU, warm + T, dt)
    means, fresh, stale = [], None, None
    bg, both = long_run_crn(case, warm+T, rng)          # Claude (review): CRN estimate of s
    for action in (0, 1):
        runs = both[action]
        qs = np.column_stack([backlog(r, ts) for r in runs])
        means.append(float(qs.sum(axis=1).mean()))
        if action == 0:
            fresh = qs
            stale = np.column_stack([backlog(r, ts-TAU) for r in runs])
            rate_new = np.column_stack([window_rate(a, ts, w) for a in bg])
            rate_old = np.column_stack([window_rate(a, ts-TAU, w) for a in bg])
    ti, censored = tint(fresh.sum(axis=1), dt)
    fitted = fit_nowcast(fresh, stale, rate_new, rate_old)
    shares = {str(m): dict(F_new=float((fluid_gap(fresh, case, m*ti)<0).mean()),
                          F_old=float((fluid_gap(stale, case, m*ti)<0).mean()),
                          F_new_rate=float((ratefluid_gap(fresh, rate_new, case, m*ti)<0).mean()),
                          F_old_rate=float((ratefluid_gap(stale, rate_old, case, m*ti)<0).mean()))
              for m in case.get('h_mult', [1,3,10])}
    for m in case.get('h_mult', [1,3,10]):
        shares[str(m)].update({f'F_old_{name}': float((gap<0).mean()) for name, gap in
                              nowcast_gaps(stale, rate_old, case, m*ti, fitted, means[1]-means[0]).items()})
    return dict(case=case, seed=case.get('seed', 1), mean_stay=means[0], mean_switch=means[1],
                s_train=means[1]-means[0], T_int=ti, T_int_censored=censored, shares=shares,
                nowcast=fitted,
                CPU=time.process_time()-clock)


def window(bg, ts, h):
    lo, hi = np.searchsorted(bg, ts, side='right'), np.searchsorted(bg, ts+h, side='right')
    widths = hi-lo
    ix = np.arange(int(widths.max(initial=0)))
    valid = ix[None, :] < widths[:, None]
    padded = np.r_[bg, np.inf]
    return np.where(valid, padded[np.minimum(lo[:, None]+ix, len(bg))]-ts[:, None], np.inf)


def lindley_cost(q, times, services, initial_services, h):
    """Integral n(t)dt = sum of each packet's residence before horizon h."""
    initial = np.cumsum(initial_services, axis=1)
    mask = np.arange(initial.shape[1])[None, :] < q[:, None]
    initial = np.where(mask, initial, 0.)
    work = initial.max(axis=1, initial=0.)
    deps = departures(times, services, work[:, None])
    future = np.where(np.isfinite(times), np.maximum(np.minimum(deps, h)-times, 0), 0.)
    return np.minimum(initial, h).sum(axis=1) + future.sum(axis=1)


def futures(q, ts, bg, case, h, rng):
    """Same bg/managed packet services and initial services in both actions."""
    n = len(ts)
    count = rng.poisson(case['u']*h, n)
    ix = np.arange(int(count.max(initial=0)))
    flow = np.where(ix < count[:, None], rng.uniform(0, h, (n,len(ix))), np.inf)
    fs = rng.exponential(1/MU, flow.shape)
    costs = np.zeros((n, 2))
    for j in (0, 1):
        at = window(bg[j], ts, h)
        sv = rng.exponential(1/MU, at.shape)
        init = rng.exponential(1/MU, (n,int(q[:, j].max(initial=0))))
        for action in (0, 1):
            t, s = (np.c_[at, flow], np.c_[sv, fs]) if j == action else (at, sv)
            order = np.argsort(t, axis=1, kind='stable')
            costs[:, action] += lindley_cost(q[:,j], np.take_along_axis(t,order,1),
                                             np.take_along_axis(s,order,1), init, h)
    return costs


def simulate(case, h, training, timing_only=False):
    clock = time.process_time()
    if 'nowcast' not in training:
        raise ValueError('missing nowcast coefficients; regenerate training with EV-D3')
    rng = np.random.default_rng(case.get('seed',1)+1000000)
    n, warm = case.get('n_inst',20000), case.get('warmup',1000.)
    _, w = rate_settings(case)
    warm = max(warm, w)
    # Claude (review): optional spacing in units of T_int; futures may overlap (unbiased; batch means for se)
    spacing = max(TAU, case['spacing_mult']*training['T_int']) if 'spacing_mult' in case else max(h+TAU, case.get('gap',0.))
    ts = warm+TAU+np.arange(n)*spacing
    bg, runs = long_run(case, 0, ts[-1]+h, rng)
    fresh = np.column_stack([backlog(r, ts) for r in runs])
    stale = np.column_stack([backlog(r, ts-TAU) for r in runs])
    costs = np.concatenate([futures(fresh[s:s+256], ts[s:s+256], bg, case, h, rng) for s in range(0,n,256)])
    d, stay = costs[:,1]-costs[:,0], costs[:,0]
    batches = case.get('batches',40)
    mm1 = lambda load: load/(MU-load)
    a,b,u = case['lamA'],case['lamB'],case['u']
    shifts = dict(fluid=0., hybrid_mm1=mm1(a)+mm1(b+u)-mm1(a+u)-mm1(b), hybrid_train=training['s_train'])
    go, gn, twins = fluid_gap(stale,case,h), fluid_gap(fresh,case,h), {}
    rate_old = np.column_stack([window_rate(a, ts-TAU, w) for a in bg])
    ro = ratefluid_gap(stale, rate_old, case, h)
    rn = ratefluid_gap(fresh, np.column_stack([window_rate(a, ts, w) for a in bg]), case, h)
    maps = {name: (go+h*shift, gn+h*shift) for name, shift in shifts.items()}
    maps.update(ratefluid=(ro, rn), ratefluid_hybrid_train=(ro+h*training['s_train'], rn+h*training['s_train']))
    nowcast = nowcast_gaps(stale, rate_old, case, h, training['nowcast'], training['s_train'])
    for name, fresh_name in (('fluid_nowcast', 'fluid'), ('ratefluid_nowcast', 'ratefluid'),
                             ('ratefluid_nowcast_hybrid_train', 'ratefluid_hybrid_train')):
        maps[name] = (nowcast[name], maps[fresh_name][1])
    if timing_only:  # Exercise all eight maps, but produce no scientific score.
        for old, new in maps.values():
            _ = (old<0, new<0)
        return dict(timing_only=True, h=h, n_inst=n, CPU=time.process_time()-clock)
    if stay.mean() <= 0:
        raise ValueError('zero observed E_stay; percentage is undefined')
    for name, (old, new) in maps.items():
        z = ((old<0).astype(int)-(new<0))*d
        stats = batch_stats(z,batches)
        ratio = stats['mean']/stay.mean()
        twins[name] = dict(G_S=stats['mean'], se=stats['se'], pct_E_stay=100*ratio,
                           se_pct=100*batch_stats(z-ratio*stay,batches)['se']/stay.mean())
    return dict(case=case, seed=case.get('seed',1)+1000000, h=h, tau=TAU, n_inst=n, batches=batches,
                spacing=spacing, E_stay=batch_stats(stay,batches),
                s_train=training['s_train'], T_int=training['T_int'], twins=twins,
                F_old=float((go<0).mean()), F_new=float((gn<0).mean()),
                F_old_rate=float((ro<0).mean()), F_new_rate=float((rn<0).mean()),
                **{f'F_old_{name}': float((gap<0).mean()) for name, gap in nowcast.items()},
                CPU=time.process_time()-clock)


def validate(case):
    if not re.fullmatch(r'[A-Za-z0-9_-]+', case['id']):
        raise ValueError('unsafe case id')
    if not (0 <= case['u'] and 0 <= min(case['lamA'],case['lamB']) and max(case['lamA'],case['lamB'])+case['u'] < MU):
        raise ValueError('unstable or negative mean load')
    if case.get('warmup',1000) < 0 or case.get('train_T',20000) <= TAU or case.get('sample_dt',.1) <= 0:
        raise ValueError('invalid run duration or sampling step')
    if not 0 <= case.get('seed',1) < 1000000 or case.get('batches',40) < 2 or case.get('n_inst',20000) < 2*case.get('batches',40):
        raise ValueError('need >=2 batches, >=2 instants/batch, and seed in [0,1000000)')
    if not set(case.get('h_mult',[1,3,10])) <= {1,3,10,30}:   # 30 added by Claude (review)
        raise ValueError('h_mult must be in {1,3,10,30}')
    if 'initial_mode' in case['params']:
        raise ValueError('initial_mode is a conditional-physics test hook only')
    arrivals(case['cls'],case['lamA'],case['params'],0,np.random.default_rng(0))
    arrivals(case['cls'],case['lamB'],case['params'],0,np.random.default_rng(0))
    rate_settings(case)


def signature(case):
    return hashlib.sha256(json.dumps(case,sort_keys=True).encode()).hexdigest()


def job(args):
    mode, case, training, mult, path, timing_only = args
    clock = time.perf_counter()
    result = train(case) if mode == 'train' else simulate(case, mult*training['T_int'], training, timing_only)
    result['case_sha256'] = signature(case)
    result['wall'] = time.perf_counter()-clock
    if mode == 'test':
        result['h_mult'] = mult
    with Path(path).open('x') as f:
        json.dump(result,f,indent=2,allow_nan=False)
    return dict(file=str(path), CPU=result['CPU'])


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['train','test'])
    p.add_argument('--cases',required=True); p.add_argument('--out',required=True)
    p.add_argument('--timing-only',action='store_true',help='test workload only; no scores')
    p.add_argument('--train'); p.add_argument('--workers',type=int,default=1)
    args = p.parse_args(argv)
    if (args.mode == 'test' and not args.train) or (args.mode == 'train' and args.timing_only):
        p.error('test requires --train; --timing-only is test-only')
    cases, out = json.loads(Path(args.cases).read_text()), Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    tasks = []
    for c in cases:
        validate(c)
        name = f"{c['id']}_s{c.get('seed',1)}"
        tr = json.loads((Path(args.train)/f'{name}.json').read_text()) if args.mode == 'test' else None
        if tr and (tr.get('case_sha256') != signature(c) or tr['T_int'] <= 0 or tr['T_int_censored']):
            raise ValueError('training mismatch or unresolved T_int')
        for mult in ([None] if args.mode == 'train' else c.get('h_mult',[1,3,10])):
            tasks.append((args.mode,c,tr,mult,out/f'{name}{"" if mult is None else "_h"+str(mult)}.json',args.timing_only))
    paths = [str(t[-2]) for t in tasks]
    if len(set(paths)) != len(paths) or any(Path(s).exists() for s in paths):
        raise FileExistsError('duplicate or existing output; refusing overwrite')
    if args.workers < 1:
        raise ValueError('workers must be positive')
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=get_context('spawn')) as pool:
        for result in pool.map(job,tasks):
            print(json.dumps(result),flush=True)


if __name__ == '__main__':
    main()
