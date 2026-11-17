# Brief V7-1 full run on GCP (Claude → Codex, 17/11/2026)

Owner: **Doan Van Tai**. Continue from the pilot (`results/letter/v7_1/REPORT_V7_1.md`, commit bf8d1295). The card `CARD_V7_1.md` is fixed.

## Facts
- The VM `dt4n-research-01` is RUNNING as **n2-standard-32** (ssh `dt4n-gcp`, code in `~/smr`, its own `.venv`, not a git repo).
- **Use at most 16 workers.** The other cores are reserved for V7-3 and V7-2.
- Do not stop, start or resize the VM; Claude manages it.

## Steps
1. rsync to `~/smr` everything the full run needs, with checksums:
   - code: `experiments/letter/v7_1_*`, the E4/EV-TE/CTMC modules it imports;
   - W1b raw; E4/E4b raw and inputs;
   - the SNDlib GÉANT network under the path the code expects (`SMR_SNDLIB`);
   - the L7.2 lock files if CTMC truth at α ≠ 6 is touched.

   Run the V7-1 tests on the VM.
2. **Split the run into two stages** if the script allows it (add a stage flag in new code only, not in existing files):
   - **(a) extract** the scales and the per-cell table (P1–P3, Y), detached with `setsid nohup`, logging `PIPELINE_START`/`PIPELINE_EXIT rc=`;
   - **(b) score:** the AUCs, bootstrap, Spearman, precision, figure.
3. After (a):
   - rsync back and compare checksums on both sides;
   - **commit and push the extracted table before running (b)** (no Co-Authored-By trailer);
   - then run (b) locally and the independent rescore `v7_1_rescore.py`, which must match to 1e-12.

   Commit `REPORT_V7_1.md` (updated), `summary.json` and the figure.
4. If anything fails, stop safely and report. **No reruns to obtain a different verdict.**

## Final message (Vietnamese)
- the card verdict;
- the AUCs with CIs per dataset;
- the regime-level Spearman;
- the precision of P2 ≥ 1;
- the h* range in seconds and in T_int;
- compute;
- commits;
- deviations.
