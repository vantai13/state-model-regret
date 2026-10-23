# Claim boundary v1.2

Người phụ trách: **Doan Van Tai** · 23/10/2026. Bổ sung cho [boundary v0](01_claim_boundary_v0.md) và thay [bản nháp v1.1](01_claim_boundary_v1_1_draft.md). Đi cùng [contract v1.2](01_definitions_v1_2.md) và [lưới v1.2](design/grid_v1_2.md).

> **Provenance.** Do AI soạn theo yêu cầu thực hiện của tác giả; tác giả chưa tự viết lại (PHASE_1 §5.4, luật 5).

## Được claim (có điều kiện, trong mô hình lý tưởng đã khai báo)

| Claim | Bằng chứng |
|---|---|
| Trong plant của contract, hai action chỉ khác cost qua capacity bỏ phí; vùng bảo toàn cho mọi contrast bằng 0 (E0, đã biết) | L1.2, ĐK1, ô N03/N04/P01 |
| Với một observation mỗi ô và belief đúng: $G_M=\lvert E\Delta\rvert\cdot\mathbf 1[a_{00}\ne a_{01}]$, $G_{S\mid M_1}=\min(E\Delta^+,E\Delta^-)$ (E0) | T01 |
| $G_{S\mid M_1}$ có dạng EVPPI có điều kiện theo observation (đối chiếu toán học, không phải khái niệm mới) | T03 |
| Trong plant này, ranh giới quyết định của oracle dịch theo quantile backlog B và $\kappa$; một tải A chung không đặt được mọi ô vào vùng có quyết định thật | Thử nghiệm REFORMULATE (DISCOVERY, chỉ $p_{\text{sw}}$) |
| Horizon ngắn (2 s) với mode kéo dài làm quyết định bị khóa bởi cấu trúc (conservation hoặc WD) | Nhãn ĐK1 của đầu dò P01, P02 |

## Chưa được claim

- Bất kỳ giá trị nào của $G_S$, $G_M$, $\Gamma$ hay regret: **chưa tính** ở ô nào.
- Hiệu ứng riêng của $\kappa$, quantile B hay $\eta$: các lát ở **cùng độ khó**, không cùng tải, và $\lambda_A$ đồng biến với điều kiện.
- Kết luận cho vùng A nặng hơn B: $\psi$ của lưới nằm trong $[-0{,}2;+0{,}05]$, gần như một phía.
- Tần suất các hiệu ứng trong mạng thật: lưới chọn có chủ đích gần ranh giới quyết định.
- Claim về horizon ngắn ở $\kappa\ge1$.
- Bất kỳ kết luận mạng thật, novelty hay khuyến nghị vận hành. Gap vẫn ở **G1**.

## Ghi chú diễn giải

- $p_{\text{sw}}$ trong $[0{,}1;0{,}9]$ giới hạn trên giá trị state, nhưng không bảo đảm gain vượt $\varepsilon_R$. Gain nhỏ ở Phase 3 là một kết quả hợp lệ.
- $p_{\text{sw}}$ trong dải chưa đủ để có bài toán quyết định: phải kèm nhãn ĐK1 `candidate`. Ô WD có thể có $p_{\text{sw}}$ trong dải chỉ vì hòa.
- Ô oracle-hằng (WD) vẫn có thể có $G_M>0$; giữ chúng cho nhánh model.
- State repair gồm thấy cả hai mode; phần "thấy mode" không phải lợi ích của refresh telemetry backlog (D22).
- Exposure: $p_{\text{sw}}$, nhãn và budget của thử nghiệm đã công khai trên GitHub; contrast chưa ai thấy.
