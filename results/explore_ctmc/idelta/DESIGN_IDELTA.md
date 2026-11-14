# I_Δ — interaction tầng prediction và cơ chế biên rỗng (thiết kế + dự đoán trước khi chạy)

Doan Van Tai — **AI (Claude) soạn và chạy theo ủy quyền** ("nếu chưa có hãy thiết kế và chạy xem thử",
14/11/2026). Exploration, không phải author-self, không confirmation, không đổi RQ/contract/nhãn PC/Gate.
File này viết **trước** khi viết runner và trước mọi outcome; runner ghi sha256 của file vào output.

## 0. Câu hỏi (ba tầng, tăng dần)

- Q1 — Có interaction ở tầng quyết định không? Đo bằng Γ = L10 + L01 − L00 − L11 (đã có trong engine).
- Q2 — Có interaction ngay ở dự đoán, trước ngưỡng không? Đo bằng I_Δ = d11 − d10 − d01 + d00.
- Q3 — Biên queue rỗng có phải nguồn của I_Δ không? Thay đổi backlog hiện tại của B (rỗng ↔ có backlog),
  giữ mọi thứ khác, đo I_Δ; kiểm giải thích thay thế (biên trên/buffer, mode, số học); nối sang Γ.

## 1. Đã có trong repo (kiểm 14/11/2026, local + GCP `~/smr`)

- Định nghĩa I_Δ và guard mean-zero: L1.5 (`notes/01_claim_boundary_v0.md` §L1.5); quyết định báo
  E|I_Δ|, P(|I_Δ|>δ), δ = ε·Cref: thẻ 9/DL-020 (thẻ nay chỉ còn trong lịch sử git).
- Engine A00 `factorial_core.aggregate` tính E|I_Δ| và quantile |I_Δ|; A04 (L3.5) đã đo cho 38 ô native
  (`results/A04/20261027_01/main_final.csv`, đã archive ở 3a72482d; bản sao trên GCP `~/smr`).
- Cơ chế: T08 P-clip (fluid slotted v1.3): ngoài vùng Clip thì M0 = M1 từng action, nên sai số gap = 0;
  L4.7 Part B kiểm 48 state native (24 ngoài Clip: max|d−dh| = 0).
- CTMC ctmc-v1: `evaluate(arrays=True)` trả d, dh, posterior; **chưa** ghép thành I_Δ, chưa quét backlog.

Còn thiếu: phép thử I_Δ ở mức mạng có quét backlog B (rỗng ↔ backlog), phân rã cơ chế, kiểm giải thích
thay thế và counterfactual "chỉ ngưỡng" cho Γ.

## 2. Đại số dùng chung (không phải outcome)

Ô (S, M): S1 = state hiện tại x, S0 = quan sát cũ y (posterior của contract), M1 = model thật, M0 = mean rollout.
d11 = Δ(x), d10 = Δ̂(x), d01 = E[Δ|y], d00 = E[Δ̂|y]. Đặt e(x) = Δ̂(x) − Δ(x) (sai số gap của M0):

    I_Δ(x, y) = −e(x) + E[e | y],   E[I_Δ | y] = 0   (tower; vì vậy báo E|I_Δ| chứ không báo mean).

Gap tách theo path và hai path độc lập, nên I_Δ = I_A(x_A, y_A) + I_B(x_B, y_B). "Giữ mọi thứ khác, chỉ đổi
backlog B" làm I_Δ thay đổi đúng bằng −[e_B(x_B) − e_B(x_B')].

**Phân rã biên (CTMC, chính xác tới truncation):** mỗi path/action, với V_free = rollout tuyến tính không cắt,

    V = V_free + μ·I0 − BN,   V̂ = V_free + C0,
    I0 = ∫₀ʰ (h−s) P(n_s = 0) ds   (idle thật — biên rỗng),
    BN = ∫₀ʰ (h−s) E[λ(m_s) 1{n_s = N}] ds   (arrival bị chặn ở N — biên trên),
    C0 = V̂ − V_free ≥ 0   (đường mean bị cắt ở 0).

Suy ra e_l = Δ_action[C0] − μ·Δ_action[I0] + Δ_action[BN]: noise Poisson và mode chỉ vào e qua các số
hạng biên. Đây là hệ quả của tuyến tính kỳ vọng, nên nó **không phải bằng chứng độc lập**. Phần thí nghiệm
kiểm số học, độ lớn, vị trí, dấu và liên kết sang Γ.

## 3. Thiết kế

### Part F — fluid slotted (plant contract v1.3), rational chính xác
Một path, H = 10, dt = 1/20, κ = 3/10, λ = 7, u = 2, μ = 10, a = 6 (ví dụ của L4.7). Dùng lại
`check_clipping.exact_reference` (Bellman rational) và `rational_mean` (M0). Quét q ∈ {0, 1/20, …, 5},
mode ∈ {OFF, ON}, cho path B (Stay: managed 0, Switch: managed u) và path A (ngược lại).
e_l(q, m) = [M0(Sw) − M0(St)] − [M1(Sw) − M1(St)] (Fraction). Ngưỡng dự báo
t*(m) = max over actions `threshold(H, increments, m)`.

### Part C — CTMC ctmc-v1 (a = 6, μ = 10, τ = 1, c_sw = 0)
**Regime (luật chọn cố định trước khi tính):** `cases_l75/sobol.json`, mỗi stratum (neg, band, pos) lấy regime
hình của L7.5 (TN0003, TB0007, TP0079) cộng hai id khác đầu tiên theo thứ tự file:
TN0003, TN0000, TN0004, TB0007, TB0001, TB0003, TP0079, TP0003, TP0004. h = `hs[0..3]` của case
(≈ 0,3 / 1 / 3 / 7 × T_int_max) → 36 dòng.

Mỗi dòng đo:
1. Quyết định: L00..L11, Cref, G_S, G_M, Γ từ `ctmc.evaluate` (disagree=False); tái tính bằng `pair_sum`.
2. Prediction: E|I_Δ|, P(|I_Δ| > δ) với δ ∈ {0,1; 0,5; 1}% Cref, q50/q90/q99 của |I_Δ| (tính chính xác trên
   cặp (y, x) của hai path bằng sort + cumsum; bỏ cặp có trọng số < 1e−22 và ghi khối lượng bị bỏ),
   E_π|e|, bias = E_π e.
3. Cơ chế: residual identity; E|I_Δ| khi bỏ số hạng BN (biên trên); dose–response e_l(n, m) với
   n = 0 … n_hi (n_hi = quantile 1 − 1e−9 của π_Stay của path); P_hit(n, m) = P(chạm 0 trong h) dưới từng action
   (chain hấp thụ); n_reach = n nhỏ nhất sao cho mọi n' ≥ n (≤ n_hi) có max_action P_hit ≤ 1e−6;
   n_1e-3 = n nhỏ nhất sao cho mọi n' ≥ n (≤ n_hi) có |e_l(n', m)| ≤ 1e−3·max_n |e_l(n, m)|;
   tỷ lệ Σ π|e_l| trong tập R = {max_action P_hit ≥ 1e−6} và khối lượng π(R).
4. Ví dụ 2×2 (h = hs[1] ≈ T_int): y_B = 0, y_A = mode của p(y_A), x_A = (y_A, low).
   "B rỗng": x_B = (0, low); "B có backlog": x_B = (min(n_reach_B(low), n_hi_B), low). In d00, d10, d01, d11, I_Δ.
5. Liên kết sang Γ (counterfactual, cùng dữ liệu): b_l = E_π e_l.
   Γ_add: M0 thay bằng Δ + b_A + b_B (sai số hằng, I_Δ ≡ 0 → interaction chỉ do ngưỡng);
   Γ_−A: chỉ bỏ phần phụ thuộc state của e_A (thay bằng b_A), giữ e_B; Γ_−B tương tự.

Chạy một lần trên host chuẩn Phase 7 `dt4n-research-01` (source `env.sh`), thư mục output mới
`results/explore_ctmc/idelta/run01/`. Không sửa file đã khóa; không đụng amplitude held-out.
Trần: 2 CPU-giờ cho toàn bộ Part C.

## 4. Dự đoán (AI viết trước khi chạy; không phải của tác giả)

- **P1** (Q2): mọi dòng có E|I_Δ| ≥ 0,5% Cref và E|I_Δ| > |Γ|. (Căn cứ: A04 fluid 38/38 ô có E|I_Δ| 0,2–14,5%
  Cref ≫ |Γ| ≤ 1,07%; CTMC chưa từng đo nên đây là dự đoán có rủi ro.)
- **P2** (control số học): residual |V − V_free − μ·I0 + BN| ≤ 1e−7·max(1, max|V|) ở mọi chain/h;
  |E[I_Δ|y]| ≤ 1e−9·(h·r_Stay) ở mọi y; L tự tính khớp `evaluate` (|ΔΓ| ≤ 1e−7 pp).
- **P3** (giải thích thay thế: biên trên/buffer): bỏ BN làm E|I_Δ| đổi ≤ 1e−6 tương đối ở mọi dòng.
- **P4** (fluid, ngưỡng sắc): e_B(q, m) = 0 chính xác (Fraction) với mọi q ≥ t*(m), và ≠ 0 ở ít nhất một
  q < t*(m), cho cả hai mode; tương tự cho path A.
- **P5** (dấu khi B rỗng, mode thấp): e_B(0, low) < 0 và e_A(0, low) > 0 ở mọi dòng CTMC. Lý do: ở state rỗng,
  mode thấp, đường mean bị ghim ở 0 dưới cả hai action, nên M0 coi thêm tải vào B là "miễn phí" trong khi truth
  thì không. Hệ quả: I_Δ(B rỗng) − I_Δ(B backlog) > 0.
- **P6** (dose–response): ở mỗi (dòng, path, mode) có n_reach ≤ n_hi: |e_l(n_reach, m)| ≤ 1e−3·max_n|e_l(n, m)|.
  Ô có n_reach > n_hi được ghi NOT_EVALUABLE (reach vượt bulk), không tính là PASS.
- **P7** (thang theo h): trong mỗi (regime, path, mode), n_reach không giảm khi h tăng qua bốn mức.
- **D1** (mô tả, AI đoán): |Γ − Γ_add| ≥ 0,25·|Γ| ở ≥ một nửa số dòng có |Γ| ≥ 0,01 pp.

Một control (P2/P3) trượt → dừng, sửa, chạy lại; ghi attempt cũ. P1/P4–P7 trượt → báo nguyên văn,
không chỉnh dự đoán/ngưỡng sau khi thấy kết quả.

## 5. Không nhận

Không confirmation (regime và Γ của L7.5 đã lộ; I_Δ thì mới). Ở plant này, phân rã biên đúng theo toán học,
nên "biên rỗng là nguồn của I_Δ" là hệ quả của plant, không phải phát hiện thực nghiệm về mạng thật. Bằng
chứng về cơ chế mạng thật cần plant/trace khác. Không novelty, không đổi G1.
