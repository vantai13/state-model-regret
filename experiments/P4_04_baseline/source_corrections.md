# L4.4 — Những điểm phải phân biệt khi triển khai

Người phụ trách: **Doan Van Tai** · AI theo ủy quyền · 30/10/2026.

1. Source thực là `experiments/R3R_08_population_numerics/population.py`;
   lean engine gọi module này. Không có population.py trong R3R_11.
2. Final Review §11.4 hiện chỉ được hai input thuật lại; reading note trong repo
   nói thiếu full snapshot. Chưa tự xác minh toàn văn §11.4; không gán kiểm nguồn
   của người viết lesson thành thao tác đã làm trong phiên này.
3. Synthetic200/law/toy results trong input là source-reported cho tới khi chạy
   độc lập; không gọi đó là kết quả mới của repo.
4. θ từ moment Stay có arithmetic uncertainty. Skeleton coi θ là scalar exact;
   phiên bản triển khai phải truyền θ_error và bao roundoff của h+θ khi θ>0.
   Ở θ0 giữ byte kết quả gốc, không cộng lỗi mới khiến bit sanity sai.
5. R1 của card v2 dùng lean level_ready, khác yêu cầu rawTrue/errors=[] đã
   đăng ký riêng cho L4.3. L4.4 phải khai rõ adapter trước khi chạy và báo raw
   flags, không gọi raw flag PASS nếu thực tế False.
6. Ω_MV⁺ có18 điểm sau age normalization, không chỉ16 pilot stage points;
   Ω_SH⁺ có72. Tuning dùng cả vùng, không lọc chỉ16/16MV hoặc57/72SH thuận lợi.
7. Hộp MV có11C/7B ở map nên HOLD theo lớp A của L4.3 không tự áp hay tự được
   gỡ cho MV; readiness phải kiểm tại từng điểm và cho baseline mới.
