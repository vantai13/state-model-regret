# Brief V7-3 phase A (Claude → Codex, 17/11/2026): night-time consolidation use case on GÉANT, with data, code, training and pilot only

Owner: **Doan Van Tai**. Repo `/home/vantai/state-model-regret`, branch `letter`. Shell as usual.

## Rules
- Do not commit.
- New files only:
  - `experiments/letter/v7_3_*.py`;
  - `tests/test_letter_v7_3*.py`;
  - `results/letter/v7_3/`;
  - data outside Git in `~/papers/data/sndlib/` (or `$SMR_SNDLIB`).
- Do not modify existing files. Reuse `experiments/ext_validity/ev_te.py` and `experiments/letter/e4_geant.py` by import.
- **Parallel jobs:** V7-1 and V7-2. Do not touch their files.
- **No test-night outcome may be computed in this phase.** Claude writes the card after reading your training report.
- No ssh; Claude runs GCP.

## Scenario (fixed by Claude; propose changes in the report, do not apply them)
- **Data:**
  - topology `geant` (SNDlib native);
  - real traffic matrices `directed-geant-uhlig-15min-over-4months-ALL-native.tgz` from SNDlib (check the official URL; open data). Record the checksum and version.
- **Split by calendar date:**
  - **train** = the first 6 weeks of nights;
  - **test** = all later nights;
  - drop days with missing or corrupt TMs, using a rule written before looking at the test nights.
- **Decision:**
  - at 00:00 each night choose **Stay** = all links on with min-hop routing, or **Switch** = a consolidated configuration;
  - hold for h = 6 h; also report h = 1, 2 and 4 h from the same rollouts;
  - switching cost c = 0.
- **Consolidated configuration (from train only):**
  - greedily switch off links in increasing order of mean 00:00–06:00 train load, keeping the graph connected;
  - stop before any link's train-mean night utilization would exceed 0.8 under min-hop rerouting of the affected OD flows;
  - only the flows that crossed removed links change path.
- **Capacity (from train only):** uniform, set so that the busiest link under Stay has its train **daytime** peak utilization at 0.9 (15-min means). Report the resulting night utilizations.
- **Truth model:** the E4/EV-TE per-link fluid-queue simulator.
  - OD demand = the real 15-min TM (piecewise constant) × the two-state fast modulation (1 ± β), β = 0.3, with the E4 fast flip rate (and no slow mode).
  - Note that the fast modulation is synthetic, which is a stated limitation.
- **Initial states:** for each night and instance, warm up from 22:00 with the real TM and an independent seed. Use N = 200 instances per night.
- **Telemetry:**
  - fresh = the full state at 00:00;
  - stale = the full state at 00:00 − τ, with τ ∈ {5, 15} min;
  - stale posterior = K = 64 forward simulations under Stay over τ from Y, using the real TM of that interval (as in E4).
- **Twins:**
  - **M0:** the fluid rollout of each configuration, with the future demand set to the **train-average night profile** (per 15-min slot, weekday or weekend matched), as an operator forecast;
  - **Hybrid:** the M0 gap + h·ŝ, where ŝ = the difference of mean backlog cost rates 00:00–06:00 between the two configurations, from simulating the train nights (operator-available);
  - **Stationary rule:** choose the configuration with the smaller ŝ-based rate;
  - stale and fresh differ only in age.
- **Reference:**
  - C_ref = the fresh true-model decision, using R_dec = 64 rollouts with the actual test-night TM, evaluated on R_eval = 128 separate CRN rollouts per configuration;
  - regret per pipeline and side; G_S per pipeline.

## Tasks (phase A)
1. **Download and parse the TMs.** Write `results/letter/v7_3/data_manifest.json`: source URL, sha256, date range, missing days, and the train/test date lists.
2. **Implement the scenario** with tests:
   - a parser round trip;
   - consolidation connectivity;
   - a capacity rule check;
   - that the CRN pairing gives identical costs for identical decisions;
   - a toy night with a known answer.
3. **Training-only outputs** in `results/letter/v7_3/train/`:
   - the removed-link list;
   - night utilizations for both configurations;
   - T_int of the network backlog under each configuration on train nights (the same estimator as the letter), and h/T_int for 6 h;
   - ŝ and its sign stability across train nights (fraction of nights with the same sign);
   - the M0 tie share on train nights;
   - night nonstationarity (slope of total demand 00:00–06:00).
4. **Pilot:** run 2 train nights end to end with small N to time every component. Project the full test-run CPU-s for N = 200, K = 64, R_dec = 64, R_eval = 128 over all test nights, for 20 workers on n2-standard-32.
5. **Report** in `results/letter/v7_3/PHASE_A_REPORT.md`:
   - everything above;
   - any proposed design change, with its reason;
   - which numbers are training-only.

## Final message (Vietnamese)
- the data summary;
- the consolidation result;
- the train-night h/T_int;
- ŝ sign stability;
- the tie share;
- the compute projection;
- proposed changes;
- files.
