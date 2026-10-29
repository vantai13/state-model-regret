# LTWW94 — Ethernet traffic across timescales

Người phụ trách/người soạn: **Doan Van Tai** · 29/10/2026.
Được duyệt L3R.4; AI-T, tác giả tự đọc: chưa có xác nhận.

Leland,Taqqu,Willinger,Wilson. IEEE/ACMToN2(1):1–15,1994,
[DOI](https://doi.org/10.1109/90.282603).
[SFU journal PDF](https://www.sfu.ca/~ljilja/ENSC835/Spring09/Assignments/papers/00282603.pdf),
local `~/papers/state-model-regret/l3r_4/LTWW94.pdf`.
Header xác nhận Extended Version/ToN1994; bản Stanford được kiểm là conference1993,
không dùng numbering của nó cho note journal. IEEE page robot-blocked; identity
đối chiếu Crossref + header journal, không nhận đã đọc publisher HTML đầy đủ.
Targeted PDF1–2/TableI,§3.1/PDF4,§4/PDF7–8 (xem Fig5/PDF8),§5.2/PDF12.

Câu hỏi: traffic có smoothing đơn thang như telegraph không?
Observation: LAN Bellcore1989–92; phân tích số byte/packet theo các cửa sổ và
aggregation levels. §4.1 dùng360000quan sát10ms trong giờ được chọn. Các kết quả
variance-time/Hurst cho thấy self-similarity trong traces này. §5.2/Fig8 báo IDC
tăng qua nhiều thang thay vì nhanh chóng bão hòa như một số mô hình truyền thống.

Inference: nguồn phản bác cách coi một exponential timescale là mô tả chung;
giữ scope Markov hai mức và kiểm đa thang sau này. Không lấy IDC hoặc CV của
interarrival làm CV_rate; không lấy min/maxutilization TableI làm bound cho edge
hiện đại10–100Mb/s. Không khẳng định mọi mạng Ethernet hay mọi traffic đều self-similar.
