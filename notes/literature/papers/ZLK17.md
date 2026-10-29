# ZLK17 — High-resolution DC microbursts

Người phụ trách/người soạn: **Doan Van Tai** · 29/10/2026.
Được duyệt L3R.4; AI-T, tác giả tự đọc: chưa có xác nhận.

Zhang, Liu, Zeng, Krishnamurthy. IMC2017,78–85.
[DOI](https://doi.org/10.1145/3131365.3131375).
[Author PDF](https://homes.cs.washington.edu/~arvind/papers/uburst.pdf),8trang,
local `~/papers/state-model-regret/l3r_4/ZLK17.pdf`.
Targeted §4/PDF3–4,§5.1–5.4/PDF4–5,§6.4/PDF7; xem Table2/Fig4/PDF4.

Câu hỏi: burst time, shape, buffer có cùng định nghĩa với plant không?
Observation: server–ToR10Gb/s, uplink40/100Gb/s (§4.2); byte counters25µs
với missed intervals xấp xỉ1% (§4.1/Table1). Ba application classes trên30racks.
Hot là egress utilization>50% trong25µs; burst là chuỗi hot liên tục.
p90 burst<200µs ở cả3class, Web50µs (§5.1). Inter-burst distribution không
exponential theo phép kiểm của bài (§5.2). Table2 có hai chiều chuyển trạng thái
rất khác nhau. Shared buffer carving động; occupancy normalize theo maximum
quan sát, không absolute size (§6.4). Caption Fig10 ghi300µs còn text nói
peak trong50ms; không xóa sự khác biệt này hoặc chọn một để suy buffer budget.

Inference: p90 hot-duration không phải mean hidden-mode holding time; egress
không là offered-input rate. Không biến200µs thành boundT_mode cho pilot.
Chưa suy CV_rate bốn cửa sổ, per-queue B_t hoặc tuổi backlog tới controller.
Hình dạng và sharing buffer là rủi ro scope cần validation. Không infer mọi DC
có cùng thang microburst hay coi mô hình đã bị bác thực nghiệm trên mọi bối cảnh.
