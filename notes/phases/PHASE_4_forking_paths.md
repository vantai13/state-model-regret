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

## Addendum L4.2 (30/10/2026) — chỉ ghi thêm

Nguồn máy đọc tiếp theo: [L4.2 JSONL](../../results/lessons/l4_2/forking_paths.jsonl).
Số thứ tự 2–5 nối sau 0–1; `logged_utc` là lúc ghi, không giả là prereg trước phân tích.

| # | Đã nhìn / đã thử | Quyết định và giới hạn |
|---|---|---|
| 2 | Ba input L4.2 đã in 18 age pairs, near148, A28, MV18; toy; mechanism255/286/67; crossδ238 và alternative headroom | Ghi pre-existing exposure, không blind prediction |
| 3 | Tính lại từ CSV L4.1 có SHA: age pairs, near-boundary, MV, mechanism, crossλAλB, δ và δ/μ, headroom; đọc hai PNG/plot source tại tag | Toàn bộ pilot đã lộ; không hộp/card mới; δ không là cơ chế/luật lớp tất định |
| 4 | Exact toys, AI example T-B, recurrence fixture, counterexamples, S10, hai implementation mutants | Chỉ teaching/implementation; không new physical coordinates/engine audit/confirmation |
| 5 | Bài optional A-by-δ và bài T07P4 author | **NOT_RUN/OPEN**; không tạo thay lời dự đoán hoặc bài tự viết của tác giả |

Giữ nguyên cardv2/CF/inventory và phần log L4.1. Các mốc .15/.1/.5/1% là descriptive
thresholds đã có trong input, không native tolerance hoặc CF scoring mới. Cùng δ=.5
còn 40AB/1A/1B; plurality8/18 không majority. Không xóa fork hoặc chỉ giữ kết quả thuận lợi.
