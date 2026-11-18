# Card V7-3: held daytime reroute on real GÉANT matrices, congested business hours (Claude, 18/11/2026)

Owner: **Doan Van Tai**. Plan: `letter_smr/briefs/V7_PLAN.md`. Comparison criteria fixed in `letter_smr/briefs/V7_CRITERIA.md` (14c03bf).
Author choices (17/11): daytime scenario; two pre-declared scenarios (`notes/ops/codex/V7_3_congested_decision.md`).
Overnight 17→18/11 the author delegated design decisions to Claude ("bạn có quyền quyết định"). **This card is AI-written under that
delegation, without mentor review or an author forecast.** Machine-readable parameters: `card_v7_3_params.json` (same commit).

**Status: written before any test-day computation.** No test-day traffic intensity, state, cost or outcome has been computed or read.

## What was already seen (exposure)
- **Night (phase A) and provisioned daytime (A2):** training and two-day pilots only. No queueing, ŝ = 0, C_ref = 0, M0 ties 100%.
  These are scope observations. Test days are not run for them: zero queueing holds by construction (offered-load envelope < capacity).
- **Congested training (commit 3b28b2c21):** 26 train weekdays (2005-05-05 … 2005-06-14), N = 200, K = 64, capacity 12 544.525 Mbit/s.
  - Pooled ŝ (Switch − Stay mean-backlog rate): DAY1 −100 492, DAY2 −100 470, DAY3 −5.75 Mbit. Days: 26/26 negative (DAY1, DAY2); 4 negative and 22 zero (DAY3).
  - The pooled values are dominated by overload days. Splitting the train days by the input-only rule below (computed by Claude from
    `day_train/day_utilizations.csv` rescaled to the congested capacity; training data only):

    | Regime | S days | O days | ŝ_S (mean over S days, Mbit) | S days negative / zero | T_int on S days, median / max (s) |
    |---|---:|---:|---:|---|---|
    | DAY1 | 14 | 12 | −320.6 | 14 / 0 | 155 / 501 |
    | DAY2 | 14 | 12 | −314.0 | 14 / 0 | 166 / 478 |
    | DAY3 | 14 | 12 | −0.4 | 1 / 13 | 172 / 412 |

  - M0 tie share in training: fresh 0.70 (DAY1, DAY2) and 0.99 (DAY3); stale ≤ 0.0013 (DAY1, DAY2) and 0.92 (DAY3).
  - On overload train days, T_int is often censored near the window length (no mixing within the window).
- **Congested pilot:** the two pilot train days 2005-05-05 and 2005-05-09 (both overload days), N = 2, full K/R. C_ref, regrets and
  timing seen. Pilot numbers: `day_train_congested/pilot/summary.json`.
- **Data metadata:** test dates and dropped incomplete days in `data_manifest.json`. The test period is 2005-06-15 … 2005-08-31
  (European summer). Nothing about test-day volumes has been opened.
- Older letter results (CTMC W1b, GÉANT E4/E4b, replay E5/E6, V7-1) are known.

## Design (fixed)
- **Days:** every test weekday after the train period that passes the phase-A exclusion rule (complete day, warmup available).
  Expected count from metadata: 50.
- **Regimes:** DAY1, DAY2, DAY3 (A2 selection unchanged; DAY3's Switch path still crosses the busiest Stay link).
- **Per record (regime × test day):** the A2 pipeline unchanged except the date gate.
  - N = 32 decision instances. K = 64 posterior samples per age. R_dec = 64 and R_eval = 128 CRN rollouts.
  - τ ∈ {300, 900} s. h ∈ {1, 2, 4, 6} h from the same rollouts. dt = 0.05 s. c = 0. Exact ties choose Stay.
  - Pipelines (locked): M0 (train-average weekday profile), Hybrid (Δ̂ + h·ŝ with the **pooled** training ŝ), Stationary (Switch iff pooled ŝ < 0).
  - Truth: the day's real 15-min matrices × independent two-state OD modulation (β = 0.3, flip rate 1/s). Fluid per-link queues
    with infinite buffers, as in the letter's GÉANT setup.
  - Reference: C_ref from the reference decision (R_dec rollouts on the day's own matrices, separate stream) evaluated on the
    paired evaluation rollouts.
- **Seeds:** test seed **7312001** (train 7302001 and pilot 7372001 differ; the night phase used 730001/7370001).
- **Extra saved arrays (for pre-declared variants):** M0 predicted costs per instance (fresh; stale per τ, averaged over K),
  the full paired evaluation, the reference-decision rollouts, and one backlog trace per action per day for a descriptive test-day T_int
  (separate seed stream, first-zero integrated autocovariance estimator of training, with censoring flags).
- **One run** on GCP (n2-standard-32, 30 workers), no retry or resume; an interruption gives INCOMPLETE.

## Day strata (input only; computed after the lock and before any truth rollout)
- **S (stable):** for both actions, every link's 15-min offered-load utilization in the window is < 1 at the congested capacity.
  Queueing then comes only from fast fluctuations. This is the regime where a stationary rate is defined.
- **O (overload):** otherwise. Backlogs grow within the window on some link, which may not be on either path of the managed flow.
  Percentages of C_ref are then deflated by uncontrollable backlog. **O results are descriptive only.**

## Metrics (letter Section II definitions)
For a record, instances i = 1…N, horizon h:
- V[i,a,h] = mean of the R_eval paired rollouts for action a. L_{P,σ}(h) = mean_i V[i, a_{P,σ}(i,h), h] for pipeline P and side σ
  (fresh, or stale with age τ). C_ref(h) = mean_i V[i, a_ref(i,h), h].
- Regret R = 100 (L − C_ref)/C_ref. Both-side regret for age τ: max(R_fresh, R_stale,τ).
- G_S^P(τ,h) = L_{P,stale τ} − L_{P,fresh}. **Negative means fresher telemetry hurts.**
  se(G_S) = sample standard deviation over instances of V[i,a_stale] − V[i,a_fresh], divided by √N.
- F_σ(h) = share of instances where M0 chooses Switch on side σ.
- **Evaluable case:** C_ref(h)/h ≥ 12.544525 Mbit, i.e. a mean total backlog of at least 1 ms of service at the congested capacity.
  Non-evaluable cases are counted and reported in Mbit only.
- Physical units, always reported next to percentages: (L − C_ref)/h and G_S/h in Mbit, and divided by the capacity in ms.

## Tests (confirmatory). Population: DAY1 and DAY2, stratum S, evaluable cases
Case = (regime, test day, τ, h) with h ∈ {2, 4, 6} h (h/T_int ≈ 43–140 at the training S-day median T_int). Cases share days and instances
and are not independent; the counts are denominators, not trials.

- **H1. Sign law for the fluid twin (zero-fit).** Predicted sign(G_S^M0) = sign(ŝ_pooled · (F_stale − F_fresh)).
  A case is resolved when F_stale ≠ F_fresh and |G_S^M0| > 2 se.
  - PASS if ≥ 80% of resolved cases agree and there are ≥ 20 resolved cases. NOT_EVALUABLE if fewer than 20. Otherwise FAIL.
- **H2. Correction learned on May–June holds in later weeks.** Hybrid (locked, pooled ŝ) both-side regret ≤ 0.5% of C_ref.
  - PASS if this holds in ≥ 80% of evaluable cases (≥ 20 cases needed, else NOT_EVALUABLE). Otherwise FAIL.
- **H3. Correction improves on the fluid twin where the twin errs.** Among evaluable cases with M0 both-side regret > 0.5%,
  the hybrid's both-side regret is lower.
  - PASS if in ≥ 90% of them. NOT_EVALUABLE if fewer than 10 such cases (then report that the fluid twin had little regret to correct).

For every verdict, report the counts behind it, the clause that decided each case (for H1, the 2·se clause), and the per-horizon split.

## Forecasts (Claude's expectations; not tests, recorded so they can be wrong)
- F1. At least 60% of usable test weekdays are stratum S (summer traffic is lower than in May–June).
- F2. M0 fresh is worse (G_S^M0 < 0, resolved) in ≥ 60% of the DAY1/DAY2 S evaluable (day, τ) cases at h = 6 h.
- F3. Median M0 both-side regret at 6 h is ≥ 5% of C_ref for DAY1/DAY2 S.
- F4. Hybrid and Stationary make the same decision in ≥ 99% of instance-horizon decisions with h ≥ 2 h.
- F5. In stratum O, every pipeline's both-side regret is ≤ 0.5% in ≥ 80% of evaluable cases (C_ref dominated by uncontrollable overload).
- F6. DAY3 S: median |G_S^M0| at 6 h is ≤ 0.5% of C_ref (ŝ ≈ 0, so no long-run effect is expected).
- F7. M0 fresh tie share on DAY1/DAY2 S test days ≥ 50%. With random tie-breaking, G_S^M0 < 0 still holds in ≥ 50% of the cases
  where it holds with Stay ties.

## Pre-declared sensitivity analyses (descriptive; scored from saved raw, no new simulation)
1. M0 tie variants: random tie (expected cost = mean of the two actions' V for tied instances) and ties → Switch.
2. Hybrid with ŝ_S (training S days only: DAY1 −320.6, DAY2 −314.0, DAY3 −0.4 Mbit).
3. h = 1 h cases (h/T_int ≈ 22 at the training S median).
4. Stratum O and DAY3 S: all metrics, descriptive.
5. Test-day T_int and h/T_int (descriptive estimator, with censoring flags).

## Inclusion rule for the paper (fixed now, whatever the outcome)
In the V7-3 version of the letter, Section V gains one paragraph on real GÉANT matrices in congested business hours:
- train (26 weekdays, May–June 2005) and test (later weekdays to 31 Aug) split; strata counts;
- the H1–H3 numbers with their denominators, in the letter's wording (no test language);
- M0 harm share and size at 6 h in % of C_ref and in ms; hybrid and stationary agreement; the tie variant; DAY3 as the s ≈ 0 control;
- one sentence that provisioned daytime and night consolidation show no queueing, so the effect needs congestion;
- one sentence on stratum O (overload-dominated, descriptive).

If H2 fails, the paper says that the correction learned in May–June did not keep regret low in the later weeks, with the numbers.
Which V7 version becomes the letter is decided by the locked criteria (14c03bf), not by these verdicts alone.

## Clarifications before the lock (Claude, 18/11/2026, after code review and before any test-day computation)
The forecasts' populations were not fully specified above. The scorer's readings are adopted as written (forecasts only; tests H1–H3 unchanged):
- F1: a weekday counts as S when it is S for every regime; per-regime S shares are also reported.
- F2: "resolved" uses the H1 resolution (F_stale ≠ F_fresh and |G_S| > 2 se).
- F4: all regimes and strata, h ≥ 2 h, unique decisions (fresh counted once per record and horizon).
- F5: each locked pipeline separately must reach 80%; a joint count is reported descriptively.
- F7: all four horizons of the DAY1/DAY2 S records (the card did not restrict them), with a per-horizon split.
