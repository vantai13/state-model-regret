# CARD PL: posterior học từ lịch sử hữu hạn + phạm vi twin có rate theo trạng thái (letter v8.4)

Người phụ trách: **Doan Van Tai**. Tác giả giao toàn quyền thiết kế và chạy (19/11/2026, "tôi cho quyền bạn thiết kế và chạy").
Thiết kế, dự đoán và luật đưa vào paper do **Claude** viết TRƯỚC mọi outcome. Codex cài đặt và chạy. Không có mentor review.
Đây là **exploration bổ sung cho letter**, không đổi verdict đã khóa.

## Câu hỏi
- **Q1 (reviewer 7/8, "oracle posterior").** Luật stale của letter dùng kernel thật e^{Q₀τ}. Nếu thay bằng posterior học từ một
  lịch sử Stay hữu hạn (cặp trạng thái cách nhau τ, như letter Sec. I nói là làm được), harm của M0 còn không? Correction còn giữ
  regret thấp không?
- **Q2 (R2, phạm vi Remark 2).** Twin có số hạng dừng ước lượng từ telemetry hiện tại (ŝ(x), twin T4 của R2-O1): khi dấu ŝ(x)
  đổi theo trạng thái thì G_S/h có tiến tới slope dự đoán không, và khi cùng dấu thì G_S có bằng 0 khi h lớn không?

## Đã thấy (exposure)
W1b (G_S, shares, tie, regret cho 93 regime với posterior thật); R2-O1 pilot (regime `Za3_u1_lA7_x-1_k1-20`: T0/T1–T3/T4 ở
h/T_int ≤ 300, slope T4 −0,2130 dự đoán và −0,2125 đo; 12 regime đã chọn và w* của chúng); P2-TIER2 (dấu m₀ = E_{π₀}Δ̂ khớp dấu s
ở 64/93, gồm 42/42 Switch-optimal; paired hybrid–stationary). Chưa ai tính posterior học từ dữ liệu.

## Mô hình và tính toán (đúng letter Sec. II; tái dùng code W1b/R2-O1, không viết lại engine)
- 92 regime matched của W1b (bỏ `Za7p5_u3-2_lA31-4_x1-3_k2`, fresh baseline unresolved như letter). c = 0, tie → Stay.
- Hai path độc lập dưới mỗi action. Gap fluid và chi phí thật tách theo path:
  Δ̂(h,x) = d_A(h,x_A) + d_B(h,x_B) + c; g(h,x) = V₁ − V₀ + c = g_A(h,x_A) + g_B(h,x_B) + c.
- **Công thức G_S dùng (chính xác, rẻ):** G_S = Σ_y π₀(y) a_old(y) G(h,y) − Σ_x π₀(x) a_new(x) g(h,x), với
  G(h,y) = Σ_p (e^{Q_{p,0}τ} g_p(h,·))(y_p) + c (kernel THẬT cho đánh giá), π₀ = π_A ⊗ π_B. Kiểm tương đương với W1b (H-PL1).
- Tuổi τ ∈ {T_int (chính), 3T_int (phụ)}; h/T_int ∈ {1, 3, 10, 30, 100}.

### Posterior học (Q1)
- Mỗi path p, mỗi seed r ∈ {0..4}: mô phỏng chuỗi Stay của path ở lưới polling δ = τ/10 bằng ma trận chuyển chính xác
  P_δ = expm(Q_{p,0} δ), trạng thái đầu ~ π_{p,0}. Độ dài lịch sử L/T_int ∈ {30, 100, 300, 1000} (prefix của một lịch sử dài nhất).
  Cặp (Y_k, X_k) = (Z_k, Z_{k+10}). Seed test: 7400000 + 1000·(chỉ số regime theo thứ tự id) + 100·(0 nếu τ=T_int, 1 nếu 3T_int) + r.
  Seed pilot riêng: 7490000 + ….
- Ước lượng k-NN: m̂_p(h,y) = trung bình d_p(h, X_k) trên các cặp có cùng mode với y và backlog gần n_y nhất, k = 50 (gồm mọi
  cặp đồng khoảng cách ở biên); nếu mode có < 50 cặp thì dùng mọi cặp của mode; nếu mode không có cặp nào thì dùng mọi cặp.
- Luật stale học: M0: a_old(y) = 1{m̂_A + m̂_B + c < 0}; hybrid: 1{m̂_A + m̂_B + c + hŝ < 0}, ŝ ∈ {s thật, s_MM1}.
- Đối chứng: kernel thật (W1b), plug-in (1{d_A(y_A)+d_B(y_B)+c < 0}).
- Báo: G_S (%C_ref và packet·s), both-side regret, share chọn action dài hạn, theo regime × τ × h × L × seed.

### Twin T4 trên mọi regime (Q2)
- Như R2-O1: ŝ_nc(x) = Σ_p [r(ℓ_{p,1}+m_pαw*) − r(ℓ_{p,0}+m_pαw*)], r(λ) = ρ/(1−ρ), w* = max{w ∈ {1,1/2,1/4,1/8,1/16}:
  max ℓ + αw < 0.95μ}; không có w* thì regime không đủ điều kiện. Fresh 1{Δ̂ + hŝ_nc(x) < 0}, stale 1{E[Δ̂ + hŝ_nc(X)|Y] < 0}
  (kernel thật). Kèm T1 (ŝ = s hằng) làm đối chứng.
- Slope dự đoán (tính TRƯỚC truth, ghi vào `predictions.json`): σ = s·[Pr(a_old^∞=1) − Pr(a_new^∞=1)], a_new^∞ = 1{ŝ_nc(X)<0},
  a_old^∞ = 1{E[ŝ_nc(X)|Y]<0} (với trạng thái ŝ_nc = 0, dùng dấu Δ̂(h̄,·) như R2-O1). Phân lớp: **đổi dấu** nếu cả hai dấu của
  ŝ_nc(X) có π₀-mass > 1e−9, ngược lại **cùng dấu**; η = min_x |ŝ_nc(x)| trên support; M = max_x |Δ̂(h̄,x)|.
- Đánh giá: lớp đổi dấu ở h = 300T_int; lớp cùng dấu ở h = 1.1·max(h̄, M/η) (tính bằng gain–bias, không expm trực tiếp nếu h lớn).

## Kiểm định (chấm cơ học)
- **H-PL1 (control).** Pipeline kernel thật tái lập G_S của W1b tại mọi ô chung (τ = T_int, h có trong W1b) với sai số tương đối
  ≤ 1e−9 (hoặc tuyệt đối ≤ 1e−9 C_ref). FAIL → dừng, báo BUG, không chấm phần còn lại.
- **H-PL2 (harm còn với posterior học).** Quần thể: regime có G_S^true < −0.1% C_ref ở τ = T_int, h = 30T_int (n_true).
  Thống kê: số regime trong đó median theo 5 seed của G_S^learned(L = 100T_int) < −0.1% C_ref. PASS nếu ≥ 0.8·n_true.
  NOT_EVALUABLE nếu n_true < 10.
- **H-PL3 (correction bền).** Hybrid (s thật), τ = T_int, h = 30T_int: số regime có both-side regret ≤ 0.5% ở MỌI seed với
  L = 100T_int ≥ (số regime đạt với kernel thật) − 2.
- **H-T4a (đổi dấu).** Regime đủ điều kiện, lớp đổi dấu, |σ| > 1e−9: PASS nếu |G_S/h − σ|/|σ| ≤ 5% ở h = 300T_int trong ≥ 90%.
- **H-T4b (cùng dấu).** Lớp cùng dấu: PASS nếu |G_S| ≤ 1e−9·C_ref ở h đánh giá trong mọi regime của lớp.
- H-T4a/b: NOT_EVALUABLE nếu lớp có < 3 regime.

## Dự báo (không phải kiểm định, Claude)
- F1: n_true ≈ 72 (42 Switch-optimal + khoảng 30 Stay-optimal, theo W1b).
- F2: ở Switch-optimal, harm còn ở mọi L (cả fallback không thông tin cũng gộp về Switch, vì dấu m₀ khớp 42/42).
- F3: ở Stay-optimal, L nhỏ làm mất harm thường hơn L lớn.
- F4: 20–40 trong 92 regime đủ điều kiện T4; đa số lớp đổi dấu.

## Luật đưa vào paper (cố định trước khi chạy)
- **Q1 → Sec. V-A, một câu, bất kể kết quả.** Số regime còn harm với posterior học (L = 100T_int, median 5 seed) trên n_true; số
  regime hybrid đạt ≤ 0.5%. Nếu H-PL2 FAIL, paper nói thẳng harm của M0 phụ thuộc posterior chính xác, và sửa limitations
  tương ứng. Sửa câu limitations về "stale posterior uses true Stay dynamics" theo kết quả.
- **Q2 → Remark 2, thay ví dụ một regime.** Đếm số regime lớp đổi dấu có slope khớp, và số regime lớp cùng dấu có G_S = 0. Nếu
  H-T4a hoặc H-T4b FAIL thì báo số thật, và Remark chỉ giữ phần đã được chứng minh (điều kiện đủ) kèm ví dụ cụ thể.
- Mọi số vào paper qua ledger (`% ID`). Không chọn L, k hay seed sau khi xem kết quả.

## Cài đặt và chạy (Codex)
1. Code: `experiments/letter/pl_posterior.py`; tests: `tests/test_pl_posterior.py` (tối thiểu: công thức G_S tách path khớp tính
   trực tiếp 4D trên regime nhỏ; k-NN đúng trên ví dụ tay; kernel thật cho kết quả của W1b trên 1 regime; T4 slope pilot R2-O1
   tái lập). Outputs: `results/letter/pl_posterior/`.
2. Pilot (seed pilot, 2 regime gồm regime NẶNG NHẤT theo N) để đo thời gian; dự phóng toàn bộ. Ngân sách local 4 CPU-h; nếu dự
   phóng vượt, dừng và báo (Claude sẽ chuyển sang GCP).
3. Tính và ghi `predictions.json` (n_true, danh sách regime theo quần thể, w*, lớp, σ, η, M, h đánh giá T4) TRƯỚC truth.
4. Ghi `lock.json` (sha256 của card, code, tests, predictions, input W1b được dùng) rồi DỪNG ở đây (Claude commit lock).
5. Truth run một lần (lệnh riêng do Claude chạy sau commit lock), không retry/resume. Raw ghi trước khi chấm.

## Sửa đổi A1 trước lock (Claude, 20/11/2026 sau pilot; chỉ dựa trên thời gian, chưa ai xem outcome)
- Codex hết quota sau khi viết code và test. Claude tiếp quản, sửa lỗi lấy biên độ α (33 raw không có `case.a`; nay lấy từ
  evaluation đã lưu, có kiểm khớp) và chạy pilot. Lần pilot hỏng giữ ở `pilot_attempt01_failed/`.
- Pilot (2 regime, gồm regime nặng nhất) dự phóng toàn bộ là 1016 CPU-h (Q1 khoảng 153 CPU-h; regime nặng nhất khoảng 42 CPU-h,
  do V(h) tới 100 T_int trên chain 13k trạng thái). Không khả thi trong một phiên, kể cả trên GCP.
- **Quần thể truth:** các regime có chi phí Q1 dự phóng ≤ 3600 CPU-s (theo đúng hệ số của `pilot.json`, tính từng regime).
  Danh sách cố định trong `predictions.json` trước truth. Các regime còn lại ghi NOT_RUN (tính toán), báo đủ trong kết quả và
  trong paper. Mọi kiểm định (n_true, H-PL2, H-PL3, H-T4a/b) tính trên quần thể này. Luật đưa vào paper giữ nguyên, kèm mẫu số.
- **Chạy:** một lần gọi `truth`, 9 tiến trình (mỗi regime một tiến trình, giới hạn CPU riêng = 4 × dự phóng + 600 s), không
  retry/resume. Mọi thứ khác trong thẻ giữ nguyên.
