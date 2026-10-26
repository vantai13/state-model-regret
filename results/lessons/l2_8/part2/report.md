# L2.8 Part2 — kết quả thực hiện,26/10/2026

Người phụ trách: **Doan Van Tai** · AI-assisted, chưa L-self/Gate.

**Đã hoàn thành:** primary targeted R01/R02/R04 và3nguồn mới được tác giả duyệt
NDT26/WM26/AIS22; ghi6notes, version/hash/phần đọc, R04→plant mapping, bốn kết
luận vùng, K-RM1–3 và judgment dependencies. Excel13→19, giữ13progress/notes.
PDF lưu ngoài Git, chỉ bảng/notes/code/results được publish.

**Phát hiện:** RM đã có information-driven approximate-policy harm và điều kiện
non-deterioration. WM26 có center×response2×2repair; NDT26 có fidelity gate và
utility regret trong Open RAN; AIS22 có model/state adequacy dưới partial
observations. Không nhận generic2×2, information-harm hoặc decision fidelity là
mới. R04 cho sufficient diagnostic, chưa predictor H1 dùng được trước outcomes.

## Kết quả đã chạy

| Kiểm | Kết quả | Điều kiện/giới hạn |
|---|---:|---|
| R02 không re-solve | **14.586588671** revenue units | Capacity2,fares10/2,Poisson rate1/class,horizon2 |
| R02 re-solve t1 | **14.079588239** revenue units | Cùng process và initial allocation(2,0) |
| Thiệt hại re-solving | **0.507000431** revenue units |18aggregatecases,không tail truncation; Decimal50/70digits,khôngMC/seed/CI |
| V1 diagnostic | **GS=−1/4 packet·s** | Hi predicted gain1/2 nhưng true gain−1/2; hai mode equiprobable; đọc frozen toy,khônggrid |
| Excel | **19nguồn/3sheets**,0PDF nhúng |6AI-T mới,13mức đọc+13notes cũ giữ nguyên |
| Artifact audit | **PASS** |1.186protected files,52legacy manifest entries,6PDF hashes/pages/renders,PC historical prefix giữ nguyên |

R02 §5/Example1/Eq10 conditional values cũng khớp:8.963616765→7.585446706.
Đây là analytic replay của một ví dụ, không simulation toàn paper hoặc2×2RM.

## Commands thực tế

```bash
.venv/bin/python -B experiments/lessons/l2_8_resolving.py
.venv/bin/python -B tools/paper_library/build_notes.py
.venv/bin/python -B experiments/lessons/audit_l2_8_part2.py
git diff --check
```

- Generator/math: **PASS**; CSV18rows và V1diagnostic2rows.
- Workbook builder/ZIP/links/localPDF checks: **PASS**.
- Audit: **PASS cho artifact còn lưu**; không chứng nhận search raw/ranking,
  toàn scientific lesson, hypothesis, novelty hoặc tác giả đã đọc.
- Không chạy MATLAB/world-model/JMLRpaper code, không grid/held-out outcomes.

## Tìm kiếm/truy cập thực tế và limitation

A1 44,A2 45,A3 60,A4repeat20=**169screening events** trong20call checkpoints,
không169unique papers/full reads. Sau VPN,3Scholar retries thành công và R02
CiteSeerX PDF lấy được; publisherR02 vẫn403, A3q1Scholar vẫntimeout, S11citation
API vẫn429 cảretry nên dùngprovider fallback ghi riêng. A4repeat tìm lại RM
family/R01, đạt same-kind result check, không identical ranking.

**Thiếu raw từng rank của các calls trước resume:** ledger giữ query/tool/filter,
số đếm/examples/checkpoint; không thể independent audit toàn per-rank decisions
hoặc tổng unique candidates. Không tạo169CSVrows giả. Không đạt2×20zero-new
stopping rule; dừng bounded scope/budget và targeted answers. Đây là limitation
thực, vì vậy **toàn L2.8 còn PARTIAL**, không full search reproducibility/coverage.

## File tra cứu

- [Bài ngắn/crosswalk/4region conclusions](../../../../notes/literature/literature_audit_part2.md).
- [Excel](../../../../papers/paper_comparison.xlsx), [catalog](../../../../papers/data/catalog.json), [workbook check](../../../../papers/data/verification.json).
- [Generator](../../../../experiments/lessons/l2_8_resolving.py), [audit source](../../../../experiments/lessons/audit_l2_8_part2.py).
- [Config](config.json), [18caseCSV](cooper_example1.csv), [V1diagnostic](v1_diagnostic.csv), [mathJSON](math_checks.json).
- [Source versions/hash/read scopes](source_access.json), [approval](author_approval.json), [reading card/forecasts](reading_card.md).
- [Call ledger](search_calls.json), [search log](../../../../notes/literature/search_log.md).
- [VerificationJSON](verification.json), [math log](run.log), [audit log](audit.log).

Không tạo chart vì chỉ vài số; không có paper PDFs trong Git.

**Còn mở:** tác giả Understanding/L-self, L2.9 prior-boundary decision và A05
chọn/test null/H1; P02 full text của L2.7 vẫn BLOCKED, không được đọc lại lượt
này. Không còn HOLD vì “chưa đọc R02/R04”, nhưng PC3formalL2.9/PC4A05judgment
vẫn HOLD. PC forecasts,contract,G1/HOLDPhase4 không đổi. Khác regime/estimand
với prior chưa tự chứng minh contribution; chưa mở Phase3.
