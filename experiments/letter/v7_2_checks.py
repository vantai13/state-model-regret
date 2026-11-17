"""Doan Van Tai — V7-2 data-window and audit safety checks (synthetic only)."""
import hashlib

import numpy as np
import pytest

from experiments.letter import v7_2_audit as V


def test_four_hour_hold_has_no_post_training_window():
    plan = V.window_plan(14400.07)
    assert [plan["holds"][str(h)]["anchor_count"] for h in (1, 2, 4)] == [24, 12, 0]
    assert plan["holds"]["4"]["minimum_record_s"] == 18300
    assert plan["holds"]["4"]["record_s_for_12_common_anchors"] == 21600


def test_window_edges_never_wrap_or_use_training_as_stale_observation():
    plan = V.window_plan(14400.07)
    for hold in plan["holds"].values():
        if hold["ready"]:
            assert hold["first_anchor_s"]-plan["max_age_s"] >= plan["train_s"]
            assert hold["last_eligible_anchor_s"]+hold["hold_s"] <= plan["duration_s"]
    assert not V.window_plan(18299.99)["holds"]["4"]["ready"]
    assert V.window_plan(18300.)["holds"]["4"]["anchor_count"] == 1
    assert V.window_plan(21600.)["holds"]["4"]["anchor_count"] == 12


@pytest.mark.parametrize("kwargs", [{"duration":float("nan")}, {"duration":-1},
    {"duration":1,"train":0}, {"duration":1,"max_age":-1}, {"duration":1,"step":0}])
def test_invalid_window_parameters_fail_closed(kwargs):
    with pytest.raises(ValueError):
        V.window_plan(**kwargs)


def test_forward_train_sampler_never_wraps_into_empty_intensity_bins():
    counts = np.array([0., 100., 0., 100.])
    draws = V.train_arrivals(counts, mean_train=50., lam=100., dt=.01,
                             rng=np.random.default_rng(912))
    assert len(draws) > 0
    assert draws.min() >= 0 and draws.max() < .04
    assert set(np.floor(draws/.01).astype(int)) <= {1, 3}
    np.testing.assert_array_equal(draws, V.train_arrivals(counts, 50., 100., .01,
                                                        np.random.default_rng(912)))


def test_training_mean_is_supplied_and_not_refit_to_pilot_slice():
    class Capture:
        def poisson(self, rates):
            np.testing.assert_array_equal(rates, [.5, 1.5])
            return np.zeros(2, dtype=int)

        def random(self, n):
            return np.zeros(n)
    assert len(V.train_arrivals([1., 3.], 2., 1., 1., Capture())) == 0


def test_manifest_detects_changed_or_missing_inputs(tmp_path):
    path = tmp_path/"input.json"
    path.write_text("unchanged")
    entries = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()}
    assert V.verify_entries(tmp_path, entries)["passed"]
    path.write_text("changed")
    assert not V.verify_entries(tmp_path, entries)["passed"]
    path.unlink()
    assert not V.verify_entries(tmp_path, entries)["passed"]


def test_exclusive_writer_preserves_existing_artifact(tmp_path):
    path = tmp_path/"artifact.json"
    V.write_new(path, {"v":1})
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        V.write_new(path, {"v":2})
    assert path.read_bytes() == before
