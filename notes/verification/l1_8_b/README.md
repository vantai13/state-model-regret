# L1.8 Part B — địa chỉ kết quả và phạm vi

Người thực hiện: **Doan Van Tai** · **22/10/2026**.

- [Report](../../../results/lessons/l1_8_b/report.md), [config](../../../results/lessons/l1_8_b/config.json), [results JSON](../../../results/lessons/l1_8_b/results.json).
- [Tám levels](../../../results/lessons/l1_8_b/level_metrics.csv), [1006 state rows](../../../results/lessons/l1_8_b/state_cells.csv), [biểu đồ](../../../results/lessons/l1_8_b/refinement_and_mode_share.png).
- [Pair checks](../../../results/lessons/l1_8_b/pair_checks.csv), [triplets](../../../results/lessons/l1_8_b/triplet_diagnostics.csv), [Richardson proxies](../../../results/lessons/l1_8_b/richardson_proxies.csv), [so luật](../../../results/lessons/l1_8_b/rule_comparison.csv).
- [Finite paths m1/2/4](../../../results/lessons/l1_8_b/finite_path_reference.csv), [forward scorer mọi level](../../../results/lessons/l1_8_b/forward_reference.csv), [zero-action](../../../results/lessons/l1_8_b/zero_action_controls.csv).
- [Near-ties](../../../results/lessons/l1_8_b/near_ties.csv), [float64/longdouble](../../../results/lessons/l1_8_b/precision_comparison.csv).
- [Đối chiếu nguồn](../../../results/lessons/l1_8_b/source_comparison.csv), [hai sai khác làm tròn](../../../results/lessons/l1_8_b/source_discrepancies.json), [audit phép tách hybrid](../../../results/lessons/l1_8_b/source_split_comparison.csv).
- [Runner log](../../../results/lessons/l1_8_b/run_output.txt), [124 tests](../../../results/lessons/l1_8_b/full_suite.txt), [JUnit](../../../results/lessons/l1_8_b/full_suite.xml).
- [Artifact audit](../../../results/lessons/l1_8_b/independent_artifact_audit.json), [manifest](../../../results/lessons/l1_8_b/artifact_manifest.json).
- [Card trước chạy](../../lessons/L1.8B_experiment_card.md), [working protocol cho v1](../../lessons/L1.8B_refinement_protocol.md).

```bash
.venv/bin/python -m experiments.lessons.run_l1_8_b
.venv/bin/python notes/verification/verify_l1_8_b_artifacts.py
# Giữ lần chạy này khi tái lập:
.venv/bin/python -m experiments.lessons.run_l1_8_b --output-dir /tmp/l1_8_b-rerun
.venv/bin/python notes/verification/verify_l1_8_b_artifacts.py --output-dir /tmp/l1_8_b-rerun
```

Code: `experiments/lessons/l1_8_refinement.py`, `l1_8_forward_reference.py`,
`run_l1_8_b.py`; tests: `tests/test_l1_8_refinement.py`.

Kết quả cuối: **13/13 Part B, 124/124 toàn repo PASS**. State counts:
4/6/14/30/62/126/254/510. GM=0 mọi level. GS từ0.9296875 xuống0.307151637 ởm128;
Richardson GS≈0.302699661, Gamma≈0.017362905 — estimates có điều kiện, chưa true limit.
Forward/backward scoring khớp trong3.6e-15; không RNG/seed hoặc probability pruning.

Cref tạm=Lstar(m128)=5.933106738, tol1%. Original pair rule báom8 cómaxcontrast
error/Richardson proxy1.219682%; hai đề xuất báom16 còn0.616263%. Chưa có hard band
cho rho/order để khóa tiêu chí v1; pair PASS không chứng nhận true continuum error.

**Khác biệt quan trọng với nguồn:** Gamma/m4 làm tròn0.025 (nguồn0.026),
Lstar/m32 làm tròn5.938 (nguồn5.939). Bảng B6 khớp đường có midpointM1 nhưng endpointM0;
đó không là fixed-model State-only split. Fixed-M0 mode share ởm128 là17.811%,
không gán≈11% của hybrid thành kết quả State-only. Order của fixed-M0 components
còn inconclusive tại triplet cuối, dù primaryGS córho gần1/2.

Lần đầy đủ đầu:122/122 tests PASS; runner dừng ởassertion kỳ vọngchỉ1rounded discrepancy
khi nguồn có2. Đã sửa cách audit để report mọi sai khác thay vì mặc định nguồn đúng;
không nới tolerance. Log/config đầu vàdevelopment_failure.json giữ nguyên. Thêm2tests
vềhybrid/forward, chuẩn hoá conditional posterior, kiểm cả diagnostic near-ties;
lần cuối124/124 PASS. Không có baseline pytest failure.

Đây là calibration toy đã exposed, chưa validation mạng, chưa kiểm hai neo vật lý
hoặc engine Phase3 tổng quát. Không sửa contract-v0/khóa contractv1, không fitH0/H1,
không mởconfirmation. G1,V3/V10/V11,HOLDPhase4 giữ nguyên; PartsC–E còn chờ.
