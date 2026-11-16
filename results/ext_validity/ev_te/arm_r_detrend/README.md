# EV-TE Arm R-DT — result (exploratory; card ecb0f9a3 committed before any detrended number)

Doan Van Tai. Code `experiments/ext_validity/ev_te_detrend.py` (Claude; Codex was at its usage limit), 33 tests PASS. Run 16/11/2026 locally: 41.4 CPU-s.

**Reading-rule outcome (CARD, primary = additive residual, set R1, both ρ, longest segment): BOUNDARY.**
- Raw reproduction check PASS: 283.733817565 and 438.891423818 min, equal to Arm R v2.
- Additive residual T_int on the longest segment: **131.7 min (ρ = 0.8)** and **845.0 min (ρ = 0.9)**.
- 1-day window medians: 55.5 and 32.2 min. The longest-window/1-day ratios are 2.37 and 26.2, so they exceed 2. Removing the time-of-day and weekday/weekend profile does not give a short, stable correlation time; the estimate grows with the window length.

| variant | ρ | 1 d median (n unc/cens) | 2 d | 4 d | longest (7.5 d) | P(Q>0) |
|---|---|---|---|---|---|---|
| raw | 0.8 | 116.0 (10/2) | 188.8 | 204.2 | 283.7 | 0.331 |
| additive | 0.8 | 55.5 (10/2) | 93.1 | 141.4 | 131.7 | 0.161 |
| multiplicative | 0.8 | 22.8 (9/3) | 26.4 | 106.8 | 470.5 | 0.170 |
| raw | 0.9 | 155.5 (7/5) | 281.3 | 394.4 | 438.9 | 0.660 |
| additive | 0.9 | 32.2 (8/4) | 103.7 | 322.3 | 845.0 | 0.387 |
| multiplicative | 0.9 | 38.5 (11/1) | 83.9 | 331.1 | 785.8 | 0.362 |

Sets R1 and R4 give identical Stay backlog series, as expected: the Stay replay does not depend on which OD is managed. Full values are in `results.json` and `summary.csv`.

**What this shows and does not show.**
- **Shows:** on these 2004 Abilene matrices, the part of the traffic that a daily/weekly profile cannot predict still has a backlog integral time of hours. Its estimate keeps growing with the observation window, consistent with slow components such as level changes across days.
- **Does not show:** that real twins forecast the profile; a long-range-dependence exponent; anything about other networks.
- **Claude's forecast** in the card (55% INTERMEDIATE, 30% BOUNDARY) was wrong on the most likely outcome.

## Post-hoc diagnostics (Claude, 16/11/2026; exploratory; the card verdict BOUNDARY is unchanged)
Script `experiments/ext_validity/ev_te_detrend_posthoc.py`; values in `posthoc/posthoc.json`. Set R1, same replay, estimator and windows as above. Residuals use adaptive forecasts built from previous bins only.

| residual around | acf of bottleneck load at 1 h / 1 d | daily-mean CV | T_int 1 d median (ρ .8/.9) | T_int longest (ρ .8/.9) | P(Q>0) (ρ .8/.9) |
|---|---|---|---|---|---|
| none (raw) | 0.64 / 0.25 | 17.5% | 116 / 156 | 284 / 439 | .33 / .66 |
| time-of-day profile (card) | 0.45 / 0.00 | 10.5% | 55 / 32 | 132 / 845 | .16 / .39 |
| trailing 1 h mean | 0.06 / 0.02 | 1.3% | 15 / 26 | 72 / 135 | .05 / .17 |
| trailing 3 h mean | 0.28 / 0.07 | 2.2% | 31 / 67 | 104 / 165 | .09 / .31 |
| trailing 6 h mean | 0.42 / 0.15 | 1.9% | 48 / 118 | 113 / 151 | .16 / .39 |
| trailing 24 h mean | 0.56 / 0.15 | 4.7% | 86 / 152 | 213 / 339 | .23 / .54 |
| profile × yesterday's level | 0.35 / −0.08 | 5.0% | 51 / 77 | 139 / 552 | .11 / .38 |

**Reading (descriptive):**
1. The time-of-day profile removes the daily cycle (acf at 1 d drops from 0.25 to 0), but level changes over hours and days remain (acf at 1 h 0.45; daily-mean CV 10.5%).
2. Around a trailing 1-hour mean, the offered load is nearly uncorrelated beyond minutes (acf at 1 h 0.06). The backlog integral time still stays at 15–26 min on 1-day windows and 72–135 min on the 7.5-day segment.
3. **The remaining scale comes from queue dynamics at high utilization** (rare long busy periods), not from input correlation; no forecast removes it.
4. **Implication (to be worded carefully):** for a twin that tracks the last hour's level, decisions held for about 1 h reach h/T_int ≈ 2–4 on 1-day estimates, and several-hour decisions reach ≥ 7. Multi-day estimates stay at 1–2 h.
