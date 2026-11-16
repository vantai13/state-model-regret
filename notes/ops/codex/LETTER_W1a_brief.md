# Codex brief LETTER-W1a: topology tie audit, numerical lemma check, CTMC saved-data tables (local, light)

From Claude for Doan Van Tai, 16/11/2026. Context: the advisor's review (letter plan) and `results/letter/CARD_W1.md`. Read the card first; its predictions are fixed. Branch `letter` (already checked out).
- cwd: `/home/vantai/state-model-regret`. Shell: `source .venv/bin/activate && source experiments/explore_ctmc/env.sh`.
- **Do not commit. Do not ssh.** Local CPU only, ≤ 8 workers.
- **Do not modify any existing file**, especially locked ones: `experiments/ext_validity/ev_te.py` and everything under `results/explore_ctmc/` or `results/ext_validity/`.
- Write new code in `experiments/letter/` (create it, with `__init__.py`) and outputs in `results/letter/w1a/`.
- Another Codex job (W1b) works in parallel on `experiments/letter/e3_*.py`; do not touch those files.

## Tasks
1. **`experiments/letter/ties_topology.py`: topology tie audit.**
   - For every EV-TE regime that was run (61), rebuild the **test** instances exactly as the locked truth run did: same `ev_te` functions, seed 1000001, N = 500. Verify determinism by reproducing one known quantity (e.g. the instance count) and say how.
   - For each τ and h, compute the twin-predicted cost vectors for pipelines M0_new, M0_old (posterior averaging with K = 128, as in `choose_twins`), P_old and CE_old.
   - Report per (regime, τ, h, pipeline): the share of instances with an exact tie across actions; the share within 1e-9 relative; and the "zero-zero" share (every action predicted at cost 0).
   - Pilot first and estimate CPU time. If the projection exceeds 2 h on 8 workers, run only h ∈ {7, 30}·T_int and τ ∈ {0.3, 3}·T_int, and say so. Claude will move the rest to GCP.
2. **`experiments/letter/lemma_check.py`: numerical check of the lemma and the hybrid proposition** on the regimes of `results/explore_ctmc/cases/asym.json`, using `experiments/explore_ctmc/ctmc.py` (`m0_vhat` with `return_T=True`, `m0_gap`, `evaluate(..., arrays=True)`).
   - (a) For each regime and path/action, $\hat V$ is constant for h ≥ T(x), to machine precision, on a grid beyond $\bar h=\max_x T(x)$.
   - (b) The fresh and stale M0 decisions are identical at all h ≥ $\bar h$.
   - (c) With true s, the hybrid fresh and stale decisions coincide for h > $\hat M/|s|$, where $\hat M=\max|\hat\Delta(\bar h,\cdot)|$ over states and posterior means. Report $\bar h$ and $\hat M/|s|$ in units of T_int.
   - Output a JSON with PASS/FAIL per check and per regime.
3. **`experiments/letter/ctmc_saved_tables.py`: tables from saved CTMC outputs** (read only), from `results/explore_ctmc/runs/*/*.json` and `runs_l72/*/*.json`:
   - per h/T_int bin {<1, 1–4, 4–7, 7–15, ≥15} and per design source: median and q90 of the M0_new tie mass (`tie_mass.c10`), the share with G_S < −0.1, and the median regret of M0_new, M0_old, hybrid_new/old, hybrid_mm1_new/old and static;
   - the sign agreement of `s_mm1` with `s`, and the regret of `hybrid_mm1` in the rows where the sign is wrong.
   - Output CSV + JSON.
4. **Tests:** `tests/test_letter_w1a.py`, small and fast (determinism of the instance rebuild on one small regime; the tie counter on a toy vector; the lemma checker on one regime).
   - Run `python3 -m pytest -q tests/test_letter_w1a.py tests/test_ev_te.py --basetemp=/tmp/lw1a_pt -o cache_dir=/tmp/lw1a_cache`.
5. **`results/letter/w1a/README.md`:**
   - tables;
   - each card prediction (P1–P6) marked as held / did not hold, mechanically;
   - CPU time;
   - one paragraph of plain facts, no claims beyond them.

## Final message (Vietnamese)
P1–P6 outcomes, the main tie table (Abilene vs GÉANT), lemma check results, CPU time, anything ambiguous.
