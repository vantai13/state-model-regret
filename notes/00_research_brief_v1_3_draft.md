# Research brief v1.3 — DRAFT sau Gate A REFORMULATE

Người phụ trách: **Doan Van Tai** · 28/10/2026 · DL-061.
AI soạn theo yêu cầu chuẩn bị thiết kế mới; chưa là brief tác giả tự viết/duyệt.
Không thay [brief v1.2](00_research_brief_v1_2.md) đi cùng kết quả Phase3.

**Main RQ giữ câu chữ:** For load-changing routing actions, how do improvements in
current-state information and action-response model fidelity differ and interact
in their effect on expected decision regret?

**Phạm vi đề xuất mới:** định giá state/model repair qua một phân phối observations
đã khai báo, thay vì chỉ điều kiện theo một snapshot cố định trong mỗi ô. Controller
S0 thay quyết định theo observation; S1 biết state nhưng không future. Gain và Γ vẫn
được xây từ bốn expected costs. D13 window cost và D21 stochastic-representation repair
được đề xuất giữ để nối với baseline; chưa mở sang parameter/structure repair.

**Evidence dẫn tới lựa chọn:** Phase3 kỹ thuật đạt, PC4 nội suy WEAKEN (d≈0,247<0,25pp),
ngoại suy FALSIFY; K5 bị R04 bác; C1 đứng bốn ô với base rate cao. Những kết quả này
không chứng minh Γ vô nghĩa hoặc population design sẽ thành công; REFORMULATE là
quyết định chuẩn bị câu hỏi/estimand mới của tác giả, ghi ở [Gate A](phases/PHASE_3_gate.md).

**Việc còn mở trước thực thi:** joint law P(Y,X), support/tail, normalization, grid,
metric/threshold, model/null/fit budget, numerical bounds và split mới. Chi tiết ở
[contract proposal](01_definitions_v1_3_draft.md). Không dùng q50/q90 làm population
đầy đủ hoặc 10 R đã mở làm test sạch cho hypothesis mới; R09/R10 giữ niêm phong.

**Phase4 thực thi HOLD:** cần P0-V10 và contract mới khóa; học/chuẩn bị được tiếp.
G1, giới hạn ideal plant, D13 không cost sau h và quyền thông tin giữ rõ. Chưa có
network evidence, validation, novelty, effect causal của từng trục hoặc hypothesis
mới được chứng minh trong thiết kế đề xuất.
