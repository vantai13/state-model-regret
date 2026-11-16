# E4: the fluid twin and its correction on the GÉANT topology (design for author approval)

Claude, 16/11/2026. It replaces `E4_DESIGN_DRAFT.md` after waves 1–2.
- **Status:** awaiting the author's approval. Nothing has run.
- **Advisor's request (E4):** "Trên GÉANT: lặp lại E2 cho mean-value twin và hybrid twin (cùng các regime đã có). Abilene chỉ dùng nếu sau E1 xác định được con số không bị chi phối bởi quy tắc hòa."

## 1. Why, and what changed after waves 1–2
- **Ties dominate in the topology model.** W1a found that about **50% of the fresh fluid twin's decisions are zero-zero ties**, in Abilene and GÉANT alike. The twin predicts zero cost for every action, and the tie goes to Stay.
  - So the topology result must separate "the correction fixes ties" from "the correction adds the long-run rate".
  - **Abilene is excluded from tests:** it is tie-dominated and its sign is forced by construction. It gets one descriptive sentence at most.
- **The CTMC (W1b) showed:** age-only harm persists; the hybrid with true s or with crude M/M/1 ŝ removes it beyond about T_int; a wrong-sign ŝ is costly.
- **E4 asks whether this survives** a real topology with several actions, synthetic modulated demand, a fluid twin and **operator-available ŝ**.

## 2. Design
- **Regimes:** the **17 confirmatory GÉANT regimes** of EV-TE: managed sets OD1–OD3 and {OD1, OD2}, so 2 or 4 actions; ρ ∈ {0.8, 0.9}; β ∈ {0.3, 0.6}; slow ∈ {0, 1}; uniform capacity, as in EV-TE.
- **Seeds:** training quantities (T_int, r_a, training action shares) are reused from EV-TE training, seed 1. **New test seed 3000001**, so these instances have never been seen.
- **Observation:** stale = full state at age τ, fresh = full state now. **Age-only by construction**, as in EV-TE.
- **Ages:** τ/T_int ∈ {0.3, 1, 3}. **Horizons:** h/T_int ∈ {1, 2, 4, 7, 15, 30}. **Instances:** N = 500 per regime; posterior samples K = 128.
- **Evaluation:**
  - for each instance and **every action**, the true cost $V_a(h)$ from R_eval = 256 CRN rollouts, at every h;
  - every pipeline below is then scored post hoc from the same costs (decision ≠ evaluation);
  - M1_new decisions use separate R_dec = 128 rollouts; C_ref = L(M1_new).
- **Sharding:** each regime is split into 10 chunks of 50 instances, so all 32 vCPUs stay busy. EV-TE's wall time was bound by one 3.5-hour regime.

## 3. Pipelines
| Pipeline | Decision rule (fresh and stale) |
|---|---|
| M0 | argmin of the fluid twin's predicted cost; ties → Stay (as in EV-TE) |
| M0-tie-r̂ | M0, but ties → the action with the lowest r̂ (needs the same information as the hybrid) |
| M0-tie-rand | M0, ties broken uniformly at random (seeded) |
| Hybrid(r̂) | argmin of $\hat V_a(h,x)+h\,\hat r_a$, for each r̂ level |
| Onset-hybrid(r̂) | argmin of $\hat V_a(h,x)+\hat r_a\max(0,h-\theta T_{int})$, **only if W2's held-out tests P15/P16 hold**, with θ as selected in W2 |
| M1_new | the true model on the fresh state (reference) |

**r̂ levels (per action):**
- **(i) Training simulation:** the long-run mean backlog per action from the EV-TE training runs. This is a simulator reference: it shows what the correction can achieve.
- **(ii) Gaussian fluid-queue approximation** from long-run statistics (mean, variance and correlation time of each link's offered load under each action):
  - $\hat r_a=\sum_e\sigma^2_{e,a}T_{e,a}/(C_e-\bar\lambda_{e,a})$;
  - computed from training-period statistics only;
  - its sign agreement with (i) is checked on training data before truth.
- **(iii) Crude per-link M/M/1-type** $\sum_e\rho_{e,a}/(1-\rho_{e,a})$. Only the ordering of actions matters.
- **(iv)** (i) × (1 ± 0.25, 0.5).
- **(v)** Reversed ordering (worst case).

## 4. Tests (thresholds to be fixed in the card before truth; unit = regime × τ cell at h = 30·T_int unless stated)
| ID | Claim | Pass if |
|---|---|---|
| E4-1 | Hybrid (i) removes the horizon-linear part: \|G_S\| ≤ 0.25% C_ref at h ≥ 7·T_int | ≥ 90% of cells |
| E4-2 | Hybrid (i) is near-optimal: regret ≤ 0.5% C_ref (fresh and stale) at h ≥ 7·T_int | ≥ 90% of cells |
| E4-3 | Operator-available ŝ: r̂ (ii) gives the same best long-run action as (i) | ≥ 90% of regimes (checked on training, before truth) |
| E4-4 | Hybrid (ii) is near-optimal: regret ≤ 0.5% at h ≥ 7·T_int | ≥ 80% of cells |
| E4-5 (descriptive) | Share of the M0 → hybrid regret reduction already captured by M0-tie-r̂ | report only |
| E4-6 (descriptive) | M0 regret and G_S vs h/T_int; tie shares; the wrong-ordering cost | report only |

**What a FAIL would mean.** The correction does not transfer to the multi-action fluid topology at that level. The letter then reports the CTMC result and gives the topology as a limitation, with the cause analysed (`result-analysis`) and no rerun.

## 5. Compute
- **CPU:** about 3×10⁴ CPU-s (17 regimes × 3 ages; M1_old is dropped, the most expensive part of EV-TE).
- **Wall:** on the VM at n2-standard-32, sharded, **about 30–60 min**. A pilot on 2 regimes × 1 chunk gives the real figure first.
- **After the run:** revert the VM to n2-custom-12-49152 and stop it.

## 6. Protocol
1. Codex code and tests: r̂ (ii)/(iii) estimators, per-action cost evaluation, all pipelines, sharding, merge.
2. Training-only checks: r̂ (ii) ordering vs (i), tie shares on training.
3. Claude writes the card with fixed thresholds, then the lock (hashes), commit and push.
4. One truth run on GCP.
5. Commit the raw outputs, then score with the locked code, then an independent rescore.
6. Analysis (`result-analysis`), then the letter figure (Fig. 4).

## 7. For the author to decide
1. Approve this design, or change the regime set (e.g. add Abilene as descriptive).
2. Thresholds of E4-1…E4-4 (0.25%, 0.5%, 90/80%).
3. Whether to include the onset-aware hybrid (decided automatically by W2's held-out P15/P16 if you agree).
