# Letter wave 2: predictions written before computation (Claude, 16/11/2026)

**Context.** Doan Van Tai, letter. Exploratory, light process. Built on W1a (93168d53) and W1b (age-only E3/E2, 93 regimes, CTMC).

**Seen before this card (preliminary, 92 regimes, Claude):**
- Age-only harm persists (194/217); the age-only/confounded median ratio is 0.96.
- The stale twin at τ ≥ T_int has regret ≈ 0.01%.
- Hybrid with true s: regret 0.013% at 1–4 T_int, ≈ 0 beyond. Hybrid with M/M/1 ŝ: 0.05% at 1–4 T_int.
- **Hybrid is worse than fresh M0 at h < T_int** (0.62–0.75% vs 0.50%). Hybrid ≈ stationary rule at h ≥ T_int.
- MMPP ŝ level (ii) was INVALID everywhere, for two reasons:
  - the sampling step T_int/10 is far above κ, so ρ̂₁ ≈ 0 and κ̂ is meaningless;
  - the locked CTMC chain accepts only a ∈ {3, 6, 7.5}.
- Worst-case hybrid threshold: 380–1618 T_int.

**Rule.** Decisions below are fixed now. No threshold, θ or estimator choice is changed after its outcome.

## A. ŝ level (ii), fixed estimator (implementation fix after an INVALID, not after a regret outcome)
- **Record:** per-bin arrival counts with bin width Δ_b = 0.01 s, over W = 100·T_int, per path, simulated with a fixed seed.
- **Estimates:**
  - λ̂ = mean count / Δ_b;
  - α̂² = Var(count/Δ_b) − λ̂/Δ_b (Poisson correction; floored at 0);
  - κ̂ = 2·Σ_{k≥1} ĉ_k Δ_b / α̂², summing autocovariances until the first non-positive lag.
- **Solver:** an independent MMPP/M/1 stationary-mean solver (`experiments/letter/mmpp.py`), validated against `ctmc.chain(…).r` at the exact parameters to 1e-8 relative.
- **P13.** sign(ŝ_mmpp) = sign(s) in ≥ 95% of regimes with s ≠ 0, and the median |ŝ − s|/|s| ≤ 0.25.
- **P14.** The hybrid with ŝ_mmpp has regret ≤ 0.1% of C_ref at h ≥ 4·T_int in ≥ 95% of rows (age-only, τ = T_int).

## B. Onset-aware hybrid (new candidate correction)
- **Gap:** $\hat\Delta(h,x)+\hat s\,\max(0,h-\theta T_{int})$, with θ ∈ {0.5, 1, 2, 4} and ŝ ∈ {true s, M/M/1}.
- **θ is chosen on the `asym` family** (33 regimes, all ages): minimize the mean regret over all h. It is then **evaluated on `zf_a3_asym` + `zf_a7p5_asym`** (held out).
- **P15 (held-out).** At h < T_int, the onset-aware regret is within +0.05 pp of fresh M0's in ≥ 80% of rows.
- **P16 (held-out).** At h ≥ 4·T_int, it is within +0.05 pp of the plain hybrid's in ≥ 90% of rows.
- If P15 fails, the plain hybrid stays the letter's correction and the short-horizon rule ("use M0 below T_int") stays.

## C. Probabilistic version of the hybrid proposition
- **Bound:** $D(h)=\pi_0\{|\hat\Delta(h,X)|\ge h|\hat s|\}+P\{|\mathbb E[\hat\Delta(h,X)|Y]|\ge h|\hat s|\}$, an upper bound on the mass where hybrid fresh and stale decisions can differ. Compute it alongside the actual disagreement mass (age-only, τ = T_int, true s).
- **P17 (math, must hold).** Actual disagreement ≤ D(h) at every (regime, h).
- **P18 (forecast).** D(h) < 1% by h ≤ 4·T_int in ≥ 80% of regimes.

## D. E1 figure data (descriptive)
- 3 regimes (one each from asym, zf_a3_asym, zf_a7p5_asym, chosen before computing as the first case of each file with s < 0).
- 3 states each: (n = 0, low mode), (n = median under π0, high mode), (n = q95 under π0, high mode).
- Data: $\hat V_a(h,x)$ and $V_a(h,x)$ for h/T_int ∈ [0.1, 30].
- **P19 (math).** $\hat V$ is flat beyond its drain time; $V_a$ grows with slope $r_a$.

## E. CTMC tie-break baseline
- **Variant:** M0 with ties broken toward 1{ŝ < 0} (true s and M/M/1).
- **P20.** At h ≥ T_int, the tie-break variant recovers < 20% of the regret gap between fresh M0 and the hybrid (ties are only about 1–2% in the CTMC). Topology is different (≈ 50% ties): that is E4.
