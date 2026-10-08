# Research brief v0 — State × Model repair cho routing làm đổi tải

Tác giả: **Doan Van Tai** · 08/10/2026 · **DRAFT**.

Tích hợp File 7; tác giả còn viết lại, tự giải thích và xác nhận. Định nghĩa: [contract](01_definitions.md). Chưa có read-back hoặc kiểm 5 phút.

**Problem.** Chuyển traffic từ A sang B làm A nhẹ đi và B nặng thêm. Twin, tức bộ ước lượng hiện tại và dự đoán phản ứng mạng để thử quyết định, có thể sai ở state hoặc model.

**Why it matters.** Đo thường xuyên hơn và dùng model chi tiết hơn có chi phí khác nhau. Cần biết mỗi cách sửa giúp quyết định bao nhiêu, khi nào đáng đầu tư và khi nào hiện trạng đã đủ.

**Known.** Theo literature map thứ cấp, dự đoán chính xác và quyết định tốt là hai việc khác nhau; state cũ có thể làm routing kém (EV-06). Với recurrence/objective tuyến tính, không clipping trên mọi path liên quan và lấy kỳ vọng nhất quán, mean rollout cho đúng expected cost (EV-20). $\Gamma\ne0$ tự nó không xác nhận cơ chế mạng (EV-01); value-of-information là prior phải kiểm (EV-27). Trong mô hình này Stay và Switch chỉ khác cost qua capacity bỏ phí; khi không queue nào rỗng, hai action tương đương (EV-32).

**Unknown.** Hai repair giảm regret bao nhiêu, ở đâu, và phụ thuộc nhau thế nào? Literature cho thang measurement/polling/control từ ms tới phút; T00 chuyển thành trục tuổi/delay minh họa và sàng lọc theo tỉ số drain/tổng delay. Mode chậm có thể còn hữu ích, chưa được kiểm; drain fluid chưa chứng minh gain.

**Gap status.** **G1 — candidate gap** (EV-05). Chưa có effect đúng thế giới mới, prediction trên dữ liệu chưa dùng hoặc timing/cost thật. Literature chủ yếu qua review; chưa xác nhận novelty.

**Main RQ.** *For load-changing routing actions, how do improvements in current-state information and action-response model fidelity differ and interact in their effect on expected decision regret?*

- **RQ1:** gain riêng/chung thay đổi theo tải chuyển, capacity còn dư, backlog quan sát và horizon thế nào?
- **RQ2:** threshold null đóng băng dự báo được pattern nào trên held-out, và động học queue thêm sức dự báo ở đâu?
- **RQ3:** repair khả thi còn đáng làm sau chi phí/độ trễ và so với baseline load-aware/age-aware mạnh không?

**Hypotheses — DRAFT, có thể bị bác.**

- **HC1:** bản đồ học từ tọa độ biết trước action (tải chuyển, backlog đo, horizon, persistence biết được) dự báo gain và độ lớn $\Gamma$ tốt hơn dự đoán hằng. Bị bác nếu không vượt dự đoán hằng trên held-out theo phép chấm khai báo trước; không dùng state/margin thật làm predictor.
- **HM1:** giải thích động học $H_1$ dự báo gain held-out tốt hơn threshold null $H_0$ đóng băng, cùng quyền thông tin/ngân sách fit. Bị bác theo tiêu chí đủ-dùng nếu sai số $H_0$ nằm trong biên đã khai báo và $H_1$ không cải thiện quá biên đó. Metric/biên kiểm phải khóa trước confirmation.
- **HP1:** ở miền có headroom regret $R_{00}$ đủ lớn, repair khả thi giữ net gain vượt $\varepsilon_R$ và vượt baseline mạnh. Bị bác nếu cận trên khoảng tin cậy net gain dưới $\varepsilon_R$, hoặc cận trên lợi thế so baseline không dương. Headroom/gain đều chuẩn hóa theo cùng reference cost dương; không lấy gain một oracle repair làm headroom.

**Primary estimand.** Expected regret $R_{sm}$ so với một oracle biết state/law nhưng không biết tương lai realized; contrasts $G_S,G_M,G_{SM},\Gamma,G_{S\mid M_1},G_{M\mid S_1}$ trên cùng $D$, báo theo điều kiện. Objective: cumulative queue occupancy — diện tích backlog cuối slot của cả hai queue trong horizon, kể cả packet chưa xong (packet·s); không phải mean delay. Đo cách sửa twin giúp lựa chọn bớt tốn kém bao nhiêu; ngưỡng % cần reference cost, không so trực tiếp với packet·s.

**Scope.** Một managed class; hai path rời, mỗi path một bottleneck; Stay/Switch chuyển lượng cố định, giữ suốt horizon; nền Markov on/off ngoại sinh; một State repair và một Model repair; Model repair chỉ đổi cách biểu diễn ngẫu nhiên, cùng $\theta$ đúng, không đo sai tham số hay sai cấu trúc. Tuổi/delay là trục quét, giữ hai neo: (a) telemetry ms + datacenter 1–10 Gb/s; (b) polling 0,1–1 s + edge 10–100 Mb/s. Schema backlog/rate còn OPEN.

**Assumptions rủi ro nhất.** AS1: nền ngoại sinh, thiếu feedback TCP. AS4: diagnostic giả định action hiệu lực ngay; repair thực tế cần timing riêng. Đây là ưu tiên bản nháp, tác giả còn xác nhận.

**Out of scope.** Nhiều controller; RL/chuỗi quyết định; active probing; tail/safety; TCP; shared bottleneck/topology lớn.

**Closest prior.** P01–P03, P11–P13 theo Final Review (EV-06, đọc thứ cấp). Khi posterior chính xác, prior khớp $D$ và $M_1$ tích phân đúng, $G_{S\mid M_1}$ là EVPI về state hiện tại sau observation (EV-27); value-of-information/model-improvement value là rủi ro lớn.

**Evidence hiện có.** Logic và liệt kê hữu hạn: phản ví dụ $\Gamma$, trộn episode, bù sai số, null 60 = 60, bảo toàn (EV-01/20/25/26/32); bảng timescale theo chế độ literature (EV-28/29/31). AoI prototype giữ đối chiếu, không làm neo (EV-10). **Chưa có network evidence cho RQ này.** Kết quả luồng nhỏ cũ chỉ là motivation.

**Kill criteria — dừng hoặc đổi claim.** K1: prior đã có cùng estimand, cơ chế và regime. K2: null đóng băng đã đủ. K3: effect không còn trước baseline mạnh. K4: signal chỉ có với tuổi/bias phi thực tế. K9: timing/cost khiến use case không hợp lý. K10: cận trên $R_{00}$ chuẩn hóa dưới $\varepsilon_R$ trên một miền → bỏ miền đó (contract §7f). K5/pipeline repair giữ ở contract §5.

**Mục còn mở.** $\Delta t,H,u$, capacity, Markov, chi tiết $S_0$, $D$, reference cost, $\varepsilon_R/\varepsilon_E$, seed streams (L1.6–L1.8); predictor, metric/biên kiểm HC1/HM1 và $H_0/H_1$ (A05); feasible repairs, ngưỡng vận hành, $d_{\text{act}}$ thật (Phase 8). Chi tiết và nơi quyết: contract §9; nguồn và giới hạn: [inventory](00_evidence_inventory.md), [claim boundary](01_claim_boundary_v0.md).
