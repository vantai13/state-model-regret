# Brief LETTER-TRUNC-N2 (phase 1: implement, test, pilot). Claude → Codex, 17/11/2026

Owner: **Doan Van Tai**. Working directory `/home/vantai/state-model-regret`, branch `letter`.
Shell setup for every command: `source .venv/bin/activate && source experiments/explore_ctmc/env.sh` (use `python3`; `rg` is not installed).

## Hard rules
- Do not commit. Do not ssh in this phase. No network.
- Do not modify any existing file. In particular, leave `experiments/explore_ctmc/ctmc.py`, `experiments/letter/e3_agediff.py`,
  `experiments/letter/shat.py` and everything under `results/letter/w1b/` byte-identical.
- New files only:
  - `experiments/letter/trunc_n2.py`;
  - `experiments/letter/trunc_n2_gcp.sh`;
  - `tests/test_letter_trunc_n2.py`;
  - outputs under `results/letter/trunc_n2/`, with the pilot in `results/letter/trunc_n2/pilot/`.
- **Parallel job:** another Codex job edits only `/home/vantai/state-model-regret-papers/letter_smr/` (figures, ledger). Do not touch it.

## Read first
- `results/letter/trunc_n2/CARD_TRUNC_N2.md`: the card. Its expectations and thresholds are fixed; do not change them.
- `experiments/letter/shat.py`: `run_one`, `timed_v`, `timed_age` (the W1b code path, including parallelism inside a regime).
- `experiments/letter/e3_agediff.py`: `prepare_regime`, `evaluate_agediff`.
- `experiments/explore_ctmc/ctmc.py`: `choose_N`, `chain`, `Chain`.
- One saved raw file, e.g. `results/letter/w1b/raw/Za7p5_u1-2_lA17-2_x-2_k1-20.json`.

## Tasks
1. **`experiments/letter/trunc_n2.py`** with subcommands `pilot`, `run`, `compare`.
   - **Population:** the 27 cases of family `zf_a7p5_asym` in `results/letter/w1b/raw/`. The case dict comes from each saved raw file's `case`.
   - **`--n-scale` (1 or 2).** Wrap `ctmc.choose_N` so that it returns exactly `scale * original(...)`.
     - Find every reference to `choose_N` in the code path (attribute access and any `from ... import` binding) and patch each one.
     - Restore the originals afterwards.
     - **Guard:** in every output, assert that each chain's N equals `scale ×` the N saved in W1b `evaluations[*]['N']`; abort otherwise.
   - **Inputs fixed to the saved run:**
     - the ŝ levels are the saved `levels` (do not call `estimate_levels`);
     - the ages are the saved `tau` values of the five evaluations, in the same order and with the same labels (`seconds_1`, `Tint_0.1`, `Tint_0.3`, `Tint_1`, `Tint_3`);
     - the horizons are `case['hs']`;
     - call `evaluate_agediff(..., disagree=False)` exactly as `timed_age` does.
   - **Parallelism:** use one process pool.
     - Schedule regimes heaviest first, using the saved W1b `cpu_seconds`.
     - Within each regime, submit the chain-V jobs (as `run_one` does with `parallel_pool`) and then the five age jobs, so that the heaviest regime does not run serially.
     - Workers are set by `--workers`.
   - **Output:** one write-once JSON per regime in `results/letter/trunc_n2/raw/<id>.json` (never overwrite). It contains:
     - the case, the n_scale, the N per chain, the saved W1b raw sha256, and the evaluations;
     - process CPU-s, wall-s and peak RSS.

     Also write `run_start.json`, which holds the sha256 of `trunc_n2.py`, `e3_agediff.py`, `ctmc.py`, `shat.py`, the card, the host, the Python version and `nproc`, and `run_summary.json`.
   - **`compare`:** load each 2N raw and the saved W1b raw, and walk every numeric leaf present in both evaluations. Exclude cpu, wall, time, sha and N fields. Classify each field explicitly; list the field names in the output.
     - (a) Percentage-of-C_ref fields: G_S percentages, regrets of every pipeline and level, the stationary rule, law predictions. Report the max abs difference in pp.
     - (b) Costs, rates, biases, T_int, s, r: report the max relative difference.
     - (c) Discrete fields (booleans, decisions, tie flags, counts): require equality.
     - Write `compare.json` and `compare.md`, with the maximum per field group, its arg-max (regime, age, h, field), and the card thresholds applied:
       - (a) ≤ 1e-6 pp;
       - (b) ≤ 1e-9 relative;
       - (c) identical.
     - Missing or extra fields are listed, not ignored.
2. **Tests** (`tests/test_letter_trunc_n2.py`):
   - the wrapper doubles N and restores the original;
   - `compare` on small synthetic dicts, covering each field class and a missing field;
   - **code-path check:** with `--n-scale 1`, the lightest regime `Za7p5_u1-2_lA17-2_x-2_k1-20` reproduces every numeric field of the saved W1b evaluations with relative difference ≤ 1e-12. If this check fails, stop and report; do not adjust tolerances.
3. **Local pilot** (`pilot` subcommand; outputs in `pilot/`). The 1 × N run of the test above counts.
   - Run `--n-scale 2` on the lightest regime, and on at most one more light regime, only to measure the 2N/1N CPU ratio of each component (chain V, prepare, ages).
   - Project the total CPU-s for all 27 regimes at 2N and the critical-path wall time of the heaviest regime `Za7p5_u3-2_lA31-4_x1-3_k2`. Use the saved per-component CPU in W1b (`cpu_components_V`, the ages' `cpu_seconds`) and the measured ratios.
   - Estimate the peak RSS of the heaviest regime at 2N from the state counts.
   - Do not read the pilot's 2N-vs-1N differences in your report: report only that the pilot ran, with its timings.
4. **`experiments/letter/trunc_n2_gcp.sh`** (do not run it). On the VM (`~/smr`, own `.venv`, not a git repo) it does the following, in order:
   - `PIPELINE_START` with a timestamp to a noclobber log `results/letter/trunc_n2/gcp_run.log`;
   - a sha256 check of the four code files and the card against a manifest `results/letter/trunc_n2/manifest.sha256` (create the manifest locally); abort on mismatch;
   - `timeout <cap> python3 -m experiments.letter.trunc_n2 run --n-scale 2 --workers <W>`, where W and the cap are arguments;
   - `compare`;
   - `PIPELINE_EXIT rc=<rc>`;
   - `sudo -n poweroff`.

## Checks
- `python3 -m pytest -q tests/test_letter_trunc_n2.py`.
- `git status` shows only the new files; `git diff --stat` on existing files is empty.

## Final message (Vietnamese)
- the files created;
- the test results (including the 1 × N reproduction: max relative difference);
- the pilot timings and 2N/1N ratios;
- the projected total CPU-s, the critical-path wall time and the peak RSS;
- the recommended workers on n2-standard-32 (32 vCPU, 128 GB);
- any deviation from this brief.
