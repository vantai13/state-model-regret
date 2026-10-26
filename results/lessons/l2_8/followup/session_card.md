# Thẻ phiên L2.8 follow-up — viết trước các call sàng, 26/10/2026 (~11:35Z)

Người phụ trách: **Doan Van Tai**. AI soạn/chạy theo yêu cầu tác giả; thẻ này là
thẻ của AI, không thay "Viết bốn thẻ phiên" mà PHASE_2 v2.0 §13 giao tác giả.
Không chạy lại hoặc ghi đè 169 screening events của Part2; lượt này là phiên mới.

## Vì sao có phiên này (gap đọc từ ledger Part2 và search_log)

| Gap Part2 | Ảnh hưởng kết luận | Xử lý lượt này |
|---|---|---|
| A1_q1 nhiễu (routing không phải mạng), A1_q2 chỉ 19, forward P04 chỉ `title.search:model` (5 records) | Vùng A1 networking — ưu tiên số 1 của AGENTS — mỏng | 2 query từ vựng networking theo PHASE_2 §13 K2 + forward P04 không lọc tiêu đề |
| A2_q1 nhiễu (ages/brain/education); A2 forward S11 bị S2 429 cả retry | Không có negative search AoI có nghĩa | 2 query AoI có cụm từ; thử lại S2 citations S11 (arXiv record) |
| A3_q1 Scholar timeout cả 2 lần; A3 dùng từ vựng ML, không DT/TE | A3 chưa có phiên networking | 2 query decision-focused/decision-aware DT/TE theo §13 K2 |
| R06 (anchor A4 trong PHASE_2 §5.4/§13) mới kiểm danh tính 24/10 | PC3 có thể bị đe dọa bởi CE trong partially observed systems | lookup abstract R06 (arXiv API), không tải PDF |
| Raw từng rank không giữ | Không audit lại được | Script lưu body HTTP + sha256 ngay sau call; CSV sàng viết ngay sau mỗi call |

## Thẻ tìm (theo search_protocol)

| Vùng | Câu hỏi | PC / câu chặn | GIỮ nếu | BỎ nếu |
|---|---|---|---|---|
| A1 | Có bài routing/TE/NDT nào sửa riêng thông tin state và model trong cùng protocol, rồi đo khác biệt/tương tác lên chất lượng quyết định? | PC3/PC4: nếu có bài đo tương tác state-info × model cho quyết định dời tải, PC3 có thể NARROW/PIVOT | Có action/decision cost và tách hai can thiệp (state info vs model) | Vehicle/robot routing, chỉ KPI prediction không có quyết định, quantum/ML không mạng |
| A2 | Giá trị của độ tươi thay đổi thế nào khi model của người quyết định sai/đơn giản hóa (CE)? | PC3/PC6: nếu prior đã cho dấu/điều kiện của tương tác freshness × CE, PC3 bị thu hẹp và có thể là prediction cho H1 | AoI/VoI có model mismatch hoặc CE và downstream cost | AoI thuần (không model mismatch), sinh học/giáo dục |
| A3 | Có bài DT/TE đo giá trị của model "đủ cho quyết định" khi state cũng bất định? | PC5/PC3: nếu có, ranh giới equivalence theo mức thông tin có prior | Decision-focused/decision-aware model cho mạng/TE, có state uncertainty | DT công nghiệp/y tế không có quyết định mạng; chỉ tên "decision-aware" |
| A4 | R06: sub-optimality của CE policy trong partially observed systems có nói về giá trị thông tin dưới CE không? | PC3 | Abstract nêu bound phụ thuộc thông tin/estimation | — |

## Query, tool, bộ lọc

| call_id | Loại | Seed | Provider | Thứ tự/giới hạn |
|---|---|---|---|---|
| FU_A1_v1 | keyword | `"stale" state "model mismatch" routing` | OpenAlex `search=` (title+abstract+fulltext) | relevance mặc định, 20 |
| FU_A1_v2 | keyword | `"network digital twin" "what-if" accuracy decision` | OpenAlex | relevance, 20 |
| FU_A1_fwd | forward | P04 `W2111010037` (doi 10.1109/90.917073) | OpenAlex `filter=cites:` | `publication_date:desc`, 20 (gần nhất trước) |
| FU_A2_v1 | keyword | `"age of information" "model mismatch" decision` | OpenAlex | relevance, 20 |
| FU_A2_v2 | keyword | `"age of information" "certainty equivalence"` | OpenAlex | relevance, 20 |
| FU_A2_fwd | forward | S11 `ARXIV:2504.19507` | Semantic Scholar citations | provider order, 20; 429 → ghi, không là 0 citations |
| FU_A3_v1 | keyword | `"decision-focused" network "traffic engineering"` | OpenAlex | relevance, 20 |
| FU_A3_v2 | keyword | `"decision-aware" "digital twin"` | OpenAlex | relevance, 20 |
| FU_A3_fwd | forward | P07 DOTE (ID tra lúc chạy) | OpenAlex cites hoặc S2 | `publication_date:desc`, 20 |
| FU_A4_R06 | lookup | arXiv 2602.02814 | arXiv API | 1 |

Biến thể A2_v2 thay `"goal-oriented sampling" "model uncertainty"` của PHASE_2 vì
probe chỉ có 3 kết quả (không thể sàng 20). Chỉ dùng title+abstract filter thì
các query cụm từ còn 0–5 kết quả, nên dùng `search=` như Google Scholar (có full
text). **Probe thiết kế query** (~15 request OpenAlex/S2/arXiv lúc 11:24–11:33Z) chỉ
xem số đếm/ID neo, không sàng record; không tính vào screening events.

## Ngân sách và luật dừng

- OpenAlex không key: ngân sách chia sẻ ~0,10 USD/ngày, 0,001 USD/request. Không
  gửi email tác giả để xin key. Lookup metadata dùng arXiv/Crossref.
- Mỗi vùng tối đa 2 query × 20 + 1 forward × 20; ~45 phút toàn phiên.
- Luật dừng (protocol): 2 query liên tiếp của một vùng **mỗi query sàng đủ 20** và
  không giữ candidate mới → ghi "đạt luật dừng của protocol cho vùng X trong phiên
  này". Không phải saturation hay chứng minh bao phủ lĩnh vực.
- Sàng: tiêu đề → abstract provider (OpenAlex/S2). Thiếu abstract → `unclear`,
  không loại vì tiêu đề. Tier1 = có thể đổi nhãn PC3/PC5; Tier2 = gần estimand/
  mechanism, khác regime; Tier3 = context. Trùng thư viện/đã sàng → `known`.
- Tối đa **3 đề xuất mới** cho cả phiên; chờ tác giả duyệt trước PDF/note.
- Không đổi PC/contract/K5/null/H1, không L2.9, không chạy Phase3.

Dedup: [known_ids.json](known_ids.json) (catalog, archive, notes, screen cũ).
