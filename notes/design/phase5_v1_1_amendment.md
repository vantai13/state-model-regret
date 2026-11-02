# Phase 5 v1.1 — một lần sửa thiết kế có khai báo

Người phụ trách: **Doan Van Tai** · 02/11/2026 · DL-126.
AI soạn và triển khai theo ủy quyền tiếp tục phương án B của tác giả.
Commit trước mọi native call v1.1. Không sửa contract hoặc artifact v1.

## 1. Kết quả cũ và diagnostic post-hoc

H-L1 v1 = **INCONCLUSIVE**, SECOND_U tại P5_01/P5_02; DL-125 và raw commit
5a2f0baf giữ nguyên, cuối cùng cho v1. Không chạy lại hoặc chấm lại verdict v1.
Sáu row lưu G_S|M1 = 0 và refinement difference = 0; đây là numerical
estimates, không phải chứng minh estimand thật bằng 0.
Width của G_S|M1 ≤ 1,523846e-9 Cref. Cost error L00/Cref tại main lần lượt
0,0004748085675 và 0,01845457351, vượt 1/4000; P5_01 thêm Cref dt delta
0,003195520706 > 1/400. V1 readiness đòi đủ sáu contrast, kể cả contrast
không dùng trong hypothesis. Sai số L00 khác khoảng 38,87 lần giữa hai
điểm; cả h và κ thay đổi, chưa tách nguyên nhân hoặc chứng minh lỗi aging.

## 2. Acceptance theo estimand và lựa chọn Cref

Với G = G_S|M1 cho H-L1, G_M|S1 cho H-L2, READY khi:

1. Cref > 0 ở cả ba levels. R1 hai trục K và dt:
   max(|G_f−G_c|/Cref_f, |G_f/Cref_f−G_c/Cref_c|) ≤ 1/400;
   không sign flip khi cả hai |z| > EPS_E = 1/200.
2. normalized_error[G] ≤ 1/4000 ở cả ba levels.
3. G/Cref ≥ −1/400 ở cả ba levels.

Giữ cùng tolerances, nhưng acceptance chỉ áp cho contrast cần dùng.
Readiness cả row theo luật cũ vẫn được ghi qua strict_v1_reasons và
strict_v1_label; không gate verdict mới. BUG S11/same-route/cost definitions
vẫn kiểm cả row trước khi phân loại; raw cross-route flags giữ nguyên.
Các lean consistency checks của contrast khác là report-only trong v1.1.

**CREF_DELTA_GATES = False.** Bỏ điều kiện riêng Cref delta ≤ 1/400;
vẫn kiểm cả cost-scale difference và ratio difference của G. Đây là lựa
chọn post-hoc sau P5_01 trượt Cref: tỷ số ổn định không tự chứng nhận mẫu
số hoặc continuous-model accuracy. Báo riêng số đếm theo toàn luật v1
như sensitivity, không chọn luật cho kết quả thuận lợi sau vòng mới.
Đây là amendment phạm vi Phase 5 v1.1 cho R1/lean acceptance; file contract,
numerics rules và plan v1 không đổi. Không mô tả đây là sửa implementation
giữ nguyên design: phạm vi acceptance, Cref gate và panel N đều thay đổi.

## 3. Estimand, labels và vận hành giữ nguyên

H-L1 z=(L01−L11)/L11 tại main (640,4), threshold 0,005.
Levels theo thứ tự (640,4) → (320,4) → (640,2), native evaluator nguyên byte.
R6 dùng d_normalized[G_S_M1] như v1: không READY hoặc |z−0,005|≤d → U;
ngoài vùng biên, z≤0,005 → MEETS, còn lại DOES_NOT_MEET. Giữ số âm,
không clamp, không refine. d chỉ diagnostic, không certified bound/CI.
BUG, execution/resource, budget hoặc U thứ hai → dừng; hai FAIL không dừng.
STRICT_NO_RETRY, một worker/1 BLAS thread, cap 1.800 CPU-s/3.600 wall-s;
call cap giảm theo budget còn lại trừ reserve 1 CPU-s; tính cả controller,
guards, descendants, failed calls và cache. Không resume hoặc tạo v1.2.

## 4. Panel, scoring, budget và exposure

- Đúng P5_03…P5_12 theo frozen protocol, cùng parameters; **N=10** cố định.
  Không sàng theo readiness hoặc prediction.
- state_verdict(planned=10): PASS M≥9 và U≤1; FAIL M+U≤8 và U≤1;
  thiếu điểm, U≥2 hoặc còn lại → INCONCLUSIVE. Không population CI/p-value.
- P5_01/P5_02 đã thấy: nhãn mới chỉ mô tả, không cộng vào N10, không đổi v1.
- P5_08 exposure cũ W0347 giữ nguyên; báo nhãn riêng và số đếm 9 điểm khác
  chỉ mô tả, không verdict N9. P5_03 chung cặp tải với P5_01/P5_02.
- H-L2 exploratory trên cùng N10; model_verdict(planned=10), READY theo
  G_M|S1. Giữ predictor/1NN và 12 predictions đã freeze; lấy đúng 10 IDs,
  không refit. Chỉ chấm đủ 10 READY, ba levels với Spearman≥0,7 và
  MedAE≤0,7·MedAE1NN; cả ba đạt→PASS, cả ba trượt→FAIL, mixed/missing→INC.
- Budget panel chung: 28.800 − 360,523961130 = **28.439,476038870 CPU-s**.
  Code lấy hiệu từ summary v1, không làm tròn tăng budget. Positive control
  riêng không thuộc panel budget, như DL-124; đo và báo CPU riêng.

## 5. Forecast, provenance và điểm dừng

Forecast AI theo ủy quyền, không author-self: H-L1 v1.1 PASS; dự kiến U do
contrast-specific refinement/width vẫn có thể làm INCONCLUSIVE. H-L2 dự
kiến FAIL exploratory do sai số magnitude trên discovery. Không đổi sau run.

Commit code + amendment + DL-126 phần A → test → một native anchor
P43_0379 → gate GO commit → một panel run → commit raw/summary ngay →
rescore cả v1/v1.1, tính verdict độc lập, kiểm 16 frozen hashes → DL-127 fact.
Gate marker phải khóa source commit, amendment SHA và anchor SHA; rescore
không gọi engine. Output/cache v1.1 tách riêng, không sửa results/phase5/.

Đây là lần sửa thiết kế duy nhất: mọi outcome v1.1 đều là điểm dừng;
INCONCLUSIVE không mở v1.2. Evidence chỉ là **validation sau một lần sửa
thiết kế có khai báo, exposure một phần**. Không independent confirmation,
không gộp thành 12/12, không claim exact-zero, Γ hoặc G_S dài-horizon.
Sau DL-127 bàn giao L5.3; chưa tự làm closest-prior check/Gate C trong lượt B.
