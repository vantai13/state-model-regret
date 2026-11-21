# S1-C — báo cáo triển khai và pilot

Người phụ trách: **Doan Van Tai**. AI hỗ trợ theo brief S1-C ngày 21/11/2026.
**EXPLORATORY; full sweep chưa chạy.** Không commit/SSH/tải dữ liệu mới trong phiên S1-C.
Chỉ tạo source/tests/script được brief cho phép và file dưới thư mục kết quả này.

## A. Đã thực hiện

- Đọc brief/PLAN_SWEEP, source EV-D/trace_cox/packet/EV-D4b/c, báo cáo wave 1–3 và X5/X5c.
- Tạo `experiments/letter/sweep_trace.py`, `tests/test_sweep_trace.py`, `experiments/letter/sweep_trace_gcp.sh`.
- Chia train/test theo thời gian 50/50; mọi ước lượng chỉ từ train. Dùng hai FIFO queues, cost tổng backlog packet·s, service exponential và managed Poisson, c_sw=0.
- M0 dùng backlog hiện tại (τ=0); thêm plug-in stale τ=1/10/30/60/120/300 s. Static=1{ŝ<0}; hybrid=1{gap_fluid+hŝ<0}. Mọi tie chọn action0.
- Hai path dùng hai flow partitions đồng bộ thời gian của cùng link. Sinh Cox arrivals từ cường độ đo thật; không bảo toàn PCAP packet/flow dependence. Giữ cùng realization và residual services cho mọi action, h, τ.
- Oracle chọn min hai realized costs (clairvoyant lower bound), không phải conditional-expected oracle. Lịch sử trước quyết định dùng action0; không mô phỏng controller vòng kín.
- Grid 27 cấu hình: 3 ngày × scale {0.8,1,1.2} × mu {(10,10),(9.5,10.5),(10.5,9.5)}. Background nominal [6.5,6.8]×scale, u=1 model packet/s.
- h/T_int={0.3,0.5,1,2,3,5,10}; N full=128, pilot=24. Uniform và alarm occupancy (backlog stale trên path static chọn ≥max(1,train q90)). Không first passage/hysteresis.
- Không lặp hoặc nén trace. Thiếu future/censored T_int/không alarm được báo riêng, không đổi thành kết quả 0.

Chi tiết thiết kế trước pilot: `DESIGN_S1C.md`; bổ sung post-hoc: `POSTHOC_FEASIBILITY.md`.

## Trace hiện có

Độ dài dưới đây bỏ bin cuối một cách bảo thủ. Bin gốc 10 ms ở ba trace dùng trong grid.

| Trace | Đường dẫn | Độ dài (s) | Train/test (s) |
|---|---|---:|---:|
| ditl_20230412 | `results/ext_validity/ev_d4/series_ditl4h_mod10.npz` | 14400.06 | 7200.03/7200.03 |
| mawi_20250311 | `results/ext_validity/ev_d3/series_20250311.npz` | 900.00 | 450.00/450.00 |
| mawi_20260414 | `results/ext_validity/ev_d3b/series_20260414.npz` | 900.02 | 450.01/450.01 |

Còn có hai đoạn DITL 15 phút 10:00 và 12:00, DITL mod250, MAWI c1 trùng và c25 nén; xem `design_ready/inventory.json`. Không đếm chúng như ngày độc lập. Bản DITL có 8 gap bins đã được extractor cũ điền; giữ nguyên, không sửa input.

Chưa cần tải nguồn khác để thực hiện grid này. Nếu mở rộng validation, cần khung liên tục dài hơn trên những ngày mới và tốt hơn là dữ liệu từ hai link/queue có timestamps, capacity và queue telemetry thực tế. Chưa kiểm hay tải nguồn mới.

## B. Test và tái lập

- Lượt test mới đầu: **4 FAIL / 12 PASS**, do fixture toy độ dài không nhất quán (3 lỗi) và assertion bitwise residual .6 vs .6000000000000001 (1 lỗi). Chỉ sửa file test mới; giữ `pytest_initial.log`.
- Sau sửa: **64 PASS, 3.44 s**, gồm S1-C, EV-D4c và trace extractor.
- Cuối: **87 PASS, 9.87 s**, thêm toàn bộ `test_ext_packet.py` và guard không dự phóng khi không có replay. `bash -n` PASS.
- Các kiểm tra có ý nghĩa: Lindley integral, fluid closed form/giảm đúng về equal-capacity EV, u=0 CRN, replay action0 khớp tích phân lịch sử, pending residual services, test-tail mutation không đổi bất cứ train fit/draw nào, không wrap, finite support, regret trên toàn population, CI theo block thay vì instants, write-once/source hash.
- EV-D4b `MN00_tau1`, seed14000, nguyên cấu hình cũ: tái chạy train, không chạy EV test; bốn đại lượng sau đều sai số tuyệt đối **0**:

| Đại lượng | Đã lưu | Tái lập |
|---|---:|---:|
| mean_stay | 14.796291962920 | 14.796291962920 |
| mean_switch | 13.743243432434 | 13.743243432434 |
| s_train | -1.053048530485 | -1.053048530485 |
| T_int | 106.585932454726 | 106.585932454726 |

CPU reference: 12.416918 s. Đây là calibration legacy có periodic replay; không dùng nó làm train của S1-C.

## C. Pilot, kể cả lượt chưa khả thi

Pilot đầu đã chọn trước: DITL scale1.2, mu=(9.5,10.5), seed211121. T_int=1015.883909 s nhưng censored; **0 test rows / NOT_EVALUABLE**. Không tính regret. Artifact giữ ở `pilot/`; dự phóng cũ trong `pilot/summary.json` **INVALID_NO_REPLAY**, xem `projection_correction.json`. Đã sửa guard báo NOT_ESTIMABLE khi rows=0; không sửa artifact cũ.

Screen bổ sung **POST_HOC_TRAIN_ONLY**: 9 cấu hình DITL trong grid, 7 khả thi theo quy tắc đã ghi trước screen (uncensored, ≥4 epoch ở h10). Chọn proxy train-work lớn nhất: `ditl_20230412_s120_c2`, mu=(10.5,9.5). Không sàng theo regret/bất đồng. Screen CPU 0.461995 s. Lỗi invocation đầu thiếu PYTHONPATH xảy ra trước output; log giữ nguyên.

Pilot khả thi: seed train=211121, test=1211121; ŝ=338.138710865 packets; T_int=345.091207790 s; ngưỡng alarm=588 packets; static chọn A.
**973 hàng = 139 epoch×h ×7 tuổi telemetry**, 98 summary cells, một cấu hình/ngày. Không phải 973 mẫu độc lập. 24 candidate epochs giảm còn 11 ở h10 vì thiếu future ở cuối trace.

Kết quả fresh τ=0, population uniform. Regret là mean trên **mọi** epoch hợp lệ, đơn vị packet·s; Δ=static−hybrid, dương là hybrid tốt hơn.

| h/T_int | n | Bất đồng | Regret M0 | Regret static | Regret hybrid | Δ packet·s | Δ (% mean C_ref) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.3 | 24 | 0/24 | 115.269 | 2585.856 | 2585.856 | 0.000 | 0.0000 |
| 0.5 | 23 | 0/23 | 424.572 | 7214.952 | 7214.952 | 0.000 | 0.0000 |
| 1 | 23 | 0/23 | 1836.035 | 31173.406 | 31173.406 | 0.000 | 0.0000 |
| 2 | 21 | 2/21 | 8451.482 | 119290.474 | 96682.203 | 22608.271 | 6.2769 |
| 3 | 20 | 2/20 | 21674.992 | 265643.096 | 212875.013 | 52768.084 | 11.3239 |
| 5 | 17 | 0/17 | 79979.723 | 673571.118 | 673571.118 | 0.000 | 0.0000 |
| 10 | 11 | 0/11 | 450895.438 | 1790274.052 | 1790274.052 | 0.000 | 0.0000 |

Ở h2: static/hybrid = 33.1196%/26.8427% mean C_ref; ở h3 = 57.0062%/45.6824%. **M0 có regret thấp hơn hybrid ở cả bảy h trong pilot**; không được kết luận hybrid là policy tốt nhất.

Population alarm, fresh τ=0:

| h/T_int | n alarm | Bất đồng | Regret static (packet·s) | Regret hybrid (packet·s) | Δ (% mean C_ref) |
|---:|---:|---:|---:|---:|---:|
| 0.3 | 10 | 0/10 | 3486.283 | 3486.283 | 0.0000 |
| 0.5 | 10 | 0/10 | 10224.329 | 10224.329 | 0.0000 |
| 1 | 10 | 0/10 | 48445.698 | 48445.698 | 0.0000 |
| 2 | 8 | 2/8 | 207120.696 | 147773.986 | 7.4219 |
| 3 | 7 | 2/7 | 478354.717 | 327588.764 | 14.3150 |
| 5 | 4 | 0/4 | 1272513.469 | 1272513.469 | 0.0000 |
| 10 | 0 | NA | NA | NA | NO_ALARMS |

Fresh exact tie M0: **0/139**. Bất đồng fresh gộp: **4/139=2.8777% epoch×h**, thực chất chỉ **hai thời điểm** lặp ở h2/h3. Khi bất đồng, mean paired gain tại h2/h3 lần lượt **237386.841 / 527680.835 packet·s**. Cả bốn đều nằm trong alarm population. Những h khác gain=0 vì action trùng; không phải không có regret.

Tuổi telemetry khác: toàn bộ số liệu trong `pilot_feasible/summary.csv`, không chọn riêng fresh để bỏ kết quả xấu. Bất đồng uniform gộp theo τ=0/1/10/30/60/120/300 s: **4/4/4/4/3/2/4 trên 139 epoch×h mỗi tuổi**. M0 ties tương ứng 0/0/0/0/0/2/14.

### CI và diễn giải

CI descriptive 95% Student-t qua contiguous-block means (khác trọng số epoch mean khi block có số điểm khác nhau). H2 và h3 uniform đều chỉ có 6 block được quan sát:

| h/T_int | Block-mean Δ (packet·s) | CI95% (packet·s) |
|---:|---:|---:|
| 2 | 23104.207 | [-15088.858, 61297.271] |
| 3 | 58631.204 | [-36928.773, 154191.181] |

**Cả hai CI chứa 0.** Chỉ có một ngày nên day-level CI=null. Các block còn có thể phụ thuộc, futures overlap; CI 0 ở nhóm action trùng không chứng nhận effect population bằng 0. Full runner sẽ báo day means/CI theo các ngày available, nhưng n tối đa chỉ 3, cần thận trọng.

Cause analysis hậu kiểm: hai điểm tạo gain có qA=1986/1855, qB=6/2. Gap fluid âm vượt hŝ ở h2/h3 nên hybrid chuyển sang B; các h còn lại hybrid giữ A. Chi tiết input/gap/cost ở `pilot_diagnostics.json`. Test/train intensity ratios A/B = **1.147754 / 0.921657**, nên background test mean xấp xỉ **8.952481 / 7.520717 packet/s**, khác nominal train 7.8/8.16. Nonstationarity và sai số finite-train ŝ là yếu tố cần giữ trong diễn giải; pilot chưa tách được chúng khỏi cơ chế trạng thái. Không tune threshold, h hay policy sau thấy gain.

## CPU và dự phóng

Pilot khả thi: **0.270275894 worker CPU-s; 1.202699033 wall-s**, ProcessPool workers2 nhưng chỉ một case, WSL/numpy2.5.3. Train CPU 0.055276209; phần còn lại 0.214999685.
Kịch bản tuyến tính 27 cases ×128 candidate points: **0.009014559 CPU-h = 32.452 CPU-s**; stress ×3 **0.027043677 CPU-h**.
Ideal wall/15 chỉ **2.163 s**, không phải dự báo wall thực tế. Import/spawn 15 worker, parent scoring, I/O, cache lạnh, scheduling chưa được cộng/benchmark trên GCP. Pilot sau screen có cache ấm; đây không là upper bound, CI hay bảo đảm budget. Giữ cap CPU của Claude nếu chạy cloud; phiên này không launch.

## D. Kiểm file, log và artifact

Audit độc lập không import module experiment/scorer: **973 rows, 139 epoch×h, 98 cells PASS**; cost→regret, policy signs, fluid direct integral, populations, summaries, raw/source hashes khớp. Max absolute gap reconstruction error 1.02e-08 packet·s; không dùng epsilon trong policy.
Snapshot 41162 tracked files: **41160 khớp SHA**. Hai file metadata `AGENTS.md`, `notes/02_decision_log.md` thay đổi bởi commit song song **631ae0878 (DL-160)**, HEAD từ eb8f03e73 sang 631ae0878; audit xác nhận footprint commit đúng hai file đó. Phiên S1-C không chạy git commit, không hoàn nguyên công việc song song. Audit đầu dừng vì thay đổi này; log giữ nguyên và lượt cuối đối chiếu với Git objects thay vì giả vờ workspace bất biến.

- Source: ba file ở A; không sửa source/helper/test đã có trước phiên.
- Cấu hình dùng tiếp: `design_ready/plan.json`; trace metadata/hash: `design_ready/inventory.json`; brief snapshot giữ nguyên.
- Raw: `pilot_feasible/ditl_20230412_s120_c2/decisions.csv`, `training.json`, `receipt.json`.
- Metrics: `pilot_feasible/summary.csv`, `day_summary.csv`, `summary.json`; raw fingerprint: `raw_manifest.json`.
- Evidence khác: `reference/reference.json`, `train_screen/summary.json`, `audit.json`, `pilot_diagnostics.json`, `projection_correction.json`, `post_pilot_source.diff`, `source_at_first_pilot/`.
- Log: `pytest_initial.log`, `pytest_fixed.log`, `pytest_final.log`, `reference.log`, `design.log`, `pilot.log`, `pilot_feasible.log`, `train_screen.log` (import FAIL), `train_screen_with_path.log` (PASS), `audit.log` (concurrent metadata), `audit_final.log` (PASS).
- Không tạo biểu đồ. Không có full-sweep outcomes/confirmation/paper claim.

Các command chính **đã chạy**, sau source `.venv/bin/activate` và `experiments/explore_ctmc/env.sh`, export PYTHONDONTWRITEBYTECODE=1 (pytest thêm PYTEST_DISABLE_PLUGIN_AUTOLOAD=1):

```bash
python -m pytest -q -p no:cacheprovider --basetemp=results/letter/sweep/trace/pytest_final tests/test_sweep_trace.py tests/test_ev_d4c.py tests/test_ext_trace_rates.py tests/test_ext_packet.py
bash -n experiments/letter/sweep_trace_gcp.sh
python -u -m experiments.letter.sweep_trace reference --out results/letter/sweep/trace/reference
python -u -m experiments.letter.sweep_trace design --out results/letter/sweep/trace/design
python -u -m experiments.letter.sweep_trace pilot --plan results/letter/sweep/trace/design/plan.json --out results/letter/sweep/trace/pilot --workers 2
PYTHONPATH="$PWD" python -u results/letter/sweep/trace/train_screen.py
python -u -m experiments.letter.sweep_trace pilot --plan results/letter/sweep/trace/design_ready/plan.json --out results/letter/sweep/trace/pilot_feasible --workers 2
python results/letter/sweep/trace/audit_pilot.py
```

`design_ready/plan.json` được tạo mới từ plan gốc, cập nhật source hashes/compute-pilot case/exposure; không overwrite plan đầu. Core numerical train/replay/policy không đổi sau pilot đầu; diff chỉ guard dự phóng/default plan/test guard.

## E. Kết luận và handoff

Implementation/test/replay/saved-row audit đã kiểm thực tế. Pilot cho tín hiệu gain của hybrid so static ở hai h trung gian, tập trung vào hai epoch; M0 tốt hơn hybrid và CI qua block còn chứa 0. Chưa xác nhận vùng lợi ích rộng, tính dừng, cơ chế riêng, novelty hoặc external validity production.

Full sweep 27 cấu hình **NOT_RUN**. Lệnh sau chỉ để **Claude chạy sau**, không được thực thi trong phiên này:

```bash
bash experiments/letter/sweep_trace_gcp.sh results/letter/sweep/trace/design_ready/plan.json results/letter/sweep/trace/full
```

Script dùng `--workers 15`, không SSH/tải/poweroff, từ chối overwrite và kiểm input hashes. Trước chuyển máy cần có đủ ba NPZ + source/test/env nằm trong plan; không tự regenerate plan hay sửa helpers để bypass hash mismatch. Plan đầu `design/` là lịch sử, nguồn trước sửa nằm trong snapshot; dùng **design_ready** cho handoff.
