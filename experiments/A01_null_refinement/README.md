# A01 — Doan Van Tai

Đọc [prereg](prereg.md); runner kiểm A03 và receipt A01 trước khi dựng D.
Hai commit riêng cho prereg và receipt; không ghi commit hash vào chính file của nó.
Chạy từ repo root sau khi đã commit source/config:

```bash
.venv/bin/python -u -m experiments.A01_null_refinement.run --run-id <unique-id> --allow-grid --workers 6
.venv/bin/python -m experiments.A01_null_refinement.selection results/A01/<unique-id>/refinement.csv
```

Part0 chỉ xuất p_sw; PartA C1–C6; chỉ khi controls PASS mới chạy PartB đủ 15 mức.
Float cost dùng longdouble từ đầu; giữ nguyên budget ref≤16, εE=.005, tol=.0025.
Mỗi JSON calibration lưu nominal và cận số riêng; CSV có e_num/unresolved/action;
rho/Richardson ở diagnostics CSV, không tham gia chọn dt. Không Monte Carlo/CI.
Control fail dừng; refinement fail HOLD. Không chạy A04, không dựng D held-out.
Engine vẫn ở experiments theo tình trạng T05; author read-back đã author-attested.
