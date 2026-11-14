# EV-D3a — realistic telemetry age τ (SNMP-like) on the real MAWI trace: card locked before the test seed (14/11/2026)

Doan Van Tai — **AI (Claude) theo ủy quyền** (`LOCKED_AI_DELEGATED`).

**Question.** EV-D2 found effects ≈ 0 at τ = 1 s, because τ ≪ T_int ≈ 78 s. Real telemetry is often polled every 30 s to 5 min. At τ ∈ {30, 300} s (τ/T_int ≈ 0.4 and ≈ 4) on the same real rate structure:
- Do nowcast (age-aware) fluid twins become harmed by fresh telemetry?
- Does the train-only leading-term law predict it?
- Do plug-in twins stay harm-free, as T12 says?

**Panel.** 20 regimes (Sobol seed 20261201; neg 8, band 4, pos 8) × τ ∈ {30, 300} s = 40 cases.
- Trace: MAWI 2025-03-11, flow-sampled s0, Cox arrivals, real time.
- h ∈ {10, 30} × T_int (train); T_int median 72 s.
- Train seed s, test seed s + 10⁶.

**Seen before the lock (train only, no D).**

| | τ = 30 s | τ = 300 s |
|---|---|---|
| Nowcast slope β₁ (median) | 0.83 | −0.33 |
| F_old − F_new, nowcast, h30 (median) | −0.032 | +0.079 |
| F_old − F_new, plug-in | ≈ 0 | ≈ 0 |

The law predicts harm (pred < 0) in 70/80 h30 rows.

**Predictions.** `predictions.csv` (160 rows), from the train JSON only.

| ID | Rows | Threshold |
|---|---|---|
| D1 plug-in null | h = 30 T_int, fluid + ratefluid (80) | G_S ≥ −max(0.25 pp, 2 se) on ≥ 90% |
| D2 nowcast sign | h = 30 T_int, \|pred\| ≥ 0.25 pp | sign agreement ≥ 85% (NOT_EVALUABLE if < 5) |
| D3 nowcast size | h = 30 T_int, nowcast twins (80) | \|G_S − pred\| ≤ max(0.15, 0.3·\|pred\|) + 2 se on ≥ 80% |
| D4 hybrid | h ∈ {10, 30}, ratefluid_nowcast_hybrid_train (80) | G_S ≥ −max(0.1, 2 se) on ≥ 90% |

Fewer than 90% of outputs → INCONCLUSIVE. One run. The test is sharded across the GCP VM and the author's PC; seeds are fixed per (case, h), so the split does not change any number.
