# Quy tắc tìm và kiểm paper — mở trước mỗi phiên

Người phụ trách: **Doan Van Tai** · áp dụng từ **24/10/2026**.
Rút gọn từ Lesson 2.4 Part 1 do tác giả cung cấp; đây là quy trình làm việc,
không phải record đã chạy lesson, đã đọc nguồn hay đã đóng Gate.

**Nhớ 7 bước: HỎI → TÌM → KIỂM → DUYỆT → ĐỌC → GHI → DỪNG.**

## Checklist dùng ngay

- [ ] **Hỏi:** câu hỏi gì, phục vụ PC nào, kết quả nào có thể làm đổi nhãn?
- [ ] **Tìm:** kiểm thư viện trước; chọn lookup hoặc discovery; networking trước.
- [ ] **Kiểm:** đúng bài, đúng version, nguồn chính thức; sàng và bỏ bản trùng.
- [ ] **Duyệt:** tối đa 3 đề xuất mới/đợt; tác giả duyệt trước khi tải/viết note.
- [ ] **Đọc:** đúng phần cần thiết; ghi mức đọc, vị trí và ai thực sự đọc.
- [ ] **Ghi:** log thao tác/số đếm thật, lý do giữ/bỏ và lỗi truy cập.
- [ ] **Dừng:** theo ngân sách hoặc luật dừng; nêu rõ phần chưa xác nhận.

## 1. Hỏi — chặn việc tìm lan man

Mở [claims PC1–PC6](claims.md), [thư viện](../../papers/README.md) và
[search log](search_log.md) trước. Copy thẻ dưới đây cho mỗi câu hỏi mới;
lookup một bài đã biết chỉ cần ghi mục đích và PC ngay trong log.

```text
THẺ TÌM KIẾM — <ID/ngày>
Câu hỏi: <một câu cụ thể>
PC / mục đích: <PC1–PC6; định vị NDT / gọi tên công cụ / kiểm prior>
Câu chặn: Nếu bài cho thấy <X>, PC<n> có thể KEEP/NARROW/PIVOT/DROP vì <lý do>.
GIỮ nếu: <đối tượng, quyết định hoặc cách đánh giá liên quan>
BỎ nếu: <phạm vi không liên quan; tiêu chí rõ ràng>
Điểm vào / query: <nguồn neo hoặc từ khóa>
Bộ lọc: <năm, venue, cách sắp xếp; ghi lý do nếu giới hạn>
Ngân sách: <thời gian>; tối đa 3 nguồn mới đề xuất trong đợt này
Dừng khi: <hết ngân sách hoặc 2 query hợp lệ liên tiếp × 20 kết quả, không giữ mới>
```

**Phạm vi:** NDT của mạng truyền thông, routing/TE, telemetry, load balancing,
AoI và networked control. Phân biệt vehicle routing với network routing, twin
của mạng với mạng kết nối các twin, sai số KPI với chất lượng quyết định.
Nguồn định vị chỉ cung cấp bối cảnh thì ghi rõ, không dùng nó xác nhận claim.

Ngoài networking: không mở rộng mặc định. Chỉ tra khi có claim cụ thể cần;
tối đa 1–2 nguồn chuẩn/khái niệm để gọi tên EVPPI/VSS/EVMI. Không bắt đọc cả
sách. Abstract đủ cho sàng/gọi tên, chưa đủ kiểm một theorem hay giả định.

## 2. Tìm — chọn đúng đường vào

| Loại ghi trong log | Cách làm |
|---|---|
| `lookup` | Biết tên/DOI: tra đúng bài và phiên bản; không tính là khảo sát literature |
| `keyword` | Dùng từ của field: `stale link state`, `telemetry freshness`, `network digital twin what-if`, `decision quality` |
| `backward` | Từ survey hoặc bài kỹ thuật gần câu hỏi, kiểm các references; đối chiếu PDF khi có |
| `forward` | Tìm bài trích nguồn neo; lọc theo câu hỏi và năm phù hợp |
| `author/venue` | Bổ sung qua tác giả/venue; tránh chỉ theo một nhóm |

Mặc định dùng một survey và một bài kỹ thuật gần câu hỏi làm điểm vào.
Ưu tiên nguồn mới để định vị, nhưng không đặt năm/citation count làm rào cứng
khi kiểm prior. Bài cũ được giữ nếu có thể ảnh hưởng PC; việc được bài mới trích
là tín hiệu để lần theo, không phải điều kiện bắt buộc.

Sàng: **tiêu đề → abstract → hình/kết luận → section cần đọc**. Chưa rõ từ
tiêu đề thì mở abstract hoặc ghi chưa rõ, không kết luận bài không liên quan.
So overlap bằng **estimand / mechanism / regime**; cùng từ khóa chưa đủ.

## 3. Kiểm — đúng bài, đúng bằng chứng

- Đối chiếu tên, tác giả, năm và DOI/arXiv/URL với publisher, proceedings,
  arXiv hoặc kho tác giả/trường; dùng dblp để đối chiếu venue. DOI chưa có thì
  dùng định danh/URL chính thức, không tự đặt.
- Ghi riêng năm online/issue nếu khác; journal/conference/magazine, preprint,
  sách hay Internet-Draft; ghi version và ngày kiểm. Một preprint có thể đã có
  bản xuất bản: kiểm cả hai, không suy trạng thái chỉ từ việc có trên arXiv.
- Chọn VoR nếu truy cập được, nếu không dùng accepted manuscript/postprint
  hoặc preprint phù hợp và ghi đúng bản thực đọc. Draft phải kiểm trạng thái,
  số version và ngày trên trang chính; không gọi Internet-Draft là RFC.
- Gộp DOI/preprint/accepted version và các ID trùng thành một công trình;
  khác biệt kết quả giữa các bản phải ghi riêng. Kiểm PDF local trước khi tải.
- Ưu tiên publisher/OA, arXiv, tác giả, kho trường, Unpaywall hoặc thư viện
  trường. Không truy cập được thì ghi blocked; không dùng thư viện lậu.

## 4–5. Duyệt rồi đọc vừa đủ

AI đề xuất tối đa **3 nguồn/đợt**: tên/ID, nguồn kiểm, Q/PC, lý do đáng đọc,
mức đọc đề nghị. **Tác giả duyệt rồi mới tải PDF hoặc tạo note nội dung mới.**
Nếu tác giả đã yêu cầu tải/đọc chính nguồn đó thì thực hiện, không hỏi lại.
Metadata và quyết định sàng trong log không phải note đọc nội dung.

PDF lưu ở `~/papers/state-model-regret/`, ngoài Git; tên có tác giả, năm,
tên ngắn và version. Không tự gửi email xin bài. Mỗi record đọc ghi:

| Mức | Ghi thế nào? |
|---|---|
| Metadata | `metadata-only`; chưa đọc abstract/nội dung |
| S — screen | Nêu phần đã xem: tiêu đề, hình hoặc kết luận; chưa kiểm claim kỹ thuật |
| A — abstract | `abstract-only`; không xác nhận theorem từ abstract |
| T — targeted | `AI đọc full text (§…/trang …), targeted`; chỉ phần đã đọc |
| F — full | Chỉ ghi khi thực sự đọc hết; nêu bản và phạm vi, kể cả appendix |

Ghi riêng **AI đọc** và **tác giả đọc**; không tự điền L-self. Tải PDF không
đồng nghĩa đã đọc. Claim nội dung cần §/trang/phương trình; tách kết quả paper
khỏi suy luận áp vào repo. So giả định trước khi ánh xạ sang contract v1.2.

## 6–7. Ghi và dừng

Mỗi query/đường vào thực chạy ghi vào [search log](search_log.md), cả lượt rỗng
hoặc lỗi. Ghi ngày, loại, thẻ/Q/PC, query/seed, tool/CSDL, bộ lọc và thứ tự,
số thực sàng, số giữ unique, lý do giữ/bỏ, hạn chế và lý do dừng. Không biết
tổng thì ghi `N/A`; không biến số kết quả trả về thành số đã đọc.

| Ngày | Loại | Thẻ / Q / PC | Query / seed | Tool, bộ lọc, thứ tự | Đã sàng | Giữ unique | Lý do / hạn chế / dừng |
|---|---|---|---|---|---:|---:|---|

**Dừng discovery:** hết ngân sách đã ghi, hoặc hai query hợp lệ liên tiếp,
mỗi query sàng 20 kết quả đầu, không có ứng viên giữ mới. Ít hơn 20 thì ghi
đúng số thực tế; lượt đó chưa đạt luật 20. HTTP403/429, timeout, thiếu abstract
hoặc bộ lọc hỏng là hạn chế dữ liệu, không phải lượt “không có paper”. Nếu
kết quả bất thường, đối chiếu công cụ thứ hai hoặc báo chưa xác nhận.

**Dừng đọc một nguồn:** đã trả lời câu hỏi, hoặc khoảng 90 phút không tiến
triển; ghi phần Unclear. Với L2.4: ngân sách hai buổi, tối đa 3 bài mới từ
snowball; không biến giới hạn này thành yêu cầu cho mọi lesson.

Citation count phải kèm nguồn/ngày; nó không chứng minh đúng/sai. Venue cũng
chỉ là tín hiệu sàng. Luật dừng không chứng minh đã bao phủ lĩnh vực.
Kết luận: **“Đã tìm theo …; chưa xác nhận … từ các nguồn đã sàng/đọc.”**
Không viết “chưa ai làm”; nhãn PC là **AI đề xuất**, chờ quyết định theo Gate.

## Lưu ở đâu cho dễ tra?

**Query/kết quả sàng:** [search log](search_log.md). **Note đã được duyệt:**
`notes/literature/papers/`. **So sánh:** [matrix](matrix.md) và
[Excel](../../papers/paper_comparison.xlsx). **Claim/nhãn:**
[claims](claims.md), [prior boundary](prior_boundary.md). Chỉ cập nhật sau thao
tác thật; không tạo số liệu minh họa thành log thật hoặc tự nâng Gate/G-level.

Các số citation, version draft và báo cáo lượt tìm trong lesson được gửi chỉ
là thông tin của nguồn hướng dẫn; phải kiểm lại trước khi dùng như kết quả của
phiên mới. Quy trình này không đổi cách đánh số lesson hay trạng thái đã học.
