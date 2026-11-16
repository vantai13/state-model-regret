# EV-SR: an a-priori test of the default-decision sign rule on new GÉANT regimes (DRAFT design for author review)

Claude, 16/11/2026, at the author's request ("tôi muốn vào 3 mức luôn á", level 3 after two external AI reviews).
- **Status: DRAFT, not locked. Nothing has run.** The card, predictions and lock are written only after the author approves this design.
- Branch `ext/validity`; never merge into main.

## 1. Why
**What is already known.**
- The paper now explains *why* the mean-value twin's harm grows linearly in h: Lemma 1, the twin is horizon-blind.
- Which *sign* the harm takes is so far supported in one exact Markov design (telemetry-age study, 91 regimes).
- At very large ages the default-decision rule is an identity.
- The external review asked for an a-priori test outside the CTMC, on new regimes and seeds, before the rule is used as a headline.

**What could refute the rule.**
- With a correct default, $G_S$ fails to become more negative (or stay flat) as the replaced telemetry ages.
- With a wrong default, $G_S$ has the sign opposite to the zero-fit prediction at large ages.

## 2. The rule for several actions (Claude; math to be checked again at card time)
- **Default action:** $a_{\mathrm{def}}$ is the mean-value twin's choice with no telemetry, i.e. the argmin of its predicted cost averaged over the stationary law under Stay.
- **Long-run best action:** $a^*=\arg\min_a r_a$.
- **Limit as $\tau\to\infty$:** $F_{\mathrm{old}}\to\delta_{a_{\mathrm{def}}}$. The h-linear rate becomes $r_{a_{\mathrm{def}}}-\sum_a r_aF_{\mathrm{new}}(a)=r_{a_{\mathrm{def}}}-\mathbb{E}_{\mathrm{new}}[r]$.
  - **Correct default** ($a_{\mathrm{def}}=a^*$): the rate is $\le0$. Fresh telemetry harms, or is neutral if $F_{\mathrm{new}}=\delta_{a^*}$.
  - **Wrong default:** the sign is that of $r_{a_{\mathrm{def}}}-\mathbb{E}_{\mathrm{new}}[r]$. This is computable zero-fit, and not automatically "help" when there are 4 actions.
- **Where the content lies.** At $\tau=10T_{int}$ this is close to an identity. The tested content is:
  - (i) the **direction along $\tau$** at finite ages;
  - (ii) the **agreement of truth with the zero-fit sign** on new regimes and seeds, outside the finite Markov model.

## 3. Design (reuses the EV-TE code path; the locked `ev_te.py` is imported, not edited)
**Topology and regimes.**
- GÉANT (SNDlib), uniform capacity as in EV-TE. GÉANT is where both signs occur.
- **New regimes.** Managed sets are the next candidates OD4, OD5 and the pair {OD3, OD4}, chosen with the same bottleneck rule. Peak utilization ρ ∈ {0.85, 0.95}; amplitude β ∈ {0.45}; slow ∈ {0, 1}. That makes **12 regimes**, none run in EV-TE.
  - Exclusions are fixed before truth: E0 (P(Q>0) < 1%) and D1 (any action with mean utilization > 1).
  - If fewer than 8 regimes remain, the design adds β = 0.3 before the lock, on the training seed only.
- **Seeds:** training 2, test 2000001, pilot 778. All differ from EV-TE.
- **Ages:** τ/T_int ∈ {0.3, 1, 3, 10}.
- **Horizons:** h/T_int ∈ {7, 15, 30}.
- **Run size:** N = 500, K = 128, R_dec = 128, R_eval = 256, as in EV-TE.

**Pipelines:** M0 (old/new), M1 (old/new), and the default decision.

**Predictions** (training seed only, before truth):
- $a_{\mathrm{def}}$, $a^*$ and the class (correct or wrong default);
- the h-linear predicted level at each (τ, h);
- the zero-fit direction along τ.

## 4. Tests (to be fixed in the card before truth; unit = series or cell; not independent trials)
| ID | Claim | Eligible | Pass if |
|---|---|---|---|
| S1 | Correct default: $G_S$ non-increasing along $\tau\in\{0.3,1,3,10\}T_{int}$, each step ≤ +0.25 pp of $C_{ref}$ | series (regime, h) with a correct default and $\lvert z\rvert\ge0.25$ at $10T_{int}$ | ≥ 80% |
| S2 | Wrong default: sign$(z)$ at $\tau=10T_{int}$ = sign$(r_{a_{\mathrm{def}}}-\mathbb{E}_{\mathrm{new}}[r])$ | cells with $\lvert\text{pred}\rvert\ge0.25$ pp | ≥ 90% |
| S3 | Truth level sign = zero-fit sign at every age, both classes | cells with $\lvert z\rvert,\lvert\text{pred}\rvert\ge0.25$ | ≥ 90% |

- If no cell is eligible for a test, it is NOT_EVALUABLE. That can happen if every new regime has a correct default; GÉANT is chosen to make this unlikely, but it is not guaranteed.
- **What a FAIL means.** The sign rule stays a CTMC result in the paper and is not a headline. No retry or rerun.

## 5. Protocol (same as EV-TE)
1. Codex implements `ev_sr.py` (imports `ev_te`) and tests; training and predictions; a timing pilot.
2. Claude writes the CARD and lock, then commits and pushes.
3. Truth runs once on GCP (VM scaled up, then reverted).
4. The raw data is committed before scoring.
5. Locked scoring, then an independent Codex rescore.
6. Report, DL entry and an AGENTS line.

The paper is updated only after the result, labeled a-priori or exploratory as appropriate.

## 6. Compute (rough, before pilot)
- GÉANT regimes in EV-TE cost 2–12.5k CPU-s each at 4 ages. The age 10·T_int needs a longer posterior simulation.
- **Estimate:** 12 regimes × about 15k CPU-s ≈ 1.8×10⁵ CPU-s, about 2 h on 32 vCPU, plus training. Overnight on GCP is not needed; a few hours suffice.

## 7. Open choices for the author
1. Approve the design as is, or change the regime grid.
2. The thresholds in §4.
3. Whether to run before or after the abstract rewrite. The rewrite does not depend on this result if the sign rule stays labeled as exploratory evidence.
