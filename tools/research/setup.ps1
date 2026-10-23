# Cài công cụ nghiên cứu cho repo state-model-regret trên Windows (PowerShell 5.1+ hoặc 7+).
# Chạy từ gốc repo:
#   powershell -ExecutionPolicy Bypass -File tools\research\setup.ps1 [-InstallUv] [-Zotero] [-NoLive]
#
#   -InstallUv  cài uv bằng installer chính thức của Astral nếu máy chưa có
#   -Zotero     cài zotero-cli và skill zotero-cli (cần Zotero 7+ desktop)
#   -NoLive     bỏ truy vấn thật tới arXiv/Crossref ở bước kiểm cuối
#
# Lưu ý: script này chưa được chạy thử trên Windows thật (bản bash tương đương đã chạy thử trên Linux).
param([switch]$InstallUv, [switch]$Zotero, [switch]$NoLive)
$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path (Join-Path $PSScriptRoot "..\.."))
Write-Host "Repo: $(Get-Location)"

function Step($msg) { Write-Host "`n== $msg" }

Step "1/5 Kiểm uv (chạy MCP server bằng uvx)"
if (-not (Get-Command uvx -ErrorAction SilentlyContinue)) {
  if ($InstallUv) {
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
  } else {
    Write-Host "Chưa có uv. Cài bằng lệnh chính thức rồi chạy lại script:"
    Write-Host '  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"'
    Write-Host "hoặc chạy lại với -InstallUv"
    exit 1
  }
}
uv --version

Step "2/5 Kiểm Python >= 3.10"
$py = (Get-Command py -ErrorAction SilentlyContinue)
if ($py) { $PY = "py"; $PYARGS = @("-3") } else { $PY = "python"; $PYARGS = @() }
& $PY @PYARGS -c "import sys; assert sys.version_info >= (3, 10), sys.version"
if ($LASTEXITCODE -ne 0) { Write-Host "Cần Python 3.10 trở lên"; exit 1 }

Step "3/5 Môi trường .venv của repo + thư viện nghiên cứu"
$venvPy = ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) { & $PY @PYARGS -m venv .venv }
& $venvPy -m pip install -q --upgrade pip
& $venvPy -m pip install -q -e ".[dev]" -r tools\research\requirements-research.txt
& $venvPy -c "import hypothesis, statsmodels, simpy, pyalex, habanero, bibtexparser; print('Thư viện nghiên cứu: import OK')"
& $venvPy -m pytest -q | Select-Object -Last 1

Step "4/5 Zotero (tuỳ chọn)"
if ($Zotero) {
  uv tool install --upgrade "zotero-mcp-server==0.15.1"
  zotero-mcp install-skill --target claude-user
  Write-Host "Nhớ bật trong Zotero: Settings > Advanced > 'Allow other applications on this computer to communicate with Zotero'."
  zotero-cli config
} else {
  Write-Host "Bỏ qua (thêm -Zotero khi đã cài Zotero desktop)."
}

Step "5/5 Kiểm MCP server trong .mcp.json"
if (-not $env:UNPAYWALL_EMAIL) {
  Write-Host "Gợi ý: đặt email cho Unpaywall (tìm bản open access hợp pháp):"
  Write-Host '  [Environment]::SetEnvironmentVariable("UNPAYWALL_EMAIL", "email-cua-ban@...", "User")'
}
if ($NoLive) { & $venvPy tools\research\check_mcp.py } else { & $venvPy tools\research\check_mcp.py --live }

Write-Host @"

Xong. Bước tiếp theo:
  1. Mở Claude Code tại thư mục repo:  claude
  2. Chấp nhận hai MCP server "arxiv" và "papersearch" khi được hỏi (hoặc gõ /mcp để xem).
  3. Thử: /search-log "value of information stale state routing"
  4. Đọc docs\RESEARCH_TOOLS.md để biết công cụ nào dùng lúc nào.
"@
