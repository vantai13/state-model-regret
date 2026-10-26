# Methodology threats — hàng đợi trước prereg Phase4

Người phụ trách: **Doan Van Tai** · L2.7 Part A,26/10/2026.
**AI-assisted draft / HOLD**. Đây là dependency queue, không là prereg, không
khóa A05/null/H1 và không xác nhận tác giả đã đọc hoặc đạt Gate.
P03/P07 AI-T; P02 mới AI-A, các vị trí §2–4 từ lesson còn chờ kiểm primary.

| ID | Threat chính xác | Evidence / giới hạn | Việc cần làm trước khi dùng trong prereg |
|---|---|---|---|
| MT1 | Bảng/sweep hay factorial riêng nó chưa đủ chứng minh contribution | P02 **official abstract** xác nhận sensitivity theo errors/horizon/update; nhận định contribution là đánh giá phương pháp của repo | Nêu câu hỏi, estimand, điều kiện/cơ chế có thể bác bỏ; không ép mọi claim phải dùng Γ |
| MT2 | Gap khác oracle không so số trực tiếp | P07 §4.1/printed1564–1565: oracle biết future demands; P02 §3.1 **pending**, recorded demand mới là lời lesson | Ghi objective/action set/info/normalization; tuned MPC dù biết demand chưa tự là global WS. D15 giữ nguyên |
| MT3 | Cost prediction accuracy chưa xác định decision loss | P03 §2–3/6.2, Theorem3.1 tồn tại; P07 §2.2–3.2. Sign xác định action, **true margin xác định loss** | Đối chiếu action flips, tie rule, signed gap và margin weighting dưới D16–18; không thay metric |
| MT4 | Tên NDT có thể rộng hơn intervention thực sự | Câu hỏi của repo/Attack12 L2.4; [landscape](../literature/ndt_landscape.md), NDT1/P05 notes đã đọc ở lượt trước; không có kết quả thực nghiệm mới lượt này | Nêu mapping/sync/what-if information nào được can thiệp và scope routing; gọi tên theo implementation/evidence thực |
| MT5 | Γ có thể xuất hiện từ decision geometry ngoài queue mechanism | L2.6 [PartB](../literature/horizon_transient.md), T01/T03; finite-support khác smooth-density assumptions | Chuyển Q-L27-01 sang A05 để thiết kế null cụ thể với cùng thông tin/budget/evaluation. Chưa chọn, triển khai hoặc freeze null |
| MT6 | Không chuyển kết luận one-shot sang repeated MPC | P02 abstract nói update frequency dampens errors; §4 reinitialization/state bias **chưa kiểm** | Phân biệt feedback sửa lặp với one-step compensation; không suy dấu D19Γ từ qualitative control story |
| MT7 | Có thể mô tả sai thiết kế của prior để làm factorial có vẻ mới | P02 abstract xét errors theo horizon/frequency; joint bias/crossed sweeps **cần full §2.2.4/§3.3/captions** | Kiểm design thực trước; OAT một anchor thiếu ô11/00 thì thiếu interaction, không khẳng định mọi sensitivity study thiếu Γ. Cần numerical bounds và mechanism/null evidence |
| MT8 | Existence theorem bị trích thành universal/frequency claim | P03 Theorem3.1/PDF3; A.1/PDF14 one-step/two-action construction; Theorem3.3 thêm local improvement | Giữ quantifier và assumptions; không dùng theorem xác nhận PC3 hay tần suất trên lưới |

MT2/MT6/MT7 còn P02 dependency; K-M5 cũng chưa đủ primary evidence. Mỗi mục cần
L-self/author review trước formal prereg. Không thay protocol/grid/threshold
hoặc coi các dòng này là Gate PASS. [Bài L2.7](../literature/model_fidelity_methods.md).
