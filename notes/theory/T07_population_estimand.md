# T07 — Estimand population v1.3: định nghĩa, giả định, identity

Người phụ trách/người soạn: **Doan Van Tai** · 28/10/2026 · DL-065.
Nhãn: **THEORY NOTE / reference cho audit; không phải contract đã khóa**.
Soạn theo ủy quyền triển khai lesson và viết thay của tác giả trong phiên làm việc.
Chưa có author-attestation về tự dẫn công thức hoặc read-back kín sách T07;
**Understanding/ownership OPEN**. Không dùng bản soạn này để tự đóng điều kiện đó.

Nguồn đặc tả: ba phần lesson L3R.2 được cung cấp; [T01](T01_single_observation.md),
[contract v1.2 D9–D23](../01_definitions_v1_2.md),
[proposal v1.3](../01_definitions_v1_3_draft.md),
[plan §9](../phases/PHASE_3R.md). Không đọc engine population để viết reference này.

## 1. Câu hỏi estimand này trả lời

Tôi muốn đo repair làm giảm bao nhiêu expected decision regret khi mỗi episode gặp
một snapshot được lấy từ một joint law đã khai báo. Tôi lấy trung bình theo snapshot
và state đứng sau snapshot đó; controller S0 vẫn chỉ nhận một snapshot mỗi episode.
Đây là câu hỏi khác thiết kế v1.2 điều kiện tại một snapshot, và không có nghĩa là
pilot đại diện cho tần suất regime ngoài đời hoặc population tự bảo đảm hiệu ứng trơn.

## 2. Ký hiệu và quyền thông tin

| Ký hiệu | Nghĩa / đơn vị | Ai biết, lúc nào |
|---|---|---|
| c | Regime: λA, λB, κ, **u**, h, τ, capacity và các lựa chọn law/cost được ghi rõ | Thiết kế trước action; η chờ L3R.5 |
| Y=y | Backlog A/B tại t0−τ, không mode; packet | S0 tại t0 |
| X=x | Backlog q=(qA,qB) và mode m=(mA,mB) tại t0 | S1 tại t0; evaluator lấy trung bình |
| P_c(Y,X) | Joint law của episode; stationary hoặc transient là lựa chọn chưa adopt | Đặc tả trước audit/confirmation |
| p(y), D(x\|y), π(x) | Marginal Y, conditional X, marginal X suy từ cùng joint law | Belief cho S0; π không mặc định stationary |
| a∈{0,1} | Stay=0, Switch=1; Switch iff gap<0, hòa Stay | Controller quyết tại t0, giữ suốt h |
| J(a;x) | Expected future cost E_w[C(a,w)\|x], packet·s | M1/evaluator; không ai thấy future w |
| Δ(x), Δ̂(x) | J(1;x)−J(0;x), predicted M0 gap theo từng state; packet·s | Δ cho M1; Δ̂ cho M0 |
| g(y), ĝ(y) | E_D[Δ\|y], E_D[Δ̂\|y] | S0 dùng cùng D cho cả hai model |
| L̄sm, C̄ref, σ̄ | Population cost; C̄ref=L̄11 đề xuất; σ̄=Eπ\|Δ\|; packet·s | Evaluator; tỷ lệ chỉ có nghĩa nếu mẫu số dương |

Regime ở đây là các tham số vật lý cố định, khác snapshot ngẫu nhiên bên trong regime.
Số cost của toy dùng **đơn vị cost quy ước**, không gán là số đo packet·s từ plant.

## 3. Định nghĩa ba tầng và sáu contrast

Đặt A(z)=1[z<0]. Với cùng true conditional law D:

```text
a00(y)=A(E[Δ̂(X)|y])      a01(y)=A(E[Δ(X)|y])
a10(x)=A(Δ̂(x))          a11(x)=A(Δ(x))

J(a;x)=E_w[C(a,w)|x]
L0m(y)=Σx D(x|y) J(a0m(y);x)
L1m(y)=Σx D(x|y) J(a1m(x);x)
L̄sm=Σy p(y)Lsm(y)

ḠS=L̄00−L̄10            ḠM=L̄00−L̄01
ḠSM=L̄00−L̄11           Γ̄=L̄10+L̄01−L̄00−L̄11
ḠS|M1=L̄01−L̄11         ḠM|S1=L̄10−L̄11
```

Tổng là ký hiệu cho kỳ vọng; với backlog liên tục cần tích phân theo measure,
gồm atom tại 0 và phần liên tục. J đã lấy kỳ vọng theo future w; không cấp w cho oracle.
M0 tính cost mean-rollout từng state rồi lấy trung bình theo D (D10), không rollout
từ state trung bình. Trong golden toy Δ̂ được cho sẵn, không kiểm vật lý mean-rollout.

Mỗi regret R̄sm=L̄sm−L̄11; trừ cùng oracle nên contrasts từ regret giống contrasts từ cost.
S0 chọn một action cho toàn conditional population của y; cho a00 nhìn x là leakage.

**D22, đường thêm backlog trước, mode sau:**

```text
a_cb(y,q)=A(E[Δ̂(X)|Y=y,Q=q])
L̄cb0=Σy p(y) Σq D(q|y) E[J(a_cb(y,q);X)|y,q]
F̄=L̄00−L̄cb0;   V̄=L̄cb0−L̄10;   ḠS=F̄+V̄.
```

Ở đây q là **cả hai backlog**; ảnh cũ y vẫn được giữ để suy mode. Không thay y bằng q,
không đổi M0 giữa endpoints. Với nhóm có xác suất 0 thì bỏ contribution của nhóm đó,
không chia cho 0. cb0 và S1 đều là benchmark lý tưởng, chưa là repair khả thi.
Không khai báo nhóm q trong toy thì cb0/F/V **không được tính**, không gán cb0=0.

**Estimand / estimator / estimate:** công thức trên là estimand của joint law đã chọn.
Pilot dùng approximation với atom riêng, K40, cutoff 1−10⁻⁴, đại diện trung vị,
renormalization, dt1/120 theo mô tả lesson; L3R.1 xác nhận ref/K, chưa audit thuật toán.
Các CSV pilot là estimates, không biến số approximation thành định nghĩa chính xác.
K80/dt1/240 chỉ đã kiểm 9 tọa độ pilot; mức số và tolerance v1.3 còn OPEN.

## 4. Giả định: nội dung, nơi dùng, khi vỡ

| ID | Nội dung | Dùng ở đâu | Nếu vỡ |
|---|---|---|---|
| A1 | p và D coherent từ cùng P(Y,X), chuẩn hóa đúng | ΣpD=P_X, mọi kỳ vọng population | Có thể đang cộng các law không tương thích |
| A2 | Trước quyết định routing Stay cố định, đã stationary | Gọi P_X=π_stationary và so tuổi τ với marginal X cố định | Transient vẫn có total expectation nhưng marginal có thể đổi theo τ |
| A3 | Quyết định định kỳ hoặc lịch độc lập state | Dùng unconditional stationary population | Trigger theo alarm phải condition **cả joint law**, không chỉ sửa trọng số tùy ý |
| B1 | D là true posterior; M1 và evaluator dùng true J/cùng law | S0M1 tối ưu và T01 | Có thể mất ḠM≥0 khi policy dùng sai law |
| B2 | Cùng belief/quyền thông tin trong một hàng S; model repair không sửa estimator | So a00/a01 dưới cùng D, D9/D21 | Repair trộn cả thông tin và model, không còn contrast hiện tại |
| B3 | Hai action, strict-negative Switch, tie Stay | Dạng regret {0,\|Δ\|}, công thức gap/stakes | Nhiều action cần bound khác; đổi tie vi phạm hợp đồng dù có tie true-cost không mất regret |
| B4 | M0/M1 S1 policy và J chỉ phụ thuộc x,c; finite/integrable cost | Đổi thứ tự kỳ vọng, invariance S1 | Nếu policy còn tùy y hoặc law/objective đổi thì không suy invariance |

A1 cho total expectation dù không A2/A3. A2/A3 là điều kiện đủ cho cách hiểu
stationary periodic đang xem xét, **chưa adopt** làm target population v1.3.
Chỉ nói S1/C̄ref/σ̄ không đổi theo τ hoặc observation channel khi **P_X, J và S1 policy
giữ nguyên**. Không được thay p hay chọn population khác rồi mặc định vẫn cùng π.

## 5. Sanity list và chứng minh

| ID | Phát biểu | Lý do | Điều kiện |
|---|---|---|---|
| S01 | Σy p(y)D(x\|y)=P_X(x) | Tổng joint mass theo Y | A1 |
| S02 | L̄10=EπJ(a10(X);X) | Thay ΣpD bằng π | A1,B4 |
| S03 | L̄11=Eπmin_a J(a;X) | Tương tự S02 | A1,B1,B3,B4 |
| S04 | Hai ô S1 không đổi khi chỉ đổi observation channel/τ với marginal X cố định | S02–S03 không chứa Y | A1,B4; A2/A3 đủ cho so tuổi dừng |
| S05 | C̄ref=L̄11 và σ̄=Eπ\|Δ\| cũng bất biến trong so sánh đó | Chỉ là hàm π,J | A1,B4, fixed π/J |
| S06 | 0≤L̄sm−L̄11≤σ̄ | Mỗi state regret là 0 hoặc \|Δ\| | A1,B1,B3 |
| S07 | ḠSM,ḠS\|M1,ḠM\|S1≥0 | Mỗi số là một ô trừ oracle | S06 |
| S08 | ḠM=E_Y[\|g(Y)\|1[a00≠a01]]≥0 | a01 tối ưu hai expected true costs cho từng y | B1/B2/B3 |
| S09 | ḠM≤σ̄ | \|E[Δ\|y]\|≤E[\|Δ\|\|y], rồi lấy E_Y | A1,B1/B2/B3 |
| S10 | ḠS\|M1=E_Y min(P(y),N(y)) | P=EΔ⁺, N=EΔ⁻, g=P−N, L11=EJStay−N | B1/B3 |
| S11 | Γ̄=ḠS\|M1−ḠS=ḠM\|S1−ḠM | Khai triển bốn L̄ | Đại số |
| S12 | ḠS<0 ⇒ Γ̄≥\|ḠS\|>0 và ḠM\|S1≥\|ḠS\|+ḠM | S11 và ḠS\|M1≥0 | S07/S11 |
| S13 | Bốn contrast không âm đều ≤σ̄ | S06 và S09 | Các điều kiện trên |
| S14 | \|ḠS\|≤σ̄; −σ̄≤Γ̄≤σ̄ | Hai ô có regret trong [0,σ̄]; Γ̄=ḠM\|S1−ḠM | S06/S08/S11 |
| S15 | Chặn lesson −σ̄≤Γ̄≤2σ̄ cũng đúng nhưng lỏng | S14 mạnh hơn, không đổi nghĩa Γ | S14 |
| S16 | F̄+V̄=ḠS | Cộng rồi trừ L̄cb0 | Đại số D22 |
| S17 | F̄,V̄ có thể âm, dương hoặc triệt tiêu; \|F̄\|,\|V̄\|≤σ̄ | cb0 cũng có regret trong [0,σ̄] | A1/B3, cùng law/evaluator |
| S18 | σ̄=0 ⇒ mọi contrast và F̄/V̄ hợp lệ đều 0 | Δ=0 gần như chắc chắn | A1/B3; tỷ lệ stakes là undefined |

**Dẫn công thức (Bước 2–4).** Theo A1,
Σy p(y)D(x|y)=Σy P(y,x)=P_X(x). Đổi thứ tự tổng hữu hạn, hoặc tích phân khả tích
(B4), cho S02/S03. A2/A3 mới cho phép gọi marginal này là stationary law trước quyết định.

Với hai action, min(0,Δ)≤aΔ≤max(0,Δ), nên
0≤J(a;x)−min J≤|Δ|. Lấy E_{Y,X} cho S06.
Với từng y, L00−L01=(a00−A(g))g=|g|1[a00≠a01]. Nếu g=0, gain bằng 0
ngay cả khi actions khác nhau. B1/B2 giữ đúng law và information khi lấy so sánh này.

Đặt P=E[Δ⁺|y], N=E[Δ⁻|y]. Khi đó L01=E[JStay|y]+min(0,P−N),
L11=E[JStay|y]−N, nên hiệu là N+min(0,P−N)=min(P,N).
Nhóm bốn L̄ cho S11; dùng ḠS|M1≥0 suy S12. Đây là hệ quả, không phải phát hiện.
Các test hữu hạn chỉ kiểm triển khai các dòng này, không thay chứng minh trên.

## 6. Danh sách có thể sai (chưa khóa hypothesis)

1. Dấu và độ lớn ḠS theo miền plant, tuổi τ và joint law đã khai báo.
2. Độ lớn/vị trí của bốn contrast không âm, gồm vùng model-value đáng kể.
3. Dấu Γ̄ ở ḠS≥0; độ lớn phần vượt |ḠS| trong harm, tức ḠS|M1.
4. Dấu, độ lớn F̄/V̄ và phần triệt tiêu **theo đường D22** trong các miền đó.

Không chốt miền/ngưỡng ở lesson này. Γ̄ dương trong harm bị ép bởi S12;
**Γ̄ lớn ⇒ harm không phải identity**. Việc 79/79 cấu hình pilot với |Γ|≥1%C̄
đều harm là quan sát discovery được L3R.1 đếm, không là chiều đảo của S12.
F̄<0 mới hỗ trợ câu hẹp “backlog mới hơn làm tăng loss của fixed-M0 trên population
này”; chưa suy ra telemetry khả thi ngoài đời có hại hoặc novelty.

## 7. Các lựa chọn để L3R.5 chốt

| Lựa chọn | Phương án / trạng thái | Hệ quả cho claim |
|---|---|---|
| P(Y,X) | Stationary periodic / transient / condition trên trigger; OPEN | Định nghĩa episode nào đang được lấy trung bình |
| Regime, η | Dùng u cho tới khi chốt η=u/2 hay u/(μ−λB) | Không nhầm label pilot với tỷ số headroom vật lý |
| Normalization | Đề xuất ratio-of-expectations Ḡ/C̄ref; E[G(y)/Cref(y)] là estimand khác; OPEN | Fraction tổng cost khác trung bình fraction của từng episode |
| Primary/secondary | %C̄ref hay %stakes cho từng hypothesis; OPEN | Không đổi thang sau khi nhìn CF outcome |
| εR, sensitivity | 1% là candidate cần lý do mới; .5%/2% là sensitivity đề xuất | Không gọi là ngưỡng v1.3 prereg trước pilot; pilot đã thấy |
| Zero denominator | Giữ absolute outputs; relative undefined/excluded có lý do, không epsilon | Không báo 0% cho 0/0 hoặc bỏ regime âm thầm |
| D22 | Có báo F̄/V̄ và policy nhóm y,q như trên hay không; OPEN | Pilot thiếu D22 nên hiện chưa tách harm do backlog/mode |
| Numerics | K, dt, tail/atom, precision, convergence, stop rules, MC/CI; OPEN | S1 quadrature estimator có thể đổi dù estimand bất biến |

Hai mẫu số trả lời hai câu hỏi khác nhau: tổng queue cost (operator) và phần decision
stakes (controller). Ngưỡng v1.2 không tự chuyển nguyên nghĩa sang population v1.3.
Mọi lựa chọn mới sẽ là sau pilot; ghi exposure thay vì gọi chúng pre-pilot.

## 8. Toy, đáp án tay và golden reference

| Toy | Tính tay / đáp án exact |
|---|---|
| Ba snapshot | GM(y)=(0,4/5,0), weights=(1/2,3/10,1/5), ḠM=6/25=0.24 |
| Tuổi ngắn | L̄01=93/10; L̄10=19/2; L̄11=9; ḠS\|M1=3/10 |
| Tuổi dài | Các g=(−4/5,−1/5), chọn Switch cả hai; L̄01=19/2; L̄10=19/2; L̄11=9; ḠS\|M1=1/2 |
| Lỗi bù trừ −2,+3 | L̄=(10,10,21/2,10); (GS,GM,GSM,Γ,GS\|M1,GM\|S1)=(−1/2,0,0,1/2,0,1/2) |
| Biến thể −4,+3 | L̄=(11,10,21/2,10); sáu contrast=(1/2,1,1,−1/2,0,1/2) |
| D22 mode-only / backlog-only | Cùng GS=−1/2 nhưng (F,V)=(0,−1/2) / (−1/2,0) |
| D22 triệt tiêu | Bốn state Δ=(−1,−1,−1,+1), Δ̂=(−1,+2,−3,+1); (GS,F,V)=(0,−1/2,+1/2) |
| Hai cách ratio | E gain/E cost=1/100; E(gain/cost)=1/20 |
| 13%C̄ / stakes30%C̄ | 13/30=43⅓% stakes, không phải 13% stakes |
| Bias b=.1,.2,.3,.4 | Population GM=.005,.020,.045,.080; snapshot y*=.35: 0,.15,.15,.15 |

Toy 10 snapshot chỉ khớp b²/2 tại b được liệt kê. Nó có bước nhảy tại b=.05 (tie Stay):
GM=0 khi b=.049, GM=.005 khi b=.05. Không suy tính trơn tổng quát từ support hữu hạn;
xấp xỉ O(b²) cần mật độ gap đều đặn quanh 0 và giả định lỗi gần biên như lesson nêu.

Golden: [tests/test_population_toys.py](../../tests/test_population_toys.py).
8 test nguồn và các test bổ sung dùng Fraction, 500 joint laws hữu hạn với seed20261028;
một kiểm thêm bound dùng lại **cùng** 500 laws, không gọi là 1.000 laws độc lập.
Golden không import engine và chỉ đánh giá toy hữu hạn. [Runner](../../experiments/lessons/run_l3r_2.py)
sẽ lưu cost/contrasts/phân số, kiểm 5 mutant và log; kết quả thực tế xem
[report](../../results/lessons/l3r_2/report.md), không coi lesson-reported 8/8 là run local.

**Read-back của tôi cần làm sau bản soạn:** tự giải thích vì sao Γ>0 trong harm,
vì sao S1 chỉ bất biến khi giữ marginal X, và vì sao GS<0 chưa nói được F<0.
Hiện chưa có xác nhận việc tự làm này. Không nâng G1, không khóa contract,
không tuyên bố engine verified hoặc mở Phase4 từ T07.


## 9. Bổ sung đặc tả vật lý trước MC — L3R.3 (DL-066, 28/10/2026)

Bổ sung này theo nguồn **đã tồn tại trước pilot**: grid_v1.md dòng14 cho R2;
contractv1 D1/D7 cho thứ tự slot; D5/D13 v1.2 cho action/cost. Không thay plant cũ.
S1: keep=(1+exp(−2dt/κ))/2, κ=Tmode/age, age=1s. S2: state là đầu slot0; mode
hiện tại cấp arrivals, phản xạ backlog tại0, cộng cost endpoint rồi đổi mode cho
slot kế. S4: chụp backlog tại đầu slot t0−age; đẩy đúng 120·ref slot pre-Stay tới
x đầu slot t0. S6: Stage3 thêm c_sw packet·s **một lần** vào cost Switch; đây là
scenario audit của pilot, không sửa D13v1.2 hoặc adopt contractv1.3.
[Đặc tả độc lập đầy đủ](../../experiments/R3R_02_audit/mc_physical_spec.md).

Sai số giữa hai mức refinement là estimate chẩn đoán, không tự là certified bound.
Không suy lỗi số luôn co đơn điệu; không suy MC dùng bin-policy có cùng law với
representative-point quadrature. So z thuần cần cùng joint law đã xấp xỉ; so với
population thật phải báo phần allowance số, tail và giới hạn tương ứng.
Số79 về largeGamma ở §6 là trên162 cấu hình Stage1+2 phân biệt, không phải toàn210.
Understanding/read-back của tác giả vẫn OPEN.
