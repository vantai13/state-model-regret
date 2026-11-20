"""Doan Van Tai — X-GÉANT rules, decision isolation, CRN and preparation guards.

Real-data regression reads saved V7-3 decisions/forecasts/states only; it never
reads old costs, V, regrets, or runs test-seed future evaluation.
"""
import json
from pathlib import Path

import numpy as np
import pytest

from experiments.letter import x_geant as X


def forbidden(*args, **kwargs):
    pytest.fail('future evaluation/truth/score is forbidden in preparation tests')


@pytest.mark.parametrize('theta', [1., 1.01, 2., 100.])
def test_threshold_at_least_one_never_switches_at_unit_or_lower_utilization(theta):
    u = np.array([[.9, .1], [1., .2], [.5, .5], [0., 0.]])
    decisions, _ = X.utilization_choices(u, theta)
    np.testing.assert_array_equal(decisions, 0)


def test_threshold_overload_follows_section4_no_unwritten_sentinel():
    # The brief's universal theta>=1 statement needs the <=1 load premise.
    # This counterexample is retained explicitly instead of changing the rule.
    d, _ = X.utilization_choices(np.array([[1.2, .8]]), 1.)
    np.testing.assert_array_equal(d, 1)


def test_threshold_strict_comparisons_and_boundary_ties():
    u = np.array([[.8, .2], [.9, .9], [.9, .8], [.7, .2], [.9, 1.]])
    d, t = X.utilization_choices(u, .8)
    np.testing.assert_array_equal(d, [0, 0, 1, 0, 0])
    np.testing.assert_array_equal(t, [1, 1, 0, 0, 0])
    m, mt = X.utilization_choices(u)
    np.testing.assert_array_equal(m, [1, 0, 1, 1, 0])
    np.testing.assert_array_equal(mt, [0, 1, 0, 0, 0])


@pytest.mark.parametrize('u', [np.array([[np.nan, 0.]]), np.array([1., 2.]), np.array([[-1., 2.]])])
def test_bad_utilization_refused(u):
    with pytest.raises(ValueError):
        X.utilization_choices(u, .8)


def test_utilization_moves_managed_flow_once_and_ignores_queues():
    # OD0 moves from link0 to link1; OD1 is background on link0 only.
    inc = np.array([[[1., 1.], [0., 0.]], [[0., 1.], [1., 0.]]])
    slot = np.array([4., 3.])
    modes = np.array([[1., -1.], [-1., 1.]])
    got = X.path_utilizations(inc, slot, modes, 10., managed=0)
    np.testing.assert_allclose(got, [[.73, .52], [.67, .28]], rtol=0, atol=1e-15)
    posterior = modes.reshape(1, 2, 2).mean(axis=1)
    np.testing.assert_array_equal(posterior, np.zeros((1, 2)))
    np.testing.assert_allclose(X.path_utilizations(inc, slot, posterior, 10., 0), [[.7, .4]])


def test_large_stale_age_analytic_expected_load_equals_slot_mean():
    slot = np.array([2., 7.])
    modes = np.array([[1., -1.], [-1., 1.]])
    got = X.expected_loads(slot, observed_modes=modes, tau=1e6)
    np.testing.assert_array_equal(got, np.broadcast_to(slot, modes.shape))
    small = X.expected_loads(slot, observed_modes=modes, tau=.1)
    np.testing.assert_allclose(small, slot*(1+.3*modes*np.exp(-.2)))
    # Empirical K samples need not have exactly zero endpoint mean even when
    # the conditional distribution is stationary. This is sampling noise.
    empirical = X.expected_loads(slot, modes=np.ones((1, 2))/64)
    assert not np.array_equal(empirical, slot[None])


def test_numeric_bases_preserved_actual_streams_new():
    from experiments.letter import v7_4_short as old
    assert (X.TEST_SEED, X.TRAIN_SEED, X.PILOT_SEED) == (7412001, 7402001, 7472001)
    assert (old.TEST_SEED, old.PILOT_SEED) == (X.TEST_SEED, X.PILOT_SEED)
    streams = [X.seeds_for(base, regime, day)
               for base in (X.TEST_SEED, X.TRAIN_SEED, X.PILOT_SEED)
               for regime in ('NEW1', 'NEW2', 'BOTH1')
               for day in ('2005-05-05', '2005-06-16')]
    actual = [s[k] for s in streams for k in ('record', 'warm', 'rate', 'posterior-300.0',
                                             'posterior-900.0', 'reference-decision', 'evaluation')]
    assert len(set(actual)) == len(actual)
    for base in (X.TEST_SEED, X.PILOT_SEED):
        for k in ('warm', 'reference-decision', 'evaluation', 'posterior-300.0', 'posterior-900.0'):
            assert X.seeds_for(base, 'DAY1', '2005-06-16')[k] != old.seeds_for(base, 'DAY1', '2005-06-16')[k]


def test_exact_hybrid_tie_and_stationary_zero():
    costs = np.array([[[0., 0.], [100., 200.]]])
    d, ties = X.fluid_choices(costs, -1., np.array([100, 200]))
    np.testing.assert_array_equal(d[:, 1], 0)
    np.testing.assert_array_equal(ties[:, 1], True)
    np.testing.assert_array_equal(d[:, 2], 1)
    d, ties = X.fluid_choices(costs, 0., np.array([100, 200]))
    np.testing.assert_array_equal(d[:, 2], 0)
    np.testing.assert_array_equal(ties[:, 2], True)


def test_saved_v73_decisions_bit_identical_on_all_horizons_and_sides():
    params = X.C.read_json(X.ROOT / X.C.PARAMS)
    path = X.C.OUT / 'records/DAY1_2005-06-16.npz'
    with np.load(path, allow_pickle=False) as old:
        fresh = old['M0_predicted_fresh']
        stale = old['M0_predicted_stale']
        saved_d, saved_t = old['decisions'], old['tie_flags']
        for side, costs in enumerate([fresh] + [stale[:, t] for t in range(2)]):
            d, ties = X.fluid_choices(costs, params['s_hat_pooled_Mbit']['DAY1'])
            if side == 0:
                for t in range(2):
                    np.testing.assert_array_equal(d, saved_d[:, :, 0, t])
                    np.testing.assert_array_equal(ties, saved_t[:, :, 0, t])
            else:
                np.testing.assert_array_equal(d, saved_d[:, :, 1, side-1])
                np.testing.assert_array_equal(ties, saved_t[:, :, 1, side-1])


def test_certified_mean_forecast_bit_identical_to_saved_v73_fresh():
    a = X.read_npz(X.BASE / 'configuration.npz')
    path = X.C.OUT / 'records/DAY1_2005-06-16.npz'
    with np.load(path, allow_pickle=False) as old:
        got = X.mean_forecast(a['incidence'][0], a['profiles'][0], float(a['capacity'].item()),
                              old['fresh_modes'], old['fresh_queues'])
        np.testing.assert_array_equal(got, old['M0_predicted_fresh'])


@pytest.mark.parametrize('q0', [0., 1., 50000.])
def test_zero_tail_forecast_matches_full_inherited_helper(q0):
    inc = np.array([[[1., 1.], [0., 0.]], [[0., 1.], [1., 0.]]])
    profile = np.tile([4., 3.], (24, 1))
    modes = np.array([[1., -1.], [-1., 1.]])
    queues = np.full((2, 2), q0)
    actual = X.mean_forecast(inc, profile, 10., modes, queues)
    expected = X.S.mean_rollout(inc, profile, 10., modes, queues,
                                hs=np.rint(X.H_SECONDS/X.S.DT).astype(int))
    np.testing.assert_array_equal(actual, expected)


def test_forecast_certificate_on_modulated_posterior_sized_states():
    inc = np.array([[[1., 1.], [0., 0.]], [[0., 1.], [1., 0.]]])
    profile = np.tile([4., 3.], (24, 1))
    rng = np.random.default_rng(123)
    modes = rng.choice([-1., 1.], size=(128, 2))
    queues = rng.uniform(0., 10., size=(128, 2))
    # 1.3*7 > 8, so the naive envelope is not a zero-cost certificate.
    # Nevertheless the deterministic mean path drains within the first slot.
    got = X.mean_forecast(inc, profile, 8., modes, queues)
    full = X.S.mean_rollout(inc, profile, 8., modes, queues,
                           hs=np.rint(X.H_SECONDS/X.S.DT).astype(int))
    np.testing.assert_array_equal(got, full)


def test_real_training_selection_is_deterministic_and_excludes_old_ods():
    original, _ = X.D.load_training()
    old = X.C.read_json(X.BASE / 'configuration.json')
    training = X.A.window_training(original, old['start_slot'])
    previous = {r['managed_OD'] for r in old['regimes']}
    args = (X.D.topology(), training['days'], old['capacity_Mbps'], previous)
    rows, inc, _, _ = X.select_regimes(*args)
    again, inc2, _, _ = X.select_regimes(*args)
    assert rows == again
    np.testing.assert_array_equal(inc, inc2)
    assert len(rows) == 6 and len(set(r['managed_OD'] for r in rows)) == 6
    for r in rows:
        assert r['managed_OD'] not in previous
        assert r['X2_eligible'] if r['set'] == 'X2' else r['X4_eligible']


def toy(monkeypatch):
    record = dict(regime='NEW1', set='X2', split='test', date='2005-06-16', stratum='S')
    data = dict(dates=np.array([record['date']]), days=np.ones((1, 24, 1)), warm=np.ones((1, 8, 1)))
    inc = np.array([[[[1.], [0.]], [[0.], [1.]]]])
    arrays = dict(incidence=inc, profiles=np.ones((2, 24, 1)), capacity=np.array(10.))
    config = dict(train_dates=['2005-05-05'], regimes=[dict(id='NEW1', managed_index=0)])
    monkeypatch.setattr(X.S, 'warm_instances', lambda *a: ((np.ones((2, 1)), np.zeros((2, 2))),
        {t: (np.ones((2, 1)), np.zeros((2, 2))) for t in X.S.TAU_SECONDS}))
    monkeypatch.setattr(X.S, 'forward_posterior', lambda *a: (np.ones((4, 1)), np.zeros((4, 2))))
    def mean(inc, profile, cap, m, q):
        costs = np.zeros((len(m), 2, 4))
        costs[:, 1] = 10.
        return costs
    monkeypatch.setattr(X, 'mean_forecast', mean)
    return data, arrays, config, record


def test_decisions_only_no_future_evaluation_or_cost_gather(monkeypatch):
    args = toy(monkeypatch)
    for obj, name in ((X.S, 'variable'), (X.E, 'costs_for_decisions'), (X, 'paired_metrics'),
                      (X, 'outcome_record'), (X, 'truth'), (X, 'score'), (X.V3, 'compute_record')):
        monkeypatch.setattr(obj, name, forbidden)
    raw, meta = X.decision_record(*args, -1., seed=X.TEST_SEED, n=2, k=2)
    assert raw['decisions'].shape == (2, 8, 3, 4)
    assert raw['path_utilization'].shape == (2, 3, 2)
    assert {'V', 'C_ref', 'costs', 'G_S', 'paired_evaluation'}.isdisjoint(raw)
    assert not meta['evaluation_called'] and not meta['C_ref_computed']


def test_test_overload_blocked_before_warmup(monkeypatch):
    data, arrays, config, record = toy(monkeypatch)
    monkeypatch.setattr(X.S, 'warm_instances', forbidden)
    data['days'] *= 100
    with pytest.raises(ValueError, match='NOT_RUN'):
        X.decision_record(data, arrays, config, dict(record, stratum='O'), -1., seed=X.TEST_SEED)


def test_truth_requires_lock_before_engine(monkeypatch, tmp_path):
    def reject(*args, **kwargs):
        raise ValueError('fixture lock missing')
    monkeypatch.setattr(X, 'verify_lock', reject)
    monkeypatch.setattr(X, 'decision_record', forbidden)
    monkeypatch.setattr(X.S, 'variable', forbidden)
    with pytest.raises(ValueError, match='lock missing'):
        X.outcome_record(None, {}, {}, stage='truth', out=tmp_path)


def test_both_gates_exact_one_percent_boundary_and_separate_sets():
    tables = dict(X2=[dict(population='test_S', rule='TH_0.5', tau_s=0, numerator=10, denominator=1000)],
                  X4=[dict(population='test_S', h_s=7200, side='all_unique_sides', numerator=9, denominator=1000)])
    got = X.signal_gates(tables)
    assert got['X2']['verdict'] == 'SIGNAL_OK'
    assert got['X4']['verdict'] == 'NOT_ENOUGH_SIGNAL'
    tables['X4'][0]['numerator'] = 10
    assert X.signal_gates(tables)['X4']['verdict'] == 'SIGNAL_OK'
    tables['X4'][0]['h_s'] = 14400
    assert X.signal_gates(tables)['X4']['verdict'] == 'NOT_ENOUGH_SIGNAL'
    tables['X2'][0]['rule'] = 'MLU'
    assert X.signal_gates(tables)['X2']['verdict'] == 'NOT_ENOUGH_SIGNAL'


def test_signal_fresh_counted_once_and_no_x2_horizon_replication(tmp_path):
    records = [dict(split='test', stratum='S', regime='NEW1', set='X2', date='2005-06-16'),
               dict(split='test', stratum='S', regime='BOTH1', set='X4', date='2005-06-16')]
    for record in records:
        d = np.zeros((2, 8, 3, 4), dtype=np.int16)
        d[:, 3, 1] = 1
        d[:, 1, 0] = 1
        costs = np.zeros((2, 2, 4))
        costs[:, 1] = 10.
        X.npz(tmp_path / 'step0/test' / f"{record['regime']}_{record['date']}.npz",
              dict(decisions=d, tie_flags=np.zeros_like(d, dtype=bool),
                   M0_predicted_fresh=costs, M0_predicted_stale=np.stack([costs, costs], axis=1),
                   s_hat_Mbit=np.array(-1.)))
    got = X.signal_tables(tmp_path, records)
    x2 = next(r for r in got['X2'] if r['rule'] == 'TH_0.5' and r['tau_s'] == 0)
    assert (x2['numerator'], x2['denominator']) == (2, 4)
    for row in got['X4']:
        if row['side'] == 'all_unique_sides':
            assert (row['numerator'], row['denominator']) == (2, 6)
            assert row['fluid_prefers_higher_rate'] == 6


def test_paired_gs_zero_for_identical_sides_and_sign_for_switch():
    n = 3
    raw = dict(decisions=np.zeros((n, 8, 3, 4), dtype=np.int16), h_seconds=X.H_SECONDS)
    reference = np.ones((n, 2, 2, 4))*1000
    evaluation = reference.copy()
    evaluation[:, :, 1] += 12.
    metrics = X.paired_metrics(raw, reference, evaluation, 10.)
    np.testing.assert_array_equal(metrics['G_S'], 0.)
    raw['decisions'][:, 0, 1] = 1
    metrics = X.paired_metrics(raw, reference, evaluation, 10.)
    np.testing.assert_array_equal(metrics['G_S'][:, 0, 0], 12.)
    np.testing.assert_array_equal(metrics['G_S'][:, 0, 1], 0.)
    np.testing.assert_array_equal(metrics['paired_Hybrid_minus_Stationary'], 0.)
    np.testing.assert_array_equal(metrics['C_ref'], 1000.)


def test_lock_detects_drift_and_extra_preparation_record(monkeypatch, tmp_path):
    code = tmp_path / 'code.py'
    code.write_text('original')
    paths = {'code': code}
    lock = dict(schema='x-geant-lock-v1', sha256={'code': X.C.sha256(code)})
    (tmp_path / 'lock.json').write_text(json.dumps(lock))
    monkeypatch.setattr(X, 'lock_paths', lambda out: paths)
    assert isinstance(X.verify_lock(tmp_path), X.C.VerifiedLock)
    code.write_text('changed')
    with pytest.raises(ValueError, match='lock mismatch'):
        X.verify_lock(tmp_path)
    code.write_text('original')
    extra = tmp_path / 'extra.npz'
    extra.write_text('unexpected')
    paths['extra'] = extra
    with pytest.raises(ValueError, match='lock mismatch'):
        X.verify_lock(tmp_path)


def test_atomic_outputs_never_replace_existing_file(tmp_path):
    path = tmp_path / 'data.npz'
    X.npz(path, dict(x=np.array([1.])))
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        X.npz(path, dict(x=np.array([2.])))
    assert path.read_bytes() == before


def test_configured_routes_use_train_only_when_available():
    path = X.OUT / 'configuration.json'
    if not path.exists():
        pytest.skip('configure has not run yet; selection integration checked after configure')
    config = X.C.read_json(path)
    a = X.read_npz(X.OUT / 'configuration.npz')
    old = X.C.read_json(X.BASE / 'configuration.json')
    old_ods = {r['managed_OD'] for r in old['regimes']}
    assert a['incidence'].shape[0] == 6
    assert config['capacity_Mbps'] == old['capacity_Mbps']
    assert len(set(r['managed_OD'] for r in config['regimes'])) == 6
    for r in config['regimes']:
        assert r['managed_OD'] not in old_ods
        if r['set'] == 'X2':
            assert r['stay_uses_busiest_link'] and r['switch_avoids_busiest_link']
        else:
            assert r['path_max_mean_utilization'][1] >= .75*r['path_max_mean_utilization'][0]
    assert config['training_only_selection']


def test_cli_preparation_dispatch_never_enters_truth_or_score(monkeypatch, tmp_path):
    seen = []
    monkeypatch.setattr(X, 'configure', lambda out: seen.append(out))
    monkeypatch.setattr(X, 'truth', forbidden)
    monkeypatch.setattr(X, 'score', forbidden)
    X.main(['configure', '--out', str(tmp_path)])
    assert seen == [tmp_path]
