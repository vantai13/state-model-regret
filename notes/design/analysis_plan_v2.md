# Analysis plan v2 — Phase 6, L6.3–L6.4

Người phụ trách: **Doan Van Tai** · 03/11/2026. Đóng băng bởi DL-135.
Được soạn theo ủy quyền, không xác nhận tác giả đã tự vượt Understanding.

## 1. Câu hỏi và phạm vi

Trong plant v1.3, switching cost tại những vị trí D(ii) đã chọn có làm
G_S=L00−L10 âm như predictor H1, trái với geometry-only H0a, và có đủ
cặp c=0 dương/c>0 âm để mô tả sign flip hay không? Main RQ giữ nguyên.
Chỉ kiểm finite panel; không population CI/p-value hoặc cơ chế duy nhất.

## 2. Members và thứ tự

results/phase6/predictions.jsonl là danh sách duy nhất; SHA256 ghi trong
DL-135. Part B quyết PASS/ALL_MEMBERS: 27 members,13 D(ii),13 twin,A−.
Một cost/base theo DL-133, không thay point sau khi có truth. Engine dùng
eta=u/2, không u. Thứ tự A− B001C00 trước, rồi base ID tăng dần: twin,D.
Giữ denominator N_D=13, không chỉ chấm điểm đã chạy. Budget có thể hết
giữa cặp; partial được giữ và không gọi là paired comparison hoàn tất.

## 3. Đo và nhãn

Levels: main(640,4), coarse K(320,4), coarse dt(640,2). Signed G_S READY
theo DL-134: R1≤1/400 trên mỗi trục, width≤1/4000 tại cả ba levels,
không sign flip ngoài ±1/200. Không negative-contrast gate hoặc Cref gate.
z=G_S/Cref, Cref=L11; d=max(hai R1 deltas, main width), không certified
bound. '+' nếu READY và z≥1/200+d; '-' nếu READY và z≤−1/200−d; còn lại U.
Primary normalized ratio không phải expectation of episode ratios.

## 4. Verdict, A− và cặp

H1_SUPPORTED nếu có ít nhất11/13 D '-' và U≤1; H0_SUPPORTED nếu có ít
nhất11/13 D '+' và U≤1. U≥2 → INCONCLUSIVE; còn lại MIXED. Áp dụng chung
ceil(4N_D/5),floor(N_D/10) nếu Part B đã chọn reduced panel; freeze này
vẫn là N_D=13. N=0 hoặc execution incomplete không thể là SUPPORT.
A− phải có nhãn '-'; nếu không, dừng validity, không đọc hypothesis.
Twin '-' hoặc U không là BUG; vẫn báo đầy đủ. Cặp can thiệp chỉ là twin
'+' và D '-'. Chữ 'lật dấu' ở mức aggregate cần H1_SUPPORTED và ít nhất
11 cặp; thiếu thì chỉ báo k/N dấu âm, không dùng chữ đó.

## 5. Dừng, budget và gián đoạn

Không dừng sớm do U: khi verdict bị khóa INCONCLUSIVE, phần còn lại vẫn
có mô tả A2/twin theo lịch cố định; không tạo quyền chọn lại. Dừng vì
BUG, execution/resource failure, budget hoặc A− không '-'. Không retry,
resume, refinement hoặc P6 v1.1. Gián đoạn/mất điện giữ partial files;
EXECUTION_INTERRUPTED và verdict INCOMPLETE, không dùng subset cứu verdict.
Panel cap7200 CPU-s; call cap1800 CPU-s, wall3600 s; Phase6 cap14400.
Prior upper cụ thể chốt tại DL-135 sau positive control, cộng mọi charge
cũ/tests/guards/failures/controller/descendants; không reset nhờ cache.
Một worker, BLAS thread1, cache panel riêng phải chưa tồn tại trước run.

## 6. Bảng đọc kết quả

Bảng triển khai từ Part C §3; làm rõ k/N và U deadband để tránh câu quá rộng.

| Kết quả | Được viết | Cấm viết | Bước tiếp |
|---|---|---|---|
| H1_SUPPORTED, ít nhất11 cặp | Trong phạm vi §8, k/13 cặp đổi G_S từ '+' tại c0 sang '-' tại c>0, phù hợp H1 đã khóa; H0a dự đoán '+' tại D | Telemetry tươi có hại; cơ chế duy nhất; mọi switching cost; dải giúp dịch sang x<0 | L6.4 prior check; G-level tối đa G2-candidate theo quyết định riêng |
| H1_SUPPORTED, dưới11 cặp | k/13 D có G_S âm nơi H0a dự đoán '+'; báo twin không '+' | Chữ 'lật dấu' cho aggregate | Thu hẹp claim |
| H0_SUPPORTED | k/13 D phù hợp H0a và trái dấu dự đoán H1, báo ngoại lệ | H0 đúng ở mọi điểm; phase thất bại hoặc chưa đủ điểm | PIVOT-watch |
| MIXED | Liệt kê từng base và nhãn | Gần đúng; xu hướng SUPPORT thay verdict | NARROW |
| INCONCLUSIVE | U tại k/13 D do NOT_READY hoặc deadband; tách nguyên nhân | Kết luận H1/H0 từ các điểm còn lại | REFORMULATE |
| A− sai, BUG hoặc INCOMPLETE | Chỉ fact về vị trí/loại dừng và full denominator | Mọi hypothesis interpretation | HOLD/điều tra |

## 7. Mô tả, không thêm verdict

z prediction và truth cho mọi member; signed G_S và |G_S| packet·s;
S=G_S|M1,M=G_M|S1,Gamma; verdict sensitivity ε=1%; hai matched h pairs
B005/B015 và B027/B040. B004/B014 c khác nhau, không cô lập h.
Không fit lại H1/H0 hoặc chọn report thuận lợi. Zero denominator báo null,
không epsilon-floor. Raw flags giữ nguyên, không clamp số âm.

## 8. Điều kiện bắt buộc đi cùng claim

Plant fluid hai path độc lập; background Markov hai mode, a/μ=0.6, μ=10,
τ=1, buffer vô hạn, action tức thời giữ suốt h. P1 stationary pre-Stay,
epoch độc lập state; M0 conditional-mean rollout, S1 backlog+mode oracle.
0<x<theta(u), P≥30, h thuộc{8,16}, κ thuộc{0.1,0.2}; c đã chọn tương ứng
0.4006–10.6842%Cref_H1 stationary, không xác nhận chi phí vận hành thực tế.
H0a fit discovery c0; H1 zero empirical fit còn A1/A2 chưa được validate.
Predictor selection adaptive sau scan; probe cùng base là computed/sealed,
không clean held-out. Numerics diagnostics không chữa shared bias hoặc
chứng minh continuous truth/convergence. Realism/D22/ownership và G1 giữ
nguyên tới quyết định riêng; không CF/SUB,R09/R10 hoặc76 outcomes p4 mới.
