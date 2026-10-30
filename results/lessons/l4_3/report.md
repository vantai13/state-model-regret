# L4.3 — Audit có phạm vi: kết quả kỹ thuật HOLD

Người phụ trách: **Doan Van Tai** · 30/10/2026.
Provenance: AI thực hiện theo ủy quyền; phạm vi A466/AB218 do tác giả chọn trực tiếp.
Forecast do AI soạn thay theo yêu cầu, không phải tác giả tự dự đoán độc lập.

**Đã thực thi tới điều kiện dừng đã preregister: HOLD ở native benchmark thứ ba.**
Không chạy ca thứ tư hoặc full relabel. Không nới dung sai, bỏ kiểm Cref hoặc nâng
mức số để đổi kết quả sau khi thấy số. Đây không phải FALSIFY của Main RQ/card.

## A. Đã thực hiện

- Đọc hai input, kiểm repo/source/freeze và interface native. Khóa code, scope,
  cases, forecasts, guard và stop rules ở **`ae174d0` trước physical calls**.
- Tác giả chọn vùng A theo bounds rõ trong L4.2:466dòng/450tọa độ; AB218dòng/216tọa độ.
  Tổng684aliases/666tọa độ. Không giả đã tái tạo ví dụ A428 thiếu bounds.
- Tái lập14dòng trên clean tag574a36f, kiểm9trường float64 từng bit. Chạy lại
  recount L4.1 từ git blobs ghimtag:1430→1376,54duplicate khớp,10/10checks PASS.
- Viết guard CF exact6coordinates, source hash/commit, identity, raw/lean validity,
  R1 gốc đủCref+sáucontrast, write-once, resume và dừng schedule khi HOLD.
- Xử lý một resource failure bằng amendment **`35e902e`**; giữ failure gốc và chỉ
  retry XPR0D ở output root mới. Không thay tiêu chí hoặc parameters.
- Phát hiện XA097 normalized trùng physical key R10; khóa sealed guard ở
  **`1db060f` trước native calls**. Ghi SEALED_BLOCKED, không thay bằng điểm khác.
- Chạy native benchmark ở ba tọa độ, mỗi tọa độ đủ ba mức; ca thứ ba failR1 nên
  dừng. Giữ tất cả raw/cache/logs, xuất bảng so sánh và ledger đủ666cases/684aliases.

Không sửa `src/`, physical engine, contract, cardv2, numerics receipt hoặc CF list.
Không chọn baseline, card mới, ngân sách CF-v3 hoặc Gate4.

## B. Command thực tế và kiểm chứng

```bash
.venv/bin/python -m pytest -q tests/test_p4_03_map_audit.py
.venv/bin/python -m experiments.P4_03_map_audit.run replay
.venv/bin/python -m experiments.P4_03_map_audit.resource_resume replay
.venv/bin/python -m experiments.P4_03_map_audit.sealed_guard benchmark
.venv/bin/python -m pytest -q
.venv/bin/python -m experiments.P4_03_map_audit.report_final --out results/lessons/l4_3/report_data
.venv/bin/python -m experiments.P4_03_map_audit.execution_ledger
.venv/bin/python -m experiments.P4_03_map_audit.verify_results --output results/lessons/l4_3/verification.json
```

| Kiểm / run | Kết quả thực tế |
|---|---|
| Audit guard tests |17PASS; gồm CF guard dưới `python -O`, modifiedΓ, raw validity, Cref R1, nhãn lật, R6 và write-once |
| Resource amendment tests |2PASS; worker chỉ khác một dòng capCPU, case arguments giữ nguyên |
| Sealed guard tests |3PASS; từ chốiR10, giữ original alias ledger, không đổi child case arguments |
| Full suite cuối |**779PASS trong100.17s** |
| Full suite trước resource/sealed amendments |774PASS112.52s và776PASS93.40s; giữ log lịch sử |
| Recount/identity pilot |**10/10PASS** |
| PartA cuối sau resource retry |**14/14PASS,126/126trường trùng bit** |
| Native benchmark |**3/4đã chạy,2PASS/1HOLD**;9level rows hoàn tất |
| Native arithmetic / validity / CF flags |**9/9True,9/9rỗng,9/9False**; identity guards không lỗi |
| Frozen/source/CF/tag hashes |PASS trước và sau run; kết quả chi tiết ở verification.json |

Tất cả test/experiment ở WSL2 local, Python3.14.5, NumPy2.5.3, SciPy1.18.1,
mpmath1.3.0; compiler g++11.4.0 và Boost header có sẵn. Worker thread1; replay có
2worker, benchmark tuần tự. Xem environment.json. Không chạy cloud hoặc gửi dữ liệu.

### Lịch sử lỗi và recovery, không xóa hoặc tô thành PASS

1. Lượt prepare ban đầu chọn nhầm dòng `done` trong log; sửa regex trước freeze,
   chưa có physical call. Một synthetic test trước freeze kỳ vọng nhầmJ; đúng làD
   vìΓ<GS. Sửa đáp án fixture trước physical run, không đổi rule/data để épPASS.
2. Người dùng ngắt phiên lúc hai replay chưa có output. Giữ3map2receipt xong,
   resume các dòng thiếu; không chạy lại ba dòng hoàn tất.
3. Attempt gốc có13/14PASS; XPR0D exit**−24=SIGXCPU** ở cap900CPU-s do AI đặt.
   Chỉ117trường thực sự đã so; field `comparisons:126` trong summary gốc là số slot
   dự kiến, không phải số đã kiểm thành công. Artifact gốc giữ nguyên.
4. Resource amendment commit trước retry, chỉ tăng XPR0D tới1800CPU-s/2400wall-s;
   worker mới khác đúng một dòng setrlimit. Retry PASS, CPU đo được
   **945.816274s**. Summary mới kiểm lại actual/expected cả14receipt, không chỉ tin flag.
   Tổng CPU của14replay có kết quả là**1928.178262s**; chưa cộng đầy đủ các lần bị ngắt
   hoặc bịkill, không gọi số này là tổng chi phí toàn phiên.
5. Native benchmark exit1 theo stop rule vìR1. Không phải lỗi command hoặc thiếu
   C++/Boost. Full run và budget chưa được mở sau HOLD.

## C. Kết quả đo được

### Pilot so với native: cả hai bên được hiển thị

Pilot K40,ref1,dt1/120s. Native main K640,ref4,dt1/480s; hai hàng xóm K320/ref4
vàK640/ref2. Ba điểm benchmark đều age1,amp6,c_sw0, không làm tròn. Tất định,
không RNG/seed hoặc sampling CI. % là theo C̄ref của từng engine; shift là **pp**.

| ID | GS pilot (%Cref) | GS native (%Cref) | Shift GS (pp) | Point class | Kết quả |
|---|---:|---:|---:|---|---|
| XM2S189 |4.010867687|3.915048600|−0.095819087|A→A|PASS tại điểm |
| XM2S110 |1.007996888|0.969564193|−0.038432696|A→D|PASS số, **UNRESOLVED R6** |
| XM2X000 |7.105285402|7.005615796|−0.099669607|AB→AB theo estimate|**HOLD R1**, không nhãn dùng được |

| ID | GM pilot | GM native | Γ pilot | Γ native |
|---|---:|---:|---:|---:|
| XM2S189 |0.592868157|0.526556474|−0.427957641|−0.358354435|
| XM2S110 |0.003070262|0.003246242|0.048393566|0.050128593|
| XM2X000 |11.742975476|11.842164285|−7.086973193|−6.990050976|

Tất cả ô bảng thứ hai cũng là%Cref. Sáu metric đầy đủ, d và shift ở
`report_data/pilot_native_metrics.csv`; không chỉ báoGS thuận lợi.

**XM2S110:** khoảng cách GS tới1% là**0.030435807pp**, nhỏ hơn
dGS=**0.034927042pp**. Point estimate làD, nhưng không được dùng như nhãn đã phân
giải. Tái tạo được con số mới làm tròn0.970/d0.035 trong summaryK6, không chứng
nhận đã tái lập file8K6 gốc đang thiếu.

### Vì sao XM2X000 buộc HOLD?

Parameters `(λA,λB,κ,η,h,c_sw)=(6,13/2,1/20,5/8,4,0)`.

| Mức | Cref (cost unit packet·s) |
|---|---:|
| K640/ref4 |1.138669405818155|
| K320/ref4 |1.138692706140862|
| K640/ref2 |1.142205420546254|

R1 theo dt:

`abs(Cref640,4 − Cref640,2) / Cref640,4 = 0.003105391881 = 0.3105391881%`

Giới hạn contract là**0.25%**. Chênh sáu contrast giữa các mức chỉ tối đa
**0.046850140pp**; max shift pilot/native của năm metric được kiểm là
**0.196111026pp**, đều dưới0.25pp. Nhưng R1 còn đòi Cref ổn định, nên vẫn **HOLD**.
Skeleton chỉ so ratio contrasts có thể bỏ sót lỗi validity này; runner dùng hàm
contract gốc, không bỏ kiểm Cref sau khi thấy kết quả.

Đã kiểm input/age/rounding/source và raw arithmetic: không thấy sai khác input,
không lỗi identity/raw validity. Blocker quan sát được là **resolution chưa đạtR1
ở điểm này**, chưa phải kết luận native hoặc pilot có bug. R1 trên pilot mịn hơn
tại điểm này chưa chạy. Không nângK/ref ngoài ba mức để cứu audit sau kết quả.

MC trực tiếp **chưa chạy**: pilot/native chưa vượt0.25pp, còn native đã failR1
riêng. Cần giải quyết numerical readiness trước việc dùng point này; nếu cardSUB
sống ởL4.5 và có coverage/code-path dependency mới, MC phải có prereg riêng.
118ca calibration cũ có minκ1/10, không cóκ1/20; không mượn coverage đó như global proof.

### Phạm vi đã chạy và chưa chạy

Benchmark dùng**40.116782CPU-s**,**42.476359wall-s** cho ba bundle đã chạy.
Ca thứ tư XM2X077/P43_0265: **NOT_RUN_AFTER_HOLD**. Không suy p95 hoặc ngân sách
full từ ba số này. Không có budget receipt/full run được tạo.

| Trạng thái ledger | Tọa độ distinct | Aliases |
|---|---:|---:|
| PASS riêng tại điểm |2|2|
| HOLD R1 |1|1|
| SEALED_BLOCKED (R10/P43_0628/XA097) |1|1|
| NOT_RUN_AUDIT_HOLD |662|680|
| **Toàn scope đã khai** |**666**|**684**|

**Chưa ước được tỷ lệ UNRESOLVED hoặc tỷ lệ lật của toàn vùng A/AB.** Chỉ quan sát
một point-estimate flip trong ba điểm. Hai A có1R6UNRESOLVED; AB có1validityHOLD.
Không dùng1/2 hoặc1/1 làm tỷ lệ toàn vùng, không tính CI cho mẫu benchmark thích nghi.
Ba forecast toàn scope là **NOT_EVALUABLE**, không chấm PASS/FALSIFY từ mẫu thiếu.

### E11 và niêm phong

Trên raw pilot,54nhóm/216so sánh cùng physical parameters vớiage1: max relative
L11 shift**0.7109021917%**, L10 shift**0.7105559643%**, cặpXA027/XM1048. Đây là
diagnostic vi phạm S04 ở approximation pilot; không trích mứcLbar làm finding.
Cancellation của shared cost chưa cho certified contrast error bound.

XA097 ởage1/2 quy về R10 `(15/2,8,u1,κ3/5,h4,c_sw0)`. Đã chặn trước native;
không thay điểm khác, không đổi denominator âm thầm. R09 không giao. Giao physical
key không tự đồng nhất population estimand với conditional A05-T; không tính thêm
D/J/gap/regret/contrast ở key niêm phong. Kết quả CF mới:**0**.

## D. File và artifact

- Source/criteria: [prereg.md](../../../experiments/P4_03_map_audit/prereg.md),
  [prereg.json](../../../experiments/P4_03_map_audit/prereg.json),
  [common guards/R1](../../../experiments/P4_03_map_audit/common.py),
  [runner](../../../experiments/P4_03_map_audit/run.py),
  [resource wrapper](../../../experiments/P4_03_map_audit/resource_resume.py),
  [sealed guard](../../../experiments/P4_03_map_audit/sealed_guard.py).
- Amendments: [resource](../../../experiments/P4_03_map_audit/resource_amendment.md),
  [sealed scope](../../../experiments/P4_03_map_audit/sealed_scope.md),
  [source corrections](../../../notes/verification/l4_3/source_corrections.md).
- PartA history: [original HOLD](partA/summary.json),
  [resource-resolved PASS](resource_v2/partA/summary.json),
  [retry numeric output](resource_v2/partA/XPR0D.json),
  [static E11/coverage diagnostics](static_diagnostics.json).
- Native raw: [P43_0379](resource_v2/native/P43_0379/level_640_4.json),
  [P43_0114](resource_v2/native/P43_0114/level_640_4.json),
  [P43_0000](resource_v2/native/P43_0000/level_640_4.json);
  mỗi folder có đủ hai coarse neighbors, comparison và worker log.
- Số liệu: [summary.json](report_data/summary.json),
  [pilot/native CSV](report_data/pilot_native_metrics.csv),
  [R1 Cref CSV](report_data/R1_reference_cost.csv),
  [point labels/validity CSV](report_data/audit_points.csv),
  [class flips](report_data/class_flips.csv),
  [toàn666cases](execution_ledger/cases.csv), [toàn684aliases](execution_ledger/aliases.csv).
- Log: [replay ban đầu](replay.log), [replay sau interruption](replay_resume.log),
  [resource retry](resource_replay.log), [native benchmark](native_benchmark.log),
  [779fulltests](full_tests_after_sealed_guard.log), [verification](verification.json).
- Config/hash: [input manifest](input_manifest.json), [environment](environment.json),
  [report manifest](report_data/manifest.json), [raw artifact hashes](artifact_manifest.json),
  [cache manifest](cache_manifest.json), [completion](../../../notes/phases/L4_3_completion.json).
  [Verification log cuối](final_artifact_check.log) kiểm lại artifact manifest và các link
  sau khi hồ sơ đầy đủ; `verification.json` được ghi trước bước tạo manifest này.

Cache local giữ nguyên tại `resource_v2/native_cache/`:48file không rỗng,
31,051,632bytes (khoảng29.6MiB), không đưa vào Git; raw rows/log/certification
metadata và hash manifest được giữ. Xem [STORAGE.md](resource_v2/STORAGE.md).
Không tạo biểu đồ, simulation MC, native_probe_summary giả hoặc CF outcomes.

## E. Kết luận và bước tiếp

Đã xác nhận bit reproducibility của sample đã khai và pilot identity bookkeeping;
ở ba điểm đã chạy, native source đúng receipt, input không làm tròn và guards đạt.
Một point-estimate flip có uncertainty hợp lệ; một điểm κ=.05 không đạtR1 doCref.
**Kết quả kỹ thuật làHOLD; L4.5 vẽ hộp/thêm card vẫn bị chặn.**

Không xác nhận accuracy toàn bản đồ, hypothesis, queue mechanism, realism hay
novelty; G1 giữ nguyên. Nhãn audit do tác giả xác nhận cònOPEN; Understanding,
T07P4 author addendum, P0-V10/L8 và bốn quyết định DL103 giữ trạng thái cũ.
Original6K2 IDs và8K6 file vẫnUNVERIFIED, không gán14replays mới thành lịch sử đó.

Bước cần thiết nếu tiếp tục native: prereg mới cho numerical coverage tạiκ=.05,
giữ failure này và cùng criteria; sau khi xử lýHOLD mới dùng nhãn choL4.5. Có thể
học L4.4 trước, nhưng chưa tự chọn baseline/card hoặc chạy confirmation.
