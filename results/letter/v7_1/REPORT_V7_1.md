# V7-1 — resource-stop pilot report

Người phụ trách: **Doan Van Tai**.

Verdict card: **NOT_EVALUABLE**. Chưa kiểm định dự đoán AUC(P2)>AUC(P1) trên cả hai dataset; không gán FAIL cho hypothesis từ một compute stop. Giữ nguyên card tại HEAD, threshold và inclusion rule; chưa sửa Table II/paper.

## Đã triển khai và chạy

Đã tạo `experiments/letter/v7_1_rule.py`, `experiments/letter/v7_1_rescore.py`, `tests/test_letter_v7_1.py`. Có code extraction, P1–P3/Y, AUC Mann–Whitney (ties=1/2), cluster-bootstrap 2.000 draws/seed 20261118, precision, per-regime onset Spearman, h*, candidate figure và rescore độc lập dùng standard-library bisect. **Full analysis chưa chạy**; triển khai không đồng nghĩa kết quả khoa học đã được xác nhận.

Command đã chạy:

```bash
source .venv/bin/activate && source experiments/explore_ctmc/env.sh
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider tests/test_letter_v7_1.py --basetemp=/tmp/v7_1_pytest_preflight
PYTHONDONTWRITEBYTECODE=1 python -u -m experiments.letter.v7_1_rule pilot
PYTHONDONTWRITEBYTECODE=1 python -m experiments.letter.v7_1_rule report-pilot
```

Preflight: 12 tests PASS, 2.58 s (`pytest_preflight.log`). Kiểm tra cuối sau bổ sung resource-stop guards được ghi riêng ở `pytest_final.log`; không dùng log này để suy full analysis PASS.

## Compute và lý do dừng

- CTMC pilot: regime lớn nhất `Za7p5_u3-2_lA31-4_x1-3_k2` (N_A=3159, N_B=9518), đủ 5 saved ages; CPU 181.102615421 s, wall 181.107848308 s.
- GÉANT pilot: `results/letter/e4/raw/G2_r90_b6_s1_chunk01.npz`, seed 3000001, chunk 1, N=50/K=128, đủ 3 ages × 6 horizons. Đây là chunk có saved CPU lớn nhất trong 340 chunks. CPU 35.557773161 s, wall 35.558594517 s.
- Pilot tổng: **216.660388582 CPU-s / 216.666442825 wall-s** (3.611107 phút), nguồn `pilot.json`.
- Projection bảo thủ = CTMC pilot wall × sparse-generator work ratio 2.934312469 + GÉANT worst-chunk wall × 340 = **12621.349153 s (210.355819 phút)**. Đây là bound scheduling bảo thủ, không actual full-run duration.
- Cross-check scheduling dùng tỷ số CPU full-job đã lưu của toàn bộ chunks / chunk pilot = 66.695292652, nhân M0-only chunk wall thực đo: **2903.017885 s (48.383631 phút)** cho toàn bộ, vẫn vượt **1.200 s / 20 phút**. Ước lượng này không CI hoặc guarantee. Nguồn metadata `results/letter/e4/raw/*.json`, `e4b/raw/*.json`; script và các số trong `summary.json.compute`.

Theo brief: dừng sau pilot để Claude chuyển GCP. Không chạy phần population còn lại, không SSH, không commit.

## Arrays, nguồn và đơn vị

**CTMC:** `results/letter/w1b/raw/*.json` có regrets và saturation decision probabilities, không có gap arrays. Tái tạo `ctmc.m0_gap(...,[inf])` trên đúng truncated state spaces. Artifact `extracted/CTMC_Za7p5_u3-2_lA31-4_x1-3_k2.npz`: `gap_A`, `gap_B` (uncorrected Switch−Stay network gap là tổng hai thành phần), `pi_A`, `pi_B`; `old_A_<age>`, `old_B_<age>` là conditional expectation full old (backlog,mode), dùng `posterior_full=exp(Q_Stay*tau)` ở chênh tuổi tăng dần. Joint law của hai queue là tích hai pi. Absolute value được lấy **sau** conditional expectation. M̂ xét mọi truncated states; Q90=weighted inverse CDF của |gap_A+gap_B|, mass fresh=1/2, mỗi stale age=1/10. Fresh lặp theo age và pooling hai sides có cùng weighting. Gap units packet·s, s units packet/backlog-cost rate; h/T_int/h* tính bằng giây của simulator. Không gọi CTMC truncated là infinite-state exact.

**GÉANT:** NPZ E4/E4b lưu `V[50,2,6]` (plant Monte Carlo cost), `decisions[50,20,2,3,6]`, `tie_flags`, `h`, `tau`, grids và instance IDs; **V không phải M0 fluid gap**. Tái tạo đúng E4 `instances`, per-instance/posterior seeds, K=128, gọi `twin_costs`, mean posterior cost rồi trừ Switch−Stay; không gọi M1 decision/evaluation truth. Artifact `extracted/GEANT_e4_G2_r90_b6_s1_01.npz`: `fresh_gap[50,6]`, `stale_gap[50,3,6]`, `h`, `tau`, `instance_id`. Chưa đủ 10 chunks/500 fresh instances để tính **regime** M̂/Q90. Full-analysis code sẽ dùng largest saved h=30T_int, empirical max fresh, Q90 pool fresh ba lần và stale ba ages một lần (equal side mass; inverse CDF, không linear interpolation). ŝ=training `r_a[1].mean-r_a[0].mean`, T_int/dt từ `results/ext_validity/ev_te/train/*.json`; units gap=Mb·s, ŝ=Mb. Seconds dùng convention fast switching rate 1/s, không phải calibration theo deployment thật.

Pilot replay: **20/20 CTMC scalar comparisons PASS**, max relative error **1.44328993201e-15**, threshold ≤1e−9. Các scalar kiểm r/T_int/variance của bốn chains, s/T_int toàn regime, fresh F_new và năm stale F_old (nguồn `evaluations[*].asymptotic` trong W1b raw). Gap scale mới không có saved scalar để so trực tiếp; không tuyên bố đã có raw scalar-gap replay. GÉANT: **3,600 decisions + 3,600 tie flags khớp bitwise**, M0 và Hybrid-i, fresh/stale, mọi age/horizon; grids/instance IDs cũng khớp, NPZ SHA khớp metadata. Xem `extraction_checks.json`, JSON/NPZ trong `extracted/` và test gap extraction trên một regime cũ khác.

## Kết quả hiện có và chưa có

| Đại lượng | CTMC pilot duy nhất | Population đầy đủ |
|---|---:|---|
| M̂ (packet·s) | 155545971.857 | Chưa tính |
| Q90 (packet·s) | 14245.6584495 | Chưa tính |
| s (packet) | 168.264591006 | Chưa tổng hợp |
| T_int (s) | 2120.45918616 | Chưa tổng hợp |
| h*=Q90/|s| (s) | **84.6622475018** | **Range chưa xác định** |
| h*/T_int | **0.0399263744638** | **Range chưa xác định** |
| AUC P1/P2/P3, CIs và P2−P1 | Không chấm pilot subset | **NOT_RUN** |
| Precision P2≥1 / regime Spearman | Không chấm pilot subset | **NOT_RUN** |

Nguồn toàn bộ số scale: `extracted/CTMC_Za7p5_u3-2_lA31-4_x1-3_k2.json:scale`, `regime_scales.csv` (scope `PILOT_ONLY_1_OF_93_REGIMES`). Không xem đây là h* range của 93 regimes hoặc 2-seed GÉANT. `summary.json` để null cho metrics chưa đo, không điền 0.

Forecast AUC(P3) nằm giữa P1/P2 và precision≥0,9 trên GÉANT: **NOT_EVALUABLE**. Không tạo `cells.csv`, `regime_onsets.csv`, `fig_rule.pdf/png`, `figure_bins.csv` hoặc `rescore.json` vì chưa có full-population scale table; không tạo figure từ một pilot rồi trình bày như population card. Rescore script đã có và toy AUC đã kiểm; **independent rescore trên dataset chưa chạy**. Bootstrap giữ regime block, hai GÉANT seeds đi cùng; Spearman dự kiến báo từng seed, onset cần mọi age và mọi saved h sau đều pass, giữ right-censoring.

## Nguyên nhân, giới hạn và handoff

Compute bottleneck là phải tái tạo posterior M0 predictor do fluid gaps không được lưu, cộng sparse semigroup ở CTMC state space lớn. Dùng V của plant thay gap hoặc bỏ regimes/ages/horizons sẽ đổi đại lượng và population, nên không làm. Đã dùng cách nhẹ: chỉ tính gap vector (không truth V), tiến dần giữa CTMC ages, batch fresh fluid costs, và reuse pilot artifacts. Cross-check scheduling vẫn vượt cap; không tiếp tục local hoặc tune criterion để cứu tính khả thi.

Claude có thể chuyển code, nguyên `pilot.json`/`extracted/`, dữ liệu nguồn và card sang GCP. Full command hỗ trợ `run --compute-location gcp`; dùng **output directory mới** và copy pilot/extracted vào đó để giữ báo cáo pilot này, ví dụ `results/letter/v7_1/full/`. Chạy full analysis, sau đó `python -m experiments.letter.v7_1_rescore --out <full-output>`; phải khớp AUC≤1e−12. Đây là hướng dẫn handoff, **không phải lệnh đã chạy hay yêu cầu bật VM**. Thực hiện trên GCP do Claude phụ trách theo brief.

## Files và deviations

- `summary.json`, `REPORT_V7_1.md`: trạng thái stop, counts, timings, metrics chưa chạy và forecast chưa chấm.
- `pilot.json`, `pilot.log`, `extraction_checks.json`, `regime_scales.csv`, `extracted/*.json/npz`: pilot thật, arrays, replay checks và units/source.
- `input_manifest.json`: SHA256 snapshot sau pilot, trước full score; **không gọi đây là lock trước pilot**. Brief/card đã đối chiếu byte với HEAD. Full code tiếp tục snapshot và verify tất cả inputs quanh analysis.
- Tests/log: `tests/test_letter_v7_1.py`, `pytest_preflight.log`, `pytest_final.log` sau kiểm tra cuối.
- Deviations cần báo: fluid gaps vắng trong E4/E4b raw nên phải tái tạo đúng original predictor inputs; tạo thêm `v7_1_rescore.py` đúng mục 6 dù initial allowlist bỏ sót. Việc dừng sau pilot là nhánh được brief yêu cầu khi vượt 20 phút.

Không sửa file có từ đầu/card/paper, không chạm V7-2/V7-3, không commit, không SSH. Card vẫn là post-hoc finite-panel analysis; không novelty/Understanding/author-self claim.
