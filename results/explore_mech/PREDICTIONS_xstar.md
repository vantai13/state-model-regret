# Dự đoán trước khi chạy xstar

Doan Van Tai — AI (Claude) soạn theo ủy quyền, **exploration**, không phải author-self, không phải claim.
Ghi 01/11/2026 trước khi có dòng xstar nào, sau khi đã chấm xslice/hslice/pslice
([checks.json](checks.json)).

## Công thức (heuristic xả backlog)

Mean model, trên posterior gần stationary (κ ≪ τ), coi chi phí là xả backlog q với headroom g: q²/(2g),
và E[q²] ∝ g⁻². Nó chọn Switch khi gA³(gA + u) < gB³(gB − u), với gA = μ − λA − u, gB = μ − λB,
λA,B = (S ∓ x·u)/2, S = λA + λB. Nghiệm x* (mã: `check.xstar_pred`):

| S \ u | 0,5 | 1 | 1,5 | 2 | 2,5 |
|---|---|---|---|---|---|
| 12,5 | 0,499 | 0,494 | 0,484 | 0,463 | 0,423 |
| 13,5 | 0,498 | 0,492 | 0,476 | 0,442 | 0,363 |
| 14,5 | 0,497 | 0,487 | 0,461 | 0,392 | 0,184 |

Công thức này đã được so **sau khi xem** xslice (S = 13,5: dự 0,492/0,442, thấy 0,495/0,415), nên xslice
không tính là kiểm. Mọi (S, u) khác S = 13,5, u ∈ {1, 2}, cùng toàn bộ κ = 0,5, chưa từng chạy.

## Dự đoán

- **X1** (κ = 0,1, h/κ = 50): mỗi chuỗi (S, u) có điểm cắt 0,5 của `actions.old.mean_switch` theo x thì
  |x*_quan sát − x*_công thức| ≤ 0,08; chuỗi không có điểm cắt trong dải x đã lấy thì mọi điểm phải nằm
  đúng phía của x*_công thức. Ở mỗi S, x*_quan sát không tăng theo u (cho lệch 1/16). Điểm đáng chú ý của
  công thức: S = 14,5, u = 2,5 phải cho x* rất nhỏ (≈ 0,18), vì B gần hết headroom sau Switch.
- **X2** (κ = 0,5, h/κ = 50): khám phá, không ngưỡng. Khi κ không còn ≪ τ, state cũ còn mang thông tin mode,
  nên công thức có thể lệch; báo độ lệch.
- **X3** (κ = 0,1): Γ < 0 chỉ khi 0 < x < x*_quan sát (cho lệch một bước lưới), như P3.

Kết quả sai được báo nguyên văn; không đổi công thức hoặc ngưỡng sau khi xem.
