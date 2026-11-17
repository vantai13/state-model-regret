# Brief V7-3 test phase, congested scenario (Claude → Codex, 18/11/2026)

Owner: **Doan Van Tai**. Codex has quota again, so code returns to Codex (author rule 17/11). Claude is PI: card, review, lock commit, GCP.

**Read first:** `results/letter/v7_3/CARD_V7_3.md` and `results/letter/v7_3/card_v7_3_params.json` (committed with this brief).
They fix the design, strata, metrics, tests, forecasts and sensitivity analyses. Implement them exactly; propose changes in the
report, do not apply them.

## Rules
- **Do not commit and do not ssh.** Claude commits, locks and runs GCP.
- **No test-day computation of any kind:** no test-day loads, strata, simulation or outcomes. Do not run `run` or the test-day
  loader on test dates. Exercise the loader and the record function on **train** dates only.
- **New files only.** Existing `v7_3_*` modules, the night/provisioned/congested training outputs and the pilots stay byte-identical.
- Keep the engine calls of `v7_3_run.compute_night` (warmup, M0, posterior, twins, reference, paired evaluation, metrics) unchanged.
  Only the date gate changes, plus the extra saved arrays below.
- Run NumPy single-threaded in tests and timing (`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`).

## Deliverables
1. **`experiments/letter/v7_3_test.py`**, commands `lock`, `verify-lock`, `run --workers W`:
   - `lock` writes `results/letter/v7_3/test_congested/lock.json` with SHA-256 of:
     - the card, the params file and this brief;
     - every source file the run and the scorer import (`v7_3_test.py`, `v7_3_score.py`, `v7_3_day.py`, `v7_3_cong.py`, `v7_3_run.py`,
       `v7_3_sim.py`, `v7_3_data.py`, `e4_geant.py`, `ext_validity/ev_te.py`, and any other imports);
     - the congested training `configuration.json`/`.npz`, `protocol.json`, `summary.json`;
     - `data_manifest.json` and the canonical SNDlib member hash it records.
   - `verify-lock` recomputes every hash and exits nonzero on any mismatch. `run` and the scorer call it first.
   - `run`:
     1. Refuses if the output directory already has records (no resume).
     2. Loads the test weekdays with a new loader. It builds the same arrays as the training cache (window slots and the two-hour
        warmup), applies the phase-A exclusion rule, and is gated on a verified lock.
     3. Computes the **input-only strata** (card rule) for every regime × test day. It writes `inputs.json` (dates, exclusions,
        per-day max 15-min utilization per action, stratum) **before** any truth rollout.
     4. Runs every regime × test day record in a process pool, with deterministic per-record seeds from `test_seed`, independent of
        worker order. Each record is written atomically (`.npz` + `.json`) as soon as it is done.
     5. Writes `run_summary.json` with status `COMPLETE` or `INCOMPLETE`, plus CPU-s per record, wall time, peak memory, host and
        Python/NumPy versions.

     Any record exception stops the pool and gives INCOMPLETE. There is no retry.
   - **Record function** = `compute_night` logic with N = 32 and the test date gate. Also save:
     - the M0 predicted costs per instance (fresh `(N,2,4)`; stale per τ averaged over K, `(N,2,2,4)`);
     - `paired_evaluation`, `reference_decision_rollouts`, `V`, `C_ref`, `decisions`, `tie_flags`, `reference_tie_flags`
       (same axes as `compute_night`).
   - **One backlog trace per action per day** on a separate seed stream (`seed_for(test_seed, 'tint|'+regime+'|'+date)`), with the
     descriptive T_int from the same estimator as training (`v7_3_day.resolution`/train code path), with censoring flags.
2. **`experiments/letter/v7_3_test_gcp.sh`** (VM pipeline):
   - `verify-lock`;
   - `timeout 6h python -m experiments.letter.v7_3_test run --workers 30`;
   - log `PIPELINE_START` / `PIPELINE_EXIT rc=` to a noclobber log;
   - `sudo -n poweroff` at exit.

   Code lives in `~/smr` with `.venv` on the VM. The SNDlib path comes from the same environment variable the code already uses.
3. **`experiments/letter/v7_3_score.py`**: verifies the lock, then computes from the raw records exactly what the card defines:
   - the strata and evaluable counts;
   - H1–H3 verdicts with counts, the deciding clause and the per-horizon split;
   - F1–F7 (held / not held);
   - sensitivity analyses 1–5, physical units (Mbit and ms) next to every percentage, and the tie shares per pipeline/side.

   Outputs go to `results/letter/v7_3/test_congested/score/`: `summary.json` and `cases.csv` (one row per regime × day × τ × h with
   every metric). Deterministic; no plotting needed.
4. **`experiments/letter/v7_3_rescore.py`**: independent recomputation of every case metric and verdict from the raw `.npz` files and
   the params file.
   - It must **not** import `v7_3_score` or `v7_3_test`.
   - It compares field by field with `score/summary.json` and `cases.csv` (relative tolerance 1e-12; verdict strings exact) and
     writes `rescore.json` (MATCH or a list of mismatches).
5. **Tests** `tests/test_letter_v7_3_test.py`:
   - synthetic V/decision arrays with known G_S, regret, both-side regret, se, F shares and verdicts;
   - the tie variants (random tie = mean of the two actions; ties → Switch);
   - the strata rule on synthetic loads (exactly 1 counts as O);
   - the evaluable threshold;
   - H1 resolution clauses and the NOT_EVALUABLE minimums;
   - lock tamper detection;
   - **equivalence:** the record function on a congested **pilot train day** (DAY1 2005-05-05, pilot seed, N = 2) reproduces the
     saved pilot arrays in `day_train_congested/pilot/` bit for bit.
   - The test-day loader on a train date returns arrays equal to the training cache.
   - Mark slow tests; report run time.

## Report
`results/letter/v7_3/TEST_PHASE_IMPL_REPORT.md` (Vietnamese, short): what was built, test results, CPU-s per pilot-sized record
measured on a train day, the projected cost for 150 records × N = 32 on 30 workers, the files, and any proposed changes.

## Final message (Vietnamese)
- tests passed / failed;
- equivalence result;
- cost projection;
- files;
- anything blocking the lock.
