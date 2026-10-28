# Phase 3 — Gate A: REFORMULATE

> 28/10/2026 · **Doan Van Tai** · contract-v1.2.
> Nhãn do tác giả chọn trực tiếp; claim/tổng hợp do AI soạn theo ủy quyền, DL-061.
> Không là human review hoặc author-attested Understanding.
> Nguồn §17–18: [lesson Part 1](../../results/lessons/l3_8/lesson_part1.txt);
> repo chưa có bản plan đầy đủ, xem [đối chiếu](../lessons/L3.8_evidence_review.md).

## 1. Validity (§17.1)

PASS bên dưới là kiểm kỹ thuật trên artifact/code/lịch sử repo, không phải human review
hoặc chứng minh được mọi hành động ngoài repo. [Kết quả kiểm hiện hành](../../results/lessons/l3_8/verification.json).

| ID | Trạng thái | Evidence |
|---|---|---|
| V3-1 Engine | PASS kỹ thuật | [L3.2](../../results/lessons/l3_2/report.md), [full-suite log](../../results/lessons/l3_8/tests.log) |
| V3-2 A01 | PASS | [L3.4](../../results/lessons/l3_4/report.md), giữ failed/partial runs |
| V3-3 dt, sai số số | PASS trong slot-model | [DL-053](../02_decision_log.md#dl-053--a01-pass-dt-cuối--1240-s-ref2-2026-10-27), [A04](../../results/A04/20261027_01/validity_status.json), [A05-T](../../results/A05_test/20261028_01/validity_status.json) |
| V3-4 Thứ tự commit | PASS | [Card lock](PHASE_3_prediction_card.lock.json), [freeze lock](../../experiments/A05_freeze/freeze.lock.json), [audit](../../results/lessons/l3_8/verification.json) |
| V3-5 Không đổi luật sau outcome | PASS theo nguồn/commit đã kiểm | [DL-044–060](../02_decision_log.md), [quyết định A05-T](../../experiments/A05_test/decision.json) |
| V3-6 Exposure | PASS về ghi nhận | [Register](../00_exposure_register.md), calibration/metadata trước test được công bố |
| V3-7 Card | PASS về chấm đủ | [A04 scores](../../results/A04/20261027_01/card_scores.csv), [A05-T verdict](../../results/A05_test/20261028_01/verdict.json) |
| V3-8 Prereg A05-F | PASS | [Prereg](../../experiments/A05_freeze/prereg.md), [DL-057–058](../02_decision_log.md) |
| V3-9 Held-out mở một lần | PASS theo hồ sơ repo | [Decision](../../experiments/A05_test/decision.json), [29 hashes](../../results/A05_test/20261028_01/output_hashes.json), không loại trừ run bị xóa ngoài hồ sơ |
| V3-10 Tái lập | PASS hồ sơ + chấm lại | [A04 manifest](../../results/A04/20261027_01/manifest.json), [A05-T manifest](../../results/A05_test/20261028_01/manifest.json), [rescore](../../results/lessons/l3_8/rescore.log) |
| V3-11 Provenance | PASS về khai báo | [Card](PHASE_3_prediction_card.md), [freeze](../lessons/A05_F_preregistration.md), [DL-059](../02_decision_log.md#dl-059--quyết-định-không-đảo-ngược-mở-a05-t-đúng-một-lần-2026-10-28), header file này |

## 2. Điều kiện quy trình (§17.2), không thay nhãn Gate A

| Điều kiện | Trạng thái / ảnh hưởng |
|---|---|
| V9 | WAIVED_BY_AUTHOR theo [DL-054](../02_decision_log.md); memo chưa gửi |
| P0-V10 / L8 | OPEN; **HOLD thực thi Phase 4** / Gate L còn điều kiện; [reader packet](../meetings/phase2_reader_packet.md) |
| DL-038, §1–2 closeout Phase 1/2 | OPEN ở phần tự viết; [Phase 1](PHASE_1_closeout.md), [Phase 2](PHASE_2_closeout.md) |
| X.3 #2 / T05 author-writing / Understanding | OPEN ở phần tác giả; [T05](../theory/T05_exact_engine.md); read-back ngoài repo đã attest không thay bài tự viết |
| A05-T / closeout Phase 3 | AI chạy theo ủy quyền, không có kỳ vọng tác giả trước run; hai mục closeout AI viết ngôi “tôi” theo yêu cầu mới, **ownership/Understanding OPEN** |

## 3. Outcome (§17.3)

- **O1:** A04 P5 đứng trên danh sách, P2/P3/P6 không đứng; [scores](../../results/A04/20261027_01/card_scores.csv).
- **O2:** PC4 nội suy WEAKEN: d≈0,247036<0,25 điểm % C_ref; [verdict](../../results/A05_test/20261028_01/verdict.json).
- **O3:** Ngoại suy h12 FALSIFY: d≈−0,141751; R09/R10 chưa mở; [report](../../results/lessons/l3_7/report.md).
- **O4:** K5 bị bác ở R04: G_M/C_ref≈0,527926%>0,5%; danh sách M19–M22 không bị sửa; [verdict](../../results/A05_test/20261028_01/verdict.json).
- **O5:** C1 đứng R05–R08, scope bốn ô, base rate cao; [giới hạn diễn giải](../lessons/L3.8_evidence_review.md).

## 4. Quyết định — DL-061

**Nhãn duy nhất: REFORMULATE**, tác giả chọn “REFORMULATE — chuẩn bị thiết kế mới”.

**Claim duy nhất:** Trong contract v1.2 một observation cố định mỗi ô ở dt 1/240 s,
estimand có điều kiện và các kết quả A04/A05-T chưa xác nhận một quy luật dự báo
khái quát, nên theo quyết định REFORMULATE của tác giả, contract mới phải định nghĩa
gain/Γ trung bình trên một phân phối observations trước khi thực thi Phase 4.

**Miền evidence:** 38 main A04 và 10 R đã mở; không outcome R09/R10/mạng thật.
[Evidence O1–O5 ở trên](../../results/A05_test/20261028_01/verdict.json),
[A04 scores](../../results/A04/20261027_01/card_scores.csv), [T01](../theory/T01_single_observation.md).
Không suy Γ vô nghĩa: thay đổi này là quyết định phạm vi của tác giả.
GO không đạt; validity không buộc HOLD; chưa đủ PIVOT/DROP; NARROW là phương án
giữ estimand mà tác giả không chọn; [bảng đối chiếu](../lessons/L3.8_evidence_review.md).

## 5. Bước tiếp theo

**Phase 4 thực thi HOLD tới P0-V10 và contract mới được khóa**, học được tiếp.
Việc đầu tiên: hoàn thiện [đề xuất v1.3](../01_definitions_v1_3_draft.md), chốt law/weights,
normalization, budget/split trước outcomes mới; chưa coi draft là contract.
Closeout được viết theo ủy quyền với exception DL-061, commit trước tag;
10 ô R đã mở là dữ liệu đã thấy, R09/R10 vẫn niêm phong.
