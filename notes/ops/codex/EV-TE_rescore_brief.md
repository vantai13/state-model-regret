# Codex brief EV-TE independent rescore (read-only inputs; write one new script + outputs)

From Claude for Doan Van Tai, 16/11/2026. Run this only after the raw truth data has been committed.
- cwd: `/home/vantai/state-model-regret`. Shell: `source .venv/bin/activate`.
- **Do not commit. Do not ssh.** Do not modify any existing file.

## Inputs (read only)
- `results/ext_validity/ev_te/raw/{regime}.npz` and `.json`.
- `predictions.csv`, `train/*.json`, `regimes.json`, `CARD.md`.
- `score.json` and `score_cells.csv`: Claude's locked-code score. Read them **only after** computing your own numbers, to compare.

## Do
1. Write `experiments/ext_validity/ev_te_rescore.py`, using numpy and stdlib only. **Do not import `ev_te` or any repo module.**
   - From `CARD.md` §3 alone, reimplement:
     - $C_{ref}$, $G_S$ (M0, P, CE), $G_M$, $\Gamma$, $z$;
     - the paired se;
     - $\Delta_{meas}$ and $\Delta_{pred}$ (from `predictions.csv` `level_h7`, `level_h30`, `Delta_pred`, `level_h30`);
     - the eligibility, including `stationary_rate_valid`;
     - H1–H4.
   - Pipeline index order is in the npz `pipelines` array; use it, do not assume.
2. Write `results/ext_validity/ev_te/rescore_independent.json`, containing:
   - per-hypothesis eligible/passed/fraction/verdict;
   - per-cell values;
   - a field-by-field comparison with `score.json` and `score_cells.csv` (max absolute difference per numeric field; any mismatch in eligible or pass flags).
3. Write `results/ext_validity/ev_te/rescore_independent.md`: MATCH or MISMATCH, with details.

## Final message
- MATCH or MISMATCH.
- The H1–H4 counts.
- The largest numeric difference.
