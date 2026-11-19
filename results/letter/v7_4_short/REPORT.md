# V7-4 — NOT_ENOUGH_SIGNAL; đóng gói trạng thái dừng

Người phụ trách: **Doan Van Tai**.

**Đã thực hiện runner, tests và bước 0 đầy đủ. Pilot timing chưa chạy; truth không chạy.**

Bước 0: 87/87 record (DAY1–DAY3 × 29 ngày S), seed 7412001, N32/K64, dt=0,05 s, τ=300/900 s, h=300/600/900/1200/1800 s.
Bất đồng Hybrid–Stationary: DAY1/DAY2 pooled **0/37.120**, stable-only **0/37.120**; DAY3 **0/18.560** cho mỗi variant.
Không horizon fresh nào đạt 1%; điều kiện ≥50 bất đồng và ≥2 horizon đều không đạt. Verdict bước 0: **NOT_ENOUGH_SIGNAL**.

| h (phút) | Pooled fresh | Pooled stale | Stable-only fresh | Stable-only stale |
|---:|---:|---:|---:|---:|
| 5 | 0/3712 (0%) | 0/3712 (0%) | 0/3712 (0%) | 0/3712 (0%) |
| 10 | 0/3712 (0%) | 0/3712 (0%) | 0/3712 (0%) | 0/3712 (0%) |
| 15 | 0/3712 (0%) | 0/3712 (0%) | 0/3712 (0%) | 0/3712 (0%) |
| 20 | 0/3712 (0%) | 0/3712 (0%) | 0/3712 (0%) | 0/3712 (0%) |
| 30 | 0/3712 (0%) | 0/3712 (0%) | 0/3712 (0%) | 0/3712 (0%) |

Các số sau giống nhau ở cả năm h, cả pooled/stable-only. Mẫu số đã gộp hai τ; fresh được lặp theo τ đúng cách đếm trong thẻ.

| Metric | Fresh | Stale |
|---|---:|---:|
| Tie M0 | 3206/3712 (86.368534%) | 9/3712 (0.242457%) |
| Tie Hybrid | 0/3712 (0.000000%) | 0/3712 (0.000000%) |
| abs(gap)>h abs(s_hat) | 128/3712 (3.448276%) | 128/3712 (3.448276%) |

Theo τ (cũng giống nhau ở mọi h và hai variant):

| τ (s) | phía | n | tie M0 | tie Hybrid | abs(gap)>h abs(s_hat) |
|---:|---|---:|---:|---:|---:|
| 300 | fresh | 1856 | 86.368534% | 0.000000% | 3.448276% |
| 300 | stale | 1856 | 0.269397% | 0.000000% | 3.448276% |
| 900 | fresh | 1856 | 86.368534% | 0.000000% | 3.448276% |
| 900 | stale | 1856 | 0.215517% | 0.000000% | 3.448276% |

DAY3: M0 tie 100% fresh/stale; Hybrid tie 0%, abs-gap exceedance 0%, bất đồng 0% ở mọi h/τ/variant.

Đây là các mẫu số dùng chung ngày/instance, không phải phép thử độc lập. Chưa tính C_ref nên chưa biết số case evaluable; 580 case chính/870 case toàn bộ chỉ là số trước gate.

## Vì sao không có signal

Đặt Δ̂ = predicted Switch − predicted Stay. Với ŝ<0, Stationary chọn Switch; Hybrid khác Stationary khi Δ̂+hŝ≥0 (tie chọn Stay).
Trong 27.840 unique-side/h instances của DAY1/DAY2, Δ̂ dương 0, âm 19.780, bằng 0 là 8.060. DAY3 có 13.920/13.920 gap bằng 0.
Thống kê |Δ̂|>h|ŝ|≈3,45% có dấu âm, cùng ủng hộ Switch. Dùng trị tuyệt đối để dự báo bất đồng đã bỏ qua chiều của gap.
Đây là observation trên panel đã tính, không phải chứng minh cho mọi trạng thái. F1/F4 không đứng, F3 đứng; F2 chưa kiểm. H-P1 vẫn NOT_RUN.
Không nới ngưỡng, thay seed/grid/strata, chạy thêm simulation hoặc đổi phương pháp để cứu signal.

## Kiểm chứng và CPU

- Tests đầu: 9 PASS/12,21 s. Tests source cuối: **11 PASS/9,83 s**; không chạy full suite.
- Regression seed V7-3, DAY1/2005-06-16, h=1 giờ: 384/384 quyết định và tie flags khớp; fresh modes/queues khớp chính xác.
- Monkeypatch phát hiện evaluation/C_ref/gather từ decisions-only; seed mới khác 10 base seed cũ; guards thiếu/uncommitted/dirty lock và negative signal đều PASS.
- Audit độc lập không import runner: **87 raw records/3.480 count rows PASS**, tái tính signal, choices, ties và ngưỡng.
- Kiểm lock cuối: **215 core SHA + 7 evidence SHA PASS**; H-P1 verbatim khớp thẻ; tracked files không thay đổi.
- Bước 0 dùng **679.197189544 CPU-s** (record compute 672.678909721 CPU-s), wall **679.301301997 s**.
- Pilot evaluation CPU=0 vì NOT_RUN; projected truth CPU=null, không suy dự phóng khi chưa pilot.

Các command đã được /usr/bin/time đo (user+system):

| Log time | CPU-s |
|---|---:|
| tests_initial.time | 11.96 |
| tests_final.time | 10.06 |
| decisions.time | 679.36 |
| signal_audit.time | 0.49 |
| diagnosis.time | 0.18 |
| finalize.time | 0.71 |
| verification.time | 0.55 |

Tổng các command **có time log**: 703.31 CPU-s; không gọi đây là toàn bộ CPU phiên vì các thao tác đọc/chuẩn bị khác không có time log.

## Pilot, predictions và lock

Thẻ ghi “Nếu không đạt: dừng”; brief vẫn liệt kê pilot timing. Đã nêu mâu thuẫn này với tác giả và giữ rollout dừng; không coi việc chưa có trả lời là chấp thuận chạy pilot.
Áp dụng stop rule đã được ghi trong thẻ, không nhận đây là một lựa chọn mới đã được tác giả xác nhận. `pilot.json` và `pilot/selection.json` ghi NOT_RUN_SIGNAL_STOP.
Hai pilot chỉ mới lên kế hoạch: DAY3/2005-07-19 (max decisions CPU 27,337847081 s), DAY1/2005-07-19 (max input work proxy còn lại); seed 7472001, đủ cỡ dự kiến.
`predictions.json` giữ nguyên H-P1/metric/forecasts/luật paper từ thẻ, n dự kiến, records, seeds và ghi pilot chưa chạy. `lock.json` là **STOP lock**, chưa commit; không phải completed-pilot lock.
Runner `create_lock()` cho nhánh pilot hoàn tất không được gọi; `finalize_signal_stop.py` chỉ hash và ghi metadata dừng. Không giả dữ liệu pilot để vượt kiểm tra hai record.
Lock SHA256: `208aecab025c31bb1afea9e1387d4401d9b25aebfb098b71f8f5e0539a94fa14`.
Guard thực tế từ chối “lock.json has not been committed to HEAD”. Khi chỉ mô phỏng HEAD trả đúng byte lock (không commit), guard kiểm đủ SHA rồi từ chối “NOT_ENOUGH_SIGNAL”. Không gọi truth runner.

## Các lựa chọn triển khai cần Claude xem

Chi tiết trước bước 0 ở IMPLEMENTATION.md và trong predictions.json: giữ tree seed/labels V7-3; dùng đủ 32 states; cùng posterior K64; stable-only lấy đúng tham số cũ DAY3 −0,4; gộp τ cho tiêu chí fresh và giữ bảng riêng τ; planned pilot theo CPU/input, không theo quality.
Có một ngoại lệ process khác: thẻ muốn code commit trước bước 0, nhưng brief cấm commit. Theo brief, đã hash code/input trước chạy và ghi code chưa commit; không nhận đã đáp ứng điều kiện commit của thẻ.
Metric (b) theo V7-3: max mean regret hai phía cùng case. Metric (a) giữ full 128 rollout cặp/action để tính sd mẫu/√128; chưa tính bằng outcome.
Không sửa file V7-3, thẻ, paper, AGENTS; không commit, push, SSH hoặc chạy truth. File mới chỉ nằm ở hai source/test được chỉ định và results/letter/v7_4_short/.

## Command

Chạy trong repo với `.venv` và `experiments/explore_ctmc/env.sh`, `PYTHONDONTWRITEBYTECODE=1`:

```bash
python3 -m pytest -q -p no:cacheprovider tests/test_v7_4_short.py --basetemp results/letter/v7_4_short/pytest_final
python3 -m experiments.letter.v7_4_short decisions
python3 results/letter/v7_4_short/verify_preparation.py --signal-only
python3 results/letter/v7_4_short/diagnose_saved_signal.py
python3 -m results.letter.v7_4_short.finalize_signal_stop
python3 -m results.letter.v7_4_short.verify_stop
```

Lệnh truth chính xác theo CLI, **CHƯA CHẠY và hiện không đủ điều kiện; kể cả commit lock vẫn bị chặn do signal**:

```bash
cd /home/vantai/state-model-regret && source .venv/bin/activate && source experiments/explore_ctmc/env.sh && PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.letter.v7_4_short truth --workers 1
```

Không có cơ sở chọn LOCAL/USE_GCP vì chưa đo pilot. `--workers 1` chỉ là cấu hình CLI minh họa chính xác, không phải một quyết định địa điểm chạy.

## Artifact

- Source: experiments/letter/v7_4_short.py; tests/test_v7_4_short.py.
- Thẻ gốc không sửa: results/letter/v7_4_short/CARD_V7_4.md.
- Input SHA/protocol: input_fingerprints.json, IMPLEMENTATION.md, decisions_started.json.
- Decisions raw: decision_records/{DAYx}_{YYYY-MM-DD}.{npz,json} — 87 cặp.
- Signal: signal.json, signal.md; diagnosis.json, diagnosis.md; hai script audit/diagnosis và signal_verification.json.
- Pilot NOT_RUN: pilot.json, pilot/selection.json; proposal chưa chạy: pilot_selection_proposal.json.
- Predictions/STOP freeze: predictions.json, lock.json, finalize_signal_stop.py.
- Kiểm lock/guards: verify_stop.py, verification.json.
- Log/time: tests_initial.*, tests_final.*, decisions.*, signal_audit.*, diagnosis.*, finalize.*, verification.*.
- Fixtures pytest: pytest_initial/, pytest_final/.
- Không tạo CSV, plot, pilot raw, truth raw hay score H-P1.

Đã xác nhận signal bằng quyết định và độ khớp triển khai trên panel này. Chưa đo timing pilot, C_ref/evaluable, Δc/se hoặc regret; không kết luận chung không có lợi thế và không thay paper.
