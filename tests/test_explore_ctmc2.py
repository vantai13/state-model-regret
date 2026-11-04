"""Doan Van Tai — tests for ctmc-v2 (L7.3 Part 2, Stage 0) [EXPLORATION ONLY; AI (Claude) theo ủy quyền]."""
from fractions import Fraction as F
import json
import math
from pathlib import Path

import numpy as np
import pytest

from experiments.explore_ctmc import ctmc, ctmc2

ROOT = Path(__file__).resolve().parents[1]


def test_amplitudes_keep_peak_and_variance_share():
    for f in (F(1, 20), F(1, 5), F(1, 2)):
        af, as_ = ctmc2.amplitudes(f)
        assert af + as_ == 6
        assert abs(ctmc2.f_of(af, as_) - float(f)) < 1e-4
    assert ctmc2.amplitudes(F(1, 5)) == (F(4), F(2))


def test_generator_rows_sum_to_zero_and_flip_both_bits():
    Q = ctmc2.generator(F(8), F(1, 5), F(2), F(4), F(2), 30)
    assert np.abs(np.asarray(Q.sum(axis=1)).ravel()).max() < 1e-12
    row = Q.getrow(4 * 3 + 0).toarray().ravel()          # n = 3, both modes low
    assert row[4 * 3 + 1] == pytest.approx(5.0) and row[4 * 3 + 2] == pytest.approx(0.5)


def test_slow_modulator_without_amplitude_lumps_to_ctmc_v1():
    load, k, N = F(15, 2), F(1, 2), 200
    v1 = ctmc.Chain(load, k, N)
    v2 = ctmc2.Chain(load, k, 10 * k, F(6), F(0), N)
    lump = v2.pi.reshape(-1, 2, 2).sum(axis=1).reshape(-1)    # sum over the slow bit
    assert np.abs(lump - v1.pi).max() < 1e-12
    assert v2.T_int == pytest.approx(v1.T_int, rel=1e-10)


def test_truth_guard():
    with pytest.raises(PermissionError):
        ctmc2.evaluate(F(7), F(8), F(1), F(1, 5), F(2), F(4), F(2), [F(1)])
    ctmc2.truth_allowed(F(7), F(8), F(1), F(1, 5), F(2), F(6), F(0))           # a_s = 0: ctmc-v1 control
    ctmc2.truth_allowed(*ctmc2.CONTROL_REGIMES['C2a'])


def test_mpm_shape_exists_and_rollout_matches_numeric():
    load, Tf, Ts, af, as_ = F(9), F(1, 5), F(20), F(4), F(2)
    sh = ctmc2.mode_shape(load, Tf, Ts, af, as_, 2)                            # sigma_f = -1, sigma_s = +1
    assert sh['shape'] == 'MPM' and sh['t1'] < sh['t2']
    hs = [1.0, 30.0, math.inf]
    got = ctmc2.m0_vhat(load, Tf, Ts, af, as_, 12, hs)
    grid = np.concatenate([np.linspace(0, 2, 200001), np.arange(2, 400, 2.5e-3)[1:]])
    d = -1.0 - 4 * np.exp(-10 * grid) + 2 * np.exp(-grid / 10)
    C = np.concatenate([[0.0], np.cumsum(0.5 * (d[1:] + d[:-1]) * np.diff(grid))])
    Mr = np.minimum.accumulate(C)
    for n in (0, 1, 3, 12):
        q = C + np.maximum(n, -Mr)
        cum = np.concatenate([[0.0], np.cumsum(0.5 * (q[1:] + q[:-1]) * np.diff(grid))])
        for j, h in enumerate(hs):
            want = cum[-1] if h == math.inf else np.interp(h, grid, cum)
            assert got[j][4 * n + 2] == pytest.approx(want, rel=1e-5, abs=1e-6)


def test_saturation_rule_zeroes_near_coincident_zero_time():
    T = np.array([20.0, 20.0 - 6e-9, 19.9, 25.0])
    sat = ctmc2.saturated(T, 20.0, F(6), F(0))
    assert sat.tolist() == [True, True, False, True]


def test_case_lists_exclude_control_regimes():
    folder = ROOT / 'results/explore_ctmc/cases_l73'
    if not folder.exists():
        pytest.skip('case lists not written yet')
    ctrl = set(ctmc2.CONTROL_REGIMES.values())
    for f in folder.glob('*.json'):
        if f.name == 'design_report.json':
            continue
        for c in json.loads(f.read_text()):
            assert tuple(F(x) for x in c['parameters'][:7]) not in ctrl
            assert max(c['N'].values()) <= 3000
