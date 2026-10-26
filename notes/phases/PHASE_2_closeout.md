# Phase 2 Closeout — HOLD

> Ngày: 26/10/2026 · Người phụ trách: **Doan Van Tai** · Contract: `contract-v1.2` · Tag: **chưa gắn** (`phase-2-closeout` chỉ gắn khi GO hoặc GO có điều kiện)
>
> **Provenance.** Toàn bộ file do AI (Claude) soạn **theo ủy quyền tác giả** ("đóng vai tác giả và thực hiện mọi thứ cần tác giả thực hiện", 26/10/2026). Theo PHASE_2 §20, hai mục đầu phải do tác giả tự viết: chúng vẫn **chưa có**; bên dưới mỗi mục chỉ là bản nháp AI được rào riêng, **không** là bằng chứng "tác giả đã học được". Nhãn và quyết định Gate là AI chọn theo ủy quyền, áp luật PHASE_2 §15–§17.

## What I understood

⟨Tác giả tự viết — chưa có.⟩

> **Bản nháp AI đóng vai tác giả — KHÔNG phải lời tác giả, không tính là understanding artifact.**
> Đề tài nằm ở hộp "đánh giá what-if trước action" của pipeline NDT: twin nhận một ước lượng state từ snapshot cũ để chấm Stay/Switch, và chính action làm đổi tải trên path B. Chữ "state" trong NDT1 là mô tả traffic/topology/cấu hình đưa vào twin; state của đề tài là backlog và mode hiện tại, ẩn sau một snapshot có tuổi. Nhiều mảnh của câu trả lời đã có tên: G_{S|M1} là EVPPI và G_{M|S1} là trung bình VSS dưới giả định ghi rõ; độ tươi đã được định giá theo cost quyết định (S11) và tuổi khác sai lệch (AoII); fidelity khác chất lượng quyết định (P03, NDT26); "model đủ cho quyết định" có lý thuyết (P12, AIS22); thông tin có thể làm hại một chính sách xấp xỉ và có điều kiện đủ để không hại (R02, R04); bảng 2×2 sửa hai nguồn lỗi đã có (WM26). Phần chưa xác nhận từ các nguồn đã đọc là Γ theo D19 với oracle không biết tương lai cho một quyết định dời tải có mode ẩn, vị trí ranh giới OεRE theo tọa độ queue, và tách backlog với mode. Khác biệt với WM26 có hậu quả: repair của họ nhập tương lai thật, nên gain của họ chứa EVPI của tương lai mà D18 loại ra. Literature không nâng gap khỏi G1, và Gate L đang HOLD vì nguồn quyết định nhãn chưa được chính tác giả đọc.

## What changed in my mental model

⟨Tác giả tự viết — chưa có.⟩

> **Bản nháp AI đóng vai tác giả — KHÔNG phải lời tác giả.**
> - "Thông tin mới không thể làm hại" chỉ đúng với policy tối ưu theo model đúng và thông tin lồng nhau (T03, K-S8); R02 Example 1 (tính lại: thiệt hại 0,507) cho thấy re-solving một chính sách xấp xỉ có thể làm hại, và R04 cho điều kiện đủ SC + Π-accuracy.
> - "κ nhỏ thì snapshot sai nhiều" là trực giác chưa có cơ sở: phương sai input không điều kiện trong 1 s tăng theo κ (SD 3,03 → 5,40 packet từ κ 0,3 → 3), nhưng đó không phải F của D22, nên không suy được chiều của F hay V.
> - "OAT là đủ" sai cho câu hỏi tương tác: P02 tự thừa nhận chỉ bias một đại lượng mỗi lần và joint bias có thể khuếch đại nhau (§4 tr18); muốn nói về Γ cần đủ bốn ô.
> - "Twin chính xác hơn thì quyết định tốt hơn" không phải định luật: P03 Thm 3.1 là một mệnh đề tồn tại, và WM26 F.1 cho thấy repair giảm nhiều MSE nhất không phải repair chọn tốt nhất.
> - Câu giữ về PC3: "Γ/Cref > 0,005 ở K3 theo D19, oracle không biết w". Nó không trùng WM26 vì repair của WM26 lộ tương lai, nên contrast của họ không cùng estimand.

## Decisions made

| DL | Quyết định |
|---|---|
| DL-040 | L2.1–L2.3: lưu artifact Part A sau exposure; formal gate HOLD |
| DL-041 | L2.6 Part B: P13 journal numbering, T-H1 là interpretation threat, không đổi D13 |
| DL-042 | Gate L: Main RQ **KEEP**; nhãn tạm (AI ủy quyền) PC1 DROP, PC2 NARROW, PC3 KEEP câu chữ/framing NARROW, PC4 HOLD, PC5 NARROW, PC6 NARROW; Gate **HOLD** |

## Evidence created

Toàn bộ là **AI-only** (AI-T/AI-A); **L-self 0/19**, chưa có dòng author-attested nào cho Phase 2. Chi tiết EV-37…EV-45 trong [evidence inventory](../00_evidence_inventory.md).

- Note nguồn AI-T: NDT1, NMRG-13, P05, P10, P04, M00, P01, S11, AoII, P13, P03, P07, P12, AIS22, R01, R02, R04, NDT26, WM26, **P02 (VoR, 26/10)**; AI-A: R43, B82, R06.
- [Bản đồ NDT](../literature/ndt_landscape.md); [OεRE draft](../literature/terms.md); [MT1–MT8](PHASE_4_methodology_threats.md); [prior boundary + nhãn tạm](../literature/prior_boundary.md); [related work](../literature/related_work_skeleton.md).
- Search: Part1 55 events, Part2 169 events (thiếu raw từng rank), follow-up 157 record có raw; 0 Tier1 ở follow-up; luật dừng 2×20 chưa đạt.
- Kiểm exact/toy: 625 (L2.4), 22 + 44 (L2.5), 293 + 122 (L2.6), 14 + 27 (L2.7), Cooper replay 18 case (L2.8). Không có network evidence; không contrast lưới nào được tính.

## Assumptions still open

- G1–G5 của ánh xạ EVPPI/VSS chỉ đúng trong plant lý tưởng với posterior/law đúng (T03).
- D13 tính endpoint occupancy nhưng không phạt backlog sau h (T-H1).
- D21 chỉ đổi biểu diễn tính ngẫu nhiên với θ đúng, không gồm sai tham số/cấu trúc (P11 không phải prior trực tiếp của D21).
- Plant lý tưởng AS1–AS9 (nền ngoại sinh, buffer vô hạn, action có hiệu lực ngay).

## Risks still open

| Risk | Lộ ra ở |
|---|---|
| WM26 có nhánh/contrast cùng estimand ở phần chưa đọc (AI đọc lại §4–5/§9/F.1 chưa thấy; 40 trang chưa đọc hết) | L-self WM26 §5/F.1 |
| P02 nay AI-T; MT2/MT6/MT7 và K-M5 có primary AI nhưng chưa L-self | L-self P02 §2.2.4/§3.3 |
| Search thiếu raw ở Part2 và chưa bão hòa; forward P07 chưa chạy được | Audit Phase 6 và Phase 9 |
| Một phần Γ có thể đến từ hình học quyết định (MT5) | Null ở A05 |
| T-H1: cost sau h không được tính | Diễn giải A04; sensitivity Phase 4 nếu cần |
| Luật K5 chưa chọn | L3.3 |
| Nhãn tạm do AI chấm sau khi thấy nhãn mentor: rủi ro "AI soạn, AI duyệt" | Tác giả tự chấm; L8 |

## What I am allowed to claim

Theo [claim boundary — Ranh giới với prior (Phase 2)](../01_claim_boundary_v1_2.md#ranh-giới-với-prior-phase-2--26102026); mỗi dòng là nhãn **tạm**, nguồn quyết định nhãn chỉ AI-T:

| Claim | Nhãn tạm | Nguồn quyết định nhãn · mức |
|---|---|---|
| PC1 | DROP (framing) | SOB14, P11 · AI-T |
| PC2 | NARROW | P11, P02, P04 · AI-T |
| PC3 | KEEP câu chữ, framing NARROW | WM26, R02, R04 · AI-T |
| PC4 | HOLD | A05 (chưa có) |
| PC5 | NARROW | P12, P03, AIS22 · AI-T |
| PC6 | NARROW | S11, P04, P13 · AI-T |
| Main RQ | KEEP | WM26 và các nguồn trên · AI-T |

## What I am NOT allowed to claim

G_{S|M1} ≥ 0 hay EVPPI/VSS là phát hiện; "fidelity khác quyết định" là mới; "state cũ làm routing kém" là mới; "thông tin có thể làm hại" là mới; "bảng 2×2 repair" là mới; giá trị bất kỳ của G_S, G_M, Γ (chưa tính); "chưa ai làm", "novel"; "Phase 2 đã đóng"; "tác giả đã kiểm mọi nguồn" (0/19 record).

## Gate decision

| Điều kiện (§15) | Trạng thái |
|---|---|
| L1 nhãn đủ cột | ⚠️ Có nhãn tạm do AI chấm theo ủy quyền; tác giả chưa tự chấm |
| L2 L-self nguồn quyết định nhãn | ❌ 0/19 |
| L3 phép dẫn hai identity | ⚠️ Code + mutant PASS; phép dẫn T03 do AI viết |
| L4 OεRE trong terms.md | ✅ (draft) |
| L5 bốn phiên audit có log, Tier1 đọc T | ⚠️ Deviation: Part2 không lưu log từng rank; follow-up có raw; luật dừng chưa đạt |
| L6 Main RQ có nhãn trong DL | ✅ DL-042 |
| L7 claim boundary, inventory, exposure | ✅ cập nhật 26/10 |
| L8 người thật đọc | ❌ ([gói cho người đọc](../meetings/phase2_reader_packet.md), chưa có ai đọc) |

**Quyết định (AI theo ủy quyền tác giả, 26/10/2026): HOLD.** Không phải lựa chọn mà là hệ quả của PHASE_2 §17: còn thiếu điều kiện validity (L2, L3; L8 khuyến nghị). Điều kiện để đổi: tác giả tự chấm hoặc xác nhận nhãn; L-self bộ tối thiểu (WM26 trước); tự dẫn T03; một người đọc thật (để lên GO có điều kiện). Không gắn tag.

## Next phase

Prior boundary đi vào L3.3 (prediction card chỉ chứa phần claim còn đứng, **commit sau** khi có nhãn do tác giả xác nhận và L-self WM26) và A05 (cần OεRE, danh sách "đã biết", nhãn PC4/PC5 chính thức). Được học Phase 3 ngay. Literature tiếp tục ở audit targeted (khi có mechanism mới ở Phase 3/6), pre-claim (sau Phase 5–6) và final novelty audit (Phase 9). HOLD Phase 4 (P0-V10) và G1 giữ nguyên.
