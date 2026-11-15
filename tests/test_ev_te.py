"""Doan Van Tai — EV-TE physics, inference, provenance and isolation checks."""
import numpy as np
import pytest

from experiments.ext_validity import ev_te as T
from experiments.ext_validity import ev_te_trace as R
from experiments.ext_validity import packet


def model():
    return T.Model(np.array([[[5., 2.], [0., 0.], [1., 1.]],
                             [[0., 2.], [5., 0.], [1., 1.]]]),
                   np.array([8., 6., 100.]), np.array([1., .1]), .6, ['od1', 'od2'], ['e1', 'e2', 'inactive'])


def test_fluid_exact_and_clipping():
    q = np.array([0., .1, 2., 100.])
    for load in (0., 6., 9., 10., 11., 17.):
        for h in (.01, 1., 17.):
            end, cost = T.fluid_step(q, load, 10., h)
            np.testing.assert_allclose(cost, packet.fluid_cost(q, load, h), atol=1e-12)
            np.testing.assert_allclose(end, np.maximum(0., q+(load-10)*h))
    assert T.fluid_step(np.array([3.]), 2., 5., 4.)[1][0] == 1.5


def test_native_cost_kernel_constant_load_closed_form():
    m = T.Model(np.array([[[7.]], [[11.]]]), np.array([10.]), np.array([1.]), 0., ['od'], ['e'])
    q = np.array([[0.], [.5], [3.], [100.]])
    hs, dt = [1, 10, 40], .1
    costs, _, _ = T.futures(m, np.ones((len(q), 1)), q, dt, hs, 619)
    expected = np.empty_like(costs)
    for a, load in enumerate([7., 11.]):
        for j, steps in enumerate(hs):
            expected[:, a, j] = packet.fluid_cost(q[:, 0], load, steps*dt)
    np.testing.assert_allclose(costs, expected, atol=1e-12, rtol=1e-14)


def test_exact_mean_twin_against_discrete_steps():
    rng = np.random.default_rng(83)
    m = T.Model(np.ascontiguousarray(rng.uniform(0, 5, (4, 3, 6))), np.array([12., 15., 17.]),
                np.array([1., .1, 1., .1, 1., .1]), .6, list('abcdef'), list('xyz'))
    modes, q = rng.uniform(-1, 1, (60, 6)), rng.uniform(0, 20, (60, 3))
    # Include exact empty and nonempty zero-drift/two-drift-sign-change cases.
    modes[0], q[0] = 0, 0
    dt, hs = .03, [1, 10, 100, 500]
    got = T.twin_costs(m, modes, q, dt, hs)
    direct = np.zeros_like(got)
    for a in range(4):
        qq, cost = q.copy(), np.zeros(len(q))
        for t in range(hs[-1]):
            load = (1+m.beta*modes*np.exp(-2*m.kappa*t*dt)) @ m.weights[a].T
            qq, cc = T.fluid_step(qq, load, m.capacity, dt)
            cost += cc.sum(axis=1)
            if t+1 in hs:
                direct[:, a, hs.index(t+1)] = cost
    np.testing.assert_allclose(got, direct, rtol=2e-12, atol=1e-9)


def test_sampled_chain_stationary_and_decay():
    m, n = model(), 50000
    qs = np.zeros((n, 3))
    for modes in (np.ones((n, 2)), np.random.default_rng(37).choice([-1., 1.], (n, 2))):
        _, final, _ = T.futures(m, modes, qs, .05, [20], 813)
        target = np.exp(-2*m.kappa) if modes.min() > 0 else np.zeros(2)
        np.testing.assert_allclose(final.mean(axis=0), target, atol=.018, rtol=0)
        assert set(np.unique(final)) == {-1., 1.}


def test_posterior_forward_distribution():
    m, n = model(), 22000
    modes, qs = np.tile([1., -1.], (n, 1)), np.tile([2., 0., 0.], (n, 1))
    pm, pq = T.posterior(m, modes, qs, .05, 12, 1, 553)
    # Independent Python forward simulator, including the initial-state timing.
    rng, qm, mm = np.random.default_rng(993), qs.copy(), modes.copy()
    p = -np.expm1(-2*m.kappa*.05)/2
    for _ in range(12):
        qm, _ = T.fluid_step(qm, (1+m.beta*mm) @ m.weights[0].T, m.capacity, .05)
        mm *= np.where(rng.random(mm.shape) < p, -1, 1)
    np.testing.assert_allclose(pm.mean(axis=0), mm.mean(axis=0), atol=.025)
    np.testing.assert_allclose(pq.mean(axis=0), qm.mean(axis=0), atol=.018)
    np.testing.assert_allclose(np.quantile(pq[:, 0], [.1, .5, .9]), np.quantile(qm[:, 0], [.1, .5, .9]), atol=.12)
    # Same underlying forward kernel/seed must also match bitwise.
    stay = T.Model(m.weights[:1], m.capacity, m.kappa, m.beta, m.od_ids, m.link_ids)
    _, direct_m, direct_q = T.futures(stay, modes, qs, .05, [12], 553)
    np.testing.assert_array_equal(pm, direct_m)
    np.testing.assert_array_equal(pq, direct_q)


def test_crn_identical_actions_and_shared_mode_path():
    m = model()
    duplicate = T.Model(np.repeat(m.weights[:1], 4, axis=0), m.capacity, m.kappa, m.beta, m.od_ids, m.link_ids)
    modes, qs = np.tile([1., -1.], (80, 1)), np.zeros((80, 3))
    costs, _, _ = T.futures(duplicate, modes, qs, .05, [4, 20, 80], 827)
    for a in range(1, 4):
        np.testing.assert_array_equal(costs[:, 0], costs[:, a])
    # Changing action count cannot consume extra random draws.
    single = T.futures(m, modes, qs, .05, [4, 20, 80], 827)
    duplicated = T.futures(duplicate, modes, qs, .05, [4, 20, 80], 827)
    np.testing.assert_array_equal(single[1], duplicated[1])


def test_active_reduction_lossless_same_physical_modes():
    m = model()
    reduced = T.Model(np.ascontiguousarray(m.weights[:, :2]), m.capacity[:2], m.kappa, m.beta, m.od_ids, m.link_ids[:2])
    mo, qq = np.tile([1., -1.], (30, 1)), np.zeros((30, 3))
    full = T.futures(m, mo, qq, .05, [20, 90], 7)[0]
    red = T.futures(reduced, mo, qq[:, :2], .05, [20, 90], 7)[0]
    np.testing.assert_array_equal(full, red)
    np.testing.assert_array_equal(T.twin_costs(m, mo, qq, .05, [20, 90]),
                                  T.twin_costs(reduced, mo, qq[:, :2], .05, [20, 90]))


def test_reduction_removes_irrelevant_ods_pathwise():
    net = T.parse_native(T.data_root() / 'sndlib-networks-native/abilene.txt')
    prepared = T.prepare_network(net, .8)
    spec = dict(network=prepared, managed=prepared['managed_sets'][0], beta=.6, slow=1)
    full, red = T.make_model(spec, reduced=False), T.make_model(spec)
    assert len(red.od_ids) < len(full.od_ids) and len(red.link_ids) < len(full.link_ids)
    paths = np.random.default_rng(273).choice([-1., 1.], (300, len(full.od_ids)))
    subset = [full.od_ids.index(name) for name in red.od_ids]
    # Feed identical retained physical mode paths, not unrelated RNG draws.
    def direct(m, modes):
        q, cost = np.zeros(m.weights.shape[:2]), np.zeros(len(m.weights))
        for z in modes:
            loads = np.einsum('aed,d->ae', m.weights, 1+m.beta*z)
            q, inc = T.fluid_step(q, loads, m.capacity, .05)
            cost += inc.sum(axis=1)
        return cost
    np.testing.assert_allclose(direct(full, paths), direct(red, paths[:, subset]), atol=1e-10, rtol=1e-13)


def test_two_action_predictor_identity():
    r, fresh, old, h = [5., 3.], [[.8, .2], [.1, .9]], [[.4, .6], [.6, .4]], np.array([7., 30.])
    slope, level = T.predictor(r, old, fresh, h)
    delta_f = np.array(old)[:, 1]-np.array(fresh)[:, 1]
    np.testing.assert_allclose(level, h*(r[1]-r[0])*delta_f, atol=1e-14)
    np.testing.assert_allclose(slope, (r[1]-r[0])*delta_f, atol=1e-14)


def test_native_and_tm_parser_and_yen():
    net = T.parse_native(T.data_root() / 'sndlib-networks-native/abilene.txt')
    assert (len(net['nodes']), len(net['links']), len(net['demands'])) == (12, 30, 132)
    timestamp, row = R.parse_tm(T.tm_files()[0], [d['id'] for d in net['demands']])
    assert timestamp.minute % 5 == 0 and row.shape == (132,) and np.all(row >= 0)
    graph = dict(a={'b', 'c'}, b={'a', 'd'}, c={'a', 'd'}, d={'b', 'c'})
    assert T.two_paths(graph, 'a', 'd') == (('a', 'b', 'd'), ('a', 'c', 'd'))
    design = T.prepare_network(net, .9)
    assert len(design['candidates']) >= 3
    assert len(design['managed_sets'][3]) == 2
    g = T.parse_native(T.data_root() / 'sndlib-networks-native/geant.txt', 10000)
    assert len(g['nodes']) == 22 and len(g['links']) == 72
    assert all(e['capacity'] == 10000 for e in g['links'])


def test_reproducible_seed_outputs():
    m, mo, qq = model(), np.tile([1., -1.], (10, 1)), np.zeros((10, 3))
    a = T.futures(m, mo, qq, .05, [10, 20], T.seed_for(1, 'regime', 7))
    b = T.futures(m, mo, qq, .05, [10, 20], T.seed_for(1, 'regime', 7))
    for x, y in zip(a, b):
        np.testing.assert_array_equal(x, y)
    assert T.seed_for(777, 'regime', 7) != T.seed_for(1000001, 'regime', 7)
    a = T.trajectory(m, .05, 100, 200, 721, [100, 200])
    b = T.trajectory(m, .05, 100, 200, 721, [100, 200])
    for x, y in zip(a, b):
        np.testing.assert_array_equal(x, y)


def test_exclusive_writers_and_abort_before_engine(tmp_path, monkeypatch):
    path = tmp_path / 'once.json'
    T.write_json(path, {'a': 1})
    with pytest.raises(FileExistsError):
        T.write_json(path, {'a': 2})
    assert T.read_json(path) == {'a': 1}
    T.write_csv(tmp_path/'once.csv', [dict(a=1)])
    with pytest.raises(FileExistsError):
        T.write_csv(tmp_path/'once.csv', [dict(a=2)])
    monkeypatch.setattr(T, 'native', lambda: pytest.fail('engine before lock'))
    with pytest.raises(FileNotFoundError, match='lock.json'):
        T.run(out=tmp_path)


def test_lock_rejects_missing_mandatory_and_mutation(tmp_path, monkeypatch):
    input_path = tmp_path / 'input'
    input_path.write_text('original')
    fingerprint = dict(files={}, tm_file_count=1, tm_pairs_sha256='a', urls={})
    T.write_json(tmp_path/'data_manifest.json', fingerprint)
    monkeypatch.setattr(T, 'lock_inputs', lambda out: {str(input_path): T.sha256(input_path)})
    monkeypatch.setattr(T, 'data_fingerprint', lambda: fingerprint)
    T.write_json(tmp_path/'lock.json', dict(sha256={str(input_path): T.sha256(input_path)}))
    T.verify_lock(tmp_path)
    input_path.write_text('mutated')
    with pytest.raises(ValueError, match='SHA256'):
        T.verify_lock(tmp_path)


class LocalPool:
    def __init__(self, **kwargs):
        pass
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def map(self, func, tasks):
        return map(func, tasks)


def test_timing_only_real_work_writes_no_costs(tmp_path, monkeypatch):
    T.write_json(tmp_path/'regimes.json', [dict(id='tiny')])
    ti, dt = .4, .01
    taus, hs = T.grid(ti, dt)
    T.write_json(tmp_path/'train/tiny.json', dict(excluded=False, T_int=ti, dt=dt, tau_steps=taus, h_steps=hs))
    monkeypatch.setattr(T, 'make_model', lambda spec: model())
    monkeypatch.setattr(T, 'ProcessPoolExecutor', LocalPool)
    T.run(out=tmp_path, timing_only=True, regimes=['tiny'], n=2, k=4, r_dec=4, r_eval=8)
    timing = T.read_json(tmp_path/'timing.json')
    assert timing['seed'] == 777 and timing['no_costs_written']
    assert timing['regimes'][0]['CPU_per_instance'] > 0
    assert {p.name for p in tmp_path.iterdir()} == {'regimes.json', 'train', 'timing.json'}
    assert not any(p.suffix == '.npz' for p in tmp_path.rglob('*'))
    with pytest.raises(FileExistsError):
        T.run(out=tmp_path, timing_only=True)


def test_trace_relaxation_ols_and_missing_windows():
    rng = np.random.default_rng(37)
    x1, x2 = rng.normal(size=(100, 2)), rng.normal(size=(100, 2))
    coef = R.ols3(x1, x2, 3+2*x1-.5*x2)
    np.testing.assert_allclose(coef, np.tile([3., 2., -.5], (2, 1)), atol=1e-14)
    np.testing.assert_allclose(R.apply_ols(coef, x1, x2), np.maximum(0., 3+2*x1-.5*x2))
    tr, _ = R.relaxation(rng.uniform(size=(500, 3)), np.ones(500, bool))
    assert np.all((tr >= 5) & (tr <= 1440))
    segment = R.longest_valid(np.array([True, False, True, True, True, False]))
    assert (segment.start, segment.stop) == (2, 5)


def test_hypothesis_denominators_no_eligible_not_pass():
    assert T.hypothesis_counts([])['H1']['verdict'] == 'NOT_EVALUABLE'
    cells = [{**{f'H{i}_eligible': True for i in range(1, 5)},
              **{f'H{i}_pass': j < 9 for i in range(1, 5)}} for j in range(10)]
    result = T.hypothesis_counts(cells)
    assert all(r['eligible'] == 10 and r['passed'] == 9 and r['verdict'] == 'PASS' for r in result.values())


def test_paired_increment_se_preserves_covariance():
    shared = np.random.default_rng(95).normal(0, 100, 200)
    gs7 = shared + np.arange(200)/100
    gs30 = shared + 3*np.arange(200)/100
    mean, se = T.paired_stats(100*(gs30-gs7)/40)
    assert mean == pytest.approx(4.975)
    assert se == pytest.approx(np.std(np.arange(200)*.05, ddof=1)/np.sqrt(200))
    assert se < .25


@pytest.fixture
def arm_r_tms(tmp_path):
    nodes = [f'n{i:02d}' for i in range(12)]
    pairs = [(source, target) for source in nodes for target in nodes if source != target]
    ids = [f'{source}_{target}' for source, target in pairs]

    def write(stamp, omit=(), value=1.):
        path = tmp_path / f'demandMatrix-abilene-zhang-5min-{stamp}.txt'
        lines = [f'{source}_{target} ( {source} {target} ) 1 {value} UNLIMITED'
                 for source, target in pairs if f'{source}_{target}' not in omit]
        path.write_text('NODES (\n)\nLINKS (\n)\nDEMANDS (\n'+'\n'.join(lines)+'\n)\n')
        return path

    return nodes, ids, write


def test_arm_r_absent_od_is_zero_in_original_order(arm_r_tms):
    _, ids, write = arm_r_tms
    counts = dict(absent_od_entries_in_files=0, absent_od_entries_filled_with_zero=0)
    stamp, values = R.parse_tm(write('20040101-0000', omit={ids[0]}), ids[::-1], counts=counts)
    assert stamp.isoformat() == '2004-01-01T00:00:00'
    np.testing.assert_array_equal(values, [1.]*131+[0.])
    assert counts == dict(absent_od_entries_in_files=1, absent_od_entries_filled_with_zero=1)


def test_arm_r_explicit_zero_entries_are_not_node_outage(arm_r_tms):
    _, ids, write = arm_r_tms
    _, values = R.parse_tm(write('20040101-0000', value=0.), ids)
    np.testing.assert_array_equal(values, np.zeros(132))


@pytest.mark.parametrize('direction', ['source', 'destination', 'both'])
def test_arm_r_node_outage_is_missing_even_with_other_entries(arm_r_tms, direction):
    nodes, ids, write = arm_r_tms
    omit = {name for name in ids if
            (direction in ('source', 'both') and name.startswith(nodes[0]+'_')) or
            (direction in ('destination', 'both') and name.endswith('_'+nodes[0]))}
    assert len(omit) == (22 if direction == 'both' else 11)
    counts = dict(absent_od_entries_in_files=0, absent_od_entries_filled_with_zero=0)
    with pytest.raises(R.NodeOutageError, match='node outage'):
        R.parse_tm(write('20040101-0000', omit=omit), ids, counts=counts)
    assert counts['absent_od_entries_in_files'] == len(omit)
    assert counts['absent_od_entries_filled_with_zero'] == 0


@pytest.mark.parametrize('bad_entry', [
    'unknown_n00 ( unknown n00 ) 1 1 UNLIMITED',
    'n00_n01 ( n00 n01 ) 1 1 UNLIMITED',
    'n00_n00 ( n00 n00 ) 1 -1 UNLIMITED',
])
def test_arm_r_parser_still_rejects_invalid_or_duplicate_ods(arm_r_tms, bad_entry):
    _, ids, write = arm_r_tms
    path = write('20040101-0000')
    text = path.read_text()
    path.write_text(text[:-2]+bad_entry+'\n)\n')
    with pytest.raises(ValueError, match='invalid or duplicate TM OD'):
        R.parse_tm(path, ids)


def test_arm_r_load_trace_counts_outages_absent_files_and_zero_fill(arm_r_tms, monkeypatch):
    nodes, ids, write = arm_r_tms
    paths = [write('20040101-0000'),
             write('20040101-0010', omit={ids[0]}),
             write('20040101-0015', omit={name for name in ids if nodes[0] in name.split('_')}),
             write('20040101-0020')]
    monkeypatch.setattr(T, 'tm_files', lambda: paths)
    monkeypatch.setattr(T, 'parse_native', lambda path: dict(demands=[dict(id=name) for name in ids]))
    _, times, values, valid, train, stats = R.load_trace()
    np.testing.assert_array_equal(valid, [True, False, True, False, True])
    assert train.all() and len(times) == 5
    assert np.isnan(values[[1, 3]]).all()
    assert values[2, 0] == 0. and values[2, 1] == 1.
    assert stats['file_count'] == 4 and stats['valid_bins'] == 3
    assert stats['node_outage_bins'] == 1 and stats['absent_file_bins'] == 1
    assert stats['malformed_count'] == 0 and stats['missing_or_malformed_bins'] == 2
    assert stats['absent_od_entries_in_files'] == 23
    assert stats['absent_od_entries_filled_with_zero'] == 1
    assert stats['train_end_exclusive'] == '2004-03-01T00:00:00'


def test_arm_r_run_drops_windows_crossing_missing_bins(tmp_path, monkeypatch):
    from datetime import datetime, timedelta

    times = [datetime(2004, 3, 1)+timedelta(minutes=5*i) for i in range(60)]
    rates, valid, train = np.ones((60, 1)), np.ones(60, bool), np.arange(60) < 5
    valid[[25, 39]] = False  # A node outage and an absent file are both missing.
    rates[~valid] = np.nan
    monkeypatch.setattr(R, 'load_trace', lambda: ({}, times, rates, valid, train, {}))
    monkeypatch.setattr(R, 'route_arrays', lambda network, managed: (np.ones((2, 1, 1)), np.array([.5])))
    regime = dict(id='tiny', network={}, managed=['od'], active_indices=[0], relevant_indices=[0],
                  alpha=1., mean_rates=[60.], relaxation_minutes=[5.],
                  OLS={str(age): dict(rate=[[0., 1., 0.]], backlog=[[0., 1., 0.]]) for age in R.AGES})
    T.write_json(tmp_path/'train.json', dict(regimes=[regime]))
    R.run(out=tmp_path)
    with np.load(tmp_path/'raw/tiny.npz', allow_pickle=False) as raw:
        selected = [times.index(datetime.fromisoformat(stamp)) for stamp in raw['timestamps']]
        assert selected == list(range(5, 13))+list(range(43, 48))
        assert all(not ({25, 39} & set(range(i-3, i+13))) for i in selected)
        assert raw['V'].shape == (13, 2, 4, 5)
        np.testing.assert_array_equal(raw['V'][:, :, 0], raw['V'][:, :, 1])
    assert T.read_json(tmp_path/'run.json')['regimes'][0]['n_instances'] == 13


def test_arm_r_backlog_time_fraction_includes_partial_draining_and_gap_reset():
    rates = np.array([[1.4], [0.], [0.], [1.4], [np.nan], [0.]])
    valid, incidence, cap = np.isfinite(rates[:, 0]), np.ones((1, 1)), np.array([1.])
    queues = R.replay_stay(rates, incidence, cap, valid)
    stats = R.backlog_stats(rates, queues, incidence, cap, valid, np.ones(6, bool))
    assert stats['observed_minutes'] == 25.
    assert stats['backlogged_minutes'] == pytest.approx(12.)
    assert stats['fraction_time_backlogged'] == pytest.approx(.48)
    assert stats['fraction_end_bins_backlogged'] == pytest.approx(.4)
    only_drain = R.backlog_stats(rates, queues, incidence, cap, valid, np.arange(6) == 1)
    assert only_drain['backlogged_minutes'] == pytest.approx(2.)
    no_bins = R.backlog_stats(rates, queues, incidence, cap, valid, np.zeros(6, bool))
    assert no_bins['fraction_time_backlogged'] is None


def test_arm_r_backlog_time_fraction_with_nonempty_zero_drift():
    rates, incidence, cap, valid = np.array([[1.4], [1.], [0.]]), np.ones((1, 1)), np.array([1.]), np.ones(3, bool)
    queues = R.replay_stay(rates, incidence, cap, valid)
    stats = R.backlog_stats(rates, queues, incidence, cap, valid, valid)
    assert stats['backlogged_minutes'] == pytest.approx(12.)
