# Mốc 2 — quyết định trước lưới v1.1

Người phụ trách: **Doan Van Tai** · 23/10/2026. Tác giả giao thực hiện toàn bộ phần kỹ thuật và lựa chọn phương án có căn cứ trong review; record này không chứng nhận bài kín sách/read-back hoặc human feedback. Không gửi heads-up theo chỉ dẫn mới của tác giả; lưu nháp trong repo.

Commit file này **trước** mọi tính toán candidate v1.1. Các test/toy không thuộc candidate và bản đồ tham số không có J được phân biệt rõ. Không có tag v1.1 khi gate understanding chưa đạt. Contract v1 và artifact cũ là snapshot lịch sử; active closeout chuyển HOLD, lịch sử tại tag không sửa.

| # | Quyết định | Căn cứ và hệ quả |
|---|---|---|
| 1 | Giữ p_sw acceptance [.1,.9] | Convention về mức liên quan quyết định, không ngưỡng gain thực dụng |
| 2 | Giữ ≥2/3 main qua screen, tối đa1 redesign tải A | Không xóa ô ngoài khoảng; p0/1 constant, ngoài khoảng khác là skewed |
| 3 | Chọn A ON/OFF độc lập B, cùng Tmode | A stationary dưới pre-Stay; nền không phụ thuộc lượng u |
| 4 | Giữ r_h=h/Tdrain_post,B | yB phải>0 ở main; nếu quantile0/trùng thì HOLD thiết kế, không tự đổi quantile; controls có h riêng |
| 5 | Quantile A/B .5/.9; A90 ở core | zA/zB là derived diagnostics; không claim persistence độc lập age/backlog-scale |
| 6 | Core18+spokes4+controls4, thêm1WD/1stress | Cấu trúc28 ô, chưa coi là grid đã qua kiểm |
| 7 | Giữ WD probe | GSgivenM1=0 có thể cùng GM>0; không gọi zero control |
| 8 | N2(a): một observation/cell | Thêm bổ đề E0; A04 báo EΔ, EΔhatM0−EΔ, EΔ+/EΔ−. Hai quantile không tái tạo population observation law |
| 9 | eps_num=1e−9*Cref, alarm uncertainty mass>.01 | Dùng làm precision alarm, không tự đổi true oracle hoặc gán mọi gap nhỏ thành0. Exact ties có certificate tách khỏi uncertified band; mass lớn buộc precision escalation, không báo PASS khi chưa resolve |
| 10 | Solver stationary số có kiểm soát đuôi, amplitude cố định | Tail target≤1e−12; báo thêm bound sai số law/posterior, residual hữu hạn riêng. Vượt tài nguyên/sai số thì HOLD, không clamp để có kết quả đẹp |
| 11 | dt_screen=age/120, kèm half-step | Screen allowed p_sw và numerical diagnostics ở hai mức; khác acceptance side→unstable, không calibration |

Thông số dự kiến để bản đồ khả thi có thể kiểm trước J: μA=μB=10packet/s; λB=8 với OFF2/ON14; λA={6.5,7.5,8.5} và OFF/ON=λA±6; age1s; κ={.3,1,3}; ηcore=.5 và ηspoke=.9 tại center λA7.5; ψ={−.15,−.05,+.05} ở core; r_h core1, spokes .5/3; quantile A90 core, B50/90, A50 spoke. u=η(10−8). Nền A giữ nguyên khi đổi η. Đây là lựa chọn được ghi **trước tính**, không phải outcome được chọn sau screen.

Giới hạn thực thi: prototype stationary cap≤50.000 queue indices; cap lựa chọn bằng analytic tail bound, không phải cố định rồi normalize tùy ý. Main quantile/posterior chưa được chứng nhận thì B2/B3 tiếp tục HOLD. Chưa chạy p_sw, margin hay contrasts trên candidate trong mốc này. Không đổi εR1%, sensitivity.5/2%, εE.5%, numerical discretization budget.25%, Cref same-cell/same-dt hoặc objective.

## N1 — tách toán học khỏi số học

True oracle vẫn Switch iff **true** Δ<0, exact tie Stay. R11=0 và bổ đề N2 nói về oracle này. Một numeric band gán Stay cho Δ<0 nhỏ sẽ thay policy, có thể phá R11=0 và GM≥0; vì vậy band chỉ đánh dấu cần tăng precision. Stable gap dùng weighted idle identity, integer/rational queue coordinates và assertions SD/WD/conservation. Nếu sai dấu hoặc không resolve được interval, dừng thay vì ép gap theo certificate. B3 cấm Lstar/margin outcomes: không tính Cref chỉ để screen; numerical checks screen dùng interval/certificates, Cref-band chỉ báo ở A04 khi Cref được phép tính. Không đưa mean-cost subtraction trở lại đường chọn action.

## N2 — supplement §7, không giả bài kín sách

Với observation cố định và b=D: a00/a01 hằng; a01=Switch iff EΔ<0; GM=abs(EΔ)1[a00≠a01]; GM≤abs(EΔhatM0−EΔ); GSgivenM1=min(EΔ+,EΔ−). Khi EΔ=0, GM=0 có thể xảy ra dù hai action khác nhau theo tie; không nói GM0 luôn có nghĩa cùng action. Bản proof và tests là technical reference, không commit `[kín sách]` thay tác giả.

## N3–N6 — sửa claim trước khi đo

ψ hai phía0 chỉ yêu cầu ở ηcore; high-η spoke ở center ổn định. Vùng generic ON/OFF khác vùng fixed amplitude±6: phải kiểm cả OFF≥0, ON+u>μ và mean load<1. Với η.9, ρBpost=.9+.1ρB; nó≥.95 **chỉ khi ρB≥.5**, không phải mọi ρB. Quantile/κ chỉ gần bất biến ở fluid limit; finite-slot rounding không cho equality tuyệt đối.

N5: p_sw chạy cả dt vàhalf, label unstable nếu acceptance class khác nhau; no reserve p_sw. Lưới được chọn có chủ đích theo decision relevance, không ước lượng tần suất gains trong mạng thật. N6: law D4, state D7, initialization D12 và State repair D20/D22 đều đổi khi A có mode; không chỉ đổi tọa độ lưới, không so trực tiếp splits với toy/v1.

Gate: P0-V3/P0-V11/V1/V8 còn evidence chưa có; full PHASE_1 source chỉ có digest rút gọn do reviewer báo, chưa kiểm byte gốc. Ưu tiên quy tắc HOLD được review trích; câu ngoại lệ từ Part E không dùng để mở gate. Không tag v1.1 hoặc chạy A01/A04 khi các điều kiện này chưa đạt. Phase2a có thể đọc song song; không claim novelty từ Γ hoặc các identity.
