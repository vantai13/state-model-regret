# PMO22 — Jupiter Evolving: TE và topology engineering trong DC của Google

Người phụ trách: **Doan Van Tai** · 04/11/2026. Note do AI (Claude) soạn.
Tác giả tự tải (thư mục Downloads, 07:06–07:08 ngày 04/11) sau danh sách L7.3-R2 đợt 3. Mức đọc: AI-T.
Tác giả tự đọc: chưa có xác nhận.

Poutievski et al. *Jupiter Evolving: Transforming Google's Datacenter Network via Optical Circuit Switches and
Software-Defined Networking*. SIGCOMM 2022, tr. 66–85.
[DOI 10.1145/3544216.3544265](https://doi.org/10.1145/3544216.3544265).

**Phiên bản.** 20 trang (gồm appendix), "Copyright held by the owner/author(s)" (camera-ready open access). Lưu tại
`~/papers/state-model-regret/l73/PMO22/PMO22_JupiterEvolving_SIGCOMM22.pdf`, sha256 `304ecc5c09f9…`.
Đọc targeted: §2/PDF3, §4/PDF5, §4.4/PDF6–7, đoạn "Traffic and Topology Engineering Cadence" (PDF8), §6.1/PDF9, §6.3/PDF10.
Không đọc §3, §5, appendix.

**Câu hỏi.** TE trong DC hiện đại chạy ở thang nào? Dùng thông tin cũ bao lâu? Traffic dự đoán được tới đâu?

**Quan sát (trích vị trí)**
- **Mức dự đoán được (§2/PDF3).** Fabric multi-tenant có "relatively predictable traffic patterns with uncertainty that
  is far from worst-case permutation".
- **Đo và dự đoán (§4.4/PDF7).**
  - Ma trận traffic cấp block gom mỗi 30 s.
  - Ma trận dự đoán là **đỉnh** sending rate của từng cặp trong **1 giờ** qua. Nó được cập nhật khi thấy thay đổi lớn và
    theo chu kỳ; mô phỏng cho thấy làm mới hằng giờ là đủ.
  - Mục tiêu là MLU.
  - Trace 30 s "shows high variability over time": đỉnh quá khứ thường không dự đoán được đỉnh tương lai, và trace không
    bắt được burst ngắn hơn 30 s. Vì vậy dùng "variable hedging" (chia traffic qua cả path trực tiếp và path transit).
  - Mức hedging tối ưu của mỗi fabric ổn định, nên cấu hình gần như tĩnh.
- **Nhịp (PDF8).**
  - TE là vòng trong, phản ứng ở thang "O(seconds) to O(minutes)" tùy mức khẩn; lời giải phải xong trong vài chục giây.
  - Topology engineering là vòng ngoài, mất O(giờ). Đổi topology thường hơn vài tuần một lần cho lợi ích hạn chế.
  - "much of the uncertainity arises from short-term variations in traffic that's stable on longer horizons".
- **Traffic (§6.1/PDF9).** Traffic giữa các block theo mô hình gravity; tải khác nhau nhiều giữa các block. Đánh giá dùng
  đỉnh một tuần để bắt chu kỳ ngày/tuần (§6.2/PDF9).

**Suy luận của AI (chưa kiểm bởi tác giả)**
- Thiết kế TE thực tế ở thang giây–phút **không** dùng state tươi làm ước lượng điểm. Nó dùng đỉnh 1 giờ cộng hedging,
  tức một planner robust dựa trên thống kê dài hạn. Điều này nhất quán với vùng tiệm cận của ctmc-v1 (planner dừng đủ
  dùng), nhưng **không phải validation**:
  - mục tiêu là MLU, không phải backlog;
  - hedging là robust optimization, không phải trung bình dừng;
  - không có so sánh với một phương án dùng state tươi.
- Câu về "short-term variations ... stable on longer horizons" là mô tả định tính của tác giả bài, không có số f.

PC liên quan: realism / RQ3. Không đổi nhãn PC, không có claim novelty.
