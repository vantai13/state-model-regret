"""Doan Van Tai — small checks for the read-only letter W1a analyses."""
import json

import numpy as np
import pytest

from experiments.ext_validity import ev_te as T
from experiments.letter import ctmc_saved_tables as S
from experiments.letter import lemma_check as L
from experiments.letter import ties_topology as A


def small_regime():
    specs = T.read_json(T.OUT / "regimes.json")
    spec = next(s for s in specs if s["id"] == "A1_r80_b3_s0")
    training = T.read_json(T.OUT / "train" / f"{spec['id']}.json")
    return spec, training, T.make_model(spec)


def test_test_instance_rebuild_matches_locked_entry_point_and_repeats():
    spec, training, model = small_regime()
    first = A.rebuild_instances(model, training, spec["id"], n=4)
    second = A.rebuild_instances(model, training, spec["id"], n=4)
    direct = T.instances(model, training["T_int"], training["dt"], 4,
                         T.seed_for(1000001, spec["id"], 0))
    assert A.state_hash(*first) == A.state_hash(*second) == A.state_hash(*direct)
    assert first[0][0].shape[0] == 4
    different = T.instances(model, training["T_int"], training["dt"], 4,
                            T.seed_for(777, spec["id"], 0))
    assert A.state_hash(*first) != A.state_hash(*different)


def test_predicted_cost_argmins_match_choose_twins_per_instance_stream():
    spec, training, model = small_regime()
    fresh, stale = A.rebuild_instances(model, training, spec["id"], n=2)
    for i in range(2):
        actual = A.predicted_costs(model, fresh, stale, training, spec["id"], i)
        expected = T.choose_twins(model, tuple(x[i:i+1] for x in fresh),
                                 [tuple(x[i:i+1] for x in pair) for pair in stale],
                                 training["T_int"], training["dt"], 128,
                                 T.seed_for(1000001, spec["id"], 100+i))
        np.testing.assert_array_equal(actual.argmin(axis=-1), expected[0])
        reduced = A.predicted_costs(model, fresh, stale, training, spec["id"], i, (1, 3))
        np.testing.assert_array_equal(reduced, actual[[1, 3]])


def test_tie_counter_tolerances_zero_and_multiple_minima():
    vectors = [[0., 0.], [2., 2.], [2., 2.+1e-9], [1., 2.], [0., 1e-20]]
    masks = A.tie_masks(vectors)
    assert masks["exact"].tolist() == [True, True, False, False, False]
    assert masks["relative"].tolist() == [True, True, True, False, False]
    assert masks["zero"].tolist() == [True, False, False, False, False]
    four = A.tie_masks([[0., 0., 1., 2.], [0., 0., 0., 0.]])
    assert four["exact"].tolist() == [False, True]
    assert four["minimum_exact"].tolist() == [True, True]
    with pytest.raises(ValueError):
        A.tie_masks([[np.nan, 0.]])


def test_lemma_checker_on_one_small_asym_regime():
    case = next(c for c in json.loads(L.CASES.read_text()) if c["id"] == "A_u1_lA7_x-1_k1-20")
    result = L.check_regime(case)
    assert result["a_vhat_constant"]["status"] == "PASS"
    assert result["b_horizon_invariance"]["status"] == "PASS"
    assert result["c_true_s_hybrid"]["status"] == "PASS"
    assert result["evaluate_arrays_replay_match"]
    assert all(p["max_abs_error"] == 0 for p in result["a_vhat_constant"]["paths"].values())
    assert result["bar_h_Tint"] > 0 and result["coincidence_bound_Tint"] > 0
    # Constancy with h does not force two different information states to agree.
    witness = result["b_literal_fresh_equals_stale"]["counterexamples"][0]
    assert witness["fresh_action"] != witness["stale_action"]


def test_saved_bins_and_strict_sign_zero_cases():
    assert [S.horizon_bin(x) for x in (.5, 1., 4., 7., 15.)] == list(S.BINS)
    assert S.sign_kind(-2., 1.) == "opposite_nonzero"
    assert S.sign_kind(0., 1e-16) == "true_zero_mm1_nonzero"
    assert S.sign_kind(-1e-16, 0.) == "true_nonzero_mm1_zero"
    assert S.sign_kind(-2., -1.) == "agree"


def test_saved_aggregation_keeps_flagged_rows_and_regret_units():
    def row(tie, gs, value, flags, kind):
        return dict(input_file=str(value), M0_new_tie_mass=tie, G_S=gs,
                    flags=flags, sign_kind=kind, **{f"regret_{p}":value for p in S.PIPES})
    rows = [row(.1, -.2, 2., "negative", "opposite_nonzero"),
            row(.3, .2, 6., "", "agree")]
    result = S.aggregate(rows, "toy", "1-4")
    assert result["rows"] == 2 and result["flagged_rows"] == 1
    assert result["M0_new_tie_mass_median"] == pytest.approx(.2)
    assert result["M0_new_tie_mass_q90"] == pytest.approx(.28)
    assert result["GS_below_minus_0p1_share"] == .5
    assert result["regret_M0_new_median_pct_Cref"] == 4.
    assert result["sign_mismatch_hybrid_mm1_new_median_pct_Cref"] == 2.
    empty = S.aggregate([], "toy", ">=15")
    assert empty["rows"] == 0 and empty["regret_M0_new_median_pct_Cref"] is None
