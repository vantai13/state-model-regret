# L4.3 — Đối chiếu hướng dẫn và giới hạn của audit

Người phụ trách: **Doan Van Tai** · 30/10/2026. AI theo ủy quyền.
Tài liệu này ghi các giới hạn khi triển khai; không thay prereg đã khóa tại
`ae174d0`, contract, card hoặc nhãn Gate4.

1. **Dung sai không chứng minh engine nào đúng.** Pilot/native lệch quá0.25pp
   kích hoạt HOLD để điều tra. Nó không tự chứng minh bug, cũng không làm native
   thành chuẩn đúng tuyệt đối. Sai số hội tụ hoặc chuyển đổi age có thể góp phần.
2. **18 cặp không cho global error bound.** Chênh≤0.200989pp trên18age pairs là
   quan sát tại các điểm đó, không đủ để nói mọi contrast pilot đáng tin ở mức0.2pp.
   Cancellation của common cost là lời giải thích có thể kiểm, không certificate.
3. **R1 trong skeleton chưa đủ.** Skeleton chỉ lấy chênh ratio trên5contrast.
   Contract `compare_levels` còn kiểm Cref, sáu contrast, raw cost-scale, ratio
   và sign flips. Runner dùng hàm frozen gốc; d cho R6 còn gồm arithmetic width.
4. **Raw và lean validity khác nhau.** Cardv2 adapter dùng lean arithmetic width
   và consistency theo tolerance. Lesson còn yêu cầu raw arithmetic_pass=True và
   validity_errors rỗng. Audit giữ cả hai như prereg, báo riêng khi chúng bất đồng;
   rawflag không phải chứng minh mô hình vật lý sai.
5. **Guard CF dùng exact physical key.** Tuổi được quy về1 bằng Fraction, không
   làm tròn; kiểm full6coordinates, gồm c_sw. Inventory loại tuple đã thấy khi
   rút CF, không bảo đảm khoảng cách dương lớn hoặc độc lập thống kê ở lân cận.
   Khóa CF chỉ được đọc để từ chối, không gọi engine trên CF kể cả timing.
6. **Alias khác regime distinct.** Phạm vi tác giả đã chọn có684aliases nhưng
   666tọa độ; mỗi tọa độ native tính một bundle, so với mọi alias pilot. Báo cả
   số dòng và số tọa độ; không chọn alias có độ dịch thuận lợi.
7. **95% cùng dấu chỉ là diagnostic trên discovery.** Không suy phân phối độ dịch
   trên mọi regime, đặc biệt từ8probes thiếu raw hoặc mẫu lấy thích nghi. Partial
   audit không được dùng để chấm dự đoán toàn vùng hoặc ước p theo card measure.
8. **Bắc cầu cần cùng đối tượng.** Triangle inequality chỉ bảo vệ cùng tọa độ,
   estimand và law với allowance được ghi; các điểm anchor khác nhau hoặc dt khác
   không tự cho một cận MC/native ở vùng chưa kiểm. κ=.05 ngoài coverage118ca cũ
   chưa tự chứng minh một code path mới; cardSUB vẫn chưa được tác giả chọn.
9. **Thiếu artifact phải để thiếu.** Không có fullPHASE_4 boundsA428,6IDsK2 gốc
   hoặc8rowsK6. Tác giả chọnA466/AB218;14replays có6map1 bổ sung, không giả là K2
   gốc. Không dựng native_probe_summary.csv từ các con số tóm tắt.
10. **Tác giả ủy quyền soạn dự đoán.** Ba forecast trong prereg doAI viết thay theo
    yêu cầu, không phải bài tác giả tự lập độc lập, không nâng Understanding.
    Nới resource cap (nếu cần trong phiên sau) phải có version/deviation trước run;
    không biến resource failure thành numerical negative result.

E11 raw đã đo: trong54nhóm cùngλA/λB/κ/η/h,216so sánh vớiage1, L11 lệch tối đa
**0.7109021917%** vàL10 **0.7105559643%**, cùngcặpXA027/XM1048. File
`results/lessons/l4_3/static_diagnostics.json` ghi rõ định nghĩa mức tương đối.
Đây là diagnostic S04 trên pilot, không trích mứcLbar làm research result.
