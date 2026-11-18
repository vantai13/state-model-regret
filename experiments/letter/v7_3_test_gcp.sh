#!/usr/bin/env bash
# Doan Van Tai — one-shot VM pipeline. Never invoke during implementation tests.
set -Eeuo pipefail
log_open=0
finish() {
    rc=$?
    trap - EXIT
    if [ "$log_open" -eq 1 ]; then
        printf 'PIPELINE_EXIT rc=%s\n' "$rc" >&3
    fi
    sudo -n poweroff || true
    exit "$rc"
}
trap finish EXIT
cd "$HOME/smr"
source .venv/bin/activate
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
log="results/letter/v7_3/test_congested/pipeline.log"
mkdir -p "$(dirname "$log")"
# An existing log is a previous attempt. Refuse it without running anything.
set -o noclobber
exec 3>"$log"
log_open=1
printf 'PIPELINE_START %s\n' "$(date -u +%FT%TZ)" >&3
python3 -m experiments.letter.v7_3_test verify-lock >&3 2>&1
timeout --signal=TERM --kill-after=30s 6h python3 -m experiments.letter.v7_3_test run --workers 30 >&3 2>&1
