#!/usr/bin/env bash
# Doan Van Tai — explicit GCP entry point; no SSH, transfer or poweroff.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
export PYTHONDONTWRITEBYTECODE=1
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
PLAN=${1:-results/letter/sweep/trace/design_ready/plan.json}
DEST=${2:-results/letter/sweep/trace/full}
case "$(realpath -m "$DEST")" in
    "$PWD/results/letter/sweep/trace/"*) ;;
    *) echo 'Output must be under results/letter/sweep/trace' >&2; exit 2 ;;
esac
test -f "$PLAN"
test ! -e "$DEST"
# Refuse to overwrite even the log from a previous attempt.
set -o noclobber
python -u -m experiments.letter.sweep_trace run --plan "$PLAN" --out "$DEST" --workers 15 > "$DEST.log" 2>&1
