# WM26 — tác giả đọc bản giải thích AI; AI kiểm bản giải thích trên PDF (26/10/2026)

Người phụ trách: **Doan Van Tai**. Tác giả gửi trong chat một bản giải thích WM26 do AI
(công cụ khác) viết, kèm câu: *"đây là những gì tôi đã đọc và đưa AI thuật lại"*, và tải
PDF về Downloads (`2610.05550v1.pdf`, 19:17). Bản giải thích lưu nguyên văn ở
[explainer_as_read.md](explainer_as_read.md).

## Phân loại mức đọc (không nâng)

- Tác giả **đã đọc bản giải thích AI** của WM26: author-attested, mức **L-2nd**.
- **Chưa phải L-self primary**: chưa có record tác giả tự mở §4.1/§5/F.1 và tự viết lại
  (PHASE_2 §5.6 luật 4; bẫy §18 số 11). Cột "Mức tôi đã đọc" trong Excel giữ nguyên.

## PDF tác giả tải

sha256 `94201c596276c55c295df09d5b1b34530db7c08617e2b97954311cdd9e38de4a` = **trùng byte**
với bản trong thư viện (`PDF_local/WM26.pdf`, arXiv 2610.05550v1). Không chép lại.

## AI kiểm từng khẳng định của bản giải thích (AI-T trên PDF)

| Khẳng định trong bản giải thích | Kết quả | Vị trí PDF |
|---|---|---|
| Same-start branching: khôi phục cùng simulator state rồi thử nhiều action | ✅ | §3 tr3 "restore the identical state" |
| H đếm model step, mỗi step = 5 environment step; H5, H20 | ✅ | §3 tr3 |
| MSE = center + response, Eq (2)–(3), là đẳng thức không phải xấp xỉ | ✅ | §4.1 tr4 |
| C_j = p_j − p̄ + z̄, S_j = z_j − z̄ + p̄; lưới P=(p̄,r̂), C=(z̄,r̂), S=(p̄,r), E=(z̄,r) | ✅ nội dung; ⚠️ công thức C/S nằm ở lời văn §4.1 và **Eq 10** (F.1), không phải "Eq (2)–(3)" | §4.1 tr4, §5 tr5, F.1 tr22 |
| Ví dụ hai action (goal 0, z=[1,3], p=[6,4]): MSE 13/4/9/0, chọn B/B/A/A | ✅ số học (ví dụ tự dựng của bản giải thích, không phải dữ liệu WM26) | kiểm Fraction trong hội thoại |
| Center ảnh hưởng gap qua 2⟨p̄ − z̄, p_i − p_j⟩ với cost bình phương | ✅ | §4.1 tr4 |
| 14/16 cell center chiếm ưu thế MSE (confirmation) | ✅ "MSE_S > MSE_C in 14/16 cells", 256 start mới | §7.1 tr6; Abstract tr1 |
| 6 trong 14 cell: S tốt hơn C trên cả hai tiêu chí dù nhiều MSE hơn | ✅ "Six of the 14 favor S on both physical criteria" | §7.1 tr6, Table 1 |
| Elite = top 30 | ✅ | F.1 tr22 |
| Oracle là chẩn đoán, không triển khai được; thừa nhận ở **Section 8** | ✅ (§8 "Limitations and Conclusion", tr9) | §8 tr9; §7.1 tr6 |
| Reacher: response error offline +8,44%, CEM success −2,34 điểm, CI cắt 0 | ✅ [−8,07; 3,52] | §7.4 tr9 (Fig.4e,f), Table tr19 |
| Cube: ngay cả E cũng không xếp hạng tốt | ✅ "Cube's encoded-goal cost remains uninformative" | tr1, tr2, tr7 |
| Fixed-pool regret = lỗi vật lý trung bình của tie latent-cost nhỏ nhất trừ lỗi nhỏ nhất trong pool | ✅ | tr4 |
| Γ = G_{S\|M1} − G_S | ✅ đại số bằng D19 (L10+L01−L00−L11) | contract v1.2 D19 |
| Ảnh minh họa (robot arm, DINO-WM, dmc2gym…) | ⚠️ link ảnh từ nguồn khác, **không phải hình của WM26** | — |

Kết luận kiểm: bản giải thích chính xác về nội dung đã kiểm; hai ghi chú nhỏ ở trên.

## Đính chính lỗi của AI repo (phát hiện nhờ bản giải thích)

Các record AI ngày 26/10 ghi câu *"the true-future oracles are diagnostic tools…"* ở
"§9 PDF9". Đúng là **§8 "Limitations and Conclusion", trang PDF 9** (AI nhầm số trang
thành số section). Nội dung trích dẫn đúng; chỉ số section sai.

| File | Xử lý |
|---|---|
| `notes/literature/related_work_skeleton.md` (bản nháp làm việc) | Sửa tại chỗ §9 → §8, có dòng đính chính ở đầu file |
| `notes/literature/author_reading_record.md` (mẫu hướng dẫn đọc) | Sửa tại chỗ để tác giả đọc đúng section |
| `WM26.md`, `prior_boundary.md` (hồ sơ Part1, nhãn tạm, dòng PC3), DL-042, `PHASE_2_closeout.md`, evidence inventory | Giữ nguyên lịch sử, **append đính chính** |
| `results/lessons/l2_9/part1/*` (report, lesson_check, source_access, reviewer view) | Giữ nguyên (record lịch sử); đính chính ở file này |
