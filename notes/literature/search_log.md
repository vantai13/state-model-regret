# Search log — nguồn cho L2.1–L2.3

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
