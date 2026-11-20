"""Doan Van Tai — synthetic summaries/guards only; never run truth or score."""
import json
import subprocess

import numpy as np
import pytest

from experiments.letter import x4b as B
from experiments.letter import x4b_card as K


def forbidden(*args, **kwargs):
    pytest.fail('future data/engine/real truth/score must not be called')


def test_evaluability_fixed_uniform_capacity_inclusive_boundary():
    # h=1 makes nextafter probe the exact >= boundary without division noise.
    threshold = .001*12544.525174
    cref = np.tile([np.nextafter(threshold, 0.), threshold, np.nextafter(threshold, np.inf)], (4, 1))
    np.testing.assert_array_equal(B.evaluability(cref, [1., 1., 1.]), [False, True, True])
    np.testing.assert_array_equal(B.evaluability(np.tile([0., threshold*300, threshold*7200], (4, 1)),
                                              [1, 300, 7200]), [False, True, True])


@pytest.mark.parametrize('cref,hs', [([[1]], [0]), ([[np.nan]], [1]), ([1], [1]), ([[1]], [1, 2]), ([], [])])
def test_evaluability_rejects_invalid_axes_and_nonfinite_values(cref, hs):
    with pytest.raises(ValueError):
        B.evaluability(cref, hs)


def test_tie_strict_additive_contributions_not_conditional_means_or_clipped():
    result = B.tie_strict_regret(np.array([2., 4., 10., -1.]), [True, True, False, False])
    assert result['tie_instances'] == result['strict_instances'] == 2
    assert result['regret_Mbit_s'] == 15/4
    assert result['tie_regret_Mbit_s'] == 6/4
    assert result['strict_regret_Mbit_s'] == 9/4
    assert result['strict_regret_share'] == .6
    assert result['tie_regret_Mbit_s']+result['strict_regret_Mbit_s'] == result['regret_Mbit_s']
    result = B.tie_strict_regret([-2., 3.], [True, False])
    assert result['strict_regret_share'] == 3.  # signed MC, no artificial [0,1] clipping
    assert B.tie_strict_regret([0., 0.], [True, False])['strict_regret_share'] is None


def synthetic_raw():
    n, nh = 4, len(B.H_SECONDS)
    choices = np.zeros((n, 3, 3, nh), dtype=int)
    choices[:, 0, 0] = 1
    choices[:, 1, 1] = 1
    choices[0, 1, 0] = 1
    ref = np.full((n, 2, 2, nh), 100000.)*B.H_SECONDS
    evaluation = ref.copy()
    evaluation[:, :, 1] += np.array([2., 4., 6., 8.])[:, None, None]
    raw = dict(decisions=choices, tie_flags=np.zeros_like(choices, dtype=bool),
               h_seconds=B.H_SECONDS, tau_seconds=np.array(B.S.TAU_SECONDS))
    raw['tie_flags'][:2, 0, 0] = True
    raw.update(B.paired_metrics(raw, ref, evaluation))
    return raw


def test_descriptive_pairs_se_unique_sides_both_side_max_and_tie_split():
    raw = synthetic_raw()
    meta = dict(regime='synthetic', set='X4b', date='synthetic-day')
    rows, pairs, ties = B.descriptive_rows(raw, meta)
    assert len(rows) == 3*2*7 and len(pairs) == 3*7 and len(ties) == 7
    fresh = next(r for r in pairs if r['side'] == 'fresh' and r['h_s'] == 300)
    assert fresh['paired_Hybrid_minus_Stationary_Mbit_s'] == .5
    assert fresh['paired_Hybrid_minus_Stationary_SE_Mbit_s'] == pytest.approx(.5)
    assert fresh['disagreement_numerator'] == 1 and fresh['instances'] == 4
    for r in rows:
        assert r['both_side_regret_pct'] == max(r['regret_fresh_pct'], r['regret_stale_pct'])
    for r in ties:
        assert r['tie_regret_sum_Mbit_s'] == 6.
        assert r['strict_regret_sum_Mbit_s'] == 14.
        assert r['strict_regret_share'] == .7
    # Fixed scalar c0: changing c[e*] never changes the card gate.
    raw['capacity_Mbps'] = np.array([1., 1.e9])
    assert B.descriptive_rows(raw, meta) == (rows, pairs, ties)
    json.dumps(dict(rows=rows, paired_rows=pairs, tie_strict_rows=ties), allow_nan=False)


@pytest.mark.parametrize('record', [dict(split='train', stratum='S'), dict(split='test', stratum='O')])
def test_outcome_blocks_non_test_S_before_lock_data_or_engine(monkeypatch, record):
    for obj, name in ((B, 'verify_lock'), (B, 'decision_record'), (B.S, 'variable')):
        monkeypatch.setattr(obj, name, forbidden)
    with pytest.raises(ValueError, match='only test-S'):
        B.outcome_record(None, record, {}, stage='truth')


def test_truth_record_requires_verified_token_before_context_or_engine(monkeypatch, tmp_path):
    monkeypatch.setattr(B, 'verify_lock', lambda out: B.C.VerifiedLock(str(tmp_path / 'lock.json'), 'digest'))
    monkeypatch.setattr(B, 'decision_record', forbidden)
    monkeypatch.setattr(B.S, 'variable', forbidden)
    with pytest.raises(ValueError, match='verified X4b'):
        B.outcome_record(None, dict(split='test', stratum='S'), {}, stage='truth', out=tmp_path)


def test_truth_record_checks_step0_before_any_future_evaluation(monkeypatch, tmp_path):
    record = dict(split='test', stratum='S', regime='NEWB1', date='2005-06-16')
    token = B.C.VerifiedLock(str(tmp_path / 'lock.json'), 'digest')
    monkeypatch.setattr(B, 'verify_lock', lambda out: token)
    monkeypatch.setattr(K, 'verify', lambda out: {})
    monkeypatch.setattr(B, 'planned_truth_records', lambda out: [record])
    monkeypatch.setattr(B, 'decision_record', lambda *args, **kw: (dict(decisions=np.zeros(1)), {}))
    monkeypatch.setattr(B, 'read_npz', lambda path: dict(decisions=np.ones(1)))
    monkeypatch.setattr(B.S, 'variable', forbidden)
    with pytest.raises(ValueError, match='truth differs from step0: decisions'):
        B.outcome_record((dict(test={}), {}, {}), record, {'NEWB1': 1.}, stage='truth', verified=token, out=tmp_path)


def test_historical_preparation_protocol_and_v2_sources_are_checked(monkeypatch, tmp_path):
    (tmp_path / 'protocol.json').write_text(json.dumps(dict(sha256=dict(code='old'))))
    (tmp_path / 'lock.json').write_text(json.dumps(dict(schema=B.LOCK_SCHEMA, sha256=dict(code='new'))))
    monkeypatch.setattr(B, 'fingerprints', lambda: dict(code='new'))
    assert B.check_sources(tmp_path)['sha256'] == dict(code='old')
    monkeypatch.setattr(B, 'fingerprints', lambda: dict(code='drift'))
    with pytest.raises(ValueError, match='drift'):
        B.check_sources(tmp_path)


def test_v2_lock_cannot_be_relocked_even_before_truth(monkeypatch, tmp_path):
    (tmp_path / 'lock.json').write_text(json.dumps(dict(schema=B.LOCK_SCHEMA)))
    monkeypatch.setattr(B, 'fingerprints', forbidden)
    with pytest.raises(FileExistsError, match='never relock'):
        B.create_lock(tmp_path)


def test_plan_keeps_all_sixty_S_records_and_excludes_O_and_train(tmp_path):
    records = [dict(split='test', stratum='S', regime='synthetic', date=str(d), status='PLANNED')
               for d in range(60)]
    others = [dict(split='test', stratum='O', regime='synthetic', date='other', status='NOT_RUN'),
              dict(split='train', stratum='S', regime='synthetic', date='train', status='PLANNED')]
    path = tmp_path / 'inputs.json'
    path.write_text(json.dumps(dict(records=records+others)))
    assert B.planned_truth_records(tmp_path) == records
    for broken in (records[:-1], records[:-1]+[records[0]],
                   [dict(r, status='NOT_RUN') if i == 0 else r for i, r in enumerate(records)]):
        path.write_text(json.dumps(dict(records=broken+others)))
        with pytest.raises(ValueError, match='all 60 distinct'):
            B.planned_truth_records(tmp_path)


def test_raw_commit_guard_is_read_only_and_checks_actual_bytes(monkeypatch, tmp_path):
    monkeypatch.setattr(B, 'ROOT', tmp_path)
    raw = tmp_path / 'raw.npz'
    raw.write_bytes(b'synthetic')
    calls = []
    def command(argv, **kwargs):
        calls.append(argv)
        if argv[-1] == 'HEAD':
            return 'commit\n'
        return 'blob\n'
    monkeypatch.setattr(B.subprocess, 'check_output', command)
    assert B.require_raw_committed([raw]) == 'commit'
    assert all('commit' not in a and 'ssh' not in a for a in calls)
    def missing(argv, **kwargs):
        if any(x.startswith('HEAD:') for x in argv):
            raise subprocess.CalledProcessError(128, argv)
        return 'commit\n'
    monkeypatch.setattr(B.subprocess, 'check_output', missing)
    with pytest.raises(ValueError, match='raw must be committed'):
        B.require_raw_committed([raw])


def test_card_lock_detects_card_scorer_and_source_lock_drift(monkeypatch, tmp_path):
    files = {k: tmp_path / k for k in ('card', 'scorer', 'lock')}
    for k, p in files.items():
        p.write_text(k)
    monkeypatch.setattr(K, 'lock_files', lambda out: files)
    payload = dict(schema='x4b-card-lock-v1', sha256={k: K.sha(p) for k, p in files.items()})
    (tmp_path / 'lock_card.json').write_text(json.dumps(payload))
    assert K.verify(tmp_path)['verified']
    for k, p in files.items():
        p.write_text('drift')
        with pytest.raises(ValueError, match='lock_card mismatch'):
            K.verify(tmp_path)
        p.write_text(k)
