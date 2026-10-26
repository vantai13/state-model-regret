# Kiểm nội dung lesson L2.9 Part 1 so với repo — 26/10/2026

Người phụ trách: **Doan Van Tai**. Lesson do mentor (AI) soạn dựa trên repo
`7f59023`; repo hiện tại `86ec878` (thêm L2.8 follow-up). AI kiểm từng khẳng định
về repo bằng file/§ thực; lesson là nguồn L-2nd, không mặc định đúng.

## Trạng thái đã cũ do lesson viết trước `86ec878`

| Lesson nói | Repo hiện tại | Hệ quả |
|---|---|---|
| P02 vẫn BLOCKED, chỉ abstract; K-M5, MT2/6/7 còn phụ thuộc P02 | P02 **AI-T trên VoR** tác giả tải 26/10 ([note](../../../../notes/literature/papers/P02.md)); addendum MT1/2/6/7, K-M4/K-M5 | Phép thử "kịch bản xấu nhất" cho P02 không còn cần; nguồn quyết định nhãn PC2 nay có thể đọc L-self |
| Chi tiết P02 của L2.7 (demand ghi trước, bias từng cái một, khởi tạo lại) "repo chưa xác nhận" | Nay **xác nhận đúng**: §2.2.4 tr10, §3.3.1 tr15, §3.3.2 tr16, §4 tr18. Riêng "−50%…+100%" không đúng cho mọi đại lượng (Bảng 2) | Lesson L2.7 đúng ở 3/4 điểm |
| L5: 169 lượt sàng, không log từng rank | Thêm phiên follow-up 157 record có raw HTTP + sha256; vẫn chưa đạt luật dừng; forward P07 chưa chạy được | L5 vẫn ⚠️, nhưng có phần kiểm lại được theo rank |
| Bộ L-self tối thiểu không gồm P02 | PHASE_2 §5.4 ghi P02 là nguồn quyết định nhãn PC2 | Nên thêm P02 (§2.2.4, §3.3, Bảng 2) nếu PC2 dùng P02 làm căn cứ |

## Khẳng định về repo: khớp

| Khẳng định | Bằng chứng |
|---|---|
| "Duyệt cả 3" không phải L-self | `results/lessons/l2_8/part2/author_approval.json`: `"author_L_self": "Not established by this approval"` |
| Excel 19 nguồn, "Chưa có xác nhận" cả 19 | `papers/data/verification.json` (`author_reading_unconfirmed`: 19) |
| DL-032 author-attested V1/V8/P0-V3/P0-V11 | `notes/02_decision_log.md` DL-032 |
| S11 = IEEE TIT 72(4):2237–2276, DOI 10.1109/TIT.2026.3663678 | `notes/literature/papers/S11.md` dòng 10 |
| P13 terminal-horizon ở journal §6 tr289 | `P13.md`; K-H4 |
| K-S3 (một dispatcher lặp cũng dồn tải), K-S5 (định tính, Fig8a/8b khác metric/pruning), K-S8 không quy về "một người" | `prior_boundary.md` dòng K-S3/K-S5/K-S8 |
| K-RM1…3 thay vì K-S9/K-S10 | `literature_audit_part2.md` §6 |
| R04: SC+Π-accuracy⇒SI⇒không làm tệ đi; Cooper vi phạm SC | `R04.md` (§3, §4.1.6/PDF13) |
| R01: allocation không hại; bid-price có thể hại (§4 Example3) | `R01.md` dòng 18 |
| K-S9…K-S11, K-F1…F3, K-H1…H4, K-M1…M7, H1-Q01…Q03, OεRE draft, DL-041 | `prior_boundary.md`, `h1_candidates.md`, `terms.md`, `02_decision_log.md` |
| WM26 có 2×2 P/C/S/E; NDT26 chọn τ trên all evaluation runs | `WM26.md`; `NDT26.md` dòng 23 |

## Khẳng định cần sửa/thu hẹp

| Lesson nói | Đúng là | Vị trí |
|---|---|---|
| PC6: "H1-Q01 cho thấy F không nhỏ một cách hiển nhiên ở κ=3" | H1-Q01 là phương sai **input không điều kiện**, "không phải Var(q(t0)\|y) và không phải F của D22"; repo không có số F/V | `freshness_decision_value.md` dòng 86–90; `h1_candidates.md` |
| PC1: "cùng estimand dưới G1–G4" | claims.md viết "dưới G1–G5"; claim boundary v1.2 tách: EVPPI dưới G1–G4, VSS dưới G2–G5 | `claims.md`; `01_claim_boundary_v1_2.md` (Bổ sung Part A) |
| PC1: "R01 Prop. 1 (cùng cấu trúc chứng minh)" | Repo không có record so cấu trúc chứng minh; đây là suy luận AI hợp lý (chính sách cũ khả thi + objective đúng) | `R01.md` |
| PC3 framing nhắc "R18" (thông tin làm hại) | R18 nằm trong **archive** (18 bài cất 24/10, không tự đưa lại danh sách bắt buộc); record cũ abstract/kết luận | `papers/archive/data/paper_notes.json` |

## Câu hỏi mentor "kém chắc nhất" (PC3, WM26 F.1): AI đã đọc lại

WM26 F.1 Eq10 PDF22: C và S nhập tương lai thật ("C imports one true pool-mean vector,
whereas S imports the candidate-wise true centered responses"); §9 PDF9: correction
không có oracle là future work; Table11–12 chỉ báo C−P, S−P, C−S. **Không thấy**
nhánh chỉ dùng thông tin hiện tại trong phạm vi đã đọc (AI-T, không toàn 40 trang).
Chi tiết: [WM26 note](../../../../notes/literature/papers/WM26.md). Đây là evidence
cho tác giả chấm, không phải nhãn.
