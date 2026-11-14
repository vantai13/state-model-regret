# Ghi chú cơ chế: vì sao telemetry tươi hại twin fluid ở horizon dài (ctmc-v1), 14/11/2026

Doan Van Tai — **AI (Claude) soạn theo ủy quyền** ("oke bạn làm cho tôi đi", 14/11/2026). Ghi chú tổng hợp
exploration, **không phải** câu cơ chế do tác giả viết.
- Các thẻ đều do AI soạn và tự chấm, không có mentor review. Thẻ CE dùng ngưỡng AI được tác giả chấp nhận nguyên ("chấp nhận, chạy đi").
- Không đổi MainRQ/contract/PC/Gate. G1. Understanding, L8 và author-self vẫn OPEN.

## 1. Câu hỏi

Phase 7 (C3) thấy rằng ở h dài, thay state cũ bằng state tươi làm twin fluid M0 tệ hơn (G_S < 0) ở đa số regime của
thiết kế. Có hai giải thích cạnh tranh, và C5 vẫn ghi "chưa đứng":
- **(a) Gộp quyết định cộng bias.** M0 lệch gần như một hằng số. Twin cũ lấy trung bình gap qua posterior, nên quyết định bị gộp về action dài hạn. Twin tươi phản ứng theo từng state, và các gap riêng lẻ vượt qua ngưỡng đã bị bias dời đi.
- **(b) Hiệu chỉnh ngẫu nhiên ngầm** (đề xuất review ngoài, 14/11). Trung bình chi phí fluid qua posterior cộng thêm khoản Jensen Var/(2r), khoản này bắt chước chi phí dài hạn mà fluid bỏ sót. State tươi xóa khoản đó.

## 2. Bằng chứng (bốn lượt, đều trên plant mô phỏng)

| Lượt | Thiết kế | Kết quả chính | File |
|---|---|---|---|
| I_Δ vòng 1 | 9 regime L7.5, thiết kế viết trước | I_Δ = −e(x) + E[e\|y] (trung bình 0). Sai số M0 e = ΔC0 − μΔI0 + ΔBN là phần dư Jensen ở biên rỗng (identity 3,4e−12). Fluid: e = 0 chính xác khi q ≥ hD | [RESULTS_IDELTA.md](../../results/explore_ctmc/idelta/RESULTS_IDELTA.md) |
| I_Δ vòng 2 | 45 regime mới, thẻ khóa | Ngoài band: tỷ lệ Γ tái tạo bằng model chỉ lệch hằng, ρ = Γ_add/Γ, có trung vị **0,11 ở h ≈ T_int, 1,13 ở 7 T_int** (H1 PASS) | [RESULTS_IDELTA2.md](../../results/explore_ctmc/idelta/RESULTS_IDELTA2.md) |
| I_Δ vòng 3 | 40 regime mới, thẻ khóa | Lặp lại ngoài band: **ρ 0,011 → 1,145** (B4). Phía harm ở 7 T_int: 80% dòng có ρ ≥ 0,75. Ngoại lệ help band lặp lại (B1/B3). Câu "help cần sai số phụ thuộc state" trượt sát nút (B2 7/11) | [RESULTS_IDELTA3.md](../../results/explore_ctmc/idelta/RESULTS_IDELTA3.md) |
| Knockout CE (sửa) | 40 regime mới, thẻ khóa; nhánh **NK** bỏ đúng phần "hiệu chỉnh ngầm" K | **NK giữ 1,00 harm, 26/26 dòng** ở 7 T_int (N1 PASS). K ≈ 4% Jensen (N3). Ở T_int, K ≈ 78% nhưng chỉ mang ~11% harm (N2 PASS). Twin CE: PB 26/26 vẫn harm, QM 23/26 (P1 FAIL) | [RESULTS_CE.md](../../results/explore_ctmc/ce_knockout/RESULTS_CE.md) |

**Mấu chốt đại số** (AI dẫn, xem [DESIGN_CE.md](../../results/explore_ctmc/ce_knockout/DESIGN_CE.md) §0):
- Gap của twin cũ là E[Δ̂|y], tức trung bình các gap twin tươi. Khoản Jensen có mặt ở cả truth cũ lẫn twin cũ.
- Sai số của twin cũ là E[e|y] = e_PB(y) + K(y), với K là Jensen của chính sai số.
- Do đó (b) chỉ có thể đi qua K.

## 3. Phát biểu (mức exploration, ctmc-v1: a = 6, τ = 1, c_sw = 0)

| # | Phát biểu | Mức |
|---|---|---|
| M1 | Interaction tầng prediction (I_Δ) là phần phụ thuộc state của sai số M0, sinh ở biên rỗng | identity / gần định lý trong plant |
| M2 | Ngoài help band, ở h ≈ T_int, Γ cần sai số phụ thuộc state. Ở h ≈ 7 T_int, Γ và phía harm tái tạo được bằng một bias hằng cộng ngưỡng | khai trước, lặp lại trên 2 panel mới |
| M3 | Ở h dài, harm **không** cần "hiệu chỉnh ngầm" (K). Đề xuất (b) bị bác trong plant này | khai trước, 1 panel mới (N1/N3) |
| M4 | Do đó cơ chế ứng viên của harm ở h dài là (a): gộp quyết định cộng bias gần hằng | suy ra từ M2 + M3; chưa có phép thử loại trừ mọi đối thủ |
| M5 | Harm còn với twin cắm backlog trung bình (26/26), nhưng yếu và đổi dấu ở 3/26 khi cắm cả mode. Claim C3 nên nói rõ: twin gộp Bayes; với twin plug-in thì phụ thuộc cách cắm | P1 FAIL theo luật đã khai; phần PB đạt ngưỡng của nó |
| M6 | Cơ chế của help band (0 < x < 0,35) | **chưa có**: ba ứng viên đã trượt |
| M7 | Hướng theo h chuyển sang plant fluid ở mức median (ρ 0,10 → 0,86) | khai trước; chưa kiểm thang T_int |

## 4. Hệ quả cho đề tài (đề xuất, tác giả quyết)

- **Đề xuất review ngoài.** Đọc Γ = VSS_tươi − VSS_cũ là đúng về đại số và giúp diễn đạt, nhưng không phải novelty. Kênh phương sai bị bác ở ctmc-v1 khi h dài. Theo luật của chính đề xuất, đi hướng dự phòng: luật horizon cộng gộp quyết định (C5, T11).
- **C5 ("planner dừng ngầm")** nay có thêm phép thử khai trước ủng hộ: N1, cộng vòng 3 B4 và phía harm của B2. Nhãn "chưa đứng" trong [CLAIMS_EVIDENCE.md](CLAIMS_EVIDENCE.md) **chưa đổi**, chờ tác giả.
- **THREATS K7** đọc F-R2 thành "harm biến mất khi c_sw > 0". Thực tế Stage F dùng base trong dải giúp, nên chưa ai kiểm harm ở vùng harm khi c_sw > 0. Đề xuất sửa câu chữ; **chưa sửa**.

## 5. Giới hạn

- Chỉ plant mô phỏng (ctmc-v1; fluid toy contract v1.2 cho M7). Không có mạng hay trace thật.
- Mọi ngưỡng do AI chọn trên dữ liệu đã lộ. Mỗi thẻ chạy một lần, AI tự chấm.
- "Dòng harm" chọn theo outcome của ô L00. Bias này làm harm dễ co, nên M3 là bảo thủ.
- K đo bằng plug-in backlog với nội suy tuyến tính. Γ_add là một counterfactual (b = trung bình).
- Không novelty: CE dưới thông tin cũ có prior (R34, CEH23); re-solving hại planner tất định có prior (R01/R02/R04).

## 6. Việc mở, theo thứ tự đề xuất

1. Tác giả tự viết câu cơ chế M4 bằng lời mình (L-self) và quyết nhãn C5.
2. Kiểm M3/M4 trên plant fluid: nhánh NK ở contract v1.2, nơi T08 cho e = 0 khi q ≥ hD.
3. c_sw > 0 ở vùng harm (lấp chỗ trống của K7).
4. Help band: xem từng state ở vài regime, nơi M0 và model chỉ lệch hằng quyết định khác nhau, trước khi đặt giả thuyết mới.
