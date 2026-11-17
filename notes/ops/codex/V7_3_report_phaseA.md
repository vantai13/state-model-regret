Đã hoàn tất Phase A. **Không tính outcome đêm test, không commit, không sửa file cũ hoặc V7-1/V7-2.**

- **Dữ liệu:** 11.460 TM GÉANT, 10.773 hợp lệ; giữ **38 đêm train / 69 đêm test**, loại 13 ngày. URL, SHA256 và danh sách ngày ở [manifest](/home/vantai/state-model-regret/results/letter/v7_3/data_manifest.json).
- **Consolidation:** tắt **15/36 physical links**, vẫn connected. Capacity **23.128,607 Mbit/s**. Busiest train-mean night utilization: **Stay 36,424% / Switch 40,474%**.
- **Training:** 38 × 200 = **7.600 instances**. Rate Stay = **0**, Switch = **0,287966 Mbit**; do đó **ŝ = +0,287966 Mbit**. Cùng dấu pooled estimate: **4/38 = 10,53%**; 34 đêm bằng 0.
- **M0 tie share:** **100%**, fresh và stale, mọi horizon.
- **h/T_int tại 6h:** Stay không xác định 38/38 đêm. Switch có ba trace xác định: **72.070,01; 341.568,96; 215,33**; 35 trace còn lại không xác định. T_int dùng instance 0 mỗi đêm; estimate gần dt chưa đủ để claim continuous-time.
- **Pilot:** hai đêm train hoàn tất; M0/Hybrid/Stationary đều có regret và G_S bằng **0 Mbit·s**. **C_ref=0**, nên normalized metrics không xác định.
- **Compute projection:** **420.318 CPU-s ≈116,76 CPU-hours**, tương đương **5,84 giờ lý tưởng với 20 workers**; stress proxy **16,03 giờ**. Đây là ngoại suy local, chưa đo trên n2-standard-32.

Đã chạy `v7_3_run train`, `v7_3_run pilot`, pytest và checker: **25 tests PASS**, replay độc lập **PASS**. Lệnh đầy đủ và lỗi preflight đã sửa được giữ trong báo cáo/log.

Đề xuất chưa áp dụng: xem lại benefit/objective của consolidation vì Stay có zero cost trên train; khóa cách báo cáo C_ref=0 và kiểm tra độ phân giải T_int trước card.

File bàn giao:

- [Báo cáo đầy đủ](/home/vantai/state-model-regret/results/letter/v7_3/PHASE_A_REPORT.md), [configuration](/home/vantai/state-model-regret/results/letter/v7_3/train/configuration.json), [CSV training](/home/vantai/state-model-regret/results/letter/v7_3/train/night_statistics.csv), [pilot/projection](/home/vantai/state-model-regret/results/letter/v7_3/pilot/summary.json).
- [Runner](/home/vantai/state-model-regret/experiments/letter/v7_3_run.py), [tests](/home/vantai/state-model-regret/tests/test_letter_v7_3.py), [log training](/home/vantai/state-model-regret/results/letter/v7_3/train_execution.log), [log test](/home/vantai/state-model-regret/results/letter/v7_3/pytest_regression.log), [audit cuối](/home/vantai/state-model-regret/results/letter/v7_3/final_integrity.json).

Raw data nằm ngoài Git tại `/home/vantai/papers/data/sndlib/`. Chưa xác nhận hiệu quả trên test; Claude có thể đọc báo cáo training để viết card.