# Tiếp nhận nhận xét trước A04 và quyết định V9

Người phụ trách: **Doan Van Tai** · 27/10/2026 · quyết định: **DL-054**.

## Nguồn và phạm vi

[Bản gốc](review_original.txt) được giữ nguyên byte, không đổi tên người review
hoặc xóa disclaimer. [Provenance](provenance.json) ghi SHA256 và phạm vi nguồn.
Đây là review mô phỏng do AI cung cấp, không có record phản hồi của GVHD thật.
Việc tác giả yêu cầu bỏ chặn A04 được xử lý bằng **waiver V9**, không bằng ghi
nhận rằng đã gửi memo hay nhận được human approval.

Reviewer chỉ truy cập public snapshot **f72306f** (A03), không có A01 local.
Do đó 324 tests/20.000 toy trials là kết quả **reviewer báo**, không phải lượt
chạy lại được xác minh trong lần tiếp nhận này. Không đổi chúng thành 336 tests
để làm như reviewer đã đọc code A01. Bản local hiện có A01 ở source60a1032,
closeoutb9a176c; artifact cũ ghi336 tests/11mutants, không phải tests mới của phiên này.

## Đối chiếu các nhận xét

| Mục nguồn | Xử lý tại local | Trạng thái |
|---|---|---|
| R1: thiếu A01 trên remote | Local có DL-050–053, manifest, CSV, controls và failed runs; verify guards và51artifact hashes. Chưa push trong phiên này | Đã kiểm evidence local; khả năng truy cập từ remote chưa được khắc phục bằng một lần push |
| R2: a00=a01 ⇒ Γ=GM_S1≥0 | Đúng theo D19: Γ=GM_S1−GM, GM=0 khi hai action cấp ô trùng nhau | Cần lưu ý khi diễn giải A04; không sửa Main RQ/card |
| R3: chỉ pairref1/ref2 chưa chứng nhận continuum | Đúng giới hạn finite-level rule. Ref4 bổ sung là đề xuất diagnostic mới, chưa tự adopt | Đưa vào danh sách quyết định prereg A04 |
| R4: D1/card chỉ certify6contrast, P6 dùng F/V | Kiểm theo scope thật của card; numerical bounds cho F/V khác dt-stability riêng của chúng | Diagnostic đề xuất; không đổi tiêu chí P6 sau freeze |
| R5: flip mass chưa có | Engine ghi not_computed; implementation/omission cần nêu trong prereg | Chưa implement, không bịa metric |
| R6: miền cheap-kill chưa chốt | Không tự chọn miền hoặc kill threshold theo một review | Chờ lesson/prereg A04, không áp hồi tố |
| R7: kernel kiểm độc lập có giới hạn | Part0 dùng shared kernel, toy aggregation không là formal proof toàn bộ vật lý | Giữ limitation, không đổi A01 PASS thành kiểm chứng toàn cục |
| R8: runner nên kiểm V9/prereg/dt | Thêm record gate đọc được bằng máy, không sửa frozen engine/guard A01 | Runner A04 tương lai cần kiểm record và các điều kiện còn lại |
| R9: thiếu người thật | Giữ OPEN cho human review; waiver V9 không đóng L8/P0-V10/T05 author-writing | Không có human attestation mới |
| R10: calibration đã exposed | Local exposure register đã ghi ở L3.4 | A04 prereg phải tiếp tục dẫn chiếu, không giả blind |

Reviewer có nhiều đề xuất có ích, nhưng không phải tất cả đều thành yêu cầu
thiết kế đã được tác giả adopt. Không tự thêm ref4, chọn H0, đổi cheap-kill domain,
đổi quota patterns hoặc đổi cách chấm card chỉ để “đáp ứng GVHD”.

## Hai điểm toán/diễn giải phải đọc thận trọng

1. **Γ dương vẫn biểu diễn superadditivity theo D19.** Khi a00=a01, Γ=GM_S1≥0
   là cấu trúc của thiết kế; dấu dương tự nó không xác nhận cơ chế vật lý mới.
   Không vì thế phủ nhận identity hay tự đổi định nghĩa interaction đã khóa.
2. **GM∈{0,|EΔ|} đã là identity T01** cho một observation/binary action/shared
   belief. Đề xuất nguồn “nếu dạng này xuất hiện mọi ô thì cân nhắc reformulate”
   không được nhận như một kill criterion mới: identity tất yếu không tự là
   evidence rằng nghiên cứu đã thất bại. Mixture theo y chỉ là đề xuất design mới.

Tuyên bố kiểu “so trong cùng lát là hết confounding” cũng cần giới hạn: hai điểm
neo trong cùng lát vẫn khác λA/observation tương ứng. Không gán causal effect
cho một trục ngoài những biến thực sự giữ cố định.

## Quyết định vận hành

Theo yêu cầu trực tiếp của tác giả “sửa lại mở để tôi có thể chạy lesson 5 đi”,
DL-054 **bỏ điều kiện gửi memo trước A04**. Ghi **WAIVED_BY_AUTHOR**, không ghi
“GVHD đã trả lời/đồng ý”. Memo vẫn chưa gửi; phần rủi ro của việc tiến hành trước
khi có góp ý thật được ghi trong DL và gate record.

[Gate record](../../phases/A04_execution_gate.json) mở riêng V9. Vẫn phải chuẩn bị
và commit prereg/exposure, kiểm runner trên synthetic/toy và kiểm card/dt trước
computation A04. Chưa có A04/held-out outcome mới trong phiên này. L8/P0-V10 và
HOLD Phase4 giữ nguyên. Waiver không là bằng chứng tác giả đã tự giải thích bài.
