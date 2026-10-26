# T03 — ví dụ tính tay cho hai identity (tài liệu hỗ trợ tự dẫn)

Người phụ trách: **Doan Van Tai** · 26/10/2026. Ví dụ do AI dựng và kiểm bằng phân số chính
xác ([script](../../experiments/lessons/t03_worked_example.py), [JSON](../../results/lessons/l2_9/t03_example/example.json));
**không phải** phép dẫn kín sách của tác giả (điều kiện L3 của Gate L vẫn mở). Dùng để tự
tính lại bằng tay rồi tự viết phép dẫn tổng quát.

## Bài toán (một bước, một queue, không hòa ở argmin nào)

- Stay: cost cố định **1** (tải nằm ở A).
- Switch: đẩy thêm u=1 gói sang B, capacity c=4, cost = **max(0, qB + w + 1 − 4)**.
- State ẩn qB: **0** (xác suất 1/3) hoặc **1** (2/3) — posterior sau snapshot y (G1).
- Tương lai w: **0** (1/3) hoặc **4** (2/3); trung bình w̄ = 8/3. Không ai biết w trước (G2).
- M1 = kỳ vọng đúng theo w (G3); M0 = rollout với w̄ cho từng qB rồi chọn argmin (G5).

## Bảng cost

| | J đúng (M1) | Ĵ mean rollout (M0) |
|---|---|---|
| Stay, qB=0 | 1 | 1 |
| Stay, qB=1 | 1 | 1 |
| Switch, qB=0 | ⅓·0 + ⅔·1 = **2/3** | max(0, 0+8/3−3) = **0** |
| Switch, qB=1 | ⅓·0 + ⅔·2 = **4/3** | max(0, 1+8/3−3) = **2/3** |

M0 đánh giá thấp Switch vì max(0,·) lồi (Jensen ở biên rỗng, EV-33).

## Bốn ô

| Ô | Action | L |
|---|---|---|
| S1M1 (L11) | qB=0→Switch, qB=1→Stay | ⅓·⅔ + ⅔·1 = **8/9** |
| S1M0 (L10) | M0 chọn Switch ở cả hai | ⅓·⅔ + ⅔·4/3 = **10/9** |
| S0M1 (L01) | E J(Stay)=1 < E J(Switch)=10/9 → Stay | **1** |
| S0M0 (L00) | E Ĵ(Switch)=⅔·⅔=4/9 < 1 → Switch | **10/9** |

## Hai identity hiện ra thế nào

1. **G_{S|M1} = L01 − L11 = 1 − 8/9 = 1/9.** EVPPI(x|y) = min_a E[J(a;x)] − E[min_a J(a;x)]
   = min(1, 10/9) − 8/9 = **1/9**. Hai biểu thức trùng vì L01 chính là "chọn một action tốt
   nhất theo trung bình trên belief" và L11 là "chọn đúng theo từng state" (G1, G3, G4).
2. **G_{M|S1} = L10 − L11 = 10/9 − 8/9 = 2/9.** VSS(x) = EEV(x) − RP(x): qB=0 → 2/3 − 2/3 = 0;
   qB=1 → 4/3 − 1 = 1/3; E[VSS] = ⅔·⅓ = **2/9**. Trùng vì ở S1, M0 chính là bài toán
   expected-value (thay w bằng w̄) và M1 là recourse problem (G2–G5).
3. Thêm: G_S = L00 − L10 = 0, G_M = L00 − L01 = 1/9, **Γ = 1/9**. Sửa state một mình vô ích
   khi vẫn dùng M0; cả hai cùng sửa mới lấy hết L00 − L11 = 2/9 = G_S + G_M + Γ.

## Bài tự làm (kín sách)

1. Viết lại hai dòng tổng quát: L01 = min_a E_D J(a;x), L11 = E_D min_a J(a;x) ⇒ G_{S|M1} = EVPPI;
   L10 = E_D EEV(x), L11 = E_D RP(x) ⇒ G_{M|S1} = E_D[VSS(x)]. Ghi giả định nào dùng ở mỗi bước.
2. Đổi P(qB=0) thành 2/3 rồi tính lại bốn ô bằng tay.

<details><summary>Đáp án bài 2 (mở sau khi tự tính)</summary>

L11 = 7/9, L01 = L00 = L10 = 8/9; EVPPI = E[VSS] = 1/9; G_S = G_M = 0; Γ = 1/9.

</details>

Khi đã tự viết phép dẫn, nhắn lại để ghi dòng L3 (author-attested) vào
[author_reading_record](../literature/author_reading_record.md).
