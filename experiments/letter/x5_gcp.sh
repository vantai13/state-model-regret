#!/usr/bin/env bash
# Doan Van Tai — X5 one-shot truth. Preparation never executes this script.
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
mkdir -p results/letter/x5_alarm/build
export TMPDIR="$PWD/results/letter/x5_alarm/build"
set -o noclobber
exec 3>results/letter/x5_alarm/truth_pipeline.log
log_open=1
printf 'PIPELINE_START %s host=%s\n' "$(date -u +%FT%TZ)" "$(hostname)" >&3
python3 -m experiments.letter.x5_alarm verify-lock >&3 2>&1
timeout --signal=TERM --kill-after=30s 2h python3 -m experiments.letter.x5_alarm truth --workers 30 >&3 2>&1
python3 -m experiments.letter.x5_alarm verify-lock >&3 2>&1
