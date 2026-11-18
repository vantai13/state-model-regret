# Brief V7-3 DEVIATION 01 scoring wrapper (Claude → Codex, 18/11/2026)

Owner: **Doan Van Tai**. Read first:
- `results/letter/v7_3/DEVIATION_V7_3_01.md` (committed a32137acd before any outcome was read);
- `CARD_V7_3.md`, `card_v7_3_params.json`;
- the locked `v7_3_score.py` / `v7_3_rescore.py`.

The raw records are committed (316a553ad). The run is INCOMPLETE: 147/150 records, the 2005-06-27 records are absent.

## Rules
- **Do not modify any locked file** (see `results/letter/v7_3/test_congested/lock.json`). `verify-lock` must still print LOCK MATCH.
- New files only. Do not commit; Claude commits. No ssh, no simulation.

## Deliverables
1. **`experiments/letter/v7_3_score_dev1.py`:**
   1. Run `verify_lock` first.
   2. Recompute the DEVIATION 01 exclusion from the inputs:
      - load every test weekday through the locked loader (`v7_3_test.load_days` with the verified token);
      - take each day's maximum 15-min total demand in the window;
      - exclude a day if it exceeds 2× the training-window maximum, computed from the congested training cache (`v7_3_day.load(v7_3_cong.OUT)`).
   3. Assert that the completed records are exactly every regime × non-excluded day, with sha256 and stratum labels intact as in `read_records`.
   4. Build filtered inputs: dates without the excluded day, records filtered, and the exclusion appended with the reason and the measured ratio.
   5. Call the locked `case_rows` and `summarize`. Do not reimplement the metrics.
   6. Also report F1 on the original 50 days.
   7. Write `results/letter/v7_3/test_congested/score_dev1/{summary.json,cases.csv,deviation.json}`. `deviation.json` holds:
      - the excluded days, their ratios, the threshold, the train maximum;
      - the top-5 test ratios;
      - the wrapper's own sha256 and the lock sha.
2. **`experiments/letter/v7_3_rescore_dev1.py`:**
   - It must **not** import `v7_3_score`, `v7_3_score_dev1` or `v7_3_test`.
   - It recomputes the exclusion independently: parse the archive with the `v7_3_data` helpers or its own minimal reader.
   - It recomputes every case and the summary with the locked `v7_3_rescore` functions (`recompute`, `rebuild_summary`).
   - It compares field by field with `score_dev1/` (rtol 1e-12; verdicts exact) and writes `score_dev1/rescore.json` (MATCH or the mismatches).
3. **Tests** `tests/test_letter_v7_3_dev1.py`:
   - the exclusion threshold logic, including that any threshold in (1.23, 19.64) gives the same set on synthetic data;
   - refusal when the completed set differs from the expected set;
   - locked files untouched.
4. **Run** both wrappers on the real committed raw, plus the test suite `tests/test_letter_v7_3*.py` (fast).

## Report and final message (Vietnamese)
Write `results/letter/v7_3/test_congested/score_dev1/REPORT_DEV1_IMPL.md` (short). It covers, and the final message summarizes:
- the exclusion result;
- the H1–H3 verdicts with their counts, deciding clauses and per-horizon splits;
- F1–F7 held / not held;
- the evaluable/non-evaluable counts per stratum;
- the rescore result;
- the files.

Do not interpret beyond the numbers; Claude writes the analysis.
