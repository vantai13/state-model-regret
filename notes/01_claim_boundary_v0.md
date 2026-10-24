# Claim boundary v0 — C1–C5 xác nhận 07/10/2026; C6–C10, NC11–NC17, U8–U9 bổ sung 08/10 (chờ tác giả xác nhận)

Tác giả: **Doan Van Tai**.

Ranh giới dựa trên inventory hiện có và literature thứ cấp; Phase 2 kiểm lại bằng primary papers. Các nhãn C1–C5, NC1–NC10, U1–U7 là phán đoán tác giả đã xác nhận ngày 07/10; các dòng bổ sung lấy từ File 5/phương án A và thu hẹp theo nguồn/contract, chưa có record tác giả tự kiểm hoặc xác nhận. Không là bằng chứng mới về mạng.

## Được claim

| ID | Claim | Inventory support |
|---|---|---|
| C1 | Γ≠0 trong bảng intervention 2×2 tự nó không đủ suy ra network mechanism. | EV-01 |
| C2 | Switch-or-stay cũ tạo scoped evidence trong controlled-flow nhỏ; kết quả không tự chuyển thành evidence cho finite-load routing. | EV-02/03/04/07/08/11/17 |
| C3 | RQ hiện tại có tiền thân rõ trong N0/N1/N2, đặc biệt cách N2 tách information-related/model-related sources; chưa khẳng định đó là nguồn duy nhất. | EV-13/14 |
| C4 | N2 chưa cung cấp direct evidence cho Main RQ mới. | EV-13, scope và script S/M/P |
| C5 | Candidate hiện ở G1; chưa có network evidence đủ điều kiện G2. | EV-05/06/13/14 và bảng G-level |
| C6 | $\Gamma$ trung bình phụ thuộc phân phối episode $D$; một $\Gamma\approx0$ trung bình có thể che hai vùng trái dấu, nên kết quả phải báo theo điều kiện. | EV-25 |
| C7 | Với pipeline cố định, gain của một oracle repair không phải cận trên cho feasible repair cùng loại; $R_{00}$ là cận trên chung cho gain so với ô 00, với cùng $D$, objective và tập action. | EV-26; contract §7(f) |
| C8 | Khi không có clipping trên mọi path liên quan của các action, cùng input/belief và cách lấy kỳ vọng nhất quán, recurrence và objective tuyến tính, mean rollout cho đúng expected cost; model repair mean → law có giá trị 0. Một trajectory không chạm biên chưa đủ. | EV-20; contract §7(d) |
| C9 | Trong lưới fluid T00 đã khai báo, sàng lọc backlog phụ thuộc tỉ số $T_{\text{drain}}/(\tau_{\text{eff}}+d_{\text{act}})$: link 1–10 Gb/s có ①–② ở 5 ms; ở 1/5 s chỉ 10 Mb/s, 1000 packet còn ②; 30 s tất cả ③. Không suy gain thực tế dương/0 hoặc điều kiện cần cho mọi backlog/tải. | EV-28, EV-29, EV-31 |
| C10 | Trong mô hình contract (D5, AS1, capacity cố định, objective cộng hai queue cùng trọng số, $c_{\text{sw}}=0$, buffer vô hạn), Stay và Switch chỉ khác cost qua capacity bỏ phí; nếu không queue nào idle dưới cả hai action trên mọi path có xác suất dương thì mọi ô tương đương và mọi contrast bằng 0. Với cùng state/belief và action, $M_0$ không dự đoán cost cao hơn $M_1$. Đây là hệ quả đã biết, không phải phát hiện. | EV-32, EV-33; contract §7(g)–(h) |

## Không được claim

| ID | Claim bị cấm hiện tại | Vì sao |
|---|---|---|
| NC1 | State repair quan trọng hơn Model repair trong load-changing routing. | Chưa có experiment đúng world/interventions. |
| NC2 | Model repair quan trọng hơn State repair. | Cùng thiếu đúng-world evidence. |
| NC3 | N2 chứng minh State/Model interaction trong finite-action routing. | Pilot old-world, thiếu feedback; labels S/M không là hai repairs đó. |
| NC4 | Shapley cho biết % lỗi thực sự do State/Model. | Đây là allocation convention, không là causal identification. |
| NC5 | Chưa ai nghiên cứu câu hỏi này. | Search hiện tại không chứng minh absence toàn field. |
| NC6 | G1 nghĩa là novelty đã được xác nhận. | G1 vẫn là candidate gap. |
| NC7 | Tag/archive kỹ chứng minh kết quả cũ đúng. | Preservation khác validation. |
| NC8 | Đổi seed là đủ held-out confirmation. | Configuration/workload exposure vẫn có thể tạo selection. |
| NC9 | F7 là State-vs-Model decomposition. | F7 phân rã static/tâm/thuần/an toàn/thông tin. |
| NC10 | Old project thất bại. | Không dùng nhãn này; project tạo scoped knowledge và motivation. |
| NC11 | Refresh khả thi vô ích vì oracle $G_S\approx0$. | EV-26: sai số có thể bù nhau; xét cận chung $R_{00}$ và kiểm operator khả thi cụ thể. |
| NC12 | Use case link 1–10 Gb/s đã hợp lý bất kể tuổi/schema telemetry; hoặc vùng ③ chứng minh mọi State repair vô ích. | EV-28/31: ở tổng ≥0,2 s, các dòng link nhanh trong lưới T00 đều ③; cột 5 ms chỉ cho triển vọng timescale, chưa xác nhận backlog tới controller hoặc gain. |
| NC13 | $G_M\ge0$ hay $G_{S\mid M_1}\ge0$ là phát hiện thực nghiệm mới. | EV-27: $G_{S\mid M_1}\ge0$ do ô 11 = oracle; $G_M\ge0$ chỉ được bảo đảm trung bình với posterior chính xác, prior khớp $D$ và nhóm theo thông tin trước action. |
| NC14 | Contract v0 đã được người đọc độc lập chấp nhận. | Chưa có biên bản/record thật; không suy từ kiểm code hoặc tích hợp tài liệu. |
| NC15 | AoI đo trên testbed dt4n đại diện cho tuổi telemetry thực tế nói chung. | EV-10 là một prototype, không dùng làm neo; EV-31 có các thang thời gian khác nhau, chưa đồng nhất thành AoI. |
| NC16 | $G_M$ đo giá trị của “model fidelity” nói chung, gồm sai tham số hoặc sai cấu trúc. | D21/§5: $M_0$, $M_1$ cùng $\theta$ đúng và cùng recurrence; chỉ khác biểu diễn ngẫu nhiên (DL-010). |
| NC17 | Phase 0 đã được GVHD duyệt, hoặc GO WITH CAUTION nghĩa là đã có cơ chế mạng, novelty hay khuyến nghị vận hành. | DL-010 là review kỹ thuật tự động, chỉ chấp thuận tiến kỹ thuật; G1 giữ; phê duyệt GVHD là record riêng. |

## Chưa biết

| ID | Câu hỏi | Phase/phép kiểm sẽ đổi boundary |
|---|---|---|
| U1 | State repair giảm regret bao nhiêu trong finite-load world? | Analytical/exact pre-spike; controlled validation sau gate. |
| U2 | Model repair giảm regret bao nhiêu? | Cùng pre-spike và validation đúng world. |
| U3 | Hai repairs bổ trợ/thay thế nhau thế nào? | Intervention design, conditional gains và threshold null. |
| U4 | Boundary nào khiến repair đáng làm hoặc model đơn giản đủ? | Analytical/exact pre-spike, equivalence bounds và subsequent network validation. |
| U5 | Main RQ novel so closest primary literature không? | Phase 2: primary paper reading và exact claim matrix. |
| U6 | Timescale/cost intervention có hợp lý không? | System/use-case analysis, feasible repairs và latency/cost. |
| U7 | Effect generalize ra khỏi sandbox/minimal topology không? | Later phase, independent validation; chưa claim hiện tại. |
| U8 | Trong triển khai thật, backlog metadata tới controller mất bao lâu, và metric/schema nào cho backlog thay vì chỉ rate? | Phase 8; EV-31/T00 có số prototype về rate/control, chưa có đo backlog age tới controller phù hợp use case. |
| U9 | Literature value-of-information/POMDP đã trả lời $G_{S\mid M_1}$ (= EVPI về state hiện tại khi posterior chính xác và prior khớp $D$) đến đâu? | Phase 2: kiểm P11 và tìm ngoài thuật ngữ NDT; không suy novelty từ tên miền ứng dụng. |

Đối chiếu [inventory](00_evidence_inventory.md), [exposure register](00_exposure_register.md) và [closeout](lessons/L0.1_CLOSEOUT.md). G1 không phải xác suất nhận paper; giữ HOLD full study cho đến đúng gate. Các bài tự kiểm, read-back và xác nhận của các lesson mới còn chờ; không ghi đã học xong chỉ vì tài liệu được tích hợp.

## Quy tắc báo cáo bổ sung từ L1.4 — 21/10/2026

**Γ > 0 phải kèm phân bố pattern (i00,i10,i01)** và phân phối γ theo vùng điều kiện,
với hai action tất định, Δ≠0 và cell11 là oracle chính xác. Pattern (1,1,1) cho biết
phải sửa cả hai để cứu lựa chọn sai của ô 00; các pattern (0,1,0),(0,0,1),(0,1,1)
là bù sai số, sửa riêng có thể làm hỏng lựa chọn vốn đúng. Không suy dấu Γ thành
network mechanism hoặc khuyến nghị đầu tư. Khi Δ=0, mọi cost thật của hai action
bằng nhau; báo riêng, không chia γ cho margin bằng 0.

[Kết quả L1.4](verification/l1_4/report.md) tái lập trong ví dụ đồ chơi:
G_S=9/8,G_M=1/4,Γ=−1/4; γ từ −3 tới +2. G_M dương trung bình nhưng model repair
làm hại 1/2 tổng xác suất episode. Toàn bộ γ dương ở ví dụ này thuộc pattern (0,0,1),
chưa phải “cần cả hai để cứu lựa chọn sai”. Đây là E0/E1 theo dự đoán cho sẵn,
chưa đổi NC1/NC2, G1 hoặc xác nhận hiểu bài cá nhân.

Nếu gap11=Δ và I_Δ=0, pattern (0,1,1) không thể xảy ra, nên γ≤|Δ|.
Một episode có γ=2|Δ| với Δ≠0 và đúng các giả định trên bác bỏ cộng tính của gaps,
chưa xác định nguyên nhân là queue vật lý. Ở Phase 3, phải kiểm tính chất (b) trên
dự đoán thực M0/M1; lưới lỗi cộng không chạm hệ số 2. Đặc tả null/I_Δ đầy đủ vẫn chờ L1.5.

## Bổ sung L1.5 — identity, diagnostic và null (21/10/2026)

F5 là đồng nhất thức cho hai action và luật hoà Stay, gồm số hạng hoà; dùng để kiểm
code, không gọi “regret được giải thích bởi sai dấu” là phát hiện. Decision consistency
không thay regret: ở ví dụ chuẩn, ô 00 và 01 cùng 50% trùng oracle nhưng R=9/8 và 7/8.

I_Δ=d11−d10−d01+d00 là diagnostic trước argmin, khác gamma sau argmin. Khi belief
bằng posterior và hai ô S0 lấy trung bình dự đoán theo cùng belief, E_D[I_Δ|y]=0.
Đây là điều kiện cần dưới các giả định, không đủ chứng nhận posterior đúng; mean-zero
vẫn có thể xảy ra với D khác belief. Không dùng guard này cho nhóm mode/margin thật.
Báo E|I_Δ| và phân phối; đề xuất P(|I_Δ|>δ) với δ khai báo trước thay tỷ lệ exact I≠0,
để mang sang thẻ 9 L1.8. Chưa khóa δ, C_ref, epsilon_E hoặc convention quantile chính thức.

[Kết quả L1.5](verification/l1_5/report.md) cho I=(1/2,−1/2,0,0), E|I|=1/4;
guard phát hiện ví dụ D lệch với mean=1/8 và ví dụ hai ô dùng belief khác với mean=7/8.
Phản ví dụ D khác belief nhưng cùng kỳ vọng sai số model vẫn có mean=0.
Không suy I khác 0 thành cơ chế vật lý, hay từ ví dụ chuẩn thành bác bỏ RQ2/H0.

[Spec làm việc](lessons/L1.5_identity_diagnostic_spec.md) ghi điều kiện F5/F6, giới hạn
phép kiểm và yêu cầu cho H0/H1 ở A05. Family/features, split theo workload/parameter,
metric/biên lỗi và ngân sách fit còn chờ khóa; không cấp true gaps/errors của held-out
cho predictor. Chưa fit H0/H1 hoặc chấm held-out. Snapshot contract-v0, G1 và các gate giữ nguyên.

## Bổ sung L1.6 — S0/M0 end-to-end (22/10/2026)

Trong cấu hình hữu hạn đã kiểm, B2 khớp golden/posterior evaluator được khai báo riêng;
M0 dùng conditional means, Jensen và idle identity khớp. Bảng chuẩn giờ sinh end-to-end,
không nhập gap L1.4 cho sẵn. Đây là E0/E1, chưa chứng nhận mọi posterior/history/H hoặc mạng thật.

Matched posterior và aggregation đúng đủ để bảo đảm GM≥0; không viết “khi và chỉ khi
belief đúng”. Prior sai vẫn có thể cho GM≥0; mean I=0 cũng chưa đủ chứng nhận posterior.
Lưới đã xem có 0/864 GM âm khi matched và 5/576 khi prior sai. Phải kiểm prior/D,
shared belief và predictor definitions trước khi diễn giải GM âm.

Theo thứ tự backlog cũ→backlog hiện tại→state đầy đủ, GS chuẩn9/8 tách thành3/8 freshness
và3/4 mode visibility. Không gán phần thấy mode cho refresh telemetry/net gain khả thi.
Ô backlog hiện tại condition evaluator D nên vẫn là diagnostic. Các conditional rows với
history/D khác nhau không chứng minh GS đơn điệu; ba persistence points không xác lập quy luật mạng.

G_S given M1 có dạng EVPPI về state dưới posterior đúng; chưa đọc/đối chiếu P11 gốc,
không claim khái niệm giá trị thông tin là novelty. Phase2a cần đối chiếu P11–P13.
[Spec](lessons/L1.6_belief_model_spec.md) · [Kết quả](../results/lessons/l1_6/report.md).
Chưa khóa contract-v1/kiểm timescale vật lý; G1,V3/V10/V11 và HOLD Phase 4 giữ nguyên.

## Bài tự đọc ranh giới — chưa có bài làm của tác giả

Với mỗi câu, chọn “được nói / không được nói / chưa biết”, ghi ID và điều kiện cần giữ:

1. “Trong mô hình của chúng tôi, model repair luôn có lợi.”
2. “Với telemetry cỡ vài trăm ms, cập nhật backlog ở link 1 Gb/s gần như không giúp gì.”
3. “Nếu cấp state thật mà không giúp, thì refresh thật cũng không giúp.”
4. “Chưa có nghiên cứu nào về giá trị thông tin trong rerouting.”

<details>
<summary>Gợi ý đối chiếu sau khi tự làm</summary>

1. **Không được nói như vậy** — NC13. Bảo đảm $G_M\ge0$ cần các điều kiện posterior/prior/nhóm ở EV-27; không âm cũng cho phép bằng 0, không chứng minh luôn có gain dương.
2. **Chưa được suy gain từ bảng drain** — C9/NC12. Trong ma trận mới, 1 Gb/s có ①–② ở tổng 5 ms và ③ ở các cột ≥0,2 s; phải nêu backlog/tải, schema và tổng delay. Các nhãn thuộc **lưới và xấp xỉ T00**. T00 không đo gain refresh hay toàn bộ State repair, nên câu “gần như không giúp gì” vượt evidence hiện có.
3. **Không được** — NC11, phản ví dụ EV-26.
4. **Không được** — NC5; phạm vi prior còn là câu hỏi U9.

</details>

## Đính chính phạm vi C7 từ L2.3 — 24/10/2026

Giữ nguyên record C7/EV-26 lịch sử. Phản ví dụ oracle-state dưới fixed-M0 không
cho phép kết luận mọi oracle repair riêng lẻ đều không upper-bound feasible
repair. Với fixed information, matched posterior, true M1 và cùng objective,
action set, M1 là Bayes optimum: model-repair gain so ô00≤GM, hoặc so ô10≤GMgivenS1.
R00 vẫn là cận chung từ ô00. [T03 v2](theory/T03_primary_reading_start.md) và
[note P11](literature/papers/P11.md) có proof/toy; đây là AI-assisted reference,
không thay historical tags hoặc independent review.
