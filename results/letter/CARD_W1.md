# Letter wave 1 — predictions written before any new computation (Claude, 16/11/2026)

**Context.** Doan Van Tai, letter for IEEE Networking Letters, following the advisor review of 16/11/2026. Branch `letter` (from `ext/validity`). Exploratory, with light process ("rút gọn process"):
- predictions are fixed here before the code runs;
- no retry or tuning to match them;
- raw outputs are committed before interpretation.

Claude has already seen the saved CTMC outputs (5,768 rows: tie masses and hybrid results under the confounded design, where fresh = full state and stale = backlog only), summarized in `letter_smr/notes/INSIGHTS.md` I9. **Nothing of the topology tie audit, of E3 (age-only) or of the estimated ŝ has been computed.**

## W1a. Topology tie audit (EV-TE test instances, seed 1000001)
Quantities:
- tie rate per pipeline (M0_new, M0_old, P_old, CE_old): the share of decision instances whose twin-predicted costs are equal across actions (exactly, and within 1e-9 relative);
- the "zero-zero" share: every action predicted at cost 0.

Predictions:
- **P1.** Abilene, M0_new: tie share ≥ 30% in at least 24 of the 32 Abilene regimes at h = 30·T_int.
- **P2.** GÉANT, M0_new: tie share < 10% in at least 13 of the 17 confirmatory GÉANT regimes.
- **P3.** In Abilene, M0_old tie share < 5% (posterior averaging rarely gives an exact tie).

If P1 holds, the Abilene harm is largely a tie artifact (the advisor's concern) and Abilene is not used in the letter beyond one sentence.

## W1a. Numerical check of the lemma and the hybrid proposition (CTMC, regimes of `cases/asym.json`)
- **P4 (math, must hold).** For every state, $\hat V_a(h,x)$ is constant for $h\ge T(x)$ (`m0_vhat` drain time). The M0 decisions, fresh and stale, are identical at every $h\ge\bar h=\max_x T(x)$.
- **P5 (math, must hold).** With true $s$, the hybrid fresh and stale decisions coincide for $h>\hat M/|s|$.
- **P6 (descriptive forecast).** The coincidence threshold $\hat M/|s|$ is ≤ 30·T_int in at least 80% of the asym regimes.

## W1b. E3: age-only comparison (stale = full state at age τ; posterior through $e^{Q_0\tau}$), CTMC
- **Regimes:** `cases/asym.json`, `zf_a3_asym.json`, `zf_a7p5_asym.json`.
- **Ages:** τ/T_int ∈ {0.1, 0.3, 1, 3}, plus τ = 1 s.
- **Horizons:** each regime's h grid.
- **P7.** Fresh telemetry still harms the M0 twin when only age differs: G_S < −0.1% at h ≥ 7·T_int in at least 60% of the rows where the confounded design has G_S < −0.1%, at τ = T_int.
- **P8.** The age-only harm is smaller than the confounded harm, with median ratio G_S(age-only)/G_S(confounded) < 1 at τ = 1 s.

## W1b. E2: hybrid twin with ŝ levels, age-only setting
ŝ levels:
- (i) true s;
- (ii) MMPP/M/1 with (λ, α, κ) estimated from a finite telemetry record;
- (iii) M/M/1 ρ/(1−ρ);
- (iv) true s × (1 ± 0.1, 0.25, 0.5);
- (v) a sign-flipped ŝ (worst case).

Predictions:
- **P9.** Levels (i) and (iv): regret ≤ 0.1% of C_ref at h ≥ 4·T_int in ≥ 95% of rows. Multiplicative noise below 100% never flips the sign.
- **P10.** Level (ii): sign(ŝ) = sign(s) in ≥ 95% of regimes. Its regret matches level (i) where the sign is right.
- **P11.** Level (v): G_S ≈ 0, but regret grows ≈ h|s| (I8), so G_S alone is not a quality measure.
- **P12.** At h < T_int, the hybrid regret is not uniformly below M0's (as seen in I10); the practical rule needs h ≳ T_int.
