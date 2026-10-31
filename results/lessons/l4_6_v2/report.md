# L4.6 (v2) — decomposition trên discovery đã lưu

Người phụ trách: **Doan Van Tai** · 31/10/2026 · AI triển khai theo ủy quyền,
không author-self prediction, human review hoặc Understanding PASS.

**Hoàn tất phần lõi:** script, kiểm tra, quantiles10/50/90 và3figures.
**D22 native DEFERRED**, F/V=null: thiết kế Q-only trong input không khớp
contract giữ(Y,Q). Không có native engine calls hoặc outcomes mới.

## Đã thực hiện và scope

- Đọc nguyên hai phần lesson, giữ bản gốc ở `inputs/`. Attachment code có UUID
  `a33f61c8-c2d5-45e8-ac8a-ed68b3fdc088` không tồn tại tại đường dẫn user gửi;
  không nhận đã kiểm code đó. Script mới bám đặc tả hai phần đã đọc được.
- Dự đoán AI được ghi tại commit59971ae trước lượt phân tích; codef8f9d3c,
  chỉnh tên cờ/ticks20f9006 trước bản output cuối. Dữ liệu là discovery đã tiếp
  xúc, không tuyên bố các dự đoán độc lập hoặc không biết outcomes trước đó.
- Pilot map1/map2/map3age amp6 từ commit574a36f: **1136 raw→1118 unique**,
  18duplicate có numeric outputs khớp. Giữ các age experiments riêng; dùng
  kappa/age vàh/age khi vẽ. Không thêm stage1/2 vào phân phối này; full recount
  chỉ dùng tra nhãn pilot cũ cho native. Không dùng amplitudes4/5/7.
- Native **597 keys** không trùng nhau:497SV(449+/48−),90MV/SH(18/72),10SUB
  đúng danh sách park. SV/MV/SH ở640/4(dt1/480s), SUB640/8(dt1/960s). Plot
  tách3panels, không pool thành phân phối native chung hay prevalence.
- P1 stationary, a=6packet/s,mu=10packet/s,c_sw=0; native tau=1s. Giữ bốn
  costs/normalization của mỗi row: Cref=L11, báo tỷ lệ100G/Cref. delta trên
  hình là lambdaB−lambdaA(packet/s), không phải timestep. Seed không áp dụng
  vì chỉ đọc output tất định; không tạo Monte Carlo hoặc sampling CI.

## Kết quả đo được

Các số sau là **median, đơn vị %Cref**, không phải CI hoặc population prevalence.
Toàn bộ quantiles10/50/90 có trong `analysis/summary.json`.

| Dữ liệu | n | GS | GM | GS\|M1 | GM\|S1 | Gamma |
|---|---:|---:|---:|---:|---:|---:|
| Pilot amp6 |1118|.534607|.014375|.554696|.238615|.117845|
| SV+ native |449|.969564|.008713|1.169907|.150442|.126433|
| SV− native |48|.060593|.004764|.139003|.082598|.074718|
| MV native |18|−2.467445|3.189998|.178876|6.951588|2.525431|
| SH native |72|−4.685250|.000001|−.010328|4.674764|4.668652|
| SUB đã thấy |10|6.775916|11.118557|.056896|4.467259|−6.683420|

**Ba câu có số làm input L4.9:**

1. Trên449SV+ native, GS|M1 cóq10/50/90 **.342879/1.169907/2.180611%**, trong
   khi medianGS=.969564%; chênh hai medians=.200343pp, không bằng median
   Gamma=.126433pp nói chung. Bỏ3raw-flagged points chỉ làm sensitivity riêng:
   446points có medianGS|M1=1.171941%,medianGS=.975746%.
2. Trên pilot, medianGS|M1 của A/AB/C lần lượt **1.677613/.682230/.013852%**;
   AB cóq10–q90=.026992–2.583081%, Gamma median−3.695446%, trong khi C có
   Gamma median+3.950787%. Vì vậy C ở scope này có conditional state value
   nhỏ, còn AB không được gom tất cả thành “state chỉ có tương tác”.
3. Trên đúng10SUB native đã park, medianGS=**6.775916%**, GS|M1=.056896%,
   Gamma=−6.683420%; đối chiếu72SH có medianGS=−4.685250%, Gamma=+4.668652%
   và GS|M1=−.010328% với numerical flags. Đây là observation theo support đã
   chọn, chưa tách tác dụng current backlog khỏi quyền biết mode bằng D22.

**Dự đoán:** P1 đúng/P2 sai/P3 đúng/P4 đúng theo file đã ghi, không một hypothesis
confirmation. P2: median marginal lớn nhất tại kappa/tau=.075, n18, giá trị
2.024199%; không thuộc[.1,.3]. Composition age/h/lambda khác giữa nhóm, nên
chưa có một peak có kiểm soát hoặc bằng chứng cơ chế S10. P3: medianGamma
delta<0=.177591% lớn hơn delta>0=.118855%, nhưng tại delta=.5 rangeGamma
−12.492979→+1.796646%; không có luật đổi dấu chỉ phụ thuộc delta từ dữ liệu này.

## Verification và giới hạn số học

- **16 new tests PASS**(.09s); **896 full tests PASS**, lượt cuối84.92s.
  Golden T-A/T-AB/T-C′, S10 toy, D22 semantic toy, bound phản ví dụ, đổi đơn vị,
  corrupt exports/coherent identity giả, partial/CF input và raw flags được kiểm.
- Independent Fraction cost calculation khớp597native rows, max difference
  **2.220446049250313e-16pp**. So exported fields qua costs rồi mới kiểm
  S11; không chỉ dựng lại một vế để tự xác nhận. MaxS11 residual toàn1715rows
  **7.105427357601002e-15pp** với algebra tolerance1e-9pp. NumPy percentile
  độc lập khớp mọi cohort; source SHA và frozen A1/A2/A3/SUB/rules khớp.
- **I2 không PASS như định lý trên các estimate.** Có97negative metric values
  trên54keys:3SV+ và51SH. Native arithmeticFalse50keys(3SV+/47SH), mọi raw
  validity flags giữ nguyên.91/97giá trị âm vượt reported arithmetic width;
  các width này không phải certified total quadrature error intervals.
- Riêng GS|M1 tại P43_0605/0609/0651 lần lượt−.0707448/−.0190386/−.00227329pp.
  Khi thêmSH, minimum là **−.104205109pp** tạiP44_009; không chỉ có3negative
  như scopeSV trong lesson. Tất cả âm có độ lớn<.25pp nhưng đó chỉ là thang
  sensitivity lịch sử, **không** phải chứng nhận nonnegativity/numerics solved
  hoặc bảo đảm mọi class gần threshold. Không clamp zero hoặc refine để cứu.
- Max-bound |Gamma|<=max(GM,GM|S1) không có vi phạm ở tolerance1e-9pp.
  Hướng dẫn suy |Gamma|lớn⇒GM|S1lớn sai khiGamma<0; test phản ví dụ giữ lại.
- Kiểm tọa độ với270CF metadata keys:0collision. SUB chỉ10savedkeys, không
  chạy66keys; CF-v2/R09/R10 không có outcomes mới. Giữ G1/Understanding/L8,
  baseline A3/SV và các gate hiện hành; không nâng toàn map thành nativePASS.

## D22: kiểm đúng information set trước khi triển khai

Contract§3 khóa a_cb(Y,Q)=A(E[gap_hat|Y,Q]); sourcePart2§8 dùngP(mode|Q).
Trong stationary Markov toy được kiểm bằngFraction, giữY choLcb0=9.6,F=0,V=.1;
bỏY choLcb0=10,F=−.4,V=.5 (toy cost). Cả hai thỏaF+V=.1 vàone-hot vềL10=9.5.
Do đó telescoping/one-hot không đủ audit semantics. Không dùng sai policy để
điền số. Production `current` và `old` arrays/export không giữjointY,Q,mode;
nativeD22/F/V vẫn **DEFERRED/null**,0probe calls. Không hứa chi phí3–40sCPU khi
chưa có estimator đúng. Phần SHOULD dừng ở lỗi thiết kế này, không mở mini-project.

## Commands và artifacts

Đã thực thi từ repo root:

```bash
.venv/bin/python -m pytest -q tests/test_p4_06_decomposition.py
.venv/bin/python -m experiments.P4_06_decomposition.decompose --out results/lessons/l4_6_v2/analysis
.venv/bin/python -m pytest -q
```

Outputdir mới bắt buộc để tránh ghi đè; muốn tái lập dùng đường dẫn mới cho
`--out`. Lượt đầu và lượt sau chỉnh field/ticks có numeric summary giống nhau;
không thay selection/threshold sau outcome. Independent checks chạy bằngPython
stdin: Fraction bốn costs, NumPy percentile, SHA mọi nguồn, verify_run năm run,
A2verify và rules_adopted. Kết quả lưu ở verification.json/log.

- [Source](../../../experiments/P4_06_decomposition/decompose.py),
  [tests](../../../tests/test_p4_06_decomposition.py).
- [Dự đoán](../../../notes/lessons/L4.6_v2_predictions.md),
  [diễn giải/chỉnh lý](../../../notes/lessons/L4.6_v2_learning_note.md).
- [CSV1715rows](analysis/rows.csv), [quantiles/diagnostics/D22](analysis/summary.json),
  [provenance/config inputs](analysis/provenance.json).
- [P1PNG](analysis/P1.png)/[PDF](analysis/P1.pdf),
  [P2PNG](analysis/P2.png)/[PDF](analysis/P2.pdf),
  [P3PNG](analysis/P3.png)/[PDF](analysis/P3.pdf).
- [Analysis log](analysis.log), [final test log](tests_final.log),
  [verificationJSON](verification.json)/[log](verification.log).
- Input/config: [Part1gốc](inputs/part1_original.txt), [Part2gốc](inputs/part2_original.txt),
  các prereg frozen gốc được liệt kê/hash trongprovenance; không có config
  simulation mới vì không có run vật lý mới. Không tạo MC logs, CI hoặc nativeF/V.

L4.7 là bước tiếp theo để kiểm clipping; không được gọi các plot này là xác
nhận mechanism hoặc realism. L4.9 nhận ba câu có số cùng limitation và exposure
history, không chỉ nhận những forecast thuận lợi.
