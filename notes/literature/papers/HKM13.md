# HKM13 — SWAN: software-driven inter-DC WAN

Người phụ trách: **Doan Van Tai** · 03/11/2026. Note do AI (Claude) soạn.
Nguồn được duyệt theo ủy quyền L7.3-R1 ("bạn hãy tự làm tự chạy thực hiện cho tôi luôn đi"), tức AI-delegated,
không phải tác giả tự sàng. Mức đọc: AI-T. Tác giả tự đọc: chưa có xác nhận.

Hong, Kandula, Mahajan, Zhang, Gill, Nanduri, Wattenhofer. SIGCOMM 2013, tr. 15–26.
[DOI 10.1145/2486001.2486012](https://doi.org/10.1145/2486001.2486012); bản CCR là 10.1145/2534169.2486012.
PDF lấy từ [trang hội nghị](https://conferences.sigcomm.org/sigcomm/2013/papers/sigcomm/p15.pdf): 12 trang, khớp
tr. 15–26. Lưu local tại `~/papers/state-model-regret/l73/HKM13/HKM13_SWAN_sigcomm13_p15.pdf`, sha256 `99bb9406a528…`.
**Bản ACM (VoR), 04/11/2026:** tác giả tự tải, lưu tại `~/papers/state-model-regret/l73/HKM13/HKM13_SWAN_SIGCOMM13_ACM_VoR.pdf`,
sha256 `104dfbe99511…`, 12 trang. pdftotext của từng trang **trùng hoàn toàn** với bản trang hội nghị (so từng trang,
tỷ lệ giống 1,0), nên mọi trích §/trang bên dưới giữ nguyên.
Đọc targeted: §1–2/PDF1–2, §3/PDF4, §4–4.3/PDF5–7, §5.1/PDF8, §6.1/PDF9, §6.4/PDF10, §6.6/PDF11, cộng Fig. 17–18.
Không đọc kỹ §4.3.1 (LP cập nhật không congestion), §7–8.

**Câu hỏi.** Chu kỳ quyết định h, tuổi thông tin τ, trễ actuation và tải của TE trên WAN là bao nhiêu?

**Quan sát (trích vị trí)**
- **Tải.** Utilization trung bình của cả những link bận hơn là 40–60% (§1/PDF1). Trên IDN, một nửa số link dưới 30% và
  ba phần tư số link dưới 50% (§2/PDF2).
- **Chu kỳ.** Service broker gom demand và cập nhật controller mỗi T_s = 5 phút. Network agent báo traffic mỗi
  T_a = 5 phút. Shim trên host ước demand cho T_h = 10 s tới (§3/PDF4). Controller tính allocation, báo cho service rồi
  đổi forwarding state mỗi T_c = 5 phút (§4/PDF5).
- **Ước demand.** Demand của interactive service lấy từ usage trung bình 5 phút gần nhất, rồi nâng lên theo sai số
  ước lượng quá khứ (§4.2/PDF6).
- **Trình tự cập nhật.** Controller chờ T_h = 10 s để service đổi rate rồi mới đổi tunnel (§4.3/PDF7). Hầu hết lần
  cập nhật xong trong 22 s, phần lớn là chờ rate limit (2 × 10 s). Data plane chỉ "in flux" trung bình 600 ms
  (§6.6/PDF11, Fig. 17).
- **Testbed.** Đặt T_s = T_c = 1 phút thay vì 5 phút để stress-test (§5.1/PDF8).
- **Mô phỏng.** Demand = max của các trung bình 5 phút trong 15 phút qua; log là sFlow. Baseline MPLS (CSPF,
  auto-bandwidth) chạy định kỳ 5 phút (§6.1/PDF9). Mỗi switch áp update tuần tự, 2 ms mỗi update (giả định dẫn
  từ [8]). Route update gây gián đoạn trung bình mỗi 7 phút trên IDN; cập nhật cần 1–3 bước (§6.4/PDF10).
- **Tần suất và dự báo.** Demand đổi mỗi 5 phút; cập nhật data plane 1 lần/10 phút làm mất 5% throughput, 1 lần/100
  phút mất 30% (§6.6/PDF11, Fig. 18b). Chỉ 1% thời gian traffic interactive thực tế trên một link lệch dự báo quá 1%
  (§6.6/PDF11).

**Suy luận của AI (chưa kiểm bởi tác giả)**
- h ≈ T_c = 5 phút là thời gian giữ một allocation. Cấu hình còn bị đổi giữa chừng do failure (§4.4, không đọc kỹ).
- τ_eff ≈ P/2 + L + W/2 theo T00, với P = T_s = 5 phút, W = 5 phút, L ≈ 22 s, nên khoảng 5 phút. Đây là phép tính của AI,
  không phải số trong bài.
- **Thang mode của demand WAN dưới 5 phút không xác định được từ bài.** Log 5 phút không phân giải được thang nhanh hơn,
  và việc "đổi mỗi 5 phút" trong thí nghiệm là thiết kế thí nghiệm, không phải phép đo.
- **Khác contract.** Background traffic là elastic và bị SWAN điều khiển rate, nên tải không ngoại sinh. Mục tiêu là
  throughput và fairness dưới capacity, không phải backlog cost. Ánh xạ sang ctmc-v1 vì thế chỉ ở mức minh họa.
- Không suy từ bài này rằng mọi WAN TE có chu kỳ 5 phút; đây chỉ là một hệ của một operator, năm 2013.

PC liên quan: realism / RQ3 (định vị use case). Không đổi nhãn PC, không có claim novelty.
