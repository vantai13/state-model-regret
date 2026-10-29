# L3R.7 — kết quả thử cải tiến bộ tính stationary

Người phụ trách: **Doan Van Tai**. Các candidate ở experiments, chưa đưa vào src hoặc confirmation.

Giữ nguyên infinite queue, tham số plant, rounding, 80 chữ số và ngưỡng sai số law 1e-10/posterior 1e-8. Candidate02–04 dùng cách đánh giá certificate mới; không gọi đó là certificate code gốc.

| Candidate | Probe / máy | Kết quả | CPU(s) | Wall(s) | Peak RSS(MiB) | Law error upper |
|---|---|---|---:|---:|---:|---:|
|1|CAL_RATE_100_A / local WSL|COMPLETED |199.560|199.590|86.0|1.42e-32|
|2|CAL_RATE_1000_A / local WSL|UNRESOLVED ArithmeticError|1260.656|1260.709|98.3|—|
|5|CAL_RATE_100_A / local WSL|COMPLETED |19.902|19.926|71.2|1.42e-32|
|6|CAL_RATE_1000_A / GCP dt4n-research-01|COMPLETED |902.461|902.514|137.9|1.41e-32|
|7|CAL_RATE_1000_B / GCP dt4n-research-01|COMPLETED |329.601|329.654|108.9|2.45e-33|

Baseline medium: **806.568s**; candidate01 **199.590s**, tỉ số wall **4.04×** trong các attempt đã đo, không phải p95.
Candidate02 trước đó không chứng nhận được normalizer khác zero; giữ nguyên ERROR và không chạy03/04. Balanced05/06/07 là phiên bản đăng ký sau lỗi này, không thay nhãn hoặc ghi đè raw cũ.
Quantiles medium đối chiếu chính xác; posterior chỉ lưu và kiểm error bounds, chưa đối chiếu trực tiếp point posterior values.

Candidate05 medium wall ratio: **40.48×** so baseline cùng máy, một attempt mỗi phiên bản; không phải p95.
**633/633 tests PASS** local trước balanced profiles; cloud chạy riêng633tests trước hai probe lớn nếu thực thi. Gồm exact rational balance, dense reference, closed-form TV/tail, interval wrapping và corruption rejection. Các kiểm này không thay full cost/accuracy audit.

Bản gốc v2 chạy riêng, giữ cả CPU_LIMIT. Nếu một baseline chạm giới hạn thì thời gian hoàn tất thật chưa biết; không coi số ceiling là thời gian giải xong.

## Phạm vi đã xác nhận

- Đây là kiểm khả năng tính stationary marginal trên local/GCP như từng dòng. Không tính joint cost/gain/contrast của regime mới hoặc chấm hypothesis card.
- Không tạo n/root/CF, không tag v1.3.1, không thay môi trường của baseline đang chạy.
- Candidate hoàn tất vẫn cần adoption/coverage/full physical cost audit, cost-moment tails, S1 route/array conversion, D22 và dry-run B.
- Bound rất nhỏ ở bảng chỉ áp dụng stationary law; không phải bound sai số toàn bộ physical costs/gains hoặc bằng chứng hypothesis đúng.
- Chưa có timing p95 main/coarse-K/coarse-dt bundle, nên chưa thể ước lượng thời gian toàn confirmation hoặc chọn n.
- Tác giả đã bật GCP; agent không start/resize VM. Môi trường và source được khóa riêng. Không so tốc độ khác máy như thể là speedup do thuật toán.

## Artifact và lệnh

`candidate_metrics.csv`, `candidate_verification.json` ở cùng thư mục báo cáo này. Raw các attempt01,02,05,06,07 nếu đã thực thi;03/04 không chạy do02FAIL.

```bash
.venv/bin/python -m experiments.R3R_07_fast_stationary.run --prereg experiments/R3R_07_fast_stationary/prereg.json --out results/R3R_numerics/20261029_candidate_01
# Với i=02,03,04 đã thực thi, mỗi lệnh một thư mục mới:
.venv/bin/python -m experiments.R3R_07_fast_stationary.sparse_run --prereg experiments/R3R_07_fast_stationary/prereg_sparse_candidate_02.json --out results/R3R_numerics/20261029_candidate_02
.venv/bin/python -m experiments.R3R_07_fast_stationary.balanced_run --prereg experiments/R3R_07_fast_stationary/prereg_balanced_candidate_05.json --out results/R3R_numerics/20261029_candidate_05
# GCP controller chạy các balanced_run06/07 sau preflight633tests:
/home/ubuntu/state-model-regret-r3r7-20261029/venv/bin/python -m experiments.R3R_07_fast_stationary.cloud_pipeline --out /home/ubuntu/state-model-regret-r3r7-20261029
.venv/bin/python -m experiments.lessons.report_stationary_candidates
```
