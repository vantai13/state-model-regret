#!/usr/bin/env bash
# Doan Van Tai — V7-1 extraction only. VM lifecycle belongs to Claude.
set -euo pipefail
cd "$HOME/smr"
out=results/letter/v7_1/full
set -o noclobber
exec > "$out/pipeline.log" 2>&1
set +o noclobber
printf 'PIPELINE_START %s\n' "$(date -u +%FT%TZ)"
trap 'rc=$?; printf "PIPELINE_EXIT rc=%s %s\n" "$rc" "$(date -u +%FT%TZ)"; exit "$rc"' EXIT
source experiments/explore_ctmc/env.sh
export PYTHONDONTWRITEBYTECODE=1
export SMR_SNDLIB="$HOME/papers/data/sndlib"
timeout --signal=TERM --kill-after=30s 2h .venv/bin/python -u -m experiments.letter.v7_1_gcp \
    --stage extract --workers 16 --out "$out"
