# Quy tắc cho Claude trong repo này

Repo nghiên cứu của **Doan Van Tai** (RQ: state repair × model repair trong load-changing routing). Đọc `README.md` để biết trạng thái và gate hiện tại trước khi làm gì.

## Nghiên cứu

- Không làm thay các understanding gate: không viết bài kín sách, read-back hay self-explanation thay tác giả, không gắn nhãn `[kín sách]`, không đổi gate, G-level hay `notes/02_decision_log.md` khi tác giả chưa yêu cầu rõ.
- Tách Fact / Claim / Evidence / Inference. Thông tin lấy từ paper phải kèm §, phương trình hoặc hình. Không chắc thì ghi `Unclear`, không đoán.
- "Chưa tìm thấy" không có nghĩa "chưa ai làm". Không tuyên bố novelty hay research gap.
- File có phần do AI soạn thì ghi provenance ở đầu file, như các note hiện có.

## Tìm và đọc paper

- Mỗi phiên tìm: skill `search-log`. Mỗi paper: skill `paper-note`.
- MCP server: `arxiv`, `papersearch` (khai báo trong `.mcp.json`). Kết quả rỗng hoặc lỗi **không** chứng minh paper không tồn tại; thử nguồn thứ hai và ghi log.
- Chỉ dùng full text hợp pháp: arXiv, bản open access (Unpaywall), trang tác giả, thư viện. Không dùng Sci-Hub hay mirror lậu; tool Sci-Hub đã bị chặn trong `.claude/settings.json`, không tìm đường vòng.
- PDF chỉ lưu trong `downloads/` hoặc `papers_local/` (đã gitignore). Không commit PDF hay đoạn dài chép từ paper. Mỗi paper tối đa một câu trích nguyên văn, dưới 15 từ.
- Không bao giờ bịa reference. Trước khi thêm vào file `.bib`, kiểm bằng skill `citation-management`: `python .claude/skills/citation-management/scripts/validate_citations.py <file.bib> --check-dois`.

## Viết và phản biện

- `scientific-writing` chỉ chạy khi tác giả gõ `/scientific-writing`. Lập luận, diễn giải và kết luận là của tác giả; Claude góp ý, chỉ ra chỗ claim vượt evidence.
- Phản biện draft hay claim: `peer-review`, `scientific-critical-thinking`.

## Code

- Module mới phải trả lời được: scientific purpose, experiment nào dùng, metric nào (master plan X.3).
- Chạy `python -m pytest -q` trước khi báo xong.
- Không thêm dependency vào `pyproject.toml` khi chưa có experiment cần. Thư viện phụ trợ: `tools/research/requirements-research.txt`.

## Zotero (nếu đã cài `zotero-cli`)

- Hỏi tác giả trước khi chạy `zotero-cli delete`, gộp duplicate hoặc sửa metadata hàng loạt.
