"""Doan Van Tai — L1.7 — Luật chơi của ngẫu nhiên: "cùng seed" so với primitive stream, máy dò CRN, và rò tương lai.

Scientific purpose:
    Kiểm câu hỏi: "Quy ước stream của tôi có thật sự cho mọi action CÙNG một tương lai không,
    và không ô nào nhìn trộm tương lai đó?"
    (1) naive_two_actions: cùng seed, nhánh Switch rút thêm số -> hai action thấy hai tương lai.
    (2) primitive_two_actions: tương lai của path B sinh TRƯỚC từ stream riêng -> hai action đọc cùng mảng.
    Zero residual alone does not prove equal futures; also compare background arrays.
    (3) identity2_residual: đẳng thức 2 (L1.2) theo từng đường; khác 0 nghĩa là CRN đã gãy.
    (4) mk_action + predictor_rng: M_K đúng luật lấy mẫu từ stream "predictor"; đưa nhầm stream
        "future" cho nó là rò, và nó sẽ "thắng" oracle không thấu thị.
Used by:
    tests/test_l1_7_streams.py; bản nháp của montecarlo.py (Phase 4).
Seed:
    DEMO_ROOT ghi trong notes/seed_registry.md, dòng "lesson-demo": CHỈ ĐỂ DẠY, không dùng cho claim.
    Kết quả phụ thuộc thuật toán sinh số của NumPy; đã chạy với numpy 2.5.3. Test chỉ kiểm TÍNH CHẤT,
    không chép cứng số ngẫu nhiên. Statistical tests may still change with NumPy versions.
Metric:
    cost (packet·slot, Δt = 1), hiệu Switch − Stay, phần dư của đẳng thức 2.
"""
from fractions import Fraction as F

import numpy as np

from experiments.lessons.l1_2_queue import two_queue_cost
from experiments.lessons.l1_4_factorial import choose

DEMO_ROOT = 144558766427411771296652109119745142241   # supplied demo root; adopted 2026-10-22, not freshly generated
DT = 1                                                 # Δt = 1 slot, như L1.2–L1.6

# Khóa của stream CHỈ gồm vai trò và chỉ số. Không có chỗ cho nhãn ô, action, model hay biến thể.
ROLE = {"episode": 0, "future": 1, "predictor": 2, "branch": 3}
PATH = {"A": 0, "B": 1}


def stream(root, role, *index):
    """Generator của một stream con: SeedSequence(root, spawn_key=(vai trò, *chỉ số)).

    Truy cập ngẫu nhiên: stream(root, "future", 37, PATH["B"]) cho đúng stream của episode 37,
    không cần chạy 36 episode trước.
    """
    if not all(type(i) is int and i >= 0 for i in index):
        raise TypeError(f"Chỉ số stream phải là số nguyên ≥ 0, nhận {index!r}")
    return np.random.default_rng(np.random.SeedSequence(root, spawn_key=(ROLE[role], *index)))


def future_rng(root, episode, path):
    """Stream "future" của một path trong một episode. CHỈ evaluator được gọi hàm này."""
    return stream(root, "future", episode, PATH[path])


def predictor_rng(root, episode):
    """Stream "predictor" của M_K trong một episode. Không bao giờ trùng stream "future"."""
    return stream(root, "predictor", episode)


def mode_path(m0, uniforms, p_onon, p_offoff):
    """Biến innovation (số đều trong [0, 1)) thành chuỗi mode: u < P(giữ mode hiện tại) -> giữ."""
    if m0 not in ("on", "off") or not 0 <= p_onon <= 1 or not 0 <= p_offoff <= 1:
        raise ValueError("invalid mode or transition probability")
    if any(not 0 <= u < 1 for u in uniforms):
        raise ValueError("innovations must be in [0,1)")
    seq = [m0]
    for u in uniforms:
        last = seq[-1]
        keep = p_onon if last == "on" else p_offoff
        seq.append(last if u < keep else ("off" if last == "on" else "on"))
    return seq


def background_B(x, th, uniforms):
    """Traffic nền của B trên slot 0..H-1. Mode slot 0 thuộc state x (đã biết); H-1 innovation tạo w."""
    if type(th["H"]) is not int or th["H"] < 1:
        raise ValueError("H must be a positive integer")
    if len(uniforms) != th["H"] - 1:
        raise ValueError(f"Cần {th['H'] - 1} innovation, nhận {len(uniforms)}")
    modes = mode_path(x[2], uniforms, th["p_onon"], th["p_offoff"])
    return [th["rate_on"] if m == "on" else th["rate_off"] for m in modes]


def path_costs(x, th, bB_stay, bB_switch):
    """Cost và capacity bỏ phí của hai action. Dùng CHUNG cho cách ngây thơ và cách primitive:
    hai cách chỉ khác nhau ở chỗ lấy traffic nền từ đâu."""
    out = {}
    for action, bB in (("Stay", bB_stay), ("Switch", bB_switch)):
        cost, idle = two_queue_cost(x[:2], [th["bA"]] * th["H"], bB,
                                    th["u"], th["cA"], th["cB"], action, dt=DT)
        out[action] = (cost, idle)
    return out


def identity2_residual(costs):
    """(C_Sw − C_St) − Δt·Σ_j (H − j)(I_j(Sw) − I_j(St)).  Bằng 0 khi hai action thấy CÙNG traffic nền."""
    (c_st, i_st), (c_sw, i_sw) = costs["Stay"], costs["Switch"]
    if len(i_st) != len(i_sw):
        raise ValueError("idle paths must have equal horizons")
    H = len(i_st)
    return (c_sw - c_st) - DT * sum((H - j) * (s - t) for j, (s, t) in enumerate(zip(i_sw, i_st)))


def naive_two_actions(seed, x, th, extra_draws):
    """LỖI MINH HOẠ: mỗi nhánh tạo generator từ CÙNG seed, nhánh Switch rút thêm extra_draws số
    (ví dụ để chia gói) TRƯỚC khi rút traffic nền. Trả (traffic Stay thấy, traffic Switch thấy)."""
    rng_stay = np.random.default_rng(seed)
    u_stay = rng_stay.random(th["H"] - 1)
    rng_switch = np.random.default_rng(seed)            # "cùng seed"
    rng_switch.random(extra_draws)                      # lần rút thêm của nhánh Switch
    u_switch = rng_switch.random(th["H"] - 1)
    return background_B(x, th, u_stay), background_B(x, th, u_switch)


def primitive_two_actions(root, episode, x, th, extra_draws):
    """CÁCH ĐÚNG: sinh TRƯỚC traffic nền của B từ stream riêng (future, episode, B); hai action chỉ đọc.
    Ngẫu nhiên riêng của nhánh Switch (nếu có) lấy từ stream "branch", không chạm stream future."""
    bB = background_B(x, th, future_rng(root, episode, "B").random(th["H"] - 1))
    stream(root, "branch", episode).random(extra_draws)   # nhánh Switch rút thêm: vô hại
    return list(bB), list(bB)


def mk_action(x, th, rng, K):
    """M_K: lấy K tương lai mẫu TỪ rng, trung bình Δ̂ = C(Sw) − C(St), rồi chọn bằng choose (hoà -> Stay).

    rng phải là predictor_rng(...). Nếu truyền nhầm một generator trùng stream "future", M_K thấu thị.
    """
    if type(K) is not int or K < 1:
        raise ValueError("K phải ≥ 1")
    total = 0
    for _ in range(K):
        bB = background_B(x, th, rng.random(th["H"] - 1))
        c = path_costs(x, th, bB, bB)
        total += c["Switch"][0] - c["Stay"][0]
    return choose(F(total, K))
