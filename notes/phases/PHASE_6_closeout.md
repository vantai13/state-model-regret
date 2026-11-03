# Phase 6 closeout — L6.4, 03/11/2026

Người phụ trách: **Doan Van Tai**. Soạn và quyết định theo ủy quyền triển khai
lesson; không xác nhận tác giả tự đọc/tự viết/kín sách hoặc human review.
**Gate D = REFORMULATE; G1 giữ nguyên; PIVOT-watch tiếp tục.** DL-138.
Phase6 đóng execution/analysis theo thiết kế đã chạy; không P6v1.1 hoặc
thiết kế Phase7 mới. Master PHASE_6§13/14/18 chưa có trong repo; closeout
dùng lesson L6.4 được cung cấp và analysis_plan_v2, không nhận áp full master.

## What I understood

Bản diễn giải theo ủy quyền, không author Understanding test: G_S không chỉ
là stake nhân số lần sai. Chi phí thật của policy là Stay cộng gap tại những
state policy chọn Switch. Phần gap trung bình tạo một thành phần tần suất;
phần gap cùng biến thiên với action tạo covariance. Thay mean gap finite-h
bằng stationary stake còn tạo một sai số nữa. Identity cho biết phép xấp
xỉ bỏ gì, không tự chứng minh cơ chế hoặc cung cấp prediction không dùng truth.

## What changed in my mental model

Không dùng P≥30, h/κ lớn, hoặc hành động đúng ở trung bình để xác nhận
uniform oracle action/A1. Tail còn có thể ảnh hưởng weighted cost. S|M1 nhỏ
không ép covariance nhỏ: truth có thể luôn Stay nhưng information giúp
approximate policy chọn những lỗi rẻ hơn. Stake ratio gần1 cũng chưa bảo
đảm H1 thắng, vì δF thay đổi theo h. [T10](../theory/T10_information_value_accounting.md)
có phép dẫn, counterexamples và điều kiện đủ cần kiểm thay cho suy đoán đó.

## Decisions made

- Giữ nguyên thiết kế, thresholds, raw và verdict; không bỏ U hoặc đổi ε.
- Chọn **REFORMULATE** đúng dòng INCONCLUSIVE của plan§6; không GO/H0/H1
  SUPPORT/PIVOT. PIVOT-watch giữ vì contribution/prediction còn chưa được
  xác nhận, không vì H0a đã thắng. Không DROP vì chưa phát hiện fatal bug.
- C1 chỉ là framework kế toán để tổ chức characterization; không nhận generic
  covariance/harm là novelty. Bỏ “S=0⇒alignment=0”, cutoff stake ratio.7,
  automatic asymptotic dominance và kill rule dùng truth để tự dự đoán truth.
- Giữ G1, MainRQ, contract v1.3, D22/realism/ownership/Understanding OPEN.
  Không mở CF/SUB, R09/R10 hoặc76 outcomes p4; không đổi Phase5 verdict.
- Memo hoàn thành trước thiết kế mới; lượt này dừng ở memo/closeout.

## Evidence theo tầng

**1 — Confirmatory reading.** L6.3 đủ81/81 calls,27 members; raw d7a298f0
trước đọc/rescore, biên bản2e034253. D13 có3'-',2'+',8U: INCONCLUSIVE.
Cả13 READY,8U đều deadband,0 NOT_READY. A− '-'; twins11'+',2U;2/13 pairs,
intervention wording=false. Không kết luận H1/H0a từ5 classified points.
Numerical diagnostics không phải population CI hoặc continuous-law truth.

**2 — Prespecified descriptive comparison.** Plan§7 yêu cầu báo prediction,
truth/contrasts/sensitivity/h pairs; không preregister riêng acceptance bằng
ratio. |z_saved|<|z_H1| ở13/13 D; ratio min/max.010341/.544585, median.317285,
mean.261978. Hai normalizers khác nhau được tách ở DL137, không quên đơn vị.
Twins NOT_READY: B015C00 width640/2=.051239383 pp; B034C00 widths
.026533652/.030476256/.037476781 pp, threshold.025 pp. Không gộp chúng vào
8 U của D. Epsilon1% descriptive vẫn INCONCLUSIVE. Hai matched h pairs:
B005→B015,c3/8,h8→16:z−.154834(U)→−1.297676('-');
B027→B040,c7/4,h8→16:z+1.002927('+')→+.021006(U).
Signed/absolute G_S,S,M,Gamma của27 members vẫn ở original summary; không
gán readiness cho các contrasts khác chỉ từ G_S READY.

**3 — Post-hoc diagnostics.** DL137, T10 và direct-centered-moment analyzer
fce64040 dùng saved surfaces, không evaluator/profile mới. Pearson z với
oracle Switch share=.912319884 trên13 selected D; không p-value/CI hoặc
claim cutoff/single cause. Không chọn lại points, fit hoặc chỉnh thresholds.

Ideal common-law identity:

```
G_S = α δF + (EΔ−α) δF + Cov(Δ,a_old−a_new).
```

Trong numerical replay, conditional grids có mean gap lệch nhau nên ghi
thêm bridge, không giấu vào covariance. Tất cả các cột dưới dùng **cùng
actual Cref=L11**, đơn vị pp; first term không phải z_H1 dùng Cref_H1.

| D | αδF | Mean-stake correction | Cov_old−Cov_new trực tiếp | Grid mean bridge | Tổng z |
|---|---:|---:|---:|---:|---:|
| B015C06 | -2.822311 | +0.802131 | +0.722758 | -0.000254 | -1.297676 |
| B027C12 | -2.295826 | +1.549449 | +1.749736 | -0.000432 | +1.002927 |

Đủ27 rows, không chỉ hai ví dụ, ở covariance.csv. Direct covariance
difference trên13 D là+.380891 đến+1.749736 pp. Max mean bridge trên D
.000569258 pp; toàn27 là.004342707 pp (B039C00). Conditional mean drift
max.001457740 packet·s. Decomposition residual max6.661338e−16 packet·s;
covariance-plus-bridge residual4.709639e−16 packet·s. Đây là consistency
trên cùng profiles, không independent validation. Không bỏ drift để claim
“Cov tính chính xác liên tục”. Các numerical values không thành causal proof.

## Failure analysis và giới hạn

Không phát hiện mismatch/bug trong rescore, replay và identities; không
tuyên bố loại mọi bug. READY bác cách giải thích8U là NOT_READY theo gate,
không loại shared numerical bias. Metric vẫn đúng estimand đã chọn; không
đổi metric hoặc gọi count deadband là statistical power với random-sample CI.
Trong saved representation, A1 uniform Stay không khớp oracle Switch mass
.495–10.211%; mean stake khác α và covariance đáng kể. Không tách riêng
unique causal effects của A1/A2. Qualitative horizon explanation chưa có
prospective test ở miền assumptions kiểm được. Chọn c tại predicted peak,
hai horizon levels, tải/c/κ confounding và same-base probes là limitations.

Nhóm stake ratio≈.72–.84 có5 D nhưng chỉ3 nhãn '-',2 U, không4/5 “âm rõ”.
P5_03 L00 normalized error≈7.8167 pp là một limitation trên case đó, không
chứng minh toàn bộ long-h region không đo được. T09 không có uniform bound
để suy h dài nhất định làm bias thắng. Không mở numerics branch mới để cứu.

## Prior và contribution boundary

[Bounded prior check](../literature/L6_4_prior_check.md):6 named works,
Galanis/Making Information More Valuable AI-T,4 nguồn AI-A;3 existing notes
đọc lại, không primary reread. Không generic harm/action-VOI novelty claim.
Gao là road traffic; arxiv/journal versions được phân biệt. Hai full PDFs
được tải nhưng chỉ đọc targeted; author levels/Excel/catalog không thay.
Không exhaustive search, covariance-priority clearance hoặc new G-level.

[Memo một trang](contribution_memo_after_P6.md) chọn provisional
characterization framework, ghi rõ empirical support còn thiếu; không bảo
đảm paper/venue. Không freeze proxy, representation, margin hoặc panel mới.

## Verification, resources và artifacts

- `python -B -m tools.analyze_phase6_covariance`:27/27 direct moment rows,
  0 evaluator/profile mới; GNU user14.65+system.50=15.15 CPU-s,wall15.28s.
- `python -B -m pytest -q tests/test_p6_covariance.py tests/test_p6_saved_analysis.py`:
  10 PASS,.52s; command.79 CPU-s. Bốn tests mới kiểm phản ví dụ S=0,
  conditional mean bridge, không tự dominance ở h dài và từ chối mass sai.
- Frozen rescore sau closeout0d963081: **RESCORE MATCH**, frozen gate record
  **PASS**; input/hash audits PASS như DL138. Không lấy752 full tests lịch
  sử thành kiểm mới của lượt này.
- Phase compute upper4200 CPU-s (trước4050), giữ cap14400; bao bảo thủ cho
  local analysis/tests/audit, không actual cumulative hoặc budget reset.
- Source: tools/analyze_phase6_covariance.py; tests/test_p6_covariance.py.
  CSV/JSON: results/phase6/closeout_l6_4/{covariance.csv,summary.json}.
  Original DL137/source/data giữ byte; raw/predictions/plan/engine không sửa.
  Không tạo simulation output/config/plot hoặc console log riêng mới.

## What I am NOT allowed to claim

H1 đúng/sai tổng thể; H0a đúng; telemetry tươi hại/không hại tổng quát;
generic harm/covariance mới; stake ratio.7 là boundary; S≈0 ép alignment≈0;
long-h dominance đã chứng minh; independent validation/realism/human review;
Understanding hoặc tác giả tự viết đã PASS. Technical closeout COMPLETE,
các mục ownership vẫn OPEN; không thêm human prerequisite cho việc đã làm.
