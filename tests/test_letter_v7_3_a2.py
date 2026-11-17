"""Doan Van Tai — nonzero controls for the independent A2 replay."""
import numpy as np
import pytest

from experiments.letter import v7_3_a2_verify as V


def nonzero_pilot():
    # Decision and evaluation streams deliberately disagree at the first two h.
    decision = np.array([[15., 21., 29., 41.], [11., 21., 61., 9.]])
    evaluation = np.array([[10., 20., 30., 40.], [14., 12., 60., 10.]])
    ref = np.array([[1, 0, 0, 1]])
    cref = np.array([[14., 20., 30., 10.]])
    decisions = np.zeros((1, 3, 2, 2, 4), dtype=int)
    decisions[:, :, 1] = 1
    costs = np.broadcast_to(evaluation[None, None, :, None, :], decisions.shape).copy()
    regret = costs-cref[:, None, None, None, :]
    gs = np.broadcast_to(np.array([4., -8., 30., -30.]), (1, 3, 2, 4)).copy()
    raw = dict(reference_decision_rollouts=decision[None, None],
               paired_evaluation=evaluation[None, None], V=evaluation[None],
               reference_decision=ref, reference_tie_flags=np.array([[False, True, False, False]]),
               C_ref=cref, decisions=decisions, costs=costs, regret=regret, G_S=gs,
               h_seconds=np.array([3600, 7200, 14400, 21600]), tau_seconds=np.array([300, 900]))
    meta = dict(N=1, R_dec=1, R_eval=1, C_ref_mean_Mbit_s=cref[0],
                regret_mean_Mbit_s=regret[0], G_S_mean_Mbit_s=gs[0],
                percentages_defined=[True]*4, reference_evaluation_streams_distinct=True)
    return raw, meta


def test_replay_distinguishes_reference_and_evaluation_and_allows_negative_regret():
    raw, meta = nonzero_pilot()
    assert raw['regret'][0, 0, 0, 0, 0] == -4
    cref, decisions = V.replay_pilot(raw, meta)
    np.testing.assert_array_equal(cref, [[14., 20., 30., 10.]])
    np.testing.assert_array_equal(decisions, raw['decisions'])


@pytest.mark.parametrize('field', ['G_S', 'reference_decision', 'reference_tie_flags', 'C_ref', 'regret'])
def test_replay_rejects_a_corrupted_nonzero_metric(field):
    raw, meta = nonzero_pilot()
    raw[field] = raw[field].copy()
    raw[field].flat[0] = not raw[field].flat[0] if raw[field].dtype == bool else raw[field].flat[0]+1
    with pytest.raises(AssertionError):
        V.replay_pilot(raw, meta)
