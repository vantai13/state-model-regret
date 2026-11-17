# Card: truncation check N → 2N for the α = 7.5 CTMC regimes (Claude, 17/11/2026)

Owner: **Doan Van Tai**. Requested by the author (17/11, Tier 2 of the v5 review plan: "kiểm N → 2N cho các regime α = 7,5").
Written by Claude before any 2N output exists. Light protocol (numerical verification, not a hypothesis test): the card, one run, raw committed before reading.

## Why
Reviewers (Codex MR1 M4; external reviews 1 and 5) asked whether the finite backlog truncation of the CTMC drives the results.
`ctmc.choose_N` picks N so the matrix-geometric stationary tail mass is ≤ 1e-13 (N ≥ 40, ×1.2 margin). The heaviest-tailed
regimes are those with amplitude α = 7.5 (peak arrival rate ℓ + α close to or above μ). An earlier check (L7.1 V5, α = 6, 4 corners)
changed results by ≤ 1.2e-10 pp. That is the only prior exposure; no α = 7.5 regime has been run at 2N.
Planned exposure before the full run: the local pilot (Codex) reruns the lightest regime Za7p5_u1-2_lA17-2_x-2_k1-20 at 1 × N
(code-path check against the saved raw) and at most two light regimes at 2N for timing. Their 2N outputs are pilot-only and the full
run recomputes them; the pilot report names them.

## Population
All 27 W1b regimes of family `zf_a7p5_asym` (results/letter/w1b/raw/Za7p5_*.json), all five ages
(1 s, 0.1, 0.3, 1, 3 T_int) and all saved horizons. No regime is excluded.

## Method
- Same code path as W1b (`experiments.letter.e3_agediff.prepare_regime` / `evaluate_agediff`, `disagree=False`), with `ctmc.choose_N`
  wrapped to return exactly 2 × its original value in the new script only. Locked files are not modified.
- ŝ levels are taken from the saved W1b raw (`levels`), not re-estimated, so only the truncation changes.
- 2N output is compared with the saved W1b raw (1 × N).

## Expectations (fixed now)
| Quantity | Threshold for "truncation has no effect at reporting precision" |
|---|---|
| Every percentage-of-C_ref field (G_S, regrets of M0, hybrid levels, stationary rule, law prediction) | max abs difference ≤ 1e-6 pp |
| Every cost, rate (r_a, s), T_int and bias field | max relative difference ≤ 1e-9 |
| Discrete fields (decisions, booleans, tie flags, counts) | identical |

**Forecast (Claude, not a test):** max abs difference about 1e-10 pp, as in L7.1 V5; every discrete field identical.
If a threshold is exceeded, the report lists the regimes and fields, and the cause is analysed before any conclusion.

## Inclusion rule for the letter (fixed now)
Whatever the outcome, the CTMC setting sentence in Section V reports the largest change found (in pp of C_ref) for the 27 α = 7.5 regimes.
If a threshold is exceeded, the letter states which reported numbers move and by how much, instead of the "no effect" clause.

## Compute
W1b took 11 072 CPU-s for these 27 regimes at N; 2N is projected at 3–5×, with the heaviest regime
(Za7p5_u3-2_lA31-4_x1-3_k2, N = 3159/9518) on the critical path. Run on GCP dt4n-research-01 resized to n2-standard-32,
then revert to n2-custom-12-49152 and leave TERMINATED (standing rule). One run, no retry; an interruption is INCOMPLETE.
