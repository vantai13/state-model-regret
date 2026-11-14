# Codex brief EV-A — exact closed-loop (re-decision) evaluator on ctmc-v1

Author of the brief: Claude (orchestrator), for Doan Van Tai, 14/11/2026. You (Codex) implement and test. Do NOT run any
scored experiment and do NOT touch GCP in this task.

## Ground rules
- Repo root (your cwd): this git worktree, branch `ext/ev-a`. Python env:
  `source /home/vantai/state-model-regret/.venv/bin/activate && source experiments/explore_ctmc/env.sh`
  (`python` exists only after activating; `rg` is not installed — use grep).
- **Read-only:** every existing file, in particular `experiments/explore_ctmc/ctmc.py`. Only ADD the files listed below.
- Do not commit; leave changes in the worktree for review. No network needed.
- Keep it compact (target ≤ 400 lines of code + tests). Reuse `ctmc` helpers; no new frameworks.

## Model (exact, ctmc-v1)
Two independent paths A, B, each a chain over states (n, m), index 2n+m, from `C.chain(load, kappa, N)` (attributes `Q`
sparse generator, `pi`, `r`, `V(hs)` = E[∫_0^h n dt | x]). Actions: Stay → loads (λA+u, λB); Switch → (λA, λB+u).
Truncations NA, NB exactly as in `C.evaluate`: `C.choose_N(lam + u, kappa)`.

Closed loop: decision epochs t_k = kΔ; the chosen action is held on [t_k, t_{k+1}); switching cost c = 0.
Information: fresh pipelines see the full state at t_k; stale pipelines see the two backlogs at t_k − τ (τ = `C.TAU` = 1;
require Δ > τ).

Decision maps are the one-shot pipelines of the contract, re-applied at every epoch, with lookahead h_p. Take them from
`ev = C.evaluate(lamA, lamB, u, kappa, [h_p], c=0, disagree=False, arrays=True)`, `ar = ev['_arrays']` (row 0):
- '11' (fresh, true model): Switch iff dA[x_A] + dB[x_B] < 0
- '10' (fresh, M0):         Switch iff dhA[x_A] + dhB[x_B] < 0
- '01' (stale, true model): Switch iff dAo[y_A] + dBo[y_B] < 0      (y = backlog index)
- '00' (stale, M0):         Switch iff dhAo[y_A] + dhBo[y_B] < 0
Strict inequality, ties → Stay (as `C.pair_sum`).

Long-run average cost rate J = E_stationary[∫_{t_k}^{t_{k+1}} (n_A + n_B) dt] / Δ.

### Exact computation
Dense P_X(a, t) = expm(Q_X(a)·t) (scipy.linalg.expm on the dense generator; n ≤ ~1000), epoch costs
v_X(a) = chain.V([Δ])[0]. Joint laws are 2-D arrays π[x_A, x_B]; paths are independent given the action, so a step is
π' = Σ_a P_A(a)ᵀ (π ∘ M_a) P_B(a).
- Fresh pipelines: chain on x at t_k. Mask M_Sw[x_A,x_B] from the fresh map, M_St = 1 − M_Sw. Step with P(a, Δ). Cost rate
  per step = Σ_a Σ (π ∘ M_a)(v_A(a)[:,None] + v_B(a)[None,:]) / Δ.
- Stale pipelines: chain on (w, a_prev), w = full state at t_k − τ. For each a_prev and each a: mask M_a(w) from the
  stale map at y = backlog(w); φ = P_A(a_prev, τ)ᵀ (π_{a_prev} ∘ M_a) P_B(a_prev, τ) is the law of x at t_k given action a;
  cost += Σ φ ∘ (v_A(a)[:,None] + v_B(a)[None,:]); π_next[a] += P_A(a, Δ−τ)ᵀ φ P_B(a, Δ−τ).
- Initial law: π_Stay,A ⊗ π_Stay,B with a_prev = Stay. Power-iterate until the change in J is < 1e−12 relative and the
  L1 change of the law < 1e−11 (max_iter argument). Report iterations, final residuals, the mass drift before
  renormalisation, and the long-run Switch fraction p.

### Zero-fit prediction (no truth: M0 and stationary quantities only)
For previous action b ∈ {Stay, Switch} let π_b be the product of the two paths' stationary laws under b.
- q_new(b) = P_{x ~ π_b}(dhA[x_A] + dhB[x_B] < 0); q_old(b) = same with backlog marginals of π_b and dhAo, dhBo.
- Two-state action chain: p* = q(St) / (1 − q(Sw) + q(St)). J_pred = (1 − p*)·r_St + p*·r_Sw, where r_St, r_Sw are the
  stationary mean total backlogs (sum over paths).
- Prediction: G_S_CL_pred = J_pred(old) − J_pred(new) = s·(p*_old − p*_new), with s = r_Sw − r_St. This is the Δ ≫ T_int limit.

Compute dhA, dhB with `C.m0_gap(lam, u, kappa, N, [h_p], side)` and dhAo, dhBo with `C.posterior_mean(stay_chain, dh)`,
exactly as `C.evaluate` does, so that they equal ev's arrays bitwise. Use `C.pair_sum` for the q's.

## Files to add
- `experiments/ext_validity/__init__.py`
- `experiments/ext_validity/closed_loop.py`:
  - `closed_loop(case, Delta, h_p, max_iter=...) -> dict`. Gives J and p for '00', '01', '10', '11', plus J_static (the rate of the action with the smaller stationary rate), iterations, residuals and CPU.
  - `zero_fit(case, h_p) -> dict` (no truth).
  - `single_epoch_costs(case, h)`, used by the golden test.
  - CLI: `predict --cases F --grid G --out P` (zero-fit only); `run --cases F --grid G --out DIR --workers N [--shard i/n] [--cap CPU_S]`. The run writes one write-once JSON per (case, Δ, h_p), forks one process per job with RLIMIT_CPU, marks UNRESOLVED/ERROR for dead children, and skips finished jobs. `time --case ...` times one job.
  - A case is `dict(id, parameters=[lamA, lamB, u, kappa], T_int_max)`. The grid is a JSON list of `[Delta_mult, h_p_mult]` in units of T_int_max. Rational h as in `experiments.explore_ctmc.design.rational`.
- `tests/test_ext_closed_loop.py`. Use tiny regimes (N ≈ 20–60) so the file runs in < 60 s.

## Required tests (all must pass)
1. **Golden one-shot.** From the P1 initial law (w ~ π_St⊗π_St, a_prev = St, so x after τ is the contract joint), a single epoch with Δ = h_p = h gives cost == `ev['h'][0]` L00/L01/L10/L11 to ≤ 1e−9 relative. Fresh pipelines start from x ~ π_St⊗π_St.
2. **Constant policy.** Force all-Stay (all-Switch). The stationary law equals π_St⊗π_St (π_Sw⊗π_Sw) and J = r_St (r_Sw) to ≤ 1e−10.
3. Mass drift per iteration ≤ 1e−12.
4. Zero-fit maps equal the evaluate arrays bitwise.
5. **Small Monte Carlo closed-loop check** on one tiny regime (e.g. λA=7, λB=15/2, u=1, κ=1/2, Δ=2, h_p=2). Simulate the closed loop with the same decision maps (uniformisation, CRN not needed), long enough that se is small. Check |J_mc − J_exact| ≤ 4·se for all four pipelines. Runtime < 30 s.

## Report back (your final message)
- Files added, the pytest summary, and the timing of `time` on one regime with NA ≈ NB ≈ 300 (e.g. λA=7, λB=7.25, u=1/2, κ=1/2; Δ = h_p = 3·T_int_max).
- Any deviation from this brief and why.
