# L4.3 — Audit có phạm vi: prereg trước physical calls

Người phụ trách: **Doan Van Tai** · 30/10/2026. AI triển khai theo ủy quyền.
Đây là verification trên discovery đã lộ, không confirmation, không chọn card/Gate4.
Các file code/config/cases/test trong manifest phải commit nguyên byte trước run.

## Phạm vi đã được tác giả chọn

Tác giả chọn nguyên văn: “Dùng A 466 dòng + AB 218 dòng theo file đề xuất
(khuyến nghị)”. Xem `scope_proposal.json`, `author_choices.json` và `cases.json`.

- A: amp6, κ/age∈[1/5,1],h/age∈[1,4],η≥1/2; mọi λ trong support map đã lộ.
  **466 dòng/450 tọa độ age1 phân biệt**. Không giả đã tái tạo ví dụ428 thiếu bounds.
- AB: amp6,λA∈[6,27/4],λB∈[13/2,15/2],κ/age∈[1/20,3/20],h/age∈[4,8],
  η∈[5/8,7/8]: **218 dòng/216 tọa độ**. Có73dòngκ/age=1/20; lớp C vẫn trong audit.
- Tổng684aliases,**666tọa độ**; chạy mỗi tọa độ một bundle và so với mọi alias pilot,
  giữ nguyên ảnh hưởng dt/age khác nhau, không chọn một alias thuận lợi.
- Chỉ c_sw0. Không làm tròn tham số; normalized age lấy Fraction chính xác.
  Khóa full6tọa độ phải có trong inventory discovery và không được trùng270CF.
- Không baseline mới (L4.4 chưa có spec), không vẽ hộp, không tải paper hoặc chạy CF.

## Exposure và dự đoán trước run

“Khi viết file này tôi đã thấy K6: 8 điểm, độ dịch lớn nhất 0,136 pp.” **Chỉ thấy
tóm tắt trong lesson**, chưa có native_probe_summary.csv hoặc tọa độ đủ8điểm.
Đã thấy XM2S110 được nguồn báo A→D/UNRESOLVED; chưa tự tái tạo kết quả ấy.
Đã thấy dữ liệu và bảng L4.1/L4.2; các dự đoán không mù đối với summary này.

Tác giả ủy quyền nguyên văn: “bạn có thể đống vai trò là tôi và ghi”. Ba câu dưới
được **AI soạn thay theo ủy quyền**, không phải tác giả tự lập độc lập. Không nâng
Understanding/ownership hoặc gán người thật đã dự đoán:

1. “Tôi dự đoán ít nhất80%aliases A có GS_native−GS_pilot<0, vì summaryK6 báo8/8
   âm. Đây là dự đoán về dấu, không phải một mô hình bias đã được fit.”
2. “Tôi dự đoán20–45trong466aliases A lật từ lớpA pilot sang lớp khác dưới point
   estimates native, vì một phần A nằm sát1%; tôi không dùng số lật làm điều kiện PASS.”
3. “Tôi dự đoán không quá dung sai ở A; ở AB, có thể có ít nhất một dòng quá0.25pp
   gầnκ/age=.05,h/age=8, vì vùng này ngoài coverage cũ. Đây là phỏng đoán AI,
   không evidence engine nào đúng.”

Nếu stop trước khi đủ mẫu, dự đoán toàn vùng là **NOT_EVALUABLE**, không chấm
đứng/sai từ vài điểm benchmark.

## Part A: tái lập và identity

Tag sạch `574a36fb4213a79d3d2aa305a489701cfc3059f2`, worktree tách riêng dưới/tmp.
Recount L4.1 chạy lại từ git blobs ghimtag (cùng SHA với working files tại tag);
không tự nhận đây là bài tác giả chạy tay. Tái lập14dòng: first/middle/last map2
resume log, plantrobust XPR0K/XPR0D (hai dòng sau restart),3map3age tuổi khác1,
6map1 lấy ID nhỏ nhất của mỗi lớp. Danh sách đầy đủ ở bit_specs.json.

Chín trường phải khớp **bit float64**, không epsilon: Cbar,Sbar,P_flip và sáu
contrast absolute. Không kiểm wall time. Thiếu danh sách6K2 gốc: sáu map1 mới là
supplement độc lập, **không giả là K2 gốc**. Kiểm8K6 nguyên bản vẫn BLOCKED_INPUT.
Nếu bất kỳ replay không khớp/lỗi/timeout, ghi HOLD và không chạy PartB.

## Part B: native benchmark trước ngân sách và full run

Mỗi tọa độ: **(640,4),(320,4),(640,2)**, native frozen và lean configuration như
confirmation. File raw write-once, resume chỉ sau kiểm config/ID/parameters/source.
Giữ mọi lỗi, không đổi source hoặc tolerance để cứu nhãn. Không dùng CF để timing.

Benchmark tuần tự4ca đã chọn trước: XM2S189, XM2S110, XM2X000, XM2X077 (IDs native
trong prereg.json). Nếu bất kỳ HOLD, dừng benchmark/full; các ca còn lại **NOT_RUN**.
Nếu cả4đạt, chốt ngân sách bằng rule đã khai:1.5×max bundleCPU đã đo ở mỗi zone
nhân số tọa độ distinct zone đó, cộng CPU đã chạy; feasibility cap8CPUh.
Budget receipt phải commit trước full. Vượtcap⇒HOLD_BUDGET, không tự đổi region.
Full có2worker; dừng schedule sau HOLD đầu tiên, giữ ca đang chạy và mọi artifact.
Job native cap1800CPU-s/2400wall-s, AS3GiB; pilot cap900CPU-s/1200wall-s, AS3GiB.
Scheduling cap8CPUh là giới hạn tài nguyên, không scientific threshold; ca in-flight
có thể cộng thêm tối đa hai job. Không tự triển khai cloud hoặc VM.

## Điều kiện không được nới sau kết quả

| Kiểm | Luật đã khóa |
|---|---|
| Bit replay | Đúng9trường mọi dòng; vi phạm⇒HOLD |
| Identity pilot | Như L4.1: diagnostic1e−12pp; không native-error certificate |
| Pilot/native | abs(shift)≤**0.25pp** cho GS,GM,Γ,GS\|M1,GM\|S1; G_SM vẫn lưu và kiểmR1 |
| R1 | Gọi **compare_levels gốc**: Cref, cả6contrast, cost-scale+ratio differences và sign flips; không dùng skeleton rút gọn |
| Arithmetic/validity | Raw arithmetic_pass literalTrue, validity_errors=[] và CF_computed literalFalse trên cả3mức; thêm lean arithmetic/consistency |
| Native identities | S07/S08,S11 cảhai vế,Γ lowerbound;1e−9pp chỉ cho algebra roundoff như skeleton, không convergence |
| Nhãn | Không giới hạn số lật; lưu point class và class ambiguity từ empirical refinement |
| R6 | d từ compare_levels (cost-scale+ratio) và arithmetic width; equality vẫn UNRESOLVED nếu không exactcertificate |
| R5 diagnostic | A dùngGS=+1%; AB dùngΓ=−1% chỉ để mô tả, chưa adopt SUBcard; báo N và unresolved/N ở cảrow/distinct scope. Không áp verdict CF vào mẫu thích nghi |
| R3 | Audit này giữ đúng3mức; R1 fail⇒HOLD. Không post-hoc nâng số để cứu audit; scorer/finite escalation của cardv2 giữ nguyên |

Raw validity và lean adapter có thể khác nhau: lesson yêu cầu rawTrue/errors rỗng,
nên audit này dừng cả khi rawguard fail mà lean tolerance vẫn đạt. Phân biệt hai
điều đó trong báo cáo, không tự gọi rawflag là proof physics bug.

PASS/PASS_LIMITED chỉ là **technical recommendation** theo kiểm đã khai. K2/K6
thiếu input luôn được ghi riêng; nhãn audit tác giả chưa xác nhận. L4.5 chỉ dùng
native từ phần audit đạt; HOLD chặn vẽ hộp/card. E11 không trích mức Lbar; độ dịch
0.25pp vượt là disagreement cần điều tra, **không mặc định native đúng hoặc chắc bug**.

## MC và giới hạn bắc cầu

Không suy triangle bound từ hai estimands/tọa độ khác nhau. Đọc coverage đã có
trước để xemκ=.05đã chạm đường code nào; chỉ thông sốκ nhỏ không tự là codepath mới.
Nếu pilot/native quá0.25pp, điều tra input/age/rounding, R1 của cảhai engine,
rồi MC độc lập nếu vẫn cần trọng tài. MC phải có design/seed/SE/resource prereg
riêng trước run; không tái dùng8node MC cũ như đã verify vùng mới. Chưa có cardSUB
được tác giả chọn, nên rule(ii) còn conditional ở L4.5; không tự mở research claim.
Giữ G1, P0-V10/L8/Understanding OPEN; không confirmation hay validation mạng thật.
