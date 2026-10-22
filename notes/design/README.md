# Thiết kế lưới — trạng thái

| File | Trạng thái | Ghi chú |
|---|---|---|
| [grid_v1.md](grid_v1.md), [grid_v1.json](grid_v1.json) | **LOCKED tại tag `contract-v1`, có lỗi thiết kế đã biết** ([DL-026](../02_decision_log.md)) | M01–M12, S01 và cả ba ô calibration bị Stay áp đảo theo từng path; mọi contrast bằng 0 theo cấu trúc. **Không dùng cho A01/A04.** File giữ nguyên byte vì report CDE đã ghi SHA-256 của nó làm input |
| [design_conditions_v1_1.md](design_conditions_v1_1.md) | DRAFT — AI đề xuất, chờ tác giả xác nhận (DL-027) | Bước B1 của v1.1: điều kiện ĐK1–ĐK8, viết trước khi chọn số |
| `grid_v1_1.md/.json` | Chưa tạo | Bước B2–B4 |

Tích hợp B1 và chạy kiểm chứng: **Doan Van Tai**, **23/10/2026**. Ngày22/10 và attribution trong bản dự thảo nguồn được giữ nguyên; không phải ngày chạy/commit mới. [Report](../../results/lessons/l1_8_v1_1_b1/report.md) phân biệt kết quả đã chạy với lựa chọn §11 chưa được chốt. Chưa triển khai/chạy `p_switch`, chưa sinh lưới ứng viên hoặc reserve v1.1, chưa tag v1.1. Số liệu s_bt của v1 không xác nhận lưới có information value.
