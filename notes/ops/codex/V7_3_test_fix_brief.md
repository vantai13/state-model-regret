# Brief V7-3 test fix before the lock (Claude → Codex, 18/11/2026)

Owner: **Doan Van Tai**. Claude's review found a crash that the synthetic tests missed. Nothing is locked yet; no test-day computation has run.

## Bug
`results/letter/v7_3/day_train_congested/configuration.npz` stores `capacity` with shape `(1,)`.
- With NumPy 2.5, `float(capacity)` raises `TypeError: only 0-dimensional arrays can be converted to Python scalars`.
- Affected: `v7_3_test.strata` (line ~108) and `_record` (line ~226).
- `run()` would crash at the strata step right after the lock, making the one-shot run INCOMPLETE.
- Reproduced by Claude: `strata(training['days'][j], arrays['incidence'][0], arrays['capacity'])` with arrays from `v7_3_day.load(v7_3_cong.OUT)`.

## Tasks
1. Fix every scalar conversion of `capacity` (and any other size-1 array) in the new files with `.item()` semantics that also accept 0-d arrays and Python floats.
   - Audit `v7_3_test.py`, `v7_3_score.py`, `v7_3_rescore.py` and `v7_3_test_common.py` for the same pattern (e.g. `float(`, `int(` on arrays).
2. Add a **slow integration test on real training data**:
   - run `compute_record` on the congested **train** day DAY1 2005-05-06 (pilot seed, N = 2, full K/R, `training_only=True`);
   - add `input_utilization` and the `strata` label exactly as `_record` does;
   - write the meta with `C.write_json` (JSON safety);
   - run `v7_3_score.case_rows` and `v7_3_rescore.recompute` and assert `compare(...) == []`.

   Better still, factor the per-record body of `_record` so that the test exercises the same code path as the run on a train date.
3. Add a **dry run of `run()`'s pre-pool steps on train dates** (a test-only path, never test dates): load the dates, compute strata, write `inputs.json` to a tmp dir.
   - It should exercise the real `configuration.npz`/`.json` types.
   - Same rules as before: no test-day access, and train dates only.
4. Rerun the full V7-3 test suite: the slow tests too, plus `tests/test_letter_v7_3*.py`. Record the results in `TEST_PHASE_IMPL_REPORT.md` (append a short "Fix 18/11" section).

## Rules
No commit, no ssh, no lock, no test-day computation. Do not edit the card, params or the earlier briefs. Keep the engine call sequence unchanged; the bitwise pilot equivalence must still pass.

## Final message (Vietnamese)
- what changed;
- the test counts;
- the integration result.
