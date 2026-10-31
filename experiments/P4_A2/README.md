# P4-A2 — eight-point baseline escalation probe

Người phụ trách: **Doan Van Tai**. Source thiết kế do AI (Claude) cung cấp;
triển khai và forecast do AI soạn theo ủy quyền tiếp diễn, không tác giả tự viết.

A1/source/card/contract không đổi. Diagnosis đọc artifacts đã commit; probe dùng
thang R3 frozen và chính row_readiness/baseline_readiness A1. Không chọn rho hoặc
regional medians. Đo đủ 8 điểm × 7 levels, cùng u0 control ở1280/ref8.

Các sửa trước freeze so với code nguồn:

- Diagnosis hash cả rows và comparisons; median diagnostic dùng định nghĩa chuẩn;
  lặp lại thì im lặng, không ghi đè. Cap8/72 không là estimated prevalence.
- Pin transitive A1/source/history và toàn input diagnosis. Quyết định được AI soạn
  theo ủy quyền có status/evidence riêng; không giả tác giả tự viết.
- Replay mọi numerical/error/baseline fields, kiểm significant bits parse lại;
  không nhầm equality của saved values với equality của toàn JSON/timing/ABI bytes.
- Resume kiểm params/ID/K/ref/dt/CF flag/receipt/schema, row SHA và replay receipts.
  Point/run HOLD không được âm thầm tiếp tục hoặc decide dù các file đã có.
- Control lỗi trả nonzero; BUG/replay/execution failure dừng trước level/điểm kế;
  giữ row, point receipt, log và CPU đã đo, kể cả call thất bại.
- Decision đòi run PASS, đủ8×7 valid rows,3×8 replay,controlPASS và budget hợp lệ.

Budget3CPUh tính unique evaluation CPU gồmcontrol, kiểm trước/sau từng điểm;
per-process cap3600CPU-s/4800wall-s/3GiB. Budget check giữa các điểm có thể phát hiện
vượt sau call; đó là HOLD, không được chọn quyết định trên attempt vượt cap.
Một worker, một BLAS thread. Không chỉnh code A2 sau freeze; sửa sau đó cần
prereg/package/attempt riêng, giữ mọi artifact cũ.

B1 chỉ là nhánh baseline cho A3 sau này, không tương đương certificate hoặc R1
per-point và không sửa card/scorer/CF. A2 chỉ trả decision.json; chưa thực thi A3.

Tests gồm actual saved A1 artifacts và một plumbing fixture trong tmp_path với
fake evaluator. 57 fake calls trong fixture không phải research engine calls,
không tạo numerical evidence hoặc artifacts research trong repository.
