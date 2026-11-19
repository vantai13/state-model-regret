# CARD V7-4: hold ngắn (5–30 phút) trên ma trận GÉANT thật, lợi thế ở horizon trung gian

Người phụ trách: **Doan Van Tai**. Tác giả duyệt P1 với năm điều kiện (20/11/2026) và giao toàn quyền quyết định cho Claude.
Thẻ do Claude viết **trước** mọi outcome. Codex cài đặt. Đây là exploration cho letter v8.4; không đổi verdict đã khóa.
Không sửa paper trước khi có kết quả.

## Câu hỏi
Trên ma trận GÉANT thật 15 phút (cùng pipeline V7-3), ở hold ngắn h ∈ {5, 10, 15, 20, 30} phút (khoảng 1,3–7,8 T_int, với T_int
trung vị 232 s), twin đã hiệu chỉnh (Hybrid) có chọn action có chi phí thật thấp hơn luật tĩnh (Stationary) khi hai luật khác
nhau không? Câu này trả lời ý 4 của reviewer 6: lợi thế ở horizon trung gian hiện chỉ có trên CTMC và GÉANT tổng hợp.

## Đã thấy (exposure)
- Toàn bộ V7-3 (hold 1–6 h, các outcome, H1–H3, F1–F7, phân tích tie). Trong đó trên trace, Hybrid và Stationary trùng
  42336/42336 quyết định ở h ≥ 2 h.
- Kiểm khả thi của Claude ngày 19/11 trên trạng thái đã lưu của V7-3 (seed 7312001), **chỉ dùng gap dự đoán**, không dùng
  outcome: ở ngày ổn định, 86,4% trạng thái có |Δ̂(1 h)| = 0 và 3,4% có |Δ̂(1 h)| > h|ŝ| với mọi h ∈ [5, 30] phút.
- Kết quả paper v8.4: tổng hợp và CTMC có lợi thế ở 1–7 T_int (81/93 CTMC, 69/102 replay ở T_int).

## Giữ nguyên (điều kiện 4 của tác giả)
Giữ pipeline V7-3 (`experiments/letter/v7_3_*.py`, không sửa file cũ; runner mới chỉ gọi lại). Cụ thể:
- dữ liệu SNDlib GÉANT 15 phút; luật loại ngày theo input (ngày 2005-06-27); strata S/O theo input;
- capacity đã hiệu chỉnh trên tập train (12544.525 Mbit/s); ŝ pooled đã huấn luyện (DAY1 −100492, DAY2 −100470, DAY3 −5,75 Mbit);
- profile weekday của M0; điều biến OD hai trạng thái (η = 0,3, flip 1 s⁻¹), dt = 0,05 s;
- N = 32, K = 64, R_dec = 64, R_eval = 128 (CRN cặp); τ ∈ {300, 900} s; tie → Stay (chặt < 0);
- C_ref từ quyết định tham chiếu trên chính ma trận của ngày (stream riêng); cổng evaluable C_ref/h ≥ 12,544525 Mbit (1 ms).

**Chỉ đổi:**
- lưới hold h ∈ {300, 600, 900, 1200, 1800} s;
- seed test mới **7412001** (pilot **7472001**; khác mọi seed cũ);
- chỉ chạy ngày tầng S (29 ngày) cho DAY1, DAY2 và DAY3 (đối chứng). Ngày tầng O không chạy (khai trước).

## Bước 0: kiểm signal chỉ bằng quyết định (điều kiện 1, trước truth, không outcome)
Chạy runner ở chế độ `decisions-only` với đúng seed test, tức cùng các trạng thái lúc quyết định của truth.
- **Được tính:** trạng thái lúc quyết định, mẫu posterior stale, dự đoán fluid, và quyết định của M0, Hybrid, Stationary ở mọi
  h, τ, phía fresh/stale.
- **Không được tính:** rollout đánh giá, C_ref, chi phí thật, regret.

Báo theo từng h (và τ):
1. tỷ lệ quyết định Hybrid ≠ Stationary, riêng phía fresh và stale;
2. tie share của M0 và Hybrid;
3. tỷ lệ |Δ̂(h)| > h|ŝ|.

**Tiêu chí đủ signal (cố định ở đây):** chạy truth nếu, trên DAY1/DAY2 tầng S, tổng số quyết định cấp instance có
Hybrid ≠ Stationary (mọi h, τ, phía) ≥ 50 **và** tỷ lệ bất đồng phía fresh ≥ 1% ở ít nhất 2 trong 5 horizon.
Nếu không đạt: dừng, ghi NOT_ENOUGH_SIGNAL, không chạy truth; paper chỉ báo tỷ lệ bất đồng. Không đổi tiêu chí sau khi xem số.

## Metric (điều kiện 2: ba đại lượng tách riêng)
- **Bất đồng action:** tỷ lệ Hybrid ≠ Stationary theo h, τ, phía.
- **Tie share:** M0 và Hybrid (fresh, stale).
- **Cải thiện regret:**
  - (a) cấp instance, có điều kiện là bất đồng: chênh chi phí thật Δc = V(a_Hybrid) − V(a_Stationary) trên 128 rollout đánh giá
    cặp (CRN), se Monte Carlo = sd/√128; **resolved** nếu |Δc| > 2 se;
  - (b) cấp case (bản ghi × τ × h), both-side regret: R_Hybrid − R_Stationary, đếm tốt hơn/bằng/tệ hơn (bằng nếu
    |Δ| ≤ 1e−9·max(|R_H|, |R_S|)) và chênh trung bình.

  Không suy "không có lợi thế" chỉ từ việc bất đồng ít.

## Quần thể đánh giá
DAY1, DAY2; tầng S (29 ngày); case evaluable (cổng 1 ms, theo từng case h, τ); h ∈ {5, 10, 15, 20, 30} phút; τ ∈ {5, 15} phút.
Instance và case dùng chung ngày, nên các con số là mẫu số, không phải phép thử độc lập. DAY3 là đối chứng mô tả
(ŝ gần 0, kỳ vọng ít bất đồng).

## Giả thuyết và luật đọc (điều kiện 3)
**H-P1 (chính, cấp instance):** trong các quyết định có Hybrid ≠ Stationary thuộc quần thể đánh giá, số resolved mà Hybrid rẻ
hơn (better) so với số resolved mà Hybrid đắt hơn (worse):

| Verdict | Điều kiện | Câu đưa vào paper |
|---|---|---|
| POSITIVE | better ≥ 10 và better ≥ 2·worse | "on real matrices at 5–30 min holds, where the corrected twin and the stationary rule disagree, the corrected choice was cheaper in X of Y resolved decisions" |
| NEGATIVE | worse ≥ 10 và worse ≥ 2·better | nói thẳng rằng ở hold ngắn trên trace, thông tin trạng thái của twin hiệu chỉnh làm tăng chi phí trong X của Y quyết định |
| MIXED | còn lại, với better + worse ≥ 10 | báo hai số đếm, không kết luận lợi thế |
| NOT_ENOUGH_SIGNAL | better + worse < 10 | lợi thế trung gian vẫn chỉ có trên CTMC và GÉANT tổng hợp; báo tỷ lệ bất đồng |

**H-P1b (phụ, mô tả):** bảng (b) theo từng h; không có verdict riêng.

**Độ nhạy khai trước (mô tả):** Hybrid với ŝ chỉ từ ngày ổn định (DAY1 −320,6; DAY2 −314,0 Mbit), cùng rollout.

## Dự báo của Claude (không phải kiểm định)
- F1: bất đồng phía fresh trong khoảng 1–6% ở mọi h.
- F2: H-P1 là POSITIVE, vì trạng thái nghẽn nặng là chỗ thông tin trạng thái có ích.
- F3: tie share của M0 phía fresh ≥ 70% ở mọi h.
- F4: với ŝ chỉ từ ngày ổn định, bất đồng nhiều hơn ŝ pooled.

## Luật đưa vào paper (cố định, bất kể kết quả)
- Câu V-C "the intermediate-horizon advantage rests on the CTMC and synthetic GÉANT results" được thay bằng câu tương ứng với
  verdict H-P1 ở bảng trên, kèm tỷ lệ bất đồng và tie share. Số qua ledger.
- Báo cả finding dương lẫn âm, và giới hạn: điều biến trong slot là tổng hợp, capacity hiệu chỉnh ở tải 0,9, chỉ 29 ngày ổn định.

## Thực hiện
1. **Codex:** runner `experiments/letter/v7_4_short.py` (gọi lại hàm V7-3, không sửa file cũ), tests `tests/test_v7_4_short.py`.
   - Test bắt buộc: chế độ decisions-only không gọi rollout đánh giá hay tính C_ref; ở hold 1 h runner tái lập đúng quyết định
     V7-3 trên 1 bản ghi khi dùng seed V7-3; seed mới khác mọi seed cũ.
   - Output vào `results/letter/v7_4_short/`.
2. **Bước 0** chạy và ghi `signal.json` (bằng code đã commit), rồi Claude chấm theo tiêu chí trên.
3. Pilot thời gian (seed pilot, gồm bản ghi nặng nhất), `predictions.json`, `lock.json`; Claude commit.
4. Truth chạy một lần (local nếu dự phóng ≤ 6 CPU-h, nếu không thì GCP). Raw commit trước khi chấm. Scorer khóa của Codex;
   Claude viết script chấm lại độc lập không import scorer.
