# Brief V7-1 (Claude → Codex, 17/11/2026): gap-scale rule analysis

Owner: **Doan Van Tai**. Repo `/home/vantai/state-model-regret`, branch `letter`. Shell: `source .venv/bin/activate && source experiments/explore_ctmc/env.sh`.

## Rules
- Do not commit; Claude commits.
- New files only:
  - `experiments/letter/v7_1_rule.py`;
  - `tests/test_letter_v7_1.py`;
  - `results/letter/v7_1/` (except `CARD_V7_1.md`, which is fixed).
- Do not modify any existing file. No ssh.
- **Parallel Codex jobs:**
  - V7-2 writes `experiments/letter/v7_2_*`, `results/letter/v7_2/`;
  - V7-3 writes `experiments/letter/v7_3_*`, `results/letter/v7_3/`, `tests/test_letter_v7_3*`.

  Do not touch their files.
- If the projected local compute exceeds 20 minutes, stop after a pilot and report: Claude moves it to GCP.

## Task
Implement exactly `results/letter/v7_1/CARD_V7_1.md`.
1. **Find the M0 gaps** without the correction. Sources:
   - CTMC: W1b raw, or recompute exactly with `experiments/explore_ctmc/ctmc.py`, `e3_agediff.py` functions at the saturation horizon. For every recomputed quantity, check that it agrees with a saved one to ≤ 1e-9 relative.
   - GÉANT: E4/E4b `raw/*.npz` (inspect which arrays hold per-instance fluid gaps for fresh and stale) and `e4_geant.py`.

   Document the exact arrays and units.
2. Compute M̂, Q90, ŝ and T_int per regime (and per seed for GÉANT); P1–P3 per cell; Y per cell from the existing cells/raw (the same definition as ledger G11_R8 / F3).
3. **Report:**
   - AUC per predictor per dataset, with a bootstrap over regimes (resample regimes, 2000 draws, seed 20261118) for the AUC difference P2 − P1;
   - the regime-level Spearman;
   - precision of P2 ≥ 1;
   - per-regime real-time h* = Q90/|ŝ| in seconds and in multiples of T_int.

   Write `results/letter/v7_1/summary.json` and `REPORT_V7_1.md`, with the verdict of the card's test, the forecasts, and every number with its source.
4. **Figure draft:** `results/letter/v7_1/fig_rule.pdf/png`, showing the share of Y = 1 against P1 and against P2 in binned form for both datasets. This is a candidate only.
5. **Tests:** AUC on toy data (known value); a gap extraction check on one regime against a saved value.
6. **Independent rescore:** a separate script `experiments/letter/v7_1_rescore.py` that does not import `v7_1_rule` and recomputes AUCs from the saved per-cell table. It must match to 1e-12.

## Final message (Vietnamese)
- the verdict;
- AUC values with CIs;
- the h* range;
- compute time;
- files;
- deviations.
