# Numerics v1.3.1 — bổ sung coverage từ L3R.7

Người phụ trách: **Doan Van Tai** · 29/10/2026 · trạng thái **REQUIRED_NOT_EXECUTED**.
Đây là addendum, không sửa kế hoạch đã khóa trong contract-v1.3, không tạo tag mới.

1. Giữ coverage κ=3,h=16 của cả vùng control, các cực trị load và tám audit IDs.
   Góc κ/h không thay thế coverage theo độ phân giải của rate.
2. Measure card v1 làm tròn λA/λB/u tới1/1000. Tính lattice bằng hữu tỉ cho
   λA=7.123,u=1.234 dẫn tới steps(-7643,+4357),degree12000 tại cảref1/ref2;
   maxpilot A-predegree24. Đây là arithmetic, **chưa** đo runtime/RAM hoặc effect.
3. Trước computation phải preregister calibration design cố định, không rút
   sample thử trong Ω−. Khai interior rate resolution/gcd classes, ceiling
   CPU/RAM, timeout, route stationary và các phương án được thử cùng stop rule.
   Benchmark trên discovery/calibration đã đăng ký; không xem CF để chọn numerics.
4. Phân biệt đo timing ở các calibration xác định với p95 của measure CF chưa
   thấy. p95 thực nghiệm của một tập calibration nhỏ không tự thành population
   p95 hoặc global runtime bound. Báo coverage, số điểm, sample quantile estimator,
   worst observed, resource contention và phần chưa phủ. Không tự điền t_reg=7phút.
5. Báo r trên calibration theo denominator/scope thực, tách R1/R6/undefined,
   không gọi r thật của Ω− là đã biết chỉ từ vài góc. Khóa numerical rule trước
   generation; r cao → HOLD, không tăng n để bù.
6. Nếu engine không chạy được trên resolution đã khóa: HOLD; đề xuất cải tiến
   thuật toán cùng independent-path audit, hoặc cardv2+DL đổi rounding/measure
   trước frame. Không tự đổi rational thành coarse grid, approximate fluid law,
   finite truncation hoặc bỏ regime khó mà vẫn gọi contract/cardv1.
7. Sau audit mới ghi K*/ref*/dt*/S1route/quadrature-tail/coverage/timing/r,
   version v1.3.1 và tag/receipt. Chưa có evidence đó thì không chốt n/root/CF.

[Số arithmetic](../../results/lessons/l3r_7/preparation/lattice_feasibility.json) ·
[Kế hoạch gốc](v1_3_numerics_freeze_plan.md) · [Thiết kế](confirmation_v1_3.md).
