# Thẻ đề xuất S3

Người phụ trách Doan Van Tai. DRAFT, EXPLORATORY-SELECTED, CHƯA KHÓA, CHƯA CHẠY. Cổng S2 tổng chưa chốt vì điều kiện thiệt hại chưa định lượng. Đây là đề xuất từ S2, chưa có xác nhận của tác giả.

Ứng viên chính là fresh, rate ŝ cùng estimator từ bản ghi 300T_int, h=T_int, c=0 và vùng D_ŝ≥0,28. D_ŝ là trung bình đều trên τ/T_int∈{0.3,1,3} của D_fresh,ŝ+D_stale,ŝ,τ, giữ đúng định nghĩa đã dùng trong H-C. Ngưỡng 0,28 chọn bằng F1 nhãn Δ≥0,1 trên 499 ID lẻ, điều kiện phủ ít nhất 10% training, tie lấy d* nhỏ hơn. Không dùng outcome của 501 ID chẵn để chọn d*. Chọn h=T cho ứng viên chính sau khám phá, hai h lân cận chỉ để tác giả so sánh.

| h/T_int | d* từ ID lẻ | Vùng trên ID chẵn | Tĩnh / hybrid (% C_ref) | Δ (điểm) và CI95% |
|---:|---:|---:|---|---|
| 0.7 | 0.32 | 109/501 | 2.419835 / 0.300760 | 2.119076 [1.289503, 2.948649] |
| 1 | 0.28 | 99/501 | 2.427720 / 0.317065 | 2.110655 [1.284329, 2.936981] |
| 1.5 | 0.21 | 93/501 | 2.389831 / 0.421539 | 1.968292 [1.195251, 2.741333] |

Với ứng viên chính, 78/99 regime trong vùng đánh giá đạt Δ≥0,1, không regime nào trong vùng có Δ≤−0,05. Lợi ích tuyệt đối trung bình 5.588285 packet·s, CI95% [1.910664, 9.265906]. Toàn bộ lưới đã thấy, nên các số này chỉ là bằng chứng chọn thẻ.

S3 dự kiến giữ mô hình/miền đã sàng tài nguyên, dùng Sobol seed mới và record seed mới. N, seed, quy tắc loại trước outcomes, cách tính CI và ngân sách cần ghi vào thẻ khóa của S3. Chỉ chọn một ứng viên làm primary trước khi chạy, hoặc định trước cách xử lý nhiều phép thử nếu giữ cả ba. Không thay h/d* theo outcomes S3.

Metric là Δ=regret(tĩnh ŝ)−regret(hybrid ŝ), cùng C_ref và phía fresh. Đề xuất kiểm vùng phủ ≥10% tất cả regime hợp lệ và mean Δ≥0,1 điểm, đồng thời CI của mean Δ có cận dưới >0. Quy ước này tương đương CI của hybrid−tĩnh có cận trên <0.

Điều kiện ngoài vùng của PLAN là hybrid không tệ hơn 0,05 điểm. Cần quyết định rõ điều kiện này áp cho mean hay từng regime và cách dùng CI trước khi chạy S3. Có thể đề xuất noninferiority cho mean ngoài vùng với cận dưới CI của Δ≥−0,05, nhưng S2 chưa thông qua quy tắc đó. Luôn báo riêng các regime Δ≤−0,05 và Δ≤−0,1, mọi estimator INVALID/fallback và tỷ lệ loại theo tài nguyên.

|ŝ|/|s| chưa dùng làm điều kiện chọn vì cần s thật. Không fit lại estimator, d* hay ngưỡng gây hại sau S3. S3 mới phải có luật báo kết quả vào paper bất kể outcome và chấm lại độc lập. Không chạy S3 trong nhiệm vụ hiện tại.
