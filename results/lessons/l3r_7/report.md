# L3R.7 — báo cáo thực hiện phần chuẩn bị confirmation

Người phụ trách/người soạn: **Doan Van Tai** · 29/10/2026.

**Kết quả mới nhất DL-078–079:** đã chạy9calibrationjobs theo prereg0efddcc;
3legacyanchorskhớp và3/6stationarycomplete,3/6CPUlimit. Full595/8numerics tests
PASS; tổng396.116CPU-s;312globaljobs chưa chạy theo stoprule. **Numerics HOLD**,
chưa chọnK*/dt*/n/root/CF. Xem [report numerics](numerics_report.md) và
[CSV thực đo](../../R3R_numerics/20261029_01/metrics.csv).
Các số587/38 vàengine0 bên dưới là **snapshot của phần chuẩn bị trước calibration**.

**Cập nhật DL-077 sau commit chuẩn bị c4b4bf5:** tác giả đã duyệt luật chọn n và
ủy quyền chọn B/concurrency theo máy. Chọn **48CPU-giờ**, profile1worker rồi bắt
đầu2/tốiđa4 khi đủRAM,1BLAS/OpenMPthread mỗiworker. n/root/CF vẫn chưa cấp.
Snapshot WSL2: Ryzen57535HS,10logicalCPU,13.65GiBRAM,9.50GiBavailable lúc15:00:53
Asia/Saigon; CPU utilization1s≈0.49%. Đây không phải benchmark engine hoặc
cam kết thời gian chạy. Resource policy chưa được OS/backend enforce.
[Policy](../../../notes/design/confirmation_compute_budget_v1.json) ·
[Snapshot](resources/20261029_01/snapshot.json) ·
[Nguyên văn trả lời](author_choices.json).

Audit sau cập nhật xác nhận budget/choices/completion đồng bộ,card/contract
khớp; không rerun toàn bộpytest cho thay đổi metadata. Số587tests bên dưới là
kết quả thực của phiên chuẩn bị đã lưu trong commitc4b4bf5.
Trạng thái **PREPARATION_COMPLETE / SAMPLING_BLOCKED**. Triển khai theo yêu cầu
“tiếp tục lesson 7 đi”, đọc đủ ba phần [intake](intake.json). Không có xác nhận
tác giả tự read-back/hiểu bài hoặc người đọc thật mới. G1, Phase4 HOLD giữ nguyên.

## 1. Đã thực hiện

- Sửa receipt checker: yêu cầu **đúng tập10file**; reject rỗng/thiếu/thừa/hash lỗi,
  malformed JSON, duplicate key, schema/commit sai. Receipt/card v1 cũ không sửa.
  Hai failure ban đầu của review af65dbc được giữ ở
  [receipt_negative_before_fix.log](logs/receipt_negative_before_fix.log).
- Viết [thiết kế](../../../notes/design/confirmation_v1_3.md): luật chọn n, B,
  power/r, collision/near-distance, controls/anchors, khả năng phân biệt, verdict
  → hành động, deviation và blinding trước CF.
- Viết [sampler](../../../experiments/R3R_07_confirmation/sampler.py): measure
  đúng card, rounding exact tie-even, stream riêng/vùng, origin giữ nguyên,
  redraw theo exact key, prefix và deterministic tests bằng root test.
- Xây [inventory](preparation/collision_inventory.json) gồm pilot3stages,
  robustness,58ôv1.2 kể cả R09/R10/R11, audit và8zero-variants bảo thủ.
  Hai control N01/S01 khác fixedplant giữ namespace riêng; generic singlequeue/
  finite toys ghi riêng thay vì tự bịa joint key. Không claim mọi công việc ngoài
  repo đã được cover hoặc8zero-variants đều thực sự đã chạy.
- Viết [adapter/scorer join](../../../experiments/R3R_07_confirmation/score.py),
  [frame gate](../../../experiments/R3R_07_confirmation/frame.py),
  [runner khóa](../../../experiments/R3R_07_confirmation/run.py) và tests từ chối.
  Runner chưa có audited execution backend; không thể chạy engine chỉ bằng đổi flag.
- Bổ sung [coverage numerics](../../../notes/design/v1_3_numerics_coverage_addendum.md)
  cho interior rational rate1/1000; không chỉnh plan/contract/tag cũ.
- Ghi forking log mới nối hash22dòng L3R.6; chỉ replay hai bảng discovery lesson
  đã đưa ra. Không sửa forking log đã khóa. Nguồn scope/versions lưu trong JSON.

## 2. Đã chạy và kiểm

```bash
.venv/bin/python -m experiments.R3R_07_confirmation.prepare --out results/lessons/l3r_7/preparation
.venv/bin/python -m pytest tests/test_r3r_07_confirmation.py -q --junitxml=results/lessons/l3r_7/logs/targeted_tests.xml
.venv/bin/python -m pytest -q --junitxml=results/lessons/l3r_7/logs/full_suite.xml
.venv/bin/python -m experiments.R3R_05_contract.freeze
.venv/bin/python -m experiments.R3R_06_cards.verify_cards
.venv/bin/python -m experiments.R3R_07_confirmation.run --attempt-log-dir results/lessons/l3r_7/refusal_attempts
.venv/bin/python -m experiments.R3R_07_confirmation.run --confirmation-run --attempt-log-dir results/lessons/l3r_7/refusal_attempts
.venv/bin/python -m experiments.R3R_07_confirmation.run --confirmation-run --receipt notes/phases/CF_execution.lock.json --attempt-log-dir results/lessons/l3r_7/refusal_attempts
.venv/bin/python -m experiments.lessons.audit_l3r_7
```

Stdout/stderr được lưu ở `logs/`; lệnh runner trả exit2 **đúng kỳ vọng từ chối**,
không phải experiment thất bại. Ba case thực: thiếu cờ, thiếu receipt, thiếu
tagv1.3.1. Hash/truncatedframe/missingGate/D22/human/realism phủ thêm trong tests.

| Kiểm | Kết quả |
|---|---|
| Targeted mới | **38/38 PASS**,3,66s |
| Full suite | **587/587 PASS**,67,35s |
| Receipt manifest/schema negative cases | **10/10 bị reject đúng** |
| Contract/card hiện hành | **21/21 +10/10 file khớp**,PASS |
| Runner CLI refusal | **3/3 REFUSED**,engine_runs0 |
| Old unpaired discovery format adapter | **88/88 UNRESOLVED**,đúng R1 |

Lần targeted đầu:30PASS/1FAIL do test viết nhầm expected phân bổ stage60/108
thành96/72; sửa expectation theo specs đã khóa, không sửa dữ liệu/science/code
inventory. Giữ [XML lần đầu](logs/targeted_initial_failure.xml). Đây khác với
receipt bug thật đã tái hiện trước sửa. Không tuyên bố mọi test luôn PASS từ đầu.

## 3. Kết quả đo/đếm và tính toán

| Đại lượng | Kết quả | Điều kiện |
|---|---:|---|
| Inventory source records | **308** | có duplicate, sealed design và conservative reserves |
| Reserved v1.3 keys | **245** | không gọi là245newregimes;247 nếu tính cả incompatible projections |
| Sampler test draws | **10.000** | root318700001,PCG64,không engine |
| κ<.2 sau snap | **62,50%** | MV+A; target≈62,87% sau snap,≈63,09% trước snap |
| Power scenario rows | **36** | n3×p+3×p−4; toán giả định |
| R5 / joint R4–R5 rows | **12 /12** | r giả định,không phải r đã đo |
| Discovery replay | **MV16/16;SH57/72** | pilotK40/ref1,đã exposed,không confirmation |
| CF/confirmation root/engine run mới | **0/0/0** | Phase4 chưa mở |

Power một card dưới giả định p+=.7,p−=.2,khôngUNRESOLVED/UNDEFINED:

| n/vùng | P(PASS) |
|---:|---:|
|30|55,2840%|
|40|68,9601%|
|60|83,6469%|

**Không chọn n60 chỉ vì dòng đẹp nhất.** B=48CPU-giờ theoDL-077; numerics chưa có
p95/timing/r nên n thực chưa được chốt.
Ví dụ n40,r+=.02,r−=.05: nhân heuristic chỉ R5 cho65,5709%; tính R4+R5 đầy đủ
cho **56,1573%**, giả định U độc lập nhãn tiềm ẩn và p là conditional MEETS khi
resolved. Không giả định độc lập giữa số U/số MEETS trong cùng sample. Cả hai
không phải power thật của CF; U phụ thuộc effect/undefined sẽ đổi phép tính.

Replay bảng lesson: MV GM/C̄ref từ **1,329633% tới13,406930%**;15SHnon-meets phân
bố λB7/λA7:12,λA7.5:2,λA8:1. Lưới và measure có trọng số khác; không suy p thật.

Arithmetic feasibility: λA7.123,u1.234 → steps(−7643,+4357),degree**12.000**,
maxpilotA-pre**24**; cảref1/ref2 cùng degree. **Chưa chạy** stationary solver ở
điểm này, chưa đo RAM/runtime, không suy runtime tăng500lần. Cần preregistered
calibration phủ interior rate resolution trước sampling; không benchmark trên
mẫu thử trong Ω−.

## 4. Chỉnh cách hiểu lesson

1. Part1§17 phép nhân chỉ xét R5 là heuristic; R4 có thể giảm power thêm.
2. Part3§5.4 INCONCLUSIVE còn do PRECISION/R4, không tự là lỗi validity. Không
   rerun mọi INCONCLUSIVE. Chỉ bug/validity failure xác định theo DL/version mới
   replay toàn batch; U nhiều không tự mở escalation ngoài budget.
3. Identity trên mọi CF row phải kiểm trong lúc evaluate từng row; không thể
   chạy toàn bộ identity “trước batch”. Zero/anchors chạy trước, mọi row qua
   identity rồi mới scorer một lần.
4. Tập corners nhỏ không tự cho biết r/p95 của toàn measure; old timing không
   cover rate1/1000. Bổ sung r/timing coverage và residual risk trong numerics.
5. L∞ width/log bỏ trục ghim nên thêm nearest cùng pinned slice. Không dùng
   metric mô tả để thay contract hoặc bỏ mẫu theo kết quả.

Kiểm chính sách RNG theo [NumPy official](https://numpy.org/doc/stable/reference/random/compatibility.html)
và [PCG64](https://numpy.org/doc/stable/reference/random/bit_generators/pcg64.html):
khóa môi trường và commit actual list khi được cấp; không hứa reproducibility
trên mọi version/build. Đây là technical docs lookup, không literature/novelty review.

## 5. Output ở đâu

| Loại | Đường dẫn |
|---|---|
| Source mới | `experiments/R3R_07_confirmation/*.py` |
| Source sửa | `experiments/R3R_06_cards/verify_cards.py` |
| Tests | `tests/test_r3r_07_confirmation.py` |
| Thiết kế/config chính sách | `notes/design/confirmation_v1_3.md` |
| Coverage numerics | `notes/design/v1_3_numerics_coverage_addendum.md` |
| Inventory | `preparation/collision_inventory.json` |
| Power/risks | `preparation/power.json`, `power.csv`, `r5_risk.csv`, `r4_r5_power.csv` |
| Sampler/numerics arithmetic | `preparation/sampler_verification.json`, `lattice_feasibility.json` |
| Discovery cũ/forking paths | `preparation/*discovery*.csv/json`, `forking_paths.jsonl` |
| Log/tests | `logs/*.log`, `logs/*.xml` |
| Refused invocations | `refusal_attempts/*.json` |
| Intake/lựa chọn/môi trường | `intake.json`, `author_choices.json`, `environment.json` |
| Resource snapshot/logs | `resources/20261029_01/snapshot.json`, `lscpu.log`, `disk.log` |
| Budget vận hành | `notes/design/confirmation_compute_budget_v1.json` (từ root repo) |
| Audit/hash index | `verification.json`, `artifact_index.json` |
| Trạng thái bàn giao | `notes/phases/L3R_7_completion.json` |

Không tạo chart/PDF, finalprereg.json, regimes_cf.json, seedallocation hoặc
executionreceipt. Không sửa src/engine cũ/tagcard/contract/frozen logs; không
papersearch/download hoặc computation outcome CF/R09/R10.

## 6. Kết luận và việc còn chờ

Đã xác nhận tooling phần chuẩn bị, measure ở mức test, guard receipt/runner,
toán power có giả định và adapter không chấm nhầm pilot thiếu refinement.
Chưa xác nhận hypothesis/causal mechanism/realism/novelty hoặc numerical
feasibility trên toàn frame. Đây không phải confirmation thành công hay thất bại.

**Chưa đủ toàn bộ gate L3R.7:** numericsv1.3.1,mức số/timing/r,D22/backend/dry-runB.
Luật n đã được tác giả duyệt và B=48CPU-giờ được chọn theoủyquyềnDL-077;
n/seed/list giữnull. Sau numerics mới áp luật,freezeprereg vàsinhdanh sách mộtlần.
Phase4 còn Gate3R/D22audit/P0-V10/L8; realism chờ disposition. Không tự đóng
Understanding hoặc thay mock review bằng GVHD. L3R.8 học/soạn được; sampling vẫn HOLD.
