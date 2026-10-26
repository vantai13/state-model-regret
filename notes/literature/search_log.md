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

## Dọn thư viện — 24/10/2026, không phải phiên tìm paper

Theo yêu cầu tác giả: giữ R32/R34/R51 trong bảng chính; 18 mã còn lại lưu tạm.
Phân loại từ metadata/notes sẵn có, không chạy query hoặc đọc nguồn mới;
không đổi nhãn PC/Gate. R51 là DT chung, không tính thành paper networking.

Bảng chính chuyển thành `papers/paper_comparison.xlsx`. Dữ liệu cũ ở
`papers/archive/data/`, gồm `classification_source_check.json` được nhắc trong
lượt kiểm lịch sử phía trên. Snapshot 21 bài, CSV và 4 nhóm cũ ở `papers/archive/`.
PDF/text và audit chưa tracked chuyển ra kho local; đường cũ/mới, checksum và
lý do ở [manifest](../../papers/archive/cleanup_manifest.json).

## L2.4 Part2–3 — 25/10/2026, AI thực hiện theo tài liệu tác giả

Thẻ trước query: [search_card.md](../../results/lessons/l2_4/search_card.md).
Lookup được ủy quyền từ hai lesson; không kế thừa số đếm hay mức đọc của mentor.
Hai đợt nguồn có tên: NDT1/NMRG/P05, rồi P10/P08/S07. Không tải ứng viên snowball chưa duyệt.

| Ngày | Loại | Q / PC | Query / seed | Tool, bộ lọc, thứ tự | Đã sàng | Giữ unique | Lý do / hạn chế / dừng |
|---|---|---|---|---|---:|---:|---|
| 2026-10-25 | lookup | Q2.2 / PC2,PC5 | NDT1 DOI10.1109/MCOM.001.2200012, arxiv2205.14206v2 | paper-search Crossref/download; web arxiv; paper-pilot pages2–7/render3,5 | 1 | 1 | T, input/optimizer/metric; bản v2 hash trùng PDF đã có ở reference, current dùng alias |
| 2026-10-25 | lookup | Q2.2 / PC2,PC6 | NMRG current page và draft-13 | web Datatracker, §4/selected§5–6 | 1 | 1 |5yếu tố gồm Logic; real-time tùy use case; vẫn Internet-Draft |
| 2026-10-25 | lookup | Q2.2 / PC2,PC5 | P05 DOI10.1109/TNSM.2026.3652800, Sapienza PDF | Crossref; web PDF §III–VI selected | 1 | 1 | Full text web đọc được; targeted; UNEX page không truy cập, không lấy đó làm nội dung |
| 2026-10-25 | lookup | Q2.2 / PC2,PC5 | P05 local download và screenshot | urllib, paper-pilot inspect cùng URL; web screenshot PDF4/11 | 0 | 0 |2local attempts403;2screenshots cache miss; dừng tải, không ghi có PDF local hoặc đã nhìn TableIII |
| 2026-10-25 | lookup | Q2.2 / PC2,PC5 | P10 arxiv2605.24662v2 | web abstract; paper-search download; paper-pilot pages3,5–8,11 | 1 | 1 | T; resync đổi inferred config, không chỉ state refresh; joint-rate khác selective risk |
| 2026-10-25 | lookup | Q2.2 / PC2,PC5 | P08 arxiv2312.03374v1; DOI10.1109/MNET.2023.3332893 | web abstract; Crossref; download; paper-pilot pages3–5 | 1 | 1 | T§2–3 xác nhận taxonomy; issue2024 khác preprint2023; chưa đọc đầy đủ field trial |
| 2026-10-25 | lookup | Q2.2 / PC5 | S07 arxiv2212.12070v3; DOI10.1109/TNET.2023.3269983 | web abstract; Crossref | 1 | 1 | Abstract-only; không tải PDF; MRE6,24% là số paper báo |
| 2026-10-25 | backward | Q2.2 / PC2,PC5 | NDT1 PDF7 references1–15 | paper-pilot page text; thứ tự references trong PDF | 15 | 0 mới | Nhận diện NMRG predecessor đã có; các mục khác chưa kiểm nội dung, không gọi15bài đã đọc |
| 2026-10-25 | forward | Q2.2 / PC2,PC5,PC6 | DOI10.1109/MCOM.001.2200012 citations | scholar-search Semantic Scholar, limit100 offset0, provider order | 100 | 0 thêm thư viện;3 đề xuất |100unique,next100; title-screen; chưa duyệt/đọc abstract ứng viên; dừng theo ngân sách |

Từng record forward/backward, source metadata/access, metric toy và log ở
[results/lessons/l2_4](../../results/lessons/l2_4/). Không chạy OpenAlex trong phiên
này; không xác nhận số169/6 từ lesson. Không claim coverage đầy đủ hay Gate L2.8.

## L2.5 Part1 — 26/10/2026, lookup nguồn tác giả yêu cầu

[Thẻ đọc trước lookup](../../results/lessons/l2_5/reading_card.md).
Câu hỏi: stale link-state × tải × routing và cost metric đã có gì; phục vụ PC2/PC3/PC4/PC6.

| Ngày | Loại | Q / PC | Query / seed | Tool / phạm vi | Đã sàng | Giữ unique | Lý do / hạn chế / dừng |
|---|---|---|---|---|---:|---:|---|
| 2026-10-26 | lookup | L2.5 / PC2,PC3,PC4,PC6 | DOI10.1109/90.917073 | paper-search Crossref | 1 | 1 | ToN9(2):162–176,2001; journal khác predecessor ICNP1998 |
| 2026-10-26 | lookup | Cùng nguồn P04 | Princeton qosroute.pdf | web open | 0 | 0 mới |403; không coi lỗi truy cập là không có paper |
| 2026-10-26 | lookup | Cùng nguồn P04 | Michigan author PDF shaikh2001impact.pdf | web + paper-pilot inspect, page text và render | 1 | 0 mới |15trang; targeted §I–III/IV-A/V-A/VI, render PDF3/4/6/12; cùng paper đã giữ |

Một paper mới trong bảng, không phải ba paper. Không query discovery, không tìm
M00/P01 hoặc đọc Part2. Dừng khi đủ câu hỏi của thẻ; không claim coverage L2.8.
PDF local/checksum ở [source_access.json](../../results/lessons/l2_5/source_access.json);
đã sửa số trang14→15 và cách đọc Fig8b (setup failures, pruning ON).
Không thêm dự đoán mù sau exposure từ attachment; không tự cấp L-self hoặc nhãn Gate.

## L2.5 Part2 — 26/10/2026, hai nguồn được tác giả yêu cầu

[Thẻ đọc trước lookup](../../results/lessons/l2_5/part2/reading_card.md).
Câu hỏi: M00 herding khác V1 fixed-M0 harm thế nào; P01 regret và §2.5 có cùng
E/M/R với D18–D21 không? PC2/PC3/PC4/PC6, không đổi nhãn hoặc research goal.

| Ngày | Loại | Seed/query | Tool / phạm vi | Đã sàng | Giữ unique | Kết quả / lỗi / dừng |
|---|---|---|---|---:|---:|---|
| 2026-10-26 | lookup | M00 DOI10.1109/71.824633 | paper-search Crossref exact DOI | 1 | 1 | TPDS11(1):6–20,2000; không lẫn predecessor PODC1997 |
| 2026-10-26 | lookup | M00 oldinfo-jver-submit.pdf Harvard | web open; paper-pilot inspect/get pages1–3/render4,10,11,12; pdftotext-layout selected pages | 1 | 0 mới | Submission28trang; MCP text cũ bị tách chữ, dùng layout+web/render; T abstract/§2/§3.1/§3.4/selected§3.6/§4–5/§7 |
| 2026-10-26 | lookup | P01 arxiv2106.04707v1 | web open abs/v1 | 0 | 0 | Cache miss; không coi là thiếu paper |
| 2026-10-26 | lookup | Cùng P01 arxiv2106.04707v1 | paper-search download_with_fallback(source=arxiv,use_scihub=false); paper-pilot pages1,3,4/render3,4; pdftotext | 1 | 1 |32trang; targeted Def1–2/§2.2–2.5/Fig2; skip full read, note bổ sung ngoài bảng chính; pdfinfo cảnh báo xref, vẫn extract/render được |

**Hai unique papers** giữ làm evidence tra, trong đó chỉ **M00** thêm catalog
(7→8); P01 không thành yêu cầu đọc full. Không keyword/forward/backward search,
không số đếm coverage. Không chạy Crossref cho P01: lần sai “dental cleaning”
trong mentor **không phải thao tác của phiên này**, không sao chép thành log.
R04 chỉ kiểm archived AI-T note/path/checksum có sẵn, không query/download hoặc
đọc lại primary. Không phục hồi18nguồn hoặc tải3 snowball chưa duyệt.

Dừng: đã đủ mô hình/cơ chế, regret definition và điều kiện của Fig2 để trả thẻ;
không cần proofs P01, full VoR M00 hoặc discovery rộng. AI-T tách mức tác giả;
publication identity M00 đã kiểm, nội dung VoR chưa đối chiếu; status công bố
chính thức P01 chưa kiểm (v1 có DOI placeholder). Không dùng lookup làm survey.
[Access/checksums](../../results/lessons/l2_5/part2/source_access.json),
[technical report](../../results/lessons/l2_5/part2/report.md). Gate/L-self/A4 còn mở.

## L2.6 Part A — 26/10/2026

[Thẻ trước lookup/query](../../results/lessons/l2_6/part_a/reading_card.md).
Câu hỏi PC2/PC3/PC4/PC6: AoI/error/uncertainty/decision value khác nhau thế nào;
S11 có dùng action feedback và có đúng controlled repair D21 không? Không đổi PC.
Tác giả đã yêu cầu5nguồn có tên: đợt1 S11/Kaul/AoII, đợt2 AY19/R32; R32 có sẵn.

| Loại | Seed/query / tool | Thực sàng | Giữ không trùng | Kết quả / giới hạn |
|---|---|---:|---:|---|
| lookup | S11 arxiv2504.19507v3, web abs/HTML + paper-search arxiv download | 1 | 1 |42trang; AI-T §§I–III/PDF1–7, §VII-C–D/PDF17; render5/6/7/17. PDF ngoài Git |
| lookup | DOI10.1109/TWC.2025.3593377, paper-search Crossref | 1 | 0 |Đúng là bài spinal codes khác, không dùng DOI này cho S11 |
| lookup | Crossref title `From Freshness to Effectiveness Goal-Oriented Sampling for Remote Decision Making`, max3; exact DOI TIT; đối chiếu arxiv journal ref | 3+1 records | 0 mới |Match DOI10.1109/TIT.2026.3663678, TIT72(4):2237–2276,2026. Sửa kết luận preprint-only của mentor; nội dung vẫn đọc v3, chưa VoR comparison |
| lookup | Kaul DOI10.1109/INFCOM.2012.6195689, Crossref; IEEE6195689 | 1 | 1 |Metadata khớp; direct IEEE bot challenge |
| lookup | Web title `Real-time status: How often should one update` Kaul Yates abstract; mở Rutgers | 2 primary records | 0 mới |Chỉ sàng IEEE/indexed abstract và Rutgers cùng bài, không xem toàn kết quả search là paper reviews. AI-A, không PDF |
| lookup | AoII title `The Age of Incorrect Information A New Performance Metric for Status Updates Maatouk 2020`, Crossref max3 | 3 | 1 |Match DOI10.1109/TNET.2020.3005549; hai metadata còn lại không phải target |
| lookup | Web title `The Age of Incorrect Information` Maatouk arxiv; mở1907.06604v2 HTML | 2 arxiv titles | 0 mới |1907.06604 đúng target;2012.13214 là bài khác, không theo. AI-T §II/Eq3–9 để sửa K3, không metadata-only cho definition |
| lookup | AY19 arxiv1903.05356v1 abs/HTML; Crossref exact-title max2 | 1+2 records | 1 |ICCPS2019, DOI10.1145/3302509.3311050; AI-T §2.2 Assumptions1,4/§2.4 Eq13–19; không gán quadratic error thành bit |
| lookup | R32 DOI10.1109/TAC.2021.3113472 Crossref; arxiv1812.07534v2 abstract; kiểm PDF local | 1 | 0 mới |Issue2022,67(7):3730–3737; lượt này A; targeted workbook record cũ giữ nguyên, không tải lại |
| keyword | scholar-search search_papers: `"age of information" "model mismatch" remote control`, limit10, không năm/venue, provider order | 10 titles | 0 mới |Result source fields là arxiv, nhiều title lạc remote sensing; chưa xác minh backend/query semantics, không gọi đây là S2 coverage |
| keyword | web fallback: `"age of information" ("model mismatch" OR misspecified) control`, không năm/venue, thứ tự provider | 18 titles | 0 mới |Title-screen, có records trùng/secondary.1candidate metadata treo A4, chưa primary content review/download/note |

5nguồn có tên được đối chiếu (kể cả R32 đã có); **chỉ S11 thêm catalog 8→9** và
chỉ1PDF mới. Kaul/AoII/AY19 là tra bổ sung trong K3.10+18 là **28title records**,
không phải28unique full/abstract reviews; không chép query hay “khoảng10” của mentor.

**A4 metadata queue:** title *Robustness Analysis of Networked Control Systems
with Aging Status*, URL https://ieeexplore.ieee.org/document/9162929, từ fallback.
Chưa xác minh DOI/model assumptions hoặc xem primary nội dung; có thể cần kiểm
robustness/mismatch, chưa đề xuất thêm thành bài bắt buộc. Không tải hoặc tạo note.
Các kết quả khác không được dùng làm evidence về estimand D19/D21.

Raw selected metadata/28title records ở [lookup_records.json](../../results/lessons/l2_6/part_a/lookup_records.json).
Không forward/backward search trong phiên này, không đạt luật hai query×20,
không kết luận thiếu prior. Dừng theo phạm vi Part A: formulation/definition đã
đủ, thuật toán/proofs/Part B không cần ở đây. A4 tiếp tục các query `value of
information + misspecified`, `age of information + model uncertainty`, `certainty
equivalence + stale` (chưa chạy ba query này trong phiên).
AI-T khác L-self; scientific dependency A4/L2.9 và formal Gate còn mở.
