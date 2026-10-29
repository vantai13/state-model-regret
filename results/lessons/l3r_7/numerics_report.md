# L3R.7 — kết quả calibration numerics đã chạy

Người phụ trách/người soạn: **Doan Van Tai** · 29/10/2026 · DL-078–079.
Prereg commit `0efddcc` trước run; trạng thái **HOLD_NUMERICS_FEASIBILITY**.

Đây là kết quả chạy thật trên engine/law hiện tại. Không cấp n/root/CF và không tạo tagv1.3.1.

| Job | Kết quả | Degree | Wall(s) | CPU(s) | RSS mẫu(MiB) | Phase cuối / lý do |
|---|---|---:|---:|---:|---:|---|
| X2065 | COMPLETED | — | 20.752 | 20.749 | 120.5 | mpmath_lu_completed / — |
| X1008 | COMPLETED | — | 4.548 | 4.546 | 115.3 | mpmath_lu_completed / — |
| X1009 | COMPLETED | — | 4.852 | 4.830 | 115.1 | mpmath_lu_completed / — |
| CAL_BASE_A | COMPLETED | 12 | 0.758 | 0.719 | 63.2 | mpmath_lu_completed / — |
| CAL_RATE_10_A | COMPLETED | 120 | 3.386 | 3.354 | 66.1 | mpmath_lu_completed / — |
| CAL_RATE_100_A | UNRESOLVED | 1200 | 118.499 | 120.309 | 351.4 | mpmath_lu_started / CPU_LIMIT |
| CAL_RATE_1000_A | UNRESOLVED | 12000 | 120.412 | 120.406 | 2267.4 | numpy_roots_started / CPU_LIMIT |
| CAL_RATE_1000_B | UNRESOLVED | 12000 | 120.457 | 120.449 | 2267.5 | numpy_roots_started / CPU_LIMIT |
| CAL_KAPPA3_A | COMPLETED | 12 | 0.757 | 0.754 | 63.2 | mpmath_lu_completed / — |

Legacy anchors khớp **3/3**, gồm numeric pair columns theo bit pattern.
Stationary marginals hoàn tất **3/6**; UNRESOLVED **3**.
Tổng worker CPU **396.116s**; tổng elapsed nối tiếp **394.422s**.

## Điều đã và chưa xác nhận

- Nếu anchors PASS: xác nhận tái lập engine ở ba regime đã thấy, chưa là global accuracy.
- Probe stationary chỉ tính marginal/certificate/quantile/posterior; không tính J/gap/regret/contrast ở joint regime mới.
- Timeout/resource/error là UNRESOLVED trong ceiling đã preregistered; không gọi là hypothesis FALSIFY hoặc chứng minh mọi thuật toán đều không chạy được.
- Hệ mpmath giải dày và bước numpy_roots cần được kiểm/đổi thuật toán khi tăng degree; không ngầm hạ rate grid hoặc dùng fluid law.
- Không chuyển timing của vài marginal thành p95 đầy đủ, không suy r của measure từ những ca này.
- **312 global calibration jobs không chạy** theo stop rule; chưa có coverage R1/R6/fullκ3h16costs.
- Route/tail/cost-moment certificate, global accuracy, D22 và dry-runB vẫn chưa đóng; n/root/CF giữ null.
- Kiểm sau run: helper `experiments/V13_step1/regime.py` chứa `cut_value` thiếu trong explicit45-file manifest. File hiện tại khớp byte với runcommit0efddcc và3anchorsreplay khớp; đây là evidence bổ sung sau run,không gọi là preregistered coverage. Fullaudit sau này phải khóa đầy đủ dependency. Chi tiết: `numerics_logs/post_run_dependency_check.json`.

## Lệnh và file

```bash
.venv/bin/python -m pytest tests/test_r3r_numerics_budget.py -q
.venv/bin/python -m pytest -q --junitxml=results/lessons/l3r_7/numerics_logs/full_suite_final.xml
.venv/bin/python -m experiments.R3R_07_numerics.run --prereg experiments/R3R_07_numerics/prereg.json --out results/R3R_numerics/20261029_01
.venv/bin/python -m experiments.lessons.report_r3r_numerics
```

Tests trước calibration: **595full/8targeted PASS**. Test suite595 chạy sau khi thêm guard direct-worker không được mở global schedule. Giữ snapshot594 trước đó.

- Prereg/code: `experiments/R3R_07_numerics/` (run.py,worker.py,budget.py,prereg.json/md).
- CSV: `results/R3R_numerics/20261029_01/metrics.csv`.
- JSON: `results/R3R_numerics/20261029_01/summary.json`, `verification.json`, từng job/result/resource/receipt.
- Logs/phase: từng job/stdout.log, progress.jsonl và `results/lessons/l3r_7/numerics_logs/calibration.log`.
- Không tạo chart/PDF, final numerics tag/receipt hoặc CF list.

## Bước tiếp theo theo evidence

Giữ card/contract v1.3 và stop rule. Cần engineering/audit thuật toán stationary ở resolution đã khóa, rồi full numerical audit trước khi khóav1.3.1. Không tự đổi measure/rounding để làm kết quả chạy được. Nới ceiling hoặc method mới cần version/DL và giữ kết quả lần này. Phase4 HOLD/G1 giữ nguyên.
