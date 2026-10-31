# L4.7 (v2) — P-clip: chứng minh, kiểm native và predictor discovery

Người phụ trách: **Doan Van Tai** · 31/10/2026. AI thực hiện theo ủy quyền;
không tác giả tự viết/tự chứng minh, human review hoặc Understanding PASS.

**Đã hoàn tất Part A, Part B và đủ50điểm Part C trong ngân sách.** P-clip
đúng dưới các giả định đã ghi. Predictor chưa được kiểm held-out; tỷ số
S_clip/sigma không cung cấp variation trong primary. Giữ G1, không khóaH-clip
hoặc tự tạo predictor khác để cứu. Không sửa contract hoặc production engine.

## Công việc và những chỉnh lý cần thiết

- [T08](../../../notes/theory/T08_clipping_anchor.md): phân tách linear/idle,
  chứng minh P-clip và Jensen có điều kiện, gap error hai dấu, cậnGM|S1.
  Tự tính bảng continuous toy riêng với slotted measurements; không trộn cost.
- [Protocol](../../../notes/lessons/L4.7_v2_protocol.json), commit29d5422 trước
  diagnostic, có predictionsAI/scope/budget. Source1aca4a4; bổ sung chứng minh
  identity S_clip=sigma sau diagnostic ở36d32c0, không giả đã dự đoán trước.
- Slot0 giữ initialmode. Strictreflection thresholdOFF=hD, ON=max(0,hD−12dt)
  trong miềncontract. q<hD chỉ là cover dùng chung hai mode, không phảiiff.
  Chạm0 với regulator0 không phải strictreflection.
- `d/dh` là **idle-cost differences** của từng path; network linear terms
  triệt tiêu khi chuyển cùngu. `saturation_cost` áp backlog thấp/modeOFF làm
  cảhai mean paths rỗng, không phải queue luôn bận như hướng dẫn mô tả.
- Engine tính weighted idlecostW=dt sum_n R_n(packet·s), không chỉR_H(packet).
  S_clip có đơn vịpacket·s; phải chiaCref/nhân100 mới thành%Cref.

## Part A và reference hữu hạn

P-clip dựa trên mọi possible stochastic path không reflection, không chỉ mean
path. Conditional expectation tuyến tính và objective tuyến tính choM0=M1
ngoàiClip. Jensen choM0<=M1 mỗiaction; hiệu hai action errors có cảhai dấu.
Không suy “clipping có thể xảy ra” là điều kiện đủ cho model error/interaction.

Ví dụ minh họa gốc được tái lập bằng **512paths**,9transitions,H10,dt.05s,
kappa.3s,lambda7,a6,u2,mu10. Đây là finite enumeration bằng floating point,
không Monte Carlo và không một continuous-limit experiment.

| q0(packet) | mode | M1(packet·s) | M0(packet·s) | M1−M0(packet·s) |
|---:|---|---:|---:|---:|
|5|OFF|1.962326300|1.962326300|+3.77e−15|
|5|ON|2.762673700|2.762673700|−1.11e−14|
|1|OFF|.233943110|.061835386|.172107724|
|1|ON|.796481596|.762673700|.033807896|

Tổng xác suất=.9999999999999999 mỗi trường hợp. Reference rationalBellman và
forwardmean được kiểm riêng trong tests để không chỉ xác nhận code minh họa.

## Part B — kiểm profile native

Ba discovery keys đã có: P43_0018(A), P43_0083(AB), P43_0021(C); dùng cảhai
path với(u,0)/(0,u), initialmodesOFF/ON, bốn backlog targets(1.5hDmax,2hDmax,
.25hDmax,0). ref4,dt1/480s; h=1s ởP43_0018 vàh=4s ởhai case còn lại.
Ghi cảq_requested/q_actual/unit/index, dùngceil lên stationary lattice rồi
phân loại lại trênq_actual. Không silently truncate backlog.

| Kiểm tra | Kết quả thực tế |
|---|---|
| State/profile checks |48:24ngoàiClip,24trongClip |
| NgoàiClip |24/24PASS; max abs(d−dh)=**0packet·s** |
| Jensen per-action |96/96PASS; mọiM1−M0center>=0, max6.698083879packet·s |
| TrongClip | max abs(d−dh)=**3.757970725packet·s** |
| Gap error sign | cóâm,zero,dương; không suy dấu gap từ chiều bias per-action |

Đọc đúng saved native law/profilekeys, refusal nếu thiếu cache. Không tạo mới
stationary roots/Bellman physical profiles hoặc gọi whole-regime evaluate.
Mean-idle per-action được dựng lại để kiểm Jensen, trueSwitchidle tái dựng từ
Wstay+d cùng error allowances. State/path probes không phải full population
numerical audit và không đóng R1 hoặc D22.

## Part C — 50điểm discovery

Chọn **18A/16AB/16C** theo oldpilotclass, lấy các vị trí cách đều trên sorted
exactphysicalkeys. Bao gồm9SUB đã park,7SV-AB và cácSV/A3cases còn lại;
không lấy thêm66SUBkeys. Labels và outcomes cũ đã thấy; đây là adaptive
discovery support, không lấy tỉ lệ của50điểm làm prevalence ngoài đời.

Budget trước run:120CPU-s/180wall-s; thực tế **34.530743CPU-s/34.969337wall-s**
choPartC, đủ50/50, không replacement. Toàn diagnostic trước summary/plot là
35.341228CPU-s/35.540843wall-s. Thời gian này không gồm fulltests/renderplot.

P_clip tính từ certified stationaryCDF tại mode-aware strict lattice cutoffs,
gộp hai path độc lập. Nó là **xác suất state cho phép ít nhất một future path
reflection**, không phải xác suất một realizedfuture thực sự sẽ reflection.
S_clip vàsigma dùng cùngK/ref/native quadrature như output gốc; đây không
phải certified total numerical intervals.

| Đại lượng | Kết quả trên50điểm |
|---|---:|
| CậnGM\|S1<=S_clip trên cùng weighted quadrature |50/50không vi phạm |
| Maxreplaydifference với savedGM\|S1 |7.44760109009049e−18pp |
| P_clip range |**.996476305602→1** (1là biểu diễn numerical) |
| P_clip>=1−1e−9 |35/50 |
| S_clip/sigma |**1 tại50/50điểm** |
| SpearmanP_clip vớiGM\|S1/Cref |.775787657 |
| SpearmanP_clip vớiabsGamma/Cref |.762484287 |
| SpearmanS_clip/sigma |null/DEGENERATE_RANGE theo luật đã khai |

P_clip ở A cómin/median/max=.996476306/.999998957/1; AB có cả16giá trị
represented1; C cómin.9999999999999966,median/max1. Không suy probability
đúng bằng1:32/50CDFintervals chạm1 và tails rất nhỏ có thể bị làm tròn.
**496/1225cặp** không có rank tách biệt theo reportedCDFerrors. Correlations
trên là rawdescriptive ranks, chịu ties/class-selection/confounding; không
p-values hoặc evidence dự báo held-out, không chứng nhận toàn thứ tự ranks.

### Vì sao S_clip/sigma không phải predictor mới trong primary?

NgoàiClip, tổng backlog hai path chỉ có linear cumulative input. Cùng managed
loadu chỉ đổi vị trí nên tổng endpointcost không đổi theoaction; c_sw=0 cho
Delta=0. Do đó **S_clip=E|Delta|=sigma pointwise theo support**, không chỉ
“hay gần bằng” trên50điểm. Chứng minh được bổ sung sau diagnostic ởT08§4.1
và một exact rational networktest; không đổi protocol/metric sau outcome.

CậnGM|S1<=S_clip vẫn đúng nhưng trongprimary chính là cậnstakes đã có,
không thêm độ chặt. Quan sátGM|S1/S_clip cómin/median/max
.00491116/.08816756/.46373854 trênsubset này. Không đổi cost/plant để làm
predictor biến thiên. S_clip dùngtrueDelta nên cũng không phải một feature
parameter-only độc lập outcomes.

## Verification và limitations

**34 targeted tests PASS(.74s);930fulltests PASS(83.72s).** Có exhaustive
mode-path support tests, strictboundary/slot0, rationalcost/Jensen, conditional
vsunconditionalmean, clipping nhưng không cóerror, nativekernel và identity
networkstakes. NămA1preregs/A2source và screeningrules cũ vẫn khớp frozen
hashes/history. Đối chiếu độc lập sourceSHA/metadata/lattice/costmetrics/ranks
PASS; full0.25pp numerical criteria không được đổi để nhậnPASS.

Giữ8rawarithmeticFalsecases của dữ liệu gốc và mọivalidityflags trongJSONL;
50/50boundcheck không xóa chúng hoặc chứng nhận toànnumerics đã solved.
Không có randomness/seed/MC trongresearchrun, không tạo confidenceinterval
thống kê;CDFerrors lànumericalbounds riêng, cònS_clipquadraturechưa certified
totalinterval. KhôngmớiCF/R09/R10/outcomesheld-out, khôngSUBresume, khôngA4.
D22nativeF/V vẫnDEFERRED. G1/Understanding/T07authoraddendum/L8 giữ.

**Được xác nhận:** P-clip/Jensen có điều kiện theo đúng slottedcontract, engine
khớp ở states đã kiểm, và predictorstakesratio bịconstant theo cấu trúcprimary.
**Chưa xác nhận:** predictionmagnitudeGamma, causalmechanism ngoàiplant,
packet/finitebuffer/realism, generalization/novelty hoặc practicalfreshnessD22.
GiữP-clip làm mệnh đề giải thích/test, chưa tự khóaH-clip ởL4.9. L4.8realism
là lesson tiếp theo; không cần mở rộngnumerics ở đây.

## Commands và output

```bash
.venv/bin/python -m pytest -q tests/test_p4_07_clipping.py
.venv/bin/python -m experiments.P4_07_clipping.check_clipping --out results/lessons/l4_7_v2/analysis
.venv/bin/python -m pytest -q
```

Chạy lại CLI phải dùng outputdir mới. Independent checks chạyPythonstdin:
SHA/metrics từrawrows, exactlattice, Spearman từsavedrows và các frozenverifiers;
kết quả ghi verification.json/log. Không thêm source/hash-lock framework.

- [ProofT08](../../../notes/theory/T08_clipping_anchor.md),
  [code](../../../experiments/P4_07_clipping/check_clipping.py),
  [tests](../../../tests/test_p4_07_clipping.py).
- [Protocol/config/predictions](../../../notes/lessons/L4.7_v2_protocol.json),
  [lesson gốc](lesson_original.txt).
- [Referencecosts](analysis/enumeration.json), [48statechecks](analysis/state_checks.json),
  [50diagnosticsCSV](analysis/diagnostics.csv)/[JSONL](analysis/diagnostics.jsonl),
  [summaryJSON](analysis/summary.json).
- [PlotPNG](analysis/predictors.png)/[PDF](analysis/predictors.pdf).
- [Runlog](run.log), [finaltestslog](tests_final.log),
  [verificationJSON](verification.json)/[log](verification.log).

Không tạo datasetconfirmation, nativeD22output, MCoutput hoặc configsimulation
mới; dùng frozenraw/cache và protocol subset cósourcehash. Attribution cũ giữ.
