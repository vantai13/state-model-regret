# Khám phá cơ chế regime v2: tổng kết (01/11/2026)

Doan Van Tai — **AI (Claude) thiết kế, chạy và soạn theo ủy quyền**; đây là exploration thích nghi trên
nhánh `explore/mechanism-regime-v2`, không phải author-self, không phải confirmation, không phải claim
novelty. Chưa tra literature cho các hiện tượng dưới đây.

## 1. Đã chạy gì

| Stage | Số regime | Mục đích | Thiết kế trước/sau khi nhìn |
|---|---|---|---|
| ref | 6 | kiểm hai máy cho dòng giống từng bit | trước |
| sobol (lưới 1/50) | 103 | dừng vì chậm 4–7 lần | trước |
| sobol4 | 16.384 | quét toàn không gian (u, phần tải tự do của A và B, log κ/τ, log h/τ) | trước |
| hslice | 256 | quét h/κ 1–160 ở 8 giá trị δ | sau 5.814 dòng sobol4 |
| xslice | 100 | quét x mịn ở u = 1, 2 | sau 5.814 dòng sobol4 |
| pslice | 258 | kiểm biến gom P = (h/κ)·\|δ\| | sau 5.814 dòng sobol4 |
| xstar | 234 | kiểm công thức ranh giới x* ở 13 tổ hợp (tải, u) mới | sau khi chấm ba lát trên |
| kslice | 150 | khám phá: các lớp đổi thế nào khi κ/τ từ 0,02 đến 2 | sau xstar |

- Plant contract v1.3: μ = 10, **a/μ = 0,6 cố định** (biên độ để held-out), τ = 1, c_sw = 0.
- Mọi điểm có h/κ ≤ 160. Code tự từ chối khóa R09/R10 sealed, 270 khóa CF-v2 và 12 khóa panel L4.9.
- Engine native đông lạnh cộng baseline margin L4.4, chạy ở **một mức số duy nhất** (K = 160, ref = 2,
  dt = 1/240).
- Hai máy (local WSL và GCP n2-standard-8) có môi trường đồng nhất: 6/6 dòng tham chiếu giống từng bit.
- Không có dòng UNRESOLVED nào.

Ký hiệu:
- S = G_S|M1, M = G_M|S1, R = S/(S+M) (chỉ tính khi S+M ≥ 0,5%), tất cả tính bằng % C̄_ref;
- δ = λB − λA (packet/s);
- **x = δ/u**;
- **P = (h/κ)·|δ|**.

## 2. Hiện tượng (mô tả; hình [sobol4/phase_x.png](sobol4/phase_x.png), [phase_R.png](sobol4/phase_R.png))

**H1. Khi P lớn, các lớp xếp theo x.** Bảng dưới lấy các regime sobol4 có P ≥ 30 và S+M ≥ 0,5%:

| x | G_S < −0,1 (state mới gây hại với M0) | Γ < 0 (thay thế) | khác |
|---|---|---|---|
| x < 0 | 693 | 0 | 0 |
| 0 < x ≤ 0,5 | 82 | 154 | 17 |
| x > 0,5 | 521 | 0 | 1 |

Bảng δ trong L4.2 là một lát u ≈ 1,5 của cấu trúc này. Theo δ tuyệt đối thì ngưỡng dịch theo u; theo x
thì ngưỡng gần như không đổi.

**H2. λA = λB là một đường đối xứng.** 2.014 regime sobol4 có M ≤ 0,253%, trung vị 0,005%. Ở xslice và
pslice, M = 0,000. Đường này không bao giờ chuyển sang vùng model chiếm ưu thế.

**H3. Chuyển pha R gom theo P tốt hơn theo h/κ.**
- Độ lệch trung bình quanh trung vị theo bin là 0,104 với P, so với 0,134 với h/κ, tính trên 10.568 dòng
  chưa nhìn lúc lập giả thuyết.
- R cắt 0,5 quanh P ≈ 10–13.
- Trong pslice, điểm cắt nằm ở 6–8 khi δ < 0 và 10–17 khi δ > 0: có **bất đối xứng theo dấu δ**.

**H4. Mean model "mù horizon".** Tỷ lệ Switch của M0 (cả state cũ lẫn mới) giống nhau đến 3 chữ số giữa
h/κ = 50 và 150. Truth thì hội tụ về một action không phụ thuộc state.

**H5. Bản đồ thực tế** (trung vị sobol4, % C̄_ref):

| Vùng | n | S | M | sửa cả hai (G_SM) | còn lại sau margin | margin gỡ |
|---|---|---|---|---|---|---|
| P < 10 | 3.147 | 0,88 | 0,13 | 0,91 | 0,89 | 0% |
| δ = 0 | 739 | 0,91 | 0,00 | 0,91 | 0,91 | 0% |
| P ≥ 10, 0 < x ≤ 0,5 | 676 | 1,21 | 3,62 | 7,35 | 2,51 | 61% |
| P ≥ 10, x < 0 | 774 | 0,01 | 1,58 | 0,03 | 0,03 | — |
| P ≥ 10, x > 0,5 | 864 | 0,05 | 2,54 | 0,43 | 0,15 | 37% |

Ở vùng "state gây hại", hệ rẻ (state cũ + M0) đã gần tối ưu. Nâng riêng state làm mất khoảng 1,5% (trung vị
inv_state = −1,52% khi x < 0), kể cả khi có margin.

**H6. Ở cùng h/κ, mọi đại lượng tính trên state hiện tại gần như không đổi theo κ; κ/τ chỉ tác động qua
state cũ.** kslice (150 regime, S = 13,5, u = 2, x ∈ {−0,5; 0; 0,25; 0,5; 0,75}, h/κ ∈ {16, 50, 150},
κ 0,02–2) cho:

| Đại lượng (cùng x, cùng h/κ ± 1%) | κ > 0,1 | κ > 0,05 | gồm cả κ = 0,02 |
|---|---|---|---|
| M: chênh tương đối lớn nhất giữa các κ | 2,0% | 5,4% | 21,6% |
| Tỷ lệ Switch của truth (state mới): khoảng | 0,0015 | 0,0025 | 0,0084 |
| S: max/min | 5,5 lần | 7,6 lần | 8,0 lần |

- Nghĩa là M là hàm của h/κ và tải, còn S đổi theo κ/τ. Điều này khớp với việc τ chỉ đi vào kênh quan sát:
  các ô S1 không chứa τ, nên đổi thang thời gian giữ nguyên tỷ lệ % C̄_ref.
- Độ lệch ở κ = 0,02 có thể do dt = 1/240 cố định: mỗi thời gian mode chỉ còn khoảng 5 slot. Đây là đặc
  điểm của estimand slotted, không phải lỗi chương trình, nhưng cần nhớ khi đọc vùng κ rất nhỏ.
- Cũng trong kslice, khi κ tăng từ 0,02 lên 0,63 (h/κ = 50):
  - ở x = 0,25, Γ yếu dần từ −6,9 về −1,0 và S giảm từ 2,6 xuống 0,45;
  - M0 với state cũ từ lật gọn (1,000/0,047 ở x = 0,25/0,5) chuyển sang dạng dần dần (0,614/0,349).
  Dải thay thế mờ đi khi state cũ còn mang thông tin mode.

## 3. Cơ chế AI đề xuất (chưa chứng minh)

1. **Truth ở h dài.**
   - Stay giữ stationary; Switch dời u từ A sang B. Chi phí thật có phần dài hạn h·c_stat, với
     c_stat = f(λA) + f(λB+u) − f(λA+u) − f(λB), f = E_stat[Q] lồi tăng.
   - Do tính lồi, c_stat < 0 ⇔ δ < 0, nên khi P lớn, action đúng = "dời sang đường nhẹ", gần như không phụ
     thuộc state. δ = 0 cho c_stat = 0.
2. **M0 không có phần dài hạn.**
   - Tốc độ trung bình nhỏ hơn μ nên đường trung bình xả về 0. M0 chỉ so chi phí xả backlog hiện có.
   - Xấp xỉ q²/(2g) với E[q²] ∝ g⁻², M0 trên posterior gần stationary chọn Switch khi
     gA³(gA+u) < gB³(gB−u). Công thức này cho x* ≈ k/(k+2) = 1/2 khi u ≪ headroom, và x* nhỏ dần khi B gần
     hết headroom sau Switch.
3. **Hệ quả.**
   - 0 < x < x*: M0 với state cũ chọn sai có hệ thống, nên state mới hoặc model đúng đều sửa được (thay thế).
   - Ngoài dải: M0 với state cũ chọn đúng nhờ trung bình hóa; state mới làm M0 phản ứng theo backlog nhất
     thời → G_S < 0 (**thông tin mới khuếch đại một model cận thị**).
4. **Đối xứng hoán đổi.**
   - Khi δ = 0, chi phí Switch tại state x bằng chi phí Stay tại state đã hoán đổi hai đường. Quyết định chỉ
     còn là so thứ tự hai state.
   - Mọi model đơn điệu theo backlog cho cùng action, trừ các cặp state không so được thứ tự. Vì vậy M ≈ 0;
     phần dư nhỏ ở h/κ nhỏ (M tới 0,19%).
5. **Gom theo P.** M lớn lên theo h·|c_stat| (≈ tỷ lệ |δ|), còn S bão hòa theo h, nên R đổi chiều khi
   (h/κ)·|δ| vượt cỡ 10. Chưa có lý do vì sao κ đứng ở mẫu số (điều này dựa trên τ = 1 cố định).

## 4. Dự đoán ghi trước và kết quả chấm

Dự đoán nằm trong [PREDICTIONS_x.md](PREDICTIONS_x.md), [PREDICTIONS_collapse.md](PREDICTIONS_collapse.md) và
[PREDICTIONS_xstar.md](PREDICTIONS_xstar.md), commit trước khi có dòng tương ứng. Bộ chấm là
[check.py](../../experiments/explore_mech/check.py); kết quả ở [checks.json](checks.json) và
[checks_xstar.json](checks_xstar.json).

| | Dự đoán | Kết quả | Ghi chú |
|---|---|---|---|
| P1 | h/κ ≥ 50, \|δ\| ≥ 1/2: truth Switch ≥ 0,9 khi δ<0, ≤ 0,1 khi δ>0 | ❌ 1/112 | u = 2, δ = 0,5, h/κ = 50 cho 0,114; ở h/κ = 150 là 0,008 |
| P2 | ranh giới M0 với state cũ ∈ [0,3; 0,6], u lớn cho x* không lớn hơn | ✅ | 0,495 (u = 1), 0,415 (u = 2), không đổi giữa h/κ 50 và 150 |
| P3 | Γ < 0 chỉ trong (0, x*); ngoài dải G_S < 0 | ✅ | 0 vi phạm |
| P4 | δ = 0: G_S ≥ −0,1, Γ ≥ −0,1(S+M) | ✅ | 36 dòng |
| P5 | \|δ\| nhỏ đạt dấu cuối của G_S muộn hơn | ❌ | đúng ở δ < 0 và ở x > x* (−1/4: 21 so với −1/2: 15; 0,75/1/1,5: 41/21/15); với δ = +1/4, +1/2 dấu G_S dương ngay từ đầu nên tiêu chí đặt sai |
| C1 | điểm cắt P* ∈ [5, 30] | ❌ 1/30 | 4,05 ở δ = −1, u = 1,5, κ = 0,8; δ = −2 không có điểm cắt vì S+M < 0,5 ở P nhỏ |
| C2 | max/min P* ≤ 2,5 và max/min (h/κ)* ≥ 2,5 | ❌ 1/6 | P gom tốt hơn h/κ ở cả 6/6 nhóm; nhóm u = 1,5, κ = 0,8 có P_ratio 3,47 |
| C3 | δ = 0: M ≤ 0,3 và R ≥ 0,9 | ❌ | M đúng (≤ 0,186); R = 0,83–0,88 ở h/κ = 2 (ngưỡng viết hớ: sobol4 đã có R trung vị 0,86 ở h/κ nhỏ) |
| X1 | công thức x*: sai số ≤ 0,08, giảm theo u | ❌ 1/15 | S = 12,5, u = 1: điểm x = 0,5 vẫn Switch 80%. 14 chuỗi còn lại sai số ≤ 0,067 |
| X2 | κ = 0,5 (khám phá) | — | M0 không lật gọn; x* thấp hơn công thức 0,06–0,16 |
| X3 | Γ < 0 chỉ trong (0, x*) ở κ = 0,1 | ✅ | ở κ = 0,5 có 14 dòng Γ < 0 ngoài dải |

Ý định tính của cơ chế (dấu truth, ranh giới M0, M ≈ 0 khi δ = 0, P gom tốt hơn h/κ, x* giảm theo u) khớp.
Phần lớn ngưỡng định lượng ghi trước thì **trượt ở mép**. Sai số của công thức x* có hướng theo tải: đoán
thấp khi S thấp, đoán cao khi S cao.

## 5. Chỗ để tác giả tự mò cơ chế

1. **Chứng minh hay bác bỏ** "dấu action thật → dấu δ khi h → ∞" trong họ slotted R2 (cần cận cho phần
   transient), và lập luận hoán đổi khi δ = 0 (tập state không so được thứ tự là gì, khối lượng bao nhiêu).
2. **Sai số có hướng của x*** theo tải: do P(Q > 0), do số mũ k của E[q²] theo headroom, hay do posterior
   không stationary?
3. **κ ≈ τ**: M0 với state cũ thành dạng dần dần (H6). Bước nhảy 0,15 trong một bước lưới ở κ = 0,5,
   x 0,31→0,38 có phải khối xác suất y = 0 (backlog rỗng) lật cùng lúc? Nếu đúng như H6 rằng M chỉ phụ
   thuộc h/κ còn S phụ thuộc κ/τ, thì R(h/κ, κ/τ) có tách được thành hai hàm một biến không?
4. **Bất đối xứng P* theo dấu δ** (6–8 so với 10–17) và việc P* tăng theo u khi δ > 0.
5. **Biến không thứ nguyên đúng cho P**: (h/κ)·|δ|·τ chỉ có nghĩa khi τ = 1 cố định; P* còn giảm nhẹ khi κ
   tăng.
6. **Dự đoán cho điều kiện chưa dùng** (biên độ a/μ ≠ 0,6; chưa chạy, vẫn held-out): nếu cơ chế xả backlog
   đúng thì a chỉ vào hệ số chung của E[q²] ở hai đường, nên **x* gần như không đổi theo a**. Ngược lại, P*
   phải đổi vì S và M co giãn khác nhau theo a. Muốn kiểm phải khóa dự đoán trước và tác giả quyết định có
   mở biên độ hay không.

## 6. Hạn chế

- Một mức số duy nhất; không có paired refinement R1 cho từng điểm.
- kslice: 14/150 dòng có cờ arithmetic, cùng kiểu (S âm rất nhỏ khi S ≈ 0).
- 670/16.384 dòng sobol4 có cờ arithmetic (S hoặc G_SM âm rất nhỏ ở chỗ giá trị gần 0; nhỏ nhất −0,077%).
  538 dòng thiếu baseline vì cùng lý do. Các cờ này không đổi lớp regime ở chỗ \|G_S\|, M lớn, nhưng chưa
  được kiểm riêng.
- Lưới λ, u bước 1/4 trong sobol4 làm x và δ rời rạc (x = 0 có khối lượng thật).
- Mật độ điểm phản ánh thiết kế Sobol, không phản ánh tần suất ngoài đời.
- Mọi hiện tượng đều là discovery thích nghi do AI thiết kế; giả thuyết lập trên 5.814 dòng sobol4 đầu tiên.
  Các lát kiểm là điều kiện chưa dùng **trong cùng plant** (a/μ = 0,6, c_sw = 0); nhãn PC/Gate/card/contract
  không đổi.

## 7. Provenance

Commit trên nhánh (chưa push, chưa merge): `754aa14b`, `fbd59e6a` (code, môi trường, sobol4), `080cee8a`
(dự đoán x), `2b0db7fd` (dự đoán gom P), `32241b0a` (bộ chấm), `d8e9002e` (hình), `4b412c31` (kết quả và
chấm), `036d752f` (dự đoán xstar), `f4f84baa` (chấm xstar, thiết kế kslice), và commit chứa file này (kết quả kslice). Dòng thô ở `<stage>/level_160_2/`; log
theo máy ở [logs/](logs/). Log sobol4 ghi thứ tự hoàn thành, nên tách được 5.816 dòng "đã nhìn" và 10.568
dòng "chưa nhìn".
