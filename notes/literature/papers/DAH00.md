# DAH00 — Dahlin: diễn giải thông tin load cũ theo tuổi của nó

Người phụ trách: **Doan Van Tai** · 04/11/2026. Note do AI (Claude) soạn.
Tác giả tự tải (`Downloads/tmp/dahlin2000.pdf`, 16:33 ngày 04/11) sau đề xuất L7.4-N1. Tác giả tải là duyệt nguồn này.
Mức đọc: AI-T. Tác giả tự đọc: chưa có xác nhận.

Michael Dahlin. *Interpreting Stale Load Information*. IEEE TPDS 11(10):1033–1047, tháng 10/2000.
[DOI 10.1109/71.888643](https://doi.org/10.1109/71.888643) (Crossref). Bản ICDCS 1999 (10.1109/icdcs.1999.776530) là
cùng công trình, không đọc.

**Phiên bản.** VoR của IEEE, 15 trang (pdfinfo: Creator "IEEE Copyright", 11/12/2000). Lưu tại
`~/papers/state-model-regret/l74/DAH00/DAH00_InterpretingStaleLoad_TPDS2000.pdf`, sha256 `b335ee2ec083…`.
Đọc targeted: Abstract và §1 (tr. 1033–1034), §3 (tr. 1034–1035), §4.1 và Eq. 2–3 (tr. 1035–1036), đoạn mở §5 và §5.1
(tr. 1036–1037), §6 (tr. 1044–1045). Không đọc §5.2–5.7 chi tiết, không đọc các hình.

**Câu hỏi đọc.** Bài có làm co claim C3/C5 hoặc câu thực dụng của τ không ("telemetry tươi chỉ có ích khi twin nhìn được
horizon hoặc tuổi")?

**Quan sát (trích vị trí)**
- **Vấn đề (§1, tr. 1033).** Gửi mỗi request tới máy trông nhẹ nhất "can behave badly if load information is old". Hiệu
  ứng bầy đàn ("herd effect"): máy trông rảnh bị quá tải vì mọi request dồn vào đó cho tới khi thông tin mới được phát.
- **Mô hình thông tin cũ (§3, tr. 1034–1035).** Ba mô hình:
  - periodic update (bulletin board cập nhật mỗi T);
  - continuous update (trễ trung bình T), hai mô hình này lấy từ Mitzenmacher (M00);
  - update-on-access.
  T đo bằng đơn vị thời gian phục vụ trung bình.
- **Thuật toán (§4, tr. 1035–1036).** Hai nguyên tắc: xét độ lớn chênh lệch, không chỉ thứ hạng; và diễn giải theo tuổi T
  và tốc độ đến λ. Basic LI (Eq. 2) chọn xác suất P_i gửi tới server i sao cho tải các server **bằng nhau ở cuối pha dài
  T**. Eq. 3 xử lý trường hợp pha quá ngắn để cân bằng hết.
- **Thiết lập đánh giá (§5, tr. 1036–1037).** Mô phỏng: Poisson, n = 100 server, λ = 0,9, FIFO, phục vụ exponential;
  500.000 job mỗi lần chạy, khoảng tin cậy 90%.
- **Kết luận (§6, tr. 1045).** LI "resolves the paradox that under some algorithms, using additional information can
  result in worse performance than using less information or none at all". Với LI, hệ "essentially always better off when
  it has and uses more information": tin tươi thì xử lý mạnh, tin cũ thì thận trọng. So với k-subset: tới 60% tốt hơn khi
  tin hơi cũ, không bệnh lý khi tin rất cũ. Đây là kết quả mô phỏng, chưa có cận giải tích (§6).

**Suy luận của AI (chưa kiểm bởi tác giả)**
- **Đây là prior trực tiếp cho câu "thêm thông tin có thể tệ hơn" trong cân tải**, và cho cách chữa bằng diễn giải theo tuổi
  và horizon của pha. Không được viết rằng ta là người đầu tiên thấy nghịch lý này ở networking.
- **Khác ta ở cơ chế và chiều.**
  - Ở Dahlin, nhiều request trong một pha cùng dùng một bảng cũ, nên có herding; luật tham lam bị hại bởi thông tin **cũ**.
  - Ở ta, một quyết định giữ suốt h, không có herding; twin mù horizon bị hại bởi thông tin **tươi** so với thông tin cũ.
  - Nhưng ý "tin cũ thì thận trọng gần với ngẫu nhiên/dừng" cùng tinh thần với giả thuyết planner ngầm (C5): posterior cũ
    gần dừng làm M0 hành xử gần planner dừng.
- **Câu thực dụng của τ phải định vị so với Dahlin.** "Muốn telemetry tươi có ích thì twin phải nhìn được horizon" là phiên
  bản một-quyết-định, model-based của nguyên tắc LI. Đây là AI đề xuất, chờ tác giả.
- Basic LI cân bằng "tới cuối pha T" chính là một luật có horizon, so được với hybrid M0 + h·s của ta. Chưa so định lượng.

PC liên quan: PC3, PC4 (định vị thông tin hại), claim C3/C5 và τ. Không đổi nhãn PC, không có claim novelty.
