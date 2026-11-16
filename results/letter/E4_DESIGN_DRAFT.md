# E4: hybrid correction on GÉANT (DRAFT; Claude, 16/11/2026; to be finalized after wave 1)

**Aim (advisor E4).** Show on a real topology that the fluid twin's long-horizon harm appears, and that the hybrid twin $\arg\min_a[\hat V_a(h,x)+h\hat r_a]$ removes it, with practical $\hat r_a$.
- EV-TE already compares stale and fresh full states that differ only in age, so E4 is age-only by construction.
- Abilene is used only if the wave-1 tie audit shows that its harm is not a tie artifact (card P1).

## Design choices (draft)
**1. Regimes.**
- The 17 confirmatory GÉANT regimes of EV-TE, as the advisor asked ("cùng các regime đã có").
- New test seed 3000001, so the hybrid is evaluated on instances not seen before.
- τ/T_int ∈ {0.3, 1, 3}; h/T_int ∈ {1, 2, 4, 7, 15, 30}.

**2. Separate decisions from evaluation.**
- For each instance, compute the true cost $V_a(h)$ of **every** action (2 or 4), with R_eval CRN rollouts, at every h. Any decision rule (M0, hybrid variants, tie-break variants) is then scored post hoc without new rollouts.
- M1_new still needs separate decision rollouts (R_dec) to avoid winner's curse; C_ref = L(M1_new).

**3. Pipelines:**
- M0 fresh and stale (posterior K = 128);
- hybrid fresh and stale for each $\hat r$ level;
- **tie-break baselines (required after W1a: about 50% zero-zero ties in topology):** M0 with ties broken toward the action with lowest $\hat r$ (same information as the hybrid), and M0 with uniformly random tie-breaking;
- M1_new.

Report which share of the hybrid's gain the tie-break baseline already captures.

**4. $\hat r_a$ levels (topology analogues of the advisor's (i)–(iii)):**
- **(i) Training estimate:** long simulation on the training seed. This is what EV-TE used as $r_a$; label it the "simulator" upper reference, not an operator-available quantity.
- **(ii) Gaussian fluid-queue approximation** per link, from long-run load statistics. For each link $e$ and action $a$:
  - mean $\bar\lambda_{e,a}$;
  - variance $\sigma^2_{e,a}=\sum_j(\beta d_j)^2$ over the ODs routed on $e$;
  - correlation time $T_{e,a}=\sum_j(\beta d_j)^2(\kappa_j/2)/\sigma^2_{e,a}$;
  - approximation $\mathbb E[Q_{e,a}]\approx\sigma^2_{e,a}T_{e,a}/(C_e-\bar\lambda_{e,a})$ for $\bar\lambda<C_e$;
  - then $\hat r_a=\sum_e\mathbb E[Q_{e,a}]$.

  Uses only means, variances and correlation times, which old telemetry provides. **To check:** accuracy against (i) on training, and sign agreement of $\hat r_a-\hat r_{\rm Stay}$.
- **(iii) Crude M/M/1-like:** $\sum_e\rho_{e,a}/(1-\rho_{e,a})$. Only the sign matters.
- **(iv)** (i) × (1 ± 0.1, 0.25, 0.5).
- **(v)** sign-flipped (i).

**5. Report:**
- G_S and regret (% C_ref) per pipeline vs h/T_int;
- tie shares;
- sign agreement of each level.

**6. Compute.**
- EV-TE spent 114k CPU-s for 61 regimes × 4 ages. GÉANT is the heavier part, and per-action costs replace per-pipeline costs.
- Rough estimate: 1–1.5×10⁵ CPU-s, i.e. 1–2 h on the VM scaled to 32 vCPU, then reverted.

**7. Protocol (light).** Code by Codex; Claude writes the predictions card before truth; one run on GCP; raw committed before scoring; independent rescore.

## Open until wave 1 returns
- Whether Abilene enters (tie audit P1–P3).
- Whether level (ii) is worth it, given W1b's MMPP/M/1 ŝ results in the CTMC.
- The final h/τ grid (cost).
