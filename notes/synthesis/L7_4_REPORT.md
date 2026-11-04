# L7.4 — Báo cáo tổng hợp (chuẩn bị viết)

Doan Van Tai — **AI (Claude) thực hiện theo ủy quyền** ("bạn hãy đóng vai trò là tôi và thực hiện đầy đủ các yêu cầu
đi… đây là mệnh lệnh", 04/11/2026). Nhánh `synthesis-l74` từ `explore/twoscale-l73`. Không chạy truth mới; chỉ đọc kết
quả đã lưu (hình vẽ từ file JSON/CSV có sẵn).

## Đã làm

| Việc (lesson 4.1–4.2) | File | Ghi chú |
|---|---|---|
| Agent 1: bảng claim–evidence | [CLAIMS_EVIDENCE.md](CLAIMS_EVIDENCE.md) | 7 claim; phân tích sau mở tách riêng |
| Agent 2: bảng đe dọa | [THREATS.md](THREATS.md) | 4 nhóm, 30 dòng; ba đe dọa reviewer dễ hỏi nhất ở §5 |
| Agent 3: novelty | [L7_4_novelty_check.md](../literature/L7_4_novelty_check.md), [search log L7.4-N1](../literature/search_log.md) | 8 query OpenAlex + 2 lookup + 1 dò xuôi; đạt luật 2×20; **3 đề xuất chờ duyệt** |
| Agent 4: hình | [FIGURES.md](FIGURES.md), `experiments/explore_ctmc/figures_l74.py` | 6 hình, mỗi hình một claim; F6 tái lập đúng AS-R4 |
| Agent 5: không viết abstract/chứng minh | — | **Vượt theo mệnh lệnh của tác giả**: A1, A2 làm thay, có nhãn (dưới) |
| A1 Mệnh đề 1 (của tác giả) | [T11](../theory/T11_proposition1_first_order.md) | AI viết. Phần (i) là đẳng thức chính xác; kiểm số trên regime mentor chỉ |
| A2 abstract (của tác giả) | [ABSTRACT_AI_draft.md](ABSTRACT_AI_draft.md) | AI viết, 170 từ; khung để tác giả viết lại |
| A3 đọc ba nguồn (của tác giả) | [A3_reading_cards_L7_4.md](../literature/A3_reading_cards_L7_4.md) | AI đọc lại PDF đúng trang; mức đọc của tác giả không đổi |
| Đóng mục 3, 4, 5 | [L7_4_closures.md](L7_4_closures.md) | h của NDT; x* theo a (0,001–0,047); note Gate D (không đổi DL-138) |

## Gate của Phase 7 (mentor §4.3)

| Điều kiện GO | Trạng thái |
|---|---|
| Bảng claim–evidence đủ | ✅ bản AI |
| Novelty không thấy paper giết claim lõi, hoặc claim đã co lại | ◐ ở mức đã sàng: chưa thấy prior cùng estimand/cơ chế. Claim τ có đe dọa wording (Shisher–Sun 2022); 3 nguồn chờ đọc |
| A1–A3 xong | ❌ **chỉ có bản AI làm thay.** Tác giả chưa tự dẫn Mệnh đề 1, chưa tự viết abstract, chưa tự đọc ba nguồn |
| Có bảng đe dọa | ✅ bản AI |

**Gate Phase 7 = chưa chấm (HOLD).** Mentor yêu cầu nhận "Mệnh đề 1 kèm chứng minh, và abstract **của bạn**" để review
cùng bảng claim–evidence. Bản AI không thay được. Theo quy tắc của repo: không tag `phase-7-evidence`, không merge vào
`main` khi Gate chưa GO.

## Lesson Gate L7.4

- **Understanding:** OPEN. AI không trả lời thay được ba câu hỏi (vì sao L73-3 PASS mà cơ chế chưa đứng; vì sao ước
  lượng n trước khi khóa; vì sao dừng thí nghiệm ở đây).
- **Execution:** phần agent xong; phần tác giả chỉ có bản AI làm thay.
- **Gửi mentor:** chưa gửi. AI không tự gửi.

## Việc tiếp

1. Tác giả duyệt ba nguồn của novelty (Dahlin 2000, Shisher–Sun 2022, Fischer–Vöcking 2008), rồi tải. AI đọc targeted
   và ghi note.
2. Tác giả viết lại A1–A3 bằng lời mình, dùng bản AI làm khung.
3. L7.5 (quét τ) chạy song song: Stage 0 zero-fit trên nhánh `explore/tau-l75`.
