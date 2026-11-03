# T10 — signed information value: stake và covariance

Người phụ trách: **Doan Van Tai** · 03/11/2026. Soạn theo ủy quyền cho L6.4;
không phải bản tác giả tự chứng minh kín sách hoặc human review. Đây là
đẳng thức kế toán và phản ví dụ toán, không hypothesis mới đã validate.

## 1. Estimand và điều kiện

X là current state, Y là observation cũ, trên **cùng joint law** của contract.
Δ(X)=J_Switch(X)−J_Stay(X), đã gồm c; J là expected future cost có điều kiện,
không phải realized path cost. a_o(Y),a_n(X)∈{0,1} là hai fixed M0 policies;
tie chọn Stay. Giả sử E|Δ|<∞ và expected costs hữu hạn. Action variables bị
chặn nên mọi tích/covariance dưới đây tồn tại. S1 ở đây gồm backlog+mode,
không mặc định là telemetry khả thi. Không đổi information sets/estimand.

Đặt F_o=E[a_o], F_n=E[a_n], δF=F_o−F_n, δa=a_o−a_n,
μ_Δ=E[Δ], α=h*s+c. Đơn vị Δ,α,G_S là packet·s; F và a không có đơn vị.

## 2. Phép dẫn

Chi phí conditional của policy là J_Stay(X)+Δ(X)a. Chi phí Stay triệt tiêu
trong hiệu hai expected costs. Do đó:

```
G_S = E[Δ δa]
    = μ_Δ δF + E[(Δ−μ_Δ)(δa−δF)]
    = α δF + (μ_Δ−α) δF + Cov(Δ,δa).
```

Cov(Δ,δa)=Cov(Δ,a_o)−Cov(Δ,a_n). Dạng chỉ center gap,
E[(Δ−μ_Δ)a_o]−E[(Δ−μ_Δ)a_n], cũng đúng vì E[Δ−μ_Δ]=0.
Với old observation, tower property cho E[Δ a_o(Y)] bằng
E[E[Δ|Y] a_o(Y)]. Đây là lý do phải giữ đúng posterior trong old_d.

H1 là αδF trong absolute cost: nếu α>0 thì misclassification rate là F;
nếu α<0 thì là1−F, nên |α|(mis_o−mis_n) vẫn bằng αδF. So với z_H1 frozen
còn phải tách numerical representation của F và normalizer Cref_H1/Cref.
Chia **cả ba phần** cho cùng actual Cref rồi nhân100 để được pp cộng được.

Covariance bằng0 **không tương đương** A1/A2. Δ≡α là điều kiện đủ để cả
stake error và covariance đều0; các sai số cũng có thể triệt tiêu dù Δ không
hằng. Oracle chọn Stay ở mọi state chỉ cho Δ≥0, không cho Δ không biến thiên
hoặc Cov=0. Tần suất Switch có thể tính xấp xỉ số, không “chính xác” liên tục.

## 3. Phản ví dụ: S|M1=0 không ép alignment bằng0

Hai state xác suất1/2, true gaps(1,3), old signal không có thông tin. Truth
chọn Stay cả trước và sau, nên S|M1=0. M0 có predicted gaps(-4,2): old mean
là-1 nên Switch luôn; fresh chỉ Switch tại state đầu. Khi đó:

```
μ_Δ=2; δF=1/2; G_S=2−1/2=3/2;
Cov(Δ,a_o)=0; Cov(Δ,a_n)=−1/2;
μ_Δ δF=1; alignment=1/2.
```

Thông tin mới giúp approximate policy dù không đổi optimal action. Vì vậy
không nhận câu “alignment chỉ tồn tại khi truth đổi action”, “S≈0 nên chỉ
còn bias”, hoặc “state mới chỉ giúp model sai khi S>0”. Đây là ví dụ quyết
định hữu hạn để kiểm logic; không phải physical routing experiment mới.

## 4. Horizon dài cần điều kiện nào?

Giả sử Δ_h=α_h+R_h, α_h=h*s+c. Nếu có bound đã chứng minh
B_h≥E|R_h| thì |G_S−α_hδF_h|≤B_h do |δa_h|≤1. Muốn bảo đảm dấu H1 cần
|α_hδF_h|>B_h; một điều kiện tiệm cận đủ là B_h=o(|α_hδF_h|).

μ_Δ/α→1 hoặc R_h(x)=O(1) tại từng x **không đủ**. Cần kiểm integrability,
tail và tốc độ δF_h, vốn cũng phụ thuộc h. Ví dụ trên hai state đều xác suất
1/2: Δ_h=(h−1,h+1),α_h=h,a_o=(1,0),a_n=(0,1). R bị chặn đều, δF=0, nhưng
G_S=−1 và alignment=−1 ở mọi h>1. Không có phần bias tăng tuyến tính để thắng.
T09§1–2 chưa chứng minh uniform transient bound cho routing law unbounded.
Không vay theorem hay thang hội tụ từ lesson hoặc từ P13 sang đây.

## 5. Cách đối chiếu cache

`tools/analyze_phase6_covariance.py` tái dùng SavedCache của DL137, không
đổi file cũ. Centered products được sum trực tiếp trên saved current/old
surfaces, không lấy G_S trừ hai phần rồi gọi residual là covariance.

Hai numerical grids xấp xỉ cùng joint law nhưng có thể cho μ_o≠μ_n.
Ghi riêng mass, mean drift và bridge F_o(μ_o−μ_n). Khi mass≈1:

```
alignment_common = Cov_old_direct − Cov_new_direct + F_o(μ_o−μ_n).
```

Code còn giữ phần new centering drift nếu μ_n lệch số float đã lưu. Không
giấu bridge trong covariance, không renormalize để làm khớp. Identity toán
trên common law và replay numerical là hai mức khác nhau. Shared profiles
không tạo independent validation hoặc error certificate cho continuous law.

## 6. Đính chính hai tài liệu lesson

- Ví dụ hai phần ở B027 dùng9.37 (α), không phải3.05 (μ_Δ); residual0.53
  packet·s gộp stake error với alignment, không phải riêng covariance.
- B015 alignment khoảng+0.72 pp, không “gần0” so với G_S≈−1.30%.
- Nhóm μ_Δ/α≈.72–.84 có5 điểm:3 nhãn '-',2 U; không phải4/5 âm rõ.
- r≈.91 và cutoff.7 là post-hoc trên13 điểm chọn có chủ đích, không null
  test, threshold adopted, causal attribution hoặc prospective prediction.
- Không có bug phát hiện trong các checks đã chạy khác với chứng minh
  không có bug; READY không loại mọi numerical bias. Không dùng chữ “loại”.
- Plan§7 hứa prediction/truth comparison; ratio là descriptive summary của
  so sánh đó, không một acceptance metric được preregistered riêng.
- “Phần nào thắng” dùng true Δ/Cov chỉ là identity đọc sau truth; không phải
  kill criterion cho predictor. Phép kiểm tương lai phải có predictor độc lập
  outcome và null/metric khóa trước; lượt này chưa tạo thiết kế đó.
