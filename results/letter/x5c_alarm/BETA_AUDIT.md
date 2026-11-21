# Rà soát η của X5c

Người phụ trách: Doan Van Tai. Nhánh A η=0,3; nhánh B η=0,6.
Không sửa source nhập từ X5/X4b/V7-3; thay đổi dưới đây chỉ là trạng thái Python
trong từng process và được khôi phục khi rời `simulator_arm`.

| Vị trí đã rà | Cách η đi vào tính toán |
|---|---|
| `v7_3_sim.variable(..., beta=BETA)` | Default bắt 0,3 khi import. Cập nhật `__kwdefaults__['beta']` theo nhánh trước mô phỏng; tham số này đi vào active-link reduction `(1+beta)`, weights/load và native C++ call. |
| `v7_3_sim.mean_endpoint` | Đọc global `BETA` trong `b=BETA*(modes@w.T)` ở mỗi call. |
| `v7_3_sim.mean_rollout` | Đọc global `BETA` trong envelope, `T.Model(..., BETA, ...)` và zero-queue shortcut. |
| `v7_3_sim.warm_instances` | Chứng nhận zero queue dùng `(1+BETA)`; khi không chứng nhận được, các call `variable` dùng default đã cập nhật. |
| `v7_3_sim.forward_posterior` | Gọi `variable` không truyền beta; default đã cập nhật là cần thiết. |
| `x4b.mean_forecast` | `T.Model(..., S.BETA, ...)` được tạo mới; fallback `S.mean_rollout` đọc global hiện hành. |
| `x4b.pilot_work_proxy` | Hai envelope dùng `(1+S.BETA)`; ranking chạy bên trong context của nhánh. Work proxy tham chiếu pilot X4b được tính ở η=0,3 vì đó là η của phép đo cũ. |
| `x_geant.expected_loads(..., beta=S.BETA)` / `path_utilizations` | Default cũng bắt 0,3 khi import. Cập nhật `__kwdefaults__['beta']` để utilization lưu đúng nhánh. |
| `x4b.train_record` | Được gọi nguyên hàm, seed 7200005 và namespace X5C-B được bind tạm. Warmup và training-rate rollout đều chạy trong runtime η=0,6. |
| X5c outcome rollouts | `reference-decision` và `evaluation` đều gọi `S.variable` trong context của nhánh; chưa chạy truth. |
| `v7_3_sim.native`, `ev_te.native`, `ev_te.Model` | `_LIB` cache chỉ chứa binary, beta được truyền ở mỗi native call hoặc qua `model.beta`. Không có kết quả simulation cache theo η để tái dùng nhầm. |
| Train-cache / profiles / capacities nhập | Là TM chưa điều biến, mean profile và capacity; không nhân sẵn BETA. Nhánh B tính lại slope, không dùng slope η=0,3. |

`_initialize` đặt cả ba giá trị: `S.BETA`, default `S.variable` và default
`X.expected_loads`, rồi kiểm tra chúng trước worker job. Metadata từng bản ghi
lưu `beta` và `runtime_beta`; audit đối chiếu tất cả bản ghi đã chạy.

Test thực tế: worker spawn η=0,6 có queue 0,01 Mbit sau một bước 0,05 s
(load 1,6, capacity 1,4 Mbit/s); η=0,3 có queue 0. Mean cost tương ứng
0,00025 Mbit·s và 0; warmup zero certificate đổi nhánh đúng. Test kiểm cả
khôi phục defaults để không làm nhiễu test X5/X4b.
