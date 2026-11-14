# External validity — Wave 3 report (EV-D3a/b: realistic telemetry age on two real MAWI traces), 14/11/2026

Doan Van Tai — **AI (Claude) điều phối và chạy, theo ủy quyền** ("tiếp tục làm đi"). Các thẻ `LOCKED_AI_DELEGATED`. Test
chạy song song trên VM GCP (12 vCPU) và máy tác giả. Nhánh `ext/validity`, không merge main.

## Câu hỏi

Wave 2 (EV-D2) thấy hiệu ứng ≈ 0 ở τ = 1 s, vì τ ≪ T_int của traffic thật. Telemetry thực tế thường cũ 30 s đến 5 phút
(SNMP). Với τ ∈ {30, 300} s trên traffic thật:
- telemetry tươi có làm hại twin không?
- luật zero-fit (chỉ từ seed train) có dự đoán đúng không?
- T12 (plug-in không bị hại) có còn đứng không?

## Kết quả (thẻ khóa trước seed test; D1–D4 giống hệt EV-D/EV-D2)

| | EV-D3a: MAWI 2025-03-11 (215,7 triệu gói) | EV-D3b: MAWI 2026-04-14 (381,3 triệu gói) |
|---|---|---|
| T_int (train, trung vị) | 72 s | 40 s |
| **D1** plug-in không harm | **PASS** 78/80 | **FAIL** 54/80 (τ = 300: plug-in harm 13/20, trung vị −0,58%) |
| **D2** dấu harm của twin nowcast theo luật | **PASS** 54/56 | **PASS** 66/68 |
| D3 độ lớn | FAIL 39/80 | FAIL 62/80 (sát 80%) |
| D4 hybrid xóa harm | FAIL 47/80 | FAIL 64/80 |
| Harm của twin nowcast (trung vị, 30 T_int) | −0,6% (τ = 30) / −1,2% (τ = 300) | **−1,6% / −4,1%** |
| Twin plug-in (trung vị) | +0,1 / +0,3% (state tươi giúp) | +0,2% / −0,6% |

## Đọc

1. **Phát hiện thực tế chính.** Với tuổi telemetry thực tế trên traffic backbone thật, twin nowcast (ước lượng state hiện tại từ dữ liệu cũ, kiểu bộ lọc) bị telemetry tươi làm hại tới vài phần trăm chi phí.
   - Luật zero-fit dự đoán đúng **dấu** ở 120/124 ô có hiệu ứng đáng kể trên hai trace.
   - **Độ lớn** chỉ đúng tới khoảng ±40–60% (D3 FAIL).
2. **Hybrid (thêm số hạng dài hạn h·ŝ) không đủ** khi telemetry rất cũ.
   - Kiểm tra sau mở trên trace 1: ŝ ước lượng chính xác (lệch 5% so với lần chạy dài gấp 10). Lỗi vì vậy không nằm ở ŝ.
   - Harm còn lại xảy ra ở regime |s| vừa phải. Twin tươi phản ứng với số hạng transient của fluid ở các backlog rất lớn, mà fluid mô hình hóa sai. Twin cũ (τ = 300 s) gần như là chính sách tĩnh.
   - **Khuyến nghị "hybrid" phải thu hẹp:** chỉ đủ khi sai số transient của model nhỏ.
3. **T12 có thêm điều kiện phạm vi** (D1 FAIL ở trace 2).
   - Giả định "cùng phân phối" vẫn đúng: twin plug-in có F_old = F_new trong train.
   - Giả định "trộn" bị vi phạm: trace 2 có biến động theo phút mạnh (trung bình từng phút 0,63–1,77×), và trace bị lặp mỗi 15 phút. T_int đo theo điểm cắt 0 đầu tiên chỉ bắt thành phần nhanh.
   - Ở h ≈ 20 phút, thành phần chậm chưa trộn, nên ngay cả twin plug-in cũng có thể bị hại khi τ = 5 phút.
   - **Câu đúng:** T12 cần h vượt xa thang tương quan **chậm nhất** của traffic.

## Sai lệch và lỗi

- **Tải trace 2:** lần đầu qua pipe bị treo 54 phút (0 byte). `pkill` của Claude cắt luôn phiên SSH của chính nó. Tải lại về đĩa có resume thì thành công.
- **Panel EV-D3b:** lần train đầu sai đường dẫn chuỗi, do sót khi sao chép script; không có output và đã chạy lại.
- **EV-D3a:** chỉ dùng trace 1, vì trace 2 về muộn. EV-D3b là lần lặp lại độc lập trên regime mới.
- **Phân tích sau khi chấm** (kiểm ŝ, phân tích D1): ghi riêng, không đổi verdict.

## Giới hạn

- Mỗi trace chỉ dài 15 phút, nên bị lặp, và thành phần chậm thành tuần hoàn.
- Chỉ giữ cấu trúc tốc độ, không giữ phụ thuộc mức gói.
- Twin nowcast là hồi quy tuyến tính. Chỉ có hai mức τ.
- AI tự thiết kế và chấm. Không novelty claim.

## Việc tiếp (đề xuất)

1. Trace dài hàng giờ (MAWI 24 h hoặc nguồn khác) để tách hẳn thành phần chậm khỏi tác động của việc lặp trace. Nên làm trước khi viết claim thực tế.
2. Đổi T_int "nhanh" thành thang tương quan chậm nhất trong luật, rồi kiểm lại D1/D3. Đây là mở rộng lý thuyết.
3. Twin có model transient tốt hơn: kiểm xem hybrid + model transient có xóa được harm ở τ lớn không.
4. Phần của tác giả: tự kiểm T12 (nay có thêm điều kiện thang chậm), quyết khuyến nghị nào đưa vào paper.

## Đính chính sau audit độc lập (14/11/2026, DL-146)

Verdict D1–D4 của cả hai trace được tính lại độc lập và đều khớp. Cách diễn giải phải sửa theo `notes/ops/codex/AUDIT_report.md`:

1. **"120/124 đúng dấu" chỉ là phép đếm trên các hàng có |dự đoán| ≥ 0,25 pp**, không phải kiểm định thống kê.
   - Các hàng tương quan rất mạnh: hai twin nowcast có tương quan 0,9996–0,9999; h = 10T và h = 30T dùng cùng seed.
   - SE trong một lần chạy không gồm sai số của train và của pha trace.
2. **"Độ lớn ±40–60%" không có mẫu số.** Thay bằng: trên các hàng được chọn ở h = 30T, trung vị |G − dự đoán|/|dự đoán| là 42% (trace 1) và 19% (trace 2); tối đa 347% và 106%.
3. **"Hybrid FAIL không do ŝ" chưa được chứng minh.** Lệch trung vị của ŝ là 5,1%, nhưng tối đa tới 148%. Muốn khẳng định cần đối chứng: thay ŝ bằng giá trị chuẩn trên cùng đường đi traffic.
4. **Bỏ cách giải thích D1 FAIL ở trace 2 bằng "thang trộn chậm".** Có hai lý do:
   - Trace 1 cũng dao động theo phút (0,69–2,86×).
   - Có một lỗi thiết kế lớn hơn (audit B3): hai đường A và B lặp **cùng** một chuỗi với hai pha độc lập, nên độ lệch pha A–B cố định trong cả lần chạy và ngẫu nhiên giữa các lần (train khác test). Nguồn sai số này chưa được định lượng.

   EV-D4 sửa lỗi này: A và B dùng hai mẫu luồng khác nhau, chung một pha thời gian thật, trên trace 4 giờ.
5. **T12:** xem đính chính trong `notes/theory/T12_plugin_stationarity.md`. D1 FAIL không bác T12, và D1 PASS cũng không chứng minh T12.
