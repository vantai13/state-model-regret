# GZL22 — Ghabashneh et al.: burst, tranh chấp buffer và loss trong DC (Meta)

Người phụ trách: **Doan Van Tai** · 04/11/2026. Note do AI (Claude) soạn.
Tác giả tự tải (`Downloads/tmp/imc2022.pdf`, 06:38 ngày 04/11) sau danh sách L7.3-R2. Mức đọc: AI-T.
Tác giả tự đọc: chưa có xác nhận.

Ghabashneh, Zhao, Lumezanu, Spring, Sundaresan, Rao. *A Microscopic View of Bursts, Buffer Contention, and Loss in
Data Centers*. IMC 2022, tr. 567–580. [DOI 10.1145/3517745.3561430](https://doi.org/10.1145/3517745.3561430).

**Phiên bản.** Bản camera-ready (acmart), trang 1 có DOI và dòng "Copyright held by the owner/author(s)". File tạo
18/01/2023, 14 trang. Chưa đối chiếu chữ với ACM DL. Lưu tại
`~/papers/state-model-regret/l73/GZL22/GZL22_microscopic_bursts_IMC22.pdf`, sha256 `b541bce41ace…`.
Đọc targeted: §1/PDF1, §2.3/PDF3, §4.2/PDF4, §5/PDF6–7, §6/PDF7–8 (Fig. 6–7), tóm tắt §7/PDF10, §8/PDF11, §9/PDF12.
Không đọc §7.1–7.3 chi tiết, §8.1–8.2.

**Câu hỏi.** Ở DC hiện đại, burst dài bao lâu, cách nhau bao lâu và tải trong/ngoài burst là bao nhiêu? Thang này có
cùng định nghĩa với T_mode không?

**Quan sát (trích vị trí)**
- **Đo (§4.2/PDF4, §5/PDF6).**
  - Millisampler trên host (eBPF), sampling 10 ms, 1 ms hoặc 100 µs, mỗi run 2000 bucket.
  - Bài dùng 1 ms trong khoảng 2 s; SyncMillisampler chạy mỗi giờ.
  - Buffer của switch giữ được khoảng 1 ms packet mỗi queue.
  - Ở 100 µs, segmentation offload có thể làm burst trông lớn hơn thật.
- **Định nghĩa burst (§5/PDF7).** Chuỗi liên tiếp các mẫu 1 ms vượt 50% line rate, theo [46] = ZLK17. 34% số
  server run có ingress bursty.
- **Burst (§6/PDF7, Fig. 6–7).**
  - Trung vị 7,5 burst/s mỗi run, p90 39,8.
  - Thời lượng trung vị 2 ms, p90 8 ms. 88% burst không tranh chấp ngắn hơn 3 ms.
  - Volume trung vị 1,8 MB, p90 9 MB.
- **Tải (§6/PDF7).**
  - Utilization trung bình của run: trung vị 6,4%, p95 dưới 45%.
  - Ngoài burst: trung vị 5,5%. Trong burst: trung vị 65,5%.
- **Tranh chấp và loss (§7 takeaways/PDF10, §8/PDF11).**
  - Tranh chấp biến động mạnh ở thang ngắn: run trung vị mất 33,3% phần buffer, 15% số run mất hơn 70%.
  - Chu kỳ ngày có, nhưng "not as dominant".
  - Loss nhiều nhất ở burst tranh chấp dài 6–10 ms với 50–60 kết nối (4–6% số burst đó có loss).
- **Counter của switch (§7/PDF9).** Switch production ở Meta chỉ cho thống kê volume ở độ phân giải 1 phút.

**Suy luận của AI (chưa kiểm bởi tác giả)**
- **Thang burst phụ thuộc độ phân giải đo.**
  - ZLK17 (counter 25 µs): p90 dưới 200 µs.
  - GZL22 (mẫu 1 ms): trung vị 2 ms, p90 8 ms.

  Cả hai dùng ngưỡng 50% nhưng không cùng thang. Vì vậy T_mode của "microburst" không có một giá trị duy nhất.
- **ON/OFF rất bất đối xứng.** T_on ≈ 2 ms, còn T_off ≈ 1/(7,5/s) ≈ 133 ms (AI-tính, coi burst đều). Với chuỗi
  Markov hai trạng thái, thời gian tương quan của mode là 1/(1/T_on + 1/T_off) ≈ 1,97 ms. Đây là đồng nhất thức toán,
  áp dụng nếu ON/OFF xấp xỉ exponential; bài không kiểm điều đó. ctmc-v1 giả định hai mode đối xứng, nên đây là một
  điểm lệch.
- **Tải theo mode.** Tải trong burst 65,5% và ngoài burst 5,5% nghĩa là cả hai mode đều ổn định trên link host, nên
  stake backlog ở link host nhỏ. Stake thật nằm ở buffer chung của rack khi nhiều burst trùng nhau, mà ctmc-v1 không mô
  hình.
- Dữ liệu một ngày, một operator (Meta), một số region. Không tổng quát cho mọi DC.

PC liên quan: realism / RQ3. Không đổi nhãn PC, không có claim novelty.
