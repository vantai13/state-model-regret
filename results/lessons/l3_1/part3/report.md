# L3.1 Part 3 — kết quả triển khai và kiểm chứng

Người phụ trách: **Doan Van Tai** · 27/10/2026. AI thực hiện theo lesson được cung cấp;
không ghi thay trải nghiệm tự học hoặc phản hồi của người thật.

## A. Đã thực hiện

- DL-044 có bốn dòng trạng thái: V9, người đọc, tự viết, provenance; làm rõ P0-V10
  đọc v1.2 và hai nghĩa V9. Giữ điều kiện V9(c); chưa gửi GVHD, A04 chờ.
- Tạo PHASE_3 từ phạm vi lesson, con trỏ README ≤15 dòng, experiment index và bảng
  Keep/Reference/Archive/Rebuild. Bản plan PHASE_3 v2.0 đầy đủ chưa có trong workspace;
  không nhận đã đối chiếu bảng gốc. Bổ sung reader packet 30–45 phút/sáu câu.
- Chuyển nguyên nội dung README cũ sang progress log, chỉ sửa đích link. History giữ nguyên.
- Rebuild lattice/law_for/queue_D/make_cell vào src/smr/cells.py; body bốn hàm khớp AST,
  ba file experiments gốc giữ nguyên byte. Module mới không import experiments.
- Contract D1–D25 và grid khớp nguyên byte tag contract-v1.2; claims, thresholds, closeouts,
  forecast, heads-up cũ và nhãn PC không đổi. Không đọc/tìm paper trong phiên này.

## B. Command và trạng thái thực chạy

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m pytest tests/test_v1_2_cells.py -q --junitxml=results/lessons/l3_1/part3/migration_pytest.xml > results/lessons/l3_1/part3/migration_pytest.log 2>&1
.venv/bin/python -m pytest -q --junitxml=results/lessons/l3_1/part3/full_pytest.xml > results/lessons/l3_1/part3/full_pytest.log 2>&1
.venv/bin/python -m experiments.lessons.verify_l3_1_part3 > results/lessons/l3_1/part3/verification.log 2>&1
git diff --check
```

Baseline **202 PASS**, 26,46 s. Test migration **26 PASS**;
full regression **228 PASS**; failures/errors/skips đều **0**.
Verification **PASS**; log và XML là output thực. Không chạy A01/A04/A05 hoặc simulation
outcome Phase 3. Các tests cũ có toy outcomes và design screen M31, không là experiment mới.
Kiểm whitespace trên bản lesson gốc ban đầu FAIL vì CRLF; snapshot lưu đã chuẩn hóa LF,
giữ SHA-256 gốc và kiểm tái tạo CRLF đúng byte. Kiểm cuối PASS.

## C. Số đo thực tế

Điều kiện: main-cell construction toàn bộ 38 ô; D trên M01/M09/M22/N01, queue A/B,
ref 1/2/4 (dt=1/120,1/240,1/480 s), age=1 s, capacity=10 packet/s.
Deterministic spectral law + finite propagation; không random seed/Monte Carlo/CI thống kê.

| Kiểm | Bản gốc | Bản Rebuild / so sánh |
|---|---|---|
| Main constructors | 38 | 38 khớp; 0 mismatch |
| D tách queue | 24 trường hợp | 24 khớp |
| Sai lệch probability lớn nhất | Reference | 0.0 |
| Support mismatch | Reference | 0 |
| Cận sai số D lớn nhất (probability) | 5.56947445e-14 | 5.56947445e-14 |
| Residual normalization lớn nhất | — | 4.33680869e-19 |
| N01 A, q=0, mode OFF/ON | Analytic 1/2,1/2 | 1/2,1/2 |
| Tests toàn repo | 202 PASS trước đổi | 228 PASS sau đổi |

So sánh implementation với reference giữ nguyên là bằng chứng migration, không phải
validation độc lập toàn bộ plant. Invariant N01 bổ sung một kiểm analytic riêng.
Không có số baseline/new-method regret để báo: Part 3 không đo đại lượng nghiên cứu.

## D. File lưu

- Source: [cells.py](../../../../src/smr/cells.py), [tests](../../../../tests/test_v1_2_cells.py),
  [verification runner](../../../../experiments/lessons/verify_l3_1_part3.py).
- Điều kiện và index: [PHASE_3](../../../../notes/phases/PHASE_3.md),
  [DL-044](../../../../notes/02_decision_log.md#dl-044--mở-phase-3-điều-kiện-còn-mở-và-bản-hiện-hành-2026-10-27),
  [README](../../../../README.md), [index](../../../../notes/03_experiment_index.md),
  [progress log](../../../../notes/00_progress_log.md),
  [reader packet](../../../../notes/meetings/phase2_reader_packet.md),
  [exposure](../../../../notes/00_exposure_register.md).
- [Config và SHA nguồn](config.json), [lesson chuẩn hóa LF](lesson_source.txt),
  [số đo từng trường hợp](D_comparison.csv), [verification JSON](verification.json).
- Log: [baseline](baseline_pytest.log), [migration](migration_pytest.log),
  [full regression](full_pytest.log), [verification](verification.log).
- XML: [migration](migration_pytest.xml), [full](full_pytest.xml).
Không tạo biểu đồ, PDF, output A01/A04/A05, record buổi đọc hoặc xác nhận đã gửi GVHD.

## E. Kết luận và tự kiểm kỹ thuật

**Xác nhận:** con trỏ đúng phiên bản; four-function migration giữ nguyên behavior trên
miền đã kiểm; tests PASS. Chưa xác nhận engine L3.2 tích hợp, hypothesis/novelty,
Understanding của tác giả, V9, P0-V10 hoặc L8. Phase 4 vẫn HOLD.

Bốn câu tự kiểm được AI trả lời về kỹ thuật (không là tác giả tự làm): (1) εR đổi
nhãn, D13 đổi J/oracle/regret nên phải tính lại. (2) Bạn học giảm ER3 nhưng không
loại ER8 từ người định hướng đề tài. (3) Toy tests có thể nhất quán với plant sai;
cần kiểm D và con trỏ contract. (4) Lý do DL-038 đo ownership, card đo validity của
dự đoán trước outcome nên AI có thể hỗ trợ soạn card với provenance trung thực.

Bài tự chấm năm dòng: **chưa có lời tác giả**. Tác động nếu đổi đã phân tích: D13,
D20, D21 và luật chọn lưới cần tính/chọn lại; εR chủ yếu relabel và ghi post hoc.
Không tự kết luận tác giả bảo vệ được dòng nào. Tác giả vẫn cần viết lý do DL-038
và §1–2 closeouts; người thật vẫn cần đọc. Có thể học L3.2 ngay; trước A01 phải
commit L3.3, trước A04 cần record V9 theo điều kiện hiện có.
