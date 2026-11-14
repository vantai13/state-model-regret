# External validity — Wave 2 report (EV-A2 Δ*, literature, EV-D2 real trace), 14/11/2026

Doan Van Tai — **AI (Claude) điều phối, Codex viết code và đọc literature**, theo ủy quyền "bạn có thể quyết định thay tôi".
- Các thẻ đều `LOCKED_AI_DELEGATED`. Không mentor review, không dự đoán do tác giả viết.
- Nhánh `ext/validity`, không merge main.

## Tóm tắt

| Phần | Câu hỏi | Kết quả theo thẻ khóa | Đọc |
|---|---|---|---|
| **EV-A2** ngưỡng đảo dấu Δ* (30 regime mới) | Luật vòng kín định vị được Δ* = −b/a, ngưỡng mà dưới đó state tươi giúp? | **Z1 FAIL 15/30**. Phía harm ở 2Δ*: **30/30**, sai lệch tương đối trung vị 13%. Phía help ở Δ*/2: 15/30 | Luật định vị Δ* đúng khi Δ* ≳ 1,1 T_int (15/16, sau khi mở). Dưới đó, truth vẫn là harm nhẹ |
| EV-A2 (exploration sau mở) | Vì sao? | Xấp xỉ "epoch tách rời với chi phí epoch chính xác" chỉ đạt 16/30, lệch ngược chiều | Truth nằm giữa hai xấp xỉ, do **feedback vòng kín** khi Δ < T_int. Cần đánh giá vòng kín chính xác; chưa có luật zero-fit cho vùng này |
| **Literature W2** | Prior gần nhất cho ba phát hiện của wave 1 | 5 query, 100 kết quả sàng (Claude); 3 nguồn đọc AI-T (Codex) | Xem dưới |
| **EV-D2** trace thật MAWI | Cấu trúc tốc độ thật từ backbone (215,7 triệu gói, lấy mẫu theo flow 1/1000) có giữ kết quả EV-D không? | **D1 40/40, D3 40/40, D4 40/40 PASS. D2 NOT_EVALUABLE**: luật dự đoán trước mọi \|G_S\| < 0,25 pp, và truth xác nhận | Ở τ = 1 s, T_int của traffic thật khoảng 78 s ≫ τ, nên dữ liệu cũ ≈ dữ liệu mới (nowcast β₁ ≈ 0,995). Giá trị state tươi theo cả hai dấu đều không đáng kể |

## Literature (chi tiết: [W2_prior_check.md](../../notes/literature/W2_prior_check.md))

- **Bumpensanti & Wang** (Management Science 2020; arXiv v3; Codex đọc AI-T):
  - re-solve thường xuyên một LP mean-value có mất mát Θ(√T) trong trường hợp xấu nhất;
  - re-solve vài lần kèm ngưỡng thì mất mát O(1).
  - Đây là prior cho câu "cập nhật planner mean-value không tự sửa sai số". Nhưng nó **không** có harm theo Δ, đổi dấu ở Δ ≲ T_int, hay số hạng transient 1/Δ.
- **Soleymani, Baras, Johansson** (CDC 2019; arXiv v1):
  - với model đúng, controller tối ưu là certainty-equivalent, và estimator dự báo từ dữ liệu cũ.
  - Cost bị phạt theo sai số ước lượng ≥ 0. Không có controller lệch, không có chu kỳ quyết định.
- **Mendelson & Kuang** (Operations Research 2026; arXiv v2):
  - ước lượng state cũ có model (emulation) kèm bảo đảm hiệu năng có điều kiện;
  - truyền tin theo sự kiện (ET) là prior.
  - Repo đổi **thời điểm quyết định**, không đổi thời điểm truyền tin.
- **Kết luận theo protocol:** đã tìm theo các query trên; *chưa xác nhận từ các nguồn đã đọc* luật vòng kín bậc một, sự đảo dấu theo Δ/T_int, hay sự đảo dấu theo trigger. Không novelty claim.
- **Câu phải tránh khi viết paper:**
  - "re-solving thường xuyên luôn sửa sai số fluid";
  - "event triggering cải thiện" (nói chung);
  - "xử lý age-aware gây hại" (nói chung). T12 chỉ nói harm cần bất đối xứng **và** bias.

## Tổng hợp wave 1 + 2 cho câu chuyện paper (AI đề xuất)

1. **Luật bậc một** (one-shot T11, vòng kín EV-A) dự đoán zero-fit dấu và độ lớn của giá trị state tươi khi chu kỳ quyết định Δ ≳ T_int. Đã kiểm trên 4 panel mới, 3 lớp traffic tổng hợp và trace thật.
2. **Ba điều kiện cho harm:**
   - twin có bias gần hằng (mù horizon);
   - xử lý dữ liệu cũ bất đối xứng (T12);
   - quyết định ở thời điểm không bị chọn lọc (alarm đảo dấu).
3. **Biên độ của hiệu ứng** theo τ/T_int (L7.5, EV-D2) và Δ/T_int (EV-A). Với traffic thật ở τ = 1 s, hiệu ứng không đáng kể vì T_int ≈ 78 s.
4. **Điểm yếu còn lại:**
   - vùng Δ < T_int chưa có luật zero-fit (EV-A2 FAIL);
   - mới có một trace thật, một mức τ.

## Sai lệch và lỗi (ghi đủ)

- **EV-A2:** ngưỡng 75% do AI chọn; FAIL báo nguyên. Exploration sau mở được ghi riêng và không dùng làm bằng chứng.
- **EV-D2:**
  - nhánh c = 25 bị bỏ **trước khóa**, vì T_int ≈ 26 phút và chi phí bộ nhớ quá lớn; quyết định chỉ dựa trên thống kê train;
  - lần launch đầu vỡ do runner thiếu thư mục `test/`, trước khi có output; đã sửa và chạy lại;
  - extractor cần `-lm` trên VM.
- **Codex W2-LIT:** một số tool MCP bị chặn approval. Codex dùng arXiv qua urllib và `pdftotext`. VoR chưa đối chiếu full text.
- **Test:** nới assertion thời gian chạy (30 s → 120 s) của test MC vòng kín, vì giới hạn này phụ thuộc tải máy và không bảo vệ claim nào.

## Việc mở (đề xuất cho wave 3, tác giả quyết)

1. **EV-D3: τ thực tế trên trace thật.** SNMP 30 s–5 phút cho τ/T_int ≈ 0,4–4. Đây là vùng thực tế mà hiệu ứng có thể lớn. Rẻ, chỉ tái dùng code.
2. Luật cho vùng feedback Δ < T_int: có thể là một đóng góp lý thuyết; khó.
3. Thêm 1–2 trace (DC, ngày khác) để tránh phụ thuộc một trace.
4. Phần chỉ tác giả làm được:
   - tự kiểm T12 và luật vòng kín;
   - viết abstract;
   - quyết nhãn C5/K7;
   - chấm Gate Phase 7;
   - L8 (người đọc thật).
