# L3R.7 — full numerical audit 02

Người phụ trách: **Doan Van Tai**.

Trạng thái: **HOLD_NUMERICAL_AUDIT**. Integrity của artifact đã kiểm, không đồng
nghĩa numerical readiness hoặc hypothesis PASS.

| Mục | Kết quả |
|---|---:|
| Full tests trên GCP | 670 PASS |
| Legacy replay / stationary regression PASS | 3 / 6 |
| Global bundles base hoàn tất / đăng ký | 5 / 114 |
| Record chưa giải quyết | 1 |
| CPU đã đo, giây | 464.154668 |
| RSS mẫu lớn nhất, MiB | 165.312 |
| Mức số đã chọn | None |
| CF / n / root | 0 / chưa chốt / chưa cấp |

Sai số R1 là diagnostic làm mịn, tách khỏi arithmetic enclosures. Coverage chỉ
trên các designs hiệu chuẩn đã khai; không suy tỷ lệ lỗi toàn population.
Không đổi metric, ngưỡng, card, plant hoặc mở R09/R10.

Lệnh chạy: `python -m experiments.R3R_08_population_numerics.cloud_pipeline
--base /home/ubuntu/state-model-regret-l3r7-full-20261029/attempt02
--prereg experiments/R3R_08_population_numerics/prereg_02.json`. Pipeline chạy pytest trước rồi registered runner.

Raw: `results/R3R_population_numerics/20261029_02/`; logs/test XML: `../attempt02/`;
CSV tài nguyên: `metrics.csv`; metric hai phương pháp: `gains_calibration_only.csv`;
kiểm chứng/hash: `verification.json` và `../export02_verification.json`;
R1/coverage: `r_coverage.json`; cấu hình: `experiments/R3R_08_population_numerics/prereg_02.json`.
Không tạo biểu đồ. Phase4 vẫn HOLD.
