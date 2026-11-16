# CMN12 — Chiaraviglio, Mellia, Neri, ToN 2012

Người phụ trách: **Doan Van Tai** · 16/11/2026 · tác giả tải PDF và yêu cầu "đọc xem bài nào hợp lí nhất thì trích"; **AI-T (Claude)**, tác giả tự đọc: chưa xác nhận.

L. Chiaraviglio, M. Mellia, F. Neri, "Minimizing ISP Network Energy Cost: Formulation and Solutions", *IEEE/ACM Trans. Netw.* 20(2):463–476, Apr. 2012, [DOI 10.1109/TNET.2011.2161487](https://doi.org/10.1109/TNET.2011.2161487). Bản đọc: PDF IEEE Xplore do tác giả tải (license VNU-HCM), lưu ngoài Git `~/papers/state-model-regret/letter_story/Chiaraviglio_ToN2012.pdf`, sha256 `10735cd5…3383`.

**Câu hỏi:** có nguồn cho thấy quyết định cấu hình mạng được tính bằng mô hình fluid và giữ lâu (hàng giờ) không? Mục đích: câu chuyện thực tiễn cho letter (rủi ro "practical relevance"), không đổi PC.

**Đã đọc (targeted):** abstract (PDF tr.1); §II công thức (PDF tr.2); §V-B real case study (PDF tr.10–11); §VI discussion (PDF tr.12).
- **§II, PDF tr.2 (printed 464):** routing dùng "a fluid model" (ràng buộc bảo toàn luồng, Eq. 2); tải link phải nhỏ hơn một độ sử dụng mục tiêu tối đa (Eq. 4). Mục tiêu là tắt node/link, giữ kết nối và ràng buộc độ sử dụng.
- **§V-B, PDF tr.10:** dùng profile tải thật trong ngày (Fig. 12). Thấp nhất 0,38 lần giờ cao điểm vào ban đêm. Ban đêm topology co về cây Steiner (tiết kiệm tối đa, 36% với OPT-V3).
- **§VI, PDF tr.12 (printed 474):** "We foresee a deployment scenario in which the network configuration changes slowly, e.g., every 30 min"; "having few reconfigurations per day mitigates the eventual extra energy cost and additional latencies…".

**Dùng trong letter:** quyết định tiết kiệm năng lượng dồn tải lên ít tài nguyên hơn, tính bằng mô hình fluid với ngưỡng độ sử dụng, và cấu hình đổi chậm, ít lần trong ngày.
**Không được nói:** bài này không đo hàng đợi ngẫu nhiên; không nói nó "bỏ qua" chi phí hàng đợi (nó dùng ngưỡng độ sử dụng như biên an toàn); không nói cấu hình được giữ đúng N giờ.
