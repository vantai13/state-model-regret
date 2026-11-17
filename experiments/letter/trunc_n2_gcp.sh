#!/usr/bin/env bash
# Doan Van Tai — same-platform handoff. Usage: bash .../trunc_n2_gcp.sh W CAP
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
printf 'PIPELINE_START %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
finish() {
    rc=$?
    trap - EXIT
    printf 'PIPELINE_EXIT rc=%s\n' "$rc"
    exit "$rc"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
sha256sum --check --strict results/letter/trunc_n2/manifest.sha256
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
export PYTHONDONTWRITEBYTECODE=1
for scale in 1 2; do
    if [[ $scale -eq 1 ]]; then out=raw_n1_vm; else out=raw_n2; fi
    printf 'RUN_START n_scale=%s %s\n' "$scale" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    timeout "$cap" python3 -m experiments.letter.trunc_n2 run \
        --n-scale "$scale" --workers "$workers" --out "results/letter/trunc_n2/$out"
    printf 'RUN_EXIT n_scale=%s rc=0 %s\n' "$scale" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
done
# No scoring or auto-poweroff: retrieve and commit raw first, per the handoff.
