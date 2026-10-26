# State × Model — giá trị cải thiện quyết định routing

Tác giả: **Doan Van Tai**.

**Mỗi lần tìm hoặc kiểm paper:** mở [quy tắc + checklist 7 bước](notes/literature/search_protocol.md).
**Hỏi → Tìm → Kiểm → Duyệt → Đọc → Ghi → Dừng**; [log các lượt thực chạy](notes/literature/search_log.md).

**Trạng thái 23/10/2026: Phase 1 đóng — GO có điều kiện sang Phase 3.** Contract khóa tại tag **`contract-v1.2`**. [Lưới v1.2](notes/design/grid_v1_2.md) ACCEPTED: 38 ô chính được neo theo ranh giới quyết định (oracle chọn Switch khoảng 30% hoặc 70%), 12 ô held-out, 6 ô kiểm âm, 2 đầu dò; mọi ô ổn định tới dt/4 và trong budget. Calibration A01: M01, M09, M22. Sáu kiểm nhất quán PASS, **193/193 tests PASS**. Chưa tính contrast hay regret ở ô nào. [Closeout](notes/phases/PHASE_1_closeout.md) · [contract v1.2](notes/01_definitions_v1_2.md) · [claim boundary](notes/01_claim_boundary_v1_2.md) · [DL-038, DL-039](notes/02_decision_log.md) · [thử nghiệm thiết kế](notes/explore/reformulate_grid_report.md).

Điều kiện còn mở: HOLD Phase 4 tới khi có người đọc độc lập (P0-V10); heads-up và memo GVHD **chưa gửi** (V9), nên gửi trước A04; lý do và câu chữ v1.2 do AI soạn, tác giả chưa tự viết lại. V1/V8/P0-V3/P0-V11 author-attested. G1 giữ nguyên. Các đoạn dưới là lịch sử, gồm trạng thái HOLD trước đó của lưới v1.1 (B4 rejected).

**L2.1–L2.3, cập nhật 24/10/2026:** đã lưu bộ literature Part A, proof T03 v2,
code tái lập và toàn bộ output toy. **21.952 toy**, I1–I6 không vi phạm;
**17/17** kiểm P11 và **202/202** tests toàn repo PASS.
[Báo cáo, checklist, commands và output](results/lessons/part_a/report.md) ·
[Literature index](notes/literature/README.md) ·
[Prior boundary](notes/literature/prior_boundary.md).
Formal Part A **HOLD**: forecasts AI-assisted đã exposed trước commit,
L-self/proof kín sách/đọc lại và review người thật chưa có record; B82/MAB11 còn
hạn chế full-text. Đây là verification toy, chưa chạy contrast lưới Phase3,
chưa freeze L3.3, không nâng G1 hoặc mở HOLD Phase4.

**Paper đang dùng:** [Excel và tiến độ đọc](papers/paper_comparison.xlsx)
· [Thư viện và hướng dẫn](papers/README.md). PDF lưu cục bộ, không đưa vào Git.

**L2.5 Part1, 26/10/2026:** đã lưu [note/bảng dịch stale state và đính chính lesson](notes/literature/state_staleness.md),
[P04 journal15trang](notes/literature/papers/P04.md), code/CSV minh họa và log.
22kiểm PASS: cùng10yêu cầu, blocked T1/T5/T10/round-robin =0/1/4/1;
T6=0 cho thấy toy hữu hạn không đơn điệu theo T. Đây không là replication P04
hoặc lưới Phase3. Part2 và L-self chưa thực hiện; G1/contract/Gate giữ nguyên.

**L2.4 Part2–3, 25/10/2026:** đã lưu [bản đồ NDT, pipeline, metric và giới hạn claim](notes/literature/ndt_landscape.md),
notes NDT1/P05/P10 và snowball thật (15 references,100 citing titles;3 đề xuất chưa duyệt).
Kiểm625 tổ hợp cost/tie PASS; đây là ví dụ minh họa, chưa chạy lưới Phase3.
Mức đọc là AI-only; Gate/L-self của tác giả chưa được xác nhận.

Các record bên dưới là lịch sử của Phase0/L1.2–L1.8 và mốc2. [Mốc2](notes/design/decisions_v1_1_m2.md) đã chốt trước candidate calculations; [report mốc2](notes/verification/v1_1_m2/README.md) ghi2/10 certificates của prototype cũ, đã được PhầnA thay thế. Lưới v1 cũ có13ô Stay áp đảo, cả3calibration bị invalid, vẫn HOLD A01/A04; tag v1 và output lịch sử giữ nguyên. Các lựa chọn §11 đã adopted theoủy quyền, không còn chờ từng quyết định kỹ thuật. Contract/claim boundary v1.1 vẫn là **draft cập nhật**, vì B4 không đạt.

Main RQ (nguyên văn Final Review cập nhật 06/10/2026):
> For load-changing routing actions, how do improvements in current-state information and action-response model fidelity differ and interact in their effect on expected decision regret?

Record lịch sử 22/10/2026: Phase 1 từng ghi hoàn tất kỹ thuật có điều kiện tại [snapshot contract-v1](https://github.com/vantai13/state-model-regret/blob/6bb631f9181cc06bfade9d71e54ad57ca3bbb284/notes/phases/PHASE_1_closeout.md). Contract/grid v1 lưu tại [definitions v1](notes/01_definitions_v1.md), [brief v1](notes/00_research_brief_v1.md), [grid/protocol](notes/design/grid_v1.md). Record này đã bị trạng thái HOLD ở đầu README thay thế. **G1/candidate gap** giữ nguyên; **HOLD Phase4 tới khi P0-V10 đạt**. P0-V3/V11, human feedback và final grid Δt A01 còn pending. V0 giữ làm snapshot lịch sử.
L0.1: **SCIENTIFIC/UNDERSTANDING PASS — PRACTICAL PENDING**; heads-up chưa gửi.
L0.2: đã thêm [RQ card v0](notes/lessons/L0.2_rq_card.md) ngày 08/10/2026; phần diễn giải chờ tác giả xác nhận, read-back chưa làm; V3/V11 còn mở và được mang sang theo phương án B.
Contract v0: [D1–D25, quyền thông tin, estimand, repairs, scope và năm sửa đổi DL-010](notes/01_definitions.md), bản kỹ thuật đóng băng tại **`contract-v0`**. Các nhãn DRAFT/OPEN giữ bên trong snapshot; tự kiểm chưa hoàn thành. Quyết định phase tại **`phase-0-closeout`**.
[T00 — timescale sanity](notes/theory/T00_timescale_sanity.md): đã cập nhật phương án A, giữ cả neo (a) ms/datacenter và (b) polling/edge; trục tổng tuổi/delay 5 ms–30 s. **10 test timescale đạt**, ma trận 40 ô khớp; AoI prototype chỉ đối chiếu. Đây là kiểm fluid có điều kiện; chưa chứng minh practical gain.
[L0.5 — phân loại legacy](legacy/INDEX.md): đã bổ sung 21 dòng phân loại và 10 giả định không mang sang; bài tác giả tự kiểm 5 dòng còn chờ. Khung package `smr` đã cài editable và **11 test đạt** (10 timescale + 1 smoke).
File 8: đã thêm khung [L0.3 — objects](notes/lessons/L0.3_objects.md), [L0.4 — estimand](notes/lessons/L0.4_estimand.md), [L0.5 — legacy](notes/lessons/L0.5_legacy.md), [L0.6 — scope](notes/lessons/L0.6_scope.md), [L0.7 — review](notes/lessons/L0.7_review.md). MẪU và bài chưa làm được ghi riêng; chưa có đủ understanding artifacts hoặc record người đọc độc lập. V3/V10/V11 còn mở; File 9 đã đóng theo B và ghi rõ điều kiện/mốc xử lý.
[Ownership Review — phần đã chọn và việc chưa hoàn thành](notes/PHASE_0_ownership_review.md): đã nêu chọn B2 và domain hai neo; self-explanation, tính tay, review và liên hệ GVHD còn Pending; formal closeout đã ghi B có điều kiện.
Review chuyển phase 08/10 ([DL-010](notes/02_decision_log.md#dl-010), review kỹ thuật tự động): **GO WITH CAUTION**; năm sửa đổi đã áp, bảo toàn/Jensen được tái lập bằng [script hữu hạn](notes/verification/verify_dl010.py). [Closeout §6](notes/phases/PHASE_0_closeout.md) ghi B, **V3/V10/V11 còn mở**; không phải GVHD duyệt.
[Inventory](notes/00_evidence_inventory.md) · [Exposure](notes/00_exposure_register.md) · [Claim boundary](notes/01_claim_boundary_v0.md).
[History](notes/00_history.md) · [Archive index](legacy/INDEX.md) · [Closeout](notes/lessons/L0.1_CLOSEOUT.md).
[Kết quả và nguồn kiểm chứng](notes/verification/2026-10-07_report.md) · [Cách tái kiểm](notes/verification/README.md).
L1.2 (09/10/2026): đã thực thi hai phần lesson hàng đợi; **11/11 test lesson, 22/22 test toàn repo đạt**. Vét cạn **5.832 cấu hình**, **2.048** không idle, **0 vi phạm**; bốn mutant bị 5/3/8/5 test phát hiện. [Experiment card](notes/lessons/L1.2_experiment_card.md) · [Báo cáo, bảng từng slot và kết quả đo](notes/verification/l1_2/report.md). Đây là verification toy plant; golden lấy từ tài liệu được cung cấp, V3/V10/V11 và G1 giữ nguyên.
L1.3 (21/10/2026): **9/9 test theo tài liệu, 20/20 test hai lesson, 3/3 kiểm bổ sung và 34/34 toàn repo đạt**. Sinh đúng bốn state, mỗi state 1/4; oracle L=6,25, luôn Stay R=1,125, luôn Switch R=0,875 packet·slot. Cả năm mutant bị bắt; M5 lọt 8 test đầu và bị test bất đối xứng chặn. EV-22 được ghi nhãn ví dụ sổ sách theo audit cấu hình trích. [Experiment card](notes/lessons/L1.3_experiment_card.md) · [Báo cáo, số liệu, log và biểu đồ](notes/verification/l1_3/report.md). Golden bổ sung H=3 có một lỗi dự đoán đã sửa và giữ log preflight; G1/V3/V10/V11 chưa đổi.
L1.4 (21/10/2026): **12/12 test lesson, 32/32 test ba lesson và 48/48 toàn repo đạt**. Lưới 1.156 và 9.604 cấu hình có 0 vi phạm ba tính chất; kiểm thêm đủ 8 pattern. G_S=1,125,G_M=0,25,Γ=−0,25 packet·slot; model repair làm hại 1/2 tổng xác suất episode dù gain trung bình dương. Năm mutant bị bắt; lỗi đổi nhãn S/M lọt 11 test đầu và bị golden bất đối xứng chặn. [Experiment card](notes/lessons/L1.4_experiment_card.md) · [Báo cáo, CSV, log, biểu đồ](notes/verification/l1_4/report.md). Dự đoán của bốn ô cho sẵn; chưa implement belief/model L1.6, G1 và các gate giữ nguyên.
L1.5 (21/10/2026): **11/11 test lesson, 43/43 bốn lesson và 61/61 toàn repo đạt**. F5 khớp 16 cặp chuẩn và 81 cặp lưới; 12.288 cấu hình belief có 0 vi phạm mean-zero. I_Δ=(1/2,−1/2,0,0), mean=0 nhưng E|I_Δ|=1/4. Năm mutant bị bắt; checker độc lập phát hiện P4 bỏ trọng số mà checker dùng chung helper bỏ sót ở test mọi belief. Thêm phản ví dụ cho thấy mean-zero chưa chứng nhận belief đúng. [Card](notes/lessons/L1.5_experiment_card.md) · [Spec làm việc cho contract-v1](notes/lessons/L1.5_identity_diagnostic_spec.md) · [Báo cáo/CSV/log/hình](notes/verification/l1_5/report.md). Chưa fit H0/H1, kiểm held-out hoặc xác nhận posterior S0; G1 và các gate giữ nguyên.
Understanding/judgment được tác giả xác nhận ngày 07/10/2026; chưa phải GVHD phê duyệt hướng mới.

L1.6 A–D (22/10/2026): **16/16 test lesson, 59/59 năm lesson, 3/3 kiểm bổ sung và 80/80 toàn repo đạt**. Belief/M0 sinh từ history và tái lập bảng L1.4–L1.5; 864 matched-prior cases có 0 vi phạm, 576 wrong-prior cases có đúng 5 G_M âm. 6.696 cặp state/action thoả Jensen và idle identity. GS=1,125 tách theo thứ tự thành freshness0,375 + mode visibility0,75; chưa là practical telemetry gain. [Card](notes/lessons/L1.6_experiment_card.md) · [Spec S0/M0](notes/lessons/L1.6_belief_model_spec.md) · [Báo cáo/CSV/log/hình](results/lessons/l1_6/report.md). Sáu mutant bị bắt; output ngoài src/experiments, không copy repo. G1/V3/V10/V11 và HOLD Phase 4 giữ nguyên.

Cài môi trường và chạy kiểm thử (Python >= 3.10):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest -q
```

L1.7 (22/10/2026): **13/13 test lesson,72/72 sáu lesson,4/4 bổ sung,97/97 toàn repo PASS**. N2000,XB,H6: CRN sample variance118.873 so với naive extra-draw353.622; exact117.496/358.152/independent323.248. H3: oracle/leak/honest cost7.836/6.5725/8.22 packet·slot; honest vẫn thắng24.75% episode, không tự là dấu leak. Sáu mutant lỗi bị bắt; R7 equivalent về action. Audit replay11332 CSV rows PASS. [Card](notes/lessons/L1.7_experiment_card.md) · [Spec/mock tham khảo](notes/lessons/L1.7_stream_exposure_spec.md) · [Seed](notes/seed_registry.md) · [Report/CSV/log/hình](results/lessons/l1_7/report.md) · [Index và audit](notes/verification/l1_7/README.md). Residual0 chưa đủ CRN; demo không là Phase4/E01 hoặc held-out. G1,V3/V10/V11 và HOLD Phase4 giữ nguyên.

L1.8 **Part A** (22/10/2026): **4/4 test core, 10/10 bổ sung, 111/111 toàn repo PASS**. Hai thẻ đổi đơn vị giữ Δt ứng viên (a) 0,12 ms, (b) 12 ms; tuổi làm tròn thành 42 và 17 slot. R2 giữ correlation qua 204 ms = 0,016907466 tại slot 12/6/3 ms; R1 thay đổi. 96 kiểm fluid boundary và 900 round trips có 0 vi phạm; đã làm rõ dấu crossing correction bằng phản ví dụ exact. [Card](notes/lessons/L1.8A_experiment_card.md) · [Spec](notes/lessons/L1.8A_slot_model_spec.md) · [Report/CSV/log/hình](results/lessons/l1_8_a/report.md) · [Index và audit](notes/verification/l1_8_a/README.md). Trạng thái tại lần chạy A: chưa thực hiện Parts B–E, chưa chốt Δt hoặc contract v1; xem record CDE mới ở cuối README. Chưa xác nhận kết quả không phụ thuộc slot hay validation mạng. G1, V3/V10/V11 và HOLD Phase 4 giữ nguyên.

L1.8 **Part B** (22/10/2026): **13/13 test mới, 124/124 toàn repo PASS**. Toy p=s=5/8 được chạy ở tám mức Δt…Δt/128 bằng DP gộp state, không Monte Carlo. GS từ 0,9296875 xuống 0,307151637; GM=0; Richardson cuối GS≈0,302699661, Γ≈0,017362905 (ước lượng có điều kiện). Forward scorer khớp backward DP trong 3,6×10⁻¹⁵. Đã phát hiện hai sai khác làm tròn và vấn đề đổi model ở phép tách B6: fixed-M0 mode share tại Δt/128 là 17,81%, không lấy ≈11% của đường hybrid làm kết quả State-only. [Card](notes/lessons/L1.8B_experiment_card.md) · [Protocol](notes/lessons/L1.8B_refinement_protocol.md) · [Report/CSV/log/hình](results/lessons/l1_8_b/report.md) · [Index/audit](notes/verification/l1_8_b/README.md). Trạng thái tại lần chạy B: chưa khóa contract v1 hoặc Parts C–E; record CDE mới bổ sung bên dưới; Δt vật lý cuối vẫn chưa được chứng nhận; G1, V3/V10/V11 và HOLD Phase 4 giữ nguyên.

L1.8 **Parts C–E** (22/10/2026): đã chọn profile stable OFF.2μ/ON1.4μ, conditional stationary prior vô hạn, lưới24main+2negative+2stress, calibration3 và reserve16 chỉ tọa độ. Ngưỡng chính1%/equivalence.5%/numerical budget.25%, Cref=Lstar cùng ô/cùng dt. Contract v1 giữ25term; brief/card/decision log/closeout và exception V11 có record. [Report và số đo thực](results/lessons/l1_8_cde/report.md) · [22 tests mới](tests/test_l1_8_contract.py) · [11 thẻ+6b](notes/lessons/L1.8D_decision_cards.md) · [Index/audit/git receipt](notes/verification/l1_8_cde/README.md). Chỉ screen/budget/timescales trên lưới mới; chưa chạy contrast hoặc margin, chưa sinh reserve. A01 final dt/full-grid computational feasibility và human feedback vẫn pending; không xem freeze là hypothesis/network validation.

Kết quả CDE thực chạy: **146/146 tests PASS**,5.832 idle pairs không mismatch; backward/forward132 giá trị sai số tối đa7.11e-15. Main s_bt0,hai controls≈1; M20/M22/M24 báo alarm conservative budget, chưa chứng nhận full-grid feasibility. Artifact auditor dựng lại28D/6.776state rows PASS.
