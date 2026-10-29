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

## L2.6 Part B — 26/10/2026, tiếp tục sau một lần gián đoạn

[Thẻ trước lookup](../../results/lessons/l2_6/part_b/reading_card.md).
Câu hỏi PC3/PC4/PC6: P13 transient/continuous staffing có ngụ ý gì cho horizon,
backlog và approximation trong binary routing? Chỉ một paper tác giả yêu cầu.

| Loại | Seed / tool / phạm vi | Thực sàng | Giữ không trùng | Kết quả / hạn chế |
|---|---|---:|---:|---|
| lookup | DOI10.1007/s11134-016-9511-0; paper-search Crossref, exact DOI | 1 paper,2calls | 1 |Một call trước gián đoạn, một lặp sau resume để lưu metadata; cùng paper, không hai kết quả độc lập |
| lookup | CWI25530/25530.pdf; web + paper-pilot inspect, pdftotext-layout | 1 | 0 mới |Journal VoR36trang,269–304; downloaded1PDF. Targeted §2/Thm1/§4/selected§5–6; không full proof/replication |
| lookup | Journal figure/equation checks; paper-pilot render PDF7/8/14/15/16/18/20/21 | 1 | 0 mới |Đã nhìn Eq2.4/2.7, Thm1, Prop4–5; Fig4–6,Tables1–2/4; terminal paragraph §6 tr289 |
| lookup | RePEc exact P13 URL do lesson cung cấp; web open2calls | 1 | 0 mới |Metadata/abstract khớp; restricted label của RePEc không phủ nhận OA journal PDF tại CWI |
| lookup | arxiv1604.05231 abs/history + HTMLv1; web open/find Eq2.10,Prop3–4 | 1 version | 0 mới |Đối chiếu numbering và terminal discussion; không tải PDF arxiv, không coi version là paper mới |

Một unique primary paper, chỉ P13 thêm catalog9→10. Không keyword/backward/
forward queries, không mở lại18nguồn archive, không chạm candidate snowball
chưa duyệt. S11/AoII và K-F levels kế thừa record PartA, không giả một lượt đọc mới.

**Sửa sau primary reading:** ΩT định nghĩa Eq2.7, không Eq3.5; terminal-horizon
explanation là journal§6/tr289 (arxiv§5.3). P13 finite-h optimizer domain μ≥0,
khác fixed stable μ của theorem. §5.1 in u3=3 trong M/M/1 example không khớp
central-moment definition (tính riêng được6); không dùng dòng đó để replication.
Không suy ON overload là global instability hoặc S1 tự quadratic trên finite support.

Dừng: đủ model/objective/statements/version/evidence/terminal paragraph và
đối chiếu cần cho PartB; không đọc proofs/appendices, không mở rộng literature.
Lookup không là audit/novelty clearance. [Metadata thao tác](../../results/lessons/l2_6/part_b/lookup_records.json),
[PDF hash/phạm vi](../../results/lessons/l2_6/part_b/source_access.json),
[report](../../results/lessons/l2_6/part_b/report.md). AI-T khác L-self; Gate còn mở.

## L2.7 Part A — 26/10/2026, lookup ba nguồn được chỉ định

[Thẻ trước lookup](../../results/lessons/l2_7/part_a/reading_card.md).
PC2/PC3/PC4/PC5: fidelity vs policy choice, comparator information và khả năng
nhận diện interaction. Chỉ P03/P07/P02; P12 thuộc PartB, không tải/đọc lượt này.

| Loại | Query / seed / tool / phạm vi | Thực sàng | Giữ unique | Kết quả / hạn chế |
|---|---|---:|---:|---|
| lookup | P03 exact PMLR amad26a + arxiv2606.25923 abs/history; web official open; paper-pilot inspect; pdftotext-layout | 1công trình,2versions đối chiếu metadata | 1, đã có R51 | PMLR27trang, AI-T §2–3/6.1–6.2/7.1 và appendix chọn lọc. Hai bản tải local qua context gián đoạn, cùng hash/cùng paper; không thêm P03 trùng R51 |
| lookup | P07 USENIX/perry + arxiv2303.00735v1; web official; inspect; pdftotext-layout | 1công trình | 1mới | NSDI PDF26trang gồmcover; AI-T §2.2–3.3/4.1–4.2. arxivv1 hiện có đúng tên DOTE: đính chính lesson về alias tên khác |
| lookup | P03/P07 targeted figure/formula check; paper-pilot render + view_image | 2công trình | 0mới | Nhìn P03 PDF3/7 Theorem/Fig4; P07 PDF4/9 Fig2/Fig3/oracle. Không full read hoặc replication |
| lookup | P02 DOI10.1016/j.trc.2023.104174, paper-search Crossref; web official portal abstract | 1công trình | 1mới | Title/authors/TR-C153:104174/2023 khớp; citations4/Crossref ngày26/10. AI-A official abstract; record có VoR20trang CC BY, không coi record là full text |
| lookup | `site.repository.tudelft.nl "Structure-free model-based predictive signal control"`; web search, exact-title known-item, không year filter | 3official records/paths của cùng paper | 0mới | Chỉ repository record, alternate repository PDF, research portal được sàng; không đếm toàn bộ search hits là paper đã sàng hoặc đọc |
| lookup | P02 file TU Delft do lesson đưa; web + inspect(pdf_url,doi) + curlHEAD25s | 1công trình | 0mới | Web Internal Error; observed inspect retry tools/call timeout300s; curl exit28/timeout25s. Earlier pre-resume attempt output không còn, không tự ghi thành công |
| lookup | P02 alternate repository file, Pure PDF, research portal PDF và publisher; web/inspect/curl | 1công trình | 0mới | Timeout/403; full text chưa đọc. DOI-only inspect/Unpaywall: No PDF URL available. API/islandora alternate URLs cũng inaccessible |
| lookup | P02 paper-search download_with_fallback, sourceCrossref, **use_scihub=false** | 1requested paper; không tự sàng3tool candidates | 0mới | Download failed; tool báo3candidate PDFs không khớp, Unpaywall không có OA URL hoặc thiếu email. Không dùng chúng làm evidence, không suy paper không OA |

**Số không trùng:**3nguồn được chỉ định,1đã có +2thêm catalog10→12;2AI-T,
1AI-A/BLOCKED. Không keyword field survey, backward/forward hay snowball.
Dừng: P03/P07 trả lời đủ câu hỏi targeted; P02 official/OA routes thất bại sau
các attempt đã lưu, không mở rộng literature hoặc lặp tải vô hạn. Full §2–4
và figures P02 còn dependency mở của PartA; không tuyên bố PartA hoàn tất hết,
không cấp novelty clearance. [Access/errors/hashes](../../results/lessons/l2_7/part_a/source_access.json),
[metadata](../../results/lessons/l2_7/part_a/source_metadata.json),
[report](../../results/lessons/l2_7/part_a/report.md).

## L2.7 Part B —26/10/2026, VE/AVE/OεRE

[Thẻ phạm vi](../../results/lessons/l2_7/part_b/reading_card.md) lưu sau metadata
lookup ban đầu, trước primary full text; không giả một pre-reading prediction.
Câu hỏi PC5/PC3: OεRE có cùng estimand/quantifiers với VE/AVE không? P12/R43 là
hai named sources tác giả yêu cầu; không mở lại reading list/archive.

| Loại | Query/seed, tool, filters | Thực sàng | Giữ unique | Kết quả/hạn chế |
|---|---|---:|---:|---|
| lookup | P12 NeurIPS2020 exact URL + arxiv2011.03506 abs/history; web official open/click | 1work/2metadata versions | 1, placeholder trước đây | NeurIPS33; arxivv1 nộp06/11/2020, có comment NeurIPS-2020 (đính chính lesson). Bibtex link Internal Error, không tự xác nhận page range5541–5552 |
| lookup | P12 official NeurIPS PDF; paper-pilot inspect, pdftotext-layout, render/view PDF3 | 1work | 0mới | Đọc AI-T §2/Eq2,§3/Def1–2,§3.1/Properties1–4 PDF2–3/đầu4; nhìn Definition1/Fig1.12trang đầy đủ downloaded, không full reading/proofs/experiments |
| lookup | R43 NeurIPS2022 exact URL, web official abstract | 1work | 1, đã có archived note | AI-A lượt này, DOI10.52202/068431-2393 hiển thị trên page; không tải PDF. Đã kiểm archived note AI-T24/10 và hash, không giả primary đọc lại hoặc R43 chỉ từng đọc abstract |
| lookup | `site.sas.com TOST alpha 0.05 90 confidence interval equivalence`; web search +2official SAS guide URLs | 1doc topic,2SAS links selected | 0paper | Official snippets có100(1−2α)% CI criterion; cả2full-page open timeout. Không coi toàn hits tìm kiếm là nguồn đã đọc |
| lookup | TOSTER author docs tại official CRAN vignette, web open và same-page anchor | 1doc | 0paper | Đọc selected Introduction/ViewingResults/DescribingResults: NHST vs TOST,α.05,90%CI; không chạy package/test trên data. Dùng làm documentation, không thêm reading list |
| keyword | `"decision equivalence" OR "regret equivalence" approximate model "information structure" OR "partial observability" model sufficiency for decisions`; web default relevance, không year/domain filter | **12result titles**, không phải12papers | 0 | Nhiều index/aggregation/person/download pages, query dài/Boolean cho dữ liệu nhiễu. Chỉ screen titles, không giữ paper mới, không tuyên bố loại paper bằng full text |

[12titles/URLs thực trả](../../results/lessons/l2_7/part_b/keyword_screen.json),
[primary versions/access/hash và archived R43 provenance](../../results/lessons/l2_7/part_b/source_access.json).
P12/R43=2unique named works, chỉ P12 thêm current catalog12→13. Tối đa1PDFmới,
không citations counts mới, không backwards/forward queries. P02 PartA không
được truy cập lại và vẫn full-text BLOCKED. Metadata held-out chỉ dùng membership,
không đánh giá outcomes hoặc dùng calibration/λA riêng làm model inputs.

Dừng: đủ targeted Def1/properties/crosswalk cho PartB; keyword đúng1limited
query theo lesson, **không đạt2queries×20 và không là A3/A4 audit**. Không chép
“9titles” từ hướng dẫn, không inference “chưa ai làm”. Một log keyword nhiễu
không cấp novelty clearance; L2.8/A4/L2.9 còn mở.

## L2.8 Part1 —26/10/2026, A4 bounded audit

[4session cards](audit_sessions.md) gắn PC3/PC4/PC5, trước rerun. Chỉ A4 chạy
ở Part1; A1–A3 và primary deep reading thuộc bước tiếp theo/Part2.

| Loại | Query/seed/tool/filter | Sàng thực | Giữ / hạn chế |
|---|---|---:|---|
| keyword | `certainty equivalence value of information negative value reoptimization`; paper-search sourcegoogle_scholar,max20,no year filter | 20titles+provider excerpts |0proposal;2hit unclear (ranks12/17), không full-text exclusions |
| keyword | `deterministic linear programming resolving revenue management information`; cùng provider,max20,no year filter |15titles+excerpts |1new Tier2 proposal; provider chỉ trả15, không giả20 |
| forward | R02 DOI10.1287/opre.50.4.720.2855; scholar-search SemanticScholar,limit20,offset0 |20titles/provider abstract excerpts |3Tier2 proposals,1đã có trong query2. next20,totalunknown.2calls cùng first page để lưu sau output quá lớn, chỉ20records được đếm |
| lookup | R01/R02/R04 exactDOIs; Crossref + Springer/INFORMS official abstracts |3unique works |AI-A primary abstracts lượt này. R01/R04 archived AI-T24/10 được đọc để kiểm provenance, không fresh full text/L-self |
| lookup | DOI10.1287/moor.2025.0898 Crossref + publisher; arxiv2308.13166/2211.01961 official abs |3proposed works |Metadata/abstract screen, không PDFs/notes/workbook rows. Online2026 cho DOI chứa2025; arxiv2211versionv2May2024 |

55screen records không là55unique/full reads. [CSV từng rank/quyết định](../../results/lessons/l2_8/part1/screening.csv),
[provider records](../../results/lessons/l2_8/part1/search_records.json),
[archived primary-reading provenance](../../results/lessons/l2_8/part1/archive_provenance.json).
Ba proposals Tier2, lý do/PC/officialIDs ở [bài Part1](literature_audit_part1.md);
chờ tác giả duyệt trước download/note, không đề xuất thêm ở đợt này.

Dừng theo Part1 scope/budget pass, **không đạt2×20 zero-new-candidate rule**:
query2chỉ15, còn candidates và forwardcontinuation. Không dùng sample counts
10/10/25/34 của tài liệu làm dữ liệu thực. Chưa xác nhận boundary/Γsameestimand
ở sources đã screen; lookupabstract không là four-session audit hoặc novelty
clearance. Full conditions/mapping của R01/R02/R04 còn mở trước L2.9.

## L2.8 Part2 —26/10/2026, primary targeted và bounded A1–A3

[Thẻ/câu hỏi PC3–PC5](audit_sessions.md), [forecast AI/exposed trước tìm](../../results/lessons/l2_8/part2/reading_card.md).
PDF local/metadata kiểm trước; R01/R02/R04 do lesson chỉ định. Sau sàng,
tác giả trả lời **“Duyệt cả3”** cho NDT26/WM26/AIS22, rồi mới tải/viết note.
[Approval](../../results/lessons/l2_8/part2/author_approval.json).

Bảng dưới là call-level checkpoints thực chạy, không payload từng rank. Các
response trước resume không còn raw records trong working context; không
fabricate169rows, không xác nhận rank-level reproducibility hoặc tổng unique
candidate. Failed calls không là zero-result searches; fallback chưa screen
không được tính vào169screen events. Mặc định max20, không year filter; query
order/relevance của provider, forward filters/continuation như limitation.

| Loại/call | Query/seed | Tool/provider | Trả / sàng | Chọn đọc mới / hạn chế |
|---|---|---|---:|---|
| keyword / A1_q1 | `routing state information model approximation interaction` | paper-search/Google Scholar | 20 / 20 | success; ; Mostly non-network routing/quantum/ML; two uncertain network titles, no complete abstract exclusions. |
| keyword / A1_q2 | `network digital twin state fidelity model fidelity decision regret` | paper-search/Google Scholar | 19 / 19 | success; NDT26; Provider reported20;19unique records returned. Existing DT² also found; not20screened. |
| keyword / A2_q1 | `age of information model mismatch value of information` | paper-search/Google Scholar | 20 / 20 | success; ; Poor query: ages/brain/education/cancer; not an informative AoI negative search. |
| keyword / A2_q2 | `fresh state information approximate model control performance` | paper-search/Google Scholar | 0 / 0 | timeout; no result; ;  |
| keyword / A3_q1 | `decision focused model partial observability model sufficiency` | paper-search/Google Scholar | 0 / 0 | timeout; no result; ;  |
| keyword / A3_q2 | `approximate value equivalence information structure decision regret` | paper-search/Google Scholar | 0 / 0 | timeout; no result; ;  |
| keyword / A4_repeat | `deterministic linear programming resolving revenue management information` | paper-search/Google Scholar | 0 / 0 | timeout; no result; ;  |
| keyword / A2_q2_fallback | `fresh state information approximate model control performance` | paper-search/OpenAlex | 20 / 0 | success; ; Retrieved but not screened; superseded by successful Scholar VPN retry |
| keyword / A3_q1_fallback | `decision focused model partial observability model sufficiency` | paper-search/OpenAlex | 20 / 20 | success; ; Used instead of repeatedly failed Scholar query |
| keyword / A3_q2_fallback | `approximate value equivalence information structure decision regret` | paper-search/OpenAlex | 20 / 0 | success; ; Retrieved but not screened; superseded by successful Scholar VPN retry |
| keyword / A4_repeat_fallback | `deterministic linear programming resolving revenue management information` | paper-search/OpenAlex | 20 / 0 | success; ; Retrieved but not screened; superseded by successful Scholar VPN retry |
| keyword / A2_q2_vpn_retry | `fresh state information approximate model control performance` | paper-search/Google Scholar | 20 / 20 | success after VPN retry; AIS22; AIS22 selected; other approximate-info-state hits remain screen/unclear |
| keyword / A3_q1_vpn_retry | `decision focused model partial observability model sufficiency` | paper-search/Google Scholar | 0 / 0 | timeout again; ; OpenAlex fallback used; no Scholar coverage for this variant |
| keyword / A3_q2_vpn_retry | `approximate value equivalence information structure decision regret` | paper-search/Google Scholar | 20 / 20 | success after VPN retry; ; R45/NeurIPS2022 official abstract screened; existing archived seed, not one of new3PDF approvals |
| keyword / A4_repeat_vpn_retry | `deterministic linear programming resolving revenue management information` | paper-search/Google Scholar | 20 / 20 | success after VPN retry; ; R01/Jasin-Kumar/RM family rediscovered; result-type replication, not exact ranking |
| forward / A1_forward | `10.1109/90.917073` | paper-search/OpenAlex | 5 / 5 | success; ; title.search:model; most cited first;1page,max4requests,timeout30s; provider says complete within this narrow filter; not prediction/digital-twin union. Possible duplicate title. |
| forward / A2_forward | `ARXIV:2504.19507` | scholar-search/Semantic Scholar | 0 / 0 | 429; ; API rate limit, not zero citations |
| forward / A2_forward_vpn_retry | `ARXIV:2504.19507` | scholar-search/Semantic Scholar | 0 / 0 | 429 again; ; VPN did not resolve remote rate limit |
| forward / A2_forward_fallback | `10.1109/TIT.2026.3663678` | paper-search/OpenAlex | 5 / 5 | success; ; Journal DOI seed instead of arxiv record; provider says5available; title/excerpt screen, two missing abstracts remain unclear. |
| forward / A3_forward | `ARXIV:2011.03506` | scholar-search/Semantic Scholar | 20 / 20 | success; WM26; First page only,next20; not exhausted. Unverified other recent IDs are screen-only, not accepted official records. |

**Selected-new unique=3:** NDT26/AIS22/WM26, đã duyệt/primary AI-T; không phải
tổng candidate count hoặc3Tier1. R45 NeurIPS2022 và arxiv2605.01694 chỉ official
abstract screen, không PDF/note; các ID khác chưa kiểm official giữ Unclear.
R01 xuất hiện lại trong A4repeat, đủ loại kết quả RM, không chứng minh same ranks.
169screen events=A1 44+A2 45+A3 60+A4repeat20, không cộng55Part1 thành lần đọc mới.

| Lookup/read | Kết quả thực | Hạn chế |
|---|---|---|
| R01 DOI official Springer + DOI-only OA + localTR | Journal metadata2010/online2009; TR2006 AI-T Prop1/PDF10–11,selected§1–4/6–7 | DOI-only không có PDFURL; journal numbering chưa kiểm |
| R04 official INFORMS + archived local PDF | Primary journal AI-T Def2–5/Props1–3/PDF8–10,selectedapplications; không download lại | Diagnostic chưa thành H1; không full paper |
| R02 publisher/CiteSeerX/DOI-onlyOA, VPN retry | Publisher403; CiteSeerXretry PDF8pages thành công; §5/Example1/PDF7 AI-T | Initial timeout/Wayback429, OAlookup khôngPDFURL; không tuyên bố mọi route hết truy cập |
| NDT26/WM26/AIS22 official abs/history + PDF sau duyệt | 3correct full PDFs đã tải, current hashes/pages; chỉ targeted reading | NDT26/WM26 preprints, không full reads/authorL-self; chưa chạy paper code |

Dừng theo bounded scope/budget và đủ targeted answer, **không đạt saturation**;
A1q2chỉ19, A2q1nhiễu, A3q1timeout cảretry, S11S2forward429 còn, A3forwardnext20.
NDT/networking ưu tiên; ngoài ngành chỉ3namedRM và2approvedmethod sources theo
PC cụ thể, không mở rộng thêm references vì cùng từ khóa. Three old Part1proposals
vẫn chưa duyệt, không tải. [Sourceaccess/hashes](../../results/lessons/l2_8/part2/source_access.json),
[primary crosswalk/region conclusions](literature_audit_part2.md). Không đổi nhãn PC/Gate.

## L2.8 follow-up — 26/10/2026 (11:24–12:12Z), phiên mới có raw response

Doan Van Tai phụ trách; AI chạy theo yêu cầu tác giả. **Không** chạy lại, sửa hay
tái dựng 169 events Part2 ở trên. Thẻ phiên viết trước call:
[session_card](../../results/lessons/l2_8/followup/session_card.md). Mỗi call lưu body
HTTP nguyên vẹn + sha256 + giờ UTC ngay sau khi gọi
([script](../../experiments/lessons/l2_8_followup_search.py),
[calls.jsonl](../../results/lessons/l2_8/followup/calls.jsonl)); quyết định từng rank ở
[screen/*.csv](../../results/lessons/l2_8/followup/screen/). ~15 request probe chỉ để
xem số đếm/ID neo, không sàng, không tính.

| Loại / call | Query / seed | Tool, bộ lọc, thứ tự | Đã sàng | Giữ unique mới | Lý do / hạn chế |
|---|---|---|---:|---:|---|
| keyword / FU_A1_v1 | `"stale" state "model mismatch" routing` | OpenAlex `search=` (gồm full text), relevance | 20 (tổng 77) | 0 | Nhiễu: 2/20 thuộc mạng; không là negative search có thông tin |
| keyword / FU_A1_v2 | `network digital twin what-if accuracy routing decision` | S2 `/paper/search` | 0 | 0 | 429 ×3, không phải zero hits |
| keyword / FU_A1_v2_oa | `network digital twin what-if decision` | OpenAlex title+abstract, relevance | 20 (269) | 1 T2 | NMF CoNEXT'25 SW; 1 known = snowball 2505.04879 |
| forward / FU_A1_fwd | P04 `W2111010037` | OpenAlex `cites:`, publication_date desc | 20 (166) | 1 T2 | Levin HotSDN 2012; record citing mới nhất trong OpenAlex là 2022 |
| keyword / FU_A2_v1 | `age of information model mismatch decision` | S2 search | 0 | 0 | 429 ×2 |
| keyword / FU_A2_v1_oa | `age of information model mismatch` | OpenAlex title+abstract | 20 (1020) | 0 | **Nhiễu 20/20** (tách "age of information"), lặp lỗi A2_q1 Part2 |
| keyword / FU_A2_v1b_oa | `"age of information" model mismatch` | OpenAlex title+abstract | 7 (7) | 0 | <20, chưa đạt luật 20 |
| keyword / FU_A2_v2 | `"age of information" "certainty equivalence"` | OpenAlex `search=` | 20 (24) | 0 | 1 known (2403.11926 ~ R32); CE trong NCS phần lớn nghĩa #2 |
| forward / FU_A2_fwd | S11 `ARXIV:2504.19507` | S2 citations | 1 | 0 | Thành công lần này; record duy nhất = bản journal của chính S11 |
| forward / FU_A2_fwd_journal | S11 `DOI:10.1109/TIT.2026.3663678` | S2 citations | 9 (9) | 1 T2 | attempt1 429, attempt2 OK; arXiv2609.06351 |
| keyword / FU_A3_v1 | `"decision-focused" network "traffic engineering"` | OpenAlex `search=` | 20 (22) | 1 T2 | CENTILE 2608.01725 |
| keyword / FU_A3_v2 | `"decision-aware" "digital twin"` | OpenAlex `search=` | 20 (71) | 0 | 20/20 ngoài mạng |
| forward / A3 (P07) | DOTE | OpenAlex title, S2 search, MCP scholar-search | 0 | 0 | **Không chạy được**: OpenAlex 0, S2 429 ×3, MCP trả 3 bài khác ([mcp_calls](../../results/lessons/l2_8/followup/mcp_calls.json)) |
| lookup | R06 + 6 đề xuất chờ duyệt + 3 đề xuất mới | arXiv API, Crossref DOI/title | 11 records | — | Không tải PDF; [bảng sàng](../../results/lessons/l2_8/followup/proposals_screen.md) |

**Tổng 157 record sàng** (A1 60, A2 57, A3 40): 4 candidate_T2 mới, 3 known, 1 trùng
trong phiên, 55 T3 context, 5 unclear (thiếu abstract), 89 exclude. **Không Tier1.**
Luật dừng 2×20 **không đạt ở vùng nào**: A1/A3 có candidate mới ở v2/v1, A2 có
query nhiễu và lượt <20; không saturation, không chứng minh bao phủ.
Đề xuất tối đa 3: arXiv2609.06351, 10.1145/3769700.3771695, arXiv2608.01725;
Levin HotSDN 2012 defer. Chờ tác giả duyệt trước PDF/note; không thêm Excel.

## Đợt đọc được duyệt — 26/10/2026 (sau L2.9)

Tác giả duyệt và tự tải PDF ([quyết định](../../results/lessons/l2_8/approved_batch/author_approval.json)).
Không chạy query mới; đây là `lookup`/đọc nguồn có tên, không tính là khảo sát lĩnh vực.

| Loại | Nguồn | Bản | Đọc | Kết quả / giới hạn |
|---|---|---|---|---|
| lookup+read | IA26 | arXiv 2609.06351v1, 44tr | AI-T §1–2.3, §3.4 | Môi trường ngoại sinh, loại trừ controlled queueing; regret so thông tin hiện tại đầy đủ |
| lookup+read | DTS25 | CoNEXT'25 SW, 2tr | AI-F | Bài ý tưởng, chưa thí nghiệm |
| lookup+read | CEN26 | arXiv 2608.01725v1, 11tr | AI-T §I, §III-D, §IV-A/D | Replay quyết định, reference hindsight |
| lookup+read | CEH23 | arXiv 2308.13166v1, 69tr | AI-T §2, §5.1, §6.1–6.3, §8 | Cận CE ∝ √var/var cần động học affine; re-solving không luôn có lợi (trích R02/R04) |
| lookup | R06, 2211.01961v2, 2605.24318v1, 2505.04879, 2601.23051v1 | PDF tác giả tải | không đọc thêm | Giữ mức hiện có theo quyết định tác giả |
| lookup | MOR 2025.0898 | — | — | Không có PDF; để sau |

Không thêm nguồn ngoài danh sách đã duyệt; không đạt/không tuyên bố saturation.

## Đối chiếu bản chính thức — 26/10/2026 (tối)

| Loại | Nguồn | File tác giả tải | Kết quả |
|---|---|---|---|
| lookup | S11 journal | IEEE TIT 72(4) tr2237, 40tr | Đúng bản; số mục khớp arXiv v3 |
| lookup | R01 journal | eCommons "6-2010", 29tr | **Không phải journal**: bìa kho + TR 2006 trùng nội dung; cần bản Springer |
| lookup | R34 | CDC 1992, 2tr scan | **Không phải TAC 1995**; đọc 2 trang làm prior tạm; cần bản TAC |

## L3.5 A04 — targeted post-discovery,27/10/2026

Người phụ trách:Doan Van Tai; skill paper-research. Thẻ trước call:
[session_card](../../results/lessons/l3_5/literature/session_card.md).
Câu hỏi PC5/PC3/PC4: quyết định đổi/gain nhỏ và threshold geometry có prior nào,
không dùng search để sửa card. Kiểm23catalog records trước; score đã commit7005a3b.

| Loại | Query/seed | Tool/filter | Đã sàng | Giữ unique mới | Hạn chế |
|---|---|---|---:|---:|---|
| keyword | `"network digital twin" "decision" "model accuracy"` | paper-search/search_papers GoogleScholar,10,relevance,no year filter |10title/snippet|1proposal|1known=P10; contexts/defer ghi từng rank|
| keyword | `routing "decision-focused" prediction error` | như trên |10title/snippet|0proposal|nhiễu vehicle/logistics/flood/medical;1concept abstract check, không negative field evidence|
| lookup | target Tao/Xu/You exact title | web search12links, arXiv2511.19961v2, Crossref exact-title1record |1targetwork|—|IEEEpageblocked; rawweblookupphụ không archive; không tính12links thành12papers|
| lookup | DOI10.1109/MWC.2026.3715457 | Crossref DOI |1metadata|0|secondary DOI sai: là PhotonicADC; bỏ, không gán cho target|
| lookup | 2606.21773v1 | official arXiv abstract |1known-from-query|0proposal|conceptual outside-domain; khôngPDF/fulltext/newnote|

Tổng keyword20records;1proposal mới Tao/Xu/You, **DOI đúng10.1109/MWC.2026.3712294**,
Crossref IEEEWirelessCommunications33(5):20–26,2026-10-01; arXivv2 abstract-only.
Chờ duyệt trướcPDF/note mới, không thêmExcel/catalog/authorprogress. Không hỏi duyệt
để làm chặn A04 vì metadata screen đã đủ phạm vi hiện tại. Không đổi PC/Gate/novelty.
[20 quyết định](../../results/lessons/l3_5/literature/screen.csv),
[tóm tắt/giới hạn](../../results/lessons/l3_5/literature/screening_summary.md),
[raw+hash](../../results/lessons/l3_5/literature/raw_hashes.json).
Dừng sau2queriesbounded, trước6phút; không2×20/saturation.0download,0newpaper-note.


## L3R.4-R1 — realism metadata lookup,29/10/2026

[Thẻ](../../results/lessons/l3r_4/literature/session_card.md): Q3R.3/K9/SR5–SR6,
không đổiPC1–PC6. Kiểm23catalog vàT00/EV/DL008 trước. Hai contextcũ giữnguyên.

|Loại|Query/tool|Số thực sàng|Giữ unique mới|Giới hạn|
|---|---|---:|---:|---|
|lookup|3exact-title queries qua paper-search/search_dblp,max3/title|0|0|Cả3trảempty,noerror; không coi lànegativeevidence|
|lookup|3exact-title queries qua search_crossref,max3,relevance|9title/metadata|3proposals|BAM10/ZLK17/LTWW94 đúngDOI/venue theoCrossref;6records khác bịloại|
|lookup verification|3publisher-domain webqueries theoDOI/title|0|0|Khôngsearchresults; khôngđọcPDF/abstract mới|

[Metadata/proposals](../../results/lessons/l3r_4/literature/proposals.md),raw từngtool
call có trong cùngfolder. Citationcounts trảvềkhông dùngchoquyếtđịnh. Dừng targeted
lookupbudget, khôngsurvey hoặc2×20.3PDF/newnotes **chờ tác giả duyệt**;0download.


### L3R.4-R1 — tác giả duyệt3nguồn và đọc targeted (29/10/2026)

Tác giả trả lời nguyên văn “Duyệt cả 3 (khuyến nghị)” trước PDF/content notes.
3nguồn mới giữ,0nguồn ngoài ngành thêm. BAM10: MSR request timeout2lần; guessed
UWimc10.pdf404; paper-pilot lấy đúng MSR PDF14trang, copy ngoàiGit. ZLK17 author
PDF8trang và LTWW94SFU journal15trang tải được. StanfordLeland là conference1993,
không dùng thay journal1994. PublisherACM403/unavailable,IEEErobotcheck; identity
Crossref+headers/officialinstitution/authorpages, không nhận publisher full-read.
Weblookup/MSR/UW là targeted access, không broadsearch/snowball. Các bước thất bại
local: command `python` không có; `.venv` không córequests; dùngurllibstdlib,
không thay dependencies. PDF3lưu ngoàiGit; raw metadata/download errors lưu
results/lessons/l3r_4/literature/. Mức AI-T,author levels không đổi.
BAM10§3.1/5.2/6.2–6.3; ZLK17§4/5/6.4; LTWW94TableI/§3.1/4/5.2.
Có evidence về variability/measurement mismatch; chưa có joint numeric envelope
cho backlogAoI/holdh/CV4windows/offeredinput/buffer. Không gán range từ abstract
hoặc plot pixel. Dừng đúng boundedround3nguồn đã duyệt; không đạt2×20, không
claim saturation/novelty/PC hoặc author đã đọc. Catalog23→26; giữ23oldrows.
