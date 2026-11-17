#!/usr/bin/env bash
# Doan Van Tai — prepared locally only. Usage on VM: bash .../trunc_n2_gcp.sh W CAP
# CAP uses timeout syntax, e.g. 4h. VM: ~/smr, independent .venv, no git needed.
set -euo pipefail
if [[ $# -ne 2 || ! $1 =~ ^[1-9][0-9]*$ || ! $2 =~ ^[0-9]+([.][0-9]+)?[smhd]?$ ]]; then
    echo 'Usage: trunc_n2_gcp.sh WORKERS TIMEOUT_CAP' >&2
    exit 64
fi
workers=$1
cap=$2
if [[ ! $cap =~ [1-9] ]]; then
    echo 'TIMEOUT_CAP must be positive' >&2
    exit 64
fi
cd ~/smr
mkdir -p results/letter/trunc_n2
set -o noclobber
exec > results/letter/trunc_n2/gcp_run.log 2>&1
printf 'PIPELINE_START %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
finish() {
    rc=$?
    trap - EXIT
    printf 'PIPELINE_EXIT rc=%s\n' "$rc"
    sudo -n poweroff || { echo 'POWEROFF_FAILED' >&2; if [[ $rc -eq 0 ]]; then rc=1; fi; }
    exit "$rc"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
sha256sum --check --strict results/letter/trunc_n2/manifest.sha256
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
export PYTHONDONTWRITEBYTECODE=1
timeout "$cap" python3 -m experiments.letter.trunc_n2 run --n-scale 2 --workers "$workers"
python3 -m experiments.letter.trunc_n2 compare
