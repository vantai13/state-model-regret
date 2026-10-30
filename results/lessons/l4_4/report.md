# L4.4 — Baseline margin + Stay: thực thi tới sanity HOLD

Người phụ trách: **Doan Van Tai** · 30/10/2026.
AI triển khai; tác giả duyệt gói đặc tả trực tiếp, forecast AI soạn thay theo
mệnh lệnh riêng. Không ghi forecast này thành tác giả tự dự đoán độc lập.

**Kết quả thực thi: HOLD ở benchmark thứ ba.** Hai điểm MV PASS toàn bundle;
điểm SH đầu tiên fail oracle-bound sanity ngay ở θ=0. Không chạy ca thứ tư,
không full 90 điểm, không tune/freeze ρ*, không chấm forecast từ subset.
Đây là numerical/sanity HOLD, chưa phải verdict của MV/SH hoặc Main RQ.

## A. Đã làm

- Đọc trọn hai input và kiểm source thật. Source population nằm ở R3R_08,
  không phải R3R_11. Full Final Review §11.4 không có snapshot để tự kiểm lại;
  không nhận lời kiểm nguồn trong input thành thao tác của phiên này.
- Proposal `daa0f92` trước mọi tính baseline; tác giả chọn nguyên văn
  “Chọn gói đặc tả đã soạn (khuyến nghị)”. Spec/author choices/DL-104/source
  prereg khóa ở **75037cc**, trước plant baseline calls.
- Giữ margin và Stay; θ=ρ·E[JStay], lưới {0,.005,.01,.02,.05}. Chọn riêng vùng:
  MV tối ưu ô00, SH tối ưu ô10, trung bình regret/Cref, mỗi tọa độ một phiếu;
  exact tie chọn ρ nhỏ hơn. Không dùng oracle để cấp θ hoặc cộng θ vào cost.
- Luật đọc đã duyệt: MV median recovery≥.5 thì diễn đạt có điều kiện về margin;
  SH median|GSθ|/Cref<.005 và medianΔL10<0 mới thu hẹp vì baseline. Giữ verdict v2.
- Tập điểm đúng **18 MV⁺ + 72 SH⁺**, giữ mọi lớp pilot, age chuẩn hóa bằng
  Fraction, không lọc các điểm thuận lợi. Không trùng CF-v2/R09/R10.
- Implement margin riêng; physical sources không sửa. Wrapper giữ mảng thật
  do side() trả về trong một lần evaluate gốc ở mỗi mức. θ0 giữ thứ tự phép
  tính gốc; θ dương tính thêm uncertainty của scale Stay và phép cộng h+θ.
- Chạy synthetic/golden/full tests, control u0 thật, rồi benchmark đã khai.
  Giữ raw/cache/logs, xuất bảng đầy đủ các ρ ở hai điểm PASS và ledger 90 điểm.

## B. Command và trạng thái thực tế

```bash
.venv/bin/python -m pytest -q tests/test_p4_04_baseline.py
.venv/bin/python -m pytest -q
.venv/bin/python -m experiments.P4_04_baseline.freeze
.venv/bin/python -m experiments.P4_04_baseline.run control
.venv/bin/python -m experiments.P4_04_baseline.run benchmark
.venv/bin/python -m experiments.P4_04_baseline.summarize
.venv/bin/python -m experiments.P4_04_baseline.diagnose
.venv/bin/python -m experiments.P4_04_baseline.verify_results --output results/lessons/l4_4/verification.json
```

| Kiểm/run | Kết quả |
|---|---|
| Targeted tests | **18 PASS**, 200 random synthetic trials, seed44004; thêm zero-action, guard, argmin và luật đọc |
| Golden exact | Ba snapshot142/15,9,10; recovery7/10; đổi dự báo y1 cho recovery−3/10; đủ8toy rows khớp |
| Full suite | **797 PASS trong83.17s** |
| Control plant u0 | **PASS**, một level640/4; mọi ô và baseline bằng Stay;4.325888CPU-s |
| Native benchmark | **3/4 đã chạy:2PASS/1HOLD**;7discovery native rows |
| Sanity trên actual arrays |6/6levels ở hai MV PASS; control PASS; SH fail ở level đầu |
| Raw arithmetic/validity |6/7discovery rows rawTrue/errors[]; SH rawFalse có2validity errors; controlTrue/errors[] |
| CF flags |**8/8 False**, gồm control; không outcomeCF hoặc sealed mới |
| Full/budget/rho freeze |**NOT_RUN/NOT_CREATED/NOT_SELECTED** theo stop rule |

Native chính K640/ref4,dt1/480; coarse neighbors K320/ref4 vàK640/ref2.
Tất định, không seed/RNG cho plant, không sampling CI. Máy local WSL2,
thread1/worker; benchmark tuần tự. Môi trường thực tế ở environment.json.
Không cloud/VM. Cache local giữ lại, không đưa binaries vào Git.

## C. Số đo thật, baseline và phương pháp mới

### Hai điểm MV hoàn tất, chưa đại diện cả vùng

| ID / alias | Parameters (λA,λB,κ,η,h,c_sw) | L00 gốc | L00 margin ρ=1% | Recovery R_M tại1% | R_M tại5% |
|---|---|---:|---:|---:|---:|
| P44_024 /X2025 |(7,8,.1,.5,12,0)|14.592717735|14.471709966|0.636502|0.959837|
| P44_065 /X2071 |(7.5,8,.3,.75,16,0)|99.361568383|98.649201529|0.290080|0.792958|

L00 là packet·s; recovery không đơn vị. ρ=1% và5% đều nằm trong lưới đã khóa,
không phải ρ* hoặc kết quả tuning toàn vùng. CSV quan sát ghi đủ cả5ρ, gồm0.

| ρ | R_M tạiP44_024 | R_M tạiP44_065 |
|---:|---:|---:|
|0|0|0|
|0.5%|0.429788|0.151945|
|1%|0.636502|0.290080|
|2%|0.818849|0.483942|
|5%|0.959837|0.792958|

GS gốc lần lượt **−10.860070% / +0.178901%Cref**; ởρ1%, GSθ là
**−2.869392% / +0.756491%Cref**. ΔL10 tạiρ1% là **−1.271874 / −1.267423packet·s**.
Stay lần lượt14.402604017/100.801868374packet·s; headroom Stay so vớiL11 là
**0% /4.894004%Cref**. Không suy trung vị vùng/tần suất hoặc dùng hai điểm này
để chọnρ*. Các điểm MV trong map có thể là lớpC/B, không lọc mất chúng.

### Vì sao điểm SH dừng?

**P44_000 /X2000**, `(7,6,.1,.5,8,0)`, K640/ref4:

| Đại lượng | Giá trị (packet·s) |
|---|---:|
| L00 gốc, không margin |4.898833610913|
| L11 oracle estimate |4.898959886544|
| L11−L00 |0.000126275632|
| Tổng arithmetic errors e00+e11 |0.000099073938|
| Độ lệch vượt phần arithmetic errors |**0.000027201694**|

Sanity yêu cầu `Lθ + eθ ≥ L11 − e11`. Vòng kiểm đầu tiên đã làρ0/ô00 và
không đạt. Raw gốc có `arithmetic_pass=False`, validity errors:
`negative_nonnegative_contrast:G_SM` và `negative_nonnegative_contrast:G_S_M1`.
GS_M1/GSM estimate âm dù lý thuyết không âm. Độ lệch tương ứng
**0.002577601%Cref**; max arithmetic width **0.005297070%Cref**.

**Điều đã xác nhận:** ngay ô00 gốc đã không thỏa oracle bound với riêng
arithmetic errors ghi trong row. Failure không cần một margin dương. Điểm SH
dừng trước kiểm θ0 bit và trước hai coarse neighbors, nên **R1 tại điểm này chưa
được đánh giá**; không ghi bit sanity/R1 của SH là PASS.

**Điều chưa xác nhận:** nguyên nhân gốc. Frozen population dùng quadrature cho
S0 và S1; row tự ghi measured refinement không phải certified total error.
Một sai lệch quadrature chưa được bao trong arithmetic error là khả năng cần
kiểm, chưa phải chẩn đoán đã chứng minh. Không kết luận oracle thật bị đánh bại,
baseline margin sai, hypothesis sai hoặc toàn frame numerics đều sai.

Frozen lean width check ở row này vẫn PASS, consistency ở dung sai1/400 không
báo lỗi. Nhưng sanity baseline đã duyệt chặt hơn: oracle inequality với reported
arithmetic errors. Không đổi sang tolerance rộng hơn sau khi thấy số để cứu run.
Đây là blocker khác **Cref-dt R1 tạiκ=.05 củaL4.3**; HOLD cũ cũng giữ nguyên.

### Thời gian, phần đã chạy và phần chưa chạy

- Benchmark wall **125.003722s**. Hai bundle MV dùng19.736685/93.054545CPU-s.
- Raw SH failed call dùng**9.907439CPU-s**. Summary runner gốc chỉ cộng CPU của
  comparison có trườngCPU nên ghi112.791230CPU-s, bỏ sót failed call này.
  **Sửa bằng báo cáo readonly**, không sửa raw hoặc frozen runner:
  discovery evalCPU=**122.698669s**; cộng control=**127.024557s**.
- Overhead baseline trong7discovery calls đo được**4.591712CPU-s**. Không suy
  overhead cho cả90điểm hoặc gọi tổng evaluateCPU là toàn chi phí process/compiler.
- Ledger: **2PASS,1HOLD,87NOT_RUN**, đủ90cases. Benchmark cuốiP44_089 chưa chạy.
- Native có7discovery rows (6baseline-ready,1sanity-failed) và1control row.
  Không gọi đây là8dòng baseline-valid.
- Chưa có budget receipt/full/ρ* freeze. Hai forecast MV/SH doAI soạn đều
  **NOT_EVALUABLE** vì thiếu toàn scope. Không chấm từ2MV hoặc0SH hoàn tất.

## D. File thực tế

- [Spec](../../../experiments/P4_04_baseline/spec.md),
  [author choices](../../../experiments/P4_04_baseline/author_choices.json),
  [prereg](../../../experiments/P4_04_baseline/prereg.json),
  [scope90cases](../../../experiments/P4_04_baseline/cases.json),
  [DL-104](../../../notes/phases/PHASE_4_baseline_reading_decision.md).
- Source: [margin.py](../../../experiments/P4_04_baseline/margin.py),
  [evaluate.py](../../../experiments/P4_04_baseline/evaluate.py),
  [runner](../../../experiments/P4_04_baseline/run.py),
  [selection/reading interface](../../../experiments/P4_04_baseline/analysis.py),
  [tests](../../../tests/test_p4_04_baseline.py).
- Số liệu: [observed baseline CSV](observed_baselines.csv),
  [mọi level/ρ đã lưu](summary/baseline_grid.csv),
  [ledger90cases](summary/case_ledger.csv), [summary](summary/summary.json),
  [diagnosis](sanity_diagnosis.json), [CPU accounting](measured_summary.json),
  [goldens](goldens.json).
- Raw: [MVfirst](native/P44_024/level_640_4.json),
  [MVlast](native/P44_065/level_640_4.json),
  [SHfailure](native/P44_000/level_640_4.json),
  [control](controls/P44_CONTROL_U0/level_640_4.json).
- Logs: [797tests](full_tests.log), [18targeted](targeted_tests.log),
  [control](control.log), [benchmark](benchmark.log),
  [diagnosis](diagnosis.log), [verification](verification.log).
- [Environment](environment.json), [artifact manifest](artifact_manifest.json),
  [cache manifest](cache_manifest.json), [verification JSON](verification.json),
  [completion](../../../notes/phases/L4_4_completion.json),
  [forking#13–15](forking_paths.jsonl), [storage](STORAGE.md).

Không tạoρ_freeze.json, selected_baseline.csv, full_summary.json hoặc budget.json.
Không biểu đồ mới, MC, CF hoặc kết quả R09/R10. Descriptor được implement trong
analysis.describe và kê ở descriptive_outputs.json; **chưa tích hợp runnerL4.8**
vì lesson đó chưa được cung cấp, và chưa cóρ* để đóng băng.

## E. Kết luận

Đã thực hiện quyết định baseline/luật đọc, implement và test độc lập, chạy plant
tới stop rule. Hai điểm MV có margin hữu ích trên lưới; chưa được suy cả vùng.
Một điểm SH chưa qua sanity của đặc tả, nên **L4.4 experimental gate cònHOLD**.

Để tiếp tục cần prereg chẩn đoán coverage của oracle-bound/quadrature, giữ toàn
failure và criteria; chưa có căn cứ sửa physical engine hoặc nới sanity. Sau
khi numerical readiness được xử lý mới hoàn tất90điểm, chọn/freezeρ* và tích hợp
output mô tả choL4.8. G1 và verdict/cardv2 giữ nguyên; không claim realism,
novelty, Understanding hoặc ownership đãPASS. Quyết định#2–4DL103 còn của tác giả.
