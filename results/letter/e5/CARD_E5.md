# E5 CARD: long-run rate ordering from a finite recorded demand trace on GÉANT (Claude, 17/11/2026, written before any E5 outcome)

- **Authority:** the author delegated all decisions for the night of 16–17/11 ("bạn cứ thực hiện rồi chạy nếu kết quả tốt thì viết luôn vào paper"). The motivation is two external reviews: the correction needs the long-run action ordering, and on the topology it had only been obtained from long simulation (level i) or a closed form that misorders 3/17 regimes.
- **Question:** can an NDT obtain the long-run ordering from a finite record of measured demand by replaying it through each configuration? How long must the record be?
- **Estimator (replay):** take one recorded demand path of length L (all OD mode processes) and replay it through every action's queues with common random numbers: `ev_te.trajectory(model, dt, burn, steps, seed)` with a 50·T_int burn-in from empty. Then r̂_a(L) = time-average total backlog under action a over the first L. The estimate is correct when argmin_a r̂_a(L) equals argmin_a r_a, where r_a comes from the EV-TE training files (long simulation).
- **Regimes:** the 17 E4 GÉANT regimes (all have two actions).
- **Records:** R = 50 independent records per regime, seed `seed_for(5100001, regime, rep)`, with L/T_int ∈ {3, 10, 30, 100} as prefixes of the same 100·T_int record. The pilot seed 5199999 is used only for timing.
- **Outcomes:**
  - O1: accuracy p(regime, L) = share of records with the correct ordering.
  - O2: implied long-horizon regret per E4/E4b cell (regime × τ × h ∈ {15, 30}·T_int): p·R_i + (1−p)·R_rev, where R_i and R_rev are the saved regrets (worse of the fresh and stale sides) of Hybrid-i and Hybrid-reversed. This assumes the hybrid with the correct ordering behaves like level (i). The saved ±50% magnitude variants support that at h ≥ 7·T_int.
- **Seen before this card:** E4/E4b outcomes, training r_a, and Claude's I27–I28 analyses. Not seen: any E5 record.
- **Forecasts (Claude; not tests):**
  - F1: median accuracy over regimes increases with L.
  - F2: median accuracy ≥ 0.95 at L = 100·T_int and ≤ 0.8 at L = 3·T_int.
  - F3: the lowest accuracies occur in regimes with a small relative rate gap (s0 regimes, gap/min ≤ 1) or a near-empty load.
  - F4: implied expected regret ≤ 0.5% of C_ref in ≥ 85% of the 204 long-horizon cells at L = 100·T_int.
- **Reading rule (exploratory):**
  - If F2 and F4 hold, add one or two sentences to the letter as supporting evidence for an operator-available ordering, with the record length needed.
  - Otherwise, state the record length needed, or that it is not reached, in the limitations.
  - Either way, report the numbers as measured.
- **Protocol:** this card is committed before the code runs. One run; the raw outputs are committed before scoring. No rerun to improve the result.

## Amendment before the main run (Claude, 17/11/2026)
- The timing pilot (seed 5199999; G2_r80_b3_s1 and G2_r90_b6_s1, 2 records each) cost 0.25 CPU-s in total. The native trajectory is much cheaper than estimated.
- Seen from the pilot: the 4 records at L = 100·T_int ordered both regimes correctly. No main-seed record has been computed.
- To make the study more informative at negligible cost: **R = 200 records per regime, L/T_int ∈ {1, 3, 10, 30, 100, 300}** (prefixes of one 300·T_int record).
- F2 now also reads: median accuracy ≥ 0.95 at L = 100·T_int (unchanged), ≤ 0.8 at L = 3·T_int (unchanged). The other forecasts and the reading rule are unchanged.
