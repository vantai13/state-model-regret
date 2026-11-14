# Codex brief AUDIT — independent review of the external-validity programme (waves 1–3) + exploitable findings

From Claude (orchestrator), 14/11/2026, for Doan Van Tai. The author has given full authority for a thorough,
independent check. You are the **independent auditor**: assume the authors (Claude and your earlier sessions) made
mistakes, and try to find any that could change a conclusion. Work locally (no GCP needed).

cwd: `/home/vantai/state-model-regret` (branch `ext/validity`). Env:
`source .venv/bin/activate && source experiments/explore_ctmc/env.sh` (`rg` not installed).
- **Do not modify any existing file.** Write only under `results/ext_validity/audit/` (new) and `notes/ops/codex/AUDIT_report.md` (new).
- Do not commit. Do not touch `results/ext_validity/ev_d4*` (a run is in progress there).

## What to audit (priority order)

**1. Verdict recomputation from raw outputs, with your own scripts that do not import our scoring code.**
- For each scored experiment, recompute every verdict from the raw files and the locked thresholds in its CARD:
  - `ev_a` (A1, A2): raw `run01/*.json`, predictions;
  - `ev_a2` (Z1);
  - `ev_b` (B1, B2) and `ev_b_rep` (R1–R3 at q75, q95);
  - `ev_d` (D1–D4), `ev_d2`, `ev_d3`, `ev_d3b`;
  - `results/explore_ctmc/csw_harm/run01` (S1–S3).
- Compare with each `score.json`. Check that the lock hashes in each `lock.json` match the current files.
- Report any mismatch.

**2. Code review for bugs that could flip a conclusion.**
- `experiments/ext_validity/closed_loop.py`: stale timing (decision on the backlog at t−τ, then τ under the old action, then Δ−τ under the new one); `zero_fit_first_order`; Kronecker products; normalisation.
- `packet.py`: CRN in futures and in `long_run_crn`; Lindley; fluid and ratefluid gaps (sign conventions, saturation ties); nowcast OLS; τ handling (EV-D3); window rates; `tint`; percent normalisation; seeds (train vs test independence).
- `trace_cox.py`: phase, looping, intensity normalisation; `trace_rates.c` (hash and binning).
- `ev_d*_panel.py` scoring: tolerance formulas; which rows are scored; the sign convention G_S = E[(a_stale − a_fresh)·D].

For anything suspicious, write a **small reproducer** under `results/ext_validity/audit/` that shows whether it matters numerically.

**3. Report consistency.** Check every number quoted in `results/ext_validity/WAVE1_REPORT.md`, `WAVE2_REPORT.md`, `WAVE3_REPORT.md`, `notes/theory/T12_plugin_stationarity.md` and DL-143–145 in `notes/02_decision_log.md` against the files.

**4. Exploitable findings for the paper.** Look for patterns in the existing data that are not yet reported and could strengthen or clarify the paper. Examples:
- Dose-response of harm in τ/T_int across EV-D2/D3a/D3b.
- Which regime features predict where the law's magnitude fails.
- Help vs harm boundaries.
- Any simple dimensionless predictor that collapses results across traces/classes.

Mark these explicitly **post-hoc / exploratory** and say what a confirmatory test would need.

**5. Threats a top-venue reviewer would raise** that the current evidence does not answer, ranked.

## Output
`notes/ops/codex/AUDIT_report.md` (Vietnamese, concise) with:
- **A.** Verdict table: experiment | ID | reported | recomputed | match?
- **B.** Bugs or risks, each with severity (blocker / major / minor), evidence (file:line, reproducer path) and whether it can change a verdict.
- **C.** Report-consistency errata.
- **D.** Exploitable findings: claim | evidence | post-hoc flag | confirmatory test needed.
- **E.** Ranked reviewer threats.
- **F.** One-paragraph overall assessment.

Your final message: a short summary of A–F and the paths written.
