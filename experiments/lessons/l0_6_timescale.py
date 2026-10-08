"""L0.6 — kiểm timescale ở mức thứ tự độ lớn (xấp xỉ fluid, một bottleneck).

Tác giả: Doan Van Tai.
Câu hỏi khoa học: thông tin backlog có còn "sống" tới lúc action có hiệu lực không?
So T_drain (tính với rho TRƯỚC quyết định) với tau_eff + d_act. Không phải validation.
tau_eff + d_act là một TRỤC QUÉT theo chế độ telemetry trong literature (T00), không phải một con số chốt.
Chạy: python -m experiments.lessons.l0_6_timescale            (ma trận vùng theo chế độ)
      python -m experiments.lessons.l0_6_timescale 0.2        (bảng chi tiết cho một mức tau_eff + d_act, giây)
"""
import math

PKT_BYTES = 1500


def tx_time_s(pkt_bytes: float, link_bps: float) -> float:
    """Thời gian truyền một packet (s). Byte nhân 8 thành bit đúng một lần."""
    return 8 * pkt_bytes / link_bps


def drain_time_s(q0_packets: float, link_bps: float, rho: float, pkt_bytes: float = PKT_BYTES) -> float:
    """Thời gian xả backlog q0 theo xấp xỉ fluid (s).

    rho KHÔNG có mặc định: người gọi phải tự chọn rho trước quyết định (kiểm timescale)
    hay rho sau Switch (chọn H). Khi rho >= 1 queue không tự xả: trả về inf.
    Miền dùng: q0 >= 0, link_bps/pkt_bytes > 0, rho >= 0.
    """
    if rho >= 1:
        return math.inf
    mu = 1 / tx_time_s(pkt_bytes, link_bps)
    return q0_packets / ((1 - rho) * mu)


def effective_age_s(period_s: float, latency_s: float = 0.0, window_s: float = 0.0) -> float:
    """Tuổi thông tin trung bình (s) khi số đo đến theo chu kỳ period_s và controller quyết định lúc bất kỳ.

    Giả định phase quyết định đều trong chu kỳ, latency cố định, không mất/đảo mẫu.
    window_s/2 là quy ước tâm cửa sổ, không phải tuổi của một mẫu backlog tức thời.
    period_s/2: thời gian trung bình kể từ số đo gần nhất; latency_s: truyền + xử lý;
    window_s/2: nếu giá trị là trung bình trên một cửa sổ (ví dụ rate từ hiệu counter).
    """
    return period_s / 2 + latency_s + window_s / 2


def zone(t_drain_s: float, info_plus_act_s: float, factor: float = 3.0) -> str:
    """Xếp vùng theo tỉ số T_drain / (tau_eff + d_act); factor là quy ước.

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
# Các tổng tau_eff + d_act minh họa trục quét, không phải số đo end-to-end (T00).
REGIMES = [(0.005, "5 ms"), (0.2, "0,2 s"), (1.0, "1 s"), (5.0, "5 s"), (30.0, "30 s")]


def conservative_drain_s(q0: float, link_bps: float) -> float:
    """T_drain nhỏ hơn trong các mức rho trước quyết định: thận trọng khi tìm vùng backlog còn liên quan; không loại mọi rho."""
    return min(drain_time_s(q0, link_bps, r) for r in RHOS)


def table_rows(info_plus_act_s: float):
    """Mỗi dòng: link, t_pkt, q0, [T_drain theo từng rho], vùng (theo T_drain thận trọng)."""
    for bps, name in LINKS:
        for q0 in Q0S:
            drains = [drain_time_s(q0, bps, r) for r in RHOS]
            yield name, tx_time_s(PKT_BYTES, bps), q0, drains, zone(min(drains), info_plus_act_s)


def zone_matrix():
    """Mỗi dòng: tên link, q0, [ký hiệu vùng cho từng chế độ trong REGIMES]."""
    for bps, name in LINKS:
        for q0 in Q0S:
            t = conservative_drain_s(q0, bps)
            yield name, q0, [zone(t, ref)[0] for ref, _ in REGIMES]


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        ref = float(sys.argv[1])
        print(f"| Link | t_pkt | q0 | T_drain ρ=0,5 | T_drain ρ=0,8 | Vùng (so {ref} s) |")
        print("|---|---:|---:|---:|---:|---|")
        for name, t_pkt, q0, (d5, d8), z in table_rows(ref):
            print(f"| {name} | {t_pkt*1e3:.4g} ms | {q0} | {d5:.4g} s | {d8:.4g} s | {z} |")
    else:
        print("| Link, q0 | " + " | ".join(n for _, n in REGIMES) + " |")
        print("|---|" + "---|" * len(REGIMES))
        for name, q0, zs in zone_matrix():
            print(f"| {name}, {q0} | " + " | ".join(zs) + " |")
