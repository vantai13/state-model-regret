# Card X-CTMC (X1, X1b, X3): BẢN CHÍNH, viết trước mọi truth (Claude, 20/11/2026)

- **Người phụ trách:** Doan Van Tai. Claude viết và duyệt thay tác giả theo ủy quyền; không mentor review, không dự báo của tác giả.
- **Design:** `DESIGN_X_CTMC.md` (commit `581e769`, letter_smr).
- **Bản chính** chép nguyên văn các test, ngưỡng và luật đưa vào paper từ bản nháp (`letter_smr/briefs/strengthen/CARD_X_CTMC_DRAFT.md`,
  commit trước pilot). Chỉ thêm mục "Bổ sung sau pilot" ở cuối.
- **Scorer thẻ:** `experiments/letter/x_ctmc_card.py`, khóa trong `lock_card.json` trước truth.
- **Thứ tự thực tế:** `predict` chạy song song lúc viết bản chính. Thẻ không dùng bất kỳ con số nào từ `predictions.json`.

## Điều đã thấy trước (exposure)
- Mọi kết quả CTMC cũ của letter, đều trên lưới đồng nhất μ = 10, cùng α, cùng κ:
  - W1b, PL (51/56 regime giữ harm với posterior học);
  - T4 (40/48 đổi dấu, 8/8 một dấu);
  - P2 (Hybrid hơn luật tĩnh ở T_int 81/93);
  - tie CTMC 0,015.
- Lưới mới **chưa có truth nào**. Pilot (4 regime nặng nhất, seed pilot) sẽ cho CPU-s và cả outcome của 4 regime đó. Bốn regime đó được **loại khỏi
  phép thử**, chỉ báo như pilot.

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
| F1 | TH_θ có harm (D1) ở ≥ 30% regime với θ ∈ {0,8; 0,9}, ít hơn với θ = 0,5 |
| F2 | T1 đứng, độ chính xác khoảng 0,9–0,95; tầng disagree thấp hơn tầng agree |
| F3 | Null utilization ở tầng disagree đúng ≤ 0,5, nên T2 đứng |
| F4 | M0 có harm ở ≥ 50% regime dị biệt tại 30 T_int |
| F5 | T5 đứng nhưng sát ngưỡng (khoảng 0,9) |
| F6 | T6 đứng; T6b đứng |

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

## Luật loại và dừng
- NOT_RUN do cap chi phí (theo pilot), báo số đếm.
- Truth một lần; bị ngắt thì INCOMPLETE, chấm trên regime COMPLETED và báo rõ.
- Không chạy lại để cải thiện. Mọi cải thiện là bước mới, có thẻ mới.


## Bổ sung sau pilot (chỉ danh sách và chi phí, không đổi test)
- Lưới: 64 regime (32 agree / 32 disagree), seed grid 2611201; 0 trùng held-out L7.2; 0 regime gần rỗng.
- NOT_RUN do cap chi phí dự phóng: 1 (XCTMC_028, khoảng 9674 CPU-s > 3600). Còn 63 regime PLANNED, dự phóng 1,67 CPU-h.
- Pilot (seed 2611204, h = 1 T_int, τ ∈ {1, 3}): XCTMC_053, XCTMC_044, XCTMC_047, XCTMC_028. Các regime này **bị loại khỏi mọi test** (scorer
  dùng `pilot_exposed_regimes`). Chi phí 2157 CPU-s.
- **Sanity XFAIL:** design §8 viết "TH_θ với θ ≥ 1 không bao giờ Switch", nhưng U_{A,0} > 1 có thể xảy ra ở mode cao. Codex đưa phản ví dụ hợp lệ
  và để test XFAIL. Lưới chỉ dùng θ ≤ 0,9, nên điều này **không** ảnh hưởng rule nào trong test. Ghi nhận là lỗi viết design của Claude.
- Đối chiếu với `ctmc` cũ ở a = 6, μ = 10: khớp (sai lệch tương đối 0). 50 test đạt + 1 XFAIL.
- `x_ctmc.score` (của Codex) chỉ báo số đếm. Verdict của thẻ do `x_ctmc_card.py` tính, theo đúng ngưỡng trên.
