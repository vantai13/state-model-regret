# ctmc-v2 — evaluator hai thang (L7.3 Phần 2, Stage 0)

Doan Van Tai — **AI (Claude) soạn và triển khai theo ủy quyền** (L7.3 Phần 2, Stage 0, 04/11/2026). Đây là exploration,
không phải author-self, không phải claim.

Namespace `ctmc-v2` mở rộng [ctmc-v1](SPEC.md):
- mỗi path có **hai bộ điều biến on-off độc lập, đối xứng**;
- mọi thứ khác giữ nguyên.

Stage 0 chỉ có đại lượng dừng, M0 và zero-fit. **Không có truth** ngoài các regime control có tên ở §6.

## 1. Plant
- **State.** Mỗi path có state (n, m), với m = (σ_f, σ_s) ∈ {−1, +1}². Index 4n + m, m = 1[σ_f = +1] + 2·1[σ_s = +1].
- **Arrival.** Poisson với rate load + σ_f·a_f + σ_s·a_s. Service mũ μ = 10 khi n > 0.
- **Mode.** σ_f đổi với tốc độ 1/T_f, σ_s đổi với tốc độ 1/T_s, độc lập. Arrival bị chặn ở N.
- **Tham số.** (λA, λB, u, T_f, T_s, a_f, a_s, c), mặc định đỉnh a_f + a_s = 6. Tỷ lệ phương sai của thang chậm là
  f = a_s²/(a_f² + a_s²):

  | f | a_f | a_s |
  |---|---|---|
  | 1/2 | 3 | 3 |
  | 1/5 | 4 | 2 |
  | 1/20 | 4,8804 | 1,1196 (làm tròn 4 chữ số; f thực ghi trong case) |

- **Miền.** λA, λB ≥ a_f + a_s; max(λA, λB) + u < 10; u ∈ [1/4, 3]; c = 0; T_f < T_s.
- **Giữ nguyên ctmc-v1.** μ, τ = 1, P1, S0 (backlog cũ, không mode), S1 (state đủ, cả hai mode), bốn ô D19, D22
  (backlog hiện tại), các twin (M0, M1, Margin, Static, Hybrid, Hybrid-MM1, Const, KO), z_∞ và các khai triển zero-fit.
- **Control (a).** Với a_s = 0, bộ điều biến chậm không ảnh hưởng arrival, nên chain gộp đúng về ctmc-v1 với κ = T_f.

## 2. M0: rollout tất định có phản xạ
- Rate kỳ vọng có điều kiện: r̄_m(t) = load + σ_f·a_f·e^{−2t/T_f} + σ_s·a_s·e^{−2t/T_s}.
- C(t) = ∫₀ᵗ (r̄_m − μ) có dạng đóng. Queue phản xạ: q(t) = n + C(t) + max(0, −min_{s≤t}(n + C(s))) =
  C(t) + max(n, −M(t)), với M(t) = min_{s≤t} C(s). M(t) **không phụ thuộc n**.
- **Bổ đề cấu trúc.** d = C′ = L + σ_f·a_f·e^{−2t/T_f} + σ_s·a_s·e^{−2t/T_s}, với L = load − μ < 0. Hàm d có nhiều nhất
  một điểm dừng, và d(∞) = L < 0. Vì vậy dấu của d theo t chỉ có ba dạng:
  - **D** (−): C giảm; q = max(0, n + C).
  - **PM** (+, −): C tăng tới t₂ rồi giảm; q = max(0, n + C) sau đỉnh.
  - **MPM** (−, +, −): C có cực tiểu C₁ tại t₁ và cực đại tại t₂. Nếu n < −C₁, queue chạm 0 tại T_a < t₁, giữ 0 tới t₁,
    rồi q = C − C₁ trên (t₁, t₃) với C(t₃) = C₁, và bằng 0 sau t₃. Nếu n ≥ −C₁, q = max(0, n + C).
- V̂(h) = ∫₀ʰ q có dạng đóng từng đoạn. Các nghiệm t₁, t₂, t₃ và thời điểm chạm 0 tìm bằng bisection 200 vòng trên đoạn
  đơn điệu. Mũ dùng `det_expm1`.
- **Hòa chính xác.** Như ctmc-v1: nếu queue dưới tải nhẹ không chạm 0 trên [0, h], gap của path đúng bằng ∓u·h²/2. Gap
  được dịch ±u·h²/2 và đặt bằng 0 ở các state đó.
- **Sửa sau control (a) attempt01 (04/11, trước mọi zero-fit).** Thêm điều kiện: state cũng được coi là bão hòa nếu
  max|d|·(h − T)² ≤ 1e−12·(1 + h), với max|d| = μ + a_f + a_s.
  - **Lý do:** nếu queue tải nhẹ chạm 0 tại T < h thì gap lệch giá trị tuyến tính tối đa max|d|·(h − T)².
  - **Lỗi đã thấy:** ở các state có T trùng h tới khoảng 1e−9 (n nguyên, tải hữu tỷ, e^{−2h/T} rất nhỏ), dấu gap do
    làm tròn quyết định. Hai path cùng sát hòa thì quyết định lật, kéo theo lệch 7,5e−4 pp so với ctmc-v1 ở regime
    (8, 7, 1, κ = 2), h = 20.
  - **ctmc-v1 không sửa** vì kết quả của nó đã khóa.

## 3. Truncation và đại lượng dừng
- **N.** Phân phối dừng của queue vô hạn là matrix-geometric với 4 pha (logarithmic reduction). N_tail là level nhỏ nhất
  có đuôi ≤ 1e−13; N = max(40, ⌈1,2·N_tail⌉).
- **Mỗi chain:** π, r, g, T_int = π[(f − r)g]/Var (như v1), và T_relax = 1/|Re λ₂(Q)|. λ₂ tìm bằng shift-invert Arnoldi,
  là giá trị riêng khác 0 có phần thực lớn nhất.
- **Công thức xấp xỉ §3d của realism v2** (chỉ là phép tính dừng):
  T_int^approx = (1 − f)·r₁(load, T_f)·T_f + f·r₁(load, T_s)·T_s, với r₁(load, κ) = T_int/κ của chain ctmc-v1 một thang,
  a = 6, cùng tải.

## 4. Guard
Truth (V ở h hữu hạn, các L/G, quyết định của M1) bị **từ chối** trừ ba trường hợp:
1. a_s = 0 (control (a), trùng ctmc-v1);
2. regime nằm trong `CONTROL_REGIMES` (§6), là các regime bị loại khỏi mọi case list và mọi thẻ;
3. `results/explore_ctmc/locks_l73.json` có sha256 của thẻ tác giả, và thẻ trên đĩa còn khớp.

## 5. Case list (write-once, `results/explore_ctmc/cases_l73/`)
Lưới: f ∈ {1/20, 1/5, 1/2} × T_s/T_f ∈ {10, 100} × T_f ∈ {1/5, 1}. Tải tối đa λ + u ≤ 9 để giữ chi phí.
- **asym:** các họ (u, λA, x) × chuỗi h phủ h/T_int ∈ [0,3; 40], dày ở (4; 7] và (7; 15].
- **mid:** bộ horizon giữa hai thang, h/T_f ≥ 10 và h/T_s ≤ 0,1 (chỉ tồn tại ở T_s/T_f = 100, với h = 10·T_f).
- **sobol:** Sobol trên (u, λA, λB, tổ hợp thang, log h/T_int ∈ [0,3; 40]).
- **xs:** lát x cho x* (dấu của z_∞).

Mọi case có N ≤ 3000 (miền D22). Case vượt ngưỡng bị loại và đếm.

## 6. Control (tiêu chí ghi trước khi chạy)
- **(a)** a_s = 0 so với ctmc-v1 ở 3 regime: |Δ| ≤ 1e−6 pp cho mọi %; ≤ 1e−9 cho tỷ lệ Switch, cộng tie mass; ≤ 1e−9
  tương đối cho r, T_int. Áp dụng cho cả zero-fit (z_∞, z_pred1, z_F/z_V) và truth.
- **(b)** M0 dạng đóng so với tích phân số của ODE phản xạ (lưới mịn, trapezoid, min chạy số). Sai số tương đối
  ≤ 1e−6 ở mọi state của 2 chain, ở h ∈ {T_f/2, T_f, T_s, 10·T_s, ∞}. Ghi riêng số state thuộc dạng MPM.
- **(c)** Monte Carlo đầu-cuối có common random numbers ở 2 regime control: |MC − chính xác| ≤ 3,5·SE cho bốn L và sáu
  contrast.
- **(d)** N → 2N:
  - truth ở regime control nặng nhất: mọi contrast đổi ≤ 0,01 pp;
  - zero-fit ở regime nặng nhất của case list: z_∞, z_pred1 đổi ≤ 0,01 pp.
- **(e)** Bit-identity local so với GCP cho JSON zero-fit của case N lớn nhất và của các regime control (bỏ cpu, host).
  Cần GCP; nếu không truy cập được thì ghi NOT RUN, không thay bằng thứ khác.
- **(f)** S, M, G_M ≥ −1e−9 pp trên mọi dòng của regime control.
- **(g)** Thêm, không chặn:
  - V(h) qua hai cách (≤ 1e−8 tương đối);
  - π so với matrix-geometric;
  - tái lập bảng dừng của mentor (tải 8,5, T_f = 0,5, T_s = 50, f ∈ {0, 0,05, 0,2, 0,5}). Chỉ báo cáo.

Một MUST trượt thì dừng, sửa, chạy lại toàn bộ control.

`CONTROL_REGIMES` (λA, λB, u, T_f, T_s, a_f, a_s):
- C2a = (7, 15/2, 1, 1/5, 2, 4, 2);
- C2b = (13/2, 7, 3/2, 1, 10, 3, 3).

Thiết kế case list kiểm theo tuple (λA, λB, u, T_f, T_s, a_f, a_s) và loại hai regime này; một test bảo đảm không có case
nào trùng.
