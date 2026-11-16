# Codex brief LETTER-W2: fixed ŝ level (ii), onset-aware hybrid, probabilistic bound, E1 data, tie-break baseline (code + local smoke test only)

From Claude for Doan Van Tai, 16/11/2026. **Read `results/letter/CARD_W2.md` first.** Its decisions (estimator, θ grid, train/held-out split, predictions P13–P20) are fixed; do not change them.
- cwd `/home/vantai/state-model-regret`, branch `letter`. Shell: `source .venv/bin/activate && source experiments/explore_ctmc/env.sh`.
- **Do not commit. Do not ssh.**
- **Do not modify existing files**, including W1a/W1b code (`experiments/letter/{ties_topology,lemma_check,ctmc_saved_tables,e3_agediff,shat,w1a_report}.py`) and anything under `results/explore_ctmc/` or `results/ext_validity/`. Import them instead.
- New code goes in `experiments/letter/` (new files only); new tests in `tests/test_letter_w2.py`.
- **The full run happens on GCP** (Claude launches it). Your job ends with a passing local smoke test.

## 1. `experiments/letter/mmpp.py`: independent MMPP/M/1 stationary-mean solver
- **Model:** two-state symmetric mode with rates λ ± α, switching rate 1/κ each way, service μ, backlog truncated at N.
- **Output:** the stationary mean backlog from the truncated generator, via a sparse solve.
- **Truncation:** choose N so that the stationary tail is ≤ 1e-13; reuse the `ctmc.choose_N` logic if importable, otherwise grow N until the mean changes by < 1e-10 relative.
- **Validation test:** at the exact parameters, match `ctmc.chain(load, κ, N, a).r` to 1e-8 relative, for a ∈ {3, 6, 7.5} and two loads each.
- **It must accept any α ≥ 0, including non-grid values.**

## 2. `experiments/letter/shat2.py`: estimator of CARD_W2 §A
- Simulate per-path arrival counts in bins Δ_b = 0.01 over W = 100·T_int with the seed `20261116 + regime_index`. Estimate λ̂, α̂ and κ̂ exactly as in the card.
- Compute r̂ for each path/action with `mmpp.py`, then ŝ_mmpp.
- Record all estimates and the relative error against true s.
- **Memory and time:** W/Δ_b can be large. Simulate the mode path exactly (exponential holding times) and draw Poisson counts per bin. Stream the autocovariance (FFT on chunks or an exact running sum up to the first non-positive lag, max lag 50·κ̂_guess bins).

## 3. `experiments/letter/w2_eval.py`: one function per regime, everything else
For one regime (from `cases/{asym,zf_a3_asym,zf_a7p5_asym}.json`), at ages τ ∈ {1 s, T_int} and the case's h grid, age-only stale observation (reuse `e3_agediff`).
- **Hybrid levels:** true s, M/M/1, ŝ_mmpp (new).
- **Onset-aware hybrid** for θ ∈ {0.5, 1, 2, 4} × ŝ ∈ {true s, M/M/1}: gap $\hat\Delta(h,x)+\hat s\max(0,h-\theta T_{int})$, applied to both fresh and stale.
- **Tie-break baseline:** M0 with exact ties → 1{ŝ < 0}, for true s and M/M/1.
- **Regret (% C_ref)** for fresh and stale of every variant, and G_S. Use the same `pair_sum` conventions as `ctmc.evaluate` (strict inequality; ties → Stay unless the variant says otherwise).
- **Probabilistic bound D(h)** of CARD_W2 §C at τ = T_int with true s, and the actual hybrid fresh/stale disagreement mass. Use `ctmc.dense_disagree` if the size allows; otherwise an exact sorted-pair computation. Never Monte Carlo.
- **E1 data** (CARD_W2 §D), only for the three pre-chosen regimes: $\hat V_a(h,x)$ and $V_a(h,x)$ on 60 log-spaced h/T_int points in [0.1, 30], for the three states per regime.
- Write one JSON per regime (write-once) to `results/letter/w2/raw/<id>.json`, with CPU seconds.

## 4. `experiments/letter/w2_run.py`: CLI
- `run --workers N --families asym,zf_a3_asym,zf_a7p5_asym --out results/letter/w2/raw`: resumable only by skipping completed files. This is a new exploratory wave, not a locked truth run.
- `analyze`: θ selection on `asym`, held-out evaluation on the other two families, P13–P20 marked held / not held mechanically, tables to `results/letter/w2/README.md` and `summary.json`.
- `figure_e1`: a 3-panel EPS + PDF in `results/letter/w2/fig_e1.{eps,pdf}`, one panel per regime, $\hat V$ dashed and $V$ solid per state, log x-axis in h/T_int. Use the paper style: DejaVu Serif 8 pt, 3.5 in wide.

## 5. Local smoke test, then stop
- `tests/test_letter_w2.py`:
  - solver validation;
  - estimator on a synthetic MMPP with known parameters (λ̂, α̂ within 5% and κ̂ within 15% for W long enough);
  - D(h) ≥ disagreement on one regime;
  - onset gap equals the hybrid gap for θ = 0.
- Run `python3 -m pytest -q tests/test_letter_w2.py --basetemp=/tmp/lw2_pt -o cache_dir=/tmp/lw2_cache`.
- Run `w2_run.py run --workers 4 --families asym` limited to **2 regimes** into `/tmp/w2_smoke/`. Report the CPU per regime and the projected total for 93 regimes.

## Final message (Vietnamese)
- Test results.
- Smoke CPU and the projection.
- The exact command for the GCP run.
- Anything ambiguous in the card.
