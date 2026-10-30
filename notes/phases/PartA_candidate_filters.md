# L4.5 Part A — Bộ lọc identity/prior/RQ, bản soạn để tác giả duyệt

Người phụ trách: **Doan Van Tai** · 30/10/2026.
Provenance: AI soạn từ ghi chú/code đã có; không mở primary paper hoặc search mới.
Trạng thái: **PROPOSED_PENDING_AUTHOR_CHOICE**, không quyết định0/1/2card.

## 1. Độ phủ RQ với cách diễn đạt có điều kiện

| Phần RQ | Card v2 đã preregister | Nếu PASS thì được nói | Còn thiếu |
|---|---|---|---|
| differ | MV:GM≥1%; SH:GS≤−1%, trên hai cặp vùng | Model repair có ích và state repair có thể gây hại dưới M0, trong các vùng đã kiểm | Phép kiểm state value dương; bằng chứng về tính đặc thù từng repair |
| interact | Γ diagnostic, không card interaction | Γ>0 trong vùng harm làS12, không finding độc lập | Phép kiểm substitution không được suy chỉ từ identity |
| expected regret | Cùng P1/RoE/Cref | Hiệu ứng theo objective đã khóa, ở mức mô hình | Không suy realism/vận hành |

**Không nói v2 “đã cho thấy” các kết quả confirmation:** chưa có outcomesCF.
SV chỉ yêu cầu GS≥1% nên **không tự chứng minh GM nhỏ**. MV chỉ yêu cầuGM≥1%
cũng không tự chứng minhGS nhỏ. Đặt hai card cạnh nhau tăng độ phủ “differ”,
nhưng gọi là **double dissociation đã xác nhận** còn cần điều kiện đối ứng
về repair kia được kiểm. Không tự thêm conjunction/equivalence vào card.

## 2. Premise DL-073 đã đổi ở đâu?

[DL-073](../02_decision_log.md#dl-073--l3r6-phân-suất-d-vùng-lật-κ-và-gói-luật-card-theo-lựa-chọn-tác-giả-2026-10-29)
chọn MV+SH, Γ diagnostic vì discovery trước đó chỉ3/162cấu hình có cảhai gains
đủ lớn. Map thích nghi về sau có161AB trên toàn bảng dedup1376, không “161chỉ
đến từ map2”. Premise thay đổi là **có support discovery đáng xem xét cho câu
substitution**, không prevalence hoặc khả thi đã xác nhận. AB membership
không tự épΓ≤−1%; không đếm161AB như161SUB. Không tái tính p-hat cho dảiδ.

Được xem lại design trước CF outcomes; DL-073/cardv2 hiện vẫn giữ nguyên byte.

## 3. Ba bộ lọc cho hai ứng viên

| Ứng viên | Identity | Prior có phạm vi | Giá trị cho RQ | AI đề xuất | Tác giả quyết |
|---|---|---|---|---|---|
| SV:GS/Cref≥1% | Không bị ép; GS có thể âm/0/dương | Freshness theo downstream cost đã có (K-S9/K-F1; S11§III/Eq10); stale-link routing P04§V-A/Fig8. Chỉ còn “ở đâu/bao nhiêu” dưới D20/D21, đặt cạnh model repair | Bổ sung state value dương; chưa tự đủ cho double dissociation | Giữ có điều kiện qua1–3 | PENDING |
| SUB:Γ/Cref≤−1% | Không bị ép; kéo theoGS,GM≥1% theoΓ≥−min(GS,GM). Một vùng theo định hướnglesson | PC3 đã được tác giả xác nhận KEEP câu chữ/framingNARROW ởDL-043. Ghi chúWM26§4.1/§5/F.1 có2×2repair, oracle tương lai thật; không nhận generic2×2 hoặc việc harm có thể xảy ra là mới | Bổ sung interaction qua negativeΓ dưới oracle không biết future | Giữ có điều kiện qua1–3 | PENDING |

“Prior” ở đây là **đối chiếu note hiện có**, không claim đã đọc lại paper. Vị trí
và mức đọc gốc theo các note; câu “không thấy contrast trong trang đã đọc” không
chứng minh literature không có contrast đó. Không nâng nhãn novelty/G-level.

### SV — ba dòng giới hạn

- Đã biết gần nhất: K-S9/K-F1 ghi decision-aware freshness; P04 ghi policy×staleness.
- Khác còn cần kiểm: **E** fixed-M0 state-repair regret/Cref; **M** current backlog+
  hidden mode so với snapshot cũ, cùng posterior; **R** one-shot load-changing queue.
- Không được nói: “thông tin tươi có giá trị quyết định” là phát hiện mới, hoặc
  tần suất trên discovery là tần suất mạng thật.

### SUB — ba dòng giới hạn

- Đã biết gần nhất: noteWM26§5/F.1/PDF5,22–23 ghi P/C/S/E và repair priority;
  R02§5/Example1/PDF7 ghi harm với approximate policy; R04§3 ghi điều kiện không hại.
- Khác còn cần kiểm: **E** Γ dưới oracle không biết futurew; **M** state hiện tại×
  randomness representation trên cùng true posterior; **R** một quyết định làm đổi tải.
- Không được nói: generic2×2/“fidelity khác decision quality” là mới; chưa thấy
  trong targetednotes=prior không tồn tại; SUB đãkhảthi trước numerics/baseline.

## 4. Các ứng viên khác — đề xuất, không thêm phép kiểm

| MD | Phần lớn trùng câu hỏi MV; conjunction chưa preregister; không chọn thêm |
|---|---|
| J | Một phần bịS12ép; không gán tên cơ chế hoặc claim mọi14Jđều bịép |
| AMP | Khác plant; để independent validation, không sửa contract±6 |
| AGE | Time scaling với giả định giữ đúng; không contribution về một chiều mới |
| X | Không cần card riêng; gắn vào cách mô tả differ nếu có evidence phù hợp |
| δ | Lens hậu nghiệm, đồng tuyến headroom; để mechanism phase6 với thiết kế riêng |

## 5. Đính chính các câu dễ thành overclaim

1. Các cột author ở hồ sơL2.9Part1 vẫn trống như snapshot lịch sử, nhưng
   phần **Gate L — nhãn được tác giả xác nhận** vàauthor_attestation26/10 đã
   có PC3/S11/WM26. Không buộc tác giả lặp lại xác nhận cũ. Candidate mới SUB
   vẫn cần lựa chọn PartA hiện tại; PC3 cũ không tựadopt F2 card hoặc novelty.
2. WM26 limitations quote ở **§8/PDF9**, không§9; note đã đính chính.
3. Lậtκ tự nó không là biến trong identity; chỉ khi vùng đối chứng đồng thời
   thỏaGS<0 hoặcGM<1% thì không-SUB mới bịép. Không có theorem cấm mọi thiết kế
   hai vùng. Chọn một vùng hiện nay vì muốn đo support SUB mà không dùng một
   negative control đã được identity bảo đảm; chưa tự chọn vùng thay thế.
4. L4.4 **đã có spec/DL-104**, nhưng experimental gate HOLD. Không làm lại quyết
   định baseline đã duyệt. Hai MV points không là baseline evidence SV/SUB.
5. Nếu không thêmSUB thìκ=.05HOLD có thể hết liên quan tới card mới; vẫn không
   tự đóng L4.3audit hoặc gỡ F1 baselineHOLD/P0-V10 để tínhCF.

## 6. Bộ lọc4–5 chưa có dữ liệu

Native label support, unresolved rates, candidate-region baseline và rho policy
chưa đầy đủ. Tối đa3hộp/ứngviên chỉ áp khi đã có đủ prerequisites và rules khóa.
**Chưa vẽ hộp, chưa đếm p-hat, chưa chọn0/1/2card.**

Nguồn hiện có: [prior boundary](../literature/prior_boundary.md),
[already implied](../literature/already_implied.md),
[freshness](../literature/freshness_decision_value.md),
[author attestation](../../results/lessons/l2_9/gate_l/author_attestation.json),
[T07](../theory/T07_population_estimand.md),
[rules proposal](../../experiments/P4_05_candidates/screening_rules.md).
