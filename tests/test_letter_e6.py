"""Doan Van Tai — E6 saved-decision replay and independent cost checks."""
from copy import deepcopy

import numpy as np
import pytest

from experiments.ext_validity import ev_te as T
from experiments.letter import e4_geant as E
from experiments.letter import e6_endtoend as S


def test_constant_rate_equals_M0_including_exact_ties_and_tiny_differences():
    costs = np.array([[[0., 1e-30, 1.], [1e-31, 0., 1.]]])
    got = S.hybrid_decisions(costs, [1e100, 1e100], [.01, 1., 30.])
    np.testing.assert_array_equal(got, E.pick(costs)[0])
    np.testing.assert_array_equal(got, [[0, 1, 0]])


@pytest.fixture(scope='module')
def small_chunk():
    spec = next(s for s in E.selected_specs() if s['id'] == 'G3_r80_b3_s1')
    tr = S.training(spec)
    raw, _ = S.load_saved_chunk(spec, tr, 3000001, 0, size=2)
    return spec, tr, raw


def test_recomputed_small_chunk_matches_all_saved_hybrids_without_true_rollouts(small_chunk, monkeypatch):
    spec, tr, raw = small_chunk
    def forbidden(*args, **kwargs):
        pytest.fail('E6 must not evaluate true costs or recompute M1_new')
    monkeypatch.setattr(E, 'mean_futures', forbidden)
    monkeypatch.setattr(E, 'compute_chunk', forbidden)
    predicted = S.regenerate_twins(spec, tr, 3000001, 0, size=2)
    levels, _ = E.rate_levels(T.make_model(spec), tr)
    counts = S.validate(predicted, raw, levels)
    assert len(counts) == 7
    assert all(c['compared'] == 2 * 2 * 3 * 6 and c['mismatches'] == 0 for c in counts.values())
    # A single wrong saved action must be detected, without changing any tie tolerance.
    bad = deepcopy(raw)
    col = raw['pipelines'].tolist().index('Hybrid-i')
    bad['decisions'][0, col, 1, 1, 2] ^= 1
    assert S.validate(predicted, bad, levels)['i']['mismatches'] == 1


def test_record_gather_matches_independent_nested_loops_and_zero_ties():
    rng = np.random.default_rng(81403)
    costs = rng.uniform(0, 3, (4, 2, 3, 2, 2))
    costs[:, 0] = costs[:, 0, :1]
    values = rng.uniform(.1, 5, (4, 2, 2))
    rates = np.array([[[0., 0.], [1., 3.], [3., 1.]],
                      [[.1, .3], [.3, .1], [10., 10.]]])
    h = np.array([.5, 4.])
    got = S.record_cost_sums(costs, values, rates, h)
    expected = np.zeros_like(got)
    for rep in range(2):
        for L in range(3):
            for n in range(4):
                for side in range(2):
                    for tau in range(3):
                        for j in range(2):
                            a = int(np.argmin(costs[n, side, tau, :, j] + h[j] * rates[rep, L]))
                            expected[rep, L, side, tau, j] += values[n, a, j]
    np.testing.assert_array_equal(got, expected)
    assert rates.argmin(axis=-1)[0, 0] == 0


def test_finalize_uses_all_500_instances_saved_reference_and_same_record_static(small_chunk):
    _, _, raw = small_chunk
    rates = np.zeros((200, 3, 2))
    rates[:, 1] = [2., 1.]
    values = np.tile(np.array([[[2., 4., 6., 8., 10., 12.],
                                [1., 2., 3., 4., 5., 6.]]]), (50, 1, 1))
    pieces = []
    for c in range(10):
        # Distinct chunks ensure normalization averages over all 500 states.
        v = values + c
        ref = v[:, 1]
        hybrid = np.broadcast_to(v[:, 0].sum(axis=0), (200, 3, 2, 3, 6)).copy()
        pieces.append(dict(V=v, ref_values=ref, hybrid_cost_sum=hybrid,
                           instance_id=c * 50 + np.arange(50),
                           **{k: raw[k] for k in ('h', 'tau', 'h_mult', 'tau_mult')}))
    got = S.finalize_regime(pieces[::-1], rates)
    all_v = np.concatenate([p['V'] for p in pieces])
    ref = all_v[:, 1].mean(axis=0)
    np.testing.assert_array_equal(got['C_ref'], ref)
    np.testing.assert_array_equal(got['static_action'][:, 0], 0)
    np.testing.assert_array_equal(got['static_action'][:, 1], 1)
    np.testing.assert_array_equal(got['regret_static'][:, 1], 0)
    expected = 100 * (all_v[:, 0].mean(axis=0) - ref) / ref
    np.testing.assert_array_equal(got['regret_static'][0, 0], expected)
    np.testing.assert_array_equal(got['regret_hybrid'][0, 0, 0, 0], expected)
    assert got['regret_hybrid'].shape == (200, 3, 2, 3, 6)
    assert got['regret_static'].shape == (200, 3, 6)
    with pytest.raises(ValueError, match='all ten chunks'):
        S.finalize_regime(pieces[:-1], rates)


def test_record_source_uses_the_prescribed_E5_lengths(small_chunk):
    spec, tr, _ = small_chunk
    rates, _ = S.load_records(spec, tr)
    with np.load(S.R.OUT / 'raw' / f"{spec['id']}.npz", allow_pickle=False) as saved:
        np.testing.assert_array_equal(rates, saved['means'][:, [3, 4, 5], :])
    assert rates.shape == (200, 3, 2)


def test_projection_uses_heaviest_observed_multiplier_and_two_hour_gate():
    metadata = [dict(CPU=1., historical_E4_CPU=10.), dict(CPU=10., historical_E4_CPU=50.)]
    p = S.pilot_projection(metadata, {'a': 1000., 'b': 2000.})
    assert p['total_CPU_seconds'] == 600. and p['allowed']
    p = S.pilot_projection(metadata, {'a': 40000.})
    assert p['total_CPU_seconds'] == 8000. and not p['allowed']
