# L3R.4 — Công thức, kiểm chứng và đính chính lesson

Người phụ trách: **Doan Van Tai** · 29/10/2026. Soạn theo ủy quyền;
Understanding/read-back của tác giả vẫn OPEN.

Với input λ+aZ(t), Z∈{−1,+1}, hai holding times Exp(mean T), đặt g=c−λ.
Điều kiện: λ−a≥0, g>0. Nếu g≥a thì stationary queue luôn rỗng. Nếu0<g<a,
cân bằng dòng xác suất với hai drift −(a+g),a−g cho density mũ ở q>0:

θ=2g/[T(a²−g²)], Pbusy=a/(a+g), atom0=g/(a+g),
E[Q]=Pbusy/θ, virtual-time-average delay=E[Q]/c,
P(Q/c>B_t)=Pbusy exp(−θcB_t), B_t≥0 (strict exceedance).

Đây là kết quả **fluid liên tục**, không exact law của slot. Tail là thời gian
vượt mức của queue vô hạn. Không gọi là finite-buffer drop probability hoặc
thời gian chờ packet/end-to-end. Arrival-weighted fluid delay cũng cần định nghĩa
và weighting khác. Stationary law với λ_post chỉ là proxy sau đổi tải, không mô tả
transient phát sinh từ stationary law trước quyết định trong horizon h.

Cov(Z(t),Z(t+s))=exp(−2|s|/T). Tích phân covariance hai lần trên cửa sổ w cho
Var(mean rate)=a² f(2w/T), f(z)=2(z−1+exp(−z))/z².
Vậy CV_rate(w)=a/λ sqrt(f(2w/T)); f→1 khiw→0, f≈2/z khiw≫T.
Code dùng expm1 và Taylor khi z<.001 để tránh cancellation, không floor số âm
nhằm giấu sai số. CV của rate window khác CV interarrival và IDC.

T=κτ, h=(h/τ)τ. Cửa sổ thực1ms/10ms/100ms/1s không đổi theo anchor.
E[số CTMC jumps trong τ]=1/κ. Slot R2 có boundary flips kỳ vọng
120ref·[1−exp(−2/(120refκ))]/2, khác CTMC event count vì có thể nhiều jump
giữa hai đầu slot. Corr(mode_old,mode_now)=exp(−2/κ), không phải backlog corr.
Corr qua actuation=exp(−2d_act/T); đây là chỉ báo thông tin mode bị cũ,
không chứng minh dấu thay đổi của GS khi M0 sai.

Recurrence q_next=max(0,q+(r+u−c)dt) đồng nhất khi rates×k, mọi time×s,
q0×ks. Backlog×ks, area-cost×ks²; cần c_sw×ks² thì normalized contrasts mới
bất biến. Kiểm homogeneity dùng đường generic cho s=.01,k=1000; không chạy
quyết định/contrast mới. η_pilot=u/2 khác φ=u/(c−λB); a/c=.6 cố định.

## A1 đã chạy

Prereg [generic_prereg.json](../../experiments/R3R_04_realism/generic_prereg.json)
commit cbed2bc trước run. Exact event-driven Exp(T), không dùng xấp xỉ flip theo dt.
Ba trường hợp chung (λ,T)=(8,.1),(8,.3),(9.5,.1),c10,a6; 8replicate/case,
burn1000s, đo4000s/replicate; seeds318400000+1000case+replicate.
Q0=0 và initial mode đối xứng, không khởi tạo từ công thức đang kiểm.
Kiểm mean/atom/tail và CV_rate(10ms,100ms,1s) bằng exact path integrals.
18/18 so sánh đạt |delta|≤4SE+1%|formula|+1e−8, đã khai trước; replica SE là
ước lượng, không CI coverage chứng nhận. [CSV](../../results/lessons/l3r_4/generic/comparisons.csv).

## Những điểm sửa khi triển khai tài liệu

- `h_over_tau=h/tau` đi kèm `h_s=h*tau` trong snippet trộn h vật lý và tỉ số;
  API mới nhận h_over_tau rõ ràng, dùng chung một anchor.
- Simulator event-driven tránh lấy1−exp(−dt/T) làm xác suất R2 boundary flip.
- Không diễn giải buffer-tail thành drop, mode correlation thành queue correlation,
  hoặc stationary post-load thành transient thực. Không suy hướng GS từ actuation.
- Không coi throughput burst của ZLK17 là hidden-mode holding time của model;
  không coi utilization threshold của BAM10 là bound khả thi.
- Không gộp vùng MV và harm hoặc nhận chúng hầu như tách rời: overlay sẽ báo
  cả overlap từ discovery cũ sau labels. L3R.1 đã phát hiện14/20 MV trùng harm.

Chưa thay kernel, contract, estimator, metric hoặc ngưỡng nghiên cứu.
