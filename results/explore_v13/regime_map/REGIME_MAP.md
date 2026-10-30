# Bản đồ regime: khi nào sửa state, khi nào sửa model (nhánh `explore/v13-regime-map`, 29–30/10/2026)

Người phụ trách: **Doan Van Tai**. AI (Claude) tự thiết kế, chạy và viết theo ủy quyền trực tiếp
("tự thiết kế và chạy tiếp… không cần viết trước hay dự đoán"; "có thể thay đổi age… tự thực hiện";
"sửa các lỗi trong regime_map bạn mắc").

Nhãn **EXPLORATION / DISCOVERY**:
- Không có prereg, không có dự đoán viết trước, không phải bằng chứng xác nhận.
- Mọi regime ở đây thành dữ liệu đã thấy.
- Không dùng ô lưới v1.2, ô R hay R09/R10.
- **10 regime map3age nằm trong hộp card Hyp-MV khi quy về age 1** (xem Errata E3).

Câu chuyện cần kiểm: *"Không có repair nào luôn tốt hơn. Giá trị của state information và model
fidelity phụ thuộc vào operating regime."*

## Errata 30/10/2026 (sau review của một phiên AI khác, AI kiểm lại từng điểm)

Bản đầu (`050b419`) có các lỗi dưới đây. Tất cả là lỗi diễn giải hoặc lỗi bộ lọc. **Không có số nào do
engine tính bị sai, nên không chạy lại engine.** Bảng và hình được vẽ lại từ các `regimes.csv` có sẵn.

| # | Bản đầu viết | Đúng là |
|---|---|---|
| E1 | κ là "tốc độ đổi mode": "κ ≤ 0,3: mode nhớ lâu", "κ = 3: mode quên nhanh" | **κ là thời gian một mode kéo dài (s)**: `r2_keep(dt, κ)` giữ mode với xác suất (1 + e^(−2dt/κ))/2 mỗi slot. κ = 0,1 nghĩa là mode đổi khoảng mỗi 0,1 s, nên sau 1 s tuổi quan sát, quan sát cũ gần như không còn nói gì về mode. κ = 3 nghĩa là mode kéo dài khoảng 3 s, quan sát cũ vẫn gần đúng, nên rơi vào D. Card v1 dùng đúng nghĩa này. |
| E2 | "Age là núm/trục state uncertainty mới" | **Age không phải chiều mới.** Plant là fluid: nhân age, κ và h cùng một hệ số thì mọi % C̄ giữ nguyên (backlog và chi phí đổi theo tỷ lệ). Regime (age a, κ, h) ≡ (age 1, κ/a, h/a). Kiểm trên dữ liệu: **18 cặp tương đương, 18/18 cùng nhóm, lệch ≤ 0,20 pp** (XA022 ≡ XM2X128: Ḡ_S 9,43 so với 9,58). Age chỉ có giá trị *diễn giải*: "chỉ đổi thông tin, giữ nguyên thế giới" (L̄10, L̄11 không phụ thuộc age; trên dữ liệu lệch ≤ 0,7% do cầu phương). Biên độ nền a/μ mới là chiều thật sự mới. |
| E3 | "Không regime nào nằm trong hộp card được tính; bộ lọc bỏ qua age/amp nên loại cả biến thể" | Bộ lọc so tọa độ thô, nên lọt **10 regime map3age nằm trong hộp Hyp-MV khi quy về age 1** (bảng dưới). Đã sửa: `inside_frozen_cards_scaled` quy (κ, h) về age 1, có test riêng. Cards v1 đóng băng ở `1414d92` lúc 29/10 10:17; map1 bắt đầu 22:37 cùng ngày, map3age bắt đầu 30/10 00:11. Vì vậy cards là prereg có trước, nhưng **Ω⁻ của Hyp-MV không còn chưa ai thấy** và phải vào exposure register (việc của tác giả). Trên hình, các điểm này được vẽ rỗng. |
| E4 | Hình tỷ lệ ghi "η (biên độ nền)" | η là **luồng điều khiển**: u = 2η packet/s đi trên A khi Stay. Biên độ nền là `amp` (±6). |
| E5 | Nhiều kết quả được gọi là "phát hiện" | Phân loại lại ở mục "Cái gì thật sự mới" bên dưới. Phần lớn là đồng nhất thức hoặc điều đã kỳ vọng. |
| E6 | "A = 301 regime" được nêu như tỷ lệ | Số đếm phụ thuộc cách lấy mẫu: map2 cố ý dồn mẫu vào vùng A. Trong lưới đều map1: A 21/344, D 243/344. |
| E7 | Tóm tắt trong chat ghi kiểm độ bền map1 "mỗi vùng ít nhất một regime" | 8 regime map1robust gồm A/B/AB/D, **không có C**. C chỉ được kiểm ở plantrobust (XA167). |
| E8 | Comment sắp xếp trong `scan.py`: "slow mode switching" | κ nhỏ là đổi mode **nhanh**. Thứ tự chạy không đổi, chỉ sửa comment. |

10 regime lọt hộp card (E3). Cột "Quy về age 1" cho tọa độ tương đương:

| ID | Đã chạy | Quy về age 1 | Vùng card | Ḡ_S | Ḡ_M | Nhóm |
|---|---|---|---|---|---|---|
| XA081 | λA 7,5, λB 8, η ½, κ 0,1, h 8, age ½ | κ 0,2, h 16 | MV Ω⁺ | −0,87 | 3,82 | B |
| XA093 | λA 7,5, λB 8, η ¾, κ 0,1, h 8, age ½ | κ 0,2, h 16 | MV Ω⁺ | −0,42 | 5,26 | B |
| XA100 | λA 7,5, λB 8, η ½, κ 0,3, h 4, age ¼ | κ 1,2, h 16 | MV Ω⁻ | +0,52 | 0,09 | D |
| XA112 | λA 7,5, λB 8, η ¾, κ 0,3, h 4, age ¼ | κ 1,2, h 16 | MV Ω⁻ | +0,57 | 0,07 | D |
| XA129 | λA 7,5, λB 8, η ½, κ 1, h 8, age ½ | κ 2, h 16 | MV Ω⁻ | +0,36 | 0,01 | D |
| XA141 | λA 7,5, λB 8, η ¾, κ 1, h 8, age ½ | κ 2, h 16 | MV Ω⁻ | +0,31 | 0,02 | D |
| XA076 | λA 7,5, λB 8, η ½, κ 0,1, h 4, age ¼ | κ 0,4, h 16 | MV BND | +0,39 | 1,70 | B |
| XA088 | λA 7,5, λB 8, η ¾, κ 0,1, h 4, age ¼ | κ 0,4, h 16 | MV BND | +0,56 | 1,42 | B |
| XA105 | λA 7,5, λB 8, η ½, κ 0,3, h 8, age ½ | κ 0,6, h 16 | MV BND | +0,55 | 0,76 | D |
| XA117 | λA 7,5, λB 8, η ¾, κ 0,3, h 8, age ½ | κ 0,6, h 16 | MV BND | +0,66 | 0,49 | D |

Lưu ý: sự tương đương chỉ xấp xỉ về số. age ½ ở dt = 1/120 tương ứng với age 1 ở dt = 1/60.

## Đã chạy

| Đợt | Regime | Nội dung |
|---|---|---|
| map1 | 344 | Lưới thô đủ tổ hợp: λA {6,5; 7,5; 8,5} × λB {6; 7; 8; 8,5} × κ {0,1; 0,3; 1; 3} × η {¼; ½; ¾} × h {2; 4; 8} |
| map1robustK / map1robustdt | 8 + 8 | 8 regime đại diện (A/B/AB/D), chạy với K = 80 và dt = 1/240 |
| map2 | 576 | Lưới mịn. XM2S (360): vùng state thắng, h 1–4, κ 0,2–1, η đến ⅞. XM2X (216): vùng thay thế/gây hại, κ 0,05–0,15, h 4–8 |
| map3age | 216 | Age ∈ {¼; ½; 2; 4} s (mốc age 1 lấy từ map1). Tương đương (κ/age, h/age) ở age 1, xem E2 |
| map4amp | 126 | **Biên độ nền ON/OFF** ±4, ±5, ±7 (plant gốc ±6), age 1 |
| plantrobust | 12 | 6 regime age/amp đại diện (A, AB, C), chạy với K = 80 và dt = 1/240 |
| jointrobust | 6 | 3 regime J, chạy với K = 80 và dt = 1/240 |

Tổng cộng **1376 dòng**, gộp pilot đợt 1–2, tất cả có c_sw = 0. Theo tọa độ không thứ nguyên
(κ/age, h/age, λ/μ, u/μ, a/μ; μ = 10) thì là **1358 điểm khác nhau**, vì 18 dòng age trùng với dòng age 1.
Bảng có sẵn các cột không thứ nguyên này.

**`age` và `amp` là mở rộng plant chỉ dùng cho exploration.** Plant hợp đồng là age 1 s, ±6. Hai tham số
nằm trong bản sao cục bộ `queue_D`/`law` ở `experiments/explore_v13/population.py`; không sửa `src/`.
Kiểm tra:
- ở age 1, ±6, bản sao trùng **từng bit** với `smr.cells.queue_D`;
- `evaluate` tái tạo chính xác một dòng map1;
- kiểm riêng: 18 regime map2 trùng tọa độ map1 khớp chính xác;
- `tests/test_explore_v13.py` có 25 test.

## Cách phân nhóm

Ngưỡng ε_R = 1% C̄_ref. Đây là công cụ đọc, không phải test.

| Nhóm | Điều kiện | Nghĩa |
|---|---|---|
| **A** · state thắng | Ḡ_S ≥ 1, Ḡ_M < 1 | Đáng sửa state, không đáng sửa model |
| **B** · model thắng | Ḡ_M ≥ 1, −1 < Ḡ_S < 1 | Ngược lại |
| **AB** · cả hai | Ḡ_S ≥ 1, Ḡ_M ≥ 1 | Hầu hết là thay thế (Γ̄ < 0) |
| **J** · "cộng hưởng" | Ḡ_S, Ḡ_M < 1, G_SM ≥ 1, Γ̄ ≥ max(Ḡ_S, Ḡ_M) | Riêng lẻ nhỏ, làm cùng lúc mới vượt ngưỡng. Nhãn mô tả, xem mục dưới |
| **C** · state gây hại | Ḡ_S ≤ −1 | State tươi cộng model mean-field làm quyết định tệ hơn |
| **D** · không đáng kể | còn lại | |

Đồng nhất thức (không phải kết quả):
- **Γ̄ = Ḡ_S|M1 − Ḡ_S**, trên dữ liệu khớp chính xác (sai khác 0).
- **Ḡ_M, Ḡ_S|M1, G_SM ≥ 0** (min ≥ −2·10⁻¹⁵). S0 là posterior Bayes dưới luật thật, nên với model thật
  quyết định đã tối ưu theo thông tin đang có.
- **Γ̄ ≥ −min(Ḡ_S, Ḡ_M)**; nếu Ḡ_S < 0 thì Γ̄ > 0.

## Cái gì thật sự mới

| Kết quả | Loại |
|---|---|
| Không có vùng "model gây hại" | Đồng nhất thức (Ḡ_M ≥ 0) |
| State chỉ gây hại khi model sai | Đồng nhất thức (Ḡ_S\|M1 ≥ 0) |
| AB "gần thay thế hoàn toàn" (53/161) | Chạm cận Γ̄ ≥ −min(Ḡ_S, Ḡ_M) |
| J "cộng hưởng" | 8/14 regime có Ḡ_S < 0, nên Γ̄ > 0 là bắt buộc. 6 regime còn lại có Γ̄ ≤ 1,11% |
| Ḡ_S\|M1 không giảm theo age (54/54) | Điều đã kỳ vọng: quan sát càng cũ càng ít thông tin. Trong tọa độ thiết kế, đây là κ/age và h/age cùng giảm |
| C không phụ thuộc age | Phần lớn do cấu trúc: L̄10 không đổi theo age, và 72% regime C có G_SM < 1% (L̄00 ≈ L̄11) |
| **Vùng A**: state có ích, model gần như vô dụng | **Discovery.** Ở age 1, ±6 (211 regime): Ḡ_S trung vị 1,53%, 90% ≤ 2,46%, max 4,01%; Ḡ_M trung vị 0,012% |
| **Trong AB**: Ḡ_S lớn nhưng Ḡ_S\|M1 nhỏ | **Discovery.** Trung vị Ḡ_S 4,96% nhưng Ḡ_S\|M1 0,71%. Có model đúng thì quan sát cũ đã gần đủ để quyết; state tươi chủ yếu bù lỗi model |
| B chuyển thành AB khi age tăng | Discovery, nhưng tương đương κ và h cùng giảm (E2) |

## Kết quả chi tiết

Số dòng theo nhóm, toàn bộ 1376 dòng, phụ thuộc cách lấy mẫu (E6): A 301 · B 43 · AB 161 · J 14 · C 334 · D 523.
Lưới đều map1 (344): A 21 · B 4 · AB 7 · J 1 · C 68 · D 243.

1. **Không repair nào luôn thắng.** Cả 4 vùng đều có và tách nhau trong tọa độ thiết kế. Bản thân câu này
   là kiểu "heatmap có crossover", chưa phải contribution nếu không có vùng hoặc luật được khóa trước và kiểm
   trên regime mới.
2. **Theo age** (54 cấu hình; mỗi cột age a tương đương κ/a, h/a ở age 1):
   - Ḡ_S|M1 lớn nhất 1,4 → 2,1 → 3,1 → 4,3 → 5,0% C̄ khi age = ¼ → ½ → 1 → 2 → 4 s.
   - Nhóm: D 30 → 9, A 4 → 23, B 8 → 0.
3. **A · state thắng**: h ngắn (1–4 s), κ 0,2–1 (mode kéo dài 0,2–1 s, không dài hơn tuổi quan sát 1 s),
   η ≥ ½, λB 7–7,5 (λA 6–7,5). Cách đọc: state tươi cho biết mode hiện tại mà quan sát cũ đã quên; horizon
   ngắn nên lỗi mean-field của M0 nhỏ.
   - Lớn nhất ở age 1: XM2S189 (λA 6,5, λB 7, κ 0,2, η ⅞, h 2), Ḡ_S +4,0% C̄ (34% stakes), Ḡ_M 0,6.
   - Lớn nhất ở age 4: XA087 (λA 7,5, λB 8, κ 0,1, η ¾, h 2), Ḡ_S +4,7%, Ḡ_M 0,00. Tương đương age 1
     với κ 0,025, h 0,5, nằm ngoài lưới age 1.
   - Hiệu ứng thật nhưng nhỏ: trung vị 1,5% so với ngưỡng 1%.
4. **B · model thắng**: mode đổi nhanh (κ ≤ 0,3), h ≥ 4–8, λB 7–8, age ≤ 1. Ví dụ XM1224, Ḡ_M 5,85.
   Pilot trong hộp card có X2065, Ḡ_M 13,4.
5. **AB · thay thế**: 155/161 regime có Γ̄ < 0, ở λA 6–6,75, λB 6,5–7, κ ≤ 0,1, η ≥ ¾, h 4–8.
   - Mạnh nhất: XM2X077 (λA 6,25, λB 7, κ 0,05, η ⅞, h 8). Sửa state +20,4%, sửa model +37,8%,
     sửa cả hai +37,8%, Ḡ_S|M1 = 0.
6. **J**: 14 regime, G_SM 1,05–2,1%, nằm ở dải chuyển tiếp giữa C và A (λA 6–6,5, λB 7,5–8, κ 0,2–0,3,
   η ¾–⅞, h 2–4). Ví dụ XM2S069: sửa state +0,48, sửa model +0,10, sửa cả hai +1,70. Γ̄ dương phần lớn là
   đại số (bảng trên); không nên gọi là phát hiện cộng hưởng.
7. **C · state gây hại**: λB cao so với λA (7,5–8,5), mode đổi nhanh (κ ≤ 0,1–0,3), h 4–8.
   - Tệ nhất: XM2X041 (λA 6, λB 7,5, κ 0,05, η ⅞, h 8), Ḡ_S −34,9% C̄, Ḡ_M 0, G_SM 0.
   - Pipeline cũ (state cũ + M0) đã chọn đúng; đưa state tươi cho M0 làm hỏng.
8. **D · không đáng kể**: κ = 3 luôn rơi vào D, vì mode kéo dài khoảng 3 s, lâu hơn tuổi quan sát, nên quan
   sát cũ vẫn đúng về mode. Cũng gặp ở κ = 1 với λB 8, và phần lớn η = ¼.
9. **Biên độ nền nhỏ (±4)** làm mọi hiệu ứng tính theo % C̄ lớn lên (tới Ḡ_M 35%, Ḡ_S −44%, Γ̄ −17).
   Phần lớn là do C̄_ref nhỏ đi: trung vị C̄(±4)/C̄(±6) = 0,32. Tính tuyệt đối, Ḡ_M|S1 chỉ tăng khoảng 15%
   (trung vị). a/μ là chiều mới thật sự, nhưng không phải núm "model error" sạch.

## Độ bền

- **map1robust (8 regime A/B/AB/D):** 8/8 giữ nguyên nhóm. Thay đổi lớn nhất 0,12 pp với K = 80,
  0,28 pp với dt = 1/240.
- **plantrobust (6 regime age/amp, có C):** 12/12 giữ nguyên nhóm. Thay đổi lớn nhất 0,19 pp.
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

## Đánh giá (sửa lại): **TỐT về bản đồ, ỔN về cái mới**

**Bản đồ tốt:**
- Đủ 4 vùng A/B/C/D, số liệu bền theo K và dt.
- Các đồng nhất thức giải thích được vì sao C và AB đi với Γ̄ lớn.
- Có bảng tọa độ không thứ nguyên để ghi exposure.

**Cái mới chỉ ở mức ổn:**
- Phần thật sự mới chỉ có vùng A (nhỏ: trung vị 1,5%) và việc Ḡ_S|M1 nhỏ trong AB.
- Phần còn lại là đồng nhất thức hoặc điều đã kỳ vọng.
- Age không phải chiều mới.

Ngoài ra:
- toàn bộ là discovery, chưa có luật a priori nào được kiểm ngoài mẫu;
- các vùng thú vị cần mode đổi nhanh hơn tuổi quan sát và λB gần bão hòa, nên tính thực tế còn mở;
- không có người thật đọc.

**Hàm ý cho exploration tiếp:**
- Nên mô tả mọi thứ theo tọa độ không thứ nguyên (κ/age, h/age, λ/μ, u/μ, a/μ).
- Nên báo cả Ḡ_S lẫn Ḡ_S|M1 để tách "state có giá trị thật" khỏi "state bù lỗi model".
- Bộ lọc hộp card phải quy về age 1 (đã sửa).
- Muốn dùng làm claim phải prereg và kiểm trên regime mới. Tác giả quyết.

## Sự cố khi chạy (ghi đúng như đã xảy ra)

1. **map2 lần đầu** (6 nhân, giới hạn 58 phút, chỉ ghi file ở cuối) bị dừng ở phút ~60 khi VS Code khởi động
   lại. Không lưu được regime nào.
2. **Lệnh chạy lại map2 lúc 23:55 bị tác giả từ chối nhưng vẫn khởi động** (tiến trình 264119). AI không biết
   và không kiểm lại.
   - Nó chạy song song với map3age khoảng 2 giờ, 16 worker trên 10 nhân, nên map3age mất 86 phút.
   - Lúc 01:51 bản map2 xếp hàng khởi động, thành hai bản cùng ghi một thư mục.
   - AI dừng cả hai, giữ 460 checkpoint, rồi chạy một bản duy nhất cho 116 regime còn lại.
   - Dòng do code cũ (trước `age`/`amp`) ghi được điền age = 1, amp = 6 (`with_plant_columns`).
   - Kiểm chéo 18 regime trùng map1: 0 sai khác.
3. WSL khởi động lại lúc 07:50 ngày 30/10 khi plantrobust đang ở 10/12. Phần còn lại chạy tiếp bằng `--resume`.
4. Nhật ký chạy: `results/explore_v13/logs/`.
   - `map2_first_run.log`: bản bị từ chối nhưng vẫn chạy.
   - `map2_second_stopped.log`: bản xếp hàng, bị dừng.
   - `map2_resume.log`: bản chạy nốt.

`map3age/specs.json` ghi đúng 216 regime đã chạy. Với bộ lọc đã sửa, `scan.py map3age` giờ chỉ sinh 206
regime; test kiểm đúng 10 regime bị loại.

## Tệp

Hình (đã vẽ lại 30/10):
- [regime_map_differ.png](regime_map_differ.png): bản đồ Ḡ_S × Ḡ_M, vùng A/B/AB/C/D/J; điểm rỗng là trong hộp card khi quy về age 1.
- [regime_map_mechanism.png](regime_map_mechanism.png): Ḡ_S|M1 × Ḡ_M|S1.
- [regime_design_age.png](regime_design_age.png): age × h, η. Mỗi cột age a ≡ age 1 với κ/a, h/a.
- [regime_design_amp.png](regime_design_amp.png): biên độ nền × h, η.
- [regime_composition_map1.png](regime_composition_map1.png): tỷ lệ nhóm theo trục, chỉ map1.

Bảng: [regime_map_table.csv](regime_map_table.csv), 1376 dòng, có `in_card` (đã quy về age 1) và các cột
không thứ nguyên.

Code:
- `experiments/explore_v13/{population,scan,regime_map,plot_map}.py`
- `tests/test_explore_v13.py`

Dữ liệu: `results/explore_v13/<đợt>/{specs.json, regimes.csv, pairs.npz, status.json}`.

Mã màu: chỉ 3 màu đã kiểm all-pairs (xanh dương / cam / xanh ngọc) cộng mực đậm và hai mức xám. Mọi
nhóm có marker hoặc chữ riêng.
