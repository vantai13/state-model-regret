# Numerics v1.3.1 — gate tính khả thi trước global audit

Người phụ trách: **Doan Van Tai** · 29/10/2026 · DL-078.
Machine contract: [prereg.json](prereg.json). Commit toàn bộ trước lần calibration.

## Câu hỏi và scope

Engine hiện tại có (1) replay đúng3anchor và (2) giải được stationary marginal
ở resolution1/1000 trong ceiling đã khai không? Đây là gate cần thiết, chưa
phải fullnumerics audit hoặc chứng minh hypothesis. Không sample CF/testseed,
không instantiate R09/R10, không tính joint outcomes cho rate probes.

## Thứ tự trước outcomes

1. Replay X2065(Stage2),X1008/X1009(Stage1),K40/ref1 bằng engine không sửa.
   So mọi numeric column trừ walltime và các cột array pairs theo bit pattern
   sau parse đúng dtype; containerNPZ có metadata nên không đòi zipbytes giống.
   Nếu thiếu c_sw trong archiveCSV thì kiểm với spec0, không tự bỏ sai khác khác.
2. Sáu stationary probes định trước: oldA marginal, rateclasses10/100/1000,
   SH-B rate1000 và κ3A/ref2. Chỉ stationary law/certificate/quantile/posterior;
   không joint J/gap/regret/contrast hoặc nhãn card.
3. Tất cả jobs ở bước1–2 đều chạy theo danh sách, không chỉ giữ ca thuận lợi.
   Một job không hoàn tất, certificate lỗi hoặc anchor lệch → **HOLD** trước
   globalcalibration. Không nới CPU/RAM,đổi lattice hoặc route sau quan sát.

## Ceiling cưỡng chế

Một worker,BLAS/OpenMP1thread;120CPU-s/job,180wall-s/job,4GiBRSS và5GiBvirtualAS.
Parent theo dõi /proc mỗi50ms vàterminateprocessgroup khi vượt; worker còn
RLIMIT_CPU120/125 vàRLIMIT_AS5GiB trước NumPy/physicalimports. Giữ stdout,
phase checkpoints,RSS/CPU/walltime và mọi lỗi. Tổng ceiling1CPU-hour cho attempt;
đây là resource budget calibration,không thay B48CPU-hours confirmation.
Ceiling này là phép kiểm vận hành đã khai,không phải chứng minh “không thể giải”.

## Nhánh có điều kiện và điều kiện freeze

Coverage metadata khai **96corners** của4vùng scored +8audit IDs,3levels/ID,
**312global jobs**. Candidate chính(K80,ref2),coarse(40,2)/(80,1);R3 hữu hạn
(160,2)rồi(160,4). Đây chưa là K*/ref* đã chọn. Toàn bộ schedule này chỉ được
activation bằng fullaudit prereg/receipt tiếp theo nếu stage0 PASS; không chạy
khi gate tính khả thi FAIL/UNRESOLVED. Stage0 không tự tạo tagv1.3.1.

Giữ route S1 y-quadrature và tailmass1e−4 của pilot trong feasibility baseline;
không ngầm đổi sang directπ/fluid/truncation. Tailmass nhỏ chưa chứng nhận
costmomenttail; fullaudit còn phải giải quyết cost/quadrature/tail/invariance,
R1–R8,κ3h16costs vàtiming/r coverage. Stationaryκ3 không tự cover horizon16.

Nếu gate0 HOLD: giữ nguồn/model/card/measure hiện tại, ghi measured blocker,
không cấp n/root/CF,không viết nullthành numericallevelsfinal. Cải tiến thuật
toán hoặc nới ceiling cần version/DL và phép kiểm mới; đổi rounding/measure
cần cardv2 trước frame. D22/human/Gate3R không được đóng bằng stage0.
