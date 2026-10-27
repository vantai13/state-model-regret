# L3.5 / A04 — kết quả và cách đọc

Người phụ trách: **Doan Van Tai** · run27/10, tổng kết28/10/2026. **Hoàn tất kỹ thuật L3.5**;
không tự nhận tác giả Understanding PASS hoặc đóng human-reader gates.

**Kết luận chính:** engine/validity PASS; P5 đứng, P2/P3/P6 không đứng;
không claim chưa phân giải. Đây là kết quả của card trên đúng danh sách,
không xác nhận cơ chế hoặc hiệu quả trong mạng thật. Kết quả âm được giữ.

## 1. Đã thực hiện và thứ tự bằng chứng

- Prereg/source/exposure commit `56c414177af7758849f1a4b46a80d9a0733ca427`.
- Receipt commit `0eb42f20ae1deaa1ed96b65bdb98907bbc4e4bf8`; nguồn A01/A03 không đổi.
- Run `20261027_01`: 38main+8controls/probes×2 mức,92cell-levels mới.
- Đọc validity trước, console chưa in contrast.
- Chấm card và commit `7005a3b1a5e0264be4faf205204f7675bd78f914` trước mở bảng/phân tích discovery.
- Reviewer phiên AI mới kiểm tay M09/P2,M17/P6 mà chưa xem nhãn grader:2/2khớp.
- Tạo ba hình (PNG+PDF), bảng headroom/route/margin, xét5patterns/giữ1candidate.
- Sàng literature20records/2queries có mục tiêu;1đề xuất mới,0PDF/0note mới.
- Không amend card, thay ô/ngưỡng/dt, promote engine vào src hoặc mở A05-T.

## 2. Validity và độ chính xác

| Kiểm | Kết quả | Giới hạn |
|---|---:|---|
| Full tests |348PASS,12test A04 mới|60.71s; không rerun11mutants lịch sử|
| Cell-level |92/92BOUNDED,92hard checks PASS|38main+8controls×2mức|
| Controls |60/60zero D19;6/6zero WD GS_M1|SD/conservation vàWD có scope khác|
| Adjacent pairs |46/46đạt;0flag|dt1/120→1/240; không chứng minh dt→0|
| max e_num/Cref_lower |0.06514874%|cap.25%; M24/ref1|
| max unresolved mass |0.18610940%|cap1%; M24/ref1,oracle/M0|
| max pair change upper/Cref_fine |0.10088363%|cap.25%; M24|
| Thời gian A04 |30.838338s|6worker; chưa bao gồm tests/plots/review|
| Calibration replay |6/6engine records trùng A01|M01/M09/M22,ref1/ref2;tính mới|

Primary dt=1/240s≈4.166667ms là **bước thời gian mô phỏng**, không phải packet delay.
H giữ theo ô: h8→1920slot,h2→480slot ởref2. Exact finite-law expectation,
long double64-bit mantissa, seed=None; không Monte Carlo/CI. Các enclosures
có điều kiện theo input/kernel bounds; validity consistency không là formal proof.

## 3. Chấm card [PREREG-CARD]

| Prediction | Yêu cầu | Kết quả | Bằng chứng tại dt cuối |
|---|---|---|---|
| P2 |≥1% ở mọi M09–M12|**Không đứng**;2/4đứng|M09=.831493%,M10=.705873%;M11=1.495685%,M12=1.620398%|
| P3 |Γ>.5% ở M19,M21|**Không đứng**;0/2đứng|.109601%,.126042%, upper vẫn dưới.5%|
| P5-K |GM≤.5% ở mọi M19–M22|**Đứng**;4/4|0%,.074096%,0%,.025051%|
| P5-Q |Ít nhất1ô M01–M04 GM≥1%|**Đứng**;2/4witness|M01=1.973020%,M03=2.396501%;M02/M04=0|
| P5 tổng |K AND Q|**Đứng**|Hai vế đều đạt|
| P6 |V>0 AND V>F ở M17,M18|**Không đứng**;0/2|V=-.402691/-2.548076 packet·s, cả haiV−F<0|

Các số phần trăm chia Cref=L11 **của chính ô và dt**, không chia L00.
Không dùng “2/4P2đứng” thay yêu cầu ALL. Không loại ô;0HOLD,0excluded.
Các nhãn card không nhạy coarse/fine. Forecast A03 **không có cơ chế preregister**;
không chấm “đúng con đường/sai con đường”, chỉ mô tả route bên dưới.
Chi tiết khoảng có đủ trong [card_details.csv](../../A04/20261027_01/card_details.csv).

## 4. Baseline và các repair, cùng đơn vị packet·s

L00=hiện trạng;L01=model repair;L10=state repair;L11=joint repair/oracle trong mô hình.
Cost thấp hơn là tốt hơn. Bảng chọn cả gain lớn và state-harm; toàn38ô ởCSV/phụ lục.

| Ô |L00 baseline|L01 model|L10 state|L11 joint/Cref|GS|GM|GSM|
|---|---:|---:|---:|---:|---:|---:|---:|
|M01|36.050488643|35.370897166|34.911816480|34.444234192|1.138672162|0.679591477|1.606254450|
|M03|43.848902078|42.862799670|42.024862343|41.147592699|1.824039735|0.986102408|2.701309379|
|M18|335.044455533|335.044455533|336.908985379|334.141613785|-1.864529846|0.000000000|0.902841748|
|M19|661.813499883|661.813499883|661.813499883|661.088936592|0.000000000|0.000000000|0.724563291|
|M20|739.835828203|739.288440873|739.835828203|738.758087794|0.000000000|0.547387330|1.077740409|
|M22|739.835828203|739.650792847|739.835828203|738.621931727|0.000000000|0.185035356|1.213896476|
|M28|239.435083479|239.435083479|239.824676209|238.863208188|-0.389592730|0.000000000|0.571875291|

**Ví dụ M03:** baseline43.848902→joint41.147593, giảm2.701309packet·s
(6.564927%Cref). Model riêng giảm.986102packet·s=2.396501%Cref.
Không diễn giải6.564927%thành tỷ lệ giảm so baseline hoặc delay dài hạn.

**Ví dụ M18:** state repair tăng cost1.864530packet·s (GS=-.558006%Cref).
Joint repair vẫn giảm.902842packet·s=.270197%Cref. Γ=2.767372packet·s
(.828203%Cref) lớn hơn headroom; đó là phục hồi harm trên nhánh state-only,
không phải có thêm2.767372packet·s lợi ích khả thi từ baseline00.

## 5. Điều tôi thấy [DISCOVERY]

- GM>0 và action flip ở4ô M01,M03,M20,M22. ChỉM01/M03đạt1%;M20/M22
  đổi quyết định nhưng margin nhỏ, vẫn equivalent_point ở.5%.34ô còn lạiGMnominal0.
- 18/38ô GS≥1%;2ôGSâm làM18/M28;không ôGS≤−1%.
- 22/38ô GSM≥1%;Gamma chỉ1ô≥1% (M07), không suy queue mechanism.
- 16/38ô R00 upper<1%, nhưng **0/3miền cheap kill**: điều kiện là mọi ô
  của miền đã đăng ký, không chia lại miền sau khi nhìn kết quả.
- Tất cả số đếm practical/equivalent trong mô tả là point labels; card và
  cheap kill dùng numeric intervals. Không tự đổi εR để tăng số ô đạt.

| Miền cheap kill | Số ô | upper(R00/Cref)<1% | max upper | Kết luận |
|---|---:|---:|---:|---|
|core|22|10|6.564927%|Không cheap-kill cả miền|
|spoke_A50|8|5|1.702935%|Không cheap-kill cả miền|
|spoke_h2|8|1|2.458273%|Không cheap-kill cả miền|

Không cần DL NARROW do cheap kill vì không miền nào đáp ứng. R00 chặn
GS/GM/GSM/GS_M1 và repair khả thi từ00; không chặn GM_S1/Gamma.

## 6. Đọc ba hình và diagnostics

[H1 mặt phẳng quyết định](../../A04/20261027_01/figures/H1_decision_plane.png):
trục X=EΔ/Cref,trục Y=EΔhat/Cref (%). Khác dấu là action flip; ở tie0
chọnStay. M01/M03nằm góc phải-dưới;M20/M22nằm trên trụcY=0 vớiX<0.
Màuκ,markerqB,floor*,h2táchpanel. Các điểm sát0có nhãn chồng, traCSV
để phân biệt. T01 giải thích regret từ flip và margin, chưa giải thích vật lý.

[H2 sáu contrast](../../A04/20261027_01/figures/H2_six_contrasts.png):
X=ô theo thứ tự thiết kế,Y=%Cref;dải xám±.5%,đường±1%.Ba nhóm táchpanel;
không nối điểm, không đọc thành tác động riêngκ/η/quantile. Error bars
=100e_num(G)/Cref dùng mẫu số điểm; interval của **tỉ số đầy đủ** traCSV/card.

[H3 headroom](../../A04/20261027_01/figures/H3_headroom.png):
X=ô theo ba miền,Y=R00/Cref,đường1%;một miền cần mọi upper dưới đường để
cheap kill. Cột lỗi thường nhỏ hơn marker; luôn đọc bảng interval khi sátbiên.

Margin table báo q50/q90/q99|Δ|,bias,|EΔ|,E|eM|,E|IΔ| vàF/V ở đủ38ô.
Đây là stratification/diagnostics, không điều chỉnh nhân quả hoặc decomposition
củaGamma thành “phần queue” và “phần geometry”. Flip-mass2D vẫn chưa tính.
D22: F+V=GS dưới fixed-M0;V không là giá trị refresh backlog riêng. M17/M18
cóVâm, bácforecastP6; không phải phát hiện rằng information có thể làm hại.
R04 diagnostic GS=predicted_gain+δold−δnew có max residual0 trong arithmetic
đã chạy; đây là bookkeeping dùng truecost, không feature hợp lệ cho A05.

## 7. Candidate và prior

**5 phát biểu đã xét,1giữ C1** — [hồ sơ đầy đủ](patterns.md).
C1:κ=1,h8 có16/16ô quan sátGM=0; gợi ý kiểm equivalence ở tọa độ nội suy
R05–R08. Không outcome held-out nào được dùng. Candidate là post-discovery,
chưa freeze;λA/MT5/identity/design/precision/horizon đều được ghi giới hạn.
C1 không là bằng chứng mechanism, không thay K5đã khóa trướcA04.
D3 bịM38bác,D4bịM18/M28bác,D1/D5chỉ giữ mô tả. Không chọn lại miền/ngưỡng.
[Tìm có mục tiêu](literature/screening_summary.md):20keywordrecords,1proposal
networking mới,khôngPDF/note/catalog update,không saturation/novelty.

## 8. Điều kết quả KHÔNG có nghĩa

So sánh cùng độ khó không cùngλA;ψ∈[−.2,.05];near-boundary không theo tầnsuất;
p_swthực vàfloorM11/M17/M18hiển thị;h2chỉκ=.3;ĐK1candidate vàcontrols riêng.
**Kết quả định giá cửa sổ [t0,t0+h], không phải long-run loss.** D13 đã có
dt·qH, không có xả sauh/terminal surcharge. Mọi kết luận phụ thuộcD(SR8),
không samplingpopulation/networkdeployment/novelty. AI review không là GVHD.

## 9. Exposure, carry và lesson gate

38main+8controls/probes cảref1/ref2đã được tính và xem sau checkpoint chấm.
A01đã lộ3calibration từ trước;A03card vẫn có trướcA01. Trong chuẩn bị đã
hiện public held-out design λA/p_sw khi đọc bảngcũ; ghi thật trong exposure,
**không** dùng làmfeature và **không** có D/J/gap-magnitude/regret/contrast
held-out mới. Không blanket nói chưa thấy bất kỳ metadata held-out nào.

K5rule duy nhất chưa bịbác nên **carry nguyên văn,m=1** sangA05-F, kể cả
Q-witness chỉM01–M04. [Handoff](../../A04/20261027_01/carry_to_A05_F.json)
không làA05freeze. C1post-discovery táchriêng;H0/H1/metric/budget/split cònchưa khóa.
Track thực thiL3.6mở: đãnote/card/exposure;nhưng không tựchạyA05-T hoặcPhase4.
L8/P0-V10/T05tựviết/Understanding tácgiả giữmở. MemoGVHD chưa gửi,V9waivedDL054.

## 10. Lệnh đã chạy, artifacts

```bash
.venv/bin/python -m pytest tests/test_a04.py tests/test_card_grading.py tests/test_card_batch.py -q
.venv/bin/python -m pytest -q --junitxml=results/lessons/l3_5/preflight/full_suite.xml
.venv/bin/python -m experiments.A04_discovery.run --run-id 20261027_01 --allow-grid --workers 6
.venv/bin/python -m experiments.A04_discovery.score_card --run-dir results/A04/20261027_01
# git commit score checkpoint7005a3b, trước hai lệnh tiếp:
.venv/bin/python -m experiments.A04_discovery.discovery --run-dir results/A04/20261027_01
.venv/bin/python -m experiments.A04_discovery.plots --run-dir results/A04/20261027_01
python3 results/lessons/l3_5/independent_review.py
.venv/bin/python -m experiments.lessons.report_l3_5
```

Toàn bộrun/raw/config/manifest/intervals: `results/A04/20261027_01/`.
Source: `experiments/A04_discovery/`; tests:`tests/test_a04.py`.
Log:`results/lessons/l3_5/A04_run01.console.log`,card_scoring.log,discovery.log,plots.log.
Checks:`verification.json`,preflight/full_suite.log,independent_review.json/.md/.py.
Sốliệu:`cells.csv`(92rows),main_final.csv(38),controls_final.csv(8),
card_scores.csv,card_details.csv,cheap_kill.csv,margin_route_diagnostics.csv.
Figures:H1/H2/H3PNG+PDF. Literature:rawqueries/screen.csv/search_log.
Không cóMonteCarlo log/seed/CI hoặc held-out output vì không chạy những tác vụ đó.

## Phụ lục — đủ38ô tại dt cuối (%Cref)

|Ô|Nhóm|GS|GM|GSM|Gamma|GS_M1|GM_S1|
|---|---|---:|---:|---:|---:|---:|---:|
|M01|core|3.305843|1.973020|4.663348|-0.615514|2.690328|1.357505|
|M02|core|1.345477|0.000000|1.765118|0.419640|1.765118|0.419640|
|M03|core|4.432920|2.396501|6.564927|-0.264494|4.168426|2.132007|
|M04|core|1.403414|0.000000|1.985593|0.582179|1.985593|0.582179|
|M05|core|0.782377|0.000000|1.484450|0.702073|1.484450|0.702073|
|M06|core|1.479422|0.000000|1.505630|0.026208|1.505630|0.026208|
|M07|core|1.264163|0.000000|2.331167|1.067004|2.331167|1.067004|
|M08|core|1.059821|0.000000|1.083779|0.023958|1.083779|0.023958|
|M09|core|0.831493|0.000000|1.452432|0.620939|1.452432|0.620939|
|M10|core|0.705873|0.000000|0.737578|0.031705|0.737578|0.031705|
|M11|core|1.495685|0.000000|2.342320|0.846635|2.342320|0.846635|
|M12|core|1.620398|0.000000|1.751055|0.130658|1.751055|0.130658|
|M13|core|0.864259|0.000000|0.894140|0.029881|0.894140|0.029881|
|M14|core|0.325631|0.000000|0.571851|0.246219|0.571851|0.246219|
|M15|core|0.823522|0.000000|0.890248|0.066727|0.890248|0.066727|
|M16|core|1.031468|0.000000|1.242874|0.211406|1.242874|0.211406|
|M17|core|0.743686|0.000000|0.996985|0.253299|0.996985|0.253299|
|M18|core|-0.558006|0.000000|0.270197|0.828203|0.270197|0.828203|
|M19|core|0.000000|0.000000|0.109601|0.109601|0.109601|0.109601|
|M20|core|0.000000|0.074096|0.145885|0.071790|0.071790|0.145885|
|M21|core|0.000000|0.000000|0.126042|0.126042|0.126042|0.126042|
|M22|core|0.000000|0.025051|0.164346|0.139295|0.139295|0.164346|
|M23|spoke_A50|0.739728|0.000000|0.929071|0.189343|0.929071|0.189343|
|M24|spoke_A50|1.113148|0.000000|1.113957|0.000809|1.113957|0.000809|
|M25|spoke_A50|1.280099|0.000000|1.702935|0.422836|1.702935|0.422836|
|M26|spoke_A50|0.794006|0.000000|0.795574|0.001569|0.795574|0.001569|
|M27|spoke_A50|0.762435|0.000000|0.767122|0.004687|0.767122|0.004687|
|M28|spoke_A50|-0.163103|0.000000|0.239415|0.402518|0.239415|0.402518|
|M29|spoke_A50|1.501683|0.000000|1.548372|0.046690|1.548372|0.046690|
|M30|spoke_A50|0.193726|0.000000|0.591298|0.397572|0.591298|0.397572|
|M31|spoke_h2|1.203644|0.000000|1.463752|0.260109|1.463752|0.260109|
|M32|spoke_h2|0.946034|0.000000|1.039407|0.093373|1.039407|0.093373|
|M33|spoke_h2|2.022827|0.000000|2.458273|0.435446|2.458273|0.435446|
|M34|spoke_h2|1.878706|0.000000|2.030998|0.152291|2.030998|0.152291|
|M35|spoke_h2|1.190495|0.000000|1.265013|0.074518|1.265013|0.074518|
|M36|spoke_h2|0.849686|0.000000|1.071649|0.221963|1.071649|0.221963|
|M37|spoke_h2|1.878546|0.000000|2.009564|0.131018|2.009564|0.131018|
|M38|spoke_h2|0.342994|0.000000|0.714743|0.371749|0.714743|0.371749|
