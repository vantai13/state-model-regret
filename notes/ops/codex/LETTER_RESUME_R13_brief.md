# Resume brief (Claude → Codex, 17/11/2026 evening): finish TRUNC-N2 scoring and close R13

Owner: **Doan Van Tai**. The author asked to continue after the pause. Read first:
- `notes/ops/codex/LETTER_HANDOFF_R13_brief.md`: the governing brief, whose rules all still apply;
- `notes/ops/codex/PAUSE_R13_20261117.md`;
- the checkpoint at `/home/vantai/.local/state/codex-pauses/R13_20261117_151247/`.

Do not reset, amend or clean either repo; keep every uncommitted change in `letter_smr`. Commit under the existing identity with **no Co-Authored-By trailer**.

## Done by Claude after the pause
- The 1×N and 2N runs both finished on the VM (`RUN_EXIT rc=0` for both; `PIPELINE_EXIT rc=0`).
- The raw 2N data, the log, the preflight log and the VM pytest log were retrieved, checksums matched on both sides, and they were committed and pushed **before any compare**: commit `91bee0fb0`.
- The VM was powered off. Confirm it is TERMINATED and report it. If it is not, power it off; do not start it.

## Part 1: score TRUNC-N2 (research repo, branch `letter`)
1. Run the locked `compare`: the primary comparison is 2N VM vs 1N VM (`DEVIATION_01.md`), plus the secondary comparison 1N VM vs the saved W1b raw (platform noise). Use the card thresholds unchanged.
2. Run the independent replay prepared in commit `81c9bf41a`. It must not import the compare module. Report it field-class by field-class.
3. Write `results/letter/trunc_n2/REPORT_TRUNC_N2.md`:
   - a verdict per field class;
   - the max abs difference in pp of C_ref for class (a), with its arg-max;
   - wall time, CPU and RSS;
   - the deviation;
   - the analysis of any class that fails, especially near-zero relative differences. Report them with their absolute size; do not re-classify.
4. Add a decision-log line to `notes/02_decision_log.md`, then commit and push.

## Part 2: close R13 (letter_smr, after Part 1)
Follow Part 2 of the handoff brief. Known state from R13b:
- 6 pages; this is acceptable, since the author will trim.
- Abstract 100 words; the limit is ≤ 100.
- `check_numbers`: 12 unmatched; `verify_letter`: 18 failed.

For each unmatched number or failed check, decide whether it is:
- (a) a new number that needs a ledger row: add it in `extend_r13`, recomputed from saved data;
- (b) a stale check expecting old v5 text or figure styles: update the check to the R13 brief, and say so;
- (c) a real error in the prose: fix the sentence minimally, within the R13b brief.

List every item in `notes/R13_closeout.md` with its class. The goal is 0 unmatched and 0 failed. Do not weaken a check just to pass it.

Then:
- insert the truncation clause (inclusion rule of the card) and add ledger `C5_R13`;
- update the 02_Code figure scripts and paper numbers already changed by R13b (verify them with `tools/pkg2`);
- rebuild, run `check_style`, and grep the PDF for card/forecast/hypothes/pass/fail;
- render the pages and look at them;
- copy the PDF to `/mnt/c/Users/VAN TAI/Downloads/SMR_letter_v6.pdf`;
- update `ROADMAP.md` and the `AGENTS.md` letter line;
- commit `letter_smr` (no push).

**No Acknowledgment or AI disclosure. The title and Corollary 1 stay unchanged.**

## Final message (Vietnamese)
- the TRUNC-N2 verdicts and the max change in pp;
- the VM state;
- the closeout table counts by class;
- the final check outputs, pages and abstract words;
- the commit hashes and paths;
- anything left undone.
