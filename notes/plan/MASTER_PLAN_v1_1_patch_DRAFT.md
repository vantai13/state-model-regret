# Bản vá đề xuất MASTER PLAN v1.0 → v1.1 (NHÁP, chờ tác giả)

Người phụ trách: **Doan Van Tai**. AI (Claude) soạn theo lesson L3R.8 Bước 8 và PHASE_3R Phụ lục D.

- **File gốc không bị sửa:** `~/dacn/quá trình thực hiện/MASTER_PLAN_RESEARCH.md` (v1.0, 06/10/2026, ngoài repo).
- Tác giả áp bản vá này bằng tay sau khi duyệt.
- Nguyên tắc: bản tối thiểu, chỉ để MASTER PLAN không còn mâu thuẫn với PHASE_3R (file phase thắng, XIX.5).

## §0 Bảng trạng thái — thay các dòng sau

| Mục | Giá trị mới |
|---|---|
| Ngày cập nhật | ⟨ngày áp bản vá⟩ |
| Phase hiện tại | **Phase 3R → Phase 4** (confirmation v1.3, chạy đúng một lần) sau khi Gate 3R có nhãn |
| Lesson hiện tại | L3R.8 (freeze, người đọc, Gate 3R, closeout); sau đó Phase 4 Bước 0 (nối runner) |
| Contract | `contract-v1.3` (tag) có mục DEFERRED; numerics card v2: `numerics-v1.3.1-lean` |
| Gap maturity | **G1**, không đổi; pilot và regime map không nâng G |
| Quyết định gần nhất | Phase 3 REFORMULATE (Gate A); L3R.7 đóng gọn (DL-095–096); Gate 3R ⟨nhãn⟩ |
| Evidence đang có | Verification engine population (E1, mức mô hình); discovery pilot và regime map; **chưa có confirmation, chưa có network evidence** |
| Blocker | Điều kiện vào Phase 4: runner; quyết định D22 và người đọc (DL-097/099). **Thay câu cũ** "blocker = audit engine + realism", nay đã lỗi thời |
| Việc đang HOLD | Realism và vận hành (Phase 6/7); novelty (Phase 8) |

## I.1 Hành trình — thêm sau "Thế hệ 3"

> **Thế hệ 3b (26–30/10/2026).** Phase 3 đóng với REFORMULATE → v1.3 bước 1 (P(a) PASS, P(b) và P(c) FAIL) →
> population pilot (discovery) → regime map (discovery) → Phase 3R: T07, audit engine, realism (UNSOURCED),
> contract v1.3, card v1, rồi L3R.7 đóng gọn bằng card v2 (lưới tốc độ 1/100) và numerics (640, 4).

## I.5 Gap maturity

Giữ G1. Thêm câu: "pilot và regime map là discovery, không nâng G-level".

## Part IV (bảng phase), Part VI (chi tiết phase), Part XIII (gate) — theo PHASE_3R §22.1

| v1.0 | v1.1 |
|---|---|
| Phase 3 analytical pre-spike, Gate A | Phase 3 (đã đóng: REFORMULATE) + **Phase 3R** (Gate 3R ≈ Gate B) |
| Phase 4 controlled core, Gate B | Gộp vào Phase 3R (MC thành verification ở L3R.3; baseline vận hành sang Phase 7) |
| Phase 5 confirmation, Gate C | **Phase 4: confirmation v1.3**, Gate C |
| Phase 6 mechanism, Gate D | **Phase 5: mechanism** (kèm D22, MI), Gate D |
| Phase 7 independent validation, Gate E | **Phase 6: independent validation**, Gate E |
| Phase 8 practical relevance, Gate F | **Phase 7: practical relevance** (realism), Gate F |
| Phase 9 synthesis, Gate G | **Phase 8: synthesis + final novelty audit** (L8), Gate G |
| Phase 10 paper | **Phase 9: paper** |

Part VI: chèn Phase 3R (trỏ tới `notes/phases/PHASE_3R.md`); đánh số lại Phase 4–9 như bảng trên.

## Part XV Kill criteria — thêm (từ PHASE_3R §22.7)

| ID | Khi nào | Hệ quả |
|---|---|---|
| K12 | Vùng hypothesis OUT ở mọi bối cảnh realism đã chọn | NARROW về mức mô hình, hoặc PIVOT sang equivalence trong vùng thực tế |
| K13 | Engine không verify được bằng phương pháp độc lập, kể cả sau khi sửa | HOLD; không khắc phục được → DROP estimand đó |
| K14 | Mọi effect còn lại chỉ là identity, hoặc trùng K-RM/EVMI ở cả ba trục E, M, R | NARROW về characterization có điều kiện, hoặc dừng |

## Phụ lục C Changelog — thêm dòng

| Version | Ngày | Thay đổi | Lý do |
|---|---|---|---|
| v1.1 | ⟨ngày⟩ | Bảng phase/gate theo PHASE_3R §22.1; §0; I.1 thế hệ 3b; K12–K14 | Reformulation v1.3. Bài học ER1: L3R.7 phình vì làm tròn 1/1000 và chứng chỉ chặt hơn mức claim cần |
