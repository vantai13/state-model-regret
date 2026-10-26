# L2.8 follow-up — nhật ký tiến độ (ghi ngay sau từng bước)

Người phụ trách: **Doan Van Tai** · ngày thực 26/10/2026 (UTC bắt đầu 11:23Z).
AI (Claude) thực hiện theo yêu cầu tác giả trong hội thoại 26/10: (1) P02 từ PDF
tác giả tự tải; (2) sàng abstract/metadata 6 đề xuất đang chờ; (3) phần kỹ thuật
còn thiếu của L2.8 (mục A/B của yêu cầu bàn giao). **Không làm L2.9** theo yêu cầu
tác giả. Base commit: `7f590236791f73dff8d8ff9f4db3df65eca1810f`, worktree sạch.

## Bước 1 — P02 (11:10–11:23Z)

- Nguồn: tác giả tự tải từ ScienceDirect vào Windows Downloads,
  `1-s2.0-S0968090X23001638-main.pdf`, mtime 2026-10-26 18:15 (giờ máy).
  sha256 `52c9b97d839d7924610fd23993fc1cec0d29d7decc2f096922587f464cc3f686`,
  2 500 525 bytes, 20 trang, PDF metadata: TR-C 153 (2023) 104174,
  doi:10.1016/j.trc.2023.104174, Creator Elsevier. Trang 1: Received 05/09/2022,
  revised 15/02/2023, accepted 14/05/2023, online 28/06/2023, CC BY 4.0.
  → bản **VoR**, khớp record TU Delft (final published version, 20 trang, CC BY).
- Lưu ngoài Git: `~/papers/state-model-regret/intake/2026-10-26_P02/P02_Poelman2023_TRC153_104174_VoR.pdf`;
  symlink `current/P02_Poelman2023_TRC_VoR.pdf`; text pdftotext -layout
  `current/P02_Poelman2023_TRC_VoR.txt` sha256 `77cf955a…f608d`.
- AI đọc text trang 1–19 (§1–§5) và render Bảng 2 trang 16 ở 220 dpi.
  Hình 1–6 chỉ đọc caption/text, không kiểm số trên đồ thị.
- Phát hiện chính (chi tiết ở note P02):
  - §3.3.1 tr15: bias thí nghiệm **một đại lượng mỗi lần**, các đại lượng khác
    chính xác; §4 tr18 nhắc lại "disturbed one by one", joint bias chưa làm.
  - Bảng 2 tr16: mỗi mức bias được quét theo prediction horizon 12/30/60 s
    (update 12 s) và update horizon 12/30/60 s (prediction 60 s): hai lát 1-D.
  - §2.2.4 tr10: reference biết demand cá nhân "recorded in advance", state
    đúng; bias e ∈ [−1,1] (turn fraction có cận riêng); bias đặt trên thế giới
    đã aggregation (step III).
  - §2.2.3 tr9–10: solver heuristic B&B greedy tail, <1% so full B&B (Fig.3d).
  - §3.2 tr13: aggregation 85→105 s/veh; 85% turn fractions/10% arrivals/5% driving.
  - §3.3.2 tr16 + §4 tr18: reinitialization bù một phần; state bias lớn làm mất bù.
  - §4 tr18: bias ≤20% → loss ≤25%; 50% → ≤150%. §5 tr19: update 60→12 s ↑≤30%.

## Bước 2 — Phiên tìm mới (bắt đầu 11:36Z)

- Script `experiments/lessons/l2_8_followup_search.py`; thẻ phiên `session_card.md`
  viết trước call; dedup `known_ids.json`.
- FU_A1_v1 (OpenAlex `search=` full text, 20/77): 0 giữ, 3 T3 context, 2 unclear
  (thiếu abstract), 15 exclude. **Chất lượng query thấp**: 2/20 thuộc mạng/truyền
  thông; full-text search kéo preprint 2026 ngoài lĩnh vực. Không coi là negative
  search có thông tin.
- CSV sàng đầu tiên viết tay có lỗi chép ID rank2 (W7164920690 → đúng W7164923690);
  thêm lệnh `screen` sinh CSV từ raw, ghi đè đúng 1 lần (`--replace`) trước commit.
- **Deviation thẻ phiên**: từ call sau, keyword thử S2 `/paper/search` (title+abstract
  relevance) trước; 429 → OpenAlex `title_and_abstract.search` sort relevance.
- FU_A1_v2: S2 search 429×3 (11:38–11:40Z, ghi 3 attempts). Fallback FU_A1_v2_oa
  (OpenAlex title+abstract, `network digital twin what-if decision`, 20/269):
  1 candidate_T2 mới (NMF adaptive NDT synchronization, DOI 10.1145/3769700.3771695),
  1 known (= snowball L2.4 arXiv2505.04879, ICC-W 2025), 6 T3, 12 exclude.
- FU_A1_fwd (OpenAlex cites P04, publication_date desc, 20/166; mới nhất 2022):
  1 candidate_T2 mới (Levin et al. "Logically centralized?" HotSDN 2012, DOI
  10.1145/2342441.2342443), 12 T3 (P04/M00 family, 2 cặp bản trùng), 2 unclear, 5 exclude.
- A1: 60 record sàng; luật dừng **không đạt** (v2 có candidate mới).
- A2: FU_A2_v1 S2 429×2 → FU_A2_v1_oa (TA không ngoặc) **nhiễu 20/20** (tách "age of
  information"), giữ log, không coi là negative search; FU_A2_v1b_oa (`"age of
  information" model mismatch`, TA) chỉ 7 record, 0 giữ; FU_A2_v2 (full-text
  `"age of information" "certainty equivalence"`, 20/24): 0 mới, 1 known (2403.11926
  ~ R32); CE trong NCS chủ yếu nghĩa #2 (state estimate), khác M0 (#3).
- FU_A2_fwd (S2 citations ARXIV:2504.19507): **thành công**, 1 record = chính bản
  journal TIT2026 của S11 (S2 tách 2 record). FU_A2_fwd_journal (DOI TIT): attempt1
  429, attempt2 OK, 9 citing; 1 candidate_T2 mới (arXiv2609.06351 information
  architecture freshness/locality), 1 trùng trong phiên.
- A2: luật dừng **không đạt** (v1b <20; v1_oa không hợp lệ vì nhiễu).
- A3: FU_A3_v1 (full-text `"decision-focused" network "traffic engineering"`, 20/22):
  1 candidate_T2 mới (CENTILE arXiv2608.01725), 8 T3, 1 unclear, 10 exclude;
  FU_A3_v2 (`"decision-aware" "digital twin"`, 20/71): 20 exclude (ngoài mạng).
  Forward P07 **không chạy được**: OpenAlex title 0, S2 429×3, MCP scholar-search
  trả 3 bài khác (fallback arXiv) — xem mcp_calls.json. P03 cited_by 0.
- A3: luật dừng **không đạt** (v1 có candidate; forward thiếu).
- Dừng phần keyword/forward theo ngân sách (OpenAlex shared budget, S2 429 lặp).

## Bước 3 — Sàng 6 đề xuất + R06 (12:00–12:08Z)

- arXiv API 1 call (6 IDs), Crossref 2 DOI + 5 title queries; xong. Kết quả và AI
  đề xuất ở `proposals_screen.md`. 2505.04879 = ICC-W 2025 (Crossref). R06 v1
  02/02/2026; Crossref có CDC 2025 cùng tác giả, khác tiêu đề (chưa xác minh quan hệ).
- 3 đề xuất mới (N1 arXiv2609.06351, N2 CoNEXT'25 SW 10.1145/3769700.3771695,
  N3 arXiv2608.01725) đã kiểm danh tính chính thức; Levin HotSDN 2012 defer.

- 12:15Z: sửa 3 dòng số đếm chép tay ở trên cho khớp `screen/*.csv` (A1_v2_oa,
  A1_fwd, A3_v1); quyết định từng rank không đổi. Tổng 157 record sàng, 4 candidate_T2.

## Bước 4 — Ghi notes, Excel, kiểm (12:15–12:40Z)

- P02 note AI-T; MT/K-M addendum; search_log/audit_sessions/README/AGENTS append.
- `l2_8_followup_p02_record.py` + `build_notes.py`: PASS, 19 nguồn, 17 PDF local.
- `l2_8_resolving.py`: PASS, output Part2 trùng byte. `audit_l2_8_part2.py`: FAIL có
  chủ đích tại dòng 99 (dòng AI của P02 đổi); kiểm riêng: chỉ P02 khác.
- `audit_l2_8_followup.py`: lần 1 sai kỳ vọng vị trí dòng Huong_dan, lần 2 link tới
  output của chính audit; sửa kỳ vọng (không nới check nội dung) → PASS.
- pytest 202 passed; git diff --check sạch.
- `git diff --cached --check` báo CSV có CRLF (csv.writer mặc định); đổi script sang
  LF theo quy ước repo (commit 08eca9b) và sinh lại 10 CSV từ cùng decisions.json —
  nội dung không đổi. Audit PASS lại, cached check sạch.
