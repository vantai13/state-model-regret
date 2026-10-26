# L2.9 Part 1 — phần AI đã làm, 26/10/2026

Người phụ trách: **Doan Van Tai** · AI (Claude) theo lesson L2.9 Part 1 do tác giả gửi.
Base `86ec878`. Theo PHASE_2 v2.0 §14, **tác giả** chấm nhãn, viết lý do và DL; AI chỉ
kiểm nguồn, mức đọc, nhất quán và phản biện. Vì vậy lượt này **không có nhãn nào**.

## Đã làm

1. **Kiểm lesson so với repo** ([lesson_check.md](lesson_check.md)). Lesson viết trên
   `7f59023` nên P02 còn ghi BLOCKED; nay P02 đã AI-T trên VoR (các chi tiết P02 mà
   lesson L2.7 dạy đúng 3/4). Một chỗ vượt record: "H1-Q01 cho thấy F không nhỏ ở
   κ=3" (H1-Q01 không phải F). PC1 trong claims.md là "dưới G1–G5".
2. **WM26 đọc lại có mục tiêu** (AI-T, [note](../../../../notes/literature/papers/WM26.md)):
   C/S nhập tương lai thật (F.1 Eq10 PDF22); nhánh không-oracle là future work (§9 PDF9);
   chỉ báo C−P, S−P, C−S. Không thấy nhánh chỉ dùng thông tin hiện tại trong phạm vi đọc.
3. **Hồ sơ 8 cột** cho PC1–PC6 và Main RQ, claim chép nguyên văn claims.md, cột Nhãn
   `⟨tác giả chấm⟩`, kèm Gate L tại HEAD và tổng hợp "không được claim là mới":
   mục cuối [prior_boundary.md](../../../../notes/literature/prior_boundary.md).
4. **Mẫu ghi L-self** [author_reading_record.md](../../../../notes/literature/author_reading_record.md)
   theo cơ chế DL-032; 7 nguồn của bộ tối thiểu; **chưa điền ô nào**.
5. Nhãn tạm của mentor lưu riêng: [reviewer_view_AI_open_after_grading.md](reviewer_view_AI_open_after_grading.md)
   (mở sau khi chấm). Ghi exposure.

## Gate L tại `86ec878`: **HOLD**

L1 ❌ (chưa nhãn) · L2 ❌ (L-self 0/19) · L3 ⚠️ (phép dẫn T03 do AI) · L4 ✅ (OεRE draft)
· L5 ⚠️ (deviation log; follow-up có raw; chưa luật dừng) · L6 ❌ · L7 ⚠️ · L8 ❌.

## Commands

```bash
.venv/bin/python -I -B experiments/lessons/audit_l2_9_part1.py   # verification.json
.venv/bin/python -m pytest -q
git diff --check
```

Kết quả thực: `audit_l2_9_part1.py` **PASS** ([verification.json](verification.json)): 7 dòng hồ sơ,
0 ô nhãn do AI điền, 6 claim khớp nguyên văn, 0 ô L-self được điền, 6 trích dẫn WM26 có
trong text PDF, 447 link, 0 PDF trong Git; hai mutant (điền NARROW, điền ngày) đều bị bắt.
`pytest -q` **202 passed**; `git diff --check` sạch. Hồi quy `audit_l2_8_followup.py` PASS
(file output của nó được khôi phục về bản commit để giữ lịch sử).

## Còn mở — việc của tác giả

1. Chấm nhãn PC1–PC6 + Main RQ vào cột trống (một câu lý do mỗi dòng), rồi mới mở
   file reviewer view và so (bài tập 1). Ghi nếu đã lỡ mở khối reviewer trước.
2. L-self bộ tối thiểu (WM26 trước), ghi vào mẫu hoặc nói trong chat để AI chép nguyên
   văn; cập nhật cột "Mức tôi đã đọc". Cân nhắc thêm P02 (nguồn quyết định PC2, §5.4).
3. Tự dẫn T03 kín sách (L3). Part 2: related work, DL Gate L, closeout, người đọc thật.
