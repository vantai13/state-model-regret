# Protocol lưới v1.2 — viết và commit trước lần chạy chính thức

Người phụ trách: **Doan Van Tai** · 23/10/2026. Quyết định: [DL-038](../02_decision_log.md). Bằng chứng thiết kế: [báo cáo thử nghiệm](../explore/reformulate_grid_report.md) (DISCOVERY, merge `87dcd53`).

> **Provenance.** Văn bản do AI soạn theo yêu cầu thực hiện của tác giả ngày 23/10. Tác giả quyết định áp dụng nhưng chưa tự viết lại lý do bằng lời mình (PHASE_1 §5.4, luật 5). Đây là mục còn mở, không phải bằng chứng hiểu kín sách.

## 1. Giữ nguyên

- Thước đo ĐK8: $\varepsilon_R$ 1% (độ nhạy 0,5% và 2%), $\varepsilon_E$ 0,5%, dung sai làm mịn 0,25%, $C_{\text{ref}}=L_*$ theo ô và theo dt, objective cumulative occupancy, luật hòa Stay.
- Plant v1.1: A ON/OFF $\lambda_A\pm6$, B OFF 2/ON 14, $\mu=10$, age 1 s, R2, D dừng có điều kiện, một observation mỗi ô, B2 với belief dùng chung, định nghĩa $M_0/M_1$.
- Solver phổ, engine idle-gap, budget A01: $\le2\times10^{11}$ phép cập nhật và $\le4$ GiB mỗi ô mỗi mức, tới dt/16.

## 2. Trục thiết kế

| Trục | Mức |
|---|---|
| $\kappa=T_{\text{mode}}/\text{age}$ | 0,3; 1; 3 |
| Quantile quan sát B | q50; q90 |
| Quantile quan sát A | q90 ở lõi; q50 ở nan hoa |
| $\eta$ (tải chuyển / dư địa B) | 0,5; 0,75 |
| Horizon vật lý $h$ | 8 s ở lõi; 2 s ở nan hoa |
| Mục tiêu $p_{\text{sw}}$ | 0,3; 0,7 |

$\lambda_A$ **không** còn là trục thiết kế. Nó được chọn cho từng lát bằng luật neo ở §3. Các đại lượng $\psi=(\lambda_A-8)/10$, $\delta=(\lambda_A+u-8)/10$ và $r_h=h/T_{\text{drain}}^{\text{post},B}$ được tính và báo cáo như tọa độ dẫn xuất.

## 3. Luật neo (`src/smr/anchoring.py`)

1. **Thang:** $\lambda_A\in\{6;\,6{,}25;\,\dots\}$, tới giá trị lớn nhất có $(\lambda_A+u)/\mu\le0{,}95$. Đáy 6 là giới hạn vật lý (OFF của A không âm với biên độ ±6); không mở thang xuống dưới.
2. **Chọn:** điểm có trung điểm $p_{\text{sw}}$ ở dt gần mục tiêu nhất; hòa thì chọn $\lambda_A$ nhỏ hơn.
3. **Chấp nhận:** khoảng $p_{\text{sw}}$ nằm trong $[t-0{,}15;\ t+0{,}15]$ ở cả dt và dt/2.
4. **Báo cáo, không dùng để chấp nhận:** độ lệch $|p-t|$; `bracketed` / `floor` / `ceiling` (mục tiêu có bị kẹp giữa hai điểm thang không); điểm có nằm ở đáy hay đỉnh thang không.
5. Hai mục tiêu chọn cùng $\lambda_A$ thì thành một ô. Một (lát, mục tiêu) không đạt được ghi là thất bại. **Không** thử $\lambda_A$ khác, không thêm lát.

## 4. Ô chính — 20 lát, kỳ vọng 38 ô

| Lát | Nhóm | $\kappa$ | A | B | $\eta$ | $h$ |
|---|---|---|---|---|---|---|
| V01–V12 | lõi | 0,3 / 1 / 3 | q90 | q50 / q90 | 0,5 / 0,75 | 8 |
| V13–V16 | nan hoa A q50 | 1 | q50 | q50 / q90 | 0,5 / 0,75 | 8 |
| V17–V20 | nan hoa h 2 s | 0,3 | q90 | q50 / q90 | 0,5 / 0,75 | 2 |

Thứ tự lát và mã ô: theo $\kappa$, rồi B, rồi $\eta$, rồi $\lambda_A$ tăng dần (M01–M38). Định nghĩa chính xác nằm trong `experiments/lessons/run_v1_2.py`.

**Tái lập bắt buộc.** Các lát này đã được tính trong thử nghiệm, nên lần chạy chính thức phải khớp **tuyệt đối** với `results/explore_reformulate/`: khoảng $p_{\text{sw}}$ ở dt, dt/2 và dt/4, $y_A$, $y_B$, $H$, budget, nhãn ĐK1, và tập ô phải trùng `proposed_v1_2_cells.csv`. Lệch bất kỳ chỗ nào thì lưới **NOT_ACCEPTED** và HOLD; không sửa bằng cách dò lại.

**Chấp nhận lưới:** đủ 38 ô; mỗi ô nằm trong $[0{,}1;0{,}9]$ ở dt, dt/2 và dt/4; nhãn ĐK1 `candidate` ở dt và dt/2; khối lượng chưa phân giải $\le0{,}01$; budget trong trần ở dt/16.

## 5. Held-out — tọa độ khai báo trước, chưa từng được tính

| Lát | Mục đích | $\kappa$ | A | B | $\eta$ | $h$ |
|---|---|---|---|---|---|---|
| H01 | nội suy $\kappa$ | 0,6 | q90 | q50 | 0,5 | 8 |
| H02 | nội suy $\kappa$ | 2 | q90 | q90 | 0,5 | 8 |
| H03 | nội suy quantile | 1 | q90 | q75 | 0,5 | 8 |
| H04 | nội suy $\eta$ | 1 | q90 | q50 | 0,625 | 8 |
| H05 | nội suy horizon | 0,6 | q90 | q90 | 0,5 | 4 |
| H06 | ngoại suy horizon | 0,3 | q90 | q90 | 0,5 | 12 |

1. Neo bằng đúng luật §3 với cả hai mục tiêu. Ô đạt được kiểm ở dt/4 và gắn nhãn ĐK1 (mã R01, R02, …).
2. (Lát, mục tiêu) không neo được thì ghi **out**. Không thay bằng ô khác.
3. Không tính contrast. Held-out không dùng cho discovery hay calibration.
4. $p_{\text{sw}}$ và $\lambda_A$ riêng của held-out **không** được làm biến đầu vào cho $H_0/H_1$, trừ khi cùng biến đó được định nghĩa cho mọi ô.
5. Ô vượt trần budget ở dt/16 chỉ được dùng ở mức dt mà A01 chọn nếu tại mức đó vẫn trong trần; nếu không, ô đó HOLD.

## 6. Ô kiểm âm và đầu dò cấu trúc

- N01–N04, W01, S01 giữ nguyên định nghĩa trong `grid_v1_1_redesign_candidate.json`. Nhãn kỳ vọng (theo v1.1): N01, N02 SD-cell; N03, N04 conservation-cell; W01, S01 WD-cell. Ở SD-cell và conservation-cell, sáu contrast phải bằng 0 chính xác (kiểm ở Phase 3; sai lệch là bug).
- Đầu dò P01: $\kappa$ 3, B q90, $\eta$ 0,5, $h$ 2, $\lambda_A$ 7 — kỳ vọng conservation-cell. P02: $\kappa$ 1, B q90, $\eta$ 0,5, $h$ 2, $\lambda_A$ 8 — kỳ vọng WD-cell. Chỉ báo cáo; không tính vào luật chấp nhận.

## 7. Calibration A01

Trong các ô lõi đủ điều kiện (trong dải ở ba mức, `candidate`, trong budget), chọn ba ô khác nhau, hòa thì chọn mã nhỏ hơn:
- **C1:** $\kappa$ nhỏ nhất, rồi $y_B/(2-u)$ nhỏ nhất (drain sau Switch ngắn nhất so với dt).
- **C2:** gần tâm lõi nhất theo các trục chuẩn hóa ($\log\kappa$, $\eta$, quantile B, mục tiêu).
- **C3:** budget lớn nhất ở dt/16, để A01 kiểm được mức tốn kém nhất.

Ô calibration không dùng làm confirmation.

## 8. Khóa

Nếu lưới được chấp nhận: viết contract, claim boundary và brief v1.2; chạy sáu kiểm nhất quán và full test suite; cập nhật closeout Gate 1; tạo tag có chú thích `contract-v1.2` (không dùng `-f`). Mọi thay đổi sau đó thành `v1.2.x` kèm DL.

## 9. Diễn giải bắt buộc (chép sang claim boundary)

1. So sánh giữa các điều kiện là ở **cùng độ khó** ($p_{\text{sw}}$ gần mục tiêu), không phải cùng tải. $\lambda_A$ thay đổi theo điều kiện, nên khác biệt giữa hai lát không được quy riêng cho $\kappa$, $y_B$ hay $\eta$.
2. $\psi$ là đại lượng dẫn xuất và gần như một phía (khoảng $[-0{,}20;+0{,}05]$ trong thử nghiệm). Kết luận chỉ áp dụng cho vùng này.
3. Kết quả có điều kiện "gần ranh giới quyết định". Đây là chọn mẫu có chủ đích, không đại diện tần suất trong mạng thật.
4. "Cùng độ khó" chỉ là xấp xỉ: báo $p_{\text{sw}}$ thực của từng ô, không coi như đúng 0,3 hay 0,7.
5. Nan hoa $h=2$ s chỉ có ở $\kappa=0{,}3$. Ở $\kappa\ge1$, horizon này bị khóa bởi cấu trúc (conservation hoặc WD), nên mọi claim về horizon ngắn chỉ cho $\kappa$ thấp.
