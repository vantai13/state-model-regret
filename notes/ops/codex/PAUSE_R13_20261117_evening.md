# Pause (author shuts down the laptop), 17/11/2026 evening (Claude)

Owner: **Doan Van Tai**. The author asked to pause. Claude stopped the Codex resume job (PID 19724 and its 4 children) with SIGTERM.
The VS Code app-server was not touched.

## State
- **VM:** `dt4n-research-01` is **TERMINATED**, at the default shape n2-custom-12-49152 (confirmed with gcloud).
- **Committed:**
  - 2N raw before compare: `91bee0fb0`;
  - resume brief: `ba6c6cc6e` (`LETTER_RESUME_R13_brief.md`, which governs the rest).
- **Uncommitted, left on disk by Codex Part 1 (do not delete):**
  - `results/letter/trunc_n2/REPORT_TRUNC_N2.md`, `analysis_*.{csv,json,log}`;
  - `experiments/letter/trunc_n2_analyze.py`;
  - edits to `trunc_n2_rescore.py` and its test;
  - a decision-log edit in `notes/02_decision_log.md`.

  Check them and their tests, then commit them as Part 1.
- **TRUNC-N2 result as reported by Codex** (not yet re-verified by Claude):
  - class (a) percentage fields: max 7.7e-9 pp, PASS;
  - class (b): FAIL by the card's literal relative rule, mostly near-zero or zero baselines (e.g. 0 → 2.3e-16 absolute);
  - class (c): 10 `margin_best.old` flags changed. These need cause analysis, probably near-ties.

  The letter's inclusion rule needs the class (a) max, plus an honest statement about (b) and (c) after the analysis.
- **letter_smr:** R13b prose and figure edits uncommitted (51 paths); checkers at 12 unmatched / 18 failed, as R13b reported. Part 2 of the resume brief has not started (or has barely started).

## Resume
Relaunch Codex with `LETTER_RESUME_R13_brief.md`, plus this note. Tell it that Part 1 artifacts exist uncommitted: verify them, commit, then do Part 2.
Claude then verifies before the v6 PDF is announced.
