# L2.7 Part B — kết quả thực hiện26/10/2026

Người phụ trách: **Doan Van Tai**. **PartB hoàn tất artifact kỹ thuật**;
toàn L2.7 vẫn còn primary P02 của PartA và author Understanding/L-self/Gate.
Không tự đổi contract/PC/K5/thresholds hoặc bắt đầu Phase3/L2.8.

## Đã thực hiện

- [P12](../../../../notes/literature/papers/P12.md) official NeurIPS2020
  PDF12trang, AI-T Eq2/Definition1–2/Properties1–4; xem Definition/Fig1/PDF3.
  Không full-read proofs/experiments/A.1.2; mức T thay vì A của lesson.
- [R43](../../../../notes/literature/papers/R43.md) official abstract AI-A lượt
  này; giữ riêng archived AI-T24/10 provenance. Không tải R43 PDF hoặc thêm lại
  reading list cũ. [Version/phạm vi/hash/access errors](source_access.json).
- Lưu [OεRE](../../../../notes/literature/terms.md),
  [bài ngắn và đáp án AI](../../../../notes/literature/model_equivalence.md),
  PC5/S0 + K-M6–7 trong prior boundary, matrix/already-implied/log,
  [L3.3/A05 queue](../../../../notes/lessons/L3.3_equivalence_queue.md).
  OεRE và numeric-label helpers là draft/reporting proposal, chưa contract-adopted.
- [Excel](../../../../papers/paper_comparison.xlsx)12→13unique works, chỉ thêm
  P12; giữ12notes và12author progress cũ. R43 tra bổ sung ngoài bảng.
- Keyword query lesson thực chạy trả12result titles, đa phần index/aggregation
  pages, giữ0. [Danh sách/query/limitations](keyword_screen.json); không phải
 12papers đọc, không negative field audit hoặc đủ luật2×20.

## Commands và kết quả thực

```bash
.venv/bin/python -B experiments/lessons/l2_7_equivalence.py
.venv/bin/python -B tools/paper_library/build_notes.py
.venv/bin/python -B experiments/lessons/audit_l2_7_part_b.py
git diff --check
```

**27/27checks PASS**,625exact two-state teaching cases,625CSV rows được auditor
đối chiếu bằng true/model action-cost enumeration riêng. Fraction arithmetic,
seed **N/A**, không RNG hoặc Monte Carlo. Không simulation paper/plant hoặc
outcomes main/held-out. V1 dùng frozen artifact, không phải experiment mới.

| Ví dụ | S0 model gain/Cref | S1 model gain/Cref | Kết luận đúng phạm vi |
|---|---:|---:|---|
| V1 frozen, Cref1,25packet·s | 0% | 20% | Equivalent dưới S0, không dưới S1 với biên0,5% |
| Hai state, một state margin0,01 | 0% | 1/1999≈0,050025% | Chọn sai tại một state vẫn đạt regret equivalence |
| Hai state có mean gap error0 nhưng local errors đảo dấu | 0% | 2/39≈5,128205% | S1 cần Eabs(error), không dùng abs(Eerror) |

Ví dụ ngoài V1 dùng arbitrary cost units, Stay10; không là ms hoặc measurement
network. Rare-state example có expected gap error0,002 dù state error2; chỉ
mean absolute error nhỏ là đủ cho bound S1, không cần nhỏ ở mọi x.
Một ví dụ khác có Γ≠0 nhưng cả hai pipelines equivalent: Γ không tự là
equivalence-boundary crossing. Common cost bias+2 vẫn giữ action/regret0.

| Cách khai báo K, **chưa chọn** | Main | Held-out |
|---|---|---|
| List M19–M22 | 4cells | 0 |
| κ=3,A/Bq90,h8,candidate | M19–M22 | 0 |
| κ≥2,A/Bq90,h8,candidate | M19–M22 | R03,R04 |

58coordinate-only rows (38main+12held-out+6controls+2probes),174membership rows.
Đây là metadata/design eligibility, không đánh giá performance. R03/R04 chỉ
η0,5; không chứng nhận η0,75 hoặc mọi κ≥2. Nếu test cell trượt, không suy unique
boundaryκ2–3 nếu chưa có monotonicity/controlled coordinates. λA được anchor
theo lát; không lấy riêng λA/p_sw của held-out làm predictor.

**7numerical interval examples/4CI input examples:** Ĝ0,001±0,001 nằm trong
biên; Ĝ0,003±0,0025 cắt biên→HOLD. Exact certified closed interval chạm0,005
vẫn thỏa≤; MC CI chạm biên không đạt strict TOST containment. Cref uncertainty
[0,9;1,1] khiến Ĝ0,0048 chưa được certified dù chia point Cref1 trông đạt.
Cref0 không chia; vượt numerical budget phải HOLD. Không tạo CI từ samples,
không chạy TOSTER. Đây không chứng nhận numerical error của solver thật.

**Restricted VE illustration:** hai kernels identity/swap cùng reward1,γ1/2
cho equal updates trên V={0}, khác khi thêm v=[0,1]. Với γ0, mọi update không
thấy kernel; không viện dẫn uniqueness dynamics của all-function case ở γ0.
Đây là Eq2 counterexample/caveat, không replication/theorem audit toàn P12.

## Những điểm đã sửa so với hướng dẫn

1. S1 expected gap-error bound không đòi pointwise-small errors; sign quyết
   định action cùng tie rule, true margin quyết định loss.
2. VE tổng quát không tự là mức(a): chỉ macro one-step/reward−J embedding
   cho exact J equivalence. Không kết luận toàn P12 không có performance/regret
   analysis từ những section đọc; không claim khác mọi AVE từ abstract.
3. Γ≠0 chưa đảm bảo crossing; K dạng list vẫn hợp lệ cho finite claim nhưng
   không tự kiểm generalization. Không suy unique κboundary từ hai slices.
4. Exact-definition closed boundary khác strict MC containment; vùng xám
   (εE,εR), không gồm εR. Interval cắt biên là chưa chứng nhận, không tự bác claim.
5. arxiv P12 có commentNeurIPS-2020; R43 có old AI-T note. Không hạ mức/provenance
   cũ hoặc biến lần đọc primary hiện tại thành T theo archived summary.
6. Giữ D25/A05 cho việc freeze/split/held-out, không tự theo A06 của lesson để
   đổi protocol. OεRE ở terms không làm phát sinh contract edit/DL adoption.

## Kết quả lưu ở đâu?

| Loại | File thực có |
|---|---|
| Code | [generator](../../../../experiments/lessons/l2_7_equivalence.py), [auditor](../../../../experiments/lessons/audit_l2_7_part_b.py), [workbook builder](../../../../tools/paper_library/build_notes.py) |
| Log | [run.log](run.log), [audit.log](audit.log), [workbook_build.log](workbook_build.log) |
| Số liệu | [toy_results.json](toy_results.json), [625gap cases](gap_bound_sweep.csv), [numeric intervals](numeric_intervals.csv), [CI inputs](CI_examples.csv), [K membership](K_membership.csv) |
| Config/protection | [config.json](config.json), [protected_before.json](protected_before.json), [grid coordinate projection](grid_coordinates.json) |
| Audit/source | [verification.json](verification.json), [source_access.json](source_access.json), [keyword_screen.json](keyword_screen.json), [Excel verification](../../../../papers/data/verification.json) |

PDF1bài/1render ở ngoài Git, paths/hash trong source_access. Không tạo chart vì
bảng đủ giải thích. Không tạo plant metrics, null fit/prereg, held-out CI/outcomes.
Backup Excel/catalog trước sửa:
`~/papers/state-model-regret/archive/2026-10-26_before_l2_7_part_b/`.
Audit kiểm **1163protected files**,52legacy-manifest entries,12notes/progress cũ,
membership projection và paper provenance. Excel3tabs/13unique/10PDFlocal/0embedded.

## Gate và việc còn mở

PartB technical evidence đủ theo phạm vi named sources, definitions, bài tập,
PC5/K-M và queue. **PC5 chưa được kiểm trên grid**, luật K5/null/split chưa chọn.
R43 primary full definitions/performance bounds còn A3/A4 audit; keyword query
nhiễu không cấp novelty clearance. L-self/Understanding/Gate/L2.8–2.9 chưa có
human confirmation. PartA còn P02 full-text BLOCKED, không đóng toàn L2.7.
SAS guide pages timeout, P12 Bibtex link lỗi; đã ghi giới hạn và chỉ dùng
official CRAN documentation/primary PDF đọc được. Contract/G1/HOLD giữ nguyên.
