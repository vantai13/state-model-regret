# Bổ sung trước pilot khả thi

Doan Van Tai. Pilot đầu `ditl_20230412_s120_c1` không có future replay vì
T_int censored (1015.8839085013924 s). Giữ nguyên mọi output. **Dự phóng trong
`pilot/summary.json` không hợp lệ**: code cũ lấy overhead không phải replay
để dự phóng, trong khi rows=0. Không dùng các con số đó để xin/chạy compute.

Train-only screen hậu kiểm 9 cấu hình DITL cũ, không future/cost test. Quy tắc
được ghi trước screen: uncensored và ít nhất 4/24 epoch còn đủ h=10*T_int;
chọn lớn nhất proxy T_int*sum(lam+u), id xử lý tie. 7/9 khả thi. Chọn
`ditl_20230412_s120_c2`, mu=(10.5,9.5), T_int=345.0912077899601 s, 11/24 h10
epochs. Không đổi full grid 27 cases, τ, h, seeds hay metric.

Chỉ sửa source mới của phiên này để chặn projection khi rows=0 và trỏ mặc
định tới `design_ready/plan.json`; không đổi train, replay, cost, policy hay
selection kernel. Source trước sửa được giữ ở `source_at_first_pilot/`, khớp
hash plan đầu. Plan mới ghi rõ exposure và selection post-hoc. Pilot khả thi
là **pilot bổ sung**, không thay hoặc cứu verdict nào; không có test hypothesis.

Lỗi thực thi screen đầu: chạy Python bằng file path chưa có PYTHONPATH root,
ModuleNotFoundError trước khi screen tạo output. Giữ log; lệnh sau chỉ thêm
PYTHONPATH, không sửa model hay thông số.
