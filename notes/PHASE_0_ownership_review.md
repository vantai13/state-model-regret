# PHASE 0 — RESEARCH OWNERSHIP & CONTRACT DECISIONS

**Project:** State × Model — Expected Decision Regret in Load-Changing Routing  
**Tác giả:** Doan Van Tai  
**Date:** 08/10/2026  
**Status:** Phase 0 closed conditionally (B), 08/10/2026; V3/V10/V11 and external review remain open.
**Provenance:** Tích hợp từ hai bản Ownership Review tác giả cung cấp ngày 08/10/2026; đối chiếu với repo tại commit `b37545b`. Phần diễn giải và phép tính là tham khảo, chưa là bài tự giải thích/tính tay đã xác nhận. Lựa chọn B2 và domain hai neo được ghi theo nội dung tác giả cung cấp; contract tổng thể còn DRAFT.

Không ghi ownership **COMPLETE** hoặc GO vô điều kiện khi còn Pending. Yêu cầu đóng phase sau đó đã được xử lý bằng **GO có điều kiện B**, không tự đổi V3/V10/V11 thành Đạt. Bảng việc còn thiếu và chỗ cần bổ sung nằm ở §10.2; các mục được hoãn sang phase sau nằm ở §10.3.

---

## 1. Research Question — Tôi đang nghiên cứu vấn đề gì?

### 1.1. Main Research Question

> For load-changing routing actions, how do improvements in current-state information and action-response model fidelity differ and interact in their effect on expected decision regret?

Diễn đạt tiếng Việt:

**Khi một quyết định định tuyến làm thay đổi tải mạng, việc cải thiện thông tin trạng thái hiện tại và cải thiện mô hình dự đoán phản ứng mạng ảnh hưởng khác nhau và tương tác với nhau như thế nào đối với tổn thất quyết định kỳ vọng?**

### 1.2. Cách hiểu tham khảo — chờ tác giả tự giải thích

Tôi nghiên cứu tình huống một controller đang chuyển tiếp một nhóm traffic qua đường A và cân nhắc chuyển nhóm traffic đó sang đường B.

Trước khi quyết định, controller sử dụng Digital Twin để dự đoán chi phí của hai hành động Stay và Switch.

Tuy nhiên, Digital Twin có thể đưa ra dự đoán sai do hai nguyên nhân.

**State information error:** Twin không biết chính xác trạng thái mạng tại thời điểm quyết định. Telemetry có thể cũ, thiếu thông tin hoặc chỉ phản ánh một phần trạng thái.

**Action-response model error:** Twin có thể biết trạng thái hiện tại nhưng vẫn dự đoán sai diễn biến của mạng sau khi chuyển traffic. Điều này quan trọng vì hành động Switch làm tăng tải trên B và giảm tải trên A.

Hai loại sai số có thể tương tác. Sửa một loại sai số không nhất thiết cải thiện quyết định nếu loại còn lại vẫn tồn tại.

Mục tiêu nghiên cứu không phải chỉ cải thiện prediction accuracy, mà là đo xem các cải thiện đó có làm giảm **expected decision regret** hay không.

Regret là phần chi phí tăng thêm do controller chọn hành động không tối ưu, so với oracle biết đúng trạng thái hiện tại và quy luật mạng nhưng không biết chính xác tương lai ngẫu nhiên.

**Tự xác nhận:** Chưa xác nhận. Bài viết lại không nhìn bản nháp: **Chưa có**; read-back: **Chưa có record**. Ghi bài làm tại [L0.2](lessons/L0.2_rq_card.md).

### 1.3. Điều tôi muốn tìm hiểu

Tôi muốn kiểm tra ba câu hỏi:

**RQ1 — Characterization:** Lợi ích riêng và lợi ích kết hợp của state repair và model repair thay đổi thế nào theo mức tải chuyển, headroom, backlog, horizon và các điều kiện mạng?

**RQ2 — Mechanism:** Những kết quả nào chỉ do ngưỡng quyết định Stay/Switch tạo ra, và khi nào queue dynamics giúp dự đoán kết quả tốt hơn một threshold null đã xác định trước?

**RQ3 — Practical relevance:** Khi nào các cải thiện thực sự đáng kể và còn giá trị sau khi xét telemetry delay, action latency, chi phí repair và baseline mạnh?

### 1.4. Điều tôi không được kết luận trước

Tôi chưa được kết luận rằng:

- State error quan trọng hơn model error, hoặc ngược lại.
- State/model interaction là một cơ chế networking mới.
- Mô hình phức tạp hơn luôn giúp decision tốt hơn.
- Việc refresh telemetry luôn có lợi.
- Nghiên cứu đã có novelty được xác nhận.

Hiện tại Research Gap vẫn ở mức **G1 — Candidate Gap**.

---

## 2. System và bốn pipeline

### 2.1. Hệ thống ban đầu

Hệ thống có hai path A và B, mỗi path có một bottleneck queue.

Controller quản lý một traffic class với lượng tải chuyển cố định.

Có hai action:

- **Stay:** giữ managed traffic trên A.
- **Switch:** chuyển managed traffic từ A sang B.

Action được duy trì trong một evaluation horizon.

Traffic nền được mô hình hóa bằng quá trình Markov ON/OFF, với hai trạng thái tải thấp và tải cao.

Trong diagnostic ban đầu, traffic nền ngoại sinh, capacity cố định, buffer vô hạn và action có hiệu lực ngay lập tức.

Các giả định này giúp cô lập cơ chế, không được coi là mô tả đầy đủ mọi mạng thực tế.

### 2.2. Ý nghĩa của S0, S1, M0, M1

| Thành phần | Định nghĩa |
|---|---|
| S0 | State estimator sử dụng telemetry lịch sử và belief về trạng thái hiện tại |
| S1 | Oracle cung cấp true current state tại thời điểm quyết định |
| M0 | Mean rollout load-aware, dự đoán bằng lượng traffic trung bình có điều kiện |
| M1 | Oracle response model, tính đúng expected cost dựa trên stochastic law |

S1 không biết tương lai. M1 biết đúng quy luật sinh traffic nhưng không biết future realization.

Bốn pipeline là:

| Pipeline | Ý nghĩa |
|---|---|
| S0M0 | Baseline |
| S1M0 | Chỉ repair state |
| S0M1 | Chỉ repair model |
| S1M1 | Full oracle |

Trong cùng episode, bốn pipeline được đánh giá với cùng true state, objective, action set và benchmark.

---

## 3. Kiểm tra phép tính 2×2

### 3.1. Thiết lập

Theo bảng running example tác giả cung cấp, được gắn nguồn Master Plan II.6 trong [EV-22](00_evidence_inventory.md). Chưa có bản Master Plan đầy đủ để đối chiếu nguồn và cách sinh các predicted cost. Đây là kiểm đại số của bảng được cung cấp, chưa là tái lập plant hoặc bằng chứng về mạng.

Để dùng $L,G,\Gamma$ đúng contract, phần này xét $D$ suy biến gồm đúng episode minh họa; với một episode thuộc $D$ tổng quát phải dùng $\ell,g,\gamma$. Các giá trị $J$ là **expected cost theo tương lai**, không phải cost của một realization ngẫu nhiên:

$$
J(Stay)=4
$$

$$
J(Switch)=4.25
$$

Vì cost càng thấp càng tốt:

$$
a^*=Stay
$$

Action gap:

$$
\Delta=J(Switch)-J(Stay)=0.25
$$

Vì vậy, chọn Switch sẽ chịu regret bằng 0.25.

### 3.2. Bốn pipeline

| Pipeline | Predicted Stay | Predicted Switch | Action | True expected cost $J$ | Regret |
|---|---:|---:|---|---:|---:|
| S0M0 | 0 | 3 | Stay | 4 | 0 |
| S1M0 | 4 | 3 | Switch | 4.25 | 0.25 |
| S0M1 | 0 | 4.25 | Stay | 4 | 0 |
| S1M1 | 4 | 4.25 | Stay | 4 | 0 |

Với cùng state/law, expected cost thật của một action không phụ thuộc pipeline nào chọn action đó. Đơn vị cost của bảng nguồn chưa được đối chiếu với plant; không tự gọi các số này là ms hay mean delay.

### 3.3. State repair gain

$$
G_S=L_{00}-L_{10}
$$

$$
G_S=4-4.25=-0.25
$$

Sửa state riêng lẻ làm quyết định tệ hơn trong ví dụ này.

Nguyên nhân là M0 vẫn đánh giá thiếu cost của Switch. State error và model error ban đầu tình cờ bù trừ, giúp baseline chọn đúng Stay.

### 3.4. Model repair gain

$$
G_M=L_{00}-L_{01}
$$

$$
G_M=4-4=0
$$

Model repair không thay đổi action nên không làm giảm regret.

### 3.5. Joint repair gain

$$
G_{SM}=L_{00}-L_{11}
$$

$$
G_{SM}=4-4=0
$$

Baseline đã chọn đúng, nên full repair không thể cải thiện thêm trong episode này.

### 3.6. Interaction

$$
\Gamma=G_{SM}-G_S-G_M
$$

$$
\Gamma=0-(-0.25)-0=0.25
$$

Có interaction dương trên contrast này.

Tuy nhiên, interaction có thể xuất hiện chỉ vì predicted action gap vượt qua decision threshold. Vì vậy:

**Gamma khác 0 không tự động chứng minh một cơ chế networking mới.**

Muốn chứng minh queue dynamics cung cấp một lời giải thích có giá trị mới, phải so sánh với threshold null được đăng ký trước và kiểm tra trên workload giữ riêng.

**Tự tính lại và xác nhận:** Chưa xác nhận. Các phép tính đã có kết quả tham chiếu; bài tính tay độc lập: **Chưa có**. Ghi tại [L0.4](lessons/L0.4_estimand.md).

### 3.7. Phân biệt prediction và decision

Mô hình có prediction error nhỏ hơn chưa chắc tạo decision tốt hơn.

Điều quan trọng là error có làm đảo thứ tự hai action hay không và quyết định sai gây regret bao nhiêu.

Do đó, RMSE chỉ đóng vai trò diagnostic. Primary outcome là expected decision regret.

---

## 4. Kiểm tra timescale

### 4.1. Câu hỏi

Thông tin backlog còn hữu ích đến lúc controller thực thi quyết định không?

Để kiểm tra sơ bộ, so sánh thời gian queue xả backlog với tuổi hiệu dụng của thông tin cộng action delay.

### 4.2. Cấu hình minh họa

- Link rate: 10 Mb/s.
- Packet size: 1.500 bytes.
- Backlog ban đầu: 100 packets.
- Utilization trước quyết định: 0.8.

Thời gian truyền một packet:

$$
t_{pkt}=\frac{8\times1500}{10^7}=0.0012\text{ s}
$$

Service rate:

$$
\mu=\frac{1}{0.0012}\approx833.33\text{ packets/s}
$$

Capacity còn lại để xả backlog:

$$
(1-\rho)\mu=0.2\times833.33
\approx166.67\text{ packets/s}
$$

Drain time:

$$
T_{drain}=\frac{100}{166.67}\approx0.6\text{ s}
$$

### 4.3. So sánh với các chế độ telemetry

Đặt:

$$
T_{total}=\tau_{eff}+d_{act}
$$

| $T_{total}$ | $T_{drain}/T_{total}$ | Nhận xét |
|---|---:|---|
| 0.2 s | 3 | Backlog có thể còn giá trị |
| 1 s | 0.6 | Cùng bậc thời gian |
| 5 s | 0.12 | Backlog ban đầu có thể đã mất |

Các vùng này là phép sàng lọc fluid, không chứng minh gain dương hoặc bằng 0. Tỉ số 3 nằm đúng biên quy ước factor 3. Đây là dòng riêng $\rho=0{,}8$; ma trận [T00](theory/T00_timescale_sanity.md) dùng min của hai mức tải nên drain 0,24 s và nhãn khác. Dùng $T_{total}$ để tránh trùng $D$, vốn là phân phối episode trong contract.

**Tự tính lại và xác nhận:** Chưa xác nhận. Bài tính tay và lời giải thích riêng: **Chưa có**; ghi tại [L0.6](lessons/L0.6_scope.md).

### 4.4. Vì sao sử dụng utilization trước quyết định?

Vì tại thời điểm telemetry được đo, action Switch chưa xảy ra.

Muốn biết backlog cũ còn ảnh hưởng tại thời điểm action có hiệu lực hay không, phải phân tích hệ thống trong khoảng thời gian trước action.

Utilization sau Switch được sử dụng cho câu hỏi khác: backlog thay đổi thế nào trong evaluation horizon sau khi action có hiệu lực.

### 4.5. Giới hạn

Drain time chỉ mô tả một phần trí nhớ của hệ thống.

Traffic mode ON/OFF có thể tồn tại lâu hơn backlog ban đầu. Do đó, backlog đã xả hết không đồng nghĩa toàn bộ state information trở nên vô giá trị.

Ở Phase 1 cần bổ sung phân tích **mode persistence** và đối chiếu với timescale telemetry/action; đặc tả/lưới còn OPEN ở L1.8. Mode không quan sát được chưa có operator refresh khả thi.

---

## 5. Các quyết định Research Contract

### 5.1. System scope

**Quyết định đề xuất:** Giữ hệ thống hai path, một bottleneck queue mỗi path, một managed traffic class và hai action Stay/Switch làm core sandbox.

**Lý do:** Giúp cô lập quan hệ giữa state information, response model và decision regret.

Topology lớn, shared bottleneck và multi-controller không thuộc core experiment. Chúng chỉ được thêm nếu phục vụ kiểm chứng một claim cụ thể.

### 5.2. State estimator

**Lựa chọn đã nêu:** B2 — Belief estimator làm baseline chính.

S0 giữ phân phối xác suất của state/mode dựa trên observation thay vì chỉ chọn mode có xác suất lớn nhất.

B1 — Point estimator được giữ làm phương án sensitivity được đề xuất; cách ước lượng backlog/mode và protocol so sánh còn phải đặc tả. Chọn B2 không tự xác nhận posterior là chính xác, prior khớp $D$ hoặc đã làm bài tự kiểm. Lựa chọn được nối vào [DL-008](02_decision_log.md) và contract D9; lý do bằng lời tác giả còn chờ.

S1 cung cấp true current state cho diagnostic, không được coi là một phương pháp telemetry triển khai miễn phí.

### 5.3. Response model

**Quyết định đề xuất:** Giữ M0 mean rollout load-aware và M1 true stochastic law làm hai điểm tham chiếu chính.

Cần thêm model trung gian có xét biến động traffic để kiểm tra liệu lợi ích M1 có đơn thuần đến từ việc M0 quá đơn giản hay không.

Định nghĩa cụ thể về cách M0 sử dụng belief của S0 và model trung gian sẽ được chốt ở L1.8.

M1 là endpoint diagnostic; chưa claim một thuật toán mới hoặc một model triển khai được.

### 5.4. Timescale và domain

**Lựa chọn đã nêu:** phương án A — domain theo tỉ số timescale, quét nhiều chế độ telemetry và giữ cả hai neo. Bản gửi gọi lựa chọn domain này là “D3”; repo dùng tên phương án A để tránh trùng **D3 = Path/capacity** trong [contract §2](01_definitions.md).

Không dùng testbed cũ làm neo đại diện mặc định. [EV-10/T00](theory/T00_timescale_sanity.md) ghi mean AoI theo ô khoảng 0,33–0,37 s; khoảng 0,58–0,62 s là tuổi hiệu dụng sau cộng nửa cửa sổ rate, không phải AoI backlog đã đo.

Thay vào đó, khảo sát nhiều mức độ trễ, từ mili giây đến hàng chục giây, gắn với những kiến trúc telemetry có nguồn tham khảo.

Hai nhóm neo:

- Telemetry nhanh cỡ ms cùng link datacenter 1–10 Gb/s.
- Polling dưới 1 s cùng link edge 10–100 Mb/s.

Kết quả được phân tích theo các tỉ số timescale thay vì khẳng định một tốc độ link luôn phù hợp hoặc không phù hợp.

Các cặp neo là cấu hình khảo sát, chưa phải use case đã được kiểm chứng độc lập.

### 5.5. Observation schema

**Trạng thái:** OPEN — quyết định ở L1.8.

Không mặc định mọi telemetry technology đều cung cấp backlog.

INT, mirroring, counters và polling có thể cung cấp các loại thông tin khác nhau.

Khi khảo sát riêng tác động của tuổi telemetry, phải giữ nguyên observation schema và các điều kiện khác để tránh confounding.

### 5.6. Objective

**Quyết định đề xuất:** Giữ cumulative queue-occupancy cost trong evaluation horizon, cộng switching cost nếu được khai báo.

Primary metric là expected regret so với cùng một non-clairvoyant oracle.

Không gọi đại lượng packet·s này là mean end-to-end delay.

### 5.7. Information rights

Các nguyên tắc cần bảo toàn:

- Controller không được biết future realization.
- S1 chỉ biết true current state.
- M1 biết true stochastic law, không biết random future realization.
- Evaluator không làm rò dữ liệu tương lai cho controller.
- Khi so sánh model repair, state estimator và thông tin được cấp phải giữ nguyên.
- Cùng episode distribution, objective, action set và oracle benchmark cho các pipeline.

### 5.8. Episode distribution

**Trạng thái:** OPEN — L1.8.

Episode phải được sinh theo quy luật của plant, không ghép tùy ý true state với stale observation.

Tách discovery và confirmation. Kết quả phải được báo theo các điều kiện đã khai báo, không lựa chọn trọng số hậu nghiệm chỉ để tạo hiệu ứng mong muốn.

### 5.9. Các giá trị số còn mở

Các tham số sau chưa được khóa:

- Slot duration và evaluation horizon.
- Traffic rate và amount of rerouted load.
- Service capacity, backlog range và mode persistence. Core diagnostic dùng buffer vô hạn; finite-buffer capacity là mở rộng ngoài AS3, không âm thầm thêm vào core.
- Telemetry age grid.
- Episode distribution.
- Practical effect threshold.
- Model trung gian.
- Observation schema theo regime.

Các tham số sẽ được chốt ở L1.8 hoặc tại phase được chỉ định trước khi chạy experiment xác nhận.

---

## 6. Điều gì đã biết và chưa biết?

### Đã biết về mặt logic

- S1M1 là oracle đầy đủ trong contract.
- Regret của S1M1 bằng 0 theo định nghĩa benchmark, nếu tính chính xác.
- Một repair riêng lẻ có thể không cải thiện decision.
- Hai error có thể bù trừ nhau.
- Gamma khác 0 không đủ chứng minh queue dynamics.
- Prediction accuracy không tương đương decision quality.
- Timescale backlog có thể giới hạn giá trị thông tin.

### Chưa có evidence đầy đủ

- State repair hay model repair quan trọng hơn trong network regime thực tế.
- Lợi ích có vượt practical threshold không.
- Dynamics explanation có dự đoán held-out tốt hơn threshold null không.
- Những cải thiện lý tưởng có thể triển khai với chi phí hợp lý không.
- Literature có còn research gap đủ mạnh không.
- Các kết quả có tổng quát hóa sang traffic model/topology khác không.

**Gap maturity:** G1 — Candidate Gap.

---

## 7. Phase 0 closeout assessment

### Technical preparation

Các tài liệu và phép tính tham chiếu đã có, bao gồm contract, evidence inventory, claim boundary, timescale note và running example.

Phase Review ngày 08/10 ghi nhận 11/11 test đạt và ma trận timescale khớp 40/40 ô. Đây là kết quả được báo cáo trong review, không phải phép chạy độc lập được thực hiện khi soạn tài liệu này.

Lần tích hợp này đã kiểm lại đại số bảng 2×2 và ba tỉ số timescale bằng số hữu tỉ chính xác, rà liên kết local và mapping D/DL/EV. Kết quả khớp bảng tham khảo; không thay bài tính tay/tự giải thích của tác giả.

### Ownership evidence

Bản giải trình hiện tại cung cấp nội dung để tác giả rà soát và sử dụng trong quá trình tự kiểm.

Nó không tự chứng minh rằng tác giả đã thực hiện các phép tính bằng tay hoặc giải thích độc lập không sử dụng tài liệu.

**Status:** Pending author verification.

### Independent review

Chưa có bằng chứng trong tài liệu được cung cấp rằng GVHD đã xác nhận Main RQ và Research Contract sau pivot.

**Status:** Pending external review.

### Phase decision

**Cập nhật quyết định 08/10:** yêu cầu tác giả đóng phase theo hướng dẫn mới được thực hiện bằng [phương án B](phases/PHASE_0_closeout.md): GO có điều kiện, mang V3/V10/V11. Khuyến nghị HOLD ở bản ownership trước được thay bằng record DL-009 này; các bài tự làm vẫn Pending. Chỉ tiến phân tích/exact nhỏ Phase 1; HOLD Phase 4 tới khi V10 đạt.

Không bắt đầu expensive simulation hoặc nâng claim novelty dựa trên bản giải trình này.

---

## 8. Các nội dung cần người thực hiện xác nhận

- [ ] Tôi có thể giải thích Main RQ và expected regret mà không dựa vào bản nháp.
- [ ] Tôi đã tính lại bảng 2×2 và các contrast.
- [ ] Tôi đã tự kiểm phép tính timescale và lý do sử dụng utilization trước quyết định.
- [ ] Tôi đã rà soát các lựa chọn và assumptions của Research Contract.
- [ ] Tôi đã kiểm nguồn gốc tài liệu và việc ghi nhận hỗ trợ theo quy định học vụ áp dụng.
- [ ] Tôi đã gửi pivot memo hoặc heads-up cho GVHD.
- [ ] Tôi đã nhận và ghi lại nhận xét của người đọc độc lập.
- [x] Bản kỹ thuật đã đóng băng và ghi decision log theo closeout B; các bước tự kiểm V3/V10/V11 vẫn mở, không được suy đã hoàn thành từ tag.

---

## 9. Hướng tiếp theo trong bản tham khảo

Sau Phase 0, vấn đề nghiên cứu đã được mô tả rõ hơn: cần đánh giá giá trị của thông tin state và response model bằng expected decision regret, chứ không chỉ bằng prediction accuracy.

Thiết kế 2×2 cung cấp cách so sánh có kiểm soát, nhưng các gain và interaction chưa phải evidence cho novelty nếu chúng chỉ xuất phát từ decision threshold hoặc lựa chọn baseline.

Timescale và observation schema là các điều kiện quan trọng quyết định use case có hợp lý hay không.

Theo closeout B, bước tiếp theo là phân tích/exact nhỏ Phase 1 đồng thời xử lý V3/V10/V11, chốt các tham số còn mở ở L1.8 và kiểm tra prior work tại Phase 2 trước khi đưa ra claim khoa học mạnh hơn.

---

## 10. Đối chiếu repo — phần nào còn chưa hoàn thành?

“Chưa có record” nghĩa là repo/nội dung được cung cấp chưa có bằng chứng hoàn thành; không khẳng định tác giả chưa từng làm ở nơi khác. Các ô dưới đây không tự đổi thành PASS khi chỉ thêm tài liệu này.

### 10.1. Đã có và đã chọn

| Mục | Record hiện có | Trạng thái |
|---|---|---|
| Working RQ và brief | [RQ card](lessons/L0.2_rq_card.md), [brief v0](00_research_brief.md) | Có bản DRAFT; tự giải thích/read-back còn chờ |
| Contract | [D1–D25, §0–10](01_definitions.md) | Có bản DRAFT và năm phép kiểm kỹ thuật; chưa đóng băng |
| B2 belief estimator | §5.2 bản gửi; [DL-008](02_decision_log.md) | Đã nêu lựa chọn B2; schema, exact/xấp xỉ và cách M0 dùng belief còn OPEN |
| Domain timescale | [T00](theory/T00_timescale_sanity.md), DL-008 | Đã chọn phương án A/cả hai neo; bỏ testbed làm neo |
| Bảng minh họa 4/4,25 | §3 trên; EV-22 | Có bảng đầy đủ và đối chiếu đại số; chưa kiểm nguồn Master Plan đầy đủ hoặc tự tính tay |
| Timescale | T00, script và tests | Review tại `b37545b`: 11/11 tests, 40/40 ô ma trận; không thay bài tự tính |
| Legacy/inventory/boundary | [Legacy](../legacy/INDEX.md), [inventory](00_evidence_inventory.md), [boundary](01_claim_boundary_v0.md) | Có tài liệu; các bài tự kiểm và giới hạn evidence vẫn giữ |

### 10.2. Những việc tác giả còn cần cung cấp

| Việc còn thiếu | Điền/lưu ở đâu | Bằng chứng để cập nhật trạng thái |
|---|---|---|
| Tự giải thích RQ bằng lời mình | [L0.2](lessons/L0.2_rq_card.md) | Bản viết lại sau khi che mẫu; xác nhận nội dung và ngày thực sự hoàn thành |
| Read-back với người thật — V3 | L0.2; [L0.7](lessons/L0.7_review.md) | Vai trò người nghe, ngày, nội dung họ hiểu lại và chỗ cần sửa |
| Phân loại state/observation/law/future, tự dựng episode | [L0.3 §1–2](lessons/L0.3_objects.md) | Bài phân loại và episode tự dựng có đơn vị/diễn tiến hợp lệ |
| Bảng quyền thông tin và ba tình huống leakage | L0.3 §3–5 | Bảng tự điền, câu trả lời và giải thích chỗ khác contract |
| Tự tính bảng 2×2 4/4,25 và contrasts | [L0.4](lessons/L0.4_estimand.md); §3 trên là tham khảo | Phép tính action/cost/regret/gain do tác giả tự làm, chưa chỉ chép đáp án |
| EV-20/21/25/26/27 và phản biện §7 | L0.4 §1, §3–5; [inventory](00_evidence_inventory.md) | Liệt kê path, diện tích, mixture, bù sai số và chứng minh theo đúng giả định |
| Chuỗi HC1/HP1 và self-check estimand | L0.4 §6–7 | Tự viết observation → mechanism → prediction → hypothesis → falsification |
| Tự kiểm ít nhất 5 dòng legacy | [L0.5](lessons/L0.5_legacy.md) | Record mở đúng tag:path, giải thích nhãn và giả định không mang sang; hiện 0/5 record |
| Tính tay timescale và SNMP | [L0.6 §1–3](lessons/L0.6_scope.md) | Phép tính riêng rho=0,8, so min hai tải, giải thích rho trước action và P/L/W |
| Lý do chọn B2/domain, assumption rủi ro nhất | L0.6 §4–5; [DL-008](02_decision_log.md) | Lựa chọn đã có; lời giải thích riêng và xác nhận assumptions còn chờ |
| Rà soát scope, objective, D22, quyền thông tin và các DL DRAFT | [Contract §10/phụ lục](01_definitions.md); [decision log](02_decision_log.md) | Xác nhận từng lựa chọn thật, ghi lý do khi đổi; chọn B2 không chốt toàn contract |
| Viết lại brief, kiểm thuật ngữ/chuỗi hypothesis | [Brief](00_research_brief.md); contract §10 | Bản tự viết/giải thích và record tự kiểm; kiểm 5 phút nếu thực hiện |
| Heads-up/pivot memo cho GVHD | [Heads-up nháp](meetings/2026-10-07_headsup.md), [bản chat](meetings/2026-10-07_headsup_chat.md) | Hai bản đang CHƯA GỬI; chưa có pivot memo riêng hoặc record gửi/nhận. Chỉ cập nhật khi có trao đổi thật |
| Người đọc độc lập và phản hồi — V10 | [L0.7 §1–3](lessons/L0.7_review.md) | Người đọc có quyền phản biện, commit/bản đã đọc, ngày, feedback và thay đổi; GVHD approval theo dõi riêng |
| Understanding artifacts — V11 | L0.2–L0.7 | Bài tự làm và tự kiểm các mục trên; nội dung tham khảo này chưa đủ |
| File 9/closeout, quyết định gate và tag | [DL-009](02_decision_log.md), [closeout](phases/PHASE_0_closeout.md), contract §10 | **Đã đóng có điều kiện B** theo yêu cầu ngày 08/10; `contract-v0` và `phase-0-closeout` ghi V3/V10/V11 mở. Bài tự làm và review độc lập vẫn còn |

### 10.3. OPEN được hoãn đúng chỗ, không phải tự điền số để đóng Phase 0

| Mục | Nơi quyết | Cần bổ sung |
|---|---|---|
| Observation schema theo telemetry regime | L1.8 | Backlog/rate đo được gì; quét tuổi giữ schema, đổi schema phải tách scenario/version |
| Belief và cách M0 dùng belief | L1.6–L1.8 | Posterior exact/xấp xỉ, prior, schema; quy tắc tích phân/mean-rollout nhất quán |
| Model baseline trung gian | L1.8 | Model nào xét biến động, cùng quyền thông tin và ngân sách; chưa có model triển khai |
| Slot/horizon, service capacity, managed load, backlog, telemetry grid | L1.8 | Running example, đơn vị, điểm ①–② cho mỗi neo; không khóa bằng số minh họa ở §3–4 |
| Mode persistence | Phase 1; lưới L1.8 | So thang mode với tuổi/delay, phân biệt refresh backlog và thấy mode |
| Phân phối episode D | L1.8 | Sinh state/history theo plant, prior phù hợp, báo theo điều kiện |
| Seed streams và exposure | L1.7–L1.8 | [Exposure register](00_exposure_register.md); tách discovery/confirmation, không nhìn seed để dành |
| Reference cost, practical/equivalence thresholds | L1.8 | Chuẩn hóa cùng thang cost; không chọn ngưỡng hậu nghiệm |
| Threshold null, H0/H1 và metric held-out | A05, trước confirmation | Fit budget, predictor biết trước action, tiêu chí đủ-dùng/biên kiểm |
| Primary literature và novelty | Phase 2 | Tự đọc closest work, exact claim matrix; giữ G1 |
| Feasible repair, timing/cost use case | Phase 8 | Đo được gì/tới controller lúc nào, action delay, net gain so baseline mạnh |

### 10.4. Phần thiếu nguồn và giới hạn kỹ thuật còn giữ

- Full Master Plan/PHASE_0 rubric và nguồn running example chưa được đối chiếu đầy đủ; bảng §3 cho phép kiểm đại số nhưng chưa tái lập dynamics.
- Primary papers mới có đối chiếu kỹ thuật, chưa có record tác giả tự đọc; các số SNMP/streaming thứ cấp cần nguồn measurement tốt hơn.
- Raw AoI chưa tái tính/khóa identity đầy đủ; bản sao backup ngoài máy, sandbox/máy khác chưa được xác minh. Xem [inventory — phần còn thiếu](00_evidence_inventory.md).
- Chưa có network evidence đúng RQ, held-out prediction hoặc repair timing/cost thật; không nâng G1 và không suy novelty từ bảng minh họa.

**Ưu tiên thực hiện:** viết lại RQ → tự tính 2×2/timescale → hoàn tất bài tự kiểm L0.3–L0.6/brief → ghi trao đổi GVHD và phản hồi người đọc → rà contract/DL → bổ sung record hoàn thành các điều kiện của closeout B; không di chuyển tag đã tạo. Các bước liên hệ người khác chỉ được ghi hoàn thành khi thật sự đã diễn ra.
