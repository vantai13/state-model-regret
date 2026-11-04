# Quyết định bộ mốc vùng (L7.3, góp ý (b) của mentor)

Doan Van Tai — **quyết định do AI (Claude) đưa ra theo ủy quyền** ("bạn hãy thực hiện giúp tôi luôn đi, đóng vai trò là tôi
mà thực hiện", 04/11/2026). Tác giả chưa tự cân nhắc hay đọc lại; có thể đổi trước khi khóa thẻ L7.3.

## Vấn đề

Hai bộ mốc đang cùng tồn tại:
- **Bản đồ twin Stage E** ([SUMMARY §4](../../results/explore_ctmc/SUMMARY.md)) dùng h/T_int < 0,3 / 0,3–3 / ≥ 3.
- **Realism v2 §1** dùng h ≲ T_int / T_int–4·T_int / ≳ 4–7·T_int.

Hai bộ đo hai thứ khác nhau:
- Bản đồ twin trả lời "twin nào tốt nhất" và lấy từ truth của 2048 regime.
- Mốc 4–7·T_int trả lời "từ đâu công thức zero-fit đúng tới 0,1 pp", tức là onset của khai triển. Đó là độ chính xác của
  một công thức, không phải lựa chọn quyết định.

## Quyết định

1. **"Vùng" trong mọi bảng của paper dùng mốc của bản đồ twin:**
   - **state:** h/T_int < 0,3;
   - **chuyển tiếp:** 0,3 ≤ h/T_int < 3;
   - **tiệm cận:** h/T_int ≥ 3.
2. **Mốc 4–7·T_int đổi tên thành "onset của z_pred1"** và chỉ dùng cho câu về độ chính xác của công thức zero-fit (claim
   L73-1). Không dùng nó để gán vùng.
3. Mốc "planner dừng đủ dùng ở h > 7·T_int" (claim L73-2) là một ngưỡng thực nghiệm chặt hơn "≥ 3". Nó được kiểm riêng,
   không phải định nghĩa vùng.

**Lý do:**
- Câu thực dụng của paper là về quyết định (twin nào dùng), nên mốc vùng phải đến từ bản đồ quyết định.
- Bộ 0,3/3 đã có truth đứng sau; bộ 1/4–7 trộn hai đại lượng khác nhau.

## Hệ quả cho realism v2 (đính chính nhãn; số h/T_int không đổi)

| Mục | Dòng | Nhãn cũ | Nhãn mới |
|---|---|---|---|
| §3a | (ii) microburst-only, mọi ρ | tiệm cận | tiệm cận (không đổi) |
| §3b | (i) ρ = 0,6, h = 0,5 ms (0,99–3,6) | chuyển tiếp | chuyển tiếp–tiệm cận |
| §3b | (i) ρ = 0,8 (0,26–0,95) | state–chuyển tiếp | state–chuyển tiếp (không đổi) |
| §3b | (i) ρ = 0,9 (0,07–0,24) | state | state (không đổi) |
| §3c | (iii), ρ = 0,3 / 0,5 (a/μ = 0,3) | tiệm cận nếu T_mode ≲ 260–350 s; state nếu ≳ 1.800–2.400 s | tiệm cận nếu T_mode ≲ 610–810 s (10–13 phút); state nếu ≳ 6.100–8.100 s |
| §3c | (iii), ρ = 0,6 / 0,8 (a/μ = 0,6) | ≲ 17 / 4,5 s; ≳ 120 / 31 s | ≲ 40 / 10 s; ≳ 400 / 100 s |
| §3d | (ii) f = 0,1, T_slow = 10 s, h = 5 s (0,52) | state | chuyển tiếp |
| §3e | (ii) ρ = 0,6, h = 5 s (0,40–1,3) | state–chuyển tiếp | chuyển tiếp |
| §3e | (ii) ρ = 0,8, h = 5 s (0,10–0,35) | state | state–chuyển tiếp |
| §3e | (ii) ρ = 0,3–0,5, h = 1 s (1,2–5,4) | chuyển tiếp | chuyển tiếp–tiệm cận |

**Kết luận realism không đổi về chất.**
- (ii) vẫn phụ thuộc việc thành phần nào được coi là mode.
- (iii) vẫn UNRESOLVED. Ngưỡng tiệm cận nay là T_mode ≲ 10–13 phút ở tải IDN, cao hơn độ phân giải 5 phút của log. Nhưng
  thang của phần ngẫu nhiên (8–30% phương sai, LPC04) vẫn chưa được đo.
