# Kiểm độc lập hai ô A04

Người phụ trách: **Doan Van Tai** · 27/10/2026.

Reviewer là **một phiên AI độc lập**, không phải GVHD/người đọc thật. Phiên này chưa xem `card_scores.*`, `card_details.csv` hoặc kết quả grader; không đọc ô khác, không chạy engine và không đọc held-out.

Phạm vi: chỉ M09/P2 và M17/P6 đã chỉ định trước. Không suy rộng verdict toàn bộ P2/P6, không tìm pattern và không xác nhận mechanism.

## Phép tính độc lập

Chỉ đọc prediction card và bốn raw record. Dùng `Fraction` trên chuỗi decimal raw, không import grading/score_card. Với A−B: [aL−bU,aU−bL]; lấy abs interval rồi kiểm upper ≤ Cref_fine.lower/400. Ratio dùng min/max của bốn corner. Kiểm không có cặp dấu đối nhau có thể xảy ra ngoài ±1/200 của Cref mỗi mức. P2 lấy L01−L10 trước propagation; P6 kiểm V>0 và (V−F)>0 theo strict inequality rồi Kleene AND.

Các khoảng dưới là numeric enclosures của slot model, không phải CI, không chứng minh giới hạn dt→0. Số hiển thị được làm tròn ra ngoài đến 18 chữ số thập phân; JSON giữ phân số chính xác. Không thay e_num thực bằng budget.

## Numeric gate và cặp dt

Bốn raw đều BOUNDED, numeric_budget_met=true; unresolved_mass oracle/M0/D22 đều 0. Đã kiểm Cref=L11 cùng interval/context; nominal±e_num thực nằm trong enclosure cho L00/L01/L10/L11/Lcb0, sáu contrast, F/V/Cref. Cờ budget được lấy từ raw: card không định nghĩa công thức budget nội bộ nên review này không tái tính công thức đó.

| Ô | dt coarse → fine (s) | 0.0025 × Cref_fine.lower | Sáu contrast |
|---|---|---:|---|
| M09 | 1/120 → 1/240 | 0.186111004615889625 | PASS 6/6 |
| M17 | 1/120 → 1/240 | 0.568260192803889750 | PASS 6/6 |

### M09: sáu contrast

| Contrast | Khoảng abs(fine−coarse) | Đổi dấu ngoài ±.005 có thể xảy ra? |
|---|---|---|
| G_S | [0.006638586815925500, 0.006638587075642200] | Không |
| G_M | [0E-18, 1.27335235E-10] | Không |
| G_SM | [0.005494159801741100, 0.005494160057613700] | Không |
| G_S_M1 | [0.005494159796071400, 0.005494160063283500] | Không |
| G_M_S1 | [0.001144426879977950, 0.001144427152234890] | Không |
| Gamma | [0.001144426752642700, 0.001144427279570070] | Không |

### M17: sáu contrast

| Contrast | Khoảng abs(fine−coarse) | Đổi dấu ngoài ±.005 có thể xảy ra? |
|---|---|---|
| G_S | [0.003895188689227100, 0.003895189020225700] | Không |
| G_M | [0E-18, 1.63564577E-10] | Không |
| G_SM | [0.003536732439008600, 0.003536732766536700] | Không |
| G_S_M1 | [0.003536732439008600, 0.003536732766536700] | Không |
| G_M_S1 | [0.000358456086256300, 0.000358456417651300] | Không |
| Gamma | [0.000358455922691700, 0.000358456581215900] | Không |

## M09/P2

| dt (s) | L01−L10 | (L01−L10)/Cref | Nhãn ≥.01 |
|---|---|---|---|
| 1/120 | [0.625638306712020000, 0.625638306802430000] | [0.008398206186163181, 0.008398206187381842] | DOES_NOT_STAND |
| 1/240 | [0.618999719721060000, 0.618999719901800000] | [0.008314926366093392, 0.008314926368531241] | DOES_NOT_STAND |

Cả hai upper ratio đều <.01. Numeric gate và pair đều đạt; verdict tại dt_final=1/240 là **DOES_NOT_STAND**. Không nhạy với dt theo tiêu chí đổi nhãn của card. Đây là counterexample cho vế tại M09; review không đọc các ô K2 còn lại.

## M17/P6

| dt (s) | V | V−F | V>0 | V−F>0 | AND |
|---|---|---|---|---|---|
| 1/120 | [-0.398814364450711940, -0.398814364303463900] | [-2.491952396629889240, -2.491952396336720900] | DOES_NOT_STAND | DOES_NOT_STAND | DOES_NOT_STAND |
| 1/240 | [-0.402691023641875700, -0.402691023307203700] | [-2.495810526156884700, -2.495810525490080000] | DOES_NOT_STAND | DOES_NOT_STAND | DOES_NOT_STAND |

Upper(V) và upper(V−F) đều ≤0 ở hai mức. Numeric gate và pair đều đạt; verdict tại dt_final=1/240 là **DOES_NOT_STAND**. Không nhạy với dt theo tiêu chí đổi nhãn của card. Đây là counterexample tại M17; review không đọc M18. Không diễn giải V thành lợi ích chỉ refresh backlog.

## Số đếm trong phạm vi hai ô

Tại fine: M09/P2 có STANDS=0, DOES_NOT_STAND=1, UNRESOLVED=0, EXCLUDED_ZERO_REFERENCE=0. M17/P6 mỗi vế V>0 và V−F>0 có STANDS=0, DOES_NOT_STAND=1, UNRESOLVED=0, EXCLUDED_ZERO_REFERENCE=0; AND cũng DOES_NOT_STAND. Hai nhãn ô cuối: 0 đứng, 2 không đứng, 0 chưa phân giải, 0 excluded. Đây không phải bảng đếm toàn bộ card.

## Thực thi và giới hạn

Đã chạy `python3 results/lessons/l3_5/independent_review.py`; không chạy test suite/engine/simulation. Lần đọc thử ban đầu bằng `python` thất bại vì shell không có lệnh đó; đã dùng `python3`. Lần chạy script đầu gặp SyntaxError tại biểu thức abs interval do thiếu dấu ngoặc; đã sửa cú pháp và chạy lại. Script assert tính đúng thứ tự interval, reference context và viết kết quả; dữ liệu từng kiểm được lưu trong JSON. Phép tính độc lập trên raw không phải validation độc lập của thuật toán sinh enclosure. Không có seed mới, không tạo data thí nghiệm mới, không mở Phase4/Gate người thật và không nhận mechanism đúng.

Files: `results/lessons/l3_5/independent_review.py`, `independent_review.json`, `independent_review.md`. Không tạo log riêng; stdout được ghi trong báo cáo chạy của phiên. SHA256 của đúng năm input và script nằm trong JSON.
