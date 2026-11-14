# T12 — Plug-in under stationarity: when freshness alone cannot cause long-horizon harm

Doan Van Tai — **AI (Claude) dẫn theo ủy quyền** (14/11/2026). Phép dẫn chưa được tác giả tự kiểm. Đây không phải
author-self, không phải novelty claim.

## Phát biểu

**Thiết lập.**
- Hệ dừng Z_t. Thông tin quan sát được là một hàm O của trạng thái: tươi I = O(Z_t), cũ I′ = O(Z_{t−τ}).
- Một pipeline là ánh xạ a = φ(·) ∈ {0 (Stay), 1 (Switch)}.
- D(h) là chênh chi phí thật Switch − Stay trên [t, t + h].

**Giả định.** Hệ trộn với thời gian tích phân hữu hạn:

  E[D(h) | Z_t] = h·s + b(Z_t) + o(1) khi h → ∞, với E|b| < ∞

(Poisson/T11; ctmc-v1 thỏa).

**Mệnh đề.** Nếu pipeline cũ là **plug-in**, tức cùng φ áp lên dữ liệu cũ (a′ = φ(O(Z_{t−τ}))), thì

  G_S(h) = E[(a′ − a)·D(h)] = E[(a′ − a)·b(Z_t)] + o(1) = O(1).

Nghĩa là G_S bị chặn khi h tăng; tính theo %C_ref ∝ h, nó → 0.

**Chứng minh (một dòng).**
- G_S = h·s·(P(a′ = 1) − P(a = 1)) + E[(a′ − a)·b] + o(1).
- Theo tính dừng, O(Z_{t−τ}) và O(Z_t) cùng phân phối, nên P(a′ = 1) = P(a = 1): số hạng h·s triệt tiêu. ∎

## Hệ quả cho đề tài

1. **Harm tăng theo h cần bất đối xứng giữa pipeline cũ và mới.** Có hai dạng:
   - xử lý theo tuổi dữ liệu: posterior Bayes (contract S0), nowcast/Kalman co về trung bình;
   - thông tin khác loại: dữ liệu tươi lộ mode/burst ẩn mà dữ liệu cũ không có (contract S1 có mode).

   Khi có bất đối xứng, luật bậc một h·s·(F_old − F_new) + B dự đoán G_S (T11).
2. **Twin "ngây thơ"** (cắm số liệu cũ như số liệu mới) không bị telemetry tươi làm hại ở horizon dài; state tươi chỉ đổi số hạng transient.
3. **Vòng kín** (EV-A): mỗi quyết định chỉ có stake Δ·s, còn số hạng transient đóng góp khoảng E[g]/Δ vào tốc độ chi phí. Khi Δ ≲ T_int, số hạng transient áp đảo và dấu có thể đảo.

## Bằng chứng số (exploration, ủy quyền)

| Đối tượng | Kết quả |
|---|---|
| EV-D, twin plug-in (fluid, ratefluid) | Pilot 9/9 không có harm ở 30 T_int, trên ba lớp traffic (MMPP, ON/OFF exponential, ON/OFF Pareto); panel xem RESULTS EV-D |
| EV-D, twin nowcast (co về trung bình) | Có harm; dấu và độ lớn theo luật bậc một |
| ctmc-v1, contract S0 (Bayes) so với S1 (có mode) | Harm (C3), theo luật bậc một (C1) |

## Giới hạn

- Cần tính dừng tại thời điểm quyết định. Quyết định theo alarm (EV-B) phá điều này: quần thể state bị chọn khác đi.
- Cần thời gian trộn hữu hạn. Heavy-tail không cắt đuôi (T_int vô hạn) nằm ngoài phát biểu.
