"""Non-circular deterministic checks on continuous-fluid path integration."""
import pytest
from experiments.R3R_04_realism.generic_sim import positive_area, above_time


def test_exact_drain_then_idle():
    assert positive_area(2, -2, 3) == 1
    assert above_time(2, -2, 3, 0) == 1
    assert above_time(2, -2, 3, 1) == .5


def test_increasing_path_and_late_threshold_crossing():
    assert positive_area(0, 2, 3) == 9
    assert above_time(0, 2, 3, 1) == 2.5
    assert above_time(0, 2, 3, 8) == 0
    assert positive_area(1, 0, 2) == 2
    assert above_time(1, 0, 2, 1) == 0


def test_split_interval_preserves_area():
    assert positive_area(3, -2, 5) == pytest.approx(positive_area(3, -2, 1) + positive_area(1, -2, 4))
