# L1.8 Part A — địa chỉ kết quả

Người thực hiện: **Doan Van Tai** · **22/10/2026**.

- [Report](../../../results/lessons/l1_8_a/report.md),[results](../../../results/lessons/l1_8_a/results.json),[config](../../../results/lessons/l1_8_a/config.json).
- [Hai thẻ](../../../results/lessons/l1_8_a/anchor_cards.csv),[refinements](../../../results/lessons/l1_8_a/anchor_refinements.csv),[R1/R2](../../../results/lessons/l1_8_a/persistence_comparison.csv).
- [E1 convergence](../../../results/lessons/l1_8_a/fluid_convergence.csv),[96 boundary cases](../../../results/lessons/l1_8_a/boundary_grid.csv),[900 round trips](../../../results/lessons/l1_8_a/round_trip_grid.csv).
- [Log runner](../../../results/lessons/l1_8_a/run_output.txt),[full suite](../../../results/lessons/l1_8_a/full_suite.txt),[JUnit](../../../results/lessons/l1_8_a/full_suite.xml).
- [PNG](../../../results/lessons/l1_8_a/slot_and_persistence.png),[artifact checks](../../../results/lessons/l1_8_a/artifact_checks.json),[manifest](../../../results/lessons/l1_8_a/artifact_manifest.json).
- [Audit đọc lại artifact](../../../results/lessons/l1_8_a/independent_artifact_audit.json): kiểm 27 file manifest ban đầu, 11 source hashes; đối chiếu 96 diện tích bằng nguyên hàm positive-part, 900 round trips và 6 dòng R1/R2 bằng Decimal 60 chữ số. PASS; đây là kiểm kỹ thuật, chưa là scientific independent review.
- [Experiment card](../../lessons/L1.8A_experiment_card.md),[model/conversion spec](../../lessons/L1.8A_slot_model_spec.md).

```bash
.venv/bin/python -m experiments.lessons.run_l1_8_a
.venv/bin/python notes/verification/verify_l1_8_a_artifacts.py
.venv/bin/python -m experiments.lessons.run_l1_8_a --output-dir /tmp/l1_8_a-rerun
.venv/bin/python notes/verification/verify_l1_8_a_artifacts.py --output-dir /tmp/l1_8_a-rerun
```

Source: `experiments/lessons/l1_8_slots.py`,`l1_8_reference.py`,`run_l1_8_a.py`.
Tests: `tests/test_l1_8_slots.py` (4core),`test_l1_8_boundaries.py` (10bổ sung).
Lần chạy cuối14/14 mới và111/111 toàn repo PASS. Không RNG/seed/Monte Carlo.

Preflight13 PASS,thêm1 kiểm candidate-coordinate scaling rồi full111 PASS.
Sau review làm rõ fields requested/represented age,format Fraction qua float cho
Python3.10,và làm tròn expected literal mean-run thành8decimals với tolerance rõ;
đã rerun111 PASS,không thay metric/config/dung sai thí nghiệm. Giữ first-run log/config
vàdevelopment_note.json. Không có baseline test failure.

Bốn core semigroup/correlation/anchor/rejection chưa chứng nhận full queue dt-invariance.
Chưa làm PartB–E hoặcPhase3 A01,không khóa contract-v1/Δt cuối cùng. T_mode b=.1s
vàrho_post=.9 là minh hoạ,anchor a chưa khai báo hai mục đó. 43% của nguồn chưa tái lập.
G1,V3/V10/V11 vàHOLDPhase4 giữ nguyên; các thẻ không thay bài kín sách của tác giả.
