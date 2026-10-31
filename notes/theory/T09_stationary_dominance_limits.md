# T09 — stationary dominance: điều kiện và lỗi cần sửa trước freeze

Người phụ trách: **Doan Van Tai** · 31/10/2026. AI-assisted, không tác giả tự
chứng minh/human review. Giữ slottedR2, finiteh, physicalcost và namespacev1.3.

## 1. Điều có cơ sở

P1 trước action đã stationary dướiStay nên E[J_Stay,h]=h*r_Stay chính xác,
vớir_Stay=E_pi[QA+QB]. Khi cảhai action stable, có thể tínhr_a từ stationary
law của từng path dướiaction đó, cùngdt,không dùng true finite-horizon cost.
Đặt s=r_Switch−r_Stay; r cóđơn vịpacket, s cũngpacket, h*r làpacket·s.

M0 dùng conditionalmeanrate drift→lambda+managed−mu<0. Với mỗi fixed(q,m),
sau hữu hạnthời gian, mọi subsequentmeanincrements đềuâm vàqueue đãxảhết;
meanpath đứng0. Do đó cumulativeM0cost tiến về một finiteconstant **phụ
thuộcstate**, không uniform trên mọi backlog. Giá trị h32profile `dh` phải
được tính từ mean-only code; `profiles.get` dựng cảtruecost nên không phải
entrypoint hợp lệ cho một heldoutpredictor không dùng M1 finiteh.

Expansion J_a,h(x)=h*r_a+T_a(x)+o(1) cần stability/moment/convergence conditions;
không tự chứng minh bằng việcpopulationStay stationary. Tronglượt này nó là
asymptoticmechanism cầnkiểm, không theorem được vay trực tiếp từP13. NoteP13
cũ nói Lévy increments, continuouscapacity/averageobjective, khác correlated
two-mode routing. Không gọi cả H-L1/H-L2 là novelty hoặc paper replication.

## 2. Không có uniform finite-h argument trong lesson

T_a(x)=O(1) theo h tại **mộtx cố định** không cho bounduniform theox khiπ
có unboundedbacklogsupport. Độ trải M0 cũng không chặn được true transient.
Vì vậy không triển khai hstar từ rangeM0 rồi nhận mọi state có cùng oracle
action sauhstar; cũng không nhậnGS|M1 bằngexact0 sau mộthữu hạn horizon.

Phản lập luận ngay trong plant: với bất kỳ finiteH, chọnQA đủ lớn đểA không
reflection dướihai actions trênmọi futurepath, QB=0 vàmB=OFF. Chuyển u khỏiA
giảmcost đúngu*dt²H(H+1)/2. ỞB, cảhai queues sau slot0đều0(vìOFFdriftâm);
managedload chỉ làm tăngcost tối đau*dt²H(H−1)/2. Do đó networkDelta<=−uHdt²<0.
Đảo lạiQB lớn,QA=0,mA=OFF choDelta>=+uHdt²>0. Các state tail/zeroatom này
có positive stationarysupport. Không thể suy mộtfiniteH khiến mọiX có cùng
action. Lập luận **không** tự chứng minh GS|M1>0 ở mọih: S10 còn cần posterior
theoY straddle boundary, không chỉ globaloracleactions khác nhau.

H-L1 được tác giả chọn sửa thành finite-panel inequality: GS|M1/Cref<=.5%
ở>=90% các tọa độ ngoại suy đã khai. Không dùng hstar hoặc exactvanishing.
GS+Gamma=GS|M1 vẫn làidentity; nếu RHS nhỏ thì chỉ có approximatecancellation,
không một evidence độc lập vềinteraction hoặc một tỷ lệ đóng góp từhai medians.

## 3. Predictor model value và tie rule

Asymptoticcandidate cho fixedstable regime, s!=0 và adequateintegrability:

```
a_stat = 1[s<0]                           # exacttie chọnStay
a_M0,h(X) = 1[Delta_hat_h(X)<0]
g_hat_h_pct = 100*abs(s)*Pr_pi(a_M0,h!=a_stat)/min(r_Stay,r_Switch)
```

Không so `sign(Delta_hat)` với `sign(s)`: nếuDelta_hat=0 vàs>0, cảhai
actions làStay nhưng signcomparison sẽ gán sai. M0 có positive-massties,
ví dụhaiqueues0/OFF, nên đây không phải một edgecase cóthể bỏqua. Giữ exact
zero/saturation certificates củameanprofiles, không thêmepsilon đổi action.
NếulambdaA=lambdaB, stationary symmetry cho s=0: predictor0; không suy
finitehmodelvalue cũng0. Numerical signuncertain thì predictorNOT_READY.

Predictor chỉ dùngparameters, stationarylaws/moments vàM0 meanprofile; không
đọc Cref/loss/contrast finiteh của điểm cần dự báo. h cancels ởnormalizer
h*min(r), nhưng finitehmisclassification vẫn phụ thuộcM0,h. Output là%Cref
asymptoticapproximation, so với finitehtrueGM|S1/Cref trong discovery/Phase5.
Stationarylaw làtrue-lawinput đượccho trongcontrolledstudy,không measured
network data hoặc deployablecheap predictor đãvalidated.

## 4. Những extrapolation cần kiểm độc lập

- g_infinity không nhất thiết lớn hơn một median10.68% của nhiều regimes;
  s vàπ khác nhau. Không suy hướng hội tụ monotonic trênmọi regime.
- s≈0 làmrelativefiniteherrors lớn; h/kappa không tự điều khiển toàn bộ
  queue mixing/draining, cònheadroom/backlogtail. Predictor có thể thua1-NN.
- Marginpositive cốđịnh có thể tiến vềStay pointwise khi h→∞, không uniform
  finiteh. Recoveryratio chỉ cónghĩa khi denominator modelgain khác0. H-L3
  không được giữ trongfreeze này theo lựa chọn tác giả.
- Lesson4.8 khôngchốt empiricaltimescale lớn: miềnrealistic vẫnUNRESOLVED.
  Longh/kappa test làmodel-conditioned extrapolation, khôngDCvalidation.
- `{k=.05,.1}x{h=16,32}` cómột tổhợp k=.1,h16 chỉđạt160; không phải cảbốn
  đều h/k>160. Panel mới dùngexactkeys và ratios320/640, guard trướcengine.
- Trongregistryhiệncó, h32chưa làdiscovery. Timingcase h32,k=.3 nếu chạy là
  calibration-only exposure mới(ratio106.67), không giả đó làđiểm cũ; tách
  khỏimọiheldoutkey và ghi history trước run. Không chạyh128.
