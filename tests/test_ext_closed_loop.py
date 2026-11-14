"""Doan Van Tai — EV-A controls; small truncations are test-only (blocked arrivals at N)."""
import json
import os
import signal
import time
from fractions import Fraction as F

import numpy as np
import pytest
from experiments.ext_validity import closed_loop as E

CASE = dict(id='test', parameters=['7', '15/2', '1', '1/2'], T_int_max=2.)


@pytest.fixture
def tiny(monkeypatch):
    monkeypatch.setattr(E.C, 'choose_N', lambda *a, **kw: 40)
    return CASE


def test_golden_one_shot(tiny):
    for h in (F(2), F(5)):
        expected = E.C.evaluate(*map(F, tiny['parameters']), [h], disagree=False)['h'][0]
        for key, cost in E.single_epoch_costs(tiny, h).items():
            assert cost == pytest.approx(expected[key], rel=1e-9)
            print('golden', h, key, 'relative_error', abs(cost / expected[key] - 1))


@pytest.mark.parametrize('action', [0, 1])
@pytest.mark.parametrize('stale', [False, True])
def test_constant_policy_stationary_law_and_mass(tiny, action, stale):
    chains = E._chains(tiny, 2)
    epoch = E._Epoch(chains, 2)
    mask = np.full(epoch.initial.shape, bool(action))
    rec, law = epoch.stationary(mask, stale, 1000)
    target = np.outer(chains[action][0].pi, chains[action][1].pi)
    if stale:
        assert np.abs(law[1 - action]).sum() == 0
        law = law[action]
    assert np.abs(law - target).sum() < 1e-10
    assert rec['J'] == pytest.approx(sum(ch.r for ch in chains[action]), rel=1e-10)
    assert rec['p'] == pytest.approx(action, abs=1e-12)
    assert rec['max_mass_drift'] <= 1e-12 and rec['status'] == 'COMPLETED'


@pytest.mark.parametrize('h', ['1/100', '2', '20'])
@pytest.mark.parametrize('parameters', [CASE['parameters'], ['13/2', '7', '2', '2']])
def test_zero_fit_bitwise_maps_and_no_truth(tiny, h, parameters, monkeypatch):
    tiny = dict(tiny, parameters=parameters)
    ar = E.C.evaluate(*map(F, tiny['parameters']), [F(h)], disagree=False, arrays=True)['_arrays']
    maps = E._m0(tiny, F(h), E._chains(tiny, F(h)))
    for key, value in maps.items():
        assert np.array_equal(value, ar[key])
    def forbidden(*a, **kw):
        raise AssertionError('truth called by zero_fit')
    monkeypatch.setattr(E.C, 'evaluate', forbidden)
    monkeypatch.setattr(E.C.Chain, 'V', forbidden)
    pred = E.zero_fit(tiny, F(h))
    assert pred['G_S_CL_pred'] == pytest.approx(pred['old']['J_pred'] - pred['new']['J_pred'], abs=1e-14)
    chains = E._chains(tiny, h)
    for name, suffix in [('new', ''), ('old', 'o')]:
        ga, gb = (maps['dh' + s + suffix][0] for s in ('A', 'B'))
        for b, pair in enumerate(chains):
            wa, wb = [ch.pi if not suffix else ch.pi.reshape(-1, 2).sum(1) for ch in pair]
            assert pred[name]['q'][b] == pytest.approx(np.sum(np.outer(wa, wb) * (ga[:, None] + gb < 0)))


def test_closed_loop_monte_carlo(tiny):
    """Independent replicas, each with a burn-in; SE is across replica time averages."""
    started = time.perf_counter()
    out = E.closed_loop(tiny, 2, 2)
    assert out['status'] == 'COMPLETED'
    for rec in out['cells'].values():
        assert rec['max_mass_drift'] <= 1e-12 and rec['law_l1'] < 1e-11 and rec['J_relative'] < 1e-12
    chains = E._chains(tiny, 2)
    ar = E.C.evaluate(*map(F, tiny['parameters']), [F(2)], disagree=False, arrays=True)['_arrays']
    masks = np.stack([E._masks(ar)[s] for s in E.CELLS])
    rng = np.random.default_rng(20261114)
    replicas, burn, samples = 1024, 80, 240
    x = np.stack([rng.choice(ch.n, (4, replicas), p=ch.pi) for ch in chains[0]], axis=-1)
    n, m = x // 2, x % 2
    Ns = np.array([ch.N for ch in chains[0]])
    costs = np.zeros((4, replicas))
    which = np.arange(4)[:, None]

    def advance(actions, duration):
        # Uniformisation of each truncated path, with action fixed over the segment.
        loads = np.stack([8 - actions, 7.5 + actions], axis=-1)
        rate = 8.5 + E.C.A + E.C.MU + 2
        clocks = np.zeros(n.shape)
        total = np.zeros(n.shape)
        active = np.ones(n.shape, bool)
        while active.any():
            idx = np.where(active)
            ends = clocks[idx] + rng.exponential(1 / rate, len(idx[0]))
            total[idx] += n[idx] * (np.minimum(ends, duration) - clocks[idx])
            clocks[idx] = ends
            active[idx] = ends < duration
            idx = np.where(active)
            z = rng.random(len(idx[0])) * rate
            arrivals = loads[idx] + np.where(m[idx], E.C.A, -E.C.A)
            n[idx] += (z < arrivals) & (n[idx] < Ns[idx[2]])
            n[idx] -= (z >= 14.5) & (z < 24.5) & (n[idx] > 0)
            m[idx] ^= ((z >= 24.5) & (z < 26.5)).astype(int)
        return total.sum(axis=-1)

    old = x.copy()
    advance(np.zeros((4, replicas)), 1)  # P1 initial stale-to-current propagation
    for epoch in range(burn + samples):
        obs = 2 * n + m
        obs[:2] = old[:2]
        actions = masks[which, obs[:, :, 0], obs[:, :, 1]]
        cost = advance(actions, 1)
        old = (2 * n + m).copy()  # full state at next decision minus tau
        cost += advance(actions, 1)
        if epoch >= burn:
            costs += cost / (2 * samples)
    for i, cell in enumerate(E.CELLS):
        mean, se = costs[i].mean(), costs[i].std(ddof=1) / np.sqrt(replicas)
        exact = out['cells'][cell]['J']
        print('MC', cell, 'J_exact', exact, 'J_mc', mean, 'se', se, 'z', (mean - exact) / se)
        assert se < .05 and abs(mean - exact) <= 4 * se
    print('MC_wall_seconds', time.perf_counter() - started)
    assert time.perf_counter() - started < 30


def test_cli_prediction_and_runner_failures(tiny, tmp_path, monkeypatch):
    cases, grid, pred = [tmp_path / n for n in ('cases.json', 'grid.json', 'pred.json')]
    cases.write_text(json.dumps([tiny]))
    grid.write_text('[[1,1],[2,1]]')
    E.main(['predict', '--cases', str(cases), '--grid', str(grid), '--out', str(pred)])
    assert len(json.loads(pred.read_text())) == 2
    run = tmp_path / 'run'
    base = ['run', '--cases', str(cases), '--grid', str(grid), '--out', str(run), '--cap', '20']
    E.main(base + ['--workers', '2', '--shard', '0/2'])
    E.main(base + ['--workers', '2', '--shard', '1/2'])
    saved = {p: p.read_bytes() for p in run.glob('*.json')}
    assert len(saved) == 2 and all(json.loads(b)['status'] == 'COMPLETED' for b in saved.values())
    E.main(base)
    assert saved == {p: p.read_bytes() for p in run.glob('*.json')}
    for mode, status in [('kill', 'UNRESOLVED'), ('exit', 'ERROR'), ('error', 'ERROR'), ('cap', 'UNRESOLVED')]:
        def fake(*a, **kw):
            if mode == 'kill':
                os.kill(os.getpid(), signal.SIGKILL)
            if mode == 'exit':
                os._exit(7)
            if mode == 'error':
                raise ValueError('test failure')
            while True:
                pass
        monkeypatch.setattr(E, 'closed_loop', fake)
        dest = tmp_path / (mode + '.json')
        E._run([(tiny, F(2), F(2), dest)], 1, 1)
        assert json.loads(dest.read_text())['status'] == status


def test_limits_and_ties(tiny):
    with pytest.raises(ValueError, match='Delta'):
        E.closed_loop(tiny, 1, 2)
    assert E.closed_loop(tiny, 2, 2, max_iter=1)['status'] == 'UNRESOLVED'
    ar = {p + s + o: np.zeros((1, 41 if o else 82)) for p in ('d', 'dh') for s in ('A', 'B') for o in ('', 'o')}
    assert all(not mask.any() for mask in E._masks(ar).values())
