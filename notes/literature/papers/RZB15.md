# RZB15 — Inside the Social Network's (Datacenter) Network

Người phụ trách: **Doan Van Tai** · 03/11/2026. Note do AI (Claude) soạn.
Nguồn được duyệt theo ủy quyền L7.3-R1 ("bạn hãy tự làm tự chạy thực hiện cho tôi luôn đi"), tức AI-delegated,
không phải tác giả tự sàng. Mức đọc: AI-T. Tác giả tự đọc: chưa có xác nhận.

Roy, Zeng, Bagga, Porter, Snoeren. SIGCOMM 2015, tr. 123–137.
[DOI 10.1145/2785956.2787472](https://doi.org/10.1145/2785956.2787472).
PDF lấy từ [trang tác giả](https://cseweb.ucsd.edu/~snoeren/papers/fb-sigcomm15.pdf): 15 trang, khớp tr. 123–137.
Lưu local tại `~/papers/state-model-regret/l73/RZB15/RZB15_fb_sigcomm15.pdf`, sha256 `d95df8228cb8…`.
Đọc targeted: §1/PDF2, §2/PDF3, §3.3/PDF4, §4.1–4.2/PDF5–6, §5.2–5.4/PDF9–11, §6.2/PDF12, Fig. 10–11, 13, 15.
Không đọc kỹ §4.3 (traffic matrix), §5.1 (flow size), §6.1, §6.3–6.4.

**Câu hỏi.** Traffic DC có nhiều thang thời gian không? Ở thang nào nó ổn định hoặc dự đoán được?

**Quan sát (trích vị trí)**
- **Tóm tắt phát hiện (§1/PDF2).**
  - Locality ổn định từ thang giây tới thang ngày.
  - Demand ổn định ngay cả trong khoảng dưới một giây.
  - Heavy hitter không lớn hơn flow trung vị nhiều; tập heavy hitter đổi nhanh, và heavy hitter tức thời thường không
    còn heavy ở khoảng dài hơn.
- **Dẫn lại Benson et al. [14] (§2/PDF3, dẫn lại).** Traffic không dự đoán được ở thang từ 150 s trở lên, nhưng tương
  đối ổn định ở thang vài giây.
- **Dữ liệu (§3.3/PDF4).** Fbflow gom theo phút; trace port mirroring chỉ dài vài phút.
- **Utilization (§4.1/PDF5).**
  - Utilization link host–RSW trung bình 1 phút dưới 1%. 99% link thường dưới 10% ở thang 1 phút.
  - Tải khác nhiều giữa các cluster: cluster nặng nhất (Hadoop) có utilization trung bình khoảng 5× cluster nhẹ
    (Frontend).
  - Demand theo chu kỳ ngày và ngày trong tuần.
- **Định nghĩa ổn định (§4.2/PDF5).** "Stable" nghĩa là gần hằng trong một khoảng và đổi chậm giữa các khoảng.
  Định nghĩa phụ thuộc độ dài khoảng.
- **Load balancing ở thang giây (§5.2/PDF9–10, Fig. 8b).**
  - Web và cache: rate theo rack đích ổn định qua các giây và tới 10 s (không có hình).
  - Mọi flow nằm trong hệ số 2 so với trung vị ở khoảng 90% số khoảng 1 s.
  - Flow trung vị có "significant change" (ngưỡng 20% của Benson) ở 45% số khoảng 1 s.
  - Hadoop không được load balance: 90% flow ở giữa lệch kích thước trung vị của chúng trong trace hơn sáu bậc độ lớn
    (cùng đoạn so sánh theo giây).
- **Heavy hitter (§5.3/PDF10–11, Table 4, Fig. 10–11).**
  - Heavy hitter là tập tối thiểu chiếm 50% traffic, xét trong cửa sổ 1, 10 và 100 ms.
  - Ở mức 5-tuple, khả năng dự đoán kém, dưới 10–15%.
  - Ở mức rack, heavy hitter còn heavy trong đa số khoảng 100 ms (trung vị).
  - Với khoảng 50% khả năng một heavy hitter còn ở khoảng sau, dự đoán bằng quan sát "không hiệu quả hơn đoán ngẫu
    nhiên bao nhiêu".
- **Hệ quả cho TE (§5.4/PDF11).** TE hiệu quả nếu 35% traffic dự đoán được (theo [14]). Chỉ heavy hitter mức rack đạt
  mức đó.
- **Arrival (§6.2/PDF12, Fig. 13).** Traffic Hadoop không có dạng on/off ở bin 15 ms hay 100 ms. Inter-arrival trung vị
  của flow khoảng 2 ms.
- **Thang ngày (Fig. 15/PDF13).** Có chuỗi trung bình 10 phút của utilization và trung bình 15 phút của drop trên
  khoảng 80.000 s.

**Suy luận của AI (chưa kiểm bởi tác giả)**
- Traffic có nhiều thang:
  - thang ms: heavy hitter đổi gần như ngẫu nhiên;
  - thang giây: Frontend ổn định ở mức tổng theo rack;
  - thang ≥ 150 s và thang ngày/tuần: có biến đổi (dẫn lại [14]; chu kỳ ngày ở §4.1/PDF5; Fig. 15).
- Bài không cho tỷ lệ phương sai f của từng thang theo nghĩa cần cho T_int, nên f vẫn là UNSOURCED.
- Utilization 1 phút rất thấp cho thấy stake của backlog cost ở mức link biên nhỏ. Tải trung bình 1 phút không phải ρ
  của một mode trong MMPP.
- Đây là một operator, năm 2015, và kết quả phụ thuộc service (Hadoop khác Frontend). Không tổng quát cho mọi DC.

PC liên quan: realism / RQ3. Không đổi nhãn PC, không có claim novelty.
