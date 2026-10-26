# L2.8 follow-up — kết quả thực hiện, 26/10/2026

Người phụ trách: **Doan Van Tai** · AI (Claude) thực hiện theo yêu cầu tác giả;
chưa L-self/Gate. Base `7f590236791f73dff8d8ff9f4db3df65eca1810f`.
**Không làm L2.9** (tác giả yêu cầu). Không đổi RQ, contract, metric, threshold,
PC forecast, K5, null/H1; không grid/held-out; không Phase3.

## Đã làm

1. **P02 không còn BLOCKED.** Bản VoR do tác giả tải (ScienceDirect, CC BY), lưu
   ngoài Git, sha256 `52c9b97d…3f686`, 20 trang. AI-T §1–§5 + Bảng 2 tr16 (render).
   [Note P02](../../../../notes/literature/papers/P02.md) (snapshot note cũ trong `snapshots/`).
2. **Dependency P02:** addendum MT1/MT2/MT6/MT7
   ([MT queue](../../../../notes/phases/PHASE_4_methodology_threats.md)) và K-M4/K-M5
   ([prior_boundary](../../../../notes/literature/prior_boundary.md), không đổi nhãn PC).
3. **Phiên tìm mới có raw** cho các gap ảnh hưởng kết luận của Part2 (A1 nhiễu/19
   record/forward lọc hẹp; A2_q1 nhiễu, S11 forward 429; A3 timeout, từ vựng ML).
   [Thẻ phiên](session_card.md) viết trước call; [script](../../../../experiments/lessons/l2_8_followup_search.py)
   lưu body HTTP + sha256 + giờ UTC ngay sau mỗi call; CSV sàng sinh từ raw.
4. **Sàng 6 đề xuất đang chờ + R06** ở mức abstract/metadata, và 3 đề xuất mới:
   [proposals_screen.md](proposals_screen.md). Chưa tải PDF, chưa note, chưa thêm Excel.
5. Catalog/Excel: chỉ record P02 đổi (AI level Abstract → Mục liên quan, có PDF local);
   19 nguồn, 19 mức "Mức tôi đã đọc" giữ nguyên.

## Kết quả định lượng

**P02 (số của paper, không tái lập):** bias **một đại lượng mỗi lần** (§3.3.1 tr15;
§4 tr18), mỗi mức quét 1-D với prediction 12/30/60 s và update 12/30/60 s (Bảng 2);
mức bias theo đại lượng: turn fraction ±20/±50/±100%, queue-head ±20/±50/±75%,
còn lại ±10/±20/±50%. Reference biết demand ghi sẵn (§2.2.4 tr10); solver heuristic
<1% so full B&B (Fig3d). Aggregation 85→105 s/xe (85% turn fraction); bias ≤20% →
loss ≤25%, 50% → ≤150%; update 60→12 s ↑≤30%. Không gán dấu Γ.

**Phiên tìm** ([calls.jsonl](calls.jsonl), [screen/](screen/)):

| Mục | Số |
|---|---:|
| Call / attempt trong ledger | 24 / 30 (21 HTTP200, 9 HTTP429) |
| Record sàng theo rank (A1 / A2 / A3) | **157** (60 / 57 / 40) |
| candidate_T2 mới / Tier1 | **4 / 0** |
| known / trùng trong phiên | 3 / 1 |
| T3 context / unclear (thiếu abstract) / exclude | 55 / 5 / 89 |
| Luật dừng 2×20 đạt ở vùng nào | **Không** |

Hai query (FU_A2_v1_oa, FU_A3_v2) nhiễu 20/20 và FU_A1_v1 18/20 ngoài mạng: ghi
đủ, không coi là negative search có thông tin. Forward P07 không chạy được
(OpenAlex không có record, S2 429 ×3, MCP fallback trả bài khác).

## Commands thực chạy

```bash
.venv/bin/python -I -B experiments/lessons/l2_8_followup_search.py call|show|screen ...   # 24 call, xem calls.jsonl
.venv/bin/python -I -B experiments/lessons/l2_8_followup_p02_record.py
.venv/bin/python -B tools/paper_library/build_notes.py          # PASS, 19 nguồn, 17 PDF local
.venv/bin/python -B experiments/lessons/l2_8_resolving.py       # PASS, output trùng byte bản commit
.venv/bin/python -B experiments/lessons/audit_l2_8_part2.py     # FAIL có chủ đích (dòng 99)
.venv/bin/python -B experiments/lessons/audit_l2_8_followup.py  # PASS (verification.json)
.venv/bin/python -m pytest -q
git diff --check
```

- `audit_l2_8_part2.py` **FAIL** ở `assert all(after[k]==v …)` dòng 99: check này
  đòi 13 dòng Ghi_chu_doc cũ không đổi so với trước Part2; follow-up cố ý cập nhật
  dòng AI của P02. Đã kiểm: chỉ P02 khác (note row và catalog), 0 mức tác giả đổi.
  **Không sửa check cũ**; audit mới kiểm phần còn lại.
- `audit_l2_8_followup.py` **PASS** ([verification.json](verification.json)): 30 attempt
  khớp raw/sha256, 157 rank khớp CSV, chỉ P02 đổi trong catalog/workbook, 0 mức tác giả
  đổi, 53 file lịch sử L2.7/L2.8 không đổi, 10 file append-only, 452 link, 0 PDF trong Git.
- `pytest -q`: **202 passed**. `git diff --check`: sạch.

## File

- Code: [l2_8_followup_search.py](../../../../experiments/lessons/l2_8_followup_search.py),
  [l2_8_followup_p02_record.py](../../../../experiments/lessons/l2_8_followup_p02_record.py),
  [audit_l2_8_followup.py](../../../../experiments/lessons/audit_l2_8_followup.py).
- Log/config: [session_log.md](session_log.md), [session_card.md](session_card.md),
  [calls.jsonl](calls.jsonl), [mcp_calls.json](mcp_calls.json), [known_ids.json](known_ids.json),
  [source_access.json](source_access.json), `raw/`, `screen/`, `snapshots/`.
- Notes cập nhật: P02, search_log, prior_boundary (append), matrix (dòng P02),
  audit_sessions, literature_audit_part2, model_fidelity_methods, already_implied,
  PHASE_4 MT, evidence inventory, exposure register, README các cấp, AGENTS.md.

## Giới hạn

- Mọi mức đọc là **AI-only**; P02 hình 1–6 chỉ đọc caption; số Bảng 2 do AI chép từ
  ảnh render (6 hàng), chưa có người kiểm.
- OpenAlex không key (ngân sách chia sẻ), S2 429 lặp → không đủ lượt để thử luật dừng;
  phiên vẫn có giới hạn, **không** saturation/coverage. 169 events cũ vẫn thiếu raw;
  phiên mới không thay thế hay tái dựng chúng.
- Đổi provider giữa phiên (S2 → OpenAlex TA, full-text → TA) đã ghi là deviation.
- PHASE_2 v2.0 lấy từ Downloads của tác giả (không có trong repo) để đối chiếu
  §5.4/§13; không thực hiện L2.9.

## Còn mở / bước tiếp theo

1. **Tác giả duyệt** (tối đa 3 mới): arXiv2609.06351 (N1), 10.1145/3769700.3771695 (N2),
   arXiv2608.01725 (N3); và quyết định 6 đề xuất cũ — AI đề xuất chỉ 2308.13166 đáng đọc T.
2. Tác giả L-self P02 nếu dùng làm nguồn quyết định nhãn PC2 (PHASE_2 §5.4).
3. Luật dừng 2×20 vẫn chưa đạt; muốn đạt cần thêm query hợp lệ (tốt nhất có API key
   do tác giả tự đăng ký) — chỉ làm khi tác giả yêu cầu.
4. L2.9, Gate L, A05, P0-V10, Phase3 giữ nguyên trạng thái mở.
