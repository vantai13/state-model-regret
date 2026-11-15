#!/bin/bash
# Doan Van Tai — EV-D4c stages on the VM; Claude starts this script in ~/smr.
set -u -o pipefail
L=~/ev_d4c.log
P=.venv/bin/python
STAGE=${1:-}

log() { echo "$* $(date -Is)" >> "$L"; }
step() {
  local name=$1 rc
  shift
  log "STAGE_START stage=$STAGE step=$name"
  if "$@" >> "$L" 2>&1; then
    log "STAGE_DONE stage=$STAGE step=$name"
  else
    rc=$?
    log "FAILED step=$name exit=$rc stage=$STAGE"
    return "$rc"
  fi
}
shutdown() {
  local rc=$1
  sync
  if ! sudo -n poweroff >> "$L" 2>&1; then
    log "FAILED step=poweroff stage=$STAGE"
    [ "$rc" -ne 0 ] || rc=1
  fi
  exit "$rc"
}

case "$STAGE" in train|test) ;; *) echo "Usage: $0 {train|test}" >&2; exit 2 ;; esac
cd ~/smr || { log 'FAILED step=cd'; exit 1; }
source .venv/bin/activate || { log 'FAILED step=activate'; exit 1; }
source experiments/explore_ctmc/env.sh || { log 'FAILED step=env'; exit 1; }
log "STAGE_START stage=$STAGE"
OUT=results/ext_validity/ev_d4c
MODULE=experiments.ext_validity.ev_d4c_panel

if [ "$STAGE" = train ]; then
  step probe_train "$P" -m experiments.ext_validity.packet train --cases "$OUT/probe_cases.json" --out "$OUT/train_probe" --workers "${WORKERS:-32}" || exit $?
  step design "$P" -m "$MODULE" design || exit $?
  step main_train "$P" -m experiments.ext_validity.packet train --cases "$OUT/cases_all.json" --out "$OUT/train" --workers "${WORKERS:-32}" || exit $?
  step select "$P" -m "$MODULE" select || exit $?
  step predict "$P" -m "$MODULE" predict || exit $?
  step describe "$P" -m "$MODULE" describe || exit $?
  log TRAIN_DONE
  log "STAGE_DONE stage=$STAGE"
else
  step verify-lock "$P" -m "$MODULE" verify-lock || shutdown $?
  success=false
  for workers in "${WORKERS:-32}" 16 8; do
    if step "run_workers_$workers" timeout 9h "$P" -m "$MODULE" run "$workers"; then
      success=true
      break
    fi
  done
  if [ "$success" != true ]; then
    log 'FAILED step=run_all_workers'
    shutdown 1
  fi
  step manifest "$P" -m "$MODULE" manifest || shutdown $?
  step score "$P" -m "$MODULE" score || shutdown $?
  log PIPELINE_DONE
  log "STAGE_DONE stage=$STAGE"
  shutdown 0
fi
