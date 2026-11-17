# Handoff brief (Claude → Codex, 17/11/2026): finish TRUNC-N2 on GCP and close R13

Owner: **Doan Van Tai**. Claude is out of budget, so the author asked that Codex continue. Work carefully and report honestly.
Repos:
- research `/home/vantai/state-model-regret` (branch `letter`; push allowed on this branch only);
- letter `/home/vantai/state-model-regret-papers/letter_smr` (local git, **never push**).

Commits: you may commit, under the existing git identity, **with no Co-Authored-By trailer**.
Shell: `source .venv/bin/activate && source experiments/explore_ctmc/env.sh`; `python3` only.

## State at handoff
- **TRUNC-N2 card:** `results/letter/trunc_n2/CARD_TRUNC_N2.md`. Its thresholds are fixed. Phase 1 is done (commit 7f11ec3f): 1×N reproduction locally max rel diff 0.
- **VM:** `dt4n-research-01` is RUNNING at the default shape n2-custom-12-49152 (12 vCPU, 48 GB), ssh alias `dt4n-gcp`. `~/smr` has the code, `results/letter/w1b/raw` and the manifest (verified OK).
- **VM code-path test failed:** the 1×N rerun on the VM differs from the locally produced W1b raw by **at most 2.3e-12 in absolute terms** (cost fields, packet·s). The max relative difference is 1.8, on near-zero values: floating-point platform noise.
  - The VM's 1×N pilot output is copied at `/tmp/vm_n1/`.
  - Do **not** loosen the test; record this as a deviation.
- **R13b** (prose plus the stationary-rule figure style) may still be running in another Codex process: it writes `letter_smr/sections`, `main.tex`, `figures/scripts/fig3*,fig4*` and `notes/R13_report.md`.
  - Do not edit those files until `/tmp/codex_r13b.md` is non-empty (R13b finished).
  - Then read `notes/R13_report.md`.

## Part 1: TRUNC-N2 on the VM (same-platform comparison)
1. Write `results/letter/trunc_n2/DEVIATION_01.md` **before** any 2N output exists. It states:
   - the VM-vs-local platform noise (numbers above);
   - that the primary comparison is therefore **2N on the VM against 1×N on the VM** (same platform), with the card thresholds unchanged;
   - that 1×N VM vs saved W1b is reported separately as platform noise.

   Add an `--out` option (separate raw directories, e.g. `raw_n1_vm/`, `raw_n2/`) to `trunc_n2.py` `run`/`compare` if needed, update the tests and the manifest, run the local tests, then commit and push (deviation and code) before launching.
2. rsync the changed code and manifest to `dt4n-gcp:smr/`. On the VM, run the tests, then launch **detached without auto-poweroff**:
   - `--n-scale 1` on all 27 regimes, then `--n-scale 2`, with `--workers 12` and a 4 h cap each, logging `PIPELINE_START`/`PIPELINE_EXIT rc=`;
   - use `ssh -n -f dt4n-gcp 'cd ~/smr && setsid nohup bash -c "..." > results/letter/trunc_n2/gcp_run.log 2>&1 < /dev/null &'`.

   Expected wall time is about 1.5–2.5 h. Poll the log over ssh every 10 minutes with sleep; do not keep a session open.
3. When done:
   - rsync the raw directories and the log back;
   - compare checksums on both sides;
   - **commit and push the raw before running compare**;
   - then run compare (2N vs VM-1N with the card thresholds; also VM-1N vs saved W1b), and commit `compare.json`/`compare.md` plus a short `REPORT_TRUNC_N2.md` (verdict per field class, arg-max, wall time and CPU, the deviation).
   - If a class fails only on near-zero values, say so with the absolute differences. Do not re-classify after seeing results; analyse the cause.
4. `ssh dt4n-gcp 'sudo -n poweroff'`. Confirm the VM stops: ssh fails, or `gcloud compute instances list` shows TERMINATED. The shape is already the default. If the VM cannot be stopped, say so loudly in the report.
5. Add a decision-log line to `notes/02_decision_log.md` (branch `letter`, after the DL-150 E6 addendum): TRUNC-N2 result, the deviation, and the commits.

## Part 2: letter (after R13b has finished)
1. **Check R13b's report** against its brief `briefs/R13b_brief_prose.md`: every item done, numbers from ledger rows, no Acknowledgment/AI text, abstract 75–100 words, Corollary 1 and the title unchanged. Fix only clear brief violations, and list them.
2. **Truncation sentence:**
   - Replace the marker `% TRUNC_N2 sentence pending ...` with one clause following the card's inclusion rule: doubling the truncation level in the 27 α = 7.5 regimes changes the reported quantities by at most X pp of C_ref (X from the comparison, 2N vs VM-1N, class (a) max). If a threshold failed, write what moves instead.
   - Add the ledger row `C5_R13` via `extend_r13` in `ledger/recompute_letter.py`, recomputed from the committed compare output.
3. **Checks:**
   - `python3 ledger/recompute_letter.py`;
   - `python3 tools/check_numbers.py` (0 unmatched);
   - `python3 tools/verify_letter.py` (0 failed);
   - `latexmk -pdf -interaction=nonstopmode -outdir=build main.tex && cp build/main.pdf main.pdf`;
   - `python3 tools/check_style.py main.pdf`;
   - grep the PDF text for card/forecast/hypothes/pass/fail;
   - look at the rendered pages (pdftoppm) for figure and legend overlap.

   More than 5 pages is acceptable (the author will trim).
4. **02_Code package:**
   - mirror the figure changes into `02_Code/figures/fig2.py`, `fig3.py`, `fig4.py`;
   - add the new numbers to `02_Code/paper_numbers.py`;
   - keep the README in the paper's terms;
   - run the package checks in `tools/pkg2/`;
   - follow `notes/code_organization_refs.md`.
5. **Deliver:**
   - copy `main.pdf` to `/mnt/c/Users/VAN TAI/Downloads/SMR_letter_v6.pdf`;
   - update `ROADMAP.md` (a short R13 status block at the top of "BẮT ĐẦU TỪ ĐÂY");
   - update the project line in `AGENTS.md` (research repo; one short line in the existing letter style);
   - commit the letter folder with the message "R13: ..." (no push).
6. **Never** add an Acknowledgment or any AI disclosure. Never change the title or Corollary 1.

## Final message (Vietnamese)
- the TRUNC-N2 result (max change in pp; verdict per class; the deviation);
- whether the VM is TERMINATED;
- the R13 check outputs, the page count and the abstract word count;
- the paths and commit hashes;
- anything left undone.
