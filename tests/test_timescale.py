"""Tác giả: Doan Van Tai. Bất biến timescale; số thực so bằng pytest.approx."""
import math

import pytest

from experiments.lessons.l0_6_timescale import drain_time_s, tx_time_s, zone


def test_tx_time_10M():
    assert tx_time_s(1500, 10e6) == pytest.approx(0.0012, rel=1e-9)


def test_drain_10M_busy():
    assert drain_time_s(100, 10e6, rho=0.8) == pytest.approx(0.6, rel=1e-9)


def test_drain_10M_idle():
    assert drain_time_s(100, 10e6, rho=0.5) == pytest.approx(0.24, rel=1e-9)


def test_drain_1G():
    assert drain_time_s(100, 1e9, rho=0.8) == pytest.approx(0.006, rel=1e-9)


def test_overload_never_drains():
    assert drain_time_s(100, 1e9, rho=1.0) == math.inf
    assert drain_time_s(100, 1e9, rho=1.2) == math.inf


def test_drain_scales_linearly_with_backlog():
    assert drain_time_s(1000, 1e8, rho=0.5) == pytest.approx(
        10 * drain_time_s(100, 1e8, rho=0.5), rel=1e-12
    )


def test_zone_boundaries():
    assert zone(2.4, 0.6) == "① còn nhớ"
    assert zone(0.6, 0.6) == "② cùng cỡ"
    assert zone(0.006, 0.6) == "③ đã quên"
    assert zone(2.4, 0.8) == "① còn nhớ"  # Tỉ số đúng 3, kể cả sai số float.
    assert zone(0.2, 0.6) == "③ đã quên"  # Tỉ số đúng 1/3.
