# Thuật ngữ Part A

Người phụ trách: **Doan Van Tai** · 24/10/2026 · AI hỗ trợ.

| Term | Nghĩa dùng trong lesson | Nguồn/giới hạn |
|---|---|---|
| J(a;x) | Expected cost theo future law khi đã biết x; không phải realized-future hindsight | D14–D15 |
| EVPPI(x\|y) | min_a E[J\|y] − E[min_a J\|y] | SOB14 Method Eq4; T03 ánh xạ sang hidden state |
| RP | min expected cost khi chọn action trước realization | T03 định nghĩa trong finite decision problem |
| WS | E[min realized cost] khi được biết cả realization trước chọn | Có thông tin mạnh hơn oracle D15; không gọi L11 là WS |
| EV / EEV | Giá trị objective của mean-input problem / true expected cost của action do mean-input problem chọn | EV khác EEV; T03 |
| Conditional VSS(x) | EEV(x)−RP(x), thay future bằng conditional mean khi biết x | Identity của dự án; B82 chỉ abstract, không mượn theorem LP |
| EVPI(delta) / EVMI | Giá trị học discrepancy theo belief / diễn giải upper bound cho model improvement | P11 §2.4 Eq2.7; không đồng nhất với D21 |
| EVIU | Tên liên quan trong lesson seed | Original source chưa kiểm, không dùng như primary evidence |
| OεRE | Operational ε-regret equivalence theo pipeline và từng ô, xem mục dưới | L2.7 PartB, AI draft; chưa adopt vào contract |

Matched belief là điều kiện đủ cho các bảo đảm đã nêu, không phải điều kiện cần
cho equality ở từng instance. Dấu Γ không tự xác nhận network mechanism.

## OεRE — operational ε-regret equivalence, L2.7 Part B

Người phụ trách: **Doan Van Tai** · 26/10/2026. **Định nghĩa vận hành nháp AI**,
không phải kết quả nghiên cứu hoặc định nghĩa mới được literature clearance.
Chỉ nằm trong terms; đổi contract cần v1.2.x + DL, chưa thực hiện lượt này.

Cố định cặp model M0/M1, pipeline s∈{S0,S1}, objective/action set, phân phối
đánh giá D, miền K và Cref(k)=Lstar(k)>0 cùng ô/dt. Gọi M0 operationally
ε-regret equivalent với M1 trên K dưới s khi **mọi k∈K** thỏa:

`|L_s0(k)−L_s1(k)| ≤ εE·Cref(k)`, với εE=0,005 theo D24.

Chênh lệch L bằng chênh lệch R vì cùng trừ Lstar. Với M1 tối ưu true cost và
matched information/law: chênh lệch không âm, là GM khi s=S0, GMgivenS1 khi s=S1.
Không suy pipeline kia từ một pipeline; V1 có tỷ lệ tương ứng0 và20%.
Đây là nhãn dung sai; không mặc định có tính bắc cầu của equivalence relation.

**Miền và provenance:** K là predicate trên tọa độ đã khai báo, kèm eligibility
`candidate` và danh sách main/held-out matches. Không dùng SD/conservation/WD
để trình bày một equivalence discovery. Cref=0: giữ absolute output, relative
label không xác định theo D23; không chia hoặc tự thay denominator.
Khóa K trước A04, hoặc ghi K là exploratory từ A04 rồi freeze trước confirmation
và chỉ claim sau independent held-out test. Metadata held-out không là outcome;
không dùng p_sw/λA riêng làm feature, không tự đổi split của D25/A05.
Một finite ID list hợp lệ cho claim trên đúng danh sách ấy, nhưng không tự có
held-out generalization. **Chưa chọn luật K5**; xem [queue L3.3](../lessons/L3.3_equivalence_queue.md).

| Tỷ lệ thật | Ý nghĩa theo ngưỡng đã khóa |
|---|---|
| 0≤abs(G)/Cref≤0,005 | Trong biên equivalence của định nghĩa đóng |
| 0,005<abs(G)/Cref<0,01 | Vùng xám: ngoài biên equivalence, chưa đạt relevance threshold |
| abs(G)/Cref≥0,01 | Đạt ngưỡng practical magnitude; cần dấu G để nói gain/harm |

**Đề xuất cách báo sai số, chưa thành protocol inference:** nếu có certified
bound `Gtrue∈[Ĝ−eG,Ĝ+eG]`, denominator biết chính xác thì chứng nhận nhãn chỉ
khi cả khoảng nằm trong **biên đóng** ±εE·Cref. Chạm biên mà bound thật sự đóng
vẫn thỏa định nghĩa; khoảng cắt biên chỉ **chưa kết luận**, không tự bác claim.
eG phải là bound của **contrast**, gồm propagated solver/posterior/tail/rounding
errors; không lấy ngân sách0,0025·Cref làm một error bar đo được.
Nếu Cref cũng chỉ biết trong [cL,cU], cL>0: điều kiện đủ bảo thủ là
`max(|Ĝ−eG|,|Ĝ+eG|)≤εE·cL`. cL≤0 thì relative certification HOLD.
Không bỏ qua denominator uncertainty hoặc gọi estimated convergence error là
certified bound. D12/D24 giữ nguyên; cần DL/version nếu adopt quy tắc mới.

**Monte Carlo:** với CI hợp lệ cho đúng normalized contrast và fixed margin,
TOST hai phía α=0,05 dùng CI90% nằm **strictly trong** (−0,005;+0,005).
CI chạm biên không đủ reject theo p<α. Cần thiết kế CI cho ratio nếu denominator
ước lượng; không tự chia hai CI độc lập. `p>0,05` từ difference test không
chứng nhận equivalence. [TOSTER official docs](https://stat.ethz.ch/CRAN/web/packages/TOSTER/vignettes/IntroTOSTt.html)
phân biệt NHST/TOST và ví dụ CI; lượt này không chạy MC/TOSTER hoặc tạo CI từ data.

**Điều kiện đủ từ gap, kèm tie Stay:** S0 có
`GM=|g|·1[a(h)≠a(g)]≤|h−g|`, a(z)=Switch iff z<0.
S1 có `GMgivenS1≤E_D|Δhat(x)−Δ(x)|`. Expected absolute error nhỏ là đủ;
**không cần** error nhỏ ở mọi x. `|E(error)|` không thay được `E|error|` ở S1.
Không flip action là điều kiện đủ, không cần; true margin vẫn quyết định loss.

**Không đồng nhất VE/AVE:** [P12](papers/P12.md) Definition1 so Bellman updates
trên Π,V và toàn state space; [R43](papers/R43.md) có approximate constraints
và performance bounds. Chỉ trong **macro one-step embedding** với reward=−J,
hai constant-action policies và V={0}, VE trở thành exact action-cost fidelity.
VE tổng quát không tự là “mức(a)” của routing; không claim OεRE mới hoặc đã
chứng minh khác mọi formulation AVE từ một abstract.
