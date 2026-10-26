# L2.6 Part B — backlog, horizon và cấu trúc quyết định

Người phụ trách: **Doan Van Tai** · **26/10/2026**. AI-only; technical execution,
chưa thay tác giả qua Understanding/L-self/Gate. [Part A](freshness_decision_value.md).
[P13 và version/vị trí](papers/P13.md) · [report và commands](../../results/lessons/l2_6/part_b/report.md).

## 1. Fluid: hóa đơn cộng dồn khác trung bình

q(t)=[q0−rt]+, r>0; tdrain=q0/r. Đặt s=min(h,q0/r):
**I(h)=∫q(t)dt=q0s−rs²/2**, còn average=I(h)/h. Khi h≥tdrain,
I(h)=q0²/(2r). Đây là fluid illustration, không rollout v1.2 hay P13 replication.

| q0(packet), r2packet/s | h(s) | Cộng dồn(packet·s) | Trung bình(packet) |
|---|---:|---:|---:|
| 10 | 10 | 25 | 2.5 |
| 10 | 100 | 25 | .25 |
| 20 | 10 | 100 | 10 |
| 20 | 100 | 100 | 1 |

Gấp đôi q0 làm **giới hạn diện tích sau khi xả hết** gấp4; với h ngắn trước lúc
xả hết, I(h)=q0h−rh²/2 nên không gọi mọi finite-h cost là bậc hai theo q0.
[T00](../theory/T00_timescale_sanity.md) cho tdrain, dùng đúng tải trước/sau
decision tùy câu hỏi; đây không là mixing time của stochastic queue.

**D13 là endpoint sum**, không tích phân liên tục. Cùng fluid q0=10,r2,
h10/100: dt1 cho20; dt.1 cho24.5; dt.01 cho24.95, hội tụ tới25. Không tuyên bố
D13 ở dt hữu hạn bằng25 chính xác. qH đã được cộng dt·qH nếu còn backlog.

## 2. Từ P13 nhân với T — giữ đúng giả định và remainder

Theo Eq2.7 journal: ΩT=T⁻¹∫EQμ(t)dt−EQμ(∞). Theorem1, với fixed μ>λ và
đúng Lévy/moment assumptions, cho ΩT=A/T+O(T⁻²),
A=[EQ0²−EQ∞²]/[2(μ−λ)]. Nhân T:

**∫EQμ(t)dt=T·EQ∞+A+O(T⁻¹).**

Capacity term αμ có ở cả ΠT/Π∞ và triệt tiêu khi so fixed μ; contract không có
term này. A có thể **dương, âm hoặc0**, không luôn là một khoản phạt dương.
Bắt đầu đúng **cả phân phối dừng** thì không có transient ở mọi T; chỉ bằng
second moments mới bảo đảm leading coefficient0, không phải mọi transient0.

Với fluid constant drift, Q∞=0, A=q0²/(2r)=25 cho q0=10,r2. Phép đối chiếu
này không chứng minh công thức P13 cho ON/OFF queue hoặc cho state gain của repo.
O(1/T) của average correction không có nghĩa GS giảm theo h.

## 3. Gap: transient có thể bị lấn át

Ví dụ abstract Δ(h)=d·h+Z, Z=±3 equiprobable, không queue plant. Theo T03,
GSgivenM1=min(EΔ+,EΔ−):

| d(cost/s) | h | Hai gap | EΔ+ | EΔ− | GSgivenM1(cost) |
|---|---:|---|---:|---:|---:|
| .5 | 2 | 4,−2 | 2 | 1 | 1 |
| .5 | 8 | 7,1 | **4** | 0 | 0 |
| 0 | 2 hoặc8 | 3,−3 | 1.5 | 1.5 | 1.5 |

Ở hàng hai, EΔ+=4, sửa số “3.5…” trong lesson. Gain hết khi stationary-rate
term quyết định cùng dấu ở cả hai states; không phải transient Z biến mất.
“Gần nhau” về stationary cost không đủ giữ hai dấu ở **mọi** h: nếu d≠0,
h đủ dài vẫn có thể lấn át Z bị chặn. d=0 mới có ví dụ gain giữ nguyên ở đây.

Grid neo p_sw không bảo đảm hai dấu strict/density lớn tại0; ties vẫn có thể làm
value0. λA thay cùng lát; spoke h2 chỉ ở κ.3. Không cô lập tác động h hoặc kết
luận dấu/monotonicity của GS từ các ví dụ hay dải p_sw.

## 4. Bậc thang, bậc hai — phụ thuộc phân phối gap

**Continuous optimizer:** toy ΠT(μ)=(μ−5)²+2μ/T có μ*∞=5, μ*T=5−1/T.
Loss normalized=1/T²: T10 → .01, T100 → .0001. Nhân T thì cumulative loss
=1/T. Đây là Taylor illustration, không kiểm lại Prop5 bằng mô phỏng P13.

**S0 binary:** true mean gap−.5; predicted=−.5+b. Bias.4 → Switch/loss0;
bias.5 → tie/Stay/loss.5; bias.6 → Stay/loss.5. Với một observation mỗi ô,
GM=|EΔ|·1[hai action khác], nên có plateau/jump theo bias.

**S1 có thể có vùng quadratic:** nếu Δ có density liên tục f quanh0 và
constant action-gap bias b nhỏ, loss=∫wrong |δ|f(δ)dδ
=f(0)b²/2+o(b²). Cần các giả định đó; không tự là mọi model repair.
Với Uniform[−a,a], exact loss=min(|b|,a)²/(4a):

| a | b | Loss(cost) |
|---:|---:|---:|
| 4 | 1 | 1/16 |
| 4 | 2 | 1/4 |
| 2 | 1 | 1/8 |

Ngoài |b|≤a, loss bão hòa, không tiếp tục b². Narrower **uniform example** có
density lớn hơn; việc neo grid không tự chứng minh f(0) tăng. Ở dt hữu hạn,
posterior/gaps của repo có discrete support; S1 cũng có thể plateau/jump. Toy
Δ∈{−2,−1,0,1,2} đều nhau: b.25 cho loss0, b1 cho1/5; không quadratic gần0.

**Q-L27-01:** liệu Γ một phần đến từ policy errors/decision geometry thay vì
queue dynamics? Hai abstract cost-table examples không có queue cho:

| Gap distribution / bias | L00 | L10 | L01 | L11 | GM | GMgivenS1 | Γ |
|---|---:|---:|---:|---:|---:|---:|---:|
| {−2,−1,0,1,2}, b1 | 5 | 23/5 | 5 | 22/5 | 0 | 1/5 | 1/5 |
| {−3/2,1/2}, b3/5 | 5 | 17/4 | 9/2 | 17/4 | 1/2 | 0 | −1/2 |

Γ≠0 không tự nhận diện network mechanism. Bias toy không phải D21 conditional
mean rollout; chưa giải thích Γ trên grid. Đưa câu hỏi sang L2.7/A05, không tự
đổi null, fit model hay xác nhận hypothesis từ hai bảng.

## 5. Heuristic second moment — chỉ B, fluid và long horizon

Với r=μ−λB>0,0<u<r,η=u/r, long-h B-only cost difference là
**E[qB²]/2·(1/(r−u)−1/r)=E[qB²]/(2r)·η/(1−η)**.
E[q²]=(Eq)²+Var(q), nên cùng mean vẫn khác coefficient khi khác dispersion.

Ví dụ qB10,r2,η.75: coefficient75packet·s, nhưng h8 cho B-only difference
**39packet·s**, vì Switch chưa xả hết (tdrain20s). Không cắm75 vào episode8s.
Full Δ còn queue A, future modes và finite horizon; coefficient không là GS/F/V.
[H1-Q02](h1_candidates.md) chỉ là candidate AI/exposed, chưa chọn H1.

## 6. Ánh xạ P13 ↔ contract và điều cần sửa

| P13 | Contract / giới hạn |
|---|---|
| Lévy independent stationary increments, initial workload independent future input | Markov ON/OFF có memory; hidden mode ghép backlog/future law; không áp trực tiếp theorem |
| Work amount Q, speed μ chọn liên tục | Packet backlog, μ10 cố định; một Stay/Switch chuyển u giữa hai queue |
| Average workload+αμ | D13 endpoint cumulative occupancy; không capacity charge; c_sw0 |
| Fixed μ>λ cho stationary expansion | Main B mean sau Switch9/9.5<10: ON overload không tự là global instability |
| Finite-h optimization μ≥0, corrected μ có thể dưới λ | Không nói P13 yêu cầu ổn định cho mọi finite-h choice; repo giữ đúng locked domain |
| Fluid constant drift khi u2=u3=0 | M0 fluid-like conditional-mean input thường **time-varying**; không đồng nhất hai model |

**T-H1:** D13 đã tính dt·qH; không có surcharge riêng cho terminal backlog hoặc
cost sau h. Kết quả chỉ cho window đã khai báo, không long-run network loss.
P13 gợi ý end-of-period explanation tại **§6/tr289**, journal khác arxiv§5.3.
[Boundary](../01_claim_boundary_v1_2.md#t-h1--giới-hạn-diễn-giải-do-horizon-hữu-hạn-26102026).

## 7. Tự kiểm và Gate

Đáp án AI: Theorem1 nói average correction có leading term từ second moments
chia T; nhân T giữ constant có dấu; số25 kiểm cả triangle/integral; S1 quadratic
cần density/small constant bias, finite support có thể step; P13 không mô hình
hidden R2 modes nên không xác nhận κ/V. Đây không thay tác giả tự giải/đọc.

[K-F1…3/K-H1…4](prior_boundary.md#l26-part-b--horizon-và-transient-26102026)
đã lưu đúng mức đọc hiện tại, không dùng level cũ trong mentor. Technical Part A
và Part B đã có artifacts; **formal Understanding/L-self/Gate chưa xác nhận**.
122checks PASS trên teaching examples, không chứng minh P13 theorem/novelty
hoặc tính contrasts grid; giữ G1/HOLD Phase4, không freeze prereg A05.
