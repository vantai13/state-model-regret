# Chẩn đoán Lesson 3R.7 và lý do sử dụng GCP

Người phụ trách: **Doan Van Tai**. Kiểm tra ngày **30/10/2026, 09:35–09:40,
Asia/Saigon**. Phạm vi: đọc repo, log và trạng thái VM; không sửa source,
không chạy lại engine/MC, không đổi gate hoặc hạ tầng.

## A. Việc đã làm và phát hiện chính

Lesson hiện tại là **L3R.7**, chuẩn bị confirmation mới sau reformulation;
khác L3.7/A05-T đã chạy một lần. Nút thắt chính là numerical audit/freeze
v1.3.1 chưa hoàn tất. Thiếu n/seed/CF là các bước phụ thuộc sau đó.

Đợt full03 đã gián đoạn và hiện không còn tiến trình thực thi. SSH hiện vào
được, supersede tình trạng timeout/refused trong các snapshot cũ. VM bật không
đồng nghĩa job đang chạy. Runner hiện tạo thư mục output mới với
`exist_ok=False`, không có nhánh tự tiếp tục từ receipts sau reboot.

Trước đó có hai lỗi triển khai được ghi trong DL-087–088: dispatch trùng ID
ở full01 và thiếu precision fallback ở full02. Không coi lỗi chứng nhận số là
hypothesis bị bác bỏ. Hai bản sửa đã có trước full03, nhưng chưa có full03
closure để xác nhận numerical readiness.

## B. Lệnh và kiểm chứng thực tế

Các lệnh đã thực thi trong phiên:

```bash
git status --short
git log -4 --format='%h %s'
gcloud compute instances describe dt4n-research-01 --project=project-6b9ba053-75ff-440b-a6b --zone=asia-southeast1-b --format='json(name,status,machineType,lastStartTimestamp,lastStopTimestamp)'
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectionAttempts=1 -o ConnectTimeout=12 dt4n-gcp true
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectionAttempts=1 -o ConnectTimeout=12 dt4n-gcp 'python3 -'
```

Lệnh Python qua SSH chỉ đọc `/proc`, progress/receipts/log, XML test đã lưu và
hash của 108 source files. Python inline trên local đối chiếu SHA256 từ ba
manifest và đọc CSV; kết quả được lưu trong các JSON cùng thư mục.
Không chạy pytest lại trong phiên chẩn đoán; không thay code cần regression.

## C. Số đo và trạng thái

| Kiểm tra | Kết quả |
|---|---|
| Local SHA256 | PASS: contract 21/21, cards 10/10, numerical source 108/108 |
| Remote SHA256 numerical source | PASS: 108/108 |
| GCP API | RUNNING, n2-standard-8 |
| SSH | PASS, exit code 0 |
| Worker/controller của bộ tính tại lần đọc | 0 / 0 |
| Receipts full03 | 122 COMPLETED: 9 reference/marginal + 113 base |
| Vòng base calibration | 113/114 ca có receipt; chưa phải toàn audit PASS |
| raise_K / raise_ref | 0 / 0 receipts |
| Ca chưa có receipt/result/resource cuối | RATE_SH_EDGE_K3_H16 |
| pipeline_result.json / summary.json full03 trên VM | Chưa có / chưa có |
| CPU ghi cho 122 receipts đã xong | 4060.270453 giây CPU; chưa gồm CPU cuối của ca bị ngắt |
| XML preflight full03 đã lưu, đọc lại trên VM | 672 tests, 0 failures, 0 errors, 0 skipped |
| Test/engine/MC chạy mới trong phiên | 0 / 0 / 0 |
| n / confirmation root / CF mới | Chưa khóa / chưa cấp / 0 |

Progress cuối trên VM là 23:51:54 ngày29/10. Dòng `active` trong file này là
snapshot cũ: `/proc` hiện không có worker/controller tương ứng. Log ca cuối
dừng sau `cost_profiles_started` lúc23:52:12 ngày29/10, không có receipt cuối.
API ghi VM dừng23:53:31 ngày29/10 và bật lại09:19:08 ngày30/10.
Đây là bằng chứng có stop/start và mất tiến trình; chưa xác định vì sao VM
dừng hoặc cơ chế kết thúc chính xác của worker, không quy thành OOM/CPU limit.

## Vì sao có GCP, và giới hạn của bằng chứng

GCP được dùng theo DL-080/084 để cung cấp môi trường riêng cho các job nặng,
với VM 8vCPU/32GB danh nghĩa; hardware log quan sát khoảng31.3GiB usable.
Baseline local cũ có ca chạm CPU ceiling1800giây và sampled RSS5217.5MiB.
Nhưng chưa có benchmark cùng thuật toán/cùng đầu vào trên hai máy để kết luận
GCP nhanh hơn hoặc local không thể chạy phiên bản cải tiến.

| Phép đo đã có | Wall time | Giới hạn diễn giải |
|---|---:|---|
| Local baseline CAL_RATE_100_A | 806.568s | Một attempt |
| Local balanced candidate cùng ca | 19.925787s | Khoảng40.48 lần trong hai attempt cùng máy; không phải p95 |
| GCP balanced CAL_RATE_1000_A | 902.514s | Đầu vào khác ca local ở trên |
| GCP balanced CAL_RATE_1000_B | 329.654s | Không dùng làm so sánh tốc độ hai máy |

Full02 dừng ở posterior error bound chưa đạt1e-8, với peak RSS134.051MiB cho
ca lỗi; sampled RSS lớn nhất cả đợt165.3125MiB. Vì thế lỗi đó không phải chạm
CPU/RAMlimit; tăng RAM không tự sửa được. Full03 chưa hoàn tất nên chưa có
kết luận tương tự cho toàn bộ các cấu hình. Stationary bound nhỏ cũng không
thay full physical-cost/gain accuracy audit.

114 calibration records có tối đa7 mức/case, tức798 population evaluations
(cộng9 reference/marginal jobs); có thể đóng sớm nếu candidate đạt. 122 receipts
không phải122/123 của toàn audit. Budget calibration12CPUh và confirmation
48CPUh là hai budget riêng, không phải số giờ đã chạy hoặc ETA.

## D. Artifacts

- [Trạng thái remote và log cuối](remote_status.json).
- [Receipts và remote source integrity](receipt_integrity.json).
- [Ca bị ngắt và kiểm controller](pending_job.json).
- [GCP API](gcp_state.json), [tổng số kiểm](verification.json).
- Config: `experiments/R3R_08_population_numerics/prereg_03.json`.
- Source runner đã đọc, không sửa: `experiments/R3R_08_population_numerics/run.py`.
- CSV có sẵn: `results/lessons/l3r_7/full_numerics/report02/metrics.csv` và
  `results/lessons/l3r_7/extended_capacity/candidate_metrics.csv`.
- Không tạo CSV/chart mới và chưa export toàn bộ raw full03; JSON mới lưu
  trạng thái đọc trực tiếp, không thay raw hoặc summary cuối còn thiếu.

## E. Kết luận và việc tiếp theo

Đã xác nhận SSH hoạt động, artifacts đã ghi còn đọc được,122 receipts
COMPLETED và không còn job chạy. Chưa xác nhận full numerical accuracy,
timing p95 bundle hoặc v1.3.1 closure; Phase4 vẫn HOLD.

Bước tiếp theo là lấy đủ artifacts/cache/provenance full03, kiểm điều kiện
tiếp tục trong một execution record phù hợp trước khi khởi chạy lại phần thiếu.
Không chạy lại mù từ đầu hoặc ghi đè attempt03. Sau khi numerical audit đủ
evidence mới freezev1.3.1, dry-runB và áp luật chọnn/seed/CF đã duyệt.
GCP là một lựa chọn hạ tầng; yêu cầu nghiên cứu là tính đúng, kiểm chứng và
khóa thiết kế. Không có yêu cầu khoa học bắt buộc riêng nhà cung cấp GCP.
