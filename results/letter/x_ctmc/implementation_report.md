# X-CTMC — báo cáo triển khai và pilot

Người phụ trách: **Doan Van Tai**. Design: `DESIGN_X_CTMC.md`, commit `ad3db0d`, có Phụ lục A.

## Thực hiện

- Tạo `experiments/letter/x_ctmc.py` và `tests/test_x_ctmc.py`; mọi artifact mới khác ở `results/letter/x_ctmc/`.
- Namespace `x-ctmc-v1`: generator và truncation từ `mmpp`; V bằng sparse `expm_multiply` trực tiếp, không bỏ tail của semigroup; fluid theo từng path; posterior full old state.
- Không sửa file có sẵn, không monkey-patch CTMC, không gọi guarded CTMC truth API từ module mới. Không commit/SSH/GCP; không chạy lệnh truth/score.
- CLI đã có: pilot, predict, lock, verify-lock, truth --workers N, score. Lượt này chỉ chạy pilot, test, CLI help và kiểm tra artifact. Full predict/lock chưa chạy. Independent rescore để lượt sau như brief.
- Estimator dùng W2 arrival counts từ `shat2`: bin 0.01 s, L=100 T_int, Poisson-corrected variance, covariance đến lag đầu không dương. Validation/solver nhận mu theo path; INVALID giữ nguyên, không fallback.
- 2000 cặp trên lịch sử Stay hữu hạn được lấy bằng uniformization không cắt Poisson tail; các cặp chồng lấp, không phải independent trials.

## Kiểm thử

- Final: **50 PASS, 1 XFAIL, 0 unexpected FAIL**, 13.61 s.
- Command: `python3 -m pytest -q -rx -p no:cacheprovider tests/test_x_ctmc.py tests/test_pl_posterior.py --basetemp=results/letter/x_ctmc/pytest_after_certificate`.
- Đã chạy riêng X-CTMC và `tests/test_pl_posterior.py` trước đó; suite PL có 20 tests PASS. Final gồm 30 X-CTMC PASS + 20 PL PASS + 1 XFAIL.
- Đối chiếu 2 regime cũ ở a=6, mu=10: V, fluid gap, G_S và C_ref khớp; audit ban đầu đo relative error 0. Backlog-only compatibility chỉ dùng cho đối chiếu cũ, experiment dùng full old state.
- Các controls gồm augmented-generator V, direct old/current 4D cost, G_S=0 khi policy trùng/constant, long-h slope identity, exact uniformization, posterior mode về 0, literal utilization rules, estimator W2, balanced grid và lock tampering.
- **Mâu thuẫn brief:** §8 nói theta>=1 không Switch, nhưng §4 cho phép U_A0>1 do overload ở high mode. Counterexample hợp lệ: ell_A=3, alpha_A=2.4, mu_A=5; ell_B=2, alpha_B=.4, mu_B=5; u=.3, modes(+1,-1) cho U_A0=1.14, U_B1=.38, nên TH_1 Switch. Giữ công thức và bốn theta trong grid; test yêu cầu kia XFAIL, không nhận toàn bộ analytic sanity PASS. Chưa có phản hồi tác giả cho câu hỏi này.

## Pilot thật

- Chọn đúng 4 regime lớn nhất theo |X_A|*|X_B| từ tham số/truncation. Seed pilot 2611204; h=1 T_int, tau={1,3} T_int. Không finite-h outcome ở 60 regime còn lại.
- Grid seed 2611201; train 2611202; test 2611203. Pilot estimates không thay cho train estimates.

| Regime | Status | CPU-s | Wall-s | State product |
|---|---|---:|---:|---:|
| XCTMC_053 | COMPLETED | 189.386036 | 189.757210 | 48919680 |
| XCTMC_044 | COMPLETED | 138.838672 | 138.923724 | 45504804 |
| XCTMC_047 | COMPLETED | 216.485311 | 216.676121 | 31108896 |
| XCTMC_028 | COMPLETED | 1611.289899 | 1611.868229 | 18982224 |

Tổng pilot, gồm stationary metadata và I/O: **2157.069702 CPU-s**, **2158.297986 s wall**.
Audit raw: 80 hàng, 80 valid, 0 INVALID_ESTIMATOR; checksum và identities đều PASS.

## Dự phóng và trạng thái trước truth

- Toàn 64 regime: **4.354528778 CPU-h**.
- Sau loại theo cap: **1.667345066 CPU-h**, 63/64 planned.
- NOT_RUN dự kiến: **1**; cap 3600 CPU-s/regime. Đây là loại theo chi phí dự phóng, không phải kết quả khoa học.
- XCTMC_028: 9673.861362 CPU-s, PROJECTED_CPU_CAP
- Dùng worst component coefficient từ 4 pilot: V scale tới 100 T_int, posterior scale theo số cột, pair calculations theo số horizon. Không tự thêm threshold tùy ý cho state product; product dùng xếp pilot và work sparse dùng dự phóng chi phí.
- Projection không phải guarantee/CI; chưa đo full h-grid hoặc hiệu năng GCP. Không xác nhận hypothesis, độ chính xác dự đoán hay practical validity.

## Certificate sau pilot và provenance

- Pilot thực thi source SHA `19bf70335d6090a98d5356d2680df206c772cedab7694f4b90449689334ce09f`; snapshot nguyên byte ở `pilot_source.py`. Final source SHA `27108474964546fccc66e08879b177cef9a62d9829a0191808b36069506b4a0f`.
- Raw pilot vẫn nguyên byte. Ở bản pilot, policy hằng có roundoff khoảng 1e-14 C_ref do semigroup multiplication. Final code certify action hằng bằng strict comparisons và dùng pi_0 P_0=pi_0 cho kỳ vọng chi phí; không epsilon, không đổi rule/metric. Các tests mới yêu cầu exact G_S=0.
- Không rerun pilot sau certificate. Timing/projection ở đây thuộc source pilot; core generator/V/fluid/posterior và heavy computations giữ nguyên. Chi phí bổ sung của certificate chưa benchmark trên full grid.
- Bốn pilot là exposed, không được nhận toàn bộ panel unseen. Future predictions ghi rõ các ID/h/age đã exposed. Chưa tạo predictions.json hoặc lock.json.
- Brief không đặt aggregate numeric PASS/FAIL threshold cho sign/slope/C5; scorer chỉ báo comparisons/counts và NOT_SPECIFIED_BY_DESIGN, không tự đặt ngưỡng.

## Danh sách đầy đủ 64 regime

Chi tiết mọi tham số/path/utilization/N/T_int/cost/reason ở `regimes.csv` và `regimes.json`.
32 agree / 32 disagree; 431 parameter-only draws; 0 held-out collisions; 0 ranking ties; 367 draws bị loại do tầng đã đủ. Không có nearly-empty regime.

| ID | Tầng | Planned status | Dự phóng CPU-s |
|---|---|---|---:|
| XCTMC_001 | agree | PLANNED | 1.057368 |
| XCTMC_002 | agree | PLANNED | 8.578402 |
| XCTMC_003 | agree | PLANNED | 266.437247 |
| XCTMC_004 | agree | PLANNED | 1.724818 |
| XCTMC_005 | agree | PLANNED | 0.131223 |
| XCTMC_006 | disagree | PLANNED | 5.337925 |
| XCTMC_007 | agree | PLANNED | 2.691449 |
| XCTMC_008 | agree | PLANNED | 2.301053 |
| XCTMC_009 | agree | PLANNED | 0.125009 |
| XCTMC_010 | agree | PLANNED | 5.952104 |
| XCTMC_011 | agree | PLANNED | 0.377415 |
| XCTMC_012 | agree | PLANNED | 0.462015 |
| XCTMC_013 | agree | PLANNED | 124.610784 |
| XCTMC_014 | agree | PLANNED | 0.623186 |
| XCTMC_015 | agree | PLANNED | 26.675575 |
| XCTMC_016 | agree | PLANNED | 1092.750450 |
| XCTMC_017 | agree | PLANNED | 75.452670 |
| XCTMC_018 | agree | PLANNED | 5.447612 |
| XCTMC_019 | agree | PLANNED | 0.028287 |
| XCTMC_020 | agree | PLANNED | 6.429416 |
| XCTMC_021 | agree | PLANNED | 0.375556 |
| XCTMC_022 | agree | PLANNED | 411.548226 |
| XCTMC_023 | disagree | PLANNED | 0.292985 |
| XCTMC_024 | agree | PLANNED | 0.015415 |
| XCTMC_025 | agree | PLANNED | 1.112843 |
| XCTMC_026 | agree | PLANNED | 20.751542 |
| XCTMC_027 | agree | PLANNED | 25.866087 |
| XCTMC_028 | agree | NOT_RUN | 9673.861362 |
| XCTMC_029 | agree | PLANNED | 2.150798 |
| XCTMC_030 | agree | PLANNED | 31.615365 |
| XCTMC_031 | agree | PLANNED | 0.434782 |
| XCTMC_032 | agree | PLANNED | 5.306042 |
| XCTMC_033 | agree | PLANNED | 36.632734 |
| XCTMC_034 | agree | PLANNED | 5.039117 |
| XCTMC_035 | disagree | PLANNED | 0.387635 |
| XCTMC_036 | disagree | PLANNED | 0.178246 |
| XCTMC_037 | disagree | PLANNED | 5.521726 |
| XCTMC_038 | disagree | PLANNED | 0.682695 |
| XCTMC_039 | disagree | PLANNED | 2.472059 |
| XCTMC_040 | disagree | PLANNED | 0.058428 |
| XCTMC_041 | disagree | PLANNED | 77.671527 |
| XCTMC_042 | disagree | PLANNED | 2.081469 |
| XCTMC_043 | disagree | PLANNED | 3.504146 |
| XCTMC_044 | disagree | PLANNED | 691.394702 |
| XCTMC_045 | disagree | PLANNED | 0.119810 |
| XCTMC_046 | disagree | PLANNED | 0.260435 |
| XCTMC_047 | disagree | PLANNED | 1068.096850 |
| XCTMC_048 | disagree | PLANNED | 2.392744 |
| XCTMC_049 | disagree | PLANNED | 0.136421 |
| XCTMC_050 | disagree | PLANNED | 0.209406 |
| XCTMC_051 | disagree | PLANNED | 143.032965 |
| XCTMC_052 | disagree | PLANNED | 0.070945 |
| XCTMC_053 | disagree | PLANNED | 850.864971 |
| XCTMC_054 | disagree | PLANNED | 0.699100 |
| XCTMC_055 | disagree | PLANNED | 7.956085 |
| XCTMC_056 | disagree | PLANNED | 66.124651 |
| XCTMC_057 | disagree | PLANNED | 0.315413 |
| XCTMC_058 | disagree | PLANNED | 812.852402 |
| XCTMC_059 | disagree | PLANNED | 2.300311 |
| XCTMC_060 | disagree | PLANNED | 1.776414 |
| XCTMC_061 | disagree | PLANNED | 2.054227 |
| XCTMC_062 | disagree | PLANNED | 0.146461 |
| XCTMC_063 | disagree | PLANNED | 9.617540 |
| XCTMC_064 | disagree | PLANNED | 81.126956 |

## Artifact

- Source: `experiments/letter/x_ctmc.py`; tests: `tests/test_x_ctmc.py`.
- Config/design: `design_snapshot.md`, `pilot_plan.json`, `regimes.json`, `regimes.csv`.
- Raw/timing: `pilot/*.json`, `pilot.json`, `pilot_console.log`, `pilot_source.py`.
- Validation: `pytest_after_certificate.log`, `verification_after_certificate.json`, `pilot_arithmetic_audit.json`, `legacy_equivalence.json`, `certificate_change.json`; các log/check trước đó được giữ.
- Không có biểu đồ, full predictions, lock, truth raw/receipt hay score output.

## Kết luận

Đã xác nhận implementation theo các controls, tương đương legacy và pilot 4/4. Các file nguồn cũ kiểm lại đều nguyên byte với HEAD. XFAIL theta>=1 còn cần tác giả/Claude xử lý trước khi nhận toàn bộ design sanity PASS. Chưa có bằng chứng từ truth/score cho X1/X1b/X3.
