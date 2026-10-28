# L3.6 — kết quả chuẩn bị và hai quyết định còn thiếu

Người phụ trách: **Doan Van Tai** · 28/10/2026. Trạng thái: **CHƯA ĐÓNG BĂNG A05-F**.

Đã đọc đủ ba attachment, đối chiếu repo5dd0dca và thực hiện phần không phụ thuộc
cách đọc D25/phạm vi model. Hai câu hỏi đã gửi tác giả; chưa có câu trả lời nên
không ghi tác giả chọnlambdaA hoặc đã khóa H0/H1/C1.

## Đã thực hiện

- Lưu nguyên ba attachment; review-intake phân biệt số reviewer tự báo với số
  local thực kiểm. Không gán review cho GVHD/người thật.
- Kiểm lại headroom/base rates, tái dựng sáu contrast từ bốn summaries A04.
- Thêm **append-only** diễn giải headroom vào noteA04 và claim boundary; scores,
  card,engine,ngưỡng,lưới giữ nguyên. Kiểm147hashes A04 vẫn khớp.
- Viết `ledger.py`: Gaussian closed form, degeneracies, feasibility, strict tie.
- Viết `scoring.py`: ratio-free paired MAE difference interval, D, các trạng thái
  SUPPORT/WEAKEN/FALSIFY/INCONCLUSIVE; đây là bộ toán, chưa là luật nghiên cứu
  được khóa vì margin/missing budget sẽ nằm trong prereg sau quyết định tác giả.
- Tạo kiểm Gauss bằng MonteCarlo và kiểm bất đẳng thức phân biệt trên toy.

## Kết quả đo thực tế

| Kiểm | Kết quả |
|---|---:|
| Toàn bộ tests | **358 PASS**,60,00s |
| Tests toán A05 mới |10 PASS |
| Ô fit/lát từ A04 |38/20 |
| a01 khớp chỉ báo target0,7 |38/38 |
| GM nominal bằng0 |34/38 |
| Upper GM/Cref≤0,5% |36/38 |
| GM/Cref≥1% được chứng nhận |2/38 |
| Tái dựng identity từ raw decimal bằng Fraction:max sai lệch |2,8118260294×10⁻¹⁹ |
| Tái dựng module float64:max sai lệch |1,8865117801×10⁻¹⁷ |
| Ô vi phạm feasibility nominal |0/38 |
| Gauss đối chiếu quadrature độc lập |2/2 test đạt |
| Gauss MonteCarlo |2/2 bộ đạt,mỗi bộ2.000.000mẫu |
| Toy kiểm khả năng phân biệt |100.000 bộ,0vượt allowance float |

MonteCarlo ở đây chỉ kiểm công thức trên dữ liệu Gaussian giả, không tính plant
hoặc outcome lưới. Seeds13601/13602; sai lệch lớn nhất của bốn summaries lần lượt
0,0031620743 và0,0008954009, tương ứng max2,0003 và2,2834 MonteCarlo standard errors,
dưới luật kiểm6SE. Đơn vị toy theo tham số đã khai, không packet·s đo trên lưới.

KiểmD dùng seed13603:1288trường hợp có excess dương do float, max6,66134×10⁻¹⁶;
0trường hợp vượt allowance16eps×max(1,D). Không nói raw excess luôn≤0. Ví dụ
lesson được tính bằng phân số: D=d=19/30, MAE0=5/6, MAE1=1/5 → SUPPORT;
ví dụ gần nhau D=1/20<1/4 → DO_NOT_OPEN. Chưa cóD của ô held-out.

## Cách đọc A04 đã bổ sung

Headroom upper của M19–M22 chỉ0,1096014850%–0,1643461187%Cref, dướiεE=0,5%.
DoGM≤R00, vếK củaP5 đứng đã được baseline headroom chặn. Không nhận rằng điều
đó chứng minh M0 mô tả tốt plant. M19/M21 cóGS=0, nênΓ=GS_M1≤R00, dưới ngưỡngP3.

EΔhat=0 cho a00=Stay nhưng không tự cho từngstatehatgap0 hoặc không cóidle.
Rho0 vẫn tạoGamma>0 vàGS<0 trong golden, nên không gọi nó tự động là strawman.
Kappa là thời gian nhớ,r2_keep dùngexp(−2dt/kappa),không đảo thành rate.

Heuristic K5 hai ô theo equivalence:(36/38)^2=0,8975069252.
Heuristic bốn ô nominalzero:(34/38)^4=0,6408867335.
Nếu C1 khóa equivalence≤0,5%, đúng sự kiện phải là(36/38)^4=0,8055186808.
Đây là các phép tính minh họa dưới giả định độc lập/trao đổi không đúng cho
thiết kế; không phải xác suất thật,p-value hoặc bằng chứng confirmation.

## Còn cần quyết định trước prereg

1. **D25/lambdaA:** (i) không dùng cho cả hai;hoặc(ii) dùng cho cả hai như
   tham sốplant được định nghĩa đồng loạt,claim chỉ về paired prediction trên
   thiết kế neo. LessonPart1§6.7 yêu cầu DL trước prereg vì nó đổi câu đã ghi
   trong hàng đợi/exposure cũ. Quyềninput chung không tự chứng minh hếtendogeneity.
2. **Phạm vi:** shared Gaussian H0/H1,cùngbudget,carryK5+C1,universe12ô và
  8ô nội suy chính như lesson;hoặc chỉ carryK5,chưa làmC1/PC4.

[Bản lựa chọn](../../../notes/lessons/L3.6_decisions_pending.md).
Chưa cóprereg,theta,predictions_heldout/discrimination held-out hoặc freeze receipt.
Không chạyfit/tínhtargetfeatures trước khi tác giả chọn. K5card giữ nguyên,m=1.
Không dựngD/tínhcost/gap/contrast held-out;A05-T chưa chạy. Human gates/Phase4 giữmở.

## Lệnh và file

```bash
.venv/bin/python -m experiments.A05_freeze.audit_fit_data
.venv/bin/python -m pytest tests/test_a05_math.py -q
.venv/bin/python -m experiments.A05_freeze.gaussian_checks
.venv/bin/python -m experiments.A05_freeze.check_discrimination
.venv/bin/python -m pytest -q --junitxml=results/lessons/l3_6/preflight/full_suite.xml
```

Source:`experiments/A05_freeze/`;tests:`tests/test_a05_math.py`.
Logs/numbers:`results/lessons/l3_6/preflight/`:a04_audit.json/.log,
gaussian_MC.json/.log,discrimination_toys.json/.log,math_tests.log,full_suite.log/.xml.
`verification.json`ghi trạng tháiPASS phần chuẩn bị và các bước **chưa làm**.
Không cóCSV/plots/θ/modelconfig/held-outprediction mới vì chưa đến bước đó.
