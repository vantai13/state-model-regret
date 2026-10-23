# Bộ công cụ nghiên cứu cho repo `state-model-regret`

> Claude soạn ngày 23/10/2026 theo yêu cầu của tác giả Doan Van Tai; tác giả đọc, sửa và quyết định giữ hay bỏ. Mọi tool trong file đã được kiểm là có thật (repo GitHub, PyPI hoặc npm) vào ngày soạn. Mục 6 ghi rõ cái gì đã chạy thử và cái gì chưa.

## 0. Đọc trước: công cụ giúp gì và không giúp gì

Công cụ làm nhanh ba việc: **tìm** paper, **đọc** paper có dấu vết, **kiểm** citation và con số. Nó không tạo evidence và không mở gate nào.

Theo [Phase 1 closeout](../notes/phases/PHASE_1_closeout.md), các gate đang giữ HOLD là V1 (tính tay độc lập), P0-V3 (read-back), P0-V11 (artifact kín sách), V8 (giải thích cho người thật), P0-V10 (người đọc độc lập). Không công cụ nào trong file này làm thay được những việc đó. Master plan của bạn cũng đã ghi hai rủi ro: phình quy trình (ER1) và phụ thuộc AI (ER2). Vì vậy quy tắc dùng là: **một công cụ chỉ đáng mở khi bạn nói được nó giúp claim hay gate nào.**

Ký hiệu cấp độ:

- 🟢 **Người mới**: dùng ngay từ Phase 2a.
- 🟡 **Khi tới phase**: cài sẵn hoặc biết trước, dùng khi plan tới bước đó.
- 🔴 **Chuyên gia / để sau**: mạnh nhưng dễ làm thay bạn hoặc tốn công; chỉ dùng khi có lý do cụ thể.

## 1. Đã cài sẵn trong repo

Chỉ cần lấy branch này về máy và mở Claude Code trong thư mục repo.

| Thành phần | File | Chức năng |
|---|---|---|
| MCP `arxiv` (arxiv-mcp-server 0.8.2, Apache-2.0) | `.mcp.json` | Tìm arXiv, tải và đọc từng section (cả bản LaTeX gốc), xuất BibTeX, `citation_graph` (references + citing qua Semantic Scholar), theo dõi chủ đề mới |
| MCP `papersearch` (paper-search-mcp 0.1.4, MIT) | `.mcp.json` | Tìm trên dblp, OpenAlex, Semantic Scholar, Crossref, arXiv, CORE, Unpaywall và nhiều nguồn khác; tra DOI |
| Chặn và cho phép tool | `.claude/settings.json` | **Chặn** `download_scihub` và `download_with_fallback` (có nhánh Sci-Hub). **Không hỏi lại** cho tool chỉ-đọc (search, abstract, outline). Tool tải file vẫn hỏi trước |
| Quy tắc cho Claude | `CLAUDE.md` | Không làm thay gate, không bịa citation, không Sci-Hub, không commit PDF, tách Fact/Claim/Evidence/Inference |
| Skill `search-log` (tự viết) | `.claude/skills/search-log/` | Ghi mỗi lần tìm vào `notes/literature/search_log.md`; quy trình citation chaining; danh sách seed P11, P12, P13, P01, P02 |
| Skill `paper-note` (tự viết) | `.claude/skills/paper-note/` | Tạo note theo template A.5, ghi mức đọc thật, đánh dấu phần AI trích; các ô Inference, Overlap, Effect on gap để `TODO(tác giả)` |
| 8 skill của K-Dense (MIT) | `.claude/skills/` | Xem bảng ở mục 3; nguồn gốc ở `tools/research/THIRD_PARTY_SKILLS.md` |
| Script cài và kiểm | `tools/research/` | `setup.sh` (macOS/Linux/WSL), `setup.ps1` (Windows), `check_mcp.py` (kiểm server và luật chặn), `requirements-research.txt` |
| `.gitignore` | `.gitignore` | Thêm `downloads/`, `papers_local/`: PDF tải về không bao giờ vào repo |

## 2. Bật trên máy của bạn (làm một lần)

1. Cài Claude Code theo tài liệu chính thức nếu chưa có. Cài [uv](https://docs.astral.sh/uv/) (script ở bước 3 có thể cài giúp).
2. Lấy branch về: merge PR `research-tooling` trên GitHub rồi `git pull`, hoặc `git fetch && git checkout research-tooling`.
3. Chạy script (tạo `.venv`, cài thư viện, chạy 165 test, kiểm hai MCP server, thử một truy vấn thật):
   - macOS / Linux / WSL: `bash tools/research/setup.sh` (thêm `--install-uv` nếu chưa có uv, `--zotero` nếu đã cài Zotero desktop).
   - Windows: `powershell -ExecutionPolicy Bypass -File tools\research\setup.ps1` (thêm `-InstallUv`, `-Zotero`).
4. Đặt biến môi trường (không ghi vào repo):
   - `UNPAYWALL_EMAIL`: email của bạn. Unpaywall cần email để trả link bản open access hợp pháp.
   - `SEMANTIC_SCHOLAR_API_KEY` (khuyên dùng, miễn phí): xin tại trang API của Semantic Scholar; tránh bị giới hạn tốc độ khi chạy `citation_graph`.
5. Mở `claude` trong thư mục repo, chấp nhận hai server `arxiv` và `papersearch` khi được hỏi. Gõ `/mcp` để xem trạng thái. Claude Code luôn hỏi trước khi bật MCP server của một repo mới clone; đó là cơ chế an toàn, không phải lỗi ([MCP docs](https://code.claude.com/docs/en/mcp)).
6. Thử: `/search-log "expected value of model improvement"`, rồi `/paper-note P11 10.1137/120889563`.

Kiểm lại bất cứ lúc nào: `python tools/research/check_mcp.py --live`.

## 3. Danh mục theo việc

Trạng thái: **Repo** = đã cài trong repo · **Script** = `setup.sh --zotero` hoặc `requirements-research.txt` cài · **Tự cài** = phần mềm desktop · **Web** = dùng trên trình duyệt, miễn phí hoặc có gói miễn phí.

### 3.1. Tìm paper và lần theo trích dẫn

| Công cụ | Chức năng | Cấp | Khi nào | Trạng thái |
|---|---|---|---|---|
| Skill `search-log` | Có log thì câu "đã tìm ở đâu" kiểm được; cảnh báo "rỗng ≠ không tồn tại" | 🟢 | Phase 2 trở đi | Repo |
| MCP `papersearch` | Tìm rộng: `search_dblp` (rất mạnh cho CS và networking), `search_openalex`, `search_semantic`, `search_crossref` | 🟢 | Phase 2 | Repo |
| MCP `arxiv` | Preprint, `citation_graph` cho citation chaining | 🟢 | Phase 2 | Repo |
| Skill `paper-lookup` | Truy 18 API (OpenAlex, Crossref, Semantic Scholar, OpenCitations, Unpaywall, CORE…) bằng `curl`, kèm provenance; forward citation bằng OpenAlex `filter=cites:` | 🟢 | Phase 2 | Repo |
| [dblp](https://dblp.org), [Semantic Scholar](https://www.semanticscholar.org), Google Scholar (bật alert theo tác giả và paper seed) | Tìm và theo dõi tay, đối chiếu với kết quả của Claude | 🟢 | Luôn | Web |
| [Inciteful](https://inciteful.xyz), [Connected Papers](https://www.connectedpapers.com), [ResearchRabbit](https://www.researchrabbit.ai) | Vẽ mạng trích dẫn quanh vài paper seed, tìm paper "hàng xóm" mà từ khoá bỏ sót | 🟡 | Khi xong vòng tìm từ khoá đầu tiên | Web |
| `pyalex` (OpenAlex), `habanero` (Crossref) | Tìm và chaining bằng code khi cần tái lập hàng trăm truy vấn | 🔴 | Final novelty audit (Phase 9) | Script |
| [openalex-mcp](https://github.com/reetp14/openalex-mcp) (npm) | MCP riêng cho OpenAlex | 🔴 | Không cần: `paper-lookup` và `papersearch` đã phủ; repo này cập nhật lần cuối 07/2025 | Không cài |

### 3.2. Quản lý tài liệu và citation

| Công cụ | Chức năng | Cấp | Khi nào | Trạng thái |
|---|---|---|---|---|
| [Zotero](https://www.zotero.org) 7+ | Thư viện tài liệu, lưu PDF hợp pháp, ghi chú, xuất citation | 🟢 | Ngay, trước khi đọc paper đầu tiên | Tự cài |
| [Better BibTeX](https://retorque.re/zotero-better-bibtex/) (plugin Zotero) | Citation key ổn định, tự xuất `.bib` mỗi khi thư viện đổi | 🟢 | Cùng lúc với Zotero | Tự cài |
| `zotero-cli` + skill `zotero-cli` ([zotero-mcp-server](https://github.com/54yyyu/zotero-mcp), MIT) | Claude tìm, đọc, chú thích trong thư viện Zotero của bạn qua shell. Tác giả tool khuyên dùng CLI thay MCP server vì rẻ context hơn nhiều | 🟡 | Khi thư viện có trên ~20 paper | Script (`--zotero`) |
| Skill `citation-management` | DOI → BibTeX, `validate_citations.py --check-dois` bắt reference sai hoặc không tồn tại | 🟢 | Mỗi lần thêm reference | Repo |
| [JabRef](https://www.jabref.org) | Thay thế Zotero nếu bạn muốn chỉnh `.bib` trực tiếp | 🔴 | Chỉ khi không dùng Zotero | Tự cài |

### 3.3. Đọc paper

| Công cụ | Chức năng | Cấp | Khi nào | Trạng thái |
|---|---|---|---|---|
| Skill `paper-note` | Note theo template A.5; mức đọc thật; Fact/Claim/Evidence/Inference; dòng matrix | 🟢 | Mỗi paper | Repo |
| MCP `arxiv`: `get_paper_outline`, `read_paper_section`, `get_paper_latex_section` | Đọc từng section, xem phương trình bằng LaTeX gốc thay vì PDF bị vỡ ký hiệu | 🟢 | Paper có trên arXiv | Repo |
| Unpaywall (qua `papersearch` hoặc `paper-lookup`) | Tìm bản open access hợp pháp khi link publisher trả 403 (đã gặp ở T03) | 🟢 | Khi không mở được bản publisher | Repo |
| Thư viện UIT, liên thông thư viện, email tác giả | Bản full text khi không có open access | 🟢 | Khi Unpaywall không có | — |
| Skill `scientific-critical-thinking` | Hỏi vặn: claim nào vượt evidence, confounder, giả định | 🟢 | Sau khi tự đọc xong, trước khi điền "Effect on gap" | Repo |
| [PaperQA2](https://github.com/Future-House/paper-qa) (Apache-2.0) | Hỏi đáp có trích dẫn trên một tập PDF lớn; cần API key mô hình | 🔴 | Không cần ở quy mô 13–30 paper; đọc tay có giá trị học hơn | Không cài |
| [GROBID](https://github.com/kermitt2/grobid), [marker](https://github.com/datalab-to/marker) | Tách PDF thành văn bản có cấu trúc, trích references hàng loạt | 🔴 | Chỉ khi phải xử lý hàng trăm PDF | Không cài |

### 3.4. Thiết kế thí nghiệm, thống kê, mô phỏng

| Công cụ | Chức năng | Cấp | Khi nào | Trạng thái |
|---|---|---|---|---|
| `hypothesis` (thư viện Python) | Property-based testing: tự sinh hàng nghìn input để kiểm invariant (bảo toàn, R11 = 0, đối xứng A/B). Hợp với lối test hiện tại của repo | 🟢 | Ngay, cho test mới | Script |
| Skill `experimental-design` | Thiết kế factorial, blocking, tránh confounding | 🟡 | Phase 3–4 (thiết kế 2×2, lưới) | Repo |
| Skill `statistical-power` | Số episode cần có, power bằng mô phỏng Monte Carlo | 🟡 | Phase 4, L4.3 | Repo |
| `statsmodels` | CI, TOST equivalence (`ttost_paired`), hồi quy | 🟡 | Phase 4–6 | Script |
| Skill `simpy` + thư viện `simpy` | Discrete-event simulation; ứng viên representation độc lập | 🟡 | Phase 7 | Repo + Script |
| [Ciw](https://github.com/CiwPython/Ciw) (MIT) | DES chuyên cho mạng hàng đợi | 🔴 | Phase 7 nếu SimPy không đủ | Không cài |
| ns-3, OMNeT++ | Mô phỏng mạng mức packet đầy đủ | 🔴 | Chỉ khi một claim cần packet-level; master plan đặt việc này sau Gate E | Không cài |

### 3.5. Ghi chú và tư duy

| Công cụ | Chức năng | Cấp | Trạng thái |
|---|---|---|---|
| Markdown trong `notes/` + git (đang dùng) | Đủ cho cả project; có lịch sử và diff | 🟢 | Có sẵn |
| [Zettlr](https://www.zettlr.com) (mã nguồn mở) hoặc Obsidian (miễn phí, không mã nguồn mở) | Đọc và liên kết note markdown dễ hơn; mở thẳng thư mục `notes/` | 🔴 | Tự cài, không bắt buộc |

### 3.6. Viết paper

| Công cụ | Chức năng | Cấp | Khi nào | Trạng thái |
|---|---|---|---|---|
| [Overleaf](https://www.overleaf.com) với template IEEEtran | LaTeX trên web, không cần cài; venue networking (INFOCOM, ToN, TNSM) dùng IEEE | 🟢 | Phase 10, hoặc báo cáo NCKH | Web |
| TeX Live / MiKTeX hoặc [Tectonic](https://tectonic-typesetting.github.io) + VS Code + [LaTeX Workshop](https://github.com/James-Yu/LaTeX-Workshop) | Viết LaTeX offline, build trong repo | 🟡 | Khi muốn bản thảo nằm trong git | Tự cài |
| [LTeX+](https://github.com/ltex-plus/vscode-ltex-plus) (VS Code, dùng LanguageTool) | Bắt lỗi ngữ pháp, chính tả tiếng Anh ngay trong file `.tex` và `.md` | 🟡 | Khi viết tiếng Anh | Tự cài |
| [Pandoc](https://pandoc.org) | Đổi markdown ↔ LaTeX ↔ Word | 🔴 | Khi cần nộp định dạng khác | Tự cài |
| Skill `scientific-writing` | Rà draft: provenance của evidence, nhất quán số liệu, reporting. **Chỉ chạy khi bạn gõ `/scientific-writing`** | 🟡 | Có draft của chính bạn | Repo |

### 3.7. Phản biện trước khi gửi người đọc

| Công cụ | Chức năng | Cấp | Khi nào | Trạng thái |
|---|---|---|---|---|
| Skill `peer-review` | Review có cấu trúc: claim–evidence, phương pháp, thống kê, citation; chạy offline | 🟡 | Trước khi gửi GVHD hoặc reviewer | Repo |
| `validate_citations.py --check-dois` | Bắt reference bịa hoặc sai metadata | 🟢 | Mỗi lần gửi tài liệu có reference | Repo |
| [academic-research-skills](https://github.com/Imbad0202/academic-research-skills) (CC BY-NC 4.0) | Bộ multi-agent: deep-research, academic-paper, academic-paper-reviewer (read-only), pipeline 10 bước | 🔴 | Phase 9–10, chủ yếu phần reviewer. Cài: `/plugin marketplace add Imbad0202/academic-research-skills` rồi `/plugin install academic-research-skills` | Không cài |
| Người đọc thật (GVHD, bạn học) | Phép kiểm độc lập duy nhất; mock review của AI không thay được (P0-V10) | 🟢 | Mỗi gate | — |

## 4. Không khuyến nghị

| Thứ | Vì sao |
|---|---|
| Sci-Hub, LibGen và mirror tương tự | Vi phạm bản quyền ở nhiều nơi; rủi ro pháp lý và học vụ. Đã chặn trong repo. Dùng open access, thư viện UIT hoặc xin tác giả |
| Tool "AI viết cả paper" (sinh idea, chạy thí nghiệm, viết bản thảo tự động) | Làm thay đúng phần bạn phải tự sở hữu; trái quy tắc ownership của repo |
| Tool "humanizer" hay "né AI detector" | Che giấu mức độ dùng AI là vấn đề liêm chính học thuật. Ghi provenance thay vì che |
| Google Scholar làm nguồn metadata chính | Không có API chính thức, hay chặn truy vấn tự động; dùng dblp, OpenAlex, Crossref làm nguồn chuẩn |
| Cài thêm MCP server "cho đủ bộ" | Mỗi server thêm tool, thêm thứ phải kiểm. Thêm khi có việc cụ thể cần |

## 5. Ví dụ một vòng làm việc ở Phase 2a

1. `/search-log` với câu hỏi gắn claim: "Giá trị của model repair (M0 → M1) đã được đặt tên và đo trong literature chưa?"
2. Claude tìm trên `papersearch` (dblp, OpenAlex) và `arxiv`, ghi từng truy vấn vào `search_log.md`.
3. `/paper-note P11 10.1137/120889563`: Claude tìm bản hợp pháp, điền phần trích kèm §, để trống phần của bạn.
4. **Bạn** đọc section được chỉ ra, tự điền "Inference của tôi" và "Effect on gap".
5. Hỏi `scientific-critical-thinking` phản biện chính phần bạn vừa viết.
6. Thêm reference vào `.bib` qua Zotero + Better BibTeX, chạy `validate_citations.py --check-dois`.

Một lưu ý từ chính repo: [T03](../notes/theory/T03_primary_reading_start.md) ghi đã mở Strong, Oakley, Brennan (2014) về EVPPI (Medical Decision Making, DOI 10.1177/0272989X13505910). P11 trong Final Review là một paper khác của cùng nhóm: Strong, Oakley (2014), *When Is a Model Good Enough?…*, SIAM/ASA JUQ, DOI 10.1137/120889563. Nên kiểm lại ánh xạ này trước khi đánh dấu P11 đã đọc.

## 6. Đã kiểm gì, chưa kiểm gì

Đã chạy trong môi trường của Claude (Linux, Python 3.13) ngày 23/10/2026:

- Hai MCP server khởi động và trả danh sách tool: `arxiv` 19 tool, `papersearch` 57 tool.
- `paper-search-mcp` 0.1.4 **hỏng** với thư viện `mcp` 2.x (lỗi import `FastMCP`). `.mcp.json` đã ghim `--with "mcp<2"`; sau đó chạy được.
- Hai luật chặn Sci-Hub khớp đúng tên tool có thật; mọi luật allow khớp tool có thật.
- `setup.sh --no-live` chạy trọn: tạo `.venv`, cài thư viện, **165/165 test đạt**, kiểm MCP đạt.
- `validate_citations.py` chạy offline và bắt được entry thiếu trường.
- Claude Code nhận ra 9 skill trong danh sách tự dùng; `scientific-writing` không có trong danh sách đó, đúng với cấu hình chỉ chạy khi gọi tay.

Chưa kiểm được:

- **Truy vấn thật tới arXiv, Crossref, OpenAlex, Semantic Scholar**: mạng của môi trường soạn chặn các API này (arXiv trả 403; Crossref trả danh sách rỗng mà không báo lỗi). Chạy `python tools/research/check_mcp.py --live` trên máy bạn để kiểm.
- `setup.ps1` chưa chạy trên Windows thật.
- `zotero-cli` mới được cài và cài skill trong một thư mục home tạm; chưa nối với Zotero desktop thật.

Về chi phí context: `papersearch` có 57 tool. Claude Code mặc định dùng tool search nên chỉ tải tool khi cần ([MCP docs](https://code.claude.com/docs/en/mcp)). Nếu bạn tắt tool search, cân nhắc bỏ `papersearch` khỏi `.mcp.json`.

## 7. Cập nhật

- MCP server đang ghim phiên bản trong `.mcp.json`. Muốn nâng: sửa số phiên bản, chạy `check_mcp.py --live`, rồi commit.
- Skill K-Dense: làm theo `tools/research/THIRD_PARTY_SKILLS.md`.
- Bỏ một thứ: xoá dòng trong `.mcp.json` hoặc thư mục trong `.claude/skills/`. Không có gì khác phụ thuộc vào chúng.
