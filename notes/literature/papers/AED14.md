# AED14 — CONGA: congestion-aware load balancing trong DC

Người phụ trách: **Doan Van Tai** · 03/11/2026. Note do AI (Claude) soạn.
Nguồn được duyệt theo ủy quyền L7.3-R1 ("bạn hãy tự làm tự chạy thực hiện cho tôi luôn đi"), tức AI-delegated,
không phải tác giả tự sàng. Mức đọc: AI-T. Tác giả tự đọc: chưa có xác nhận.

Alizadeh, Edsall, Dharmapurikar, Vaidyanathan, Chu, Fingerhut, Lam, Matus, Pan, Yadav, Varghese. SIGCOMM 2014,
tr. 503–514. [DOI 10.1145/2619239.2626316](https://doi.org/10.1145/2619239.2626316).
PDF lấy từ [trang tác giả](https://people.csail.mit.edu/alizadeh/papers/conga-sigcomm14.pdf): 12 trang, khớp số
trang ACM. Lưu local tại `~/papers/state-model-regret/l73/AED14/AED14_CONGA_author.pdf`, sha256 `b0a6e69eaa00…`.
Đọc targeted: §1–2.1/PDF2, §2.6–2.6.1/PDF4, §3.1–3.4/PDF5, §3.6 và §5.1/PDF6. Không đọc §5.2–5.5 (kết quả FCT)
và §6 (Price of Anarchy).

**Câu hỏi.** Một quyết định flowlet giữ trong bao lâu (h)? Thông tin congestion cũ bao nhiêu (τ)?

**Quan sát (trích vị trí)**
- **Phản ứng.** CONGA phản ứng với congestion ở thang RTT, khoảng 100 µs. Để so sánh, scheduler Hedera chạy mỗi 5 s
  (§1/PDF2).
- **Đo flowlet.** Bài đo với các gap 250 ms, 500 µs và 100 µs. Khi tính theo flow, 50% byte nằm trong flow lớn hơn
  khoảng 30 MB; với "Flowlet (500µs)" con số này giảm còn khoảng 500 KB (§2.6.1/PDF4). Đây là trung vị theo byte,
  không phải thời lượng.
- **Bộ ước lượng tải (DRE).** Thanh ghi X tăng theo byte của mỗi packet và được nhân với (1 − α) mỗi T_dre.
  Khi đó X ≈ R·τ với τ = T_dre/α, tức một bộ lọc low-pass bậc một có rise time τ. Metric là X/(Cτ) lượng tử hóa
  3 bit (§3.2/PDF5).
- **Aging.** Metric không được cập nhật lâu (ví dụ 10 ms) giảm dần về 0, nên path tưởng bị nghẽn sẽ được thử lại
  (§3.3/PDF5).
- **Phản hồi.** Leaf đích giữ metric trong Congestion-From-Leaf Table cho tới khi có packet ngược chiều để piggyback
  (§3.3/PDF5). Trễ phản hồi vì thế phụ thuộc traffic ngược chiều.
- **Phát hiện flowlet.** Mỗi entry có một age bit, timer kiểm mỗi T_fl. Cách này phát hiện được gap nằm giữa T_fl và
  2·T_fl (§3.4/PDF5–6).
- **Tham số (§3.6/PDF6).**
  - Mặc định: Q = 3, τ = 160 µs, T_fl = 500 µs.
  - Hiệu năng bền với Q = 3–6, τ = 100–500 µs, T_fl = 300 µs–1 ms.
  - τ nên lớn hơn RTT để lọc burst dưới-RTT của TCP. T_fl có thể đặt bằng trễ leaf-to-leaf lớn nhất để không gây
    reordering.
- **Testbed (§5.1/PDF6).** 64 server, 2 leaf, 2 spine, link server 10 Gb/s, uplink 40 Gb/s. CONGA-Flow dùng
  T_fl = 13 ms, tức mỗi flow một quyết định.

**Suy luận của AI (chưa kiểm bởi tác giả)**
- h của một quyết định là thời lượng flowlet, tối thiểu cỡ T_fl. Nếu flowlet 500 KB chạy ở rate 1–10 Gb/s thì kéo
  dài 0,4–4 ms. Rate của từng flow là UNSOURCED, nên khoảng này là phép tính của AI.
- τ ≈ hằng số thời gian DRE, 0,1–0,5 ms (tuổi trung bình của một bộ lọc bậc một bằng τ), cộng trễ piggyback.
  Trễ piggyback không có số trong phần đã đọc. Ngưỡng aging 10 ms là chặn trên thô cho tuổi của một metric còn được
  dùng; đây là ví dụ trong bài, không phải phân phối tuổi.
- **Khác contract.**
  - Metric là rate lượng tử hóa, không phải backlog.
  - Mục tiêu là cân bằng max congestion trên path.
  - Quyết định đi theo flowlet, nên h thay đổi chứ không cố định.
- Không suy rằng CONGA "validate" vùng state của ctmc-v1. Bài chỉ cho thấy một thiết kế thực dùng state tươi ở thang
  RTT.

PC liên quan: realism / RQ3. Không đổi nhãn PC, không có claim novelty.
