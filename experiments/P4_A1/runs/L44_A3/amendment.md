# A3/B1 — protocol tối thiểu, trước mọi evaluation A3

Người phụ trách: **Doan Van Tai**. Source do AI (Claude) cung cấp; AI triển khai
và soạn forecast theo ủy quyền tiếp diễn. Yêu cầu hiện tại của tác giả ưu tiên
rút gọn process; không tự nhận author self-writing/Understanding.

1. Giữ 90 keys của L44_A1 (18 MV, 72 SH), levels (640,4)/(320,4)/(640,2),
   rho {0,1/200,1/100,1/50,1/20}; dùng nguyên engine/runner/checks/helpers DL104.
2. Giữ mọi điểm NOT_READY, cap=1. BUG/execution/replay mismatch/CPU cap vẫn dừng.
   Resources như A1: 2 workers, 1 BLAS thread/worker, 8 CPU giờ toàn run.
3. Freeze trước control/benchmark. Replay cố định bốn benchmark keys ×3 levels
   (=12 rows) với A1 trước full. Không replay toàn57, không diagnostic phụ.
4. Chạy đủ 90×3; mỗi key một phiếu. MV target00, SH target10; argmin mean
   normalized regret chính xác bằng Fraction, tie chọn rho nhỏ hơn.
5. Riêng từng support: STABLE iff cả3 cùng rho* và narrow/not-narrow DL104.
   MV median R_M>=1/2; SH median abs(GS_theta)/Cref<1/200 và median deltaL10<0.
   Các trường mẫu số/claim_readiness giữ báo cáo DL104, không thêm verdict gate.
6. STABLE chỉ là robustness trong ba mức đã kiểm; có thể cùng bias, không phải
   certificate hoặc numerics/convergence từng point đã solved. Khác mức thì
   UNRESOLVED vì validity, rho_freeze=null; không dùng câu baseline claim đó.
7. Dừng numerical branch sau A3 dù verdict nào; không A4 hay mức thứ tư để cứu.
   Chuyển phần evidence còn sống sang L4.5 Part B; SV/SUB không tự đổi scope.

Chỉ giữ files choices/amendment/prereg và budget commit vì runner A1 yêu cầu
sẵn, không thêm runner/lesson/forking checklist/history-lock framework. Source
A1/A2 và artifacts cũ giữ nguyên. Không CF/sealed outcomes/card change.
