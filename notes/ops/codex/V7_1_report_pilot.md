Đã triển khai và chạy pilot V7-1. **Verdict: NOT_EVALUABLE** — dừng đúng quy định khi dự toán vượt 20 phút local.

- **Compute thực đo:** 216,66 CPU-s / 216,67 wall-s. Dự toán toàn bộ: **48,38 phút** theo CPU metadata cũ; **210,36 phút** theo cách bảo thủ.
- **Kiểm chứng:** chạy `v7_1_rule pilot` và pytest; **15/15 tests PASS**. CTMC đạt **20/20** đối chiếu, sai số tương đối tối đa **1,44×10⁻¹⁵**. GÉANT khớp bitwise **3.600 decisions + 3.600 tie flags**.
- **AUC P1–P3, CIs, precision, Spearman và forecasts:** chưa chấm trên population đầy đủ. Independent dataset rescore chưa chạy; chưa tạo figure.
- **h\* range:** chưa xác định. Riêng CTMC pilot có **h\*=84,6622 s = 0,0399264 T_int**, chỉ đại diện **1/93 regimes**.

Code mới: [analysis](/home/vantai/state-model-regret/experiments/letter/v7_1_rule.py), [rescore độc lập](/home/vantai/state-model-regret/experiments/letter/v7_1_rescore.py), [tests](/home/vantai/state-model-regret/tests/test_letter_v7_1.py).

Kết quả và đường dẫn artifact nằm trong [báo cáo](/home/vantai/state-model-regret/results/letter/v7_1/REPORT_V7_1.md), [summary.json](/home/vantai/state-model-regret/results/letter/v7_1/summary.json), [pilot.log](/home/vantai/state-model-regret/results/letter/v7_1/pilot.log), [regime_scales.csv](/home/vantai/state-model-regret/results/letter/v7_1/regime_scales.csv) và [verification.json](/home/vantai/state-model-regret/results/letter/v7_1/verification.json).

**Điểm lệch cần báo:** raw GÉANT không chứa M0 fluid gaps nên phải tái tạo từ đúng seed/input cũ. File rescore được tạo theo mục 6 dù initial allowlist bỏ sót.

804 input hashes đã kiểm tra. Không sửa file cũ/card, không commit, không SSH. Phần còn lại cần Claude chuyển GCP theo brief.