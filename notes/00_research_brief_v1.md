# Research brief v1

Tác giả: **Doan Van Tai** · 22/10/2026 · **TECHNICAL FREEZE CÓ ĐIỀU KIỆN**.
Định nghĩa: [contract v1](01_definitions_v1.md); thiết kế: [annex](design/grid_v1.md).
Đây là bản viết để kiểm và trao đổi; chưa phải bài tác giả tự viết lại hay record read-back.

Chuyển một lượng traffic từ A sang B làm A nhẹ đi và B nặng thêm. Twin dùng observation cũ để suy state hiện tại rồi dự báo cost hai action. Sai state và dùng mean traffic có thể làm chọn action khác; giảm prediction error không mặc nhiên giảm decision regret. Câu hỏi là hai repair riêng và chung thay đổi regret ở điều kiện nào, với cùng objective và law.

**Main RQ:** *For load-changing routing actions, how do improvements in current-state information and action-response model fidelity differ and interact in their effect on expected decision regret?*

**RQ1** mô tả GS,GM,GSM,Γ và conditional gains (D19) theo tải chuyển/headroom, backlog quan sát, horizon và persistence biết trước action. **RQ2** so sức dự báo held-out của threshold null H0 và giải thích queue H1 (D25). **RQ3** kiểm feasible net gain so εR và baseline mạnh. Scope model fidelity chỉ là biểu diễn randomness, cùng θ đúng (D21), không sửa parameter/TCP/structural error.

Primary objective là cumulative endpoint queue occupancy packet·s (D13), oracle biết state/law nhưng không realized future (D15). Regret và contrasts (D18–D19) dùng chung D, action set và oracle. Secondary1000L/E[N] ms/packet là cùng đại lượng trên expected packets ban đầu+các arrivals, không completed-packet mean delay. Reference Lstar cùng ô/cùng dt; εR1% với sensitivity.5%/2%, εE.5%, numerical budget.25% (D23–D24). Ngưỡng là convention, chưa phải SLA.

Lưới đã chọn: 24 main cells z={1/3,1,3,10},κ={.3,1,3},η={.5,.9},ρB.8,h=Tdrain_post; thêm2negative/2stress, không bỏ ô theo outcome. D12 condition stationary B tại backlog đo, với profile OFF.2μ/ON1.4μ; A deterministic.5μ và khởi tạo kiểm soát. D8 backlog không nhiễu có timestamp, mode ẩn. S0 posterior B2 cùng prior D (D9); M0 load-aware mean rollout từng state, M1 exact law (D10); S giữ cố định giữa model. Main State repair gồm age+mode; D22 tách current-backlog với model cố định. Reserve16 tọa độ chưa sinh/scored; calibration3 ô đã khai báo, final dt chờ A01.

**Chuỗi lập luận đã có, chưa là network claim:** (1) B toy GS thay .9296875→.307151637 khi refine1→128; (2) clipping và endpoint convention khiến discretization thay action/cost, không chỉ đổi nhãn đơn vị; (3) vì thế mọi bản đồ gains cần kiểm refinement nhỏ hơn vùng equivalence; (4) HC1 chỉ khóa **khung** dự báo bằng observables, không khóa một hình dạng từ toy; (5) HC1 bị bác nếu predictor đã khóa không thắng constant predictor trên held-out theo metric/biên A05. Richardson GS≈.302699661 chỉ estimate của toy. Mode share17.81% ở fixed-M0 split m128; không dùng≈11% của hybrid làm evidence cho State-only. Những con số này là verification/discovery đã exposed, không confirmation.

**HC1 (khung):** observable-coordinate map dự báo conditional gains/magnitude Γ tốt hơn constant predictor fit chỉ discovery/calibration. Metric, target normalization, biên thắng và split khóa A05 sau discovery, trước confirmation. HC1 fail không làm mất giá trị descriptive RQ1.

**HM1 (khung):** H1 dự báo gains held-out tốt hơn H0 đã đóng băng, cùng quyền thông tin, ngân sách fit và targets. Đủ-dùng/null được kiểm bằng biên sai số khai báo; p>.05 không chứng minh equivalence. A05 phải khóa metric trên đúng đơn vị, không áp εE trực tiếp cho MSE có đơn vị bình phương. Nếu H0 đã đủ và H1 không cải thiện vượt biên, không claim queue dynamics có predictive value thêm.

**HP1 (khung):** ở domain có R00 headroom đủ, feasible repair net gain vượt εR và baseline load-aware/age-aware mạnh. Chi phí/timing phải cùng đơn vị/objective; Phase8 khóa operator và operational threshold. Cận trên R00 dưới εR là cheap kill cho domain; gain của một diagnostic endpoint không phải cận trên mọi feasible pipeline.

Giả định nguy hiểm nhất là **AS1 — background ngoại sinh**: real traffic phản hồi TCP/action có thể làm sai toàn bộ counterfactual. Thứ hai là backlog observation lý tưởng D8 và timing tức thời AS4; thấy mode là oracle diagnostic, chưa có feasible sensor. Path rời, fixed action, fluid/infinite queues, θ đúng hạn chế claim. Nhiều controller, TCP, tail/loss/safety, routing nhiều bước, shared bottleneck nằm ngoài scope.

Gap vẫn **G1/candidate**. Các identity và negative controls xác nhận implementation logic, không chứng minh novelty hoặc practical value. Phase2a còn phải đọc primary P11–P13 để xác định quan hệ EVPPI/VOI/model-improvement value. Không có evidence mạng thật, feedback độc lập hoặc human explanation mới trong L1.8. Closest-prior map hiện chỉ có reading note/review thứ cấp.

Việc còn mở: A01 final dt và runtime full-grid; A05 H0/H1/metrics/split trước confirmation; intermediate model Phase5; feasible repair, telemetry rate-only, actual timing/cost Phase8; P0-V3/P0-V11 và human explanation còn pending; **P0-V10 trước Phase4**. Full Final Review và mẫu PHASE_1 gốc chưa có trong repository để đối chiếu toàn bộ. Chi tiết tại closeout. Conditional freeze cho phép chuẩn bị Phase2a và exact pre-spike theo gates, không mở full study hoặc claim G2.
