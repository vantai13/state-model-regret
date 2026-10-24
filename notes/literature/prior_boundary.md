# Prior boundary — Part A, chưa phải quyết định Gate L

Người phụ trách: **Doan Van Tai** · 24/10/2026 · AI đề xuất, không L-self.

## Prediction receipt và deviation

Bảng dự đoán ở [prior_predictions.md](prior_predictions.md), claims ở
[claims.md](claims.md). Bộ khung lưu trong commit `5ab4750`; proof T03 v2 lưu
trong `3870931`. Cả hai sau exposure từ hội thoại; không đáp ứng điều kiện
prediction commit trước L2.2. Không sửa timestamp hoặc lịch sử để giả đạt.

| ID | Dự đoán đã exposed | Closest prior đã kiểm | Đã ngụ ý | Khác biệt còn cần kiểm | Hậu quả cho prediction | Nhãn AI đề xuất / mức tin cậy |
|---|---|---|---|---|---|---|
| PC1/C1 | DROP contribution | SOB14 Eq4 T; B82 A + T03 proof | EVPPI functional, conditional VSS theo định nghĩa, nonnegativity | Không còn claim khái niệm mới; original B82 reading thiếu | Không dự đoán identity/dấu ≥0 như discovery | DROP như contribution; giữ framing, source gate còn mở |
| PC2/C2 | NARROW | P11 Eq2.7–2.8 T; SOB14 T | So input-information và model-discrepancy value có prior | K2 so repair effects đúng D21 trong load-changing queue; không parameter/structure repair | Giữ ngưỡng/K2 exploratory, chưa chạy | NARROW tạm; chưa có outcome grid |
| PC3/C3 | KEEP | T03 identity; P11 không tự quyết định cùng interaction estimand | Gamma là difference-of-gains, hai dấu có toy | Predictive mechanism/regime còn cần blind-spot L2.8 và A05 | K3 không đủ chứng minh mechanism | KEEP là forecast; Gate L chưa đánh giá đủ |
| PC4/C4 | NARROW | Chưa đủ primary về threshold null | Không có evidence thắng null | Feature/metric/budget/split theo D25/A05 | Không tự fit/chọn baseline bây giờ | NARROW forecast, đánh giá HOLD tới A05/L2.8 |
| PC5/C5 | NARROW | T01 E0; P12 chưa đọc | Same action có thể giữ decision loss nhỏ dù cost bias | OεRE/value equivalence và miền K5 cần kiểm | Giữ K5/Q5; không gán nghiệm đúng trước chạy | NARROW forecast, pending L2.4 |
| PC6/C6 | NARROW | Contract D22; P13 chưa đọc | Full state gồm backlog+mode | D22 fixed-M0 split, timescale/horizon hợp lệ | K6 chưa chạy; không gọi mode visibility là refresh-only | NARROW forecast, pending L2.5–L2.7 |

## Không được claim là mới hoặc được xác nhận

- Khái niệm EVPPI, VSS, dấu ≥0 dưới đúng giả định; Gamma bookkeeping.
- Ý tưởng so giá trị học inputs với giá trị học model discrepancy để định hướng
  nghiên cứu/cải tiến model (P11 §2.4 Eqs2.7–2.8).
- “Model fidelity nói chung” từ M0→M1 của D21; tên EVIU như primary đã đọc.
- Tần suất/độ lớn contrast của mạng thật từ toy hoặc lưới chọn gần boundary.
- Main RQ đã được literature xác nhận mới, hoặc P11 đã giải quyết hết Main RQ.

## Trạng thái

Đủ bộ artifact kỹ thuật Part A sau chạy và audit, xem report. Formal Part A
**HOLD**: không có L-self/proof kín sách/đọc lại sau một ngày của tác giả; missing
pre-reading commit là deviation không thể khôi phục. B82 full reading và MAB11
§2 còn hạn chế truy cập; không dùng chúng để claim bounds. Không cấp phép freeze
L3.3 bằng một technical PASS. G1 và HOLD Phase4 giữ nguyên; L2.4 được học tiếp.
