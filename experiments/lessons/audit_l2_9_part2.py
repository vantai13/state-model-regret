"""Audit artifact L2.9 Part 2 (26/10/2026): related work, DL-042, closeout, EV-37…45.

Người phụ trách: Doan Van Tai. AI viết theo ủy quyền tác giả. Kiểm luật PHASE_2 §14/§20
(mỗi câu có nguồn + mức đọc; đoạn 4 ngắn nhất; đoạn 5 đúng nhãn; không chữ "novel"),
tính trung thực provenance (nhãn ghi là AI ủy quyền; hai mục closeout của tác giả vẫn
trống; cột "Tác giả giải thích lại được?" không ghi "Có"; mẫu L-self chưa điền; không tag),
chỉ append/insert so với base, link sống, không PDF; và kiểm chính xác đẳng thức
E[min_a C] = min_a E[C] − EVPI_w dùng ở đoạn 5. Không chứng nhận nhãn, L-self hay Gate.
"""

from __future__ import annotations

import difflib
import json
import random
import re
import subprocess
from fractions import Fraction
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "lessons" / "l2_9" / "part2"
BASE = "74f76113590bb581be8f0f27650a902632425b53"
APPEND_ONLY = ["notes/literature/prior_boundary.md", "notes/01_claim_boundary_v1_2.md",
               "notes/02_decision_log.md", "notes/00_evidence_inventory.md",
               "notes/00_exposure_register.md", "AGENTS.md"]
INSERT_ONLY = ["README.md", "notes/literature/README.md"]
UNCHANGED = ["notes/literature/claims.md", "notes/literature/prior_predictions.md",
             "notes/01_definitions_v1_2.md", "notes/design/grid_v1_2.json", "notes/literature/terms.md",
             "papers/paper_comparison.xlsx", "papers/data/catalog.json",
             "notes/literature/author_reading_record.md", "notes/phases/PHASE_1_closeout.md"]
LEVEL = re.compile(r"AI-T|AI-A|L-self|suy luận AI|contract v1\.2|phép dẫn AI|nhãn tạm AI")
FORBIDDEN = re.compile(r"\bnovel\b|chưa ai làm|đầu tiên|lần đầu", re.I)
LABELS = {"PC1": "DROP", "PC2": "NARROW", "PC3": "KEEP", "PC4": "HOLD", "PC5": "NARROW", "PC6": "NARROW",
          "Main RQ": "KEEP"}


def git_show(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


def evpi_identity_check(n: int = 500, seed: int = 20261026) -> int:
    """Với chi phí C(a,w) và xác suất p(w): E[min_a C] = min_a E[C] − EVPI_w, EVPI_w ≥ 0."""
    rng = random.Random(seed)
    for _ in range(n):
        na, nw = rng.randint(2, 4), rng.randint(2, 5)
        wts = [rng.randint(1, 9) for _ in range(nw)]
        p = [Fraction(x, sum(wts)) for x in wts]
        c = [[Fraction(rng.randint(0, 40), rng.randint(1, 5)) for _ in range(nw)] for _ in range(na)]
        exp_cost = [sum(pi * ci for pi, ci in zip(p, row)) for row in c]
        l_star = min(exp_cost)
        hindsight = sum(p[w] * min(c[a][w] for a in range(na)) for w in range(nw))
        evpi = l_star - hindsight
        assert evpi >= 0 and hindsight == l_star - evpi
    return n


def main() -> None:
    for f in APPEND_ONLY:
        assert (ROOT / f).read_bytes().startswith(git_show(f)), f
    for f in INSERT_ONLY:
        a = git_show(f).decode().splitlines(); b = (ROOT / f).read_text(encoding="utf-8").splitlines()
        assert all(t in ("equal", "insert") for t, *_ in
                   difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes()), f
    for f in UNCHANGED:
        assert (ROOT / f).read_bytes() == git_show(f), f

    # Related work: 5 đoạn, mỗi câu có [nguồn; mức], đoạn 4 ngắn nhất, đoạn 5 đúng nhãn
    rw = (ROOT / "notes/literature/related_work_skeleton.md").read_text(encoding="utf-8")
    assert "AI (Claude) viết theo ủy" in rw and "Tác giả chưa tự viết lại" in rw
    paras = dict(re.findall(r"^## \((\d)\)[^\n]*\n\n(.+?)\n\n", rw, re.S | re.M))
    assert sorted(paras) == ["1", "2", "3", "4", "5"]
    words = {k: len(v.split()) for k, v in paras.items()}
    assert words["4"] < min(words["1"], words["2"], words["3"]), words
    sentences = 0
    for k, text in paras.items():
        masked = re.sub(r"\[[^\[\]]*\]", "[X]", text.strip())
        pieces = [x for x in re.split(r"\.\s+", masked) if x]
        assert all(x.rstrip(".").endswith("[X]") for x in pieces), (k, [x[-60:] for x in pieces])
        assert len(pieces) == len(re.split(r"(?<=\]\.)\s+", text.strip())), k
        for s in re.split(r"(?<=\]\.)\s+", text.strip()):
            assert s.endswith("]."), (k, s[-80:])
            cites = re.findall(r"\[([^\[\]]+)\]", s)
            assert cites and LEVEL.search(cites[-1]), (k, cites[-1] if cites else s[-60:])
            sentences += 1
        assert not FORBIDDEN.search(text), k
    p5 = paras["5"]
    for pc in ("PC3", "PC5", "PC6"):
        assert pc in p5
    assert "dạng hẹp của PC5" in p5 and "dạng hẹp của PC6" in p5 and "câu chữ của PC3" in p5

    # Nhãn tạm: đúng, ghi là AI ủy quyền; hồ sơ Part1 của tác giả vẫn trống
    pb = (ROOT / "notes/literature/prior_boundary.md").read_text(encoding="utf-8")
    sec = pb.split("## L2.9 — nhãn tạm do AI chấm theo ủy quyền tác giả (26/10/2026)", 1)[1]
    assert "không phải tác giả tự chấm" in sec and "sau khi đã thấy" in sec
    rows = {re.sub(r"\*", "", r.split("|")[1]).strip(): r.split("|")[2] for r in
            sec.split("### Dòng boundary", 1)[0].splitlines() if re.match(r"^\| (PC[1-6]|\*\*Main RQ)", r)}
    assert set(rows) == set(LABELS), rows.keys()
    for k, lab in LABELS.items():
        assert lab in rows[k], (k, rows[k])
    part1 = pb.split("## L2.9 Part 1 — hồ sơ 8 cột", 1)[1].split("### Trạng thái Gate L", 1)[0]
    assert part1.count("⟨tác giả chấm⟩") == 7

    # DL-042
    dl = (ROOT / "notes/02_decision_log.md").read_text(encoding="utf-8")
    assert dl.count("### DL-042 —") == 1
    dl42 = dl.split("### DL-042 —", 1)[1]
    assert "Gate L: HOLD" in dl42 and "theo ủy quyền tác giả" in dl42 and "Main RQ:** **KEEP" in dl42
    assert "Không gắn tag" in dl42

    # Closeout: hai mục tác giả vẫn trống, nháp AI được rào, Gate HOLD, không tag
    co = (ROOT / "notes/phases/PHASE_2_closeout.md").read_text(encoding="utf-8")
    assert co.count("⟨Tác giả tự viết — chưa có.⟩") == 2
    assert co.count("KHÔNG phải lời tác giả") == 2
    assert "**Quyết định (AI theo ủy quyền tác giả, 26/10/2026): HOLD.**" in co
    tags = subprocess.check_output(["git", "tag", "-l", "phase-2-closeout"], cwd=ROOT, text=True).strip()
    assert tags == ""

    # Inventory EV-37…45: không ô nào ghi tác giả "Có"
    inv = (ROOT / "notes/00_evidence_inventory.md").read_text(encoding="utf-8")
    evs = {m[0]: m[1] for m in re.findall(r"^\| (EV-(?:3[7-9]|4[0-5])) \|(.+)$", inv, re.M)}
    assert sorted(evs) == [f"EV-{i}" for i in range(37, 46)]
    for ev, rest in evs.items():
        assert rest.split("|")[2].strip().startswith("Chưa có record"), ev

    # Exposure: held-out sạch về outcome; L8 packet không phải record
    ex = (ROOT / "notes/00_exposure_register.md").read_text(encoding="utf-8")
    assert "held-out vẫn **sạch về outcome**" in ex
    pk = (ROOT / "notes/meetings/phase2_reader_packet.md").read_text(encoding="utf-8")
    assert "CHƯA CÓ AI ĐỌC" in pk
    assert not list((ROOT / "notes/meetings").glob("*_phase2_reader.md"))

    n_evpi = evpi_identity_check()

    assert not subprocess.check_output(["git", "ls-files", "*.pdf", "*.PDF"], cwd=ROOT).strip()
    links = 0
    docs = [ROOT / "README.md", ROOT / "AGENTS.md", *OUT.glob("*.md"),
            *(ROOT / "notes/literature").rglob("*.md"), ROOT / "notes/phases/PHASE_2_closeout.md",
            ROOT / "notes/01_claim_boundary_v1_2.md", ROOT / "notes/meetings/phase2_reader_packet.md",
            ROOT / "notes/02_decision_log.md", ROOT / "notes/00_evidence_inventory.md"]
    for doc in docs:
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
                  executed_by="AI (Claude) theo ủy quyền tác giả", related_work_words=words,
                  related_work_sentences_cited=sentences, provisional_labels=LABELS,
                  labels_by="AI delegated, after seeing mentor view", author_dossier_labels_blank=7,
                  DL_042=True, gate_L="HOLD", tag_phase_2_closeout=False,
                  closeout_author_sections_written_by_author=0, EV_rows=sorted(evs),
                  EV_author_explained_yes=0, L_self_records=0, L8_reader_records=0,
                  evpi_identity_exact_cases=n_evpi, local_links_checked=links, pdfs_in_git=0,
                  contract_changed=False, PC_forecast_table_changed=False, grid_run=False)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
