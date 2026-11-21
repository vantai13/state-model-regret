#!/usr/bin/env bash
# Doan Van Tai — Claude launches two shards on n2-highcpu-32.
# VM poweroff/revert belongs to Claude's driver. No retry/resume here.
set -Eeuo pipefail
if [[ $# != 1 ]]; then
    printf 'Usage: S3_LOCK_SHA256=<sha> bash experiments/letter/s3_ctmc/s3_gcp.sh {0|1}\n' >&2
    exit 2
fi
case "$1" in
    0|0/2) shard=0/2; shard_tag=0_of_2 ;;
    1|1/2) shard=1/2; shard_tag=1_of_2 ;;
    *) printf 'SHARD must be 0, 1, 0/2 or 1/2\n' >&2; exit 2 ;;
esac
: "${S3_LOCK_SHA256:?Set the reviewed S3 lock SHA256 before launching}"
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
export PYTHONDONTWRITEBYTECODE=1
out=results/letter/sweep/s3/runs
mkdir -p "$out"
set -o noclobber
exec 3>"${out}/gcp_shard_${shard_tag}.log"
printf 'PIPELINE_START %s shard=%s workers=15\n' "$(date -u +%FT%TZ)" "$shard" >&3
trap 'rc=$?; printf "PIPELINE_EXIT rc=%s %s\n" "$rc" "$(date -u +%FT%TZ)" >&3' EXIT
python3 -B -u -m experiments.letter.s3_ctmc.runner verify-lock --expected-sha "$S3_LOCK_SHA256" >&3 2>&1
timeout --signal=TERM --kill-after=60s 6h \
    python3 -B -u -m experiments.letter.s3_ctmc.runner run-shard \
    --shard "$shard" --workers 15 --expected-lock-sha "$S3_LOCK_SHA256" >&3 2>&1
