# L2.6 Part A — độ tươi khác giá trị cho quyết định

Người phụ trách: **Doan Van Tai** · **26/10/2026**. AI-only, chưa L-self/Gate.
Theo attachment hiện tại: **chỉ Part A**, P13/backlog–horizon để Part B.
[Kết quả/commands](../../results/lessons/l2_6/part_a/report.md).

## K3 — bốn nghĩa của “giá trị”, viết bằng estimand

| Đại lượng | Công thức / đơn vị | Trả lời câu gì? | Điều cần giữ rõ |
|---|---|---|---|
| AoI | A(t)=t−u(t), seconds hoặc slots | Bản tin mới nhất đã giao được sinh bao lâu rồi? | Không đo error hoặc decision loss |
| Giảm bất định | Ví dụ H(mode trước)−H(mode sau), bit | Biết state chắc hơn bao nhiêu? | 1bit trong toy là Shannon entropy; không gán cùng đơn vị cho mọi VoI |
| Giá trị quyết định, model đúng | GSgivenM1=L01−L11=min(EΔ+,EΔ−), packet·s | Biết current state giúp chọn action giảm true cost bao nhiêu? | Matched belief/law/objective, optimal action, nested information; T03 |
| Giá trị state repair với M0 | GS=L00−L10, packet·s | Pipeline dùng conditional mean model được lợi/hại bao nhiêu? | Có thể âm; analog information-harm đã biết trong RM: K-RM1/R02 §5/PDF7 AI-T, L2.8 Part2. Không cùng intervention/cơ chế |

V1: tiết lộ mode hi/lo equiprobable giảm **1bit**, nhưng GSgivenM1=0,
GS=−1/4 vì M0 đảo action ở hi. Timestamp minh họa age1→0 là thiết kế teaching
riêng; finite-age R2 không thật sự độc lập mode. Không suy V1 là posterior ở
κ=.3 hoặc một ô v1.2. [V1 gốc](information_harm.md).

## Nguồn networking đo những gì?

| Nguồn / mức AI trong lượt này | Estimand và vị trí | Quan hệ / giới hạn |
|---|---|---|
| Kaul/Yates/Gruteser2012, **A** | Time-average AoI; abstract publisher/kho Rutgers; DOI10.1109/INFCOM.2012.6195689 | Có optimal generation rate trong FCFS abstraction; chưa kiểm full theorem |
| Maatouk et al.2020 AoII, **T** | §II/Eq3–9 arxiv1907.06604v2: time penalty × information-error penalty | Không chỉ “thời gian từ khi sai”; age/error đã có metric kết hợp, chưa bằng regret |
| AY19 Ayan et al., **T** | arxiv1903.05356v1 §2.2/Assumptions1,4; §2.4/Eq13–19: quadratic estimation error và link-specific uncertainty reduction | Không đo Shannon bit; biết system parameters. DOI10.1145/3302509.3311050, ICCPS2019:109–117 |
| R32 Soleymani et al., **A** | arxiv1812.07534v2 abstract: change in value function, rate–regulation tradeoff, Gauss–Markov | IEEE TAC67(7):3730–3737, **2022 issue**; DOI có2021. Không từ abstract suy mọi control assumption/bound |
| S11 Li et al., **T** | [Note S11](papers/S11.md), §III/Eq10, §VII-D/Theorem9/Cor2 | Known-kernel controlled source; optimal sampling/actions, không cùng D19. Journal TIT2026 đã xác minh, đọc arxivv3 |
| EVPPI state | [SOB14/T03](already_implied.md) | Bằng GSgivenM1 dưới điều kiện; không khái niệm mới |

AoII/AY19 được đọc thêm đúng definition để sửa bảng; không ghi metadata-only
hay abstract-only cho claim kỹ thuật đã xem. Record R32 targeted từ lượt trước
được bảo toàn; lượt này chỉ abstract/metadata, không tính thành lần đọc full mới.

Nguồn trực tiếp: [Kaul/Rutgers](https://www.researchwithrutgers.org/en/publications/real-time-status-how-often-should-one-update/),
[AoII §II](https://arxiv.org/html/1907.06604v2#S2),
[AY19 §2.4](https://arxiv.org/html/1903.05356v1#S2.SS4),
[R32 abstract](https://arxiv.org/abs/1812.07534v2).
Các statement là paper báo cáo; chưa replication các policy hoặc proofs.

## AoI: công thức nào đúng ở đâu?

u(t)=max{Si:Di≤t} là generation timestamp tươi nhất đã giao, không nhất thiết
packet đến sau cùng nếu out-of-order. Age reset về realized delivery delay d,
không về0 khi d>0. S11 Eq1–4/PDF3/5 dùng slots và holding action.

Với generation period T, fixed exogenous delay d, không mất/giao đảo thứ tự:
diện tích một răng liên tục T(d+T/2), nên time-average **d+T/2**. Với slotted
unit1 và các tuổi d,d+1,…,d+T−1: average **d+(T−1)/2**. Không hoán đổi hai
convention. Tăng rate trong queue thực có thể làm d thay đổi; công thức fixed-d
không tự là nghiệm tối ưu FCFS của Kaul.

Age tại đúng một decision không bằng time-average nếu decision phase không
uniform. D8 khóa age1s; repo không tối ưu AoI policy. AuD là prior được S11 §I
nhắc, chỉ là đối chiếu timing, không gán toàn metric AuD cho estimand D18.

## Mode: quay về cùng giá trị khác chưa từng đổi

R2 đối xứng, rate1/Tmode: p'(t)=(1−2p)/Tmode, p(0)=1;
p_same(t)=(1+exp(−2t/Tmode))/2. Correlation time a=Tmode/2 là **e-fold time**,
không phải thời điểm quên hẳn. P(không lần switch nào)=exp(−t/Tmode).
`src/smr/design.py:103` dùng cùng one-step keep; không sửa source.

| κ, age1s | P(same sau1s) | P(same sau8s) | P(không switch trong1s) | a(s) |
|---|---:|---:|---:|---:|
| .3 | .500636 | .500000 | .035674 | .15 |
| 1 | .567668 | .500000056 | .367879 | .5 |
| 3 | .756709 | .502414 | .716531 | 1.5 |

P(same) gồm cả0,2,4,… switches. Không đọc giá trị gần.5 là xác suất ít đổi;
chỉ là gần mất thông tin về mode đầu. Với κ3, đáp án “không đổi sau1s” phải hỏi
nghĩa: cùng giá trị cuối=.756709, không có switch nào=.716531.

## Backlog: heuristic input variance, chưa là posterior error

Stationary symmetric telegraph input có biên độ δ6packet/s, covariance
δ²exp(−|s|/a). Lượng input lệch mean trong cửa sổ τ có variance
**2δ²a[τ−a(1−exp(−τ/a))]**, từ tích phân covariance, τ1s.

| κ | Var/δ² (s²) | SD lượng đến (packet) |
|---|---:|---:|
| .3 | .255057 | 3.030192 |
| 1 | .567668 | 4.520623 |
| 3 | .810377 | 5.401257 |

Đây là **unconditional integrated input**: chưa phản xạ0, chưa điều kiện theo
snapshot y hay mode đầu; không phải Var(q(t0)|y) và không phải F của D22.
Trong queue thật, service/clipping và posterior có thể thay xu hướng; không kết
luận κ nhỏ/lớn luôn làm snapshot sai nhiều, F/V/GS tăng theo κ. λA còn đổi theo
lát matched-difficulty. [Hàng đợi heuristic H1](h1_candidates.md), chưa khóa H1.

## Điều kiện refresh có ích: trực giác và identity

“State đã đổi, còn ảnh hưởng trong h, đủ lật action” là gợi ý tìm cơ chế, **không
phải ba điều kiện cần/đủ tổng quát**. Quan sát thêm có thể hữu ích cả khi state
thực chưa đổi nhưng belief chưa chắc; còn margin nhỏ riêng nó không bảo đảm gain.

Với binary actions/cùng belief và true model, đặt Δ=J(Sw)−J(St):
L01=EJ(St)+min(0,EΔ); L11=EJ(St)−EΔ−. Hiệu bằng min(EΔ+,EΔ−).
Do đó gain strict>0 cần **cả hai dấu strict có positive mass**, với gap khả tích.
Nếu Δ=−1/2 hoặc0, mỗi giá trị1/2, p_sw=.5 nhưng EΔ+=0 và value=0.
Dải p_sw của grid/candidate **không tự chứng nhận strict gain**. Nếu thêm
|Δ|≤g thì value≤g/2, đạt khi Δ=±g equiprobable; không có bound g/2 vô điều kiện.

Bài tập đổi gap lo thành+3/2 (cost table giả định, không đổi queue plant):
giữ JSt(hi,lo)=(3,3/2), đặt JSw=(5/2,3). S0/M1 chọn Stay,
L01=9/4; S1/M1 chọn hi→Switch,lo→Stay, L11=2; gain=**1/4 packet·s**.
EΔ+=3/4, EΔ−=1/4, khớp min. V1 thật vẫn gain0, GS−1/4.

## Prior, tự kiểm và trạng thái

Networking đã đo freshness theo downstream cost; không nhận ý này là mới.
S11 formulation dùng Pa cho source bị action tác động, nhưng §VII-C còn có
approximate solver. “Mọi nguồn đều đúng model/không approximation” vượt evidence.
Threshold S11 nói nới **allowed sampling budget**, không phải mọi sample thêm.
GS/Γ với D21 còn chờ A4/L2.8, không từ hai keyword queries kết luận vắng prior.

Đáp án tự kiểm AI: định nghĩa/răng cưa ở trên; giảm entropy không đổi argmin
thì decision value có thể0; κ3 sau1/8s có same probability .756709/.502414;
backlog cần xét tích phân input+queue posterior; khác S11 còn ở intervention
D21 và estimand one-shot, không phải chỉ khác tên NDT. Đây không thay bài tự
kiểm của tác giả hoặc tạo forecast mù sau exposure.

293checks PASS trên ví dụ; không outcomes lưới, không xác nhận PC6. Có thể học
Part B/P13 tiếp; **Understanding/L-self/formal Gate còn mở**, giữ G1/HOLD Phase4.
