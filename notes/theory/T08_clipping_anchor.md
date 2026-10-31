# T08 — P-clip trong plant slotted v1.3

Người phụ trách: **Doan Van Tai** · 31/10/2026. AI soạn theo yêu cầu thực hiện
L4.7, không phải tác giả tự viết/tự chứng minh hoặc human review. Note hỗ trợ
paper, không tự chứng nhận Understanding, novelty hay hoàn tất Phase4.

Nguồn đặc tả: contract v1.3§1–3, T07, lessonL4.7 được cung cấp và source
`piecewise.py`, `profiles.py`, `population.py` của production engine. Không đổi
contract/engine/metric. Đây là chứng minh cho **họ slotted R2**, không nhận đã
chứng minh continuous-limit hoặc packet-Poisson variant.

## 1. Định nghĩa đúng units và thời điểm

Cố định current state x gồm backlog và mode của hai path, action a giữ suốtH
slots, dt=h/H, queue vô hạn, arrivals ngoại sinh, cost endpoint tuyến tính.
Với một path: q0>=0, xi_k=(lambda+6z_k+managed(a)−10)dt, k=0..H−1.
Modez0 đã biết; mỗi transition trước slotk>=1 có keep probability
p=(1+exp(−2dt/kappa))/2∈(0,1). Vì vậy mọi H−1-bit transition sequence có
xác suất dương, **slot0 không có transition**. M0 dùng conditional means
E[xi_k|x,a]=(lambda+managed−10)dt+6dt z0(2p−1)^k.

Đặt i_k=max(0,−q_k−xi_k) là unused service **packet** trong slotk. Lindley:

```
q_(k+1)=q_k+xi_k+i_k
R_n=sum(k=0..n−1) i_k=max(0,max(j=1..n)(−q0−S_j)), S_j=sum(k<j)xi_k
q_n=q0+S_n+R_n
J(a;x)=dt[Hq0+sum(k=0..H−1)(H−k)E[xi_k|x,a]+sum(n=1..H)E[R_n|x,a]]
```

R_n có đơn vịpacket; **idle cost** W=dt sum_n R_n có đơn vịpacket·s.
`piecewise.idle` trả weighted regulator trên action lattice; `quantum*dt`
đổi rawprofile sangpacket·s. Nó không chỉ trả total unused capacityR_H.
M0 dùng cùng linear term, thay E[R_n] bằng R_n của đường conditional mean.

## 2. P-clip và chiều sai số cost

**P-clip:** nếu không có strict reflection trên mọi future path có xác suất
dương, với currentx/action đã cố định, thì J_M0(a;x)=J_M1(a;x).

Thật vậy, mọiq0+S_n>=0 nênR_n=0. Kỳ vọng tuyến tính cho
E[q_n|x,a]=q0+sum(k<n)E[xi_k|x,a]>=0. Các partial sum của mean path đều
không âm; Lindley của mean path cũng không thêm regulator. Hai cost bằng
nhau vì cost là tổng tuyến tính theoq_n. Chạm đúng0 nhưng không cần cắt một
đối số âm vẫn thuộc trường hợp này. Không dùng điều kiện mean path riêng
không rỗng để suy mọi stochastic path đều không rỗng.

Với mọi future vectorxi, q_n=max(q0+S_n,max(j=0..n)(S_n−S_j)) là max của
các affine functions, nên lồi. Jensen có điều kiện theo cùngx/action cho
J_M0(a;x)<=E[J(a;future)|x]=J_M1(a;x). Không cần các increments độc lập.
M0 có thể phản xạ mà vẫn bằngM1, ví dụH=1, future rate đã biết hoàn toàn.
Vì vậy possible reflection chỉ là điều kiện **cần**, không đủ cho model error.

Đặt e_a=J_M1(a;x)−J_M0(a;x)>=0. Gap error:
Delta_hat−Delta=e_Stay−e_Switch, có thể mang cả hai dấu. Chênh idle cost,
argmin threshold và regret là ba mắt xích khác nhau. Có clipping không tự
chứng minh Γ khác0, độ lớnΓ, hoặc dấuΓ.

## 3. Clip chính xác trong slotted model

Clip(x) là tồn tại một action, một path và future mode sequence có xác suất
dương sao cho có strict reflection trongh. Tách riêng từng path/action.
Vớiv_OFF=lambda−6+managed−10=−D, v_ON=v_OFF+12 và D>0:

```
t_OFF = h D
t_ON  = max(0, h D − 12dt)       # slot0 bắt buộcON; sau đó có thểOFF
strict reflection possible <=> q0 < t_mode
```

Đường allOFF sau slot0 nhỏ nhất theo từng increment. Khi mode0=OFF, min
partial sum là−hD. Khi mode0=ON, slot đầu tăngv_ONdt>0 trong miềncontract,
H−1slot sau lấyOFF nên min partial sum làmin(0,−hD+12dt). So với−q0 cho
công thức trên. NếuD<=0, mọiincrements>=0 nênthreshold0. Tổng quát ngoài
miềnv_ON>0 dùng minimum partial sum của sequence nhỏ nhất, không tự áp
công thức chuyên biệt. Biênq0=t_mode không có positive unused service.

**Chỉnh lý lesson§9.5:** q0<hD là một **cover bảo thủ** dùng được cho cảmode,
không phải iff tại mọi current state khi slot0 đã cố định. Ví dụH=1, modeON,
q0=0: q0<hD có thể đúng nhưng không thể reflection. Dùng cover choS_clip vẫn
cho cận hợp lệ, nhưng nó làm mất độ chặt; không trộn hai định nghĩa khi báo.

Trong miềncontract, D>0 ở cảhai action: u<10−lambdaA<=4 vàlambdaB<10 cho
minimum service headroom khiOFF vẫn dương. Stationary pre-Stay có atom
(q=0,modeOFF) với positive mass. Vì vậy Clip có positive probability trong
population này; P-clip không tự tạo một hộp parameter “không interaction”.

## 4. Cận population và yêu cầu về information

NgoàiClip, hai action costs vàgaps khớp, nên S1M0 có cùng strict-negative
decision với oracleS1M1 và regret0. TrongClip, regret nhị phân không vượt
|Delta(x)|. Dùng cùng true stationaryπ vàcùng action/cost:

```
G_M|S1=E_pi[|Delta(X)| 1{a10!=a11}] <= S_clip=E_pi[|Delta(X)| 1{Clip(X)}]
P_clip=pi(Clip), sigma=E_pi|Delta|, S_clip/sigma∈[0,1] khi sigma>0
```

S_clip vàsigma có đơn vịpacket·s; 100S_clip/Cref mới là%Cref. P_clip và
S_clip/sigma không có đơn vị. S_clip dùng trueDelta nên là **outcome-informed
diagnostic**, không phải independent/cheap parameter-only predictor.

Nếu Clip cóπ-mass0, thìDelta_hat=Delta π-a.s.; true sharedD(X|Y) cho cùng
gap kỳ vọng ởS0, nênGM=GM|S1=Gamma=0 vàGS=GS|M1. Điều kiện này phải đúng
trên population/support, không suyGamma=0 toànpopulation từ vài state busy.
TừT07: |Gamma|<=max(GM,GM|S1)<=max(GM,S_clip). Không thay cận này bằng
|Gamma|<=S_clip hoặc suy |Gamma|lớn bắt buộcGM|S1lớn khiGamma<0.

## 5. Đối chiếu engine và chỗ dễ hiểu sai

- `piecewise.mean_idle` dùng conditionalmean theoinitialmode, correlationr^k,
  và running maximum của cumulative deficits. Cách tính khớpM0 của contract.
- `profiles.get`: d=W_Switch−W_Stay, dh=M_Switch−M_Stay là **idle-cost
  differences**. Path gap đầy đủ còn linear term
  (post−pre)dt²H(H+1)/2. Hai path đổi đúng cùngu, nên linear terms triệt tiêu
  trong network gap; `population.pair_loss` cộngdA+dB+c_sw là đúng.
- `saturation_OFF_max_index` áp modeOFF vàbacklog thấp để cảhai **mean paths
  rỗng ngay slot đầu và giữ rỗng**. Khi đó actual mean costs bằng0, idle
  difference bù linear term vàdh=(pre−post)dt²H(H+1)/2. Đây không phải
  trường hợp queue luôn bận như lesson§9.1 mô tả. Với backlog cao không
  thể reflection, d=dh=0; mỗi path vẫn có linear cost/gap riêng.
- Kiểm Jensen phải so per-action true/mean idle costs (chung linear term),
  không yêu cầu d−dh cùng một dấu. Khi so `profiles.values`, indices thuộc
  stationary latticeunit; code mới ghi rõ q_requested,q_actual vàceil index,
  không dùngint() âm thầm truncate. Không sửa code production frozen.

## 6. Tự tính ví dụ cái bồn và giới hạn

Ví dụ minh họa continuous hai fixed-rate paths của lesson, không phải slotted
R2 measurement: h=1/2, netrates(−7,+5) đồngkhả năng. q0=5 cho true costs
(13/8,25/8), mean19/8=2.375, mean-path19/8. q0=1 cho (1/14,9/8),
true67/112≈.598214, mean-path3/8, Jensen gap25/112≈.223214packet·s.
Self-checklambdaA8,u1.5,h2: D_Stay=6.5packet/s, hD=13packet; thresholdON
của slottedmodel là13−12dt thay vì13.

Chỉ với fluid/infinite-buffer/linear-cost/conditional-mean/action-fixed/exogenous
background mới được dùng lập luận này nguyên dạng. Không xác nhận packet/drop,
realism hay novelty; clipping là một nguồn sai số cấu trúc cần thiết củaM0
trong plant, còn dự báo magnitudeΓ cần kiểm độc lập. PartC correlations trên
discovery không thay held-out prediction hoặc so null1-NN ởPhase5.
