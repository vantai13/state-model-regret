#!/usr/bin/env bash
set -Eeuo pipefail
cd /home/vantai/state-model-regret
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
log=results/letter/x_ctmc_c/truth_pipeline.log
set -o noclobber
exec 3>"$log"
printf 'PIPELINE_START %s host=%s\n' "$(date -u +%FT%TZ)" "$(hostname)" >&3
trap 'rc=$?; printf "PIPELINE_EXIT rc=%s %s\n" "$rc" "$(date -u +%FT%TZ)" >&3' EXIT
python3 -m experiments.letter.x_ctmc_card verify --out results/letter/x_ctmc_c >&3 2>&1
timeout --signal=TERM --kill-after=30s 2h python3 -m experiments.letter.x_ctmc_c truth --workers 8 >&3 2>&1
