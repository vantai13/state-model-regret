"""Small S2 tests, no CTMC truth or old-test edits."""
import importlib.util
from pathlib import Path

import pandas as pd
import pytest

spec = importlib.util.spec_from_file_location("s2_under_test", Path(__file__).with_name("analyze_s2.py"))
s2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s2)


@pytest.mark.parametrize("static,hybrid,reference,absolute,pp", [
    (3., 1., 200., 2., 1.), (1., 3., 200., -2., -1.), (2., 2., 10., 0., 0.),
])
def test_paired_delta_sign_units_and_tie(static, hybrid, reference, absolute, pp):
    assert s2.paired_delta(static, hybrid, reference) == (absolute, pp)


@pytest.mark.parametrize("reference", [0., -1., float("inf"), float("nan")])
def test_delta_rejects_bad_normalizer(reference):
    with pytest.raises(ValueError):
        s2.paired_delta(1., 2., reference)


@pytest.mark.parametrize("n,total,mean,expected", [(10, 100, .1, "PASS"),
    (9, 100, 10., "FAIL"), (10, 100, .099999, "FAIL"),
    (100, 100, -.1, "FAIL"), (0, 100, None, "NOT_EVALUABLE")])
def test_numeric_gate_is_joint_coverage_and_mean(n, total, mean, expected):
    assert s2.gate(n, total, mean) == expected


def test_intervals_and_no_repeated_regime_statistics():
    assert s2.ci([.2, .2, .2]) == pytest.approx((.2, .2))
    assert s2.ci([.2]) == (None, None)
    with pytest.raises(ValueError, match="collapse"):
        s2.stats(pd.DataFrame({"regime": ["R1", "R1"]}), 2)


def test_fixed_id_split_keeps_all_horizons_together():
    frame = pd.DataFrame({"regime": ["S1A_0001", "S1A_0001", "S1A_0002", "S1A_0003"]})
    train, evaluation = s2.split_ids(frame)
    assert set(train.regime) == {"S1A_0001", "S1A_0003"}
    assert set(evaluation.regime) == {"S1A_0002"}


def test_one_threshold_uses_training_only_and_deterministic_tie():
    training = pd.DataFrame({"D": [0., .1, .5, .9], "delta_pp": [0., 0., .2, .3]})
    best, grid = s2.select_threshold(training, [0., .1, .2, .5, 1.])
    assert best["d_star"] == .2  # .2 and .5 tie in F1; smaller threshold wins.
    assert best["f1"] == 1.
    assert grid[-1]["eligible_coverage"] is False


def test_exclusive_creation_preserves_original(tmp_path):
    target = tmp_path / "result.json"
    s2.json_once(target, {"first": 1})
    with pytest.raises(FileExistsError):
        s2.json_once(target, {"second": 2})
    assert '"first"' in target.read_text() and '"second"' not in target.read_text()
