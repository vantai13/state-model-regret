# Research contract v1.2 — LOCKED (tag `contract-v1.2`)

Người phụ trách: **Doan Van Tai** · 23/10/2026. Thay [bản nháp v1.1](01_definitions_v1_1_draft.md) (lưới B4 bị từ chối). Quyết định: DL-038 (REFORMULATE), DL-039 (lưới ACCEPTED). Lưới: [grid_v1_2.md](design/grid_v1_2.md). Snapshot cũ giữ tại tag `contract-v0` và `contract-v1`.

> **Provenance.** Các dòng thay đổi so với v1.1 (D1, D2, D4, D5, D8, D12, D25 và hai mục cuối) do AI soạn theo yêu cầu thực hiện của tác giả ngày 23/10. Tác giả chưa tự viết lại bằng lời mình (PHASE_1 §5.4, luật 5): đây là mục còn mở. Viết lại câu chữ không đổi nội dung kỹ thuật thì không cần phiên bản mới; đổi nội dung thì thành `v1.2.x` kèm DL.

Main RQ: *For load-changing routing actions, how do improvements in current-state information and action-response model fidelity differ and interact in their effect on expected decision regret?*

| ID | Term | Định nghĩa vận hành | Đơn vị | Trạng thái |
|---|---|---|---|---|
| D1 | Slot Δt | dt_screen=age/120 và dt/2; dải p_sw kiểm thêm ở dt/4. Final dt chọn ở A01 trên M01, M09, M22 bằng luật làm mịn của v1 (\|ΔG\|≤.0025·Cref giữa hai mức kề, không đổi dấu ngoài vùng εE) | s | LOCKED rule; final dt A01 |
| D2 | Horizon h | Số giây vật lý cố định: lõi 8 s, nan hoa 2 s (chỉ κ 0,3), held-out 4/8/12 s; ô kiểm âm giữ h của v1.1. Hcoarse=ceil(h/dt_coarse), finer H=ref·Hcoarse, cùng h cho mọi action và pipeline. r_h=h/T_drain^post,B chỉ là tọa độ dẫn xuất | s | LOCKED |
| D3 | Path, capacity | A/B rời, một bottleneck mỗi path, capacity bằng nhau và cố định trong episode; hệ chuẩn μ=10 | packet/s | LOCKED |
| D4 | Nền, θ | Nền A/B độc lập ON/OFF, R2 đối xứng, Tmode chung; B OFF 2/ON 14; A λA±6, biên độ không đổi theo u. λA của từng ô chọn bằng luật neo v1.2 (thang 6; 6,25; …; (λA+u)/μ≤0,95; mục tiêu p_sw 0,3/0,7; cửa sổ ±0,15 ở dt và dt/2). ψ=(λA−λB)/μ và δ=(λA+u−λB)/μ là dẫn xuất | packet/s | LOCKED |
| D5 | Action, u | Stay: managed u trên A; Switch: chuyển đúng u sang B tại t0, giữ suốt h; u=2η, η∈{0,5; 0,75} (held-out 0,625) | packet/s | LOCKED |
| D6 | Recurrence | q_next=max(0,q+background_amount+managed_amount−capacity_amount); không finite-buffer cap | packet | LOCKED |
| D7 | State x | (qA,qB,mA,mB); mA từ placeholder deterministic thành mode ngẫu nhiên thật, mode hiệu lực slot0 | packet, mode | LOCKED |
| D8 | Observation y, age | Snapshot backlog A/B tại t0−age, không nhiễu, không mode, có timestamp; age 1 s. Mức quan sát là quantile của phân phối dừng trước quyết định: A q90 (lõi), q50 (nan hoa); B q50, q90 (held-out q75); lấy ở dt thô và giữ cố định vật lý khi làm mịn | packet, s | LOCKED ideal; rate-only Phase 8 |
| D9 | Estimator S | B2 posterior trên cả hai backlog/mode, b=D theo ideal law; một belief giữ nguyên giữa M0/M1; numeric approximation phải báo cận | distribution | LOCKED |
| D10 | Model M | M0: trung bình **cost của mean rollout từng state trong belief**, conditional mode, load-aware; M1: trung bình cost đúng law. Cùng θ; không rollout từ mean-state thay belief | packet·s | LOCKED |
| D11 | Future w | Realized background sau t0; evaluator giữ riêng, không controller/oracle nào nhận | — | LOCKED |
| D12 | Episode, D | D stationary conditional cho A/B tại yA,yB; A trước quyết định mangu; pre-Stay tới t0. Spectral interval residual+Lyapunov tail+Bellman return bound; law≤1e−10, posterior≤1e−8. Prior tính lại mỗi dt, giữ observation coarse vật lý; D_A,D_B lưu riêng với cận propagation/normalization, không Cartesian product; belief cùng law với evaluator. Lưới: design/grid_v1_2.json (38 ô chính, 12 held-out, 6 kiểm âm, 2 đầu dò) | probability | LOCKED |
| D13 | Cost C | Δt Σ(k=1..H)(qA,k+qB,k), c_sw=0; endpoint occupancy, gồm packet còn tồn, bỏ k0 và phần sau h | packet·s | LOCKED |
| D14 | Objective J | E_w[C(action,w) given x,θ]; không hindsight realization | packet·s | LOCKED |
| D15 | Oracle a* | Argmin true J, biết x/law nhưng không w, một benchmark cho mọi ô | action | LOCKED |
| D16 | Decision | True rule Switch iff true/predicted gap<0, exact tie Stay. Implementation idle-based gap+SD/WD certificates; uncertified small interval phải tăng precision/HOLD, không tự gán oracle Stay | action | LOCKED |
| D17 | Gap, margin | Δ=J(Switch)−J(Stay); predicted gap tương ứng; margin=abs(Δ), chỉ diagnostic sau freeze | packet·s | LOCKED |
| D18 | Regret | r=J(chosen)−J(a*)≥0; Rsm=E_D[r]; Lsm=E_D[J(chosen)] | packet·s | LOCKED |
| D19 | Contrasts | GS=L00−L10; GM=L00−L01; GSM=L00−L11; Γ=L10+L01−L00−L11; GSgivenM1=L01−L11; GMgivenS1=L10−L11 | packet·s | LOCKED |
| D20 | State repair | S0→S1 gồm age và thấy cả mA,mB; noise repair vẫn structural0; không so trực tiếp split với v1 | — | LOCKED |
| D21 | Model repair | M0→M1; S không đổi kể cả mô hình bù age; chỉ randomness representation với θ đúng, không parameter/structure repair | — | LOCKED |
| D22 | Current-backlog diagnostic | Current-backlog cả hai queue nhưng giấu cả hai mode; posterior đúng, fixed-M0 split. Mode visibility giờ là A+B; không đổi model giữa các endpoint | — | LOCKED |
| D23 | Practical εR | Primary .01 của Cref=Lstar mỗi ô, cùng Δt; sensitivity .005/.02; Cref0 giữ absolute output, loại nhãn relative có lý do | fraction | LOCKED convention |
| D24 | Equivalence εE | .005 của Cref; numerical estimated error budget≤.0025*Cref. Exact point-label chưa là inference; MC tương đương cần90%CI hoàn toàn trong biên (TOST α.05) | fraction | LOCKED convention |
| D25 | Null H0, H1 | Threshold null và giải thích động học; cùng thông tin trước action và ngân sách fit. A05 khóa hàm, metric, biên và split sau discovery, trước confirmation. Held-out R01–R12 không dùng cho discovery hay calibration; p_sw và λA riêng của held-out không làm biến đầu vào trừ khi định nghĩa cho mọi ô | — | DEFERRED A05 |

## 7. Hệ quả E0 và điều kiện

Giữ các identity của v1 khi **true oracle**, posterior/law đúng và shared S. Numeric band 1e−9·Cref và alarm uncertain mass > .01 chỉ là precision diagnostics; certified exact ties báo riêng. Không resolve được dấu thì HOLD thay vì claim R11=0 từ số đã clamp.

Một observation mỗi ô: bổ đề N2 tại [reference](theory/T01_single_observation.md), không phải phát hiện. a00/a01 hằng trong ô; GM=|EΔ|·1[action khác]≤|model gap bias|; G_S|M1=min(EΔ+,EΔ−). A04 báo kèm EΔ, model bias và hai phần EΔ±.

D4/D7/D12/D20/D22 của v1.1 vẫn có hiệu lực: A có mode thật, nên State repair gồm thấy cả hai mode; không so trực tiếp attribution với Part B hoặc v1.

## 8. Lưới v1.2 và cách đọc (bắt buộc)

1. So sánh giữa các điều kiện là ở **cùng độ khó** (p_sw gần mục tiêu), không phải cùng tải. λA thay đổi theo lát, nên khác biệt giữa hai lát không được quy riêng cho κ, quantile B hay η.
2. ψ là dẫn xuất và gần như một phía: 34/38 ô chính ψ<0, 3 ô ψ=0, 1 ô ψ>0; khoảng [−0,2; +0,05]. Kết luận chỉ áp dụng cho vùng này.
3. Kết quả có điều kiện "gần ranh giới quyết định": chọn mẫu có chủ đích, không đại diện tần suất trong mạng thật.
4. "Cùng độ khó" chỉ xấp xỉ: báo p_sw thực của từng ô (lệch mục tiêu tối đa 0,13).
5. Nan hoa h=2 s chỉ ở κ 0,3; ở κ≥1 horizon này bị khóa bởi cấu trúc (conservation hoặc WD), nên claim về horizon ngắn chỉ cho κ thấp.
6. p_sw trong dải chưa đủ để có bài toán quyết định: luôn kèm nhãn ĐK1 `candidate` (đầu dò P02 có p_sw 0,52 nhưng là WD-cell).

Gate và phạm vi: calibration A01 = M01, M09, M22; A04 chạy trên 38 ô chính và ô kiểm âm; held-out chỉ dùng ở A05. Ở SD-cell và conservation-cell sáu contrast phải bằng 0 chính xác. Scope và quyền thông tin kế thừa v1: evaluator giữ w, chỉ S1 nhận x trong nhánh quyết định; không TCP, shared bottleneck hay claim vận hành. A01 final dt, A05 null/held-out, Phase 8 feasible repairs và P0-V10 (người đọc độc lập) vẫn có nơi quyết.

Changelog v1.1→v1.2: D1 thêm kiểm dt/4 và ô calibration; D2 horizon vật lý thay r_h; D4 λA neo theo lát, ψ dẫn xuất, bỏ "ψ hai phía của 0"; D5, D8 mức η và quantile; D12 trỏ lưới v1.2; D25 luật cho held-out. Giữ nguyên: objective, R2, B2 dùng chung, εR 1% (độ nhạy 0,5%/2%), εE 0,5%, dung sai làm mịn 0,25%, Cref=L* theo ô và dt, luật hòa Stay.
