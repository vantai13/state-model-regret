# DL-104 — Baseline margin + Stay và luật đọc trước outcomes

Người phụ trách: **Doan Van Tai** · 30/10/2026.
Provenance: **AI soạn, tác giả duyệt trực tiếp**.
Trạng thái: **ADOPTED_BY_AUTHOR_CHOICE**, trước plant baseline outcomes.

Lựa chọn nguyên văn: **“Chọn gói đặc tả đã soạn (khuyến nghị)”**, dựa trên
proposal commit `daa0f92`; xem [author choices](../../experiments/P4_04_baseline/author_choices.json).
Không suy từ yêu cầu triển khai chung hoặc chữ ký giả lập.

- Giữ Bθ và Stay. θ=ρ·E[JStay], không dùng Cref để điều khiển hoặc cộng θ vào cost.
- ρ∈{0,.005,.01,.02,.05}; chọn riêng MV/SH trên đủ18/72 tọa độ discovery,
  mỗi tọa độ age1 một phiếu, không lọc lớp. MV tối ưu ô00, SH tối ưu ô10 theo
  trung bình regret/Cref; exact tie chọn ρ nhỏ hơn.
- MV: median recovery≥.5 thì câu claim nêu margin lấy lại phần lớn lợi ích
  so với controller mean-field không margin. SH: median|GSθ|/Cref<.005 và
  medianΔL10<0 mới thu hẹp thành tác hại với controller không margin.
- Điều kiện đối thủ loại trường hợp GSθ nhỏ chỉ vì controller bị làm tệ đi.
  Baseline không đổi card v2 verdict, không cấp card mới.
- Discovery chỉ chọn ρ*/xem trước; luật câu claim áp lại trên mô tả CF ở Phase5.
  Không dùng mẫu discovery thích nghi làm tần suất hoặc suy luận p-value.
- Vùng A/AB ngoài hai hộp trên DEFERRED bởi L4.3/L4.5; numerical readiness kiểm
  riêng từng điểm MV/SH. HOLD L4.3 giữ nguyên, không CF/R09/R10 outcomes mới.

Tác giả yêu cầu AI viết dự đoán thay bằng mệnh lệnh riêng, đã lưu nguyên văn.
Forecast ở spec§7 là **AI theo ủy quyền**, không tác giả tự viết độc lập và không
nâng Understanding/ownership. [Đặc tả](../../experiments/P4_04_baseline/spec.md).

ρ* chưa biết lúc DL này được viết. Chỉ được chọn/đóng băng theo luật sau full
discovery PASS; nếu partial/HOLD thì giữ NOT_SELECTED, không tune trên subset.
Descriptor cho L4.8 đã có interface, integration phải ghi đúng trạng thái thực tế.
