# Mốc 2 — N1–N6, thực chạy ngày 23/10/2026

Người phụ trách: **Doan Van Tai**. Đã commit các quyết định tại **27eeed4** trước bản đồ tham số. Chưa hoàn thành lưới v1.1 hoặc mở Gate1; heads-up chỉ lưu nội bộ theo yêu cầu.

| Phép kiểm | Kết quả thực tế |
|---|---|
| Baseline trước thay đổi | 154/154 PASS |
| Test mới / toàn repo | 11/11 / **165/165 PASS** |
| Truth, 300 structural ties | Subtraction sai95; idle identity sai0 |
| M0, 468 structural ties | Subtraction sai182; idle identity sai0 |
| N2, kiểm hữu tỉ hai state | 1.875 ca, 0 vi phạm |
| N2 canonical | L00=59/8, L01=57/8, GM=1/4, GSgivenM1=7/8 packet·slot; model bias=1/2 |
| Stationary references | 5 ca PASS; 3 ca −2/+1 đối chiếu closed form Decimal70 digits |
| Hai mutant dùng cost subtraction | Mỗi mutant bị1 test bắt; FAIL có chủ đích, production source không bị sửa |
| Bản đồ khả thi | 2/10 CERTIFIED_STATIONARY_PROTOTYPE; 8/10 HOLD_CAP |
| Hash audit | 111 historical output files +63 output/snapshot mốc2, 12 source hashes và2 inputs PASS |

Các counts95/182 là fixtures deterministic của repo trong phiên này, không nhận105/114/183/6549 của reviewer là số tự tái lập. Không RNG/seed mới, không Monte Carlo CI. N2 là E0/reference, không là bài kín sách của tác giả.

Rà API sau lần đầu phát hiện mixed Fraction/float có thể làm mất dấu của gap rất nhỏ. Đã lưu regression FAIL trước sửa, chuyển endpoint arithmetic sang Fraction rồi chạy lại11/11 và165/165 PASS. [Lần đầu và source snapshots](../../../results/lessons/v1_1_m2/first_run/development_issue.md) được giữ; [regression log](../../../results/lessons/v1_1_m2/first_run/precision_regression.txt) là FAIL có chủ đích trước bản sửa, không phải test suite cuối.

## Stationary và ngân sách

Điều kiện: μ=10packet/s; B OFF2/ON14; A OFF/ON=λA±6; η=.5 cho9 bộ core; η=.9 tại center cho1 bộ spoke; age1s, Δt=1/120s. A/B modes độc lập, R2 probabilities có interval từ Decimal exp. Tail target của prototype1e−20, infinite-law error target1e−10, posterior target1e−8, cap≤50.000 queue indices.

| λA | κ | η | qA90 được chứng nhận (packet) | Bound law error | Bound posterior error |
|---|---|---|---|---|---|
| 6.5 | .3 | .5 | 419/120≈3.491667 | 1.448625e−16 | 1.504004e−12 |
| 7.5 | .3 | .5 | 281/40=7.025 | 3.393976e−16 | 1.886781e−12 |

8 bộ còn lại cần cap từ52.810 đến1.907.307 theo construction hiện tại, nên giữ HOLD. Đây không phải kết luận plant bất ổn; tất cả10 bộ thỏa stability/ON-crossing/OFF≥0. Chưa đo full-DP runtime hoặc qA90 của8 bộ bị HOLD. B3 còn cần error propagation/strict-sign resolution end-to-end trước khi dùng API mới tính p_switch.

Sai số TV thực đối chiếu closed form ở3 reference cases lần lượt9.649337e−18,1.560062e−17,2.112511e−17; đều nằm trong bounds đã báo. Không gọi finite capped chain là infinite stationary law chính xác. [Giải thích certificate](../../theory/T02_stationary_certificate.md).

N4: qB90≈4.833333,16.133333,48.366667packet tại κ=.3,1,3; q90/κ≈16.111111,16.133333,16.122222. Đây là closed-form float estimates ở finite slot, không equality tuyệt đối. N3 sửa lỗi nguồn: η=.9,ρB=.2 cho postload=.92, nên không đúng rằng luôn≥.95.

## Code, log và số liệu

| Loại | File |
|---|---|
| Source | [idle_gap.py](../../../src/smr/idle_gap.py), [single_observation.py](../../../src/smr/single_observation.py), [stationary.py](../../../src/smr/stationary.py) |
| Test | [N1/N2](../../../tests/test_v1_1_numerics.py), [stationary](../../../tests/test_stationary_certificate.py) |
| Runner và fixture | [runner](../../../experiments/lessons/run_v1_1_m2.py), [numerics](../../../experiments/lessons/v1_1_numerics.py) |
| Config / metrics | [config.json](../../../results/lessons/v1_1_m2/config.json), [results.json](../../../results/lessons/v1_1_m2/results.json), [report.md](../../../results/lessons/v1_1_m2/report.md) |
| Log / JUnit | [run_output.txt](../../../results/lessons/v1_1_m2/run_output.txt), [full_suite.txt](../../../results/lessons/v1_1_m2/full_suite.txt), [full_suite.xml](../../../results/lessons/v1_1_m2/full_suite.xml) |
| N1 / N2 | [structural_ties.csv](../../../results/lessons/v1_1_m2/structural_ties.csv), [N2_lemma.json](../../../results/lessons/v1_1_m2/N2_lemma.json) |
| Stationary | [certificates CSV](../../../results/lessons/v1_1_m2/stationary_certificates.csv), [mass NPZ](../../../results/lessons/v1_1_m2/stationary_reference_masses.npz) |
| Feasibility | [parameters CSV](../../../results/lessons/v1_1_m2/feasibility_parameters.csv), [regions CSV](../../../results/lessons/v1_1_m2/feasible_regions.csv), [scaling CSV](../../../results/lessons/v1_1_m2/quantile_scaling.csv) |
| Plot | [N1_N3_N4_diagnostics.png](../../../results/lessons/v1_1_m2/N1_N3_N4_diagnostics.png) |
| Artifact audit | [script](../verify_v1_1_m2_artifacts.py), [receipt + mutant commands](../../../results/lessons/v1_1_m2/audit/verification_receipt.json), [M1 log](../../../results/lessons/v1_1_m2/audit/mutant_M1.txt), [M0 log](../../../results/lessons/v1_1_m2/audit/mutant_M0.txt), [original manifest](../../../results/lessons/v1_1_m2/artifact_manifest.json) |
| Historical CDE audit | [read-only receipt](../../../results/lessons/v1_1_m2/legacy_CDE_audit.json); active closeout được đối chiếu snapshot nguồn lịch sử, không sửa input hash |
| Quyết định / contract | [mốc2](../../design/decisions_v1_1_m2.md), [25 definitions draft](../../01_definitions_v1_1_draft.md), [claim boundary draft](../../01_claim_boundary_v1_1_draft.md), [closeout HOLD](../../phases/PHASE_1_closeout.md) |
| Tài liệu tham khảo / heads-up | [N2 proof](../../theory/T01_single_observation.md), [primary reading, còn thiếu](../../theory/T03_primary_reading_start.md), [heads-up nháp nội bộ](../../meetings/2026-10-23_headsup.md) |

## Lệnh đã chạy và cách tái lập

Lệnh lần đầu, có historical baseline154 đã lưu trước thay đổi:

```bash
PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_v1_1_m2
.venv/bin/python notes/verification/verify_v1_1_m2_artifacts.py
.venv/bin/python notes/verification/verify_l1_8_cde_artifacts.py --read-only
```

Runner từ chối ghi đè config đã có. Để tính lại với source hiện tại, chọn thư mục trống và copy historical baseline; đây là bằng chứng baseline cũ, không giả lần chạy hiện tại vẫn chỉ có154 test:

```bash
mkdir -p /tmp/v1_1_m2-rerun
cp results/lessons/v1_1_m2/baseline.{json,txt,xml} /tmp/v1_1_m2-rerun/
PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_v1_1_m2 --output-dir /tmp/v1_1_m2-rerun
```

Audit canonical artifacts trong process mới, ghi receipt/mutant logs vào thư mục mới:

```bash
.venv/bin/python notes/verification/verify_v1_1_m2_artifacts.py --output-dir /tmp/v1_1_m2-audit-new
```

Không có CSV grid contrasts, p_switch, A01/A04, human read-back hoặc email đã gửi. Chưa tạo tagv1.1; contract-v1 vẫn trỏ6bb631f. Full PHASE_1 nguồn có SHA bắt đầu47f9a335 chưa có để tự kiểm; ghi đúng provenance từ review. V1/V8/P0-V3/P0-V11 chưa có record, Phase2a mới bắt đầu đọc primary, chưa kết luận novelty. Technical PASS không đổi các gate này.
