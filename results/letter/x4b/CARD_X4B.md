# Card X4b (hai link nghẽn khác nhau trên GÉANT thật): viết trước truth (Claude, 20/11/2026)

- **Người phụ trách:** Doan Van Tai. Claude viết và duyệt thay tác giả theo ủy quyền; không mentor review, không dự báo của tác giả.
- **Design:** `letter_smr/briefs/strengthen/DESIGN_X4B.md` (`dea74a3`).
- **Code chuẩn bị:** `experiments/letter/x4b.py` (Codex). Lệnh truth và score sẽ do Codex thêm **sau** thẻ này; lock lại trước truth.

## Điều đã thấy (exposure)
- **Bước 0 (chỉ quyết định), test-S:** Hybrid ≠ Stationary ở 93/5760 (900 s), 62/5760 (1200 s), 6/5760 (1800 s); 0 ở các h khác.
  - Toàn bộ bất đồng nằm ở **NEWB3, 19/07/2005**.
  - Ưu tiên fluid chặt về action có rate cao hơn: fresh 135/1920, stale khoảng 957/1920 mỗi h.
- **Dự đoán train** (`predictions.json`): dấu G_S của M0 theo ŝ·ΔF̂.
- **Pilot:** một bản ghi, seed pilot 7472001, đã thấy outcome của bản ghi đó.
- Ngày test là cùng các ngày V7-3/X-GÉANT, nhưng regime NEWB1–3 (OD và capacity e*) là mới.

## Quyết định trước truth
- **Cổng evaluability với capacity theo link:** dùng capacity đồng nhất c₀ = 12 544,525174 Mbit/s (71/72 link) cho ngưỡng "mean C_ref backlog / h ≥ 1 ms ×
  c₀". Cùng thước với X-GÉANT; chọn trước khi có outcome.
- Chỉ ngày S vào truth (60 bản ghi). Không chạy ngày O.

## Phép đọc và test
**B1 (đọc thăm dò, không phải pass/fail; chỉ một ngày có bất đồng).**
- Phạm vi: các (bản ghi, phía, h ≤ 1800 s) mà Hybrid và Stationary bất đồng ở ≥ 1% instance.
- Đại lượng: hiệu regret theo cặp Hybrid − Stationary, trung bình qua instance, SE theo instance.
- Đọc:
  - **GAIN** nếu trung bình < 0 và |trung bình| ≥ 2·SE;
  - **LOSS** nếu > 0 và ≥ 2·SE;
  - ngược lại **UNRESOLVED**.

**B2 (test, không kém hơn):** trên mọi (bản ghi, phía, h ≤ 1800 s) evaluable, regret both-side của Hybrid ≤ của Stationary + 0,05 điểm % C_ref.
- **ĐỨNG** nếu ≥ 95%.
- NOT_EVALUABLE nếu < 20 trường hợp evaluable.

**B3 (test, harm của M0 không do tie).** Ở h ∈ {3600, 7200} s, trên bản ghi evaluable:
- **(a)** dấu G_S của M0 theo dự đoán train ŝ·ΔF̂: ô gộp (regime, τ, h), resolved như X-GÉANT (|mean| ≥ 2·SE theo ngày và ≥ 0,25% C_ref). **ĐỨNG** nếu độ
  chính xác ≥ 0,80 trên ô resolved; NOT_EVALUABLE nếu < 4 ô resolved.
- **(b) Mô tả:** tách regret phía fresh của M0 thành phần từ quyết định tie và phần từ quyết định chặt. Báo tỉ lệ phần chặt.

## Dự báo của Claude
| F | Dự báo |
|---|---|
| F1 | B1: UNRESOLVED ở đa số ô; nếu resolved thì nghiêng GAIN |
| F2 | B2 đứng (Hybrid trùng Stationary gần mọi quyết định) |
| F3 | B3(a) NOT_EVALUABLE hoặc không đứng (ít ngày evaluable, share đổi theo mùa như X2) |
| F4 | B3(b): phần chặt chiếm ≥ 30% regret phía fresh của M0 |

## Luật đưa vào paper (cố định trước, mọi kết cục)
- **Sec. V-C, một câu**, viết trong mọi kết cục:
  - có link nghẽn thứ hai trên đường Switch (capacity đặt cho utilization 0,85), Hybrid khác luật tĩnh ở x/y quyết định, tất cả trong một ngày;
  - kết quả B1 (GAIN/LOSS/UNRESOLVED kèm số);
  - B2.
- **B3(b) có phần chặt ≥ 10% regret phía fresh:** thêm một mệnh đề "unlike the single-bottleneck flows, part of M0's fresh regret comes from strict fluid
  preferences (x%)". Nếu < 10% thì một mệnh đề ngược lại.
- **B3(a):** con số trong cùng câu trong mọi kết cục.

## Dừng
Truth một lần trên GCP. Bị ngắt thì INCOMPLETE. Raw commit trước khi chấm. Chấm lại độc lập (Codex hoặc Claude).
