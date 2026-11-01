#!/usr/bin/env bash
# Doan Van Tai — set up a second machine with the same environment as the local one [AI (Claude) theo ủy quyền].
# Same Python (3.14.5), same pinned wheels (requirements.lock), same g++ major/minor as local (11.4) for the
# lazily compiled native helpers. Run from the synced repo root: bash experiments/explore_mech/remote_setup.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
want_gxx=11.4
if ! command -v uv >/dev/null; then curl -LsSf https://astral.sh/uv/install.sh | sh; fi
export PATH="$HOME/.local/bin:$PATH"
if ! g++ --version 2>/dev/null | head -1 | grep -q " $want_gxx"; then
  sudo apt-get update -y -qq && sudo apt-get install -y -qq g++-11 >/dev/null
  mkdir -p "$HOME/smr-bin" && ln -sf /usr/bin/g++-11 "$HOME/smr-bin/g++"
  echo 'export PATH="$HOME/smr-bin:$PATH"' >> "$HOME/.bashrc"
  export PATH="$HOME/smr-bin:$PATH"
fi
# native dyadic helper needs Boost.Multiprecision headers; same Ubuntu 22.04 package as local
dpkg -s libboost1.74-dev >/dev/null 2>&1 || sudo apt-get install -y -qq libboost-dev=1.74.0.3ubuntu7 libboost1.74-dev=1.74.0-14ubuntu3
uv python install 3.14.5
uv venv -p 3.14.5 .venv --allow-existing
grep -v '^-e ' experiments/explore_mech/requirements.lock > /tmp/smr-req.txt
uv pip install -p .venv/bin/python -r /tmp/smr-req.txt
uv pip install -p .venv/bin/python --no-deps -e .
.venv/bin/python -m experiments.explore_mech.env_check
