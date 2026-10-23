---
name: search-log
description: Ghi mỗi phiên tìm literature vào notes/literature/search_log.md (ngày, nguồn, query, số kết quả, số giữ lại, lý do, lỗi) và hướng dẫn citation chaining backward/forward. Dùng khi tìm paper cho Phase 2, khi tác giả nói "tìm paper", "search log", "citation chaining", "forward citation", "ai trích paper này", hoặc sau bất kỳ lần gọi tool tìm paper nào.
argument-hint: "[câu hỏi tìm kiếm]"
---

# search-log — tìm literature có dấu vết

Mục đích: một năm sau, tác giả (và reviewer) biết **đã tìm gì, ở đâu, bằng từ nào, bỏ gì và vì sao**. Không có log thì câu "chưa tìm thấy prior" không kiểm được.

## Trước khi tìm

1. Viết **một câu hỏi tìm kiếm** gắn với claim cụ thể trong `notes/01_claim_boundary_*.md` (ví dụ: "Đã có ai đo giá trị của state refresh khi action làm đổi tải chưa?").
2. Chọn họ từ khoá. Thử nhiều cách gọi vì mỗi cộng đồng dùng từ khác: value of information + routing/queue · expected value of model improvement · decision-focused / value-aware model learning · stale / old information + load balancing · model mismatch vs state estimation error + predictive control · transient queue approximation + decision · digital twin fidelity + decision.

## Khi tìm

Công cụ có sẵn trong repo:

| Việc | Tool |
|---|---|
| Tìm rộng CS | `mcp__papersearch__search_dblp`, `search_openalex`, `search_semantic`, `search_crossref` |
| Preprint | `mcp__arxiv__search_papers` |
| Backward + forward của một paper arXiv | `mcp__arxiv__citation_graph` (Semantic Scholar) |
| Forward/backward bất kỳ DOI | skill `paper-lookup` → OpenAlex. Forward: `https://api.openalex.org/works?filter=cites:W…`; backward: `filter=cited_by:W…` (W… là OpenAlex ID của seed, lấy từ `https://api.openalex.org/works/doi:<DOI>`) |
| Bản open access | `mcp__papersearch__search_unpaywall` |

**Kết quả rỗng hoặc lỗi KHÔNG phải bằng chứng "không có paper".** `paper-search-mcp` trả danh sách rỗng mà không báo lỗi khi mạng hoặc API hỏng. Gặp kết quả rỗng: thử nguồn thứ hai và ghi cả hai vào log.

## Ghi log

Thêm dòng vào `notes/literature/search_log.md`. Nếu file chưa có, tạo với header:

```markdown
# Search log — Phase 2
| Ngày | Câu hỏi (claim nào) | Nguồn/tool | Query nguyên văn + filter | Số KQ sàng | Số giữ | ID giữ lại | Lý do bỏ / ghi chú | Lỗi/rỗng |
|---|---|---|---|---|---|---|---|---|
```

Mỗi lần gọi tool tìm kiếm một dòng. Ghi query **nguyên văn** (kể cả filter, năm). Paper giữ lại: ghi DOI hoặc arXiv ID, không chỉ tiêu đề.

## Citation chaining

1. Chọn paper hạt giống (seed). Thứ tự ưu tiên của master plan (VIII.2), mã P theo Final Review §3:
   - P11 — Strong, Oakley (2014). *When Is a Model Good Enough? Deriving the Expected Value of Model Improvement via Specifying Internal Model Discrepancies.* SIAM/ASA JUQ 2(1):106–125. DOI 10.1137/120889563.
   - P12 — Grimm, Barreto, Singh, Silver (2020). *The Value Equivalence Principle for Model-Based Reinforcement Learning.* NeurIPS 2020.
   - P13 — Mathijsen, Zwart (2017). *Transient error approximation in a Lévy queue.* Queueing Systems 85:269–304. DOI 10.1007/s11134-016-9511-0.
   - P01 — Choudhury, Joshi, Wang, Shakkottai (2021). *Job Dispatching Policies for Queueing Systems with Unknown Service Rates.* MobiHoc 2021.
   - P02 — Poelman, Hegyi, Verbraeck, van Lint (2023). *Structure-free model-based predictive signal control: A sensitivity analysis on a corridor with spillback.* Transportation Research Part C 153, 104174.
   Kiểm DOI và tiêu đề bằng nguồn gốc trước khi ghi; đừng nhầm hai paper cùng tác giả (ví dụ P11 khác với Strong, Oakley, Brennan 2014 về EVPPI trong Medical Decision Making).
2. **Backward:** danh sách references của seed → sàng theo tiêu đề và abstract.
3. **Forward:** các paper trích seed → sàng, ưu tiên mới nhất.
4. Mỗi bước một dòng log, cột "Câu hỏi" ghi `chain: <seed> backward/forward`.
5. Dừng khi hai vòng liên tiếp không thêm paper nào đổi được claim boundary. Ghi lý do dừng.

## Báo lại cho tác giả

Tóm tắt: số phiên, số paper giữ, paper nào nên đọc bằng skill `paper-note` trước và vì sao (nó đe doạ claim nào). Không kết luận "gap tồn tại".
