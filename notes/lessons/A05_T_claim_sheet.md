# A05-T — claim sheet trước khi mở held-out

Người phụ trách: **Doan Van Tai** · 28/10/2026 · DL-059.
AI (Claude) soạn theo ủy quyền trực tiếp của tác giả, commit **trước** khi chạy A05-T.
Đây không phải văn bản tác giả tự viết và không chứng minh tác giả đã hiểu L3.7.

## 1. Kỳ vọng của tác giả (để trống có chủ đích)

```
A05-T — kỳ vọng của tôi, viết lúc ……, TRƯỚC khi chạy
PC4 nội suy:    tôi đoán …… vì ……
PC4 ngoại suy:  tôi đoán …… vì ……   (nhánh này không được thiếu ô nào)
K5 (R03/R04):   ……        C1 (R05–R08): ……
Nếu kết quả ngược kỳ vọng, thứ đầu tiên tôi kiểm là: ……
```

**Chưa điền.** AI không viết thay dự đoán của tác giả. Bất kỳ kỳ vọng nào viết sau run
đều phải ghi giờ thật và không được trình bày là dự đoán trước dữ liệu.

## 2. Câu claim viết sẵn cho từng verdict

Các ô vuông được điền bằng số từ output. Không viết câu mới dưới áp lực.

**PC4, nhánh nội suy (verdict chính, cần ≥ 6/8 ô eligible):**

| Verdict | Câu được viết | Không được viết |
|---|---|---|
| SUPPORT | Trên [n]/8 ô nội suy eligible, H1 có MAE thấp hơn H0 ít nhất 0,25 điểm % C_ref theo luật đã khóa; d ∈ [lo, hi]; MAE0 = […], MAE1 = […] | "Động học queue giải thích Γ", "H1 chính xác" |
| WEAKEN | H1 gần sự thật hơn H0 nhưng lợi thế nằm dưới margin đã khóa; d ∈ [lo, hi] | "Gần như SUPPORT" |
| FALSIFY | Trên các ô này, H1 ở dạng đã khóa không dự báo tốt hơn H0; d ∈ [lo, hi] | "H0 đủ tốt" (chỉ được ghi dưới nhãn Inference, kèm MAE0 so với εE = 0,5%) |
| INCONCLUSIVE | Chưa kết luận được vì [thiếu ô / D trên tập eligible < m / khoảng d vắt qua ranh giới] | "Thiên về …" |

**PC4, nhánh ngoại suy R11/R12 (cần đủ 2/2):** dùng cùng bốn câu, scope chỉ hai ô có h = 12 s.
Báo riêng, không gộp với nhánh nội suy và không chọn nhánh thắng.

**K5 (R03/R04, κ = 2, luật khóa trước A04):**
- STANDS: "Luật K5 đứng ở R03/R04", kèm nhãn headroom và base rate heuristic ≈ 0,90.
- DOES_NOT_STAND: "Luật K5 bị bác ở [ô]". Danh sách M19–M22 đã đứng ở A04 không bị ảnh hưởng.
- UNRESOLVED: "Chưa phân giải ở [ô] vì [gate]".
- Không được mở rộng sang κ khác, hay η = 0,75 ở κ = 2.

**C1 (R05–R08, khóa sau A04, post-discovery):** cùng ba trạng thái. STANDS phải kèm base rate
heuristic ≈ 0,81 và được ghi là bằng chứng yếu.

## 3. Chẩn đoán khai trước (DIAGNOSTIC_NOT_VERDICT)

Tính cho **mọi** ô đã mở, bất kể verdict; không đổi verdict:
1. Bất biến tầng 1 (bug).
2. Regime: a00/a01 danh nghĩa và G_M bằng 0 về cấu trúc; R00/C_ref; p_sw của engine so với p_2 công khai.
3. Vị trí của khoảng truth so với hai dự báo, và phần đóng góp vào d (bão hòa ở ±|p0 − p1|).
4. Phân rã level/shape theo contrast: chênh lệch trung bình, sai số có dấu, MAE tại trung điểm, MAE sau khi bỏ trung bình.

## 4. Giới hạn đã biết trước

- |d| ≤ D. SUPPORT ở nhánh nội suy đòi d đạt ít nhất khoảng 42% mức tối đa; ở nhánh ngoại suy, khoảng 53%.
- Trên dự báo đã khóa, chênh lệch H1–H0 chủ yếu nằm ở mức (τ), không ở hình dạng.
- Trục h = 4 s chỉ có ở R09/R10, nên **không được kiểm** ở A05-T.
- A05-T không là network evidence, không là cơ chế, không nâng G-level.
