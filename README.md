# State × Model — giá trị cải thiện quyết định routing

Người phụ trách: **Doan Van Tai**.

Main RQ:
> For load-changing routing actions, how do improvements in current-state information and action-response model fidelity differ and interact in their effect on expected decision regret?

## Trạng thái hiện hành — 04/11/2026

**Phase 7 exploration CTMC đã merge vào main theo yêu cầu tác giả (DL-139); Gate Phase 7 HOLD, không tag.**
- L7.1–L7.3 là test theo thẻ do AI soạn.
- L7.4 tổng hợp: [báo cáo](notes/synthesis/L7_4_REPORT.md), [claim–evidence](notes/synthesis/CLAIMS_EVIDENCE.md).
- L7.5 Stage 0 chỉ có zero-fit; [thẻ τ](results/explore_ctmc/l75/CARD_L7_5.md) chưa khóa.
- G1 không đổi.


Phase 5 đã đóng sau bước đọc kết quả L5.3 và discovery Phase 4, theo
[quyết định numbering v1.2](notes/phases/PHASE_4_entry_decision.md).
Hai exploration `mechanism-regime-v2` và `p4-regions` đã được gộp;
chúng vẫn là exploration, không phải confirmation hoặc author-self work.

**Phase 6 closeout L6.4: Gate D = REFORMULATE; G1 giữ nguyên, PIVOT-watch tiếp tục.**
Verdict INCONCLUSIVE giữ nguyên:13 D READY,8 U deadband. Đã tính covariance
trực tiếp trên saved surfaces của27 members,0 evaluator/profile mới;
identity residual≤6.67e−16 packet·s và conditional-grid mean bridge được giữ.
Không nhận S≈0⇒alignment≈0 hoặc h dài tự làm H1 thắng.10 targeted tests PASS;
six-source prior check có2 AI-T/4 AI-A, không novelty/prior-clearance claim.
Phase compute upper4200 CPU-s là bao bảo thủ, không actual tổng. Memo đã
soạn theo ủy quyền; Understanding/author-self OPEN. Dừng ở memo, chưa thiết
kế/chạy Phase7. Source/plan/predictions/old data/catalog giữ byte.
[Closeout](notes/phases/PHASE_6_closeout.md) ·
[Memo đóng góp](notes/phases/contribution_memo_after_P6.md) ·
[Phép dẫn và đính chính](notes/theory/T10_information_value_accounting.md) ·
[Prior check](notes/literature/L6_4_prior_check.md) ·
[Direct covariance CSV](results/phase6/closeout_l6_4/covariance.csv) ·
[DL-138](notes/02_decision_log.md).

**L6.3 đã chạy đúng một lần: execution COMPLETE, verdict INCONCLUSIVE (fact).**
81/81 calls,27/27 members; stop_reason=null. D13: '-'3,'+'2,U8;
A− '-'; twin '+'11,'-'0,U2;2/13 intervention pairs, wording flag=false.
Raw `d7a298f0` commit/push trước rescore; RESCORE MATCH và verdict tính
độc lập từ counts khớp. Runner1339.9 CPU-s/cap7200; prior upper2600,
closeout phase upper4000 CPU-s, không actual tổng. Source/freeze giữ byte.
[Summary](results/phase6/summary.json) · [DL-136](notes/02_decision_log.md).
**L6.4 đã chẩn đoán trên dữ liệu lưu, DL-137:** 13/13 D READY; cả 8 U là
deadband, 0 NOT_READY. Hai D '+' là B027C12/B050C19. Replay cache tái lập
4 losses×27 members, max sai khác 7.11e−15 packet·s; 0 evaluator/profile mới.
Sai lệch predictor chủ yếu ở việc thay gap theo state bằng stake hằng:
correction 0.584–3.299 pp; representation M0≤0.000064 pp, normalizer≤0.0557 pp.
Đây là post-hoc trên cùng frozen profiles, chưa loại shared bias hoặc
tách riêng A1/A2. INCONCLUSIVE giữ nguyên, không kết luận từ subset 5 điểm.
Probe/replay đã mở theo yêu cầu chẩn đoán; không retry/resume/refine.
Tại checkpoint DL137 chưa Gate D/prior; closeout hiện hành ở DL138 phía trên.
Phase upper lúc đó4050 CPU-s là bao bảo thủ, không actual tổng.
[Bảng27 members](results/phase6/analysis_l6_4/members.csv) ·
[Audit/hashes](results/phase6/analysis_l6_4/summary.json) ·
[Analyzer cache-only](tools/analyze_phase6_saved.py).

**Checkpoint L6.2 Part B/C: Gate D-entry GO theo DL-135.**
Probe9/9 calls,3/3 class READY; d=0.06713/0.11356/0.04162 pp,
ALL_MEMBERS27, estimate5864.27 CPU-s dưới cap7200. Raw probe/replay
giữ kín G_S/z tớiL6.4. Positive control PASS: replay c=1/16 không field
mismatch, hai saved anchors trái dấu được label đúng. Full752 tests PASS;
4/4 local mutants KILLED. Runner e3b0fa92, control raw094ff321.
Predictions và analysis plan v2 đã freeze; prior upper Phase6=2600 CPU-s
trước L6.3, không actual tổng. Panel nay đã chạy; không retry/resume.
[Probe summary](results/phase6/probe/summary.json) ·
[Predictions](results/phase6/predictions.jsonl) ·
[Plan v2](notes/design/analysis_plan_v2.md) ·
[Control report](results/phase6/gate_anchor/report.json) ·
[Runner](experiments/P6_band/run.py) · [DL-134/135](notes/02_decision_log.md).
G1 và các giới hạn về A1/A2/realism/ownership giữ nguyên; Gate là
verification của pipeline, không validation của H1.

**Checkpoint Part A′: PASS readiness của cửa sổ D(ii), DL-133.**
Một lượt tại `cc3b2623`; raw `832c70ac` trước diễn giải. Identity 14/14,
D(ii) 13/13 base, twin 13/13, A− 1/1 qua. Chọn một c/base theo đỉnh
|z_K320|, không thay điểm sau K640; |z_K640|=1.0591–2.9520%Cref_H1.
Full 709 PASS trước sửa allowlist; targeted sau sửa 52 PASS. Runner 390.83
CPU-s; closeout upper cộng dồn 1750 CPU-s, không phải actual tổng đo.
Đây là adaptive predictor design trước truth, chưa xác nhận A1/A2/H1.
Tại checkpoint DL-133, Part B/C/L6.3 chưa chạy; trạng thái mới ở DL-135 phía trên.
[Runner](experiments/P6_band/select_dii.py) ·
[Candidates](results/phase6/window_revision03/candidates.csv) ·
[Summary](results/phase6/window_revision03/summary.json) ·
[DL-133](notes/02_decision_log.md).
Giữ rho/P_min/z_min/H0/H1; bỏ tỷ lệ 2/3 D(i) và thu hẹp sang D(ii) theo
ủy quyền, không kiểm vế dải giúp dịch sang x<0. Không revision04.
Predictor/identity và lịch sử giữ byte; window.py chỉ thêm module độc lập
mới vào certificate allowlist, không đổi các phép tính.

**Lịch sử L6.2 Part A revision02: STOP theo DL-132, được giữ nguyên.**
685 tests PASS. Grid mở rộng c≤6, vẫn giữ51base/margins/H1/H0 vàK320/ref4;
đủ **1.020 dòng**, 510 dòng cũ khớp mọi trường. Sau MUST+SHOULD có
**6 D(i) từ 3 base, 102 D(ii), 302 A**. Giới hạn2cost/base chỉ cho tối đa
**5 D(i)** vào witness, trong khi10D cần ít nhất7D(i), nên W9 không đạt.

B035 bổ sung3điểm D(i), dự đoán1,027–1,308%Cref_H1; không được coi ba
mức c là ba base. Không có finalwitness nên **K640/PartB/panel chưa chạy**.
Không mở revisiongrid thứba hoặc hạz_min1% để cứu. STOP chỉ áp dụng thiết
kế/grid hiện tại, không kết luận H1sai hoặc plantkhôngcó hiệu ứng.
[Scan revision02](results/phase6/window_revision02/scan.csv) ·
[summary](results/phase6/window_revision02/summary.json) ·
[DL-132](notes/02_decision_log.md#dl-132--l62-part-a-mở-rộng-độ-phủ-c-khai-trước-sửa-windowpy-02112026).
H1/identity code giữbyte; 7certificates phân tầng được tái dùng cóprovenance,
không phải7lượt kiểm mới hay51identityPASS. [Revision01 HOLD](results/phase6/window_revision01/summary.json),
[BLOCKED cũ](results/phase6/window/summary.json) và lỗi CSV trước đó giữ nguyên.

L6.1 đã chốt câu hỏi Phase 6 (DL-129). Chọn dấu G_S
dưới switching cost, H1 dùng M0-only; H0a là dải `0 < x < 0.54−0.07u`,
fit hai tham số trên discovery, đúng 1418/1448 (97,93%) trong mẫu.
Chọn h-invariance làm mô tả phụ trong cùng panel, không knockout;
budget toàn Phase 6 ≤4 CPU-giờ, panel ≤2 giờ, không retry/resume/v1.1.
**Đính chính exposure:** pilot c_sw>0 có P tối đa40 (bốn dòng P40), nên
`c_sw>0, P≥30` không tự là điều kiện chưa dùng; phía x<0 chưa có active key
trong inventory. Thiết kế c_sw theo DL-132 đã STOP trước probe; không hạ
z_min=1%, mở rộng thêm grid hoặc calibration để cứu witness.
[Quyết định, recipe fit và kiểm toy](notes/02_decision_log.md#dl-129--phase-6-l61-chọn-câu-hỏi-cơ-chế-h1-h0-và-can-thiệp-02112026).

V1 chính thức **INCONCLUSIVE**; v1.1 **PASS 10/0/0** sau một lần sửa thiết kế có khai báo, chỉ giữ
claim numerical finite-panel ở h/κ 320/640, có exposure một phần.
H-L2 PASS exploratory, nhưng Spearman chịu cấu trúc cụm và MedAE phụ thuộc
thành phần panel; cả hai thay đổi acceptance đều cần để H-L1 PASS, nên đây
là lượng hóa phù hợp một giới hạn được kỳ vọng, chưa phải contribution/novelty.
**Gate C = NARROW, G1 giữ nguyên (DL-128)**; bàn giao Phase 6 theo ủy quyền,
realism/D22/Understanding còn mở;
panel Phase 6 đã chạy một lần; dữ liệu panel/probe/control đã mở để chẩn đoán
L6.4 như trên, không còn là fresh data.
Không retry/resume/refine Phase 5 hoặc gọi đó là confirmation độc lập.

[Closeout L5.3: evidence, sensitivity, prior và claim](notes/phases/PHASE_5_closeout.md) ·
[DL-128](notes/02_decision_log.md#dl-128--phase-5-gate-c-narrow-02112026) ·
[Summary v1](results/phase5/summary.json) · [Summary v1.1](results/phase5_v1_1/summary.json) ·
[Amendment](notes/design/phase5_v1_1_amendment.md) ·
[Runner v1.1](experiments/P5_v11/run.py) · [Tests](tests/test_p5_v11.py).

**Đính chính exposure:** nhánh p4-regions đã tính 77 regime có h/κ>160
trước commit freeze L4.9, trong đó W0347 trùng P5_08 ở mức (160,2).
Ở dòng này S=G_S|M1/Cref=0,0%, M=G_M|S1/Cref=16,21328185%.
16,2% là model value, không phải state value hoặc một FAIL của H-L1.
Panel không còn được gọi là 12 tọa độ hoàn toàn chưa từng tính; chưa có
bằng chứng người chọn panel đã nhìn dòng này. Không sửa lịch sử frozen.
H-L1 giữ bài chấm gốc nhưng được đọc như validation có exposure một phần;
không dùng nó một mình để claim confirmation độc lập.
[Exposure và quyết định](notes/02_decision_log.md#dl-122--dọn-repo-hợp-nhất-exploration-và-đính-chính-exposure-02112026).

## Điểm vào

- [Contract v1.3](notes/01_definitions_v1_3.md), [amendment](notes/design/contract_v1_3_amend1.md), [claim boundary](notes/01_claim_boundary_v1_3.md).
- [Phase 4 v2](notes/phases/PHASE_4_v2.md): bản triển khai tối thiểu, không phải full master plan.
- [Freeze L4.9](notes/design/analysis_plan_v1.md), [lock](notes/design/analysis_plan_v1.lock.json), [report lịch sử](results/lessons/l4_9_v2/report.md).
- [Mechanism exploration](results/explore_mech/SUMMARY.md), [scorecard](results/explore_mech/checks.json), [xstar scorecard](results/explore_mech/checks_xstar.json).
- [Practical regions](results/explore_p4/SUMMARY.md), [raw W0347](results/explore_p4/wide/level_160_2/W0347.json).
- [Decomposition](results/lessons/l4_6_v2/report.md), [T08 clipping](notes/theory/T08_clipping_anchor.md), [T09 limits](notes/theory/T09_stationary_dominance_limits.md).
- [Baseline A3](results/lessons/p4_a3/report.md), [SV FAIL_SCREEN và SUB checkpoint](results/lessons/l4_5/part_b/report.md).
- [Paper library](papers/README.md); mọi lần tìm paper theo [search protocol](notes/literature/search_protocol.md).
- Phase 7: [CTMC SUMMARY](results/explore_ctmc/SUMMARY.md), [L7.3 kết quả](results/explore_ctmc/l73/RESULTS_L7_3.md), [L7.5 Stage 0](results/explore_ctmc/l75/STAGE0_REPORT_L75.md), [threats](notes/synthesis/THREATS.md), [T11](notes/theory/T11_proposition1_first_order.md).

SUB/CF-v2 vẫn park, R09/R10 vẫn sealed, D22 native DEFERRED;
G1, realism, L8 và Understanding không tự nâng. Cấu trúc dấu theo x vẫn
exploratory; moment dừng chính xác không tự làm ranh giới x* chính xác.
X1 chỉ có 10/15 crossing quan sát được ở κ=.1; 5 chuỗi còn lại là kiểm phía,
không phải 5 sai số điểm. Biên độ 4/5/6/7 đã có thiết kế/kết quả trong lịch sử;
không mặc định a≠6 là held-out sạch.

## Cấu trúc và kiểm tra

`src/`: thư viện; `experiments/`: Phase 4, exploration và dependency native/guards;
`tests/`: tests còn áp dụng; `notes/`: định nghĩa, theory, freeze và provenance;
`results/`: evidence hiện dùng, CSV/summary/plots và raw native cần replay.
Không tạo thêm file lesson/report cho lượt dọn này; lesson và lộ trình in trong chat.

```bash
.venv/bin/python -m pytest -q -p no:cacheprovider   # 1 FAIL có chủ đích sau DL-139 (guard P6 window)
.venv/bin/python -m experiments.P4_01_recount.verify_artifacts
```

Các audits/runner cũ đã archive không còn được coi là entrypoint hiện hành.
Dữ liệu native 597 nguồn và các mức refinement Phase 4 được giữ để replay;
JSON từng regime của exploration và lesson cũ được lấy lại từ tag khi cần.

## Archive và khôi phục

Lịch sử Git được giữ nguyên. Mốc trước dọn: `archive/main-before-cleanup-2026-11-02`.
Raw exploration: `archive/mechanism-before-cleanup-2026-11-02` và
`archive/p4-regions-before-cleanup-2026-11-02`; còn tag regime-map/population.
Ví dụ đọc một artifact cũ mà không khôi phục cây:

```bash
git show archive/main-before-cleanup-2026-11-02:notes/03_experiment_index.md
git show archive/mechanism-before-cleanup-2026-11-02:results/explore_mech/xstar/level_160_2/S0000.json
```

Cache bị ignore và worktrees được chuyển ra `/home/vantai/state-model-regret-archive/2026-11-02/`;
symlink cache giữ nguyên đường dẫn replay ở máy này. Cache không phải dữ liệu
đã commit; clone mới cần rebuild hoặc cung cấp lại cache. Liên kết lịch sử
trong các tài liệu frozen có thể trỏ tới artifact đã archive: dùng tag tương ứng.


Kiểm trực tiếp bundle Claude6ffe8e84:541testsPASS,16freezehash/3run guards/597
native sources khớp. Bản hiện hành giữ thêm5modules regression còn áp dụng;
587tests đã PASS. Raw exploration đã archive: analyzer từ chối raw thiếu/partial
trước khi ghi CSV/score; replay score từ savedCSV đã khớp cả dự đoán trượt.
Bundle đã import vào branch `archive/claude-cleanup-2026-11-02` và chuyển ngoài repo;
bundle chỉ chứa branch ref, không chứa5tags được kể trong lời trả lời.
