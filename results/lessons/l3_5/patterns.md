# A04 — mọi pattern đã xét, không chỉ pattern được giữ

Người phụ trách: **Doan Van Tai**. [DISCOVERY · post-outcome], sau score commit
`7005a3b1a5e0264be4faf205204f7675bd78f914`. **5 phát biểu đã xét, 1 candidate giữ**;
không cộng identities/sáu forecast branches/ba cheap-kill domains vào số5 này.
Các số dưới là interval-aware trừ D5 ghi rõ nominal. Full38×5 rows ở
`results/A04/20261027_01/pattern_checks.csv`; JSON scope/matches/counterexamples/
unresolved ở `patterns_considered.json`. Không chấm các dòng này như A03.

| ID | Phát biểu đã xét | Ô khớp/trái hoặc chưa phân giải | Quyết định |
|---|---|---|---|
| D1 | Trong lưới đã thấy, GM≥1% chỉ tại κ=.3,Aq90,Bq50,h8,target.3 | Miền dương M01,M03;36ô còn lại <1%, không ô trái | Giữ mô tả; không candidate mới: miền dương2ô, threshold giải thích đủ ở tầng sổ cái; không held-out cùng tọa độ |
| D2 | κ=1,h8: GM/Cref≤.005 trên miền tọa độ quan sát |16/16: M09–M16,M23–M30;0trái,0unresolved | **C1**, exploratory equivalence candidate; kiểm interpolation phải khóa riêng A05-F |
| D3 | Mọi ô h2 có GSM/Cref≥.01 |M31–M37 khớp; **M38 trái**, GSM/Cref=.0071474322 | Loại phát biểu “mọi ô”; không loại M38 để cứu pattern |
| D4 | GS≥0 ở mọi ô chính |32certified ≥0; **M18,M28 trái**;M19–M22 intervals cắt0 nên4unresolved | Loại; information harm dưới M0 không là phát hiện mới |
| D5 | K5 M19–M22 có nominal GS=F=V=0 |4/4nominal;EΔhat=0 từng ô | Mô tả route; không kết luận vật lý/novelty hoặc rằng joint repair không có giá trị |

## C1 — vùng model sufficiency tại κ=1 (post-discovery)

**Phát biểu đã quan sát:** tại κ=1,h=8s,A/B quantile∈{.5,.9},η∈{.5,.75},
target thiết kế∈{.3,.7}, tất cả **16 ô hiện có** có GM nominal=0 và upper
GM/Cref≤`1.3412526671280924e-12`, nhỏ hơn ngưỡng equivalence .005.
Không gọi residual enclosure đó là số regret thật dương; đây là upper bound.
Ô khớp đầy đủ: M09,M10,M11,M12,M13,M14,M15,M16,M23,M24,M25,M26,M27,M28,M29,M30.
Ô trái trong miền: **không có**; ô ngoài miền không được gọi là bằng chứng cho luật.
Không suy tính đúng cho mọi quantile/η hoặc mọiκ từ16điểm hữu hạn.

**Giả thuyết để xem xét ở A05-F, chưa khóa:** sufficiency còn giữ khi nội suy
quantile B=.75 hoặcη=.625 tạiκ=1,h8. Theo **tọa độ thiết kế** có sẵn, R05/R06
kiểm Bq75 và R07/R08 kiểmη=.625; chưa dựng D/đọc outcome của chúng. Đây là
mở rộng sau discovery, **không** là luật đã khóa trong A03, và không biến thành
forecast được phép chấm trước khi có A05-F. Không thêm ô nếu nó sai.

**Tầng sổ cái:** a00=a01 ở16/16; T01 giải thích GM=0 tại các ô đó. Điều T01
không tự cho là tại tọa độ nội suy chưa thấy hai action có còn trùng không.
`margin_route_diagnostics.csv` có dấu GS,bias,|EΔ|,E|eM|,q50/90/99|Δ|,F/V
cho mọi ô; không chỉ chọn vài ô đẹp. State repair vẫn có thể hại: M28 ở miền này.
C1 nói về model repair dưới S0; không nói M0 chính xác hay model repair dưới S1=0.

**Sáu giải thích thay thế đã kiểm/xác định giới hạn:**

1. λA khác giữa các lát, từ6đến8.5 trong miền; chưa tách được tác động κ với neo
   tải/backlog. Không dùng λA/p_sw thực của held-out làm feature hoặc nguyên nhân.
2. MT5: threshold geometry chưa bị loại. H1/H0 phải cạnh tranh cùng information
   budget ở A05; A04 không có causal identification.
3. Identity: GM=|EΔ|1[a00≠a01] được đáp ứng; chỉ coordinate association và nội suy
   là candidate, không nhận identity là contribution mới.
4. Thiết kế: chọn p_sw trong band/candidate không bảo đảm a00=a01. Không kiểm
   tần suất thực tế;κ=1 không phải random treatment.
5. Precision/dt:16/16BOUNDED, cặp1/120→1/240đạt; không cứu bằng loại ô HOLD.
   Không chứng minh dt→0; candidate sử dụng cùng dt đã khóa.
6. T-H1: chỉh8; không suy long-run, h2 hoặc terminal-cost objective.

**Prior gần nhất:** T01 trong repo là lý do đại số; các hồ sơ P12/AIS22/R51/P07
đã có trong catalog giúp đặt giới hạn model adequacy/decision quality. Lượt này
không đọc lại full text hoặc nâng author levels. [Phiên tìm có mục tiêu](literature/screening_summary.md)
sàng20records và để1đề xuất mới ở queue; chưa xác nhận theorem overlap hoặc novelty.

**Đưa sang A05-F:** có, như **đề cử post-discovery**, không tự chọn H1/null/metric/
fit/split, không tự freeze. L3.6 phải xác định phép bác bỏ và thông tin trước action
theo D25; có thể từ chối C1 nếu chỉ lặp threshold null. K5 từ A03 vẫn phải carry
nguyên văn và báo riêng; C1 không thay/mở rộng K5 hoặc Q-witness.

Không có cơ chế queue mới được xác nhận trong A04. Một candidate hợp lệ để kiểm
tiếp không đồng nghĩa đã loại được mọi giải thích thay thế; các mục còn mở ở trên
là lý do cần A05, không là bằng chứng causal.
