# Proposal cho L3R.5 — chưa adopt vào contract

Người phụ trách: **Doan Van Tai** · 29/10/2026.

Đề xuất câu phạm vi:

> Kết quả trong plant fluid hai đường, nền Markov hai mức với a/c=.6,
> buffer vô hạn, action tức thời, ideal backlog observation. S1 thấy cả hidden
> modes và là oracle information benchmark; không phải telemetry repair có thể
> triển khai. L3R.4 envelopev1 (6bef959, exportfix830a187) chưa có đủ ranges
> tương thích cho hai bối cảnh DL-008; realism cả MV và SH vẫn HOLD_UNSOURCED.

S1 có thêm thông tin không bảo đảm GS≥0 khi quyết định vẫn qua M0 sai;
không diễn giải mọi state-gain là giá trị thông tin có thể đạt trong triển khai.

Các cột nên carry sang CF khi contract/frame được tác giả chọn:
nhãn realism từngcontext+versioncommit; buffer flag+budget/proxy rõ scope;
actuation flag+corr; mode-oracle flag+corr overage; source/UNSOURCED reason.
Không gán B_t/d_act giả định thành measured parameters.

CF frame chưa chọn. Lọc(IN/EDGE) hiện không có ứng viên được chứng nhận do
thiếu nguồn, không đồng nghĩa không có regime khả thi. Phân tầng có thể giữ
UNSOURCED riêng nhưng claim phải nói chưa sàng lọc được realism; cần quyết định
L3R.5/L3R.7 và ngân sách, không coi recommendation trong lesson là author selection.
AuditL3R.3 HOLD/numericsNOT_FROZEN không được tự bỏ qua. Không sinh hoặc chấm CF.
