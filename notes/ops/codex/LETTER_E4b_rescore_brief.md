# Codex brief LETTER-E4b-RESCORE: independent rescore of E4b (new seed)

From Claude for Doan Van Tai, 16/11/2026.
- cwd `/home/vantai/state-model-regret`, branch `letter`. Shell: `source .venv/bin/activate && source experiments/explore_ctmc/env.sh`.
- **Do not commit. Do not ssh. Do not modify existing files** (including your own `experiments/letter/e4_rescore.py`).
- E4b = E4 with test seed **5000001**, output `results/letter/e4b/`, card `results/letter/e4b/CARD_E4B.json` (tests E4-1/E4-2/E4-4 at h/T_int ∈ {15, 30}, 102 units; thresholds in the card), lock `results/letter/e4b/lock.json` (30 files), VM manifest `results/letter/e4b/raw_sha256_vm.txt`. Extra tests X1–X3 are defined in `results/letter/e4b/CARD_E4B.md` and scored by Claude's `experiments/letter/e4b_extra.py` into `score_extra.json`.

## Do
1. Write `experiments/letter/e4b_rescore.py`. It may import your independent `experiments.letter.e4_rescore` (parameterize paths, seed and horizons). It must **not** import `e4_geant`, `e4_rhat`, `e4b_run`, `e4b_extra` or `ev_te`.
2. Same checks as for E4: hashes (VM manifest, json→npz, lock), 17 × 10 chunks, 500 unique instances per regime, seed 5000001, pilot false, onset θ 0.5; every row of `cells.csv`, `reductions.csv`, `regimes.csv` field by field; E4-1/E4-2/E4-3/E4-4 counts and verdicts against `score.json`.
3. Recompute X1–X3 from the definitions in `CARD_E4B.md` (not from `e4b_extra.py`) and compare with `score_extra.json`.
4. Output `results/letter/e4b/rescore_independent.json` and `.md`.

## Final message (Vietnamese)
MATCH or the list of mismatches, the verdict table (yours vs locked), and anything that looks like a convention difference.
