# T03 v2 — đối chiếu EVPPI/VSS và giới hạn EVMI

Người phụ trách: **Doan Van Tai** · cập nhật 24/10/2026. AI triển khai theo ủy
quyền. Đây là phép dẫn tham khảo, chưa phải tác giả tự dẫn kín sách hoặc L-self.
Contract v1.2 và các historical tags giữ nguyên.

## Giả định đủ, không phải điều kiện cần cho từng instance

| ID | Giả định | Contract |
|---|---|---|
| G1 | b(x)=D(x\|y), S0M0/S0M1 dùng chung belief | D9/D12 |
| G2 | S1 biết toàn bộ x=(qA,qB,mA,mB), chưa biết future w | D7/D11/D20 |
| G3 | M1 trả đúng J(a;x)=E[C(a,x,w)\|x,theta], tối ưu trên cùng action set | D10/D14/D15 |
| G4 | Các ô chấm cùng true D, objective và thông tin trước action đã khai báo | D18 |
| G5 | M0 rollout conditional mean future theo từng x rồi chọn argmin; exact tie Stay | D10/D16/D21 |

Giả sử cost khả tích, action set hữu hạn; các min tồn tại. Belief sai vẫn có thể
cho cùng action/equality; không dùng cách nói “khi và chỉ khi belief đúng”.

## 1. EVPPI: phép dẫn theo observation cố định y

Với a01=argmin_a E_b[J(a;x)] và a11(x)=argmin_a J(a;x):

1. G1/G3/G4 cho L01=min_a E_D[J(a;x)].
2. G2/G3/G4 cho L11=E_D[min_a J(a;x)].
3. GSgivenM1=L01−L11=min_a E_D J−E_D min_a J.
4. SOB14 Method, Eq4 dùng Xi và X−i với conditional expectation. Thay Xi=x,
   X−i=w, NB=−C, condition toàn bộ joint law theo y; tower property cho đúng
   biểu thức ở bước 3. Xác suất vật lý hidden state khác diễn giải unknown
   parameter của paper, nhưng functional bằng nhau dưới các giả định trên.

Đặt Delta=JSw−JSt, P=E Delta+, N=E Delta−. Vì
min(JSt,JSw)=JSt−Delta− và min_a E J=E JSt+min(0,P−N),

    GSgivenM1 = N + min(0,P−N) = min(P,N) >= 0.

Dương nghiêm ngặt iff P(Delta>0)>0 và P(Delta<0)>0. p_sw trong (0,1) và
nhãn candidate chưa chứng nhận điều kiện này: ví dụ Delta∈{−1,0} đồng xác suất
cho p_sw=.5 nhưng gain0. Không đưa dấu không âm vào prediction như discovery.

Với nhiều observations phải lấy E_y theo đầy đủ support; hai quantile không đủ
đại diện population. Với z là partial state information, chỉ khi chọn tối ưu
theo E[J\|y,z] mới có EVPPI(z\|y). D22 fixed-M0 không tự là EVPPI.

## 2. Conditional VSS: phép dẫn

Cố định x. EV(x) là min objective khi thay future bằng mean có điều kiện;
aEV(x)=argmin_a J0(a;x), RP(x)=min_a J(a;x), EEV(x)=J(aEV(x);x).
Theo định nghĩa VSS(x)=EEV(x)−RP(x)≥0. G2–G5 cho a10=aEV và a11 tối ưu J,
nên L10=E_D EEV(x), L11=E_D RP(x):

    GMgivenS1 = E_D[VSS(x)] >= 0.

Đây là identity suy ra từ định nghĩa trong finite decision problem; không mượn
bounds LP/fixed-recourse của Birge khi chưa đọc đủ hoặc chưa kiểm giả định.
GM không tự là global VSS: S0M0 trung bình cost mean rollout trong từng state,
còn global EV thay cả hidden mode bằng mean input. V2 cho GM=1/4, global VSS0.

WS=E[min_a C(a,w,x)] cho phép hindsight future; L11 vẫn chọn trước future.
Do đó WS≤RP≤EEV bởi thông tin và optimality, nhưng L11 không phải WS.
EV và WS không có ordering chung cho toy nhị phân: V4 EV1/4>WS1/8.
Riêng cost toy lồi theo arrivals nên Jensen vẫn cho EV≤RP; không phủ định
Jensen hoặc mọi bound chỉ vì một ordering EV≤WS sai.

## 3. Belief sai, tie và các identity còn lại

Giữ M1 đúng, S1 full, đánh giá D nhưng S0 chọn từ b khác D:

    GSgivenM1 = EVPPI_D(x|y) + [E_D J(a_b;x) − min_a E_D J(a;x)].

Phần dư không âm, có thể0. V2 b_hi=3/4 cho 1/2=1/4+1/4. Subjective EVPPI_b
khác đánh giá true-law D; hai giá trị có thể tình cờ bằng nhau dù belief sai.
Tie Switch là equivalent control cho I1 dưới matched belief, không phải mutant
được yêu cầu làm identity vỡ. Khi belief sai, tie theo b chưa chắc tie theo D.

Gamma=GSgivenM1−GS=GMgivenS1−GM là bookkeeping, không tự là network mechanism.
Với một observation, T01 cho GM=|E Delta|1[a00≠a01]≤|model gap bias|.

## 4. EVMI và các cận trên

P11 §2.4 Eq2.7 tính EVPI(delta) theo belief, diễn giải upper bound cho EVMI;
không đo trực tiếp D21. M0 giống prior point0 chỉ về action trong toy, không
phải controller cài discrepancy prior. Biết theta không suy delta(x) đã biết ở
S0: V2 tiết lộ delta(x) có thể lộ mode, cho value1/4 (state information).
Conditional on x và biết toàn bộ discrepancy function thì không còn model
information cần học; vẫn có thể chịu loss vì dùng approximation.

Oracle state repair dưới fixed-M0 không luôn upper-bound feasible state repair:
V1 GS=−1/4 còn no-op gain0. Nhưng model-repair cần phân biệt: với cùng S0 info,
matched posterior và M1 đúng, L0,Mtilde≥L01, nên gain≤GM. Tương tự ở S1,
gain so với ô10≤GMgivenS1. R00 là cận chung từ ô00 cho cùng D/objective/actions,
không phải cận duy nhất cho mọi lớp repair. Đây là suy luận E0, không discovery.

## 5. Source và reproducibility

- [SOB14 note](../literature/papers/SOB14.md): AI targeted Method Eq1–4,
  published pp312–313, PDF pages4–5; không dùng regression method như outcome repo.
- [B82](../literature/papers/B82.md): abstract-only; [MAB11](../literature/papers/MAB11.md):
  nguồn bị giới hạn truy cập; [E07](../literature/papers/E07.md): abstract-only.
- [P11](../literature/papers/P11.md): AI targeted full-text §§2–6; không L-self.
- Script `python3 -m experiments.lessons.l2_2_voi_mapping`; JSON/CSV/log ở
  `results/lessons/l2_2/`; P11 toy ở `results/lessons/l2_3/`.
- Invariant I2 dùng VSS độc lập với a10; checker dùng lại a10 sẽ xanh ngay cả
  khi M0 bỏ mode. Full family/mutant counts là replication của các số đã exposed.

## Changelog

24/10/2026: v2 thêm hai phép dẫn, G1–G5, source notes, independent VSS checker,
corrections về strict positivity, D22, EV≤RP, EVMI và model upper bounds.
Không biến commit hiện tại thành chứng cứ dự đoán/viết proof trước exposure.
Record v1 bên dưới giữ nguyên để bảo toàn provenance và giới hạn đọc lúc đó;
các phát biểu “chưa” lịch sử không thay trạng thái v2 ở trên.

## Record v1 — 23/10/2026 (giữ nguyên)

Người phụ trách: **Doan Van Tai** ·23/10/2026. Đây là reading reference, không xác nhận tác giả đã tự đọc kín sách hoặc hoàn tất Phase2a.

**Nguồn đã mở:** Strong,Oakley,Brennan(2014), *Estimating Multiparameter Partial Expected Value of Perfect Information…*, DOI10.1177/0272989X13505910. Full publisher text, Method/Partial EVPI, Eqs1–4 định nghĩa optimal expected benefit trước/sau biết một nhóm inputs, vẫn tích phân uncertainty còn lại. [Primary publisher](https://journals.sagepub.com/doi/10.1177/0272989X13505910). Không copy phương pháp regression/experiment của họ thành kết quả của repo.

**Nguồn tiếp cận một phần:** Birge(1982), *The value of the stochastic solution in stochastic linear programs with fixed recourse*, DOI10.1007/BF01585113. Indexed primary PDF/abstract mô tả benefit của stochastic solution so deterministic expected-value approximation. [Primary repository PDF](https://deepblue.lib.umich.edu/bitstream/handle/2027.42/47912/10107_2005_Article_BF01585113.pdf). Direct fetch trả403 trong phiên này; không ghi đã đọc full paper hoặc kiểm tất cả assumptions/bounds của nó.

**Nguồn tiếp cận một phần:** Escudero, Garín, Merino, Pérez(2007), *The value of the stochastic solution in multistage problems*, TOP15,48–64, DOI10.1007/s11750-007-0005-4. Indexed publisher abstract nói mở rộng EVPI/VSS sang multistage và các bounds phụ thuộc cấu trúc bài toán. [Primary publisher](https://doi.org/10.1007/s11750-007-0005-4). Direct publisher fetch không truy cập được và bản author's proof qua CiteSeer trả403. Chưa đọc phần định nghĩa/chứng minh đầy đủ, không áp dụng trực tiếp inequalities của paper cho queue.

**Suy luận riêng từ contract/toán:** đổi benefit thành−cost, chọn revealed inputs=current state và uncertainty còn lại=future arrivals conditional on state; GSgivenM1 có dạng EVPPI có điều kiện observation. Với state đã biết, M0 thay future arrivals bằng conditional means: GMgivenS1 có quan hệ với VSS/certainty-equivalent comparison. Bài Birge là stochastic linear programming/fixed recourse; queue dynamics binary action không tự thỏa mọi assumption của paper. GM khi state còn ẩn giữ averaging belief trên state, nên không tự gọi nó là VSS của mean của toàn bộ random inputs.

Γ=GMgivenS1−GM chỉ là identity bookkeeping. Chưa kiểm đủ literature về tương tác thông tin-state và stochastic approximation; không kết luận “chưa ai làm”, không nâng G1. P11–P13 trong review cũ chưa được ánh xạ đủ sang bibliographic records. Các nguồn trên giúp xác định thành phần có prior name; chưa hoàn tất novelty search, prediction hoặc network validity. Việc tìm thêm tên VSS không tự giải quyết câu hỏi interaction.
