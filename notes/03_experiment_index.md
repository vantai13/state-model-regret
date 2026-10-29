# Experiment index — evidence v1.2 và thiết kế population v1.3

Người phụ trách: **Doan Van Tai** · cập nhật 29/10/2026 (L3R.6).
[Bản hiện hành](../README.md) · [Phase 3R](phases/PHASE_3R.md) ·
[contract v1.3](01_definitions_v1_3.md). Kết quả A01/A04/A05 giữ
[contract v1.2](01_definitions_v1_2.md) và [protocol cũ](design/v1_2_protocol.md).

| Experiment | Câu hỏi | Tầng evidence | Trạng thái / điều kiện | Cấu hình / nơi quyết |
|---|---|---|---|---|
| A01 | dt nào làm sáu contrast ổn định, controls đúng zero? | E0/E1 numerical verification trong plant | **PASS**, dt=1/240 s (ref2), DL-053; giữ run01 FAIL/run02 INTERRUPTED | [Prereg](../experiments/A01_null_refinement/prereg.md), [report](../results/lessons/l3_4/report.md), [CSV](../results/A01/20261027_03/refinement.csv) |
| A04 | State/model repairs khác và tương tác thế nào trên lưới neo? | Discovery trong plant, không network evidence | **HOÀN TẤT KỸ THUẬT** DL-056;92/92 BOUNDED;P5 đứng,P2/P3/P6 không đứng | [Prereg](../experiments/A04_discovery/prereg.md), [note](lessons/L3.5_A04_note.md), [scores](../results/A04/20261027_01/card_scores.csv) |
| A05-F | Khóa H0/H1 và phép đánh giá nào trước held-out? | Freeze/provenance; kết quả confirmation báo riêng | **FROZEN** DL-058;12hệ số/model,369tests lịch sử;K5m=1/C1/PC4;A05-T ở dòng sau | [Prereg](../experiments/A05_freeze/prereg.md), [freeze](lessons/A05_F_preregistration.md), [report](../results/lessons/l3_6/freeze_report.md) |
| A05-T | H1 khác threshold null thế nào trên held-out? | Confirmation trong plant theo freeze | **ĐÃ CHẠY MỘT LẦN** DL-059–060: PC4 nội suy WEAKEN, ngoại suy FALSIFY; K5 DOES_NOT_STAND (R04); C1 STANDS; rescore PASS | [Decision](../experiments/A05_test/decision.json), [report](../results/lessons/l3_7/report.md), [verdict](../results/A05_test/20261028_01/verdict.json); R09/R10 niêm phong |
| V13-STEP1 | Ba prediction về chế độ sai của M0 có đứng trên discovery cũ? | Discovery/consistency | P(a)PASS;P(b)/P(c)FAIL, fallback DL-063 | [Report](../results/V13_step1/report.md) |
| V13-PILOT | Population có tín hiệu khả thi trên regime đã thử? | Discovery thích nghi | Tag explore-v13-pilot=a7435e9; branch không merge, chưa audit engine | [Discovery record](phases/PHASE_3R_discovery_record.md); raw chỉ trên tag/branch |
| R3R_01 | SUMMARY/raw, cấu hình trùng và exposure có khớp? | Verification dữ liệu đã lưu, không engine verification | L3R.1 kỹ thuật PASS;216ID/210cấu hình, E1–E7; không outcome mới | [Prereg](../experiments/R3R_01_recount/prereg.json), [report](../results/lessons/l3r_1/report.md), [CSV chỉ tham số](../results/R3R_01_recount/20261028_01/discovery_regimes.csv) |
| L3R.2/T07 | Population estimand, identity và D22 có đúng trên toy hữu hạn? | E0/theory + kiểm reference | 16 golden/439 full PASS, 500 laws/0 vi phạm, 5 mutant KILLED; chưa audit pilot | [T07](theory/T07_population_estimand.md), [spec](../experiments/lessons/l3r_2_spec.json), [report](../results/lessons/l3r_2/report.md) |
| R3R_02 / L3R.3 | Pilot có tính đúng estimand trong scope được kiểm? | Verification trong plant | Audit **HOLD**, evidence có giới hạn;467full/19oldtests/12mutants/19repro PASS; no CF | [Prereg](../experiments/R3R_02_audit/prereg.json), [code map](verification/l3r_3/code_map.md), [report](../results/lessons/l3r_3/report.md) |
| R3R_04 / L3R.4 | Design có cùng phù hợp dải nguồn ở bối cảnh DL008 không? | Formula verification + realism screen, chưa validation | **HOLD_UNSOURCED** cảMV/SH,a/b;216ID/210distinct;491full/18MCchecksPASS; labels commit trước overlay | [Envelope](realism/envelope_v1.json), [worksheet](realism/worksheet_v1.md), [labels](../results/lessons/l3r_4/screen/labels.csv), [report](../results/lessons/l3r_4/report.md) |
| R3R_05 / L3R.5 | Population/thước/schema và luật số đã khóa trước cards chưa? | Contract/provenance + parameter/toy verification | **LOCKED_WITH_DEFERRED**,tagcontract-v1.3→3d2359b;532full/41targetedPASS;khôngnewresearchoutcomes | [Contract](01_definitions_v1_3.md),[schema](design/regime_schema_v1_3.json),[receipt](phases/contract_v1_3.lock.json),[report](../results/lessons/l3r_5/report.md) |
| R3R_06 / L3R.6 | Discovery nói gì để vẽ vùng; card nào có thể sai/PASS? | Prediction cards + discovery tóm tắt có log, không evidence | **CARDS_FROZEN** 1414d92, receipt PASS; Hyp-MV/Hyp-SH primary, không secondary; 9/9 checks, 549 full/17 targeted PASS; không CF/engine | [Cards](phases/PHASE_3R_hypothesis_cards.md), [log](phases/PHASE_3R_forking_paths.md), [receipt](phases/PHASE_3R_hypothesis_cards.lock.json), [report](../results/lessons/l3r_6/report.md) |

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
đã carry nguyên văn luật K5 chưa bị bác ở thời điểm A04 (m=1); freeze hiện hành và
kết quả test sau đó xem hai dòng A05-F/A05-T, không dùng trạng thái A03 thay hiện tại.

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

L3.8 là tổng hợp quyết định, không phải run mới: [Gate REFORMULATE](phases/PHASE_3_gate.md),
[closeout](phases/PHASE_3_closeout.md), [audit](../results/lessons/l3_8/report.md), DL-061.
391 tests local PASS; hai mục closeout AI soạn ngôi “tôi” theo ủy quyền, ownership OPEN.
Phase4 thực thi HOLD tới P0-V10 và contract mới khóa; [proposal v1.3](01_definitions_v1_3_draft.md).
