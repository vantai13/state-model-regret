# Gate L — GO có điều kiện (26/10/2026)

Người phụ trách: **Doan Van Tai**. Theo yêu cầu "mở tất cả cái chặn… sang phase 3" và các xác
nhận trực tiếp của tác giả ([nguyên văn](author_attestation.json)), ghi theo cơ chế DL-032.

## Đã ghi

- [author_reading_record](../../../../notes/literature/author_reading_record.md): 7 dòng bộ tối thiểu
  (WM26, R02, R04, P11, S11, P12, T03) + P02 = **author-attested 26/10**; lời giải ở vở, chưa chép vào repo.
- Excel: "Mức tôi đã đọc" = **Mục liên quan** cho WM26, R02, R04, P02, S11, P12 (17 nguồn khác giữ nguyên).
- [prior_boundary](../../../../notes/literature/prior_boundary.md): nhãn chính thức + lập luận bền nhãn cho 5 nguồn §5.4 còn AI-T.
- [DL-043](../../../../notes/02_decision_log.md): Main RQ KEEP; **Gate L GO có điều kiện**.
- [Closeout](../../../../notes/phases/PHASE_2_closeout.md) cập nhật; claim boundary, inventory (EV-48), exposure.
- Tag `phase-2-closeout`.

## Gate

L1 ✅ · L2 ✅ (bộ tối thiểu author-attested) · L3 ✅ · L4 ✅ · L5 ⚠️ deviation · L6 ✅ · L7 ✅ · **L8 ❌**.

## Phase 3: được làm gì

Commit prediction card L3.3 (chỉ phần claim còn đứng) → A01 (chỉ sau L3.3) → A02–A04; A05 khóa
H1/null/metric/split trước held-out. **Trước A04** gửi memo GVHD (V9). Phase 4 vẫn HOLD tới P0-V10.

## Còn mở

Người đọc thật (L8); hai mục đầu closeout bằng lời tác giả; bản journal R01, R34 (không chặn).

## Commands

```bash
.venv/bin/python -B tools/paper_library/build_notes.py
.venv/bin/python -I -B experiments/lessons/audit_gate_l.py
.venv/bin/python -m pytest -q
```

Kết quả thực: `build_notes.py` PASS (23 nguồn, 17 chưa xác nhận); `audit_gate_l.py` **PASS** ([verification.json](verification.json)); `pytest -q` 202 passed; `git diff --check` sạch.
