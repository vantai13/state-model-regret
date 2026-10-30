# L3R.7 — tạm dừng sau native05, 30/10/2026

Người phụ trách: **Doan Van Tai**. Trạng thái: **PAUSED_BY_AUTHOR / NUMERICS HOLD**.
Tác giả yêu cầu: “bạn chạy xong tạm dừng lại đi, và push hết code lên cho tôi”.
Không mở thêm physical run sau yêu cầu này. Lesson7 **chưa hoàn tất kỹ thuật**.

## A. Đã thực hiện

- Sao lưu full03/preflight1087files; recovery04 khôi phục122receipts, chạy nốt
  ca bị VMstop. Giữ112newCOMPLETED và1UNRESOLVED khi dừng theoDL091, export910files.
- Tạo native interval evaluator cho cùng stored-decimal spectral law, giữ
  certificate/thresholds. Full05 replay cùng9reference/marginal và114calibration
  records,111physicaldesigns; candidate global levels đăng ký hữu hạn tới640/ref8.
- Thêm công cụ export, audit độc lập, đối chiếu mọi parent level có sẵn, CSV và
  hình readiness. Source108gốc/card/contract giữ byte; source graph full05 là122files.
- R3R_12_validation và R3R_13_budget_resume mới là code chuẩn bị có guard, **chưa
  preregistered hoặc thực thi**. Proposal24CPUh chưa adopted; failed native05 bị
  budget-only continuation từ chối. Không có run06/07, CFlist hoặc root mới.

## B. Command và kiểm chứng thực tế

```bash
.venv/bin/python -m pytest -q --junitxml=results/lessons/l3r_7/full_numerics/native05/local_full_suite_701.xml
.venv/bin/python -m pytest -q tests/test_selected_validation_guards.py tests/test_native_budget_continuation.py
.venv/bin/python -m experiments.lessons.compare_native05
.venv/bin/python -m experiments.lessons.plot_native05
```

Cloud đã chạy `experiments.R3R_11_native_population.cloud_pipeline` với
`--prereg experiments/R3R_11_native_population/prereg.json`, source commit
`1fb66807a798260b87adb0d7edabf7cdcf92e77d`, isolated checkout/venv trên n2-standard-8.
Preflight: **693testsPASS**, Python3.13.13/sáu package pins trong prereg. Local sau
khi thêm các guard: **701testsPASS**; post-pause targeted8testsPASS và CLIhelpPASS.
Các test không thay full accuracy audit. Chưa chạy lại test/engine để che lỗi full05.

## C. Kết quả đo được

| Metric | Kết quả |
|---|---:|
| Receipts full05 | 288:286COMPLETED,2UNRESOLVED |
| Legacy anchors / stationary marginals | 3PASS /6PASS |
| Base calibration bundles | 114/114 hoàn tất |
| K80/ref2 readiness | 72/114 |
| K160/ref2 readiness | 80/114 |
| K160/ref4 | 49bundles hoàn tất,41ready;2lỗi;63chưa chạy |
| Global320/4,640/4,640/8 | Chưa chạy |
| CPU full05, kể cả hai job lỗi | 6972.840511CPU-s |
| Sampled peak RSS lớn nhất full05 | 183.69140625MiB |
| Export SHA256 | 2410/2410files khớp |
| Same-level representation comparison | 3948values,0disagreements |
| Current hash checks | contract21/card10/numericalsource122:PASS |
| Selected K*/ref*,n/root/CF | Chưa có/chưa có/chưa cấp/0 |

**Lỗi thực tế:** CAL_CORNER_049 và050 ởstage raise_ref đều trả
`TypeError: Object of type bool is not JSON serializable`. Resource outcome là
WORKER_FAILED, không CPU/RAMlimit. Đã tái hiện `json.dumps` với `numpy.bool(False)`;
nhánh `arithmetic_pass` có thể giữ NumPy scalar khi kiểm arithmetic trảFalse.
Điều này **không chứng minh arithmetic đã đạt**. Sửa transport sau này phải giữ
False và mọi threshold. Chưa triển khai production fix hoặc rerun sau lệnh tạm dừng.
Các fileJSON đã xuất đều hợp lệ; hai job lỗi chưa ghi được levelJSON mới. Raw/log
được giữ nguyên bytes. Vị trí gây lỗi được suy từ source/logger và type reproduction;
chưa có traceback hoặc rerun bổ sung để xác nhận đường runtime cụ thể.

Benchmark component local (law4357terms,3q đãthấy,3repeat/method): median CPU
reference **10.257424295s**, native **0.681294830s**, ratio**15.0558×**. Đây chỉ
component comparison trênWSL2, không whole-engine/cloudspeedup hoặc populationp95.
Guard invocation đầu chưa có committedprereg bịtừchối trước evaluation và đượcgiữ;
lần benchmark đãprereg sau đó PASS. Không chọn bỏ repeat hoặc ca thất bại.

Readiness trên fixed calibration không là tỷ lệ thành công của CF. Chưa có
hypothesis verdict, confidence interval từ CF hoặc evidence mới về realism/novelty.

## D. Artifacts

- [Prereg full05](../../../experiments/R3R_11_native_population/prereg.json).
- [Evaluator](../../../experiments/R3R_10_interval_evaluation/),
  [native driver](../../../experiments/R3R_11_native_population/),
  [validation chưa chạy](../../../experiments/R3R_12_validation/),
  [budget continuation draft](../../../experiments/R3R_13_budget_resume/).
- [Raw full05](../../R3R_population_numerics/20261030_05/),
  [GCP test log](full_numerics/attempt05/full_suite.log),
  [local701log](full_numerics/native05/local_full_suite_701.log).
- [Metrics CSV](full_numerics/native05/report/metrics.csv),
  [gains calibration CSV](full_numerics/native05/report/gains_calibration_only.csv),
  [đối chiếu cũ/mới](full_numerics/native05/report/prior_representation_comparison.csv).
- [Readiness PNG](full_numerics/native05/report/numerical_readiness.png) /
  [SVG](full_numerics/native05/report/numerical_readiness.svg).
- [Run verification](full_numerics/native05/report/verification.json),
  [pause verification](full_numerics/native05/pause_verification.json),
  [serialization diagnosis](full_numerics/native05/serialization_diagnosis.json),
  [infrastructure](full_numerics/native05/final_infrastructure.json).

Redundant tar/scp transfer copies ở `~/.cache/state-model-regret/`; authoritative
raw/log/code/CSV/chart được giữ trong repo. Không có PDF mới hoặc paper search.

## E. Kết luận và điểm tiếp tục

Đã xác nhận source integrity, test snapshots, transfer integrity và3948same-level
comparisons trong combined arithmetic enclosures; không coi đó là global numericsPASS.
Native05 dừng đúng với hai lỗiserialize, trước khi có numerical selection/timingp95.

**Công việc tạm dừng.** Đã kiểm không còn owned research workers/controllers.
TemporarySSHrule đã xóa và APIxácnhận; **VM vẫn RUNNING**, không start/resize/stopVM.
Không có v1.3.1tag/receipt,n,confirmationroot/CF; Phase4HOLD, human/UnderstandingOPEN.

Khi tác giả yêu cầu tiếp tục: sửa boolserialization với regression tái hiệnFalse,
version/prereg mới và full registered replay theo deviation policy; tiếp tục accuracy
và đo fixedcost nếu đủ điều kiện. Chỉ sau closure thật mới freeze, dry-runB,
áp luật n, cấp root và sinh CFlist một lần. Không dùng budget-only resume cho lỗi này.
