# BAAZ11 — MicroTE: fine-grained TE cho data center

Người phụ trách: **Doan Van Tai** · 04/11/2026. Note do AI (Claude) soạn.
Tác giả tự tải bản ACM sau danh sách L7.3-R2; AI coi đó là duyệt nguồn này. Mức đọc: AI-T.
Tác giả tự đọc: chưa có xác nhận.

Benson, Anand, Akella, Zhang. CoNEXT 2011, tr. 1–12.
[DOI 10.1145/2079296.2079304](https://doi.org/10.1145/2079296.2079304). Bản đọc là VoR từ ACM, 12 trang, lưu tại
`~/papers/state-model-regret/l73/BAAZ11/BAAZ11_MicroTE_CoNEXT11_VoR.pdf`, sha256 `c5bc8bdb75f7…`.
Đọc targeted: §3/PDF3–4, §4–4.1.2/PDF4–6 (Fig. 2), §5/PDF6, §5.1.3–5.1.4/PDF7, §7.3.2–7.3.3/PDF11 (Table 1).
Không đọc §5.3 (LP và bin-packing chi tiết), §6, §7.1–7.2.

**Câu hỏi.** Chu kỳ quyết định, tuổi đo và thang ổn định của traffic giữa các ToR là bao nhiêu? Câu "không dự đoán được
từ 150 s trở lên" mà RZB15 và T00 dẫn lại có nguồn gốc ở đâu?

**Quan sát (trích vị trí)**
- **Dữ liệu.** DC CLD (MapReduce) có 1.500 server và 75 ToR, sự kiện mạng ghi ở độ phân giải 1 s trong nhiều ngày.
  Ma trận traffic ToR-to-ToR được đưa vào mô phỏng theo từng giây (§3/PDF3). Có thêm DC UNV (web 3-tier) (§4.1/PDF5).
- **So sánh baseline.**
  - Routing tối ưu được tính với ma trận traffic biết đúng mỗi giây, mục tiêu là MLU.
  - ECMP kém tối ưu 15–20% khi tải nặng; Fat-Tree kém 23% (§3–4/PDF4).
  - Heuristic của Fat-Tree chạy mỗi giây, dùng utilization trung bình 10 s (§3/PDF4).
- **Câu 150 s (§4/PDF4).** "These studies show that data center traffic is bursty and that the traffic matrix lacks
  predictability at time scales of 150 seconds or longer". Câu này dẫn [13] Kandula et al. IMC'09 và [6] Benson et al.
  WREN'09. **MicroTE không tự đo con số này.**
- **Mức dự đoán được (§4.1.1/PDF5, Fig. 2a).** Một cặp ToR được coi là dự đoán được nếu traffic đổi không quá 20% trong
  1 s.
  - Khoảng 35% tổng traffic dự đoán được qua các khoảng thời gian.
  - CLD: trong 80% số khoảng 1 s, hơn 27% traffic còn ổn định ít nhất 1 s nữa.
  - UNV: trong hơn 65% số khoảng, 100% traffic ổn định trong 1 s tiếp theo.
- **Thời gian ổn định (§4.1.1/PDF5, Fig. 2b; top 100 cặp ToR).**
  - CLD: 60% số cặp ổn định trung bình 1,6–2,5 s.
  - UNV: khoảng 35% số cặp ổn định trung bình 1,5–5 s.
- **Vì sao có ổn định (§4.1.2/PDF5).** Ở CLD là bước reduce của MapReduce. Ở UNV là cấu trúc tầng của ứng dụng, và sự
  ổn định ở UNV ngắn.
- **Thiết kế (§5/PDF6).** Mỗi khoảng 1 s: route traffic dự đoán được một cách tối ưu, phần còn lại chia bằng weighted
  ECMP.
- **Đo (§5.1.3/PDF7).**
  - Mỗi server ghi ma trận traffic mỗi 0,1 s và gửi cho designated server mỗi 1 s.
  - Ngưỡng δ = 20%.
  - Bài viết rằng traffic giữa cặp ToR "predictable on a 2-second time scale", nên trung bình chạy phải ở thang
    dưới 2 s.
- **Gửi cập nhật (§5.1.4/PDF7).** Designated server chỉ gửi lên controller khi tập cặp dự đoán được đổi, hoặc khi
  volume đổi quá δ.
- **Phản ứng (§7.3.2–7.3.3/PDF11).**
  - Cài route trung bình dưới 40 ms với 10 flow/server; tệ nhất dưới 150 ms với 80 flow/server.
  - Giải LP mất 0,6 s với 100 ToR khi 50% số cặp dự đoán được; mất hơn 0,5 s với 200 ToR khi chỉ 5% số cặp dự đoán
    được (Table 1).

**Suy luận của AI (chưa kiểm bởi tác giả)**
- h = 1 s là chu kỳ quyết định chính bài nêu. Thời gian giữ một quyết định cũng là 1 s, vì route được tính lại mỗi
  khoảng.
- τ_eff ≈ P/2 + L + W/2, với P = 1 s, W = 0,1 s, L ≈ 0,04–0,15 s (chưa tính LP), nên khoảng 0,6–0,7 s. Đây là phép tính
  của AI theo công thức T00.
- Thời gian ổn định 1,5–5 s là ứng viên gần nhất cho T_mode của thành phần demand thang giây. Nó **không phải** thời
  gian lưu một mode exponential: định nghĩa là run-length dưới ngưỡng 20%, chỉ xét top 100 cặp.
- Câu 150 s vẫn là dẫn lại, chỉ lùi về được một bước (Kandula'09, Benson WREN'09 chưa đọc).

PC liên quan: realism / RQ3. Không đổi nhãn PC, không có claim novelty.
