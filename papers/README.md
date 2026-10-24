# Bắt đầu đọc paper ở đây

Người phụ trách: **Doan Van Tai** · 24/10/2026. Phân nhóm/thứ tự là AI đề xuất.

**Trước mỗi lần tìm/kiểm paper:** dùng [quy tắc + checklist 7 bước](../notes/literature/search_protocol.md).
Ưu tiên NDT/networking; 21 bài hiện có là kho tham chiếu, không phải yêu cầu đọc hết.

**Bạn đang học Part A: mở [Excel](paper_comparison_part_a.xlsx), tab `Bat_dau_Part_A`.**

| Thứ tự | Bài chính | Học để hiểu gì? |
|---|---|---|
| 1 | SOB14 — Strong, Oakley, Brennan | EVPPI: giá trị thông tin state |
| 2 | B82 — Birge | VSS: giá trị dùng stochastic model |
| 3 | P11 — Strong, Oakley | EVMI: học discrepancy khác dùng M0/M1 |

B82 chưa có PDF local; không ghi đã đọc full. MAB11, E07, SOC12 là ba nguồn bổ trợ gốc,
không cần đọc hết trước ba bài chính. Ba tài liệu tra cứu R10/R07/R18 không thành bài bắt buộc mới.

## 21 bài nằm ở đâu trong lộ trình?

| Nhóm | Các bài | Khi nào dùng? |
|---|---|---|
| [01 — Part A đọc chính](groups/01_Part_A_doc_chinh/README.md) | SOB14, B82, P11 | Học ngay, theo thứ tự trên |
| [02 — Part A bổ trợ](groups/02_Part_A_bo_tro/README.md) | MAB11, E07, SOC12; R10, R07, R18 | Tra khi cần, không đọc cả sách |
| [03 — Audit trước Phase 3](groups/03_Audit_truoc_Phase3/README.md) | R01, R04, R02, R03, R06, R25, R29 | Sau Part A; ưu tiên R01 → R04 để đối chiếu claims |
| [04 — Part B để sau](groups/04_Part_B_de_sau/README.md) | R43, R12, R32, R34, R51 | L2.4/L2.6/L2.7; chưa cần học lúc này |

15 bài shortlist là nguồn audit bổ sung, **không phải15 bài mới phải học hết cho Part A**.
Catalog59 nguồn ở review run là phạm vi tìm kiếm, không phải danh sách bài tập.
Nhóm04 chỉ gom bài audit liên quan Part B; không thay các paper gốc P12/P13 của lesson plan.

## Thư mục/file có chức năng gì?

| Nơi | Chức năng |
|---|---|
| `paper_comparison_part_a.xlsx` | Học/tra cứu: bắt đầu → phân loại → danh sách → ghi chú |
| `part_a_quick_view.csv` | Bảng nhanh6 nguồn Part A gốc; không phải toàn bộ21 bài |
| `groups/01…04/` | Mỗi nhóm có README, tên bài, mục đích và link nguồn |
| `PDF_local/01…04/` | Mở PDF theo thứ tự học; lối mở đến bản gốc, không là bài trùng |
| `PDF_local/Part_A/` | Kho PDF gốc của các lesson Part A |
| `PDF_local/review_2026-10-24/` | Kho PDF gốc tải trong lượt audit |
| `PDF_local/inbox/` | PDF bạn đưa thêm, ví dụ Secomandi R04 |
| `PDF_local/_backups/` | Sao lưu trước khi sắp xếp; không phải tài liệu học |
| `data/` | Dữ liệu nguồn cho Excel, phân nhóm và kết quả kiểm |
| `../notes/literature/` | Note/proof/đối chiếu; `review_runs/` giữ log và kết quả audit |

PDF thật nằm ở `~/papers/state-model-regret/`; `PDF_local` là alias local, Git bỏ qua.
Giữ nguyên11 PDF gốc, tạo11 lối mở theo nhóm;10 mục chưa có PDF vẫn có link/trạng thái thật.

## Các mã dễ nhầm

- `P11`, `R04`: ID paper ở hai danh sách khác nhau. **R04 không phải P04**.
- `PC1…PC6`: claims của đề tài. `P0…P3`: độ ưu tiên, không phải lesson/part.
- `A1…A6` ở cột Vùng: vùng tìm kiếm literature, không phải Part A/B.
- **R51 = P03** (DT²); **R43 không phải P12** (AVE2022 khác VE2020).

Nội dung AI/đọc thứ cấp không thành bạn đã đọc. Cập nhật tiến độ ở `Danh_sach`;
`Ghi_chu_doc` giữ ghi chú và vị trí nguồn. Phân nhóm không đổi contract/claim/Gate.

Tái tạo: `.venv/bin/python tools/paper_library/build_notes.py`.
Builder giữ mức bạn đã đọc và ghi chú hiện có theo ID.
[Kiểm phân loại](data/verification.json) · [Kiểm nguồn](data/classification_source_check.json)
· [PDF gốc/lối mở](data/classification_manifest.json).
