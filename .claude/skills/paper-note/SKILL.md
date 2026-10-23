---
name: paper-note
description: Tạo hoặc cập nhật paper note theo template A.5 (notes/literature/papers/Pxx_*.md) cho một paper cụ thể, kèm mức đọc, Fact/Claim/Evidence/Inference và dòng trong literature matrix. Dùng khi tác giả nói "ghi chú paper", "đọc paper P01", "paper note", "điền matrix", hoặc đưa DOI/arXiv ID/tiêu đề cần đọc cho Phase 2.
argument-hint: "[Pxx] [DOI | arXiv ID | tiêu đề]"
---

# paper-note — ghi chú paper đúng kỷ luật của repo

Mục tiêu: tác giả đọc paper nhanh hơn và trung thực hơn. Skill này **không** đọc thay tác giả, **không** kết luận novelty, **không** đổi G-level hay gate.

## Bước 1 — Xác định đúng paper

1. Từ DOI / arXiv ID / tiêu đề, lấy metadata từ nguồn gốc:
   - arXiv ID → `mcp__arxiv__get_abstract`.
   - DOI → `mcp__papersearch__get_crossref_paper_by_doi`, hoặc skill `paper-lookup` (OpenAlex/Crossref).
   - Chỉ có tiêu đề → tìm ở ít nhất hai nguồn (ví dụ `search_openalex` và `search_dblp`), so tiêu đề, tác giả, năm.
2. Ghi **phiên bản thực đọc** (preprint vX hay bản xuất bản), venue, năm, URL. Hai bản có thể khác nội dung.
3. Ghi mọi lần tìm vào `notes/literature/search_log.md` bằng skill `search-log`.

## Bước 2 — Lấy full text hợp pháp

Thứ tự: arXiv (`mcp__arxiv__download_paper`, rồi `get_paper_outline` + `read_paper_section`) → bản open access qua Unpaywall (`mcp__papersearch__search_unpaywall`, hoặc `paper-lookup`) → trang tác giả hoặc repository của trường.

- **Không bao giờ dùng Sci-Hub hay mirror lậu.** Tool Sci-Hub đã bị chặn trong `.claude/settings.json`; đừng tìm đường khác.
- Không có bản hợp pháp: ghi `Mức đọc: abstract-only` và bảo tác giả lấy qua thư viện UIT, liên thông thư viện, hoặc email tác giả.
- PDF chỉ lưu trong `downloads/` hoặc `papers_local/` (đã gitignore). **Không commit PDF.**

## Bước 3 — Điền note

Tạo `notes/literature/papers/Pxx_<họ-tác-giả-đầu><năm>.md` bằng cách copy [template.md](template.md) (template A.5 của master plan). Đầu file ghi provenance:

```
> Người phụ trách: Doan Van Tai · ngày · Phần (AI trích) do Claude trích từ nguồn, tác giả cần kiểm lại với bản gốc.
> Mức đọc: full / targeted sections (§…) / abstract-only — ghi đúng phần ĐÃ mở được.
```

Quy tắc điền:

| Ô | Ai điền | Cách điền |
|---|---|---|
| Problem, Input, Output, System/action, Objective, Assumptions, Oracle, Method, Experiment, Known result | AI có thể trích | Mỗi ý kèm §/equation/figure. Đánh dấu `(AI trích)`. Không thấy thì ghi `Unclear`, không đoán |
| Fact / Claim / Evidence | AI có thể trích | Tách đúng bốn loại. Claim của tác giả paper ≠ Fact |
| Inference của tôi | **Tác giả** | Ghi `TODO(tác giả)` và 2–3 câu hỏi gợi ý, ví dụ: "Giả định nào của paper không mang sang được action làm đổi tải?" |
| Evidence có đủ cho claim không? | **Tác giả** | `TODO(tác giả)` + câu hỏi gợi ý. AI chỉ được nêu chỗ claim rộng hơn setting đã test, kèm §, trong khối "Gợi ý của AI — không phải kết luận" |
| Overlap, Khác biệt, Effect on gap | **Tác giả** | `TODO(tác giả)`. Effect on gap chỉ nhận: weaken / kill / refine / chưa rõ |

Trích dẫn: tối đa **một** câu trích nguyên văn mỗi paper, dưới 15 từ, có dấu ngoặc kép và §. Còn lại diễn giải bằng lời mình.

## Bước 4 — Matrix

Thêm hoặc sửa một dòng trong `notes/literature/matrix.md` (tạo file với header ở cuối [template.md](template.md) nếu chưa có). Ô chưa kiểm ghi `Unclear`. Cột "Effect on gap" để `TODO(tác giả)`.

## Bước 5 — Báo lại cho tác giả

Trả lời ngắn: đường dẫn note, mức đọc thật, danh sách `TODO(tác giả)`, và một câu hỏi phản biện quan trọng nhất về paper đó.

## Không làm

- Không viết "paper này chưa làm X nên đây là gap". Limitation ≠ research gap. "Chưa tìm thấy" ≠ "chưa ai làm".
- Không sửa `notes/02_decision_log.md`, gate, G-level, hoặc đánh dấu `[kín sách]` thay tác giả.
- Không thêm paper vào file `.bib` khi chưa kiểm metadata (dùng `citation-management`, `validate_citations.py --check-dois`).
