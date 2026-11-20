# Card X5: quyết định khi có cảnh báo nghẽn trên ma trận GÉANT thật (Claude, 21/11/2026 0h)

Viết **trước** mọi outcome của X5 (cả step 0 lẫn truth). Tác giả ủy quyền toàn bộ ("tự thiết kế tự chạy và cho bạn quyền", 20/11/2026 khuya);
mọi quyết định dưới đây là của AI theo ủy quyền. Thiết kế: `state-model-regret-papers/letter_smr/briefs/strengthen2/DESIGN_X5_ALARM.md`.

## Câu hỏi
Điểm yếu (c) và (d) của letter v10:
- (c) trên ma trận thật, regret của M0 gần như chỉ đến từ tie;
- (d) lợi ích riêng của hybrid so với luật tĩnh chỉ thấy trên dữ liệu tổng hợp; trên ma trận thật hybrid trùng luật tĩnh, trừ một ngày (X4b).

Lý thuyết (Prop. 2, Cor. 1) nói hybrid khác luật tĩnh khi gap fluid tức thời lớn so với h|ŝ| và ngược dấu ŝ. Với quyết định lấy mẫu đều,
điều đó hiếm (X4b: 161/40320). **X5 hỏi:** khi quyết định được kích hoạt bởi cảnh báo nghẽn tức thời trên đường mà luật tĩnh chọn (e* trên đường
Switch của NEWB1–3), hybrid có thấp hơn luật tĩnh ở hold ngắn–trung bình không, có trùng ở hold dài không, và harm của M0 có đến từ ưu tiên chặt không.

## Điều đã thấy trước (exposure)
- X4b trên cùng regime NEWB1–3 và cùng 60 bản ghi test-S, với điểm quyết định lấy đều: bất đồng 161/40320, chỉ ngày 19/7/2005; B1 6 GAIN/0 LOSS/
  3 UNRESOLVED; B2 70/70; phần chặt 0,81% regret tươi của M0. Capacity, ŝ train (pooled) của X4b dùng lại nguyên, chỉ từ train.
- V7-3, V7-4, X2, X-CTMC, X1c và toàn bộ kết quả letter.
- **Chưa thấy:** bất kỳ số nào ở điểm cảnh báo (tỷ lệ cảnh báo, quyết định, regret).

## Thiết kế khóa
- Regime NEWB1, NEWB2, NEWB3; capacity, managed flow, e* đúng như `results/letter/x4b/configuration.json`.
- Bản ghi: đúng 60 bản ghi test-S trong kế hoạch truth của X4b. Seed **mới**: test 7000001, pilot 7000003 (khác mọi seed cũ).
- Mỗi bản ghi: M = 512 warm-up ứng viên (độc lập, như X4b). **Cảnh báo:** backlog của e* ở trạng thái tươi ≥ 1 ms phục vụ của e*, tức
  Q_e* ≥ 0,001 · c[e*] Mbit. Chọn tối đa N = 32 ứng viên có cảnh báo theo thứ tự chỉ số; trạng thái cũ (τ = 300, 900 s) lấy từ chính các quỹ đạo đó.
  Bản ghi có < 8 cảnh báo là ALARM_RARE: không vào truth, được đếm.
- Rule, horizon, K, R_dec, R_eval, chuẩn hóa C_ref, cổng evaluability: đúng như X4b.

## Bước 0 (chỉ quyết định, trước truth)
Báo: số cảnh báo/512 theo bản ghi, số bản ghi ALARM_RARE, share bất đồng Hybrid ≠ Stationary (phía tươi) theo regime và h, share tie của M0 tươi.
**Cổng:** SIGNAL_OK nếu ở ít nhất một regime có ≥ 5 bản ghi không RARE, share bất đồng phía tươi gộp ≥ 5% ở ít nhất một h ≤ 1800 s.
Ngược lại NOT_ENOUGH_SIGNAL: dừng, không truth, báo đúng như vậy.

## Test (đơn vị: bản ghi = (regime, ngày); SE qua ngày; đơn vị chênh lệch: điểm phần trăm của C_ref)
- **T1 (d, chính).** Ô = (regime, h), h ∈ {300, 600, 900, 1200, 1800} s, đủ điều kiện nếu share bất đồng phía tươi gộp của ô ≥ 5% và có ≥ 5 bản ghi.
  D = trung bình theo ngày của chênh lệch regret phía tươi theo cặp Hybrid − Stationary (định nghĩa paired như X4b).
  - GAIN nếu D ≤ −0,05 và D + 2SE < 0; LOSS nếu D ≥ +0,05 và D − 2SE > 0; còn lại UNRESOLVED.
  - **ĐỨNG** nếu số ô đủ điều kiện ≥ 3, số GAIN ≥ ⌈một nửa số ô đủ điều kiện⌉ và LOSS = 0. **ĐỔ** nếu ≥ 3 ô đủ điều kiện mà không đạt.
    **NOT_EVALUABLE** nếu < 3 ô đủ điều kiện.
- **T2 (trùng ở hold dài, Prop. 2).** Ở h = 7200 s, quyết định phía tươi của Hybrid trùng Stationary ở ≥ 95% điểm cảnh báo gộp mọi regime.
- **T3 (c, harm chặt).** Ở điểm cảnh báo, share tie của M0 tươi gộp ≤ 10%, **và** regret trung bình phía tươi của M0 ở h = 7200 s > 0,5% C_ref
  ở ≥ 2/3 regime.
- **T4 (hiệu chỉnh ở hold dài).** Regret hai phía của Hybrid ở h = 7200 s ≤ 0,5% C_ref ở ≥ 80% bản ghi evaluable.
- **Mô tả, không test:** G_S của M0 và Hybrid theo h; share phần chặt trong regret tươi của M0; tỷ lệ cảnh báo; chênh lệch Hybrid − Stationary ở 3600 s.

## Dự báo của Claude (không phải test, ghi để có thể sai)
T1 ĐỨNG với GAIN tập trung ở 300–900 s (khoảng 55%); T2 ĐỨNG (80%); T3 ĐỨNG (70%); T4 ĐỨNG (75%); cổng bước 0 qua (75%).

## Luật đưa vào paper (cố định trước, mọi kết cục)
- Letter v10 Sec. IV-B4, ngay sau câu X4b, thêm 1–2 câu trong **mọi** kết cục: thiết kế cảnh báo (một mệnh đề), kết quả T1 (số GAIN/LOSS/UNRESOLVED
  trên số ô đủ điều kiện, khoảng D), T3 (share tie, regret M0), T4 (share). Nếu NOT_ENOUGH_SIGNAL: một mệnh đề báo share bất đồng.
- Abstract và Introduction chỉ đổi nếu T1 ĐỨNG (khi đó một mệnh đề "including congestion-triggered decisions on real traffic matrices").
- Không chọn theo kết quả: không thêm/bỏ regime, ngưỡng hay h sau khi thấy số. Cải thiện sau đó là bước mới, gắn nhãn post hoc.
