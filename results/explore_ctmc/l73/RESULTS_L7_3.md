# L7.3 Phần 2 — kết quả held-out hai thang (ctmc-v2)

Doan Van Tai — **test theo thẻ do AI soạn theo ủy quyền tác giả.** [CARD_L7_3.md](CARD_L7_3.md) do AI viết; tác giả nói
"khóa, chạy đi". Khóa ở commit `4514477e` ([locks_l73.json](../locks_l73.json)); **không có mentor review** trước khi khóa.
G-level vẫn G1.

## 1. Lượt chạy

- **Đúng một lượt**, 04/11/2026 04:01–04:35 UTC, trên GCP `dt4n-research-01` (quy tắc một máy).
- Ba stage asym, sobol, mid: **640/640 case COMPLETED**, 0 UNRESOLVED, 0 ERROR.
- Không dòng nào bị cờ S, M, G_M, F1 hay V1 âm. Truth tốn 3,9 CPU-h.
- **Kiểm chấm.** Điểm do `check_l73.py` (đã khóa) chấm trên GCP; chấm lại ở máy local cho `score_l73.json` trùng từng byte.
  Hash mọi file khóa vẫn khớp sau lượt chạy.

## 2. Verdict

| ID | Claim | Giá trị | Ngưỡng | n dòng | Verdict |
|---|---|---|---|---:|---|
| L73-1, T_s/T_f = 10 | đồng hồ T_int | (4; 7] 1,000 · (7; 15] 1,000 · (15; 40] 1,000 | 0,90 · 0,95 · 0,95 | 192 · 231 · 160 | PASS |
| L73-1, T_s/T_f = 100 | đồng hồ T_int | (4; 7] 0,993 · (7; 15] 1,000 · (15; 40] 1,000 | 0,90 · 0,95 · 0,95 | 146 · 166 · 123 | PASS |
| L73-2 | planner dừng ở h > 7·T_int | 0,967 | ≥ 0,90 | 727 | **PASS** |
| L73-3 | vùng state giữa hai thang (rủi ro) | 0,939 | ≥ 0,50 | 180 | **PASS** |
| L73-4 | harm chỉ với backlog (rủi ro) | 0,958 | ≥ 0,70 | 24 | **PASS** |

L73-1 cả 6 phần đều đạt, nên L73-1 **PASS**. Tổng cộng 4 PASS, 0 FAIL, 0 INCONCLUSIVE.

Các báo cáo phụ (không đổi verdict):
- L73-1 ở (1; 4]: 0,197 (T_s/T_f = 10) và 0,104 (100).
- L73-2: 0,964 (10) và 0,971 (100).
- L73-3 theo tổ hợp (f, T_f): 0,87–1,00.
- L73-4: 1,000 (10; n = 10) và 0,929 (100; n = 14).

## 3. Ý nghĩa theo thẻ (§7)

- **C-1 đứng như viết.** T_int của cả quá trình vẫn là đồng hồ onset với traffic hai thang, ở cả T_s/T_f = 10 và 100.
- **C-2 đứng.** "Planner dừng đủ dùng từ khoảng 7·T_int" chuyển sang traffic hai thang.
- **C-3 đứng.** Ở h = 10·T_f = T_s/10, M0 với state tươi thắng Static ít nhất 0,1 pp ở 94% regime.
- **C-4 đứng.** Harm chỉ với backlog vẫn xuất hiện; cỡ mẫu nhỏ (xem §4).

## 4. Lưu ý khi đọc (ghi sau khi mở, không đổi verdict)

1. **L73-4 dựa trên 24 dòng harm.** Có 428 dòng có h/T_int ≤ 1, nhưng chỉ 24 dòng có G_S < −0,5% (16 sobol, 8 asym).
   Phần T_s/T_f = 10 có đúng n = 10, bằng mức tối thiểu. PASS là đúng thẻ, nhưng bằng chứng mỏng. Ở một thang (L72-5) có
   91 dòng.
2. **L73-3 vượt xa kỳ vọng AI ghi trong thẻ** (0,2–0,4). Cách đọc hợp lý: ở MID, h/T_int chỉ 0,015–0,27, tức sâu trong
   vùng state theo mốc 0,3. Kết quả này **đúng như đồng hồ T_int dự báo**: thang chậm làm T_int lớn lên, nên vùng state
   kéo dài theo thời gian tuyệt đối. Test **không tách** được "state tươi lộ mode chậm" khỏi "đồng hồ T_int đúng", vì ở
   đây hai cách giải thích trùng nhau.
   - Kỳ vọng 0,2–0,4 dựa trên tỷ lệ "Static đủ" của bản đồ Stage E, vốn dùng một định nghĩa khác, nên nó sai.
   - Mô tả thêm: regret Static trừ regret M0 tươi có trung vị 0,72 pp (p10 0,14, p90 3,5); G_S > 0 ở 87% dòng MID.
3. **Trước onset, khai triển bậc một vô dụng.** Khoảng (1; 2] chỉ 0,03, (2; 4] chỉ 0,26 (asym ∪ sobol, mô tả sau khi mở),
   thấp hơn một thang (0,38–0,61 ở (2; 4]). Điều này ủng hộ quyết định gọi 4–7·T_int là "onset của z_pred1", tách khỏi mốc
   vùng.
4. **Phạm vi.** Hai bộ điều biến đối xứng, đỉnh a_f + a_s = 6, T_s/T_f ≤ 100, tải ≤ 9, N ≤ 3000. Thiếu asym ở tổ hợp nặng
   nhất (f = 1/2, T_f = 1, T_s = 100). Chưa có burst bất đối xứng (GZL22, BAAZ09).

## 5. Hệ quả cho paper và việc còn mở

- Theo Lesson 7.3, câu thực dụng "dùng T_int của backlog để định vị hệ thống" chỉ được viết **sau** khi thẻ hai thang đã
  chấm. Điều kiện này **đã thỏa** cho phạm vi ở §4.4.
- Câu nháp, để tác giả viết lại bằng lời mình:

  > "Trong ctmc-v1 và ctmc-v2 (hai thang, T_s/T_f ≤ 100), T_int của toàn quá trình xếp các vùng: h/T_int < 0,3 thì state
  > tươi có giá trị; từ khoảng 7·T_int thì planner dừng đủ dùng và công thức zero-fit đúng tới 0,1 pp."

- **Còn mở:**
  - tác giả tự đọc LPC04, BAAZ11, GZL22;
  - mentor review thẻ (sau khi mở thì chỉ còn mang tính hồi cứu);
  - held-out tiếp theo với burst bất đối xứng, đổi một trục mỗi lần;
  - realism WAN dưới 5 phút; h của NDT.
