# ctmc-v1 — evaluator CTMC MMPP/M/1 hai path (L7.1)

Doan Van Tai — **AI (Claude) soạn và triển khai theo ủy quyền** (lesson 7.1). Đây là exploration,
không phải author-self, không phải claim. Namespace `ctmc-v1`: plant khác plant fluid của contract v1.3;
giữ P1, S0/S1, bốn ô D19 và estimand regret, đổi luật queue.

## Plant
- Mỗi path có state (n, m), n = 0..N (số packet trong hệ), m ∈ {0 = thấp, 1 = cao}; index 2n + m.
- Arrival Poisson, rate `load + σ_m·a` với σ_0 = −1, σ_1 = +1, a = 6. Service mũ μ = 10 khi n > 0.
  Mode đổi tốc độ 1/κ mỗi chiều (P(cùng mode sau t) = (1 + e^{−2t/κ})/2 = keepR2). Cắt: arrival bị chặn ở N.
- Stay: A mang λA+u, B mang λB. Switch: A mang λA, B mang λB+u. Action tức thời, giữ suốt h; c_sw cộng một
  lần vào Switch. τ = 1. Miền: λA, λB ≥ 6, max(λA, λB) + u < 10, u ∈ [1/4, 3], c_sw = 0 (Stage F mới có c > 0).
- **Held-out:** a ≠ 6 bị từ chối ở mọi hàm tính L/G; a = 0 chỉ được dùng cho control V2 (phân phối dừng).

## Truncation N
Cho mỗi path, lấy tải nặng hơn trong hai action (A: λA+u; B: λB+u). Phân phối dừng của queue vô hạn là
matrix-geometric π_n = π_0 R^n. N_tail = n nhỏ nhất có π_inf(level ≥ n) ≤ 1e−13; N = max(40, ⌈1,2·N_tail⌉).
V5 kiểm N → 2N ở góc nặng.

## Đại lượng một chain (load, κ, N)
- π: nghiệm chính xác của πQ = 0 trên chain cắt (sparse LU); r = π·f, f(n, m) = n.
- g: phương trình Poisson Qg = −(f − r), πg = 0. T_int = π[(f − r)g]/Var_π(n).
- V(h) = E[∫₀ʰ n dt | x] = h·r + g − e^{Qh}g (cách 1). Cách 2: exponential của generator bổ sung
  [[Q, f], [0, 0]] nhân e_last. V4 đòi hai cách khớp.
- M0: rollout tất định với rate kỳ vọng có điều kiện r̄(t) = load + σ·a·e^{−2t/κ}. Vì load < μ, q(t) =
  max(0, n + C(t)), C(t) = (load − μ)t + σ·a·(κ/2)(1 − e^{−2t/κ}); Vhat(h) = ∫₀ʰ q. Vhat(∞) hữu hạn.
- **Hòa chính xác của M0 (sửa 03/11 trước khi khóa):** nếu queue của một path dưới tải nhẹ hơn không chạm 0 trên
  [0, h] thì rollout tuyến tính theo tải và gap của path đó đúng bằng ∓u·h²/2. Gap từng path được dịch ±u·h²/2
  (hai dịch chuyển triệt tiêu trong tổng) và đặt đúng 0 ở state bão hòa; hai path cùng bão hòa → hòa chính xác →
  Stay, như luật certified tie của contract. Trước khi sửa, dấu ở các state này do làm tròn quyết định.
- **Môi trường số:** mọi lượt chạy source `env.sh` (tắt AVX-512 của numpy, OpenBLAS kernel Haswell); expm1 của
  M0 dùng `det_expm1` (chỉ +, ×, ÷ làm tròn chuẩn). Lý do: V7 attempt01 trượt vì kernel SIMD khác nhau giữa
  AMD local và Xeon GCP.

## Population P1 và bốn pipeline
- X ~ π_Stay từng path, độc lập. Y = n tại t0 − τ (không có mode). Posterior S0 cho vector v:
  E[v(X) | y] = Σ_m π(y,m)·(e^{Q_Stay·τ}v)(y,m) / p(y).
- Gap thật d_A = V_A[λA] − V_A[λA+u], d_B = V_B[λB+u] − V_B[λB]; Δ(x) = d_A + d_B + c. Gap M0 dh tương tự.
- Switch khi gap < 0 (strict); hòa → Stay. L_sm = h·r_Stay + E[a_sm·Δ]; S0 dùng E[Δ | Y] (tower property).
- Tổng trên mọi cặp tính chính xác: sắp xếp gap path B, cộng dồn, searchsorted. Không Monte Carlo.
- Contrast lấy từ phần E[a·Δ] (không trừ hai số cỡ h·r). Mọi % là % của C_ref = L11.

## Twin (cùng mảng, cùng P1)
M0, M1 trên S0/S1; Margin (Switch khi Δ̂ < −ρ·h·r_Stay, ρ ∈ {0, 1/200, 1/100, 1/50, 1/20}, chọn ρ tốt nhất
riêng cho S0 và S1); Static (Switch khi h·s + c < 0, s = r_Switch − r_Stay); Hybrid (Switch khi Δ̂ + h·s < 0,
trên S0 và S1); Const (action có E_π[J] nhỏ hơn); Hybrid-MM1 (s thay bằng s của M/M/1 bỏ burst).
z_∞ = 100·s·(F_old − F_new)/r_min với F là tỷ lệ Switch của M0 ở h = ∞.

## Control và tiêu chí (ghi trước khi chạy)
- V1 u = 0: bốn L bằng nhau chính xác (==), mọi contrast = 0.
- V2 a = 0: π khớp hình học cắt (1 − ρ)ρ^n/(1 − ρ^{N+1}) với sai số tuyệt đối ≤ 1e−12; mean khớp.
- V3 Monte Carlo đầu-cuối ở 3 regime (burn-in Stay ≥ 30·T_int từ queue rỗng → Y → τ → X → action từng
  pipeline → chi phí tới h, common random numbers cho hai action). Đạt khi |MC − chính xác| ≤ 3,5·SE cho
  bốn L và sáu contrast ở cả 3 regime. ID của 3 regime ghi trong controls và loại khỏi mọi phép chấm.
- V4 hai cách tính V: sai khác tương đối ≤ 1e−8 (so với max|V|) ở h ngắn và h ≥ 20·T_int.
- V5 (đầu Stage D) N → 2N ở góc nặng nhất: mọi contrast chuẩn hóa đổi ≤ 0,01 pp.
- V6 mọi dòng: S, M, G_M ≥ −1e−9 % (sai số số học), vi phạm → cờ.
- V7 các regime V3 cho JSON giống từng bit trên mọi máy (trừ cpu, host).
- V9 M0 dạng đóng so với tích phân số: sai số tương đối ≤ 1e−7. V10 posterior qua expm_multiply so với
  expm dày ở chain nhỏ: ≤ 1e−10. V11 Static ở c = 0 trùng luật sign(δ) (s < 0 ⇔ λB < λA).
- Một MUST trượt → dừng, sửa, chạy lại toàn bộ control.
