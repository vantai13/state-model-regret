# Card X5c: cảnh báo nghẽn trên đường mà luật tĩnh chọn, ma trận GÉANT thật, η = 0,3 và 0,6 (Claude, 21/11/2026 ~1h15)

Viết **trước mọi outcome của X5c**. Thay thế `results/letter/x5b_burst/CARD_X5B.md`: X5b được **rút trước khi có bất kỳ outcome nào** (Codex bị dừng sau
khoảng 1 phút, chưa tạo file). Tác giả ủy quyền toàn bộ (20/11/2026 khuya). Thiết kế: `letter_smr/briefs/strengthen2/DESIGN_X5C_ALARM.md`.

## Vì sao sửa (từ X5 step 0, đã thấy)
- Thẻ X5 định nghĩa cảnh báo là "nghẽn tức thời **trên đường mà luật tĩnh chọn**", nhưng ghi kèm "(e* trên đường Switch của NEWB1–3)". Phần trong ngoặc
  sai: ŝ train của X4b là NEWB1 +64371, NEWB2 −76945, NEWB3 +29918 (Mbit), nên luật tĩnh chọn **Stay** ở NEWB1 và NEWB3, **Switch** ở NEWB2.
  Cảnh báo trên e* (đường Switch) ở NEWB1/NEWB3 không thể tạo bất đồng Hybrid–Stationary. Ngày duy nhất có cảnh báo (NEWB3, 29/8) có cả ba luật chọn Stay.
- Ở NEWB2, cảnh báo trên e* gần như không xảy ra vì với η = 0,3 link dưới khoảng 77% utilization không nghẽn (tải đỉnh của e* vượt dung lượng ở 4/29 ngày).
- X5 vẫn giữ nguyên verdict NOT_ENOUGH_SIGNAL và được báo trong paper theo luật của nó.

## Thiết kế khóa
- Như X5 (regime NEWB1–3, capacity và managed flow của X4b, 60 bản ghi test-S, M = 512, N ≤ 32, MIN_ALARMS = 8, K, R_dec, R_eval, h, cổng
  evaluability, paired metrics), trừ:
  - **Link cảnh báo** của mỗi regime = link nghẽn của đường mà luật tĩnh chọn theo dấu ŝ train của nhánh: Switch (e*) nếu ŝ < 0, ngược lại link nghẽn
    của đường Stay (`path_bottleneck_indices_after[0]` trong cấu hình X4b). Cảnh báo khi backlog link đó ở trạng thái tươi ≥ 0,001·c[link] Mbit
    (1 ms phục vụ của chính link đó).
  - **Nhánh A:** η = 0,3, ŝ train của X4b (không đổi). Seed test 7100001, pilot 7100003.
  - **Nhánh B:** η = 0,6 ở mọi mô phỏng, ŝ train tính lại trên các bản ghi train của X4b theo đúng phương pháp X4b, seed train 7200005; link cảnh báo theo
    dấu ŝ mới. Seed test 7200001, pilot 7200003.

## Bước 0 và cổng (mỗi nhánh riêng)
Như X5: SIGNAL_OK nếu ở ít nhất một regime có ≥ 5 bản ghi không RARE, share bất đồng phía tươi gộp ≥ 5% ở ít nhất một h ≤ 1800 s. Nhánh không qua thì
dừng nhánh đó (NOT_ENOUGH_SIGNAL), nhánh kia vẫn tiếp.

## Test (mỗi nhánh riêng)
**T1–T4 đúng nguyên văn `results/letter/x5_alarm/CARD_X5.md`.** Nhánh A là kết quả chính (mô hình cơ sở của letter); nhánh B là độ nhạy theo độ bụi trong slot.

## Dự báo của Claude (không phải test)
Nhánh A: cổng qua (70%), T1 ĐỨNG (50%), T2 ĐỨNG (75%), T3 ĐỨNG (65%), T4 ĐỨNG (70%). Nhánh B: cổng qua (75%), T1 ĐỨNG (50%).

## Luật đưa vào paper (cố định trước, mọi kết cục)
- Sec. IV-B4, sau câu X4b, trong **mọi** kết cục:
  1. một mệnh đề X5 (cảnh báo trên đường Switch gần như không xảy ra, 517/30720 ứng viên, Hybrid trùng Stationary 0/32);
  2. một câu X5c nhánh A: cảnh báo trên đường mà luật tĩnh chọn, số cảnh báo, T1 (GAIN/LOSS/UNRESOLVED trên số ô đủ điều kiện), T3 (share tie, regret M0),
     T4; hoặc NOT_ENOUGH_SIGNAL với share bất đồng;
  3. một mệnh đề nhánh B (T1 và T3, hoặc NOT_ENOUGH_SIGNAL).
- Nếu T1 nhánh A ĐỨNG: câu "intermediate-horizon gains therefore rest mainly on CTMC and synthetic GÉANT results" sửa thành câu nói lợi ích trên ma trận
  thật xuất hiện ở các quyết định kích hoạt bởi cảnh báo, và abstract thêm một mệnh đề. Nếu không: giữ nguyên, abstract không đổi.
- Không chọn theo kết quả; mọi cải thiện sau là bước mới gắn nhãn post hoc.
