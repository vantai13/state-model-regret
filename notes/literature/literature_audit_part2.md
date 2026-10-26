# L2.8 Part2 — re-solving và các prior gần state × model

Người phụ trách: **Doan Van Tai** ·26/10/2026 · AI-assisted, chưa L-self/Gate.
[Report/commands](../../results/lessons/l2_8/part2/report.md) ·
[Excel](../../papers/paper_comparison.xlsx).

**Kết quả chính:** R01/R02/R04 đã đọc primary targeted; R02 lấy được sau retry
VPN. Ba nguồn mới NDT26/WM26/AIS22 đã được tác giả duyệt và đọc targeted.
WM26 có bảng2×2 repair: không được nhận design này hoặc decision-aware fidelity
là mới. Chưa chấm nhãn L2.9, chưa khóa H1 hoặc chạy Phase3.

## 1. Sáu nguồn trả lời gì?

| Nguồn | Kết quả đã kiểm, vị trí | Phạm vi đối với repo |
|---|---|---|
| [R01](papers/R01.md), TR2006 của journal2010 | Prop1/PDF10–11: re-solve stochastic **integer allocation** không giảm expected revenue | Cùng proof structure K-S8, không literally cùng estimand EVPPI; SLP không bằng true MDP/M1 |
| [R02](papers/R02.md), journal2002 | §5/Example1/PDF7: DLP re-solving có thể làm giảm expected revenue, không do rounding | Analog GS<0; khác timeline/interventions; không cho D19Γ hoặc frequency trong queue |
| [R04](papers/R04.md), journal2008 | Def3–4/Prop2/PDF9: SC+Π-accuracy⇒SI; Prop1/PDF8: SI⇒non-deterioration | Cho sufficient conditions, chưa thành predictive H1 cho plant |
| [NDT26](papers/NDT26.md), preprint2026 | §IV–VI/PDF6–9: utility-regret, on-policy fidelity gate và learned fallback trong Open RAN | Prior networking trực tiếp; power-offset mismatch khác D21, không independent hidden-state reveal |
| [WM26](papers/WM26.md), preprint2026 | §5/F.1/PDF5,22: P/C/S/E center×response repair grid | Tier1 cho framing; true-future repair không D20×D21, E không true-performance oracle |
| [AIS22](papers/AIS22.md), JMLR2022 | Def7/Thm9/PDF15–18: joint compressed-state/model approximation và bounded policy loss | Prior model adequacy dưới partial observations; cần uniform assumptions, không tự xác nhận PC5 |

Tất cả **AI-T**, không full reading; mức tác giả chưa có xác nhận.
PDF ngoài Git, version/hash/phần đọc ở [source manifest](../../results/lessons/l2_8/part2/source_access.json).
Archived AI-T24/10 giữ nguyên và không được tính thành tác giả đã đọc.

## 2. R01: ba bước, và chỗ DLP có thể gãy

1. Sau quan sát mới, allocation còn lại từ lời giải cũ vẫn feasible trong SLPR-h.
2. Lời giải mới tối ưu objective nên objective không kém allocation cũ.
3. Objective bằng expected revenue thật **của allocation policy đó**; lấy kỳ vọng
   qua observations giữ bất đẳng thức. Với approximation không đánh giá đúng
   policy, bước chuyển sang true value không còn bảo đảm.

Đó là cấu trúc monotonicity của decision theory, không bằng chứng hai bài toán
có cùng EVPPI. §4/Example3/PDF16 còn cho re-solving **bid-price** làm hại ngay cả
khi dùng SLP: lớp policy rất quan trọng. Không khái quát SLP thành M1.

§6/Table1/PDF24 có DLP401980±406 và409740±468 với các schedule khác nhau;
đây là paper simulation1000replications/95%CI, chưa tái lập. Hai numerical examples
không đủ suy GS<0 hiếm hoặc phổ biến trên lưới chọn gần decision boundary.

## 3. R02: đã chạy lại phản ví dụ

Giữ đúng Example1: capacity2, fares10/2, independent Poisson rate1 mỗi class,
horizon2, re-solve t1. Initial allocation(2,0); khi first-period high arrivals=0,
DLP mới chọn(1,1). Đặt q=exp(−1):

| Expected revenue | Công thức | Kết quả tính lại |
|---|---|---:|
| Không re-solve | 20−40q² | 14.586588671 |
| Re-solve t1 | 20−8q−22q² | 14.079588239 |
| Thiệt hại | 8q−18q² | **0.507000431** |

Đơn vị revenue units; không seed/MC/CI vì cộng xác suất18nhánh gộp đủ toàn bộ
support liên quan, không cắt tail. Decimal50digits, so closed forms và replay70digits.
Conditional branch khớp Eq10: **8.963616765→7.585446706**.
[Code](../../experiments/lessons/l2_8_resolving.py) ·
[18nhánh CSV](../../results/lessons/l2_8/part2/cooper_example1.csv).
Không phải replication toàn paper, cả4ô RM hay kết quả plant v1.2.

## 4. R04 → plant: dùng được đến đâu?

SC là **MP-feasibility** của updated old solution ở successor states; không chỉ
action cũ còn hợp lệ trong hệ vật lý. Π-accuracy là objective khớp true expected
return của policy được MP sinh/update, không đòi khớp toàn dynamics. Prop3 cần
thêm SC, time-dependent MP và Eq9, cho old value≤re-solving value+α1+αn.
Remark2/PDF10 nhắc α thường cần policy evaluation: chưa phải predictor rẻ.

Trong Cooper example, old(2,0) không thỏa demand bound(1,1) của DLP mới
(§4.1.6/PDF13); capacity-feasible chưa đủ SC. Vì vậy không gộp cơ chế này và
Jensen mean-rollout thành một cơ chế giống hệt.

**Suy luận one-shot của repo:** cho fixed y, a0=a0(y) là old action, a1(x) là
argmin Jhat theo S1. Nếu action cũ khả thi và Jhat đánh giá đúng true J của cả
hai action, thì J(a0,x)−J(a1,x)≥0. Đây là analog đủ, không áp nguyên định lý SC.
Với b=Jhat−J và δ=J−Jhat:

```text
true improvement = predicted improvement − b(a0,x) + b(a1,x)
                 = predicted improvement + δ(a0,x) − δ(a1,x).
```

Nếu |b(a,x)|≤εx cho cả hai, lower bound là−2εx; nếu đã chứng nhận một phía
0≤δ≤εx thì bound−εx. Lấy expectation cho GS. Common action-independent bias
cũng triệt tiêu trong gap. Đây là **sufficient diagnostic dựa trên true costs hoặc
certified errors**; chưa có feature chỉ từ inputs dự đoán được miền GS≥0.

V1 hi: old Switch, new Stay; predicted gain1/2, δold0,δnew1, true gain−1/2.
Lo gain0, hai mode xác suất1/2 ⇒ **GS=−1/4**. Action cũ vẫn feasible mà có hại.
[CSV diagnostic](../../results/lessons/l2_8/part2/v1_diagnostic.csv).
Không dùng true costs để chọn H1 rồi gọi predictive validation. Không cần mở
Jasin/Kumar thành reading mới trong đợt này; gợi ý gần-degeneracy vẫn chỉ queue.

## 5. A1–A4: đã chạy gì và kết luận vùng

[Thẻ dự đoán trước phiên](../../results/lessons/l2_8/part2/reading_card.md)
ghi AI/exposed: A1 0Tier1/1Tier2, A2 0/1, A3 0/2. Đây không phải blind prediction
của tác giả. [Ledger từng call/retry](../../results/lessons/l2_8/part2/search_calls.json).

| Vùng | Screening events | Kết luận có giới hạn |
|---|---:|---|
| A1 routing/NDT | 20+19keyword,5forward P04 | NDT26 Tier2 cho trực tiếp NDT gating/regret. P03 đã có; những nguồn đọc chưa xác nhận cùng D19Γ. Forward chỉ filter `title.search:model`, chưa union prediction/digital twin. PC3/PC5 cần thu hẹp framing, chưa clearance |
| A2 freshness/model mismatch | 20+20keyword,5forward S11 fallback | AIS22 Tier2 cho information-state/model approximation, không D19. Query1 rất nhiễu, không có giá trị làm negative coverage. S2forward429 cảretry; OpenAlex journal-DOI thay arxiv seed, không coi hai tập citations giống nhau |
| A3 model adequacy/information | 20OpenAlex+20Scholar,20forward P12 | WM26 Tier1 framing có2×2; R45 official abstract là Tier2 screening/seed cũ, không primary T. **Bất ngờ:** có prior2×2 gần hơn dự đoán0Tier1. Chưa xác nhận cùng state-repair/model-repair estimand; không kết luận đã clearance PC5 |
| A4 re-solving | 20Scholar repeat variant2; Part1 riêng55events | R01/R02/R04 primary trả lời mechanism/conditions: prior có harm và sufficient non-harm. Scholar repeat tìm lại RM family/R01, xác nhận cùng **loại kết quả**, không exact ranking |

**169 là số lượt sàng**, không169unique works hoặc full reads. Ba nguồn mới
được chọn đọc duy nhất: NDT26/AIS22/WM26, có phê duyệt; không tự tải các nguồn
screen-only hoặc3proposals Part1. Keyword A3q1 timeout cả trước/sau VPN nên dùng
OpenAlex; ba retry Scholar khác thành công. S11 citation API vẫn429.

**Giới hạn hồ sơ:** payload từng rank của các calls trước resume không còn trong
working context; chỉ checkpoint số đếm/query/examples được giữ. Ledger ghi rõ,
không tạo169dòng giả. Không audit độc lập được toàn per-rank decisions hoặc tổng
candidate unique; chỉ3selected-for-reading được dedup/verified primary. Đây là
deviation về lưu log, không coi artifact checks là full search reproducibility.

Dừng theo session scope/budget, **không đạt2×20 zero-new/saturation**: còn candidate,
A1q2chỉ19, forward chưa exhausted, query nhiễu/timeout/missing abstracts. Kết luận
vùng chỉ áp vào các nguồn đã sàng/đọc, không tuyên bố đã bao phủ lĩnh vực.

## 6. Prior boundary và Gate

K-S9/K-S10 đã dùng trong freshness nên dùng **K-RM1/2/3**, không ghi đè ID cũ.
K-RM1: information-driven re-solving của approximate policy có thể hại (R02).
K-RM2: feasible old allocation + true policy objective cho monotonicity (R01).
K-RM3: SC+Π-accuracy⇒SI đủ cho non-deterioration (R04).

| Claim | Judgment hiện tại, không sửa forecast cũ |
|---|---|
| PC3 | **HOLD formal L2.9**. Không còn lý do “chưa đọc R02/R04”; cần wording thừa nhận RM và WM26. Không nhận first information-harm hoặc first2×2 repair. Chưa xác nhận prior cùng D20/D21/D19Γ |
| PC4 | **HOLD A05/L2.9**. Biết điều kiện R04 nhưng chưa có input-only usable H1 hoặc evidence vượt null. NDT26 threshold evaluation reuse không thay held-out test |
| PC5 | Forecast NARROW giữ nguyên. AIS/VE đã có adequacy priors; chưa đo GM/Cref hoặc chứng nhận K5, không đổi do một search hit |

Reviewer “đây là re-solving issue”: thừa nhận analog harm/non-harm đã có;
regime của repo là load-changing queue, hidden current mode, một quyết định;
estimand là true-expected-cost regret/interaction theo ô. **Khác regime/estimand
chưa tự thành contribution**; cần L2.9/A05 và kiểm evidence tiếp theo.

Technical reading/math artifacts đã có; **toàn L2.8 chưa PASS khoa học/formal**:
per-rank log có giới hạn, author Understanding/L-self/review và L2.9 còn mở.
G1/HOLD Phase4, contract, forecast, K5/null/H1 giữ nguyên.
