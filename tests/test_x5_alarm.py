"""Doan Van Tai — X5 selection, X4b reduction, card boundaries and guards."""
import json

import numpy as np
import pytest

from experiments.letter import x4b as B
from experiments.letter import x5_alarm as A
from experiments.letter import x5_alarm_card as C


def forbidden(*args, **kwargs):
    pytest.fail('unexpected data/engine/future call')


def toy():
    data = dict(dates=np.array(['2005-06-16']), days=np.ones((1, 24, 1)), warm=np.ones((1, 8, 1)))
    arrays = dict(incidence=np.array([[[[1.], [0.]], [[0.], [1.]]]]),
        capacity=np.array([[10., 10.]]), profiles=np.ones((2, 24, 1)))
    config = dict(train_dates=['2005-05-05'], regimes=[dict(id='NEWB1', managed_index=0,
        e_star_index=1, alarm_threshold_Mbit=1.)])
    record = dict(regime='NEWB1', set='X4b', split='test', date='2005-06-16', stratum='S', status='PLANNED')
    return data, arrays, config, record


def test_alarm_disabled_reduces_bitwise_to_x4b_on_real_record():
    config = B.C.read_json(B.OUT / 'configuration.json')
    arrays = B.read_npz(B.OUT / 'configuration.npz')
    record = B.planned_truth_records(B.OUT)[0]
    token = B.C.VerifiedLock(str(B.OUT / 'configuration.json'), B.C.sha256(B.OUT / 'configuration.json'))
    data, exclusions = B.V3.load_days([record['date']], config, verified=token)
    assert not exclusions
    streams = A.seeds_for(A.PILOT_SEED, record['regime'], record['date'])
    slopes = B.C.read_json(B.OUT / 'training_summary.json')['s_hat_pooled_Mbit']
    expected, _ = B.decision_record(data, arrays, config, record, slopes[record['regime']],
        seed=A.PILOT_SEED, n=8, k=2, streams=streams)
    got, meta = A.decision_record_x5(data, arrays, config, record, slopes[record['regime']],
        seed=A.PILOT_SEED, m=8, n=8, k=2, alarm_threshold=-np.inf, streams=streams)
    for key, value in expected.items():
        assert got[key].dtype == value.dtype and got[key].shape == value.shape
        assert got[key].tobytes() == value.tobytes(), key
    assert meta['N'] == 8 and meta['selected_indices'] == list(range(8))
    assert not meta['evaluation_called'] and not meta['C_ref_computed']


@pytest.mark.parametrize('alarms', [0, 7, 8, 10])
def test_selection_preserves_order_and_stale_trajectory_alignment(monkeypatch, alarms):
    data, arrays, config, record = toy()
    m, n, k = 12, 8, 2
    marked = np.array([0, 2, 3, 4, 5, 6, 7, 9, 10, 11])[:alarms]
    modes = np.where(np.arange(m) % 2, 1., -1.)[:, None]
    queues = np.zeros((m, 2)); queues[marked, 1] = 1.
    stale = {tau: ((-modes if tau == 300. else modes), queues+tau+np.arange(m)[:, None])
             for tau in A.S.TAU_SECONDS}
    def warm(inc, demands, cap, count, seed):
        assert count == m
        return (modes, queues), stale
    calls = []
    def posterior(inc, demand, cap, state, tau, count, seed):
        calls.append((tau, tuple(v.copy() for v in state)))
        return tuple(np.repeat(v, count, axis=0) for v in state)
    monkeypatch.setattr(A.S, 'warm_instances', warm)
    monkeypatch.setattr(A.S, 'forward_posterior', posterior if alarms >= 8 else forbidden)
    monkeypatch.setattr(B, 'mean_forecast',
        (lambda inc, profile, cap, mo, qu, hs: np.zeros((len(mo), 2, len(hs)))) if alarms >= 8 else forbidden)
    monkeypatch.setattr(B, 'paired_metrics', forbidden)
    monkeypatch.setattr(A.S, 'variable', forbidden)
    raw, meta = A.decision_record_x5(data, arrays, config, record, -1., seed=A.TEST_SEED, m=m, n=n, k=k)
    indices = marked[:n]
    assert meta['candidates'] == m and meta['alarms'] == alarms
    assert meta['selected_indices'] == indices.tolist()
    np.testing.assert_array_equal(raw['fresh_modes'], modes[indices])
    np.testing.assert_array_equal(raw['fresh_queues'], queues[indices])
    for i, tau in enumerate(A.S.TAU_SECONDS):
        np.testing.assert_array_equal(raw['stale_modes'][:, i], stale[tau][0][indices])
        np.testing.assert_array_equal(raw['stale_queues'][:, i], stale[tau][1][indices])
    if alarms < 8:
        assert meta['status'] == 'ALARM_RARE' and 'decisions' not in raw and not calls
    else:
        assert meta['status'] == 'SELECTED' and len(raw['decisions']) == n
        for tau, state in calls:
            for got, expected in zip(state, stale[tau]):
                np.testing.assert_array_equal(got, expected[indices])
    assert {'V', 'C_ref', 'costs', 'regret'}.isdisjoint(raw)


def test_x5_seed_namespace_is_disjoint_and_labels_match_x4b():
    seen = []
    for seed in (A.TEST_SEED, A.PILOT_SEED):
        for regime in C.REGIMES:
            for date in ('2005-06-16', '2005-07-19'):
                streams = A.seeds_for(seed, regime, date)
                old = B.seeds_for(seed, regime, date)
                assert streams.keys() == old.keys()
                for key in streams.keys()-{'base'}:
                    assert streams[key] != old[key]
                    seen.append(streams[key])
    assert len(set(seen)) == len(seen)


@pytest.mark.parametrize('change, expected', [({}, 'SIGNAL_OK'),
    ({'numerator': 4}, 'NOT_ENOUGH_SIGNAL'), ({'records': 4}, 'NOT_ENOUGH_SIGNAL'),
    ({'h_s': 3600}, 'NOT_ENOUGH_SIGNAL'), ({'side': 'stale_300'}, 'NOT_ENOUGH_SIGNAL'),
    ({'denominator': 0}, 'NOT_ENOUGH_SIGNAL')])
def test_step0_gate_uses_fresh_regime_cell_and_exact_five_percent(change, expected):
    row = dict(regime='NEWB1', h_s=1800, side='fresh', records=5, numerator=5, denominator=100)
    assert A.signal_gate([dict(row, **change)])['verdict'] == expected


@pytest.mark.parametrize('mean, se, expected', [
    (-.05, 0., 'GAIN'), (.05, 0., 'LOSS'), (-.049999, 0., 'UNRESOLVED'),
    (.049999, 0., 'UNRESOLVED'), (-.05, .025, 'UNRESOLVED'),
    (.05, .025, 'UNRESOLVED'), (-.05, .024999, 'GAIN'), (.05, .024999, 'LOSS'),
    (0., 0., 'UNRESOLVED')])
def test_t1_gain_loss_boundaries(mean, se, expected):
    assert C.t1_reading(mean, se) == expected


@pytest.mark.parametrize('readings, expected', [
    (['GAIN', 'GAIN'], C.NA), (['GAIN', 'GAIN', 'UNRESOLVED'], C.STANDS),
    (['GAIN', 'UNRESOLVED', 'UNRESOLVED'], C.FALLS), (['GAIN', 'GAIN', 'LOSS'], C.FALLS),
    (['GAIN', 'GAIN', 'UNRESOLVED', 'UNRESOLVED'], C.STANDS),
    (['GAIN', 'GAIN', 'UNRESOLVED', 'UNRESOLVED', 'UNRESOLVED'], C.FALLS)])
def test_t1_card_verdict_and_ceiling_half(readings, expected):
    cells = [dict(eligible=True, reading=r, D_pp=-.1) for r in readings]
    assert C.t1_result(cells)['verdict'] == expected


def synthetic_records(*, days=5, mismatch_long=0, ties=0, gaps=None, bad=None):
    """Consistent action-gather raw; C_ref positive and X4b-evaluable."""
    n, hs = 20, B.H_SECONDS
    result = []
    gaps = {} if gaps is None else gaps
    for regime in C.REGIMES:
        for day in range(days):
            d = np.zeros((n, 3, 3, len(hs)), dtype=np.int16)
            d[:, 0] = 1
            d[:2, 2, 0, :-1] = 1
            d[:mismatch_long, 2, 0, -1] = 1
            if bad is not None and bad(regime, day):
                d[:, 1, 2, -1] = 1  # Only stale_900 fails: one record, not two age trials.
            flags = np.zeros_like(d, dtype=bool)
            flags[:ties, 0, 0] = True
            raw = dict(decisions=d, tie_flags=flags, h_seconds=hs,
                tau_seconds=np.array(B.S.TAU_SECONDS), pipelines=np.array(B.PIPES), sides=np.array(B.SIDES))
            evaluation = np.full((n, 2, 2, len(hs)), 1e6)
            evaluation[:, :, 1] += gaps.get(regime, .006)*1e6
            raw.update(B.paired_metrics(raw, evaluation.copy(), evaluation))
            meta = dict(regime=regime, set='X4b', date=f'2005-07-{day+1:02d}',
                candidates=512, alarms=20)
            result.append((raw, meta))
    return result


def test_card_on_consistent_raw_and_se_over_days_not_instances():
    inputs = synthetic_records()
    result = C.evaluate_raw(inputs)
    assert result['T1']['verdict'] == C.STANDS
    assert result['T1']['eligible_cells'] == 15 and result['T1']['counts']['GAIN'] == 15
    assert result['T2']['verdict'] == result['T3']['verdict'] == result['T4']['verdict'] == C.STANDS
    # Give days different paired percentages, then compare the daily ddof=1 SE.
    for index, (raw, _) in enumerate(inputs):
        raw['paired_Hybrid_minus_Stationary'][:, 0, 0] = -(index % 5 + 1)*1000
    cell = C.evaluate_raw(inputs)['T1']['cells'][0]
    assert cell['D_pp'] == pytest.approx(-.3)
    assert cell['SE_over_days_pp'] == pytest.approx(np.std([-.1, -.2, -.3, -.4, -.5], ddof=1)/np.sqrt(5))
    assert cell['days'] == 5


def test_t1_insufficient_days_and_disagreement():
    assert C.evaluate_raw(synthetic_records(days=4))['T1']['verdict'] == C.NA
    records = synthetic_records()
    for raw, _ in records:
        raw['decisions'][:, 2, 0, :-1] = 0
    assert C.evaluate_raw(records)['T1']['eligible_cells'] == 0


def test_t1_exact_five_percent_and_loss_from_raw():
    records = synthetic_records(gaps={r: .01 for r in C.REGIMES})
    for raw, _ in records:
        raw['decisions'][1:, 2, 0, :-1] = 0
        # Reverse the Hybrid/Stationary actions and recompute the action gather.
        raw['decisions'][:, [1, 2]] = raw['decisions'][:, [2, 1]]
        raw.update(B.paired_metrics(raw, raw['reference_decision_rollouts'], raw['paired_evaluation']))
    result = C.evaluate_raw(records)['T1']
    assert result['verdict'] == C.FALLS and result['eligible_cells'] == 15
    assert result['counts']['LOSS'] == 15
    assert all(r['disagreement_share'] == .05 and r['D_pp'] == .05 for r in result['cells'])


def test_t1_has_no_extra_evaluability_filter():
    records = synthetic_records()
    for raw, _ in records:
        raw['C_ref'][:] = 1.
    result = C.evaluate_raw(records)
    assert result['T1']['eligible_cells'] == 15 and result['T1']['verdict'] == C.STANDS
    assert result['T4']['verdict'] == C.NA


def test_t1_averages_daily_percentages_with_equal_day_weight():
    records = synthetic_records()
    for i, (raw, _) in enumerate(records):
        raw['C_ref'][:] = 1e6*(i % 5+1)
    first = C.evaluate_raw(records)['T1']['cells'][0]
    assert first['D_pp'] == pytest.approx(np.mean([-.06/(i+1) for i in range(5)]))


@pytest.mark.parametrize('mismatch, expected', [(1, C.STANDS), (2, C.FALLS)])
def test_t2_both_sides_of_95_percent(mismatch, expected):
    result = C.evaluate_raw(synthetic_records(mismatch_long=mismatch))['T2']
    assert result['verdict'] == expected and result['instances'] == 300
    assert result['share'] == pytest.approx(1-mismatch/20)


@pytest.mark.parametrize('ties, expected', [(2, C.STANDS), (3, C.FALLS)])
def test_t3_tie_threshold_counts_fresh_once_across_all_h(ties, expected):
    result = C.evaluate_raw(synthetic_records(ties=ties))['T3']
    assert result['verdict'] == expected
    assert result['tie_denominator'] == 15*20*7
    assert result['tie_share'] == ties/20


@pytest.mark.parametrize('gaps, expected, over', [
    ({'NEWB1': .005}, C.STANDS, 2), ({'NEWB1': .005, 'NEWB2': .005}, C.FALLS, 1)])
def test_t3_regret_strict_half_percent_and_two_regimes(gaps, expected, over):
    result = C.evaluate_raw(synthetic_records(gaps=gaps))['T3']
    assert result['verdict'] == expected and result['regimes_over_half_percent'] == over


@pytest.mark.parametrize('extra_bad, expected, meets', [(False, C.STANDS, 12), (True, C.FALLS, 11)])
def test_t4_one_record_both_stale_ages_and_80_percent(extra_bad, expected, meets):
    result = C.evaluate_raw(synthetic_records(bad=lambda regime, day:
        day == 4 or (extra_bad and regime == 'NEWB1' and day == 3)))['T4']
    assert result['verdict'] == expected and result['meets'] == meets
    assert result['evaluable_records'] == 15


def test_t4_excludes_only_non_evaluable_record_and_keeps_negative_estimates():
    inputs = synthetic_records()
    raw, _ = inputs[0]
    raw['C_ref'][:, -1] = 1.
    raw['regret'][:, 0, 0, 0] = -2.
    result = C.evaluate_raw(inputs)
    assert result['T4']['evaluable_records'] == 14
    assert result['descriptive']['strict_fresh_M0']['signed_MC_estimates_preserved']
    assert result['descriptive']['strict_fresh_M0_by_h']['300']['regret_sum_Mbit_s'] == 14*20*6000-40
    assert 'SE_over_days_pp' in C.report(result)


def test_t4_regret_exact_half_percent_is_inclusive():
    records = synthetic_records(gaps={r: .005 for r in C.REGIMES}, bad=lambda *args: True)
    result = C.evaluate_raw(records)['T4']
    assert result['verdict'] == C.STANDS and result['meets'] == 15


def test_card_rejects_duplicate_raw_records():
    records = synthetic_records()
    with pytest.raises(ValueError, match='duplicate raw'):
        C.evaluate_raw(records+[records[0]])


def test_truth_refuses_missing_lock_before_loading_data(monkeypatch, tmp_path):
    monkeypatch.setattr(A, 'load_context', forbidden)
    with pytest.raises(ValueError, match='lock required'):
        A.truth(tmp_path)
    assert not (tmp_path / 'truth').exists()


def test_truth_refuses_no_signal_before_engine(monkeypatch, tmp_path):
    monkeypatch.setattr(A, 'verify_lock', lambda out: B.C.VerifiedLock('fake', 'digest'))
    monkeypatch.setattr(A, 'check_sources', lambda out: {})
    monkeypatch.setattr(A, 'load_context', forbidden)
    (tmp_path / 'step0').mkdir()
    (tmp_path / 'step0/summary.json').write_text(json.dumps(dict(complete=True, gate=dict(verdict='NOT_ENOUGH_SIGNAL'))))
    with pytest.raises(ValueError, match='NOT_ENOUGH_SIGNAL'):
        A.truth(tmp_path)
    assert not (tmp_path / 'truth').exists()


@pytest.mark.parametrize('command', ['pilot', 'lock'])
def test_no_signal_also_stops_pilot_and_lock(monkeypatch, tmp_path, command):
    monkeypatch.setattr(A, 'check_sources', lambda out: {})
    monkeypatch.setattr(A, 'load_context', forbidden)
    (tmp_path / 'step0').mkdir()
    (tmp_path / 'step0/summary.json').write_text(json.dumps(dict(complete=True, gate=dict(verdict='NOT_ENOUGH_SIGNAL'))))
    with pytest.raises(ValueError, match='NOT_ENOUGH_SIGNAL'):
        A.main([command, '--out', str(tmp_path)])


@pytest.mark.parametrize('overrides', [dict(m=513), dict(n=31), dict(k=63), dict(r_dec=63),
    dict(r_eval=127), dict(min_alarms=7), dict(alarm_threshold=0.), dict(streams={}), dict(horizons=[300])])
def test_truth_rejects_count_and_stream_overrides_before_engine(monkeypatch, tmp_path, overrides):
    token = B.C.VerifiedLock('fake', 'digest')
    monkeypatch.setattr(A, 'verify_lock', lambda out: token)
    monkeypatch.setattr(A, 'require_signal', lambda out: {})
    monkeypatch.setattr(A, 'decision_record_x5', forbidden)
    with pytest.raises(ValueError, match='cannot override'):
        A.outcome_record_x5(None, toy()[3], {}, stage='truth', verified=token, out=tmp_path, **overrides)


def test_invalid_stage_and_parameter_drift_are_rejected(monkeypatch, tmp_path):
    monkeypatch.setattr(A, 'decision_record_x5', forbidden)
    with pytest.raises(ValueError, match='explicit pilot or truth'):
        A.outcome_record_x5(None, toy()[3], {}, stage='step0')
    params = A.parameters(); params['M'] = 513
    (tmp_path / 'configuration.json').write_text(json.dumps(dict(schema='x5-alarm-configuration-v1', parameters=params)))
    with pytest.raises(ValueError, match='stage/count/parameter'):
        A.check_sources(tmp_path)


def test_truth_one_shot_refuses_existing_directory(monkeypatch, tmp_path):
    monkeypatch.setattr(A, 'verify_lock', lambda out: B.C.VerifiedLock('fake', 'digest'))
    monkeypatch.setattr(A, 'validate_preparation', lambda out: {})
    monkeypatch.setattr(A, 'planned_truth_records', lambda out: [toy()[3]])
    monkeypatch.setattr(A, 'load_context', forbidden)
    (tmp_path / 'truth').mkdir()
    with pytest.raises(FileExistsError):
        A.truth(tmp_path)


def test_truth_compares_entire_step0_before_rollout(monkeypatch, tmp_path):
    token = B.C.VerifiedLock('fake', 'digest')
    record = toy()[3]
    monkeypatch.setattr(A, 'verify_lock', lambda out: token)
    monkeypatch.setattr(A, 'require_signal', lambda out: {})
    monkeypatch.setattr(A, 'planned_truth_records', lambda out: [record])
    monkeypatch.setattr(A.S, 'variable', forbidden)
    old = dict(fresh_modes=np.ones((8, 1)))
    B.npz(tmp_path / f"step0/test/{record['regime']}_{record['date']}.npz", old)
    raw = dict(fresh_modes=np.zeros((8, 1)))
    meta = dict(status='SELECTED', CPU_s=0., wall_s=0.)
    monkeypatch.setattr(A, 'decision_record_x5', lambda *args, **kwargs: (raw, meta))
    context = (dict(test={}), {}, {})
    with pytest.raises(ValueError, match='truth differs from step0: fresh_modes'):
        A.outcome_record_x5(context, record, {'NEWB1': -1.}, stage='truth', out=tmp_path, verified=token)


def test_lock_detects_file_drift_and_parameter_override(monkeypatch, tmp_path):
    code = tmp_path / 'code.py'; code.write_text('original')
    monkeypatch.setattr(A, 'lock_paths', lambda out: dict(code=code))
    monkeypatch.setattr(A, 'check_sources', lambda out: {})
    value = dict(schema=A.LOCK_SCHEMA, parameters=A.parameters(), sha256=dict(code=B.C.sha256(code)))
    (tmp_path / 'lock.json').write_text(json.dumps(value))
    assert isinstance(A.verify_lock(tmp_path), B.C.VerifiedLock)
    code.write_text('changed')
    with pytest.raises(ValueError, match='lock mismatch'):
        A.verify_lock(tmp_path)


@pytest.mark.parametrize('name', ['npz', 'json'])
def test_outputs_never_overwrite_existing_file(tmp_path, name):
    path = tmp_path / ('raw.'+name)
    write = (lambda: B.npz(path, dict(value=np.ones(1)))) if name == 'npz' else (lambda: B.C.write_json(path, dict(value=1)))
    write(); before = path.read_bytes()
    with pytest.raises(FileExistsError):
        write()
    assert path.read_bytes() == before
