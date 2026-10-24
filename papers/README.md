# Paper — Part A

Người phụ trách: **Doan Van Tai** · 24/10/2026.

Mở **[Excel so sánh](paper_comparison_part_a.xlsx)**:

- **So_sanh_Part_A:** 6 bài; topic, năm, tác giả, claim, điểm so sánh và giới hạn.
- **Tien_do_doc:** mức AI đã đọc, phần đã đọc, mức bạn xác nhận, nguồn và link PDF.
- **Huong_dan:** cách dùng và ý nghĩa các trạng thái.

[Xem nhanh trên GitHub (CSV)](part_a_quick_view.csv).

Đọc trước **SOB14 → B82 → P11**. MAB11, E07 và SOC12 là nguồn bổ trợ.
Nội dung so sánh là AI đề xuất; không xác nhận novelty hoặc việc bạn đã đọc.

PDF thật ở `~/papers/state-model-regret/Part_A/`. Trên máy này có thể mở qua
`papers/PDF_local/Part_A/`; alias này được Git bỏ qua. PDF không push GitHub.
Bài chưa tải được vẫn có DOI/URL và trạng thái thật trong Excel.
Hiện có PDF **SOB14, P11, SOC12**; **B82, MAB11, E07** chưa tải được.

Tái tạo: cài `tools/paper_library/requirements.txt`, chạy
`.venv/bin/python tools/paper_library/build.py --download` từ repo root.
Builder tạo lại từ `data/catalog.json`; lưu các sửa tay trong Excel trước khi chạy.
[Kết quả kiểm](data/verification.json) · [Tình trạng PDF](data/pdf_status.json).
