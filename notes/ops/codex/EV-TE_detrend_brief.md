# Codex brief EV-TE Arm R-DT — detrended backlog integral time (exploratory, local only)

From Claude for Doan Van Tai, 16/11/2026.
- cwd: `/home/vantai/state-model-regret`. Shell: `source .venv/bin/activate && source experiments/explore_ctmc/env.sh`.
- **Do not commit. Do not ssh.**
- Do not modify any existing file, in particular `experiments/ext_validity/ev_te.py`, `ev_te_trace.py` and `packet.py`. Anything under `results/ext_validity/ev_te/` other than the new folder is also off limits.
- Local CPU only, `--workers 8` or fewer.

## Read first
`results/ext_validity/ev_te/arm_r_detrend/CARD.md`. It was committed before any computation (ecb0f9a3) and is the specification. Follow it exactly, including the reading rule. Do not change thresholds or windows after seeing numbers.

## Do
1. **New script** `experiments/ext_validity/ev_te_detrend.py`.
   - Import and reuse `ev_te_trace` (`load_trace`, `replay_stay`, `longest_valid`, `route_arrays`), `ev_te as S` (`prepare_network`, `estimate_tint`) and `packet.tint`. Do not copy-modify them.
   - Implement the profile (288 time-of-day slots × weekday/weekend, 5-slot circular moving average, training bins only), the additive residual (primary) and the multiplicative residual (secondary).
   - Same α scaling, managed sets R1/R4, ρ ∈ {0.8, 0.9}, active-link reduction recomputed per demand variant.
   - Windows: all non-overlapping contiguous valid training windows of 1, 2 and 4 days, plus the longest valid segment.
   - Per window: T_int (minutes) and the censored flag. Per variant: P(total backlog > 0).
   - Diagnostic: T_int of the bottleneck offered load.
   - Implied h/T_int for h ∈ {5, 15, 30, 60} min.
2. **Tests** in a new file `tests/test_ev_te_detrend.py`:
   - the synthetic sanity test of CARD §8 (24 h sinusoid + AR(1) with 30 min time constant, 5-min bins): raw within 20% of 24h/2π, residual within 30% of 30 min;
   - profile and residual shape checks.
   - Then run `python3 -m pytest -q tests/test_ev_te_detrend.py tests/test_ev_te.py --basetemp=/tmp/evte_dt_pt -o cache_dir=/tmp/evte_dt_cache`. All must pass.
3. **Run.** Write to `results/ext_validity/ev_te/arm_r_detrend/`:
   - `results.json`: every value, plus window lists;
   - `summary.csv`;
   - `README.md`: tables of raw vs additive vs multiplicative T_int per ρ, set and window length; P(Q>0); censored counts; implied h/T_int; and **the CARD reading-rule outcome applied mechanically** (REACHABLE / BOUNDARY / INTERMEDIATE, or pipeline mismatch if the raw longest-segment T_int differs from 283.7/438.9 min by more than 1%).
   - Also report the plain numbers and one paragraph on what they do and do not show. No claims beyond the card.
4. Record the CPU time.

## Final message (Vietnamese)
- The reading-rule outcome.
- The main table (compact).
- The raw-reproduction check.
- The test result.
- Anything ambiguous.
