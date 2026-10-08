"""Tác giả: Doan Van Tai. Bất biến của script timescale. So số thực bằng pytest.approx; chỉ dùng == cho inf và chuỗi."""
import math

import pytest

from experiments.lessons.l0_6_timescale import (
    REGIMES,
    conservative_drain_s,
    drain_time_s,
    effective_age_s,
    tx_time_s,
    zone,
    zone_matrix,
)


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
    assert drain_time_s(1000, 1e8, rho=0.5) == pytest.approx(10 * drain_time_s(100, 1e8, rho=0.5), rel=1e-12)


def test_zone_boundaries():
    assert zone(2.4, 0.6) == "① còn nhớ"
    assert zone(0.6, 0.6) == "② cùng cỡ"
    assert zone(0.006, 0.6) == "③ đã quên"
    assert zone(2.4, 0.8) == "① còn nhớ"  # Đúng biên 3, kể cả sai số float.
    assert zone(0.6, 0.2) == "① còn nhớ"
    assert zone(0.2, 0.6) == "③ đã quên"  # Đúng biên 1/3.


def test_effective_age_snmp_counter_rate():
    # Poll 60 s, rate lấy từ hiệu counter (cửa sổ 60 s), bỏ qua độ trễ truyền: tuổi trung bình khoảng 60 s.
    assert effective_age_s(60, 0.0, 60) == pytest.approx(60.0, rel=1e-12)


def test_effective_age_instant_sample():
    # Mẫu tức thời mỗi 10 ms, độ trễ 2 ms: 5 ms + 2 ms.
    assert effective_age_s(0.01, latency_s=0.002) == pytest.approx(0.007, rel=1e-9)


def test_regime_anchor_points():
    # Ghim cả trục quét và 40 ô tính tay trong T00; kiểm hai neo thực sự qua generator.
    assert [ref for ref, _ in REGIMES] == pytest.approx([0.005, 0.2, 1.0, 5.0, 30.0])
    matrix = {(name, q0): zones for name, q0, zones in zone_matrix()}
    assert list(matrix.values()) == [
        list("①②③③③"), list("①①②②③"),
        list("①③③③③"), list("①②③③③"),
        list("②③③③③"), list("①③③③③"),
        list("③③③③③"), list("②③③③③"),
    ]
    assert matrix[("1 Gb/s", 1000)][0] == "①"  # Neo (a).
    assert matrix[("10 Mb/s", 1000)][1] == "①"  # Neo (b).
    assert matrix[("10 Mb/s", 1000)][-1] == "③"
    assert zone(conservative_drain_s(1000, 1e9), 0.005) == "① còn nhớ"
