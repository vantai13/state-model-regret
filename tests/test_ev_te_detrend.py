"""Doan Van Tai — tests for EV-TE Arm R-DT (Claude, 16/11/2026). CARD §8 synthetic sanity test plus shape checks."""
from datetime import datetime, timedelta

import numpy as np

from experiments.ext_validity import ev_te_detrend as D


def synthetic(days=60, theta=30., amp=1., sd=.2, seed=0):
    rng = np.random.default_rng(seed)
    n = days * 288
    t = np.arange(n) * 5.
    phi = np.exp(-5. / theta)
    noise = np.zeros(n)
    eps = rng.normal(0, sd * np.sqrt(1 - phi**2), n)
    for i in range(1, n):
        noise[i] = phi * noise[i-1] + eps[i]
    x = 10 + amp * np.sin(2 * np.pi * t / 1440.) + noise
    times = [datetime(2004, 3, 1) + timedelta(minutes=5*i) for i in range(n)]
    return x[:, None], times


def test_sinusoid_plus_ar1_raw_and_residual_tint():
    x, times = synthetic()
    raw = D.tint_minutes(x[:, 0])
    assert not raw['censored']
    assert abs(raw['T_int'] - 1440 / (2*np.pi)) <= .2 * 1440 / (2*np.pi)
    mask = np.ones(len(x), bool)
    prof, slot, wkend = D.profile(x, times, mask)
    res = D.residual(x, prof, slot, wkend, x.mean(axis=0), 'additive')
    r = D.tint_minutes(res[:, 0])
    assert not r['censored']
    assert abs(r['T_int'] - 30.) <= .3 * 30.


def test_profile_shape_smoothing_and_residual_mean():
    x, times = synthetic(days=14)
    mask = np.ones(len(x), bool)
    prof, slot, wkend = D.profile(x, times, mask)
    assert prof.shape == (2, 288, 1) and slot.max() == 287 and set(np.unique(wkend)) == {0, 1}
    res = D.residual(x, prof, slot, wkend, x.mean(axis=0), 'additive')
    assert abs(res.mean() - x.mean()) < .05
    mult = D.residual(x, prof, slot, wkend, x.mean(axis=0), 'multiplicative')
    assert np.all(mult >= 0) and abs(mult.mean() - x.mean()) < .1


def test_residual_keeps_missing_and_clips():
    x = np.array([[1.], [np.nan], [0.]])
    times = [datetime(2004, 3, 1, 0, 5*i) for i in range(3)]
    prof = np.full((2, 288, 1), 5.)
    slot = np.array([0, 1, 2]); wk = np.zeros(3, int)
    r = D.residual(x, prof, slot, wk, np.array([1.]), 'additive')
    assert r[0, 0] == 0. and np.isnan(r[1, 0]) and r[2, 0] == 0.


def test_windows_non_overlapping_within_valid_runs():
    valid = np.array([True]*700 + [False] + [True]*300)
    ws = D.windows(valid, 288)
    assert [(w.start, w.stop) for w in ws] == [(0, 288), (288, 576), (701, 989)]
