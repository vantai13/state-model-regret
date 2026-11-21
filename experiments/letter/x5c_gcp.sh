#!/usr/bin/env bash
# Doan Van Tai — one-shot X5c truth, one arm or ARMS="A B" in one session.
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
requested_arms="${ARMS:-${1:-}}"
case "$requested_arms" in A|B|"A B") ;; *) printf 'Usage: x5c_gcp.sh A|B, or ARMS="A B"\n' >&2; exit 2 ;; esac
cd "${SMR_REPO:-$HOME/smr}"
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
export PYTHONDONTWRITEBYTECODE=1
export SMR_SNDLIB="${SMR_SNDLIB:-$HOME/papers/data/sndlib}"
mkdir -p results/letter/x5c_alarm/build
export TMPDIR="$PWD/results/letter/x5c_alarm/build"
set -o noclobber
overall_rc=0
for arm in $requested_arms; do
    exec 3>"results/letter/x5c_alarm/arm_${arm}/truth_pipeline.log"
    log_open=1
    printf 'PIPELINE_START arm=%s %s host=%s\n' "$arm" "$(date -u +%FT%TZ)" "$(hostname)" >&3
    arm_rc=0
    # Explicit rc capture preserves fail-stop within an arm and lets the other
    # arm run even if this arm fails its independent gate/lock.
    python3 -m experiments.letter.x5c_alarm verify-lock --arm "$arm" >&3 2>&1 || arm_rc=$?
    if [ "$arm_rc" -eq 0 ]; then
        timeout --signal=TERM --kill-after=30s 2h python3 -m experiments.letter.x5c_alarm truth --arm "$arm" --workers 30 >&3 2>&1 || arm_rc=$?
    fi
    if [ "$arm_rc" -eq 0 ]; then
        python3 -m experiments.letter.x5c_alarm verify-lock --arm "$arm" >&3 2>&1 || arm_rc=$?
    fi
    printf 'PIPELINE_EXIT rc=%s arm=%s %s\n' "$arm_rc" "$arm" "$(date -u +%FT%TZ)" >&3
    log_open=0
    exec 3>&-
    if [ "$arm_rc" -ne 0 ]; then overall_rc=$arm_rc; fi
done
exit "$overall_rc"
