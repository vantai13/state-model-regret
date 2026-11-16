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
