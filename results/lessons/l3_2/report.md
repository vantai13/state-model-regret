# L3.2 — engine exact cho bốn ô: báo cáo thực chạy

Người phụ trách: **Doan Van Tai** · 27/10/2026. AI triển khai bốn phần lesson;
đây là verification kỹ thuật, chưa là Understanding/ownership của tác giả.

## A. Đã thực hiện

Engine mới ở [experiments/A00_engine](../../../experiments/A00_engine/): core Side/cut/aggregate,
toy Fraction, native side_table, mean-path vectorized, D22, per-quantity numeric enclosures,
quantile intervals, adapter ba schema, evaluate_cell và guard. Tất cả dùng chung aggregate,
không dựng tích D_A×D_B; chỉ checker toy được phép liệt kê cặp.
Có [T05 AI hỗ trợ + phần tác giả còn trống](../../../notes/theory/T05_exact_engine.md).
Chưa promote source vì T05 author-owned/author-attested còn OPEN. Src/kernel gốc giữ nguyên.

Đính chính lesson: cells.py đã có; baseline 228; idle tính trước update q; guard kiểm
commit A05-F thật. E3/E6 giữ là arrival-law toys ngoài D7; D7 H=1 với mode biết trước
phải cho M0=M1. Float cut mẫu thiếu value/probability/conditional-posterior/rounding errors,
nên đã bổ sung. Bốn lỗi ở lượt native/float đầu đã sửa; [record](development_checks.json).
Nháp đếm migration 48 là lỗi số học: 8×2×2=32; không đổi IDs/ref, giữ bản expected gốc.

## B. Commands và trạng thái

```bash
.venv/bin/python -m pytest tests/test_engine_core.py tests/test_engine_extended.py tests/test_engine_float.py tests/test_engine_physics.py tests/test_engine_refinement.py tests/test_engine_guard.py tests/test_cells_migration.py -q --junitxml=results/lessons/l3_2/engine_pytest.xml > results/lessons/l3_2/engine_pytest.log 2>&1
.venv/bin/python -m experiments.A00_engine.run_mutants > results/lessons/l3_2/mutation_run.log 2>&1
.venv/bin/python -m pytest -q --junitxml=results/lessons/l3_2/full_pytest.xml > results/lessons/l3_2/full_pytest.log 2>&1
.venv/bin/python -m experiments.A00_engine.report_verification > results/lessons/l3_2/verification.log 2>&1
git diff --check
```

Engine tests **72 PASS** (12.331 s), toàn repo
**300 PASS** (56.947 s), baseline trước thay đổi **228 PASS**
tại commit f465db1 ([log trước](../l3_1/part3/full_pytest.log)). Không failures/errors/skips
ở lượt cuối. Mutation **11/11 KILLED**, không tính collection/setup error là kill.
M4 tương đương trong Fraction; bị bắt bằng float conservation tại backlog lớn.
Raw traceback logs/XML giữ nguyên byte; [.gitattributes](../../../.gitattributes) chỉ bỏ
kiểm blank-at-eol cho hai pattern mutant output vì pytest tự in trailing spaces.
Source vẫn kiểm whitespace bình thường; xem development_checks.json.

Đã kiểm: 300 ledger ngẫu nhiên (seed 20261027), 400 plant synthetic (20261028),
2.000 key-perturbation trials (20261029), 40 trials biến đổi probability/value/D22 (20261030).
Các số case là số vòng thực trong test, không phải 300/400 pytest test cases riêng.
Ba loại kiểm được tách: identity báo cáo; bất đẳng thức (oracle/Jensen/sign); đường độc lập
(brute, Fraction DP/idle, native/reference, golden). Identity không được tính là validation.

## C. Số đo

Golden canonical: H=2, dt=1, c=3 packet/slot, u=2; A nền1, B nền0/5,
Pkeep=1/2; D theo golden Phase1. Cost/contrast: packet·s trong toy time scale.
E7 là ledger offsets với K=0, không phải cost queue tuyệt đối.

| Toy | L00 | L01 | L10 | L11 | GS | GM | Γ | F | V | E abs I_delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Canonical | 7.375 | 7.125 | 6.25 | 6.25 | 1.125 | .25 | -.25 | .375 | .75 | .25 |
| E7 offsets | -.25 | -.25 | -.875 | -1 | .625 | 0 | .125 | .375 | .25 | 1.125 |

E2: GS=1.5, GM=1, Γ=−1. E5: GS=−1, GM=0, Γ=1.5. Các giá trị tính thật bằng Fraction.
Canonical/native khớp và từng khoảng chứa đáp án Fraction; cận từng đại lượng ở CSV/JSON.
Không gọi e_num là CI, không suy dt-convergence hoặc validity trên grid từ toy.

| L1.8B toy | Bản cũ GS | Engine mới GS | Cref cũ | Cref mới |
|---|---:|---:|---:|---:|
| ref1, dt=1 s | 0.9296875 | 0.9296875 | 6.390625 | 6.390625 |
| ref128, dt=1/128 s | 0.30715163723 | 0.30715163723 | 5.93310673775 | 5.93310673775 |

Đủ 8 mức ref1…128, max absolute contrast difference=3.46944695e-18
packet·s. Đây là tái lập teaching cell L1.8B; không phải A01/final dt của v1.2.

Migration: 58 record metadata; 32 D-only cases trên 8 IDs đã khai báo, A/B, ref1/2.
Probability difference=0, support mismatch=0; không D held-out. Regression cũ còn rerun D-only
L3.1 và screen M31; không gọi những phép đó là “chỉ toy”. Không J/gap/contrast grid mới.

## D. Output và source

- Tài liệu: [README](../../../README.md), [AGENTS](../../../AGENTS.md),
  [DL-045/046](../../../notes/02_decision_log.md), [Phase3](../../../notes/phases/PHASE_3.md),
  [exposure](../../../notes/00_exposure_register.md), [progress](../../../notes/00_progress_log.md),
  [index](../../../notes/03_experiment_index.md), [T05](../../../notes/theory/T05_exact_engine.md).
- [Config, seeds, source hashes](config.json), [expected trước code](expected_before_code.json).
- [Golden CSV](golden_results.csv), [JSON](golden_results.json), [canonical numeric](canonical_numeric.json),
  [per-quantity enclosures](canonical_enclosures.csv), [L1.8B old/new](L18B_refinement.csv),
  [D-only old/new](D_migration.csv), [verification JSON](verification.json).
- Logs: [engine](engine_pytest.log), [full](full_pytest.log), [mutation](mutation_run.log),
  [mỗi mutant + test bắt lỗi](mutants/summary.json), [verification](verification.log).
- XML: [engine](engine_pytest.xml), [full](full_pytest.xml); mỗi mutant có log/XML riêng.
- Source/test: [engine](../../../experiments/A00_engine/), [core tests](../../../tests/test_engine_core.py),
  [checker độc lập](../../../tests/engine_checker.py), [physics](../../../tests/test_engine_physics.py),
  [intervals](../../../tests/test_engine_float.py), [refinement](../../../tests/test_engine_refinement.py),
  [guard](../../../tests/test_engine_guard.py), [migration](../../../tests/test_cells_migration.py),
  [extended golden](../../../tests/test_engine_extended.py).
Không tạo plot/PDF, output A01/A04/A05, prediction card hay record người đọc.

## E. Kết luận

**Technical verification PASS** trong phạm vi đã kiểm. Engine v1 thực nghiệm có đủ
giao diện để chuẩn bị A01; chưa đo/verify grid, không kết luận hypothesis/novelty/network gain.
Bounds là enclosure có điều kiện theo input/kernel và giả định arithmetic finite; test containment
không thay một proof độc lập toàn bộ hệ sai số. Guard kiểm commit sạch/thứ tự, không kiểm nội dung
card hoặc thay runner thực thi các điều kiện V9/A01. Low-level synthetic APIs không là security boundary.

Chưa tính EVPI_w/flip mass 2D. T05 tác giả, ownership/read-back còn OPEN nên code giữ experiments;
không nhận Understanding PASS. L3.3 card chưa commit; A01/A04/A05 chưa chạy. V9 giữ điều kiện(c),
A04 chờ; P0-V10/L8 còn mở, Phase4 HOLD. Có thể học/soạn L3.3 tiếp theo.
