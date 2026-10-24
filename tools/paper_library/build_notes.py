"""Build the reading route, Part A entry sheet, catalog, and paper-note workbook.

Responsible: Doan Van Tai. Note columns are AI drafts until the author rewrites them.
Reads papers/data/{catalog,pdf_status,audit_2026-10-24,paper_notes}.json.
PDFs stay under ~/papers/ and are never embedded in the workbook.
"""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation
from reading_plan import organize, plan

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "papers"
DATA = DEST / "data"
LOCAL = Path.home() / "papers" / "state-model-regret"
OUTPUT = DEST / "paper_comparison_part_a.xlsx"

LISTS = {
    "venue_type": ["Journal", "Conference", "Workshop", "Preprint", "Book", "Book chapter", "Working paper", "Thesis"],
    "peer": ["Có", "Không", "Chưa rõ"],
    "priority": ["P0", "P1", "P2", "P3"],
    "author_reading": ["Chưa có xác nhận", "Chưa đọc", "Metadata", "Abstract", "Mục liên quan", "Full bài"],
    "ai_reading": ["Thứ cấp", "Metadata", "Abstract", "Mục liên quan", "Full bài"],
    "access": ["Có (local)", "OA chưa tải", "Paywall – cần thư viện", "Sách – thư viện", "Không có"],
    "code": ["Có", "Không", "N/A", "Chưa kiểm"],
    "writer": ["AI (chưa kiểm)", "Tôi"],
}
LIST_HEADERS = ["ID", "Tên bài", "Tác giả", "Năm", "Nơi đăng", "Hình thức công bố", "Loại paper",
                "Peer-reviewed?", "Vùng", "Ưu tiên", "Liên quan tới claim", "Mức tôi đã đọc",
                "PDF / Truy cập", "DOI / Link", "Nhóm đọc"]
LIST_WIDTHS = [8, 46, 24, 7, 24, 15, 18, 13, 24, 9, 44, 17, 20, 30, 12]
NOTE_HEADERS = ["ID", "Tên bài", "Vấn đề", "Cách làm", "Kết quả chính + vị trí", "Giới hạn",
                "Khác với đề tài tôi", "Overlap E/M/R", "Mức AI đã đọc", "Dataset / Code",
                "Citations (nguồn, ngày)", "BibTeX key", "Việc tiếp theo", "Ghi chú do", "Updated at"]
NOTE_WIDTHS = [8, 34, 34, 34, 42, 32, 34, 10, 14, 12, 18, 22, 30, 15, 12]
HEADER_FILL = PatternFill("solid", fgColor="D9D9D9")  # the only fill colour in the workbook
TEXT = Font(name="Calibri", size=11, color="000000")
BOLD = Font(name="Calibri", size=11, color="000000", bold=True)
LINK = Font(name="Calibri", size=11, color="000000", underline="single")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def claim_text(codes, mapping):
    parts = [c.strip() for c in codes.split(",") if c.strip()]
    return "\n".join("• " + mapping[c] for c in parts)


def rows():
    catalog = json.loads((DATA / "catalog.json").read_text())
    status = {r["id"]: r for r in json.loads((DATA / "pdf_status.json").read_text())}
    audit = json.loads((DATA / "audit_2026-10-24.json").read_text())["papers"]
    extra = json.loads((DATA / "paper_notes.json").read_text())
    notes, pmap, claims = extra["notes"], extra["part_a_priority_map"], extra["claim_text"]
    shared = ("type", "peer", "area", "emr", "problem", "method", "result", "citations", "bibkey", "code", "kind")
    out = []
    for p in catalog["papers"]:
        n, s = notes[p["id"]], status[p["id"]]
        local = s["file"] if s["status"] == "Đã tải" else ""
        out.append(dict(id=p["id"], title=p["title"], authors=p["authors_short"], year=p["year"],
                        venue=p["venue"], url=p["source_url"], priority=pmap[p["priority"]],
                        claims=claim_text(n["claims"], claims), ai=p["ai_reading"], limit=p["limit"],
                        diff=p["compare"], next=p["next_read"], local=local, group="Part A",
                        access="Có (local)" if local else n["access"], **{k: n[k] for k in shared}))
    for p in audit:
        n = notes[p["id"]]
        local = p["pdf_local"] if p["pdf_local"] and (LOCAL / p["pdf_local"]).is_file() else ""
        out.append(dict(id=p["id"], title=p["title"], authors=p["authors_short"], year=p["year"],
                        venue=p["venue"], url=p["source_url"], priority=p["priority"],
                        claims=claim_text(p["claims"], claims), ai=p["ai_reading"], limit=n["limit"],
                        diff=n["diff"], next=p["next_read"], local=local, group="Audit 24/10",
                        access="Có (local)" if local else n["access"], **{k: n[k] for k in shared}))
    return out


def style(sheet, widths, row_height):
    sheet.freeze_panes = "C2"
    sheet.sheet_view.showGridLines = True
    for i, width in enumerate(widths, 1):
        sheet.column_dimensions[sheet.cell(1, i).column_letter].width = width
    for row in sheet.iter_rows():
        for cell in row:
            cell.font, cell.border = TEXT, BORDER
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    for cell in sheet[1]:
        cell.font, cell.fill = BOLD, HEADER_FILL
    sheet.row_dimensions[1].height = 30
    for r in range(2, sheet.max_row + 1):
        sheet.row_dimensions[r].height = row_height
    sheet.auto_filter.ref = sheet.dimensions
    sheet.page_setup.orientation = "landscape"
    sheet.page_setup.paperSize = sheet.PAPERSIZE_A3
    sheet.sheet_properties.pageSetUpPr.fitToPage = True
    sheet.page_setup.fitToWidth, sheet.page_setup.fitToHeight = 1, 0
    sheet.print_title_rows = "1:1"


def add_list(sheet, column, values, last_row):
    rule = DataValidation(type="list", formula1='"' + ",".join(values) + '"', allow_blank=True)
    rule.errorTitle, rule.error, rule.showErrorMessage = "Chọn trong danh sách", "Chọn một giá trị có sẵn.", True
    sheet.add_data_validation(rule)
    rule.add(f"{column}2:{column}{last_row}")


def build(data, kinds):
    previous_reading, previous_notes = {}, {}
    if OUTPUT.exists():
        previous = load_workbook(OUTPUT)
        if "Danh_sach" in previous:
            sheet = previous["Danh_sach"]
            for row in sheet.iter_rows(min_row=2, values_only=True):
                previous_reading[row[0]] = row[11]
        if "Ghi_chu_doc" in previous:
            for row in previous["Ghi_chu_doc"].iter_rows(min_row=2, values_only=True):
                previous_notes[row[0]] = list(row)
        previous.close()
    book = Workbook()
    book.properties.creator = book.properties.lastModifiedBy = "Doan Van Tai"
    book.properties.title = "Paper notes — Part A và literature audit 2026-10-24"
    start = book.active
    start.title = "Bat_dau_Part_A"
    start.append(["Thứ tự", "Mã", "Bài / tác giả", "Học để hiểu gì", "Phần cần đọc", "Ưu tiên lúc này", "PDF / nguồn", "Bạn đã đọc"])
    original_a = sorted((d for d in data if d["id"] in {"SOB14", "B82", "P11", "MAB11", "E07", "SOC12"}),
                        key=lambda d: d["reading_plan"]["order"])
    for i, d in enumerate(original_a, 1):
        a = d["reading_plan"]
        start.append([i, d["id"], d["title"] + "\n" + d["authors"], a["purpose"], a["section"],
                      "Đọc chính" if i <= 3 else "Bổ trợ, tra khi cần", d["access"],
                      previous_reading.get(d["id"], "Chưa có xác nhận")])
    style(start, [9, 10, 43, 38, 42, 26, 23, 23], 76)
    classified = book.create_sheet("Phan_loai")
    classified.append(["Mã", "Bài / tác giả", "Nhóm đọc", "Khi nào", "Lesson / giai đoạn", "Đọc để làm gì", "PDF / nguồn", "Mã trùng / lưu ý"])
    ordered = sorted(data, key=lambda d: d["reading_plan"]["order"])
    for d in ordered:
        a = d["reading_plan"]
        classified.append([d["id"], d["title"] + "\n" + d["authors"], d["reading_group"], a["when"], a["lesson"], a["purpose"], d["access"], a["alias"]])
    style(classified, [10, 44, 37, 43, 28, 44, 25, 30], 62)
    listing = book.create_sheet("Danh_sach")
    listing.append(LIST_HEADERS)
    for d in data:
        listing.append([d["id"], d["title"], d["authors"], d["year"], d["venue"], d["type"], d["kind"], d["peer"],
                        d["area"], d["priority"], d["claims"], previous_reading.get(d["id"], "Chưa có xác nhận"), d["access"],
                        d["url"].replace("https://doi.org/", "doi:"), d["reading_group"]])
    style(listing, LIST_WIDTHS, 62)
    notes = book.create_sheet("Ghi_chu_doc")
    notes.append(NOTE_HEADERS)
    for d in data:
        notes.append(previous_notes.get(d["id"], [d["id"], d["title"], d["problem"], d["method"], d["result"], d["limit"], d["diff"], d["emr"],
                     d["ai"], d["code"], d["citations"] or None, d["bibkey"], d["next"], "AI (chưa kiểm)", "2026-10-24"]))
    style(notes, NOTE_WIDTHS, 80)
    for r, d in enumerate(data, 2):  # links only on DOI and PDF columns, never on the title
        listing.cell(r, 14).hyperlink = d["url"]
        listing.cell(r, 14).font = LINK
        if d["study_local"]:
            listing.cell(r, 13).hyperlink = "PDF_local/" + d["study_local"]
            listing.cell(r, 13).font = LINK
    for sheet, members, column in [(start, original_a, 7), (classified, ordered, 7)]:
        for r, d in enumerate(members, 2):
            sheet.cell(r, column).hyperlink = "PDF_local/" + d["study_local"] if d["study_local"] else d["url"]
            sheet.cell(r, column).font = LINK
    last = len(data) + 1
    for column, values in [("F", LISTS["venue_type"]), ("G", kinds), ("H", LISTS["peer"]),
                           ("J", LISTS["priority"]), ("L", LISTS["author_reading"]), ("M", LISTS["access"])]:
        add_list(listing, column, values, last)
    for column, key in [("I", "ai_reading"), ("J", "code"), ("N", "writer")]:
        add_list(notes, column, LISTS[key], last)
    guide = book.create_sheet("Huong_dan")
    guide.append(["Mục", "Cách dùng"])
    for row in [
        ("Bắt đầu", "Mở Bat_dau_Part_A. Hiện chỉ học SOB14 → B82 → P11; ba bài còn lại là bổ trợ."),
        ("Phân loại", "Phan_loai chia đủ21 bài thành4 nhóm theo thời điểm học; nhóm Part B để sau."),
        ("Audit khác lesson", "15 bài shortlist mới là kết quả tìm literature, không phải15 bài bắt buộc của Part A."),
        ("Các mã", "P11/R04 là ID paper; PC3 là claim; P0/P1 là độ ưu tiên; A1–A6 là vùng tìm kiếm, không phải Part A/B."),
        ("Hai sheet", "Danh_sach: tra cứu nhanh, mỗi bài một dòng. Ghi_chu_doc: ghi chú khi đọc sâu, cùng ID và tên bài."),
        ("Hình thức công bố", "Journal, Conference, Workshop, Preprint, Book, Book chapter, Working paper, Thesis."),
        ("Loại paper", "Lý thuyết, Phương pháp, Thực nghiệm / đánh giá, Survey, Sách / giáo trình, Hệ thống."),
        ("Ưu tiên", "P0 có thể bác bỏ claim của tôi; P1 rất gần; P2 bổ trợ; P3 chỉ bối cảnh. Part A quy đổi: Cốt lõi → P1, Bổ trợ → P2."),
        ("Liên quan tới claim", "Claim nào của đề tài bị bài này ảnh hưởng (nguyên văn đầy đủ ở notes/literature/claims.md)."),
        ("Overlap E/M/R", "Estimand / Mechanism / Regime: D trùng, P một phần, N khác. Đây là công cụ đối chiếu, không phải phép chứng nhận mới/cũ tự động."),
        ("Mức đọc", "Cập nhật mức của bạn tại Danh_sach → Mức tôi đã đọc. Bat_dau_Part_A hiển thị lại khi dựng file. Mức AI là riêng; Thứ cấp = chỉ qua nguồn khác."),
        ("Ghi chú do", "AI (chưa kiểm) = AI soạn. Khi tự viết lại bằng lời mình, đổi thành Tôi."),
        ("Kết quả chính", "Luôn ghi kèm vị trí (§, trang, Eq., Prop.) để kiểm lại được."),
        ("Citations", "Ghi kèm nguồn và ngày lấy vì con số thay đổi theo thời gian. Ô trống = chưa lấy."),
        ("BibTeX", "Chỉ ghi citation key; BibTeX đầy đủ để trong file .bib (tránh lỗi #NAME? của Excel)."),
        ("Link", "Tên bài không có link. Bấm cột DOI / Link để mở nguồn, cột PDF / Truy cập để mở PDF trên máy này."),
        ("Cập nhật", "Builder giữ mức bạn đã đọc và các ghi chú hiện có theo ID. Metadata/nhóm đọc lấy từ JSON; có backup trước lượt phân loại."),
    ]:
        guide.append(row)
    style(guide, [20, 120], 32)
    book.save(OUTPUT)


def verify(data, kinds):
    with ZipFile(OUTPUT) as archive:
        assert archive.testzip() is None and not any(n.endswith(".pdf") for n in archive.namelist())
    book = load_workbook(OUTPUT)
    assert book.sheetnames == ["Bat_dau_Part_A", "Phan_loai", "Danh_sach", "Ghi_chu_doc", "Huong_dan"]
    ids = [d["id"] for d in data]
    assert len(ids) == len(set(ids)) == 21
    listing, notes = book["Danh_sach"], book["Ghi_chu_doc"]
    for sheet in (listing, notes):
        assert sheet.max_row == 22 and [sheet.cell(r, 1).value for r in range(2, 23)] == ids
        fills = {c.fill.fgColor.rgb for row in sheet.iter_rows() for c in row if c.fill.fill_type == "solid"}
        assert fills <= {"00D9D9D9"}, fills
    for r, d in enumerate(data, 2):
        assert listing.cell(r, 2).hyperlink is None and notes.cell(r, 2).hyperlink is None
        assert "PC" not in listing.cell(r, 11).value and listing.cell(r, 11).value.startswith("• ")
        assert listing.cell(r, 7).value in kinds and listing.cell(r, 6).value in LISTS["venue_type"]
        assert listing.cell(r, 12).value in LISTS["author_reading"] and notes.cell(r, 14).value in LISTS["writer"]
        assert notes.cell(r, 9).value in LISTS["ai_reading"] and notes.cell(r, 9).value != "Full bài"
        assert listing.cell(r, 14).hyperlink.target == d["url"]
        if d["local"]:
            assert (LOCAL / d["local"]).read_bytes()[:5] == b"%PDF-"
    assert book["Bat_dau_Part_A"].max_row == 7
    assert [book["Bat_dau_Part_A"].cell(r, 2).value for r in range(2, 8)] == ["SOB14", "B82", "P11", "MAB11", "E07", "SOC12"]
    assert book["Phan_loai"].max_row == 22
    counts = {g["id"]: sum(d["reading_plan"]["group"] == g["id"] for d in data) for g in plan()["groups"]}
    assert list(counts.values()) == [3, 6, 7, 5]
    for d in data:
        if d["study_local"]:
            assert (LOCAL / d["study_local"]).resolve() == (LOCAL / d["local"]).resolve()
    result = dict(status="PASS", workbook=OUTPUT.name, papers=len(ids), sheets=book.sheetnames,
                  part_a=sum(d["group"] == "Part A" for d in data), audit=sum(d["group"] != "Part A" for d in data),
                  local_pdfs=sum(bool(d["local"]) for d in data), title_links=0, fill_colours=["D9D9D9"],
                  author_reading_unconfirmed=sum(listing.cell(r, 12).value == "Chưa có xác nhận" for r in range(2, 23)), embedded_pdfs=0,
                  reading_groups=counts, original_pdf_paths_preserved=True,
                  workbook_sha256=hashlib.sha256(OUTPUT.read_bytes()).hexdigest())
    (DATA / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    kinds = json.loads((DATA / "paper_notes.json").read_text())["kind_values"]
    data = organize(rows())
    build(data, kinds)
    verify(data, kinds)
    print("Workbook:", OUTPUT, flush=True)
