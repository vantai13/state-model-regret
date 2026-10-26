# L2.9 Part 2 — related work, DL Gate L, closeout (26/10/2026)

Người phụ trách: **Doan Van Tai**. **Toàn bộ do AI (Claude) thực hiện theo ủy quyền tác
giả** ("đóng vai tác giả và thực hiện mọi thứ cần tác giả thực hiện"); không phần nào
được ghi là tác giả tự làm. Base `74f7611`.

## Đã làm

1. **Nhãn tạm** PC1–PC6 + Main RQ, dòng PC3 đủ 8 cột (kèm hệ quả EVPI_w), K3 cho
   PC3/PC5/PC6: [prior_boundary](../../../../notes/literature/prior_boundary.md) (mục
   "L2.9 — nhãn tạm do AI chấm theo ủy quyền"). Hồ sơ Part 1 vẫn giữ 7 ô `⟨tác giả chấm⟩`.
2. **Related work một trang**: [related_work_skeleton.md](../../../../notes/literature/related_work_skeleton.md).
3. **Claim boundary** mục "Ranh giới với prior (Phase 2)": 12 nhóm không được claim là mới
   + bảng được claim (tạm): [claim boundary](../../../../notes/01_claim_boundary_v1_2.md).
4. **DL-042** Gate L: Main RQ KEEP, Gate **HOLD** (L2 ❌, L3 ⚠️, L8 ❌): [decision log](../../../../notes/02_decision_log.md).
5. **Evidence inventory EV-37…EV-45** (cột tác giả: "Chưa có record") và **exposure Phase 2**
   (held-out sạch về outcome).
6. **[PHASE_2_closeout.md](../../../../notes/phases/PHASE_2_closeout.md)**: hai mục đầu giữ
   "tác giả tự viết — chưa có", kèm bản nháp AI được rào riêng; Gate HOLD; **không gắn tag**.
7. **[Gói người đọc L8](../../../../notes/meetings/phase2_reader_packet.md)** (chưa ai đọc).

## Không thể làm thay (AI không tạo được bằng chứng của người thật)

- L-self (tác giả tự đọc nguồn quyết định nhãn): 0/19, [mẫu ghi](../../../../notes/literature/author_reading_record.md) chưa điền.
- Tự dẫn T03 kín sách (L3); hai mục đầu closeout bằng lời tác giả; người đọc thật (L8).
- Vì vậy Gate L **HOLD** theo PHASE_2 §17, dù mọi việc soạn thảo đã xong.

## Commands và kết quả

```bash
.venv/bin/python -I -B experiments/lessons/audit_l2_9_part2.py   # verification.json
.venv/bin/python -m pytest -q
git diff --check
```

Kết quả thực:
- `audit_l2_9_part2.py` **PASS** ([verification.json](verification.json)): 23 câu related work
  đều kết thúc bằng trích dẫn có mức đọc; đoạn 4 = 75 từ < đoạn 1–3 (161/184/188); 0 từ cấm;
  nhãn khớp; 7 ô `⟨tác giả chấm⟩` còn nguyên; EV-37…45 không ô nào "Có"; DL-042 Gate HOLD;
  không tag; đẳng thức E[min_a C] = min_a E[C] − EVPI_w đúng trên 500 case chính xác (Fraction).
  Mutant: thêm "novel", bỏ trích dẫn một câu (lần đầu **lọt**, đã sửa audit tách câu độc lập),
  kéo dài đoạn 4, ghi "Có" ở EV — đều bị bắt.
- `pytest -q` **202 passed**; `git diff --check` sạch.
- Hồi quy: `audit_l2_9_part1.py` và `audit_l2_8_followup.py` **FAIL có chủ đích** tại
  `notes/01_claim_boundary_v1_2.md` (lesson Part 2 yêu cầu thêm mục Phase 2 vào file này);
  output cũ của chúng không bị ghi đè.
