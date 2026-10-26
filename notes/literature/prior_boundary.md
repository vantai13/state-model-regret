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

## L2.7 Part B — OεRE và PC5,26/10/2026

Bảng forecast đầu file và claims.md giữ nguyên; đây là **cập nhật evidence AI**,
không sửa prediction đã exposed hoặc nhận PC5 được grid xác nhận.

| ID | Đã có | Còn cần kiểm | Pipeline/miền | Trạng thái nhãn |
|---|---|---|---|---|
| PC5/C5 | P12 §3/Def1/§3.1 AI-T: decision-relevant model sufficiency; P03/P07 decision fidelity đã có. R43 official abstract lượt này: tolerance/performance bounds; archive có AI-T24/10, chưa tái kiểm primary definitions | Vị trí/điều kiện OεRE theo coordinates và thông tin; norm/quantifiers/representation của AVE có overlap đến đâu; không chỉ khác tên/domain | **S0**, GM/Cref≤.005 mọi K5=M19–M22; Q5=M01–M04 có ít nhất1ô≥.01. K/Q vẫn exploratory, không đổi hoặc mở rộng ở đây | Giữ NARROW forecast cũ; chưa chấm formal L2.9/novelty/Gate, không kết luận PC5 PASS |

[OεRE trong terms](terms.md#oεre--operational-ε-regret-equivalence-l27-part-b)
là định nghĩa vận hành nháp, không kết quả hoặc contract amendment. Exact error
interval/denominator certification là reporting proposal; adopt cần DL/version.
Một cell không được certified chưa tự bác uniform equivalence; need true value
hoặc interval hoàn toàn ngoài biên. Không lấy mean across K thay “mọi cell”.

| ID | Đã biết và phạm vi | Source/mức đọc |
|---|---|---|
| K-M6 | Restricted policy/function tests có thể giữ Bellman updates dù không khớp toàn dynamics | P12 Def1/PDF3, §3.1/Properties1–4 AI-T. Chỉ macro one-step/reward−J embedding mới cho mức(a) exact action-cost fidelity; không gán VE tổng quát bằng mức(a) |
| K-M7 | Approximation tolerance cho VE và performance bounds đã có; không nhận “ε-equivalence dẫn tới decision quality” như khái niệm mới | R43 official abstract AI-A lượt này; archived AI-T24/10 tồn tại, provenance ở note/source_access. Không từ abstract xác nhận bound/formula đầy đủ |

**PC3↔PC5:** Γ=GMgivenS1−GM; gains khác nhau có thể dẫn đến equivalence statuses
khác nhau, nhưng Γ≠0 không đủ chứng minh boundary crossing. V1 có0%/20%, còn
abstract example mới cho Γ≠0 mà cả hai cùng trong biên. Chưa chạy grid outcomes.

[Queue L3.3/A05](../lessons/L3.3_equivalence_queue.md) so3candidate K rules:
list/κ3 có4main+0held-out, κ≥2 có4main+R03/R04 theo metadata. **Chưa chọn rule**,
không dùng held-out outcomes/p_sw/λA riêng làm inputs; R03/R04 chỉη.5. Không suy
unique boundaryκ2–3 nếu thiếu monotonicity/controlled coordinates. D25/A05 giữ
quyền freeze/test; không tự chuyển bước theo A06 trong lesson.

Keyword query giới hạn đã sàng12result titles, đa phần index pages, giữ0;
không phải12papers đọc, không đạt2×20 và không clearance A3/A4. L2.8/A4/L2.9,
L-self/Understanding/Gate/A05 còn mở. PartB có artifacts kỹ thuật; **toàn L2.7
vẫn còn primary P02 của PartA BLOCKED**. [Bài PartB](model_equivalence.md).

## L2.8 Part1 — A4 threat register,26/10/2026

[4session cards và execution](literature_audit_part1.md). PC3/PC4 có Tier1 priority
R02/R01/R04 do tác giả chỉ định; official abstracts hiện xác nhận re-solving
và approximation là prior phải kiểm. Full policy/timeline/assumptions/mapping
vẫn chưa verified lượt này; archived AI-T24/10 không là L-self hoặc fresh full
read. Không biến “stochastic” thành exactM1 hoặc non-deterioration cho mọi policy.

Giữ forecast/table PC đầu file và claims.md byte-unchanged. **Prior-clearance
judgment cho claim bị ảnh hưởng HOLD** tới primary Part2/A1–A3/L2.9; không tự
chọn KEEP/DROP/NARROW/PIVOT mới. GS<0⇒Γ>0 chỉ theo true-model VOI assumptions,
không sufficient mechanism evidence. Không chọn/null-fit hoặc chạy Phase3.

## L2.8 Part2 — primary re-solving và3nguồn được duyệt,26/10/2026

Bảng forecast PC phía trên giữ nguyên. Primary targeted **AI-T** R01/R02/R04
đã thực hiện; không còn HOLD vì chưa đọc hai bài này. Bản R01 là TR2006,
chưa kiểm journal numbering; tác giả L-self chưa xác nhận.

| ID | Đã biết | Primary evidence / giới hạn |
|---|---|---|
| K-RM1 | Cập nhật thông tin qua re-solving approximate allocation có thể giảm true expected revenue | R02 §5/Example1/PDF7; không do rounding, không tự là D20/Jensen hoặc D19Γ |
| K-RM2 | Feasible old allocation và objective đúng true policy value cho non-deterioration | R01 TR Prop1/PDF10–11; chỉ allocation policy, không bid-price hoặc true MDP |
| K-RM3 | SC+Π-accuracy⇒SI⇒non-deterioration; approximate bound cần thêm Eq9 | R04 §3/Def2–5/Props1–3/PDF8–10; Remark2: error terms thường cần policy evaluation |

K-S9/K-S10 đã dùng trong freshness, không ghi đè bằng ID từ lesson gửi.
R04→one-shot diagnostic và V1 kiểm được ở [Part2](literature_audit_part2.md);
chưa chuyển thành H1 input-only, chưa chọn null hoặc freeze A05.

NDT26 §IV–VI/PDF6–9 cho fidelity gate/utility regret trực tiếp trong Open RAN.
WM26 §5/F.1/PDF5,22 có center×response **2×2repair**: Tier1 cho framing PC3/PC4;
không nhận generic factorial repair là contribution. Axes/true-future oracles
khác D20/D21/D15, khác biệt đó chưa đủ chứng minh contribution. AIS22 Def7/
Theorem9/PDF15–18 cho prior model adequacy dưới partial observations của PC5.
Cả3đã được tác giả duyệt, đọc AI-T; không tự gán L-self hoặc publication cho preprints.

**PC3 formal judgment HOLD L2.9**, PC4 HOLD A05/L2.9; PC5 NARROW forecast
cũ giữ nguyên, chưa có K5 outcome. Nguyên nhân hiện tại là cần chấm wording/
prior boundary/null evidence, không phải R02/R04 full-text blocked. A1–A3 có
bounded sessions nhưng thiếu per-rank raw log, không saturation/coverage proof.
G1/HOLD Phase4 giữ nguyên. Không tiếp Phase3 ở lượt này.

## L2.8 follow-up — P02 primary và phiên tìm bổ sung, 26/10/2026

Bảng forecast PC phía trên giữ nguyên; **không đổi nhãn PC, không chấm L2.9**.

| ID | Cập nhật evidence | Vị trí / giới hạn |
|---|---|---|
| K-M4 | Bias definitions/ranges và thiết kế đã kiểm: bias một đại lượng mỗi lần trên thế giới đã aggregation; quét 1-D theo prediction và update horizon; không joint bias | P02 VoR §2.2.4 tr10, §3.3.1 tr15, Bảng 2 tr16, §4 tr18; AI-T |
| K-M5 | Từ candidate → **prior đã báo trong paper**: reinitialization thường xuyên bù một phần loss; state bias lớn (±50%) làm mất bù hoặc thêm loss | P02 §3.3.2 tr16, §4 tr18, §5 tr19; mô phỏng 10 seed, corridor 4 nút; metric delay/xe, không D19Γ |

PHASE_2 v2.0 §5.4 ghi P02 là nguồn quyết định nhãn PC2; L-self của tác giả còn mở.
Phiên tìm bổ sung (157 record, không Tier1, 4 T2) ở [search log](search_log.md) (mục "L2.8 follow-up");
không đạt luật dừng 2×20. Ba đề xuất mới chờ duyệt, không ảnh hưởng nhãn trước khi đọc.

## L2.9 Part 1 — hồ sơ 8 cột, nhãn chờ tác giả chấm (26/10/2026)

Người phụ trách: **Doan Van Tai**. AI lập hồ sơ theo PHASE_2 v2.0 §14 (phần "AI có
thể hỗ trợ": kiểm nguồn/mức đọc/nhất quán) và lesson L2.9 Part 1. **Cột Nhãn để
trống**: tác giả chấm; không có nhãn nào ở đây là nhãn tạm hay Gate L. Repo tại
`86ec878`. Mọi mức đọc dưới đây là **AI**; L-self của tác giả: 0/19 có record.
Cột "Câu hỏi hậu quả" là câu hỏi để tác giả trả lời, không phải đáp án.

| Claim (nguyên văn claims.md) | Closest prior (vị trí) | Prior đã chứng minh/đo | Khác biệt chính xác (E/M/R) | Câu hỏi hậu quả | Nguồn quyết định nhãn · mức đọc | Nhãn | Ngày/DL |
|---|---|---|---|---|---|---|---|
| **PC1** Dưới G1–G5 của T03, GSgivenM1 bằng EVPPI(x\|y), GMgivenS1 bằng trung bình VSS(x) | SOB14 Method Eq1–4; P11 §2.4; B82 (VSS); T03 v2; R01 Prop1 tương tự cấu trúc "chính sách cũ vẫn khả thi" (suy luận AI) | Định nghĩa EVPPI/VSS và dấu ≥0 dưới giả định; claim boundary v1.2 (Part A): EVPPI dưới G1–G4, VSS dưới G2–G5 | E trùng dưới giả định; M/R chỉ là ánh xạ sang plant | Nếu bỏ ánh xạ này, có prediction nào của đề tài đổi không? | §5.4: SOB14, P11 · AI-T. **L3: phép dẫn T03 do AI viết**, tác giả chưa tự dẫn | ⟨tác giả chấm⟩ | — |
| **PC2** Trong K2=M09–M12, (GS−GM)/Cref≥.01 ở từng ô | P11 §2.4 Eq2.7–2.8; WM26 §5, F.1 Eq10, Table10–12; P02 VoR §3.3/Bảng2/§4 (K-M4, K-M5); P04 (K-S2). Chờ duyệt: N1 2609.06351, N2 10.1145/3769700.3771695 | So giá trị thông tin đầu vào với sửa discrepancy (P11); so ưu tiên repair C vs S theo chất lượng xếp hạng, oracle tương lai thật (WM26); xếp hạng độ nhạy từng đại lượng, update thường bù một phần (P02, bias một đại lượng mỗi lần) | E: GS−GM theo D19, regret so oracle D15 không biết w, chuẩn hoá Cref theo ô; M: D20 lộ state hiện tại (backlog+mode) vs D21 đổi biểu diễn randomness, θ đúng; R: hai path, một quyết định làm đổi tải, ô gần ranh giới | Bỏ "queue làm đổi tải + oracle không biết tương lai" thì PC2 còn prediction nào mà P11/WM26/P02 chưa cho? | §5.4: P11, P02, P04 · AI-T (P02 VoR từ 26/10, không còn cần phép thử kịch bản xấu nhất). Lesson thêm WM26 · AI-T | ⟨tác giả chấm⟩ | — |
| **PC3** Trong K3={M19,M21}, Γ/Cref>.005 ở từng ô; khả năng giải thích/dự đoán ngoài discovery phải kiểm riêng với null | WM26 F.1 Eq10/Table11–12 (P/C/S/E); R02 §5 Ex1 (K-RM1); R04 §3 Def2–5/Prop1–3 (K-RM3); R01 Prop1, §4 Ex3 (K-RM2); P04 §V-A Fig8 (K-S5, định tính); AIS22 Def7/Thm9; R06 (abstract); P02 (sweep update×bias 1-D) | 2×2 sửa hai nguồn lỗi với oracle tương lai thật, so ưu tiên repair (WM26); thông tin làm hại approximate re-solving (R02) và điều kiện đủ không hại (R04; R01 cho allocation, không mọi bid-price) | E: Γ=L10+L01−L00−L11 theo ô; WM26 báo C−P, S−P, C−S, **không thấy** E−C−S+P trong trang đã đọc; C/S của WM26 nhập tương lai thật (F.1 PDF22), nhánh không-oracle là future work (§9 PDF9). M: lộ hidden state hiện tại × biểu diễn đúng randomness trên cùng posterior. R: một quyết định, queue làm đổi tải | Nếu D20 được thay bằng repair dùng tương lai thật như WM26, GS gồm cả EVPI tương lai: prediction nào về dấu Γ ở K3 sẽ đổi? | §5.4: R04, R06 "có thể PC3" · R04 AI-T, R06 AI-A; lesson thêm WM26, R02 · AI-T (WM26 đọc lại 26/10) | ⟨tác giả chấm⟩ | — |
| **PC4** Queue-dynamics explanation dự đoán tốt hơn threshold null với cùng thông tin và budget | P04 §III (K-S2); M00 §3.4; P13 Thm1, Prop4 (K-H1, K-H2); H1-Q01…Q03; MT5; NDT26 §VI-D (τ chọn trên all evaluation runs); P02 §3.3.2 (K-M5) | Nhiều biến giải thích đã có: period so với holding time, moment bậc hai của workload ban đầu, SC+Π-accuracy, refresh bù lỗi lặp | Phụ thuộc H1/null/metric/split do A05 khóa (D25), hiện chưa có | Literature có thể quyết được câu này không, hay chỉ A05? | §5.4: P04, P13 · AI-T; không nguồn nào quyết định outcome | ⟨tác giả chấm⟩ | — |
| **PC5** Trong K5=M19–M22, GM/Cref≤.005 ở mọi ô; trong Q5=M01–M04 có ít nhất một ô GM/Cref≥.01 | P12 Def1/§3.1 (K-M6); R43 (K-M7, AI-A lượt L2.7B); AIS22 Def7/Thm9; P03 Thm3.1. Chờ duyệt: 2308.13166 (cận CE ∝ variance), N3 2608.01725 | Model đủ cho quyết định không cần khớp toàn dynamics, kể cả partial observation; bound cho approximate VE | E: OεRE mức regret theo ô (draft terms.md), GM dưới S0; M: M0 mean rollout từng state vs M1; R: tọa độ κ/q/η của queue. K5/Q5 là nháp exploratory, luật K chưa chọn (L3.3 queue) | Có nói được gì về **vị trí** ranh giới K5/Q5 mà P12/AIS22 không nói? | §5.4: P03, P12 · AI-T; AIS22 AI-T | ⟨tác giả chấm⟩ | — |
| **PC6** Trong K6={M17,M18}, fixed-M0 D22 split F=L00−Lcb0, V=Lcb0−L10 có V>0 và V>F | S11 §III/Eq10 (K-S9, K-F1); AoII (K-S10); R32 (A); P13 Thm1 (K-H1); P04 (K-S2). Chờ duyệt: N1, N2 | Độ tươi đánh giá theo cost quyết định; tuổi khác sai lệch; vai trò backlog ban đầu với cost cộng dồn | Tách backlog và mode ẩn dưới fixed-M0 (D22) trong plant làm đổi tải; V gồm thấy mode A+B, không phải lợi ích refresh backlog | Repo **chưa có** số nào về F/V: H1-Q01 chỉ là phương sai input không điều kiện, "không phải F của D22" (freshness_decision_value.md). Dự đoán V>F dựa trên gì? | §5.4: S11, P04, P13 · AI-T | ⟨tác giả chấm⟩ | — |
| **Main RQ** (nguyên văn README) | WM26; K-RM1–3; NDT26; AIS22; P03; P04; S11; P13 | Xem các dòng trên | AI chưa thấy nguồn đã đọc nào trùng **cả** E, M, R | Luật PHASE_2 §15/MASTER PLAN: Main RQ KEEP trừ khi prior trùng cả ba trục | Tất cả AI-T; L-self 0 | ⟨tác giả chấm⟩ | — |

### Trạng thái Gate L tại `86ec878` (PHASE_2 §15)

| ĐK | Trạng thái | Thiếu gì |
|---|---|---|
| L1 | ❌ chưa có nhãn | Tác giả chấm bảng trên |
| L2 | ❌ L-self 0/19; P02 nay AI-T VoR, WM26 đọc lại AI-T | [Mẫu ghi L-self](author_reading_record.md), tác giả tự điền |
| L3 | ⚠️ code + mutant PASS; phép dẫn T03 do AI viết | Tác giả tự dẫn kín sách |
| L4 | ✅ OεRE có trong terms.md (draft, chưa adopt contract) | — |
| L5 | ⚠️ 4 phiên có log; Tier1 AI-T; Part2 thiếu raw từng rank (deviation); follow-up 157 record có raw, 0 Tier1; luật dừng 2×20 chưa đạt; forward P07 chưa chạy được | Ghi deviation ở DL Gate L |
| L6 | ❌ | Part 2 |
| L7 | ⚠️ có mục AI; chưa có mục "Ranh giới với prior (Phase 2)" trong claim boundary | Part 2 |
| L8 | ❌ | Người đọc thật |

Theo PHASE_2 §17: còn thiếu điều kiện validity ⇒ **HOLD**; đủ L1–L7 thiếu L8 ⇒ tối đa GO có điều kiện.

### Tổng hợp "không được claim là mới" (gom từ các mục đã có, AI)

EVPPI/VSS/VOI≥0 và Γ bookkeeping (Part A, T03); stale state làm hại routing và
herding (K-S1…S3, P04/M00); độ tươi theo decision cost, tuổi khác sai lệch
(K-S9…S11, K-F1); initial backlog/horizon ảnh hưởng cost cộng dồn (K-H1…H4);
fidelity khác chất lượng quyết định, decision-focused model (K-M1…M3, P03, P07,
NDT26); sensitivity theo bias/horizon/update (K-M4, K-M5, P02); model đủ cho quyết
định và approximate VE (K-M6, K-M7, AIS22); thông tin làm hại approximate re-solving
và điều kiện đủ không hại (K-RM1…RM3); bảng 2×2 sửa hai nguồn lỗi và so ưu tiên
repair (WM26). Danh sách là chỉ mục, không phải nhãn; chi tiết và giới hạn ở các mục gốc.

## L2.9 — nhãn tạm do AI chấm theo ủy quyền tác giả (26/10/2026)

**Provenance:** Doan Van Tai yêu cầu AI "đóng vai tác giả và thực hiện mọi thứ cần
tác giả thực hiện" (hội thoại 26/10). Nhãn dưới đây do **AI (Claude) chấm thay theo ủy
quyền**, dựa trên evidence AI-T; **không phải tác giả tự chấm**. Cột `⟨tác giả chấm⟩` ở
hồ sơ Part 1 phía trên giữ trống cho bản tự chấm. AI chấm **sau khi đã thấy** nhãn tạm
của mentor (exposure), nên đây không phải chấm mù. Nhãn **tạm**, không phải Gate L chính thức.

| Claim | Nhãn tạm | Lý do một câu | Nhãn sẽ đổi nếu | Để thành chính thức |
|---|---|---|---|---|
| PC1 | **DROP** như contribution; giữ làm framing | Identity dưới giả định ghi rõ, prior trực tiếp SOB14 Eq1–4/B82 (claim boundary v1.2, Part A) | Phép dẫn T03 sai ở một giả định G1–G5 (khi đó là sửa ánh xạ, không thành contribution) | L3: tác giả tự dẫn T03 kín sách |
| PC2 | **NARROW** | Câu hỏi "repair nào đáng hơn" đã có prior (P11 §2.4 Eq2.7–2.8; WM26 F.1; P02 §3.3.4: "state is still the most important quantity"); chỉ còn đặc trưng theo ô của GS−GM dưới D20/D21 trong plant queue | L-self thấy prior đã đo GS−GM với oracle không biết tương lai trong queue làm đổi tải → DROP | L-self P11, P02 (nguồn §5.4), WM26 |
| PC3 | **KEEP ở câu chữ**; framing **NARROW** | Không nguồn đã đọc trùng cả E (Γ D19, oracle không biết w), M (lộ hidden state hiện tại × biểu diễn randomness trên cùng posterior), R (một quyết định làm đổi tải); WM26 dùng oracle tương lai thật (F.1 PDF22, §9 PDF9) và chỉ báo C−P, S−P, C−S | L-self WM26 thấy nhánh chỉ dùng thông tin hiện tại hoặc contrast tương tác cùng D19 → NARROW/PIVOT; một nguồn chờ duyệt (vd. 2308.13166) cho dấu Γ tổng quát dưới CE → NARROW và thành prediction cho H1 | L-self WM26 §5/F.1, R02 §5, R04 §3 |
| PC4 | **HOLD** | Literature không quyết được; cần H1/null/metric/split khóa ở A05 (D25), phải vượt K-S2, K-H1, K-H2, H1-Q03, MT5 | Prereg A05 tồn tại | A05 |
| PC5 | **NARROW** | "Model đủ cho quyết định" có prior (P12 Def1; R43; AIS22 Def7/Thm9; P03 Thm3.1); còn vị trí ranh giới OεRE dưới S0 trên tọa độ queue và sự phụ thuộc vào mức thông tin; luật K5 chưa chọn | Nguồn chờ duyệt (2308.13166) hoặc nguồn khác cho vị trí ranh giới trong queue → DROP/PIVOT | L-self P12, AIS22; chọn luật K ở L3.3 |
| PC6 | **NARROW** | Độ tươi theo cost quyết định (S11 §III/Eq10, nguồn bị action điều khiển), tuổi khác sai lệch (AoII), vai trò backlog ban đầu (P13 Thm1) đã có; còn tách backlog và mode ẩn dưới fixed-M0; repo chưa có số F/V nên V>F là dự đoán rủi ro | N1/N2 (chờ duyệt) đã tách thành phần backlog/mode như vậy → DROP/PIVOT | L-self S11 §III, P13 Thm1 |
| **Main RQ** | **KEEP** | Chưa thấy nguồn đã đọc trùng cả E, M, R; gần nhất WM26 khác lượng thông tin của repair (tương lai thật so với state hiện tại), khác oracle, khác regime | Một nguồn trùng cả ba trục | L2, L8 |

### Dòng boundary đầy đủ cho PC3 (bài tập 2, AI theo ủy quyền)

| Cột | Nội dung |
|---|---|
| Claim | Trong K3={M19,M21}, Γ/Cref>.005 ở từng ô; khả năng giải thích/dự đoán ngoài discovery phải kiểm riêng với null |
| Closest prior | WM26 §4.1/§5 PDF4–5, F.1 Eq10/Table10–12 PDF22–23, §9 PDF9 |
| Prior đã chứng minh/đo | Trên pool candidate cố định, thay center bằng trung bình endpoint thật (C) hoặc responses bằng responses thật (S); báo C−P, S−P, C−S; S cho lựa chọn tốt hơn C ở 16/16 cấu hình (mean) dù center chiếm >½ MSE ở 14/16 (F.1 PDF23) |
| Khác biệt chính xác | **E:** Γ=L10+L01−L00−L11 theo ô, regret so oracle không biết w; WM26 không báo E−C−S+P trong trang đã đọc. **M:** D20 lộ state hiện tại (backlog, mode ẩn); D21 đổi biểu diễn randomness với θ đúng, không chèn tương lai thật. **R:** một quyết định nhị phân làm đổi tải trong plant queue; WM26 là latent world model với pool CEM |
| Vì sao tạo kiến thức | Dưới M1, repair lộ w cho loss E_D E_w[min_a C(a,w)] = L* − E_D[EVPI_w(x)], nên "state repair" kiểu WM26 có gain lớn hơn G_{S\|M1} của D20 đúng bằng E_D[EVPI_w] ≥ 0 (đẳng thức, AI suy luận; kiểm số học ở audit L2.9 Part 2). Vì vậy Γ theo D19 **không suy được** từ C−P, S−P, C−S của WM26; dấu Γ ở K3 là câu hỏi riêng. Đề xuất cho L3.3/A05 (chưa adopt): báo kèm E_D[EVPI_w] ở các ô K3 để thấy phần thông tin tương lai bị loại khỏi estimand |
| Mức đọc nguồn quyết định | WM26 AI-T (đọc lại 26/10); R02, R04 AI-T; L-self 0 |
| Nhãn | KEEP ở câu chữ; framing NARROW (không claim: thông tin có thể làm hại, 2×2 repair, fidelity khác quyết định) |
| Ngày/DL | 26/10/2026 · DL-042 |

### K3 — so dự báo đã lộ với nhãn tạm (bài học, không phải calibration)

Bảng dự báo (`prior_predictions.md`) là AI-assisted và đã lộ trước khi lưu (DL-040);
nhãn tạm ở trên cũng do AI chấm. Không tính thống kê. Chỉ so PC3/PC5/PC6.

| Claim | Dự báo đã lộ | Nhãn tạm (AI ủy quyền) | Điều đã đổi suy nghĩ (nguồn) | Bài học |
|---|---|---|---|---|
| PC3 | KEEP, độ chắc thấp | KEEP câu chữ, framing NARROW | Thẻ AI trước phiên A3 ghi "0 Tier1" (`l2_8/part2/reading_card.md`), kết quả có **WM26** Tier1; A4 cho K-RM1–3; WM26 đọc lại: oracle tương lai thật | Prior gần nhất cho tương tác thông tin × model nằm ở ML world model và revenue management, không ở networking; phiên tìm theo tên khái niệm nên chạy sớm |
| PC5 | NARROW | NARROW | AIS22 (A2, Tier2) cho adequacy dưới partial observation; P12 Def1 là VE theo tập policy/hàm test | "Đủ cho quyết định" có prior rộng hơn dự báo; phần còn lại chỉ đứng nếu nói được **vị trí** theo tọa độ |
| PC6 | NARROW | NARROW | S11 có nguồn bị action điều khiển (§III PDF5); H1-Q01 "không phải F của D22" | Repo không có số F/V; không suy độ lớn F từ phương sai input |

### Đính chính L2.9 (26/10/2026)

Đính chính 26/10 (sau khi kiểm bản giải thích WM26 tác giả đã đọc): câu WM26 "the true-future oracles are diagnostic tools…" nằm ở **§8 (Limitations and Conclusion), trang PDF 9**, không phải "§9" như các dòng AI ở trên ghi; nội dung trích dẫn không đổi. [Chi tiết](../../results/lessons/l2_9/wm26_author_reading/check.md). Áp cho hồ sơ Part 1 (dòng PC3), bảng nhãn tạm và dòng PC3 8 cột ở trên.
