# Thẻ giả thuyết L7.2 — mở biên độ held-out a = 3 và a = 7,5 (ctmc-v1)

> **Provenance.** Doan Van Tai — **bản soạn của AI (Claude) theo yêu cầu "bạn hãy đóng vai trò là tôi và soạn cho
> tôi"** (03/11/2026). Đây **không phải** thẻ do tác giả tự viết: tác giả chưa đọc, chưa sửa, chưa tự viết lại claim
> bằng lời mình; mentor chưa review. Theo Lesson 7.2 §2.6, một thẻ do agent viết không làm G-level nhúc nhích (vẫn G1),
> và kết quả mở held-out theo thẻ này phải được báo là "test theo thẻ do AI soạn theo ủy quyền". **Chưa khóa**: chỉ khóa
> khi tác giả đọc thẻ và `check_l72.py` rồi nói "khóa" (Lesson 7.2 §2.5).

## 1. Ngày, tác giả, commit gốc

- Ngày: 03/11/2026. Nhánh `explore/ctmc-phase7`, commit gốc `e6feec85`.
- Namespace ctmc-v1 ([SPEC](../../../experiments/explore_ctmc/SPEC.md)); μ = 10, τ = 1, c_sw = 0, P1, S0/S1, D19 giữ nguyên.

## 2. Năm claim (câu abstract)

- **C-A (onset zero-fit).** Ở horizon dài hơn khoảng 4–7 lần thời gian tương quan T_int của queue, một công thức không
  fit tham số dự đoán giá trị của state tươi đối với twin mù horizon tới 0,1 điểm phần trăm của C_ref.
- **C-B (dải hẹp tính trước được).** State tươi làm hại twin mù horizon ở mọi tải trừ một dải 0 < x < x*, và biên x*
  tính được trước từ zero-fit.
- **C-C (planner dừng đủ ở horizon dài).** Khi h ≥ 7·T_int và δ ≠ 0, một planner dừng không nhìn state có regret không
  quá 0,1% C_ref; dải giúp co lại khi burst mạnh lên.
- **C-D (không cần mode oracle).** Harm từ state tươi đã xuất hiện khi state mới chỉ gồm backlog (không có mode), và phần
  backlog của harm khớp con số zero-fit ở horizon dài.
- **C-E (harm cần planner ngầm).** Harm xảy ra khi twin, với state cũ, đúng nhờ lấy trung bình; một twin sai đều (KO)
  không bị state tươi làm hại thêm nhưng có regret lớn hơn M0 nhiều lần. Kèm: hai đồng hồ — P xếp thứ tự "state hay model
  thắng", còn h/T_int xếp thứ tự hội tụ tới z_∞.

## 3. Held-out, miền, trần CPU, case list

| | a = 3 (a/μ = 0,3) | a = 7,5 (a/μ = 0,75) |
|---|---|---|
| Miền | λA, λB ≥ 6, max(λ) + u < 10, u ∈ [1/4; 3], κ ∈ [0,02; 5] | λA, λB ≥ 7,5, max(λ) + u < 10, κ ∈ [0,02; 5] |
| AS (kiểu asym) | `cases/zf_a3_asym.json`: 33 regime × 7 horizon | `cases/zf_a7p5_asym.json`: 27 regime × 7 horizon |
| SO (Sobol) | `cases/zf_a3_sobol.json`: 600 regime × 1 horizon | `cases/zf_a7p5_sobol.json`: 600 regime × 1 horizon |
| XS (lát x, h = 10·T_int) | `cases/zf_a3_xs.json`: 276 regime, 6 chuỗi (u, λA, κ) | `cases/zf_a7p5_xs.json`: 200 regime, 6 chuỗi |
| CPU ước lượng (thô, ±2 lần) | ~6,5 CPU-h | ~21 CPU-h với trần |

- **Trần:** 900 CPU-s mỗi case (RLIMIT_CPU). Vượt trần → UNRESOLVED, báo riêng, **không chạy lại với trần khác**.
- **Một lần chạy** mỗi case list. Truth ở AS và SO dùng `evaluate_d22` khi max(N_A, N_B) ≤ 3.000 (để có F, V), ngược lại
  dùng `evaluate`; XS dùng `evaluate`. KO có trong mọi output.
- **Số zero-fit đóng băng** (đã tính trước, không có cột truth): `l72/ZEROFIT_a3.csv`, `l72/ZEROFIT_a7p5.csv`,
  `l72/compare_amplitudes.json`. Khi khóa, sha256 của các file này và của 6 case list được ghi vào `locks_l72.json`.

## 4. Những gì đã thấy trước khi viết

- **Toàn bộ dữ liệu a = 6** của L7.1, D22 và KO (truth đã mở), kể cả các số hiệu chỉnh dùng để đặt ngưỡng dưới đây:
  regret Static ≤ 0,1% ở 96,2% dòng δ ≠ 0, h ≥ 7·T_int; onset bậc một (quyết định ở h = ∞) 44,6% / 96,3% / 100% / 100%
  ở (2; 4] / (4; 7] / (7; 15] / (15; 40]; G_S > 0,1% ở 10,5% dòng wide có h ≥ 7·T_int; tỷ lệ regret KO/M0 tươi trên
  dòng harm (h > 4·T_int) có q10 = 1,71; P đúng 95,4% so với nền 86,2% và h/T_int 87,9% ở Stage E; Spearman −0,92 so với
  −0,74; D22 ở a = 6: F < 0 ở 100% dòng harm có h < T_int, tỷ lệ F/G_S khớp zero-fit ở 99,8% dòng h ≥ 3·T_int.
- **Zero-fit ở a = 3 và a = 7,5** (không truth): T_int trung vị 41 s / 339 s; z_∞ < −0,5 ở 74% / 58% regime Sobol,
  z_∞ > 0,5 ở 8,7% / 0,2%; phần backlog z_F,∞/z_∞ trung vị 0,83 / 0,90; x*_zf 0,19–0,29 / 0,12–0,16; M0 với state cũ chọn
  đúng action dài hạn ở trung vị 0,91 / 0,83 trên regime harm zero-fit (state mới: 0,71 / 0,73); KO chọn đúng khoảng
  0,14 / 0,12.
- **Lý do đổi L72-4 trước khi khóa:** ở h > 7·T_int, zero-fit đã cho tỷ lệ dòng z_pred1 > 0,1% là 15,7% (a = 3) và 1,1%
  (a = 7,5), nên một ngưỡng ở vùng đó gần như chắc đạt. Ở 1 < h/T_int ≤ 4 zero-fit không đáng tin: a = 6 cho truth 12,5%,
  khai triển bậc một 22,6%, z_∞ 6,7%; ở held-out, khai triển bậc một cho 22,7% (a = 3) và 13,6% (a = 7,5), z_∞ cho 6,2% và 0%.
- Không có giá trị truth nào ở a ≠ 6 (đã kiểm: 0 file; code từ chối bằng PermissionError).

## 5. Quy ước chung cho mọi dự đoán

- Một **dòng** = (regime, h) có status COMPLETED. T_int = T_int lớn nhất trong 4 chain của regime (trường `h_Tint`).
- **Khoảng h/T_int** là nửa mở bên trái: (lo; hi]. **Dòng harm**: G_S < −0,5% (trừ khi ghi khác). δ = λB − λA.
- **n tối thiểu:** một dự đoán hoặc một khoảng có ít hơn 10 dòng đủ điều kiện → INCONCLUSIVE ở biên độ đó.
- **UNRESOLVED:** nếu hơn 10% số case đủ điều kiện về tham số của một dự đoán là UNRESOLVED/ERROR → INCONCLUSIVE ở biên
  độ đó; ngược lại bỏ các case đó khỏi mẫu số và báo số lượng.
- Mọi "≤", "≥" là bao gồm dấu bằng; mọi % là của C_ref = L11. z_pred1 và z_F,∞, z_∞, x*_zf lấy **nguyên văn** từ file
  zero-fit đóng băng (ghép theo stage, id, h).

## 6. Bảng dự đoán (chấm riêng ở a = 3 và a = 7,5)

| ID | Claim | Loại | Tập và điều kiện | Đại lượng | Ngưỡng |
|---|---|---|---|---|---|
| L72-1 | C-A | onset | AS ∪ SO, theo từng khoảng (4; 7], (7; 15], (15; 40] | tỷ lệ dòng có \|G_S − z_pred1\| ≤ 0,1 pp | ≥ 0,90 / ≥ 0,95 / ≥ 0,95. Đạt khi cả ba khoảng đạt; (2; 4] chỉ báo, không chấm |
| L72-2 | C-B | rủi ro | XS, mỗi chuỗi (u, λA, κ) | x_edge = điểm G_S đổi dấu từ + sang − lần đầu theo x > 0, nội suy tuyến tính giữa hai điểm lưới (cùng cách tính x*_zf trong `zf_report.x_star`); không đổi dấu → "không dải" | \|x_edge − x*_zf\| ≤ 0,05 (nếu x*_zf không tồn tại thì truth cũng phải "không dải"), đạt ở ≥ 5/6 chuỗi. Chuỗi có điểm UNRESOLVED trong [x*_zf − 0,1; x*_zf + 0,1] bị loại; còn < 4 chuỗi → INCONCLUSIVE |
| L72-3 | C-C | onset | AS ∪ SO, δ ≠ 0, h/T_int > 7 | tỷ lệ dòng có regret Static ≤ 0,1% | ≥ 0,90 |
| L72-4 | C-C | rủi ro (so sánh hai biên độ, một verdict) | SO, δ ≠ 0, 1 < h/T_int ≤ 4 | tỷ lệ dòng có G_S > 0,1%, ký hiệu p_3 và p_7,5 | p_7,5 ≤ p_3 − 0,05 (dải giúp co khi burst mạnh, ở horizon vừa nơi zero-fit không đáng tin) |
| L72-5 | C-D | rủi ro | AS ∪ SO có D22, dòng harm, h/T_int ≤ 1 | tỷ lệ dòng có F < 0 | ≥ 0,70 |
| L72-6 | C-D | onset | AS ∪ SO có D22, dòng harm, h/T_int > 7, \|z_∞\| ≥ 0,5 | tỷ lệ dòng có \|F/G_S − z_F,∞/z_∞\| ≤ 0,1 | ≥ 0,80 |
| L72-7 | C-E | rủi ro | AS ∪ SO, dòng harm, h/T_int > 4 | tỷ lệ dòng có regret(KO, state mới) ≥ 1,5 × regret(M0, state mới) | ≥ 0,90 |
| L72-8 | C-E | rủi ro | (a) SO, S + M ≥ 0,5%; (b) AS, \|z_∞\| ≥ 0,5 | (a) độ chính xác ngưỡng đơn tốt nhất cho nhãn S > M (197 phân vị, như `analyze.py`); (b) Spearman của \|G_S − z_∞\|/\|z_∞\| | (a) acc(P) ≥ tỷ lệ lớp đa số + 0,05 **và** acc(P) ≥ acc(h/T_int); (b) Spearman với h/T_int ≤ Spearman với h/κ − 0,1. Đạt khi cả hai đạt |
| L72-Z | C-E | zero-fit (không tính là bằng chứng) | AS ∪ SO, δ ≠ 0, G_S < −0,1%, h/T_int ≥ 4 | trung vị tỷ lệ state M0 chọn đúng action dài hạn (cũ; mới) | cũ ≥ 0,75 và cũ − mới ≥ 0,05 (kiểm hợp lý; zero-fit ở h = ∞ đã cho 0,91/0,71 và 0,83/0,73) |

Định nghĩa đại lượng: G_S, S, M = trường `G_S`, `S`, `M` của dòng; regret = `regret[...]`; F = `d22.F`; P = (h/κ)·|δ|;
M0 chọn đúng action dài hạn = `shares.M0_old` nếu s < 0, ngược lại 1 − `shares.M0_old` (tương tự với `M0_new`).

## 7. Ý nghĩa từng kết cục

- **L72-1 đạt ở cả hai biên độ** → câu C-A đứng như viết. Đạt ở a = 3, trượt ở a = 7,5 → co lại thành "từ khoảng 7·T_int
  ở tải vừa". Trượt cả hai → bỏ "0,1 pp", chỉ giữ phát biểu tiệm cận (toán).
- **L72-2** đạt → biên dải giúp tính trước được ở biên độ mới; trượt → chỉ giữ "dải hẹp" định tính.
- **L72-3** trượt ở a = 7,5 → onset của planner dừng muộn hơn khi T_int lớn; C-C thu về a ≤ 6. **L72-4** trượt →
  "dải co khi burst mạnh" không đứng ở horizon vừa (chỉ còn phát biểu zero-fit ở h = ∞).
- **L72-5/6** đạt → harm không cần mode oracle ở biên độ mới (trong phạm vi N ≤ 3.000); trượt ở a = 7,5 → burst mạnh làm
  mode quan trọng hơn; claim C-D thu về burst yếu/vừa.
- **L72-7** đạt → KO sai đều và tệ hơn M0 nhiều lần ở biên độ mới, ủng hộ C-E; trượt → phần "KO tệ hơn nhiều lần" của C-E
  không chuyển giao. L72-Z trượt → giả thuyết planner ngầm sai ngay ở mức zero-fit/hữu hạn; dừng claim C-E.
- **L72-8** đạt → "hai đồng hồ" đứng ở biên độ mới; trượt (a) → P không phải biến xếp thứ tự chung; trượt (b) → h/T_int
  không hơn h/κ.
- Không có kết luận "đạt" chung: mỗi dự đoán, mỗi biên độ báo riêng (L72-4 là ngoại lệ có chủ đích: một so sánh giữa
  hai biên độ, một verdict).

## 8. Cấm sau khi mở

- Không đổi ngưỡng, tập, khoảng, định nghĩa, file zero-fit hay trần CPU; không chạy lại case UNRESOLVED.
- Không bỏ dòng sau khi thấy kết quả; không thêm dự đoán và gọi là đã khóa.
- Quan sát mới sau khi mở ghi riêng, nhãn "khám phá sau khi mở".
- Kết quả báo là "test theo thẻ do AI soạn theo ủy quyền tác giả"; không ghi là thẻ tác giả tự viết.
