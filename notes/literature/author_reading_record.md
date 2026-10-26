# Record tự đọc (L-self) của tác giả — mẫu, chưa điền

Người phụ trách: **Doan Van Tai** · tạo 26/10/2026 cho L2.9 (Gate L, điều kiện L2).
Khung do AI dựng; **AI không điền** cột nào của tác giả. Cơ chế giống
[DL-032](../02_decision_log.md#dl-032--phần-a-author-attestation-và-budget-trước-screen-2026-10-23):
tác giả xác nhận trực tiếp → repo ghi **author-attested**, không phải independently verified.

## Cách ghi (một trong hai)

1. Tác giả tự điền một dòng ở bảng dưới và commit; hoặc
2. Tác giả nói trong chat theo mẫu *"Tôi đã tự đọc ⟨ID⟩ ⟨§/trang⟩ bản ⟨version⟩ ngày
   ⟨dd/mm⟩; tóm tắt: …"* → AI chép **nguyên văn** câu đó vào cột "Xác nhận", ghi giờ,
   rồi cập nhật Excel và evidence inventory. Không suy ra mức đọc từ "Duyệt",
   từ việc tải PDF hay từ note AI.

Sau đó: cột **"Mức tôi đã đọc"** trong `papers/paper_comparison.xlsx` (Danh_sach)
do tác giả chọn trong danh sách thả; `build_notes.py` giữ nguyên giá trị đó khi dựng
lại. Thêm một dòng author-attested vào `notes/00_evidence_inventory.md`.

## Bộ tối thiểu theo lesson L2.9 Part 1 (thứ tự theo khả năng đổi nhãn)

Vị trí cần đọc lấy từ lesson; bản đọc/hash ở `results/lessons/*/source_access.json`.

| # | ID | Phần nên đọc | Claim | Bản có sẵn (local) | Ngày | § thực đọc | 2–3 câu tác giả tự viết | Khác note AI ở đâu | Xác nhận (author-attested) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | WM26 | §4.1, §5; F.1 Eq10, Table10 (PDF4–5, 22–23); §8 PDF9 | PC3, PC2 | `PDF_local/WM26.pdf` (arXiv v1) | 26/10/2026 | §4.1, §5, F.1 (tr4–5, 22) | Ở vở của tác giả, chưa chép vào repo | — | **author-attested** 26/10 ([xác nhận](../../results/lessons/l2_9/gate_l/author_attestation.json)) |
| 2 | R02 | §5 Example1; đối chiếu `results/lessons/l2_8/part2/cooper_example1.csv` | PC3 | `PDF_local/R02_Cooper2002.pdf` | 26/10/2026 | §5 Example 1 | Ở vở của tác giả, chưa chép vào repo | — | **author-attested** 26/10 ([xác nhận](../../results/lessons/l2_9/gate_l/author_attestation.json)) |
| 3 | R04 | §3 Def2–4, Prop1–2, Remark2 | PC4, PC3 | `PDF_local/R04_Secomandi2008.pdf` | 26/10/2026 | §3 Def 2–4, Prop 1–2 | Ở vở của tác giả, chưa chép vào repo | — | **author-attested** 26/10 ([xác nhận](../../results/lessons/l2_9/gate_l/author_attestation.json)) |
| 4 | P11 | §2.4 Eq2.7–2.8 | PC2 (§5.4: PC1, PC2) | archive Part A | 26/10/2026 | §2.4 Eq 2.7–2.8 | Ở vở của tác giả, chưa chép vào repo | — | **author-attested** 26/10 ([xác nhận](../../results/lessons/l2_9/gate_l/author_attestation.json)) |
| 5 | S11 | §III, Eq10 | PC6 | `PDF_local/2504.19507v3.pdf` | 26/10/2026 | §III Eq 10 | Ở vở của tác giả, chưa chép vào repo | — | **author-attested** 26/10 ([xác nhận](../../results/lessons/l2_9/gate_l/author_attestation.json)) |
| 6 | P12 | Def1, §3.1 | PC5 | `PDF_local/P12_Grimm2020_NeurIPS_VE.pdf` | 26/10/2026 | Definition 1, §3.1 | Ở vở của tác giả, chưa chép vào repo | — | **author-attested** 26/10 ([xác nhận](../../results/lessons/l2_9/gate_l/author_attestation.json)) |
| 7 | T03 | Tự dẫn hai identity kín sách (L3, không phải đọc nguồn) | PC1 | `notes/theory/T03_primary_reading_start.md` (chỉ mở sau khi tự dẫn) | 26/10/2026 | Tự dẫn kín sách hai identity (L3) | Ở vở của tác giả, chưa chép vào repo | — | **author-attested** 26/10 ([xác nhận](../../results/lessons/l2_9/gate_l/author_attestation.json)) |

Nguồn quyết định nhãn khác theo PHASE_2 v2.0 §5.4 (giữ AI-T nếu tác giả lập luận
được rằng chúng không đổi nhãn): SOB14 (PC1), P04 (PC2/PC4/PC6), P13 (PC4/PC6),
P03 (PC5), **P02 (PC2, nay có VoR `PDF_local/P02_Poelman2023_TRC_VoR.pdf`)**, R06 (PC3, abstract).

## Record đã có

| Ngày | Nguồn | Tác giả nói (nguyên văn) | Mức ghi nhận | Ghi chú |
|---|---|---|---|---|
| 26/10/2026 | WM26 §4.1, §5, F.1; R02 §5 Ex1; R04 §3; P11 §2.4; P02 §2.2.4/§3.3/Bảng 2; S11 §III Eq10; P12 Def1/§3.1; tự dẫn T03 | "Đọc WM26, Đọc R02, R04, P11, Đọc P02, S11, P12, Tự dẫn T03" (trả lời câu hỏi chọn); "thực ra tôi đã làm phần lớn các yêu cầu của bạn ngoài vở rôi á mà tiện thể chưa ghi vào" | **L-self + L3, author-attested** (DL-032) | Làm ngoài vở; lời giải chưa trong repo, không kiểm độc lập. Nhãn: "Xác nhận nhãn tạm". [Xác nhận](../../results/lessons/l2_9/gate_l/author_attestation.json) |
| 26/10/2026 | WM26 (bản giải thích AI, dựa trên arXiv v1 sha256 `94201c59…`) | "đây là những gì tôi đã đọc và đưa AI thuật lại" | **L-2nd, author-attested**: tác giả đã đọc bản giải thích AI | **Chưa phải L-self primary** (chưa có record tự mở §4.1/§5/F.1 và tự viết). [Bản đã đọc](../../results/lessons/l2_9/wm26_author_reading/explainer_as_read.md) · [AI kiểm bản giải thích](../../results/lessons/l2_9/wm26_author_reading/check.md) |

Để dòng WM26 thành L-self: tác giả tự mở §4.1, §5, F.1 và trả lời không nhìn tài liệu ba
câu do chính bản giải thích gợi ý — (1) center của WM26 khác mean rollout của M0 thế nào;
(2) repair C/S có biết endpoint tương lai thật không; (3) vì sao P/C/S/E không đo cùng Γ —
rồi ghi câu trả lời bằng lời mình vào bảng trên.

`author_approval.json` của L2.8 Part2 ("Duyệt cả 3") là quyết định duyệt đọc, **không** phải L-self.

Gói hướng dẫn tự đọc từng nguồn (trang cần mở + câu tự trả lời): [author_reading_pack](author_reading_pack.md).
Ví dụ tính tay hỗ trợ tự dẫn T03: [T03_worked_example](../theory/T03_worked_example.md).
