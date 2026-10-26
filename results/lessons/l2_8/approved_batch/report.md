# Đợt đọc được duyệt — IA26, DTS25, CEN26, CEH23 (26/10/2026)

Người phụ trách: **Doan Van Tai**. Bạn duyệt và tự tải 9 PDF ([quyết định](author_approval.json)).
Đọc targeted 4 nguồn được chọn; mức đọc ghi theo quy tắc repo (AI-T/AI-F), **chưa L-self**.

## Kết quả

| Nguồn | Trả lời câu hỏi | Ảnh hưởng nhãn tạm |
|---|---|---|
| [IA26](../../../../notes/literature/papers/IA26.md) | Định giá thông tin theo decision-relevant predictability; Định lý 3 (§3.4): fresh-local thắng ⇔ τ/T > ½log(1/(1−η_S(0))); môi trường ngoại sinh, **loại trừ controlled queueing** (§1 tr3) | PC2, PC6 NARROW giữ |
| [DTS25](../../../../notes/literature/papers/DTS25.md) | Bài ý tưởng 2 trang, chưa thí nghiệm | Không đổi |
| [CEN26](../../../../notes/literature/papers/CEN26.md) | Replay quyết định, reference là runtime thật; CESNET vi phạm 20,5%→9,0% | PC5 NARROW giữ |
| [CEH23](../../../../notes/literature/papers/CEH23.md) | Cận CE–tối ưu O(√var)/O(var) khi động học **affine trong kỳ vọng** (Assumption 5); queue phản xạ vi phạm | PC5 NARROW giữ; thêm H1-Q04 |

Nguồn còn lại: R06 (abstract đủ), 2505.04879 (background), 2211.01961 và 2605.24318 (để sau),
2601.23051 (bỏ khỏi hàng đợi) — PDF lưu thư viện. MOR 2025.0898 không có PDF.

## Commands

```bash
.venv/bin/python -I -B experiments/lessons/l2_8_approved_batch_catalog.py   # +4 hàng, 23 nguồn
.venv/bin/python -B tools/paper_library/build_notes.py                       # PASS
.venv/bin/python -I -B experiments/lessons/audit_l2_8_approved_batch.py      # verification.json
.venv/bin/python -m pytest -q
git diff --check
```

Kết quả thực: catalog script +4 hàng (23 nguồn); `build_notes.py` PASS (21 PDF local,
23 mức tác giả "Chưa có xác nhận"); `audit_l2_8_approved_batch.py` **PASS**
([verification.json](verification.json)): 9 PDF đúng hash/số trang, 12 trích dẫn có trong text,
19 record cũ không đổi, 0 nhãn tạm đổi, 0 record L-self thêm. `pytest -q` 202 passed;
`git diff --check` sạch.

## Còn mở

L-self của bạn cho mọi nguồn (0/23); Gate L vẫn HOLD. Để một nguồn thành L-self: bạn tự mở
đúng phần ghi ở note, rồi nhắn 2–3 câu bằng lời mình để ghi vào
[author_reading_record](../../../../notes/literature/author_reading_record.md).
