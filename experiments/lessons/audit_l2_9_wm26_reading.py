"""Audit lượt ghi nhận tác giả đọc bản giải thích WM26 (26/10/2026).

Người phụ trách: Doan Van Tai. AI viết. Kiểm: PDF tác giả tải trùng bản thư viện; trích dẫn
trong check.md có trong text PDF; số học ví dụ của bản giải thích; record ghi L-2nd (không
L-self), ô tác giả của bộ tối thiểu vẫn trống, Excel không đổi; đính chính §9→§8 chỉ append
(hoặc sửa đúng chỗ ở hai file làm việc); Gate L vẫn HOLD; link sống; không PDF trong Git.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import re
import subprocess
from fractions import Fraction as F
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "lessons" / "l2_9" / "wm26_author_reading"
BASE = "b0b7df0de609757f277e4b595b23c882a04efd7d"
WM_SHA = "94201c596276c55c295df09d5b1b34530db7c08617e2b97954311cdd9e38de4a"
DOWNLOAD = Path("/mnt/c/Users/VAN TAI/Downloads/2610.05550v1.pdf")
QUOTES = ["restore the identical state", "five environment steps each",
          "MSES > MSEC in 14/16", "Six of the 14 favor S on both physical criteria",
          "elites are the top 30", "LIMITATIONS AND CONCLUSION",
          "the true-future oracles are diagnostic tools rather than deployable corrections",
          "improves offline H5 response error by 8.44%", "−2.34 points [−8.07, 3.52]",
          "Cube's encoded-goal cost remains uninformative"]
APPEND_ONLY = ["notes/literature/papers/WM26.md", "notes/literature/prior_boundary.md",
               "notes/02_decision_log.md", "notes/phases/PHASE_2_closeout.md",
               "notes/00_evidence_inventory.md", "AGENTS.md"]


def git_show(path: str) -> str:
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT, text=True)


def norm(s: str) -> str:
    s = s.replace("’", "'").replace("L IMITATIONS", "LIMITATIONS")
    return re.sub(r"\s+", " ", s)


def main() -> None:
    lib = (Path.home() / "papers/state-model-regret/current/WM26.pdf").resolve()
    assert hashlib.sha256(lib.read_bytes()).hexdigest() == WM_SHA
    download_checked = DOWNLOAD.exists()
    if download_checked:
        assert hashlib.sha256(DOWNLOAD.read_bytes()).hexdigest() == WM_SHA
    text = norm((Path.home() / "papers/state-model-regret/current/WM26.txt").read_text(encoding="utf-8"))
    for q in QUOTES:
        assert norm(q) in text, q
    pages = (Path.home() / "papers/state-model-regret/current/WM26.txt").read_text(encoding="utf-8").split("\f")
    assert "L IMITATIONS AND CONCLUSION" in pages[8] and "diagnostic" in pages[8]  # PDF trang 9, §8

    z, p = [F(1), F(3)], [F(6), F(4)]
    zb, pb = sum(z) / 2, sum(p) / 2
    modes = {"P": p, "C": [x - pb + zb for x in p], "S": [x - zb + pb for x in z], "E": z}
    mse = {k: sum((a - b) ** 2 for a, b in zip(v, z)) / 2 for k, v in modes.items()}
    pick = {k: "AB"[min(range(2), key=lambda j: v[j] ** 2)] for k, v in modes.items()}
    assert mse == {"P": 13, "C": 4, "S": 9, "E": 0} and pick == {"P": "B", "C": "B", "S": "A", "E": "A"}

    rec = (ROOT / "notes/literature/author_reading_record.md").read_text(encoding="utf-8")
    assert "L-2nd, author-attested" in rec and "Chưa phải L-self primary" in rec
    assert '"đây là những gì tôi đã đọc và đưa AI thuật lại"' in rec
    rows = [r for r in rec.splitlines() if re.match(r"^\| [1-7] \|", r)]
    assert len(rows) == 7 and all(all(c.strip() == "" for c in r.strip().strip("|").split("|")[5:]) for r in rows)
    for f in ("notes/literature/author_reading_record.md", "notes/literature/related_work_skeleton.md"):
        cur = (ROOT / f).read_text(encoding="utf-8")
        assert "§9 PDF9" not in cur, f
        ops = difflib.SequenceMatcher(a=git_show(f).splitlines(), b=cur.splitlines(), autojunk=False).get_opcodes()
        assert all(t in ("equal", "insert", "replace") for t, *_ in ops), f
        assert sum(1 for t, *_ in ops if t == "replace") <= 2, f
    for f in APPEND_ONLY:
        assert (ROOT / f).read_text(encoding="utf-8").startswith(git_show(f)), f
    assert "Gate L: HOLD" in (ROOT / "notes/02_decision_log.md").read_text(encoding="utf-8")
    assert (ROOT / "papers/paper_comparison.xlsx").read_bytes() == subprocess.check_output(
        ["git", "show", f"{BASE}:papers/paper_comparison.xlsx"], cwd=ROOT)
    ex = (OUT / "explainer_as_read.md").read_text(encoding="utf-8")
    assert ex.startswith("<!--\nProvenance:") and "Section 8" in ex and "8,44%" in ex

    assert not subprocess.check_output(["git", "ls-files", "*.pdf", "*.PDF"], cwd=ROOT).strip()
    links = 0
    for doc in [ROOT / "README.md", ROOT / "AGENTS.md", *OUT.glob("*.md"), *(ROOT / "notes").rglob("*.md")]:
        for link in re.findall(r"\]\(([^)]+)\)", doc.read_text(encoding="utf-8")):
            if "://" in link or link.startswith(("#", "mailto:")):
                continue
            target = unquote(link.split("#", 1)[0].strip("<>"))
            if (doc.parent / target).resolve() == (OUT / "verification.json").resolve():
                links += 1
                continue
            assert (doc.parent / target).exists(), (str(doc), link)
            links += 1
    result = dict(artifact_status="PASS", responsible="Doan Van Tai", date="2026-10-26", base_commit=BASE,
                  wm26_pdf_sha256=WM_SHA, download_copy_identical=download_checked,
                  explainer_claims_quotes_verified=len(QUOTES), toy_arithmetic_verified=True,
                  author_reading_level="L-2nd author-attested (AI explainer)", author_L_self_WM26=False,
                  excel_unchanged=True, erratum="WM26 'diagnostic tools' sentence is §8 (PDF p9), not §9",
                  gate_L="HOLD", local_links_checked=links, pdfs_in_git=0)
    (OUT / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
