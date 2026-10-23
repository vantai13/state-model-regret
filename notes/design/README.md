# Thiết kế lưới — trạng thái

| File | Trạng thái | Ghi chú |
|---|---|---|
| [grid_v1.md](grid_v1.md), [grid_v1.json](grid_v1.json) | **LOCKED tại tag `contract-v1`, có lỗi thiết kế đã biết** ([DL-026](../02_decision_log.md)) | M01–M12, S01 và cả ba ô calibration bị Stay áp đảo theo từng path; mọi contrast bằng 0 theo cấu trúc. **Không dùng cho A01/A04.** File giữ nguyên byte vì report CDE đã ghi SHA-256 của nó làm input |
| [design_conditions_v1_1.md](design_conditions_v1_1.md) | Lựa chọn kỹ thuật đã ADOPTED tại mốc 2; chưa khóa contract | Điều kiện ĐK1–ĐK8 và bổ sung N1–N6; provenance bản nguồn B1 được giữ |
| [decisions_v1_1_m2.md](decisions_v1_1_m2.md) | Đã commit `27eeed4` trước tính tham số ứng viên | 11 lựa chọn; chưa chứng nhận human gates |
| `grid_v1_1.md/.json` | Chưa tạo; **HOLD** | Prototype vượt cap tại 8/10 bộ tham số; B2–B4 chưa hoàn thành |

Tích hợp B1 và chạy kiểm chứng: **Doan Van Tai**, **23/10/2026**. Ngày22/10 và attribution trong bản dự thảo nguồn được giữ nguyên; không phải ngày chạy/commit mới. [Report](../../results/lessons/l1_8_v1_1_b1/report.md) phân biệt kết quả đã chạy với lựa chọn §11 chưa được chốt. Chưa triển khai/chạy `p_switch`, chưa sinh lưới ứng viên hoặc reserve v1.1, chưa tag v1.1. Số liệu s_bt của v1 không xác nhận lưới có information value.

Cập nhật mốc 2, **Doan Van Tai**, 23/10/2026: [báo cáo kiểm chứng và bản đồ khả thi](../verification/v1_1_m2/README.md). Full suite **165/165 PASS**; 2/10 bộ tham số đạt chứng nhận stationary/quantile/posterior của prototype, 8/10 cần cap lớn hơn 50.000 đã khai báo. Đây là giới hạn của phương pháp chứng nhận hiện tại, không phải bằng chứng các plant này không có stationary law. Không xóa bộ bị HOLD hoặc đổi threshold để dựng lưới đẹp hơn. [Closeout active](../phases/PHASE_1_closeout.md) là **HOLD**; heads-up giữ nội bộ, chưa gửi.
