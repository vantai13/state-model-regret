# DL-105 — Giữ SV/SUB có điều kiện qua Part A và khóa luật sàng

Người phụ trách: **Doan Van Tai** · 30/10/2026.
Provenance: **AI soạn, tác giả duyệt trực tiếp**.
Trạng thái: **ADOPTED_BY_AUTHOR_CHOICE**, trước mọi real-box p-hat.

Tác giả chọn nguyên văn:

- “Giữ SV và SUB có điều kiện (khuyến nghị)”.
- “Chọn gói luật sàng đã soạn (khuyến nghị)”.

Proposal commit736633a; [author choices](../../experiments/P4_05_candidates/author_choices.json).
Đây là hai quyết định chuẩn bị trong L4.5, **chưa phải số card0/1/2** của
DL-103#2. Không suy số card hoặc vùng từ yêu cầu triển khai chung.

## Part A được duyệt

Giữ SV và SUB qua identity/prior/giá trịRQ với các giới hạn trong
[candidate filters](PartA_candidate_filters.md). PC3 đã author-attested ởDL-043,
không yêu cầu làm lại L-self cũ; không biến note-only review hôm nay thành đọc
primary mới hoặc novelty clearance.

SV thêm câu hỏi state value dương; riêngGS≥1% không đủ chứng minh model value
nhỏ. SUB đo negativeΓ không bịép bởi AB membership; một vùng theo định hướng
lesson, không theorem cấm mọi minus region. Premise DL-073 thay đổi ở support
discovery đáng xét, không prevalence. Ngưỡng3/162 lịch sử làmin(GS,GM)>.5%.

## Luật sàng được duyệt

n60,π0=.5,α=.025/card, robust conditional power; haircut.10; power≥.5;
UNRESOLVED≤.05 mỗi vùng; tốiđa3hộp/candidate, mỗi hộp ghi mọi kết cục.
SV hai vùng vớip_minus_plan=.2 làgiảđịnh, r_minus đo riêng. SUB một vùng với
Γ/Cref≤−.01. UNDEFINED/khôngresolved xửlýrõ; khôngsilentexclude/doublecount.
Không split/measure weights ởv1. Không dùng pilot thay native.

F1 giữ nguyên; F2 nếu có tốiđa2card α1/40/card, FWER≤1/20, unionF1+F2≤1/10.
Baseline áp đúng vùng/cùng quyềnthôngtin vàđiềukiệnđốithủ, chỉảnhhưởngcâuclaim;
không tự bỏSV khi margin làmcontroller tệ hơn, không sửa verdictv2.

## Phần chưa được quyết định

**Part B BLOCKED** do L4.3/L4.4 HOLD, chưa có baseline/native đúng candidate
support, rho policy hoặc bounds commit. Chưa thửhộp, chưa tínhp-hat. Các bảng
power exact đã chạy chỉ làdesign giảđịnh. Khôngđược ghi “0card” từ thiếu dữliệu.

Chưa chọnfinal0/1/2card, chưavùng/cardv3/CFv3budget/Gate4, chưa tínhCF.
DL cuối về sốcard vẫn cần đủnămbộlọc và tácgiả quyết trước L4.6. G1 giữnguyên.
