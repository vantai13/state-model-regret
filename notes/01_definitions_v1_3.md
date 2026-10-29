# Research contract v1.3 — LOCKED với các mục DEFERRED

Người phụ trách/người soạn: **Doan Van Tai** · 29/10/2026 · **DL-071**.
Tag bất biến: `contract-v1.3`. Machine specification:
[contract_spec.json](../experiments/R3R_05_contract/contract_spec.json).

> **Provenance.** Soạn/triển khai theo ủy quyền; tác giả đã chọn P1, thước/ngưỡng,
> cam kết D22 và phương án tag A qua [trả lời nguyên văn](../results/lessons/l3r_5/author_choices.json).
> Chưa xác nhận tác giả tự viết lại hoặc read-back. Understanding/P0-V10/L8/T05 OPEN.
> Tag khóa nội dung; không chứng nhận numerics/realism và không mở Phase 4.

Contract này dùng cho thiết kế population tiếp theo. [v1.2](01_definitions_v1_2.md)
giữ nguyên thẩm quyền với kết quả A04/A05-T cũ. [Draft DL-061](01_definitions_v1_3_draft.md)
giữ nguyên snapshot lịch sử. Đổi nội dung đã khóa hoặc điền phần DEFERRED phải
tạo **v1.3.1 + DL**, không di chuyển/amend tagv1.3. Chỉnh câu chữ thuần túy cũng
phải giữ bản tag làm nguồn đối chiếu.

## 1. Main RQ, regime và mô hình được giữ

*For load-changing routing actions, how do improvements in current-state
information and action-response model fidelity differ and interact in their
effect on expected decision regret?*

Đọc “expected” theo population P1 dưới đây, bên trong một regime; không lấy
trung bình qua tần suất regime ngoài đời. MainRQ giữ nguyên; candidate gap G1
chỉ về điều kiện/độ lớn trong plant đã khai, chưa là novelty hoặc network evidence.

**Regime c:** tuple hữu tỉ `(lambdaA,lambdaB,u,kappa,h,c_sw)`; μ=10packet/s,
a=6packet/s,τ=1s là các hằng số của namespace này. Primary c_sw=0. c_sw>0 là
scenario khác có định danh khác, chưa được nhận robustness claim từ pilot.
Một snapshot/episode không phải một regime. ID/role/K/ref không thuộc identity.
Thay μ/a/τ/law/cost/information contract cần namespace/version mới, không tái
sử dụng tuple sáu thành phần như thể các giả định vẫn giống nhau.

Các tọa độ thiết kế dẫn xuất:
ρA=(λA+u)/μ,ρB=λB/μ,ρA_post=λA/μ,ρB_post=(λB+u)/μ,
φ=u/(μ−λB),κ=T_mode/τ,h/τ. Không dùng η trần; pilot provenance có
`eta_pilot=u/2`, không đồng nghĩa φ khiλB≠8. λA là tọa độ tự do, không neo
theo p_sw/J/gap/outcome. Giữ a/μ=.6 và chỉ hai mức background.

**Validity:** λA,λB≥a;λA+u<μ;λB<μ;κ,h>0;c_sw≥0;u>0, ngoại lệ u=0 chỉ control.
Đây là điều kiện stationary **trước** quyết định. B sau Switch có thể overload
trong finiteh mà cost vẫn hữu hạn; không đòiλB+u<μ như luật vật lý. Cận.95 hay
dảiκ/h là **frame choices** ởL3R.6–7, không lén đưa vào validator validity.
[JSON schema](design/regime_schema_v1_3.json) kiểm cấu trúc; cross-field semantics
do [schema.py](../experiments/R3R_05_contract/schema.py) kiểm. Không nhận float
nhị phân làm exact key; nhận integer hoặc chuỗi hữu tỉ/thập phân chính xác.

**Plant/objective kế thừa D3–D7,D11,D13–D17 v1.2.** Hai path rời, nền độc lập,
ngoại sinh, rateλ±a, buffer vô hạn; action Stay để u trên A, Switch chuyển đúng u
sang B tức thời và giữ h. Vớiδ=τ/(120ref), keepR2=(1+exp(−2δ/T_mode))/2.
Mode đầu slot cấp arrivals; q_next=max(0,q+(r+managed−μ)δ); cost ở cuối slot
δΣ(k=1..H)(qA,k+qB,k), bỏ k=0 và phần sau h. c_sw nếu có cộng đúng một lần vào Switch.
Jδ(a;x)=E_w[Cδ(a,w)|x], không realized-future hindsight. Oracle biếtx/law,
không biếtw; strict gap<0 mớiSwitch, exact certified tie chọn Stay.

**Làm rõ dt:** δ thay cả transition kernel, stationary law và endpoint cost.
Vì thế estimand được viết chính xác là `L̄_sm(c;δ)` của họ slottedR2; δ* còn
DEFERRED. K là approximation quadrature của estimand ởδ, không định nghĩa
population. Chưa adopt continuous-limit objective hoặc Richardson extrapolation.
Schema identity không gồmref/K: chúng là độ phân giải khi tính cùng operating
regime trong họ đã khóa. Khi đóng numerics phải chọn cùng global δ* trước CF.
Không tự ceil h để đổi câu hỏi: tại mọi mức kiểm, H=h/δ phải nguyên; frame phải
chọnh tương thích lattice trước sampling hoặc ghi thay đổi version/DL.

## 2. Population P1 và quyền thông tin

Trước decision, Stay đã tồn tại đủ lâu để có stationary law dướiu trênA và0
trênB. Epoch quyết định độc lập state, đánh giá one-shot; không suy feedback
của các lần switch liên tiếp. Y=(yA,yB) là backlog tại t0−τ, không mode/nhiễu,
có timestamp. X=(qA,qB,mA,mB) ở đầu slot0 tại t0. Joint law:

`P_c,δ(Y=y,X=x)=Σ_mold π_A,δ^u(yA,moldA) π_B,δ^0(yB,moldB)
                  · K_Stay,δ^τ((y,mold),x)`.

Từ cùng một joint suy p(y),D(x|y),π(x); Σyp(y)D(x|y)=π(x). Không uniform
q50/q90, không chọn vài snapshot thuận lợi rồi gọi là full population.
S0 dùng **true posterior D**, giữ chung giữaM0/M1. S1 nhậnX gồm hai hidden modes.
M0/M1 cùngθ và quyền thông tin: M0 tính cost của mean rollout **từng state**
rồi lấy E_D; M1 true expected future cost. Không rollout từ mean-state;
model repair không sửa posterior, parameter hoặc cấu trúc.

| Bên | Được biết tại decision | Không được nhận |
|---|---|---|
| S0M0/S0M1 | c,Y,timestamp và trueD(.|Y); khác cost model | X hoặc realizedw |
| S1M0/S1M1 | c,X; mode là quyền oracle | realizedw |
| cb0 diagnostic | c,Y,hai current backlogsQ; trueD(X|Y,Q),fixed M0 | current modes hoặcw |
| Oracle/evaluator | c,X,trueJδ; evaluator tích phân theo cùngP | Oracle không dùngw; không truyềnX cho S0 |

P2a lọc theoY chỉ giữ D trên tậpYđược chọn nhưng đổi marginal X; P2b báo động
condition cả history/joint; P3transient có law khác. **Không chọn P2/P3 làm
primary/diagnostic trongv1.3.** Đổi law cần version/DL/audit. P1 có dilution do
episode ítstakes và không đại diện alarm-driven controllers.

v1.2 recovery là condition toànjoint tạiY=y*: p trở thànhDirac và marginal X
trở thànhD(.|y*), **không** giữ unconditionalπ cho S1. Tính bất biến S1 theo
observation channel chỉ đúng khiπ,Jδ vàS1policy cố định. Đổi κ vớiτ=1 thường
đổi T_mode/π/J; không suy S1invariant theoκ. Population không bảo đảm smooth.

## 3. Estimands, contrast và D22

ĐặtA(z)=1[z<0],Δδ=Jδ(Switch)−Jδ(Stay),Δhatδ là M0 state gap.

```text
a00(y)=A(E_D[Δhatδ|y])    a01(y)=A(E_D[Δδ|y])
a10(x)=A(Δhatδ(x))        a11(x)=A(Δδ(x))
L̄_sm(c;δ)=E_P[Jδ(a_sm(Y,X);X)]
R̄_sm=L̄_sm−L̄_11

ḠS=L̄00−L̄10       ḠM=L̄00−L̄01        ḠSM=L̄00−L̄11
Γ̄=L̄10+L̄01−L̄00−L̄11
ḠS|M1=L̄01−L̄11    ḠM|S1=L̄10−L̄11
```

J đã lấy kỳ vọng future; không cấp thêm realizedw. Tổng/tích phân gồm atom tại 0
và support thích hợp. Định nghĩa không phải estimates từK40 hoặc quantile representatives.

**D22 — định nghĩa/cam kết LOCKED; engine implementation và audit DEFERRED
trước Phase 4.** `a_cb(Y,Q)=A(E[Δhatδ(X)|Y,Q])` vớiQ là cả hai current backlogs,
giữ Y để suy modes, không đổi M0. L̄cb0=E[Jδ(a_cb(Y,Q);X)],
F̄=L̄00−L̄cb0,V̄=L̄cb0−L̄10,ḠS=F̄+V̄. Không có đường tính thì đểnull,
không gán cb0=0. Golden toy/reference không chứng nhận productionD22 đã có.
Claim SH trước D22 chỉ nói state(backlog+mode oracle); F̄<0 chỉ hỗ trợ câu hẹp
về ideal current backlog dưới fixed M0, vẫn chưa là feasible telemetry có hại.

Danh sách **S01–S18** giữ nguyên công thức/điều kiện ở
[T07§5](theory/T07_population_estimand.md#5-sanity-list-và-chứng-minh).
IdentityΓ=GS|M1−GS=GM|S1−GM; GS<0⇒Γ≥|GS|>0 không là finding có thểconfirm.
Γ lớn⇒harm không là identity. |GS|≤σ̄ và−σ̄≤Γ≤σ̄; D22 F/V có thể triệt tiêu.
S01/S02/S03 cần joint coherence; GM≥0 cần true/shared D vàM1 optimal cùng information.

## 4. Thước đo, ngưỡng và lớp kết quả

**Primary normalization LOCKED:** ratio-of-expectations `Ḡ/C̄ref`,
C̄ref=L̄11 ở **cùng δ và K/quadrature** với bốn cost/contrasts khi estimate.
Không dùngE[G(Y)/Cref(Y)],L00 làm thước hoặc chọn thước cho nhiềuPASS hơn.
Stakesσ̄=Eπ|Δδ| chỉ mô tả; không verdict riêng, không “primary hoặc stakes”.

εR=**.01C̄ref**, sensitivity.005/.02 **chỉ mô tả**, không lật verdict.
εE=**.005C̄ref**; tolerance refinement=.0025C̄ref=**.25pp** củaC̄ref.
Lựa chọn SAU pilot, giữ con sốv1.2 đã có trước populationpilot; không kế thừa
nghĩa một-snapshot, không chọn từ so sánh kết quả giữa các phương án.
Đây là quy ước, chưa SESOI vận hành/SLA; RQ3 thuộcPhase7.

Mẫu số0: relativeundefined/null, giữabsoluteoutputs và lý do; báo sốexcluded
riêng, không epsilon-floor, không0%cho0/0. Stakes0⇒mọi contrast bằng 0, ratio theo σ undefined.
Các exclusion phải được khai trước; không âm thầm bỏ regime sau outcome.

Tối đa **2 primary cards + 1 secondary**, phân suất ởL3R.6, không tự ghi Hyp-MV/SH
đãfrozen từcontract. Primary có family/multiplicity rule trước CF; sốcard ít
không tự kiểm soát false-positive rate. Secondary có prereg verdict riêng, không
cứu primary. Γ mặc địnhdiagnostic; chỉ thànhprimary nếu card L3R.6 cấp một suất.
D22 F/V,GM|S1,GS|M1,GSM,P(flip),tie mass,%stakes,R00/C̄ref là diagnostic,
không tạo verdict mới sau primary FAIL. Pattern mới phải gọi discovery mới.
Association của Hyp-MI không phải cơ chế/RQ2; H0/H1 và ngân sách fit DEFERRED → Phase 5.

## 5. Numerical rules LOCKED; mức/thuật toán DEFERRED

AuditL3R.3 **HOLD**, không tự đóng từ contract này. K*,ref*/δ*, routeS1(quaY
haytrựcπ), quadrature/support-tail policy và moment/error accounting còn
**DEFERRED→numerics freeze v1.3.1 trước khiL3R.7 rút CF**. Các candidateK320/ref2
chỉ là discovery evidence, chưa là global levels. Tolerance không phải errorcertificate.

| Rule | Nội dung khóa |
|---|---|
| R1 | Với mọi6 contrast, kiểm cả \|Gf−Gc\|/Cref_f và \|Gf/Cref_f−Gc/Cref_c\|≤.0025; thêm \|Cref_f−Cref_c\|/Cref_f≤.0025. Không signflip khi cả hai normalized endpoints ngoài±εE. Ghi arithmetic uncertainty riêng. |
| R2 | Mọi regime có main(K,ref), coarse K(K/2,ref),coarse dt(K,ref/2). Kiểm riêng hai axis, không chỉ đồng thời K/ref để lỗi triệt tiêu. K/ref main chẵn≥2; h vật lý giữ đúng tại mọi mức. |
| R3 | Tối đa **2 bước leo thang dùng chung**: từ(K,ref)→(2K,ref)→(2K,2ref). Mỗi main mới vẫn kiểm hai coarse-axis neighbors. Không reset budget cho rule khác. Lưu mọi lần đo và nguyên nhân, không chọn mức thuận lợi. |
| R4 | Hếtbudget vẫn không đạt ⇒UNRESOLVED theo criterion; không đếm PASS/FALSIFY. Báo full denominator, sốundefined/excluded và hai extremes unresolved-all-meet/all-fail. Verdict giống nhau mới robust với unresolved; nếu khác phải hạ ít nhất một bậc theo ordering prereg L3R.6–7, không kết luận SUPPORT/REFUTE dứt khoát. Chưa có mapping thì INCONCLUSIVE. |
| R5 | u_max=.10 ở mỗi stratum chấm. UNRESOLVED/Neligible>.10⇒INCONCLUSIVE; đúng.10 vẫn dùng R4, không bỏ unresolved khỏiN. N=0⇒INCONCLUSIVE. |
| R6 | Khoảng cách normalized estimate tới boundary của criterion≤max measured refinement difference thì dùng bước kế tiếp hoặcUNRESOLVED. Boundary effect+εR,harm−εR,equivalence±εE; equality xử lý bảo thủ trừ khi có exact certificate thực. Arithmetic/sign/tie chưacertified cũng không tựcoiStay/MEETS. |
| R7 | Refinement difference là diagnostic estimate, không certified errorinterval, không cận cumulative error. Hoãn mức vẫn có degrees of freedom: giảm bằng protocol hữu hạn/cùngrules/exposure/freeze, không phủ nhận rủi ro. |
| R8 | Globallevel/method chọn trên discovery/calibration đã khai, phủ corners của proposedCFframe, trước CF sampling. Ít nhất8 IDs audit cũ trong spec; thêm corners nếu frame mới cần, khai role/calibration trước outcomes, không dùng CF. Cần audit/coverage closure, runtime budget và receipts v1.3.1. |

R1/R6 chưa bảo đảm correctness ở mọiregime hoặc gầnthreshold; không gọi
measured-delta là CI. Atom,stationary TV,posterior,moment/tail,loss impact,
quadrature và floatingcertificates là các lớp khác nhau; không dùng TVbound
cho unbounded mean Q hoặc bỏ probability rồirenormalize như exact population.
Giữ probability guards của D12 v1.2: stationary-law TV error≤1e−10 và
posterior error≤1e−8 cần chứng nhận riêng; chúng không chứng nhận cost moment.
Support/tail/quadrature details chưa được phép ngầm carry từ pilot1−1e−4/K40.

**Stop controls:** zero-action và exact-conservation certified cases phải bằng 0 chính xác,
không epsilon/clamp để biến FAIL thành 0. Floating residual không tự động là physics bug nhưng
phải dừng, kiểm exact arithmetic/certificate và ghi deviation trước khi tiếp tục.
Anchor replay cùnglevel/code phải khớp saved pilot tolerance đã khai; so khác
level phải dùng declared numericalcomparison, không đòi rawK* giống K40.
Ít nhất X2065/X1008/X1009 dùng làm anchor; prereg đủ field/tolerance trước calibration.
Không early stop do “đã đủ”, không bỏ regime sau outcome. Lỗi control/anchor⇒dừngrun,
sửa/version/deviation rồi chạy lại **toàn bộ registered batch** cùnganalysis;
giữ attempt cũ, không ghi “một run” chỉ tính retry thuận lợi. Policy retry cụ thể khóa ở L3R.7.

## 6. Assumptions, realism và exposure

| Giả định | Nội dung và nếu vỡ | Nơi kiểm tiếp |
|---|---|---|
| AS-path/fluid/background | Hai path rời,một managed class,nền ngoại sinh hai mode,không TCP/noise packet/shared bottleneck. Nếu vỡ không mang nguyên J/counterfactuals sang mạng thật | Phase6 |
| AS-buffer/instant/observe | Infinite buffer, instant action, ideal backlog; không có empirical B_t/d_act/AoI phù hợp. Finite buffer/drop,actuation,estimator thực có thể đổi effect theo hướng chưa biết | Phase6–7 |
| AS10 | Pre-Stay stationary; transient/diurnal drift đổi episodeweights | P3/audit mới |
| AS-epoch/oneshot | Epoch độc lập state, one-shot; không alarm selection hoặc feedback policy lặp | Jointlaw/control mới |
| AS11 | S0 true posterior dùng chung; lọc bằngM0 có thểmất GM≥0 | Phase5 robustness |
| AS12 | S1 biết mode: oracle information benchmark, không feasible telemetry | D22;Phase7 |
| AS13 | Primary c_sw=0; chưa có robustness với switching cost | Phase5 paired intervention |
| AS14/AS-a | τ=1 chỉ là mapping khi co toàn bộ times/q0/c_sw đúng; a/μ=.6 fixed. Không suy packet DES hoặc biên độ khác | Phase6 |

Scope bắt buộc đi cùng mọi claim:

> Plant fluid hai đường rời, nền Markov hai mức a/μ=.6, buffer vô hạn, action
> tức thời, ideal backlog có tuổi τ; population P1 stationary pre-Stay ở epoch độc
> lập state; primary c_sw=0. S1 gồm hidden mode oracle, không repair triển khai được.
> Realism vùng discovery **chưa sàng lọc được** theo envelope v1, HOLD_UNSOURCED.
> Chưa biết có gặp ở mạng thật không; không đồng nghĩa đã biết OUT.

Carry [envelopev1/rules](realism/envelope_v1.json) tại commit6bef959, execution830a187;
buffer UNSOURCED, actuation UNSOURCED, mode oracle TRUE. Tail của infinite queue không phải drop;
stationary post-load không phải transient; mode correlation không phải backlog correlation; không suy dấu GS.
Nguồn/ranges mới tạo envelope v2 sau quan sát, không sửa ngầm nhãn v1.

38 ô A04, 10 R đã mở (R01–R08,R11/R12), 216 pilot ID (210 scientific keys) và audit/
generic checks là discovery/verification, không là clean confirmation cho hypothesis mới.
**R09/R10 vẫn niêm phong, không tự phân vào CF.** CF mới chỉ sinh tham số ở L3R.7 sau
numerics freeze; tuyệt đối không J/gap/contrast/outcome trước Gate3R/Phase4.
Collision inventory phải gồm mọi discovery/canonical plant coordinates trước CF; exact key
có c_sw, không K/ref. Báo nearest L∞ trên (λA/μ,λB/μ,u/μ,κ,h/τ,c_sw/(μτ²));
distance nhỏ không làm mẫu độc lập, exact freshness không chứng nhận realism.

## 7. Các mục hoãn và gate

[Inventory 21 dòng](../experiments/R3R_05_contract/contract_spec.json) triển khai
19 mục lesson với 6b/11b riêng. Phần chưa đóng phải có nơi và deadline:

| Mục | Đã khóa | DEFERRED/closure |
|---|---|---|
| 6b D22 | Định nghĩa, cam kết thực hiện, giới hạn claim | Engine path và audit trước Phase 4 |
| 11b numerics | R1–R8, tolerance, u_max, finite escalation | K*/δ*, quadrature/tail, route S1, audit coverage và runtime → v1.3.1 trước L3R.7 sampling |
| 19 RQ2 | Không dùng Hyp-MI làm mechanism evidence | H0/H1, ngân sách fit, held-out fairness → prereg Phase 5 |

Card allocation/regions/multiplicity/aggregate verdicts thuộc L3R.6; CF frame/strata,
sample-size, power, seeds, scorer/deviations thuộc L3R.7–8. Chúng là downstream work,
chưa được tạo hay giả vờ frozen ở contract. Claim boundary hiện chỉ là khung.

Tag v1.3 cho phép **viết/khóa card L3R.6 trên bản cố định**, không cho sinh CF khi
11b chưa đóng. Phase 4 HOLD tới numerical audit/closure, D22 audit, P0-V10/người đọc thật
và mọi Gate3R đạt; L8/T05/Understanding giữ OPEN. V9 waiver DL-054 không miễn các gate khác.
G1 không đổi, chưa có hypothesis evidence/contribution/novelty. RQ2 → Phase 5, RQ3 → Phase 7;
“interact” chỉ mô tả nếu L3R.6 không cấp primary slot cho Γ.

Diff và chuỗi nghiên cứu: [diff](design/v1_3_contract_diff.md),
[Problem→Contribution](design/v1_3_research_chain.md),
[numerics freeze plan](design/v1_3_numerics_freeze_plan.md).
