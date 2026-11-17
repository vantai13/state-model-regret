Đã hoàn tất triển khai, test và pilot local. Brief khớp byte với HEAD; không commit, SSH hoặc dùng mạng.

Các file mới:

- [trunc_n2.py](/home/vantai/state-model-regret/experiments/letter/trunc_n2.py): `pilot`, `run`, `compare`.
- [trunc_n2_gcp.sh](/home/vantai/state-model-regret/experiments/letter/trunc_n2_gcp.sh): script GCP, **chưa chạy**.
- [test_letter_trunc_n2.py](/home/vantai/state-model-regret/tests/test_letter_trunc_n2.py).

Kiểm chứng:

- `python3 -m pytest -q tests/test_letter_trunc_n2.py`: **21 PASS**.
- Tái lập 1×N: **5.830 numeric leaves**, max relative difference **0**, đạt ngưỡng `1e-12`.
- `bash -n`: PASS; manifest **5/5 OK**.
- **128/128 protected files** giữ nguyên SHA; `git diff --stat` rỗng.

Pilot duy nhất regime `Za7p5_u1-2_lA17-2_x-2_k1-20`, với 4 workers:

| Component | 1N CPU-s | 2N CPU-s | 2N/1N |
|---|---:|---:|---:|
| Chain V | 11,672873 | 15,651865 | 1,340875 |
| Prepare, không gồm V | 0,140286 | 0,159793 | 1,139053 |
| Tổng năm ages | 2,791477 | 4,472037 | 1,602032 |

Tổng: **14,605 → 20,284 CPU-s**; wall time **5,100 → 7,299 s**.

Dự phóng toàn bộ 27 regime ở 2N: **16.155,31 CPU-s**; critical path regime nặng nhất **3.585,36 s ≈ 59,76 phút**; peak RSS khoảng **304,35 MiB/process**. Khuyến nghị n2-standard-32: **32 workers**, timeout **3 giờ**. Đây là ước lượng từ một pilot nhẹ, chưa phải đo trên VM.

Lỗi ban đầu: thiếu thư mục pytest temporary và adapter truyền horizon dạng rational string vào `Chain.V`. Đã giữ artifacts lỗi, sửa adapter mới sang `Fraction`, rồi kiểm tra số học 1N đạt; không đổi tolerance.

[Báo cáo và đường dẫn artifacts](/home/vantai/state-model-regret/results/letter/trunc_n2/report.md), [metrics dự phóng](/home/vantai/state-model-regret/results/letter/trunc_n2/pilot/projection.json), [log test cuối](/home/vantai/state-model-regret/results/letter/trunc_n2/pytest_verified.log), [manifest](/home/vantai/state-model-regret/results/letter/trunc_n2/manifest.sha256).

Chưa chấm khác biệt khoa học pilot 2N–1N; chưa chạy full population hoặc tạo full-run `compare.json`/`compare.md`, nên chưa kết luận truncation PASS/FAIL.