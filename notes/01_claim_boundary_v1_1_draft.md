# Claim boundary v1.1 — draft sau N1–N6

Người phụ trách: **Doan Van Tai**, 23/10/2026. Bổ sung cho [boundary v0](01_claim_boundary_v0.md); chưa là contract đã tag. [Closeout active](phases/PHASE_1_closeout.md) vẫn **HOLD**.

Một observation cố định trong mỗi ô và belief b=D làm hai policy hàng S0 có action hằng trong ô. Bổ đề N2 là hệ quả E0 của thiết kế: G_M=|EΔ|·1[a00≠a01] và G_S|M1=min(EΔ+,EΔ−). G_M=0 chưa đủ kết luận mean model đầy đủ; tại EΔ=0 nó còn có thể bằng0 dù hai action khác nhau. Cần báo EΔ, model gap bias và hai phần EΔ±, thay vì chỉ vẽ G_M. Hai mức quantile không tái tạo được population law của observations. [Proof và exact checks](theory/T01_single_observation.md).

Đổi benefit thành −cost và coi current state là nhóm inputs được tiết lộ, G_S|M1 có dạng EVPPI conditional on observation; đây là đối chiếu toán học, không phải khái niệm mới. Nguồn primary đã tiếp cận và giới hạn mapping VSS ở [reading note](theory/T03_primary_reading_start.md). Chưa có kết luận novelty cho interaction Γ; giữ **G1**.

Trục 1/κ được diễn giải là tuổi thông tin tương đối. Với quantile backlog và horizon r_h, quy mô backlog cùng đổi theo persistence; z chỉ là chẩn đoán dẫn xuất. Không claim persistence có hiệu ứng riêng đã tách khỏi tuổi thông tin và backlog scale. Finite-slot q90/κ chỉ gần bất biến, không đồng nhất chính xác.

Lưới v1.1 sẽ được chọn có chủ đích theo decision relevance. Tỉ lệ ô có contrast lớn không ước lượng tần suất xuất hiện trong mạng thật. Screen p_switch phải dùng cả Δt_screen và một nửa; khác phía acceptance thì gắn `unstable`, không dùng calibration. Chưa có screen này trong mốc 2 vì prior/budget của lưới chưa đạt.

A chuyển từ deterministic background sang ON/OFF làm đổi law, initialization và nội dung State repair. Tuple đã có m_A dạng placeholder; nay m_A có uncertainty thực. Các split freshness/mode visibility không so trực tiếp với toy hoặc v1, và chưa là lợi ích của telemetry triển khai được.

Idle identity và numerical certificates bảo vệ luật true oracle Switch iff Δ<0. Epsilon là precision alarm; không đổi mọi gap âm nhỏ thành tie. API sign resolution chưa thay cho error propagation end-to-end của B3. Stationary solver là prototype có error certificate theo assumptions đã ghi; 8/10 bộ vượt cap của construction hiện tại không chứng minh plant không có stationary law hoặc mọi solver đều bất khả thi.

Verification này không có episode mới trên candidate grid, Monte Carlo, CI lấy mẫu, network validation hoặc independent human validation. Human gates chưa có record không được đóng bằng proof/code tham khảo.
