# Thẻ giả thuyết L7.3 — held-out hai thang (ctmc-v2)

> **Provenance.** Doan Van Tai — **bản soạn của AI (Claude) theo yêu cầu "bạn hãy thực hiện giúp tôi luôn đi, đóng vai
> trò là tôi mà thực hiện"** (04/11/2026).
> - Đây **không phải** thẻ do tác giả tự viết: tác giả chưa đọc, chưa sửa, chưa viết lại claim bằng lời mình, chưa tự trả
>   lời câu "nếu chỉ đạt … thì claim còn đứng không". Các câu trả lời trong thẻ là của AI.
> - Mentor chưa review.
> - Theo Lesson 7.3 Phần 2, một test khóa trước theo thẻ agent viết vẫn hợp lệ nhưng không làm G-level đổi (vẫn G1).
>   Kết quả phải được báo là "test theo thẻ do AI soạn theo ủy quyền".
>
> **Chưa khóa.** Chỉ khóa khi tác giả (nên có mentor review trước) đọc thẻ này và
> [`check_l73.py`](../../../experiments/explore_ctmc/check_l73.py), rồi nói "khóa".

## 1. Ngày, nhánh, namespace

- Ngày: 04/11/2026. Nhánh `explore/twoscale-l73`.
- Namespace **ctmc-v2** ([SPEC_v2](../../../experiments/explore_ctmc/SPEC_v2.md)): mỗi path có hai bộ điều biến on-off độc
  lập, đối xứng.
  - Đỉnh a_f + a_s = 6; f = a_s²/(a_f² + a_s²) ∈ {1/20, 1/5, 1/2}; T_s/T_f ∈ {10, 100}; T_f ∈ {1/5, 1}.
  - Tải λ + u ≤ 9; N ≤ 3000.
  - μ = 10, τ = 1, c_sw = 0. P1, S0/S1, D19 và D22 như ctmc-v1.
- **Chỉ đổi một trục so với L7.1** (thêm thang chậm). Burst bất đối xứng để sau.

## 2. Bốn claim (câu abstract)

- **C-1 (đồng hồ).** Với traffic hai thang, T_int của **cả quá trình** vẫn là đồng hồ đúng. Từ khoảng 4–7·T_int, công thức
  zero-fit bậc một dự đoán giá trị của state tươi đối với twin mù horizon tới 0,1 điểm phần trăm của C_ref. Điều này đúng
  với cả T_s/T_f = 10 và 100.
- **C-2 (planner dừng).** Khi h > 7·T_int và δ ≠ 0, một planner dừng không nhìn state có regret không quá 0,1% C_ref, như
  với traffic một thang.
- **C-3 (vùng state kéo dài, rủi ro).** Ở horizon nằm giữa hai thang (h = 10·T_f = T_s/10), state tươi vẫn có giá trị vì
  nó lộ ra mode chậm. M0 với state tươi thắng planner dừng ở đa số regime.
- **C-4 (harm không cần mode oracle, rủi ro).** Harm của state tươi đối với twin mù horizon vẫn xuất hiện khi state mới chỉ
  gồm backlog. Backlog không trở thành "có ích" chỉ vì nó mang thông tin về mode chậm.

## 3. Tập case, trần, cách chạy

| Tập | File (write-once) | Nội dung | Dùng cho |
|---|---|---|---|
| AS | `cases_l73/asym.json` | 100 regime × 13 horizon, h/T_int ∈ {0,3; …; 40} | C-1, C-2, C-4 |
| SO | `cases_l73/sobol.json` | 360 regime × 1 horizon, h/T_int log-đều [0,3; 40] | C-1, C-2, C-4 |
| MID | `cases_l73/mid.json` | 180 regime × 1 horizon, h = 10·T_f = T_s/10 (T_s/T_f = 100) | C-3, C-4 |

- **Không chạy truth cho `xs.json`**: không claim nào dùng nó.
- **Truth:** mọi case của AS, SO, MID dùng `ctmc2.evaluate_d22` (mọi case có N ≤ 3000), để có F, V.
- **Trần:** 900 CPU-s mỗi case (RLIMIT_CPU). Vượt trần thì UNRESOLVED, báo riêng, **không chạy lại**.
- **Một máy duy nhất:** truth chạy một lần, chỉ trên GCP `dt4n-research-01`; runner từ chối máy khác.
  - **Lý do:** control (e) cho thấy hai máy lệch ở bit cuối, tương đối ≤ 1,1e−14, dù mọi quyết định trùng nhau.
  - Số zero-fit đóng băng cũng tính trên cùng máy: `l73/ZEROFIT_2s.csv`, từ `m0_l73_gcp/`, có trường `hosts` trong
    `zerofit_summary.json`.
- **Khi khóa**, sha256 của thẻ, `check_l73.py`, `ctmc2.py`, `scan2.py`, ba case list và hai file zero-fit được ghi vào
  `locks_l73.json`.

## 4. Những gì đã thấy trước khi viết

- **Toàn bộ truth ctmc-v1** của L7.1, D22, L7.2 (a = 3, 6, 7,5). Đây là các số hiệu chỉnh:
  - onset |G_S − z_pred1| ≤ 0,1 pp: 94% / 98% ở (4; 7], 100% ở (7; 15] và (15; 40] (a = 3 / 7,5);
  - regret Static ≤ 0,1% ở h > 7·T_int: 95% / 100%;
  - D22: F < 0 ở 99% / 100% dòng harm có h ≤ T_int;
  - bản đồ twin Stage E: ở h/T_int < 0,3, M0 tươi là twin tốt nhất nhưng Static "đủ" ở 64–94% regime có x < 0 hoặc
    x > 0,5.
- **Zero-fit ctmc-v2 trên 1.051 case, không có truth** ([zerofit_summary](zerofit_summary.json)):
  - T_relax/T_int 1,43–1,91 (5–95%);
  - z_∞ < −0,5 ở 78–90% regime, z_∞ > 0,5 ở 0–8%;
  - **phần backlog z_F,∞/z_∞ trên dòng harm** có trung vị 0,51–0,71 (T_s/T_f = 10) và 0,24–0,63 (T_s/T_f = 100),
    **thấp hơn rõ** so với 0,83–0,90 của ctmc-v1;
  - ở MID, h/T_int chỉ 0,015–0,27, nơi z_pred1 bậc một không dùng được (trung vị từ −69 tới +36).
- **Truth ctmc-v2 chỉ ở hai regime control** C2a, C2b (loại khỏi mọi tập trên). Không có truth nào khác ở ctmc-v2: code từ
  chối bằng PermissionError khi chưa có `locks_l73.json`.
- **Bộ mốc vùng** đã được quyết định trước thẻ ([zone_thresholds_L73.md](../../../notes/realism/zone_thresholds_L73.md)):
  vùng dùng 0,3 / 3·T_int; 4–7·T_int chỉ là onset của z_pred1.

## 5. Quy ước chung

- **Dòng** = (case, h) có status COMPLETED. T_int = T_int lớn nhất trong 4 chain (trường `h_Tint` của file zero-fit).
- **Khoảng h/T_int** nửa mở bên trái: (lo; hi]. **Dòng harm**: G_S < −0,5%. δ = λB − λA. Mọi % là % của C_ref = L11.
- **n tối thiểu:** một dự đoán hoặc một phần có ít hơn 10 dòng đủ điều kiện thì INCONCLUSIVE.
- **UNRESOLVED:** đơn vị là case phân biệt đủ điều kiện theo tham số. Nếu hơn 10% là UNRESOLVED, ERROR hoặc thiếu file
  thì INCONCLUSIVE; ngược lại bỏ các case đó khỏi mẫu số và báo số lượng.
- Mọi "≤", "≥" bao gồm dấu bằng. z_pred1 và h/T_int lấy **nguyên văn** từ `ZEROFIT_2s.csv` (ghép theo stage, id, h).
  **Dự đoán và phép đo cùng một đại lượng ở cùng h:** G_S ở h hữu hạn so với z_pred1 ở chính h đó, không so với z_∞.

## 6. Bảng dự đoán

| ID | Claim | Loại | Tập và điều kiện | Đại lượng | Ngưỡng |
|---|---|---|---|---|---|
| L73-1 | C-1 | onset | AS ∪ SO, **riêng từng** T_s/T_f ∈ {10, 100} và **từng khoảng** (4; 7], (7; 15], (15; 40] (6 phần) | tỷ lệ dòng có \|G_S − z_pred1\| ≤ 0,1 pp | ≥ 0,90 ở (4; 7]; ≥ 0,95 ở (7; 15] và (15; 40]. Đạt khi cả 6 phần đạt. (1; 4] chỉ báo |
| L73-2 | C-2 | onset | AS ∪ SO, δ ≠ 0, h/T_int > 7 | tỷ lệ dòng có regret Static ≤ 0,1% | ≥ 0,90 (báo thêm theo từng T_s/T_f, không chấm) |
| L73-3 | C-3 | rủi ro | MID (h = 10·T_f), mọi dòng (mọi regime có δ ≠ 0) | tỷ lệ dòng có regret(M0, state mới) ≤ regret(Static) − 0,1 pp | ≥ 0,50 (báo thêm theo từng tổ hợp (f, T_f), không chấm) |
| L73-4 | C-4 | rủi ro | AS ∪ SO ∪ MID, dòng harm, h/T_int ≤ 1 | tỷ lệ dòng có F < 0 (D22: L00 − L_cb0 < 0) | ≥ 0,70 (báo thêm theo từng T_s/T_f, không chấm) |

Định nghĩa đại lượng: G_S = trường `G_S` của dòng truth; regret = `regret[...]` (`M0_new`, `static`); F = `d22.F`.

### Câu hỏi "nếu chỉ đạt … thì claim còn đứng không" (AI trả lời thay tác giả)

- **L73-1, (4; 7] ≥ 0,90.**
  - Một thang cho 94–98%. Hai thang thêm một transient chậm, nên chừa chỗ xuống 0,90.
  - Nếu chỉ đạt 0,80, câu "đồng hồ T_int vẫn đúng như một thang" **không đứng**: onset đã muộn hơn. Vì vậy ngưỡng không
    thấp hơn 0,90.
  - Tách theo T_s/T_f vì một phần đạt có thể che một phần trượt.
- **L73-1, (7; 15] và (15; 40] ≥ 0,95.** Ở một thang hai khoảng này đạt 100%. Nếu chỉ còn 0,90, công thức có lệch hệ thống
  ở horizon dài, mà phần đó lẽ ra gần như toán. Claim không đứng.
- **L73-2 ≥ 0,90.** Một thang cho 95–100%. Nếu chỉ đạt 0,80, câu thực dụng "planner dừng đủ dùng" phải thêm điều kiện về
  thang chậm. Claim không đứng như viết.
- **L73-3 ≥ 0,50.**
  - Đây là ngưỡng **đa số**. Theo bản đồ một thang ở h/T_int < 0,3, Static "đủ" ở 64–94% regime có x < 0 hoặc x > 0,5. Nên
    nếu vùng state chỉ như một thang, AI kỳ vọng tỷ lệ M0 tươi thắng Static ≥ 0,1 pp chỉ khoảng 0,2–0,4.
  - Nếu chỉ đạt 0,35, state tươi giữa hai thang có ích ở thiểu số regime, giống một thang. Câu "vùng state kéo dài nhờ mode
    chậm" không đứng.
  - Ngưỡng này **không chắc đạt nhờ zero-fit**: ở MID, z_pred1 không dùng được, và không có số zero-fit nào cho regret.
- **L73-4 ≥ 0,70.**
  - Một thang cho 99–100%. Nhưng zero-fit cho thấy phần backlog của harm ở h = ∞ giảm mạnh với hai thang (trung vị
    0,24–0,71), tức là rủi ro thật.
  - Nếu chỉ đạt 0,60, harm chỉ có backlog không còn là hiện tượng chung. Claim C-4 phải co lại về traffic một thang hoặc
    T_s/T_f nhỏ.
  - Ngưỡng 0,70 giữ như L72-5 để hai lần so sánh được.

## 7. Ý nghĩa từng kết cục

- **L73-1:**
  - đạt cả 6 phần: C-1 đứng như viết;
  - đạt ở T_s/T_f = 10, trượt ở 100: co lại thành "đồng hồ T_int đúng khi hai thang cách nhau tới 10 lần";
  - trượt ở (4; 7] nhưng đạt từ 7: co thành "từ khoảng 7·T_int";
  - trượt cả các khoảng dài: chỉ giữ phát biểu tiệm cận h → ∞ (toán).
- **L73-2:** đạt thì câu thực dụng "planner dừng đủ từ khoảng 7·T_int" chuyển sang traffic hai thang; trượt thì câu đó
  thu về traffic một thang, và cần ngưỡng theo T_relax hoặc T_s.
- **L73-3:** đạt thì vùng state kéo dài tới cỡ T_s, ủng hộ cơ chế "state tươi lộ mode chậm"; trượt thì vùng state giữa hai
  thang vẫn hẹp như một thang, và nhãn vùng chỉ đọc theo h/T_int.
- **L73-4:** đạt thì harm không cần mode oracle, kể cả với thang chậm; trượt thì với thang chậm, backlog-only bớt hại và
  claim C-4 thu về một thang hoặc T_s/T_f nhỏ.
- Không có kết luận "đạt" chung. Mỗi dự đoán báo riêng; các báo cáo phụ theo T_s/T_f hay (f, T_f) không đổi verdict.

## 8. Cấm sau khi mở

- Không đổi ngưỡng, tập, khoảng, định nghĩa, file zero-fit, trần CPU hay máy chạy. Không chạy lại case UNRESOLVED.
- Không bỏ dòng sau khi thấy kết quả. Không thêm dự đoán rồi gọi là đã khóa.
- Quan sát mới sau khi mở ghi riêng, nhãn "khám phá sau khi mở".
- Kết quả báo là "test theo thẻ do AI soạn theo ủy quyền tác giả"; không ghi là thẻ tác giả tự viết.
