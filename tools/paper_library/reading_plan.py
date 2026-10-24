"""Reading-stage views over existing PDFs; originals are never moved.

Responsible: Doan Van Tai. Classification is an AI proposal, not a Gate decision.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "papers"
DATA = DEST / "data"
LOCAL = Path.home() / "papers" / "state-model-regret"


def plan():
    return json.loads((DATA / "reading_plan.json").read_text())


def organize(data):
    reading = plan()
    groups = {g["id"]: g for g in reading["groups"]}
    assert set(reading["papers"]) == {d["id"] for d in data}
    records, before = [], {}
    for d in data:
        assignment = reading["papers"][d["id"]]
        d["reading_plan"] = assignment
        d["reading_group"] = groups[assignment["group"]]["title"]
        d["study_local"] = ""
        source = LOCAL / d["local"] if d["local"] else None
        digest = None
        folder = LOCAL / assignment["group"]
        folder.mkdir(exist_ok=True)
        if source and source.is_file():
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            before[str(source)] = digest
            alias = folder / f"{d['id']}_{d['year']}.pdf"
            if alias.is_symlink():
                assert alias.resolve() == source.resolve(), ("Conflicting alias", alias)
            elif alias.exists():
                raise FileExistsError("Refusing to overwrite local file: " + str(alias))
            else:
                alias.symlink_to(source.resolve())
            d["study_local"] = alias.relative_to(LOCAL).as_posix()
            assert hashlib.sha256(alias.read_bytes()).hexdigest() == digest
        records.append(dict(id=d["id"], group=assignment["group"], source=d["local"],
                            view=d["study_local"], available=bool(d["study_local"]), source_sha256=digest))
    for group in reading["groups"]:
        members = sorted((d for d in data if d["reading_plan"]["group"] == group["id"]),
                         key=lambda d: d["reading_plan"]["order"])
        assert len(members) == group["count"]
        intro = f"# {group['title']}\n\nDoan Van Tai · 24/10/2026 · AI đề xuất.\n\n{group['role']} {group['when']}.\n\n"
        header = "| Mã | Bài | Đọc để làm gì | Lesson / giai đoạn | PDF |\n|---|---|---|---|---|\n"
        body, local_body = [], []
        for d in members:
            a = d["reading_plan"]
            pdf = "Có" if d["study_local"] else "Chưa có; dùng link nguồn"
            body.append(f"| {d['id']} | [{d['title']}]({d['url']}) | {a['purpose']} | {a['lesson']} | {pdf} |")
            target = Path(d["study_local"]).name if d["study_local"] else d["url"]
            local_body.append(f"| {d['id']} | [{d['title']}]({target}) | {a['purpose']} | {a['lesson']} | {pdf} |")
        repo_folder = DEST / "groups" / group["id"]
        repo_folder.mkdir(parents=True, exist_ok=True)
        (repo_folder / "README.md").write_text(intro + header + "\n".join(body) + "\n\nPDF cục bộ: `papers/PDF_local/" + group["id"] + "/`.\n")
        (LOCAL / group["id"] / "README.md").write_text(intro + header + "\n".join(local_body) + "\n\nCác PDF là lối mở đến bản gốc; không phải bài mới.\n")
    for name, digest in before.items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest
    local_intro = "# Bắt đầu ở đây\n\nDoan Van Tai · 24/10/2026.\n\nHọc ngay: **SOB14 → B82 → P11**. Mở thư mục 01 trước.\n\n"
    for g in reading["groups"]:
        local_intro += f"- [{g['id']}]({g['id']}/README.md): {g['role']}\n"
    local_intro += "\nKho gốc: Part_A = PDF lesson; review_2026-10-24 = PDF tải lúc audit; inbox = PDF bạn cung cấp; _backups = bản sao dự phòng.\n"
    (LOCAL / "00_BAT_DAU.md").write_text(local_intro)
    manifest = dict(owner="Doan Van Tai", as_of="2026-10-24", papers=len(data),
                    original_pdfs_unchanged=len(before), pdf_views=sum(r["available"] for r in records),
                    groups={g["id"]: g["count"] for g in reading["groups"]}, records=records)
    (DATA / "classification_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return data
