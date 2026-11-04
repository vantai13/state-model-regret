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


## L4.5 — local-note review, không online search (30/10/2026)

Người phụ trách **Doan Van Tai**; skill paper-research. Q: prior boundary cho
SV/PC6 wording và SUB/PC3, trạng thái author attestation nào hiện có? Đọc protocol,
claims/library index/log trước; review targeted7note files +1author_attestation,
không primary PDF. Không có lookup/keyword/backward/forward/author-venue query mới.
Onlinequeries0/searchrecords0/newuniques0/proposals0/downloads0/newprimaryreads0.
PC3 đãauthor-attested DL043; K-S9/K-F1 giới hạn câu vềfreshness; noteWM26§5/F.1
vàđínhchính§8/PDF9 giữscope. Không đổiExcel/catalog/PC/authorprogress hoặc novelty.
Dừng đủscope note-level, khôngsaturation/field absence. [Record/giới hạn](../../results/lessons/l4_5/literature_review.md).


## L4.8-R1 — existing-source lookup và primary reread,31/10/2026

Người phụ trách **Doan Van Tai**; skillpaper-research. [Thẻ/Q/PC và stop](../../results/lessons/l4_8_v2/literature/session_card.md).
Đãkiểmcatalog26,claims,log,T00,worksheetv1/approvalL3R.4 trướcqueries. Q:
evidence có đủjointmapping choDCaggregate-routing/backlogage/holdh/inputlaw
hay chỉmotivation? KhôngđổiPC/novelty/gatehoặcauthorreadingprogress.

|Loại|Query/source|Thực sàng/đọc|Giữunique mới|Kết quả/giới hạn|
|---|---|---|---:|---|
|lookup|Crossref exactDOI10.1145/3131365.3131375|1metadata|0|ZLK17đúngtitle/authors/IMC2017; nguồn cũ |
|lookup|Crossref exactDOI10.1145/1879141.1879175|1metadata|0|BAM10đúngtitle/authors/IMC2010; nguồn cũ |
|lookup|Crossref exactDOI10.1109/MCOM.001.2200012|1metadata|0|NDT1journalidentity60(11):22–27; bản đọcacceptedarxivv2 giữ riêng |
|targeted reread|paper-pilot/get_pdf_page_text trên3PDFlocalSHAkhớpcatalog|3calls/15PDFpages:ZLK1/3/4/5/7,BAM1/3/6/7/9,NDT1/2/4/5/6|0|AI-T,khôngfullread. XemảnhZLKTable2/PDF4,BAMTable4/PDF7,NDTFig4/PDF5 |

Onlinequeries3;metadatarecords3;existinguniques3;newuniques0/newproposals0/
downloads0.0keyword/backward/forward/author-venuequeries,khôngfieldcoverage
hoặcsaturation. Cácnguồnđãđượcduyệt từtrước nênkhôngyêucầuduyệtlại.0lỗi
tool/access tronglượt này. T00 lànote-levelreview,khôngrereadprimaryPlanck/
Hedera/Kuźniar. Không gán throughput/peakbuffer/hotduration thànhofferedinput/
instantbacklog/meanmode hoặcτ; NDT1syntheticrouting khôngempiricalvalidation.
10Gb/sserver-ToR khôngtựthànhcặpuplinkalternatives40/100Gb/s. Thiếujoint
numericdomainvẫngiữUNRESOLVED,khôngIN/OUTgiả. Dừngbounded3nguồncũ; không
tìmvôhạnđểépPASS. KhôngđổiExcel/catalog26/authorlevels/envelopev1.
[Access/reading record vàrawmetadata](../../results/lessons/l4_8_v2/literature/review.json),
[source review/claim boundary](../realism/L4_8_source_review.md).

## 31/10/2026 — L4.9, local-note review only

Đối chiếu local P13 note đã có để tránh gán expansion của Markov routing
thành theorem Lévy của paper; không mở primary PDF/metadata/web mới trong
lượt này.0queries/0records screened/0new sources/0downloads, không lookup
hoặc field coverage; catalog/Excel/author levels giữ nguyên. T09 ghi rõ các
stability/moment/conditional-state dependencies chưa chứng minh. Dừng ở
claim boundary đủ dùng cho finite-panel freeze; không claim primary reread,
paper replication hoặc novelty. [T09](../theory/T09_stationary_dominance_limits.md).


## L5.3 — closest prior: 3 existing-source lookups, targeted reread (02/11/2026)

Người phụ trách **Doan Van Tai**; skill [paper-research](/home/vantai/.codex/skills/paper-research/SKILL.md).
Q/MainRQ-PC3/PC4 boundary: P13 đã ngụ ý hướng state/transient và dạng1/h tới
đâu; M00/P04 làm hẹp câu về state/model routing thế nào? Giữ nếu đối chiếu
estimand/mechanism/regime ảnh hưởng claim; không dùng khác giả định tạo novelty.
Đã đọc protocol, claims, library index/catalog và log trước thao tác. Tác giả
yêu cầu thực hiện L5.3 với đúng3nguồn hiện có, không cần đề xuất/duyệt mới.

| Loại | Query/source thật | Tool/bộ lọc | Thực sàng/đọc | Giữ unique mới | Kết quả/giới hạn |
|---|---|---|---|---:|---|
| lookup | 10.1007/s11134-016-9511-0 | paper-search/get_crossref_paper_by_doi, exact DOI | 1metadata | 0 | P13 Mathijsen/Zwart2017, QueueingSystems85:269–304; nguồn cũ |
| lookup | 10.1109/71.824633 | cùng tool, exact DOI | 1metadata | 0 | M00 IEEE TPDS11(1):6–20; bản đọc submission riêng |
| lookup | 10.1109/90.917073 | cùng tool, exact DOI | 1metadata | 0 | P04 ToN9(2):162–176; nguồn cũ |
| targeted reread | 3PDF local, SHA khớp catalog | paper-pilot/get_pdf_page_text,4calls | P13PDF4/7/8/14; M00PDF10/12; P04PDF5/7/9 =9pages | 0 | AI-T; không full-read/proofs, không render/numeric digitization |

P13Eq2.4/2.7/tr275,Thm1/tr276,Prop4–5/tr282: normalized-vs-cumulative loss,
không transfer Lévy theorem sang correlated binary routing. M00§3.4 herding
text đủqualitativeclaim; extraction có legacy font/line artifacts, không lấy
số liệu plot. P04§III-A/B tr166/168/170: timescale/traffic/topology matters,
không đồng nhất holding time vớiκ. Đối chiếu thêm5notes P13/M00/P04/T09/
horizon_transient và targeted searches trongalready_implied/prior_boundary.

3onlinequeries/3metadatarecords/3existinguniques;0keyword/backward/forward/
author-venuequeries,0newunique/proposals/downloads/notes. 4PDFcalls/9pages;
0access/tool failures, extractionM00 hạn chế như trên. Không cập nhật citations,
Excel/catalog/authorreadingprogress, không nhậnL-self. Không fieldcoverage,
saturation hoặc novelty. Dừng đủbounded3nguồn/tables choL5.3; không thêm
Puterman hoặcnguồnngoàingành. [Kết quả/claim boundary](../phases/PHASE_5_closeout.md#closest-prior-check-targeted-không-novelty-search).


## L6.1 — prior check giới hạn trước chọn câu hỏi (02/11/2026)

Người phụ trách **Doan Van Tai**; skill paper-research. Câu hỏi/MainRQ-PC3/4:
đã có nguồn gần cơ chế mean/fluid bỏ dài hạn khiến switching cost đổi dấu
value of state information hay chưa? Đọc thư viện/R02/V1/T09 trước; kiểm
metadata/abstract hai đề xuất Veatch2001 và Bozkurt2602.02814, thêm tối đa
một query networking switching-cost nếu cần. Giữ khi E/M/R ảnh hưởng câu
hỏi hoặc wording; không mở rộng chỉ vì cùng từ khóa. Ngân sách bounded
lookup hai nguồn, tối đa ba đề xuất, không broad survey; không dùng lượt
4queries của Claude thành thao tác local. Chưa duyệt PDF/note mới; lựa chọn
duyệt/hoãn/từ chối sẽ ghi DL129 trước native. Chi tiết kết quả nối cuối mục.


**Kết quả lượt L6.1 (bổ sung sau thao tác thật):**
- Note review5nguồn đã có: R02§5Example1 (theo noteAI-T), information_harm§1/3,
  already_implied L2.8 targeted text search, T09§1–3 và CEH23§2/5.1/6.1/8
  (theo noteAI-T). Không primary reread, không nâng author levels. CEH23 đã
  có trong26-source catalog, hỗ trợ wording uncertainty→nominal, assumptions
  affine/smooth khác reflected queue; không chuyển bounds sangplant.

| Loại/thao tác | Query/seed | Kết quả thực đọc/sàng | Giữ | Hạn chế/decision |
|---|---|---|---|---|
| lookup exact title | paper-search/search_crossref: `Fluid analysis of arrival routing Veatch`, max3 | 3metadata/title records,1đúng title | 1metadata candidate | Hai record khác lệch estimand hoặc ngoài ngành, không đi tiếp |
| lookup exact ID | web.open `https://arxiv.org/abs/2602.02814` | 1official metadata+abstract, v1 submitted02/02/2026 | 1abstract candidate | CE policy at state estimate theoabstract; không đọc§1/proofs hoặc suy bounds ápM0 |
| lookup title + author access | web.search `"Fluid analysis of arrival routing" Veatch switching cost`, domainsIEEE/Gordon/ResearchGate | 8returned entries,screenedtitles; chỉ official Gordon snippet dùng đối chiếu identity | 0newunique | RG/khácpaper không dùng làm evidence nội dung. Không có primary abstract của đúng Veatch qua lookup này |
| access attempt | web.open Gordon author page | 404,0page read | 0 | Lỗi access không là evidence không có prior |

Veatch: M.H.Veatch2001, *Fluid analysis of arrival routing*, IEEE TAC46(8):
1254–1257, DOI[10.1109/9.940928](https://doi.org/10.1109/9.940928),
**metadata-only**. Bozkurt/Mahajan/Nayyar/Ouyang: *Sub-optimality bounds for
certainty equivalent policies in partially observed systems*,
[arxiv2602.02814v1](https://arxiv.org/abs/2602.02814v1), **abstract-only**,
preprint; không gán peer-reviewed. Không lấy citations làm evidence/không
cập nhật counts vào catalog. Chưa xác nhận prior trùng E/M/R từ phạm vi này.

Tổng:3successful lookup/access paths +1failed access; 2search queries
(Crossref title +web title),2opens. 3+8+1=12record views,không12unique;
2candidateunique metadata/abstract giữ ởlog,0nguồn mới vào catalog.
0keyworddiscovery/forward/backward/author-venue rounds,0PDFdownload/
newcontentnotes/primarypagesread. Không nhận4queries củaClaude thànhlocal.
Không đạt2×20, khôngfieldcoverage/saturation/novelty. Một lỗi helper metadata
u0ZeroDivisionError được sửa bằng tách control u=0, không paper/tool failure.

**Lựa chọn theoủyquyền trongDL129:** khôngduyệt bổsung PDF/note ởL6.1;
Veatch ưu tiên nếu cần kiểm trướcclaimGateD, Bozkurt chưa cần vìCEH23đãcó,
đềxuất#3chưađịnhdanh khôngnhậnlàpaper. Dừngboundedmetadataround; priorcheck
hiện tại không xácnhậnnội dung switchingcost củaVeatch hoặcabsenceofprior.
Không hỏi author-reading/attestation để thay tácgiả;không thêm bài đọc bắtbuộc.


## L6.4 — prior check theo sáu nguồn được cung cấp (03/11/2026)

Người phụ trách: **Doan Van Tai**; skill paper-research. MainRQ/PC3/PC4/PC6:
information harm với approximate controller và phép tách decision value theo
action/stake có prior nào trong đúng sáu nguồn của lesson? Câu chặn: nếu
prior đã có harm hoặc action-based VOI thì không nhận các ý tổng quát đó
là contribution; không tự đổi PC/G-level. Kiểm catalog/log/notes R02/M00/
CEH23 và T09 trước; sáu URL mới chưa có trong catalog/log, không có PDF
local tương ứng với hai nguồn yêu cầu đọc. Đây là lookup, không khảo sát
lĩnh vực. Nguồn road-traffic không được gọi là computer-network routing.
Ngân sách: sáu exact sources, bounded follow-ups để kiểm version/access;
đọc targeted Galanis và Making Information More Valuable theo yêu cầu
trực tiếp, không cần duyệt lại. Bốn nguồn khác metadata/abstract trước;
không đề xuất nguồn thứ bảy, không mở keyword/backward/forward. Dừng khi
đã kiểm sáu identities và hai targeted reads, hoặc access bị chặn sau một
fallback hữu ích. Không cập nhật Excel/catalog/author levels. Kết quả thật,
số đếm, lỗi và mức đọc ghi tiếp sau thao tác; không chép “6 snippets đã
đọc” từ lesson thành lịch sử phiên này. Sáu web opens đầu đã thực hiện khi
ghi entry: City timeout, EconPapers inaccessible; bốn landing pages đọc được.

**Kết quả thao tác thực tế (không nhập số đếm từ lesson):**

| Loại | Query/seed, công cụ và bộ lọc | Đã xem/sàng | Giữ/giới hạn |
|---|---|---:|---|
| lookup URL | web.open City21336; arxiv2210.04418/1908.01633/2005.05191; ROSAPdot34297; EconPapersDP20906, không năm/ranking filter |6 opens:4 official metadata/abstracts,2 access failures |4 identities đọc được;2 chờ fallback, không coi là negative result |
| lookup title/access | web.search `Galanis 2015 value information unawareness 21336 city journal economic theory` (City/ScienceDirect/doi.org); `"Making Information More Valuable" Whitmeyer published` (arxiv/ScienceDirect/Wiley/markwhitmeyer); `"20906" Eilat Eliaz information` (CEPR/EconPapers) |17 displayed title entries trên3queries, không có per-query rank ledger |Galanis/MIV/CEPR là3 named identities, aliases/duplicate versions không đếm nguồn mới; related Galanis/khác title không đi tiếp |
| lookup DOI | paper-search/get_crossref_paper_by_doi `10.1016/j.jet.2015.01.015` |1 metadata record |JET157:384–396,May2015; không dùng citation count làm evidence |
| lookup fallback/primary | web.open arxiv HTML2210.04418v6,CEPRdp20906,Citycanonical/eprint21336;3 web.find `3.2`,`extensive`,`Intensive` trên cùng MIV;1 web.open lines248 |4 successful opens và3 find segments |Cùng3 identities, không7papers; xác nhận v6/§3.2 và hai fallback đọc được |
| OA download được yêu cầu | paper-pilot/inspect_open_access_pdf CityacceptedPDF và arxiv2210.04418v6 |2 PDFs,13/48 pages |2 nguồn AI-T, PDFs ngoài Git; không nâng author reading |
| targeted primary read | paper-pilot/get_pdf_page_text Galanis[4–9],MIV[6–9,14–16],Galanis[9] đọc lại |3 calls,14 page views/13 unique pages |Galanis§2/3.1–3.6,MIV Eq1/Def2.1–2.2/§3.2; không full-read/proof audit/figure reading |
| publication access | web.click arxiv2005.05191→dblp corr-page |1 access failure,0 page read |response>4MB; SIROCCO2020 chỉ identity theo arxiv comments, VoR chưa kiểm |
| lookup publication status | web.search `"Making Information More Valuable" Whitmeyer journal` (ScienceDirect/Wiley/markwhitmeyer/arxiv); `"Payoffs-Beliefs Duality and the Value of Information" journal` (ScienceDirect/Springer/arxiv/HAL) |14 displayed title entries trên2queries |2 đúng title là arxiv records đã có,12 lệch title không đọc tiếp; không tìm được VoR trong lượt này, không suy chưa xuất bản |

Tổng5 title/access queries (đều lookup, không keyword discovery),31 displayed
title-entry views, không31unique/abstract reads;10 web opens (8 được/2 lỗi),
3find và1click lỗi. Sáu named works dedup,2 AI-T/4 AI-A. Một Crossref metadata
lookup;2 OA downloads/3 PDF page calls như bảng. Đọc lại3 existing notes
R02/M00/CEH23, không primary reread hoặc nâng AI level của chúng.
3 access limitations: CityshortURL timeout,EconPapers inaccessible,dblp>4MB;
hai lỗi đầu có official fallback. pypdf local thiếu, pdftotext có sẵn dùng
định vị section, không cài dependency. Không gọi Scholar/forward/backward/
author-venue/discovery;0 nguồn tự đề xuất ngoài6,0 catalog/Excel/author-level
updates. PDF/page/sha/source claims và E/M/R ở [prior check](L6_4_prior_check.md).
Gao là road traffic, không làm computer-network prior. Dừng đủ bounded
sources/targeted reads; không2×20,saturation,coverage,novelty hoặcprior clearance.

## L7.3-R1 — realism use cases: library review + metadata lookup (03/11/2026)

Người phụ trách: **Doan Van Tai**; AI (Claude) theo ủy quyền L7.3 Phần 1; skill paper-research.

```text
THẺ TÌM KIẾM — L7.3-R1 / 03-11-2026
Câu hỏi: các bối cảnh routing thật (flowlet LB trong DC; TE/lập lịch flow DC ở thang giây; TE trên WAN;
  vòng what-if của NDT) có horizon h, tuổi telemetry τ, thang burst và tải nào, có nguồn?
PC / mục đích: realism / RQ3 (định vị use case), không đổi nhãn PC.
Câu chặn: nếu nguồn cho h, τ, T_mode cùng định nghĩa thì có thể gán vùng state/chuyển tiếp/tiệm cận của
  ctmc-v1; nếu không, ô giữ UNSOURCED, không suy OUT.
GIỮ nếu: nguồn networking đo hoặc mô tả chu kỳ quyết định, tuổi đo, thang burst/đa thang.
BỎ nếu: road traffic/vehicle routing, sai số KPI không có quyết định.
Điểm vào: thư viện hiện có (ZLK17, BAM10, NDT1, LTWW94, T00/worksheet v1); exact-title lookup cho
  SWAN, B4, CONGA, Roy2015.
Ngân sách: một buổi; tối đa 3 đề xuất mới; không tải/đọc trước khi tác giả duyệt.
Dừng khi: đủ lookup cho các ô UNSOURCED ưu tiên (chu kỳ TE WAN, flowlet LB, burst đa thang DC).
```

| Ngày | Loại | Thẻ / Q / PC | Query / seed | Tool, bộ lọc, thứ tự | Đã sàng | Giữ unique | Lý do / hạn chế / dừng |
|---|---|---|---|---|---:|---:|---|
| 03/11 | library | L7.3-R1 / realism | catalog + notes/literature/papers + notes/realism + T00 | grep local | 33 notes, 8 realism files | 4 dùng lại (ZLK17, BAM10, NDT1, LTWW94) + T00 (Planck/Hedera/MicroTE/Kuźniar ở mức note) | LTWW94 đã có từ L3R.4 (không phải nguồn mới); CONGA/SWAN/MicroTE/B4 không có trong catalog |
| 03/11 | lookup | L7.3-R1 | "SWAN achieving high utilization software-driven WAN"; "B4 experience globally-deployed software defined WAN"; "CONGA distributed congestion-aware load balancing datacenters"; "Inside the Social Network's Datacenter Network" | paper-search `search_dblp`, max 5 | 0 | 0 | Cả 4 trả rỗng: hạn chế công cụ (dblp), không phải bằng chứng không có bài |
| 03/11 | lookup | L7.3-R1 | cùng 4 exact titles | paper-search `search_crossref`, max 5, relevance | 20 | 4 | SWAN 10.1145/2486001.2486012 (SIGCOMM'13, tr.15–26; CCR 10.1145/2534169.2486012); B4 10.1145/2486001.2486019 (SIGCOMM'13, tr.3–14); CONGA 10.1145/2619239.2626316 (SIGCOMM'14, tr.503–514); Roy et al. 10.1145/2785956.2787472 (SIGCOMM'15, tr.123–137). Mức: metadata-only (+ abstract Crossref của bản CCR). 16 kết quả khác lệch chủ đề |

Đề xuất 3 nguồn (chờ tác giả duyệt; chưa tải, chưa note nội dung): SWAN, CONGA, Roy2015 — lý do ở
[realism_v2_draft.md](../realism/realism_v2_draft.md) §6. B4 giữ làm phương án thay SWAN, không đề xuất trong đợt
này. Đây là lookup theo tên, không phải khảo sát lĩnh vực; không 2×20, không saturation, không novelty.

### L7.3-R1 đợt 2 — duyệt theo ủy quyền, tải và đọc (03/11/2026)

Tác giả nhắn "bạn hãy tự làm tự chạy thực hiện cho tôi luôn đi" sau khi AI dừng ở bước "chờ duyệt 3 nguồn". AI hiểu tin
nhắn này là ủy quyền cho AI duyệt cả 3 đề xuất. Ghi nhận đây là duyệt **AI-delegated**: tác giả không tự sàng
abstract, và không có nguồn nào được ghi là tác giả đã đọc.

| Ngày | Loại | Thẻ / Q / PC | Query / seed | Tool, bộ lọc, thứ tự | Đã sàng | Giữ unique | Lý do / hạn chế / dừng |
|---|---|---|---|---|---:|---:|---|
| 03/11 | lookup (OA) | L7.3-R1 | 3 DOI: SWAN, CONGA, Roy2015 | paper-search `search_unpaywall` | 3 | 0 | Cả 3 trả `result: []` |
| 03/11 | lookup (OA) | L7.3-R1 | 3 DOI trên | paper-pilot `inspect_open_access_pdf` (doi) | 3 | 0 | SWAN và Roy2015 bị 403 ở dl.acm.org; CONGA: "No PDF URL available" |
| 03/11 | lookup | L7.3-R1 | 3 DOI trên | scholar-search `get_paper_details` | 3 | 2 | SWAN và Roy2015 khớp DOI/DBLP; CONGA bị 404 ở Semantic Scholar (lỗi công cụ, DOI đã kiểm qua Crossref ở đợt 1) |
| 03/11 | lookup (bản tác giả) | L7.3-R1 | 3 exact title + "pdf" (Roy2015 thêm "ucsd") | WebSearch | 3 truy vấn | 3 URL chọn | Chỉ chọn trang hội nghị hoặc trang tác giả: conferences.sigcomm.org/…/p15.pdf, people.csail.mit.edu/alizadeh/…/conga-sigcomm14.pdf, cseweb.ucsd.edu/~snoeren/…/fb-sigcomm15.pdf. Không dùng bản TR, bản khóa học hay mirror khác; không dùng thư viện lậu |
| 03/11 | download | L7.3-R1 | 3 URL trên | curl, lưu `~/papers/state-model-regret/l73/` | 3 | 3 | HTTP 200 application/pdf. Số trang 12/12/15 khớp tr. 15–26, 503–514, 123–137. sha256: 99bb9406a528…, b0a6e69eaa00…, d95df8228cb8… |
| 03/11 | read (AI-T) | L7.3-R1 / realism | HKM13, AED14, RZB15 | pdftotext, grep theo câu hỏi h/τ/burst/tải, rồi đọc đoạn quanh kết quả | 3 | 3 | Mục đã đọc ghi trong từng note. Đã sửa 3 trích sai sau khi đối chiếu text: CONGA "lớn hơn 500 KB", CONGA ~100 µs ở §1 chứ không phải §2.1, Roy2015 §4.1 bổ sung Hadoop 5× và chu kỳ ngày. Không đọc toàn văn |

Kết quả đợt 2:
- **Note tạo mới:** [HKM13](papers/HKM13.md), [AED14](papers/AED14.md), [RZB15](papers/RZB15.md).
- **Bản nháp:** [realism_v2_draft.md](../realism/realism_v2_draft.md) cập nhật §2–6.
- **Không đổi:** catalog và Excel trên `main`, mức đọc của tác giả, nhãn PC, envelope v1. B4 không dùng, vẫn
  metadata-only.
- **Phạm vi:** không backward/forward snowball, không 2×20, không saturation, không novelty.
- **Lý do dừng:** đã đủ để lấp các ô h/τ của (i) và (iii) và thêm bằng chứng đa thang cho (ii). Các ô còn UNSOURCED
  (f/T_slow, thời lượng flowlet, h/τ của NDT) cần nguồn khác. Theo giới hạn 3 nguồn mỗi đợt, đợt này không đề xuất thêm.

## L7.3-R2 — danh sách nguồn để tác giả tải (04/11/2026)

Người phụ trách: **Doan Van Tai**; AI (Claude) soạn. Tác giả nhắn: "bạn đưa tất cả tên bài báo mà bạn muốn tải đi tôi
sẽ tải và bạn kiểm tra tốt hơn". Đợt này chỉ tra metadata và sàng tiêu đề/abstract; chưa tải PDF, chưa tạo note.

```text
THẺ TÌM KIẾM — L7.3-R2 / 04-11-2026
Câu hỏi: nguồn nào lấp được các ô UNSOURCED của realism v2: f/T_slow (phương sai tải theo thang) cho DC và WAN,
  thời lượng flowlet, h/τ của vòng what-if NDT? Nguồn nào cho bản gốc của số đang trích gián tiếp (MicroTE)?
PC / mục đích: realism / RQ3; không đổi nhãn PC.
Câu chặn: nếu nguồn cho T_mode/f dưới 5 phút ở WAN hoặc f ở thang giây–phút ở DC thì nhãn (ii)/(iii) có thể đổi
  từ UNRESOLVED/không bền sang có điều kiện rõ hơn; nếu không, giữ nguyên.
GIỮ nếu: đo traffic DC/WAN theo nhiều thang thời gian, chu kỳ TE, flowlet, NDT có thời gian vòng.
BỎ nếu: road/urban traffic, dự báo traffic không có thang thời gian hay quyết định, digital twin ngoài mạng.
Ngân sách: một lượt; tối đa 3 đề xuất mới có ưu tiên, phần còn lại ghi dự phòng theo yêu cầu tác giả.
```

| Ngày | Loại | Thẻ / Q / PC | Query / seed | Tool, bộ lọc, thứ tự | Đã sàng | Giữ unique | Lý do / hạn chế / dừng |
|---|---|---|---|---|---:|---:|---|
| 04/11 | library | L7.3-R2 | P07 DOTE (đã có PDF) | grep text local | 1 | 1 | TE epoch "a few minutes", demand 5 phút, Appendix A về predictability (PDF3, 6, 9, 18). Chỉ AI grep, chưa note mới |
| 04/11 | backward | L7.3-R2 | references của RZB15 [12, 13, 14, 17, 26, 27] và AED14 [2, 8, 18, 28]; P07 [Roughan 2002] | pdftotext local | 11 | 4 | MicroTE (= RZB15 [14], AED14 [9]), Kandula IMC'09, Bullet Trains, Roughan IMW'02. Benson IMC'10 = BAM10 đã có; Hedera đã có trong T00; VL2, ECHO bỏ (không thang thời gian) |
| 04/11 | lookup | L7.3-R2 | MicroTE; Kandula'09; Ghabashneh'22; B4 and After; HULA; Planck; Kuźniar'18; Bullet Trains; Roughan'02 | paper-search `search_crossref`, max 3 | 24 | 9 | Mỗi bài 1 DOI khớp tiêu đề và tác giả. Planck và Roughan có 2 bản (conf + CCR; IMW + chương sách 2003), gộp thành 1 công trình mỗi bài |
| 04/11 | lookup | L7.3-R2 | 10.1145/1005686.1005697 | `get_crossref_paper_by_doi` | 1 | 1 | Lakhina et al., SIGMETRICS'04, tr. 61–72 |
| 04/11 | lookup | L7.3-R2 | LetFlow; Hedera (exact title) | paper-search `search_dblp` | 0 | 0 | Cả 2 rỗng: hạn chế công cụ |
| 04/11 | lookup | L7.3-R2 | LetFlow NSDI'17 | WebSearch | 9 | 1 | Trang USENIX chính thức, open access, tr. 407–420, không có DOI |
| 04/11 | keyword | L7.3-R2 | "datacenter traffic predictability timescales traffic engineering measurement"; "network digital twin what-if analysis routing optimization loop time" | paper-search `search_semantic` | 0 | 0 | Cả 2 lỗi HTTP 429 (rate limit) |
| 04/11 | keyword | L7.3-R2 | "data center traffic predictability timescale traffic engineering" | `search_openalex`, max 20, relevance | 20 | 1 | Lakhina'04 (phân rã OD flow thành trend chu kỳ, burst ngắn, nhiễu). 19 bài bỏ: road/air traffic, dự báo ML không có thang, anomaly |
| 04/11 | keyword | L7.3-R2 | "network digital twin what-if analysis routing" | `search_openalex`, max 20, relevance | 20 | 3 dự phòng | TwinNet (Comput. Netw. 2022), Polverini (NOMS'23), Aben-Athar (ICC Wksp'25). NDT1 trùng thư viện; còn lại ngoài mạng hoặc survey. Abstract không nêu h, τ |

Kết quả:
- **Đề xuất ưu tiên (3):** MicroTE 10.1145/2079296.2079304; Ghabashneh et al. 10.1145/3517745.3561430; Roughan et al.
  10.1145/637201.637213. Lakhina 10.1145/1005686.1005697 là phương án thay cho Roughan.
- **Dự phòng (metadata-only):** Kandula'09, B4, B4 and After, HULA, LetFlow, Bullet Trains, TwinNet, Polverini'23,
  Aben-Athar'25.
- **Bản chính thức để đối chiếu nguồn đã đọc:** SWAN, CONGA, RZB15, NDT1 (đang đọc arXiv v2), Planck, Kuźniar'18.
- **Mức đọc:** mọi ứng viên mới đều metadata-only (+ abstract OpenAlex nếu có). Chưa tải, chưa note.
- **Phạm vi:** không 2×20, không saturation, không novelty.
- **Lý do dừng:** đủ ứng viên cho từng ô UNSOURCED; Semantic Scholar bị rate limit; chờ tác giả tải.

### L7.3-R2 đợt 2 — tác giả tải và paper cũ trong Downloads (04/11/2026)

Tác giả nhắn: "tôi đã tải rồi á, bạn còn có là các paper cũ của tôi bạn hãy xem thử mục tải về ở window ... và bổ sung
thông tin thêm cho lesson đi". AI coi việc tác giả tải là duyệt các nguồn đó, và tin nhắn là ủy quyền đọc paper cũ.

| Ngày | Loại | Thẻ / Q / PC | Query / seed | Tool, bộ lọc, thứ tự | Đã sàng | Giữ unique | Lý do / hạn chế / dừng |
|---|---|---|---|---|---:|---:|---|
| 04/11 | intake | L7.3-R2 | `C:\Users\VAN TAI\Downloads` (file mới 04/11) | ls theo thời gian, pdftotext trang 1, pdfinfo | 4 | 4 | MicroTE VoR (12 tr.); Roughan, `download.pdf` (10 tr., bản tác giả của bản ITC 2003, không phải IMW 2002); Kuźniar'18 AM (25 tr., trong `tmp/`); SWAN ACM VoR. Ghabashneh'22 và các bản VoR khác chưa có |
| 04/11 | library (author files) | L7.3-R2 / NDT | paper NDT cũ trong Downloads và `Downloads\Digital Twin` | pdftotext trang 1 + grep thời gian vòng | 8 | 4 | Giữ ZBEK26, VGC23, HHZ26, AAA25 (có số thời gian). Bỏ 3 survey không có số vòng routing; Kuri & Kumar CDC'92 là R34 đã có. Zotero storage: 1 PDF AoI survey (Yates 2020), không thuộc câu hỏi này |
| 04/11 | lookup | L7.3-R2 | Vilalta (title); 10.1109/TNSM.2026.3737654; 10.1038/s41598-026-71181-2 | `search_crossref`, `get_crossref_paper_by_doi` | 5 | 3 | VGC23 = IEEE ComMag 61(12):128–134, DOI 10.1109/MCOM.003.2300105; ZBEK26 = TNSM 23:8111–8124; HHZ26 = Sci. Rep. 2026 |
| 04/11 | backward | L7.3-R2 | BAAZ11 refs [5, 6, 13, 17] | pdftotext local | 4 | 0 mới | Câu 150 s: BAAZ11 §4/PDF4 trích [13] Kandula'09 và [6] Benson WREN'09. BAM10 (= [5]) §6.4 có chu kỳ ngày, không có câu 150 s |
| 04/11 | read (AI-T) | L7.3-R2 / realism | BAAZ11, RGK03, KPKC18, SWAN VoR (so trang), BAM10 §6.4, P07 (grep), 4 paper NDT | pdftotext + grep + đọc đoạn quanh; render KPKC18 PDF9 để đọc Table 2 | 11 | — | SWAN VoR trùng chữ 12/12 trang với bản đã đọc. KPKC18 AM khớp số 250/400 ms của T00 |

Kết quả:
- **Note mới:** [BAAZ11](papers/BAAZ11.md), [RGK03](papers/RGK03.md), [KPKC18](papers/KPKC18.md),
  [NDT_timing_L73](papers/NDT_timing_L73.md).
- **Bổ sung:** [BAM10](papers/BAM10.md), [P07](papers/P07.md), [HKM13](papers/HKM13.md).
- **Bản nháp:** [realism v2](../realism/realism_v2_draft.md) cập nhật §2–6, thêm §3e.
- **Lưu PDF:** chép (không di chuyển) vào `~/papers/state-model-regret/l73/{BAAZ11,RGK03,KPKC18,HKM13,ndt_old}/`, có
  sha256 trong note.
- **AAA25:** trước đây tác giả quyết định "không đọc thêm" (đợt 26/10); lần này đọc theo yêu cầu mới, chỉ để tìm thời
  gian vòng.
- **Không đổi:** catalog và Excel trên `main`, mức đọc của tác giả, nhãn PC.
- **Phạm vi:** không novelty, không 2×20.
- **Lý do dừng:** đã dùng hết các file tác giả cung cấp có liên quan; các ô còn thiếu cần Kandula'09, Benson WREN'09,
  Ghabashneh'22 hoặc nguồn NDT có thời gian giữ quyết định.

### L7.3-R2 đợt 3 — quét toàn bộ Downloads và đính chính (04/11/2026)

Tác giả nhắn: "liệt kê thêm các bài đi để tôi tải và kiểm tra trong thư mục windown tôi nhiều bài á, coi bài nào dùng
được không".

**Đính chính đợt 2.** Dòng intake ở đợt 2 ghi "Ghabashneh'22 ... chưa có" là **sai**. Hai file `Downloads/tmp/imc2022.pdf`
(GZL22) và `odflows-sigm04.pdf` (LPC04) đã được tải lúc 06:38 cùng ngày; lượt quét đầu chỉ xem file mới ở thư mục gốc
và `tmp/10.1016@…`. Dòng cũ giữ nguyên làm lịch sử.

| Ngày | Loại | Thẻ / Q / PC | Query / seed | Tool, bộ lọc, thứ tự | Đã sàng | Giữ unique | Lý do / hạn chế / dừng |
|---|---|---|---|---|---:|---:|---|
| 04/11 | intake (toàn bộ) | L7.3-R2 | `C:\Users\VAN TAI\Downloads` đệ quy (Documents, Desktop, OneDrive: 0 PDF; Zotero: 1) | find + pdftotext trang 1 + sha256 so với `~/papers/state-model-regret/` | 132 | 2 mới | 24 file trùng thư viện theo sha256. 2 mới dùng được: GZL22, LPC04. 106 còn lại không dùng: CV, thuyết minh/báo cáo NCKH, slide và lab môn học, sách IELTS, tài liệu RL (Sutton & Barto, DQN, survey GNN/RL routing), benchmark CIS, survey/eBook NDT chung |
| 04/11 | read (AI-T) | L7.3-R2 / realism | GZL22, LPC04 | pdftotext + grep + đọc đoạn quanh | 2 | 2 | GZL22: burst 1 ms trung vị 2 ms, p90 8 ms, 7,5/s; tải trong/ngoài burst 65,5%/5,5%. LPC04: chu kỳ/spike/nhiễu 92/6/2% (Sprint) và 70/19/12% (Abilene) |
| 04/11 | lookup | L7.3-R2 | Benson WREN'09; Jupiter Evolving; FLARE; Heffes–Lucantoni; Yates AoI survey | `search_crossref`, max 3 | 15 | 5 | DOI: 10.1145/1592681.1592692 (WREN'09; bản CCR 10.1145/1672308.1672325); 10.1145/3544216.3544265; 10.1145/1232919.1232925; 10.1109/JSAC.1986.1146393; 10.1109/JSAC.2021.3065072 (bản arXiv v1 đã có trong Zotero của tác giả) |
| 04/11 | keyword | L7.3-R2 | "backbone traffic variability fine timescales seconds minutes traffic matrix" | `search_openalex`, max 15 | 15 | 1 | OnlineTE (arXiv 2605.16187, 2026): abstract nói TE WAN triển khai thu demand định kỳ và "can take minutes to react". Còn lại là luận văn, Starlink, Tor, anomaly, hoặc trùng (RZB15) |

Kết quả:
- **Note mới:** [GZL22](papers/GZL22.md), [LPC04](papers/LPC04.md).
- **Bản nháp:** realism v2 thêm §3c′ và §3f, sửa §2, §4–6.
- **Đề xuất cho tác giả tải (metadata-only):** Kandula'09, Benson WREN'09, Jupiter Evolving, FLARE, Heffes–Lucantoni.
  OnlineTE và LetFlow là open access.
- **Không đổi:** catalog và Excel trên `main`, nhãn PC.

### L7.3-R2 đợt 4 — tác giả tải 8 bài, chốt Phần 1 (04/11/2026)

Tác giả nhắn: "tôi tải hết rồi á, hoàn thiện đầy đủ lesson và push lên đi". Tác giả tải là duyệt các nguồn đã liệt kê.

| Ngày | Loại | Thẻ / Q / PC | Query / seed | Tool, bộ lọc, thứ tự | Đã sàng | Giữ unique | Lý do / hạn chế / dừng |
|---|---|---|---|---|---:|---:|---|
| 04/11 | intake | L7.3-R2 | Downloads, file mới sau 07:00 | find -newermt + pdftotext/pdfinfo + sha256 | 9 file | 8 | Jupiter, Benson WREN'09, Kandula'09, Heffes–Lucantoni, OnlineTE v1, LetFlow, FLARE (2 file trùng sha256, giữ 1), Yates JSAC |
| 04/11 | read (AI-T) | L7.3-R2 / realism | 8 bài trên | pdftotext + grep; render tr. 202–206, 208 (KSG09, mất chữ số khi trích text), tr. 69 (BAAZ09), tr. 1189 (YSB21), tr. 858 (HL86) | 8 | 8 | Câu "≥ 150 s": **không tìm thấy** trong KSG09 (ảnh 6/7 trang; tr. 207 chỉ grep) và BAAZ09 (grep toàn văn). KSG09: TM đổi trung vị 82% ở 10 s và 100 s. YSB21 eq. 21 cho P/2 + L |
| 04/11 | backward | L7.3-R2 | GNM26 refs [17, 35, 46] | pdftotext | 3 | 0 đề xuất | RedTE (SIGCOMM'24) và Namyar et al. (NSDI'24) là ứng viên cho thang dưới 5 phút ở WAN. Chưa tra DOI; giữ cho đợt sau theo giới hạn 3 đề xuất mỗi đợt |

Kết quả:
- **Note mới:** [KSG09](papers/KSG09.md), [BAAZ09](papers/BAAZ09.md), [PMO22](papers/PMO22.md),
  [KKSB07](papers/KKSB07.md), [VPA17](papers/VPA17.md), [GNM26](papers/GNM26.md), [HL86](papers/HL86.md),
  [YSB21](papers/YSB21.md).
- **Bản nháp:** [realism v2](../realism/realism_v2_draft.md) viết lại thành bản hợp nhất "hoàn tất kỹ thuật Phần 1", thêm
  §0 tóm tắt, §5 kết luận, §6 bàn giao Phần 2 và §7 nguồn.
- **Không đổi:** catalog và Excel trên `main`, mức đọc của tác giả, nhãn PC/Gate.
- **Phạm vi:** không novelty, không 2×20, không saturation.
- **Lý do dừng:** mọi ô của bảng use case đã có nguồn hoặc UNSOURCED rõ lý do. Các lỗ còn lại cần nguồn mới (WAN dưới
  5 phút; h của NDT; f của DC).

## L7.4-N1 — novelty: bốn claim lõi và claim τ (04/11/2026)

Theo L7.4 §4.2 mục 3 và yêu cầu "đóng vai trò là tôi… về phần bài paper cần bài nào nói tôi sẽ lấy cho bạn". AI (Claude)
chạy. Thẻ: câu hỏi là có prior nào cùng estimand/cơ chế/regime với C1, C3/C5, C4, C6 và claim τ không
([L7_4_novelty_check](L7_4_novelty_check.md) §2). Trước khi tìm đã đọc lại L6_4_prior_check, M00, information_harm,
state_staleness, freshness_decision_value. Ngân sách: 1 buổi, tối đa 3 đề xuất mới.

| Ngày | Loại | Thẻ / Q / PC | Query / seed | Tool, bộ lọc, thứ tự | Đã sàng | Giữ unique | Lý do / hạn chế / dừng |
|---|---|---|---|---|---:|---:|---|
| 04/11 | keyword | Q1 / C3,C5 | "interpreting stale load information age load balancing" | `search_openalex`, max 20, relevance | 20 | 2 | Dahlin TPDS 2000 (+ ICDCS'99, cùng công trình); Fischer–Vöcking TCS 2008. AoI survey đã có (YSB21). Còn lại ngoài ngành (thể thao, điện) |
| 04/11 | keyword | Q2 / τ | "age of information fresher updates worse decisions non-monotone value of information" | `search_openalex`, max 20 | 18 | 0 mới | Arı et al. ISIT 2024 (10.1109/isit57864.2024.10619298, sai số không đơn điệu theo tuổi) chỉ sàng; 2609.06351 đã chờ duyệt; còn lại ngoài ngành |
| 04/11 | keyword | Q3 / C1 | "certainty equivalent fluid model controller queue state information harm long horizon" | `search_openalex`, max 20 | 20 | 0 | Toàn bộ ngoài ngành (y tế, kinh tế, công nghiệp) |
| 04/11 | keyword | Q4 / τ | "does fresher data always improve remote inference age of information non-monotone" | `search_openalex`, max 20 | 16 | 0 mới | Arı et al. 2410.08706 (cùng nhóm Q2); coupon-collector 2603.26998 chỉ sàng |
| 04/11 | keyword | Q5 / C3,C4 | "optimal routing control queues delayed queue length information" | `search_openalex`, max 20 | 20 | 0 mới | Kuri–Kumar TAC 1995 = R34 (đã có, cần VoR). Jacko–Niño-Mora 2008, He–Yang–Yao 2025 (RJSQ, dao động JSQ khi có trễ), Doldo–Pender 2021 chỉ sàng |
| 04/11 | forward | Q6 / C3 | các bài trích Dahlin 10.1109/71.888643 | `get_citing_papers` (OpenAlex), max 40, most-cited | 40 (trên 114) | 0 mới | Chủ yếu cân tải web/CDN; Fischer–Vöcking xuất hiện lại. Truncated tại max_results |
| 04/11 | keyword | Q7 / C4,NDT | "network digital twin telemetry freshness staleness decision quality what-if" | `search_openalex`, max 20 | 20 | 0 | CENTILE 2608.01725 đã chờ duyệt; còn lại DT ngoài mạng (xe, lưới điện, nhà máy) |
| 04/11 | keyword | Q8 / C1 | "value of state information misspecified model certainty equivalence average cost bias long horizon Markov" | `search_openalex`, max 20 | 20 | 0 | Ngoài ngành (kinh tế, tài chính, RL chung) |
| 04/11 | keyword | Q9 / C2,C6 | "static versus dynamic routing value of queue state information horizon relaxation time" | `search_openalex`, max 20 | 20 | 0 | Vehicle routing chiếm đa số; routing hai server quan sát một phần chỉ sàng |
| 04/11 | lookup | τ | "How does data freshness affect real-time supervised learning Shisher Sun" | `search_crossref`, max 5 | 5 | 1 | DOI 10.1145/3492866.3549711, MobiHoc 2022 tr. 31–40 |
| 04/11 | lookup | C3 | DOI 10.1109/71.888643 | `get_crossref_paper_by_doi` | 1 | (đã tính ở Q1) | IEEE TPDS 11(10):1033–1047 |

Kết quả:
- **Đề xuất (chờ duyệt, metadata-only):** Dahlin 2000; Shisher–Sun 2022; Fischer–Vöcking 2008.
- **Dừng:** đạt luật 2×20 (Q7 và Q8 liên tiếp, mỗi query 20 kết quả, không giữ mới); Q9 cũng không giữ.
- **Hạn chế:**
  - chỉ OpenAlex và Crossref; không Semantic Scholar hay Google Scholar;
  - không dò ngược từ M00/Dahlin;
  - không tra venue SIGCOMM/NSDI riêng.
- **Không đổi:** catalog/Excel trên `main`, nhãn PC/Gate, mức đọc của tác giả. Không tải PDF, không note nội dung mới.

### L7.4-N1 đợt 2 — tác giả tải 3 nguồn đề xuất, AI đọc targeted (04/11/2026)

| Ngày | Loại | Thẻ / Q / PC | Query / seed | Tool, bộ lọc, thứ tự | Đã sàng | Giữ unique | Lý do / hạn chế / dừng |
|---|---|---|---|---|---:|---:|---|
| 04/11 | intake | L7.4-N1 | Downloads/tmp (dahlin2000.pdf, fischer2009.pdf) và Downloads (3492866.3549711.pdf), file sau 15:00 | find -newermt + pdfinfo + sha256 | 3 | 3 | Không trùng sha256 với thư viện. Chép vào `~/papers/state-model-regret/l74/{DAH00,SS22,FV09}/` |
| 04/11 | read (AI-T) | C3,C5,τ | DAH00 §1, §3, §4.1 Eq. 2–3, §5–5.1, §6 | pdftotext -raw, page headers | 1 | 1 | §6 tr. 1045: LI giải nghịch lý thêm thông tin tệ hơn |
| 04/11 | read (AI-T) | τ | SS22 Abstract, §1, §3.1, Thm 3.4/3.6 | pdftotext -raw | 1 | 1 | Không đọc §4–6 (lập lịch) và thí nghiệm |
| 04/11 | read (AI-T) | C3,C6 | FV09 Abstract, §1.1, §2.3, §4 mở đầu, §6 | pdftotext -raw | 1 | 1 | Năm số tạp chí là 2009 (đề xuất ghi 2008 theo DOI); không đọc chứng minh |

Kết quả: 3 note mới. L7_4_novelty_check §5 ghi ảnh hưởng tới wording. Catalog/Excel trên `main` chưa cập nhật (sẽ làm ở
merge nếu tác giả muốn), mức đọc của tác giả không đổi.
