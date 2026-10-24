"""Download the Part A PDFs (optional) and write the Part A quick-view CSV.

Responsible: Doan Van Tai. Summaries/comparisons are AI-assisted proposals.
PDFs are stored under ~/papers/, never copied into the Git repository.
The Excel workbook is built by build_notes.py (since 2026-10-24).
"""
import argparse
import csv
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request


ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "papers"
DATA = DEST / "data"
LOCAL = Path.home() / "papers" / "state-model-regret"


def download(paper):
    target = LOCAL / paper["pdf_file"]
    target.parent.mkdir(parents=True, exist_ok=True)
    errors = []
    old = Path.home() / "papers" / "l2_part_a" / (paper["id"] + ".pdf")
    urls = paper["pdf_urls"]
    data, source = None, None
    if target.is_file():
        data, source = target.read_bytes(), "existing local copy"
    elif old.is_file():
        data, source = old.read_bytes(), urls[0]
    else:
        for url in urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=20) as response:
                    candidate = response.read()
                if not candidate.startswith(b"%PDF-"):
                    raise ValueError("Response is not a PDF")
                data, source = candidate, url
                break
            except Exception as error:
                errors.append(type(error).__name__ + ": " + str(error))
    if data:
        if not data.startswith(b"%PDF-"):
            raise ValueError("Invalid cached PDF: " + paper["id"])
        # Validate a complete PDF and its identity before recording success.
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            trial = Path(tmp) / "paper.pdf"
            trial.write_bytes(data)
            info = subprocess.run(["pdfinfo", str(trial)], capture_output=True, text=True, check=True).stdout
            first = subprocess.run(["pdftotext", "-f", "1", "-l", "1", str(trial), "-"], capture_output=True, text=True, check=True).stdout
        tokens = set(re.findall(r"[a-z]+", paper["title"].lower()))
        observed = set(re.findall(r"[a-z]+", first.lower()))
        overlap = len(tokens & observed) / len(tokens)
        if overlap < .70:
            raise ValueError("PDF title needs manual review: " + paper["id"])
        pages = int(next(line.split(":", 1)[1] for line in info.splitlines() if line.startswith("Pages:")))
        if not target.exists():
            target.write_bytes(data)
        return dict(id=paper["id"], status="Đã tải", file=paper["pdf_file"],
                    pages=pages, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                    source=source, title_overlap=round(overlap, 3), errors=errors)
    return dict(id=paper["id"], status="Chưa tải được", file="", errors=errors,
                source=paper["source_url"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    catalog = json.loads((DATA / "catalog.json").read_text())
    papers = catalog["papers"]
    assert len(papers) == 6 and all(p["part"] == "Part_A" for p in papers)
    if args.download:
        LOCAL.mkdir(parents=True, exist_ok=True)
        with ThreadPoolExecutor(max_workers=4) as pool:
            records = list(pool.map(download, papers))
        (DATA / "pdf_status.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
        alias = DEST / "PDF_local"
        if not alias.exists() and not alias.is_symlink():
            alias.symlink_to(LOCAL, target_is_directory=True)
        readme = LOCAL / "Part_A" / "README.md"
        readme.write_text("# Part A — State × Model Regret\n\nDoan Van Tai. PDF cục bộ; không push GitHub.\n\n" + "\n".join(
            f"- {p['id']}: {p['title']} — {s['status']}. {p['source_url']}"
            for p, s in zip(papers, records)) + "\n")
    records = json.loads((DATA / "pdf_status.json").read_text())
    assert [r["id"] for r in records] == [p["id"] for p in papers]
    with (DEST / "part_a_quick_view.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["ID", "Ưu tiên", "Topic", "Năm", "Tác giả", "Claim chính", "So với nghiên cứu của tôi", "AI đã đọc", "Nguồn"])
        for paper in papers:
            writer.writerow([paper[k] for k in ("id", "priority", "topic", "year", "authors_short", "claim", "compare", "ai_reading", "source_url")])
    print("CSV:", DEST / "part_a_quick_view.csv", "— Excel: chạy tools/paper_library/build_notes.py", flush=True)


if __name__ == "__main__":
    main()
