# Bước numerics freeze — DEFERRED, chưa chạy

Người phụ trách: **Doan Van Tai** · 29/10/2026 · deadline: trước L3R.7 rút CF.
Đây là kế hoạch đóng phần11b, không phải kết quả audit PASS hoặc lịch hẹn tự động.

1. Sau khi vùng/card L3R.6 có tọa độ, lập coverage map cho κ/h/tải cực trị của
   frame định sinh. Tám IDs audit cũ trong contract_spec là điểm bắt đầu;
   nếu chưa phủ góc, khai thêm calibration bằng design trước computation.
2. Preregister candidate global K/ref, cùng h và hai coarse-axis neighbors,
   route S1, quadrature/support/tail policy, arithmetic certificates, stopping
   budget và runtime ceiling. Chỉ discovery/calibration, không CF/R09/R10.
3. Replay anchors X2065/X1008/X1009 ở code/levels cũ để kiểm đúng provenance;
   so candidate mới theo R1–R8, không bắt K* tái lập số K40 tuyệt đối.
4. Audit candidate route/S1/D22 nếu dùng; tách stationary TV, moments/tails,
   quadrature và floating error. Sparse differences hoặc K320 ở hai điểm
   không tự là global bound. Giữ FAIL/UNRESOLVED và các run sau quan sát riêng.
5. Chọn global levels/method bằng luật đã khóa; báo coverage, accuracy/runtime
   tradeoff và lý do giữ audit HOLD hay đóng có giới hạn. Nếu không đạt thì
   chưa lấy mẫu CF; muốn đổi rule/corner scope phải DL/version trước run mới.
6. Tạo contract **v1.3.1 + DL + tag mới** khi đóng phần DEFERRED. Không sửa tag
   v1.3 hoặc điền các null như thể đã có trước đây. L3R.7 mới thiết kế ngân sách,
   frame, power, seeds, collision audit; Phase4 còn D22/human/Gate3R.

Không dựa vào outcome CF để chọn K/dt, route S1, frame corners hoặc truncation.
R3 đã khóa hai bước escalation hữu hạn dùng chung; R6 không mở một budget mới
cho từng threshold. Refinement smallness không loại bỏ mọi numerical degrees
of freedom: báo residual risk và giữ near-threshold unresolved.
