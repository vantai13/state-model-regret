# Experiment index — contract v1.2

Người phụ trách: **Doan Van Tai** · cập nhật 28/10/2026.
[Bản hiện hành](../README.md) · [Phase 3](phases/PHASE_3.md) ·
[contract](01_definitions_v1_2.md) · [protocol](design/v1_2_protocol.md).

| Experiment | Câu hỏi | Tầng evidence | Trạng thái / điều kiện | Cấu hình / nơi quyết |
|---|---|---|---|---|
| A01 | dt nào làm sáu contrast ổn định, controls đúng zero? | E0/E1 numerical verification trong plant | **PASS**, dt=1/240 s (ref2), DL-053; giữ run01 FAIL/run02 INTERRUPTED | [Prereg](../experiments/A01_null_refinement/prereg.md), [report](../results/lessons/l3_4/report.md), [CSV](../results/A01/20261027_03/refinement.csv) |
| A04 | State/model repairs khác và tương tác thế nào trên lưới neo? | Discovery trong plant, không network evidence | **HOÀN TẤT KỸ THUẬT** DL-056;92/92 BOUNDED;P5 đứng,P2/P3/P6 không đứng | [Prereg](../experiments/A04_discovery/prereg.md), [note](lessons/L3.5_A04_note.md), [scores](../results/A04/20261027_01/card_scores.csv) |
| A05-F | Khóa H0/H1 và phép đánh giá nào trước held-out? | Freeze/provenance, chưa là kết quả thực nghiệm | **FROZEN** DL-058;12hệ số/model,369tests;K5m=1/C1/PC4;chưa A05-T | [Prereg](../experiments/A05_freeze/prereg.md), [freeze](lessons/A05_F_preregistration.md), [report](../results/lessons/l3_6/freeze_report.md) |
| A05-T | H1 khác threshold null thế nào trên held-out? | Confirmation trong plant theo freeze | **ĐÃ CHẠY MỘT LẦN** DL-059–060: PC4 nội suy WEAKEN, ngoại suy FALSIFY; K5 DOES_NOT_STAND (R04); C1 STANDS; rescore PASS | [Decision](../experiments/A05_test/decision.json), [report](../results/lessons/l3_7/report.md), [verdict](../results/A05_test/20261028_01/verdict.json); R09/R10 niêm phong |

**Tên có phạm vi:** các script `run_v1_1_a1.py`, `run_v1_1_a4.py`, `run_v1_1_a5.py`
là các bước A1/A4/A5 của quy trình dựng lưới v1.1, **không phải A01/A04/A05 của
Phase 3**. `results/lessons/v1_2/` chứa screen thiết kế đã có; không là outcome A04.
Phiên L3.1 Part 3 chỉ kiểm migration D; [output riêng](../results/lessons/l3_1/part3/report.md).

Output A01: [run03](../results/A01/20261027_03/manifest.json), [selection](../results/A01/20261027_03/selection.json).
Output A04: [run01](../results/A04/20261027_01/manifest.json), [report](../results/lessons/l3_5/report.md).
A05-F: [theta](../results/A05_F/20261028_01/theta.json), [predictions](../experiments/A05_freeze/predictions_heldout.json), [discrimination](../experiments/A05_freeze/discrimination.json).
Output A05-T: [run](../results/A05_test/20261028_01/), [diagnostics](../results/A05_test/20261028_01/diagnostics.json), [claim sheet](lessons/A05_T_claim_sheet.md).
Mọi lần chạy ghi commit card/code, config/seed (hoặc deterministic), exposure và output.

L3.2: [engine thực nghiệm](../experiments/A00_engine/) đã kiểm toy/D-only, chờ T05
tác giả để promote. [Verification](../results/lessons/l3_2/report.md) không là outcome A01/A04.

A03/L3.3: [card](phases/PHASE_3_prediction_card.md) đã freeze (14sanity,4forecast,
1luật K5), [receipt](phases/PHASE_3_prediction_card.lock.json); engine/already_implied
read-back author-attested. Trước A01 phải verify card commit/SHA/receipt/tag. A05-F
carry nguyên văn luật K5 chưa bị bác (m=1); chưa H1/null/fit/split hoặc A05 freeze.

A01 đủ ref1/2/4/8/16, mọi cặp đạt; A04 vẫn phải kiểm riêng cặp1/120→1/240
trên từng ô. 336tests/11mutant PASS; verification không xác nhận continuum/network/RQ.

DL-054 thay điều kiện chờ memo của DL-044 bằng waiver do tác giả yêu cầu; không
ghi V9 human-fulfilled. [Review tiếp nhận](reviews/2026-10-27_pre_A04/intake.md)
chỉ là input tham khảo, không phải GVHD đã kiểm A01. Các đề xuất mới cần được
chốt trong prereg; không tự thay card, metric, ngưỡng hoặc mở held-out.


L3.6 đã hoàn tất kỹ thuật theo [completion](phases/A05_F_completion.json).
Source A05-F giữ nguyên sau prediction checkpoint; A05-T runner nên ở thư mục
riêng và phải kiểm frozen receipt cùng actual planned IDs trước khi dựng D/cost.
Không mở R09/R10 để xem thử: D của nhóm đã thấp hơn margin trước outcomes.
