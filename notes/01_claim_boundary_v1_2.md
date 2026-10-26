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

## Bổ sung Part A — 24/10/2026

AI triển khai theo yêu cầu tác giả; [T03 v2](theory/T03_primary_reading_start.md)
và [prior boundary](literature/prior_boundary.md) là reference, không L-self.

- GSgivenM1 bằng EVPPI(x|y) dưới G1–G4; GMgivenS1 bằng E_D[VSS(x)] theo
  định nghĩa conditional mean-future problem dưới G2–G5. Nonnegativity và
  Gamma difference-of-gains không là contribution.
- P11 §2.4 Eq2.7–2.8 đã so input/discrepancy information. Không gọi D21 là
  EVMI hoặc model fidelity gồm parameter/structure repair.
- Chỉnh phạm vi C7 v0: fixed-M0 oracle-state gain không luôn bound feasible
  state-repair gain. Riêng M1 tối ưu true cost với matched belief và cùng info,
  GM/GMgivenS1 vẫn bound model repairs cùng info tương ứng. R00 là cận chung,
  không phải cận duy nhất. Đây là E0/proof, toy chỉ verification.
- p_sw band/candidate chưa chứng nhận hai dấu strict của true gap; không kết
  luận GSgivenM1>0 từ nhãn thiết kế đơn độc. D22 fixed-M0 không tự là EVPPI.
- Số 21.952 toy và 17 kiểm P11 không phải output lưới v1.2, network evidence
  hoặc novelty. Predictions là AI-assisted exposed; formal Gate còn HOLD.

## T-H1 — giới hạn diễn giải do horizon hữu hạn, 26/10/2026

AI soạn theo yêu cầu L2.6 Part B; đây là **interpretation threat**, không đổi
objective, contract, thresholds hoặc estimand.

D13 **đã tính** endpoint occupancy, bao gồm Δt·(qA,H+qB,H) và các packet còn
tồn trong horizon. Nó không có một terminal surcharge bổ sung hoặc cost sau h.
Regret/contrasts chỉ định giá window [t0,t0+h]; action để lại backlog có thể
có hậu quả ngoài window chưa được tính. Không diễn giải kết quả như long-run
network loss hoặc total cost cho tới khi mọi packet được phục vụ xong.

P13 journal [§6/tr289](https://ir.cwi.nl/pub/25530/25530.pdf) bàn end-of-period
effect như một explanation có thể; arxivv1 đặt đoạn đó ở §5.3. Không dùng việc
source nói tới congestion còn lại để khẳng định D13 bỏ toàn bộ backlog qH.
Chưa có terminal-cost sensitivity experiment và không tự thêm vào protocol.

Các giới hạn literature đi kèm: P13 Theorem1 cần Lévy/moment/stability conditions;
Prop5 nói normalized cost với continuous capacity choice. S1 quadratic-loss
illustration còn cần smooth density và small constant gap bias, không có từ
riêng p_sw band/finite posterior. Không nhận “initial state matters”, average
so cumulative, VOI≥0 hoặc Γ bookkeeping là contribution. Mọi hypothesis về
mode/F/V/Γ của grid vẫn chờ chạy đúng protocol và audit L2.8/L2.9.

[Note P13](literature/papers/P13.md) · [phép tính/crosswalk](literature/horizon_transient.md)
· [DL-041](02_decision_log.md#dl-041--l26-part-b-prior-và-interpretation-threat-2026-10-26).
