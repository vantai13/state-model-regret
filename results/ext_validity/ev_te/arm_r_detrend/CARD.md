# EV-TE Arm R-DT — backlog integral time of the unpredictable part of real Abilene traffic (exploratory)

**Provenance.** Doan Van Tai, author delegation 16/11/2026: "tôi muốn vào 3 mức luôn á" (level 2 of the plan after two external AI reviews). Claude wrote this card **before any detrended number was computed**. Codex implements and runs. This is exploratory and outside the EV-TE lock. It changes no locked file, verdict or existing number.

## Question
On the real Abilene traffic matrices (Arm R v2, 5-min bins), the backlog integral time under Stay is 284 min (ρ = 0.8) and 439 min (ρ = 0.9). So TE epochs of 5–60 min sit at h/T_int = 0.011–0.21.

An external review noted that the integral to the first zero of a 24 h sinusoid's autocorrelation is 24 h/2π ≈ 229 min. That is the same order. **Is the measured T_int mostly the diurnal cycle**, which a twin with a forecast already knows? Or does the part that cannot be predicted from the time of day also have a long correlation time?

## Method (fixed now)
1. **Data and parser:** the same as Arm R v2. Absent OD = 0; node-outage bins are missing. Training uses the first two calendar months; the rest is test.
2. **Profile per OD, estimated on training bins only.** Mean by 5-min time-of-day slot, separately for weekdays and weekends (288 slots × 2), smoothed by a centered moving average over 5 slots (circular in the day). Missing bins are skipped.
3. **Residual demand:** $\tilde d_t = d_t - P(t) + \bar d$, clipped at 0. Here $P$ is the profile and $\bar d$ the training mean, so the mean load level is kept.
   - Secondary variant (multiplicative): $\tilde d_t=\bar d\,d_t/P(t)$, with $P(t)$ floored at 1% of $\bar d$.
4. **Replay:** both the raw and the residual demand go through the identical fluid replay under Stay (`replay_stay`). Same scaling α as Arm R v2 at ρ ∈ {0.8, 0.9}, same managed sets R1 = {OD1}, R4 = {OD1, OD2}, same active-link reduction (recomputed for the residual demand).
5. **T_int:** the same estimator (`packet.tint`, to the first zero) on the total backlog.
   - **Windows:** contiguous valid training windows of 1, 2 and 4 days (all non-overlapping ones), plus the longest valid segment (7.5 days, as in Arm R v2). Report the median and the range per window length.
   - **Censored windows** are counted and reported, never dropped silently.
   - **P(total backlog > 0)** per variant; if it is below 1% (as in design rule E0), the variant's T_int is reported as NOT_EVALUABLE.
6. **Diagnostic:** T_int of the bottleneck link's offered load, raw and residual, over the same windows.
7. **Implied h/T_int** for h ∈ {5, 15, 30, 60} min.
8. **Sanity test (unit test, before real data):** a synthetic series of a 24 h sinusoid plus AR(1) noise with time constant 30 min, at 5-min bins. Raw T_int must be within 20% of 24 h/2π, and residual T_int within 30% of the AR(1) integral time (30 min).

## Reading rule (fixed now; primary = additive residual, set R1, both ρ, window = longest segment)
- **REACHABLE:** residual T_int ≤ 15 min at both ρ, and the 1-day and longest-window medians are within a factor 2. Then hourly TE epochs reach h/T_int ≥ 4, the range where the paper's long-horizon checks start to hold, *for a twin that forecasts the diurnal profile*.
- **BOUNDARY:** residual T_int ≥ 60 min at either ρ, or the longest-window median exceeds the 1-day median by more than a factor 2 (dependence growing with window length). The paper's statement that TE epochs lie below T_int stands for the unpredictable part too; practical claims stay scoped to decisions held much longer.
- **INTERMEDIATE:** otherwise. Report the values as they are.
- Raw T_int on the longest segment must reproduce Arm R v2 (283.7 and 438.9 min) within 1%. If it does not, stop and report a pipeline mismatch.

## Forecast (Claude, before computing; not a test)
The residual T_int will be shorter than the raw T_int by a factor ≥ 3. Whether it reaches ≤ 15 min is uncertain (55% INTERMEDIATE, 30% BOUNDARY, 15% REACHABLE): backbone residuals often keep slow components such as week-to-week level changes.

## Not in scope
No new twin evaluation, no change to EV-TE verdicts, no claim that real twins forecast the profile. Any paper text based on this result is labeled descriptive and exploratory.
