# Codex brief EV-A run — deploy and run the locked closed-loop panel on GCP

From Claude (orchestrator), 14/11/2026. The VM `dt4n-research-01` is RUNNING with 12 vCPU (ssh alias `dt4n-gcp`).
Your job: deploy, verify, run once, bring the raw results back. **Do not score, do not edit any locked file, do not
change code.** If anything fails, stop and report; do not rerun or patch.

Local worktree (your cwd): branch `ext/ev-a`, already committed (`398f86f8`). Locked files are listed in
`results/ext_validity/ev_a/lock.json`.

## Steps
1. **Sync code and inputs to a fresh remote directory `~/smr_ext`**, excluding `.git` and `results/` except `results/ext_validity/ev_a/{cases.json,grid.json,predictions.csv,lock.json,CARD.md}`. Use rsync over ssh (`-e "ssh -o BatchMode=yes"`). Do not touch the remote `~/smr`; only use its venv `~/smr/.venv`.
2. **Remote checks, before the run:**
   - `sha256sum` of every file in `lock.json` must equal the locked hashes.
   - `python -c` printing the python/numpy/scipy versions, from the remote venv after `source experiments/explore_ctmc/env.sh`.
   - Golden test on the remote: `python -m pytest -q -p no:cacheprovider tests/test_ext_closed_loop.py`. It must pass.
3. **Launch detached**. rsync must finish before the launch; do not put `&` at the end of an `&&` chain:
   `ssh -n -f dt4n-gcp 'cd ~/smr_ext && mkdir -p logs && setsid nohup bash -c "source ~/smr/.venv/bin/activate && source experiments/explore_ctmc/env.sh && python -m experiments.ext_validity.closed_loop run --cases results/ext_validity/ev_a/cases.json --grid results/ext_validity/ev_a/grid.json --out results/ext_validity/ev_a/run01 --workers 12 --cap 3600" > logs/ev_a_run01.log 2>&1 < /dev/null &'`
4. **Monitor** every ~60 s until 420 JSON files exist in `run01/` and no runner process is left. Anchor the pgrep pattern: `pgrep -f '^\S*python -m experiments.ext_validity.closed_loop run'`. Keep the polling output short.
5. **Bring back** `~/smr_ext/results/ext_validity/ev_a/run01/` and `logs/ev_a_run01.log` into the same local paths. Count the statuses (COMPLETED / UNRESOLVED / ERROR) and the total CPU from the JSON files.
6. Do not stop or delete the VM; Claude manages the VM.

## Report back (final message)
The remote versions, the golden-test result, the hash check, wall time, status counts, total CPU, and any error text.
