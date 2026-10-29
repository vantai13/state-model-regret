# Numerics v1.3.1 — resource extension v2, sau lần đo v1

Người phụ trách: **Doan Van Tai** · 29/10/2026 · DL-080.
Config: [prereg_extended_v2.json](prereg_extended_v2.json). Commit trước chạy.

Tác giả yêu cầu chạy lâu hơn để xác định khả năng máy,đề nghị GCP nếu cần.
Đây là thay ceiling sau khi đã thấy CPU-limit v1; không gọi là prereg ban đầu.
Giữ nguyên toàn bộ v1results và các thông số khoa học/card/measure.

- Chỉ chạy lại đúng3stationarymarginals bịCPU-limit v1:degree1200A,degree12000A/B.
  Không rút seed hoặc sample từ measure; không jointcost/gap/regret/contrast.
- Ceiling **1800CPU-s/2400wall-s/6GiBRSS/7GiBAS mỗi job**,1worker,BLAS1thread;
  tối đa7200CPU-s cho attempt. Worker/solver/kernel hiện tại không sửa.
- Reuse3anchorskhớp và3marginalscomplete từv1; không rerun chúng để lấy timing đẹp.
- Ghi rootfinding/LU phase,CPU/wall/RSS,error/certificate. Không nới ceiling trong
  attempt này; không bỏ một trong ba job vì kết quả không thuận lợi.
- Nếu không hoàn tất thì ghi đúng resource/error; không suy mọi thuật toán đều
  bất khảthi. Nếu cảba hoàn tất chỉ đạt gatefeasibility khi gộp evidencev1/v2;
  chưa cóglobalnumericsaudit,tagv1.3.1,n/root/CF hoặc permission Phase4.
- Budget này làcalibration, tách B48CPUh confirmation. GCPchỉ đang kiểm capacity/
  access read-only; không tựcreate/start/resizeVM hoặc tạo chi phí mới theo config này.
- Đã bổ sung helper V13_step1 vào source manifest; fullaudit tiếp phải kiểm
  transitive dependencyclosure vàenvironment. Cloud run nếu có cần manifest
  vàenvironment riêng, không giả định bitwise reproducibility qua môi trường.
