"""Same stored decimal spectral law; outward integer powers and sums at384bits.

This candidate changes evaluation cost, not the infinite law or its certificate.
It is not installed into the running recovery04 or production confirmation.
"""
import ctypes as C
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import mpmath as mp
import numpy as np

from smr.stationary_spectral import lower, upper
from experiments.R3R_08_population_numerics.fast_law import FastLaw, up, INF
from experiments.R3R_08_population_numerics.piecewise import LD, EPS


@lru_cache(None)
def library():
    source = Path(__file__).with_name('native') / 'points.cpp'
    target = Path(tempfile.gettempdir()) / ('smr-spectral-points-' + hashlib.sha256(source.read_bytes()).hexdigest()[:24] + '.so')
    if not target.exists():
        subprocess.run(['g++', '-O3', '-std=c++17', '-shared', '-fPIC', str(source), '-o', str(target)], check=True)
    lib = C.CDLL(str(target))
    lib.spectral_points.argtypes = [C.c_size_t, C.POINTER(C.c_char_p), C.c_size_t,
        C.POINTER(C.c_uint64), C.POINTER(C.c_char_p)]
    lib.spectral_points.restype = C.c_char_p
    return lib


def point_boxes(terms, zero, indices):
    indices = list(indices)
    if any(isinstance(q, (bool, np.bool_)) or not isinstance(q, (int, np.integer)) for q in indices):
        raise ValueError('integer powers required without truncation')
    qs = [int(q) for q in indices]
    if any(q < 0 or q > 2**40 for q in qs):
        raise ValueError('nonnegative integer power within declared native budget required')
    def encode(z):
        return [mp.nstr(z.real, 80).encode(), mp.nstr(z.imag, 80).encode()]
    fields = [part for term in terms for z in term for part in encode(z)]
    initial = [part for z in zero for part in encode(z)]
    args = (C.c_char_p * len(fields))(*fields)
    atoms = (C.c_char_p * len(initial))(*initial)
    powers = (C.c_uint64 * len(qs))(*qs)
    result = json.loads(library().spectral_points(len(terms), args, len(qs), powers, atoms))
    if 'error' in result:
        raise ArithmeticError(result['error'])
    if result['bits'] != 384 or len(result['points']) != len(qs):
        raise ArithmeticError('native point result schema mismatch')
    return result['points']


def interval(box):
    re, im, rad, exponent = box
    re, im, rad = int(re), int(im), int(rad)
    if rad < 0:
        raise ArithmeticError('negative enclosure radius')
    scale = mp.iv.mpf(2)**int(exponent)
    return mp.iv.mpc(mp.iv.mpf([re-rad, re+rad])*scale,
                     mp.iv.mpf([im-rad, im+rad])*scale)


def posteriors(law, indices):
    mp.mp.dps = 80
    mp.iv.dps = 80
    boxes = point_boxes(law.terms, law.zero, indices)
    values, errors = [], []
    for off, on in boxes:
        a, b = interval(off), interval(on)
        p = (a+b).real
        low = lower(p) - law.error
        if low <= 0:
            raise ArithmeticError('conditioning event not certified')
        ratio = b.real / p
        error = 2*law.error/low + upper(ratio)-lower(ratio) + mp.mpf('4e-16')
        if error > mp.mpf('1e-8'):
            raise ArithmeticError('posterior certificate fails')
        values.append(LD(str((upper(ratio)+lower(ratio))/2)))
        errors.append(up(LD(str(error)) + 32*EPS))
    return np.asarray(values, dtype=LD), np.asarray(errors, dtype=LD)


class NativePosteriorFastLaw(FastLaw):
    """Same binary guard; batch only the points requiring precision fallback."""
    def posterior(self, indices):
        indices = np.atleast_1d(indices).astype(np.int64)
        p, e = self.point(indices)
        total, et = p.sum(axis=1), e.sum(axis=1)
        positive = total > et
        center = np.zeros(len(indices), dtype=LD)
        error = np.full(len(indices), INF, dtype=LD)
        center[positive] = p[positive, 1]/total[positive]
        low = np.maximum(LD(0), (p[positive, 1]-e[positive, 1])/(total[positive]+et[positive]))
        high = np.minimum(LD(1), (p[positive, 1]+e[positive, 1])/(total[positive]-et[positive]))
        error[positive] = up(np.maximum(center[positive]-low, high-center[positive])+32*EPS)
        need = np.flatnonzero(error > LD('1e-8'))
        missing = [int(q) for q in np.unique(indices[need]) if int(q) not in self._posterior_fallback_cache]
        if missing:
            values, errors = posteriors(self.law, missing)
            self._posterior_fallback_cache.update({q: (v, e) for q, v, e in zip(missing, values, errors)})
        for i in need:
            center[i], error[i] = self._posterior_fallback_cache[int(indices[i])]
        if np.any(error > LD('1e-8')):
            raise ArithmeticError('fast posterior error exceeds1e-8')
        return center, error
