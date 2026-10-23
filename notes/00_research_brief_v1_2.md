# Research brief v1.2

Người phụ trách: **Doan Van Tai** · 23/10/2026. Bản tóm tắt đi cùng tag `contract-v1.2`.

> **Provenance.** Do AI soạn theo yêu cầu thực hiện của tác giả. PHASE_1 yêu cầu brief do tác giả tự viết (hai trang, gồm chuỗi HC1/HP1); bản này là chỗ giữ chỗ cho tới khi tác giả viết lại.

For load-changing routing actions, how do improvements in current-state information and action-response model fidelity differ and interact in their effect on expected decision regret?

**Hệ và đo lường.** D1–D25 tại [contract v1.2](01_definitions_v1_2.md). Hai path tách, capacity 10 packet/s, recurrence phản xạ, nền A/B ON/OFF, cumulative occupancy (packet·s), oracle biết state và law nhưng không biết tương lai. S0 là posterior từ một snapshot backlog cũ; S1 thấy backlog và mode hiện tại. M0 là mean rollout theo từng state trong belief; M1 là expected cost đúng law. Đo sáu contrast D19 và regret D18.

**Lưới v1.2.** 38 ô chính, mỗi ô được neo để oracle chọn Switch khoảng 30% hoặc 70% số tình huống; 12 ô held-out neo cùng luật; 6 ô kiểm âm; 2 đầu dò cấu trúc. Horizon vật lý 8 s (nan hoa 2 s). So sánh ở cùng độ khó, không cùng tải ([claim boundary](01_claim_boundary_v1_2.md)).

**Ngưỡng.** εR 1% của Cref = L* theo ô (độ nhạy 0,5%/2%), εE 0,5%, dung sai làm mịn 0,25%, luật hòa Stay.

**Tiếp theo.** Phase 3 bắt đầu bằng A01 trên M01, M09, M22 (chọn dt cuối, kiểm ô kiểm âm cho contrast bằng 0). A04 trên 38 ô chính; A05 khóa $H_0/H_1$ trước khi chạm held-out. Phase 2a (P11–P13) đọc song song, xong trước A05. Phase 4 HOLD tới khi có người đọc độc lập (P0-V10). G1 giữ nguyên.
