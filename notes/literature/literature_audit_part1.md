# L2.8 Part 1 — audit theo claim, A4 screening

Người phụ trách: **Doan Van Tai** ·26/10/2026 · AI-assisted, chưa L-self.
Part1 dựng thẻ và chạy A4 có giới hạn. **Không ghi hoàn tất toàn L2.8**:
primary reading R01/R02/R04 và A1–A3 thuộc bước tiếp theo/Part2 của tài liệu.
Không đổi PC/contract/null/K5, không chạy Phase3 hoặc cấp novelty clearance.

## Đã chạy, phân biệt với ví dụ trong lesson

[Bốn thẻ A1–A4](audit_sessions.md) gắn PC3/PC4/PC5, câu chặn,2queryvariants,
anchor/forward và budget. A1–A4 là literature sessions, khác A01/A04/A05 experiments.

| A4 thực chạy | Sàng | Kết quả / điểm chưa đủ |
|---|---:|---|
| Google Scholar qua paper-search, query1 CE/info/reoptimization | 20records | Titles+search excerpts; không giả đọc full abstracts |
| Google Scholar, query2 DLP/resolving/RM/information | 15records | Provider trả15, không đủ20; có1candidate Tier2 |
| Forward từ R02 DOI, Semantic Scholar | 20records | First page offset0,next20; total không trả. Cùng page gọi2lần để lưu compact result, chỉ đếm20 |
| Known-item R01/R02/R04 | 3works | Crossref metadata + **official publisher abstract AI-A**; không full text lượt này |

[55screen rows/query/rank/decision](../../results/lessons/l2_8/part1/screening.csv),
[machine records](../../results/lessons/l2_8/part1/search_records.json).
35keyword+20forward là lượt records, không55paper unique hoặc55full reads.
Một DOI xuất hiện cảquery2/forward, không là hai work. Không dùng số10/10/25/34
trong lesson làm số liệu của phiên này. Không đạt2×20 zero-new-candidate rule;
forward còn continuation, dừng theo bounded Part1 pass, không kết luận field rỗng.

## Ba Tier1 đã được chỉ định — ưu tiên, chưa phán quyết PC

| ID/metadata | Official evidence đọc lượt này | Điều cần kiểm primary ở Part2 |
|---|---|---|
| R02 Cooper2002, Operations Research50(4):720–727, DOI10.1287/opre.50.4.720.2855 | Publisher **Abstract**: updating allocation có thể giảm expected revenue | Policy, timeline, comparator, assumptions và counterexample; không coi là D20 hoặc Γ measurement |
| R01 Chen/Homem-de-Mello, Annals OR177:91–114,2010; online25/08/2009, DOI10.1007/s10479-009-0603-7 | Springer **Abstract**: successive two-stage/simple-recourse programs không làm xấu corresponding allocation policy; property không giữ cho một số bid-price policies | Phân biệt allocation/bid-price, stochastic approximation vs exact M1; kiểm proposition/version trước transfer |
| R04 Secomandi2008, MSOM10(3):468–483, DOI10.1287/msom.1070.0184 | Publisher **Abstract**: sufficient conditions để control-algorithm re-solving không làm xấu performance | Kiểm consistency/accuracy, policy class và bound; không tự chọn null từ abstract |

[R01 publisher](https://link.springer.com/article/10.1007/s10479-009-0603-7),
[R02 publisher](https://pubsonline.informs.org/doi/10.1287/opre.50.4.720.2855),
[R04 publisher](https://pubsonline.informs.org/doi/10.1287/msom.1070.0184).
Archive đã có **AI-T24/10** cho R01/R04; đã kiểm provenance/path/hash, không hạ
record cũ thành “chỉ metadata”, không coi note cũ là primary vừa đọc lại.
R01 bảnTR trong note cũ không tự bằng VoR; PDF link OptimizationOnline của
lesson chưa đọc lượt này. Chưa nguồn nào thành tác giả L-self.

## Chỉ3candidate Tier2 mới, chờ duyệt trước PDF/note

| Candidate / identity kiểm | PC / lý do đáng kiểm | Giới hạn |
|---|---|---|
| Infrequent Resolving Algorithm for Online Linear Programming, Li/Wang/Zhang; DOI10.1287/moor.2025.0898, online16/09/2026/Crossref | PC3/PC4: re-solving schedule và regret của approximate control; query2 và forward cùng work | Online LP/demand learning, chưa same GS; chưa đọc theorem, không lấy2025 trong DOI làm publication year |
| Certainty Equivalence Control-Based Heuristics in Multi-Stage Convex Stochastic Optimization Problems; Chen Yan/Reiffers-Masson; arxiv2308.13166 | PC3/PC4: CE/decision-dependent noise/re-solving performance | Đã mở arxiv identity/abstract; chưa theorem transfer, journal status chưa kiểm |
| Reoptimization Nearly Solves Weakly Coupled Markov Decision Processes; Gast/Gaujal/Chen Yan; arxiv2211.01961, v2ngày06/05/2024 | PC3/PC4: repeated LP relaxation và performance; alternative mechanism prior | Multi-component asymptotic MDP, chưa controlled2×2 hoặc same regret; không gọi mọi reoptimization tương đương |

Nguồn kiểm: [Crossref/DOI](https://doi.org/10.1287/moor.2025.0898),
[arxiv2308](https://arxiv.org/abs/2308.13166), [arxiv2211](https://arxiv.org/abs/2211.01961).
Chỉ metadata/screening, **chưa tải PDF, tạo paper-content notes hoặc thêm Excel**.
Các hit chưa rõ khác vẫn ghi Unclear/not prioritized trong ledger, không bị bác
bỏ chỉ vì snippet. Ví dụ query1rank12/17 chưa xác minh identity/estimand.

## Đính chính và bài tự kiểm

CE có thể nói plug-in parameter, point-state estimate hoặc mean future noise.
D21 gần nghĩa thứ3: **mean rollout có điều kiện theo từng x, sau đó average cost
trên belief**, không thay cả current-state posterior bằng mean state hoặc luôn
đặt B=8. M1 là expected cost đúng conditional law, không một stochastic sample.

One-slot toy B∈{2,14},p=1/2,capacity10,q0=0: Ebacklog=2packet, backlog từ
mean B8=0. Đây là Jensen illustration, không conditional R2 hoặc grid outcome.
Γ=GSgivenM1−GS; với true-model VOI assumptions/shared law/objective/actions,
GSgivenM1≥0 nên GS<0⇒Γ>0 là **đại số**, không một phát hiện/measurement mới.
Đã kiểm9rational cases và toy bằng Fraction; chưa suy mechanism hoặc tần suất.

Đáp án tự kiểm AI: (1) claim-search cho tiêu chí giữ/bỏ và dừng; (2) M0 gần
mean-future CE; (3) dấuΓ theo điều kiện trên là hệ quả đại số; (4) Tier1 chưa
kiểm đủ thì evidence/gap judgment bị ảnh hưởng HOLD, không tự DROP nguồn.
Không thay bài Understanding của tác giả.

## Hai câu cho từng vùng — chưa giả audit đã chạy

- **A1:** Chưa chạy phiên networking trong Part1. NDT/P04 prior đã có từ lesson
  trước nhưng chưa cấp same-estimand Γ clearance; giữ audit/gap judgment HOLD.
- **A2:** Chưa chạy phiên freshness×model mismatch ở đây. S11 known-law không
  tự giải quyết mismatch; cần A2 trước judgment, không nhận “chưa ai làm”.
- **A3:** Chưa chạy phiên adequacy×information, keyword cũ L2.7B không đủ thay.
  VE/AVE là prior phải đối chiếu quantifiers; PC5 novelty judgment vẫn HOLD.
- **A4:** Official abstracts xác nhận re-solving/approximation là prior cần kiểm.
  Full mapping/counterexample/conditions còn Part2 và forward chưa hết, nên
  chưa clearance PC3/PC4 hoặc kết luận trùng/khác hoàn toàn Main RQ.

## Checklist toàn L2.8, không chỉ Part1

Thẻ4phiên: có; A4 bounded rerun: có nhưng chưa exhausted; Tier screening: có,
tạm thời; matrix/log/known-prior update: có;4status summaries: có. Primary
R01/R02/R04 và A1–A3: **chưa làm trong Part1**. Không freeze null, đổi nhãn PC
hoặc phục hồi21paper/18nguồn archive; Excel13nguồn và tiến độ giữ nguyên.
