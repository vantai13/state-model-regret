"""Doan Van Tai — X4b vector capacities and preparation-only invariants."""
import json

import numpy as np
import pytest

from experiments.letter import x4b as B


def forbidden(*args, **kwargs):
    pytest.fail('test-seed future evaluation/truth/score is forbidden')


def test_capacity_rule_uses_total_switch_load_and_changes_only_e_star():
    inc = np.array([[[1., 1.], [0., 1.], [0., 0.]],
                    [[0., 1.], [1., 1.], [1., 0.]]])
    cap, e, load = B.calibrate_capacity(inc, np.array([4., 2.]), [1, 2], 10.)
    assert e == 1
    np.testing.assert_allclose(cap, [10., 6/.85, 10.], rtol=0, atol=0)
    assert load[1, e]/cap[e] == pytest.approx(.85, abs=1e-15)
    np.testing.assert_array_equal(cap[[0, 2]], 10.)


def test_e_star_tie_uses_native_link_index_before_any_capacity_change():
    inc = np.ones((2, 3, 1))
    cap, e, _ = B.calibrate_capacity(inc, np.ones(1), [2, 1], 10.)
    assert e == 1 and cap[1] == 1/.85


@pytest.mark.parametrize('cap', [0., -1., np.nan, [10., 0.]])
def test_invalid_capacity_rejected(cap):
    with pytest.raises(ValueError):
        B.capacity_vector(cap, 2)


def test_vector_strata_and_scalar_reduction():
    inc = np.array([[[1., 0.], [0., 1.]], [[0., 1.], [1., 0.]]])
    demand = np.array([[4., 3.], [5., 3.]])
    assert B.strata(demand, inc, [10., 5.])['stratum'] == 'O'
    assert B.strata(demand, inc, [10., 6.])['stratum'] == 'S'
    assert B.strata(demand, inc, [10., 10.]) == B.V3.strata(demand, inc, 10.)


@pytest.mark.parametrize('queues', [0., 1., 50000.])
def test_vector_mean_forecast_matches_imported_full_path_with_early_checkpoints(queues):
    inc = np.array([[[1., 1.], [0., 0.]], [[0., 1.], [1., 0.]]])
    profile = np.tile([4., 3.], (24, 1))
    modes = np.array([[1., -1.], [-1., 1.]])
    q = np.full((2, 2), queues)
    cap = np.array([8., 5.])
    got = B.mean_forecast(inc, profile, cap, modes, q)
    expected = B.S.mean_rollout(inc, profile, cap, modes, q,
        hs=np.rint(B.H_SECONDS/B.S.DT).astype(int))
    np.testing.assert_array_equal(got, expected)


def test_forecast_fallback_when_later_mean_load_exceeds_one_capacity():
    inc = np.array([[[1.], [0.]], [[0.], [1.]]])
    profile = np.full((8, 1), 4.)
    profile[2:] = 6.
    modes, q = np.ones((1, 1)), np.zeros((1, 2))
    cap = np.array([5., 10.])
    got = B.mean_forecast(inc, profile, cap, modes, q)
    expected = B.S.mean_rollout(inc, profile, cap, modes, q,
        hs=np.rint(B.H_SECONDS/B.S.DT).astype(int))
    np.testing.assert_array_equal(got, expected)
    assert got[0, 0, -1] > got[0, 0, 2]


def real_context():
    """One input record, never read any saved truth/score or outcome arrays."""
    config = B.C.read_json(B.X.OUT / 'configuration.json')
    old = B.read_npz(B.X.OUT / 'configuration.npz')
    # Saved preparation states are used only by the imported test data loader;
    # load exactly one test-day TM, not an outcome file.
    token = B.C.VerifiedLock(str(B.X.OUT / 'protocol.json'), B.C.sha256(B.X.OUT / 'protocol.json'))
    data, exclusions = B.V3.load_days(['2005-06-16'], config, verified=token)
    assert not exclusions
    record = dict(regime=config['regimes'][0]['id'], set='X2', split='test', date='2005-06-16', stratum='S')
    arrays = dict(old, capacity=np.full(old['incidence'].shape[2], float(old['capacity'].item())))
    return data, arrays, config, record, old


def test_real_homogeneous_vector_matches_x_geant_decisions_and_pilot_costs():
    data, arrays, config, record, scalar_arrays = real_context()
    slope = -1.
    # Same pilot-seed streams on both implementations, explicit old h grid.
    # Small counts keep this a regression test; the actual pilot uses full sizes.
    streams = B.X.seeds_for(B.PILOT_SEED, record['regime'], record['date'])
    expected, _ = B.X.decision_record(data, scalar_arrays, config, record, slope,
                                     seed=B.PILOT_SEED, n=2, k=2)
    actual, _ = B.decision_record(data, arrays, config, record, slope, seed=B.PILOT_SEED,
        n=2, k=2, horizons=B.X.H_SECONDS, streams=streams)
    for key in ('decisions', 'tie_flags'):
        np.testing.assert_array_equal(actual[key], expected[key][:, :3])
    for key in ('fresh_modes', 'fresh_queues', 'M0_predicted_fresh', 'M0_predicted_stale', 'path_utilization'):
        np.testing.assert_array_equal(actual[key], expected[key])
    raw, meta = B.pilot_record((dict(test=data), arrays, config), record,
        {record['regime']: slope}, n=2, k=2, r_dec=2, r_eval=3, horizons=B.X.H_SECONDS, streams=streams)
    inc = scalar_arrays['incidence'][0]
    cap = float(scalar_arrays['capacity'].item())
    checks = []
    for count, purpose in ((2, 'reference-decision'), (3, 'evaluation')):
        m, q = (np.repeat(expected[k], count, axis=0) for k in ('fresh_modes', 'fresh_queues'))
        checks.append(B.S.variable(inc, data['days'][0], cap, m, q, streams[purpose],
            hs=np.rint(B.X.H_SECONDS/B.S.DT).astype(int))[0].reshape(2, count, 2, 4))
    comparison = B.X.paired_metrics(expected, *checks, cap)
    for key in ('V', 'C_ref', 'reference_decision', 'paired_evaluation', 'reference_decision_rollouts'):
        np.testing.assert_array_equal(raw[key], comparison[key])
    for key in ('costs', 'regret', 'G_S'):
        np.testing.assert_array_equal(raw[key], comparison[key][:, :3])
    np.testing.assert_array_equal(raw['paired_Hybrid_minus_Stationary'], comparison['paired_Hybrid_minus_Stationary'])
    assert meta['seed_base'] == B.PILOT_SEED and meta['pilot']


def test_actual_seed_namespaces_and_purposes_are_disjoint():
    roots = [(base, regime, date) for base in (B.TEST_SEED, B.TRAIN_SEED, B.PILOT_SEED)
        for regime in ('NEWB1', 'NEWB2', 'NEWB3') for date in ('2005-05-05', '2005-06-16')]
    values = [v for args in roots for k, v in B.seeds_for(*args).items() if k != 'base']
    assert len(set(values)) == len(values)
    for args in roots:
        for key, value in B.seeds_for(*args).items():
            if key != 'base':
                assert value != B.X.seeds_for(*args)[key]


def test_test_overload_blocked_before_warmup(monkeypatch):
    monkeypatch.setattr(B.S, 'warm_instances', forbidden)
    data = dict(dates=np.array(['2005-06-16']), days=np.ones((1, 24, 1))*20)
    arrays = dict(incidence=np.ones((1, 2, 2, 1)), capacity=np.array([[10., 5.]]))
    config = dict(train_dates=['2005-05-05'], regimes=[dict(id='NEWB1')])
    record = dict(regime='NEWB1', split='test', date='2005-06-16', stratum='O')
    with pytest.raises(ValueError, match='NOT_RUN'):
        B.decision_record(data, arrays, config, record, -1., seed=B.TEST_SEED)


def test_decisions_only_never_evaluates_future_or_gathers_outcomes(monkeypatch):
    inc = np.array([[[[1.], [0.]], [[0.], [1.]]]])
    data = dict(dates=np.array(['2005-06-16']), days=np.ones((1, 24, 1)), warm=np.ones((1, 8, 1)))
    arrays = dict(incidence=inc, capacity=np.array([[10., 8.]]), profiles=np.ones((2, 24, 1)))
    config = dict(train_dates=['2005-05-05'], regimes=[dict(id='NEWB1', managed_index=0)])
    record = dict(regime='NEWB1', split='test', date='2005-06-16', stratum='S')
    monkeypatch.setattr(B.S, 'warm_instances', lambda *a: ((np.ones((2, 1)), np.zeros((2, 2))),
        {t: (np.ones((2, 1)), np.zeros((2, 2))) for t in B.S.TAU_SECONDS}))
    monkeypatch.setattr(B.S, 'forward_posterior', lambda *a: (np.ones((4, 1)), np.zeros((4, 2))))
    monkeypatch.setattr(B, 'mean_forecast', lambda inc, profile, cap, m, q, hs: np.zeros((len(m), 2, len(hs))))
    for obj, name in ((B.S, 'variable'), (B.E, 'costs_for_decisions'), (B, 'paired_metrics'),
                      (B, 'pilot_record'), (B.X, 'truth'), (B.X, 'score')):
        monkeypatch.setattr(obj, name, forbidden)
    raw, meta = B.decision_record(data, arrays, config, record, -1., seed=B.TEST_SEED, n=2, k=2)
    assert raw['decisions'].shape == (2, 3, 3, 7)
    assert {'V', 'costs', 'regret', 'G_S', 'C_ref'}.isdisjoint(raw)
    assert not meta['evaluation_called'] and not meta['C_ref_computed']


def test_gate_exact_one_percent_and_intermediate_hold_only():
    row = dict(population='test_S', h_s=1800, side='all_unique_sides', numerator=10, denominator=1000)
    assert B.signal_gate(dict(disagreement=[row]))['verdict'] == 'SIGNAL_OK'
    for change in (dict(h_s=3600), dict(numerator=9), dict(population='train_S'), dict(denominator=0)):
        assert B.signal_gate(dict(disagreement=[dict(row, **change)]))['verdict'] == 'NOT_ENOUGH_SIGNAL'


def test_signal_counts_each_unique_side_once_with_strict_higher_rate(tmp_path):
    record = dict(split='test', stratum='S', regime='NEWB1', date='2005-06-16')
    d = np.zeros((2, 3, 3, 7), dtype=np.int16)
    d[:, 1, 0] = 1
    costs = np.zeros((2, 2, 7))
    costs[0, 1] = 10.
    B.npz(tmp_path / 'step0/test/NEWB1_2005-06-16.npz', dict(decisions=d,
        tie_flags=np.zeros_like(d, dtype=bool), M0_predicted_fresh=costs,
        M0_predicted_stale=np.stack([costs, costs], axis=1), s_hat_Mbit=np.array(-1.)))
    table = B.signal_tables(tmp_path, [record])
    for row in table['disagreement']:
        if row['side'] == 'all_unique_sides':
            assert (row['numerator'], row['denominator'], row['fluid_prefers_higher_rate']) == (2, 6, 3)


def test_gs_zero_identical_sides_stationary_and_pathwise_action_gap_identity():
    n, h = 3, len(B.H_SECONDS)
    raw = dict(decisions=np.zeros((n, 3, 3, h), dtype=np.int16), h_seconds=B.H_SECONDS)
    ref = np.full((n, 2, 2, h), 1000.)
    evaluation = ref.copy()
    evaluation[:, :, 1] += 12.
    actual = B.paired_metrics(raw, ref, evaluation)
    np.testing.assert_array_equal(actual['G_S'], 0.)
    raw['decisions'][:, 0, 1] = 1
    actual = B.paired_metrics(raw, ref, evaluation)
    np.testing.assert_array_equal(actual['G_S'][:, 0, 0], 12.)
    np.testing.assert_array_equal(actual['G_S'][:, 2], 0.)
    delta_action = raw['decisions'][:, :, 1:]-raw['decisions'][:, :, :1]
    gap = actual['V'][:, 1]-actual['V'][:, 0]
    np.testing.assert_array_equal(actual['G_S'], delta_action*gap[:, None, None, :])
    np.testing.assert_array_equal(actual['paired_Hybrid_minus_Stationary'], actual['costs'][:, 1]-actual['costs'][:, 2])


@pytest.mark.parametrize('command', ['predict', 'pilot', 'lock'])
def test_no_signal_stops_downstream_before_any_data_or_engine(monkeypatch, tmp_path, command):
    monkeypatch.setattr(B, 'check_sources', lambda out: {})
    monkeypatch.setattr(B, 'load_context', forbidden)
    monkeypatch.setattr(B, 'pilot_record', forbidden)
    (tmp_path / 'signal.json').write_text(json.dumps(dict(gate=dict(verdict='NOT_ENOUGH_SIGNAL'))))
    with pytest.raises(ValueError, match='NOT_ENOUGH_SIGNAL'):
        B.main([command, '--out', str(tmp_path)])


@pytest.mark.parametrize('command', ['truth', 'score'])
def test_cli_refuses_truth_and_score(monkeypatch, command):
    monkeypatch.setattr(B.X, command, forbidden)
    with pytest.raises(SystemExit) as e:
        B.main([command])
    assert e.value.code == 2


def test_lock_drift_and_extra_record_detection(monkeypatch, tmp_path):
    code = tmp_path / 'code.py'
    code.write_text('original')
    paths = dict(code=code)
    monkeypatch.setattr(B, 'lock_paths', lambda out: paths)
    (tmp_path / 'lock.json').write_text(json.dumps(dict(schema='x4b-lock-v1', sha256=dict(code=B.C.sha256(code)))))
    assert isinstance(B.verify_lock(tmp_path), B.C.VerifiedLock)
    code.write_text('changed')
    with pytest.raises(ValueError, match='lock mismatch'):
        B.verify_lock(tmp_path)
    code.write_text('original')
    paths['extra'] = code
    with pytest.raises(ValueError, match='lock mismatch'):
        B.verify_lock(tmp_path)


def test_atomic_output_refuses_overwrite(tmp_path):
    p = tmp_path / 'data.npz'
    B.npz(p, dict(x=np.ones(1)))
    before = p.read_bytes()
    with pytest.raises(FileExistsError):
        B.npz(p, dict(x=np.zeros(1)))
    assert p.read_bytes() == before


def test_real_ranking_and_all_link_capacities_from_train_only():
    original, _ = B.D.load_training()
    old = B.C.read_json(B.X.BASE / 'configuration.json')
    training = B.A.window_training(original, old['start_slot'])
    original_x = B.C.read_json(B.X.OUT / 'configuration.json')
    previous = [r['managed_OD'] for r in original_x['regimes'] if r['set'] == 'X2']
    net = B.D.topology()
    info, incs, caps, busy, eligible = B.select_regimes(net, training['days'], old['capacity_Mbps'],
        {r['managed_OD'] for r in old['regimes']}, previous)
    assert [r['managed_OD'] for r in info] == [r['managed_OD'] for r in eligible[3:6]]
    assert [r['id'] for r in info] == ['NEWB1', 'NEWB2', 'NEWB3']
    for r, inc, cap in zip(info, incs, caps):
        assert inc[0, busy, r['managed_index']] == 1 and inc[1, busy, r['managed_index']] == 0
        assert np.count_nonzero(cap != old['capacity_Mbps']) == 1
        e = r['e_star_index']
        load = np.einsum('nsd,aed->nsae', training['days'], inc, optimize=True).mean(axis=(0, 1))
        assert load[1, e]/cap[e] == pytest.approx(.85, abs=2e-15)
        assert r['path_bottleneck_indices_after'][0] != r['path_bottleneck_indices_after'][1]
