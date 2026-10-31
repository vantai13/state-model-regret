# L4.9 (v2) — đã freeze dự đoán, chưa chạy held-out

Người phụ trách: **Doan Van Tai** · 31/10/2026. AI hỗ trợ triển khai;
không tác giả tự viết proof/forecast kín sách hoặc human review.

## Kết quả và quyết định

Tác giả chọn nguyên văn “Dùng bộ H-L1/H-L2 đã sửa như đề xuất” trước predictor
mới, rồi chọn “H-L1 primary; H-L2 exploratory, không fit thêm (khuyến nghị
theo stop rule)” sau discovery. Hai choices được lưu riêng, không backdate.

H-L1: GS|M1/Cref≤0,5% ở ít nhất90% panel ngoại suy cố định. Không có uniform
finite h*, không nhận exact zero. H-L2: giữ formula, Spearman≥.7 và MedAE
giảm≥30% so1NN, nhưng chỉ exploratory; không fit thêm. H-L3 không adopted.
[T09](../../../notes/theory/T09_stationary_dominance_limits.md) chỉ ra lỗi
pointwise→uniform trên unbounded state và sửa sign comparison tại exact ties.

Part B dùng toàn86 saved native keys có h/κ≥30, không chọn theo predictor:

| Discovery sample | n | Spearman | MedAE stationary (pp) | MedAE1NN (pp) |
|---|---:|---:|---:|---:|
| Tất cả đã khai | 86 | .549016 | 5.267210 | 1.517567 |
| Không raw arithmetic flag, sensitivity riêng | 45 | .628611 | 5.175858 | 1.480960 |

Predictor sai số lớn **3,470825 lần** null trên primary discovery sample;
chưa đạt cả hai ngưỡng tham khảo. Đây là exploration, không held-out FAIL
hoặc bằng chứng theorem sai. Giữ41 raw flags, không lọc để cải thiện primary
score. No-flag sensitivity cũng thua. Không thêm predictor thay thế.

Null:1.231 unique physical keys (597 native+634 pilot), frozen scaling và
deterministic ties; discovery leave-one-physical-key-out. 1 pilot sealed
alias được bỏ **trước** parse metric. Không mở sealed R09/R10 hoặc CF outcomes.
4 saved discovery grid checks cho mean-only `dh` có max difference **0** và
zero/saturation flags giống nhau; chênh Pmis giữa native grid và K320 tối đa
6,882216e−5. Không dùng kiểm tra này để sửa predictor/K/primary score.

## Đã chạy

Từ repo root, các lệnh chính thực tế:

```bash
.venv/bin/python -m pytest -q tests/test_p4_09_stationary.py
.venv/bin/python -m experiments.P4_09_stationary.discovery
.venv/bin/python -m experiments.P4_09_stationary.timing
.venv/bin/python -m pytest -q
.venv/bin/python -m experiments.P4_09_stationary.verify_saved
.venv/bin/python -m experiments.P4_09_stationary.freeze_predictions
```

20 targeted tests PASS sau sửa; full suite **962 PASS trong90,36s wall**.
Bao gồm counterexample hữu hạn, ties, mean-only noncircularity, fixed1NN,
H-L1/U rule, H-L2 three-level scoring và collision/extrapolation checks.
Saved-score verification:86/86 NN references và1.231 training rows khớp;
Spearman/MedAE tái tính bằng saved rows khớp summary. Không random simulation,
seed không áp dụng; stationary solver/quadrature deterministic.

Lần đầu test bắt lỗi conversion `str(Fraction)`→longdouble trong adapter mới.
Đã lỡ khởi động full tests/discovery trước khi đọc failed test; discovery
dừng trước prediction đầu tiên, full suite1 FAIL/961 PASS. Sửa scale bằng
`P.number(quantum*dt)` ở18234ac7 rồi chạy lại. Giữ đầy đủ failed attempt và
traceback, không sửa engine/công thức hoặc bỏ failure khỏi lịch sử.

Part B86/86:13,533231 CPU-s /13,562679 wall-s. Benchmark dùng nguyên native
evaluator, main640/4, ba points h16 từ discovery và một h32 calibration mới:

| Case | Cache/trạng thái | Worker CPU-s | Native call CPU-s |
|---|---|---:|---:|
| P44_002 | Saved profiles; completed | 2.843346 | .298654 |
| P44_005 | Saved profiles; completed | 3.046664 | .662336 |
| P44_014 | Saved profiles; completed | 2.687716 | .320538 |
| CAL_L49_H32 | Fresh profiles/reused stationary; SIGXCPU returncode−24 | 60.552639 | Chưa hoàn tất |

Original recorded h16 calls tương ứng28,790172/38,290002/12,097328 CPU-s,
có mức reuse khác nhau; không gọi warm timings là cold full-bundle cost.
H32=(λA7,λB6,κ.3,η.5,h32), h/κ106,67: mới và calibration-only, đã khai
trước run, khác mọi held-out key. Giới hạn60CPU/90wall cho từng case; không
retry hoặc ngoại suy chắc chắn tổng cost. **Part C partial; feasibility
UNRESOLVED.** Worker log được giữ, không có completed h32 row hay số đo giả.

## Freeze và giới hạn claim

Plan commit **faa4f848** đứng trước parameter-only forecast. Đã lưu12/12
forecast,2,309191 CPU-s; **0 finite-h M1 outcomes**. Chỉ stationary laws/moments,
M0 mean profiles và null cũ được dùng. [Plan](../../../notes/design/analysis_plan_v1.md)
có9 mục: hypothesis, predictor, null,12 exact coordinates, numerical rule,
budget/stop, exposure và claim boundary; [lock](../../../notes/design/analysis_plan_v1.lock.json)
ghi16 SHA256 và engine guards. Đủ12 coordinates mới, ratios320/640>160;
không sàng điểm theo forecast. Không chạy Phase5 trong lesson này.

Future cap8CPU-giờ, tối đa12×3 levels640/4,320/4,640/2; không thay N, nới
threshold hoặc refine để cứu. H-L1 dùng mẫu số12, cần≥11 MEETS khi không U;
readiness/R6 boundary uncertainty được giữ. H-L2 exploratory phải có đủ12
READY và đọc metrics ở cả3 levels. Resource stop/incomplete→INCONCLUSIVE.
R6/refinement là numerical sensitivity, không certified error bound/CI.

Bảng exploration input đã được đưa nguyên số vào plan §7. Metadata bin
counts230/338/284/248/36 khớp trên1.136raw rows (18duplicates); bin3–10 chỉ
337metric rows sau bỏ sealed XA097, không tuyên bố full-bin median đã replay.
Search rộng hơn thấy26 fixedκ.1/age1 slices h2→4→8:24 theo xu hướng
state↓/model↑,2 ngoại lệ λA=λB=8.5 được giữ. Sáu slices nguồn input không
được cung cấp IDs đầy đủ. Mọi SV FAIL_SCREEN/10SUB/L4.6–4.8/Part B/h32 partial
đều là exposure trước freeze, không held-out evidence.

Chỉ kiểm local P13 note đã có, không primary reread mới;0 online literature
queries/newpapers/downloads, không đổi catalog/Excel/author reading levels.
Không nhận novelty/transient theorem hoặc empirical DC validation.
Đóng băng thiết kế không tự đóng **Gate4/P0-V10/L8/Understanding**; h32
feasibility còn mở. SUB66 chưa chạy/CF270 vẫn park; D22 native DEFERRED.
Bước tiếp cần kiểm Gate4 và quyết định thực thi trong hard budget đã khai;
không tự chạy held-out để hoàn tất tài liệu.

## Artifacts

- Source/config: [P4_09_stationary](../../../experiments/P4_09_stationary/),
  [protocol](../../../experiments/P4_09_stationary/protocol.json),
  [20 tests](../../../tests/test_p4_09_stationary.py).
- Data: [86 predictions CSV](discovery/predictions.csv), [JSONL](discovery/predictions.jsonl),
  [summary](discovery/summary.json), [null training](discovery/nn_training.csv),
  [12 future predictions CSV](future_predictions.csv), [JSONL](future_predictions.jsonl).
- Checks: [saved scores](saved_score_verification.json), [mean profiles](mean_only_validation.json),
  [exposure](discovery/exposure_audit.json), [exploration replay](supplied_exploration_replay.json),
  [freeze verification](freeze_verification.json).
- Logs: [full tests](tests.log), [failed tests](tests_attempt01_failed.log),
  [discovery](discovery.log), [failed discovery](discovery_attempt01_failed.log),
  [timing](timing.log), [timing JSON](timing/summary.json),
  [stopped h32 worker](timing/CAL_L49_H32/worker.log), [verification](verification.log),
  [parameter-only forecasts](future_predictions.log).
- Figure: [PNG](discovery_predictions.png), [PDF](discovery_predictions.pdf).
  Không có held-out truth CSV, MC output hoặc h32 completed row được tạo.
