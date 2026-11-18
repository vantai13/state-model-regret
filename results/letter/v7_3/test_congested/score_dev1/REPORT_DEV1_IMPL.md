V7-3 DEVIATION 01 — báo cáo triển khai và kiểm chứng, 18/11/2026

Người phụ trách: **Doan Van Tai**. Thực hiện brief tại HEAD `e3597bc3d`.
Đây là **AMENDED_ANALYSIS_DEVIATION_01**. Run gốc vẫn **INCOMPLETE**;
không chuyển thành run confirmatory hoàn tất. Không commit, SSH hoặc chạy
simulation mới trên trace; các toy controls có sẵn chỉ chạy trong test nhanh.

Hai wrapper mới dùng nguyên các hàm metric đã khóa: `case_rows`/`summarize`
và `recompute`/`rebuild_summary`. Scorer gọi `verify_lock` trước mọi input,
đọc test qua `load_days` với verified token, lấy train maximum qua
`v7_3_day.load(v7_3_cong.OUT)`. Rescorer tự duyệt archive cho cả train/test,
không import scorer, scoring wrapper hoặc test runner. Cả hai kiểm tập record
Cartesian, SHA-256, nhãn stratum, số sample và các raw identities.

Loại duy nhất **2005-06-27**: maximum 15-min total demand trong decision window
**1,551,524.830142 Mbit/s**, so với train maximum **78,984.130573 Mbit/s**,
tỷ lệ **19.64350077523515×**, vượt ngưỡng cố định **2×**. Không có exclusion
do thiếu ngày/warmup. Còn **49 ngày × 3 regime = 147 record**, đúng toàn bộ
record hoàn tất; mỗi regime có **29 S / 20 O**.

| Top-5 ngày test | Maximum demand (Mbit/s) | Tỷ lệ so với train maximum |
|---|---:|---:|
| 2005-06-27 | 1551524.830142 | 19.64350077523515 |
| 2005-06-23 | 96867.686137 | 1.2264196039667914 |
| 2005-06-21 | 78323.773350 | 0.9916393683362803 |
| 2005-07-18 | 73036.688313 | 0.9247007947437851 |
| 2005-07-13 | 69476.241321 | 0.8796227902614884 |

Cấu hình raw giữ nguyên: seed **7312001**, N=32, K=64, R_dec=64, R_eval=128,
dt=0.05 s, τ={300,900} s, h={1,2,4,6} h. Mỗi record sinh 8 case.
Evaluable iff C_ref(h)/h ≥ **12.544525 Mbit** theo card.

| Stratum | Record | Case | Evaluable | Non-evaluable |
|---|---:|---:|---:|---:|
| S | 87 | 696 | 150 | 546 |
| O | 60 | 480 | 408 | 72 |
| Tổng | 147 | 1176 | 558 | 618 |

H1–H3 dùng DAY1/DAY2, S, h={2,4,6} h: 348 case, trong đó 272 non-evaluable
và **76 evaluable**. Có 828 case ngoài population này. Các count là mẫu số
theo card; case dùng chung ngày/instance, không phải independent trials.

| Test | Gộp | h=2 h | h=4 h | h=6 h | Clause quyết định gộp |
|---|---|---|---|---|---|
| H1 | **PASS 20/22 (90.91%)** | NOT_EVALUABLE 0/0 | NOT_EVALUABLE 8/8 | NOT_EVALUABLE 12/14 | pass_share ≥80%, resolved n≥20 |
| H2 | **PASS 76/76 (100%)** | NOT_EVALUABLE 16/16 | PASS 28/28 | PASS 32/32 | pass_share ≥80%, n≥20 |
| H3 | **PASS 16/16 (100%)** | NOT_EVALUABLE 0/0 | NOT_EVALUABLE 8/8 | NOT_EVALUABLE 8/8 | pass_share ≥90%, selected n≥10 |

Mọi NOT_EVALUABLE ở bảng trên do `minimum_cases`, giữ nguyên ngưỡng khi chia
horizon. H1 chỉ đếm resolved cases; F_EQUAL và GS_WITHIN_2SE không vào mẫu số.
H2 đếm Hybrid both-side regret ≤0.5% C_ref; H3 chỉ chọn M0 regret >0.5% C_ref.

| Horizon | Evaluable | H1 F_EQUAL | H1 GS_WITHIN_2SE | H1 agree/disagree | H2 regret ≤0.5% | H3 M0 ≤0.5% | H3 HYBRID_LOWER |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2 h | 16 | 4 | 12 | 0/0 | 16 | 16 | 0 |
| 4 h | 28 | 4 | 16 | 8/0 | 28 | 20 | 8 |
| 6 h | 32 | 4 | 14 | 12/2 | 32 | 24 | 8 |
| Tổng | 76 | 12 | 42 | 20/2 | 76 | 60 | 16 |

| Forecast | Số đo | Ngưỡng | Verdict |
|---|---|---|---|
| F1, 50 ngày gốc | 29/50 = 58% | ≥60% | **NOT_HELD** |
| F1, 49 ngày | 29/49 = 59.183673% | ≥60% | **NOT_HELD** |
| F2 | 12/32 = 37.5% resolved harm tại 6 h | ≥60% | **NOT_HELD** |
| F3 | Median M0 both-side regret 0% C_ref, n=32 | ≥5% C_ref | **NOT_HELD** |
| F4 | Hybrid–Stationary agreement 42336/42336 = 100% | ≥99% | **HELD** |
| F5 | M0 338/408; Hybrid 408/408; Stationary 408/408 | Mỗi pipeline ≥80% | **HELD** |
| F6 | DAY3 S median abs(G_S) tại 6 h = 0% C_ref, n=18; 0 Mbit / 0 ms | ≤0.5% C_ref | **HELD** |
| F7 | Fresh tie share 86.368534% trên 232 record-horizon; random-tie harm retention 84/84 | Tie ≥50%, retention ≥50% | **HELD** |

F1 mỗi regime có cùng count như bảng. F4 mỗi horizon 2/4/6 h đều
14112/14112. F5 joint count là 338/408; M0 theo h=1/2/4/6 h lần lượt
82/96, 82/98, 88/104, **86/110 (78.181818%, NOT_HELD ở 6 h)**;
Hybrid và Stationary đều 100% trên các mẫu số tương ứng. F7 dùng cả bốn
horizon DAY1/DAY2 S, kể cả non-evaluable: retention theo h=1/2/4/6 h là
16/16, 16/16, 24/24, 28/28; tie share bằng 86.368534% ở từng horizon.

Trong 32 evaluable case DAY1/DAY2 S tại 6 h: median both-side regret của M0,
Hybrid và Stationary đều 0% C_ref. M0 có 12/32 case G_S<0; median harm size
trên 12 case là **22.314668% C_ref = 55.798151 Mbit = 4.448008 ms**.
Hybrid và Stationary đều 0/32 harm cases. Đây là số đo, không thêm diễn giải.

Các command đã chạy, với `source .venv/bin/activate` và
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`:

```bash
python3 -m experiments.letter.v7_3_test verify-lock
python3 -m pytest -q tests/test_letter_v7_3_dev1.py --basetemp=/tmp/v7_3_dev1_tests_initial
python3 -m pytest -q -m 'not slow' tests/test_letter_v7_3*.py --basetemp=/tmp/v7_3_dev1_fast_suite -o cache_dir=/tmp/v7_3_dev1_pytest_cache
python3 -m experiments.letter.v7_3_score_dev1
python3 -m pytest -q -m 'not slow' tests/test_letter_v7_3*.py --basetemp=/tmp/v7_3_dev1_recovery_suite -o cache_dir=/tmp/v7_3_dev1_recovery_cache
python3 -m experiments.letter.v7_3_score_dev1
python3 -m experiments.letter.v7_3_rescore_dev1
python3 -m experiments.letter.v7_3_test verify-lock
git diff --exit-code
git diff --cached --exit-code
```

Test mới ban đầu: 31 PASS/3.17 s; fast suite ban đầu: 125 PASS/7.78 s.
Lần score đầu **FAIL ở JSON serialization (`numpy.int64`)**, sau khi ghi CSV.
Chỉ sửa I/O của wrapper: đổi NumPy scalar sang Python scalar và chỉ tái sử dụng
CSV có nội dung trùng từng byte; không sửa metric hoặc file locked. Thêm ba
regression tests, fast suite cuối: **128 PASS, 4 deselected, 9.52 s**.
Có 4 warning marker `slow` chưa đăng ký; không sửa cấu hình pytest có sẵn.
Lần score tiếp theo hoàn tất. CSV đầu/cuối cùng SHA-256
`6676b07844040df695e17e7444c41f5333c65afa150917b46dee89c9affb78c5`.

Independent rescore: **MATCH**, **1176 case**, **0 mismatch**, mọi trường của
CSV/summary/deviation được so sánh; rtol=1e-12, atol=0, verdict exact.
Kiểm tra cuối **LOCK MATCH**; 8/8 integrity checks true, source SHA khớp
output, không thay tracked file và HEAD vẫn `e3597bc3d`. Lock SHA-256:
`e1bd0c956cb2a8af3fb73692b9f160fd53673c24ca6f3b1fd667b88ff3047b5b`.

File mới:

- Source: `experiments/letter/v7_3_score_dev1.py`,
  `experiments/letter/v7_3_rescore_dev1.py`, `tests/test_letter_v7_3_dev1.py`.
- Output đều dưới `results/letter/v7_3/test_congested/score_dev1/`:
  `summary.json`, `cases.csv`, `deviation.json`, `rescore.json`,
  `REPORT_DEV1_IMPL.md`.
- Log/evidence cùng thư mục: `pytest_fast.log`, `pytest_fast_recovery.log`,
  `score.log` (giữ lỗi đầu), `score_recovered.log`, `rescore.log`,
  `verify_lock_final.log`, `integrity_checks.log`, `serialization_failure_receipt.json`.
- Cấu hình gốc giữ nguyên tại `results/letter/v7_3/card_v7_3_params.json`;
  lock tại `results/letter/v7_3/test_congested/lock.json`.

Không tạo biểu đồ hoặc simulation output mới. Đã xác nhận việc chấm amended
population và rescore khớp; run 150 record gốc vẫn INCOMPLETE, không có outcome
cho ngày bị loại. Phần diễn giải nghiên cứu dành cho Claude theo brief.
