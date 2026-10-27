# A04 — L3.5

Người phụ trách: **Doan Van Tai**. [Prereg](prereg.md) phải commit trước run;
receipt `prereg.lock.json` ở commit tiếp theo khóa nguồn/config/exposure.
Engine/card A01/A03 giữ nguyên. Không có CLI chọn ô/refinement/threshold mới.

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m experiments.A04_discovery.run --run-id 20261027_01 --allow-grid --workers 6
# Đọc validity.csv + validity_status.json; không mở cells.csv trước validity.
.venv/bin/python -m experiments.A04_discovery.score_card --run-dir results/A04/20261027_01
# Commit card_scores.csv/card_details.csv/card_scores.json trước lệnh dưới.
.venv/bin/python -m experiments.A04_discovery.discovery --run-dir results/A04/20261027_01
.venv/bin/python -m experiments.A04_discovery.plots --run-dir results/A04/20261027_01
```

Run ID phải mới: không ghi đè run cũ. Scorer không ghi đè evidence đã chấm.
Mọi rerun sau khi thấy discovery là replication/recomputation, không prereg mới.
`output_hashes.json` chứa hash inputs/raw/validity; score checkpoint khóa hash đó.
Hai review tay không thay human reader L8/P0-V10. `main_final.csv`/`controls_final.csv`
tách denominators; `margin_route_diagnostics.csv` không là feature cho A05.
