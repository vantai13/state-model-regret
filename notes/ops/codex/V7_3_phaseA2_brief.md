# Brief V7-3 phase A2 (Claude → Codex, 17/11/2026): daytime held reroute on real GÉANT TMs (training and pilot only)

Owner: **Doan Van Tai**. The author chose (17/11):
- run a **daytime** scenario;
- report the night consolidation result (phase A, training only, near-zero queueing, C_ref = 0, 100% ties) separately, as a scope observation.

Phase A artifacts are committed and must stay unchanged. Add new code paths (a scenario flag or new module `v7_3_day*.py`) without changing the night results.

## Rules
- Do not commit; Claude commits.
- No test-day outcome may be computed.
- No ssh; Claude runs GCP.
- New files only, or additive changes to `v7_3_*` that keep the night outputs byte-identical. Re-run the phase-A tests to show this.
- **Parallel job:** V7-1 runs on the VM. Do not touch `v7_1_*`.

## Daytime scenario (fixed by Claude from the phase-A design; propose changes in the report, do not apply them)
- **Days:** weekdays only. The train weekdays come from the existing train period; the test weekdays are the later ones. Use the same exclusion rule as phase A.
- **Window:** the 6-hour window with the highest mean total demand on train weekdays (start at a 15-min boundary). The decision is made at its start, and held for 6 h; also report 1, 2 and 4 h from the same rollouts.
- **Capacity:** the same rule as phase A (busiest Stay link at a train daytime peak utilization of 0.9; reuse the value if it is identical).
- **Actions:** as in Section V / E4.
  - Stay is the min-hop path of a managed OD flow; Switch is its second-shortest path (Yen, k = 2).
  - **Managed flows:** the top 3 OD flows by train-window mean volume that cross the busiest Stay link in the window. This gives **3 regimes**, one managed flow each.
  - Switching cost c = 0.
- **Truth, telemetry, posterior, twins and reference:** as in phase A.
  - truth: real 15-min TM × fast two-state modulation, β = 0.3;
  - τ ∈ {5, 15} min; K = 64 posterior simulations under Stay;
  - M0 with the train-average weekday profile forecast;
  - hybrid with ŝ from the train simulation of the window;
  - stationary rule;
  - C_ref from R_dec = 64 / R_eval = 128 CRN.
- **T_int:** check the estimator's resolution (phase A flagged estimates near dt). Use a dt or sampling that resolves the backlog autocovariance, and report the check.

## Training-only outputs (`results/letter/v7_3/day_train/`)
- the window;
- the managed flows and their paths;
- utilizations of both actions;
- T_int per regime with the resolution check, and h/T_int for 6 h;
- ŝ and its sign stability across train days;
- the M0 tie share;
- nonstationarity within the window;
- the C_ref scale (nonzero?).

## Pilot
Run 2 train days end to end with small N for timing. Project the CPU-s of the full test run (N = 200 per day) for 20 workers on n2-standard-32.

## Report
`results/letter/v7_3/PHASE_A2_REPORT.md`.

## Final message (Vietnamese)
- the window;
- the regimes;
- utilizations;
- T_int and h/T_int;
- ŝ sign stability;
- the tie share;
- the C_ref scale;
- the compute projection;
- proposed changes;
- files.
