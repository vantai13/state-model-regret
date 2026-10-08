"""L0.6 — kiểm timescale ở mức thứ tự độ lớn (fluid, một bottleneck).

Tác giả: Doan Van Tai.
Câu hỏi: thông tin backlog có còn "sống" tới lúc action có hiệu lực không?
So T_drain (rho TRƯỚC quyết định) với tau_eff + d_act; không phải validation.
Chạy: python -m experiments.lessons.l0_6_timescale [tau_eff_cong_d_act_giay]
Mặc định 0.6 s; nguồn và giả định: notes/theory/T00_timescale_sanity.md.
"""
import math

PKT_BYTES = 1500


def tx_time_s(pkt_bytes: float, link_bps: float) -> float:
    """Thời gian truyền một packet (s); byte nhân 8 thành bit đúng một lần."""
    return 8 * pkt_bytes / link_bps


def drain_time_s(q0_packets: float, link_bps: float, rho: float, pkt_bytes: float = PKT_BYTES) -> float:
    """Thời gian xả backlog q0 theo xấp xỉ fluid (s).

    rho không có mặc định: chọn trước quyết định để kiểm timescale, hoặc sau
    Switch để chọn H. Khi rho >= 1 queue không tự xả: trả về inf.
    Miền dùng: q0 >= 0, link_bps/pkt_bytes > 0, rho >= 0.
    """
    if rho >= 1:
        return math.inf
    mu = 1 / tx_time_s(pkt_bytes, link_bps)
    return q0_packets / ((1 - rho) * mu)


def zone(t_drain_s: float, info_plus_act_s: float, factor: float = 3.0) -> str:
    """Xếp vùng theo tỉ số; factor là quy ước, không phải ngưỡng khoa học.

    Cần info_plus_act_s > 0, factor > 1. isclose chỉ xử lý sai số máy tại biên.
    """
    ratio = t_drain_s / info_plus_act_s
    if ratio >= factor or math.isclose(ratio, factor, rel_tol=1e-12, abs_tol=0.0):
        return "① còn nhớ"
    if ratio <= 1 / factor or math.isclose(ratio, 1 / factor, rel_tol=1e-12, abs_tol=0.0):
        return "③ đã quên"
    return "② cùng cỡ"


LINKS = [(10e6, "10 Mb/s"), (100e6, "100 Mb/s"), (1e9, "1 Gb/s"), (10e9, "10 Gb/s")]
Q0S = (100, 1000)
RHOS = (0.5, 0.8)
INFO_PLUS_ACT_S = 0.6  # Kịch bản đại diện; khảo sát thêm 0.35 và 1.0 s trong T00.


def table_rows(info_plus_act_s: float = INFO_PLUS_ACT_S):
    """Link, t_pkt, q0, drains theo rho, vùng theo drain nhỏ hơn (thận trọng)."""
    for bps, name in LINKS:
        for q0 in Q0S:
            drains = [drain_time_s(q0, bps, r) for r in RHOS]
            yield name, tx_time_s(PKT_BYTES, bps), q0, drains, zone(min(drains), info_plus_act_s)


if __name__ == "__main__":
    import sys

    ref = float(sys.argv[1]) if len(sys.argv) > 1 else INFO_PLUS_ACT_S
    print(f"| Link | t_pkt | q0 | T_drain ρ=0,5 | T_drain ρ=0,8 | Vùng (so {ref} s) |")
    print("|---|---:|---:|---:|---:|---|")
    for name, t_pkt, q0, (d5, d8), z in table_rows(ref):
        print(f"| {name} | {t_pkt*1e3:.4g} ms | {q0} | {d5:.4g} s | {d8:.4g} s | {z} |")
