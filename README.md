# State × Model — giá trị cải thiện quyết định routing

Tác giả: **Doan Van Tai**.

**L3R.7 — tạm dừng theo yêu cầu tác giả, 30/10/2026 (DL-094):** native05 đã
kết thúc **HOLD**:286receiptsCOMPLETED,2lỗi JSONserialize ởCAL_CORNER_049/050,
6972.840511CPU-s,peak183.691MiB. Local701testsPASS/GCPpreflight693PASS;
2410exportfiles khớpSHA,3948same-levelcomparisons khớp trong arithmeticenclosures.
Không còn researchworker; temporarySSHrule đãxóa,VMvẫnRUNNING. **Lesson7 chưa
hoàn tất**, chưa v1.3.1/n/root/CF;Phase4HOLD. Các snapshot dưới đây là lịch sử.
[Báo cáo tạm dừng](results/lessons/l3r_7/pause_report_20261030.md) ·
[Metrics](results/lessons/l3r_7/full_numerics/native05/report/metrics.csv) ·
[Prereg](experiments/R3R_11_native_population/prereg.json).

**L3R.7 — bản đồng bộ ngày 30/10/2026:** đã lưu mã, thiết kế, prereg và các
kết quả hiện có. Lần kiểm hash này xác nhận contract21/card10/numerical-source108
khớp; không chạy lại thí nghiệm. Preflight GCP gần nhất ghi **672 tests PASS**.
Trạng thái đợt full03 hiện **chưa xác minh được vì SSH timeout**; tiến trình thu
kết quả local không còn chạy. Snapshot cuối23:50:47 ngày29/10 ghi120lượt hoàn tất,
3ca còn chạy ở vòng đầu; chưa có export cuối của03 trong repo.
**Chưa khóa v1.3.1/n/seed/CF; Lesson7 chưa hoàn tất, Phase4 HOLD.**
[Trạng thái lần push](results/lessons/l3r_7/full_numerics/push_snapshot_20261030.json) ·
[Giải thích bài7](notes/lessons/L3R.7_explained_vi.md) ·
[Báo cáo đợt02](results/lessons/l3r_7/full_numerics/report02/report.md).

**L3R.7 — đã chạy hai probe lớn trên GCP** (29/10/2026, DL-084–085):
633/633 tests PASS trên local và 633/633 PASS riêng trên GCP. Balanced candidate:
medium local **19,926 s** (baseline806,568s, quantiles khớp); hai marginal degree12000
trên GCP **902,514 s / 329,654 s**, peakRSS **137,9 / 108,9 MiB**, law error bounds
**1,408e-32 / 2,453e-33**. Phiên bản balanced hoàn tất3/3probe đã đăng ký.
Giữ failed candidate02 và baselinev2 B bị ngắt/thiếu finalreceipt; không tô thànhPASS.
29file export khớp SHA256; ruleSSH tạm đã xóa, VM vẫn RUNNING do tác giả bật.
**Candidate chưa adopted; numerics v1.3.1/fullaccuracy/D22 còn HOLD. Chưa n/root/CF.**
[Kết quả candidate](results/lessons/l3r_7/extended_capacity/candidate_report.md) ·
[CSV](results/lessons/l3r_7/extended_capacity/candidate_metrics.csv) ·
[Baseline và lần gián đoạn](results/lessons/l3r_7/extended_capacity/report.md).

**Snapshot numerics v1 — kết quả HOLD** (29/10/2026, DL-078–079):
prereg `0efddcc` trước run; **595/595 full tests,8/8 numerics tests PASS**.
Replay **3/3 anchor khớp**, stationary **3/6 hoàn tất,3/6 UNRESOLVED do CPU ceiling**.
Hai probe degree12000 dừng ở numpy_roots, khoảng2.21GiBRSS; degree1200 dừng ở
mpmath LU437×437. Tổng396.116CPU-s;312globaljobs chưa mở theo stop rule.
**Chưa khóa v1.3.1, chưa cấp n/root/CF; Phase4 HOLD/G1.**
[Báo cáo numerics](results/lessons/l3r_7/numerics_report.md) ·
[Số đo CSV](results/R3R_numerics/20261029_01/metrics.csv).

**Snapshot L3R.7 trước calibration — phần chuẩn bị hoàn tất, chưa sinh confirmation**
(29/10/2026, DL-075–076): **587/587 full tests,38/38 targeted PASS**; sửa checker
receipt thiếu manifest, giữ nguyên10file cardv1 và21file contract. Sampler dùng
seed thử,10.000draws; inventory308records/245reservedv1.3keys; power36scenarios;
runner từ chối đúng, engine0/CF0/rootconfirmation0. **DL-077: luật n đã duyệt,
B48CPU-giờ theoủyquyền,2worker banđầu/tốiđa4,1luồngBLAS mỗiworker**;
numericsv1.3.1 và audited backend/dry-runB còn DEFERRED. **Sampling/Phase4 HOLD**,G1.
[Thiết kế](notes/design/confirmation_v1_3.md) · [Report](results/lessons/l3r_7/report.md) ·
[Completion](notes/phases/L3R_7_completion.json).

**Phase 3R — L3R.6 đã đóng băng hypothesis cards v1** (29/10/2026, DL-073–074):
freeze commit **1414d92**, [receipt](notes/phases/PHASE_3R_hypothesis_cards.lock.json) verify PASS.
Tác giả chọn **phương án D**: Hyp-MV (ḠM/C̄ref≥1%) và Hyp-SH (ḠS/C̄ref≤−1%) primary, không secondary;
Γ̄ chỉ diagnostic vì Γ̄≥−min(ḠS,ḠM) (discovery: 3/162 cấu hình có thông tin). Ω⁻ hai card chỉ lật
κ∈[1;3] (ngoại suy). π₀=½, CP 97,5%, Bonferroni, R4 bốn góc, R5 u_max10%; measure khóa trong card.
**9/9 phép kiểm, 17/17 targeted, 549/549 full tests PASS.** AI soạn, tác giả duyệt; phép7 bằng lời
tác giả và Understanding OPEN. Không CF/engine/seed; R09/R10 ngoài mọi vùng. CF sampling chờ numerics
v1.3.1; **Phase4 HOLD**, G1. [Cards](notes/phases/PHASE_3R_hypothesis_cards.md) ·
[Forking log](notes/phases/PHASE_3R_forking_paths.md) · [Claim boundary](notes/01_claim_boundary_v1_3.md) ·
[Report](results/lessons/l3r_6/report.md) · [Completion](notes/phases/L3R_6_completion.json).

**Phase 3R — L3R.5 đã khóa contract v1.3 với mục DEFERRED** (29/10/2026, DL-071–072):
Tag **contract-v1.3 → 3d2359b**,21frozen inputs khớp receipt;
**532/532 full tests,41/41 targeted tests PASS**. P1/RoE/εR1%/εE.5%/c_sw0primary
được tác giả chọn; stakes chỉ mô tả, không dùng OR. Schema giữ210scientific keys
trên216ID; quênc_sw→162,đưaK/ref→228 trên234metadata records.
D22 đã cam kết/khóa định nghĩa; enginepath/auditDEFERRED. Numerical rules LOCKED,
K*/dt*/quadrature-tail/S1routeDEFERRED→v1.3.1 trướcCFsampling. RealismHOLD_UNSOURCED,
auditL3R.3HOLD; **Phase4HOLD**,G1,Understanding/P0-V10/L8/T05OPEN.
Đã đạt điều kiện contract choL3R.6; chưa tạo hypothesis card hoặcCF.
[Contract](notes/01_definitions_v1_3.md) · [Brief](notes/00_research_brief_v1_3.md) ·
[Lock receipt](notes/phases/contract_v1_3.lock.json) · [Report](results/lessons/l3r_5/report.md) ·
[Completion](notes/phases/L3R_5_completion.json).

**Phase 3R — L3R.4 đã chạy screen; realism HOLD_UNSOURCED** (29/10/2026, DL-069–070):
**491/491 full tests,24/24 targeted tests,18/18 generic MC comparisons PASS**.
Nguồn mới3được duyệt/đọc targeted; Excel26nguồn,23record/progress cũ giữ nguyên.
Envelope commit6bef959, export fix830a187 không đổi luật; labels1164500 trước overlay.
**216ID/210cấu hình đều UNSOURCED ở cả DC và edge**, kể cả f1.5/2/3.
MV20ID,SH80ID(78distinct),giao14ID từ discovery cũ; cả MV/SH nhánh(d) HOLD.
Không đủ nguồn tương thích chưa có nghĩa OUT/phi thực tế; chưa empirical validation.
[Report](results/lessons/l3r_4/report.md) · [Nhãn](results/lessons/l3r_4/screen/labels.csv) ·
[Worksheet](notes/realism/worksheet_v1.md) · [Review giới hạn input](results/lessons/l3r_4/blind_review.md) ·
[Completion](notes/phases/L3R_4_completion.json).
L3R.5 học/soạn được; L3R.3 auditHOLD/numericsNOT_FROZEN giữ; contractv1.3DRAFT,
Understanding/P0-V10/L8/T05OPEN, **Phase4 thực thi HOLD**,G1.

**Phase 3R — L3R.3 đã chạy audit; gate HOLD** (29/10/2026, DL-068):
**467/467 tests**, 19 tests gốc riêng, **12/12 mutants**, **19/19 clean reproductions** đạt.
MC: C1 **80/80**, C2 **80/80 sau kiểm arithmetic**, C3 node **8/8**, max|z| **2,313697**.
Giữ UNRESOLVED ở các mức số khai gốc; X2065 qua kiểm sau tăng K80/ref2 (0,050361ppC).
19 lần tái lập thuộc 9 tọa độ vật lý; kiểm bổ sung được ghi riêng. KEEP lõi/snapshot với
lớp test/API trong experiments. Numerics v1.3 và read-back tác giả chưa khóa/hoàn tất.
[Report](results/lessons/l3r_3/report.md) · [CSV/metric](results/lessons/l3r_3/summary.csv) ·
[Code map](notes/verification/l3r_3/code_map.md) · [Completion](notes/phases/L3R_3_completion.json).
L3R.4 học tiếp được; **Phase4 thực thi HOLD**, contract v1.3 vẫn DRAFT.

**Phase 3R — L3R.2 hoàn tất kỹ thuật** (28/10/2026, DL-065):
[T07 estimand/proofs](notes/theory/T07_population_estimand.md) đã commit trước audit;
**16/16 golden, 439/439 full tests PASS; 500 joint laws/0 vi phạm; 5/5 mutant KILLED**.
[Report/số đo](results/lessons/l3r_2/report.md) · [JSON exact](results/lessons/l3r_2/toys/metrics.json) ·
[Completion](notes/phases/L3R_2_completion.json). T07 soạn theo ủy quyền;
Understanding/ownership OPEN. Tiếp theo **L3R.3 audit engine**; chưa engine verification,
Contract v1.3 vẫn DRAFT, Phase 4 thực thi HOLD.

**Phase 3R — L3R.1 hoàn tất kỹ thuật** (28/10/2026, DL-064):
pilot được đóng băng tại tag `explore-v13-pilot` → `a7435e9`, không merge branch.
Đếm một lần từ raw: **216 ID/210 cấu hình phân biệt; harm80/216 hoặc78/210**;
423 tests toàn repo PASS,3/3mutant bị bắt. SUMMARY nguồn giữ nguyên, E1–E7 ghi riêng.
[Discovery record](notes/phases/PHASE_3R_discovery_record.md) ·
[Report/log](results/lessons/l3r_1/report.md) · [Số liệu](results/R3R_01_recount/20261028_01/recount.json) ·
[Completion](notes/phases/L3R_1_completion.json). Trạng thái sau L3R.1: tiếp theo L3R.2;
engine audit/realism chưa làm, Understanding và điều kiện Phase4 vẫn OPEN/HOLD.

**L3.8 — Gate A: REFORMULATE** (DL-061, 28/10/2026):
391/391 tests toàn repo vừa kiểm lại PASS; validity/evidence và điều kiện quy trình
được tách riêng. Tác giả chọn chuẩn bị thiết kế mới; hai mục closeout được viết ngôi
“tôi” theo ủy quyền trực tiếp, **Understanding/ownership vẫn OPEN**.
[Gate note](notes/phases/PHASE_3_gate.md) · [Closeout](notes/phases/PHASE_3_closeout.md) ·
[Record tác giả](notes/phases/PHASE_3_author_decision.json) ·
[Audit L3.8](results/lessons/l3_8/report.md). Bước tiếp: hoàn thiện
[contract v1.3 DRAFT](notes/01_definitions_v1_3_draft.md) và [brief DRAFT](notes/00_research_brief_v1_3_draft.md).
**Thực thi Phase 4 HOLD tới P0-V10 và contract mới được khóa**; học tiếp được.

**L3.6/A05-F đã đóng băng** (DL-057–058): D25(ii), shared Gaussian H0/H1,
12 hệ số/model, 2 candidates/bên, LOSO 20 lát. **369 tests PASS**; θ, features,
predictions và luật chấm đã commit đúng thứ tự, source/SHA guard PASS.

H1 có LOSO summary MSE thấp hơn H0 **21,13%** trên discovery; chưa là kết quả test.
D của nhóm nội suy chính **0,59124 điểm %Cref**, ngoại suy **0,47495**, đều vượt
margin0,25. Nhóm yếu R09/R10 chỉ **0,21230** nên giữ chưa mở theo luật đã khóa.
Universe12 ô; A05-T mở **R01–R08,R11/R12**, R09/R10 niêm phong.

**L3.7/A05-T đã chạy đúng một lần** (DL-059–060, 28/10/2026): validity 20/20, p_sw 20/20,
chấm lại độc lập khớp. **PC4 nội suy WEAKEN** (d = 0,247 < m = 0,25 điểm % C_ref;
MAE0 0,690, MAE1 0,443); ngoại suy h12 **FALSIFY** (d = −0,142); **K5 bị bác ở R04**
(G_M/C_ref 0,528%); **C1 đứng** ở R05–R08 (khóa sau discovery/trước test; n=4, base rate cao). Không SUPPORT,
không cơ chế. Gate A được tác giả chọn REFORMULATE ở L3.8. [Report L3.7](results/lessons/l3_7/report.md) ·
[verdict](results/A05_test/20261028_01/verdict.json).

[Report L3.6](results/lessons/l3_6/freeze_report.md) · [Audit](results/lessons/l3_6/freeze_verification.json) ·
[Prereg](experiments/A05_freeze/prereg.md) · [Freeze](notes/lessons/A05_F_preregistration.md) ·
[Biểu đồ](results/lessons/l3_6/freeze_diagnostics.png) · [Completion](notes/phases/A05_F_completion.json).

**Trạng thái 28/10/2026:** Phase 2 GO có điều kiện (DL-043); Phase 3 đã hoàn tất
kỹ thuật tới **L3.7/A05-T**, L3.8 chốt REFORMULATE. Contract `contract-v1.2` và prediction card `a03-card-v1`
giữ nguyên. **A04: 92/92 cell-level BOUNDED, 46/46 cặp dt đạt**, không HOLD/cờ dt;
348 tests PASS. Primary dt=1/240 s theo DL-053, pair1/120→1/240 cho từng ô.

**Card: P5 đứng; P2, P3, P6 không đứng.** K5 đạt4/4; Q5 có2/4 witness. Chấm và
commit `7005a3b` trước discovery, kiểm tay độc lập hai ô khớp. Không xác nhận cơ chế.
Đã xét5 phát biểu, giữ1 candidate C1 sau discovery; cả3 miền không bị cheap kill.
K5 đã carry nguyên văn m=1 vào **A05-F**, C1 khóa sau A04; kết quả held-out ở khối L3.7 phía trên.

[Note A04](notes/lessons/L3.5_A04_note.md) · [report đầy đủ](results/lessons/l3_5/report.md) ·
[kiểm chứng](results/lessons/l3_5/verification.json) · [38 ô cuối](results/A04/20261027_01/main_final.csv) ·
[card scores](results/A04/20261027_01/card_scores.csv).
[A01](results/lessons/l3_4/report.md) vẫn PASS: dt1/240, giữ các failed/partial artifacts;
11/11 mutants là kiểm lịch sử A01, không chạy lại trong A04.
[Card](notes/phases/PHASE_3_prediction_card.md) · [L3.3](results/lessons/l3_3/report.md) ·
[L3.2](results/lessons/l3_2/report.md). Engine vẫn ở experiments, chưa promote.

```text
Bản hiện hành thiết kế population (29/10/2026):
  Contract:       notes/01_definitions_v1_3.md (tag contract-v1.3, có DEFERRED)
  Brief / Claims: notes/00_research_brief_v1_3.md · notes/01_claim_boundary_v1_3.md (điền theo cards L3R.6)
  Cards v1.3:     notes/phases/PHASE_3R_hypothesis_cards.md (+ .lock.json; FROZEN 1414d92)
  Receipt:        notes/phases/contract_v1_3.lock.json
  Kết quả cũ:     notes/01_definitions_v1_2.md · notes/design/grid_v1_2.json · notes/design/v1_2_protocol.md
  Phase:          notes/phases/PHASE_3R.md (L3R.6 cards frozen; numerics/realism HOLD)
  Gate / Closeout: notes/phases/PHASE_3_gate.md · PHASE_3_closeout.md (REFORMULATE, ownership OPEN)
  Draft lịch sử:  notes/01_definitions_v1_3_draft.md (DL-061, đã supersede cho thiết kế mới)
  Log:            notes/02_decision_log.md · notes/00_exposure_register.md
  Experiments:    notes/03_experiment_index.md (A01 | A04 | A05-F | A05-T)
  D v1.2:         src/smr/cells.py (nguồn experiments giữ nguyên)
  Engine L3.2:    experiments/A00_engine/ (read-back author-attested, chưa promote)
  Prediction:     notes/phases/PHASE_3_prediction_card.md (a03-card-v1)
  A05-F freeze:   notes/lessons/A05_F_preregistration.md · experiments/A05_freeze/
  KHÔNG hiện hành: definitions v0/v1/v1.1; src/smr/design.py (plant L1.8C)
```

[Contract v1.3](notes/01_definitions_v1_3.md) · [brief v1.3](notes/00_research_brief_v1_3.md) ·
[claim boundary v1.3](notes/01_claim_boundary_v1_3.md) · [Phase 3 cũ và phân loại artifact](notes/phases/PHASE_3.md) ·
[experiment index](notes/03_experiment_index.md) · [progress log lịch sử](notes/00_progress_log.md).
[Contract v1.2](notes/01_definitions_v1_2.md) vẫn đi cùng kết quả cũ;
claim boundary v1.2 có addendum Phase2/A04, D1–D25 và lưới giữ nguyên.

**Điều kiện:** A03/A01 prereg đã khóa trước run; A04 dùng dt1/240 và kiểm cặp1/120→1/240 từng ô.
**V9 đã được tác giả miễn làm điều kiện tiên quyết theo DL-054 (`WAIVED_BY_AUTHOR`)**;
memo chưa gửi, chưa có phản hồi GVHD thật. Prereg/exposure, runner/tests và A04 đã hoàn tất.
[Completion A04](notes/phases/A04_completion.json) ghi trạng thái sau run; gate record là snapshot trước run.
[Gate record](notes/phases/A04_execution_gate.json) · [preflight L3.5](notes/lessons/L3.5_preflight.md).
A05-F đã khóa; A05-T đã chạy một lần sau quyết định DL-059. **HOLD Phase 4 tới P0-V10**. Người đọc P0-V10/L8 và các mục
tác giả tự viết còn mở. [Gói cho người đọc](notes/meetings/phase2_reader_packet.md).
Không dùng nháp heads-up 23/10 nguyên trạng (đã lỗi thời). Main RQ/contract/G1 giữ nguyên.

Main RQ:
> For load-changing routing actions, how do improvements in current-state information and action-response model fidelity differ and interact in their effect on expected decision regret?

**Mỗi lần tìm hoặc kiểm paper:** đọc [quy tắc + checklist](notes/literature/search_protocol.md).
[Search log](notes/literature/search_log.md) · [Excel tiến độ đọc](papers/paper_comparison.xlsx) ·
[thư viện](papers/README.md). PDF lưu ngoài Git.

Cài môi trường và chạy kiểm thử (Python >= 3.10):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest -q
```
