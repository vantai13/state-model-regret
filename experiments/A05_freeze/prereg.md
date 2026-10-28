# A05-F — PREREG trước fit và held-out predictions

Người phụ trách: **Doan Van Tai** · contract-v1.2 · DL-057 · 28/10/2026.
Tác giả trực tiếp chọn D25(ii), thiết kế A, K5+C1+PC4 và giao chốt chi tiết kỹ
thuật. Code/prereg do AI triển khai theo ủy quyền, không evidence tác giả tự dẫn
hoặc human review. Commit/hash thực ghi trong theta, predictions và receipt.

**RQ2:** trên thiết kế neo đã khóa, với cùng sổ cái Gaussian và ngân sách fit,
các biến động học trước action có thêm predictive value so với biến thiết kế không?
Prereg này commit sau author decision51c926f, trước fit và mọi feature/prediction
held-out mới. A04 đã exposed toàn38main; đây là discovery model selection.

## 1. Ba nhánh, giữ riêng provenance và kết quả

1. **PC4:** H1 soH0; metric chính duy nhất = MAE trung bình đều của
   **(GS,GM,Gamma)/Cref**, mỗi ô mỗi contrast trọng số1/(3n). Không đổi metric theoD.
   Margin **m=1/400=.0025**, tức0,25 điểm phần trămCref, bằng nửaepsilonE.
   Ds theo từng contrast chỉ diagnostic, không sáu cơ hội support riêng.
2. **K5/P5-rule:** [carry_K5.json](carry_K5.json) chứa nguyên văn Section4card,
   metadata nguyên vẹn, m_rule_count=1. MainK M19–M22vàQ M01–M04đãSTANDS;
   giữ Q-witness M01/M03, không thêmheld-outQ. TestK R03/R04,GM/Cref≤1/200,
   ALL; dùng nguyên grader A03 (numeric enclosure, adjacent dt, Kleene).
   Nhãn “khóa trướcA04”, không tiêu quota hypothesis mới.
3. **C1:** hậu discovery, tại **R05–R08** (κ1,h8,Aq90;Bq75 hoặceta.625),
   **GM/Cref≤1/200 ở mọi ô**. Chấm bằng cùng luật interval/eligibility củaK5,
   nhưng báo riêng là khóa sauA04. Không claimnominalGM=0 chính xác hoặc mọi
   tọa độ liên tục trong vùng. Một counterexample chắc chắn bác ALL;
   HOLD/intervalcắtbiên làUNRESOLVED, không được bỏ ô để cứu luật.

Base rates A04: GMnominal0=34/38;certifiedGM/Cref≤.005=36/38;≥.01=2/38;
a01=1[target=.7] ở38/38. K5 heuristic(36/38)^2=.8975069252. C1equivalence
heuristic đúng sự kiện(36/38)^4=.8055186808; .6408867335=(34/38)^4 chỉ cho
nominalzero, không gán nhầm choC1. Các heuristic giả định trao đổi/độc lập không
đúng ở thiết kế này, không phải xác suất/p-value thật.

**Nhãn headroom khóa trước:** nếu ô equivalence STANDS và upper(R00/Cref)<.005,
ghi STANDS_HEADROOM_LIMITED: headroom đủ chặn, không có evidence riêng M0 tốt.
Nếu không chứng nhận được điều kiện ấy thì không gắn nhãn; điểm chấm không đổi.
Headroom của R chỉ được tính trong A05-T, không làmfeature hoặc chọnô.

## 2. D25 và thông tin

DL-057 chọn **(ii)**: lambdaA là plant parameter cùng định nghĩa cho38main+12R,
cả H0/H1 có quyền dùng. Không p_sw thực, cost,J,L,gap,bias/margin/headroom thật,
quantile|Delta|,Cref thật hoặcD của ô test trongfeatures. Model trực tiếp dự báo
các đại lượng **đã chuẩn hóa**, không đọc Cref thật củaR để chuẩn hóa prediction.
Quyềninput chung không tự chứng minh hếtendogeneity; kết luận chỉ về paired
prediction trên thiết kế neo, không absolute forecast accuracy hoặc causal mechanism.

`features.py` chỉ đưa qua whitelist id,slice,kappa,alphaA,alphaB,eta,h,lambdaA,
yA,yB vàtarget lấy từ anchors.target. ID/slice chỉ dùng chiafold/truyvết,
không covariate. Không group,floor,p_sw/label,budget hoặc kết quảscreen làmfeatures.
Bậc0: kappa,quantile,eta,h,target. Bậc1: lambdaA,yA,yB và hằng số rateB8,
amplitude6,capacity10,age1,u=2eta. Bậc2: các công thức bên dưới.
**Không feature bậc3, không dựng posterior D held-out.**

## 3. Công thức features, leakage check từng họ

Tất cả dùng duy nhất whitelist/hằng số. Không kernel/engine/DP/rollout/cost/gap.
Kappa là **thời gian nhớ** theo exp(−2dt/kappa), không switching rate.

- target_signed=+1 cho .3,−1 cho .7, dùng chung trong mọihead của cả hai model.
- load_A=lambdaA/10;log_kappa=lnkappa;quantile_difference=alphaA−alphaB;
  eta;log_observation_sum=ln(1+yA+yB);alphaB;log_h=lnh. Bậc0–1, không dynamics.
- Proxy qA=max(0,yA+(lambdaA+u−10)age),qB=max(0,yB+(8−10)age),age=1.
  Đây là fluid proxy từ stale observation, không Eq hiện tại hoặcposterior moment.
- e_l^a=max(0,(10−rate_l−managed_l^a)h−q_l) /
  [1+q_l+|10−rate_l−managed_l^a|h]. A:managedSt=u,Sw0;B:St0,Swu.
  Ký hiệuast,asw,bst,bsw tương ứng bốn giá trịe. Chỉ là mức vượt biên fluid,
  khôngJ hoặcDelta thật. Leakage check: tính bằng scalar arithmetic từ bậc1.
- V(t)=36[kappa*t−kappa²/2*(1−exp(−2t/kappa))], variance input telegraph
  stationary của một queue. vh=2V(h),vtotal=2V(1+h) cho hai input độc lập.
  Không coi là conditional queue variance. Công thức ổn địnhexpm1/series ởxnhỏ.
- proxyB=qB²/[2*(10−8)]*eta/(1−eta), hệ số fluid long-windowQ02;
  không coi nó là cost trongh hoặc fullqueuegap. Miềneta<1 đã có ởfit/test.

| Tên bậc2 | Công thức |
|---|---|
| boundary_shift | (asw−ast)−(bst−bsw) |
| variance_h_scaled | ln(1+vh/(1+qA²+qB²)) |
| boundary_joint | ast+bsw |
| B_drain_proxy | ln(1+proxyB/[1+h(1+qA+qB)]) |
| boundary_balance | ast−bsw |
| variance_age_h_scaled | ln(1+vtotal/(1+yA²+yB²)) |
| boundary_difference | asw−bst |
| variance_boundary | ln(1+vh/(1+h²))*(ast+asw+bst+bsw) |

Q01,Q02,Q04 chỉ là candidate covariates; không nhận novelty từ tuổi×tải hoặc
variance. Q03 dùng truecost bị loại. Phi tuyến reflectedqueue/CE-gap chưa được
kiểm nhân quả ở A05; cầnknockout khác nếu muốn cơ chế.

## 4. Cấu trúc H0/H1 và cùng ngân sách

Cùng Gaussian: Delta~N(mu,sigma²),eM~N(b,tau²),rho **cố định0** cho cả hai.
Rho0 vẫn tạo đượcGamma>0,GS<0; giới hạn shared-Gaussian/rho phải báo.
Cùng tầng identity s=(Edelta,Ehatdelta,Eneg,T10)/Cref→6contrast.
Gaussian closedform trongledger.py;degeneraciesđược xử lý. Nếu roundoff ra ngoài
feasible: En=max(En,0,−Ed),T10=clip(T10,−En,Ed+En), dùng chung hai bên;
đây là two-stage range projection, không tuyên bố Euclidean projection.

Mỗihead mu,sigma,b,tau có **3 hệ số** trên[1,target_signed,zhead]. Mu,b tuyến
tính; sigma,tau=exp(loglinear), logprediction clip[−16,2] dùng chung để ổn định.
**k=4×3=12** hệ số/model, rho khôngfit. Không fitted parameter theo ô/lát.
12 nhỏ hơn20lát nhưng vẫn ít dữ liệu; báoLOSO và không suy populationCI.

Hai tập ứng viên/bên, thứ tựtie đã khai. Bảng zhead theo(mu,sigma,b,tau):

| Model/candidate | mu | sigma | b | tau |
|---|---|---|---|---|
| H0/coordinates_0 | load_A | log_kappa | quantile_difference | eta |
| H0/coordinates_1 | load_A | log_observation_sum | alphaB | log_h |
| H1/dynamics_0 | boundary_shift | variance_h_scaled | boundary_joint | B_drain_proxy |
| H1/dynamics_1 | boundary_balance | variance_age_h_scaled | boundary_difference | variance_boundary |

H0 dùng geometry/Gaussian và bias theo tọa độ, không strawman constantcontrast.
H1 dùng closedform physics transformations; cả hai truy cùng bộmetadata.
H1thắng chỉ là thông tin động học trong **họ bị giới hạn này**, không causalproof.

## 5. Fit và20-fold LOSO

Fit đúng **38mainA04ref2**, gồm3calibration. y gồm4normalizedsummarycenters;
T10=GM_S1−Eneg, cả hai từ cùngraw/ref2. Không bootstrap,MC,held-out outcomes.
Features scale bằngmean/std của **training partition mỗi fold**,std≤1e−12→1;
validation/test không tham gia scale. Không thêmpowers/bins/knots/tuners saufit.

Lossfit=mean squared error của4summaries +1e−4*sum(coef_nonintercept²).
Hai optimizer starts/model/fold:(sigma,tau)=(.03,.03),(.1,.1); mu/bstart OLS
với cùng headfeatures/labels ởtraining partition, clippedvàobounds. Mu/bcoeff
[-1,1];logheadintercept[-12,1],slopes[-6,6]. Scipy least_squaresTRF,2-pointjac,
max_nfev1200 mỗi start;ftol/xtol/gtol1e−10. Chọn successfulstartloss nhỏ nhất,
tie theo thứ tựstart. Không start thành công→FAILkhôngfreeze,giữlog;khôngtestlook.

LOSO bỏ **toàn lát** V01–V20 (V09/V10mỗi lát1ô,18lát khác2ô). Validationloss
=MSE4summaries mean trong lát; chọn candidate nhỏ nhất **mean đều20lát**,
tie theo candidate order. Không chọn bằngcontrastmetric hoặcheld-outD.
Sau chọnfit lại trên38ô bằng cùngprocedure. 80LOSO fits+2fullfits,
164solverstarts tổng;ngân sáchbằng nhau.Hai θ và mọi CVresults commit trước
đọc sanitizeddesignfeatures của12R. Loss liên tục vàcontrastthreshold khác nhau:
fit summaries tốt chưa đảm bảo gain predictions tốt.

## 6. Ô test và luật mở trước outcomes

Universe cả12R đã đăng ký: primaryR01–R08(nội suy1trục),weakR09/R10(h4,κ.6),
extraR11/R12(h12). Membership kiểm lại bằng tọa độ,khônglambdaA/p_sw hay error.
D_primary=mean_{i,g∈GS,GM,Gamma}|predH0−predH1|. D_group tương tự nhóm2ô.
Chỉ dự báo điểm đã khóa,khôngtargettruth. D được tính bằngFraction trên decimal
predictions đã ghi, so với margin1/400, khôngtolerance thuậnlợi ởngưỡng.

- D≥m→comparison nhóm được mở ởA05-T;D<m→DO_NOT_OPEN_COMPARISON.
- K5R03/R04 vàC1R05–R08 vẫn mở cho các luật tương ứng.
- Outcome IDs thực cần =union(các nhóm cóD≥m,K5,C1). Vì vậy cả12được đăngký,
  nhưng ôkhông cần cho bất kỳ nhánh nào giữ chưa mở. Đây là luật điều kiện
  trước predictions,không chọn từng ô theo metadata/outcome hoặc thay universe.
- Chưa có truth thì chưa cód/MAEtest hoặc SUPPORT/WEAKEN/FALSIFY thực nghiệm.
  NếuDthấp thì không sửa model/metric/margin sau khi đã thấy predictions.

## 7. Luật chấm A05-T đã khóa

Truth tại dt1/240;adjacent1/120→1/240 theo nguyêncardA03:6D19contrasts,
e_num vàmassgates,không chọn dtthuậnlợi. Reference intervalCref=L11cùngrow.
Đối với PC4 thêm điều kiện numerical **halfwidth của mỗi true ratio≤m/10=.00025**
(0,025điểm%Cref),đểprecisionnhỏ hơnmargin. K5/C1giữgates gốcA03,khôngđổiđiểm.

Unavailable/HOLD/unconverged/ref0:giữlistID+lýdo. PC4primarycho tốiđa2/8,
ít nhất6ô;secondary2ô cầnđủcả2. Loại cảô khỏiMAE củaPC4,không loại riêngcontrast.
Nếu quábudget→INCONCLUSIVE; nếu đủ thì chấm tậpeligible đã khai,báon/Nvàkhông
suy chocácôthiếu. RecomputeD trêneligible;nếu<m→INCONCLUSIVE. K5/C1khôngloạiô;
Kleeneunknowngiữmẫu số. Không normalize như chưa hềcóôHOLD.

Với từngscalartruth[yL,yU], d_i(y)=|p0−y|−|p1−y| làđơnđiệu;
lo/hi từhaiendpoint,meanvới trọngsốđều quaôvà3contrast. Đây là enclosure paired,
không lấyriêngMAE0 interval trừMAE1 đểmấtcorrelation. MAEriêng báo mincảkink
ởprediction nếu nằmtronginterval. Preds làdeterministic frozenpoints,khôngCI.

| Verdict | Điều kiện sau Dgate/eligibility |
|---|---|
| SUPPORT | lower(d)≥m |
| WEAKEN | lower(d)>0 vàupper(d)<m |
| FALSIFY | upper(d)≤0 |
| INCONCLUSIVE | khoảng chứa hơn1vùng trên,hoặcquality/missing-budgetkhôngđạt |

Exactd0→FALSIFY;exactdm→SUPPORT. D≥m cầncho discrimination,khôngproofpower
hoặcguaranteemọioutcomeplant. Primary verdictchỉtừ8nội suy(eligible>=6);
weak/extrabáoriêng.Khácverdictgiữscope,khôngpool/chọnnhómthắng.
Ba nhánhPC4/K5/C1khônggộp“tỉ lệthànhcông”. Không cơ chếqueue/human review tựsuy.

## 8. Thứ tự và artifacts

1. DL-057/author_choicescommit riêng trướcprereg (đãcó).
2. Prereg,config,source/tests,source.lockcommit trướcfit.
3. Fit38/20LOSO,logs,theta.jsoncommit riêng.
4. Sauverifytheta,featuresR chỉbậc0–2;ghi exposure. KhôngD,cost,gap,CrefR.
5. predictions_heldout,features_heldout,discriminationcommit riêng.
6. freeze.lock vàcanonicalnotes/lessons/A05_F_preregistration.mdcommit sau
   checkpoint;DLghi commit+SHA256 haifile predictions/discrimination.
7. **Dừng L3.6.** Không chạyA05-T. L3.7cần dòngquyếtđịnhkhôngđảongược trước
   run;humanreaderL8/P0-V10khuyếnnghị,khôngtựtạoattestation hoặcđóngPhase4.

`score_test.py`verify SHA/source/theta/freeze trước mởinputtruth. FrozenA00engine
guardgiữđểbảo tồnA01/A04receipts;scorerA05mớikiểmnghiêmfreezehoànchỉnh.
Mọi model/config/pred code giữnguyên saupredictioncheckpoint;khôngamend/force.

## 9. Exposure và giới hạn claim

Đã thấy38A04vàcalibration,forecastsAI-assisted,tọađộ/publicλA,p_swheld-out cũ.
DL-057naycho phépλAcùngđịnhnghĩa cho cảhai;khôngdùngp_swthực. Testfeatures
bậc2khôngđồngnghĩachưa“chạm”metadata:ghi đầyđủgiờvàhash. Khôngbậc3/outcomes.
Kếtquảfinite-window[t0,t0+h],khônglong-runloss. Gaussiansai support/pointmass,
rho0/vật lýproxy/cỡ20lát/anchoring làlimitationschung,khôngsuycausalnovelty.
