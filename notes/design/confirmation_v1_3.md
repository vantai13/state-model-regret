# L3R.7 — Thiết kế confirmation v1.3

Người phụ trách/người soạn: **Doan Van Tai** · 29/10/2026.
Trạng thái: **PREPARATION_ONLY / N_RULE_ADOPTED_NUMERICS_DEFERRED** (DL-077).

**Cập nhật DL-078–079:** gate numerics đã chạy9jobs sau prereg0efddcc;
3legacyanchorskhớp,stationary3/6complete và3/6CPUlimit. Kết quả
**HOLD_FEASIBILITY_STAGE0**;312globalcalibrationjobs chưa mở. Các mục fullaudit,
timing/r/levels, n/root/CF phía dưới vẫn DEFERRED.
[Report](../../results/lessons/l3r_7/numerics_report.md).
Triển khai theo ba phần lesson; không phải prereg cuối hoặc Gate3R GO.
Card v1 `1414d92` và contract v1.3 `3d2359b` giữ nguyên byte/tag.
G1 không đổi; Phase4 HOLD; Understanding do tác giả tự đánh giá, vẫn OPEN.

## 1. Đại lượng và đơn vị

Đơn vị phân tích là **regime** rút từ measure đã khóa trên một vùng. Population là
measure trong plant, không phải tập mạng ngoài đời. Primary: Hyp-MV và Hyp-SH;
Γ chỉ diagnostic; không secondary. Giữ nguyên scorer `R3R_06_cards/verdict.py`,
α=1/40 mỗi card, π0=1/2, AND, R4 bốn góc và R5 >10% mỗi vùng.
MEETS là GM/C̄ref≥1% cho MV, GS/C̄ref≤−1% cho SH; không cứu SH bằng dấu âm đơn thuần.

## 2. Luật chọn n, ngân sách và trạng thái chưa chốt

**Tác giả đã duyệt “Đồng ý khóa luật này” (DL-077):** bốn vùng được chấm cùng n∈{30,40,60}.
Chọn n lớn nhất vừa B theo p95 thời gian CPU của **cả bundle** main/coarse-K/coarse-dt,
cộng 30% dự phòng. Cắt BND trước: sau khi chọn n cho bốn vùng, thêm 15/vùng BND nếu
cả hai vừa ngân sách; nếu không là 0 cho cả hai. Không hạ n<30; nếu không đủ thì HOLD
hoặc tăng B bằng DL trước sampling. Tính cả fixed validation cost cho controls,
anchors hai mức và identical-model checks, không tính ba lần chi phí bundle.

`cost_seconds = 1.30 * ((4*n + 2*n_bnd)*p95_bundle_seconds + fixed_validation_seconds)`.
Đây là dự toán kế hoạch, không phải hard upper bound hay timing đã đo. Báo riêng
đuôi thời gian, số luồng, CPU-giờ và wall-time; không lấy B/threads làm thời gian đảm bảo.
Các số 7phút/24/40–80CPU-giờ trong lesson là ngoại suy pilot, **chưa** dự toán CF đáng tin.

Tác giả ủy quyền chọn B/concurrency theo máy: “tùy theo ý bạn, bạn có thể xem máy
củ tôi mà chạy”. Theo resource snapshot WSL2, chọn **B=48 CPU-giờ**, đã gồm30%
dự phòng; tối đa4worker processes, mỗi worker1luồng BLAS/OpenMP. Profile một
worker trước, bắt đầu2 khi memory budget cho phép, nếu không dùng1/HOLD.
Pool target6GiB, chừa3GiBMemAvailable và0.5GiBpooloverhead; worker count cuối
theo peakRSS bảo thủ, không chỉ sốcore. Chưa enforce bằng OS/backend trong phiên này.
[Policy machine-readable](confirmation_compute_budget_v1.json),
[snapshot](../../results/lessons/l3r_7/resources/20261029_01/snapshot.json).
48CPU-giờ/4worker tương đương lý tưởng12h bậnCPU, không phải wall-time đo được.

Hiện tại **n=null,n_bnd=null,root=null,workers_final=null**. Luật đã AUTHOR_ADOPTED;
`power.select_allocation` chỉ là evaluator, số giả không cấp n thực tế.
Sau v1.3.1 đo p95 bundle/fixed cost và r theo coverage rồi mới áp luật với B48.
Prereg sau này phải ghi hash/version policy này; đổi B cần DL/version trước draw.

## 3. Power và giới hạn của phép nhân gần đúng

Xuất bảng n={30,40,60}, p+={.6,.7,.8}, p−={.1,.2,.3,.4} vào
`results/lessons/l3r_7/preparation/power.csv`. Giả định r=0 và UNDEFINED=0;
độc lập giữa samples/vùng; collision rejection được khai riêng, không claim iid
chính xác sau khi rút không hoàn lại trên measure đã làm tròn.
Không dùng 16/16 hay 57/72 làm ước lượng population p; p− chưa có discovery.

Ví dụ p+=.7,p−=.2: P(PASS) một card xấp xỉ .553/.690/.836 cho n30/40/60.
Đây là xác suất có điều kiện theo giả định, không phải forecast CF thật.
P(cả hai card PASS) chỉ bằng bình phương khi có thêm giả định độc lập giữa hai card.

`r5_risk.csv` tính P(U>floor(.1*n)) chính xác bằng nhị thức. `r4_r5_power.csv`
tính thêm R4: Ω+ cần số MEETS chắc chắn≥k_support; Ω− cần MEETS+U≤k_reject;
đồng thời mỗi vùng U≤floor(.1*n). p được hiểu là P(MEETS | resolved), U độc lập
với nhãn tiềm ẩn, không có UNDEFINED. Tính tổng multinomial, không coi R5 và k độc lập.

**Đính chính mức diễn giải của bài tập Part1 §17:** nhân power r=0 với xác suất
qua R5 chỉ là heuristic, bỏ ảnh hưởng R4 và phụ thuộc giữa số U/số MEETS.
n40,p+=.7,p−=.2,r+=.02,r−=.05: heuristic≈.655709; mô hình đầy đủ này≈.561573.
Không gọi số nào là measured power; nếu U phụ thuộc mạnh vào effect, bảng vẫn sai
về population và cần báo giới hạn. Tăng n không chữa r gần/vượt .1.

## 4. Sampler, seed và collision

Thứ tự cố định: MV+A, MV-ii, MV-BND, SH+A, SH-ii, SH-BND.
Mỗi vùng dùng `SeedSequence(root, spawn_key=(index,))` và PCG64 riêng; không dùng
action/model/K/ref trong seed key. λA/λB/u uniform; κ/h log-uniform; tọa độ ghim
giữ cố định; độc lập trước làm tròn. Bước λ/u/κ=1/1000, h=1/120s, ties-to-even.
c_sw=0. Validate đúng schema, không ceil horizon hoặc tự bỏ mẫu không hợp lệ.

Hiện chỉ dùng **dải test318700000–318709999**, root318700001; không engine trên mẫu thử,
không lưu chúng thành CF. Danh sách thật chưa tồn tại. Confirmation root cấp mới
sau numerics và n, commit allocation + prereg trước draw; không tái dùng audit/generic/demo.

Inventory dùng tuple hữu tỉ `(λA,λB,u,κ,h,c_sw)`, không chứa K/ref/id. Nguồn: cả
ba stage pilot (216ID/210keys),18robustnessID,58ô v1.2,8audit IDs và8biến thể u0
**dự phòng bảo thủ**, không attest cả8 đã chạy. Với v1.2 dùng u=2η; các control
khác amplitude hoặc baseline không hợp lệ lưu namespace riêng, không ép thành
regime P1. Generic single-queue/finite algebraic toys không có đủ joint key;
ghi namespace và checksum thay vì tự bịa λB/u/h. R09/R10 chỉ reserve tọa độ;
R11 có trong inventory. Coverage chỉ bao gồm nguồn local đã đăng ký, không chứng nhận
mọi lần làm việc ngoài repo/máy khác.

Trùng chính xác với inventory hoặc batch: redraw, ghi count, tối đa1000/vùng;
vượt thì dừng, giữ attempt, không đổi seed. Trùng gần giữ nguyên, chỉ báo mô tả.
Mọi row giữ **origin_region**, kể cả κ=.300/1; không reassign theo geometry.
Global keys shared giữa vùng; prefix/stream isolation không loại bỏ ảnh hưởng
của exact collision với vùng xử lý trước, nên mọi redraw phải được báo.

Báo contract L∞ theo vector đã khóa và thêm L∞ chuẩn hóa width, κ/h trên log.
Metric thêm bỏ các trục ghim, nên báo cả nearest cùng pinned slice để không gọi
một điểm sai λB là gần. Sensitivity mô tả: bỏ các điểm có distance cùng pinned
slice≤d, d∈{.05,.10} width/log metric, báo lại n/count/rate; không đổi verdict,
không dùng nó để redraw hoặc chọn measure sau outcomes.

Đã kiểm tài liệu chính thức: [NumPy compatibility](https://numpy.org/doc/stable/reference/random/compatibility.html)
cho phép thay luồng trong một số phiên bản/điều kiện; [PCG64](https://numpy.org/doc/stable/reference/random/bit_generators/pcg64.html)
cam kết integer stream theo seed; [NEP19](https://numpy.org/neps/nep-0019-rng-policy.html)
không bảo đảm toàn bộ phép biến đổi phân phối xuyên môi trường. Ghi versions/build,
commit **danh sách** cùng hash; Phase4 chỉ đọc, không regenerate. Giữ môi trường
Python3.14.5/NumPy2.5.3/SciPy1.18.1 của phiên chuẩn bị trong environment.json;
khóa lại full environment khi prereg thực được tạo.

## 5. Controls, anchor và identity

Trong P1 stable với OFF drain âm, stationary có atom ở0; một OFF run dài có
xác suất dương nên không chứng nhận mọi state trong support tránh rỗng. Vì thế
không dùng control “stationary conservation” của v1.2 trong các vùng này.
Đây không cấm snapshot/finite-horizon toy conservation đã có, hoặc zero-action.

- Zero-action u0 ở tâm measure MV+A/SH+A: λ/u axes lấy midpoint, κ/h lấy geometric
  midpoint rồi snap; u sau đó đặt0, role control. Sáu contrast phải zero **chính xác**.
- Identical models: M1:=M0 trong nhánh test, dùng hai row cố định đầu tiên của
  MV+A và SH+A (không theo outcome); GM và GM|S1 phải zero chính xác. Đây là kiểm
  nhân tạo bookkeeping, không phải evidence model thật tương đương.
- Identity kiểm trên mọi row, không phải toàn bộ có thể chạy trước outcomes:
  control/anchors trước, sau đó per-row identity trong lúc evaluate rồi mới chấm.
  ΣpD=π guard, GM/GS|M1/GM|S1≥0 và σ̄ bounds theo audit đã khóa; không lỏng guard theo kết quả.
- X2065/X1008/X1009: replay code/levels cũ K40/ref1 so byte/đơn vị đúng artifact
  gốc; mức v1.3.1 so calibration bằng luật đã khai, không đòi bằng pilot K40.

Hai zero controls + ba anchors hai mức =8 lượt; identical-model/identity overhead
phải đo riêng trong fixed cost hoặc bundle. Không cộng control/anchor vào N.
Thực chạy các nhánh này thuộc Phase4; L3R.7 chỉ test guard trên số giả.

## 6. Dry-run và khóa thực thi

A: kiểm scorer + format adapter bằng bảng giả, phủ MEETS/FAILS/UNRESOLVED/UNDEFINED,
R5 3/30 vs4/30, R4 đồng nhất vs downgrade, các verdict, shared boundary và control1e−16.
C: từ chối thiếu cờ, receipt/hash/manifest, tag, Gate3R/human/D22, truncated list.
Adapter trên số **pilot cũ thiếu coarse pairs** phải UNRESOLVED; Ω− N0 là đúng.
Đây chưa phải B (toàn engine ở mức v1.3.1); không gọi dummy raw costs là measurement.
B **DEFERRED** tới numerics v1.3.1; chỉ chạy discovery/calibration đã khai.
D (engine trên mẫu thử từ các vùng, đặc biệt Ω−) bị cấm.

`run.py` hiện là entry point khóa, ghi cả invocation bị từ chối và không import
physical engine. **Audited backend/orchestration thực vẫn DEFERRED**, phụ thuộc
v1.3.1/D22 và dry-run B; không thể execute dù ai chỉ đổi một cờ status.
Các interface schema trong gates.py là dự thảo cho việc tích hợp, không tạo
tag/receipt v1.3.1 hoặc công nhận audit chỉ bằng boolean.

Thứ tự sau này: commit tooling/tests → v1.3.1 evidence/tag → n+B+seed allocation+
prereg commit → một lần generate ở directory đã ghi trong prereg → commit list/
generation log/execution receipt → verify tất cả trước engine → Gate3R cho Phase4.
Manifest phải bao phủ **toàn bộ** module tooling, receipt checker và scorer đã
khóa; không chỉ sampler.py. Bug sampler: cùng root, giữ attempt cũ, DL/version
prereg cùng deviation chain trước attempt mới; không tùy chọn path để sinh lại.

## 7. Khả năng phân biệt và hành động trước outcomes

MV+A16góc được chọn sau pilot; các effect nhỏ gần1% có thể đổi sau numerics hoặc
ở nội suy. SH+A15non-meets tập trung gần λA≈λB; lưới không cùng trọng số measure.
Thể tích continuous của λA−λB<.25 trong rectangle SH bằng .25²/2=.03125;
đó là geometry, không phải prevalence harm. Ω− hai card chưa có discovery;
các suy luận trơn/κ đều chưa được kiểm. FALSIFY không chứng minh pattern “chỉ ở góc”.

| Verdict/codes | Cách đọc được phép | Hành động đã soạn trước |
|---|---|---|
| PASS | Claim majority ở Ω+ và non-majority ở Ω− đứng trong measure, chưa cơ chế | Phase5 kiểm can thiệp κ/h/λ; MI null; SH ghi backlog+mode oracle, D22 theo audit |
| WEAKEN-W1 | Effect cũng có ở Ω−, chưa đặc thù κ | Thu hẹp đặc thù κ; thiết kế Phase5 mới trước outcomes, không sửa card CF |
| WEAKEN-W2 | Chưa phân biệt được control | Giữ giới hạn độ chính xác của Ω−; không chạy lại CF để kiếm PASS |
| WEAKEN-W3 | Dương nhưng chưa đủ độ chính xác/robustness ở Ω+ | Không mở rộng claim, báo n/U/R4; không đổi n sau outcomes |
| FALSIFY | Majority prediction trong Ω+ bị bác, không chứng minh nguyên nhân | NARROW hoặc đề xuất PIVOT có DL; không phát biểu “M0 luôn đủ tốt” |
| INCONCLUSIVE-PRECISION | Thiếu phân biệt thống kê; chưa phải lỗi engine | Báo chưa kết luận; không tự rerun hay tăng n trên CF cũ |
| INCONCLUSIVE-VALIDITY/R5 | Thiếu validity hoặc vượt U policy | Chỉ sửa lỗi có bằng chứng theo deviation; không coi U nhiều tự động là bug |
| INCONCLUSIVE-R4 | Verdict không robust ở extremes | Báo giới hạn; không mở escalation ngoài R3 để cứu kết quả |

**Sửa diễn giải Part3 §5.4:** INCONCLUSIVE còn có PRECISION/R4, không chỉ numerics
hoặc validity. Chỉ rerun toàn batch khi có bug/validity failure xác định và được
ghi DL/version; không rerun mọi INCONCLUSIVE. Cả hai FALSIFY: tối đa một vòng
discovery→confirmation mới theo reformulation budget, phải có lý do cụ thể viết
trước vòng mới; nếu không, báo kết quả âm/equivalence đúng phạm vi.

## 8. Deviation, blinding và không dừng theo kết quả

Deviation log chứa UTC, sự cố, nguyên nhân, artifacts/code versions, **đã thấy gì
trước quyết định**, hành động, ảnh hưởng verdict; append-only, không sửa lịch sử.

| Sự cố | Luật |
|---|---|
| Hạ tầng dừng | Resume đúng row/config/version, giữ checkpoint; không bỏ row |
| Control/anchor/identity sai | Dừng, giữ output, sửa version/DL, chạy lại toàn batch đã đăng ký |
| Bug sau partial outcomes | Ghi rõ exposure, giữ cả kết quả cũ/mới, sửa rồi replay toàn batch; giữ card/vùng/ngưỡng |
| Hết B | Pause không chấm partial; DL tăng B trước resume; không đổi n đã rút |
| U nhiều/sát biên | Chỉ R3 hữu hạn → R4 → R5; không thêm mức để cứu primary |
| Kết quả đẹp/xấu | Cùng validity checks luôn chạy; mọi debug bổ sung ghi “triggered after outcome” |

Runner thực sau tích hợp chỉ in progress/error, không giá trị/partial verdict.
Per-row results không đưa ra màn hình, không cho scorer mở khi thiếu batch.
Scorer chạy một lần sau controls/anchors/all rows complete; lưu hash verdict và
marker write-once. Retry hạ tầng không được phát sinh scoring lần hai; rerun do
bug có version/deviation và lưu cả hai. Không dùng bảng power để dừng sớm.

## 9. Bàn giao và phần còn thiếu

Chuẩn bị được: design, power, sampler/tests, inventory/distance, guard/tests,
decision map, deviation/blinding, adapter refusal với saved pilot unpaired.
Chưa có: mức số final, timing/r coverage thực, n, confirmation root, final
prereg/list/execution receipt, audited backend và dry-run B. Không tạo file có
tên prereg.json/regimes_cf.json chứa placeholders để tránh bị hiểu là đã freeze.

Numerics v1.3.1 phải phủ κ=3,h=16 **và** interior rational rate1/1000. Tính từ
tham số λA=7.123,u=1.234 cho degree12000 so maxpilot24, ref2 không giảm degree;
DL-078–079 đã chạy marginalA/B:CPUlimit ởbước tìmnghiệm,RSSmẫu≈2.21GiB;
chưa có timingcủafullregime hoặc p95measure. Không benchmark trên mẫu thử CF. Calibration phải
khai design trước computation. Nếu đổi measure/rounding để giảm chi phí, cần
cardv2+DL, không sửa ngầm cardv1.

Ngân sách/luật đã chốt theo DL-077; sau numerics mới chốt n rồi sinh CF. Phase4 còn D22 audit,
P0-V10/L8 và Gate3R; realism HOLD_UNSOURCED chỉ được phân xử tại Gate3R, không tự waive.
Không khẳng định hypothesis, cơ chế, realism hay novelty đã được xác nhận.
