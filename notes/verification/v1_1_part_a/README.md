# Phần A — solver, B2–B4 và kiểm readiness B5

Người phụ trách: **Doan Van Tai** · 23/10/2026.

**Kết quả: HOLD / NARROW REQUIRED.** Solver và code được kiểm chứng; cả hai lưới không đạt quy tắc chấp nhận. Initial **8/22**, sau đúng một redesign **11/22**, cần **15/22**. Không khóa calibration, không nâng draft thành contract chính thức và không tạo tagv1.1. Giữ đủ28 ô+6 reserve, không xóa ôout.

| Phép kiểm | Kết quả |
|---|---|
| Baseline → full suite |165 → **177/177 PASS**, 12 tests mới|
| Stationary certificate original |**20/20 PASS**, 10 bộ ×dt1/120 và1/240|
| Stationary sau một redesign |**20/20 PASS**, giữ target law1e−10/posterior1e−8|
| Max law / posterior error |**1.02853e−29 / 4.000001e−16**|
| So solver cũ |10/10 comparisons PASS, allowance array evaluation báo riêng|
| D/ĐK1/budget |34ô mỗi thiết kế,272 queue-support artifacts audit;2 SD+2 conservation controls|
| B3 |88 sign-only evaluations, unresolved mass0; không reserve screen hoặc margin/Lstar outputs|
| Max p_sw interval width |**5.77094e−13**|
| Kiểm D queue B độc lập bằng code cũ |136 comparisons, maxTV **1.31666e−14**|
| Sáu consistency checks |4PASS,1PARTIAL(full source),1FAIL(grid/calibration)|

Cấu hình: μ10packet/s, age1s, A backgroundλA±6, B OFF2/ON14; κ.3/1/3, ηcore.5/spoke.9. Lưới đầuλA6.5/7.5/8.5, một redesign7/7.2/8.1. Observation vật lý lấy quantile coarse và giữ cố định; finer prior được tính lại, Hfine=2Hcoarse. Đây là numerical verification trong plant lý tưởng, không Monte Carlo/CI lấy mẫu, không hypothesis hoặc network validation.

Source hướng dẫn đề nghị nâng cap bằng sparse. Sparse đã thử và ghi cả trường hợp law bound2.293e−10 không đạt; phương án phổ sau đó giữ nguyên toàn bộ10 bộ ban đầu, không phải bỏκ3 hoặc λ8.5 vì RAM. Root finder chỉ tìm approximation; interval balance/boundary/normalization, independent tail và Bellman bound mới là certificate. [Derivation T04](../../theory/T04_spectral_stationary.md).

Mutant gamma bị bắt. Audit bổ sung native cost-subtraction mutant lọt test dyadic ban đầu; giữ record đó, thêm keep.97 vào cùng test bảo toàn rồi mutant bị bắt. Full suite sau bổ sung vẫn177/177PASS. [Development note](../../../results/lessons/v1_1_a6/mutation_development_note.md), [mutant đầu](../../../results/lessons/v1_1_a6/native_subtraction_mutant_first_attempt.txt), [mutant cuối](../../../results/lessons/v1_1_a6/native_subtraction_mutant.txt). Không thay production kernel hoặc tính lại candidate outcomes để có kết quả thuận lợi.

## Kết quả và artifacts

| Loại | Đường dẫn |
|---|---|
| Báo cáo đầy đủ, gồm22 hàng so p_sw | [report.md](../../../results/lessons/v1_1_a6/report.md) |
| Metrics / cấu hình / sáu checks | [results.json](../../../results/lessons/v1_1_a6/results.json), [config.json](../../../results/lessons/v1_1_a6/config.json), [readiness.json](../../../results/lessons/v1_1_a6/readiness.json) |
| Biểu đồ / CSV so sánh | [part_A_diagnostics.png](../../../results/lessons/v1_1_a6/part_A_diagnostics.png), [screen_comparison.csv](../../../results/lessons/v1_1_a6/screen_comparison.csv) |
| Prior original / redesign | [certificates.csv original](../../../results/lessons/v1_1_a1/certificates.csv), [redesign](../../../results/lessons/v1_1_a1_redesign/certificates.csv) |
| Đối chiếu solver v1 / sparse trial | [v1_comparisons.csv](../../../results/lessons/v1_1_a1/v1_comparisons.csv), [sparse_trials.json](../../../results/lessons/v1_1_a1/sparse_trials.json) |
| Candidate nguyên bản / redesign | [initial JSON](../../design/grid_v1_1_candidate.json), [redesign JSON](../../design/grid_v1_1_redesign_candidate.json) |
| D / ĐK1 / budget initial | [supports.json](../../../results/lessons/v1_1_a2/supports.json), [labels.csv](../../../results/lessons/v1_1_a2/labels.csv), [budget.csv](../../../results/lessons/v1_1_a2/budget.csv); NPZ riêng từng queue trong cùng thư mục |
| D / ĐK1 / budget redesign | [supports.json](../../../results/lessons/v1_1_a2_redesign/supports.json), [labels.csv](../../../results/lessons/v1_1_a2_redesign/labels.csv), [budget.csv](../../../results/lessons/v1_1_a2_redesign/budget.csv) |
| Screen initial / redesign | [screen.csv initial](../../../results/lessons/v1_1_a4/screen.csv), [redesign](../../../results/lessons/v1_1_a4_redesign/screen.csv) |
| Log screen | [initial](../../../results/lessons/v1_1_a4/run_output.txt), [redesign](../../../results/lessons/v1_1_a4_redesign/run_output.txt) |
| Quyết định B4 | [selection.json](../../../results/lessons/v1_1_a5/selection.json), [grid decision record](../../design/grid_v1_1.md) |
| Full test log / XML | [full_suite.txt](../../../results/lessons/v1_1_a6/full_suite.txt), [full_suite.xml](../../../results/lessons/v1_1_a6/full_suite.xml) |
| D/dominance audit | [factorized_law_audit.json](../../../results/lessons/v1_1_a6/factorized_law_audit.json), [dominance_mass.csv](../../../results/lessons/v1_1_a6/dominance_mass.csv) |
| Packaging | [packaging_check.json](../../../results/lessons/v1_1_a6/packaging_check.json), [wheel_build.txt](../../../results/lessons/v1_1_a6/wheel_build.txt); native CPP có trong wheel |
| Draft đã cập nhật | [definitions](../../01_definitions_v1_1_draft.md), [claim boundary](../../01_claim_boundary_v1_1_draft.md), [brief](../../00_research_brief_v1_1_draft.md) |
| Trạng thái / nguồn | [closeout](../../phases/PHASE_1_closeout.md), [protocol trước screen](../../design/v1_1_A_protocol.md), [DL-032…037](../../02_decision_log.md), [exposure](../../00_exposure_register.md) |
| Heads-up | [Nháp trong repo, chưa gửi](../../meetings/2026-10-23_headsup.md) |

## Source và chạy lại

- [stationary_v2.py](../../../src/smr/stationary_v2.py): sparse trial và longdouble rounding bounds.
- [stationary_spectral.py](../../../src/smr/stationary_spectral.py): approximation/certificate và quantile/posterior intervals.
- [gap_screen.py](../../../src/smr/gap_screen.py), [idle_backward.cpp](../../../src/smr/native/idle_backward.cpp): weighted idle DP và sign-probability interval.
- [test_stationary_spectral.py](../../../tests/test_stationary_spectral.py), [test_gap_screen.py](../../../tests/test_gap_screen.py):12 test functions mới.
- [A1 runner](../../../experiments/lessons/run_v1_1_a1.py), [A1 redesign](../../../experiments/lessons/run_v1_1_a1_redesign.py), [A2](../../../experiments/lessons/run_v1_1_a2.py), [A4](../../../experiments/lessons/run_v1_1_a4.py), [A5](../../../experiments/lessons/run_v1_1_a5.py).

Cần Python/dependencies trong pyproject và compiler C++17 (`g++`). Native library build trong temporary directory theo hash CPP, không commit binary. Wheel bình thường đã build và kiểm CPP inclusion; thử `--no-build-isolation` đầu không chạy được do môi trường thiếu setuptools.build_meta, log được giữ. Không phải lỗi numerical experiment.

Lệnh đã thực thi và cấu hình nằm trong report/config. Runners không ghi đè dữ liệu cũ; A4 redesign kiểm candidate/source hashes trước resume. Tái lập A1 redesign hoặc audit có thể chọn output mới:

```bash
PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_v1_1_a1_redesign --output-dir /tmp/part-a-prior-replay-new
.venv/bin/python notes/verification/verify_v1_1_part_a.py --output-dir /tmp/part-a-audit-new
PYTHONPATH=src:. .venv/bin/python notes/verification/verify_v1_1_factorized_law.py
```

Hai thiết kế đầy đủ cần worktree/clone với output trống; initial exposure/commits trong history giữ nguyên. Source hashes cho screen redesign và report được lưu; immutable old artifact manifests đã audit, không sửa hash cũ để khớp tài liệu active mới.

## Chronology và giới hạn

`27eeed4 → e3161cf(C0) → 9f0783e(C1) → 571d4cf(C2) → c7ddef3(C3) → 6b87256(C4) → 19d03cc(redesign prereg) → 3fe81d2(candidate mới) → ae876ab(screen mới) → 8126ef9(C5 rejected)`.

V1/V8/P0-V3/P0-V11 đã author-attested trực tiếp, không lưu artifact, chưa independent validation. V9/P0-V10 còn thiếu; P0-V10 chặnPhase4. Full Final Review/PHASE_1 source chưa được tự mở nên check4PARTIAL. Không tạo full SHA/câu trích từ digest rút gọn.

B5 đã kiểm readiness và giữ draft do B4fail. Không tạo file contract chính thức hoặc tagv1.1 cho grid không được chấp nhận. Calibration, A01/A04, convergence cuối, contrasts và hypothesis vẫn chưa chạy. Cần protocol NARROW/REFORMULATE mới trước nghiên cứu tiếp; không lượtλ thứ hai hoặc bỏout trong protocol đã kết thúc.
