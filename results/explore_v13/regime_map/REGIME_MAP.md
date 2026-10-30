# Bản đồ regime: khi nào sửa state, khi nào sửa model (nhánh `explore/v13-regime-map`, 29–30/10/2026)

Người phụ trách: **Doan Van Tai**. AI (Claude) tự thiết kế, chạy và viết theo ủy quyền trực tiếp
("tự thiết kế và chạy tiếp… không cần viết trước hay dự đoán"; "có thể thay đổi age… tự thực hiện").

Nhãn **EXPLORATION / DISCOVERY**:
- Không có prereg, không có dự đoán viết trước, không phải bằng chứng xác nhận.
- Mọi regime ở đây thành dữ liệu đã thấy.
- Không regime nào nằm trong hộp card Phase 3R (MV/SH, frozen 1414d92) được tính trên nhánh này. Bộ lọc
  bỏ qua `age`/`amp` nên loại cả các biến thể age/amp của tọa độ card.
- 88 điểm "rỗng" trên hình là regime pilot cũ (đợt 2, đã lộ từ trước), không phải dữ liệu mới.
- Không dùng ô lưới v1.2, ô R hay R09/R10.

Câu chuyện cần kiểm: *"Không có repair nào luôn tốt hơn. Giá trị của state information và model
fidelity phụ thuộc vào operating regime."*

## Đã chạy

| Đợt | Regime | Nội dung |
|---|---|---|
| map1 | 344 | Lưới thô đủ tổ hợp: λA {6,5; 7,5; 8,5} × λB {6; 7; 8; 8,5} × κ {0,1; 0,3; 1; 3} × η {¼; ½; ¾} × h {2; 4; 8} |
| map1robustK / map1robustdt | 8 + 8 | 8 regime đại diện, chạy với K = 80 và dt = 1/240 |
| map2 | 576 | Lưới mịn. XM2S (360): vùng state thắng, h 1–4, κ 0,2–1, η đến ⅞. XM2X (216): vùng thay thế/gây hại, κ 0,05–0,15, h 4–8 |
| map3age | 216 | **Age** (độ cũ của quan sát) ∈ {¼; ½; 2; 4} s. Mốc age 1 lấy từ map1 |
| map4amp | 126 | **Biên độ nền ON/OFF** ±4, ±5, ±7 (plant gốc ±6), age 1 |
| plantrobust | 12 | 6 regime age/amp đại diện, chạy với K = 80 và dt = 1/240 |

Tổng cộng **1376 regime khác nhau** (gộp pilot đợt 1–2), tất cả có c_sw = 0.

**`age` và `amp` là mở rộng plant chỉ dùng cho exploration.** Plant hợp đồng là age 1 s, ±6. Hai tham số
này nằm trong bản sao cục bộ `queue_D`/`law` ở `experiments/explore_v13/population.py`; không sửa `src/`.
Bản sao được kiểm như sau:
- ở age 1, ±6 trùng **từng bit** với `smr.cells.queue_D`;
- `evaluate` tái tạo chính xác một dòng map1;
- 18 regime map2 trùng tọa độ map1 khớp chính xác (`tests/test_explore_v13.py`, 24 test).

## Cách phân nhóm

Ngưỡng ε_R = 1% C̄_ref. Đây là công cụ đọc, không phải test.

| Nhóm | Điều kiện | Nghĩa |
|---|---|---|
| **A** · state thắng | Ḡ_S ≥ 1, Ḡ_M < 1 | Đáng sửa state, không đáng sửa model |
| **B** · model thắng | Ḡ_M ≥ 1, −1 < Ḡ_S < 1 | Ngược lại |
| **AB** · cả hai | Ḡ_S ≥ 1, Ḡ_M ≥ 1 | Hầu hết là **thay thế** (Γ̄ < 0) |
| **J** · cộng hưởng | Ḡ_S, Ḡ_M < 1, G_SM ≥ 1, Γ̄ ≥ max(Ḡ_S, Ḡ_M) | Riêng lẻ gần vô dụng, chỉ làm cùng lúc mới có ích |
| **C** · state gây hại | Ḡ_S ≤ −1 | State tươi cộng model mean-field làm quyết định tệ hơn |
| **D** · không đáng kể | còn lại | |

Hai đồng nhất thức dùng để đọc:
- **Γ̄ = Ḡ_S|M1 − Ḡ_S**, khớp chính xác (sai khác 0) trên 1376 regime.
- **Ḡ_M, Ḡ_S|M1, G_SM ≥ 0** (min ≥ −2·10⁻¹⁵). Với model thật, quyết định đã tối ưu Bayes theo thông tin
  đang có, nên **không tồn tại vùng "model gây hại"**. Chỉ state mới gây hại được, và chỉ khi model sai.

## Kết quả

Số regime theo nhóm, sau khi bỏ trùng: A 301 · B 43 · AB 161 · J 14 · C 334 · D 523.

1. **Không repair nào luôn thắng.** Cả 4 vùng bạn yêu cầu đều có và tách nhau rõ trong tọa độ thiết kế.
   Ngoài ra có thêm 2 kiểu: thay thế và cộng hưởng.
2. **Age là núm "state uncertainty" đúng nghĩa.**
   - Ḡ_S|M1 (giá trị state khi model đúng) không giảm theo age ở **54/54** cấu hình. Giá trị lớn nhất:
     1,4 → 2,1 → 3,1 → 4,3 → 5,0% C̄ khi age = ¼ → ½ → 1 → 2 → 4 s. Điều này khớp lý thuyết: quan sát cũ
     là bản "làm nhiễu" của quan sát mới, nên giá trị thông tin của state tươi tăng.
   - Nhóm đổi theo age (54 cấu hình): D 30 → 9, A 4 → 23, B 8 → 0.
3. **A · state thắng**: h ngắn (1–4 s), κ 0,2–1, η ≥ ½, λB 7–7,5 (λA 6–7,5).
   - Lớn nhất ở age 1: XM2S189 (λA 6,5, λB 7, κ 0,2, η ⅞, h 2), Ḡ_S +4,0% C̄ (34% stakes), Ḡ_M 0,6.
   - Lớn nhất ở age 4: XA087 (λA 7,5, λB 8, κ 0,1, η ¾, h 2), Ḡ_S +4,7% C̄ (38% stakes), Ḡ_M 0,00.
   - Hiệu ứng thật nhưng **khiêm tốn: ≤ 5% C̄**.
4. **B · model thắng**: κ ≤ 0,3, h ≥ 4–8, λB 7–8, quan sát mới (age ≤ 1). Ví dụ XM1224, Ḡ_M 5,85.
   Pilot trong hộp card có X2065, Ḡ_M 13,4. **Khi age tăng, B chuyển thành AB.**
5. **AB · thay thế**: 155/161 regime AB có Γ̄ < 0, và 53 regime gần thay thế hoàn toàn
   (Γ̄ ≈ −min(Ḡ_S, Ḡ_M)). Vùng này ở λA 6–6,75, λB 6,5–7, κ ≤ 0,1, η ≥ ¾, h 4–8.
   - Mạnh nhất: XM2X077 (λA 6,25, λB 7, κ 0,05, η ⅞, h 8). Sửa state +20,4%, sửa model +37,8%,
     sửa cả hai +37,8%, Ḡ_S|M1 = 0.
   - Nghĩa là state tươi chỉ **làm nạng cho model sai**: Ḡ_S lớn nhưng Ḡ_S|M1 ≈ 0. Trên bản đồ
     Ḡ_S × Ḡ_M nó giống "state có ích"; hình cơ chế tách được hai loại.
   - Thay thế mạnh dần theo age (min Γ̄ −1,0 → −9,3) và khi nền nhỏ hơn.
6. **J · cộng hưởng (Γ̄ > 0 thật)**: chỉ có **14 regime, nhỏ**: G_SM 1,05–2,1%, Γ̄ ≤ 1,8%.
   - Vị trí: λA 6–6,5, λB 7,5–8, κ 0,2–0,3, η ¾–⅞, h 2–4. Đây là dải chuyển tiếp giữa C và A.
   - Ví dụ XM2S069: sửa state +0,48, sửa model +0,10, sửa cả hai +1,70.
   - Cơ chế: với model sai, state tươi hơi hại; với model đúng, state có ích (Ḡ_S|M1 ≈ 1,2). Phải sửa model
     trước thì sửa state mới có lợi.
   - Trần cấu trúc: khi Ḡ_S ≥ 0 thì Γ̄ ≤ Ḡ_S|M1, mà Ḡ_S|M1 ≤ 5,3% trên toàn bộ dữ liệu.
7. **C · state gây hại**: λB cao so với λA (7,5–8,5), κ ≤ 0,1–0,3, h 4–8.
   - Tệ nhất: XM2X041 (λA 6, λB 7,5, κ 0,05, η ⅞, h 8), Ḡ_S −34,9% C̄, Ḡ_M 0, G_SM 0.
   - Pipeline cũ (state cũ + M0) đã chọn đúng; đưa state tươi cho M0 làm hỏng. Ḡ_S|M1 ≈ 0.
   - **Không phụ thuộc age**: là hiện tượng của model sai, không phải của state cũ.
8. **D · không đáng kể**: κ = 3 luôn rơi vào D (mode quên nhanh so với h); κ = 1 với λB 8; phần lớn η = ¼.
9. **Biên độ nền nhỏ (±4)** làm mọi hiệu ứng tính theo % C̄ lớn lên (tới Ḡ_M 35%, Ḡ_S −44%, Γ̄ −17).
   Nhưng **phần lớn là do C̄_ref nhỏ đi**: trung vị C̄(±4)/C̄(±6) = 0,32. Tính tuyệt đối, Ḡ_M|S1 chỉ tăng
   khoảng 15% (trung vị). Biên độ không phải núm "model error" sạch, vì nó dịch cả hai trục.

## Độ bền

- **map1, 8 regime đại diện (một hoặc hơn mỗi nhóm A/B/AB/D):** cả 8 giữ nguyên nhóm.
  Thay đổi lớn nhất: 0,12 pp với K = 80, 0,28 pp với dt = 1/240.
- **plantrobust (age/amp, 6 regime đại diện):** 12/12 giữ nguyên nhóm. Thay đổi lớn nhất 0,19 pp
  (C ở age 4 khi dt = 1/240).
- **jointrobust (3 regime J):** 6/6 vẫn là J. G_SM lệch ≤ 0,02 pp, Γ̄ lệch ≤ 0,03 pp.
- **Chưa kiểm độ bền:** nhóm B ở age ≠ 1, và các regime map2 ở h = 1.

| Kiểm | Regime gốc | Plant | Thay đổi | Ḡ_S | Ḡ_M | Γ̄ | Nhóm | Lệch tối đa (pp) |
|---|---|---|---|---|---|---|---|---|
| XPR0K | XA087 | age 4, ±6 | K = 80 | +4,67 → +4,66 | 0,00 → 0,00 | +0,29 → +0,28 | A → A | 0,015 |
| XPR0D | XA087 | age 4, ±6 | dt = 1/240 | +4,67 → +4,65 | 0,00 → 0,00 | +0,29 → +0,29 | A → A | 0,025 |
| XPR1K | XA039 | age 4, ±6 | K = 80 | +3,97 → +3,96 | 0,01 → 0,01 | +0,05 → +0,05 | A → A | 0,015 |
| XPR1D | XA039 | age 4, ±6 | dt = 1/240 | +3,97 → +3,95 | 0,01 → 0,01 | +0,05 → +0,05 | A → A | 0,022 |
| XPR2K | XA022 | age 2, ±6 | K = 80 | +9,43 → +9,43 | 16,21 → 16,20 | −9,28 → −9,27 | AB → AB | 0,012 |
| XPR2D | XA022 | age 2, ±6 | dt = 1/240 | +9,43 → +9,36 | 16,21 → 16,22 | −9,28 → −9,21 | AB → AB | 0,076 |
| XPR3K | XA167 | age 4, ±6 | K = 80 | −20,85 → −20,85 | 0,00 → 0,00 | +20,86 → +20,85 | C → C | 0,002 |
| XPR3D | XA167 | age 4, ±6 | dt = 1/240 | −20,85 → −21,04 | 0,00 → 0,00 | +20,86 → +21,04 | C → C | 0,186 |
| XPR4K | XB069 | age 1, ±4 | K = 80 | +17,23 → +17,19 | 35,47 → 35,40 | −16,90 → −16,86 | AB → AB | 0,069 |
| XPR4D | XB069 | age 1, ±4 | dt = 1/240 | +17,23 → +17,05 | 35,47 → 35,46 | −16,90 → −16,72 | AB → AB | 0,178 |
| XPR5K | XB045 | age 1, ±4 | K = 80 | +4,25 → +4,23 | 0,00 → 0,00 | +0,03 → +0,03 | A → A | 0,019 |
| XPR5D | XB045 | age 1, ±4 | dt = 1/240 | +4,25 → +4,23 | 0,00 → 0,00 | +0,03 → +0,03 | A → A | 0,023 |

## Đánh giá: **TỐT** (mức exploration)

**Đạt:**
- Đủ 4 vùng A/B/C/D, cộng thêm thay thế và cộng hưởng.
- Vùng có cấu trúc rõ trong tọa độ thiết kế: age × h × η × κ × λ.
- Age cho hiệu ứng đơn điệu đúng lý thuyết (54/54).
- Có đồng nhất thức giải thích vì sao C và AB thường đi với Γ̄ lớn.
- Bền theo K và dt ở các điểm đã kiểm.

**Chưa lên RẤT TỐT vì:**
1. State thắng chỉ ≤ 5% C̄, cộng hưởng ≤ 2,1%.
2. Toàn bộ là discovery, chưa có luật dự báo a priori nào được kiểm ngoài mẫu.
3. `age`/`amp` nằm ngoài plant hợp đồng.
4. Các vùng thú vị cần κ ≤ 0,3 (mode nhớ lâu) và λB gần bão hòa, nên tính thực tế (Phase 8 / L3R.4) còn mở.
5. Không có người thật đọc.

**Hàm ý cho bài:**
- Câu "không repair nào luôn thắng" đứng được trên dữ liệu discovery.
- Trục "state uncertainty" nên là **age** (hoặc tương đương), không phải κ/η.
- Nên báo cả Ḡ_S lẫn Ḡ_S|M1 để tách "state có giá trị thật" khỏi "state làm nạng".
- Muốn dùng làm claim phải prereg và kiểm trên mẫu regime mới. Tác giả quyết.

## Sự cố khi chạy (ghi đúng như đã xảy ra)

1. **map2 lần đầu** (6 nhân, giới hạn 58 phút, chỉ ghi file ở cuối) bị dừng ở phút ~60 khi VS Code khởi động
   lại. Không lưu được regime nào.
2. **Lệnh chạy lại map2 lúc 23:55 bị tác giả từ chối nhưng vẫn khởi động** (tiến trình 264119). AI không biết
   và không kiểm lại.
   - Nó chạy song song với map3age khoảng 2 giờ, 16 worker trên 10 nhân, nên map3age mất 86 phút.
   - Lúc 01:51 bản map2 xếp hàng sau map3age/map4amp khởi động, thành hai bản cùng ghi một thư mục.
   - AI dừng cả hai, giữ 460 checkpoint, rồi chạy một bản duy nhất cho 116 regime còn lại.
   - Dòng do code cũ (trước `age`/`amp`) ghi được điền age = 1, amp = 6 (`with_plant_columns`).
   - Kiểm chéo 18 regime trùng map1: 0 sai khác.
3. WSL khởi động lại lúc 07:50 ngày 30/10 khi plantrobust đang ở 10/12. Phần còn lại chạy tiếp bằng `--resume`.
4. Nhật ký chạy: `results/explore_v13/logs/`.
   - `map2_first_run.log`: bản bị từ chối nhưng vẫn chạy.
   - `map2_second_stopped.log`: bản xếp hàng, bị dừng.
   - `map2_resume.log`: bản chạy nốt.

## Tệp

Hình:
- [regime_map_differ.png](regime_map_differ.png): bản đồ Ḡ_S × Ḡ_M, vùng A/B/AB/C/D/J.
- [regime_map_mechanism.png](regime_map_mechanism.png): Ḡ_S|M1 × Ḡ_M|S1.
- [regime_design_age.png](regime_design_age.png): tọa độ thiết kế, age × h, η.
- [regime_design_amp.png](regime_design_amp.png): biên độ nền × h, η.
- [regime_composition_map1.png](regime_composition_map1.png): tỷ lệ nhóm theo trục, chỉ map1.

Bảng: [regime_map_table.csv](regime_map_table.csv), 1376 dòng, cũng là bản đọc bằng bảng cho hình.

Code:
- `experiments/explore_v13/{population,scan,regime_map,plot_map}.py`
- `tests/test_explore_v13.py`

Dữ liệu: `results/explore_v13/<đợt>/{specs.json, regimes.csv, pairs.npz, status.json}`.

Mã màu: chỉ 3 màu đã kiểm all-pairs (xanh dương / cam / xanh ngọc) cộng mực đậm và hai mức xám. Mọi
nhóm có marker hoặc chữ riêng. Không có màu thứ tư nào qua kiểm all-pairs.
