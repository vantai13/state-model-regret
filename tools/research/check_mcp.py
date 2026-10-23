#!/usr/bin/env python3
"""Kiểm tra các MCP server khai báo trong .mcp.json có khởi động được không.

Scientific purpose: không có. Đây là công cụ hạ tầng (Lane B): nó trả lời câu hỏi
"server có chạy và có đúng các tool mình nghĩ không?" trước khi dùng nó để tìm paper.

Cách dùng (chạy từ gốc repo):
    python tools/research/check_mcp.py            # chỉ handshake + liệt kê tool
    python tools/research/check_mcp.py --live     # thêm một truy vấn thật mỗi server (cần Internet)

Script chỉ dùng thư viện chuẩn, chạy được trên Windows, macOS, Linux.
Nó cũng kiểm rằng mọi luật "deny" mcp__... trong .claude/settings.json trỏ tới tool có thật,
để một luật chặn bị gõ sai tên không lặng lẽ mất tác dụng.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_VERSION = "2025-06-18"

# Một truy vấn chỉ-đọc cho mỗi server khi chạy --live. Chủ đề lấy từ RQ của repo.
LIVE_CALLS = {
    "arxiv": ("search_papers", {"query": "Lindley recursion queue transient", "max_results": 2}),
    "papersearch": ("search_crossref", {"query": "value of information routing stale state", "max_results": 2}),
}

_VAR = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")


def expand(value: str) -> str:
    """Mở rộng ${VAR} và ${VAR:-default} giống cú pháp của Claude Code."""
    return _VAR.sub(lambda m: os.environ.get(m.group(1)) or (m.group(2) or ""), value)


class Server:
    def __init__(self, name: str, spec: dict):
        self.name = name
        cmd = expand(spec["command"])
        exe = shutil.which(cmd)
        if exe is None:
            raise FileNotFoundError(f"không tìm thấy lệnh '{cmd}' trên PATH (cài uv: xem docs/RESEARCH_TOOLS.md)")
        args = [expand(a) for a in spec.get("args", [])]
        env = dict(os.environ)
        env.update({k: expand(v) for k, v in spec.get("env", {}).items()})
        self.proc = subprocess.Popen(
            [exe, *args], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=env, text=True, encoding="utf-8", bufsize=1,
        )
        self.lines: queue.Queue[str] = queue.Queue()
        self.stderr_tail: list[str] = []
        threading.Thread(target=self._pump, args=(self.proc.stdout, self.lines), daemon=True).start()
        threading.Thread(target=self._pump_err, daemon=True).start()
        self._id = 0

    @staticmethod
    def _pump(stream, q):
        for line in stream:
            q.put(line)

    def _pump_err(self):
        for line in self.proc.stderr:
            self.stderr_tail = (self.stderr_tail + [line.rstrip()])[-15:]

    def send(self, method: str, params: dict | None = None, notify: bool = False):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        if not notify:
            self._id += 1
            msg["id"] = self._id
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()
        return None if notify else self._id

    def wait(self, req_id: int, timeout: float) -> dict:
        deadline = time.monotonic() + timeout
        while True:
            left = deadline - time.monotonic()
            if left <= 0:
                raise TimeoutError(f"quá {timeout:.0f}s không có phản hồi")
            if self.proc.poll() is not None and self.lines.empty():
                raise RuntimeError("server đã thoát. stderr:\n  " + "\n  ".join(self.stderr_tail))
            try:
                line = self.lines.get(timeout=min(left, 0.5))
            except queue.Empty:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue  # bỏ qua dòng log lạc vào stdout
            if msg.get("id") == req_id:
                if "error" in msg:
                    raise RuntimeError(f"lỗi JSON-RPC: {msg['error']}")
                return msg["result"]

    def request(self, method, params=None, timeout=60.0):
        return self.wait(self.send(method, params), timeout)

    def close(self):
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()


def mcp_rules(kind: str) -> dict[str, set[str]]:
    """Luật allow/deny dạng mcp__<server>__<tool> trong .claude/settings.json, gom theo server."""
    path = ROOT / ".claude" / "settings.json"
    if not path.exists():
        return {}
    rules = json.loads(path.read_text(encoding="utf-8")).get("permissions", {}).get(kind, [])
    out: dict[str, set[str]] = {}
    for rule in rules:
        m = re.fullmatch(r"mcp__(.+?)__(.+)", rule)
        if m:
            out.setdefault(m.group(1), set()).add(m.group(2))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--live", action="store_true", help="gọi thêm một truy vấn thật (cần Internet)")
    ap.add_argument("--only", nargs="*", help="chỉ kiểm các server có tên này")
    ap.add_argument("--init-timeout", type=float, default=240.0,
                    help="giây chờ khởi động; lần đầu uvx phải tải package nên có thể lâu")
    ns = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):  # console Windows mặc định không phải UTF-8
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    config =json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]
    deny, allow = mcp_rules("deny"), mcp_rules("allow")
    failures = 0
    for name, spec in config.items():
        if ns.only and name not in ns.only:
            continue
        print(f"\n== {name}: {spec['command']} {' '.join(spec.get('args', []))}")
        srv = None
        try:
            srv = Server(name, spec)
            info = srv.request("initialize", {
                "protocolVersion": PROTOCOL_VERSION, "capabilities": {},
                "clientInfo": {"name": "smr-check-mcp", "version": "1"},
            }, timeout=ns.init_timeout)
            srv.send("notifications/initialized", notify=True)
            si = info.get("serverInfo", {})
            print(f"   khởi động OK: {si.get('name')} {si.get('version')} (protocol {info.get('protocolVersion')})")
            tools, cursor = [], None
            while True:
                res = srv.request("tools/list", {"cursor": cursor} if cursor else {})
                tools += [t["name"] for t in res.get("tools", [])]
                cursor = res.get("nextCursor")
                if not cursor:
                    break
            print(f"   {len(tools)} tool: {', '.join(sorted(tools))}")
            for t in sorted(deny.get(name, set())):
                state = "có thật, đã bị chặn" if t in tools else "KHÔNG tồn tại -> luật deny gõ sai tên?"
                print(f"   deny mcp__{name}__{t}: {state}")
                if t not in tools:
                    failures += 1
            for pattern in sorted(allow.get(name, set())):
                hits = [t for t in tools if fnmatch.fnmatchcase(t, pattern)]
                if not hits:
                    failures += 1
                    print(f"   allow mcp__{name}__{pattern}: KHÔNG khớp tool nào -> gõ sai tên?")
            if allow.get(name):
                n = len({t for t in tools for p in allow[name] if fnmatch.fnmatchcase(t, p)})
                print(f"   allow (không hỏi lại): {n} tool chỉ-đọc; các tool tải file vẫn hỏi trước")
            if ns.live and name in LIVE_CALLS:
                tool, args = LIVE_CALLS[name]
                if tool not in tools:
                    print(f"   live: bỏ qua, server không có tool {tool}")
                else:
                    res = srv.request("tools/call", {"name": tool, "arguments": args}, timeout=120)
                    text = " ".join(c.get("text", "") for c in res.get("content", []) if c.get("type") == "text")
                    structured = res.get("structuredContent", {}).get("result")
                    if res.get("isError"):
                        flag = "LỖI"
                    elif not text.strip() and not structured:
                        # paper-search-mcp trả danh sách rỗng, không báo lỗi, khi mạng hỏng.
                        flag = "RỖNG (thường do mạng/proxy; rỗng KHÔNG có nghĩa là không có paper)"
                    else:
                        flag = "OK"
                    shown = text or json.dumps(structured, ensure_ascii=False)
                    print(f"   live {tool}: {flag} — {shown[:300].strip()}")
                    failures += flag != "OK"
        except Exception as exc:  # báo lỗi rõ ràng, kiểm tiếp server sau
            failures += 1
            print(f"   THẤT BẠI: {exc}")
        finally:
            if srv:
                srv.close()
    print("\nKết quả:", "mọi kiểm tra đạt" if failures == 0 else f"{failures} kiểm tra thất bại")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
