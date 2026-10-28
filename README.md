# State × Model — giá trị cải thiện quyết định routing

Tác giả: **Doan Van Tai**.

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
Bản hiện hành (28/10/2026):
  Contract:       notes/01_definitions_v1_2.md (tag contract-v1.2, D1–D25)
  Brief / Claims: notes/00_research_brief_v1_2.md · notes/01_claim_boundary_v1_2.md
  Lưới:           notes/design/grid_v1_2.json · notes/design/v1_2_protocol.md
  Phase:          notes/phases/PHASE_3R.md (L3R.2; Phase3 cũ đã closeout)
  Gate / Closeout: notes/phases/PHASE_3_gate.md · PHASE_3_closeout.md (REFORMULATE, ownership OPEN)
  Proposal mới:   notes/01_definitions_v1_3_draft.md (CHƯA KHÓA, không thay contract kết quả cũ)
  Log:            notes/02_decision_log.md · notes/00_exposure_register.md
  Experiments:    notes/03_experiment_index.md (A01 | A04 | A05-F | A05-T)
  D v1.2:         src/smr/cells.py (nguồn experiments giữ nguyên)
  Engine L3.2:    experiments/A00_engine/ (read-back author-attested, chưa promote)
  Prediction:     notes/phases/PHASE_3_prediction_card.md (a03-card-v1)
  A05-F freeze:   notes/lessons/A05_F_preregistration.md · experiments/A05_freeze/
  KHÔNG hiện hành: definitions v0/v1/v1.1; src/smr/design.py (plant L1.8C)
```

[Contract](notes/01_definitions_v1_2.md) · [brief](notes/00_research_brief_v1_2.md) ·
[claim boundary](notes/01_claim_boundary_v1_2.md) · [Phase 3 và phân loại artifact](notes/phases/PHASE_3.md) ·
[experiment index](notes/03_experiment_index.md) · [progress log lịch sử](notes/00_progress_log.md).
Claim boundary có addendum Phase 2 và kết quả A04 sau tag; D1–D25 và lưới giữ nguyên.

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
