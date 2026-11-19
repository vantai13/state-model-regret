# V7-4: giải thích signal từ raw đã lưu

Người phụ trách: Doan Van Tai.

**NOT_ENOUGH_SIGNAL: 0/37.120 bất đồng pooled và 0/37.120 stable-only ở DAY1/DAY2.**

Phân tích sau bước 0, chỉ dùng decision/prediction đã lưu; không simulation, rollout đánh giá, C_ref hay regret.

Đặt Δ̂ = chi phí M0 dự đoán của Switch trừ Stay. Với ŝ<0, Stationary chọn Switch;
Hybrid khác Stationary khi Δ̂+hŝ≥0, kể cả tie vì tie chọn Stay. Trong toàn bộ panel đã tính,
Δ̂≤0. Vì thế hai Hybrid đều chọn Switch ở cả fresh/stale, tất cả τ và h.

Thống kê |Δ̂|>h|ŝ| không phải điều kiện đủ cho bất đồng. Các exceedance ở đây mang dấu âm,
ủng hộ cùng action Switch. Đây là điểm thiếu trong lập luận khả thi dựa trên trị tuyệt đối của Claude,
không phải bằng chứng rằng seed/horizon mới tạo được action signal.

| Miền | Δ̂>0 | Δ̂<0 | Δ̂=0 | Tổng (fresh không lặp theo τ) |
|---|---:|---:|---:|---:|
| DAY1 | 0 | 9830 | 4090 | 13920 |
| DAY2 | 0 | 9950 | 3970 | 13920 |
| DAY3 | 0 | 0 | 13920 | 13920 |

DAY1/DAY2: các thống kê sau giống nhau ở cả 5 horizon (5,10,15,20,30 phút),
hai variant pooled/stable-only; mỗi phía và horizon có mẫu số 3.712 khi gộp τ.

| τ (s) | phía | n/h/variant | % bất đồng | % tie M0 | % tie Hybrid | % abs(Δ̂)>h abs(ŝ) |
|---:|---|---:|---:|---:|---:|---:|
| 300 | fresh | 1856 | 0.000000 | 86.368534 | 0.000000 | 3.448276 |
| 300 | stale | 1856 | 0.000000 | 0.269397 | 0.000000 | 3.448276 |
| 900 | fresh | 1856 | 0.000000 | 86.368534 | 0.000000 | 3.448276 |
| 900 | stale | 1856 | 0.000000 | 0.215517 | 0.000000 | 3.448276 |

Dự báo: F1 không đứng (fresh=0%); F3 đứng (tie M0 fresh≈86,37% ở mọi h);
F4 không đứng (cả hai variant đều 0 bất đồng). F2 chưa kiểm vì không truth.

Kiểm triển khai: regression h=1 giờ/seed V7-3 tái lập đúng decisions, tie flags và trạng thái;
audit độc lập raw toàn bộ 87 record khớp signal. Không thay seed, grid, metric hoặc ngưỡng.

Đây là kết luận về signal của panel hữu hạn. Không kết luận chung “không có lợi thế”;
chưa tính C_ref nên chưa biết số case evaluable, chưa đo Δc, se hoặc regret.
