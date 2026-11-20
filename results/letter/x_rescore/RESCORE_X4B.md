# Chấm lại độc lập X4b

Người phụ trách: **Doan Van Tai**.

Kết quả đối chiếu: **MATCH**. Đã so 1201 trường vô hướng, khớp 1201; 0 sai khác ngoài tolerance.

Script chỉ dùng artifact đã commit trong `results/letter/x4b/` và thẻ được brief chỉ định. Không import module thí nghiệm/chấm gốc. Không chạy lại simulation hoặc truth.

| Phép đọc | Tính lại | Kết quả gốc |
|---|---|---|
| B1, thăm dò | GAIN 6, LOSS 0, UNRESOLVED 3; 9 ô | GAIN 6, LOSS 0, UNRESOLVED 3; 9 ô |
| B2 | STANDS, 70/70 = 100.0% | STANDS, 70/70 = 100.0% |
| B3(a) | NOT_EVALUABLE; 0/8 ô resolved, accuracy = null | NOT_EVALUABLE; 0 ô resolved, accuracy = null |
| B3(b), mô tả | strict chiếm 0.810074821% regret fresh của M0 | 0.810074821% |

## Dữ liệu và cách tính

60 bản ghi test-S, ba regime NEWB1–NEWB3; N=32, K=64, R_dec=64, R_eval=128; τ={300,900} s; h={300,600,900,1200,1800,3600,7200} s. Seed train=7402001, truth=7412001. Giá trị cost/regret có đơn vị Mbit·s.

Dựng lại decisions từ cost M0, h·ŝ và luật tĩnh; exact tie chọn Stay. Reference action lấy từ trung bình R_dec rollouts, rồi đánh giá trên R_eval rollouts riêng. Lấy trung bình `paired_evaluation` theo rollout để tính cost từng action, index theo decision để tính cost từng pipeline; regret = cost − C_ref và G_S = L_stale − L_fresh. Giữ nguyên signed Monte Carlo estimates. Các mảng kết quả lưu sẵn chỉ dùng đối chiếu.

Cổng evaluability: mean(C_ref)/h ≥ 0,001 × 12544.525174 = 12.544525174 Mbit. B1 không loại ô theo cổng này. B2 dùng max(mean regret fresh, mean regret stale), biên 0,05 điểm % C_ref, tối thiểu 20 ô và tỷ lệ đạt ≥95%. B3(a) tính SE theo ngày, cần đồng thời |mean|≥2SE và |G_S|≥0,25% C_ref; cần ≥4 ô resolved để chấm accuracy ≥0,80.

## B1 và so sánh với baseline

Mọi bất đồng nằm ở NEWB3 ngày 19/07/2005. SE dưới đây theo 32 instance trong cùng bản ghi/phía/h; các ô chia sẻ cùng ngày và instance, không phải các thử nghiệm độc lập.

| h (s) | Phía | Bất đồng/32 | Hybrid − Stationary (Mbit·s) | SE (Mbit·s) | Hiệu (điểm % C_ref) | Đọc |
|---:|---|---:|---:|---:|---:|---|
| 900 | fresh | 31/32 | -11002014.237691 | 498290.497737 | -1.979545315 | GAIN |
| 900 | stale_300 | 31/32 | -11002014.237691 | 498290.497737 | -1.979545315 | GAIN |
| 900 | stale_900 | 31/32 | -11002014.237691 | 498290.497737 | -1.979545315 | GAIN |
| 1200 | fresh | 21/32 | -8067164.631061 | 1077521.295524 | -1.451490286 | GAIN |
| 1200 | stale_300 | 20/32 | -7734358.088783 | 1102886.832495 | -1.391609834 | GAIN |
| 1200 | stale_900 | 21/32 | -8067164.631061 | 1077521.295524 | -1.451490286 | GAIN |
| 1800 | fresh | 2/32 | -1041894.753105 | 725243.697210 | -0.187463621 | UNRESOLVED |
| 1800 | stale_300 | 2/32 | -1041894.753105 | 725243.697210 | -0.187463621 | UNRESOLVED |
| 1800 | stale_900 | 2/32 | -1041894.753105 | 725243.697210 | -0.187463621 | UNRESOLVED |

| B2, chỉ các ô có thay đổi | Ngày | τ (s) | h (s) | Hybrid (% C_ref) | Stationary (% C_ref) | Hiệu (điểm %) |
|---|---|---:|---:|---:|---:|---:|
| NEWB3 | 2005-07-19 | 300 | 900 | 0.027665347 | 2.007210662 | -1.979545315 |
| NEWB3 | 2005-07-19 | 300 | 1200 | 0.615606818 | 2.007216652 | -1.391609834 |
| NEWB3 | 2005-07-19 | 300 | 1800 | 1.819764959 | 2.007228581 | -0.187463621 |
| NEWB3 | 2005-07-19 | 900 | 900 | 0.027665347 | 2.007210662 | -1.979545315 |
| NEWB3 | 2005-07-19 | 900 | 1200 | 0.555726366 | 2.007216652 | -1.451490286 |
| NEWB3 | 2005-07-19 | 900 | 1800 | 1.819764959 | 2.007228581 | -0.187463621 |

B2 có 64/70 ô trùng baseline và 6 ô có regret both-side thấp hơn; không diễn giải tỷ lệ 100% là Hybrid có lợi ở mọi ô. B1 tại 1800 s vẫn âm nhưng chưa đạt 2SE.

## B3 và dự báo trước truth

| Regime | τ (s) | h (s) | Ngày evaluable | G_S (% C_ref) | Mean (Mbit·s) | SE theo ngày (Mbit·s) | Dấu train | Resolved |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| NEWB2 | 300 | 3600 | 3 | -0.116572526 | -186189.157140 | 120897.148994 | -1 | False |
| NEWB2 | 300 | 7200 | 3 | -0.145260748 | -232198.736049 | 161776.312548 | -1 | False |
| NEWB2 | 900 | 3600 | 3 | -0.116572526 | -186189.157140 | 120897.148994 | -1 | False |
| NEWB2 | 900 | 7200 | 3 | -0.145260748 | -232198.736049 | 161776.312548 | -1 | False |
| NEWB3 | 300 | 3600 | 4 | -0.022309466 | -36247.420319 | 36247.420319 | 1 | False |
| NEWB3 | 300 | 7200 | 6 | -0.014995445 | -16260.036788 | 43001.378680 | 1 | False |
| NEWB3 | 900 | 3600 | 4 | -0.022309466 | -36247.420319 | 36247.420319 | 1 | False |
| NEWB3 | 900 | 7200 | 6 | -0.015645252 | -16964.643511 | 42532.071597 | 1 | False |

8/8 ô không đạt ngưỡng độ lớn 0,25% C_ref; 8/8 ô không đạt 2SE. Không có accuracy xác định và không thể kết luận luật dấu đã được xác nhận hoặc bị bác.

| h (s) | Bản ghi | Instance | Strict / tie | Tổng regret (Mbit·s) | Strict regret (Mbit·s) | Strict (%) |
|---:|---:|---:|---:|---:|---:|---:|
| 3600 | 7 | 224 | 127 / 97 | 22513828.886322 | 0.000000 | 0.000000000 |
| 7200 | 9 | 288 | 136 / 152 | 29931500.517125 | 424846.408444 | 1.419395624 |

Tổng fresh đếm một lần cho mỗi (record,h), không nhân đôi theo τ: 512 instance, 263 strict/249 tie. Strict regret = 424846.408444 Mbit·s; tie regret = 52020482.995003 Mbit·s; tổng = 52445329.403447 Mbit·s. Strict chỉ chiếm 0.810074821%: có hai bottleneck vẫn chưa loại được sự chi phối của ties trong regret fresh của M0.

Đối chiếu dự báo: F1 sai ở vế đa số UNRESOLVED (thực tế 6 GAIN/3 UNRESOLVED), vế nghiêng GAIN khi resolved phù hợp; F2 đúng; F3 phù hợp với nhánh NOT_EVALUABLE; F4 không đứng (strict <30%). Theo luật inclusion của card, strict cũng <10%. Đây là đọc lại kết quả đã lưu; không thay ngưỡng, chọn subset, fit hoặc thử predictor mới.

## Kiểm chứng và tái lập

- SHA256 NPZ theo receipt: 60/60; raw manifest: 121/121 file.
- 131 input khớp byte với blob đã commit ở HEAD `69e947bc46259316744ce0cfd590471d4bfc7062`; raw commit được score ghi nhận: `f449b8c71664bef326eb2effa323c5874e8f3556`.
- 13 nhóm đối chiếu raw, 672900 giá trị; 0 sai khác; prediction mismatches = 0.
- So mọi trường của `card_verdicts.json`, kể cả rows/cells/by_h và provenance: 1201/1201. 77 sai khác làm tròn trong tolerance; max absolute = 1.19209289551e-07, tại `B3b.rows[9].C_ref_Mbit_s`.
- Tolerance chỉ để đối chiếu số: rtol=1e-12, atol=1e-09; không thêm epsilon vào tiêu chí card.
- Self-test giải tích và ngưỡng: 24 PASS, 0 FAIL, 0 ERROR; bao gồm reference action từ tập rollout riêng, exact tie, signed regret âm, ngưỡng 2SE/evaluability, abstention và phát hiện sai khác lồng nhau.

```bash
python -B experiments/letter/x4b_rescore_independent.py --self-test
python -B experiments/letter/x4b_rescore_independent.py
python -B experiments/letter/x4b_rescore_independent.py --check-only
```

Source: `experiments/letter/x4b_rescore_independent.py`. Kết quả và toàn bộ trường tính lại: `results/letter/x_rescore/rescore_x4b.json`. Báo cáo: `results/letter/x_rescore/RESCORE_X4B.md`. Không tạo CSV, biểu đồ hoặc file log mới; stdout và kiểm tra nằm trong JSON/báo cáo. Không sửa artifact gốc, không commit.

Rescore xác nhận tính tái lập của phép chấm trên raw đã lưu; không kiểm chứng lại simulator hay suy ra external validity, novelty hoặc độ chính xác của Monte Carlo ngoài các kiểm tra này.
