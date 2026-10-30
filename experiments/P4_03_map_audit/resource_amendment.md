# L4.3 — Resource amendment sau SIGXCPU, trước attempt mới

Người phụ trách: **Doan Van Tai**. AI sửa giới hạn tài nguyên do mình đặt; không
phải tác giả đổi tiêu chí khoa học hoặc xác nhận audit PASS.

Prereg `ae174d0` và mọi output gốc giữ nguyên. Attempt gốc:13/14replays PASS,
**117 trường thực sự đã kiểm**, không phải126 (126 là số slot so sánh dự kiến).
XPR0D không có numeric output: process exit−24=SIGXCPU tại cap900CPU-s. Log gốc
của ca này ghi1146.535s wall; cap ban đầu đã không đủ. Không gọi đó là bit mismatch
hoặc một negative result về hypothesis.

Amendment chỉ áp cho **retry duy nhất XPR0D**, sau khi đã kiểm failure là−24:
CPU1800s/hard1805s, wall2400s. Giữ AS3GiB, thread1, clean tag, tham số, K40/ref2,
chín trường và bit criterion. Worker mới khác worker frozen đúng một dòng setrlimit;
hash và phép so source kiểm điều này trước call. Không chỉnh native engine/R1/tolerance.

Output mới ở `results/lessons/l4_3/resource_v2/`; failure gốc không chuyển/xóa/ghi đè.
PartA tổng hợp mới gồm13receipt gốc và1retry; kiểm lại actual/expected bit của cả14,
không chỉ tin cờmatches. Nếu retry vẫn không đạt, giữ HOLD và không chạy native.

Nếu PartA được giải quyết, wrapper dùng nguyên native controller/worker frozen,
chỉ đổi root output và routing child entrypoint sang root mới. Native vẫn cùng666
tọa độ,4benchmark,3levels,nguồn frozen,CFguard,0.25pp và mọi stop rule ban đầu.
`budget.py` dùng cùng công thức tài nguyên đã khai; không thêm card hoặc CF.
Đây là resolution của resource HOLD, không xóa lịch sử initial HOLD hoặc nới scientific tolerance.
