# Codex brief EV-D4c-RESCORE — independent recomputation of the EV-D4c verdicts

From Claude (orchestrator) for Doan Van Tai, 15/11/2026.
- cwd: `/home/vantai/state-model-regret`, branch `ext/validity`.
- Shell: `source .venv/bin/activate && source experiments/explore_ctmc/env.sh`.
- Do not commit. Do not ssh. Do not edit any existing file.

## Task
Recompute every EV-D4c verdict from the raw inputs **without importing or reading the code of `experiments/ext_validity/ev_d4c_panel.py` or `ev_d4_panel.py`**.
- Work only from the specification in `results/ext_validity/ev_d4c/CARD.md`, sections "Rows and statistics" and "Hypotheses and thresholds".
- Use the Python standard library only (`json`, `csv`, `statistics`, `math`).

**Inputs** (read-only):
- `results/ext_validity/ev_d4c/cases.json`
- `predictions.csv`
- `selection.json`
- `test/*.json`
- `raw_manifest.json`

**First:** check every `test/*.json` against `raw_manifest.json` (sha256 and count), and report any mismatch.

## Recompute
1. **Per arm (C, L, H):**
   - completed outputs vs expected (cases × 2 h);
   - INCONCLUSIVE flag (< 90%);
   - the arm's status from `selection.json`.
2. **Rows.** For nowcast twins `fluid_nowcast`, `ratefluid_nowcast` with both h10 and h30 test outputs:
   - **Filter:** keep the row if |100·pred_abs(h30) / E_stay(h30).mean| ≥ 0.25.
   - `G_S` and `se` (absolute) and `pct_E_stay` come from `twins[twin]`.
   - **inc_ok:** sign(G_S30 − G_S10) == sign(pred30 − pred10), with sign(0) = 0.
   - **level_ok:** sign(pct30) == sign(pred30%).
   - **ratio:** (G_S30 − G_S10) / (pred30 − pred10).
   - **noise:** |G_S30 − G_S10| > 2(se10 + se30).
3. **Group by the case field `r`:** low {0.1, 0.3, 0.5}, band {0.8, 1.0, 1.2}, high {2.5, 5.0}. For each (arm, group) and each (arm, r):
   - n;
   - inc share;
   - level share;
   - median ratio;
   - number of regimes;
   - the noise-filtered inc share and its n;
   - NOT_EVALUABLE when n < 10.
4. **Verdicts:**
   - H1 and H2;
   - the WORKS/FAILS/MIXED label for L and H;
   - H3 per the CARD reading table;
   - D6 for each arm, on plug-in twins `fluid`, `ratefluid`: |pct30 − pct10·E10/E30| ≤ max(0.25, 2(se_pct30 + se_pct10·E10/E30)), where E = E_stay mean; threshold 0.90.
5. **Compare** with `results/ext_validity/ev_d4c/score.json`:
   - every verdict;
   - every share and median, to 1e-12 relative;
   - row counts.
   - Also compare row by row with `score_rows.csv` (same keys, same inc_ok/level_ok/noise_ok).

## Output
- `results/ext_validity/ev_d4c/rescore_independent.py`: your script.
- `results/ext_validity/ev_d4c/rescore_independent.json`:
  - the recomputed values;
  - a `mismatches` list (empty if all match);
  - the manifest check;
  - the number of compared fields.
- **Final message:** match or mismatch, listing any mismatch exactly; and any place where the CARD text allowed two readings, with the one you chose.
