# Search log — tra cứu và tìm paper

**Trước mỗi phiên:** mở [quy tắc + checklist](search_protocol.md).
Các bảng L2.1–L2.3 bên dưới giữ nguyên lịch sử; phiên mới dùng bảng cuối file,
phân biệt lookup/keyword/backward/forward/author/venue.

Người phụ trách: **Doan Van Tai** · AI đặt query và screen, 24/10/2026.
Được tạo theo yêu cầu hoàn tất các deliverable. Chỉ log lượt thực sự chạy;
không dựng số đếm cho các phiên chat trước. Lookup có tên không được tính thành
bốn phiên blind-spot A1–A4 của L2.8.

| Ngày | Vùng | Query/đường vào | Tool/CSDL | Screened | Giữ | Lý do |
|---|---|---|---|---:|---:|---|
| 2026-10-24 | L2.3 | DOI 10.1137/120889563 | paper-search Crossref | 1 | 1 | P11, metadata+abstract khớp |
| 2026-10-24 | L2.2 | DOI 10.1177/0272989X13505910 | paper-search Crossref | 1 | 1 | SOB14, online 2013, issue 2014 |
| 2026-10-24 | L2.2 | DOI 10.1007/BF01585113 | paper-search Crossref | 1 | 1 | B82, metadata; mở abstract publisher riêng |
| 2026-10-24 | L2.2 | DOI 10.1007/s11750-007-0005-4 | paper-search Crossref | 1 | 1 | E07, metadata; mở abstract publisher riêng |
| 2026-10-24 | L2.3 | DOI 10.1111/j.1467-9876.2011.01014.x | paper-search Crossref | 1 | 1 | SOC12, precursor, screen abstract |
| 2026-10-24 | L2.2 | https://aisberg.unibg.it/handle/10446/885 | web open | 0 | 0 | HTTP403; không tính là đã đọc §2 |
| 2026-10-24 | L2.2 | https://link.springer.com/article/10.1007/BF01585113 | web open | 1 | 1 | Publisher abstract đọc được, full text chưa xác nhận |
| 2026-10-24 | L2.2 | https://link.springer.com/article/10.1007/s11750-007-0005-4 | web open | 1 | 1 | Publisher abstract đọc được, chỉ dùng mức A |
| 2026-10-24 | L2.3 | https://eprints.whiterose.ac.uk/id/eprint/87843/ | web open | 1 | 1 | Metadata và link published PDF |
| 2026-10-24 | L2.2 | https://eprints.whiterose.ac.uk/id/eprint/78428/ | web open | 1 | 1 | Metadata và PDF SOB14; giữ khác biệt online/issue year |

Các đường PDF, checksum, lỗi tải và kết quả đọc nằm trong source_access.json và
paper note. Bản ghi trùng DOI không tính là bài độc lập. Không dùng citation
count làm bằng chứng chất lượng; không gọi thư viện lậu.

## Lượt bổ sung để giải quyết nguồn bị chặn, cùng ngày

| Query/đường vào | Tool | Phạm vi thực screen | Kết quả |
|---|---|---|---|
| DOI B82 10.1007/BF01585113 | paper-search download_with_fallback, use_scihub=false | Lookup1, không phải search coverage | Không có direct/repository PDF; Unpaywall không trả OA URL hoặc thiếu email cấu hình |
| "The value of information in multi-stage linear stochastic programming" Maggioni Allevi Bertocchi | web search | Giữ1 primary repository record, các kết quả khác không screen đầy đủ | Metadata/abstract MAB11; giữ mức A, không xác nhận §2 |
| "The value of the stochastic solution" "1982" pdf Birge | web search | Giữ1 Deep Blue primary PDF candidate, các kết quả khác không screen đầy đủ | PDF403; không dùng các nguồn thứ cấp để thay full text |
| Deep Blue PDF và MAB11 retrieve PDF | web open | 2 access attempts, không tính thành 2 paper mới | Cả hai HTTP403; dừng, ghi giới hạn |
| P11/SOB14 published PDF | urllib + pdftotext local | 2 PDF tải thành công | T theo section/page trong note; không gọi F/L-self |

Không cộng các lookup trùng vào tổng unique paper hoặc coi đây là blind-spot
session. Lượt search bổ sung không đạt stopping rule hai query×20 results và
không được dùng để kết luận không có prior.

## Thư viện Excel — chỉ Part A, 24/10/2026

Theo yêu cầu tạo thư viện/Excel và push bảng; sau đó tác giả giới hạn chỉ Part A.

| Đường vào thực chạy | Nguồn/tool | Screen / giữ trong thư viện | Kết quả |
|---|---|---|---|
| DOI của SOB14/B82/P11/E07/SOC12 | paper-search Crossref | 5 / 5 | Metadata chính thức khớp; năm workbook theo issue, không nhầm online year |
| MAB11, exact-title query | web search, repository Bergamo | 1 primary record / 1 | Working paper2011; chỉ dùng abstract, không tự cấp peer review |
| SOC12, exact-title OA query | web search, White Rose | 1 primary PDF / 1 | Tải author manuscript,36trang; vẫn ghi mức đọc abstract |
| 6 link PDF trong papers/data/catalog.json | urllib / local cache, pdfinfo, pdftotext p1 | 6 attempts / 3 PDF thành công | SOB14/P11/SOC12: title/hash/pages kiểm được; B82/MAB11 HTTP403; E07 trả non-PDF |
| B82 primary PDF + E07 DOI-only | paper-pilot inspect_open_access_pdf | 2 retries / 0 PDF mới | B82 vẫn403; E07 không có OA PDF URL; không dùng shadow libraries |

Các lookup ngoài Part A trước lúc tác giả thu phạm vi không được đưa vào Excel
hoặc thư viện. Không ghi các mục đó như đã hoàn thành Part B. Workbook chỉ có
6 bài; comparison/priority là AI đề xuất, hai targeted và bốn abstract readings,
không mục nào được tự ghi full reading hay L-self. Không tính là blind-spot L2.8.

## Kiểm danh tính và phân loại21 bài — 24/10/2026

Người phụ trách: Doan Van Tai; AI thực hiện theo yêu cầu làm rõ paper/thư mục.

| Lookup thực chạy | Nguồn/tool | Screened / giữ | Kết quả |
|---|---|---|---|
| 15 DOI trong6 nguồn Part A và15 bài audit | paper-search Crossref | 15 / 15 | Title/DOI tồn tại; không nâng mức đọc nội dung |
| R43, R06, R07, R18, R51 | NeurIPS, arXiv, trang tác giả MIT | 5 / 5 | Đối chiếu loại nguồn và identity; preprint/sách không tự thành journal |
| R10 chapter DOI | Springer official chapter page | 1 / 1, trùng DOI đã lookup | Publisher ghi1997, pp137–152; không dùng placeholder1970 từ Crossref |
| MAB11 exact-title + repository filter | web search, Bergamo repository | 1 primary / 1 | Working paper2011, giữ abstract-only |
| R51 / P03 | PMLR official proceedings | 1 / 1, cùng paper đã kiểm | DT² cùng bài, không phải hai paper khác nhau |

21 unique IDs được kiểm metadata, không phải21 full-text reviews. Phân nhóm
3 đọc chính /6 bổ trợ /7 audit /5 để sau là AI đề xuất lộ trình; không thêm bài
bắt buộc cho Part A, không đổi contract/claims/Gate. DOI/URL/kết quả kiểm tại
`papers/data/classification_source_check.json`. Bản ghi audit/nguồn gốc vẫn giữ.

## Phiên tiếp theo — theo quy tắc tìm và kiểm paper

Áp dụng từ 24/10/2026. Thay đổi quy trình này không chạy query hay kiểm paper
mới, nên chưa thêm dòng kết quả. Ghi từng query/đường vào thực chạy; thẻ tìm
kiếm và ý nghĩa các cột ở [quy trình](search_protocol.md).

| Ngày | Loại | Thẻ / Q / PC | Query / seed | Tool, bộ lọc, thứ tự | Đã sàng | Giữ unique | Lý do / hạn chế / dừng |
|---|---|---|---|---|---:|---:|---|
