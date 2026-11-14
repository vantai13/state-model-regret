# EV-D — realistic arrival processes on an independent packet simulator: card locked before the test seed (14/11/2026)

Doan Van Tai — **AI (Claude) theo ủy quyền** (`LOCKED_AI_DELEGATED`).
- Simulator `packet.py` was written by Codex and reviewed by Claude.
- Claude's review edits: h_mult 30, `spacing_mult`, a CRN estimate of s, a relaxed R² test.
- Pilots on 9 non-panel regimes were seen before this card (`/tmp/evd_pilot*`, summarised in the wave report).

**Questions (E2/E5, P7/P8).** Under non-Markov, asymmetric and heavy-tailed traffic, with realistic twins (backlog and window-rate telemetry, no hidden modes):
1. Does a **plug-in** stale twin (same map on older data) avoid long-h harm? By stationarity F_old = F_new, so the h-linear term vanishes.
2. Does an **age-aware (nowcast)** stale twin show harm?
3. Does the leading-term law h·ŝ·(F_old − F_new), with ŝ and F from the train seed only, predict it?
4. Does the hybrid remove it?

**Panel.** 20 regimes (Sobol seed 20261171; neg 8, band 4, pos 8) × {mmpp2, onoff_exp (K = 8, f = ¼), onoff_pareto (α = 1.5, cap 100)} = 60 cases. h ∈ {3, 10, 30} × T_int (train). 10,000 instants spaced 3 T_int. Train seed s, test seed s + 10⁶.

**Predictions.** `predictions.csv` holds 360 numbers. They use only the train JSON: no D, no test.

| ID | Rows | Threshold |
|---|---|---|
| D1 plug-in null | h = 30 T_int, fluid + ratefluid (120) | G_S ≥ −max(0.25 pp, 2 se) on ≥ 90% |
| D2 nowcast sign | h = 30 T_int, nowcast twins with \|pred\| ≥ 0.25 pp | sign agreement ≥ 85% (NOT_EVALUABLE if < 5) |
| D3 nowcast size | h = 30 T_int, nowcast twins (120) | \|G_S − pred\| ≤ max(0.15, 0.3·\|pred\|) + 2 se on ≥ 80% |
| D4 hybrid | h ∈ {10, 30} T_int, ratefluid_nowcast_hybrid_train (120) | G_S ≥ −max(0.1, 2 se) on ≥ 90% |

- Fewer than 90% of (case, h) outputs → INCONCLUSIVE.
- Percentages use the test E_stay as a denominator only.
- One run; no rerun; no change after the test.
