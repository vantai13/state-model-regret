# T11 — Mệnh đề 1: khai triển bậc một của G_S theo h

Doan Van Tai — **AI (Claude) viết theo ủy quyền** ("đóng vai trò là tôi và thực hiện đầy đủ các yêu cầu… đây là mệnh
lệnh", 04/11/2026). Đây là việc A1 của Lesson 7.4. Mentor ghi rõ việc này là của tác giả và không ủy quyền được.
**Bản này không phải tác giả tự dẫn**, không thay cho Understanding. Tác giả cần tự viết lại từng bước (§6).

## 1. Giả thiết

Hai action a ∈ {Stay, Switch}. Mỗi action có một CTMC hữu hạn trên cùng không gian state 𝒳 của mạng (tích hai path),
generator Q_a, tốc độ chi phí f(x) = tổng backlog.

1. **A1.** Mỗi Q_a bất khả quy, có phân phối dừng π_a. Đặt r_a = π_a f. Bias g_a là nghiệm duy nhất của
   −Q_a g_a = f − r_a·1 với π_a g_a = 0.
2. **A2 (P1).** X ~ π_Stay. Y là quan sát cũ, có luật đồng thời với X (ở ctmc-v1, Y là backlog ở t0 − τ).
3. **A3.** Hai quyết định của twin, a_old(Y) và a_new(X) ∈ {0, 1} (1 = Switch), là hàm đo được. Phần (i) dưới đây không
   cần chúng độc lập với h. Phần (ii) cần F_old(h) → F_old, F_new(h) → F_new và B(h) → B khi h → ∞. Với M0 điều này đúng vì
   gap M0 hội tụ về gap ở h = ∞.
4. **A4.** s = r_Switch − r_Stay ≠ 0. Chi phí chuyển c ≥ 0 tính một lần khi Switch.

Ký hiệu:
- V_a(h, x) = E_x[∫_0^h f(X_t) dt] dưới Q_a;
- Δ(h, x) = V_Switch(h, x) − V_Stay(h, x) + c;
- F_old = P(a_old = 1), F_new = P(a_new = 1);
- B = E[(a_old − a_new)(b + c)], với b = g_Switch − g_Stay;
- r_min = min(r_Stay, r_Switch);
- β_C = c + π_Stay b nếu s < 0, và β_C = 0 nếu s > 0.

**Mệnh đề 1.**
- **(i)** Với mọi h > 0: G_S(h) = h·s·(F_old − F_new) + B + R_h, với |R_h| ≤ P(a_old ≠ a_new)·K·e^{−γh}.
- **(ii)** Tồn tại h0 sao cho với h > h0: C_ref(h) = h·r_min + β_C + R′_h, với |R′_h| ≤ K·e^{−γh}.

Do đó z(h) = 100·G_S/C_ref = z_pred1(h) + O(e^{−γh}), với z_pred1(h) = 100(h s ΔF + B)/(h r_min + β_C). Ngoài ra
z_pred1(h) = z_∞ + O(1/h), với z_∞ = 100 s (F_old − F_new)/r_min.

γ > 0 là khe phổ nhỏ hơn của hai generator (trừ một lượng nhỏ tùy ý nếu có khối Jordan). K là hằng số chỉ phụ thuộc
Q_a, g_a.

## 2. Bước 1: V_a(h, x) = h r_a + g_a(x) − (e^{Q_a h} g_a)(x)

Đặt W(h) = h r_a·1 + g_a − e^{Q_a h} g_a. Khi đó W(0) = 0 và:

  dW/dh = r_a·1 − Q_a e^{Q_a h} g_a = r_a·1 − e^{Q_a h}(Q_a g_a) = r_a·1 + e^{Q_a h}(f − r_a·1) = e^{Q_a h} f,

vì Q_a giao hoán với e^{Q_a h} và e^{Q_a h}·1 = 1 (hàng của ma trận chuyển cộng lại bằng 1).

Mặt khác, V_a(0, ·) = 0 và theo phương trình Kolmogorov thuận, dV_a/dh (x) = E_x f(X_h) = (e^{Q_a h} f)(x). Hai hàm
có cùng phương trình vi phân tuyến tính và cùng điều kiện đầu, nên bằng nhau. ∎

Trong code đây là `ctmc.Chain.V`: `out = h*r + g − expm_multiply(Q h, g)`.

## 3. Bước 2: mọi pipeline có L = h·r_Stay + E[a·Δ]

Pipeline (twin, thông tin I) chọn a(I) ∈ {0, 1}. Chi phí thật bắt đầu từ X là
V_Stay(h, X) + a(I)·(V_Switch − V_Stay + c)(h, X), nên:

  L = E[V_Stay(h, X)] + E[a(I)·Δ(h, X)].

Số hạng đầu **đúng chính xác** bằng h·r_Stay: E_{π_Stay}[V_Stay(h, X)] = h r_Stay + π_Stay g_Stay − π_Stay e^{Q h} g_Stay.
Ta có π_Stay g_Stay = 0 (chuẩn hóa), và π_Stay e^{Q_Stay h} = π_Stay vì π dừng. Nên cả hai số hạng sau bằng 0. ∎

Đây là `E_stay = scale = h * r_stay` trong `ctmc.evaluate`, và là lý do mọi L chỉ khác nhau ở E[a·Δ].

## 4. Bước 3: G_S và định nghĩa của B

Theo Bước 1,

  Δ(h, x) = h s + c + b(x) − ε_h(x),  với ε_h = e^{Q_Switch h} g_Switch − e^{Q_Stay h} g_Stay.

Với chuỗi hữu hạn bất khả quy, e^{Q_a h} g_a → 1·(π_a g_a) = 0 theo hàm mũ, nên ‖ε_h‖_∞ ≤ K e^{−γh}.

G_S = L00 − L10 = E[(a_old − a_new)·Δ(h, X)]. Thay Δ vào:

  G_S = (h s + c)(F_old − F_new) + E[(a_old − a_new) b(X)] − E[(a_old − a_new) ε_h(X)]
      = h s ΔF + B + R_h.

Ở đây B = E[(a_old − a_new)(b + c)] gộp cả c, đúng như `B = old[1] − new[1]` trong `ctmc.evaluate_m0`, trong đó
`pair_sum` cộng `v + c` trên tập Switch. R_h = −E[(a_old − a_new) ε_h] và |R_h| ≤ P(a_old ≠ a_new)·K e^{−γh}.

**Phần (i) là đẳng thức chính xác** với mọi cặp quyết định, kể cả quyết định đổi theo h như M0. Giả thiết A3 chỉ cần cho
phần giới hạn. ∎

## 5. Bước 4: truth tiến về action dài hạn; β_C

M1 trên state mới chọn Switch khi và chỉ khi Δ(h, X) < 0 (hòa chọn Stay), nên C_ref = L11 = h r_Stay + E[min(0, Δ)].
Vì 𝒳 hữu hạn, M := max_x |c + b(x)| + K < ∞.

- **s < 0:** khi h > h0 := M/|s|, mọi x có Δ < 0, tức truth luôn Switch. Khi đó:

  C_ref = h r_Stay + h s + c + π_Stay b − π_Stay ε_h = h r_Switch + β_C + R′_h,

  với β_C = c + π_Stay b và R′_h = −π_Stay ε_h = −π_Stay e^{Q_Switch h} g_Switch. Số hạng −π_Stay e^{Q_Stay h} g_Stay
  bằng 0 như ở Bước 2.
- **s > 0:** khi h > h0, mọi x có Δ > 0, tức truth luôn Stay. Khi đó C_ref = h r_Stay **chính xác**, nên β_C = 0 và
  R′ = 0.

Trong cả hai trường hợp h r_Stay hoặc h r_Switch chính là h·r_min, vì action dài hạn là action có r nhỏ hơn. ∎

**Lưu ý về h0.** Với N lớn, max_x |b(x)| lớn (b tăng theo backlog), nên h0 "cho mọi x" có thể rất lớn. Trong thực tế
phần lệch là khối lượng của các state mà truth còn chọn khác action dài hạn. Khối lượng này giảm nhanh khi h/T_int tăng:
`shares.M1_new` = 0,9969 ở 1·T_int và 0,999996 ở 3·T_int (bảng §7). Đây cũng là cơ chế của luật "planner dừng đủ dùng"
(L72-3, L73-2).

## 6. Bước 5: chia hai vế; kiểm bằng số

Đặt N = h s ΔF + B và D = h r_min + β_C. Khi h > h0:

  z − z_pred1 = 100[(N + R_h)/(D + R′_h) − N/D] = 100(R_h D − N R′_h)/(D(D + R′_h)) = O(e^{−γh}),

vì N, D = Θ(h). Và z_pred1 − z_∞ = 100(B r_min − s ΔF β_C)/(r_min(h r_min + β_C)) = O(1/h). Đây là lý do hội tụ về z_∞
chậm (1/h), trong khi z_pred1 khớp z rất sớm (hàm mũ). ∎

## 7. Kiểm bằng số: regime `A_u1-2_lA9_x-1_k1-2` (L7.1 asym, đọc file đã lưu)

λA = 9, λB = 17/2, u = 1/2, κ = 1/2. s = −12,667, r_min = r_Switch = 34,387, β_C = 875,58, T_int = 151 s,
z_∞ = −2,373.

| h (s) | h/T_int | z = G_S (%) | z_pred1 (quyết định ở h) | R_h (packet·s) | C_ref − (h r_min + β_C) | share Switch của truth |
|---:|---:|---:|---:|---:|---:|---:|
| 50,4 | 0,33 | −0,104 | +4,028 | −107,4 | −414,6 | 0,9456 |
| 80 | 0,53 | −0,252 | +2,278 | −91,1 | −266,9 | 0,9774 |
| 151 | 1,00 | −0,591 | +0,408 | −60,1 | −93,7 | 0,9969 |
| 454 | 3,00 | −1,425 | −1,350 | −12,4 | −1,24 | 0,999996 |
| 500 | 3,31 | −1,494 | −1,439 | −9,95 | −0,65 | 0,999998 |
| 1.510 | 9,99 | −2,054 | −2,053 | −0,133 | −6,2e−7 | 1,000000 |
| 4.540 | 30,0 | −2,265 | −2,265 | −1,6e−6 | 0 | 1,000000 |

Nguồn: `results/explore_ctmc/runs/asym/…json` (truth) và `m0/asym/…json` (zero-fit). R_h = G_S·C_ref/100 − (h s ΔF + B).

- **R_h giảm theo hàm mũ.** Từ h = 1.510 tới 4.540 nó giảm 8,2·10⁴ lần, cho 1/γ ≈ 268 s ≈ 1,8·T_int. Điều này khớp với
  T_relax/T_int ≈ 1,4–1,9 đo ở ctmc-v2 (Stage 0 L7.3 §3).
- **Trước khoảng 3·T_int**, C_ref còn lệch hàng trăm packet·s, vì truth chưa chọn hẳn Switch. z_pred1 khi đó sai cả dấu
  (+4,0 so với −0,1). Đây đúng là vùng "onset" (4–7·T_int) mà L73-1 chấm.
- z_pred1 tính với quyết định ở h và với quyết định ở h = ∞ trùng nhau từ h ≥ T_int (cột `z_pred_first_order_inf_decisions`
  của file truth).

## 7b. Nguồn chuẩn (mentor review 04/11: T11 là công cụ, không phải đóng góp)

- Bước 1 (V = h r + g − e^{Qh} g) và vai trò của bias g là khai triển gain/bias chuẩn của bài toán chi phí trung bình.
- Trích: M. L. Puterman, *Markov Decision Processes: Discrete Stochastic Dynamic Programming*, Wiley, 1994,
  DOI 10.1002/9780470316887. Chương 8 "Average Reward and Related Criteria", tr. 331–440, DOI 10.1002/9780470316887.ch8.
- **Mức đọc: metadata-only** (Crossref, 04/11/2026). Mục cụ thể (phương trình đánh giá, khai triển Laurent) và phiên bản
  thời gian liên tục (có thể ở chương khác) **chưa kiểm**. Cần đọc trước khi trích số mục trong paper.

## 8. Phạm vi và việc của tác giả

- Chứng minh dùng không gian state hữu hạn (N cắt). Với chuỗi vô hạn cần thêm điều kiện để g_a tồn tại, ‖ε_h‖ giảm
  đều và b bị chặn trên tập khối lượng; chưa làm.
- Phần (i) là kế toán chính xác; không nói gì về dấu của ΔF hay B. Dấu là việc của cơ chế "planner ngầm" (chưa chứng minh).
- **Tác giả tự làm (OPEN):** viết lại Bước 1–5 bằng lời của mình, kín sách; tự giải thích vì sao E_π[V_Stay] = h r_Stay
  đúng chính xác; tự tính lại một dòng của bảng §7. Chưa có record nào ghi tác giả đã làm.
