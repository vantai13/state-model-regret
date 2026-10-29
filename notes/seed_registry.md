# Sổ seed của repo hiện tại

Người phụ trách: **Doan Van Tai** · Cập nhật: **22/10/2026**.
“Đã xem” là đã đọc một đại lượng nghiên cứu từ seed/regime; xem thêm
[exposure register](00_exposure_register.md), gồm các seed lịch sử không được cấp lại.
Sổ này không xác nhận exposure trên mọi máy/sandbox.

| Stage | Root | Vai trò / phạm vi | Ngày tiếp nhận | Trạng thái | Regime / artifact |
|---|---|---|---|---|---|
| lesson-demo | 144558766427411771296652109119745142241 | future,predictor,branch; episode0–1999 | 22/10/2026 | Đã exposed qua đáp án tài liệu; được cấp cho demo L1.7 | [Card](lessons/L1.7_experiment_card.md), [config](../results/lessons/l1_7/config.json) |
| discovery | Chưa cấp | Phase4 | — | Chưa sinh/mở | Chờ L1.8/V10 |
| calibration | Chưa cấp | Fit H0/H1 | — | Chưa sinh/mở | Chờ protocol |
| confirmation | Chưa cấp | Sau freeze | — | Chưa sinh/mở | Chờ seed và regime chưa exposed |

Root demo được chép nguyên từ tài liệu L1.7 Part2. Tài liệu nói sinh bằng
SeedSequence().entropy ngày09/10/2026; đây là provenance do nguồn cung cấp,
không phải entropy sinh mới hoặc lịch sử đã được kiểm độc lập tại repo này.
Root này lớn hơn mọi dải số nguyên cũ được liệt kê trong exposure register;
điều đó không làm regime đã xem trở thành held-out. Không dùng demo cho claim nghiên cứu.

Draft cho demo: gốc theo stage, khóa con chỉ role và integer index≥0;
future=(1,episode,path), predictor=(2,episode), branch=(3,episode), episode=(0,episode).
Không đưa cell/action/model/K/variant vào khóa. Numeric encoding vẫn có thể vi phạm quy ước;
interface chưa cô lập quyền đọc. Chờ thẻ8 L1.8 khóa kiến trúc research contract v1.
Predictor hiện rút tuần tự K mẫu: prefix nested nếu cùng root/episode/H;
chưa có stream riêng theo sample k. RNG NumPy2.5.3/PCG64 được ghi trong config mỗi lần chạy.


## L1.8D v1 — schema stage × role, 22/10/2026

Khóa stage_root(discovery/calibration/confirmation) × role(episode/future/predictor/branch) × episode_id/future_id/branch_id. Pipeline/actor variant không nằm trong key future dùng CRN. Đây là làm rõ đề xuất L1.7, không cấp root: **roots_allocated=false, draws mới=0**. Phase3 exact không cần RNG. Cấp seed chỉ trước phase dùng tương ứng, không instantiate confirmation sớm. DL-019; machine schema trong notes/design/grid_v1.json.


## L3R.3 — audit/verification (DL-066, 28/10/2026)

Người phụ trách Doan Van Tai. Cấp dải **318300000–318399999** cho audit discovery,
không dùng confirmation. Một seed riêng theo regime/check/replicate; không đưa
action/pipeline vào future stream (CRN). Productionseed sau pilotNselection ghi
trongrun manifest; retry độc lập offset+50000, tối đa1 lần4N. Chưa rút trước
commitprereg; trạng thái cấp dải không có nghĩa mọi seed đã sử dụng.


### L3R.3 sau audit — 29/10/2026

Dải318300000–318399999 có roots đã dùng ghi trong
[used_seeds.json](../results/lessons/l3r_3/used_seeds.json). Seeds chi tiết đi kèm
N/check/regime/receipt; pilot2048 và production phân biệt, retry+50000 độc lập.
Root318351301 dùng cho X2065precision extension sau quan sát, không gọi là final
prereg ban đầu. Unit/symbolic-conservation tests của phiên MC ghi trongprovenance.
Không cấp lại roots verification cho confirmation.
