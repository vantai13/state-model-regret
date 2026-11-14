"""Doan Van Tai — periodically replayed empirical intensity, Poisson packets.

This preserves rate structure, not the trace's packet/flow dependence. Every
call draws its own continuous uniform phase on [0,L). The twin's T_r is a
calibration of the observed count series, not a truth timescale. The default
uses unbiased linear FFT autocorrelation, trapezoidal integration through its
linearly interpolated first zero. Constant series use bin/2 by convention
(no fluctuation timescale is identifiable; arrivals remain homogeneous).
Cached inputs are invalidated by file size and mtime; arrays are read-only.
"""
from functools import lru_cache
import json
from pathlib import Path

import numpy as np


def autocorrelation_time(counts, dt):
    x = np.asarray(counts, dtype=float)
    if x.ndim != 1 or not len(x) or not np.isfinite(x).all() or not np.isfinite(dt) or dt <= 0:
        raise ValueError('need a finite nonempty series and positive bin')
    z = x-x.mean()
    if not np.any(z):
        return dt/2
    n = len(z)
    size = 1 << (2*n-1).bit_length()
    cov = np.fft.irfft(abs(np.fft.rfft(z, n=size))**2, n=size)[:n]
    cov /= np.arange(n, 0, -1)
    r = cov/cov[0]
    hits = np.flatnonzero(r[1:] <= 0)
    if not len(hits):
        raise ValueError('autocorrelation has no observed zero crossing; specify T_r')
    k = int(hits[0])+1
    area = np.sum((r[:k-1]+r[1:k])/2)*dt
    return float(area + .5*dt*r[k-1]**2/(r[k-1]-r[k]))


@lru_cache(maxsize=16)
def _load(path, key, dt, mtime_ns, size):
    with np.load(path, allow_pickle=False) as data:
        counts = np.array(data[key], dtype=float)
        if 'metadata' in data:
            meta = json.loads(str(data['metadata'].item()))
            if not np.isclose(meta['bin'], dt, rtol=1e-12, atol=0):
                raise ValueError('params bin disagrees with series metadata')
    if counts.ndim != 1 or not len(counts) or not np.isfinite(counts).all() or np.any(counts < 0):
        raise ValueError('trace counts must be a finite nonnegative nonempty vector')
    mean = counts.mean()
    if not np.isfinite(mean) or mean <= 0:
        raise ValueError('trace counts must have positive mean')
    rates = counts/mean
    rates.setflags(write=False)
    return rates


def series(params):
    path = Path(params['series']).resolve()
    key, dt = params.get('key', 's0'), params.get('bin', .01)
    if key not in ('all', 's0', 's1') or not np.isfinite(dt) or dt <= 0:
        raise ValueError('invalid trace key or bin')
    st = path.stat()
    return _load(str(path), key, float(dt), st.st_mtime_ns, st.st_size), float(dt)


@lru_cache(maxsize=16)
def _calibration(path, key, dt, mtime_ns, size):
    return autocorrelation_time(_load(path, key, dt, mtime_ns, size), dt)


def relaxation(params):
    if 'T_r' in params:
        tr = params['T_r']
    else:
        # Load/validate before calibration, including the bin metadata check.
        series(params)
        path = Path(params['series']).resolve()
        st = path.stat()
        tr = _calibration(str(path), params.get('key', 's0'), float(params.get('bin', .01)),
                          st.st_mtime_ns, st.st_size)
    if not np.isfinite(tr) or tr <= 0:
        raise ValueError('T_r must be finite and positive')
    return float(tr)


def arrivals(lam, params, T, rng):
    if not np.isfinite([lam, T]).all() or min(lam, T) < 0:
        raise ValueError('invalid trace rate or duration')
    rates, dt = series(params)
    phase = rng.uniform(0, len(rates)*dt)
    index = int(phase/dt)
    offset = phase-index*dt
    pieces = []
    # Chunk long horizons; boundary bins use their actual clipped widths.
    bins = int(np.ceil((T+offset)/dt))
    for first in range(0, bins, 65536):
        ix = np.arange(first, min(first+65536, bins))
        left = np.maximum(0., ix*dt-offset)
        width = np.maximum(0., np.minimum(T, (ix+1)*dt-offset)-left)
        counts = rng.poisson(lam*rates[(index+ix) % len(rates)]*width)
        pieces.append(np.repeat(left, counts)+rng.random(counts.sum())*np.repeat(width, counts))
    return np.sort(np.concatenate(pieces)) if pieces else np.empty(0)
