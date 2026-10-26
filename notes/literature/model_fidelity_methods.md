# L2.7 Part A — fidelity, oracle và factorial

Người phụ trách: **Doan Van Tai** · 26/10/2026 · AI-assisted, chưa L-self.
P03/P07 đã kiểm primary targeted; **P02 mới abstract, full text bị chặn**.
Part B/P12/OεRE chưa thực hiện. Contract/PC/forecast/G1/HOLD giữ nguyên.

## Đọc bài nào để hiểu gì?

| Nguồn | Vai trò | Trạng thái thực |
|---|---|---|
| [P03 = R51](papers/P03.md), ICML2026 | Model có fidelity tốt vẫn có thể chọn policy sai; expected decision regret đã có | AI-T PMLR §2–3/6.1–6.2/7.1 và appendix chọn lọc |
| [P07 DOTE](papers/P07.md), NSDI2023 | Networking đã tối ưu thẳng TE objective; oracle biết future demands | AI-T §2.2–3.3/4.1–4.2, không A như lesson ghi |
| [P02 Poelman](papers/P02.md), TR-C2023 | Sensitivity theo model/input errors, horizon và update frequency | AI-A official abstract; §2–4/hình còn BLOCKED |

P03 dùng learned dynamics, ranking loss và tập policies; D21 dùng hai model cố
định, thay mean rollout bằng đúng expectation. DOTE dùng historical demands →
split ratios lặp theo epoch; repo chọn Stay/Switch một lần từ backlog/mode
information. P02 là phương pháp control tác giả đã chỉ định, không mở thêm một
reading list ngoài networking. Khác setup không tự xác nhận novelty.

**Một câu khác biệt cho trục model:** repo đo giá trị của việc dùng đúng
conditional expectation thay cho mean rollout trên cùng cost/action set/law,
đặt cạnh state-information intervention; không đo giá trị học model discrepancy
của P11 hoặc lợi ích đổi training loss của P03. [P05/workflow](papers/P05.md)
đã được đọc ở L2.4, được dẫn lại làm bối cảnh, không giả một lượt primary mới.

## Ba kết quả đã kiểm

**1. Fidelity và decision quality.** P03 Theorem3.1 có KL/misspecification
assumptions và quantifier **tồn tại reward/Π**; không nói cải thiện MSE thường
hoặc luôn gây hại. A.1 dựng one-step/two-action counterexample. §6.1.3 có partial
observation; không viết “P03 chỉ full state”. §6.2 dùng expected-return regret
trong finite candidate set; MC500rollouts/policy ở B.4.2, không hindsight.
Vì vậy metric#5 trong [landscape](ndt_landscape.md) đã bổ sung P03.

Sign của estimated action gap xác định lựa chọn khi kèm tie rule. **Magnitude
của true gap xác định loss khi chọn sai**, nên “chỉ dấu quyết định regret” là
quá mạnh. D16 đã dùng true margin; không đổi metric hoặc thêm threshold.

**2. Oracle khác nhau thì gap khác nghĩa.** Với hai futures đồng xác suất:

| Ví dụ | Cost Stay(w1,w2) | Cost Switch(w1,w2) | Action tối ưu không biết w | RP | WS | Future EVPI |
|---|---|---|---|---:|---:|---:|
| Lesson | (2,6) | (4,3) | Switch | 3,5 | 2,5 | 1 |
| Bài tập | (2,6) | (6,3) | Stay | 4 | 2,5 | 1,5 |

Đơn vị cost minh họa, không phải ms/network measurements. Controller chọn đúng
có avoidable regret0, vẫn cách hindsight oracle1 hoặc1,5. Cùng action set/cost/
information law, `J(controller)−WS = [J(controller)−RP] + [RP−WS]`.
“Không xóa được EVPI” chỉ áp cho controller bị ràng buộc cùng thông tin trước
quyết định; thêm future information sẽ đổi bài toán. D15 biết x/law, không w;
P07 §4.1 biết future demands. P02 recorded-future comparator **chưa xác nhận**;
tuned MPC có future demand cũng không tự là global WS optimum.

**3. Ba ô OAT từ một anchor chưa xác định interaction.** V1 frozen có:

| Ô | 00 | 10 | 01 | 11 |
|---|---:|---:|---:|---:|
| Expected cost L (packet·s) | 1,25 | 1,50 | 1,25 | 1,25 |
| Expected regret R=L−L11 | 0 | 0,25 | 0 | 0 |

Lesson gọi L là regret: đã sửa ở đây. Từ anchor11: state-only error0, model-only
error0,25; additive prediction `L00=L10+L01−L11=1,50`, actual1,25.
Prediction error0,25 bằng **Γ**. Từ anchor00: GS=−0,25, GM=0, GSM=0;
GSgivenM1=0, GMgivenS1=0,25. Hai OAT ở hai anchor đối diện nếu gộp đủ bốn ô
cũng xác định được Γ; không khẳng định mọi sensitivity design đều thiếu nó.

GS/GM là **simple effects** tại baseline, không phải classical averaged main
effects. Average state effect=−0,125; model effect=+0,125. Với cost orientation,
standard cross-difference `L11−L10−L01+L00=−Γ`; gain synergy `GSM−GS−GM=Γ`.

Ba ô10/01/11 như V1 có thể hoàn tất bằng L00=1,25/1,50/1,75, cho
Γ=+0,25/0/−0,25 **ở mức đại số khi chỉ biết ba cost**. Các completions là bảng
trừu tượng, không khẳng định khả thi dưới J/law/M0 cố định của V1 hoặc D21.
Bài tập additive (L00,L10,L01,L11)=(4,3,2,1) có Γ=0.
**OAT đủ để cộng effects khi có giả định additivity hợp lệ**; ba ô tự nó không
kiểm được giả định đó. Full factorial là một thiết kế dùng được trong
sensitivity analysis; tự có factorial không chứng minh contribution/mechanism.

## Những điểm cần sửa so với lesson được gửi

- arxiv2303.00735v1 hiện có đúng tên DOTE, không xác nhận alias tên khác.
- P03 §6.1.3 báo65%/100% trên20seeds nhưng dùng known true ranking targets;
  full FQE pipeline từ §6.2. MLP main text/appendix chưa thống nhất, không tự
  chọn một cấu hình thật. Phần đã đọc không là audit toàn paper.
- Không kết luận P02 “không có tổ hợp”: cần kiểm bias×horizon/frequency và joint
  biases từ full text. Các số của lesson chưa trở thành kết quả đã kiểm.
- Không gán Γ<0 cho P02 hay Γ>0 cho P04/Fig8: khác interventions/estimands.
  Do đó chưa có cơ sở gọi hai paper là prior trái dấu của đúng D19.
- Một action loại cơ chế **sửa lặp sai số tích lũy bằng feedback**; vẫn có thể
  có state/model error compensation trong quyết định một lần. Không cấm mọi
  cơ chế “state bù model” theo thiết kế.

## Bài tự kiểm — đáp án AI, không thay Understanding của tác giả

1. Theorem3.1: với assumptions của nguồn, **có** reward và candidate policies
   làm model simulation-optimal xếp sai; không cho tần suất trên workloads.
2. P07 oracle biết realization demand của epoch; D15 chỉ biết distribution.
   Hindsight gap còn chứa future EVPI, nên không so trực tiếp các con số.
3. V1 additive-prediction error=Γ=1/4; đây là non-additivity, chưa là mechanism.
4. One-shot không reinitialize state rồi quyết định lại trong h; compensation
   trong một quyết định vẫn có thể xảy ra. P02 chi tiết còn đợi full text.
5. Trả lời reviewer: factorial xác định conditional effects và Γ trên cùng
   objective/distribution/actions. Nó có thể nằm trong một sensitivity study.
   Contribution cần điều kiện/cơ chế kiểm được, uncertainty bounds và null phù
   hợp; A05 còn mở, chưa chọn/khóa null từ lesson này.

[K-M1…5](prior_boundary.md#l27-part-a--trục-model-26102026) ·
[MT1…8 cho Phase4, HOLD](../phases/PHASE_4_methodology_threats.md) ·
[Report và phép tính](../../results/lessons/l2_7/part_a/report.md).

**Bổ sung 26/10 (L2.8 follow-up):** P02 full text nay đọc được qua VoR tác giả tải;
AI-T §1–§5 và Bảng 2. Thiết kế: bias một đại lượng mỗi lần, quét 1-D theo
prediction/update horizon, không joint bias; reference biết demand ghi sẵn.
Các dòng P02 ở trên là record lúc BLOCKED. [Note P02](papers/P02.md).
