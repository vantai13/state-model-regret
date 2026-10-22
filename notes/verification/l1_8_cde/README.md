# L1.8 C–E — verification index

Người thực hiện: **Doan Van Tai** · 22/10/2026.

- [Report có metric thực](../../../results/lessons/l1_8_cde/report.md), [results JSON](../../../results/lessons/l1_8_cde/results.json), [run log](../../../results/lessons/l1_8_cde/run_output.txt).
- [28-cell diagnostic CSV](../../../results/lessons/l1_8_cde/design_diagnostics.csv), [plot](../../../results/lessons/l1_8_cde/design_diagnostics.png), [config/hash](../../../results/lessons/l1_8_cde/config.json).
- [Consistency checks](../../../results/lessons/l1_8_cde/consistency_checks.json), [full-suite log](../../../results/lessons/l1_8_cde/full_suite.txt), [JUnit](../../../results/lessons/l1_8_cde/full_suite.xml).
- [Artifact auditor](../verify_l1_8_cde_artifacts.py), [audit result](../../../results/lessons/l1_8_cde/independent_artifact_audit.json).
- [Active v1](../../01_definitions_v1.md), [brief](../../00_research_brief_v1.md), [cards](../../lessons/L1.8D_decision_cards.md), [changes](../../lessons/L1.8E_changes_v0_v1.md), [closeout](../../phases/PHASE_1_closeout.md).

5 consistency checks PASS, full-source comparison PARTIAL. No grid contrasts/margins, reserve coordinates only. Budget là conservative estimates; A01 final dt/runtime và P0-V3/V10/V11/human feedback còn pending. Artifact auditor độc lập về công thức, không phải một người reviewer độc lập.

Git evidence: `push_receipt.json` và `push_output.txt` trong thư mục này được ghi sau khi push; receipt đối chiếu local/remote main, annotated contract-v1 và peeled target. Tag cũ không di chuyển. Receipt được commit bổ sung sau tag nên main có thể là descendant của tag; tagged scientific files vẫn phải byte-exact. Lần tái lập dùng output-dir mới, không ghi đè artifacts snapshot.
