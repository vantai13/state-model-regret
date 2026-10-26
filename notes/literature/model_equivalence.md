# L2.7 Part B — “đủ tốt” theo thông tin và regret

Người phụ trách: **Doan Van Tai** ·26/10/2026 · AI-assisted, chưa L-self.
PartB có artifact kỹ thuật; toàn L2.7 còn primary P02 của PartA và human Gate.

## Ba nghĩa khác nhau

| Mức | Tiêu chí | Quan hệ / ví dụ |
|---|---|---|
| a: exact prediction | Jhat(a)=J(a) cho mọi action, ở các information states đang xét | Mạnh hơn cần thiết; small prediction error không đồng nghĩa exact equality |
| b: decision | Cùng action với M1, kèm same action set và tie Stay | Đủ cho cùng performance; common bias+2 vào cả action costs vẫn đạt b nhưng không a |
| c: operational regret | Chênh true expected performance ≤εE·Cref theo từng ô/pipeline | Có thể chọn khác action ở state có margin nhỏ mà vẫn đạt c |

Với cùng objective/law/action set/tie và đúng evaluation distribution:
**a⇒b⇒c**, không có chiều ngược tổng quát. Sign/tie xác định action; magnitude
true gap xác định loss. [Định nghĩa OεRE](terms.md#oεre--operational-ε-regret-equivalence-l27-part-b)
là mức c, không là contribution hoặc kết quả PC5 đã xác nhận.

V1 frozen: GM/Cref=**0 dưới S0**, GMgivenS1/Cref=**20% dưới S1**,
Cref=1,25packet·s. Cùng model pair có thể đủ dưới thông tin này, không đủ dưới
thông tin khác. Γ=GMgivenS1−GM; **Γ≠0 chỉ nói hai gains khác nhau**, chưa bảo
đảm chúng nằm khác phía εE. Code có ví dụ Γ≠0 nhưng cả hai đều equivalent.

## Cận gap và bài tập

Đặt a(z)=1[z<0] cho Switch, tie Stay. Với g=EΔ,h=EΔhat:
GM=(a(h)−a(g))g=abs(g)·1[action khác]≤abs(h−g). Nếu action khác thì h nằm ở
nửa trục đối diện g theo tie rule nên distance≥abs(g); action giống/g=0 cho0.
Áp từng x rồi lấy E cho **GMgivenS1≤E|Δhat−Δ|**. Đây là proof extension của
repo từ T01, không theorem được P12/R43 cung cấp.

- Bài tập hai state đồng xác suất: Stay cost10; true gaps(−0,01;+1), predicted
  gaps(+0,01;+1). Model chọn sai ở state thứ nhất; loss kỳ vọng0,005cost,
  Cref9,995; ratio=1/1999≈**0,050025%<0,5%**. Đạt c dù trượt b dưới S1.
- Expected error nhỏ không đòi từng state nhỏ: true gaps(−1;+1), predicted(+1;+1),
  weights(0,001;0,999) cho Eabs(error)=0,002 nhưng rare-state error2.
- Không thay Eabs(error) bằng abs(Eerror): true gaps(−0,5;+0,5), predicted đảo
  dấu, mean error0 nhưng S1 decision loss0,5. Không sửa contract từ các ví dụ.

## Đọc P12/R43 để giới hạn claim

[P12](papers/P12.md) **AI-T** official NeurIPS2020 §2/§3/§3.1:
VE là equal Bellman updates trên mọi π∈Π,v∈V và mọi state; richer test sets
thu hẹp class. Khác full dynamics vẫn có thể VE khi test sets bị giới hạn.
Chỉ khi gói cả h thành macro step/reward=−J, Π={Stay,Switch},V={0}, nó trở thành
exact action-cost fidelity của mức a. V={0} trong original MDP chỉ kiểm reward
một bước, không tự kiểm cumulative J. Không gán VE nói chung bằng mức a.

[R43](papers/R43.md) **lượt này AI-A**, có archived AI-T note24/10: AVE thay
equalities bằng tolerance và suy performance bounds (official abstract).
Không từ abstract kết luận OεRE khác mọi AVE/value-based formulation. Audit
A3/A4 còn cần primary norm/quantifiers/information mapping, không chỉ tên gọi.

## Định nghĩa và certification cần tách

εE=0,005, εR=0,01, numerical budget0,0025 theo D23/D24, không thay đổi.
Định nghĩa OεRE dùng **≤**, vùng xám **(εE,εR)**; εR thuộc phía relevance.
Exact bound đóng có thể chạm εE mà vẫn đạt; MC/TOST CI phải nằm strictly trong
open margins theo p<α. Interval cắt biên chưa chứng nhận, không tự chứng minh
non-equivalence. Error budget không phải error bar đã đo; còn phải bound
contrast và denominator Cref nếu Cref không biết chính xác.

Ví dụ chuẩn hóa: Ĝ0,001±0,001 →[0;0,002], đạt; Ĝ0,003±0,0025 →
[0,0005;0,0055], HOLD. CI90%[−0,004;0,008] không chứng nhận equivalence;
không được gọi p>0,05 là “như nhau”. Chỉ dùng input intervals minh họa, **không
chạy MC hoặc tính CI từ data**. Các numeric-label helpers là đề xuất reporting
trong lesson, không thay solver/protocol hoặc D24 mà chưa DL/version.

## K5 và câu trả lời reviewer

Luật κ≥2,A/Bq90,h8,eligible candidate khớp **M19–M22 và R03/R04**; ID list hay
κ=3 chỉ khớp4main,0held-out. **Chưa chọn luật**. Chỉ đọc tọa độ/design labels;
không J/margins/contrasts held-out. Xem [queue L3.3/A05](../lessons/L3.3_equivalence_queue.md).

Một ID list vẫn định nghĩa được finite claim trên chính list; nó không tự đưa
ra prediction ở test cells mới. Nếu R03/R04 trượt, không suy unique boundary
nằm giữa κ2 và3 khi thiếu monotonicity/control các tọa độ khác. R03/R04 chỉ
η0,5, chưa kiểm η0,75 hoặc toàn continuous region.

**Tự kiểm, đáp án AI:** “đủ tốt” phải ghi task/s/K/law/normalization; PC5 đang
chỉ S0; no-flip chỉ đủ, không cần. P12 là Bellman equality, OεRE là realized
policy-performance functional theo expectation. CI cắt biên thì HOLD. Chọn K
trước A04 hoặc record exploratory rồi freeze/test độc lập; không claim mới từ
definition. Tác giả vẫn cần tự đọc/giải thích, không tự điền Understanding.

[Report/commands/CSV](../../results/lessons/l2_7/part_b/report.md) ·
[PC5/K-M6–7](prior_boundary.md#l27-part-b--oεre-và-pc5-26102026).
