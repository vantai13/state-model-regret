# Phase 3 closeout — REFORMULATE, ownership còn mở

> 28/10/2026 · Người phụ trách: **Doan Van Tai** · contract-v1.2.
> Nhãn REFORMULATE do tác giả chọn; AI soạn tổng hợp và hai mục ngôi “tôi” theo yêu cầu
> trực tiếp ở DL-061. Hai mục là bản viết theo ủy quyền, không phải nguyên văn tác giả
> tự viết hoặc bằng chứng Understanding. Chưa có xác nhận tác giả đọc/duyệt câu chữ.
> Khung từ [lesson Part 2](../../results/lessons/l3_8/lesson_part2.txt), không nhận đã đối chiếu template §21 của plan đầy đủ.

## What I understood

**Bản viết ngôi thứ nhất theo ủy quyền, không phải bài tác giả tự viết.**

Tôi hiểu Main RQ hỏi sửa thông tin trạng thái hiện tại và sửa model phản ứng với action
khác nhau và tương tác thế nào đối với expected decision regret. Tôi đo câu hỏi đó bằng
bốn trường hợp sửa của D18/D19, với oracle biết state/law nhưng không biết tương lai.
A04 cho P5 đứng trên danh sách trong khi P2/P3/P6 không đứng; điều này chưa biến một
pattern discovery thành luật ngoài mẫu. A05-T kiểm các dự báo đã khóa trên 10 ô mới:
PC4 nội suy WEAKEN, ngoại suy FALSIFY, K5 bị R04 bác và C1 đứng ở bốn ô đã định.
Mức0,247 điểm % không là SUPPORT vì thấp hơn margin0,25 đã khóa, dù H1 có MAE thấp
hơn ở nội suy. Với một observation cố định, GM=|EΔ| nhân chỉ báo hai action khác nhau,
nên true gap0 vẫn cho GM0 ngay cả khi action khác. Γ là factorial interaction theo D19,
không tự chứng minh cơ chế và cũng không mất ý nghĩa chỉ vì thiết kế một observation.
Tôi chọn REFORMULATE để chuẩn bị estimand qua nhiều observations, với phân phối và
weights được định nghĩa trước, thay vì sửa ngưỡng hoặc dự báo sau outcome để cứu kết quả.
Phase3 chưa chứng minh hiệu quả mạng thật, novelty hoặc khả năng khái quát ngoài scope đã đo.

## What changed in my mental model

**Bản hồi tưởng đề xuất theo ủy quyền, viết sau dữ liệu; không xác nhận đây là niềm tin
thật trước run của tác giả và không bổ sung kỳ vọng trước A05-T hồi tố.**

- Trước tôi có thể gắn model dùng động học với dự báo tốt hơn; bây giờ tôi chỉ nhận
  lợi thế khi đạt metric/margin đã khóa, vì PC4 chỉ WEAKEN ở nội suy và FALSIFY ở ngoại suy.
- Trước tôi có thể xem luật đứng trong discovery là dấu hiệu khái quát; bây giờ tôi
  giữ scope của từng claim, vì R04 đã bác luật K5 nhưng không xóa quan sát M19–M22.
- Tôi chuyển từ mong Γ tự giải thích cơ chế sang dùng nó làm đại lượng đo cần kiểm
  thêm, đồng thời chuẩn bị một thiết kế nhiều observations có law và weights rõ.

## Decisions made

| DL | Quyết định đã có |
|---|---|
| DL-044 | Bản triển khai Phase 3, điều kiện còn mở, current pointers |
| DL-045–046 | Engine exact trong experiments; numerical bounds, tests/mutants; ownership tách riêng |
| DL-047–049 | K5 danh sách + luật, attested read-back, card A03 khóa trước A01 |
| DL-050–053 | A01 prereg, giữ FAIL/partial, sửa certificates/performance, chốt dt=1/240 s |
| DL-054 | Tác giả waive memo V9 trước A04, không GVHD_APPROVED |
| DL-055–056 | A04 prereg và discovery; card giữ byte; carry K5, đề cử C1 hậu discovery |
| DL-057–058 | D25(ii), thiết kế A, H0/H1/metric/margin/split/θ/predictions đóng băng |
| DL-059–060 | Quyết định mở A05-T trước run; kết quả WEAKEN/FALSIFY/K5 bị bác/C1 đứng |
| DL-061 | Tác giả chọn REFORMULATE; ủy quyền viết hai mục ngôi “tôi”, giữ ownership OPEN; contract mới trước Phase4 |

[Decision log](../02_decision_log.md) là nguồn lịch sử; closeout không viết lại các entry cũ.

## Evidence created

E0/E1 **trong mô hình đã khai báo**, không có network evidence hoặc nâng G1:

- [L3.2](../../results/lessons/l3_2/report.md): engine, golden cases, bounds, 11/11 mutants lịch sử.
- [L3.3](../../results/lessons/l3_3/report.md): card 14 sanity/4 forecast/1 luật K5, receipt/hash trước outcomes.
- [A01](../../results/lessons/l3_4/report.md): controls PASS, 15 calibration levels, 12 pairs;
  chọn dt=1/240 s, giữ run01 FAIL và run02 INTERRUPTED.
- [A04](../../results/lessons/l3_5/report.md): 38 main + 8 controls/probes ×2dt =92 BOUNDED,
  46 pairs; P5 đứng, P2/P3/P6 không đứng; discovery không thành confirmation.
- [A05-F](../../results/lessons/l3_6/freeze_report.md): 12 hệ số/model, 20 slice LOSO;
  quyền thông tin/ngân sách khớp, metric MAE đều GS/GM/Γ, margin0,25 điểm %.
- [A05-T](../../results/lessons/l3_7/report.md): 10 ô mới ×2dt=20 BOUNDED, 10 pairs;
  nội suy WEAKEN, ngoại suy FALSIFY, K5 bị bác R04, C1 đứng R05–R08.
- [Kiểm L3.8](../../results/lessons/l3_8/verification.json): hash/chronology/liên kết,
  full tests và chấm lại dữ liệu lưu, không outcome mới.

## Assumptions still open

AS1–AS9 kế thừa [scope](../01_definitions.md#8-scope-và-assumptions) và
[contract v1.2](../01_definitions_v1_2.md): nền ngoại sinh; hai path độc lập;
slotted/infinite buffer; action tức thời; ON/OFF Markov/tham số cố định;
capacity cố định; path rời; (q,m) là state đủ; managed u cố định.
Chưa kiểm external validity của các giả định này; AS1/AS4 vẫn là rủi ro lớn.

- Một observation cố định mỗi ô; không population/mixture nhiều observations.
- Lưới neo gần ranh giới, có chủ đích, λA đổi theo lát; không tách riêng causal effect của κ/η/quantile.
- D13 đã tính backlog endpoint nhưng không cost sau h/terminal surcharge bổ sung.
- D21 chỉ sửa biểu diễn randomness với cùng θ đúng, không parameter/structure repair.
- H0/H1 chung Gaussian/rho=0, feature xấp xỉ; enclosure số có điều kiện trên input bounds,
  không sampling CI hoặc chứng minh continuum convergence.

## Risks still open

| Rủi ro | Trạng thái / nơi xử lý |
|---|---|
| PC4 không đạt lợi thế đã khóa; lỗi ngoại suy | Giữ verdict; redesign tương lai phải có protocol/test mới |
| K5 không khái quát; main có headroom chặn | Không nâng equivalence bốn ô thành luật tọa độ |
| C1 n=4, base rate cao | Chỉ claim bốn ô; không gọi heuristic0,8055 là xác suất thật |
| Γ là factorial interaction, chưa là cơ chế | T01 không tự bác ý nghĩa D19; knockout/mechanism chưa có |
| Người đọc/ownership | P0-V10/L8, lý do DL-038, closeout Phase1/2, T05/Understanding còn OPEN |
| Run ngoài lịch sử repo | Không thể loại trừ run bị xóa bằng Git; không ghi audit tuyệt đối |

## What I am allowed to claim

[Claim boundary hiện hành](../01_claim_boundary_v1_2.md) và [Gate A](PHASE_3_gate.md):
báo các số đo đã lưu trong scope plant/lưới/dt; báo H1 có lợi thế nội suy dưới margin;
ngoại suy không tốt hơn H0; K5 bị phản ví dụ R04; C1 equivalence đứng bốn ô.
Không suy vượt scope chỉ vì một nhãn Gate tương lai.

## What I am NOT allowed to claim

H1 SUPPORT/chính xác tuyệt đối; H0 đủ tốt; K5 đúng cho κ≥2; C1 đúng toàn vùng;
Γ chứng minh cơ chế hoặc vô nghĩa; kết quả cho h=4/R09/R10; 10 ô đã mở còn là test sạch
cho giả thuyết mới; network benefit/long-run loss/novelty; tác giả đã tự hiểu hoặc GVHD đã duyệt.

## Gate decision

**REFORMULATE**, tác giả chọn trực tiếp; [DL-061](../02_decision_log.md),
[Gate A và claim duy nhất](PHASE_3_gate.md), [record nguyên văn](PHASE_3_author_decision.json).
Khuyến nghị NARROW trước đó của AI không được adopt. Việc cho AI viết hai đoạn
thay quy tắc không ủy quyền của lesson ở mức soạn/đóng hồ sơ, không tạo evidence tự hiểu.

## Next phase

Được học tiếp; **thực thi Phase 4 HOLD tới P0-V10 và contract mới được khóa**.
Đã chuẩn bị [v1.3 DRAFT](../01_definitions_v1_3_draft.md) và [brief DRAFT](../00_research_brief_v1_3_draft.md),
chưa adopt/khóa công thức hoặc chạy outcomes mới. `PHASE_4.md` chưa được viết;
tài liệu methodology threats không thay plan. Commit hồ sơ Gate/closeout này trước
tag `phase-3-closeout` không force; tag đóng hồ sơ Phase3, không xác nhận Understanding
hoặc cho phép thực thi Phase4. Các mục tự viết trước đây và human gates vẫn OPEN.
