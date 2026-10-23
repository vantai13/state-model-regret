#!/usr/bin/env bash
# Cài công cụ nghiên cứu cho repo state-model-regret trên máy cá nhân (macOS, Linux, WSL).
# Chạy từ bất kỳ đâu:  bash tools/research/setup.sh [--install-uv] [--zotero] [--no-live]
#
#   --install-uv  cài uv bằng installer chính thức của Astral nếu máy chưa có
#   --zotero      cài zotero-cli và skill zotero-cli (cần Zotero 7+ desktop)
#   --no-live     bỏ truy vấn thật tới arXiv/Crossref ở bước kiểm cuối
#
# Script chỉ cài vào: .venv của repo, cache của uv, và (nếu --zotero) ~/.claude/skills/zotero-cli.
# Nó không sửa file nào đã commit.
set -euo pipefail

INSTALL_UV=0; ZOTERO=0; LIVE=1
for arg in "$@"; do
  case "$arg" in
    --install-uv) INSTALL_UV=1 ;;
    --zotero) ZOTERO=1 ;;
    --no-live) LIVE=0 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "Tham số lạ: $arg (xem --help)"; exit 2 ;;
  esac
done

cd "$(dirname "$0")/../.."
echo "Repo: $(pwd)"

step() { printf '\n== %s\n' "$1"; }

step "1/5 Kiểm uv (chạy MCP server bằng uvx)"
if ! command -v uvx >/dev/null 2>&1; then
  if [ "$INSTALL_UV" = 1 ]; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
  else
    echo "Chưa có uv. Cài bằng lệnh chính thức rồi chạy lại script:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "hoặc chạy lại với --install-uv"
    exit 1
  fi
fi
uv --version

step "2/5 Kiểm Python >= 3.10"
PY=python3
"$PY" -c 'import sys; assert sys.version_info >= (3, 10), sys.version' \
  || { echo "Cần Python 3.10 trở lên"; exit 1; }
"$PY" --version

step "3/5 Môi trường .venv của repo + thư viện nghiên cứu"
if [ ! -x .venv/bin/python ]; then
  "$PY" -m venv .venv
fi
.venv/bin/python -m pip install -q --upgrade pip
.venv/bin/python -m pip install -q -e ".[dev]" -r tools/research/requirements-research.txt
.venv/bin/python -c 'import hypothesis, statsmodels, simpy, pyalex, habanero, bibtexparser; print("Thư viện nghiên cứu: import OK")'
.venv/bin/python -m pytest -q 2>&1 | tail -1

step "4/5 Zotero (tuỳ chọn)"
if [ "$ZOTERO" = 1 ]; then
  uv tool install --upgrade "zotero-mcp-server==0.15.1"
  zotero-mcp install-skill --target claude-user
  echo "Nhớ bật trong Zotero: Settings > Advanced > 'Allow other applications on this computer to communicate with Zotero'."
  zotero-cli config || echo "zotero-cli chưa nối được Zotero: mở Zotero desktop rồi thử 'zotero-cli config'."
else
  echo "Bỏ qua (thêm --zotero khi đã cài Zotero desktop)."
fi

step "5/5 Kiểm MCP server trong .mcp.json"
if [ -z "${UNPAYWALL_EMAIL:-}" ]; then
  echo "Gợi ý: đặt email cho Unpaywall để tìm bản open access hợp pháp, ví dụ thêm vào ~/.bashrc hoặc ~/.zshrc:"
  echo "  export UNPAYWALL_EMAIL=\"email-cua-ban@...\""
fi
if [ "$LIVE" = 1 ]; then
  .venv/bin/python tools/research/check_mcp.py --live
else
  .venv/bin/python tools/research/check_mcp.py
fi

cat <<'EOF'

Xong. Bước tiếp theo:
  1. Mở Claude Code tại thư mục repo:  claude
  2. Chấp nhận hai MCP server "arxiv" và "papersearch" khi được hỏi (hoặc gõ /mcp để xem).
  3. Thử: /search-log "value of information stale state routing"
  4. Đọc docs/RESEARCH_TOOLS.md để biết công cụ nào dùng lúc nào.
EOF
