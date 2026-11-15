# Codex brief EV-TE Arm R fix — parser rule, retrain and descriptive run (local only)

From Claude for Doan Van Tai, 16/11/2026.
- cwd: `/home/vantai/state-model-regret`. Shell: `source .venv/bin/activate && source experiments/explore_ctmc/env.sh`.
- **Do not commit. Do not ssh.** The Arm S truth run is in progress on GCP; do **not** touch `experiments/ext_validity/ev_te.py`, `results/ext_validity/ev_te/{lock.json,CARD.md,predictions.csv,regimes.json,train/,raw/}` or any locked file. `ev_te.py` is locked: any byte change breaks `verify-lock` at scoring.

## Why
Arm R is descriptive and outside the lock (CARD §2, D2). The strict parser kept only 3,149 of 48,096 TM files. Claude checked a 1-in-10 sample (4,810 files):
- **Files omit OD pairs with zero traffic in that bin.** Absent pairs are small ODs (present median 0.03–0.26 Mb/s; the global minimum present value is 0.01333, about one quantum).
- **About 13% of bins (641/4,810) have a whole-node outage.** Some node has no entry as source or as destination; files with about 110 entries are one node's 22 ODs missing.

## Do
1. **In `experiments/ext_validity/ev_te_trace.py`, change the parser rule:**
   - an absent OD entry = 0 Mb/s;
   - a bin is **missing** if its file is absent, or if any of the 12 nodes has zero entries as source or zero entries as destination (node outage);
   - windows crossing a missing bin are dropped, as now.
   - Record the counts: files, absent-OD entries filled with 0, node-outage bins, absent-file bins, and valid bins.
2. Update `tests/test_ev_te.py`, adding only Arm R tests: absent = 0; node-outage = missing.
3. **Write all new outputs to `results/ext_validity/ev_te/arm_r_v2/`.** Keep `arm_r/` and `arm_r_train.log` untouched as history.
   - Run Arm R `train` (all same rules as before: train = first 2 calendar months; $\alpha$, $e^*$, managed OD1 and {OD1, OD2} from the train-period mean TM; $\rho\in\{0.8,0.9\}$).
   - Then run `run` and `summary` (descriptive).
   - Use `--workers 8` or fewer: local CPU only.
4. Run `python3 -m pytest -q tests/test_ev_te.py tests/test_ext_packet.py tests/test_ev_d4c.py --basetemp=/tmp/evte_r2_pt -o cache_dir=/tmp/evte_r2_cache`. All must pass.
5. Write `results/ext_validity/ev_te/arm_r_v2/README.md` with:
   - the parser counts;
   - the train $T_{int}$ (minutes) per $\rho$;
   - the managed ODs;
   - per ($\rho$, set, twin P/N, $\tau$, $h$): $G_S$ in % of $E_{stay}$ ± se, $n$, and $h/T_{int}$;
   - the fraction of time backlogged;
   - one plain-English paragraph of what is descriptive and what is not.
   - No verdicts, and no claims beyond the numbers.

## Final message
- The parser counts.
- $T_{int}$.
- The summary table (compact).
- The test result.
- Anything ambiguous.
