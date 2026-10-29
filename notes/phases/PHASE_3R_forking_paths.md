# Phase 3R — Nhật ký forking paths L3R.6

Người phụ trách: **Doan Van Tai**. Bản đọc được sinh từ
[forking_paths.jsonl](../../results/lessons/l3r_6/forking_paths.jsonl) bằng `experiments/R3R_06_cards/render_log.py`;
JSONL là nguồn. Mọi số là DISCOVERY trên pilot đã lộ, không phải evidence. Cột “Ai” = AI
nghĩa là phiên triển khai chạy tóm tắt; lựa chọn giữ/bỏ là của tác giả (DL-073).

| # | UTC | Ai | Luật / bảng | Đã xem | Giữ/Bỏ | Mục đích / lý do |
|---|---|---|---|---|---|---|
| 0 | 2026-10-29T02:49:48 | AI (lesson author, Part 2) + phiên triển khai | — (không phải luật) | Lesson Part 2 bốn bảng: phủ (lambdaB,kappa,h) kèm số MV/SH; danh sách lambdaB=8,kappa<=.3,h>=8; MV theo lambdaA ở lambdaB=8; góc lambdaA=8; Lesson Part 2 số trích: rhoA=.9 cặp (8,1)->G_M 0.00 và (7.5,1.5)->5.85..13.41; G_S -8.47..-21.57 ở lambdaB=8,lambdaA=7; G_M 1.33..2.56 ở kappa=.3; SH 36/36,21/36,0/40,0/20; Lesson Part 1 §8: S1..S10 từ discovery record §5 và DL-063; Discovery record §2-§6, L3R.4 overlay MV20/SH80/giao14, contract/T07 đã đọc trước phiên | — | Mục 0: những gì đã xem trước khi viết luật vùng |
| 1 | 2026-10-29T02:50:06 | AI | table: Part2 §5.1 coverage reproduction | 48 ô | — | tái lập bảng lesson |
| 2 | 2026-10-29T02:50:06 | AI | table: Part2 table 3: MV by lambdaA at lambdaB=8, kappa<=.3, h>=12 | 5 ô | — | tái lập bảng lesson |
| 3 | 2026-10-29T02:50:06 | AI | listing: Part2 §6 rhoA=.9 pair | 6 cấu hình | — | tái lập bảng lesson |
| 4 | 2026-10-29T02:50:06 | AI | listing: Part2 table 2 reproduction | 40 cấu hình | — | tái lập bảng lesson |
| 5 | 2026-10-29T02:50:06 | AI | table: Part2 table 4: corner lambdaA=8 | 3 ô | — | tái lập bảng lesson |
| 6 | 2026-10-29T02:50:06 | AI | table: Part2 §8.3 SH counts reproduction | 4 ô | — | tái lập bảng lesson |
| 7 | 2026-10-29T02:50:19 | AI | MV+A: lambdaB=8, lambdaA∈[7;15/2], kappa∈[1/10;3/10], h∈[12;16], u∈[1;3/2], c_sw=0 | n=16 · MV=16, SH=11 |  | candidate MV_plus |
| 8 | 2026-10-29T02:50:19 | AI | MV+B: lambdaB=8, lambdaA∈[7;15/2], kappa∈[1/10;3/10], h∈[8;16], u∈[1;3/2], c_sw=0 | n=24 · MV=20, SH=16 |  | candidate MV_plus |
| 9 | 2026-10-29T02:50:19 | AI | MV-ii: lambdaB=8, lambdaA∈[7;15/2], kappa∈[1;3], h∈[12;16], u∈[1;3/2], c_sw=0 | n=0 · MV=0, SH=0 |  | candidate MV_minus |
| 10 | 2026-10-29T02:50:19 | AI | MV-i: lambdaB∈[6;7], lambdaA∈[7;15/2], kappa∈[1/10;3/10], h∈[12;16], u∈[1;3/2], c_sw=0 | n=32 · MV=0, SH=24 |  | candidate MV_minus |
| 11 | 2026-10-29T02:50:19 | AI | MV-BND: lambdaB=8, lambdaA∈[7;15/2], kappa∈[3/10;1], h∈[12;16], u∈[1;3/2], c_sw=0 | n=8 · MV=8, SH=4 |  | candidate MV_bnd |
| 12 | 2026-10-29T02:50:19 | AI | SH+A: lambdaB∈[6;7], lambdaA∈[7;8], kappa∈[1/10;3/10], h∈[8;16], u∈[1;3/2], c_sw=0 | n=72 · MV=0, SH=57, SH_and_GSM_lt_epsE=57 |  | candidate SH_plus |
| 13 | 2026-10-29T02:50:19 | AI | SH+B: lambdaB∈[6;8], lambdaA∈[7;8], kappa∈[1/10;3/10], h∈[8;16], u∈[1;3/2], c_sw=0 | n=108 · MV=20, SH=73, SH_and_GSM_lt_epsE=57 |  | candidate SH_plus |
| 14 | 2026-10-29T02:50:20 | AI | SH-ii: lambdaB∈[6;7], lambdaA∈[7;8], kappa∈[1;3], h∈[8;16], u∈[1;3/2], c_sw=0 | n=0 · MV=0, SH=0, SH_and_GSM_lt_epsE=0 |  | candidate SH_minus |
| 15 | 2026-10-29T02:50:20 | AI | SH-i: lambdaB=8, lambdaA∈[7;8], kappa∈[1/10;3/10], h∈[8;16], u∈[1;3/2], c_sw=0 | n=36 · MV=20, SH=16, SH_and_GSM_lt_epsE=0 |  | candidate SH_minus |
| 16 | 2026-10-29T02:50:20 | AI | G-A: lambdaB=8, lambdaA∈[7;15/2], kappa∈[1/10;3/10], h∈[12;16], u∈[1;3/2], c_sw=0 | n=16 · GS_nonneg=3, Gamma_fails=0, Gamma_meets=16, Gamma_negative=0, MV=16, SH=11, informative_min_gt_epsE=1 |  | candidate Gamma |
| 17 | 2026-10-29T02:50:20 | AI | G-B: lambdaB=8, lambdaA=15/2, kappa∈[1/10;3/10], h∈[12;16], u∈[1;3/2], c_sw=0 | n=8 · GS_nonneg=3, Gamma_fails=0, Gamma_meets=8, Gamma_negative=0, MV=8, SH=3, informative_min_gt_epsE=1 |  | candidate Gamma |
| 18 | 2026-10-29T02:50:20 | AI | G-C: lambdaB=8, lambdaA∈[7;8], kappa∈[1/10;3/10], h∈[8;16], u∈[1;3/2], c_sw=0 | n=36 · GS_nonneg=18, Gamma_fails=0, Gamma_meets=36, Gamma_negative=9, MV=20, SH=16, informative_min_gt_epsE=3 |  | candidate Gamma |
| 19 | 2026-10-29T02:50:20 | AI | ALL c_sw=0: c_sw=0 | n=162 · GS_nonneg=73, Gamma_fails=0, Gamma_meets=162, Gamma_negative=9, informative_min_gt_epsE=3 |  | Gamma clamp diagnostic over all |
| 20 | 2026-10-29T03:10:34 | Tác giả chọn, AI ghi | — | rules_tried=13 | Giữ: MV+A: Ω_MV⁺ (tác giả chọn); MV-BND: Ω_MV_BND chỉ mô tả; MV-ii: Ω_MV⁻ lật κ, ngoại suy (tác giả chọn); SH+A: Ω_SH⁺ (tác giả chọn); SH-ii: Ω_SH⁻ lật κ, ngoại suy (tác giả chọn) · Bỏ: G-A: không cấp suất Γ; G-B: không cấp suất Γ; G-C: không cấp suất Γ; MV+B: không chọn; rộng hơn nhưng gồm κ.3/h8 có MV0; MV-i: đối chứng lật headroom gần như chắc đạt, ít thông tin; SH+B: chồng vùng MV và trộn λB8; SH-i: λB8 16/36 không phải đối chứng sạch | Γ diagnostic: 3/162 cấu hình min(ḠS,ḠM)>.5%; 70/73 cấu hình ḠS≥0 tự đạt do identity |
| 21 | 2026-10-29T03:14:02 | AI | SH-BND: lambdaB∈[6;7], lambdaA∈[7;8], kappa∈[3/10;1], h∈[8;16], u∈[1;3/2], c_sw=0 | không nhìn dữ liệu | Giữ (mô tả) | Ω_SH_BND mô tả, đối xứng Ω_MV_BND; không chấm |

Tổng 22 dòng; 13 luật được tóm tắt trên discovery, 1 luật khai không nhìn dữ liệu.
