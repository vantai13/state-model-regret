# Phase 4 (hợp nhất discovery) — Forking log L4.1

Người phụ trách: **Doan Van Tai** · 30/10/2026.
Provenance: AI theo ủy quyền; tác giả chưa kiểm các phân tích.
Nguồn máy đọc: [forking_paths.jsonl](../../results/lessons/l4_1/forking_paths.jsonl).
`logged_utc` là lúc ghi log, không giả là thời điểm phiên dạy đã tính số.

| # | Đã nhìn / đã thử | Nguồn | Quyết định và giới hạn |
|---|---|---|---|
| 0 | Trước triển khai đã nhận số lớp, A/AB, q90, ngưỡng near-substitution .1/.05pp; bảng δ, MV+A11C/7B; monotonic age và ratio amplitude; số native E11/E12 được input báo | Ba input L4.1; REGIME_MAP574a36f | Ghi exposure có sẵn, không tự nhận tái lập native hoặc biết tọa độ K6 |
| 1 | Recount sáu raw;54duplicate; sáu lớp; identity; A/AB; MV+A cũ; bảngδ theo lát trong input;54nhóm age,54cặp amp; inventoryv3 | Recount và manifest tại results/P4_01_recount/20261030_01 | Lưu tất cả kết quả; không có hộp mới/card; không có tọa độ mới, native audit hoặc CF outcome |

Đây là forking log **#0 khởi đầu Phase4**, không nối lại số thứ tự log Phase3R.
Các ngưỡng/bảng trong input đã được xem; chúng không phải prediction mới. Các
candidate vùng A/GS|M1 nhỏ trong AB chưa qua lọc prior, baseline hoặc native audit.
Recount không độc lập với AI theo nghĩa tác giả tự viết: code và fixture đều AI soạn.

Inventoryv3 frozen giữ nguyên, kể cả namespace amp khác plant và tám probe chưa
lưu outcome. Không biết K6 có cùng tám probe ấy, không nâng trạng thái chỉ do đều có8.
Log này và [exposure register](../00_exposure_register.md) phải commit trước native
audit L4.3 Part B hoặc mọi tính hộp mới L4.5; L4.1 không thực hiện các bước đó.
