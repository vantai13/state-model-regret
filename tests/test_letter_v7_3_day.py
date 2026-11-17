"""Doan Van Tai — A2 controls use synthetic inputs or training-only metadata."""
import numpy as np
import pytest

from experiments.ext_validity import ev_te as T
from experiments.letter import v7_3_day as A
from experiments.letter import v7_3_sim as S


def enumerated_paths(net, source, target):
    graph = {n: set() for n in net['nodes']}
    for e in net['links']:
        graph[e['source']].add(e['target'])
    all_paths = []
    todo = [(source,)]
    while todo:
        path = todo.pop()
        if path[-1] == target:
            all_paths.append(path)
        else:
            todo.extend(path+(v,) for v in graph[path[-1]] if v not in path)
    return sorted(all_paths, key=lambda p: (len(p), p))


def toy_day():
    training = dict(dates=np.array(['2005-05-05']), days=np.full((1, 24, 1), 6.),
                    warm=np.zeros((1, 8, 1)))
    arrays = dict(incidence=np.array([[[[2.]], [[1.]]]]),
                  capacity=np.array(10.), profiles=np.full((2, 24, 1), 6.))
    config = dict(train_dates=['2005-05-05'], regimes=[dict(id='DAY1')],
                  window_start='10:15', window_end='16:15')
    return training, arrays, config


def test_window_maximizes_train_weekday_mean_and_earliest_exact_tie():
    days = np.ones((2, 96, 2))
    days[:, 41:65] = 10
    start, scores = A.select_window(days)
    assert start == 41 and scores.shape == (73,) and scores[41] == 20
    assert A.clock(start) == '10:15' and A.clock(start+24) == '16:15'
    assert A.select_window(np.ones((3, 96, 2)))[0] == 0


@pytest.mark.parametrize('shape', [(0, 96, 2), (2, 95, 2), (2, 96)])
def test_window_rejects_incomplete_shapes(shape):
    with pytest.raises(ValueError, match='complete'):
        A.select_window(np.zeros(shape))


@pytest.mark.parametrize('start', [0, 1, 7, 8, 41, 72])
def test_warmup_and_selected_window_keep_exact_source_slots(start):
    dates = np.array(['2005-05-05', '2005-05-06', '2005-05-07', '2005-05-08'])
    days = np.broadcast_to(np.arange(96)[None, :, None], (4, 96, 1)).copy()
    past = np.broadcast_to(np.arange(-8, 0)[None, :, None], (4, 8, 1)).copy()
    result = A.window_training(dict(dates=dates, days=days, warm=past), start)
    assert result['dates'].tolist() == dates[:2].tolist()
    np.testing.assert_array_equal(result['days'][0, :, 0], np.arange(start, start+24))
    np.testing.assert_array_equal(result['warm'][0, :, 0], np.arange(start-8, start))


def test_managed_ranking_does_not_silently_require_bottleneck_avoidance():
    # Three ODs all cross a>b. The top OD's second-shortest path still crosses it.
    # Construct three upstream sources and a common a>b link.
    nodes = ['a', 'b', 'c', 'd', 's1', 's2', 's3']
    pairs = [('s1', 'a'), ('s2', 'a'), ('s3', 'a'), ('a', 'b'),
             ('a', 'c'), ('c', 'd'), ('d', 'b'), ('s1', 's2')]
    net = dict(nodes=nodes,
               links=sorted([dict(id=f'{u}{v}:{x}>{y}', source=x, target=y)
                             for u, v in pairs for x, y in [(u, v), (v, u)]],
                            key=lambda e: (e['source'], e['target'])),
               demands=[dict(id='f1', source='s1', target='b'),
                        dict(id='f2', source='s2', target='b'),
                        dict(id='f3', source='s3', target='b')])
    days = np.broadcast_to(np.array([4., 3., 2.]), (2, 24, 3)).copy()
    infos, incs, bottleneck = A.regimes_for(net, days, 20.)
    assert net['links'][bottleneck]['source'] == 'a'
    assert net['links'][bottleneck]['target'] == 'b'
    assert [r['managed_OD'] for r in infos] == ['f1', 'f2', 'f3']
    assert infos[0]['switch_avoids_busiest_link'] is False
    assert infos[1]['switch_avoids_busiest_link'] is False
    for j, info in enumerate(infos):
        paths = enumerated_paths(net, net['demands'][j]['source'], 'b')
        assert tuple(info['stay']) == paths[0] and tuple(info['switch']) == paths[1]
        unchanged = np.arange(3) != j
        np.testing.assert_array_equal(incs[j, 0][:, unchanged], incs[j, 1][:, unchanged])
        assert not np.array_equal(incs[j, 0][:, j], incs[j, 1][:, j])


@pytest.mark.parametrize('dt', [.05, .005])
def test_zero_covariance_resolution_is_undefined_at_every_dt(dt):
    got = A.resolution(np.zeros(1000), dt)
    assert got['T_int_s'] is None and got['h6_over_T_int'] is None
    assert got['status'] == 'UNDEFINED_ZERO_VARIANCE' and got['variance_Mbit2'] == 0


def test_resolution_uses_same_letter_estimator_and_checks_grid():
    # A smooth, positive periodic covariance has a well-resolved first zero.
    dt = .005
    trace = 2+np.sin(2*np.pi*np.arange(20000)*dt)
    got = A.resolution(trace, dt)
    ti, censored, _ = T.estimate_tint(trace, dt)
    assert got['T_int_s'] == ti and got['censored'] == censored
    assert .15 < ti < .17 and got['status'] == 'RESOLVED'
    assert got['steps_per_T_int'] > 30 and got['relative_change_at_2dt'] < .001


def test_sign_stability_does_not_turn_all_zero_into_directional_stability():
    zero = A.sign_summary([0., 0., 0.])
    assert zero['nonzero_sign_stability_fraction'] is None
    assert zero['sign_counts'] == dict(positive=0, zero=3, negative=0)
    mixed = A.sign_summary([2., 0., -1., 3.])
    assert mixed['nonzero_sign_stability_fraction'] == .5
    assert mixed['nonzero_sign_stability_numerator'] == 2


@pytest.mark.parametrize('date', ['2005-06-15', '2005-05-07', '2005-08-31'])
def test_test_or_weekend_date_rejected_before_any_engine_call(monkeypatch, date):
    tr, ar, cf = toy_day()
    monkeypatch.setattr(S, 'warm_instances', lambda *a, **k: pytest.fail('engine called'))
    monkeypatch.setattr(S, 'variable', lambda *a, **k: pytest.fail('engine called'))
    with pytest.raises(ValueError, match='forbids'):
        A.compute_day(tr, ar, cf, date, 'DAY1', -1.)


def test_end_to_end_nonzero_toy_reference_crn_and_all_horizons():
    tr, ar, cf = toy_day()
    raw, meta = A.compute_day(tr, ar, cf, '2005-05-05', 'DAY1', -1.,
                             n=1, k=2, r_dec=2, r_eval=3, seed=4201)
    assert raw['decisions'].shape == (1, 3, 2, 2, 4)
    assert raw['paired_evaluation'].shape == (1, 3, 2, 4)
    assert (raw['reference_decision'] == 1).all()
    assert meta['reference_evaluation_streams_distinct']
    np.testing.assert_array_equal(raw['h_seconds'], [3600, 7200, 14400, 21600])
    np.testing.assert_array_equal(raw['G_S'], 0.)
    assert meta['regime'] == 'DAY1' and meta['training_only']


def test_daytime_relative_warmup_keeps_5_and_15min_states():
    inc = np.ones((2, 1, 1))
    fresh, old = S.warm_instances(inc, np.full((8, 1), 12.), 10., 1, 7851)
    # Sustained offered load is >=8.4, so at least one actual mode path queues.
    assert fresh[0].shape == (1, 1) and fresh[1].shape == (1, 1)
    assert set(old) == {300., 900.}
    assert old[300.][1].shape == old[900.][1].shape == (1, 1)
    # beta=0 analytic state/checkpoint timing tested through relative pieces.
    m, q = np.ones((1, 1)), np.zeros((1, 1))
    for seconds in (6300., 600., 300.):
        _, m, fq, _ = S.variable(inc[:1], [[12.]], 10., m, q, 123,
                                 lengths=[round(seconds/S.DT)], beta=0.)
        q = fq[:, 0]
        assert q[0, 0] == pytest.approx(2*(6300 if seconds == 6300 else 6900 if seconds == 600 else 7200),
                                            rel=1e-10)


def test_projection_counts_all_three_regimes_two_days_and_full_kr():
    records = [dict(regime=r, N=2, K=64, R_dec=64, R_eval=128,
                    timings=dict(warmup=dict(CPU_s=t, wall_s=t)))
               for r in ['DAY1', 'DAY2', 'DAY3'] for t in [1., 3.]]
    p = A.project(records, 50)
    assert p['projected_CPU_s'] == 3*2*100*50
    assert p['ideal_wall_s_20_workers'] == p['projected_CPU_s']/20
    assert p['slower_day_projected_CPU_s'] == 3*3*100*50
    records[0]['K'] = 4
    with pytest.raises(ValueError, match='fixed full K/R'):
        A.project(records, 50)
