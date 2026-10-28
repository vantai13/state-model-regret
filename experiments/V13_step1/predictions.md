# v1.3 bước 1 — ba dự đoán viết trước khi tính dữ liệu theo từng state

Người phụ trách: **Doan Van Tai** · 28/10/2026 · nhãn **[DISCOVERY]** · DL-062.
AI (Claude) viết theo ủy quyền trực tiếp ("viết 3 prediction rồi chạy kiểm tra thử").
Đây không phải dự đoán do tác giả tự viết, và không là understanding artifact.

## Đã thấy trước khi viết (khai thật)

- Phân loại ba chế độ **ở mức ô** trên 38 ô main và 10 ô R (review Phase 3, đã kiểm lại):
  mù M19–M22 (và R04); đảo dấu M01, M03 (và R01, R11); 32 ô main cùng dấu.
- Bảng "lens hằng số" của reviewer (`lens_check.py`) trên 38 ô main, gồm G_M|S1 thật. Chưa tính
  tương quan hạng của lens; đã thấy tương quan hạng −0,41 giữa E|e_M|/stakes và G_M|S1/stakes.
- **Chưa thấy:** bất kỳ đại lượng theo từng state nào (δ̂, δ, e_M theo state, khối lượng idle
  của đường fluid, cửa sổ gần biên). Mọi số dưới đây được tính sau commit chứa file này.

Vì nhãn ô đã biết, kết quả ở đây chỉ là kiểm tính nhất quán của một cơ chế trên dữ liệu
discovery, **không** phải bằng chứng xác nhận. Xác nhận cần mẫu regime mới (bước 3 của review).

## Định nghĩa dùng chung

38 ô main, ref 2, dt = 1/240 s; bảng `Side` của engine A00 cho A và B (không đổi engine).
Với state x_l của queue l: δ̂_l là thành phần gap theo M0, δ_l là thành phần thật, e_l = δ̂_l − δ_l.

- **Đường fluid chạm rỗng (certified):** hàng A: δ̂_A(x) > err_dh(A), tức đường trung bình của A
  dưới Switch idle trong h. Hàng B: δ̂_B(x) < −err_dh(B), tức đường trung bình của B dưới Stay idle.
- **Không chạm rỗng (certified):** certificate `zero_dh` của engine, hoặc δ̂ = 0 chính xác.
- Các state còn lại là "chưa phân giải" và được báo riêng.
- I_A, I_B: tổng khối lượng D_l trên các state có fluid chạm rỗng (certified) của A, B.
- **Một phía B:** I_A ≤ 0,05 và I_B ≥ 0,20. **Một phía A:** I_B ≤ 0,05 và I_A ≥ 0,20.
- Target thiết kế lấy từ cột `targets` của A04 (tầng 0): 0,3 nghĩa là Stay đúng theo thiết kế,
  0,7 nghĩa là Switch.

## P(a) — mù là do cả hai đường fluid không chạm rỗng (sanity)

**Dự đoán:** ở mọi ô mù (M19–M22), 100% support của cả A và B được chứng nhận không chạm rỗng,
tức EΔ̂ = 0 không đến từ hai phía triệt tiêu nhau. Ở mọi ô không mù, I_A + I_B > 0.
**PASS** khi cả hai vế đúng. Gần như đồng nhất thức (δ̂_A ≥ 0 ≥ δ̂_B); vai trò là sanity check.

## P(b) — đảo dấu là khi M0 chỉ thấy một phía của trade-off

**Dự đoán:** đặt "đoán đảo" = (target 0,3 và một phía B) hoặc (target 0,7 và một phía A).
Nghĩa là M0 chỉ thấy lợi của phía đáng ra không thắng, nên chọn ngược với action thiết kế.
**PASS** khi tập "đoán đảo" chứa cả M01 và M03, và chứa **tối đa 2** trong 36 ô còn lại.
FAIL nếu thiếu M01 hoặc M03, hoặc có từ 3 ô sai trở lên.

## P(c) — sai số tại biên quyết định giải thích G_M|S1 tốt hơn bias trung bình

Với stakes = E|Δ| (E_pos + E_neg), ε = 0,1·stakes, trên phân phối D = D_A × D_B:

- **Lens biên:** L_b = Σ p·e_M² / (2ε), tổng trên các cặp state có 0 < |Δ| ≤ ε và e_M·Δ < 0
  (sai số hướng qua biên). Đây là xấp xỉ bậc hai f(0)·E[e²]/2 cho G_M|S1.
- **Lens trung bình:** `band_regret` của reviewer (Gauss khớp E|Δ|, bias hằng = bias trung bình của ô).

**Dự đoán:** trên 32 ô main cùng dấu, Spearman(G_M|S1/stakes, L_b/stakes) ≥ 0,6 **và** lớn hơn
Spearman(G_M|S1/stakes, lens trung bình/stakes) ít nhất 0,2. **PASS** khi cả hai đúng.
ε = 0,05 và 0,2·stakes chỉ báo độ nhạy, không đổi verdict.

## Cổng validity trước khi chấm

G_M|S1 tính lại từ chính các bảng `Side` phải khớp giá trị A04 (`G_M_S1`) trong
2·e_G_M_S1 + 10⁻¹²·C_ref ở mọi ô. Lệch thì dừng: không chấm, giữ output.

## Đọc kết quả cho câu hỏi "v1.3 có đáng xoay quanh chế độ sai số không"

| P(b) | P(c) | Hàm ý cho bước 2 (tác giả quyết) |
|---|---|---|
| PASS | PASS | Lý thuyết chế độ và "fidelity tại biên" đáng được prereg trong v1.3 |
| PASS | FAIL | Chế độ hữu ích để phân tầng; không đặt estimand quanh sai số tại biên |
| FAIL | PASS | Câu chuyện "fidelity tại biên" mà không cần phân loại fluid |
| FAIL | FAIL | Fallback của review: population characterization (câu chuyện 2) hoặc NARROW |

P(a) FAIL nghĩa là phải xem lại engine/certificate trước, không diễn giải tiếp.
Với chỉ 2 ô đảo dấu trong main, P(b) có lực phân biệt rất thấp; PASS chỉ là "không mâu thuẫn".
Không dùng 10 ô R đã mở, không chạm R09/R10, không đổi ngưỡng sau khi chạy.
