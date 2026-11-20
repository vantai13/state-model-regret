# Card X5b: cảnh báo nghẽn trên ma trận GÉANT thật với điều biến trong slot η = 0,6 (Claude, 21/11/2026 ~1h)

Bước mới, **post hoc so với X5**, viết trước mọi outcome của X5b. Tác giả ủy quyền toàn bộ (20/11/2026 khuya). Thiết kế:
`state-model-regret-papers/letter_smr/briefs/strengthen2/DESIGN_X5B_BURST.md`.

## Vì sao có bước này (từ X5 step 0, đã thấy)
- X5 (η = 0,3) dừng NOT_ENOUGH_SIGNAL: cảnh báo 517/30720 ứng viên, tất cả trong một ngày (NEWB3, 29/8/2005), và ngày đó Hybrid trùng Stationary 0/32.
- **Nguyên nhân đã kiểm:** điều biến trong slot bị chặn ở (1+η) lần mức trung bình, nên link có utilization trung bình dưới 1/(1+η) ≈ 0,77 không
  bao giờ có hàng đợi. Tải đỉnh (1+η)·tải/dung lượng của e* trong warm-up vượt 1 ở 0/8 ngày (NEWB1), 4/29 (NEWB2), 3/23 (NEWB3); nhiều ngày có
  chứng nhận hàng đợi bằng 0. Vậy với η = 0,3, đường mà luật tĩnh chọn gần như không nghẽn tạm thời, nên telemetry không có thông tin để vượt luật tĩnh.
- **Câu hỏi X5b:** độ bụi (burstiness) trong slot của ma trận thật là chưa biết. Với η = 0,6 (mức cao đã có trong lưới GÉANT tổng hợp của letter),
  kết luận (c), (d) trên ma trận thật có đổi không.

## Điều đã thấy trước
- Toàn bộ X5 step 0 (η = 0,3), bảng tải đỉnh ở trên, X4b, V7-3, V7-4, X2 và mọi kết quả letter.
- **Chưa thấy:** bất kỳ số nào với η = 0,6 trên ma trận thật (cảnh báo, quyết định, regret, ŝ train).

## Thiết kế khóa (giống X5, chỉ khác những điểm ghi rõ)
- **η = 0,6** cho mọi mô phỏng: warm-up, posterior, rollout quyết định và đánh giá, **và ŝ train** (tính lại trên 26 ngày train theo đúng cách X4b,
  seed train mới 7000015). Mọi thứ khác của X4b (regime NEWB1–3, capacity, e*, managed flow, 60 bản ghi test-S, K, R_dec, R_eval, h, cổng
  evaluability) giữ nguyên.
- Cảnh báo, chọn mẫu, ALARM_RARE: như X5 (M = 512, Q_e* ≥ 0,001·c[e*] Mbit, N ≤ 32, < 8 là RARE). Seed test 7000011, pilot 7000013.

## Bước 0 và cổng
Như X5: SIGNAL_OK nếu ở ít nhất một regime có ≥ 5 bản ghi không RARE, share bất đồng phía tươi gộp ≥ 5% ở ít nhất một h ≤ 1800 s.
Ngược lại NOT_ENOUGH_SIGNAL: dừng, báo.

## Test
**T1–T4 đúng nguyên văn `results/letter/x5_alarm/CARD_X5.md`** (cùng ngưỡng, đơn vị, quy ước), áp cho dữ liệu X5b.

## Dự báo của Claude (không phải test)
Cổng qua (60%). Nếu qua: T1 ĐỨNG (45%), T2 ĐỨNG (75%), T3 ĐỨNG (60%), T4 ĐỨNG (65%).

## Luật đưa vào paper (cố định trước, mọi kết cục)
- Letter Sec. IV-B4, sau câu X4b, trong **mọi** kết cục:
  1. một mệnh đề X5: quyết định kích hoạt khi e* có backlog ≥ 1 ms gần như không xảy ra (517/30720 ứng viên, một ngày, Hybrid trùng Stationary 0/32),
     vì điều biến η = 0,3 không làm link dưới khoảng 77% utilization nghẽn;
  2. một câu X5b: với η = 0,6, số cảnh báo, kết quả T1 (GAIN/LOSS/UNRESOLVED trên số ô đủ điều kiện), T3, T4; hoặc NOT_ENOUGH_SIGNAL với share bất đồng.
- Câu "intermediate-horizon gains therefore rest mainly on CTMC and synthetic GÉANT results" giữ nếu T1 không ĐỨNG; nếu T1 ĐỨNG thì sửa thành
  "on real matrices they appear only at congestion alarms with the higher within-slot modulation".
- Abstract chỉ đổi nếu T1 ĐỨNG (một mệnh đề có điều kiện η = 0,6). Không chọn theo kết quả.

## Rút (21/11/2026 ~1h15)
X5b bị rút trước mọi outcome (Codex dừng sau ~1 phút, chưa tạo file). Thay bằng `results/letter/x5c_alarm/CARD_X5C.md` vì cảnh báo phải đặt trên đường mà luật tĩnh chọn.
