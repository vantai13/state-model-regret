"""Doan Van Tai — decisions-only, seed, raw-statistics and committed-lock guards.

No real test-seed evaluation is allowed in this test module. The regression
reads only saved V7-3 decision/state arrays and recomputes decisions.
"""
import json
from pathlib import Path
import subprocess

import numpy as np
import pytest

from experiments.letter import v7_4_short as V


def forbidden(*args, **kwargs):
    pytest.fail('forbidden evaluation/reference/truth input access')


def toy(monkeypatch):
    record = dict(regime='DAY1', date='2005-06-16', stratum='S')
    data = dict(dates=np.array([record['date']]), warm=np.ones((1, 8, 1)), days=np.ones((1, 24, 1)))
    arrays = dict(incidence=np.ones((1, 2, 1, 1)), capacity=np.array(10.), profiles=np.ones((2, 24, 1)))
    config = dict(regimes=[dict(id='DAY1')])
    params = dict(s_hat_pooled_Mbit={'DAY1': -100.}, s_hat_S_Mbit_sensitivity={'DAY1': -.4})
    monkeypatch.setattr(V, 'selected_records', lambda: [record])
    monkeypatch.setattr(V.S, 'warm_instances', lambda *a: ((np.ones((2, 1)), np.zeros((2, 1))),
        {t: (np.ones((2, 1)), np.zeros((2, 1))) for t in V.S.TAU_SECONDS}))
    monkeypatch.setattr(V.S, 'forward_posterior', lambda *a: (np.ones((4, 1)), np.zeros((4, 1))))
    def mean(inc, profile, cap, m, q, **kw):
        costs = np.zeros((len(m), 2, len(kw['hs'])))
        costs[:, 1, :] = 10.
        return costs
    monkeypatch.setattr(V.S, 'mean_rollout', mean)
    return data, arrays, config, params, record


def test_decisions_only_cannot_call_evaluation_or_reference(monkeypatch):
    args = toy(monkeypatch)
    for obj, name in ((V, 'evaluation_rollouts'), (V, 'reference_metrics'),
                      (V.E, 'costs_for_decisions'), (V.S, 'variable'),
                      (V.V3, 'compute_record'), (V, 'outcome_record')):
        monkeypatch.setattr(obj, name, forbidden)
    raw, meta = V.decision_record(*args, n=2, k=2)
    assert raw['decisions'].shape == (2, 5, 2, 2, 5)
    assert not meta['evaluation_called'] and not meta['C_ref_computed']
    assert {'C_ref', 'V', 'regret', 'paired_evaluation'}.isdisjoint(raw)
    assert not any('evaluation' in k or 'reference' in k for k in meta['timings'])


def test_seed_roots_are_fresh_and_streams_distinct():
    old = V.legacy_seeds()
    assert 7312001 in old and 7372001 in old and 7302001 in old
    assert V.TEST_SEED != V.PILOT_SEED
    assert V.TEST_SEED not in old and V.PILOT_SEED not in old
    streams = [V.seeds_for(seed, 'DAY1', '2005-06-16') for seed in old + [V.TEST_SEED, V.PILOT_SEED]]
    for key in ('record', 'warm', 'posterior-300.0', 'posterior-900.0', 'reference-decision', 'evaluation'):
        assert len({r[key] for r in streams}) == len(streams)
    for stream in streams:
        assert stream['evaluation'] != stream['reference-decision']


def test_input_selection_is_exactly_29_per_regime():
    records = V.selected_records()
    assert len(records) == 87
    assert all(r['date'] != V.EXCLUDED_DATE and r['stratum'] == 'S' for r in records)
    assert {g: sum(r['regime'] == g for r in records) for g in V.REGIMES} == dict.fromkeys(V.REGIMES, 29)


def test_truth_refuses_uncommitted_lock_before_input_or_engine(tmp_path, monkeypatch):
    (tmp_path / 'lock.json').write_text('{}\n')
    def no_commit(*args, **kwargs):
        raise subprocess.CalledProcessError(128, args[0])
    monkeypatch.setattr(V.subprocess, 'check_output', no_commit)
    monkeypatch.setattr(V, 'load_context', forbidden)
    monkeypatch.setattr(V, 'outcome_record', forbidden)
    monkeypatch.setattr(V.S, 'warm_instances', forbidden)
    with pytest.raises(ValueError, match='not been committed'):
        V.run_truth(tmp_path)
    assert not (tmp_path / 'truth').exists()


def test_truth_refuses_missing_or_dirty_lock(tmp_path, monkeypatch):
    with pytest.raises(ValueError, match='missing or not committed'):
        V.run_truth(tmp_path)
    (tmp_path / 'lock.json').write_text('{}\n')
    monkeypatch.setattr(V.subprocess, 'check_output', lambda *a, **k: b'{"changed":true}\n')
    with pytest.raises(ValueError, match='differs from HEAD'):
        V.run_truth(tmp_path)
    assert not (tmp_path / 'truth').exists()


def test_low_level_truth_needs_verified_token(monkeypatch):
    monkeypatch.setattr(V, 'decision_record', forbidden)
    with pytest.raises(ValueError, match='verified lock'):
        V.outcome_record({}, {}, {}, {}, {}, stage='truth')


def test_committed_lock_checks_all_hashes_and_signal(tmp_path, monkeypatch):
    signal = tmp_path / 'signal.json'
    signal.write_text(json.dumps({'signal_gate': {'verdict': 'NOT_ENOUGH_SIGNAL'}}))
    code = tmp_path / 'code.py'
    code.write_text('fixture')
    lock = tmp_path / 'lock.json'
    value = dict(schema='v7-4-short-lock-v1', sha256={'code': V.C.sha256(code)})
    lock.write_text(json.dumps(value))
    monkeypatch.setattr(V.subprocess, 'check_output', lambda *a, **k: lock.read_bytes())
    monkeypatch.setattr(V, 'preparation_paths', lambda *a: {'code': code})
    with pytest.raises(ValueError, match='NOT_ENOUGH_SIGNAL'):
        V.verify_committed_lock(tmp_path)
    code.write_text('tampered')
    with pytest.raises(ValueError, match='locked file hashes differ'):
        V.verify_committed_lock(tmp_path)


def test_signal_gate_boundary_and_tau_pooling():
    rows = [dict(population='DAY1_DAY2', variant='pooled', h_s=h, side=side,
                 disagree=10 if side == 'fresh' else 0, disagree_share=.01 if side == 'fresh' else 0.)
            for h in V.H_SECONDS.tolist() for side in V.SIDES]
    assert V.signal_verdict(rows)['verdict'] == 'SIGNAL_OK'
    rows[0]['disagree'] -= 1
    assert V.signal_verdict(rows)['verdict'] == 'NOT_ENOUGH_SIGNAL'
    rows[0]['disagree'] += 1
    for row in rows:
        if row['side'] == 'fresh' and row['h_s'] != 300:
            row['disagree_share'] = .00999
    assert V.signal_verdict(rows)['verdict'] == 'NOT_ENOUGH_SIGNAL'


def test_exact_ties_and_stable_sensitivity(monkeypatch):
    args = toy(monkeypatch)
    raw, _ = V.decision_record(*args, n=2, k=2)
    # Exact threshold tie uses the V7-3 helper and must choose Stay.
    costs = np.array([[[0.], [300.]]])
    d, ties = V.choices(costs, -1., -.4, np.array([300]))
    assert d[0, 1, 0] == 0 and ties[0, 1, 0]
    assert d[0, 2, 0] == 1
    rows = V.signal_rows(raw, args[-1])
    assert len(rows) == 40
    assert all(row['denominator'] == 2 for row in rows)
    assert {'pooled', 'stable_only'} == {r['variant'] for r in rows}


def test_saved_raw_supports_paired_instance_and_case_metrics():
    # Pure synthetic arrays; no simulator, C_ref rollout or real outcome.
    n, nh = 2, 5
    raw = dict(decisions=np.zeros((n, 5, 2, 2, nh), dtype=np.int16), h_seconds=V.H_SECONDS)
    raw['decisions'][:, 1] = 1
    raw['decisions'][:, 2] = 0
    evaluation = np.full((n, V.R_EVAL, 2, nh), 1e5)
    evaluation[:, :, 1] += np.arange(V.R_EVAL)[None, :, None] - 100
    reference = np.full((n, V.R_DEC, 2, nh), 1e5)
    reference[:, :, 1] -= 1
    got = V.reference_metrics(raw, reference, evaluation)
    assert got['paired_evaluation'].shape == (n, 128, 2, nh)
    assert got['reference_decision_rollouts'].shape == (n, 64, 2, nh)
    paired_difference = evaluation[:, :, 1] - evaluation[:, :, 0]
    np.testing.assert_allclose(paired_difference.mean(axis=1), -36.5)
    np.testing.assert_allclose(paired_difference.std(axis=1, ddof=1)/np.sqrt(128), np.sqrt(129/12))
    regret = got['regret'].mean(axis=0).max(axis=1)
    np.testing.assert_allclose(regret[1] - regret[2], -36.5)
    assert got['evaluable'].shape == (5,)


def test_one_hour_reproduces_saved_v7_3_decisions(tmp_path, monkeypatch):
    # Read only input matrices and saved old decisions, never saved V/cost/regret.
    context = V.load_context(tmp_path)
    data, arrays, config, params, records = context
    record = next(r for r in records if r['regime'] == 'DAY1' and r['date'] == '2005-06-16')
    monkeypatch.setattr(V, 'evaluation_rollouts', forbidden)
    monkeypatch.setattr(V, 'reference_metrics', forbidden)
    monkeypatch.setattr(V.E, 'costs_for_decisions', forbidden)
    original_variable = V.S.variable
    eval_seed = V.seeds_for(7312001, record['regime'], record['date'])
    def reject_evaluation(*args, **kwargs):
        assert args[5] not in (eval_seed['evaluation'], eval_seed['reference-decision'])
        return original_variable(*args, **kwargs)
    monkeypatch.setattr(V.S, 'variable', reject_evaluation)
    raw, _ = V.decision_record(data, arrays, config, params, record,
                               seed=7312001, horizons=np.array([3600]))
    oldpath = V.C.OUT / 'records' / 'DAY1_2005-06-16.npz'
    with np.load(oldpath, allow_pickle=False) as old:
        np.testing.assert_array_equal(raw['decisions'][:, :3], old['decisions'][:, :, :, :, :1])
        np.testing.assert_array_equal(raw['tie_flags'][:, :3], old['tie_flags'][:, :, :, :, :1])
        np.testing.assert_array_equal(raw['fresh_modes'], old['fresh_modes'])
        np.testing.assert_array_equal(raw['fresh_queues'], old['fresh_queues'])
