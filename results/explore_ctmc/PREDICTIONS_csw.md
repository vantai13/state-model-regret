# Dự đoán Stage F: switching cost c_sw > 0 trong CTMC (khóa trước khi chạy truth của Stage F)

Doan Van Tai — **AI (Claude) soạn theo ủy quyền L7.1**, exploration, không phải author-self, không phải claim.
Ghi ngày 03/11/2026, sau khi đã đọc Stage D (điểm chấm bridge/asymptote) và Stage E (khám phá rộng), trước mọi
dòng truth có c > 0. Bộ chấm: [check_csw.py](../../experiments/explore_ctmc/check_csw.py). Số zero-fit đóng băng:
[PREDICTIONS_csw_numbers.csv](PREDICTIONS_csw_numbers.csv) (`--mode m0`, chỉ M0 và đại lượng dừng, có c).

## Câu hỏi

Đây là bản CTMC của nhánh D(ii) Phase 6. M0 mù horizon, nên c làm đổi quyết định của M0 ở thang O(1) ở mọi h,
còn stake của truth h·s + c bị h·s chi phối. Giới hạn zero-fit không phụ thuộc h:
z_∞(c) = 100·s·(F_old(c) − F_new(c))/r_min.

## Thiết kế (đã chọn trước truth, chỉ từ M0)

6 base trong dải giúp (x = 1/20 hoặc 1/10; [stage_f_design.json](stage_f_design.json)). Mỗi base chọn c* trên lưới
1/8…6 để z_∞(c) âm nhất (hòa → c nhỏ hơn), giống cách Phase 6 chọn c tại đỉnh |z| dự đoán. Mỗi base có hai case: c* và
c = 0 (twin). Horizon: h/T_int ∈ {1/3, 1, 3, 10, 30} và h/κ ∈ {80, 160} (hai tỷ lệ của Phase 6).

**Điều đã thấy trước khi viết (chỉ M0):** khi c tăng, F_old và F_new cùng giảm và tiến sát nhau, không vượt qua
nhau như ở fluid. z_∞(c*) chỉ còn −0,089 đến +0,205 (c = 0: +0,17 đến +1,71). Khai triển bậc một ở h = T_int cho z
dương (0,7–1,4) ở cả 6 case c*. **Exposure:** truth c = 0 ở h/κ = 50/150 của ba base (7, 71/10, 1, 1/5), (7, 71/10, 1, 1)
và (13/2, 67/10, 2, 1/5) đã có trong xslice. Stage D cho thấy khai triển bậc một chỉ đáng tin từ h/T_int ≈ 3 (AS-R1).

## Dự đoán

| ID | Nhãn | Điều kiện | Dự đoán (ngưỡng) |
|---|---|---|---|
| F-T1 | toán | dòng h/T_int ≈ 30 | \|z − z_∞(c)\| ≤ 0,1 + 0,1·\|z_∞(c)\| ở mọi case |
| F-R1 | rủi ro (onset có c) | dòng h/T_int ≥ 3 | \|z − z_pred1\| ≤ 0,1 pp ở ≥ 90% dòng |
| F-R2 | rủi ro (không có harm) | mọi dòng của 6 case c* | G_S ≥ −0,25% ở ≥ 90% dòng |
| F-R3 | rủi ro (mẫu dấu Phase 6) | case c*, dòng h/T_int < 3 | G_S > 0 ở ≥ 70% dòng |
| F-R4 | toán + onset | cặp (c*, c = 0) cùng base, cùng h, h/T_int ≥ 3 | G_S(c*) < G_S(0) ở ≥ 90% cặp |
| F-R5 | rủi ro (can thiệp có c) | mọi dòng có G_S < −0,1% | G_S^hybrid ≥ −0,1% ở ≥ 95% dòng (INCONCLUSIVE nếu không có dòng nào) |

## Ý nghĩa từng kết cục

- F-R2 và F-R3 đạt → trong CTMC, switching cost không tạo ra harm của state tươi đối với M0, và ở horizon vừa
  state tươi vẫn giúp. Cơ chế D(ii) của Phase 6 phụ thuộc representation (posterior hẹp của fluid).
- F-R2 trượt → c vẫn tạo harm ở horizon hữu hạn dù z_∞(c) ≈ 0; phần bị chặn B/h quyết định dấu.
- F-R1 trượt → khai triển bậc một kém hơn khi có c (c đẩy quyết định M0 về gần hòa).
- F-T1 trượt → bug ở đường c > 0; dừng.
