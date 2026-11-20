# Card X-GÉANT (X2; X4 dừng ở cổng), Claude, 20/11/2026, viết trước mọi truth test-seed

- **Người phụ trách:** Doan Van Tai. Claude viết và duyệt thay tác giả theo ủy quyền toàn quyền; không mentor review, không dự báo của tác giả.
- **Design:** `letter_smr/briefs/strengthen/DESIGN_X_GEANT.md` (commit `581e769`).
- **Code:** `experiments/letter/x_geant.py`. Lock gốc: `lock.json`. Thẻ này và scorer thẻ được khóa bổ sung trong `lock_card.json`.

## Lệch protocol cần ghi
- Codex tạo `lock.json` (chưa commit) **trước** khi thẻ này được viết.
- Chưa có truth test-seed nào. Thẻ viết sau khi đã thấy:
  - số đếm bước 0 (chỉ quyết định);
  - dự đoán từ ngày train (`predictions.json`);
  - một pilot (BOTH1, 19/07/2005, seed pilot), gồm outcome của bản ghi đó.
- Không có outcome test-seed nào của X2 được tính hay đọc.

## Điều đã thấy (exposure)
- **Bước 0 (chỉ quyết định):**
  - X2 test-S: bất đồng fresh/stale TH_0,5 = 501, TH_0,65 = 582, TH_0,8 = 361, TH_0,9 = 177, MLU = 443, trên 5568 mỗi rule;
  - tie = 0 với TH_0,65/0,8/0,9;
  - X4 Hybrid ≠ Stationary 0/8352 (M0 tie 100%) nên NOT_ENOUGH_SIGNAL, X4 dừng.
- **Dự đoán từ train-S** (`predictions.csv`, 96 dòng NEW):
  - ŝ < 0 ở cả ba regime;
  - ΔF̂ > 0 (stale Switch nhiều hơn) với TH_0,65 và TH_0,8, nên dấu dự đoán G_S = −1 (fresh hại);
  - ΔF̂ < 0 với TH_0,9, nên dấu dự đoán +1 (fresh lợi);
  - TH_0,5 và MLU có ΔF̂ ≈ 0 (bỏ phiếu trắng, trừ NEW1 0,0022);
  - Hybrid và Stationary: ΔF̂ = 0, cả hai phía luôn Switch.
- Null utilization cùng dấu với dự đoán ở **mọi** ô X2, vì đường Switch vừa ít tải hơn vừa có ŝ < 0. Vì vậy **phép so với null là NOT_EVALUABLE
  ở X2** (khai trước).
- Các kết quả V7-3/V7-4 cũ trên DAY1–3 đã biết; regime NEW1–3 là OD mới.

## Quần thể và đơn vị
- **X2:** regime NEW1–3, bản ghi test-S, rule TH_0,65, TH_0,8, TH_0,9 (ô có dấu dự đoán ≠ 0), τ ∈ {300, 900} s, h ∈ {4, 6} h, bản ghi có
  `evaluable = True` ở h đó.
- **Ô gộp** = (regime, rule, τ, h): trung bình G_S qua các ngày evaluable, SE theo ngày (độ lệch chuẩn / √n). Ô **resolved** nếu |mean| ≥ 2·SE và
  |mean| ≥ 0,25% của mean C_ref.
- **Đơn vị phụ, ở mức bản ghi:** resolved nếu |G_S| ≥ 2·SE theo instance và ≥ 0,25% C_ref.
- Các ô không độc lập (cùng ngày, cùng rollouts CRN).

## Test (confirmatory)
| ID | Claim | Đạt nếu | NOT_EVALUABLE nếu |
|---|---|---|---|
| G1 | Dấu G_S của rule ngưỡng dự đoán từ ngày train (ŝ·ΔF̂) | độ chính xác ≥ 0,80 trên ô gộp resolved | < 6 ô gộp resolved |
| G2 | Rule có số hạng dừng (Stationary, trùng Hybrid ở X2) không bị freshness ảnh hưởng và có regret thấp | G_S = 0 ở mọi bản ghi **và** median both-side regret ≤ 0,5% C_ref trên bản ghi evaluable ở h ∈ {4, 6} h | < 20 bản ghi evaluable |
| G3 | Stationary hơn rule ngưỡng | both-side regret Stationary ≤ min_θ both-side regret của TH_θ ở ≥ 90% (bản ghi, τ, h) evaluable | < 20 |

**Mô tả (không phải test):**
- D1: G_S theo rule, kể cả M0, TH_0,5, MLU;
- D2: độ chính xác ở mức bản ghi;
- D3: harm tính bằng ms của link service, cạnh % C_ref;
- D4: ô dự đoán sai, kèm nguyên nhân phân tích sau, không đổi verdict.

## Dự báo của Claude (để có thể sai)
- **F1:** TH_0,65 và TH_0,8 có G_S < 0 resolved ở đa số ô gộp; TH_0,9 có G_S > 0.
- **F2:** G1 đứng với độ chính xác 0,8–1. Rủi ro: ngày test không dừng.
- **F3:** G2 và G3 đứng; Stationary gần như không có regret vì Switch tối ưu (ŝ rất âm).

## Luật đưa vào paper (cố định trước, mọi kết cục)
- **G1 và G3 đứng:**
  - Sec. V-C thêm 2 câu: trên cùng ma trận thật, rule ngưỡng utilization (quyết định chặt, không tie) bị telemetry tươi làm tệ hơn ở θ mà
    train dự đoán, và tốt hơn ở θ = 0,9 như dự đoán; dấu đúng ở x/y ô; rule dừng tránh được cả hai.
  - Intro: câu phân biệt issue 1 thêm vế "and the same sign rule holds for a threshold twin on real matrices".
  - Ledger ID mới.
- **G1 không đứng:** một câu V-C với x/y, ghi rằng ngày không dừng làm sai dự đoán dừng.
- **G2 hoặc G3 không đứng:** một câu giới hạn.
- **X4 (NOT_ENOUGH_SIGNAL):** một mệnh đề nối vào câu V74 hiện có: trên các flow có đường Switch cũng tải cao, twin fluid tie ở mọi quyết định nên
  Hybrid trùng luật tĩnh (0/8352). Ledger ID mới.

## Dừng
- Truth một lần trên GCP. Bị ngắt thì INCOMPLETE; không resume hay retry.
- Scorer thẻ (`x_geant_card.py`) khóa trước truth; không sửa sau outcome.
