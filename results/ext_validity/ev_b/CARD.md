# EV-B — decisions triggered by an alarm (THREATS K5): card, locked before truth (14/11/2026)

Doan Van Tai — **AI (Claude) theo ủy quyền** (`LOCKED_AI_DELEGATED`). Exploration/external validity on ctmc-v1.

**Question.** Real controllers often act after an event, not at a random stationary instant. Under such triggers, does fresh telemetry still harm the horizon-blind twin at long h? Does the zero-fit first-order law, re-weighted to the alarm population, still predict G_S?

**Population.** The decision is taken only when the old backlog of the Stay path A is at or above its stationary q90 (alarm probability ≈ 10%). Path B is unconditioned. Same one-shot pipelines as the contract.

**Panel.** 30 fresh regimes (seed 20261151; neg/band/pos 10 each), 0 overlap with every earlier list, N ≤ 2500. h ∈ {1, 3, 10} × T_int_max.

**Predictions.** `predictions.csv` holds 90 zero-fit numbers G_S_pred, computed from M0, the stationary g and the alarm weights only.

| ID | Condition | Threshold |
|---|---|---|
| B1 | h = 10 T_int, all 30 rows | \|G_S − pred\| ≤ max(0.1 pp, 5% \|pred\|) on ≥ 90% |
| B2 | h = 10 T_int, rows with \|pred\| ≥ 0.25 pp | sign(G_S) = sign(pred) on ≥ 90% (NOT_EVALUABLE if < 5 rows) |

- The tolerance is relative, following the lesson of DL-142 S1 (an absolute 0.1 pp was too tight for large harm).
- Descriptive only: h = 3 T_int agreement; whether harm present without the alarm is kept under it.
- **Reading.** B1 and B2 PASS means harm and its zero-fit law carry over to event-triggered decisions.
