# Research contract v1 — snapshot kỹ thuật có điều kiện

Tác giả: **Doan Van Tai** · 22/10/2026. Kế thừa [v0](01_definitions.md), không sửa snapshot/tag v0. Gate **G1**; HOLD Phase4 tới P0-V10. User đã chọn cấu hình Part C/D ngày22/10. Khóa kỹ thuật không xác nhận P0-V3/V11 hoặc phản hồi người thật đã xong. Ngoại lệ tag trước P0-V11 ghi DL-024. Dữ liệu số/lưới đặt ở [annex](design/grid_v1.md), [machine manifest](design/grid_v1.json), giữ **25/25** term.

Main RQ giữ nguyên: *For load-changing routing actions, how do improvements in current-state information and action-response model fidelity differ and interact in their effect on expected decision regret?*

RQ1: gains theo thông tin biết trước action. RQ2: H0/H1 dự báo held-out. RQ3: feasible net gain và baseline mạnh. Model fidelity ở đây chỉ là biểu diễn randomness với cùng θ và recurrence; không đo parameter/structural error. [Brief v1](00_research_brief_v1.md), [11 thẻ + 6b](lessons/L1.8D_decision_cards.md), [closeout](phases/PHASE_1_closeout.md) là record đi kèm; khi mâu thuẫn phải HOLD và tăng version, không sửa ngầm.

| ID | Term | Định nghĩa vận hành | Đơn vị | Trạng thái |
|---|---|---|---|---|
| D1 | Slot Δt | Khoảng thời gian; mode hiện tại → arrivals → service → transition mode. Rates vật lý nhân Δt thành lượng/slot; ứng viên age/120, cuối theo A01 | s | PROTOCOL LOCKED; final A01 |
| D2 | Horizon h | HΔt; cùng H giữa bốn pipeline/action **trong mỗi ô**; được đổi giữa các ô theo annex | s | LOCKED |
| D3 | Path, capacity | A/B rời, một bottleneck mỗi path, capacity bằng nhau và cố định trong episode; hệ chuẩn μ=10 | packet/s | LOCKED |
| D4 | Nền, θ | A deterministic5; B OFF2/ON14 với Markov đối xứng R2, Tmode theo κ; θ đúng dùng chung; không feedback action | packet/s | LOCKED |
| D5 | Action, u | Stay: managed u trên A; Switch: chuyển đúng u sang B tại t0, giữ suốt h; u=2η | packet/s | LOCKED |
| D6 | Recurrence | q_next=max(0,q+background_amount+managed_amount−capacity_amount); không finite-buffer cap | packet | LOCKED |
| D7 | State x | (qA,qB,mA,mB) tại đầu slot0, mode hiệu lực slot0; mA deterministic | packet, mode | LOCKED |
| D8 | Observation y, age | Snapshot backlog A/B không nhiễu, không mode, có timestamp tại t0−age; age1s chuẩn; schema giống hai neo | packet,s | LOCKED ideal; rate-only Phase8 |
| D9 | Estimator S | S0 B2: posterior từ y/timestamp/θ và prior đúng D; một belief dùng chung hai model. S1 trả state hiện tại thật, chỉ diagnostic | distribution | LOCKED |
| D10 | Model M | M0: trung bình **cost của mean rollout từng state trong belief**, conditional mode, load-aware; M1: trung bình cost đúng law. Cùng θ; không rollout từ mean-state thay belief | packet·s | LOCKED |
| D11 | Future w | Realized background sau t0; evaluator giữ riêng, không controller/oracle nào nhận | — | LOCKED |
| D12 | Episode, D | Condition stationary B trên backlog đo, A khởi tạo kiểm soát; chạy Stay tới t0. D và prior S0 theo cùng law; tọa độ báo cáo biết trước action | probability | LOCKED |
| D13 | Cost C | Δt Σ(k=1..H)(qA,k+qB,k), c_sw=0; endpoint occupancy, gồm packet còn tồn, bỏ k0 và phần sau h | packet·s | LOCKED |
| D14 | Objective J | E_w[C(action,w) given x,θ]; không hindsight realization | packet·s | LOCKED |
| D15 | Oracle a* | Argmin true J, biết x/law nhưng không w, một benchmark cho mọi ô | action | LOCKED |
| D16 | Decision | Chọn Switch iff predicted J(Switch)−J(Stay)<0; exact tie Stay; near-tie alarm không đổi policy | action | LOCKED |
| D17 | Gap, margin | Δ=J(Switch)−J(Stay); predicted gap tương ứng; margin=abs(Δ), chỉ diagnostic sau freeze | packet·s | LOCKED |
| D18 | Regret | r=J(chosen)−J(a*)≥0; Rsm=E_D[r]; Lsm=E_D[J(chosen)] | packet·s | LOCKED |
| D19 | Contrasts | GS=L00−L10; GM=L00−L01; GSM=L00−L11; Γ=L10+L01−L00−L11; GSgivenM1=L01−L11; GMgivenS1=L10−L11 | packet·s | LOCKED |
| D20 | State repair | S0→S1 toàn phần: age về0 và thấy mode; noise component bằng0 cấu trúc trong schema này | — | LOCKED |
| D21 | Model repair | M0→M1; S không đổi kể cả mô hình bù age; chỉ randomness representation với θ đúng, không parameter/structure repair | — | LOCKED |
| D22 | Current-backlog diagnostic | Age0, vẫn giấu mode; conditional posterior đúng từ D. Tách GS theo cùng M0: L00→LcurrentM0→L10; M1 path riêng | — | LOCKED |
| D23 | Practical εR | Primary .01 của Cref=Lstar mỗi ô, cùng Δt; sensitivity .005/.02; Cref0 giữ absolute output, loại nhãn relative có lý do | fraction | LOCKED convention |
| D24 | Equivalence εE | .005 của Cref; numerical estimated error budget≤.0025*Cref. Exact point-label chưa là inference; MC tương đương cần90%CI hoàn toàn trong biên (TOST α.05) | fraction | LOCKED convention |
| D25 | Null H0, H1 | Threshold null và giải thích động học; cùng thông tin trước action/ngân sách fit. A05 khóa hàm, metrics, biên và split sau discovery, trước confirmation | — | DEFERRED A05 |

Quyền thông tin: S0 chỉ y/history/timestamps/θ/prior; S1 nhận x riêng. Cả hai model có θ đúng; không ô nào nhận w. Evaluator có x,w và chấm mọi action trên cùng law. Khi chuyển M0/M1 không tái fit/recompute S theo model. Oracle biết state/law, không biết tương lai realized. B1 MAP chỉ sensitivity: chọn support-state có mass lớn nhất, tie lexicographic (qA,qB,mA,mB; off<on); không đổi primary B2.

Các hệ quả E0 giữ từ v0 §7: R11=0; GM≥0 khi posterior/law/decision thật sự đúng; GSgivenM1 là giá trị thông tin hiện tại có điều kiện observation; Γ không có dấu cố định. Không cần queue để Γ khác0; không claim novelty từ Γ. No-idle trên mọi path của hai action ⇒ mọi action cost bằng nhau ⇒ contrasts0. Regret bất kỳ repair trên cùng action set/objective/D không vượt R00; cheap-kill theo headroom R00, không theo gain của riêng một repair.

IΔ=pred_gap11−pred_gap10−pred_gap01+pred_gap00. Báo Eabs(IΔ), P(abs(IΔ)>δ) với δ=εE*Cref; E[IΔ]=0 chỉ áp conditional on cùng observation và belief chính xác, không phủ nhận interaction episode. F5 giữ tie term của L1.5. State diagnostics: posterior mass của state thật, posterior expected abs(q−q_true), báo tách A/B; đây là posterior loss chẩn đoán, không gọi belief là point estimator. D22 dùng mô hình cố định, không dùng đường hybrid M1→M0 để gán toàn bộ gain cho State repair.

Primary packet·s; secondary1000 L/E[N] ms/packet với N=qA0+qB0+mọi arrivals cả hai queue trong h. E[N] theo D, action-invariant và cùng denominator cho bốn ô/contrasts. Ratio of expectations; không mean episode ratios hoặc delay completed-packets. Cref và mọi percentage cũng dùng endpoint convention D13.

Scope/assumptions kế thừa v0 §8: một managed class, action cố định, nền ngoại sinh, path rời, buffer vô hạn fluid, law đúng, observation lý tưởng, no TCP/multi-controller/tail/safety. Primary scientific risk **AS1**: action có thể đổi background qua TCP, làm sai counterfactual; telemetry backlog lý tưởng D8 và action tức thời AS4 là rủi ro operational kế tiếp. Hai neo chỉ mapping timescale, Tmode thật/d_act thật chưa đo. Chưa xác nhận practical relevance hoặc novelty; G1 giữ nguyên.

Các mục còn mở và nơi quyết: final Δt/calibration/budget A01 Phase3; H0/H1, predictor/metric HC1/HM1/splits A05 trước confirmation; intermediate models Phase5 (MK variance và M(j) khác estimand); feasible repairs/cost/timing/rate-only Phase8; primary-paper boundary Phase2a; external feedback, P0-V3/P0-V11 understanding trước nâng gate; P0-V10 người đọc độc lập trước Phase4. Không có confirmation root được cấp/phát sinh; stage×role seed schema ở thẻ8, Phase3 exact không RNG.

Quản lý version: ghi DL + phiên bản minor/major mới khi đổi definition, grid, D, threshold, estimand; tag cũ không di chuyển. Phase3 contrast chỉ chạy khi `contract-v1` tồn tại và grid commit là ancestor. Thứ tự git chỉ chứng minh chronology repository, không chứng minh không có exposure ngoài máy. Record nguồn [consistency_checks.json](../results/lessons/l1_8_cde/consistency_checks.json) phân biệt PASS nội bộ và đối chiếu Final Review đầy đủ còn thiếu.
