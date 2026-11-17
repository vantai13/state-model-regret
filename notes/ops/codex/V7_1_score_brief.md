# Brief V7-1 scoring (Claude → Codex, 17/11/2026)
Owner: **Doan Van Tai**. The extraction table is committed and pushed before scoring (536dc4863). Now run stage (b) **locally**:
the scoring stage of `experiments/letter/v7_1_gcp.py` (or `v7_1_rule.py`) on `results/letter/v7_1/full/`, exactly as `CARD_V7_1.md` and
`V7_1_brief.md` item 3–4 define (AUCs, bootstrap over regimes with 2000 draws and seed 20261118, regime-level Spearman, precision of P2 ≥ 1,
h* table, figure draft), then the independent rescore `v7_1_rescore.py` (must match to 1e-12). Update `REPORT_V7_1.md` and `summary.json`
with the card verdict, forecasts and every number with its source.
Rules: **do not commit or push** (Claude commits); do not touch `v7_3_*` (a parallel job) or anything else; no ssh. Final message in
Vietnamese: verdict, AUCs with CIs per dataset, Spearman, precision, h* range, files.
