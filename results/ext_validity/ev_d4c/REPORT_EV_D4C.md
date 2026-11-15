# EV-D4c — luật dấu hỏng ở đâu và vì sao: dải τ/T_int × lặp trace × tải (15/11/2026)

Doan Van Tai — **AI theo ủy quyền** (`LOCKED_AI_DELEGATED`): Claude thiết kế, khóa, chấm; Codex viết code và chấm lại độc lập.

Tác giả yêu cầu làm cả hai đề xuất của EV-D4b và giao code cho Codex. Thẻ: [CARD.md](CARD.md).

## Trình tự

| Bước | Commit | Ghi chú |
|---|---|---|
| Thẻ giả thuyết | `8136c510` | Viết trước mọi output EV-D4c |
| Code (Codex, 34 test) và thiết kế probe | `1fc67ac9` | |
| Train 60 probe + 480 case, 1920 dự đoán, khóa 17 file | `d818dbc4` | Có đính chính về lỗi chuẩn hóa trong `describe` |
| Một lần chạy test trên VM n2-standard-32 | — | 960/960 job, 55 phút |
| Dữ liệu thô + manifest | `a820c7c6` | Commit trước khi đọc điểm |
| Điểm | `f5852a42` | Chấm lại local trùng từng byte với VM |
| Codex chấm lại độc lập | `d4429686` | Stdlib, không import code chấm: **MATCH**, 12 842 trường |

## Thiết kế

Ba nhánh trên cùng trace DITL 2023-04-12, hai đường A/B là hai tập flow rời nhau, chung một pha:

- **C**: trace 4 giờ liên tục, tải thấp (≤ 0,775), 20 regime mới.
- **L**: cùng 20 regime và cùng seed như C, chỉ đổi sang đoạn 15 phút cho lặp.
- **H**: đoạn lặp, tải cao (0,78–0,975), 20 regime mới.

τ = r·T_int với r ∈ {0,1; 0,3; 0,5 | 0,8; 1; 1,2 | 2,5; 5}, ba nhóm low | band | high. Cả 3 nhánh giữ đủ 20/20 regime.

T_int trung vị theo nhánh: C 126 s, L 19 s, H 74 s.

## Kết quả theo thẻ

| ID | Kết quả | Verdict | Dự đoán của AI trước khi chạy |
|---|---|---|---|
| H1: C, nhóm low, dấu phần tăng ≥ 0,80 | 52/73 = 71,2% | **FAIL** | PASS (sai) |
| H2: C, nhóm band, ≤ 0,65 và tỷ lệ phần tăng trung vị < 0,5 | 54,2% và 0,196 | **PASS** | PASS |
| H3: nguyên nhân | band L 106/106 = 1,00 (WORKS); band H 104/105 = 0,99 (WORKS) | **LOOPING** | LOOPING (độ tin thấp) |
| D6-C: T12 dạng O(1), trace liên tục | 279/320 = 87,2% | **FAIL** | PASS (sai) |
| D6-L, D6-H (khám phá) | 98,1% / 97,5% | PASS | không dự đoán |

Theo luật đọc khai trước, H3 = **LOOPING**: luật dấu hỏng ở τ ≈ T_int chỉ trên traffic liên tục, còn việc lặp trace che lỗi đi. Wave 3 PASS là do lặp trace; không phải do tải (nhánh H tải cao vẫn PASS khi lặp), cũng không phải do khác trace (cùng trace DITL).

## Đọc

1. **Trên trace lặp, luật bậc một gần như hoàn hảo** ở mọi tuổi và mọi tải:
   - đúng 99–100% về dấu;
   - tỷ lệ phần tăng thực/dự đoán trung vị 1,0–1,2.
2. **Trên trace liên tục, luật chỉ đúng ở hai đầu**:

   | r = τ/T_int | 0,1 | 0,3 | 0,5 | 0,8 | 1 | 1,2 | 2,5 | 5 |
   |---|---|---|---|---|---|---|---|---|
   | Dấu phần tăng (C) | 23/25 | 17/24 | 12/24 | 12/28 | 15/27 | 18/28 | 26/31 | 31/36 |
   | Sau lọc nhiễu (mô tả) | 10/10 | 11/12 | 10/13 | 9/16 | 8/10 | 13/17 | 20/22 | 30/30 |
   | Tỷ lệ phần tăng trung vị | 1,32 | 1,33 | 0,21 | −0,25 | 0,14 | 0,43 | 1,16 | 1,18 |

   - Ở dải giữa (r ≈ 0,5–1,2), hệ số dốc của luật sai hẳn.
   - Lọc nhiễu (bỏ các hàng có phần tăng nhỏ hơn 2 se) nâng nhóm low lên 88,6% (31/35) và nhóm band lên 69,8% (30/43). Lọc nhiễu không đổi verdict khai trước. Nó cho thấy một phần lỗi ở r ≤ 0,5 là hàng có hiệu ứng nhỏ, còn lỗi ở band vẫn là lỗi thật.
3. **T12 trên trace liên tục** (post-hoc, `posthoc.json`):
   - đứng khi τ ≤ 1,2·T_int: **235/240**, tái lập EV-D4b (237/240 với τ ≤ 2,7·T_int);
   - hỏng khi τ ≥ 2,5·T_int: **44/80** (31/40 và 13/40). Ở đó lợi ích của state tươi đối với twin plug-in vẫn tăng theo giá trị tuyệt đối từ 10T lên 30T (trung vị phần tăng +0,42 và +0,67 điểm % E_stay). Đây là **lợi**, không phải hại: trung vị G là +2,0…+2,7% ở 10T và +1,0…+1,5% ở 30T.
4. **Cách đọc thống nhất (giả thuyết, chưa kiểm riêng).**
   - Phần dư của khai triển bậc một giảm theo mode chậm nhất của traffic (γ ở Mệnh đề 1).
   - Traffic liên tục 4 giờ có thành phần chậm hơn T_int rất nhiều. Đoạn lặp 15 phút cắt mất chúng và làm tương quan tuần hoàn.
   - Khi telemetry cũ cỡ T_int hoặc hơn, twin bỏ lỡ chính các thành phần chậm này, nên ở 30·T_int vẫn chưa đạt vùng tiệm cận.
   - Giả thuyết này hợp với cả H2 (luật dấu) lẫn D6 ở τ lớn (T12), nhưng chưa có test phân biệt với giả thuyết khác.

## Hệ quả cho claim và paper

- **T12** (plug-in không có hại tăng theo h): giữ cho τ ≲ T_int trên traffic thật. Ghi rõ điều kiện "h dài so với thành phần chậm nhất".
- **Luật dấu cho twin nowcast trên trace thật**: chỉ đứng ở τ rất nhỏ và τ ≥ 2,5·T_int. Phải viết là giới hạn, kèm nguyên nhân đã xác định: lặp trace che lỗi; traffic liên tục có thành phần chậm.
- **Kết quả wave 3** (trace lặp) không được dùng làm bằng chứng cho traffic liên tục.

## Giới hạn

- Một trace DITL, một khung giờ, một đoạn lặp (10:00).
- Các hàng tương quan mạnh: cùng seed cho hai h và hai twin; C và L dùng chung regime.
- Phân tích theo r và phần lọc nhiễu là post-hoc.
- AI tự thiết kế và chấm. Không có review của người.
