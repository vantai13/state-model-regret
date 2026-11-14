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

## Đính chính sau audit độc lập (14/11/2026, DL-146)

AI (Claude) ghi theo ủy quyền. Nguồn: `notes/ops/codex/AUDIT_report.md` mục B1–B3. Claude đã kiểm lại B1 bằng giải tích. Tác giả chưa tự kiểm.

1. **Mệnh đề chỉ nói G_S(h) = O(1)**, tức không có số hạng tăng theo h. Nó **không** nói G_S ≥ 0, cũng không nói |G_S| < 0,25% C_ref ở h hữu hạn.
   - Phản ví dụ: CTMC hai trạng thái đối xứng (T_int = 1/2), dừng và trộn, dùng một policy cố ý sai. Ta có G_S = −(1 − e^{−2h})(1 − e^{−2τ})/4, nên tại τ = 1 là **−1,44% E_stay ở h = 30 T_int** và −0,14% ở 300 T_int.
   - Vì vậy hệ quả 2 phải đọc là: twin plug-in không bị hại **tăng theo h**. Một hại bị chặn vẫn có thể vượt ngưỡng thực tế ở h vừa phải.
2. **Lỗ hổng trong phép dẫn.** Bước thay D(h) bằng E[D | Z_t] trong tích với a′ = φ(O(Z_{t−τ})) cần hai điều kiện:
   - Z_t phải đủ để biết chi phí tương lai khi đã biết quá khứ (Markov với state đầy đủ);
   - phần dư o(1) phải đều theo state.

   Nếu Z thiếu memory, đẳng thức sai. Ví dụ iid của audit: G thực = 0, còn vế phải = −0,5. CTMC đầy đủ state của repo thỏa điều kiện này, nhưng traffic thật thì chưa chắc.
3. **Phép thử đúng nội dung T12** là hại của plug-in không tăng từ h = 10 lên h = 30 T_int, chứ không phải ngưỡng −0,25% tại 30 T_int. Phép thử này là D6 của EV-D4.
   - Dữ liệu EV-D3 (post-hoc, mô tả), τ = 30 s: |G(30T)|/|G(10T)| ≈ 1,05–1,11 cho plug-in, so với 1,8–2,7 cho nowcast. Kết quả này hợp với T12.
   - Ở τ = 300 s trên trace 2, plug-in đổi dấu (+0,45% → −0,58%). Kết quả này chưa giải thích được.
4. **Trace lặp tuần hoàn thì tương quan không bao giờ tắt.** Vì vậy "thang trộn chậm nhất" trong báo cáo wave 3 chưa được đo, và không được dùng như một điều kiện đã chứng minh.
