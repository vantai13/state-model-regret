# Contract v1.3 — đề xuất REFORMULATE, CHƯA KHÓA

Người phụ trách: **Doan Van Tai** · 28/10/2026 · DL-061.
AI soạn hướng thiết kế theo lựa chọn REFORMULATE của tác giả. Đây là proposal để
xem xét, chưa là contract được adopt, không tag `contract-v1.3`, không cấp quyền chạy.
[v1.2](01_definitions_v1_2.md) vẫn là contract của mọi kết quả Phase3.

## 1. Vì sao thay đổi?

v1.2 điều kiện theo một snapshot cố định mỗi ô; nó đo được gain/Γ theo D18/D19 nhưng
chưa đo giá trị bình quân khi controller gặp phân phối snapshots. PC4 không SUPPORT,
K5 bị phản ví dụ, nên tác giả chọn chuẩn bị thiết kế này thay vì chỉ NARROW danh sách.
Không lập luận “Γ vô nghĩa”; mixture cũng không tự khắc phục threshold geometry,
bảo đảm H1 thắng hoặc tạo novelty. [Gate A](phases/PHASE_3_gate.md), [T01](theory/T01_single_observation.md).

## 2. Thay đổi tối thiểu đề xuất

Giữ plant/Stay–Switch/quyền thông tin, θ chung, cost D13 trong window, và ý nghĩa model
repair D21 để có phép nối với v1.2; thay tầng điều kiện theo snapshot bằng population
observations được khai báo. Mọi thay đổi vật lý/objective khác phải có lý do và DL riêng.

Đặt c là điều kiện plant đã đăng ký (θ,u,κ,h,age…); Y là snapshot backlog hai queue
ở t0−age, không có mode; X là backlog/mode tại t0. Đề xuất:

1. Khai báo joint law `P_c(Y,X)` từ prior trước quyết định và kernel theo law của plant,
   rồi suy `p_c(y)` và `D_c(x|y)`. Không lấy uniform trên q50/q90 hoặc normalize vài
   observation thuận lợi thành population.
2. Mỗi policy S0 thay action theo Y; S1 nhận X. M0/M1 dùng cùng thông tin trong một
   hàng S, evaluator/oracle không nhận realized future w.
3. Định nghĩa loss đề xuất:

   `L̄_sm(c) = Σ_y p_c(y) E_{X~D_c(.|y)}[J_c(π_sm(y,X); X)]`.

   J đã là expected future cost theo D14; không cộng thêm hindsight realization.
   Tổng thay bằng tích phân nếu law quan sát liên tục trong một thiết kế khác.
4. Lấy sáu contrast từ bốn `L̄` theo cùng phép trừ D19. Từ T01:

   `Ḡ_M = Σ_y p_c(y)|E[Δ|y]| 1[a00(y)≠a01(y)]`, `Γ̄ = Σ_y p_c(y)Γ(y)`.

   Đây là hệ quả có điều kiện law/weights đúng, không phải contribution mới. Hòa vẫn
   được xử lý theo D16. Không trộn conditional probabilities của các y khác nhau.

**Đây là công thức proposal**, chưa thay estimand của report A04/A05-T hoặc prereg cũ.

## 3. Phải chốt trước mọi computation khoa học mới

| Hạng mục | Trạng thái / yêu cầu |
|---|---|
| Target population Y | OPEN: law stationary/transient nào, điều kiện trước action và managed u; cần một law coherent cho cả Y/X |
| Support/tail | OPEN: đầy đủ support hoặc certified truncation; ghi missing probability và cost impact, không bỏ y sau outcome |
| Normalization | OPEN: đề xuất C̄_ref=L̄11; ratio-of-expectations khác E[gain(y)/C_ref(y)], phải chọn trước |
| Grid và λA | OPEN: luật neo v1.2 theo y cố định không tự là luật accepted cho population mới |
| Metric/εR/εE/margin | OPEN: không carry nhãn0,5%/0,25pp như prereg cho estimand mới; chọn có lý do trước outcomes |
| H0/H1 và fit budget | OPEN: fairness thông tin/complexity, optimizer, features, selection và discrimination phải đăng ký lại |
| Exact/MC và budget | OPEN: convergence/tail/cost bounds hoặc seed schema/CI; chưa chọn runner hoặc chi phí tính |
| Discovery/test split | OPEN: tạo split mới trước computation/model selection; 10 R đã mở không còn clean test cho hypothesis mới |
| R09/R10 | Giữ niêm phong theo freeze cũ; không tự phân bổ làm test cứu redesign |
| Human/ownership | P0-V10/L8 OPEN; T05 vẫn trong experiments, không promote engine vì có draft này |

## 4. Thứ tự tiếp theo

Hoàn thiện proposal và reader packet → tác giả quyết các lựa chọn quan trọng → ghi
DL mới/prereg/contract có version → khóa split, law, metric, numerical budget → chỉ
thực thi Phase4 khi P0-V10 và các điều kiện mới đạt. Được học/thiết kế trên giấy lúc này;
không lấy tag closeout hoặc lựa chọn REFORMULATE làm waiver người đọc.

Không fit lại H1, không thử mixture trên outcomes R đã mở để tìm cấu hình thuận lợi,
không chạy model/simulation mới trong L3.8. Các định nghĩa/brief v1.2 giữ byte nguyên.
