# L2.5 Part2 — hai cơ chế thông tin có thể gây hại

Người phụ trách: **Doan Van Tai** · **26/10/2026**. Technical execution đã chạy;
AI-only, chưa phải tác giả qua Understanding/L-self/Gate. Tiếp [Part1](state_staleness.md).

## 1. Cơ chế và điều cần sửa trong lesson

| | Herding theo tin cũ | Dùng approximate model: V1 |
|---|---|---|
| Điều xảy ra | Nhiều decisions dựa cùng posted load cũ, tiếp tục dồn tải vào server trông rỗng | Thấy mode đúng nhưng M0 tính sai cost/đảo thứ tự action trong mode hi |
| Cần nhiều controller? | Không: một dispatcher lặp decisions cũng đủ | Một decision đã có thể xảy ra |
| Tại sao không phản bác VOI≥0? | So heuristic policies trong hệ động, không phải cùng bài toán Bayes tối ưu trên hai information sets lồng nhau | Controller tối ưu forecast sai; thiếu giả định true-model optimizer |
| Evidence | M00 §3.4, PDF10–12; P04 §III-A/IV-A | V1 enumerate exact, bảng bên dưới |
| Giới hạn contract | Episode chỉ một action giữ suốt h, nên không có chuỗi quyết định cập nhật-phản hồi này | M0 conditional mean rollout có thể có bias; chưa đo trên lưới v1.2 |

Tên “một controller” hay “load-aware” tự nó không loại herding trong mọi hệ.
M00 §3.6/PDF14 còn mô tả record-insert tính các arrivals đã đưa vào bảng;
không viết prior “không có model để sai”. Đúng hơn: trong phạm vi đọc chưa xác
nhận một controlled model repair đúng D21 và cùng estimand D19.

VOI không âm khi law/belief, objective, action/policy set khớp, policy dùng thêm
thông tin tối ưu và có thể bỏ qua nó; **không chỉ dựa vào số người quyết định**.
[T03](../theory/T03_primary_reading_start.md) ghi bộ điều kiện đủ của dự án.
Không suy G1–G5 là điều kiện cần cho từng instance.

M00 dùng randomness để giảm đồng bộ trong các cấu hình nghiên cứu; d2 không
luôn tốt hơn d3/random/centralized rules. Bản thực đọc là submission28trang,
khác TPDS2000 identity; xem [note và vị trí](papers/M00.md).

## 2. Bốn server — kiểm ví dụ, không replication

Ban đầu q=(0,3,3,3), thêm8 jobs, **không có service**. Ba policy stale dùng cùng
bảng cố định; d2 chọn uniform pair không lặp, hòa chọn đều. Convention không
lặp khớp footnote1 M00 PDF4; ví dụ này không phải queue experiment của paper.

| Policy | E[q cuối] (jobs) | max E[q] | E[max q] |
|---|---|---:|---:|
| Stale shortest | (8,3,3,3) | 8 | 8 |
| Uniform random | (2,5,5,5) | 5 | 409001/65536 ≈6,241 |
| Stale d2 | (4,13/3,13/3,13/3) | 13/3 | 3177203/559872 ≈5,675 |
| Fresh shortest, tie index nhỏ nhất | (5,4,4,4) | 5 | 5 |

Trong6pair, server1 được chọn ở3pair; ba server còn lại đối xứng nên xác suất
mỗi job là (1/2,1/6,1/6,1/6). Chưa service nên E[q]=q0+8p. DP exact kiểm đủ
phân phối terminal:1/165/165/1 states theo bốn dòng, tổng332records.
**max E[q] khác E[max q]**; không dùng bảng kỳ vọng tải để suy response time hay
optimality. Tie index của fresh toy được khai báo riêng, không gán cho M00.

## 3. V1 — tính độc lập, rồi đối chiếu helper cũ

Một slot1s, capacity3, managed U2, q0=(0,0). A={2,3}, B_lo={0,1}; hai mode
equiprobable, mỗi cặp arrivals có xác suất1/4 conditional on mode.
Cost: cuối slot qA+qB nhân dt=1s, **packet·s**. Tie chọn Stay.

Stay: [bA+2−3]+ + [bB−3]+; Switch: [bA−3]+ + [bB+2−3]+.
M1 lấy expectation qua arrivals; M0 thay arrivals bằng mean **theo từng mode**.
S0 average forecast costs qua mode, không chạy từ một mean-state trộn mode.

| Case/mode | J(St) | J(Sw) | J0(St) | J0(Sw) | S1/M0 | S1/M1 |
|---|---:|---:|---:|---:|---|---|
| V1, hi={1,6} | 3 | 5/2 | 2 | 5/2 | Stay | Switch |
| V1, lo | 3/2 | 0 | 3/2 | 0 | Switch | Switch |
| Bài tập, hi={2,5} | 5/2 | 5/2 | 2 | 5/2 | Stay | Stay (tie) |
| Bài tập, lo | 3/2 | 0 | 3/2 | 0 | Switch | Switch |

V1 hi/Stay: A góp3/2, B góp(0+3)/2=3/2; mean B chỉ góp[3,5−3]+=1/2,
nên underestimate1. Hi/Switch: B góp(0+5)/2=5/2, bằng cost tại mean;
lo cũng không có bias. S0/M0 forecasts=(7/4,5/4), S0/M1=(9/4,5/4): cả hai
chọn Switch. S1/M0 chọn sai Stay ở hi, tạo loss thực thêm1/2 trong mode đó.

| Case | L00 | L10 | L01 | L11 | GS | GM | GSM | Γ | GSgivenM1 | GMgivenS1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 | 5/4 | 3/2 | 5/4 | 5/4 | −1/4 | 0 | 0 | 1/4 | 0 | 1/4 |
| hi={2,5} | 5/4 | 5/4 | 5/4 | 5/4 | 0 | 0 | 0 | 0 | 0 | 0 |

V1 expected regrets R00/R10/R01/R11=(0,1/4,0,0); bài tập đều0.
Ở bài tập J0 vẫn bias Stay1/2, nhưng true hi gap=0: sai forecast không còn
trả giá khi chọn Stay. Vì vậy GS=0 **không chứng minh M0 đúng**. Các bài tập đã
exposed trước lượt tính; không có dự đoán mù hoặc score calibration cá nhân.

Jensen áp dụng cho fixed-action convex backlog cost của toy này. Không suy mọi
NDT objective đều có mean-rollout lower bound; variance tăng riêng nó cũng không
đủ bảo đảm Jensen gap tăng (cần convex order hay điều kiện thêm).

## 4. Những gì có thể kiểm trên lưới sau này

Nếu GS<0, trước hết audit posterior, objective/law, action/tie và numerical error;
sau đó kiểm statewise model bias, true decision gap và action flips. Dấu âm riêng
nó không xác định duy nhất cơ chế. Nếu GSgivenM1≥0 và GS<0 thì Γ>0 là hệ quả
**đại số** Γ=GSgivenM1−GS, không phải evidence độc lập của mechanism.

η đo managed load, không phải herd size. |Δ| không nhất thiết tăng đơn điệu theo u;
lưới matched-difficulty còn đổi λA theo lát, nên không quy mọi khác biệt cho η.
Chưa chạy lưới, chưa lựa H1/null, chưa dùng toy để xác nhận hypothesis hoặc G2.

## 5. P01, prior và A4

[P01 targeted screen](papers/P01.md): đã kiểm Def2/§2.5/Fig2; **AI-T**, không A.
Skip full read hiện tại vì parameter-learning proofs ngoài D21; quyết định này
có thể mở lại, không chứng minh paper không đe dọa PC2. Không thêm P01 thành
paper bắt buộc trong Excel. Metric/crossover là paper báo, chưa replication.

[K-S1…8, đoạn khác biệt và hàng đợi A4](prior_boundary.md#trục-state--l25-part2-26102026)
đã ghi cùng mức đọc. R04 có archived AI-T record từ24/10/2026; lượt này chỉ kiểm
provenance, chưa tái đọc primary. A4 cần đối chiếu điều kiện/control re-solving,
không chỉ đối chiếu tên “certainty equivalent”; chưa được nói GS<0 là mới.

## 6. Câu trả lời tự kiểm — AI soạn, không thay bài tự kiểm của tác giả

1. Hai cơ chế là repeated stale-feedback herding và policy conditioning lên model
   xấp xỉ sai; số controller không phân chia hai cơ chế.
2. V1 S0 chọn Switch nhờ average cost; S1 hi làm M0 chọn Stay do underestimate1.
3. Thay M0 bằng M1 thì state gain V1=0; T03/EVPPI bảo đảm không âm dưới giả định.
4. Kiểm matched posterior, law/objective/ties, numerical tolerance và statewise
   forecast/true gap; Γ>0 không là kiểm tra cơ chế độc lập.
5. Re-solving là prior cụ thể cần A4. Khác one-shot với sequential chưa đủ tuyên
   bố mới; phải kiểm E/M/R và điều kiện của R04. L2.9 mới chốt câu chữ.

## 7. Artifact và Gate

Code: [l2_5_information_mechanisms.py](../../experiments/lessons/l2_5_information_mechanisms.py).
[Kết quả exact](../../results/lessons/l2_5/part2/toy_results.json),
[CSV tổng hợp](../../results/lessons/l2_5/part2/summary.csv),
[log chạy](../../results/lessons/l2_5/part2/run.log),
[báo cáo/kiểm độc lập](../../results/lessons/l2_5/part2/report.md).
44checks PASS, V1 khớp helper L2.2 và frozen L2.3; Part1/PartA giữ nguyên số liệu.
Đây là technical completion Part2; **Understanding/L-self/Gate chưa xác nhận**.
Có thể học nội dung L2.6 theo lesson, giữ G1/HOLD Phase4; không tự mở Phase3.
