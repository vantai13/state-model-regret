# EV-D4c — where and why the nowcast sign law fails: τ/T_int band × looping × load (card; hypotheses fixed 15/11/2026 before any EV-D4c output)

Doan Van Tai — **AI (Claude) theo ủy quyền** (`LOCKED_AI_DELEGATED` once `lock.json` exists). The author asked for both EV-D4b follow-ups and for the coding to go to Codex. Claude wrote this card and the score specification; Codex implements the code; Claude reviews, locks and reads the result.

Status: **LOCKED_AI_DELEGATED** (lock after train, before the test seed). The Why/Panel/Rows/Hypotheses sections and the hypotheses below were committed before any EV-D4c probe, train or test existed. The section "Seen before the lock" is added after train. The lock is written after `predict`, before the test seed.

## Why

1. **EV-D4b** (continuous 4 h DITL, load ≤ 0.775) failed D2 at 70%. The post-hoc breakdown by τ/T_int (computed from `posthoc.json`, on rows with |pred30| ≥ 0.25 pp) gives the following.

   Increment sign means the sign of G(30T) − G(10T) against the predicted 20T·ŝ·ΔF.

   | τ/T_int | n | level sign at 30T | increment sign | median increment ratio |
   |---|---|---|---|---|
   | < 0.6 | 87 | 69 | 75 (86%) | 0.61–1.06 |
   | 0.6–1.3 | 28 | 11 | 12 (43%) | −0.46…0.59 |
   | 1.3–4 | 39 | 30 | 30 (77%) | 0.55–0.87 |
   | > 4 | 4 | 0 | 0 | −2.1 |

2. **Wave 3** (looped 15-min MAWI segments, two other traces, load up to 0.975) re-binned the same way (descriptive, computed 15/11 from the committed `ev_d3`/`ev_d3b` data). It passes in every band, **including 0.6–1.3**:
   - level sign 28/28 and increment sign 26/28 in the 0.6–1.3 band;
   - level and increment sign 44/46 above 4.

   So τ/T_int alone does not explain the EV-D4b failure. The candidate causes are:
   - looping (a 15-min loop removes the slower-than-15-min components and makes the rate periodic);
   - load;
   - the trace itself.

EV-D4c tests the band (hypothesis b of the EV-D4b report) and separates the three causes (proposal a, extended by a high-load loop arm). Everything is on the same DITL trace.

## Panel

Three arms. Traffic: paths A/B are the two disjoint 10% flow subsets s0/s1, with one shared phase (audit B3).

| Arm | Series | Regimes | Case seeds |
|---|---|---|---|
| **C** continuous, low load | `ev_d4/series_ditl4h_mod10.npz` (4 h, 10:00–14:00) | R_low: 20 fresh regimes, Sobol seed 20270115 + k (k = stratum index), strata neg 8 / band 4 / pos 8, max(λA, λB) + u ≤ 7.75 | 15000+i |
| **L** looped, low load | `ev_d4/diag_loop15/series_202304121000.npz` (one 15-min file, looped) | **the same R_low** | the same 15000+i |
| **H** looped, high load | the same loop segment | R_high: 20 fresh regimes, Sobol seed 20270126 + k, same strata, 7.75 < max(λA, λB) + u ≤ 9.75 | 17000+i |

C and L differ **only in the series**.

**Telemetry age in units of T_int.**
1. A probe train at τ = 1 s, with the case seed, gives T_int per (arm, regime). Train T_int does not depend on τ: in EV-D4b, T_int was identical across the six τ to 0.1 s.
2. The cases are then τ = round(r·T_int_probe, 2) for r ∈ {0.1, 0.3, 0.5, 0.8, 1.0, 1.2, 2.5, 5.0}.
3. Groups: **low** = {0.1, 0.3, 0.5}, **band** = {0.8, 1.0, 1.2}, **high** = {2.5, 5.0} (high is descriptive only).

**Everything else as in EV-D4b:**
- h ∈ {10, 30} × T_int (train);
- n_inst = 10⁴, spacing 3 T_int, 40 batches, train_T = 10⁵ s, sample_dt = 0.2 s;
- test seed = train seed + 10⁶;
- predictions from train JSON only, with leading term h·ŝ·(F_old − F_new) for the two nowcast twins.

**Feasibility.** Applied by `select` after train, before predictions are looked at:
- a regime is kept in an arm if every r case has T_int not censored and T_int ≤ 240 s;
- C and L keep only regimes that pass in **both** arms, so the comparison stays matched;
- an arm with fewer than 10 kept regimes STOPs (no test for that arm).

## Rows and statistics (score specification)

Rows are the two nowcast twins (fluid_nowcast, ratefluid_nowcast) for cases where both h outputs exist. The filter is the EV-D4b D2 filter: |pred30| ≥ 0.25 pp, with pred30 = 100·pred_abs(h30) / E_stay_test(h30).mean.
- **increment sign:** sign(G_S(h30) − G_S(h10)) = sign(pred_abs(h30) − pred_abs(h10)), using absolute G_S.
- **level sign:** sign(pct_E_stay(h30)) = sign(pred30).
- **increment ratio:** (G_S(h30) − G_S(h10)) / (pred_abs(h30) − pred_abs(h10)).
- **secondary noise filter**, reported only: rows with |G_S(h30) − G_S(h10)| > 2·(se_h10 + se_h30).

A group with fewer than 10 rows is NOT_EVALUABLE. An arm with fewer than 90% of its expected test outputs is INCONCLUSIVE.

## Hypotheses and thresholds

| ID | Statement | PASS iff |
|---|---|---|
| **H1** | arm C, low r: the law predicts the slope sign | increment-sign share ≥ 0.80 |
| **H2** | arm C, band r: EV-D4b's failure replicates on fresh regimes, and the slope itself is wrong | increment-sign share ≤ 0.65 **and** median increment ratio < 0.5 |
| **H3** | cause of the band failure (reading rule below) | — |
| **D6-C** | T12 corrected (no h-linear term in the plug-in effect), arm C | EV-D4b D6 formula, share ≥ 0.90 |
| D6-L, D6-H | the same on the looped arms | exploratory: a looped rate is periodic, hence not mixing, and T12's assumption may not hold |

**H3 reading rule.** Each band group in arms L and H is labelled WORKS (increment-sign share ≥ 0.80), FAILS (≤ 0.65) or MIXED.

| H2 | L band | H band | H3 |
|---|---|---|---|
| PASS | WORKS | any | **LOOPING**: the law breaks at τ ≈ T_int only on continuous traffic; looping hides it |
| PASS | FAILS | WORKS | **LOAD** |
| PASS | FAILS | FAILS | **TRACE_OR_OTHER**: DITL differs from the wave-3 traces |
| anything else | | | **UNRESOLVED** |

Rows share regimes and seeds, so they are correlated (two twins, eight r values per regime). Shares are not independent trials, and no p-values are given.

## Forecast

AI expectation, written before any output; not a threshold:
- **H1 PASS**;
- **H2 PASS**;
- **H3 = LOOPING**, low confidence. The reason: the continuous trace has components slower than T_int that a 15-min loop removes. Their contribution to the O(1) term need not settle by 10T.
- **D6-C PASS**.

One run. No rerun to rescue a verdict.

## Seen before the lock

Train only (probe + main train, finished 15/11 02:44 UTC on the VM n2-standard-32). No D, no test output. `select` kept **20/20 regimes in every arm**; no design exclusion.

| | C | L | H |
|---|---|---|---|
| T_int (s), min / median / max | 61.9 / 125.8 / 181.3 | 9.8 / 19.3 / 26.7 | 19.9 / 74.3 / 144.9 |
| nowcast β₁ (path A, median), r = 0.1 / 0.3 / 0.5 / 0.8 / 1.0 / 1.2 / 2.5 / 5 | .94 / .79 / .64 / .40 / .26 / .14 / −.13 / .00 | .80 / .49 / .30 / .13 / .07 / .03 / .01 / .02 | .93 / .81 / .73 / .60 / .51 / .41 / −.01 / −.20 |
| F_old − F_new, fluid nowcast, h30 (median), same r order | .04 / .05 / .06 / .05 / .06 / .07 / .20 / .38 | .10 / .22 / .26 / .31 / .32 / .31 / .31 / .16 | .06 / .07 / .08 / .05 / .00 / −.01 / .05 / .05 |
| h30 rows with \|pred\| ≥ 0.25 pp (approx., E_stay ≈ train mean_stay·h), low / band / high, of 120 / 120 / 80 | 73 / 83 / 67 | 94 / 106 / 67 | 98 / 105 / 76 |

- Erratum on `seen_before_lock.json`: its `n_filter_rows_h30` divides by the train `mean_stay`, which is a cost **rate**, not the horizon cost, so it counts every row. The approximate counts in the table above use mean_stay·h (checked on EV-D4b: 14.80·3197.6 = 47 312 vs test E_stay 46 677). The score is not affected: it normalises by the test E_stay(h30), as the card says.
- Every group has ≥ 10 rows, so no group is expected to be NOT_EVALUABLE.
- In L the nowcast loses information faster in units of T_int (β₁ .80 already at r = 0.1). In H, F_old − F_new is about 0 at r = 1.0–1.2, so band predictions in H are driven by large ŝ rather than by the share difference.
- Status: **LOCKED_AI_DELEGATED** from the commit that adds `lock.json`.

