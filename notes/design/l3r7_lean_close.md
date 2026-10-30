# L3R.7 — đóng gọn bằng card v2 (DL-095)

Người phụ trách: **Doan Van Tai** · 30/10/2026. AI (Claude) soạn và chạy theo ủy quyền
("bạn hãy làm theo hương dẫn và đống lesson này giúp tôi đi", "tôi chỉ muốn đóng lesson 7 này thôi, làm sao cho phù hợp đi";
[nguyên văn](../../results/lessons/l3r_7/lean_close/author_choices.json)). Hướng dẫn gốc do một
phiên AI khác viết; tác giả dán vào và yêu cầu làm theo. Không phải human review.
Máy chạy: [prereg](../../experiments/R3R_14_lean_close/prereg.json).

## Vì sao đổi

L3R.7 dừng ở HOLD (DL-094). Chỗ kẹt không phải khoa học mà là chi phí tính toán:

- Card v1 làm tròn λA, λB, u tới **1/1000**. Một tốc độ như 7,123 làm lưới trạng thái lên bậc
  khoảng 12.000.
- Trên native05, ca có tốc độ trên lưới thô mất **0,2–1 s** mỗi mức; ca tốc độ 1/1000 mất **230–780 s**.
- Với luật n đã duyệt (DL-077: n ∈ {60, 40, 30}, 48 CPU-giờ), mức đó chỉ đủ khoảng n ≈ 20 < 30, nên dù
  numerics đóng được, L3R.7 vẫn HOLD_BUDGET.
- Thiết kế đã lường trước: "Nếu đổi measure/rounding để giảm chi phí, cần card v2 + DL, không sửa ngầm
  card v1" ([confirmation_v1_3 §9](confirmation_v1_3.md)).

Luật chọn mức của native05 đòi mọi đồng nhất thức nằm trong **cận số học khoảng**. Đây là phần "quá tay":
- Ví dụ CAL_CORNER_001 rớt vì G_SM = −0,00094, tức lệch 0,019 pp C̄, trong khi contract chấp nhận
  sai số làm mịn tới 0,25 pp.
- Tính lại trên native05 chỉ bằng R1 của contract: mức (160, 2) có 107/114 ca đạt (7 ca rớt vì C̄ đổi
  0,26–0,29% theo dt); mức (160, 4) có 49/49 ca đã tính đạt. Không ca nào vi phạm đồng nhất thức quá 0,25 pp.

## Đổi gì, giữ gì

| Giữ nguyên | Đổi |
|---|---|
| Claim, vùng Ω⁺/Ω⁻/BND, measure (đều/log-đều), ngưỡng ±1%, α = 1/40 mỗi card, π₀ = ½, R4, R5, bảng verdict | Card v2: bước làm tròn λA, λB, u = **r** (chọn theo luật dưới); κ vẫn 1/1000, h vẫn 1/120 s |
| Contract v1.3, R1–R8, TOL_NUM = 1/400 | Kiểm nhất quán: đồng nhất thức so với **TOL_NUM × C̄** thay cho cận số học; cờ chặt vẫn được ghi |
| Luật n DL-077, B = 48 CPU-giờ; thiết kế kiểm cố định và dry-run DL-093 | Các ca tốc độ lẻ trong calibration được làm tròn về r; thêm 4 điểm "nội vùng" bậc lưới lớn nhất |
| Code tính toán native05 (122 file, kiểm hash trước mỗi bước) | Bộ chạy mỏng `experiments/R3R_14_lean_close/` ghi JSON an toàn, ghi một lần, có checkpoint |

Card v1 giữ nguyên byte và vẫn là prereg hợp lệ của lần đóng băng 29/10.

Card v2 chép claim/vùng/ngưỡng từ v1. Lựa chọn duy nhất mới là r, và r được chọn trên dữ liệu
calibration theo luật khai trước, không theo regime map hay outcome CF.

## Luật đã khai trước (trước mọi phép tính của bước này)

1. **Đối chiếu môi trường.** Chạy lại 4 ca native05 trên máy local (Python 3.14 so với 3.13 trên GCP).
   Đạt nếu C̄ và sáu contrast lệch ≤ 10⁻⁹·C̄.
2. **Chọn r** trong {1/10, 1/20, 1/40, 1/100}, thô nhất trước.
   - Với 8 ca tốc độ lẻ của native05, so G/C̄ ở mức (160, 2) giữa bản 1/1000 và bản làm tròn về r.
   - Đạt khi: mọi ca, mọi contrast lệch ≤ 1/400, và không đổi MEETS/DOES_NOT_MEET của G_M (ngưỡng +1%)
     hay G_S (ngưỡng −1%), trừ khi giá trị gốc nằm trong 1/400 quanh ngưỡng.
   - Không r nào đạt thì HOLD, không dùng card v2.
3. **Chọn mức số** (contract R8):
   - Ứng viên theo thứ tự native05: (80,2) → (160,2) → (160,4) → (320,4) → (640,4) → (640,8).
   - Mỗi mức chính so với hai láng giềng (K/2, ref) và (K, ref/2) bằng `rules.compare_levels` nguyên bản.
   - Cả ba hàng phải có sai số số học chuẩn hóa ≤ 1/4000 và qua kiểm nhất quán theo dung sai.
   - Chọn mức đầu tiên mà **mọi** ca calibration đạt. Không mức nào đạt thì HOLD.
   - Tập calibration v2 gồm 106 ca thô của native05 (giữ nguyên), 8 ca tốc độ lẻ đã làm tròn về r, và
     4 điểm nội vùng bậc lớn nhất (λ = cận dưới + r).
4. **Thời gian và n.**
   - Mỗi bundle (mức chính + hai láng giềng) chạy với cache lạnh. Lấy p95 (method higher) theo lớp;
     p95 kế hoạch = max các lớp.
   - Chi phí cố định theo DL-093.
   - n áp đúng `power.select_allocation` (DL-077).
5. **Sau đó**, theo thứ tự, mỗi bước một commit:
   - card v2 khóa (lock mới);
   - receipt numerics v1.3.1-lean;
   - n;
   - root lấy từ nguồn ngẫu nhiên của hệ điều hành, commit cùng prereg **trước** lần rút duy nhất;
   - danh sách CF (chỉ tham số), inventory có thêm 10 regime-map đã quy về age 1;
   - dry-run B trên 4 góc discovery của DL-093 (kiểm đường ống, không phải evidence).

**Cấm:** chạy engine trên bất kỳ regime CF nào; R09/R10; đổi claim/ngưỡng/vùng/α/π₀/R4/R5/verdict; đổi r,
mức, n hay root sau khi rút.

## Sau L3R.7 (không làm ở đây)

L3R.8 vẫn còn:
- audit D22;
- người đọc thật (P0-V10/L8);
- quyết định realism (HOLD_UNSOURCED);
- Gate 3R.

Phase 4 HOLD giữ nguyên.

Hướng dẫn gốc cũng đề nghị chuyển trọng tâm sang cơ chế và validation độc lập. Đó là các lesson sau,
do tác giả quyết.
