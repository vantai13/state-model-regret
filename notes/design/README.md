# Thiết kế lưới — trạng thái

| File | Trạng thái | Ghi chú |
|---|---|---|
| [grid_v1.md](grid_v1.md), [grid_v1.json](grid_v1.json) | **LOCKED tại tag `contract-v1`, có lỗi thiết kế đã biết** ([DL-026](../02_decision_log.md)) | M01–M12, S01 và cả ba ô calibration bị Stay áp đảo theo từng path; mọi contrast bằng 0 theo cấu trúc. **Không dùng cho A01/A04.** File giữ nguyên byte vì report CDE đã ghi SHA-256 của nó làm input |
| [design_conditions_v1_1.md](design_conditions_v1_1.md) | Lựa chọn kỹ thuật đã ADOPTED tại mốc 2; chưa khóa contract | Điều kiện ĐK1–ĐK8 và bổ sung N1–N6; provenance bản nguồn B1 được giữ |
| [decisions_v1_1_m2.md](decisions_v1_1_m2.md) | Đã commit `27eeed4` trước tính tham số ứng viên | 11 lựa chọn; chưa chứng nhận human gates |
| [grid_v1_1.md](grid_v1_1.md), [JSON](grid_v1_1.json) | **REJECTED / NARROW REQUIRED** | 28ô+6reserve; screen8/22→11/22, yêu cầu15; không calibration/freeze |
| [v1_2_protocol.md](v1_2_protocol.md) | Commit `d696eef` trước lần chạy chính thức | REFORMULATE (DL-038): neo λA theo ranh giới quyết định, horizon vật lý, held-out khai báo trước |
| [grid_v1_2.md](grid_v1_2.md), [JSON](grid_v1_2.json) | **ACCEPTED, LOCKED tại `contract-v1.2`** | 38 ô chính, 12 held-out, 6 kiểm âm, 2 đầu dò; calibration M01, M09, M22 (DL-039) |

Tích hợp B1 và chạy kiểm chứng: **Doan Van Tai**, **23/10/2026**. Ngày22/10 và attribution trong bản dự thảo nguồn được giữ nguyên; không phải ngày chạy/commit mới. [Report](../../results/lessons/l1_8_v1_1_b1/report.md) phân biệt kết quả đã chạy với lựa chọn §11 chưa được chốt. Chưa triển khai/chạy `p_switch`, chưa sinh lưới ứng viên hoặc reserve v1.1, chưa tag v1.1. Số liệu s_bt của v1 không xác nhận lưới có information value.

Cập nhật mốc 2, **Doan Van Tai**, 23/10/2026: [báo cáo kiểm chứng và bản đồ khả thi](../verification/v1_1_m2/README.md). Full suite **165/165 PASS**; 2/10 bộ tham số đạt chứng nhận stationary/quantile/posterior của prototype, 8/10 cần cap lớn hơn 50.000 đã khai báo. Đây là giới hạn của phương pháp chứng nhận hiện tại, không phải bằng chứng các plant này không có stationary law. Không xóa bộ bị HOLD hoặc đổi threshold để dựng lưới đẹp hơn. [Closeout active](../phases/PHASE_1_closeout.md) là **HOLD**; heads-up giữ nội bộ, chưa gửi.

## PhầnA — trạng thái mới nhất23/10/2026

Doan Van Tai. [Báo cáo](../verification/v1_1_part_a/README.md). Solver phổ đã chứng nhận20/20 trường hợp original và20/20 redesign; cap50.000 không còn chặn. D/ĐK1/budget của cả hai thiết kế được commit trước screen;88 sign-only rows có unresolved mass0. Một lượt redesign λ7/7.2/8.1 không đủ15/22: chỉ11in. Giữ mọi out/reserve, không thử lần hai. Draft definitions/boundary đã cập nhật phương pháp nhưng không được promote thành contract chính thức. Các đoạn2/10/HOLD_CAP phía trên là record mốc2 đã được kết quả này thay thế.
