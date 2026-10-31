# Phase 4 v2 — tách nguồn, cơ chế và freeze hypothesis

Người phụ trách: **Doan Van Tai** · 31/10/2026 · [DL-117](../02_decision_log.md#dl-117--l45-v2-đổi-loại-evidence-park-sub-và-gói-cf-v2-31102026).
AI soạn theo yêu cầu thực hiện lesson và ủy quyền tiếp diễn; không tác giả tự
viết/tự ký hoặc human review. **Bản triển khai tối thiểu từ L4.5 (v2)**, không
phải toàn văn PHASE_4_v2/Phụ lục B hay Master Plan v1.2 chưa được cung cấp.
Nguồn lesson được giữ tại [bản gốc](../../results/lessons/l4_5_v2/lesson_original.txt).

## 0.1. Trạng thái thật khi bắt đầu

| Phần | Trạng thái và evidence có thể dùng |
|---|---|
| L4.1–L4.2 | Recount/toys/reading hoàn tất theo scope; map1376 là discovery, chưa phải toàn map native |
| L4.3 | Audit gốc vẫn có HOLD/sealed block; không ghi full audit PASS. SV A1 đã chạy497keys, scope riêng |
| L4.4/A3 | Baseline STABLE tại3mức; MV rho5%, medianR_M .862967–.867986 → narrow; SH rho0 → không narrow |
| L4.5 v1 / SV | FAIL_SCREEN:216MEETS/224FAILS/9U trên449plus;0/48 MEETS ởminus; planning power≈2.5655e-5 |
| L4.5 v1 / SUB | **PARKED_AS_DISCOVERY**:10/76 keys hoàn tất,10PASS;2calls đang dở đã hủy khi còn STOP;66 keys chưa có kết quả hoàn chỉnh |
| F2 | **0 card mới do lựa chọn thiết kế evidence**; SUB chưa được sàng, không có SUB FAIL/PASS |
| Gói MV/SH CF-v2 | **PARKED**,270 keys tham số giữ nguyên,0outcomes; optional kiểm phụ sau này khi có quyết định riêng |
| L4.5 v2 | Research task hoàn tất; learning note do AI soạn, Understanding của tác giả chưa được xác nhận |
| G-level | G1; chưa có finding cơ chế, realism, novelty hoặc confirmation mới |

Lịch sử [DL-115/116 và checkpoint](../../results/lessons/l4_5/part_b/report.md)
không bị sửa. Lệnh SIGCONT/resume trong pause snapshot cũ đã hết hiệu lực theo
DL-117; tiến trình cũ đã được kết thúc. Giữ10keys làm dữ liệu **đã thấy** khi
tạo hypothesis, không gọi chúng là held-out. Không tạo SUB rho*, manifest hay p-hat.

## 0.2. Mục tiêu evidence

Main RQ, contract v1.3, objective/normalization và identities giữ nguyên. Hướng
hiện tại ưu tiên mô tả có điều kiện trên design khai trước, tách nguồn, mechanism
và dự đoán có thể sai trên điều kiện thực sự chưa dùng tạo hypothesis.

Prereg/card/CI của gói cũ vẫn hợp lệ cho estimand theo hộp và measure của chúng.
Park là đổi ưu tiên nghiên cứu **sau** SV FAIL_SCREEN và10 SUBkeys đã lộ, không
phải chứng minh công cụ đó sai hoặc đổi verdict sau outcomeCF. Báo lại lịch sử
này trong freeze L4.9. Held-out điều kiện chưa được chọn, nên hiện chưa có
evidence thay thế confirmation. Không tự mở R09/R10 hoặc CF-v2 outcomes.

## 1. Bảng giữ, park và thay cách làm

| Thành phần | Quyết định hiện hành | Lý do/phạm vi |
|---|---|---|
| Main RQ, contract v1.3, native engine, S01–S18, toys | Giữ | Lõi định nghĩa và verification, không đổi byte để đổi workflow |
| Map/pilot/native đã có, gồm10 SUBkeys | Giữ làm discovery | Giữ cả failures, numerical flags và exposure; không gán nhãn toàn map đã native |
| Margin+Stay, rho/reading A3 và SV | Giữ | MV narrow do recovery≈86%; SH/SV không narrow theo luật đã khai |
| SV FAIL_SCREEN | Giữ nguyên | Feasibility fail trong support, không chứng minh state value vắng mặt |
| SUB_BOX76 và screening tiếp theo | Park | Không chạy 66 keys còn lại chỉ để hoàn thành machinery cũ |
| Card v3, CF-v3 và phân suất F2 mới | Không tạo;0card mới | Không còn là evidence chính của hướng này |
| Card/CF-v2, CP, family và P0-V10 của gói đó | Park cùng gói, giữ nguyên | Không xóa prereg, đổi alpha hoặc tự gỡ gate để chạyCF |
| Freeze cho hướng mới | Một file ngắn + commit trước test | Ghi miền/design/measure nếu có, metric/epsilon, baseline, exposure, dự đoán và điều kiện bác bỏ |
| Numerical verification | Giữ kiểm tra tương xứng | Tất định vẫn có approximation/roundoff; không tạo A4 để cứu kết quả |
| Realism, mechanism và representation khác | Công việc tiếp theo | Chưa thực hiện trong lesson này; không giả đã có evidence |

## 2. Diễn giải học tập — AI soạn, không phải lời tác giả tự viết

1. Engine tính kỳ vọng không dùngMC, nhưng plant vẫn stochastic và evaluator vẫn có sai số numerical.
2. Card prevalence hỏi p=Pr_measure(G/Cref>=epsilon) trong miền và measure đã chọn; đây là câu hỏi có nghĩa nhưng hẹp.
3. CF kiểm sampling uncertainty của p;449điểm thích nghi không mặc nhiên thay thế mẫu từ measure đã khóa.
4. p=1−F_Z(epsilon−) là công thức tổng quát; liên hệ với median cần xử lý atoms/ties và không tự tạo verdict thống kê.
5. SV có median≈.97% và216MEETS, nhưng FAIL_SCREEN được quyết bằng haircut/power/unresolved, không chỉ bằng median.
6. Map có design khai trước phải báo đủ điểm, độ lớn và vùng chưa phân giải; chưa được giả hàm trơn hoặc lưới đã phủ mọi boundary.
7. Held-out điều kiện cần dự đoán trước cho điều kiện chưa thấy; ±4 và các amplitude/map đã lộ không tự thành held-out mới.
8. Vì mục tiêu hiện tại là điều kiện/cơ chế, tôi park machinery prevalence, giữ lịch sử và chờ freeze mới trước evaluation mới.

Ba câu trả lời personal-artifact, vẫn là **AI-assisted draft**: quan hệ prevalence
với median chỉ đơn giản trong trường hợp phân phối phù hợp; SV FAIL_SCREEN không
loại trừ effect khu trú; held-out có thể là amplitude/law/representation mới,
nhưng chưa chọn ứng viên nào hoặc viết prediction hậu kiểm.

Self-check do AI trả lời để tác giả tự đối chiếu, không chấm author Understanding:

1. Plant stochastic; evaluator kỳ vọng deterministic nhưng có sai số numerical.
2. CI của CF nhắm prevalence theo miền/measure và sự ngẫu nhiên của các regime được rút.
3. Median1.4% chưa đủ kết luận power cao: còn cần p_epsilon, unresolved và luật n/alpha.
4. Thêm vùng dưới threshold làm p giảm theo measure nếu các phần khác giữ nguyên;0/48 không chứng minh effect0 ở mọi regime mới.
5. Trả lời reviewer bằng lịch sử thật: pivot sau SV FAIL, SUBpartial đã lộ; giữ records và chỉ gọi test tương lai là held-out sau freeze mới.

### Chỉnh lý lesson trước khi dùng làm lập luận

- Deterministic không đồng nghĩa exact hoặc continuous. Native dùng quadrature,
  approximation và finite precision; không suy60draw mới chắc lặp lại48% từ lưới thích nghi.
- Với Z=G/Cref và CDF F_Z, p_epsilon=1−F_Z(epsilon−). Nếu phân phối liên tục và
  median duy nhất, p_epsilon>1/2 tương đương median>epsilon; các trường hợp
  bằng nhau/atoms/nonunique cần quy ước riêng. Sample median và CP verdict khác nhau.
- Median đơn thuần không quyết planning power. p_cond=.60 vẫn có thể FAIL_SCREEN
  sau haircut;0/48 MEETS chỉ nói không đạt1%, không nói effect bằng0.
- Ví dụ log-đều[.2,1] trong[.2,3] có mass ln5/ln15=59.4316%, không 40%.
  Nếu muốn ví dụ thấp hơn1/2, mở miền đến10 cho ln5/ln50≈41.14% (toy, không dữ liệu nghiên cứu).
- SV-minus đã đo: medianGS/Cref .060593%, max .697799%, min−.051785%; cách nói
  “tắt hẳn” không được suy chỉ từ0/48. SV-plus216/449=48.1069% là raw fraction,
  p_cond216/440=49.0909% mới là rate resolved dùng trong screening v1.

## 3. Lộ trình sau lesson này

| Lesson | Công việc | Trạng thái |
|---|---|---|
| L4.6 | Tách G_S_M1,G_M_S1,Gamma trên dữ liệu đã có; xem D22 native/cb0 với audit đúngjoint | Core đã chạy:1118pilot+597native,3figures; [report](../../results/lessons/l4_6_v2/report.md). NativeD22DEFERRED: Q-only trong hướng dẫn bỏY, chưa có joint estimator đúng |
| L4.7 | Kiểm mệnh đề clipping, predictor/null/knockout với điều kiện rõ | [T08](../theory/T08_clipping_anchor.md),48statechecks/50discoverydiagnostics đã chạy; S_clip/sigma=1cấu trúc primary, P_clipgần1/ranks chưaheldout. Khôngnull/knockout mới, chưakhóaH-clip. [Report](../../results/lessons/l4_7_v2/report.md) |
| L4.8 | Realism nhẹ, chọn use case và miền có lý do | Chưa có nguồn mới; áp search protocol khi làm |
| L4.9 | Freeze hypothesis có cơ chế và held-out condition chưa dùng | Chưa khóa hypothesis/design/held-out; ghi cả lịch sử SV FAIL và SUB partial |
| Gate4 / evaluation sau | Dựa trên freeze mới và evidence đúng phạm vi | Chưa được thông qua hoặc chạy trong lesson này |

Không đóng toàn Phase4 tại L4.5. Không nâng ownership/Understanding/G-level từ
AI-work. Không gọi pivot này là prereg trước discovery; chỉ evaluation tương lai
mới có thể được đánh giá theo freeze mới.
