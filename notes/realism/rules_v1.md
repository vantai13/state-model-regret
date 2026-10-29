# L3R.4 — Luật phân loại v1, trước bảng216

Người phụ trách: **Doan Van Tai** · 29/10/2026.
Machine specification: [envelope_v1.json](envelope_v1.json).

1. Bối cảnh a/b lấy từ DL-008; không thêm WAN. Chỉ tham số thiết kế và công thức
   liên tục trong A2. Không J, quyết định, regret, gap hoặc contrast mới.
2. τ_eff cần nguồn cùng observation schema. Nếu có dải hợp lệ, chỉ một τ trong
   dải được dùng đồng thời cho T=κτ, h=(h/τ)τ, delay, CV ở các cửa sổ vật lý cố định.
   Nếu chưa có dải τ: UNSOURCED, không tìm anchor tối ưu. Hai anchor minh họa
   a=10ms,b=100ms dùng dịch đơn vị, **không dùng làm chứng cứ hay chứng nhận IN**.
3. Các ràng buộc bắt buộc: τ_eff, h giữ quyết định, CV_rate ở bốn cửa sổ, T_mode,
   offered mean/peak load, observation schema, hình dạng variability.
   Mỗi ràng buộc cần định nghĩa/nguồn và dữ liệu so sánh được. Thiếu bất kỳ
   ràng buộc nào ⇒ UNSOURCED trước xét nhãn khác; ghi rõ cả phần known tension.
   Policy này cố ý không suy OUT từ envelope không đầy đủ.
4. Với envelope đầy đủ: IN nếu giao các miền τ hợp lệ khác rỗng; EDGE nếu không IN
   nhưng giao khác rỗng khi nới tối đa **k=1 đại lượng**, mỗi biên dương được nới
   **f=2**; OUT nếu còn lại. Không thay τ cho từng đại lượng. Kể cả EDGE, τ vẫn
   trong dải tuổi có nguồn, không nới tuổi. Báo thêm f=1.5 và3. Đây là dung sai
   sàng lọc kỹ thuật (1 ràng buộc, tối đa hệ số2), không ngưỡng fitted từ pilot.
   Ràng buộc định tính chỉ được nới nếu đã khai phép nới có nghĩa; không tự bỏ qua.
5. Buffer/actuation/mode-oracle là ba cờ riêng, không cộng thành điểm realism.
   Buffer: tính tail vô hạn P(Q/c>B_t) cho cả A/B trước và stationary proxy sau
   Switch nếu có B_t có nguồn. Tail>1% gắn risk; đây là ngưỡng engineering minh họa,
   không xác suất drop. Không B_t ⇒ UNSOURCED. Đồng thời lưu sensitivity B_t/T=1,5,10
   cho bốn queue, không coi budget giả định là buffer thực.
   Actuation: nếu có d_act tương thích, corr=exp(−2d_act/T); corr≤exp(−2) gắn risk.
   Không nguồn ⇒ UNSOURCED; không tự gán dấu thay đổi gain. Mode oracle luôn TRUE;
   lưu corr của mode cũ-hiện tại exp(−2/κ), không gọi là backlog correlation.
6. Delay là **virtual time-average E[Q]/c**, không packet/end-to-end delay.
   Hình dạng fluid/two-mode/a/c=.6/ideal backlog/infinite buffer/instant action
   luôn ghi scope. M0 vẫn frozen; không nâng scope sang repair triển khai được.
7. Dán nhãn đủ216 ID/210tọa độ trước, commit CSV/receipt. Sau checkpoint này mới
   overlay discovery đã lưu ở tag explore-v13-pilot, không tính outcome mới.
   Harm GS/Cref≤−1%; MV GM/Cref≥1% là diagnostic cutoffs cũ, không hypothesis CF mới.
   Báo riêng hai vùng, cả overlap; không giả định tách rời. Đếm cả ID và tọa độ
   (λA,λB,κ,u,h,c_sw,ref,K), không diễn giải tỷ lệ là tần suất ngoài đời.
8. Quyết định riêng MV/SH: có IN→(a); chỉ EDGE→(b); OUT ở mọi context→(c);
   phần lớn UNSOURCED→(d) HOLD realism. Nhãn khác nhau trong vùng phải báo phân bố.
   Nguồn bổ sung sau labels phải tăng phiên bản, ghi sau quan sát, không sửa v1.

Stationary-only cross-check khai trước: X2041,X2012,X1009 (coverage λB/κ của
audit discovery), A_pre/B_pre, ref1/2; so atom, meanQ/c và tail tại delay=5T với
fluid reference. Đây là diagnostic approximation; mean spectral chưa có cận moment
chứng nhận, không dùng TV certificate như cận kỳ vọng unbounded. Không cờ PASS
toàn engine hay reopen gateL3R.3 từ phép kiểm này.

Tác giả chưa tự read-back lesson; người soạn theo ủy quyền không thay xác nhận đó.
L3R.5 chỉ nhận proposal scope; chưa adopt contract/numerics hoặc chọn CF frame.
