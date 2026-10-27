# Experiment index — contract v1.2

Người phụ trách: **Doan Van Tai** · cập nhật 27/10/2026.
[Bản hiện hành](../README.md) · [Phase 3](phases/PHASE_3.md) ·
[contract](01_definitions_v1_2.md) · [protocol](design/v1_2_protocol.md).

| Experiment | Câu hỏi | Tầng evidence | Trạng thái / điều kiện | Cấu hình / nơi quyết |
|---|---|---|---|---|
| A01 | dt nào làm sáu contrast ổn định, controls đúng zero? | E0/E1 numerical verification trong plant | **PASS**, dt=1/240 s (ref2), DL-053; giữ run01 FAIL/run02 INTERRUPTED | [Prereg](../experiments/A01_null_refinement/prereg.md), [report](../results/lessons/l3_4/report.md), [CSV](../results/A01/20261027_03/refinement.csv) |
| A04 | State/model repairs khác và tương tác thế nào trên lưới neo? | Discovery trong plant, không network evidence | **CHƯA CHẠY**; sau A01, V9 chưa đạt nên chờ | D18–D22; 38 main + controls; [DL-044](02_decision_log.md#dl-044--mở-phase-3-điều-kiện-còn-mở-và-bản-hiện-hành-2026-10-27) |
| A05-F | Khóa H0/H1 và phép đánh giá nào trước held-out? | Freeze/provenance, chưa là kết quả thực nghiệm | **CHƯA KHÓA**; sau discovery, nên có người đọc trước freeze | D25; chưa có card freeze được adopt |
| A05-T | H1 khác threshold null thế nào trên held-out? | Confirmation trong plant theo freeze | **CHƯA CHẠY**; sau A05-F | D25; R01–R12, không calibration/discovery |

**Tên có phạm vi:** các script `run_v1_1_a1.py`, `run_v1_1_a4.py`, `run_v1_1_a5.py`
là các bước A1/A4/A5 của quy trình dựng lưới v1.1, **không phải A01/A04/A05 của
Phase 3**. `results/lessons/v1_2/` chứa screen thiết kế đã có; không là outcome A04.
Phiên L3.1 Part 3 chỉ kiểm migration D; [output riêng](../results/lessons/l3_1/part3/report.md).

Output A01: [run03](../results/A01/20261027_03/manifest.json), [selection](../results/A01/20261027_03/selection.json).
Output A04/A05-F/A05-T: **chưa tạo**.
Mọi lần chạy ghi commit card/code, config/seed (hoặc deterministic), exposure và output.

L3.2: [engine thực nghiệm](../experiments/A00_engine/) đã kiểm toy/D-only, chờ T05
tác giả để promote. [Verification](../results/lessons/l3_2/report.md) không là outcome A01/A04.

A03/L3.3: [card](phases/PHASE_3_prediction_card.md) đã freeze (14sanity,4forecast,
1luật K5), [receipt](phases/PHASE_3_prediction_card.lock.json); engine/already_implied
read-back author-attested. Trước A01 phải verify card commit/SHA/receipt/tag. A05-F
carry nguyên văn luật K5 chưa bị bác (m=1); chưa H1/null/fit/split hoặc A05 freeze.

A01 đủ ref1/2/4/8/16, mọi cặp đạt; A04 vẫn phải kiểm riêng cặp1/120→1/240
trên từng ô. 336tests/11mutant PASS; verification không xác nhận continuum/network/RQ.
