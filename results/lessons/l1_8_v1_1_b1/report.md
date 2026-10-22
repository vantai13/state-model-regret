# B1 v1.1 — kết quả tích hợp/kiểm chứng

Người thực hiện: **Doan Van Tai** · **23/10/2026**, Asia/Saigon. Ngày nguồn patch22/10 và attribution được giữ nguyên; không nhận đây là bài kín sách/V11 hoặc independent review.

- Baseline trước áp patch: **146/146 PASS**.
- Dominance tests: **8/8 PASS**; toàn repo **154/154 PASS**.
- Vét cạn **12,672 state-parameter configurations**, **116,352 cặp path**. Bốn điều kiện SD1/SD2/WD1/WD2:0 vi phạm path-wise và0 vi phạm dấu M0.
- Gồm9.216 ca nguồn +3.456 ca bổ sung low-arrival/H1. Ca nguồn không kích hoạt SD2/WD2; coverage assertion đã phát hiện lỗi này ở lần đầu, dù154 tests PASS. Log/config/JUnit và coverage counts được giữ trong first_run/. Không nới tiêu chí coverage để PASS.
- **40,068 path Switch thắng**:0 vi phạm điều kiện cần; conservation **1,672 states**,0 vi phạm.
- Phân loại v1 từ **6,776 rows D đã lưu**, không tính J: **13 SD-cell,2 conservation-cell,13 candidate**. SD=M01–M12,S01; calibration M01/M02/M10 đều SD.
- Reserve v1:6/12 tọa độ held-out thỏa SD2 từ tham số A;4 extrapolation còn lại không SD2. Không sinh D reserve, không tính action values.
- WD/tie toy: truth J(Stay)=54.5,J(Switch)=54; M0=54/54 → chọn Stay, regret0.5 packet·time-unit. WD không phải zero control.
- Ba mutant có chủ đích: **3/3 KILLED** bằng assertion của reference tests; chạy trong memory, không tạo mutant patch/file hoặc sửa source thật.
- Guards mới bắt NaN/Inf, empty/zero support; state probability10⁻⁴⁰ không bị bỏ bởi tolerance. No RNG, no seed mới.

## Đã sửa gì

Áp patch sau git apply --check. Giữ provenance nguồn, thêm người tích hợp/ngày thực. Code mới dominance.py; tám điều kiện/proofs và DL-026…028; status hiện tại HOLD A01/A04 trên grid v1. Gia cố phân loại ô bằng support certificates thay vì chỉ so mass≈1.

Sửa các claim quá mạnh: p_sw trong khoảng không đủ chứng minh State gain dương (ties); ngoài khoảng nhưng chưa0/1 là oracle-lệch. Fraction(float_P) không tự là exact law R2. Solver stationary A sau này cần tail/error control, không chỉ finite residual. PHASE_1 full chưa có nên xung đột V11 là reported/source comparison pending, không tự xác minh trích dẫn.

## Phạm vi đã thực hiện và còn chờ

**B1 hoàn thành phần tích hợp/verification; bản điều kiện vẫn DRAFT để tác giả review.** Chưa chọn số lưới v1.1, chưa có grid_v1_1.md/json, chưa p_switch/ĐK2, chưa calibration/reserve mới hoặc A01; không tag contract-v1.1. Bảy lựa chọn §11, dt screen và cách xác nhận dấu R2 phải chốt/commit trước B3. Không gửi heads-up/email, không tạo human feedback, không thay bài tự làm.

v1 và snapshot A/B/CDE giữ byte; không di chuyển tag contract-v1 hoặc v0. Support/regime v1 được dùng lại là exposed verification. Random200paths/ô của mock review là exposure do attachment báo, không có seed/log để tái lập; không tính nó là kiểm PASS trong phiên này. G1 giữ nguyên, P0-V3/V10/V11 còn OPEN.

## Commands và files

```bash
git apply --check .git/l1_8_b1_source.patch
git apply .git/l1_8_b1_source.patch
PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_v1_1_b1
```

Runner gọi pytest thật (command,returncode,Junit trong results.json). Baseline được chạy trước áp patch; lesson/full tests sau áp patch và sửa integration. CSV ghi scalar/Fraction, no Monte Carlo CI. Đơn vị test toy là packet×teaching time unit; không quy thành physicalms của R2.

| File | Nội dung |
|---|---|
| config.json,results.json | SHA2564inputs, source hashes, tag/base, actual commands/metrics |
| baseline.json/.txt/.xml,lesson.txt/.xml,full_suite.txt/.xml | Trước/sau và JUnit thực |
| exhaustive_conditions.csv | Đếm state từng điều kiện, vi phạm path/M0 |
| v1_classification.csv | 28 old cells, mass/support certificates/label |
| v1_reserve_parameters.csv | 16 old coordinates, chỉ kiểm SD2 tham số; no D |
| wd_tie_example.csv | J và M0 hai action của teaching counterexample |
| mutation_checks.csv | Ba lỗi được cài trong memory và test bắt lỗi |
| artifact_checks.json,artifact_manifest.json | Read-back CSV/JUnit/hashes và frozen snapshots |
| first_run/ | Lần runner FAIL coverage: log/config/JUnit và phân tích nguyên nhân, giữ nguyên byte |
| run_output.txt,report.md | Log và báo cáo hiển thị kết quả |

Source src/smr/dominance.py; tests/test_dominance_v1_1.py; conditions notes/design/design_conditions_v1_1.md; decisions/exposure ở notes/02_decision_log.md và notes/00_exposure_register.md. Không tạo biểu đồ: đây là theorem/control verification và bản điều kiện B1, chưa có kết quả grid v1.1 để vẽ.
