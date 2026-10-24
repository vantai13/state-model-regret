# L2.1–L2.3 — đáp án tham khảo và trạng thái tự kiểm

Người phụ trách: **Doan Van Tai** · 24/10/2026 · AI soạn theo yêu cầu thực hiện.
Đây là đáp án tham khảo, không phải bài kín sách, read-back hoặc chứng cứ tác
giả đã hiểu. Không tự điền PASS cho understanding gates.

## L2.1

1. **Topic khác claim?** “State/model và routing” là topic; “trong K2 từng ô có
   (GS−GM)/Cref≥.01” có miền, hướng, ngưỡng và điều kiện bác bỏ. PC4 còn chờ
   metric/baseline ở A05 nên không được nói đã operationalize đầy đủ bây giờ.
2. **Vì sao PC1 làm framing nhưng không giết PC2?** EVPPI functional đã có;
   giá trị theo điều kiện hoặc quan hệ giữa repairs trong regime cụ thể vẫn cần
   kiểm. Điều này chưa xác nhận PC2 mới hoặc đúng.
3. **L-self khác L-2nd/AI-only?** Tác giả phải mở/đọc nguồn mới có L-self. AI
   đọc primary hỗ trợ technical note nhưng không thành tác giả đã đọc.
4. **Vì sao dự đoán trước đọc?** Để lưu belief trước exposure và tránh hồi tố.
   Ở đây đã lỡ thứ tự; hai commit mới không khôi phục được tính mù.
5. **Vì sao hash không ở chính commit?** Nội dung quyết định hash; ghi hash vào
   nội dung lại đổi hash. Ghi receipt trong commit sau, không backdate.
6. **Dự đoán và Gate label?** KEEP/NARROW/PIVOT/DROP là forecasts/decisions khác
   thời điểm. HOLD là thiếu evidence, không phải forecast calibration.
7. **Khi nào dừng đọc/tìm?** Dùng luật đã lưu ở literature/README; nguồn Tier1
   chưa đọc đủ tạo giới hạn/HOLD tương ứng, không thay bằng suy đoán từ seed.

## L2.2

1. **Bốn thế giới?** WS biết realized uncertainty trước chọn; RP chọn tối ưu
   expected true cost; EV tối ưu mean-input objective; EEV chấm action EV bằng
   luật thật. Oracle D15 biết state nhưng không future, nên không phải WS.
2. **Ánh xạ SOB14?** Xi→x, X−i→w, d→a, NB→−C; dùng conditional law cho w|x,
   không bỏ dependence của future với mode hiện tại. T03 có đủ phép dẫn.
3. **Giả định đủ?** G1 matched/shared belief; G2 full state; G3 đúng M1/argmin;
   G4 cùng evaluator/objective; G5 mean rollout conditional theo x. Đây không
   phải tập điều kiện cần cho equality ở mọi instance.
4. **Vì sao EVPPI không âm và khi nào dương?** min E J≥E min J. Hai action cho
   min(E Delta+,E Delta−); cần cả hai dấu strict có positive mass. Delta−1/0
   đồng xác suất cho p_sw=.5 nhưng EVPPI0.
5. **V1?** L00=L01=L11=5/4, L10=3/2; GS−1/4, GM0, Gamma1/4,
   GSgivenM1=0, GMgivenS1=1/4. WS9/8, RP5/4, EV1, EEV5/4.
6. **V2?** L00=3, L01=11/4, L10=L11=5/2; GS1/2, GM1/4, Gamma−1/4,
   GSgivenM1=1/4, GMgivenS1=0. Global VSS0 khác GM1/4; giữ thêm uncertainty
   không bảo đảm approximation-induced action tốt hơn.
7. **Belief sai?** True-law GSgivenM1=EVPPI_D+decision loss của action từ b;
   phần dư≥0, không luôn dương. V2 b_hi3/4 cho 1/2=1/4+1/4. Subjective
   EVPPI_b là giá trị khác, equality có thể tình cờ giữ dù b sai.
8. **Partial state?** Chỉ thành partial-information VOI nếu controller tối ưu
   true conditional expected cost theo thông tin đó. D22 fixed-M0 split không
   tự được gọi EVPPI; full state gồm cả backlog lẫn modes.
9. **Vì sao I2 dễ thành tautology?** Nếu định nghĩa VSS bằng chính action a10
   đang test thì hai vế dùng cùng lỗi. Checker độc lập dựng mean-input action
   từ definition; ignored-mode mutant bị bắt ở 5.730 toy, reused-action checker0.
10. **Tie control?** Matched-belief I1 giữ khi hòa chọn Switch vì hai action có
    cùng relevant expected cost. Đây là equivalent control, không đòi làm đỏ.
11. **EV≤WS?** Không chung: V4 EV1/4>WS1/8. WS≤RP≤EEV giữ bởi thông tin và
    optimality; riêng toy có EV≤RP do convexity/Jensen.
12. **Gamma?** Hai identity difference-of-gains là bookkeeping. Positive Gamma
    có thể do bù sai số, không đủ gọi queue mechanism. H0/H1 phải khóa A05,
    kiểm held-out với cùng thông tin và budget.
13. **Phạm vi code?** H1, hai mode và iid two-point arrivals conditional theo
    mode; exact enumeration không chứng minh mọi horizon/plant hoặc mạng thật.
    Hai phép dẫn là phần tổng quát; test chỉ kiểm implementation ở họ đã khai báo.
14. **Query cho L2.8?** “interaction between partial state information and
    certainty equivalent decision loss”; so riêng conditional VOI khi cả hai
    trục là information với cặp information/approximation của dự án. Đây là
    query seed, chưa chạy thành blind-spot session trong Part A.

## L2.3

1. **P11 đo gì?** §2.4 Eq2.7: expected value học discrepancy dưới joint belief,
   so với input information Eq2.8. EVMI là diễn giải upper bound; không tự bằng D21.
2. **Point0/point1 vì sao cùng VOI0?** Cả hai prior đã chắc về delta nên học
   không đổi belief; chỉ point1 đúng actual delta của toy, nên true loss khác.
3. **GMgivenS1 tại state hi?** Regret(M0)−regret(M1)=1/2−0. Averaging modes
   V1 bằng1/4; không lẫn per-state gain với aggregate.
4. **Có thể nói EVMI0 cho toàn D21?** Phải chỉ rõ mapping. Biết discrepancy
   function thì không còn structural information để học; nhưng delta(x) vẫn
   có thể chưa biết do hidden x. V2 disclosure cho1/4, là state information.
5. **Prior ảnh hưởng thế nào?** VOI là đánh giá trong belief; VOI0 không xác
   nhận model đúng. Prior quá hẹp là một failure mode; same optimal action cũng
   có thể cho VOI0 dù còn uncertainty. P11 §§2.3/6 bàn elicitation/generous priors.
6. **Cận trên nào đúng?** V1 GS−1/4 không upper-bound no-op0 dưới fixed-M0.
   Với cùng information và matched posterior, M1 tối ưu nên model repair gain
   bị GM hoặc GMgivenS1 chặn trên. R00 là cận chung từ ô00, không cận duy nhất.
7. **Câu không claim mới?** So giá trị biết inputs với giá trị học model
   discrepancy để định hướng cải tiến. Khác domain không tạo novelty.
8. **Nếu mở sang sai theta?** Cần version mới cho model/estimator/evaluator và
   intervention D9/D10/D12/D21, theta thật/ước lượng và conditioning tách rõ;
   kiểm lại G1/G3/G5, nonnegativity, predictions/exposure trước chạy. Học theta
   có thể là input VOI của P11, không tự structural discrepancy EVMI. Tác vụ này
   không thực hiện thay đổi scope đó.

Các câu trả lời không xác nhận authorship/read-back. [Checklist hiện tại](../../results/lessons/part_a/report.md).
