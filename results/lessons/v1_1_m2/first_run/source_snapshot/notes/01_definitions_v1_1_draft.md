# Research contract v1.1 — DRAFT, chưa tag

Người phụ trách: **Doan Van Tai** · 23/10/2026. Lựa chọn theo ủy quyền kỹ thuật, [mốc2](design/decisions_v1_1_m2.md), không là bài kín sách/read-back. [v1](01_definitions_v1.md) giữ snapshot; active [closeout](phases/PHASE_1_closeout.md) HOLD. Chưa có grid manifest được chốt hoặc A01/A04. Vẫn25term, ngưỡng/objective/cùng θ không đổi.

Main RQ: *For load-changing routing actions, how do improvements in current-state information and action-response model fidelity differ and interact in their effect on expected decision regret?*

| ID | Term | Định nghĩa vận hành | Đơn vị | Trạng thái |
|---|---|---|---|---|
| D1 | Slot Δt | dt_screen=age/120 và half; ứng viên, final theo A01 sau gate | s | PROTOCOL ADOPTED; final A01 |
| D2 | Horizon h | h=Hdt, cùng giữa action/pipeline trong cell; r_h riêng theo quantileB và headroom; control horizon khai báo riêng | s | ADOPTED |
| D3 | Path, capacity | A/B rời, một bottleneck mỗi path, capacity bằng nhau và cố định trong episode; hệ chuẩn μ=10 | packet/s | ADOPTED |
| D4 | Nền, θ | Nền A/B độc lập ON/OFF, symmetric R2, Tmode dùng chung; A amplitude±6 giữ nguyên khiu đổi; thông số theo mốc2 | packet/s | ADOPTED |
| D5 | Action, u | Stay: managed u trên A; Switch: chuyển đúng u sang B tại t0, giữ suốt h; u=2η | packet/s | ADOPTED |
| D6 | Recurrence | q_next=max(0,q+background_amount+managed_amount−capacity_amount); không finite-buffer cap | packet | ADOPTED |
| D7 | State x | (qA,qB,mA,mB); mA từ placeholder deterministic thành mode ngẫu nhiên thật, mode hiệu lực slot0 | packet, mode | ADOPTED |
| D8 | Observation y, age | Snapshot backlog A/B không nhiễu, không mode, có timestamp tại t0−age; age1s chuẩn; schema giống hai neo | packet,s | ADOPTED ideal; rate-only Phase8 |
| D9 | Estimator S | B2 posterior trên cả hai backlog/mode, b=D theo ideal law; một belief giữ nguyên giữa M0/M1; numeric approximation phải báo cận | distribution | ADOPTED |
| D10 | Model M | M0: trung bình **cost của mean rollout từng state trong belief**, conditional mode, load-aware; M1: trung bình cost đúng law. Cùng θ; không rollout từ mean-state thay belief | packet·s | ADOPTED |
| D11 | Future w | Realized background sau t0; evaluator giữ riêng, không controller/oracle nào nhận | — | ADOPTED |
| D12 | Episode, D | D stationary conditional cho A/B tại yA,yB; A trước quyết định mangu; pre-Stay tới t0. Numeric prior cần cận sai số law/posterior, belief cùng law với evaluator | probability | ADOPTED |
| D13 | Cost C | Δt Σ(k=1..H)(qA,k+qB,k), c_sw=0; endpoint occupancy, gồm packet còn tồn, bỏ k0 và phần sau h | packet·s | ADOPTED |
| D14 | Objective J | E_w[C(action,w) given x,θ]; không hindsight realization | packet·s | ADOPTED |
| D15 | Oracle a* | Argmin true J, biết x/law nhưng không w, một benchmark cho mọi ô | action | ADOPTED |
| D16 | Decision | True rule Switch iff true/predicted gap<0, exact tie Stay. Implementation idle-based gap+SD/WD certificates; uncertified small interval phải tăng precision/HOLD, không tự gán oracle Stay | action | ADOPTED |
| D17 | Gap, margin | Δ=J(Switch)−J(Stay); predicted gap tương ứng; margin=abs(Δ), chỉ diagnostic sau freeze | packet·s | ADOPTED |
| D18 | Regret | r=J(chosen)−J(a*)≥0; Rsm=E_D[r]; Lsm=E_D[J(chosen)] | packet·s | ADOPTED |
| D19 | Contrasts | GS=L00−L10; GM=L00−L01; GSM=L00−L11; Γ=L10+L01−L00−L11; GSgivenM1=L01−L11; GMgivenS1=L10−L11 | packet·s | ADOPTED |
| D20 | State repair | S0→S1 gồm age và thấy cả mA,mB; noise repair vẫn structural0; không so trực tiếp split với v1 | — | ADOPTED |
| D21 | Model repair | M0→M1; S không đổi kể cả mô hình bù age; chỉ randomness representation với θ đúng, không parameter/structure repair | — | ADOPTED |
| D22 | Current-backlog diagnostic | Current-backlog cả hai queue nhưng giấu cả hai mode; posterior đúng, fixed-M0 split. Mode visibility giờ là A+B; không đổi model giữa các endpoint | — | ADOPTED |
| D23 | Practical εR | Primary .01 của Cref=Lstar mỗi ô, cùng Δt; sensitivity .005/.02; Cref0 giữ absolute output, loại nhãn relative có lý do | fraction | ADOPTED convention |
| D24 | Equivalence εE | .005 của Cref; numerical estimated error budget≤.0025*Cref. Exact point-label chưa là inference; MC tương đương cần90%CI hoàn toàn trong biên (TOST α.05) | fraction | ADOPTED convention |
| D25 | Null H0, H1 | Threshold null và giải thích động học; cùng thông tin trước action/ngân sách fit. A05 khóa hàm, metrics, biên và split sau discovery, trước confirmation | — | DEFERRED A05 |

## 7. Hệ quả E0 và điều kiện

Giữ các identity của v1 khi **true oracle**, posterior/law đúng và shared S. Near-zero float không là định nghĩa oracle mới. Numeric band1e−9*Cref, alarm uncertain mass>.01, là precision diagnostics; certified exact ties báo riêng; không dùng Cref/Lstar ở B3 khi chưa được phép nhìn. Không resolve được dấu thì HOLD thay vì claim R11=0 từ số đã clamp.

Một observation mỗi ô: bổ đề N2 và proof tại [reference](theory/T01_single_observation.md), không phải phát hiện. a00/a01 hằng, GM=abs(EΔ)1[action differs]≤abs(model_gap_bias); GSgivenM1=min(EΔ+,EΔ−). GM0 không chứng minh mean-model đủ, và khi EΔ0 hai action vẫn có thể khác. A04 báo companion EΔ/model bias/positive-negative parts. Trộn nhiều y có thể dựng lại chỉ khi có đủ conditional cells và đúng weights; hai quantile không đủ.

D4/D7/D12/D20/D22 thay đổi plant và estimand interpretation, không chỉ đổi grid. Primary State gain gồm thấy hai mode, nên không so trực tiếp attribution với PartB/v1. κ là relative-age axis1/κ; z derived, không claim independent persistence effect. Selected decision-relevance grid không ước lượng prevalence ở mạng thật.

Version/gate: B2 parameters→ĐK1; B3 chỉ p_sw ởdt/half và numeric checks, không reserve p_sw hoặc margin outcomes; unstable không calibration; giữ mọi ô, tối đa1 redesign. B5 consistency không tự cho tag khi V11 thiếu. Nguồn gate full và artifacts người thật còn chờ; không có lời GO độc lập từ tests. Scope/rights kế thừa v1: evaluator giữ w, chỉ S1 nhận x trong decision branch; no TCP/shared bottleneck/tail operational claim. N1/N2/stat solver là engineering/theory verification, không hypothesis confirmation.
