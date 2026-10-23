# Thử nghiệm REFORMULATE lưới — kế hoạch viết trước khi tính

> **Provenance.** Claude (AI) soạn và chạy theo yêu cầu của **Doan Van Tai** ngày 23/10/2026 ("REFORMULATE Phase 1 … chạy thử nghiệm trên một nhánh khác, tìm cách hiệu quả nhất"). Tác giả chưa xác nhận nội dung. Đây là **DISCOVERY trên nhánh `explore/reformulate-grid`**, không phải preregistration chính thức, không thay đổi `main`, không tạo tag.
>
> File này được commit **trước** mọi phép tính của thử nghiệm.

## 1. Câu hỏi

Cách đặt lưới nào cho Phase 3 một bộ ô mà (i) câu hỏi Stay/Switch thật sự có tranh chấp, (ii) ổn định khi làm mịn slot, (iii) nằm trong ngân sách máy tính tới dt/16, và (iv) vẫn phủ các trục của RQ1 — để Phase 3 không phải quay lại Phase 1?

## 2. Được tính và bị cấm

| Được tính (chỉ dùng plant) | Bị cấm |
|---|---|
| Chứng chỉ prior dừng, D/support | $J$, $L_*$, $C_{\text{ref}}$, margin hay độ lớn $\Delta$ |
| Khoảng $p_{\text{sw}}=P_D(a^*=\text{Switch})$ (chỉ dấu) | Belief, $M_0$, $M_1$, pipeline, regret, mọi contrast |
| Nhãn ĐK1, budget, đơn vị lattice, thời gian chạy | Lưu bất kỳ giá trị nào theo từng state |

Mọi ô đã tính được ghi vào `exposure.csv` (ô, $\lambda_A$, mức dt, khoảng $p_{\text{sw}}$).

## 3. Tọa độ được bảo vệ (để dành held-out, không tính ở đây)

Thử nghiệm chỉ dùng: $\kappa\in\{0{,}3;1;3\}$; quantile $y_B\in\{0{,}5;0{,}9\}$; quantile $y_A\in\{0{,}5;0{,}9\}$; $\eta\in\{0{,}5;0{,}75\}$; horizon $\in\{r_h=1;\ h=2;\ h=8\}$ (giây, age = 1). Mọi tọa độ khác — ví dụ $\kappa\in\{0{,}6;2;4\}$, quantile 0,75, $\eta$ giữa 0,5 và 0,75, $h\in\{4;16\}$ — **không được tính** trong thử nghiệm này, để còn dùng làm held-out sạch.

## 4. Giữ nguyên

Thước đo (ĐK8); plant v1.1: $\mu=10$, nền B OFF 2/ON 14 ($\lambda_B=8$), nền A $\lambda_A\pm6$ không đổi theo $u$, age 1 s, R2, D dừng có điều kiện, một observation mỗi ô; dt $=1/120$ và $1/240$; khoảng $[0{,}1;0{,}9]$; solver phổ và engine idle-gap đã kiểm.

## 5. Năm thủ tục thiết kế được so sánh

| Mã | Cách đặt $\lambda_A$ | Horizon |
|---|---|---|
| P0 | Lưới v1.1 sau redesign (dữ liệu cũ, không tính lại) | $r_h=1$ |
| P1 | Đối xứng trước quyết định: $\lambda_A=\lambda_B-u$ (A và B giống hệt trước quyết định) | $r_h=1$ |
| P2 | Như P1 | $h$ vật lý $\in\{2;8\}$ s |
| P3 | **Neo theo ranh giới**: chọn $\lambda_A$ trên thang để $p_{\text{sw}}$ gần mục tiêu | $r_h=1$ |
| P4 | Neo theo ranh giới | $h$ vật lý $\in\{2;8\}$ s |

**Lát (slice).** $\kappa(3)\times y_B(2)\times\eta(2)\times$ horizon(3) với $y_A=q90$: 36 lát; thêm $y_A=q50$ ở $\kappa=1$: 12 lát.

**Thang $\lambda_A$.** $6;\ 6{,}25;\ \dots$ đến giá trị lớn nhất có $(\lambda_A+u)/\mu\le0{,}95$. Lý do: OFF của A không âm cần $\lambda_A\ge6$; bước 0,25 giữ lattice đơn giản.

**Luật neo (P3, P4).** Mục tiêu $t\in\{0{,}3;0{,}7\}$. Chọn điểm thang có $p_{\text{sw}}$ ở dt thô gần $t$ nhất; hòa thì chọn $\lambda_A$ nhỏ hơn. Ô được neo nếu $p_{\text{sw}}$ ở **cả hai** mức dt nằm trong $[t-0{,}15;\ t+0{,}15]$.

## 6. Chỉ số so sánh

1. Tỉ lệ ô chính có $p_{\text{sw}}$ ở cả hai mức dt trong $[0{,}1;0{,}9]$, và khoảng cách nhỏ nhất tới mép.
2. Tỉ lệ lát neo được (P3, P4).
3. Budget: số ô vượt $2\times10^{11}$ phép cập nhật ở dt/16 (công thức budget của A2).
4. Độ phủ trục: số mức của $\kappa$, $y_B$, $y_A$, $\eta$, horizon, $\psi$ trong tập ô đạt.
5. Độ trôi $p_{\text{sw}}$ giữa dt và dt/2.
6. Nội suy: dự đoán $\lambda_A$ neo ở $\kappa=1$ từ $\kappa=0{,}3$ và $3$ (nội suy theo $\log\kappa$); kiểm $p_{\text{sw}}$ tại điểm dự đoán. Đây là phép thử xem held-out có thể đặt bằng nội suy mà không cần screen hay không.

## 7. Luật khuyến nghị (viết trước)

Ưu tiên theo thứ tự:
1. **Không vòng lặp**: $\ge90\%$ ô chính đạt chỉ số 1, và mọi ô chính trong budget tới dt/16.
2. **Độ phủ**: mỗi trục RQ1 có $\ge2$ mức trong tập ô đạt.
3. Ít thay đổi so với contract hiện có.
4. Ít exposure.

Kết quả là **đề xuất cho tác giả**. Việc áp dụng vào `main` cần tác giả quyết, một DL và một protocol chính thức viết trước khi chạy lại.
