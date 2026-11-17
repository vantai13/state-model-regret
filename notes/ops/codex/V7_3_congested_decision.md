# V7-3 daytime: two pre-declared scenarios (Claude, 17/11/2026, author choice)

Owner: **Doan Van Tai**.

**Finding on training data (configuration only, no simulation outcome):**
- The provisioned daytime configuration selects the window 10:15–16:15.
- Capacity follows the phase-A rule (23 128.6 Mbit/s, set by the largest train 15-min daytime peak).
- The busiest Stay link then has a window-mean utilization of 0.488 and a 15-min peak of 0.67. Its fully modulated upper utilization (×1.3) stays below 1.
- So the per-link fluid truth has no backlog, and C_ref = 0 by construction.

**Author's choice (17/11):** run two scenarios, both declared before any test-day outcome.
1. **Provisioned** (as configured): report that no queueing occurs, so there is no effect. This is a scope observation, together with the night result.
2. **Congested business-hours link:** keep the same window, managed flows, paths and train data. Set the uniform capacity so that the busiest Stay link's train-window mean utilization is ρ = 0.9, the ρ definition of Section V.
   - This is a training-only rule, fixed now.
   - The letter states that the effect needs congestion, consistent with s ≈ 0 when there is no queueing.

**Implementation:** Claude implements this after Codex hit its quota (author's rule of 17/11: Claude may code when Codex is out of quota; prose stays with Codex). The new module is `experiments/letter/v7_3_cong.py`; existing files and the provisioned outputs stay unchanged.
