# L7.4 — Đóng các mục 3, 4, 5 trong danh sách "còn gì nữa"

Doan Van Tai — **AI (Claude) soạn theo ủy quyền** (04/11/2026), theo đánh giá của mentor về năm mục: hai mục đóng ngay
(3, 4), hai mục để sau (2, 5), một mục nên làm (1). Ở đây đóng mục 3 và 4 bằng dữ liệu đã có, và ghi note đóng Gate D
(mục 5). Không chạy gì mới.

## 3. h của NDT

**Đóng.** NDT không có h riêng. Nó là một thủ tục ra quyết định gắn vào vòng điều khiển mà nó phục vụ: TE, cân tải,
admission. Câu dùng trong paper (nháp, để tác giả viết lại):

> "NDT dùng horizon h của vòng điều khiển mà nó phục vụ; τ là tuổi telemetry vào NDT cộng thời gian NDT chạy."

- Nguồn:
  - realism v2 §0 và §2, dòng (iv): h UNSOURCED, "NDT là thủ tục ra quyết định gắn vào một vòng khác";
  - `NDT_timing_L73.md`: các paper NDT đã đọc chỉ cho thời gian đồng bộ hoặc đánh giá twin (thêm vào τ), không cho thời gian giữ quyết định;
  - YSB21 (AoI).
- Ảnh hưởng claim: không claim nào cần một giá trị h của NDT. Use case được định vị bằng h/T_int của vòng nó phục vụ.

## 4. x* có đổi theo biên độ a không

**Đóng, bằng số đã có.**
- x* là đại lượng zero-fit (đổi dấu + → − của z_∞ trên lát x), tính được cho mọi a.
- Cùng họ (u, λA, κ), a = 3 cho x* lớn hơn a = 6 từ **0,001 đến 0,047**:

  | (u, λA, κ) | x*(a = 3) | x*(a = 6) | chênh |
  |---|---:|---:|---:|
  | (1/2, 8, 1/5) | 0,236 | 0,190 | 0,046 |
  | (1/2, 8, 1) | 0,192 | 0,147 | 0,045 |
  | (1, 7, 1/5) | 0,289 | 0,242 | 0,047 |
  | (1, 7, 1) | 0,243 | 0,242 | 0,001 |
  | (2, 13/2, 1/5) | 0,255 | 0,241 | 0,014 |
  | (2, 13/2, 1) | 0,214 | 0,205 | 0,009 |

  Nguồn: `results/explore_ctmc/l72/compare_amplitudes.json`; SUMMARY §11B. a = 7,5 dùng họ khác (λ ≥ 7,5), không so trực
  tiếp được.
- Mentor tóm là "khoảng 0,01–0,05"; bảng cho thấy có một họ chỉ lệch 0,001.
- Lập luận "x* bất biến theo a" (SUMMARY fluid §5.6) chỉ đúng khi headroom nhỏ hơn nhiều so với a. Nó không mâu thuẫn với
  lập luận "x* dịch theo a"; cả hai đều chỉ là heuristic.
- Biên dải ở h hữu hạn khớp biên của z_pred1 cùng h tới 0,00057 trên 12/12 chuỗi (L72-2, **sau mở**). Vì vậy câu hỏi
  "x* dịch bao nhiêu" trả lời được bằng zero-fit, không cần truth mới.

## 5. Gate D (Phase 6)

**Note đóng (đề xuất, không thay DL-138 trên `main`).**
- **Vấn đề Gate D.** Predictor Phase 6 dùng α·δF với α = h·s + c, và bỏ mất trọng số theo state và tương quan
  (L6.4 diagnosis, DL-137). Gate D = REFORMULATE.
- **Bản sửa đã có trong CTMC.** Theo T11, công thức đúng là G_S = h s ΔF + B + O(e^{−γh}). Predictor Phase 6 chỉ giữ
  hạng đầu h s ΔF (với c), và thiếu đúng B (trọng số bias theo state của các state mà hai quyết định khác nhau) cùng β_C
  ở mẫu số. Luật bậc một đủ hai hạng này đã được kiểm trong CTMC: L73-1, L72-1 a = 3, AS-R1a.
- **Không làm lại trong engine fluid.**
  - Lý do mentor nêu: làm lại rất đắt và không cần cho paper. Paper dùng CTMC làm model chính, còn plant fluid là phần
    khám phá và giới hạn.
  - CTMC cũng cho thấy cơ chế D(ii) (c_sw > 0 gây harm) phụ thuộc representation (F-R2).
- **Còn mở:**
  - DL-138 và Gate D trên `main` giữ nguyên. Note này chỉ đi vào `main` khi merge nhánh Phase 7 có quyết định riêng;
  - tác giả và mentor quyết có ghi DL mới hay không.
