# Dự đoán trước khi chạy xslice / phần còn lại của hslice

Doan Van Tai — bản nháp cơ chế do AI (Claude) soạn theo ủy quyền, **exploration**, không phải author-self,
không phải claim. Ghi ngày 01/11/2026, sau khi nhìn 5.814/16.384 dòng sobol4 và trước khi có bất kỳ
dòng xslice nào. hslice: 16/256 dòng (shard 12/16, h/κ ≈ 58) đang chạy để kiểm phần đọc action, kết
quả chưa được xem khi file này được viết.

## Điều đã thấy (sobol4, h/κ > 20, S+M ≥ 0,5%)

Lớp tách theo x = (λB − λA)/u (= δ/u, δ là "δ" trong bảng L4.2, chỉ khác chia cho u):

| x | lớp |
|---|---|
| < 0 | G_S < 0 (state cũ tốt hơn state mới khi dùng M0), P_flip ≈ 0 |
| = 0 | không lớp nào (93/93) |
| 0 < x ≲ 0,4–0,5 | Γ < 0 (thay thế), P_flip cao |
| x ≳ 0,5 | G_S < 0 lại, P_flip ≈ 0 |

Theo δ tuyệt đối, ngưỡng dịch theo u (0,5 khi u ≤ 1; 0,75–1 khi u > 2); theo x, ngưỡng gần 0,4–0,5 ở mọi
dải u. L4.2 đã ghi "chưa có lời giải thích plant" cho bảng δ.

## Cơ chế đề xuất (chưa kiểm)

1. **Truth ở horizon dài.** Stay giữ stationary; Switch dời u từ A sang B. Khi h ≫ κ, chi phí thật có
   phần dài hạn h·c_stat với c_stat = f(λA) + f(λB+u) − f(λA+u) − f(λB), f = E_stationary[Q](λ) lồi tăng.
   Do f lồi, c_stat < 0 ⇔ λB < λA: **dấu action thật ở h/κ lớn = dấu δ, không phụ thuộc u và backlog**.
   δ = 0 ⇒ c_stat = 0, truth chỉ còn phần transient.
2. **Mean model không có phần dài hạn.** M0 lăn đường trung bình; tốc độ trung bình λ + managed < μ nên
   fluid xả về 0 và mọi chi phí M0 là transient (xả backlog hiện có). Xấp xỉ xả backlog q với headroom g:
   chi phí q²/(2g). Lấy trung bình theo posterior gần stationary (κ ≪ τ), M0 chọn Switch khi
   E[qA²]/(gA(gA+u)) > E[qB²]/(gB(gB−u)), gA = μ−λA−u, gB = μ−λB. Nếu E[q²] ∝ g^(−k), tuyến tính hóa cho
   ngưỡng **x* ≈ k/(k+2)**; k = 2 (heavy-traffic) cho x* = 1/2.
3. **Hệ quả.** 0 < x < x*: truth Stay nhưng M0 (state cũ) Switch → P_flip ≈ 1; state mới cho M0 thấy các
   trạng thái B đang nghẽn nên đôi khi Stay đúng → G_S > 0 và sửa model cũng đủ → Γ < 0. Ngoài dải này M0
   (state cũ) chọn đúng action dài hạn nhờ trung bình hóa; state mới làm M0 phản ứng theo backlog transient,
   vốn không quyết định ở h dài → **G_S < 0: thông tin mới khuếch đại một model cận thị**.

## Dự đoán sẽ kiểm (ngưỡng ghi trước)

- **P1** (hslice, xslice): ở h/κ ≥ 50 và |δ| ≥ 1/2, tỷ lệ Switch của truth trên state hiện tại
  (`actions.current.true_switch`) ≥ 0,9 khi δ < 0 và ≤ 0,1 khi δ > 0.
- **P2** (xslice): ở h/κ ∈ {50, 150}, tỷ lệ Switch của M0 trên state cũ (`actions.old.mean_switch`) ≥ 0,9
  khi 0 ≤ x ≤ 0,25 và ≤ 0,1 khi x ≥ 0,75; điểm cắt 0,5 nằm trong [0,3; 0,6] cho cả u = 1 và u = 2, và
  x*(u=2) ≤ x*(u=1) + 1/16.
- **P3** (xslice): Γ < 0 chỉ khi 0 < x < x* (cho phép lệch một bước lưới ở mép); ngoài dải, G_S < 0 khi
  |δ| ≥ 1/2.
- **P4** (hslice, xslice): δ = 0 cho G_S ≥ −0,1% và Γ ≥ −0,1·(S+M) ở mọi h/κ.
- **P5** (hslice): h/κ nhỏ nhất mà dấu của G_S đạt dấu ở h/κ = 160 tăng khi |δ| giảm (δ = ±1/4 muộn hơn
  δ = ±1/2, ±1).

Sai bất kỳ dự đoán nào sẽ được báo nguyên văn; không chỉnh ngưỡng sau khi xem. a/μ vẫn 0,6 (biên độ
khác là điều kiện chưa dùng, để sau).
