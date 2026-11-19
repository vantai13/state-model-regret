# V7-4 — kết quả (Claude, 20/11/2026)

Người phụ trách **Doan Van Tai**. Tác giả duyệt P1 và giao toàn quyền quyết định. Claude viết thẻ (`28419eda3`, trước mọi tính
toán) và kiểm độc lập. Codex viết runner, test và audit, rồi chạy bước 0 (`e183d8d78`).

## Verdict
**NOT_ENOUGH_SIGNAL, truth không chạy (đúng luật dừng của thẻ).**
- Trên DAY1/DAY2, 29 ngày ổn định, hold 5–30 phút, τ ∈ {5, 15} phút, cả hai phía: Hybrid và Stationary trùng nhau ở **37120/37120**
  quyết định.
- Kết quả giống hệt với Hybrid dùng ŝ chỉ từ ngày ổn định (−320 Mbit, nhỏ hơn khoảng 300 lần).
- DAY3 (đối chứng): 0/18560.

## Nguyên nhân (kiểm độc lập trên raw, không dùng outcome)
- Gap fluid Switch − Stay **không bao giờ dương**, cả phía fresh lẫn stale, ở mọi hold.
  - Phía fresh: 86,4% bằng 0 (tie, M0 chọn Stay), phần còn lại âm.
  - Phía stale: 0,24% bằng 0.
- Mọi ưu tiên chặt của twin fluid đều chỉ về Switch, cùng dấu với ŝ < 0. Vì vậy phần hiệu chỉnh không bao giờ đổi quyết định
  so với luật tĩnh, dù h hay |ŝ| nhỏ đến đâu.
- Trên trace này, sai lầm của M0 chỉ đến từ tie, nhất quán với V7-3 (M0 không bao giờ ưu tiên chặt đường có rate cao hơn).
- Lợi thế ở horizon trung gian chỉ có thể xuất hiện khi ưu tiên fluid mâu thuẫn với thứ tự rate. Điều đó không xảy ra ở kịch bản
  trace này (nghẽn nằm trên đường Stay).

## Sai sót của Claude ở bước kiểm khả thi (19/11)
- Claude báo "3,4% trạng thái có |Δ̂| > h|ŝ|" và suy ra Hybrid có thể khác Stationary ở khoảng 3%.
- Phép đếm đó **bỏ qua dấu**: mọi gap lớn đều cùng dấu với ŝ, nên không tạo bất đồng.
- Codex phát hiện, Claude kiểm lại và xác nhận. Sai sót không ảnh hưởng outcome (chưa có outcome nào được tính), nhưng dẫn tới dự báo F1 sai.

## Dự báo của Claude
| Dự báo | Kết quả |
|---|---|
| F1: bất đồng phía fresh 1–6% | **Sai** (0%) |
| F2: H-P1 POSITIVE | Không đánh giá được (không chạy truth) |
| F3: tie M0 phía fresh ≥ 70% | Đứng (86,4%) |
| F4: ŝ chỉ ngày ổn định cho nhiều bất đồng hơn | **Sai** (0 cả hai) |

## Đưa vào paper (luật cố định trong thẻ, nhánh NOT_ENOUGH_SIGNAL)
Câu V-C về horizon trung gian được thay bằng: ở hold 5–30 phút trên cùng các ngày ổn định, twin hiệu chỉnh vẫn chọn đúng action
của luật tĩnh ở cả 37120 quyết định, vì không ưu tiên fluid nào nghiêng về đường có rate cao hơn; vì vậy lợi thế trung gian chỉ
dựa trên CTMC và GÉANT tổng hợp. Ledger `V74_SIGNAL`.

## Giới hạn
- Một kịch bản trace (ba flow, đường Switch tránh link bận nhất), 29 ngày ổn định, tải hiệu chỉnh 0,9, điều biến tổng hợp trong slot.
- Kết quả không có nghĩa là thông tin trạng thái vô dụng trong mọi mạng thật. Nó cho thấy kịch bản này không chứa tình huống mà
  lợi thế trung gian có thể xuất hiện.
- Một kịch bản có nghẽn ở cả hai đường (ưu tiên fluid có thể ngược thứ tự rate) là việc tiếp theo nếu cần.
