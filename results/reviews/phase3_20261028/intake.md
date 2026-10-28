# Tiếp nhận review Phase 3 (AI review do tác giả dán, 28/10/2026)

Người phụ trách: **Doan Van Tai**. Review được viết bởi một phiên AI khác, dựa trên commit
`1f620ec`. Đây không phải review của người thật, không thay P0-V10/L8. Văn bản review chỉ có
trong hội thoại, không lưu byte-exact ở đây. Hai script đi kèm được lưu nguyên văn trong thư mục này.
AI (Claude) kiểm lại theo ủy quyền của tác giả, chỉ đọc dữ liệu đã lộ (A04 main, A05-T R).

## Số liệu của review đã kiểm lại

| Claim | Kết quả |
|---|---|
| Ba chế độ: main 32 cùng dấu / 4 mù / 2 đảo; R 7/1/2 | Khớp. Mù: M19–M22, R04. Đảo: M01, M03, R01, R11 |
| G_M > 0 ở 7/48 ô | Khớp: M01, M03, M20, M22, R01, R04, R11 |
| EΔ̂/EΔ ở ô cùng dấu: trung vị 1,74, khoảng 0,71–2,87, > 1 ở 36/39 | Khớp (1,743) |
| Spearman(E\|e_M\|/stakes, G_M\|S1/stakes) ≈ −0,41 trên main | Khớp (−0,413) |
| Ô mù: EΔ̂ = 0; E\|e_M\| = E\|Δ\| | EΔ̂ = 0 chính xác; hai đại lượng lệch khoảng 10⁻¹⁸, trong cận số 10⁻¹² |
| K5: 20–67% stakes nhưng 0,11–0,16% C_ref; R04: G_M = 77% stakes | Khớp |
| Toy ở phụ lục | `toy_output.txt` khớp từng số được trích |
| Lens hằng số sai từ 0,002 đến 900 lần | Khớp (M24 0,002; M07 900,5) |

## Điều review không nói nhưng output cho thấy

- **Lens sai theo cả hai chiều.** Trung vị actual/lens = 0,958. Lens dự báo thừa hơn 2 lần ở
  11/32 ô cùng dấu, và dự báo thiếu hàng trăm lần ở M07, M22, M30, M16. Docstring của script giả
  định một chiều ("sai số nằm xa biên"), nhưng dữ liệu cho thấy cả xa biên lẫn dồn tại biên.
- **Ở toy population, Γ̄ âm ở mọi dòng có b < 0** (mục C và D của `toy_output.txt`). Câu "dấu của
  Γ̄ là đại lượng thực nghiệm" vẫn đúng về nguyên tắc; toy này chỉ không minh họa được trường hợp Γ̄ > 0.

## Lưu ý trước khi làm bước 1 của review

1. **Bước 1 không mù.** Nhãn ba chế độ đã được thấy trên chính 38 ô main, nên kết quả chỉ là kiểm
   tính nhất quán (DISCOVERY). Xác nhận cần mẫu regime mới.
2. **Guard.** Guard đã khóa chỉ biết A01/A04/A05-T và nằm trong receipt A01, nên không sửa.
   Bước 1 dùng mức truy cập "A04" (chỉ ô main), ghi rõ trong DL-062 và manifest.
3. **Literature.** Review tự báo 12 lượt tìm và 13 lượt mở trang. Các lượt này **chưa** được ghi vào
   `notes/literature/search_log.md` vì không có log gốc. Ba đề xuất nguồn mới vẫn chờ tác giả duyệt.
