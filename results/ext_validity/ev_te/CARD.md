# EV-TE CARD — state–model regret on real WAN topologies (locked before truth)

- **Author approval.** Doan Van Tai approved the design ("oke", 15/11/2026, `DESIGN.md`) and delegated the run ("bạn tự chạy kiểm tra tất cả").
- **Roles.** Claude wrote this card (orchestrator, under author delegation). Codex implemented the code (`notes/ops/codex/EV-TE_brief.md`, report `EV-TE_codex_report.md`).
- **Status.** Exploration on branch `ext/validity`, never merged into main. No mentor review. Author expectations before the run: none recorded.
- **What was seen before this lock:**
  - training-seed outputs only: seed A = 1, comprising $r_a$, $T_{int}$, $P(Q>0)$, action shares $F$ and `predictions.csv`;
  - a cost-free timing pilot on seed 777 (`timing.json`; it writes no costs).
- **Not seen:** no truth-seed (B = 1000001) value has been computed or seen.

## 1. Design (as approved, made precise in the brief)
**Topologies** (SNDlib):
- Abilene: real capacities.
- GÉANT: SNDlib gives no installed capacity, so a uniform 10000 Mb/s is used (limitation).

**Model.**
- Fluid offered-load links; cost $\sum_e\int Q_e\,dt$; switching cost $c=0$.
- Stay = min-hop path; Switch = second path (Yen $k=2$).
- Managed sets OD1, OD2, OD3 and {OD1, OD2}, chosen at the bottleneck $e^*$ under all-Stay routing:
  - Abilene: IPLSng→ATLAng; OD1–3 = CHINng_LOSAng, CHINng_HSTNng, CHINng_ATLAng.
  - GÉANT: ch1.ch→at1.at; OD1–3 = ch1.ch_de1.de, ch1.ch_se1.se, ch1.ch_at1.at.
- Per-OD two-state modulation, rate $d(1\pm\beta)$, $\kappa=1$ (fast).
  - With `slow=1`, ODs at odd demand rank use $\kappa=0.1$.
  - $\rho\in\{0.8,0.9\}$ (peak mean utilization under Stay); $\beta\in\{0.3,0.6\}$.
  - This gives 64 regimes.

**Information.** Stale = full state $(Q,\text{modes})$ at age $\tau$; fresh = the same at age 0, so the two differ **only in age**.

**Grids.**
- $\tau/T_{int}\in\{0.1,0.3,1,3\}$; $h/T_{int}\in\{1,2,4,7,15,30\}$.
- $T_{int}$ comes from `packet.tint` on training (range 0.293–96.6 fast time units).
- $dt=\min(0.05,T_{int}/40)$.

**Pipelines** (code `PIPES`): `M0_new` (= P_new = CE_new), `M0_old` (posterior averaging, $K$ samples), `P_old`, `CE_old`, `M1_new`, `M1_old`.

**Evaluation.**
- $R_{eval}$ rollouts with common random numbers from $X$.
- M1 decisions come from independent rollouts.
- $C_{ref}=L(\text{M1\_new})$.

**Fixed run parameters** (from the pilot):
- $N=500$ instances per regime, $K=128$, $R_{dec}=128$, $R_{eval}=256$;
- 32 workers on n2-standard-32;
- wall cap 9 h (pipeline `timeout`);
- projection about 1.9×10⁵ CPU-s.
- One invocation only, with **no retry, resume or rerun**. If the run is interrupted, it is INCOMPLETE.

## 2. Exclusions and pre-lock decisions (training seed only)
- **E0 (design rule $P(Q>0)<1\%$).** G1_r80_b3_s0, G2_r80_b3_s0 and G3_r80_b3_s0 are not run (0.925%, 0.971% and 0.990%).
- **D1 (Claude, 16/11).** 12 GÉANT regimes have an action whose mean link utilization exceeds 1: G1_r90_* with action 1, G4_r80_* with action 3, and G4_r90_* with actions 1 and 3.
  - Proposition 1 needs finite stationary rates for every action.
  - These regimes are **run and reported descriptively, but are not eligible for H1–H4** (score flag `stationary_rate_valid`).
  - This leaves **49 confirmatory regimes × 4 ages = 196 cells**.
- **D2 (Claude, 16/11).** Arm R (`ev_te_trace.py`) is descriptive and outside this lock. A review found that:
  - the TM files omit OD pairs with zero traffic (absent entries are small ODs, present median 0.03–0.26 Mb/s, minimum 0.0133);
  - about 13% of bins have a whole-node outage.

  The Arm R parser will be corrected (absent = 0; node-outage bins = missing) and re-trained in a new folder after this lock. The old `arm_r/` stays as history.

## 3. Pre-registered tests (unit = cell = regime × τ; counts are denominators, not independent trials)
**Notation.**
- $z=100\,G_S/C_{ref}$ at $h=30T_{int}$.
- pred = $100\cdot h_{30}\sum_a r_a[F_{old}(a)-F_{new}(a)]/C_{ref}(h_{30})$.
- $\Delta_{meas}=100[G_S(30)-G_S(7)]/C_{ref}(h_{30})$, with a paired se over instances.
- $\Delta_{pred}=100\{h_{30}\,\text{slope}(h_{30})-h_7\,\text{slope}(h_7)\}/C_{ref}(h_{30})$.

| ID | Claim | Eligible (and `stationary_rate_valid`) | Pass if |
|---|---|---|---|
| H1 | sign$(z_{M0})$ = sign(pred$_{M0}$) | $\lvert z\rvert\ge0.25$ and $\lvert\text{pred}\rvert\ge0.25$ | ≥ 90% of eligible |
| H2 | sign$(\Delta_{meas})$ = sign$(\Delta_{pred})$ for M0 | $\lvert\Delta_{pred}\rvert\ge0.25$ pp and $\lvert\Delta_{meas}\rvert\ge2$ se | ≥ 90% |
| H3 | $\lvert\Delta_{meas}-\Delta_{pred}\rvert\le\max(0.25,\,0.25\lvert\Delta_{pred}\rvert,\,2\,\text{se})$ for M0 | as H2 | ≥ 80% |
| H4 | plug-in: $\lvert\Delta^P_{meas}\rvert\le\max(0.25,\,2\,\text{se})$ | all valid cells | ≥ 90% |

- If no cell is eligible, the verdict is NOT_EVALUABLE.
- The scoring code is `ev_te.score` as locked (`hypothesis_counts`).

**Descriptive only** (no verdict):
- the share of cells with $z<-0.1\%$ for M0, P and CE;
- $z$ against $\tau$;
- $G_M$, $\Gamma$ and the CE twin;
- slow vs fast;
- the D1 regimes;
- Arm R.

## 4. Forecasts (Claude, written before truth; not tests)
- **H4 should pass.** In this stationary model the plug-in twin's stale and fresh observations have the same marginal law, so Corollary 1 applies directly. A failure would point to a code or numerical problem, or to an increment that has not converged by $7T_{int}$.
- **H1 and H2 are uncertain.**
  - The M0 twin's action shares may still change between $7T_{int}$ and $30T_{int}$, which moves $B$.
  - In Abilene every Switch action removes all long-run queueing ($r_{Switch}=0$), so the sign of $s$ is the same in all Abilene regimes. Sign variety comes only from GÉANT.
- **H3 is the hardest test** (magnitude within 25%).
- **Arm R** (strict-subset train estimate before the parser fix): $T_{int}\approx115$ min. So real 5–60 min TE epochs lie at $h/T_{int}<1$, the transient regime where the paper's long-horizon law is not the operative description.

## 5. Protocol after the lock
1. Commit and push the code, training outputs, predictions, this card and `lock.json`.
2. Run truth on GCP once (`ev_te_pipeline.sh`; `verify-lock` first; the VM powers off).
3. rsync `raw/` back and commit the raw data **before** scoring.
4. Score with the locked `ev_te.score`.
5. Codex runs an independent rescore (stdlib/numpy only, no `ev_te` import).
6. Write `REPORT_EV_TE.md`, DL-149 and an AGENTS line.
