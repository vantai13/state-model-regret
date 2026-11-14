# EV-D2 — real backbone rate structure (MAWI) driving the packet simulator: card locked before the test seed (14/11/2026)

Doan Van Tai — **AI (Claude) theo ủy quyền** (`LOCKED_AI_DELEGATED`). Code: `trace_rates.c/.py` and `trace_cox.py` by Codex, reviewed; panel by Claude.

## Data
- **Trace:** MAWI samplepoint-F, 2025-03-11 14:00, 15 minutes (http://mawi.wide.ad.jp/mawi/samplepoint-F/2025/202503111400.html).
  - Streamed and parsed on GCP: 215,748,878 packets, exactly the count MAWI publishes; parse errors 0.08%.
  - Bins of 10 ms.
- **Flow-sampled stream s0:** 5-tuple FNV-1a hash ≡ 0 mod 1000. CoV 4.0 at 10 ms and 2.5 at 1 s; ACF integral time 0.41 s.
- **Arrivals:** Cox process with intensity λ·R(t), where R = s0 / mean(s0) on a 15-minute loop. Each path draws an independent uniform phase.
- **Time scale:** c = 1, i.e. real time.
  - A c = 25 arm was designed but **dropped before the lock**: the train T_int reached about 26 minutes and the mean backlog about 7,000 packets, a pathological regime whose memory cost was impractical.
  - That decision used train statistics only; no test outcome was seen.

## Panel and predictions
- **Panel:** 20 regimes (Sobol seed 20261191; neg 8, band 4, pos 8). h ∈ {3, 10, 30} × T_int (train); median T_int is 78 s. 10,000 instants spaced 3 T_int. Train seed s, test seed s + 10⁶.
- **Predictions:** `predictions.csv` has 120 rows, computed from the train JSON only. The leading-term law is h·ŝ·(F_old − F_new) for the nowcast twins.

## Scoring (identical to EV-D)

| ID | Rows | Threshold |
|---|---|---|
| D1 plug-in null | h = 30 T_int, fluid + ratefluid | G_S ≥ −max(0.25 pp, 2 se) on ≥ 90% |
| D2 nowcast sign | h = 30 T_int, \|pred\| ≥ 0.25 pp | sign agreement ≥ 85% (NOT_EVALUABLE if < 5) |
| D3 nowcast size | h = 30 T_int, nowcast twins | \|G_S − pred\| ≤ max(0.15, 0.3·\|pred\|) + 2 se on ≥ 80% |
| D4 hybrid | h ∈ {10, 30} T_int, ratefluid_nowcast_hybrid_train | G_S ≥ −max(0.1, 2 se) on ≥ 90% |

- **Rule:** fewer than 90% of outputs → INCONCLUSIVE. One run.
- **Limitation:** one 15-minute trace, one sampling stream, and only the rate structure; the trace's packet-level dependence is not preserved.
