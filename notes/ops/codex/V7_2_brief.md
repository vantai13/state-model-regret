# Brief V7-2 (Claude → Codex, 17/11/2026): real continuous trace, compatibility audit (no truth run)

Owner: **Doan Van Tai**. Repo `/home/vantai/state-model-regret`, branch `letter`. Shell as usual.

## Rules
- Do not commit. New files only: `experiments/letter/v7_2_*`, `results/letter/v7_2/`.
- Do not modify existing files.
- **Parallel jobs:** V7-1 (`v7_1_*`) and V7-3 (`v7_3_*`). Do not touch their files.
- ssh to `dt4n-gcp` is allowed only if the VM is already RUNNING, and only for read-only listing. Do not start or stop VMs; Claude does that.

## Question
Can the letter's setting be evaluated on a **real, continuous packet trace** (DITL, used in EV-D4b, branch content under `results/ext_validity/ev_d4b/`, data on the VM) with a decision held 1, 2 and 4 hours? The setting is:
- stale and fresh full-state observations that differ only in age;
- the stale twin averaging over the posterior;
- M0, hybrid with rates learned from an earlier part of the trace, the stationary rule, and C_ref from a stochastic reference.

## Tasks
1. Read `results/ext_validity/ev_d4b/REPORT_EV_D4B.md`, `ev_d4c`, their code and data manifests. Summarize in a table:
   - the queue model, the twins, observation types, ages, holds, actions, T_int values;
   - the computed pipelines and how they map to the letter's pipelines;
   - which raw outputs exist.
2. Classify the reuse:
   - (A) already-saved outputs answer the letter's question directly;
   - (B) a new run with existing code plus small adapters is needed;
   - (C) it is not feasible without a new simulator.

   For (B), write a design draft `results/letter/v7_2/DESIGN.md`:
   - trace windows: train on the first part, test on later windows;
   - holds;
   - pipelines;
   - how ŝ is learned from the train part;
   - the C_ref method;
   - a compute estimate from a short local pilot on a small trace slice, if the data is local; otherwise from saved EV-D4b timings.
3. **Do not compute any test outcome.** Claude writes the card before the truth run.

## Final message (Vietnamese)
- the class (A/B/C) with reasons;
- the design summary;
- the compute estimate;
- risks: one trace, load ≤ 0.775, sign-law weakness near τ ≈ T_int.
