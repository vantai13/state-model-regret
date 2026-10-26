# L2.8 Part1 — audit theo claim,26/10/2026

Người phụ trách: **Doan Van Tai**. Đã thực hiện phần phương pháp/thẻ và A4
bounded screening; **không hoàn tất toàn bộ7việc của L2.8**. Nội dung cuối tài
liệu đặt primary deep read và A1–A3 vào Part2; các việc đó ghi pending dưới đây.

## Đã làm và kết quả thực

- [4session cards](../../../../notes/literature/audit_sessions.md), PC/câu chặn,
  2queries/anchor/forward/budget/Tier/stopping rule.
- A4 Google Scholar qua paper-search: **20+15records**; forwardR02 qua Semantic
  Scholar **20records**. **55lượt sàng/54định danh**, không54works đã dedup mọi
  version hoặc full reads. Same forwardpage gọi2lần để lưu compact response,
  không đếm40. Total citing papers không trả; next20 còn mở.
- R01/R02/R04: Crossref metadata, official publisher abstracts **AI-A lượt
  này**. R01/R04 có archived AI-T24/10, provenance được kiểm riêng. Không đọc
  lại full primary hoặc tự điền L-self; không dùng bảng10/10/25/34 của lesson.
- **3new Tier2proposals**, có DOI/arxiv chính thức, chỉ trong log/screening,
  chưa approval PDF/note; không tải PDF, không thêm reading list/Excel. Ba Tier1
  ưu tiên vẫn là R01/R02/R04 tác giả đã chỉ định, full conditions còn cần kiểm.
- Cập nhật matrix/log/already-implied/prior threat appendix và
  [bài ngắn, tự kiểm,4status summaries](../../../../notes/literature/literature_audit_part1.md).
  Không đổi PC labels/forecasts/RQ/contract/null/K5 hoặc chạy Phase3.

**Điểm đã xác nhận:** R02 abstract báo allocation updating có thể làm giảm
expected revenue; R01 abstract phân biệt corresponding allocation policy và
một số bid-price policies; R04 abstract đưa sufficient re-solving conditions.
Không coi re-solving là D20, stochastic approximation là exactM1 hoặc kết quả
RM là Γ đo trong routing. V1 pattern không tự chứng minh mới hoặc trùng hẳn prior.

## Đã chạy và kiểm

```bash
.venv/bin/python -B experiments/lessons/audit_l2_8_part1.py
git diff --check
```

Tool calls/query/rank/error/filter được lưu trong search_records/search_log;
2GoogleScholar calls và forward2calls cùng page,3Crossref namedDOIs +1Crossref
candidate DOI; web official3publishers và3candidate identity routes.
Source cards/notes là AI-only; không claim GoogleScholar trả đầy đủ corpus.

Auditor **PASS**:55rows/counts/ranks,3proposals không trùng,59protectedfiles,
52legacy-manifest entries và2archived-note hashes. Workbook/catalog/verification
giữ byte-identical, vẫn13nguồn. Không tạo test giả kiểm hypothesis từ literature.

Kiểm toán học exact Fraction:9cases GS<0/GSgivenM1≥0 đều choΓ>0. Jensen toy
one-slot, q0=0,capacity10packet,B={2,14}đồng xác suất: expected backlog
**2packet**, mean-rollout backlog**0packet**. Seed N/A, không RNG/MC hoặc plant
grid. Đây là minh họa marginal; M0 thật dùng conditional mean paths từng x rồi
averagecost trên belief. Γidentity cần shared law/objective/actions và VOI assumptions.

## Output

| Loại | Nơi lưu |
|---|---|
| Bài/checklist/cards | [bài Part1](../../../../notes/literature/literature_audit_part1.md), [4cards](../../../../notes/literature/audit_sessions.md) |
| Query/screening | [search_records.json](search_records.json), [screening.csv](screening.csv), [search log](../../../../notes/literature/search_log.md) |
| Source/protection | [archive_provenance.json](archive_provenance.json), [protected_before.json](protected_before.json) |
| Math/verification | [math_checks.json](math_checks.json), [verification.json](verification.json), [audit.log](audit.log), [auditor source](../../../../experiments/lessons/audit_l2_8_part1.py) |

Không tạo simulation config, PDF mới hoặc biểu đồ; audit budgets/query config
nằm trong cards và JSON. Không tạo measured network metrics hay held-out outputs.

## Trạng thái và bước còn lại

| Việc trong7-item checklist của toàn lesson | Trạng thái |
|---|---|
| 4cards | Đã lưu |
| A4 rerun | Đã chạy bounded pass; không exhausted và không đạt2×20 |
| R01/R02/R04 primary deep read | **Pending Part2**, current abstract+historical-note provenance không thay được |
| A1–A3 | **NOT RUN**, không coi old lookups/keywordL2.7B thay audit |
| Tier classify | Screening tạm;3namedTier1 +3newTier2proposals, chưa full-text judgment |
| Matrix/log/already-implied | Đã cập nhật, không giả claim clearance |
| 2sentences/vùng | Đã lưu; A1–A3 ghi rõ chưa chạy, A4 HOLD mapping |

Query2chỉ15 và có candidates, forward còn nextpage; dừng theo Part1 bounded
scope, không theo negative-field stopping rule. Current full-primary đọc0bài;
wholeL2.8/affected prior-clearance judgments/L-self/L2.9 vẫn OPEN/HOLD. P02
fulltext L2.7A vẫn BLOCKED, không được phiên này giải quyết. Không đổi nhãn PC
hoặc tự chọn null để xử lý threat; bước sau là primary Part2 và các sessions còn lại.
