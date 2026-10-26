"""Cập nhật record P02 (catalog + dòng AI trong Ghi_chu_doc) sau khi có VoR.

Người phụ trách: Doan Van Tai. AI viết theo yêu cầu 26/10/2026 (L2.8 follow-up).
Chỉ sửa ID P02. Dừng nếu dòng Ghi_chu_doc của P02 không do AI ghi, hoặc nếu
"Mức tôi đã đọc" khác "Chưa có xác nhận" — khi đó tác giả đã tự ghi, không đè.
Snapshot catalog/workbook trước khi sửa nằm ở results/lessons/l2_8/followup/snapshots/.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "papers" / "data" / "catalog.json"
XLSX = ROOT / "papers" / "paper_comparison.xlsx"
SNAP = ROOT / "results" / "lessons" / "l2_8" / "followup" / "snapshots"
PDF = Path.home() / "papers/state-model-regret/current/P02_Poelman2023_TRC_VoR.pdf"
PDF_SHA = "52c9b97d839d7924610fd23993fc1cec0d29d7decc2f096922587f464cc3f686"

NEW = {
    "type": "Journal (VoR, CC BY)",
    "claims": "• PC2 (PHASE_2 v2.0 §5.4: nguồn quyết định nhãn) / PC3/PC4/PC5: bias một đại lượng mỗi lần; sweep 1-D theo prediction/update horizon; không gán dấu Γ.",
    "ai": "Mục liên quan",
    "access": "Có (VoR 20 trang local; tác giả tải 26/10)",
    "local": "P02_Poelman2023_TRC_VoR.pdf",
    "local_sha256": PDF_SHA,
    "local_source": "Tác giả tải từ ScienceDirect 26/10/2026 (1-s2.0-S0968090X23001638-main.pdf)",
    "role": "L2.7 PartA dependency: AI-T VoR §1–5 + Bảng 2 (L2.8 follow-up 26/10); chưa L-self.",
    "method": "Aimsun + MPC structure-free 4 nút; I reference biết demand ghi sẵn → II aggregation → III bias trên aggregation (§2.1, §2.2.4).",
    "result": "Bias 1 đại lượng/lần (§3.3.1 tr15); Bảng 2 tr16 quét prediction 12/30/60 s và update 12/30/60 s; update ngắn bù một phần, state bias lớn làm mất bù (§3.3.2, §4).",
    "limit": "Không joint bias (§4 tr18); solver heuristic <1% so full B&B (Fig3d); metric delay/xe so reference, không regret/oracle D15. Hình chỉ đọc caption.",
    "next": "Tác giả đọc §2.2.4, §3.3, Bảng 2 nếu dùng cho nhãn PC2 ở L2.9; MT2/6/7 cập nhật ở follow-up.",
    "updated": "2026-10-26",
}


def main() -> None:
    SNAP.mkdir(parents=True, exist_ok=True)
    assert hashlib.sha256(PDF.read_bytes()).hexdigest() == PDF_SHA, "PDF hash mismatch"
    xsnap = SNAP / "paper_comparison_before_2026-10-26.xlsx"
    if not xsnap.exists():
        shutil.copy2(XLSX, xsnap)
    csnap = SNAP / "catalog_before_2026-10-26.json"
    assert csnap.exists(), "catalog snapshot must exist before edit"

    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    p = next(x for x in data["papers"] if x["id"] == "P02")
    assert p["author_reading"] == "Chưa có xác nhận"
    for key in ("type", "claims", "ai", "access", "local", "local_source", "role",
                "method", "result", "limit", "next"):
        p[key] = NEW[key]
    p["local_sha256"] = NEW["local_sha256"]
    row = p["note_row"]
    row[3], row[4], row[5] = NEW["method"], NEW["result"], NEW["limit"]
    row[8], row[12], row[14] = NEW["ai"], NEW["next"], NEW["updated"]
    assert row[13] == "AI (chưa kiểm)"
    data["as_of"] = "2026-10-26"
    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    book = load_workbook(XLSX)
    lst, notes = book["Danh_sach"], book["Ghi_chu_doc"]
    r_list = next(r for r in range(2, lst.max_row + 1) if lst.cell(r, 1).value == "P02")
    assert lst.cell(r_list, 12).value == "Chưa có xác nhận", "author recorded a level; do not touch"
    r_note = next(r for r in range(2, notes.max_row + 1) if notes.cell(r, 1).value == "P02")
    assert notes.cell(r_note, 14).value == "AI (chưa kiểm)", "note row not AI-authored; stop"
    for c, v in enumerate(row, start=1):
        notes.cell(r_note, c).value = v
    book.save(XLSX)
    book.close()
    print(json.dumps({"updated": "P02", "catalog_as_of": data["as_of"],
                      "xlsx_snapshot": str(xsnap.relative_to(ROOT))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
