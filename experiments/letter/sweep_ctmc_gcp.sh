#!/usr/bin/env bash
# Doan Van Tai — S1-A; invoke on the VM as bash .../sweep_ctmc_gcp.sh 0 (or 1).
# Claude owns VM lifecycle. Another job shares it; no automatic poweroff.
set -Eeuo pipefail
if [[ $# != 1 ]]; then
    printf 'Usage: bash experiments/letter/sweep_ctmc_gcp.sh {0|1|0/2|1/2}\n' >&2
    exit 2
fi
case "$1" in
    0|0/2) shard=0/2; shard_tag=0_of_2 ;;
    1|1/2) shard=1/2; shard_tag=1_of_2 ;;
    *) printf 'SHARD must be 0, 1, 0/2 or 1/2\n' >&2; exit 2 ;;
esac
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
export PYTHONDONTWRITEBYTECODE=1
# Parent output retains the first cost model; v2 is the reviewed handoff.
out=results/letter/sweep/ctmc/v2
mkdir -p "$out"
set -o noclobber
exec 3>"${out}/gcp_shard_${shard_tag}.log"
printf 'PIPELINE_START %s shard=%s workers=15\n' "$(date -u +%FT%TZ)" "$shard" >&3
trap 'rc=$?; printf "PIPELINE_EXIT rc=%s %s\n" "$rc" "$(date -u +%FT%TZ)" >&3' EXIT
# run checks sample/pilot/source/dependency and raw checksums before computing.
python3 -B -u -m experiments.letter.sweep_ctmc run --out "$out" --workers 15 --shard "$shard" >&3 2>&1
