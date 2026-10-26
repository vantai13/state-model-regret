# Prior boundary — Part A, chưa phải quyết định Gate L

Người phụ trách: **Doan Van Tai** · 24/10/2026 · AI đề xuất, không L-self.

## Prediction receipt và deviation

Bảng dự đoán ở [prior_predictions.md](prior_predictions.md), claims ở
[claims.md](claims.md). Bộ khung lưu trong commit `5ab4750`; proof T03 v2 lưu
trong `3870931`. Cả hai sau exposure từ hội thoại; không đáp ứng điều kiện
prediction commit trước L2.2. Không sửa timestamp hoặc lịch sử để giả đạt.

| ID | Dự đoán đã exposed | Closest prior đã kiểm | Đã ngụ ý | Khác biệt còn cần kiểm | Hậu quả cho prediction | Nhãn AI đề xuất / mức tin cậy |
|---|---|---|---|---|---|---|
| PC1/C1 | DROP contribution | SOB14 Eq4 T; B82 A + T03 proof | EVPPI functional, conditional VSS theo định nghĩa, nonnegativity | Không còn claim khái niệm mới; original B82 reading thiếu | Không dự đoán identity/dấu ≥0 như discovery | DROP như contribution; giữ framing, source gate còn mở |
| PC2/C2 | NARROW | P11 Eq2.7–2.8 T; SOB14 T | So input-information và model-discrepancy value có prior | K2 so repair effects đúng D21 trong load-changing queue; không parameter/structure repair | Giữ ngưỡng/K2 exploratory, chưa chạy | NARROW tạm; chưa có outcome grid |
| PC3/C3 | KEEP | T03 identity; P11 không tự quyết định cùng interaction estimand | Gamma là difference-of-gains, hai dấu có toy | Predictive mechanism/regime còn cần blind-spot L2.8 và A05 | K3 không đủ chứng minh mechanism | KEEP là forecast; Gate L chưa đánh giá đủ |
| PC4/C4 | NARROW | Chưa đủ primary về threshold null | Không có evidence thắng null | Feature/metric/budget/split theo D25/A05 | Không tự fit/chọn baseline bây giờ | NARROW forecast, đánh giá HOLD tới A05/L2.8 |
| PC5/C5 | NARROW | T01 E0; P12 chưa đọc | Same action có thể giữ decision loss nhỏ dù cost bias | OεRE/value equivalence và miền K5 cần kiểm | Giữ K5/Q5; không gán nghiệm đúng trước chạy | NARROW forecast, pending L2.4 |
| PC6/C6 | NARROW | Contract D22; P13 chưa đọc | Full state gồm backlog+mode | D22 fixed-M0 split, timescale/horizon hợp lệ | K6 chưa chạy; không gọi mode visibility là refresh-only | NARROW forecast, pending L2.5–L2.7 |

## Không được claim là mới hoặc được xác nhận

- Khái niệm EVPPI, VSS, dấu ≥0 dưới đúng giả định; Gamma bookkeeping.
- Ý tưởng so giá trị học inputs với giá trị học model discrepancy để định hướng
  nghiên cứu/cải tiến model (P11 §2.4 Eqs2.7–2.8).
- “Model fidelity nói chung” từ M0→M1 của D21; tên EVIU như primary đã đọc.
- Tần suất/độ lớn contrast của mạng thật từ toy hoặc lưới chọn gần boundary.
- Main RQ đã được literature xác nhận mới, hoặc P11 đã giải quyết hết Main RQ.

## Trạng thái

Đủ bộ artifact kỹ thuật Part A sau chạy và audit, xem report. Formal Part A
**HOLD**: không có L-self/proof kín sách/đọc lại sau một ngày của tác giả; missing
pre-reading commit là deviation không thể khôi phục. B82 full reading và MAB11
§2 còn hạn chế truy cập; không dùng chúng để claim bounds. Không cấp phép freeze
L3.3 bằng một technical PASS. G1 và HOLD Phase4 giữ nguyên; L2.4 được học tiếp.

## Trục state — L2.5 Part2, 26/10/2026

Phụ lục này giữ nguyên bảng PC/forecast phía trên. **AI đề xuất; chờ L-self,
A4/L2.8 và L2.9**, không là quyết định novelty/Gate. Vị trí M00 theo submission
28trang; vị trí P04 theo journal15trang. [Bài Part2](information_harm.md).

| ID | Đã biết / điều kiện cần giữ | Evidence và mức đọc |
|---|---|---|
| K-S1 | Stale link-state có thể tăng blocking/flapping trong cấu hình nhất định; không là định luật blocking tăng với T ở mọi mạng | P04 §III-A/IV-A, tr166–167,171/Fig1; AI-T |
| K-S2 | Tác hại phụ thuộc period so với traffic/holding times; không suy T càng lớn luôn càng tệ hay holding time=Tmode | P04 §III, tr168–170/Fig2–3,6; M00 §3.4 PDF10–12; AI-T |
| K-S3 | Nhiều quyết định theo cùng tin cũ có thể dồn tải và thua random/load-independent; một dispatcher lặp decisions cũng có thể làm vậy | P04 §III-A/IV-A; M00 §3.4 PDF12; AI-T. Không phản bác VOI tối ưu |
| K-S4 | Random small-choice và random age có thể phá đồng bộ, hữu ích trong các regime được xét; không luôn d2 tối ưu | M00 §3.4 PDF10–12, §4 PDF15/19–21, §7 PDF25; AI-T |
| K-S5 | Lợi ích cost granularity phụ thuộc update policy; đây là prior định tính, không phải clean2×2 hay Γ | P04 §V-A tr172–173/Fig8:8a total blocking, pruningOFF;8b setup failures, pruningON; AI-T |
| K-S6 | Age khác error; threshold/period bị tác động bởi hold-down/refresh. Trigger không bảo đảm error cứng dưới threshold | P04 §II-D tr165/§III-B tr168–170; AI-T; counterexample Part1 |
| K-S7 | Lợi ích partial/delayed queue info phụ thuộc load và policy/baseline; không có threshold .8/.9 phổ quát | P01 §2.5/Fig2 PDF4, Def2/Eq3 PDF3; **AI-T**, không abstract-only |
| K-S8 | Optimal true-model policy với matched law/objective và thông tin lồng nhau có thể bỏ qua info; GSgivenM1≥0. Không quy về “iff một người” | T03 G1–G4 và proof; exact toy kiểm, AI-only; original reading limits PartA giữ nguyên |

K-S1…8 là giới hạn câu chữ, không tự làm mọi kết quả của RQ thành đã biết.
Prediction card/A05 không nhận “refresh hữu ích”, “age so timescale matters” hoặc
VOI≥0 là contribution; κ/age-only H1 còn phải vượt null theo đúng D25.
K-S5 cần tác giả tự kiểm §V-A/Fig8 trước dùng viết PC3. Không chọn H1/null mới ở đây.

### Ba câu khác biệt — bản nháp AI, chờ A4/L2.9

1. Trong các phần networking đã đọc, P04/M00 cho thấy nhiều quyết định dùng tin
   cũ có thể làm hại routing/load balancing, với hiệu ứng tùy timescale, policy
   và cost granularity; chúng đã có mô hình và action làm đổi tải.
2. D20 của repo làm tươi backlog và lộ mode cho một action giữ suốt h, được định
   giá bằng expected regret so oracle không biết tương lai, đặt cạnh D21 sửa
   mean-rollout thành exact expectation trên cùng posterior/law/protocol.
3. Phần cần kiểm là dấu/điều kiện của fixed-M0 GS, GS−GM và Γ trong thiết kế đó;
   chưa xác nhận chúng được đo đúng như vậy ở các section đã đọc, và V1 chỉ là
   ví dụ tồn tại, không chứng minh mới hoặc chứng minh cơ chế trên lưới.

### Hàng đợi A4 — R04 đã có provenance, chưa được clearance

**Câu hỏi:** khi re-solve một certainty-equivalent model với thông tin mới, hiệu
năng thật có thể giảm dưới những điều kiện nào; chúng tương ứng GS ở D20/D21
đến đâu? Kiểm định nghĩa, policy class, timeline, model consistency và objective,
không chỉ tên thuật ngữ. Chưa nhận GS<0 là phát hiện mới, chưa đổi PC/Gate.

R04 = Secomandi2008, *An Analysis of the Control-Algorithm Re-solving Issue in
Inventory and Revenue Management*, DOI10.1287/msom.1070.0184, đã có **AI-T note
24/10** trong archive local. Lượt này chỉ kiểm record đó: §1.1–1.2/§2.5–2.6/
§3/§4.1.5 được record đánh dấu targeted, không coi là một lần đọc primary mới.
Không phục hồi thư viện ngoài ngành hoặc đưa R04 vào hàng đợi bắt buộc.
Provenance/path/checksum ở [source_access.json](../../results/lessons/l2_5/part2/source_access.json).
Phần scientific dependency A4/L2.9 còn mở; không tự tạo L-self từ note AI cũ.

## Freshness và decision value — L2.6 Part A, 26/10/2026

AI-only, không đổi bảng PC, forecasts, D25 hoặc Gate. [K3 và phép tính](freshness_decision_value.md).

| ID | Đã có / giới hạn claim | Nguồn và phạm vi đọc |
|---|---|---|
| K-S9 | Độ tươi phải được đối chiếu với downstream decision/control cost; đây không phải ý mới | S11 §III/Eq10 PDF5–7 AI-T; R32 abstract AI-A; AY19 §2.4/Eq13–19 AI-T |
| K-S10 | Kết hợp thời gian sai và information-error penalty đã có AoII; không chỉ đo tuổi packet hoặc tự bằng decision regret | Maatouk et al.2020, arxiv1907.06604v2 §II/Eq3–9 AI-T; journal DOI10.1109/TNET.2020.3005549 |
| K-S11 | Trong formulation của S11, optimal average cost có vùng phẳng theo **allowed rate budget** trên threshold; không nói mọi policy gửi thêm đều vô hại | S11 v3 §VII-D/PDF17/Theorem9/Cor2, AI-T statement; proof AppendixO chưa đọc |

**Đính chính metadata:** S11 có journal identity IEEE TIT72(4):2237–2276,2026,
DOI10.1109/TIT.2026.3663678 đã kiểm Crossref/arXiv. DOI TWC related sai vẫn
được log để tránh dùng nhầm; bản thực đọc là arxivv3, chưa đối chiếu toàn VoR.
R32 là issue2022, không lấy2021 trong DOI làm issue year.

“Cột M1” của S11 chỉ là tương đồng known-law assumption; S11 có action feedback
và approximate LP solver §VII-C. Không suy cả field chưa xét approximate models,
hoặc estimand của S11 bằng GSgivenM1. Keyword screening của lượt này không đủ
clearance GS/Γ; A4/L2.8 tiếp tục câu hỏi freshness×model mismatch theo E/M/R.

PC6/K6 giữ nguyên forecast; [H1-Q01](h1_candidates.md) chỉ ghi heuristic input
variance có provenance AI/exposed. Chưa có queue posterior errors/F/V trên lưới;
không kết luận dự đoán PC6 đúng hoặc sai. P13/Part B chưa thực hiện.

## L2.6 Part B — horizon và transient, 26/10/2026

Các trạng thái Part A ở trên là record lúc lưu; Part B nay đã thực hiện kỹ thuật.
Không sửa bảng PC/forecast hoặc biến các AI notes thành L-self.

| ID | Prior có điều kiện, không nhận là mới | Nguồn / mức đọc |
|---|---|---|
| K-F1 | Đánh giá freshness theo downstream decision/control cost đã có | S11 §III/Eq10 AI-T, K-S9/record PartA giữ nguyên |
| K-F2 | Optimal cost có thể phẳng theo allowed sampling-rate budget trên threshold; không phải mọi packet thêm đều vô hại | S11 §VII-D/Theorem9/Cor2, **AI-T statement**, không AI-A; proof chưa kiểm |
| K-F3 | AoII kết hợp time và error penalty, không chỉ age packet | AoII §II/Eq3–9 **AI-T** của PartA, không metadata-only |
| K-H1 | Với fixed μ>λ và đúng Lévy/moment assumptions: cumulative correction=A+O(1/T), A=[EQ0²−EQ∞²]/[2(μ−λ)], có thể dương/âm/0 | P13 Theorem1/tr276 + Eq2.7/tr275, AI-T statement + phép nhân T của dự án |
| K-H2 | Second moment của initial workload đi vào leading shift μ*T−μ*∞ bậc1/T | P13 journal Prop4/Eq4.4/tr282, AI-T; không tự là routing gap formula |
| K-H3 | Steady-state optimizer mất O(1/T²) dưới normalized finite-horizon objective; nhân T cho cumulative bound O(1/T) | P13 journal Prop5/tr282, AI-T statement; không mang bound sang binary D21 |
| K-H4 | Bỏ cost sau finite horizon có thể ảnh hưởng capacity choice và để lại congestion; đây là explanation paper đề xuất | P13 **journal §6/tr289**, không §5.3 journal; AI-T |

[Note P13](papers/P13.md) ghi version/numbering/assumptions và lỗi số học cần
tránh chép. [Bài PartB](horizon_transient.md) kiểm25/100, endpoint quadrature,
continuous/density/finite-support examples. Chưa có J/regret/contrasts trên grid.

**PC3/PC4:** “S0 step còn S1 quadratic” chỉ đúng thêm giả định về density/bias;
finite posterior cũng có jumps. Γ có thể khác0 trên abstract tables không queue,
nhưng bias examples không là D21 và chưa giải thích real-grid mechanism.
Q-L27-01 chờ L2.7/A05; không tự thêm baseline hoặc đổi null.

**PC6:** P13 có prior về initial workload/horizon, không trực tiếp mô hình R2
memory/hidden modes hoặc tách F/V. Main B có mean9/9.5<capacity10 dù ON14>10;
không lấy ON overload làm proof instability. Khác Lévy assumption vẫn chặn
transfer theorem; khác assumptions riêng nó không chứng minh novelty.

[H1-Q02](h1_candidates.md) chỉ lưu B-only long-h second-moment heuristic;
finite-h8, queueA và mode effects còn thiếu. [T-H1](../01_claim_boundary_v1_2.md#t-h1--giới-hạn-diễn-giải-do-horizon-hữu-hạn-26102026)
đã bổ sung trước diễn giải regret; giữ D13 không đổi. L2.6 có artifacts kỹ thuật
cho cả2parts; **Understanding/L-self/Gate/A4/L2.9 còn mở**, G1/HOLD Phase4 giữ nguyên.

## L2.7 Part A — trục model,26/10/2026

AI-only. Không sửa bảng PC/forecast hoặc đổi Gate. [Bài và đính chính](model_fidelity_methods.md).

| ID | Prior / phạm vi câu được nói | Nguồn và mức thực đọc |
|---|---|---|
| K-M1 | Simulation fidelity khác decision quality: dưới assumptions của Theorem3.1, **tồn tại reward/Π** khiến model simulation-optimal xếp sai; không có kết luận tần suất | P03=R51 §3/PDF3, A.1/PDF14, §6.1/PDF6–7 AI-T; P07 §2.2/4.2 AI-T |
| K-M2 | Đánh giá twin bằng expected-return decision regret đã có trong finite policy set; true values được ước lượng MC, không hindsight selection | P03 §2/Eq1–4, §6.2/PDF7–8, B.4.2/PDF17 AI-T;500rollouts/policy |
| K-M3 | Tối ưu trực tiếp TE objective từ historical demands, bỏ explicit demand-prediction stage, đã có trong networking | P07 §2.2–3.2/printed1558–1562 AI-T; không phải không dùng model/DNN |
| K-M4 | Sensitivity theo aggregation/model/input biases, prediction horizon và update frequency đã có | P02 **official abstract AI-A** xác nhận phạm vi chung; bias definitions/ranges/combined designs ở full text chưa kiểm |
| K-M5 | Frequent updates dampen prediction errors là prior được abstract báo; reinitialization bù model/demand và thất bại khi state biased là **candidate chưa xác nhận** | P02 abstract AI-A; §4 từ lesson chỉ là vị trí cần đọc, chưa AI-T hoặc measured Γ |

**Không suy dấu Γ từ P02/P04.** Factorial có thể nằm trong một sensitivity
study; ba ô OAT từ một anchor không xác định interaction khi thiếu assumptions.
GS/GM là simple effects tại baseline; cost cross-difference=−Γ. P03 có partial
observation, nhưng các section đã đọc chưa xác nhận controlled D20×D21 cùng
posterior/objective/actions. Khác setup không là novelty clearance.

[MT1…8](../phases/PHASE_4_methodology_threats.md) là queue HOLD trước Phase4;
MT2/6/7 còn P02 full-text dependency, MT5 chờ A05 cụ thể hóa null. Không tự khóa
null/H1, không đổi thresholds và chưa chạy grid. **L2.7 Part A chưa hoàn tất
primary P02; Part B/P12/OεRE, L-self/Gate/A4/L2.8–2.9 còn mở.**
