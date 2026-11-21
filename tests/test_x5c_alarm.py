"""Doan Van Tai — X5c bitwise reduction, selected link, eta and run guards."""
import json
import os
from pathlib import Path
import subprocess

import numpy as np
import pytest

from experiments.letter import x5_alarm as A
from experiments.letter import x5c_alarm as C

B = C.B


def forbidden(*args, **kwargs):
    pytest.fail('unexpected engine/test-data/future access')


def toy():
    data = dict(dates=np.array(['2005-06-16']), days=np.ones((1, 24, 1)), warm=np.ones((1, 8, 1)))
    arrays = dict(incidence=np.array([[[[1.], [0.]], [[0.], [1.]]]]),
        capacity=np.array([[10., 20.]]), profiles=np.ones((2, 24, 1)))
    config = dict(train_dates=['2005-05-05'], regimes=[dict(id='NEWB1', managed_index=0,
        e_star_index=1, path_bottleneck_indices_after=[0, 1])])
    record = dict(regime='NEWB1', set='X4b', split='test', date='2005-06-16', stratum='S', status='PLANNED')
    return data, arrays, config, record


def test_same_estar_and_eta_reduces_bitwise_to_x5():
    config = B.C.read_json(B.OUT / 'configuration.json')
    arrays = B.read_npz(B.OUT / 'configuration.npz')
    record = next(r for r in B.planned_truth_records(B.OUT)
                  if (r['regime'], r['date']) == ('NEWB3', '2005-08-29'))
    token = B.C.VerifiedLock(str(B.OUT / 'configuration.json'), B.C.sha256(B.OUT / 'configuration.json'))
    data, excluded = B.V3.load_days([record['date']], config, verified=token)
    assert not excluded
    # Negative slope selects e*: force the SAME slope/streams in both paths.
    streams = A.seeds_for(A.PILOT_SEED, record['regime'], record['date'])
    expected, _ = A.decision_record_x5(data, arrays, config, record, -1.,
        seed=A.PILOT_SEED, m=8, n=8, k=2, streams=streams)
    got, meta = C.decision_record_x5c(data, arrays, config, record, -1., arm='A',
        seed=A.PILOT_SEED, m=8, n=8, k=2, streams=streams)
    assert expected.keys() == got.keys() and meta['status'] == 'SELECTED'
    for key in expected:
        assert got[key].dtype == expected[key].dtype and got[key].shape == expected[key].shape
        assert got[key].tobytes() == expected[key].tobytes(), key
    assert meta['alarm_link_index'] == meta['e_star_index'] == 27
    assert meta['runtime_beta'] == dict.fromkeys(meta['runtime_beta'], .3)


@pytest.mark.parametrize('slope,link,action,threshold', [(-2., 1, 'Switch', .02),
    (2., 0, 'Stay', .01), (0., 0, 'Stay', .01)])
def test_link_and_threshold_follow_slope_and_own_capacity(slope, link, action, threshold):
    _, arrays, config, _ = toy()
    spec = C.alarm_spec(config['regimes'][0], arrays['capacity'][0], slope)
    assert spec == dict(alarm_link_index=link, alarm_action=action,
        alarm_threshold_Mbit=threshold, s_hat_Mbit=slope)


@pytest.mark.parametrize('slope,link', [(1., 0), (-1., 1)])
@pytest.mark.parametrize('alarms', [0, 7, 8, 10])
def test_selected_link_queue_order_and_stale_alignment(monkeypatch, slope, link, alarms):
    data, arrays, config, record = toy()
    m, n = 12, 8
    marked = np.array([0, 2, 3, 4, 5, 6, 7, 9, 10, 11])[:alarms]
    modes = np.where(np.arange(m) % 2, 1., -1.)[:, None]
    queues = np.zeros((m, 2))
    queues[marked, link] = .001 * arrays['capacity'][0, link]
    stale = {tau: (-modes, queues + tau + np.arange(m)[:, None]) for tau in C.S.TAU_SECONDS}
    monkeypatch.setattr(C.S, 'warm_instances', lambda *args: ((modes, queues), stale))
    monkeypatch.setattr(C.S, 'forward_posterior',
        lambda inc, demand, cap, state, tau, k, seed: tuple(np.repeat(v, k, axis=0) for v in state))
    monkeypatch.setattr(B, 'mean_forecast', lambda inc, profile, cap, mo, qu, hs: np.zeros((len(mo), 2, len(hs))))
    monkeypatch.setattr(C.S, 'variable', forbidden)
    raw, meta = C.decision_record_x5c(data, arrays, config, record, slope,
        arm='A', seed=7100001, m=m, n=n, k=2)
    indices = marked[:n]
    assert meta['alarm_link_index'] == link and meta['e_star_index'] == 1
    assert meta['alarms'] == alarms and meta['selected_indices'] == indices.tolist()
    assert meta['alarm_threshold_Mbit'] == .001 * arrays['capacity'][0, link]
    assert meta['status'] == ('ALARM_RARE' if alarms < 8 else 'SELECTED')
    np.testing.assert_array_equal(raw['fresh_queues'], queues[indices])
    for i, tau in enumerate(C.S.TAU_SECONDS):
        np.testing.assert_array_equal(raw['stale_modes'][:, i], stale[tau][0][indices])
        np.testing.assert_array_equal(raw['stale_queues'][:, i], stale[tau][1][indices])
    assert config['regimes'][0]['e_star_index'] == 1
    assert 'alarm_threshold_Mbit' not in config['regimes'][0]


def test_eta_defaults_restore_and_affect_actual_simulation():
    old = C.S.BETA, C.S.variable.__kwdefaults__, C.X.expected_loads.__kwdefaults__
    with C.simulator_arm('A'):
        a = C._beta_probe(None)
    with C.simulator_arm('B'):
        b = C._beta_probe(None)
        assert C.X.expected_loads(np.ones(1), np.ones((1, 1)))[0, 0] == 1.6
    assert a['queue_Mbit'] == 0 and b['queue_Mbit'] == pytest.approx(.01)
    assert a['runtime_beta'] == dict.fromkeys(a['runtime_beta'], .3)
    assert b['runtime_beta'] == dict.fromkeys(b['runtime_beta'], .6)
    assert (C.S.BETA, C.S.variable.__kwdefaults__, C.X.expected_loads.__kwdefaults__) == old


def test_eta_really_applies_in_spawned_workers(tmp_path):
    values = C.run_jobs(C._beta_probe, [None, None], None, tmp_path, 2, 'B')
    assert all(v['pid'] != os.getpid() for v in values)
    assert all(v['runtime_beta'] == dict.fromkeys(v['runtime_beta'], .6) for v in values)
    assert all(v['queue_Mbit'] == pytest.approx(.01) for v in values)
    assert C.S.BETA == .3 and C.S.variable.__kwdefaults__['beta'] == .3


def test_eta_applies_to_mean_model_endpoint_and_warm_certificate(monkeypatch):
    inc = np.ones((2, 1, 1))
    modes, queues = np.ones((1, 1)), np.zeros((1, 1))
    with C.simulator_arm('A'):
        a = B.mean_forecast(inc, np.ones((1, 1)), np.array([1.4]), modes, queues, [.05])
    with C.simulator_arm('B'):
        b = B.mean_forecast(inc, np.ones((1, 1)), np.array([1.4]), modes, queues, [.05])
    assert not a.any() and np.all(b > 0)
    np.testing.assert_allclose(b, np.full((1, 2, 1), .00025))
    calls = []
    def variable(inc, demand, cap, mo, qu, seed, **kwargs):
        calls.append(C.runtime_beta())
        return None, mo, (qu + 1)[:, None, :], None
    monkeypatch.setattr(C.S, 'variable', variable)
    with C.simulator_arm('A'):
        fresh, _ = C.S.warm_instances(inc, np.ones((8, 1)), np.array([1.4]), 1, 1)
        assert not calls and not fresh[1].any()
    with C.simulator_arm('B'):
        fresh, _ = C.S.warm_instances(inc, np.ones((8, 1)), np.array([1.4]), 1, 1)
        assert len(calls) == 3 and fresh[1][0, 0] == 3
        assert all(v == dict.fromkeys(v, .6) for v in calls)


def test_train_worker_calls_original_method_with_new_seed_namespace(monkeypatch, tmp_path):
    saved = B._CONTEXT, B.TRAIN_SEED, B.seeds_for, C.X.publish
    record = dict(regime='NEWB1', date='2005-05-05', split='train')
    def train(r):
        assert r == record and B.TRAIN_SEED == 7200005
        assert set(B._CONTEXT[0][0]) == {'train'}
        assert B._CONTEXT[1] == tmp_path / 'train'
        assert B.seeds_for(7200005, r['regime'], r['date']) == C.seeds_for(7200005, r['regime'], r['date'], arm='B')
        assert C.runtime_beta() == dict.fromkeys(C.runtime_beta(), .6)
        return dict(s_hat_Mbit=1.)
    monkeypatch.setattr(B, 'train_record', train)
    assert C.run_jobs(C._train_worker, [record], (dict(train={}), {}, {}), tmp_path, 1, 'B') == [dict(s_hat_Mbit=1.)]
    assert (B._CONTEXT, B.TRAIN_SEED, B.seeds_for, C.X.publish) == saved


def test_b_training_persisted_before_test_plan_access(monkeypatch, tmp_path):
    out = tmp_path / 'arm_B'
    slopes = {'NEWB1': 1., 'NEWB2': -1., 'NEWB3': 0.}
    monkeypatch.setattr(C, 'BRIEF_SNAPSHOT', tmp_path / 'brief.md')
    monkeypatch.setattr(C, 'source_paths', lambda: {})
    def training(config, arrays, dest, workers):
        assert dest == out and not (dest / 'configuration.json').exists()
        result = dict(complete=True, s_hat_pooled_Mbit=slopes)
        C.C.write_json(dest / 'train/summary.json', result)
        return result
    monkeypatch.setattr(C, '_training', training)
    original = B.planned_truth_records
    def plan(directory):
        assert C.C.read_json(out / 'train/summary.json')['s_hat_pooled_Mbit'] == slopes
        return original(directory)
    monkeypatch.setattr(B, 'planned_truth_records', plan)
    monkeypatch.setattr(B.V3, 'load_days', forbidden)
    result = C.configure('B', out)
    assert result['status'] == 'CONFIGURED'
    config = C.C.read_json(out / 'configuration.json')
    assert config['s_hat_pooled_Mbit'] == slopes and config['parameters']['beta'] == .6
    assert config['train_summary_sha256'] == C.C.sha256(out / 'train/summary.json')
    before = (out / 'configuration.json').read_bytes()
    with pytest.raises(FileExistsError):
        C.configure('B', out)
    assert (out / 'configuration.json').read_bytes() == before


def test_b_local_training_stop_never_reads_test_plan(monkeypatch, tmp_path):
    monkeypatch.setattr(C, 'BRIEF_SNAPSHOT', tmp_path / 'brief.md')
    monkeypatch.setattr(C, 'source_paths', lambda: {})
    monkeypatch.setattr(C, '_training', lambda *args: dict(complete=False, status='LOCAL_RUNTIME_LIMIT'))
    monkeypatch.setattr(B, 'planned_truth_records', forbidden)
    monkeypatch.setattr(B.V3, 'load_days', forbidden)
    assert C.configure('B', tmp_path / 'arm')['status'] == 'LOCAL_RUNTIME_LIMIT'
    assert not (tmp_path / 'arm/configuration.json').exists()


def test_training_creates_fresh_arm_parent_before_first_worker(monkeypatch, tmp_path):
    config = B.C.read_json(B.OUT / 'configuration.json')
    arrays = B.read_npz(B.OUT / 'configuration.npz')
    out = tmp_path / 'new_arm_B'
    calls = []
    def jobs(fn, records, context, dest, workers, arm):
        assert (out / 'train/started.json').is_file()
        assert set(context[0]) == {'train'} and arm == 'B'
        calls.extend(records)
        return [dict(r, s_hat_Mbit=42., CPU_s=1., wall_s=1.) for r in records]
    monkeypatch.setattr(C, 'run_jobs', jobs)
    monkeypatch.setattr(B.V3, 'load_days', forbidden)
    result = C._training(config, arrays, out, 8)
    assert result['complete'] and len(calls) == 78
    assert result['s_hat_pooled_Mbit'] == dict.fromkeys(('NEWB1', 'NEWB2', 'NEWB3'), 42.)
    assert (out / 'train/summary.json').is_file()


def test_seed_namespaces_are_disjoint_from_x5_and_each_other():
    seen = set()
    for arm in ('A', 'B'):
        setting = C.arm_settings(arm)
        for seed in [v for k, v in setting.items() if k.endswith('_seed')]:
            for regime in ('NEWB1', 'NEWB2', 'NEWB3'):
                streams = C.seeds_for(seed, regime, '2005-06-16', arm=arm)
                old = A.seeds_for(seed, regime, '2005-06-16')
                for key in streams.keys() - {'base'}:
                    assert streams[key] != old[key] and streams[key] not in seen
                    seen.add(streams[key])


@pytest.mark.parametrize('arm', ['A', 'B'])
def test_truth_refuses_missing_lock_before_data(monkeypatch, tmp_path, arm):
    monkeypatch.setattr(C, 'load_context', forbidden)
    with pytest.raises(ValueError, match='lock required'):
        C.truth(arm, tmp_path)
    assert not (tmp_path / 'truth').exists()


@pytest.mark.parametrize('arm', ['A', 'B'])
def test_truth_refuses_failed_arm_gate_before_data(monkeypatch, tmp_path, arm):
    monkeypatch.setattr(C, 'verify_lock', lambda *args: C.C.VerifiedLock('fake', 'digest'))
    monkeypatch.setattr(C, 'check_sources', lambda *args: {})
    monkeypatch.setattr(C, 'load_context', forbidden)
    C.C.write_json(tmp_path / 'step0/summary.json', dict(complete=True, gate=dict(verdict='NOT_ENOUGH_SIGNAL')))
    with pytest.raises(ValueError, match='NOT_ENOUGH_SIGNAL'):
        C.truth(arm, tmp_path)
    assert not (tmp_path / 'truth').exists()


@pytest.mark.parametrize('command', ['pilot', 'lock'])
def test_failed_gate_also_refuses_pilot_and_lock(monkeypatch, tmp_path, command):
    monkeypatch.setattr(C, 'check_sources', lambda *args: {})
    monkeypatch.setattr(C, 'load_context', forbidden)
    C.C.write_json(tmp_path / 'step0/summary.json', dict(complete=True, gate=dict(verdict='NOT_ENOUGH_SIGNAL')))
    fn = C.pilot if command == 'pilot' else C.create_lock
    with pytest.raises(ValueError, match='NOT_ENOUGH_SIGNAL'):
        fn('A', tmp_path)


@pytest.mark.parametrize('overrides', [dict(m=513), dict(n=31), dict(k=63), dict(r_dec=63),
    dict(r_eval=127), dict(min_alarms=7), dict(alarm_threshold=0.), dict(streams={}),
    dict(horizons=[300]), dict(seed=7200001)])
def test_truth_rejects_overrides_before_engine(monkeypatch, tmp_path, overrides):
    token = C.C.VerifiedLock('fake', 'digest')
    monkeypatch.setattr(C, 'verify_lock', lambda *args: token)
    monkeypatch.setattr(C, 'require_signal', lambda *args: {})
    monkeypatch.setattr(C, 'decision_record_x5c', forbidden)
    with pytest.raises(ValueError, match='cannot override'):
        C.outcome_record_x5c(None, toy()[3], {}, arm='A', stage='truth',
            verified=token, out=tmp_path, **overrides)


def test_lock_detects_source_or_arm_or_seed_drift(monkeypatch, tmp_path):
    code = tmp_path / 'code.py'
    code.write_text('original')
    monkeypatch.setattr(C, 'lock_paths', lambda out: dict(code=code))
    monkeypatch.setattr(C, 'check_sources', lambda *args: {})
    monkeypatch.setattr(C, 'require_signal', lambda *args: {})
    value = dict(schema=C.LOCK_SCHEMA, arm='A', parameters=C.parameters('A'), sha256=dict(code=C.C.sha256(code)))
    path = tmp_path / 'lock.json'
    path.write_text(json.dumps(value))
    assert isinstance(C.verify_lock('A', tmp_path), C.C.VerifiedLock)
    with pytest.raises(ValueError, match='lock mismatch'):
        C.verify_lock('B', tmp_path)
    value['parameters']['test_seed'] += 1
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match='lock mismatch'):
        C.verify_lock('A', tmp_path)
    value['parameters'] = C.parameters('A')
    path.write_text(json.dumps(value))
    code.write_text('changed')
    with pytest.raises(ValueError, match='lock mismatch'):
        C.verify_lock('A', tmp_path)


def test_parameter_drift_rejected_before_sources(monkeypatch, tmp_path):
    params = C.parameters('B')
    params['test_seed'] = 1
    C.C.write_json(tmp_path / 'configuration.json', dict(schema='x5c-alarm-configuration-v1', arm='B', parameters=params))
    monkeypatch.setattr(C, 'source_paths', forbidden)
    with pytest.raises(ValueError, match='seed/parameter'):
        C.check_sources(tmp_path, 'B')


def test_truth_one_shot_never_overwrites_directory(monkeypatch, tmp_path):
    monkeypatch.setattr(C, 'verify_lock', lambda *args: C.C.VerifiedLock('fake', 'digest'))
    monkeypatch.setattr(C, 'validate_preparation', lambda *args: {})
    monkeypatch.setattr(C, 'planned_truth_records', lambda *args: [toy()[3]])
    monkeypatch.setattr(C, 'load_context', forbidden)
    (tmp_path / 'truth').mkdir()
    with pytest.raises(FileExistsError):
        C.truth('A', tmp_path)


def test_truth_checks_all_step0_arrays_before_rollouts(monkeypatch, tmp_path):
    token = C.C.VerifiedLock('fake', 'digest')
    record = toy()[3]
    monkeypatch.setattr(C, 'verify_lock', lambda *args: token)
    monkeypatch.setattr(C, 'require_signal', lambda *args: {})
    monkeypatch.setattr(C, 'planned_truth_records', lambda *args: [record])
    monkeypatch.setattr(C.S, 'variable', forbidden)
    B.npz(tmp_path / f"step0/test/{record['regime']}_{record['date']}.npz", dict(fresh_modes=np.ones((8, 1))))
    monkeypatch.setattr(C, 'decision_record_x5c', lambda *args, **kwargs:
        (dict(fresh_modes=np.zeros((8, 1))), dict(status='SELECTED')))
    with pytest.raises(ValueError, match='truth differs from step0: fresh_modes'):
        C.outcome_record_x5c((dict(test={}), {}, {}), record, {'NEWB1': -1.},
            arm='A', stage='truth', out=tmp_path, verified=token)


@pytest.mark.parametrize('fail_a', [False, True])
def test_gcp_both_arms_have_separate_logs_and_one_final_shutdown(tmp_path, fail_a):
    # Shell harness: every python/timeout/sudo executable is a local stub.
    # No experiment truth, SSH, cloud call or real poweroff is executed.
    bindir = tmp_path / 'bin'
    bindir.mkdir()
    capture = tmp_path / 'capture'
    capture.write_text('')
    scripts = {
        'python3': '#!/bin/bash\nprintf "%s\\n" "$*" >>"$CAPTURE"\n'
                   'if [[ "$*" == *"verify-lock --arm A"* && "$FAIL_A" == 1 ]]; then exit 7; fi\n',
        'timeout': '#!/bin/bash\nshift 3\nexec "$@"\n',
        'sudo': '#!/bin/bash\nprintf "SHUTDOWN\\n" >>"$CAPTURE"\n'}
    for name, content in scripts.items():
        p = bindir / name
        p.write_text(content)
        p.chmod(0o755)
    for path in ('.venv/bin/activate', 'experiments/explore_ctmc/env.sh'):
        p = tmp_path / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('true\n')
    for arm in ('A', 'B'):
        (tmp_path / f'results/letter/x5c_alarm/arm_{arm}').mkdir(parents=True)
    env = dict(os.environ, SMR_REPO=str(tmp_path), ARMS='A B', CAPTURE=str(capture),
               FAIL_A=str(int(fail_a)), PATH=str(bindir) + os.pathsep + os.environ['PATH'])
    proc = subprocess.run(['bash', str(C.ROOT / 'experiments/letter/x5c_gcp.sh')], env=env, capture_output=True, text=True)
    assert proc.returncode == (7 if fail_a else 0), proc.stderr
    lines = capture.read_text().splitlines()
    assert lines.count('SHUTDOWN') == 1 and lines[-1] == 'SHUTDOWN'
    assert any('truth --arm B --workers 30' in line for line in lines)
    assert any('truth --arm A' in line for line in lines) != fail_a
    for arm in ('A', 'B'):
        log = (tmp_path / f'results/letter/x5c_alarm/arm_{arm}/truth_pipeline.log').read_text()
        assert log.count('PIPELINE_START') == 1 and log.count('PIPELINE_EXIT') == 1
