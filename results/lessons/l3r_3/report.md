# L3R.3 — Audit engine population

Người phụ trách: **Doan Van Tai** · thực hiện 28–29/10/2026 · DL-066–068.
**Kết luận audit: HOLD.** Bộ kiểm kỹ thuật đã thực hiện, evidence **PASS có giới hạn**;
chưa đủ để tự khóa numerics v1.3: read-back tác giả còn OPEN, một số mức số khai gốc
UNRESOLVED, cost allowance đầy đủ chưa interval-certified. Không nâng G1/Phase4.

## Đã làm và quyết định engine

Đọc đủ4phần lesson; trả lời(a)–(n) kèm file:dòng tại [code map](../../../notes/verification/l3r_3/code_map.md).
Commit prereg **6499d7f** trước engine outcomes mới; T07 gốc315d203 đã có trước kết luận.
S1/S2/S4/S6 MC được làm rõ từ tài liệu R2/slot cũ trước pilot, không thay plant.
MC do phiên độc lập chỉ đọc đặc tả/T07/contract; code/provenance giữ riêng, không human review.

Chọn **KEEP lõi và snapshot pilot, thêm lớp test/API trong experiments/R3R_02_audit**.
Không gọi đây là REBUILD toàn bộ hoặc đã có production enginev1.3. Snapshot và19tests gốc
giữ nguyên byte từtag a7435e9. API thêm giúp hỏi policy tại y/x tùy ý và test explicit tables.
Trong8regimes audit chưa xác nhận bug làm thay đổi số pilot; hai lỗi phát hiện nằm ở
adapter toy và arithmetic của MC checker, đã có regression/proof trước sửa.
Vì vậy **chưa kích hoạt chạy lại216ID/pilotv2**. Nếu sau này tìm ra bug thật ở engine,
vẫn phải giữv1, viết regression/prediction rồi rerun toàn216ID, không chọn phần thuận lợi.

## Kết quả kiểm thực tế

| Phép kiểm | Kết quả |
|---|---|
| T1/T4/T5/T7 + MC unit trong full suite | **467/467 PASS**, 99.39s; gồm28test audit mới |
|19test toy gốc pilot, import alias không sửa byte | **19/19 PASS**,0.04s; chạy riêng ngoài full testpaths |
| Mutation | **12/12 bị bắt**:11 bởi assertions,1 bị mathematical guard Jensen từ chối; không đếm arbitrary runtime crash là KILLED |
| T2 xác suất,16side cases | **16/16 PASS**, maxTV=9.51564e-11, mỗi tolerance=removed mass+1e−12 |
| T2 cost so direct stationary, khai gốc đếnK160 | **6/8 PASS**, X1008/X1009 giữUNRESOLVED ở mức gốc |
| T3 atom so fluid,ref1 | **11/16 PASS**,5case coarse ngoài.01; không gọi đó là bug slotted law |
| T3 atom ởref2 | **16/16** trong.01 và lệch giảm; κ dependence ở finite dt không tự là lỗi |
| T6 so actual snapshot với evaluate_sidesv1.2 | **8/8 PASS**, maxrelative=3.18943e-18; chỉ kiểm phần khác code, không độc lập belief |
| MC C1,5state×2action×8regimes | **80/80 PASS** theo3SE/luật retry |
| MC C2,2side×5y×8regimes | **77/80 PASS ban đầu**;3alarm còn lại được giải thích bằng exact conservation và kiểm lạiPASS |
| MC C3 trên cùng discrete-node law | **8/8 PASS** sau retry đã khóa, max abs(z)=2.313697; conditional law vẫn có numerical solve error đã công bố |
| MC C3 full stationary |8/8khớp mean theo3SE+allowance refinement; ban đầu1SE-targetUNRESOLVED, precision extension sau đóPASS |
| Clone/venv mới | **19/19 PASS**, 57808 snapshot-pair records khớp exact numeric values |

T1 integer-count adapter đưa cùng toy rational qua actual pair_values mà không làm mất tie.
500jointlaws seed20261028 ở T07 được dùng lại, không gọi replay là500laws mới độc lập.
T4u0 và T5far-state conservation kiểm **0 chính xác**, không epsilon/clamp.
T5là kiểm theo state, không giả định cả population không bao giờ chạm0.

Mutation matrix thực chạy nằm ở[mutants.json](mutants.json). Ma trận trong lesson là
dự đoán, không phải bằng chứng mọi test phải bắt mọi mutant. Thêm analytic R2 conditional
mode test đã bắt no-age; vì thế câu “chỉ MC bắt được” không còn đúng cho bộ kiểm mới.
Đính chính nguồn lesson: report L1.5 dòng63–81 và các replay XML **có evidence** checker
chung helper bỏ sót P4 ở test any-belief; bản kiểm độc lập bắt được. Code map trỏ đúng
artifact; không nhận đã rerun các mutant lịch sử trong lượt này.
MC dùng policy hộp đen không tự chứng minh information restrictions/optimality của policy;
S0leak/M0semantics vẫn cần code map/toy, không gán coverage tưởng tượng cho MC.
D22mode-leak mutant áp vào prototype finite-toy, chưa là D22 outcome trên pilot.

## Những số pilot đã được kiểm lại

Regimes đã exposed; age1s,μ10packet/s,λ±6,R2,pre-Stay; bảng dưới **ref1,K40,dt1/120s**.
L là expected cost **packet·s**; GS/GM chiaC̄=L11, đơn vị**%C̄**. Không phải CF/held-out mới.

| ID | L00(S0/M0) | L01(S0/M1) | L10(S1/M0) | L11 oracle | GS %C̄ | GM %C̄ |
|---|---:|---:|---:|---:|---:|---:|
| X2065 | 37.983758 | 33.503211 | 38.388916 | 33.419634 | -1.212335 | 13.406930 |
| X2029 | 25.481843 | 24.030170 | 30.665190 | 24.030170 | -21.570165 | 6.041042 |
| X2041 | 14.399370 | 14.399370 | 16.445571 | 14.399370 | -14.210347 | 0.000000 |
| X1001 | 21.519752 | 21.499533 | 22.707651 | 21.499533 | -5.525232 | 0.094046 |
| X3001 | 24.344047 | 24.344047 | 24.356618 | 24.344027 | -0.051640 | 0.000000 |
| X1008 | 53.307748 | 53.305306 | 53.214771 | 53.201176 | +0.174766 | 0.004592 |
| X2012 | 7.141110 | 7.141110 | 7.106365 | 7.106362 | +0.488929 | 0.000008 |
| X1009 | 212.879871 | 212.823706 | 212.029042 | 211.896213 | +0.401531 | 0.026506 |

Ví dụX2065: sửa model giảm cost37.983758→33.503211packet·s, gain13.406930%C̄.
X2029: state-only làm cost tăng, GS=−21.570165%C̄. Đây vẫn là discovery của plant;
audit xác nhận phạm vi tính toán, không biến chúng thành hypothesis confirmation hoặc mạng thật.

## Numerics: cái gì đạt, cái gì chưa được khóa

S1cost ởκ3 co khiK tăng nhưng K40 không đủ: X1008 maxerror khoảng.942ppC,
X1009 khoảng.939ppC. K160 còn.3265/.3162ppC > .25.
K320 được khai **sau quan sát** tạiDL-067, trước run bổ sung; maxerror còn
**0.228886ppC** và
**0.217601ppC**.
Không đổi nhãn của hàng prereg gốc hoặc nóiK320đã khai từ đầu.
Đây là sai số estimator S1 qua quadrature, không bác identity estimand.

Candidate từlesson **K40,ref2(dt1/240)** đã được đo cùng checkK20/ref2 vàK40/ref1;
bảng[summary.csv](summary.csv) giữ cả maxdelta theo%C̄/theo%stakes và sign-flip.
Không tự adopt candidate thành mức toàn miền: absoluteS1/Cbar error ởκ3 yêu cầu
quadrature tốt hơn hoặc thiết kế direct-state integration được audit riêng.
Ngoài ra X2065 có coarse pairK20→K40/ref2 lệch.440885ppC, nên đã chạy **K80/ref2**
theo đúng một bậc escalation khai gốc; status/delta mới ở summary, giữ coarse pairFAIL
precision ban đầu. Không lấy 9robustness points cũ làm chứng nhận cặpK20mới.
Ref2 được hỗ trợ bởi atom nhưng chưa là certificate cho mọi contrast/regime mới.
Giữ tolerance .25ppC,sign rule ngoàiεE.5%C,thang stakes riêng; không suy tolerance
theoC đủ cho mọi hypothesis theo stakes. Primary/εR/K*/stop rule cuối thuộcL3R.5.
UNRESOLVED không tính PASS/FALSIFY; tỷ lệngưỡng10% vẫn là proposal choL3R.7.

Pilot ghi tail probability; tail cost và independent-law finite-cap bounds có trongMC
diagnostics. Chúng được tính float64, sparse residual không tự là certified invariant
error. Refinement difference là **estimate**, không phải rigorous bound. Full population
MC dùng allowance đó nên kết luận phải có giới hạn; không gọi all z≤3 cho target này.
Bin-policy integral không bằng point quadrature; strict-node comparison tránh trộn hai law.
3SE là quy tắc audit, không global family-wise confidence guarantee; công thức
1−(1−p)^m chỉ đúng khi các alarm độc lập, còn các metricCRN ở đây tương quan.

## MC sample sizes, SE và các lần có vấn đề

Dảiseed318300000–318399999 chỉverification. C1/C2/C3 trên8regimes audit dùng **ref1**;
ref2 được probe/reproduce, chưa được MC production độc lập trên toàn8regimes này.
C1/C2N65536, alarm→4N/seed mới một lần.
C3pilotN2048/target; Nproduction được khóa ởcommit4c4908f **trước final runs**,
Nban đầu32768–524288, X2029nodes retry lên2097152 theo luật có sẵn.
Mean/SD/SE và từng seed ở[mc_run01](mc_run01/); moments giữ per-episode contrasts,
mean,sd,cross_sum để kiểm lại SE. Không cần giả episode liên tiếp làIID: mỗi initial
state được rútIID từ invariant law độc lập, future streams độc lập episode vàCRN theoaction.

X2065stationary ban đầuSEmax=.103446939ppC vượt.1: [final gốc](mc_run01/X2065/final.json)
giữUNRESOLVED. Sau khi khai[precision extension](../../../experiments/R3R_02_audit/precision_extension.json),
N=1048576,seed318351301 choSEmax=**0.051907363ppC**, đạt.1.
Đây là kiểm thêm sau outcome, không sửa N hoặc status của final gốc.

Các sai sót đã giữ dấu vết:

1. InitialT1đỏ1/25: adapter đổiFraction→LD trước sign làm mất exact tie,cost lệch.15.
   Sửa bằnginteger-count homogeneity, không sửa engine hoặc tăngtol; fixture/log/XML giữ.
2. Một MC diagnostic index vượt bảng khiq đã ở miền provablybusy; sửa guard có ý nghĩa
   zero-idle, resume phần chưa xong, giữprepare_before_resume và traceback.
3. Ba C2z tới~212 do raw cost subtraction nhiễu~1e−15 trong bài có variance thật0.
   Phiên MC độc lập thêm no-idle certificate; raw_gap/rawcost không sửa. Check mới3/3PASS,
   không thêm epsilon,z vẫn3; [receipt](mc_run01/X1008/C2_arithmetic_resolution.json).
4. Một mutant bịJensen guard từ chối; lần đầu ghiEXECUTION_ERROR rồi phân loại cụ thể
   mathematical invariant rejection, không coi mọi exception làKILLED.
5. Phiên bị tác giả ngắt: giữ incompletefull-test log/partialrepro/K320logs. /tmpclone cũ
   không còn sau resume nên dựng clone/venv mới;12job trước+7job sau đều cùngsource/deps.
6. CSVStage2cũ chưa cộtc_sw; chỉmetadata mới0 được kiểm vớispec gốc. Mọi cột đã có và
   pair-values khớp; không nới numeric tolerance hoặc rerunengine để sửa schema-checker.

## Thời gian đo trên máy này

8declaredregimes, một số job chạy đồng thời; gồm chi phí setup/cache/CPU contention.
Đây là performance measurement, **không** benchmark isolated hoặc lời hứa thời gianPhase4.

| ref | K | Median s/regime | Min–max s |
|---|---:|---:|---:|
| 1 | 40 | 11.270 | 4.318–25.548 |
| 1 | 80 | 31.892 | 9.158–97.220 |
| 1 | 160 | 73.321 | 15.825–258.265 |
| 2 | 40 | 39.463 | 23.770–77.991 |
| 2 | 20 | 13.158 | 7.013–23.937 |

19 lần tái lập thuộc **9 tọa độ vật lý**:9 mứcK80,9mức ref2 và baselineX2065;
không gọi đó là19regimes vật lý độc lập.

Nền tảngx86_64,Python3.14.5,NumPy2.5.3,SciPy1.18.1; longdouble cómantissa63bit,
eps1.0842e−19 theo np.finfo, không chỉ dựa vào tênfloat128. Repro dùng freshnativecache
và deps pin. Chỉ đã kiểm cùng nền tảng, không claim tái lập Mac/Windows.

## Lệnh, source và output

```bash
.venv/bin/python experiments/R3R_02_audit/run_engine_audit.py X2065 --out <new-dir>
.venv/bin/python experiments/R3R_02_audit/run_mutants.py
.venv/bin/python experiments/R3R_02_audit/run_mc.py prepare X2065 --out <new-dir>
.venv/bin/python experiments/R3R_02_audit/run_mc.py final X2065 --out <same-dir>
.venv/bin/python experiments/R3R_02_audit/run_extensions.py precision
.venv/bin/python experiments/R3R_02_audit/run_extensions.py K320 --id X1008
.venv/bin/python experiments/R3R_02_audit/run_extensions.py K320 --id X1009
.venv/bin/python experiments/R3R_02_audit/run_pilot_original_tests.py
.venv/bin/python -m pytest -q --junitxml=results/lessons/l3r_3/full_suite.xml
.venv/bin/python experiments/lessons/report_l3r_3.py
.venv/bin/python experiments/lessons/audit_l3r_3.py
```

Các lần đã chạy ghi command thực với outputpath trongcontroller receipts; script từ chối
ghi đè completed output. `<new-dir>` chỉ minh họa rerun, không nhận nó là path đã thực thi.
Clone/venv setup và resume có source/receipts, original19jobs đã soát không rerun thêm.

- [Spec/phạm vi/seed](../../../experiments/R3R_02_audit/prereg.json),[Nselection](../../../experiments/R3R_02_audit/MC_N_selection.json),[extension](../../../experiments/R3R_02_audit/prereg_extension.json).
- [Pilot snapshot](../../../experiments/R3R_02_audit/pilot_population.py),[API/adapter](../../../experiments/R3R_02_audit/bridge.py),[MC độc lập](../../../experiments/R3R_02_audit/independent_mc.py),[MC provenance](../../../experiments/R3R_02_audit/independent_mc_provenance.json).
- [SummaryJSON](summary.json),[CSV](summary.csv),[engine probes](engine_run01/),[MC/SE/moments](mc_run01/),[K320](K320_extension/).
- [Full log](full_tests.log),[XML](full_suite.xml),[originaltests](pilot_original_tests.log),[mutants](mutants.json),[repro](repro_run01/comparison_final.json).
- [Completion](../../../notes/phases/L3R_3_completion.json),[integrity verification](verification.json).

Không tạoplot hoặcCFoutcome; không promote code lênsrc,khôngmergetagpilot,
không đổi contractv1.2/card/A05freeze/R09/R10. Các số đã nhìn vẫn làdiscovery.

## Còn gì trước khi đóng gate?

Tác giả tự read-back/giải thích code cònOPEN; không ghiAIsoạn là tự viết. Chưa khóa
numericsv1.3 toàn miền, chưa có interval-certified tail/cost/policy bound ở lớppopulation,
D22 outcome/indicatorN3 chưa cài. N7 đã tái lập mới8cặp, không xác nhận code lịch sử củaclaim.
L3R.4 được học/thực hiện trong phạm vi củalesson; **L3R.5 không tự khóa numerics**
từ các dấuPASS riêng. P0-V10/L8/T05author-writing/G1/Phase4HOLD giữ nguyên.
