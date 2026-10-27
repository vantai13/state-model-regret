# State × Model — giá trị cải thiện quyết định routing

Tác giả: **Doan Van Tai**.

**Trạng thái 27/10/2026:** Phase 2 đóng **GO có điều kiện** (DL-043, tag
`phase-2-closeout`); Phase 3 mở. L3.1 Part3 và L3.2 hoàn tất kiểm kỹ thuật (DL-044–046).
Contract khóa tại `contract-v1.2`: 38 main, 12 held-out, 6 controls, 2 probes;
calibration M01/M09/M22. Chưa chạy A01/A04/A05; chưa tính regret/contrast trên lưới.
Kiểm L3.2: **300/300 tests PASS** (baseline 228; thêm 72), **11/11 mutant bị bắt**.
Engine mới ở experiments, chờ T05 tác giả; 32 D-only comparisons có sai lệch **0**.
[Report và số đo L3.2](results/lessons/l3_2/report.md) · [L3.1](results/lessons/l3_1/part3/report.md).

```text
Bản hiện hành (27/10/2026):
  Contract:       notes/01_definitions_v1_2.md (tag contract-v1.2, D1–D25)
  Brief / Claims: notes/00_research_brief_v1_2.md · notes/01_claim_boundary_v1_2.md
  Lưới:           notes/design/grid_v1_2.json · notes/design/v1_2_protocol.md
  Phase:          notes/phases/PHASE_3.md
  Log:            notes/02_decision_log.md · notes/00_exposure_register.md
  Experiments:    notes/03_experiment_index.md (A01 | A04 | A05-F | A05-T)
  D v1.2:         src/smr/cells.py (nguồn experiments giữ nguyên)
  Engine L3.2:    experiments/A00_engine/ (T05 tác giả OPEN, chưa promote)
  KHÔNG hiện hành: definitions v0/v1/v1.1; src/smr/design.py (plant L1.8C)
```

[Contract](notes/01_definitions_v1_2.md) · [brief](notes/00_research_brief_v1_2.md) ·
[claim boundary](notes/01_claim_boundary_v1_2.md) · [Phase 3 và phân loại artifact](notes/phases/PHASE_3.md) ·
[experiment index](notes/03_experiment_index.md) · [progress log lịch sử](notes/00_progress_log.md).
Claim boundary/brief hiện hành có addendum Phase 2 sau tag; D1–D25 và lưới giữ nguyên.

**Điều kiện:** L3.3 commit trước mọi A01; V9 chưa gửi, giữ điều kiện nên **A04 chờ**;
A05-F khóa trước A05-T; **HOLD Phase 4 tới P0-V10**. Người đọc P0-V10/L8 và các mục
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
