# KKSB07 — FLARE: chia traffic theo flowlet không reorder

Người phụ trách: **Doan Van Tai** · 04/11/2026. Note do AI (Claude) soạn.
Tác giả tự tải (thư mục Downloads, 07:06–07:08 ngày 04/11) sau danh sách L7.3-R2 đợt 3. Mức đọc: AI-T.
Tác giả tự đọc: chưa có xác nhận.

Kandula, Katabi, Sinha, Berger. *Dynamic Load Balancing Without Packet Reordering*. ACM SIGCOMM CCR 37(2) (2007),
tr. 51–62. [DOI 10.1145/1232919.1232925](https://doi.org/10.1145/1232919.1232925).

**Phiên bản.** 11 trang, trang đầu là public review của CCR. Hai file tác giả tải trùng sha256; giữ một bản tại
`~/papers/state-model-regret/l73/KKSB07/KKSB07_FLARE_CCR07.pdf`, sha256 `297f59fec63a…`. Chưa đối chiếu số trang với ACM DL.
Đọc targeted: §4–5/PDF3–4, §8/PDF5–6 (Fig. 3–5), §9.1–9.2/PDF6–7 (Fig. 6–7).

**Quan sát (trích vị trí)**
- **Định nghĩa (§4/PDF3).** Flowlet timeout δ phải lớn hơn MTBS, tức chênh lệch trễ lớn nhất giữa các path song song.
  Khi đó đổi path giữa hai flowlet không gây reorder.
- **Ước lượng MTBS (§5/PDF4).** FLARE ước MTBS bằng ping định kỳ, làm mượt bằng trung bình chạy exponential. Measurement
  interval mặc định 0,5 s.
- **Thí nghiệm (§8/PDF5–6).** Thí nghiệm dùng MTBS = 50 ms, gần RTT xuyên lục địa, trên trace ISP. Flow lớn vẫn bị chia
  thành nhiều flowlet nhỏ ngay cả khi δ = 50 ms (Fig. 3). Fig. 5 cho khoảng cách giữa hai flowlet của cùng flow, chuẩn hóa
  theo RTT.
- **Độ chính xác (§9.1/PDF6–7).** Chia flowlet chính xác ngang chia packet khi MTBS dưới 100 ms (Fig. 6). Sai số tính trên
  cửa sổ 300 ms vì router thường buffer khoảng 300 ms traffic.

**Suy luận của AI.** Timeout của flowlet, và do đó cận dưới của h ở ô (i), **tỷ lệ với chênh lệch trễ giữa các path**:
khoảng 50 ms trên WAN/ISP (FLARE), 0,2–0,5 ms trong DC (VPA17, AED14). Bối cảnh của FLARE là ISP, không phải DC.

PC liên quan: realism / RQ3. Không đổi nhãn PC.
