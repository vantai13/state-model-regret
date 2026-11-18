# V7-3 DEVIATION 01: anomalous test day 2005-06-27 (Claude, 18/11/2026, author decision)

Owner: **Doan Van Tai**. Written and committed **before any test outcome was read**.

## What happened
- **The run.** The one-shot locked run (lock eba210194, launched 00:34 UTC) had 147/150 records complete after 2 h 52 min.
- **The missing records.** The three missing records are 2005-06-27 for DAY1, DAY2 and DAY3. That day's input is anomalous:
  - the maximum 15-min total GÉANT demand in the window is **1 551 525 Mbit/s**;
  - that is **19.64×** the training-window maximum, 78 984 Mbit/s over the 26 train weekdays;
  - the next-highest test weekday is 2005-06-23 at 1.23×.
- **Why the records were slow.**
  - The simulator's reduction keeps only links whose modulated load can exceed capacity, plus the ODs crossing them.
  - On 06-27 that is 51–52 links and 429–430 ODs, against 5–6 links and 114–133 ODs on 06-23.
  - The 06-23 records took 4 267–4 895 s. With work roughly proportional to links × ODs, a 06-27 record needs on the order of 40 h.
  - The 6-hour cap therefore cannot be met: the run would end INCOMPLETE whether stopped now or at the cap.
- **Author decision (18/11, about 10:35, "Dừng + sửa có khai báo"):**
  - stop the run now;
  - record the locked outcome as **INCOMPLETE**;
  - score the completed records under the amended rule below, labeled as a deviation.

## Exposure before this note
- Per-record CPU and wall times, peak memory and the npz hashes printed in `pipeline.log`.
- The input-only strata in `inputs.json`.
- Input-only analyses of the test matrices:
  - window total demand for all 50 test weekdays;
  - active link and OD counts for 2005-06-23, 06-27, 07-15 and 08-02.
- **No cost, decision, C_ref, regret, G_S or T_int of any test record has been opened.**

## Amended rule (DEVIATION 01, input-only, fixed now)
- **Exclusion.** A test weekday is excluded as a measurement anomaly if its maximum 15-min total demand in the decision window exceeds **2×** the training-window maximum (78 984 Mbit/s).
  - Only 2005-06-27 is excluded.
  - Every threshold between 1.23× and 19.64× gives the same exclusion set, so the threshold is not tuned.
- **Effect on the population.** 49 test weekdays. Strata per regime: S 29 / O 20 (06-27 was O for every regime).
- **What stays unchanged:** the tests H1–H3, the forecasts F1–F7, the thresholds, the populations, the sensitivity analyses and the inclusion rule of `CARD_V7_3.md`.
  - F1 is reported on both 50 and 49 days.
- **Scoring.** A thin wrapper written by Codex calls the locked scorer and rescorer functions on the 147 records with the excluded day removed.
  - It modifies no locked file.
  - It recomputes the exclusion from the test inputs and checks that the completed records are exactly the non-excluded ones.
- **Labels.** Reports and the paper call this an amended analysis, not the original confirmatory run.
  - The paper states that one test day with a measurement anomaly (total demand about 20× the training maximum) was excluded by an input rule.

## Lesson
- The pilot covered only training days, and the card's exclusion rule checked only completeness.
- Future cards on trace data need a pre-declared input sanity rule for spikes, and a cost check on the heaviest input day (pitfall in `experiment-protocol`).
