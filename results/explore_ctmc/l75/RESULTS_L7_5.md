# L7.5 — kết quả held-out tuổi telemetry τ (ctmc-v1, a = 6)

Doan Van Tai — **test theo thẻ do AI soạn theo ủy quyền, có mentor review trước khi khóa.** [CARD_L7_5.md](CARD_L7_5.md)
đã được mentor review; tác giả ủy quyền khóa và chạy ("bạn không chờ tôi nói khóa… tự chạy luôn đi"). Khóa ở commit
`8649c43b` ([locks_l75.json](../locks_l75.json)), trước mọi truth ở τ ≠ 1 ngoài hai regime control. G-level G1.

## 1. Lượt chạy

- **Đúng một lượt truth chính**, 04/11/2026, trên GCP `dt4n-research-01` (quy tắc một máy). Ba stage sobol, old, xs:
  **1.625/1.625 unit COMPLETED**, 0 UNRESOLVED, 0 ERROR, 0 dòng bị cờ (S, M, G_M âm).
- 10,5 CPU-h (sobol 5,1; old 0,7; xs 4,7), trong mức dự trù 5–15. Unit nặng nhất 725 CPU-s, dưới trần 900.
- Hash mọi file khóa vẫn khớp sau lượt chạy. Truth thô commit ở `f63047e8` trước file điểm chính thức.
- **File điểm:** [score_l75.json](../score_l75.json), tạo trên GCP bằng `score_l75_post.py` vì `main()` đã khóa lỗi ở phần
  D22 chỉ báo (§5). Verdict dùng nguyên `load()`/`score()` đã khóa.
- Stage D22 (chỉ báo) chạy sau, riêng thư mục: §5.

## 2. Verdict

| ID | Claim | Loại | Giá trị | Ngưỡng | n | Verdict |
|---|---|---|---|---|---|---|
| L75-1a | C-τ1, prior đúng | onset | 171/174 = 0,983 | ≥ 0,90 | 174 chuỗi, 58 regime | PASS |
| L75-1b | C-τ1, prior sai | onset | 98/98 = 1,000 | ≥ 0,90 | 98 dòng, 33 regime | PASS |
| L75-2 | C-τ2 | onset | 1,000 ở cả 9 phần | 0,90 / 0,95 / 0,95 | 273 / 182 / 273 dòng mỗi phần | **PASS** |
| L75-3 | C-τ3 | rủi ro | 328/328 = 1,000 | ≥ 0,90 | 328 chuỗi có thông tin, 88 regime; 218 đạt hiển nhiên | **PASS** |
| L75-4 | C-τ4 | rủi ro | 8/8 | 8/8, n_min 6 | 8 series | **PASS** |

L75-1 = PASS (cả 1a, 1b). Tổng: **4 PASS, 0 FAIL, 0 INCONCLUSIVE.**

## 3. Chi tiết

**L75-1a.**
- 3 chuỗi trượt dung sai 0,05 pp là đúng ba chuỗi zero-fit đã báo không đơn điệu:

  | Chuỗi | x | Bước tăng truth | Bước tăng zero-fit |
  |---|---:|---:|---:|
  | TN0024, h = 74,1 | −0,14 | 0,075 | 0,077 |
  | TP0028, h = 158 | 0,53 | 0,059 | 0,062 |
  | TP0067, h = 40,4 | 0,55 | 0,084 | 0,086 |

- Cả ba có G_S rất nhỏ (|G_S| < 0,22 pp), gần ranh giới harm/help.

**L75-1b.** Mọi dòng prior sai ở τ = 10·T_int có G_S > 0. Thấp nhất +0,10 pp; trung vị +3,8 pp (99 dòng, trong đó 98 dòng
chấm).

**L75-2.** |G_S − z_pred1| lớn nhất: 0,025 pp (h = 7·T_int), 0,006 (15·T_int), 0,0015 (30·T_int). Trên các dòng
|z_pred1| ≥ 0,5 cũng đạt 1,000 ở cả 9 phần.

**L75-3.**
- Theo h, số chuỗi có thông tin / đạt hiển nhiên: 0,3·T_int 88 / 3; T_int 81 / 10; 3·T_int 69 / 22; 7·T_int 48 / 43;
  15·T_int 30 / 61; 30·T_int 12 / 79.
- Không chuỗi nào có S giảm quá 0,01 pp; không vi phạm nào > 0,1 pp.

**L75-4.** Lệch biên truth so với zero-fit trên 8 series: tối đa 1,8e−5 (họ u = 1/2, κ = 1 ở τ = T_int). Dung sai là 0,01.

## 4. Chỉ báo và khám phá sau khi mở (không đổi verdict)

- **Quy tắc cũ của L75-1** (z_pred1 < −0,5 ở cả 8 τ): 87/87.
- **R-a, tầng band:** 143/162 chuỗi (0,883) có G_S không giảm theo τ.
- **L75-2 ở h = 3·T_int:** 0,744 (τ ≤ 0,03·T_int), 0,335 (0,1–0,3·T_int), 0,092 (≥ T_int). Onset ở 3·T_int kém dần khi
  telemetry cũ đi. Đây là mô tả sau khi mở.
- **10 series L75-4 bị loại vì thiếu phân giải:** biên truth vẫn khớp biên zero-fit tới ≤ 1,5e−4, kể cả ở τ = 0,01·T_int.
  Không chấm; điều kiện loại đặt trước khóa vì 0,1 pp ứng với 0,04–0,59 đơn vị x ở các series này. Kết quả này cho thấy
  sai số z_pred1 thật ở lát x nhỏ hơn nhiều so với giới hạn đã kiểm (0,1 pp). Không dùng nó để nới dung sai về sau.
- **F8** ([h = 7·T_int](F8_truth_GS_S.png), regime chọn trước khóa):
  - TN0003 (prior đúng): G_S từ −0,69 xuống −3,71, bão hòa từ τ ≈ T_int.
  - TB0007 (prior sai): G_S từ −1,84 (τ nhỏ) lên +25,55.
  - TP0079: từ −0,21 xuống −5,90.
  - S ≤ 0,003 pp, vì ở 7·T_int truth đã chọn action dài hạn.
- **F8 ở h = T_int** ([sau mở, mô tả](F8_truth_GS_S_h1T.png)): S tăng theo τ ở cả ba regime (0,04 → 0,42; 0,05 → 1,50;
  0,01 → 0,86). z_pred1 ở h = T_int sai xa, đúng như đã biết là trước onset.

## 5. D22 (stage chỉ báo)

- **Lượt chạy:** stage riêng `--mode l75d22`, sau truth chính, cùng máy. **741/741 unit COMPLETED** (sobol 658,
  old 83), 0 UNRESOLVED, 0 dòng bị cờ. 7,87 CPU-h, so với dự trù 5,1 (khoảng 1,5 lần).
  - Ba unit nặng nhất chạy đầu tiên: 239, 266, 272 CPU-s, hơi rẻ hơn bản zero-fit của chúng (275, 282, 301 CPU-s).
  - Phần vượt dự trù đến từ V và posterior, không từ J.
- **Phần harm do backlog** (D22 truth, dòng harm G_S < −0,5%, SO ∪ OLD, mọi h):

  | τ/T_int | 0,003 | 0,01 | 0,03 | 0,1 | 0,3 | 1 | 3 | 10 |
  |---|---:|---:|---:|---:|---:|---:|---:|---:|
  | n dòng harm | 152 | 177 | 194 | 200 | 198 | 184 | 145 | 94 |
  | trung vị F / G_S | 0,66 | 0,81 | 0,86 | 0,90 | 0,92 | 0,90 | 0,88 | 0,84 |
  | tỷ lệ F < 0 | 0,97 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 |

- **Đọc (chỉ báo):**
  - Harm khi state tươi chỉ có backlog xuất hiện ở mọi tuổi (F < 0 ở 97–100% dòng harm).
  - Phần backlog tăng theo τ từ 0,66 lên khoảng 0,9 rồi giảm nhẹ, cùng chiều zero-fit (0,65 → 0,89–0,91, h = ∞).
  - Câu "harm chỉ vì S1 biết mode" vẫn không đứng ở τ ≠ 1.
- **Lỗi checker (sau khi mở):** `check_l75.main()` đã khóa dừng ở phần D22 chỉ báo, trước khi ghi file điểm.
  - Nguyên nhân: `done.flags` trả về thuộc tính `DataFrame.flags` của pandas, không phải cột `flags`.
  - **File khóa không bị sửa.** `score_l75_post.py` gọi đúng `load()` và `score()` đã khóa (kiểm sha256 trước), ghi
    `score_l75.json` cùng cấu trúc `counts` như `main()`. Phần D22 tính bằng bản sao đã sửa một chỗ (`done['flags']`).
  - Verdict không phụ thuộc phần D22. File điểm tạo trên GCP trùng phần verdict với lần chấm lại ở local.

## 6. Ý nghĩa theo thẻ (§7) và giới hạn

**Câu tiêu đề được phép viết (trong model, đúng điều kiện):**
> Với twin mean-value mù horizon ra một quyết định giữ suốt h, ở h ≥ 7·T_int, chiều của giá trị refresh telemetry theo
> tuổi của telemetry bị thay do một bit quyết định: quyết định mù thông tin của twin có trùng action tốt hơn dài hạn không.
> Prior đúng thì refresh càng hại khi telemetry bị thay càng cũ, bão hòa từ khoảng τ ≈ T_int; prior sai thì refresh có ích.
> Độ lớn theo luật zero-fit z_pred1(τ, h) tới 0,1 pp ở mọi tuổi đã thử.

**Giới hạn phải đi kèm:**
1. **L75-1 và L75-2 là onset**, tức zero-fit đã báo trước. Chúng xác nhận luật bậc một ở τ ≠ 1, không phải bằng chứng
   độc lập cho cơ chế. Bit prior đúng ở h = ∞ là một đẳng thức (91/91).
2. **L75-3 đạt** trên 328 chuỗi có thông tin: với model đúng, state tươi có giá trị hơn khi state cũ cũ hơn, dù Y chỉ có
   backlog. Đặt trong khung SS22 thì ở đây chuỗi "đủ gần Markov" theo nghĩa thực nghiệm. Ánh xạ điều kiện của SS22 Thm 3.4
   **chưa kiểm**, nên không viết rằng SS22 dự đoán kết quả này.
3. **L75-4** chỉ chấm 8 series đủ phân giải, đều ở τ ≥ 0,1·T_int.
4. **Bit cần biết s**, tức action tốt hơn dài hạn. Ngoài thực tế s phải ước lượng.
5. **Phạm vi:** ctmc-v1 a = 6, hai mode đối xứng, một quyết định, P1. Chưa có vòng kín (K4), nhiều path, burst bất đối
   xứng, ctmc-v2.
6. **Thẻ do AI soạn** theo ủy quyền, có mentor review trước khóa; tác giả chưa tự viết lại claim. G1.

## 7. Câu hỏi cơ chế của mentor (vì sao M0 mù chọn Switch ở 0 < x ≲ 0,47)

**Số liệu** (zero-fit, [M0_GAP_PARTS.json](M0_GAP_PARTS.json)): gap M0 ở h = ∞, lấy trung bình theo phân phối dừng của
Stay; âm thì nghiêng về Switch.

| Regime | x | Backlog TB dưới Stay (A / B) | gap A | gap B | tổng | s |
|---|---:|---|---:|---:|---:|---:|
| TN0003 | −0,54 | 18,0 / 7,1 | −106,9 | +13,6 | −93,3 | −3,43 |
| TB0007 | 0,28 | 19,5 / 6,7 | −199,1 | +78,9 | −120,2 | +18,88 |
| TP0079 | 0,81 | 3,4 / 3,0 | −1,53 | +2,47 | +0,94 | +1,16 |

**Bản nháp của AI, để tác giả viết lại bằng lời mình:**
- Ở h = ∞, M0 chỉ so chi phí **xả lượng backlog đang có** dưới hai bộ tải. Nó không thấy h·s, phần chênh tốc độ chi phí ở
  trạng thái dừng.
- Dưới Stay, path A mang λA + u. Khi 0 < x < 1, tải này lớn hơn λB, nên A giữ nhiều backlog hơn (TB0007: 19,5 so với 6,7).
- Switch bớt u khỏi A, làm A xả nhanh hơn đúng đống backlog lớn; lợi gần tỷ lệ với bình phương backlog của A. Switch thêm u
  vào B, làm B xả chậm hơn đống backlog nhỏ, nên thiệt ít hơn. Vì vậy M0 mù chọn Switch.
- Nhưng về dài hạn, Switch đặt tải λB + u > λA + u lên B. Chi phí dừng lồi theo tải, nên s > 0: Stay tốt hơn.
- Khi x lớn hơn, λB + u tiến gần μ, chi phí xả của B tăng mạnh (TP0079: gap B > |gap A|), và M0 mù quay về Stay. Ranh giới
  của chuyển đổi đó là đầu trên của dải giúp ở τ lớn (x ≈ 0,42–0,5).
