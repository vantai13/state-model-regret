"""Doan Van Tai — analytic, chronological-split and CRN checks for S1-C."""
import json

import numpy as np
import pytest

from experiments.ext_validity import packet as P
from experiments.letter import sweep_trace as S


def toy_trace():
    x = np.tile(np.r_[np.ones(100), np.full(100, 8.)], 40)
    return dict(counts=[x, np.roll(x, 50)], dt=.1, cut=4000, train_means=[4.5, 4.5],
                train_s=400., test_s=400., duration_s=800.)


def case(u=1.):
    return dict(id='toy', trace='ditl_20230412', scale=1., lam=[6.5, 6.8], mu=[10., 11.], u=u)


def test_test_tail_cannot_change_training(tmp_path):
    a, b = tmp_path/'a.npz', tmp_path/'b.npz'
    # Use identical train prefixes on both paths, radically different test.
    for path, tail in ((a, 1.), (b, 100000.)):
        x = np.r_[np.tile([1., 4., 6., 2.], 50), np.full(200, tail), 1.]
        with path.open('xb') as f:
            np.savez(f, s0=x, s1=x*2, metadata=json.dumps({'bin': 1.}))
    ta, tb = S.load_trace(a), S.load_trace(b)
    assert ta['train_means'] == tb['train_means'] == [3.25, 6.5]
    aa, bb = S.train_model(ta, case(), 123), S.train_model(tb, case(), 123)
    aa.pop('CPU_s'); bb.pop('CPU_s')
    assert aa == bb
    ba, bc = S.make_tape(ta, case(), True, 12), S.make_tape(tb, case(), True, 12)
    for x, y in zip(ba.bg, bc.bg):
        np.testing.assert_array_equal(x, y)


def test_tail_not_renormalized_and_no_periodic_wrap():
    rng = np.random.default_rng(71)
    counts = np.r_[np.ones(1000), np.full(1000, 20.)]
    draws = S.cox_segment(counts, .1, 1000, 2000, 1., 10., rng)
    assert len(draws) == pytest.approx(20000, rel=.03)
    assert 0 <= draws[0] < draws[-1] < 100.
    with pytest.raises(ValueError):
        S.cox_segment(counts, .1, 1500, 2500, 1., 10., rng)


@pytest.mark.parametrize('mu', [(10., 10.), (9.5, 10.5), (7., 8.)])
def test_fluid_matches_direct_integral_and_exact_ties(mu):
    q = np.array([[0., 0.], [1., 7.], [1000., 1000.], [10., 0.]])
    lam, u, h = [6.5, 6.8], 1., 2.
    def integral(q, load, capacity):
        d = load-capacity
        end = np.minimum(h, q/-d) if d < 0 else h
        return q*end + d*end*end/2
    expected = integral(q[:, 0], lam[0], mu[0])-integral(q[:, 0], lam[0]+u, mu[0])
    expected += integral(q[:, 1], lam[1]+u, mu[1])-integral(q[:, 1], lam[1], mu[1])
    np.testing.assert_allclose(S.fluid_gap(q, lam, mu, u, h), expected, atol=1e-12)
    assert S.fluid_gap(q, lam, mu, u, h)[2] == 0.
    if mu == (10., 10.):
        legacy = dict(lamA=lam[0], lamB=lam[1], u=u)
        np.testing.assert_array_equal(S.fluid_gap(q, lam, mu, u, h), P.fluid_gap(q, legacy, h))


def test_lindley_cost_and_pending_residuals():
    initial = np.array([.5, .6])
    at, services, h = np.array([.2, .4, 1.8]), np.array([.7, .3, .8]), 2.
    expected = P.lindley_cost(np.array([2]), at[None, :], services[None, :], initial[None, :], h)[0]
    assert S.path_cost(initial, at, services, h) == pytest.approx(expected, abs=1e-14)
    run = (np.array([0., .1, 1.8]), np.array([.5, 1.1, 2.6]), np.array([.5, .6, .8]))
    np.testing.assert_array_equal(S.pending_services(run, .2), [.3, .6])
    np.testing.assert_allclose(S.pending_services(run, .5), [.6], rtol=0, atol=2e-16)
    assert not len(S.pending_services(run, 1.5))


def test_tape_replay_reproduces_action_zero_history():
    c = case()
    tape = S.make_tape(toy_trace(), c, False, 88)
    runs = S.history(tape, c, 0)
    # This is a full pathwise identity, including unfinished packets and
    # residual services, rather than merely matching a Monte Carlo mean.
    for t, h in ((0., .5), (10., 3.), (100., 50.)):
        direct = sum(S.occupation(r, t, t+h) for r in runs)
        assert S.replay_costs(tape, runs, c, t, h)[0] == pytest.approx(direct, abs=1e-9)
    with pytest.raises(ValueError):
        S.replay_costs(tape, runs, c, 390., 20.)


def test_u_zero_crn_and_nested_horizons():
    c = case(u=0.)
    tape = S.make_tape(toy_trace(), c, False, 89)
    runs = S.history(tape, c, 0)
    short = S.replay_costs(tape, runs, c, 12., 5.)
    long = S.replay_costs(tape, runs, c, 12., 10.)
    assert short[0] == short[1] and long[0] == long[1]
    np.testing.assert_array_less(short, long)
    assert S.fluid_gap([3., 7.], c['lam'], c['mu'], 0., 5.) == 0.


def test_decision_grid_is_past_only_and_finite():
    ts = S.decision_times(1000., 10., 24, 300.)
    assert len(ts) == 24 and ts[0] == 320. and ts[-1] == 997.
    assert np.all(ts-300. >= 20.)
    assert not len(S.decision_times(300., 10., 24, 300.))


def test_blocks_not_points_and_single_day_has_no_ci():
    rows = [dict(block=b, delta_static_minus_hybrid=v) for b, v in [(0, 1.), (0, 3.), (1, 6.)]]
    r = S.cluster_ci(rows)
    assert r['n_clusters'] == 2 and r['mean'] == 4.
    assert r['low'] < 4 < r['high']
    assert S.cluster_ci(rows[:2])['low'] is None


def test_summary_has_whole_population_paired_regret(tmp_path):
    c = case()
    (tmp_path/'toy').mkdir()
    rows = []
    for i, (rs, rh, cref, alarm) in enumerate([(4., 1., 2., True), (0., 0., 3., False), (1., 2., 5., True)]):
        rows.append(dict(case_id='toy', trace=c['trace'], block=i, h_mult=.3, tau_s=0.,
            regret_M0=8., regret_static=rs, regret_hybrid=rh, C_ref=cref,
            delta_static_minus_hybrid=rs-rh, alarm=alarm, disagreement=rs != rh, M0_tie=i == 1))
    S.write_csv(tmp_path/'toy/decisions.csv', rows)
    receipt = dict(case=c, support=[dict(h_mult=.3, h_s=3., n_candidates=3),
                                   dict(h_mult=10., h_s=100., n_candidates=0)])
    table = S.summarize([receipt], tmp_path, dict(taus_s=[0.]))
    uniform, alarm, missing, _ = table
    assert uniform['n'] == 3 and uniform['mean_delta'] == pytest.approx(2/3)
    assert uniform['n_disagreement'] == 2 and uniform['disagreement_share'] == pytest.approx(2/3)
    assert uniform['mean_delta_when_disagree'] == 1.
    assert alarm['n'] == 2 and alarm['mean_delta'] == 1.
    assert missing['status'] == 'NOT_EVALUABLE' and missing['mean_delta'] is None
    import csv
    days = list(csv.DictReader((tmp_path/'day_summary.csv').open()))
    assert days[0]['n_days'] == '1' and days[0]['ci_low'] == ''


def test_no_overwrite_or_outside_outputs(tmp_path):
    p = tmp_path/'new.json'
    S.write_json(p, {'x': 1})
    with pytest.raises(FileExistsError):
        S.write_json(p, {'x': 2})
    assert json.loads(p.read_text()) == {'x': 1}
    with pytest.raises(ValueError):
        S.output_path(S.ROOT/'results/other')


def test_simulation_train_saved_before_test_and_exact_policy_pairing(tmp_path, monkeypatch):
    trace = toy_trace()
    monkeypatch.setattr(S, 'load_trace', lambda *a: trace)
    monkeypatch.setattr(S, 'train_model', lambda *a: dict(T_int=2., T_int_censored=False, s_hat=-.3,
        static_action=1, alarm_threshold_packets=1., CPU_s=0.))
    original = S.make_tape
    def checked_tape(*args, **kwargs):
        assert (tmp_path/'record/training.json').exists()
        return original(*args, **kwargs)
    monkeypatch.setattr(S, 'make_tape', checked_tape)
    plan = dict(train_fraction=.5, pilot_seed=1, full_seed=2, pilot_points=4, full_points=8,
                taus_s=[0., 1.], h_mult=list(S.H_MULT))
    r = S.simulate_case(case(), plan, 'pilot', tmp_path/'record')
    assert r['status'] == 'COMPLETE' and r['rows'] > 0
    import csv
    rows = list(csv.DictReader((tmp_path/'record/decisions.csv').open()))
    for row in rows:
        cs = [float(row['cost_stay']), float(row['cost_switch'])]
        assert float(row['C_ref']) == min(cs)
        assert float(row['delta_static_minus_hybrid']) == pytest.approx(
            cs[int(row['action_static'])]-cs[int(row['action_hybrid'])])
        assert row['action_M0'] == str(int(float(row['fluid_gap']) < 0))
        assert row['action_hybrid'] == str(int(float(row['hybrid_gap']) < 0))
    for a, b in zip(rows[::2], rows[1::2]):
        assert a['cost_stay'] == b['cost_stay'] and a['cost_switch'] == b['cost_switch']


def test_censored_timescale_emits_all_missing_cells(tmp_path, monkeypatch):
    monkeypatch.setattr(S, 'load_trace', lambda *a: toy_trace())
    monkeypatch.setattr(S, 'train_model', lambda *a: dict(T_int=10., T_int_censored=True, CPU_s=0.))
    monkeypatch.setattr(S, 'make_tape', lambda *a: pytest.fail('test must not be simulated'))
    plan = dict(train_fraction=.5, pilot_seed=1, pilot_points=4, h_mult=list(S.H_MULT))
    r = S.simulate_case(case(), plan, 'pilot', tmp_path/'censored')
    assert r['status'] == 'NOT_EVALUABLE' and r['rows'] == 0 and len(r['support']) == 7


def test_content_check_detects_mutation(tmp_path, monkeypatch):
    src = tmp_path/'source'
    src.write_text('original')
    plan = dict(schema='S1-C-v1', h_mult=list(S.H_MULT), taus_s=list(S.TAUS),
                source_sha256={'source': S.sha(src)}, trace_sha256={})
    path = tmp_path/'plan.json'
    S.write_json(path, plan)
    monkeypatch.setattr(S, 'ROOT', tmp_path)
    assert S.verify_plan(path) == plan
    src.write_text('changed')
    with pytest.raises(ValueError, match='changed input'):
        S.verify_plan(path)


def test_gcp_entrypoint_uses_15_workers():
    script = (S.ROOT/'experiments/letter/sweep_trace_gcp.sh').read_text()
    assert '--workers 15' in script and 'noclobber' in script
    assert '\nssh ' not in script and '\npoweroff' not in script and '\nshutdown' not in script


def test_empty_pilot_cannot_be_a_runtime_benchmark():
    plan = dict(cases=[{}]*27, full_points=128, pilot_points=24)
    missing = S.runtime_projection(.2, .1, 0, plan)
    assert missing['status'] == 'NOT_ESTIMABLE' and missing['CPU_hours'] is None
    measured = S.runtime_projection(2., .5, 100, plan)
    expected_cpu = 27*(.5+1.5*128/24)
    assert measured['CPU_hours'] == expected_cpu/3600
    assert measured['ideal_wall_hours_15_workers'] == expected_cpu/3600/15
