# Budget-only continuation — draft, chưa adopted hoặc thực thi

Người phụ trách: **Doan Van Tai**.

Đây là công cụ dự phòng cho parent kết thúc sạch nhưng thiếu jobs vì budget.
Mức24CPUh trong builder là proposal; **chưa có prereg và chưa cấp thêm budget**.
Khi dùng phải cung cấp một DL resource decision mới và commit prereg trước run.

Không thay estimator, per-job caps, case list, global candidates hoặc thresholds.
Nếu mọi mức đã xong nhưng accuracy không đạt, thêm budget không được xem là cách
cứu kết quả. Nếu parent có failed computations, builder cũng từ chối.

Native05 hiện có hai lỗi JSON serialization, nên **không đủ điều kiện dùng công
cụ này**. Cần chẩn đoán/sửa bug và quyết định version/replay riêng sau khi tác giả
yêu cầu tiếp tục. Hiện công việc tạm dừng; không có run06/CF hoặc numerics tag.
