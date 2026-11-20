# Card X1c (xác nhận cải thiện T3 trên lưới mới): viết trước pilot, predict và truth (Claude, 20/11/2026)

- **Người phụ trách:** Doan Van Tai. Claude viết và duyệt thay tác giả theo ủy quyền; Codex hết quota, nên Claude code.
- **Design:** `letter_smr/briefs/strengthen/DESIGN_X1C.md`.
- **Module:** `experiments/letter/x_ctmc_c.py`, bản sao của `x_ctmc.py` chỉ đổi namespace, seed, bản ghi W2 1000 T_int và pilot song song.
- **Scorer:** `experiments/letter/x_ctmc_card.py`, file đã commit, không sửa, chạy với `--out results/letter/x_ctmc_c`. Tên file thẻ phải là
  `CARD_X_CTMC.md` theo scorer.

## Điều đã thấy (exposure)
- Toàn bộ kết quả X-CTMC trên lưới seed 2611201: verdict, raw, phân tích post-hoc.
- Phân tích post-hoc `results/letter/x_ctmc/posthoc_shat/summary.json`: W2 1000 T_int cho sai số độ dốc 0,117, dấu 0,964 trên lưới **cũ**.
  Đó là lý do có thẻ này.
- Lưới mới (seed 2611301) **chưa có outcome nào**. Chỉ có danh sách tham số, tính từ seed để kiểm module.

## Mục tiêu
Xác nhận trên lưới mới rằng với ŝ từ bản ghi 1000 T_int:
- **T3** đứng (sai số độ dốc trung vị ≤ 0,25);
- **T1** đứng (dấu ≥ 0,90).

Các test khác lặp lại với cùng ngưỡng.

## Đơn vị và quần thể
- **Ô** = (regime, rule, τ, h); h ∈ {30, 100} T_int cho các test dấu và độ dốc.
- Các ô cùng regime **không độc lập**. Báo thêm kết quả theo regime: đa số các ô của regime.
- **Đủ điều kiện (eligible):** regime COMPLETED; |G_S| ≥ 0,25% C_ref; |ΔF̂| ≥ 0,01.
- Phân tầng agree/disagree tính chỉ từ tham số.

## Test (confirmatory)
| ID | Claim | Đạt nếu | NOT_EVALUABLE nếu |
|---|---|---|---|
| T1 | Với rule theo tải đo (TH_θ, MLU), dấu của G_S dự đoán bởi ŝ_hat·ΔF̂ (chỉ dữ liệu nhà mạng) | độ chính xác ≥ 0,90 trên ô eligible | < 20 ô hoặc < 8 regime eligible |
| T2 | Dự đoán có hàng đợi hơn null utilization ở tầng disagree | độ chính xác(law) − độ chính xác(null) ≥ 0,20 trên ô eligible tầng disagree | < 10 ô eligible tầng disagree |
| T3 | Độ dốc ở h = 100 T_int | trung vị \|G_S/h − ŝ_hat·ΔF̂\| / \|G_S/h\| ≤ 0,25 trên ô eligible (TH, MLU) | < 20 ô |
| T4 | Như T1 cho M0 trên lưới dị biệt | độ chính xác ≥ 0,90 | < 20 ô |
| T5 | Hybrid_hat both-side regret ≤ 0,5% C_ref ở h ∈ {30, 100} T_int | ≥ 90% ô (regime, τ, h) có dấu(ŝ_hat) = dấu(s) | < 20 ô |
| T6 | C5: dấu G_S của M0 theo c5_sign (harm ⇔ action gộp = action dài hạn đúng) | độ chính xác ≥ 0,85 trên ô M0 eligible | < 20 ô |
| T6b | C5: rule stale tập trung hơn fresh, \|p_old − ½\| ≥ \|p_new − ½\| | ≥ 80% ô M0 eligible | < 20 ô |

**Mô tả (không phải test):**
- D1: share regime có harm (G_S < −0,5% C_ref ở 30 T_int, τ = T_int) theo từng rule.
- D2: tie share theo rule.
- D3: ô có dấu(ŝ_hat) ≠ dấu(s), cùng regret tương ứng.
- D4: chênh lệch Hybrid − Stationary ở 1–10 T_int, cả hai chiều.


## Dự báo của Claude (để có thể sai)
| F | Dự báo |
|---|---|
| F1 | T3 đứng, sai số khoảng 0,10–0,20 |
| F2 | T1 đứng, khoảng 0,93–0,97 |
| F3 | T2, T4, T5, T6, T6b đứng |
| F4 | Estimator invalid ở khoảng 10–20/63 regime |

## Luật đưa vào paper (cố định trước, mọi kết cục)
- **T1 và T2 đứng:**
  - Sec. V-A thêm 2–3 câu: rule theo tải đo cũng bị hại; dấu dự đoán được từ dữ liệu nhà mạng; null không có hàng đợi kém ở tầng disagree.
  - Intro: nâng câu phân biệt của issue 1 thành "the characterization also predicts…".
  - Contribution 1 nhắc điều này.
- **T1 đứng, T2 không:** báo độ chính xác và ghi rõ null utilization ngang bằng. Claim yếu hơn: dấu dự đoán được, nhưng không cần mô hình hàng đợi.
- **T1 không đứng:** một câu giới hạn ở Sec. V với số ô đúng/tổng.
- **T3:** con số đi kèm đoạn T1 trong mọi kết cục.
- **T4 và T5 đứng:** một câu Sec. V-A ("on a heterogeneous grid with path-specific μ, α, κ…"). Không đứng: câu giới hạn thay cho phát biểu về lưới
  đồng nhất.
- **T6 và T6b đứng:** một câu Sec. V-A mô tả cơ chế gộp là "consistent with". Nhãn C5 nâng thành "đứng có điều kiện" trong CLAIMS_EVIDENCE (AI quyết theo
  ủy quyền). Không đứng: không đổi paper (C5 vốn không có trong paper); ghi DL.
- **D1–D4:** D1 và D4 vào cùng đoạn với T1/T5 nếu có chỗ; nếu không có chỗ thì vào 02_Code/README.


**Riêng X1c:**
- T3 đứng: câu post-hoc về độ dốc trong paper được thay bằng kết quả xác nhận: "with 1000 T_int records, on a fresh grid…".
- T3 không đứng: paper giữ câu 27% và thêm rằng bản ghi dài hơn không xác nhận được trên lưới mới.

## Luật loại và dừng
- NOT_RUN do cap chi phí (theo pilot), báo số đếm.
- Truth một lần; bị ngắt thì INCOMPLETE, chấm trên regime COMPLETED và báo rõ.
- Không chạy lại để cải thiện. Mọi cải thiện là bước mới, có thẻ mới.


