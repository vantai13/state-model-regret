# Phase 5 Closeout — L5.3, 02/11/2026

Người phụ trách: **Doan Van Tai**. AI soạn và chốt theo ủy quyền hiện có của
tác giả; không ghi tác giả tự viết, tự đọc, tự chứng minh hoặc human review.
**Gate C: NARROW → bàn giao Phase 6; G1 giữ nguyên.** DL-128 là quyết định
sau outcome. Báo cáo và closeout gộp trong file này theo L5.3 Part 3; template
§17 lấy từ PHASE_5 do tác giả gửi, không nhận đã áp đầy đủ master plan thiếu.

## What I understood

Read-back **AI theo ủy quyền**, không phải Understanding test của tác giả:
verdict phải đi cùng estimand, acceptance, mẫu số và exposure. Lý thuyết đơn
giản → prior gần nhất → khác biệt giả định thực sự đổi kết quả là ba bước
thu hẹp claim; khác metric hay tên bài không tạo novelty. S|M1 và M|S1 là
hai simple effects khi yếu tố kia ở mức tốt; không trả lời chi phí đầu tư RQ3.

## What changed in my mental model

Tóm tắt AI theo ủy quyền, chưa có author self-writing/read-back mới:
acceptance cần được thiết kế trước theo estimand; thay acceptance sau outcome
là design revision phải báo, kể cả hợp lý và đối xứng. Một limit check phù
hợp stationary intuition vẫn hữu ích nhưng chưa đủ cho claim contribution.
R6 diagnostic không phải error bound; metric gộp có thể che composition.
Không đổi forecast cũ, không biến numerical zero thành theorem về true S.

## Decisions made

- V1: runner `3331d163`, Gate4 `8a8644f1`, raw `5a2f0baf`, DL-124/125:
  INCONCLUSIVE/SECOND_U; 2/12 điểm, 6 calls, 360.523961130 CPU-s. Cuối cùng.
- V1.1: source/amendment `6058b077`, Gate `f14ef9c6`, raw `a609e79b`,
  DL-126/127: một declared revision trước 10 điểm còn lại; acceptance theo
  contrast và Cref delta report-only; N10, cùng tolerances/levels/engine.
  30/30 calls, H-L1 PASS 10/0/0, H-L2 PASS exploratory; 1269.059224554 CPU-s.
  Tổng hai panel 1629.583185684/28800 CPU-s; anchor riêng như prereg.
- STRICT_NO_RETRY/no resume/refine/v1.2 giữ nguyên. Không sửa bất kỳ byte
  source/tests/data/lock/predictions cũ trong L5.3; không gọi native engine.
- DL-128 chọn NARROW, giữ G1 và PIVOT-watch theo ủy quyền, sau outcome;
  không ghi author-attested hoặc author-self khi chưa có xác nhận thực tế.

## Evidence created

### H-L1, S tuyệt đối và M trên cùng tọa độ

V1 chính thức INCONCLUSIVE; v1.1 PASS 10/0/0 theo luật riêng. Bảng dưới là
**numerical estimates tại main (640,4)**; costs đơn vị packet·s, S/M tương
đối là %Cref. S=(L01−L11), M=(L10−L11), Cref=L11; không clamp số âm.
Hai coarse levels (320,4)/(640,2) chỉ dùng đúng acceptance đã khai.

| ID | (λA;λB) | h/κ | Cref | S (packet·s) | S (%Cref) | M (%Cref) | M (packet·s) |
|---|---|---:|---:|---:|---:|---:|---:|
| P5_03 | (6;6.5) | 640 | 8.237371 | +0.000000000 | +0.000000000 | 4.660112 | 0.383871 |
| P5_04 | (6.5;6) | 320 | 4.123705 | -0.000027217 | -0.000660001 | 4.425564 | 0.182497 |
| P5_05 | (6.5;6) | 320 | 16.481654 | -0.000138299 | -0.000839110 | 4.409556 | 0.726768 |
| P5_06 | (6.5;6) | 640 | 8.242393 | -0.000028029 | -0.000340063 | 4.536443 | 0.373911 |
| P5_07 | (7;8) | 320 | 9.606943 | +0.000000000 | +0.000000000 | 16.214597 | 1.557727 |
| P5_08 | (7;8) | 320 | 38.406944 | +0.000000000 | +0.000000000 | 16.270430 | 6.248975 |
| P5_09 | (7;8) | 640 | 19.213886 | +0.000000000 | +0.000000000 | 17.563234 | 3.374580 |
| P5_10 | (8;7) | 320 | 9.856000 | -0.000453191 | -0.004598123 | 9.876626 | 0.973440 |
| P5_11 | (8;7) | 320 | 39.402594 | -0.002471699 | -0.006272936 | 9.849357 | 3.880902 |
| P5_12 | (8;7) | 640 | 19.462993 | -0.000473209 | -0.002431325 | 10.790046 | 2.100066 |

Trên panel, S_est ∈ [−0.002471699394,0] packet·s;
Cref ∈ [4.123705271,39.402593852]; z_est ∈ [−0.006272935744%,0].
M_est ∈ [4.409556324%,17.563233794%], hay [0.182497208,6.248974855] packet·s.
Đây là mô tả **simple effects**, không phải “model quan trọng hơn state”.

- Khoảng cách nhãn tới threshold ít nhất 0.5 pp; d_max=0.019328538386 pp,
  min(distance/d)=25.886079. Tại P5_11, z_est=−0.006272935744% nhưng
  d=0.004033240932 pp. Với invariant true S|M1≥0, đây là **lower bound**
  cho sai khác thật, lớn hơn d; không phải upper bound/CI. Không dùng “80 lần
  sai số thấy được” để bảo đảm true S cách ngưỡng an toàn hoặc máy tính sẽ
  phát hiện mọi hypothesis sai. Một điểm đổi nhãn vẫn giữ PASS là tính chất
  phép đếm 10/0/0, không certificate sai số chung.
- Native discovery cùng tải 7/8, u=1: tại h/κ≈6.67, S_est=0.0867 và
  Cref=7.074; tại 40: 0.0393/43.135; tại 53.33: 0.0177/57.573.
  Panel 7/8 có S_est=0, Cref=9.607–38.407. S tuyệt đối nhỏ chứ dữ liệu
  không chỉ cho thấy mẫu số phình lên. Không suy monotonic ở mọi tải hoặc
  cô lập tác động h/κ. Cref(P5_06)/Cref(P5_04)=1.998783 và
  Cref(P5_05)/Cref(P5_06)=1.999620 chỉ hỗ trợ scaling h·κ trên các cặp này.
- P5_08 MEETS; 9 điểm khác 9/0/0. Nếu giữ N10 và giả sử riêng P5_08 là
  DNM/U, kết quả vẫn PASS. Đây là sensitivity, không verdict N9. P5_08 vẫn
  có exposure W0347; P5_01/02 chỉ mô tả, không gộp thành 12/12.

### Sensitivity của hai thay đổi acceptance

Đếm trên đủ 10 saved points; cột dừng là **mô phỏng** quy tắc U thứ hai,
không thực thi thêm và không sửa verdict v1 N12 hoặc v1.1 N10. Biến thể
bỏ Cref gate được kiểm bằng raw Fractions, không parse reason đã làm tròn.

| Phạm vi acceptance | Gate Cref | M/F/U đầy đủ | Kết quả mô phỏng theo thứ tự |
|---|---|---|---|
| Sáu contrast (luật v1) | Có | 3/0/7 | INCONCLUSIVE, U2 tại P5_04 |
| Sáu contrast | Không | 3/0/7 | INCONCLUSIVE, U2 tại P5_04 |
| G_S_M1 | Có | 7/0/3 | INCONCLUSIVE, U2 tại P5_04 |
| G_S_M1 (v1.1 đã khai) | Không | 10/0/0 | PASS |

**PASS cần cả hai thay đổi** trên bộ dữ liệu này. Lý do khoa học không xóa
việc chọn luật sau khi thấy P5_01/P5_02 trượt. Khi chỉ mẫu số C đổi thành
C(1+ε), G cố định, z'−z=−z·ε/(1+ε), không phải chính xác ε·z;
ε=0.0032 ở threshold 0.005 cho độ dịch ≈0.001595 pp. Tính này không
chứng nhận Cref hội tụ hoặc bound sai số của tử số.

### H-L2 exploratory và composition

Predictions và 1-NN giữ nguyên L4.9; đủ 10 READY riêng G_M_S1.
Ngưỡng: Spearman≥0.7 và MedAE≤0.7·MedAE1NN, cả ba levels.
MedAE đơn vị pp của %Cref, cùng fixed panel; không random-sample CI/p-value.

| K/ref | Spearman | MedAE stationary (pp) | MedAE 1-NN (pp) | Verdict |
|---|---:|---:|---:|---|
| 640/4 | 0.975627893 | 1.143553012 | 2.918238639 | PASS exploratory |
| 320/4 | 0.975627893 | 1.146219825 | 2.915975242 | PASS exploratory |
| 640/2 | 0.975627893 | 1.163940598 | 2.970591140 | PASS exploratory |

Main Spearman stationary/1NN=0.975628/0.943880. Gán mỗi điểm trung bình
truth của cùng cặp tải cho 0.962950: **in-sample post-hoc diagnostic có dùng
outcomes**, không phải baseline dự báo prospective hoặc đối thủ đã freeze.
Panel có 36 cặp giữa nhóm, 9 cặp trong nhóm; rank correlation chịu cấu trúc nhóm.

| Tập mô tả tại main | N | MedAE stationary | MedAE 1-NN | Tỉ số |
|---|---:|---:|---:|---:|
| Cả panel | 10 | 1.143553012 | 2.918238639 | 0.391864118 |
| h/κ=320 | 6 | 1.845243498 | 2.541076784 | 0.726165974 |
| h/κ=640 | 4 | 0.540530366 | 3.284251882 | 0.164582494 |
| Bỏ P5_08 | 9 | 0.935559347 | 3.222417065 | 0.290328448 |

Các dòng subset không tạo hypothesis/verdict mới; riêng ratio 320 vượt 0.7.
Stationary dự đoán cao hơn truth 10/10, relative errors 2.376–18.721% trên
panel. Bốn điểm tải thấp dùng NN key 7|6|1|1/10|16|0, khác cặp tải; NN dùng
feature scaling đã freeze, không thay sau kết quả. Ở bốn điểm tải cao x320,
1-NN có absolute error thấp hơn stationary. Aggregate PASS có composition
và baseline limitations; không suy predictor chính xác hoặc thắng ngoài panel.
Forecast DL-126 **H-L2 FAIL** giữ nguyên; hướng giảm gap khi x tăng là
một cách giải thích hậu nghiệm, chưa xác nhận cơ chế khiến forecast sai.

Post-hoc gap·x: 7/8=864.059–866.278; 8/7=589.282–598.758;
6.5/6=68.989–69.202 pp. Dạng gap≈c/x là candidate bàn giao, chưa freeze
hypothesis mới hoặc kiểm h/κ=1280. Code predictor còn dùng a_M0,h trong
misclassification probability; không đồng nhất toàn predictor với hằng M∞
độc lập h. Suy tỉ số x0/(x−x0) cần thêm giả định c và anchor cùng asymptotic
form; chưa phải theorem cho plant. Không refit hay tiêu thêm reformulation budget.

### Closest-prior check (targeted, không novelty search)

Đã kiểm Crossref 3 DOI; đọc lại 9 PDF pages, SHA khớp catalog. Mức đọc lượt
này **AI-T**, không L-self; không tải/đề xuất nguồn mới, không đổi Excel/catalog.
P13 journal PDF36 trang; M00 submission28 trang chưa đối chiếu VoR; P04 journal15 trang.

| Nguồn và vị trí primary đã xem | Kết quả nguồn | Giới hạn khi áp sang repo / ảnh hưởng claim |
|---|---|---|
| [P13](https://ir.cwi.nl/pub/25530/25530.pdf), §2.1 tr272/PDF4; Eq2.4/2.7 tr275/PDF7; Thm1 tr276/PDF8; Prop4–5 tr282/PDF14; DOI [10.1007/s11134-016-9511-0](https://doi.org/10.1007/s11134-016-9511-0) | Fixed μ>λ và moment assumptions: average correction A/T+O(T⁻²); stationary optimizer gap O(T⁻²) trong normalized objective. Nhân T cho cumulative gap O(T⁻¹). | Lévy input, continuous capacity và average objective khác correlated ON/OFF, binary routing, conditional state information và cumulative regret. Analog cho transient-fading, không theorem về S của repo hoặc chuyển decay rate. Hướng định tính không claim là phát hiện. |
| [M00](https://www.eecs.harvard.edu/~michaelm/NEWWORK/postscripts/oldinfo-jver-submit.pdf), §3.4/PDF10,12; DOI [10.1109/71.824633](https://doi.org/10.1109/71.824633) | Repeated dispatch theo stale bulletin board có thể herding và thua random trong cấu hình xét. | Khác one-shot expected regret/optimal-information intervention; không đồng nhất M00 với G_S của repo hoặc cho rằng stale information nói chung vô dụng. PDF có legacy font artifacts; dùng qualitative text, không số hóa đồ thị. |
| [P04](https://rtcl.eecs.umich.edu/rtclweb/assets/publications/2001/shaikh2001impact.pdf), §III-A/B tr166/168/170, PDF5/7/9; DOI [10.1109/90.917073](https://doi.org/10.1109/90.917073) | Blocking/flapping và update tradeoffs phụ thuộc connection durations, burstiness, topology. | Holding time khác mode κ, blocking khác regret. Tỉ lệ timescale không phải ý mới; nguồn không xác nhận clean controlled Γ của repo. |
| [T09](../theory/T09_stationary_dominance_limits.md), §1–3; nội bộ, AI-assisted | Expansion và predictor là asymptotic candidates có điều kiện; không uniform finite-h action. | Ergodicity đơn thuần không tự chứng minh cost expansion/integrability hoặc finite-panel accuracy. Không exact-zero/h* chung; không nhận theorem đã chứng minh cho repo. |

T09 cần stability, moment và convergence/integrability phù hợp trước khi
đổi pointwise transient reasoning thành claim trong expectation. Γ=S|M1−G_S|M0
là identity **ở mọi regime**, kiểm algebra 10/10 main rows; S|M1 nhỏ chỉ cho
approximate cancellation. Không uniform oracle action không tự chứng minh
S|M1>0 cho mọi finite h; còn cần posterior straddle như T09§2.

## Assumptions still open

Realism/L4.8 UNRESOLVED (h32τ ngoài dải minh họa); c_sw>0, amplitudes khác6
chưa được Phase5 validate; một số amplitude cũ đã explored, không tự coi là
fresh held-out. D22 native F/V DEFERRED; L8/human review/Understanding không
tự đóng. Expansion, positive asymptotic model gain và c/x cần điều kiện riêng.

## Risks still open

- Post-hoc design revision, P5_08 exposure và P5_03 cùng cặp tải đã thấy;
  không independent confirmation, không saturation/literature absence.
- Numerical width không bao mọi discretization bias; d không certified;
  4 raw rows có negative flags giữ nguyên. Root cause chưa được chẩn đoán độc lập.
- L00/Cref error ở P5_01/03/02 lần lượt 0.000474809/0.078166806/0.018454574:
  giữ κ, h×2 → error×164.628; giữ h, κ×2 → ×0.236092. Các load khác h×2
  cho ×1.96–11.00. Đây là error-estimate behavior, chưa chứng minh true error
  hoặc aging cause. Không có validation đầy đủ G_S|M0/Γ trên toàn panel;
  một vài row có thể READY không đủ cho claim interaction toàn vùng.
- Chưa xác nhận novelty từ các nguồn đã đọc; P13 không transfer theorem,
  khác giả định cũng chưa là contribution. PIVOT-watch vẫn mở.

## What I am allowed to claim

**Câu claim được chọn theo ủy quyền, phạm vi hẹp:**

> Trong plant v1.3, hai path rời với nền đổi mode ẩn, a/μ=0.6, u=1,
> c_sw=0 và một action Stay/Switch giữ suốt h, các numerical estimates của
> state-information value khi model đúng M1 đạt ngưỡng ≤0.5%Cref ở 10/10
> tọa độ P5_03…P5_12 có h/κ∈{320,640}, theo acceptance v1.1. V1 chính thức
> INCONCLUSIVE; acceptance v1.1 được khai sau v1 và trước vòng N10. PASS
> phụ thuộc cả scope acceptance và bỏ gate Cref; theo luật gốc, sensitivity
> trên N10 là 3M/0F/7U. Trên cùng tọa độ, model gain khi state là oracle là
> 4.4096–17.5633%Cref. Đây là hai simple effects và lượng hóa finite-panel
> phù hợp với stationary/transient intuition, có analog P13 dưới giả định
> khác; chưa là theorem về plant hoặc contribution/novelty được xác nhận.

Claim đi kèm exposure P5_08, các estimates âm/d diagnostic, ba levels đã khai
và nhãn **validation sau một lần sửa thiết kế có khai báo, exposure một phần**.
State oracle gồm backlog và mode hiện tại, không chỉ refresh backlog; model
gain so conditional-mean rollout M0 với true-law M1 của đúng contract này.

## What I am NOT allowed to claim

Không exact S=0, uniform h*, state vô dụng, model quan trọng hơn nói chung,
12/12, prevalence/CI, independent confirmation, predictor accurate/universal,
Γ đã được validate trên toàn panel, realism, cơ chế đã xác nhận hoặc RQ3.
Không ghi tác giả đã tự đọc/hiểu hoặc author-attested sau outcome từ yêu cầu
“lesson tiếp theo đi”; catalog/author-reading record không bị sửa.

## Gate decision

**NARROW → Phase 6, G1 giữ nguyên, PIVOT-watch.** Bảy mục validity đã kiểm:
(1) source/tests/anchor trước calls; (2) reading/caps/no-retry trước calls;
(3) single run/order/deviations; (4) CPU accounting; (5) labels/rescores;
(6) P5_08 disclosure và 76 outcomes không gộp; (7) claim giới hạn và prior
có vị trí. PASS không là điều kiện validity và không chứng minh true-error bound.
PIVOT-watch: nếu kiểm sau cho thấy không còn kết quả định lượng có giá trị
beyond simple theory, xem lại contribution; không tự nâng hoặc đổi PC/RQ.
Quyết định theo ủy quyền sau outcome, không author-self/human review.

## Next phase

Chỉ bàn giao, **chưa chạy hoặc thiết kế Phase6**: vùng chuyển tiếp discovery
7/8 ở h/κ≈6.67–40 và 6.5/6 ở ≈6.67–13.33; G_S|M0/Γ tại nơi L00 đo được;
c/x coefficient candidate post-hoc; diagnostic numerics L00. Không giả định
mọi effect ở transition đều khác0 hoặc không chịu identity. Full raw v1.1
G_S/Γ nay đã inspected, phải coi là exposed. CF/SUB park, R09/R10 sealed,
76 p4-regions outcomes khác chưa mở. Không v1.2 hoặc engine call trong L5.3.

Kiểm local lượt này: hai printers L5.3 chạy read-only; 63 tests PASS 7.31s;
rescore v1 và v1.1 MATCH, 16 frozen hashes đúng. Full650 đã PASS ở DL-126,
không chạy lại full suite cho docs-only closeout. Không CSV/plot/report riêng.
