**Phân loại B:** tái dùng được FIFO DES, nhưng cần adapter cho chronological split, stale posterior averaging và stochastic reference \(C_\mathrm{ref}\). Output EV-D4b/c hiện có chưa trả lời trực tiếp setting letter.

**Chặn dữ liệu:** trace local dài **4 giờ 0,07 giây**. Với train giờ đầu, hold 4 giờ cần tối thiểu **5 giờ 5 phút** dữ liệu; thiết kế 12 anchor chung cần **6 giờ**. Hold 1/2 giờ có đủ coverage, hold 4 giờ được ghi **DATA_BLOCKED**.

- **Thiết kế draft:** train trước test; stale/fresh cùng full state, chỉ khác tuổi; M0, hybrid dùng ŝ học trên train, stationary rule; \(C_\mathrm{ref}\) dùng Monte Carlo với stream chọn action và evaluation riêng.
- **Đã chạy:** `v7_2_audit` với ba lệnh `audit`, `pilot`, `estimate`, cùng pytest. **26/26 PASS**, lượt cuối **1,82 s**. Kiểm SHA256 khớp **1.200 raw outputs**, **540 train/probe files**, **28 mục source-lock**.
- **Compute:** pilot train-only tiêu tốn **0,065602 CPU-s**. Cấu hình draft 20 regime × 96 states ước tính trung tâm **11,68 CPU-giờ** cho 1/2 giờ, **23,09 CPU-giờ** cho 1/2/4 giờ khi đủ dữ liệu. Đây là ngoại suy, chưa xác nhận runtime hoặc precision ở hold dài.
- **Rủi ro:** một trace; mean-load panel ≤0,775; sign-law yếu gần \(\tau\approx T_\mathrm{int}\). Input hiện tại là counts dùng tạo **Cox arrivals**, chưa phải replay nguyên timestamp packet.

Đã lưu [báo cáo và bảng mapping](/home/vantai/state-model-regret/results/letter/v7_2/REPORT.md), [DESIGN.md](/home/vantai/state-model-regret/results/letter/v7_2/DESIGN.md), [source audit](/home/vantai/state-model-regret/experiments/letter/v7_2_audit.py), [inventory CSV](/home/vantai/state-model-regret/results/letter/v7_2/raw_inventory.csv), [compute JSON](/home/vantai/state-model-regret/results/letter/v7_2/compute_estimate.json), [test log](/home/vantai/state-model-regret/results/letter/v7_2/tests_final.log) và [verification cuối](/home/vantai/state-model-regret/results/letter/v7_2/final_verification.json).

**Không tính test outcome mới, không commit, không sửa file có sẵn hoặc thao tác VM.** Chưa tạo figure/card; bàn giao draft để Claude giải quyết coverage và viết card trước truth run.