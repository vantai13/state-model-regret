# V7-4 signal — decisions-only

Người phụ trách: Doan Van Tai.

**NOT_ENOUGH_SIGNAL**; không rollout đánh giá, C_ref hay regret.

Bảng chính: DAY1/DAY2 tầng S, gộp hai τ; mẫu số có lặp cùng fresh qua τ.

| h (phút) | variant | phía | bất đồng / n | % bất đồng | % tie M0 | % tie Hybrid | % abs(gap)>h abs(s) |
|---:|---|---|---:|---:|---:|---:|---:|
| 5 | pooled | fresh | 0/3712 | 0.000000 | 86.368534 | 0.000000 | 3.448276 |
| 5 | pooled | stale | 0/3712 | 0.000000 | 0.242457 | 0.000000 | 3.448276 |
| 10 | pooled | fresh | 0/3712 | 0.000000 | 86.368534 | 0.000000 | 3.448276 |
| 10 | pooled | stale | 0/3712 | 0.000000 | 0.242457 | 0.000000 | 3.448276 |
| 15 | pooled | fresh | 0/3712 | 0.000000 | 86.368534 | 0.000000 | 3.448276 |
| 15 | pooled | stale | 0/3712 | 0.000000 | 0.242457 | 0.000000 | 3.448276 |
| 20 | pooled | fresh | 0/3712 | 0.000000 | 86.368534 | 0.000000 | 3.448276 |
| 20 | pooled | stale | 0/3712 | 0.000000 | 0.242457 | 0.000000 | 3.448276 |
| 30 | pooled | fresh | 0/3712 | 0.000000 | 86.368534 | 0.000000 | 3.448276 |
| 30 | pooled | stale | 0/3712 | 0.000000 | 0.242457 | 0.000000 | 3.448276 |
| 5 | stable_only | fresh | 0/3712 | 0.000000 | 86.368534 | 0.000000 | 3.448276 |
| 5 | stable_only | stale | 0/3712 | 0.000000 | 0.242457 | 0.000000 | 3.448276 |
| 10 | stable_only | fresh | 0/3712 | 0.000000 | 86.368534 | 0.000000 | 3.448276 |
| 10 | stable_only | stale | 0/3712 | 0.000000 | 0.242457 | 0.000000 | 3.448276 |
| 15 | stable_only | fresh | 0/3712 | 0.000000 | 86.368534 | 0.000000 | 3.448276 |
| 15 | stable_only | stale | 0/3712 | 0.000000 | 0.242457 | 0.000000 | 3.448276 |
| 20 | stable_only | fresh | 0/3712 | 0.000000 | 86.368534 | 0.000000 | 3.448276 |
| 20 | stable_only | stale | 0/3712 | 0.000000 | 0.242457 | 0.000000 | 3.448276 |
| 30 | stable_only | fresh | 0/3712 | 0.000000 | 86.368534 | 0.000000 | 3.448276 |
| 30 | stable_only | stale | 0/3712 | 0.000000 | 0.242457 | 0.000000 | 3.448276 |

Tổng bất đồng chính: 0; horizon fresh ≥1%: [] s.

Các bảng theo τ, DAY3 và toàn bộ 87 bản ghi nằm trong signal.json. Các số đếm là mẫu số, không phải thử độc lập.
CPU record: 672.678910 s; wall: 679.301302 s.

Source chưa commit theo brief; SHA được lưu trước bước 0. Claude cần duyệt và commit trước truth.
