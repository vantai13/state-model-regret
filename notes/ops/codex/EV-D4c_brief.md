# Codex brief EV-D4c — code for the three-arm sign-law card (implement + tests; no runs on GCP)

From Claude (orchestrator) for Doan Van Tai, 15/11/2026. The author delegated design to Claude and coding to Codex.
- cwd: `/home/vantai/state-model-regret` (branch `ext/validity`).
- Shell: `source .venv/bin/activate && source experiments/explore_ctmc/env.sh`. Use `python3` if `python` is missing.
- **Do not commit. Do not ssh. Do not run the full panel.**

## Read first
1. `results/ext_validity/ev_d4c/CARD.md`, the specification. **Do not edit it.**
2. `experiments/ext_validity/ev_d4b_panel.py` and `experiments/ext_validity/ev_d4_panel.py` (`predict`, `score`, `STRATA`, `NOWCAST`, `PLUGIN`). Reuse, do not copy logic you can import.
3. `experiments/ext_validity/ev_d4b_pipeline.sh`.
4. `experiments/ext_validity/packet.py`: `train`, `simulate`, `job`, the CLI, and the `background`/`path_keys` path.

## Edit ONLY these new files
- `experiments/ext_validity/ev_d4c_panel.py`
- `experiments/ext_validity/ev_d4c_pipeline.sh`
- `tests/test_ev_d4c.py`

Do not change any existing file. If `packet.py` cannot handle something the card needs, **stop and report**; do not patch it. This applies in particular to τ < 1 s: L-arm T_int can be about 8 s, so r = 0.1 gives τ ≈ 0.8 s. Check for `max(TAU, ...)`, `ts - tau` and window-rate edge effects.

## `ev_d4c_panel.py`: commands (`python -m experiments.ext_validity.ev_d4c_panel <cmd>`)

`OUT = results/ext_validity/ev_d4c`. Every writer raises `FileExistsError` if its output already exists.

**Shared constants:**
- `R = (0.1, 0.3, 0.5, 0.8, 1.0, 1.2, 2.5, 5.0)`;
- groups `low = (0.1, 0.3, 0.5)`, `band = (0.8, 1.0, 1.2)`, `high = (2.5, 5.0)`;
- `TINT_MAX = 240.0`, `MIN_REGIMES = 10`;
- series:
  - `SER_C = 'results/ext_validity/ev_d4/series_ditl4h_mod10.npz'`;
  - `SER_L = 'results/ext_validity/ev_d4/diag_loop15/series_202304121000.npz'`.

**Case fields** are the same as the EV-D4b cases (`lamA, lamB, u, seed, n_inst=10000, spacing_mult=3, train_T=100000., sample_dt=0.2, h_mult=[10, 30], batches=40, cls='trace_cox', params=dict(series=..., key='s0', path_keys=['s0', 's1'], bin=0.01), stratum, trace`), plus `arm`, `regime`, `r`, `tau`.

1. **`design-probe`** → `probe_cases.json` (60 cases).
   - **R_low:** use the EV-D4b `design()` regime generator logic (same `D4.STRATA`, the same `u`/`lamA`/`x` formulas, the same acceptance) with Sobol `seed = 20270115 + k` per stratum and cap 7.75 → 20 regimes.
   - **R_high:** the same generator with `seed = 20270126 + k` and acceptance `7.75 < max(lamA, lamB) + u <= 9.75` (with `lamA` grid upper bound from 9.75) → 20 regimes.
     - With `20270126 + k`, no stratum seed coincides with R_low's.
     - If a stratum cannot be filled, raise.
   - **Arms:**
     - C = R_low on SER_C, seeds 15000+i;
     - L = the same R_low on SER_L, the same seeds 15000+i;
     - H = R_high on SER_L, seeds 17000+i.
   - Regime ids `{arm}{N|B|P}{k:02d}`, e.g. `CN00`, `LN00`, `HP07`. C and L with the same suffix are the same regime.
   - Probe case id `{regime}_probe` with `tau = 1.0`.
2. **(train, existing CLI)** `python -m experiments.ext_validity.packet train --cases OUT/probe_cases.json --out OUT/train_probe --workers N`.
3. **`design`** → `cases_all.json` (480 cases = 3 arms × 20 × 8).
   - For each regime, read `train_probe/{regime}_probe_s{seed}.json`.
     - If `T_int_censored`, or T_int ≤ 0: keep the regime out of `cases_all` and list it in `design_excluded.json`.
     - Else make 8 cases with `tau = round(r * T_int_probe, 2)`, `id = f'{regime}_r{round(r*10):02d}'` (r01, r03, r05, r08, r10, r12, r25, r50; `packet.validate` forbids dots in ids — amended 15/11 after Codex's stop report; keep the numeric field `r`), the same seed.
   - If any τ < 0.01, raise.
4. **(train, existing CLI)** `--cases OUT/cases_all.json --out OUT/train`.
5. **`select`** → `cases.json` + `selection.json`.
   - A regime passes in its arm iff all its r cases have `T_int_censored` false and `T_int <= TINT_MAX`.
   - **C and L are paired:** regime suffix `XNkk` is kept in C and in L only if both pass (and neither was design-excluded).
   - H is independent.
   - `selection.json` records per arm: excluded regimes with the reason, the kept count, the rule text, and `arm_status` OK/STOP.
     - An arm with fewer than `MIN_REGIMES` kept regimes is `STOP` and gets no cases in `cases.json`.
     - If all three arms STOP: exit non-zero.
6. **`predict`** → `predictions.csv`. Reuse `ev_d4_panel.predict` by rebinding `OUT/CASES/PRED` as in `ev_d4b_panel._bind` (add `arm`, `r` columns only if trivial; otherwise derive them from `cases.json` at score time).
7. **`describe`**: train only.
   - **It must never open anything under `test/`.**
   - Prints and writes `seen_before_lock.json`:
     - per arm: kept regimes, T_int min/median/max;
     - per arm × r: median nowcast β₁ for path A (the train JSON `nowcast` field; inspect its structure);
     - per arm × r: median `F_old − F_new` for the fluid nowcast at h30 (from `shares['30']`);
     - per arm × group: number of h30 prediction rows with |100·pred_abs / train mean_stay| ≥ 0.25 (approximate D2 filter count).
8. **`run N`**: as `ev_d4b_panel.run`.
   - Test seed, resumable, tasks sorted heaviest first.
   - Assert `train case_sha256 == packet.signature(case)`.
   - Only cases in `cases.json`.
9. **`manifest`** → `raw_manifest.json`, as in EV-D4b.
10. **`verify-lock`**
    - Read `lock.json` (`{"created": ..., "sha256": {relpath: hex}}`) and compare every file. Exit 1 on any mismatch or missing file.
    - Print `LOCK_PASS n` on success.
    - No `lock` writer: Claude writes the lock.
11. **`score`** → `score.json`, exactly the CARD section "Rows and statistics" and the H1/H2/H3/D6 table.
    - Group by the design value `r`, not by the realized τ/T_int.
    - **Per arm:** `completed/of`, an `inconclusive` flag (< 90%), and per group and per r:
      - `n`;
      - `inc_share`;
      - `level_share`;
      - `median_inc_ratio`;
      - `n_regimes`;
      - the noise-filtered `inc_share_noise` with its n.
    - **Verdicts:**
      - **H1** (C low ≥ 0.80);
      - **H2** (C band share ≤ 0.65 AND median ratio < 0.5);
      - band labels WORKS/FAILS/MIXED for L and H, and **H3** per the reading table. H3 is UNRESOLVED if H2 is not PASS, or if any needed group is NOT_EVALUABLE or INCONCLUSIVE;
      - **D6-C, D6-L, D6-H**: plug-in twins `('fluid', 'ratefluid')`, the formula of `ev_d4_panel.score` D6, threshold 0.90; L and H are marked `exploratory: true`.
    - NOT_EVALUABLE for a group with n < 10.
    - A stopped arm is reported `STOP` and is not scored.
    - Also write per-row records to `score_rows.csv` (arm, regime, r, tau, twin, pred30, G30, G10_abs, G30_abs, pred10_abs, pred30_abs, inc_ok, level_ok, inc_ratio, noise_ok).

## `ev_d4c_pipeline.sh STAGE` (runs on the VM in `~/smr`; started by Claude)
The pattern is `ev_d4b_pipeline.sh`: log to `~/ev_d4c.log`, with `STAGE_START`/`STAGE_DONE` lines and timestamps.
- **`train`:**
  1. probe train (`--workers ${WORKERS:-32}`; the VM is now n2-standard-32, 128 GB);
  2. `design`;
  3. main train;
  4. `select`;
  5. `predict`;
  6. `describe`;
  7. `TRAIN_DONE`.
  - On any failure, stop with a `FAILED step=...` line. **No poweroff.**
- **`test`:**
  1. `verify-lock` (abort, then sync and poweroff if it fails);
  2. `run` with retry on fewer workers (${WORKERS:-32}, 16, 8) under `timeout 9h`;
  3. `manifest`;
  4. `score`;
  5. `PIPELINE_DONE`, `sync`, `sudo -n poweroff`.

## Tests (`tests/test_ev_d4c.py`, fast, under 60 s total)
- `design-probe` logic, on a temp OUT:
  - 60 cases;
  - strata counts 8/4/8 per arm;
  - load windows hold;
  - C and L share lamA/lamB/u/seed per suffix and differ only in `params.series` and `arm`/`id`;
  - H seeds 17000+;
  - deterministic across two calls.
- `design` from fake probe JSONs: τ = round(r·T, 2); a censored probe is excluded.
- `select` pairing: C fails → the paired L is dropped too; H independent; STOP below 10.
- `score` on synthetic fake `cases.json`, `predictions.csv` and test JSONs with hand-computed expected shares:
  - all four H3 branches;
  - NOT_EVALUABLE (n < 10);
  - an INCONCLUSIVE arm;
  - D6.
- `describe` never touches `test/`: monkeypatch `open`/`Path.read_text`, or make `test/` unreadable.
- `verify-lock`: PASS and a FAIL on a one-byte change.
- **τ < 1 s smoke:** if cheap (seconds), one tiny `packet.train`/`simulate` on SER_L with τ = 0.8 and a small `train_T`/`n_inst`, to show no error and finite output. If it is not cheap, explain why and do a code-reading check instead.

Then run `pytest -q tests/test_ev_d4c.py` and the existing `tests/test_ext_packet.py` (it must still pass).

## Final message
- Files written.
- Test results (counts and time).
- What you found about τ < 1 s.
- A rough cost estimate:
  - how long one probe train takes locally for one C and one L case, if you measured it;
  - otherwise use EV-D4b: 120 trains plus 240 tests took about 44 min for the test on 12 vCPU, and test cost scales roughly with T_int.
- Any place where the card was ambiguous and the choice you made.

## Amendment 15/11 (after the first Codex stop report)
- Case ids use `_r{round(r*10):02d}` (see `design`), because `packet.validate` rejects dots. Nothing else changes.
- Your stop was correct. Continue now with the full brief, including the τ < 1 s smoke check.
