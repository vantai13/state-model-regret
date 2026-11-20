#!/usr/bin/env bash
# Doan Van Tai — X4b one-shot truth. Never execute during preparation/tests.
set -Eeuo pipefail
log_open=0
finish() {
    rc=$?
    trap - EXIT
    if [ "$log_open" -eq 1 ]; then
        printf 'PIPELINE_EXIT rc=%s %s\n' "$rc" "$(date -u +%FT%TZ)" >&3
    fi
    sudo -n poweroff || true
    exit "$rc"
}
trap finish EXIT
cd "$HOME/smr"
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
export SMR_SNDLIB="$HOME/papers/data/sndlib"
log="results/letter/x4b/truth_pipeline.log"
set -o noclobber
exec 3>"$log"
log_open=1
printf 'PIPELINE_START %s host=%s\n' "$(date -u +%FT%TZ)" "$(hostname)" >&3
python3 -m experiments.letter.x4b verify-lock >&3 2>&1
python3 -m experiments.letter.x4b_card verify >&3 2>&1
timeout --signal=TERM --kill-after=30s 2h python3 -m experiments.letter.x4b truth --workers 30 >&3 2>&1
python3 -m experiments.letter.x4b verify-lock >&3 2>&1
python3 -m experiments.letter.x4b_card verify >&3 2>&1
