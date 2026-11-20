# IDZ16 — Idzikowski et al.: survey thiết kế và vận hành tiết kiệm năng lượng ở mạng lõi

- Người phụ trách: **Doan Van Tai** · 20/11/2026. Note do AI (Claude) soạn.
- Tác giả duyệt nguồn ngày 20/11, issue 1, đề xuất số 1 trong `letter_smr/briefs/issue1/search/SYNTHESIS_SEARCH.md`.
- Tác giả tự tải: `Downloads/idzikowski2016.pdf`.
- Mức đọc AI: AI-T. Tác giả tự đọc: chưa có xác nhận.

F. Idzikowski, L. Chiaraviglio, A. Cianfrani, J. López Vizcaíno, M. Polverini, Y. Ye. *A Survey on Energy-Aware Design and Operation of
Core Networks*. IEEE Commun. Surveys Tuts. 18(2):1453–1499, 2016. [DOI 10.1109/COMST.2015.2507789](https://doi.org/10.1109/COMST.2015.2507789).
Metadata đối chiếu Crossref ngày 20/11.

**Phiên bản.**
- Bản **early access** ("accepted for publication… not fully edited"), 46 trang PDF.
- Chưa đối chiếu số trang bản in, nên chỉ trích §/bảng, không trích trang in.
- Lưu tại `~/papers/state-model-regret/current/IDZ16_COMST2016_earlyaccess.pdf`, sha256 `8eb71007…`.

**Đọc targeted:** §IV, phần thảo luận từng nhóm routers và LCs (PDF p17–18); Table XII (PDF p34, thuộc §VI). Không đọc §III, §V và phần
còn lại của §VI.

**Câu hỏi (issue 1):** lớp twin hoặc optimizer không có hàng đợi có phổ biến trong quyết định mạng được giữ lâu không?

**Quan sát (trích vị trí)**
- **§IV, PDF p18 (nhóm routers):** "QoS, it is ensured by imposing a maximum link utilization constraint, normally with an
  overprovisioning factor". Sự kiện kích hoạt "will be likely the TM change (as considered by most of the surveyed work)"; "the future
  traffic is assumed to be known by most works".
- **§IV, PDF p18 (nhóm LCs):** QoS "is normally ensured by means of the standard overprovisioning"; "a limited number of approaches consider
  the future traffic to be unknown (which is a realistic assumption)".
- **Table XII, PDF p34 ("QoS evaluation metrics…"):** "Link/Node utilization" ở 61 bài, "Propagation delay" ở 9 bài, "Queue length" ở 1 bài [161].

**Suy luận của AI (chưa kiểm bởi tác giả)**
- Trong vận hành tiết kiệm năng lượng mạng lõi, gần như mọi công trình đánh giá cấu hình bằng utilization, không có hàng đợi, và kích
  hoạt theo thay đổi TM. Đây là lớp mô hình không có hàng đợi cho quyết định giữ lâu.
- Survey **không** nói các bài đó dùng mẫu tức thời theo nghĩa backlog của M0, và **không** nói chúng bị hại.

**Dùng trong letter (v8.6):** câu motivation ở Introduction, `\cite[Sec.~IV and Table~XII]{Idzikowski:COMST:2016}`. Theo luật hai agent,
Claude và Codex kiểm trước khi đưa vào.
