#!/bin/bash
# Doan Van Tai — GCP truth pipeline; explicitly invoked only after review/lock.
# This file is prepared locally, never executed during the EV-TE coding brief.
set -euo pipefail
cd "${SMR_REPO:-$HOME/smr}"
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
P=.venv/bin/python3
OUT=results/ext_validity/ev_te
MODULE=experiments.ext_validity.ev_te
LOG="$OUT/truth_pipeline.log"
# Exclusive log also prevents a second pipeline from racing write-once outputs.
set -o noclobber
exec 3> "$LOG"
set +o noclobber
exec 1>&3 2>&1
finish() {
    local rc=$?
    trap - EXIT
    echo "PIPELINE_EXIT rc=$rc time=$(date -Is)"
    sync
    sudo -n poweroff || { echo 'POWEROFF_FAILED'; [ "$rc" -ne 0 ] || rc=1; }
    exit "$rc"
}
trap finish EXIT
echo "PIPELINE_START time=$(date -Is)"
"$P" -m "$MODULE" verify-lock
# One invocation; no retries with reduced worker count or partial resumption.
# N/K/R are fixed before lock by the reviewed card/pilot, defaults below.
timeout --signal=TERM --kill-after=60s 9h "$P" -m "$MODULE" run \
    --workers "${WORKERS:-32}" --N "${EV_TE_N:-500}" \
    --K "${EV_TE_K:-128}" --R-dec "${EV_TE_R_DEC:-128}" --R-eval "${EV_TE_R_EVAL:-256}"
# Raw data must be committed/reviewed by the orchestrator before scoring.
echo "TRUTH_DONE raw=$OUT/raw; scoring is a separate authorized stage"
