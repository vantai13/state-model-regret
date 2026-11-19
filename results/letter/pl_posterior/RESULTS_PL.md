# PL — kết quả (Claude, 20/11/2026)

Người phụ trách **Doan Van Tai**. Exploration bổ sung cho letter v8.4. AI làm theo ủy quyền toàn quyền của tác giả (19/11/2026):
Claude thiết kế và viết thẻ; Codex viết code và test cho tới khi hết quota; Claude sửa lỗi lấy α, viết sửa đổi A1 (trước lock),
chạy pilot, predict, lock, truth, chấm, và chấm lại độc lập. Không có mentor review và không có dự đoán của tác giả.

## Mốc
- Thẻ, code, pilot, predictions, lock: commit `b2237a8ad` (lock sha edb0bf30…), trước truth.
- Truth chạy đúng một lần: 71/71 regime COMPLETED, 2,87 CPU-h tiến trình con, 19,3 phút wall, 9 tiến trình.
- Raw commit `307dc4cb5` trước khi chấm.
- Chấm bằng scorer đã khóa (`scores.json`), rồi chấm lại độc lập (`rescore_independent.py`, không import scorer): **MATCH**.

## Phạm vi (sửa đổi A1)
- 71/92 regime matched có chi phí Q1 dự phóng ≤ 3600 CPU-s.
- 21 regime nặng ghi NOT_RUN vì tính toán (danh sách trong `predictions.json`, `not_run_compute`). Phần lớn thuộc họ tải cao và mode chậm (κ = 2 s), với T_int lớn.

## Kiểm định (chấm cơ học)
| Kiểm định | Verdict | Số đếm |
|---|---|---|
| H-PL1: kernel thật tái lập W1b | PASS | 497/497 ô |
| H-PL2: harm của M0 còn với posterior học (L = 100 T_int, median 5 seed), τ = T_int, h = 30 T_int | PASS | 51/56 (cần ≥ 44,8) |
| H-PL3: hybrid (s thật) có both-side regret ≤ 0,5% ở mọi seed | PASS | 71/71 (kernel thật 71) |
| H-T4a: ŝ đổi dấu, slope ở 300 T_int lệch dự đoán ≤ 5% | PASS | 40/40 (cả 40 có G_S < −0,1% C_ref) |
| H-T4b: ŝ cùng dấu, \|G_S\| ≤ 1e−9 C_ref | PASS | 8/8 |

Các mẫu số là regime dùng chung mô hình, không phải phép thử độc lập.

## Mô tả thêm (post-hoc, không phải kiểm định)
- **Harm theo độ dài lịch sử L = 30/100/300/1000 T_int:** 50/51/52/53 trên 56.
- **5 regime mất harm ở L = 100 đều là Stay-optimal**; 36/36 Switch-optimal giữ harm.
- Ở τ = 3 T_int: 48/50.
- **Trung vị theo regime của G_S M0 ở 30 T_int:**
  - kernel thật −4,52%;
  - posterior học −4,52%;
  - plug-in +0,13%, khớp Remark 1.

## Dự báo của Claude
- F1 (n_true ≈ 72): không so được trực tiếp, vì dự báo cho 92 regime trong khi quần thể chạy là 71; đo được 56/71.
- F2 (Switch-optimal giữ harm ở mọi L): đứng ở L = 100 (36/36).
- F3 (L nhỏ làm mất harm nhiều hơn): đứng (6 → 3).
- **F4 (20–40 regime đủ điều kiện T4): sai**, thực tế 48 (40 đổi dấu, 8 cùng dấu).

## Đọc kết quả
- **Q1:** harm của M0 không đến từ việc stale được cho kernel thật. Một posterior học từ lịch sử Stay hữu hạn bằng k-NN cho cùng harm (trung vị gần như trùng). Điều này khớp cơ chế "gộp quyết định" (C5): mọi phép lấy trung bình gap fluid trên trạng thái cũ đều gộp quyết định về action dài hạn.
- **Correction** giữ regret thấp với posterior học, đúng như Remark 2 (với số hạng dừng hằng thì kernel không quan trọng).
- **Q2:** điều kiện cùng dấu là ranh giới đúng trên toàn bộ các regime đủ điều kiện:
  - ŝ(x) đổi dấu thì harm tuyến tính theo slope dự đoán (40/40);
  - ŝ(x) cùng dấu thì G_S = 0 (8/8).

## Giới hạn
- 21 regime nặng không tính.
- Posterior học dùng trạng thái đầy đủ (backlog và mode). Chưa kiểm khi mode bị ẩn.
- Lịch sử là mô phỏng chính xác của chuỗi Stay, không phải telemetry thật.
- Twin T4 là một dạng nowcast cụ thể, với w* chọn theo luật trong thẻ.

## Đưa vào paper (theo luật cố định trong thẻ)
- Sec. V-A: một câu về Q1, kèm mẫu số 71/92.
- Remark 2: thay ví dụ một regime bằng số đếm 40/40 và 8/8.
- Limitations: câu về posterior thật được sửa theo kết quả.
