# EV-D4b — telemetry-age dose response on a 4 h continuous real trace (low load): results (15/11/2026)

Doan Van Tai — **AI (Claude) theo ủy quyền** (`LOCKED_AI_DELEGATED`).
- Thẻ khóa ở `e8700550` trước seed test.
- Chạy một lần, chỉ trên VM GCP: 240/240 job trong 44 phút. Bản băm dữ liệu thô ghi trước khi chấm.
- Dữ liệu thô `29e65ffd`, điểm `380ffb6c`.
- Chấm lại local trùng từng byte với điểm trên VM. Script stdlib độc lập cho cùng các số.

## Kết quả theo thẻ

| ID | Kết quả | Verdict |
|---|---|---|
| D1 plug-in không bị hại ở 30 T | 240/240 | **PASS** |
| D6 T12 đã sửa: hại plug-in không tăng theo h | 237/240 | **PASS** |
| D4 hybrid không bị hại | 239/240 | **PASS** (một phần là hiển nhiên, xem Đọc 2) |
| D2 dấu harm của twin nowcast theo luật | 110/158 = 69,6% < 85% | **FAIL** |
| D3 độ lớn | 139/240 = 57,9% < 80% | **FAIL** |
| D5 dose response theo τ | Spearman 0,54 < 0,8 | **FAIL** |

Trung vị G (% E_stay) của twin nowcast ở h = 30T theo τ = 1/10/30/60/120/300 s:
- quan sát: −0,06 / +0,13 / +0,18 / −0,35 / −0,17 / −0,21;
- dự đoán: +0,07 / +0,19 / +0,15 / +0,14 / +0,08 / −0,43.

T_int (train) trung vị 111 s (63–177).

## Đọc

1. **T12 (bản đã sửa sau audit) đứng trên traffic thật liên tục.** Trên trace 4 giờ không lặp đoạn, với hai đường A/B đồng bộ thời gian thật:
   - telemetry tươi **giúp** twin plug-in, ví dụ trung vị +0,42% ở 10T và +0,16% ở 30T khi τ = 30 s; +2,6%/+1,2% khi τ = 300 s;
   - lợi ích giảm theo 1/h, đúng như một hiệu ứng bị chặn;
   - D6: không có số hạng tăng theo h.

   D1 FAIL ở trace 2 của wave 3 không tái hiện ở đây. Tuy vậy, không thể quy nó cho lỗi pha A–B (audit B3), vì tải và trace cũng khác.
2. **Hybrid PASS, nhưng một phần là hiển nhiên.** Ở 30T, trong 71/120 case hybrid ra cùng quyết định với dữ liệu cũ và mới, vì h·ŝ lấn át state, nên G = 0. Ở 10T chỉ 18/120. Câu đúng: **ở tải thấp, hybrid không bị hại**; không được nói là "hybrid sửa được harm".
3. **Luật dấu bậc một không đứng trên trace liên tục** (D2 FAIL, 70%). Phân tích post-hoc chỉ ra lỗi nằm ở tuổi trung gian (`posthoc.json`, `experiments/ext_validity/ev_d4b_posthoc.py`):

| τ | τ/T_int | Dấu ở 30T | Dấu phần tăng 10T → 30T so với dự đoán | Tỷ lệ tăng thực/dự đoán (trung vị) |
|---|---|---|---|---|
| 1–10 s | ≤ 0,1 | 36/40 | 39/40 | 0,64–0,98 |
| 30 s | 0,3 | 21/28 | 23/28 | 0,78 |
| **60–120 s** | **0,5–1,1** | **25/52** | **27/52** | **0,22 / −0,01** |
| 300 s | 2,7 | 28/38 | 28/38 | 0,84 |

   - Ở τ ≤ 0,3 T_int và τ ≈ 2,7 T_int, **hệ số dốc** của luật gần đúng. Lỗi dấu ở mức (level) đến từ số hạng transient B lớn: ở h = 10T, twin nowcast bị hại −1,3…−2,3% rồi đổi dấu ở 30T.
   - Ở **τ ≈ T_int**, chính hệ số dốc sai: phần tăng thực chỉ bằng 0,22 hoặc −0,01 lần dự đoán.
   - Thay F_train bằng F đo trên test **không** sửa được dấu (vẫn 110/158), nên lỗi không nằm ở việc ước lượng tỷ lệ chọn.
   - Một giả thuyết, **chưa kiểm**: ở τ ≈ T_int, nowcast tuyến tính (β₁ 0,6 → 0,23) xử lý sai thành phần biến động chậm của trace, khiến số hạng h·s·ΔF không còn là thành phần dẫn ở 30T.
4. **So với wave 3** (luật dấu PASS trên trace lặp 15 phút): khác biệt có thể do việc lặp trace, do tải (≤ 0,775 ở đây, tới 0,975 ở wave 3), hoặc do trace. Thiết kế này không tách được ba nguyên nhân đó.

## Hệ quả cho claim

- **Giữ được:** plug-in không bị hại theo h (T12 dạng O(1)), trên trace thật liên tục. Đây là kết quả dương cho một claim lý thuyết đã được sửa.
- **Phải thu hẹp:** "luật zero-fit dự đoán dấu harm của twin nowcast". Câu này chỉ đứng khi τ ≪ T_int hoặc τ ≫ T_int, tức chỉ trên các trace lặp ở wave 3. Trên trace liên tục ở tải thấp, sign agreement là 70%, và ở τ ≈ T_int gần như tung đồng xu.
- **Hybrid:** "không bị hại ở tải thấp", phần lớn vì nó trở thành policy tĩnh.

## Giới hạn

- Một trace, một khung giờ, tải ≤ 0,775.
- Các hàng tương quan mạnh: cùng seed cho hai giá trị h và hai twin.
- Phân tích theo τ và theo h là post-hoc. AI tự thiết kế và chấm.

## Việc tiếp (đề xuất, chờ tác giả)

1. Thẻ kiểm giả thuyết ở Đọc 3, khóa trước: chỉ dùng τ ∈ [0,4; 1,2] T_int, và dự đoán rằng phần tăng của nowcast theo h nhỏ hơn 0,5 lần luật.
2. Tách nguyên nhân lặp trace với tải: chạy cùng regime tải thấp trên một đoạn 15 phút cho lặp. Chỉ cần chạy lại phần train/test của EV-D4b với chuỗi lặp; khoảng 45 phút trên VM.
