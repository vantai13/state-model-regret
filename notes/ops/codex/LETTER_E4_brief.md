# Codex brief LETTER-E4: GÉANT fluid twin vs hybrid correction (code, training-only checks, local pilot)

From Claude for Doan Van Tai, 16/11/2026. **Read `results/letter/E4_DESIGN.md` (approved by the author) first.**
- cwd `/home/vantai/state-model-regret`, branch `letter`. Shell: `source .venv/bin/activate && source experiments/explore_ctmc/env.sh`.
- **Do not commit. Do not ssh.**
- **Do not modify existing files.** `experiments/ext_validity/ev_te.py` is locked: import it.
- New code goes in `experiments/letter/e4_geant.py` (+ `e4_rhat.py` if useful); tests in `tests/test_letter_e4.py`; outputs in `results/letter/e4/`.
- The full truth run happens on GCP after Claude writes the card. Your job ends with the training checks and a pilot.

## Facts (checked by Claude in ev_te.py)
- **Locked helpers to import:**
  - `make_model(spec)`: model with `weights[action, link, OD]` (mean rates incl. α), `capacity`, `kappa` (per-OD mode **switching rate**; mode autocorrelation $e^{-2\kappa t}$), `beta`;
  - `instances(model, ti, dt, n, seed)`: fresh state and stale states per τ;
  - `posterior(model, modes, queues, dt, age, k, seed)`: K samples of the current state given a stale full state;
  - `twin_costs(model, modes, queues, dt, hs)`: the fluid twin's predicted cost per action and h;
  - `futures(model, modes, queues, dt, hs, seed)`: true costs per action and h from CRN rollouts (rows = state × rollout);
  - `seed_for(...)`; `grid(ti, dt)`.

  Training outputs live in `results/ext_validity/ev_te/train/<regime>.json`: T_int, dt, `r_a` (per action, batch stats), training action shares.
- **Regimes:** the 17 confirmatory GÉANT regimes (`stationary_rate_valid` True in `results/ext_validity/ev_te/score.json`). Specs in `results/ext_validity/ev_te/regimes.json`.
- **Test seed 3000001** (new). N = 500, K = 128, R_eval = 256, R_dec = 128. τ/T_int ∈ {0.3, 1, 3}; h/T_int ∈ {1, 2, 4, 7, 15, 30}, using `grid`-style rounding to dt steps.

## Do
1. **Per-action true costs.** For each instance, $V[n, a, h]$ = mean over R_eval CRN rollouts of `futures` from the fresh state. Every pipeline's cost is then $V[n, a^{\rm pipe}_n, h]$.
   - **Regression test:** if feasible, reproduce the locked EV-TE `pipeline_V` for M0_new on one small regime with seed 1000001 and EV-TE's seed derivation. Otherwise reproduce it on a toy model exactly, and explain.
2. **Decisions** for fresh (state X) and stale (posterior average over K samples given the age-τ full state), per τ:
   - **M0:** argmin of twin_costs; exact ties → Stay (action 0), as EV-TE does.
   - **M0-tie-r̂:** ties → the action with the lowest r̂ among the tied actions; r̂ levels (i), (ii), (iii).
   - **M0-tie-rand:** ties → a uniformly random tied action (seeded).
   - **Hybrid(r̂):** argmin over a of $\hat V_a(h,x)+h\,\hat r_a$; for the stale side, average $\hat V$ over the posterior, then add $h\hat r_a$.
   - **Onset-hybrid(r̂, θ):** $\hat V_a+\hat r_a\max(0,h-\theta T_{int})$. Implement it, but it is **disabled by default** (Claude enables it after W2 with a fixed θ).
   - **M1_new:** argmin of the mean of R_dec separate rollouts (`seed_for(seed,'M1_new')`-style independent stream), fresh only. C_ref = L(M1_new).
   - Record the tie share per pipeline and side.
3. **r̂ levels (per action a):**
   - **(i) Training simulation:** `r_a` from the EV-TE training files.
   - **(ii) Gaussian fluid approximation** from model statistics (no simulation). For each link e under action a:
     - $\bar\lambda_{e,a}=\sum_j w_{a,e,j}$;
     - $\sigma^2_{e,a}=\sum_j(\beta w_{a,e,j})^2$;
     - $T_{e,a}=\sum_j(\beta w_{a,e,j})^2/(2\kappa_j)\,/\,\sigma^2_{e,a}$;
     - $\mathbb E[Q_{e,a}]\approx\sigma^2_{e,a}T_{e,a}/(C_e-\bar\lambda_{e,a})$ if $\bar\lambda_{e,a}<C_e$, else flag;
     - $\hat r_a=\sum_e\mathbb E[Q_{e,a}]$, in the same backlog units as (i).
   - **(iii) Ordering-only:** $\sum_e\rho_{e,a}/(1-\rho_{e,a})$ with $\rho=\bar\lambda/C$. Used only for tie-break and ordering, never in the hybrid magnitude.
   - **(iv) Noise on (i):** $\hat r_a=r_{\rm Stay}+(r_a-r_{\rm Stay})(1+\varepsilon)$, ε ∈ {−0.5, −0.25, 0.25, 0.5}.
   - **(v) Reversed:** $\hat r_a=r_{\max}+r_{\min}-r_a$.
4. **Sharding.** Split each regime into 10 chunks of 50 instances. All random streams derive deterministically from (seed, regime, chunk, purpose), so a chunk's result does not depend on scheduling.
   - One write-once npz + json per (regime, chunk) in `results/letter/e4/raw/`: V, decisions per pipeline/side/τ/h, tie flags, CPU.
   - A `merge` step builds per-regime and per-cell tables.
5. **Training-only checks (before truth, no test seed):** per regime, the r̂ (ii) and (iii) best action vs (i), and the full ordering agreement; tie shares of M0 on the EV-TE **training** instances (seed 1, small N = 100 is enough). Write `results/letter/e4/training_checks.json`. This feeds design test E4-3.
6. **CLI** `python3 -m experiments.letter.e4_geant {train-checks,run,merge,score}`:
   - `run --workers N --chunks all|<list>`;
   - `score` computes E4-1…E4-6 with thresholds read from a card file given by `--card` (Claude writes it). Without a card it only writes descriptive tables.
7. **Tests** in `tests/test_letter_e4.py`:
   - the regression of item 1;
   - tie handling on a toy cost array;
   - the hybrid equals M0 when r̂ is constant across actions;
   - reversed r̂ flips the best action;
   - Gaussian approximation sanity (single link: monotone in load, matches the formula);
   - sharding determinism (same chunk twice gives the same bytes).

   Run `python3 -m pytest -q tests/test_letter_e4.py --basetemp=/tmp/le4_pt -o cache_dir=/tmp/le4_cache`.
8. **Pilot:** `run --workers 4` on 2 regimes × 1 chunk (choose the cheapest and the most expensive per EV-TE CPU in `results/ext_validity/ev_te/raw/*.json`), into `/tmp/e4_pilot/`. Report CPU per chunk and the projected total for 17 × 10 chunks.

## Final message (Vietnamese)
- Tests.
- The training checks table: r̂ (ii)/(iii) agreement with (i); training tie shares.
- Pilot CPU and the projection.
- The exact GCP command.
- Anything ambiguous.
