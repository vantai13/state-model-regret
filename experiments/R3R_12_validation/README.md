# Selected-level validation — chưa thực thi

Người phụ trách: **Doan Van Tai**.

Đây là code chuẩn bị theo DL-093. Chưa có `prereg.json`, chưa chạy physical jobs
của module này. Parent native05 đang HOLD nên `prepare` từ chối tạo cấu hình.

Guard yêu cầu global audit đủ114cases,3legacyanchors,6marginals và selected levels.
Jobs dự kiến chỉ dùng coordinates đã có: zero/anchor checks, identical-model
timing trên bốn rational-rate calibration và dry-run discovery đã chọn bằng
metadata. Mọi job phải có source/levels/resources prereg commit trước execution.

Không sinh CF/seed, không tạo numerics tag hoặc bỏ qua human/Gate3R. Mức đọc,
Understanding và Phase4 không thay đổi. Tạm dừng theo yêu cầu tác giả ngày30/10.
