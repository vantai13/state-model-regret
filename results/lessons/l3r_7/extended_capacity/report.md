# L3R.7 — đo dài hơn để đánh giá máy local

Người phụ trách: **Doan Van Tai** · 29/10/2026 · baseline theo DL-080.
Prereg commit `7009bc9`. Giữ nguyên 3 đầu vào khoa học; giới hạn mỗi job: 1800 CPU-s, 2400 wall-s, 6 GiB RSS, 7 GiB address space; 1 worker.

Trạng thái: **LOCAL_BASELINE_PARTIAL_AFTER_INTERRUPTION**. Hoàn tất **1/3** probe mới; gộp với v1 là **4/6** stationary probes.

| Probe | Kết quả | CPU(s) | Wall(s) | Peak RSS(MiB) | Phase/lý do |
|---|---|---:|---:|---:|---|
|CAL_RATE_100_A|COMPLETED|806.161|806.568|350.684|mpmath_lu_completed / —|
|CAL_RATE_1000_A|UNRESOLVED|1801.000|1801.110|5217.500|numpy_roots_completed / CPU_LIMIT|
|CAL_RATE_1000_B|INTERRUPTED_UNVERIFIED|chưa biết|chưa biết|chưa biết|mpmath_lu_started / MISSING_FINAL_RECEIPT_AFTER_TURN_INTERRUPTION|

Tổng CPU chính xác: **chưa biết s**; CPU lower bound đã quan sát: **4422.711 s**. Peak RSS lớn nhất trong các receipt đầy đủ: **5217.5 MiB**.
Ca B không có final resource/result sau phiên bị ngắt. Last CPU sample1815.55s vượt ceiling1800s; không xác nhận finalCPU, peakRSS, exit reason hoặc budget enforcement của ca này. Không suy numerical PASS từ việc process đã dừng.

## Cách đọc kết quả

- Đây là mở rộng giới hạn tài nguyên sau khi v1 chạm CPU limit, theo ủy quyền của tác giả; không khai là có giới hạn này từ đầu.
- Giữ nguyên toàn bộ error/partial của v1. Không chạy lại những ca PASS để chọn timing thuận lợi.
- Chỉ tính stationary law, certificate, quantile và posterior error bounds; chưa tính joint cost, global accuracy hoặc p95 của một CF regime.
- Nếu memory limit: chỉ kết luận vượt resource budget local đã khai. VM GCP 32 GB có thêm RAM nhưng phải đo, audit và khóa environment riêng.
- Nếu CPU limit: GCP 8 vCPU chưa chắc nhanh hơn cho một job một thread; cần đo từng core và đánh giá thuật toán.
- Nếu certificate/root finding có lỗi: tăng RAM/CPU không tự sửa correctness; cần giữ kết quả và audit.
- Nếu tất cả complete: vẫn cần kiểm certificate, reuse v1 và full audit trước v1.3.1/n/root/CF.
- Tác giả đã bật GCP; API xác nhận RUNNING. Phiên này không start/create/resize VM; cloud profile có prereg và môi trường riêng.

## Lệnh và artifact

```bash
.venv/bin/python -m experiments.R3R_07_numerics.run --prereg experiments/R3R_07_numerics/prereg_extended_v2.json --out results/R3R_numerics/20261029_02
.venv/bin/python -m experiments.lessons.report_extended_capacity
```

CSV: `results/R3R_numerics/20261029_02/capacity_metrics.csv`.
JSON: `capacity_verification.json`, `summary.json`, từngprobe/resource/result/progress.
Log: `results/lessons/l3r_7/extended_capacity/run.log`.
Không cóCF/newseed/practicalnetworkvalidation; không sửa card/measure hoặctag đãkhóa.
