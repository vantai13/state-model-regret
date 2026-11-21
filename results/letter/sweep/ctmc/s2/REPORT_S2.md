# Báo cáo S2 CTMC

Người phụ trách Doan Van Tai. EXPLORATORY, POST HOC. Raw S1-A ở commit `c34c9ed32`.

Đã chạy summarize trên raw đã commit và phân tích regret theo cặp. 1000/1000 regime COMPLETED, 0 INVALID, đủ 14 h × 3 τ × 8 luật, tương ứng 336000 policy rows và 168000 cặp phía/rate. MMPP/M/1 có 702 regime, fallback M/M/1 có 298. Không chạy truth CTMC mới ngoài hai control X-CTMC cũ.

Δ = regret(luật tĩnh cùng rate) − regret(hybrid cùng rate). Δ dương nghĩa là hybrid có lợi. Đơn vị chuẩn hóa là điểm phần trăm của cùng C_ref, đơn vị tuyệt đối là packet·s. Từng tuổi được giữ riêng. Bảng chính lấy trung bình đều ba tuổi trong từng regime trước khi tính thống kê. CI95% dùng Student t trên regime. Với lưới Sobol thiết kế và đã sàng tài nguyên, các khoảng này chỉ là tham chiếu mô tả, chưa có bảo đảm coverage cho quần thể mạng thực. Các h trong cùng regime phụ thuộc nhau, không được đếm thành các lần thử độc lập.

## Cổng S2

Phần định lượng có vùng phủ ≥10% regime và Δ trung bình ≥0,1 điểm đạt ở 47/56 tổ hợp h/phía/rate khi xét các bin đặc trưng đã khai báo, trượt 9/56. Nếu vùng là toàn bộ 1000 regime thì đạt 32/56. Không dùng tập con chọn bằng outcome làm feature hay vùng dự đoán. Đây là tìm vùng khám phá trên nhiều bin.

Mỗi ô dưới đây ghi Δ trung bình toàn bộ regime và kết quả phần cổng có tồn tại vùng đạt trong các bin. Stale trung bình đều τ/T_int∈{0.3,1,3}.

| h/T_int | Fresh s đúng | Fresh ŝ | Stale s đúng | Stale ŝ |
|---:|---:|---:|---:|---:|
| 0.1 | 0.1097 / PASS | 0.1258 / PASS | 0.0316 / PASS | 0.0451 / PASS |
| 0.2 | 0.3336 / PASS | 0.3617 / PASS | 0.0938 / PASS | 0.1194 / PASS |
| 0.3 | 0.4516 / PASS | 0.4938 / PASS | 0.1417 / PASS | 0.1719 / PASS |
| 0.5 | 0.5117 / PASS | 0.5686 / PASS | 0.1838 / PASS | 0.2243 / PASS |
| 0.7 | 0.4818 / PASS | 0.5492 / PASS | 0.1812 / PASS | 0.2162 / PASS |
| 1 | 0.4151 / PASS | 0.4877 / PASS | 0.1578 / PASS | 0.2028 / PASS |
| 1.5 | 0.3132 / PASS | 0.3852 / PASS | 0.1099 / PASS | 0.1729 / PASS |
| 2 | 0.2395 / PASS | 0.3087 / PASS | 0.0822 / PASS | 0.1442 / PASS |
| 3 | 0.1487 / PASS | 0.2088 / PASS | 0.0497 / PASS | 0.1078 / PASS |
| 5 | 0.0697 / PASS | 0.1188 / PASS | 0.0233 / FAIL | 0.0698 / PASS |
| 7 | 0.0392 / PASS | 0.0810 / PASS | 0.0131 / FAIL | 0.0518 / PASS |
| 10 | 0.0203 / FAIL | 0.0542 / PASS | 0.0067 / FAIL | 0.0385 / PASS |
| 20 | 0.0052 / FAIL | 0.0289 / PASS | 0.0015 / FAIL | 0.0219 / PASS |
| 30 | 0.0023 / FAIL | 0.0200 / PASS | 0.0006 / FAIL | 0.0068 / FAIL |

Cổng tổng giữ `NOT_DECIDED_UNQUANTIFIED_HARM`. Từ “đáng kể” chưa có định lượng, nên không tự gán GO/NO-GO. Không có bin trung bình ba tuổi có mean Δ≤−0,05. Khi xét riêng tuổi, có 3 bin đạt mức sàng ≤−0,05, trong đó 2 bin ≤−0,1. Không tự kết luận ý nghĩa thống kê từ mean hoặc CI sau nhiều phép sàng.

| h/T_int | τ/T_int | Phía/rate | Đặc trưng và bin | n/1000 | Δ trung bình | CI95% |
|---:|---:|---|---|---:|---:|---|
| 3 | 3 | stale/hat | abs_shat_over_abs_s [0.25, 0.5) | 26 | -0.076916 | [-0.207655, 0.053824] |
| 5 | 3 | stale/hat | D_side [0.1, 0.3) | 2 | -0.135349 | [-2.383997, 2.113299] |
| 5 | 3 | stale/hat | disagreement [0.1, 0.3) | 2 | -0.135349 | [-2.383997, 2.113299] |

## Phát hiện và luật vùng

1. Fresh ŝ tại h=T_int có regret tĩnh 0.615431% và hybrid 0.127763% C_ref, Δ=0.487668 điểm, CI95% [0.369768, 0.605569]. Có 234/1000 regime đạt Δ≥0,1, trung vị 0.00001020 điểm. Stale trung bình ba tuổi chỉ đạt 0.202793 điểm.
2. H-A chỉ đứng một phần. Fresh ŝ, Stay và |s|/r_min≤0,1 có 101 regime. Tại h=0,1T chỉ 17/101 đạt Δ≥0,1, còn h=T đạt 64/101 và h=3T đạt 53/101. Với s đúng tại h=3T chỉ 47/97, nên phát biểu cho mọi h≤3T không đứng.
3. H-B có ngoại lệ. Nhóm |s|/r_min≥0,3 ở fresh ŝ, h=T có 48/557 ô vi phạm |Δ|<0,05. Tại h=30T còn 24/1000 ngoại lệ. Tỷ lệ cao các ô gần 0 chưa xác nhận luật đồng nhất.
4. H-C tại fresh ŝ, h=T chọn d*=0.28 chỉ từ 499 ID lẻ. Trong 501 ID chẵn, vùng có 99/501=19.76%, regret tĩnh 2.427720% so với hybrid 0.317065% C_ref. Δ=2.110655 điểm [1.284329, 2.936981], tương ứng 5.588285 packet·s. Có 78/99 đạt Δ≥0,1 và 0 regime Δ≤−0,05.
5. 15 hàng regime×h×phía×rate thuộc 7 regime có Δ≤−0,05 sau trung bình tuổi. Xét riêng tuổi có 52 hàng thuộc 8 regime, gồm 42 fresh và 10 stale. Tất cả dùng ŝ và có |ŝ|/|s| từ 0.0536 đến 0.4319. Tệ nhất là S1A_0414, stale h=3T, τ=3T, Δ=-1.576391 điểm, -4.301204 packet·s. Quan hệ này phù hợp rủi ro hiệu chỉnh thiếu do |ŝ| nhỏ. Cơ chế nhân quả chưa được can thiệp kiểm tra.

Tại fresh ŝ, h=T, Spearman theo 1000 regime lần lượt bằng -0.6244 cho |s|/r_min, 0.4608 cho min κ/T_int, -0.6017 cho chênh tải, và 0.9703 cho share bất đồng. Đây là tương quan mô tả. D(h) tổng và share bất đồng là hai đặc trưng khác nhau. D tổng bằng D_fresh+D_stale, có miền [0,2], được trung bình trên ba tuổi ở luật H-C. |ŝ|/|s| là chẩn đoán dựa trên s của mô hình, chưa dùng được làm bộ lọc triển khai khi không biết s.

## Kiểm tra, thời gian và file

Lệnh chính đã chạy là `python3 -B -m experiments.letter.sweep_ctmc summarize --out results/letter/sweep/ctmc/v2 --source run`, `python3 -B results/letter/sweep/ctmc/s2/analyze_s2.py`, và `python3 -B results/letter/sweep/ctmc/s2/audit_s2.py` sau khi source env. Pytest chạy file test S2 mới cùng test tái lập hai regime cũ, 18/18 PASS trong 4,70 s. Chấm lại độc lập PASS 5,133,099 kiểm tra, không import analyzer/evaluator. X-CTMC_001 so 24 hàng, X-CTMC_002 so 16 hàng, max sai lệch 0. SHA raw khớp receipt và commit, runner/tests cũ giữ nguyên.

S1-A theo receipt dùng 48613.505190 CPU-s worker, tương đương 13.5038 CPU-h. Hai shard chạy đồng thời, wall lớn nhất 1788.290573 s. CPU/wall lệnh phân tích cục bộ có trong `*_execution.json`, `input_audit.json`, `report_timing.json` và `FINAL_CHECK.json`. Không coi tổng thời gian lệnh là thời gian làm việc tương tác.

Source mới gồm `analyze_s2.py`, `test_analyze_s2.py`, `audit_s2.py`, `report_s2.py`. Cấu hình ở `analysis_config.json`. Bảng theo h/tuổi ở `by_h.csv`, `by_h_and_age.csv`, cặp gốc ở `paired_by_age.csv`, trung bình regime ở `paired_regime_h.csv`. Bin, tương quan và H-A/B/C có CSV cùng tên. `harm_region_screen.csv` giữ toàn bộ sàng, `harm_regions_by_age.csv` giữ các bin tuổi âm. `harm_regions.csv` của lượt đầu chỉ có newline vì không có vùng trung bình tuổi đạt mức sàng, không dùng làm bảng có schema. `harm_by_age.csv` và `harm_regime_h.csv` giữ ô thiệt. Log ở `analyze_s2.log`, `audit_s2.log`, `pytest_validation.log`, `report_s2.log`, log summarize ở `../summarize_run.log`. Số dùng trong báo cáo được chép từ CSV vào `key_numbers.json`.

Ba PNG là `delta_by_gap_h.png`, `delta_by_kappa_h.png`, `delta_by_estimator_ratio_h.png`. Màu có giới hạn bão hòa, số đầy đủ giữ ở CSV. Khi đọc CSV bằng pandas, dùng `dtype={'level': str}`, `low_memory=False`, `float_precision='round_trip'` để giữ nhãn true và tọa độ h.

## Đề xuất tiếp theo

`S3_CANDIDATES.md` là thẻ nháp cho fresh ŝ tại h=T với D tổng≥0,28, kèm hai lựa chọn lân cận. Nghiên cứu còn một số hạn chế. Thứ nhất, split ID vẫn nằm trong lưới khám phá và việc chọn h cho thẻ là post hoc. Thứ hai, CI chưa hiệu chỉnh cho việc xét nhiều vùng và chưa chứng minh sai số numerical dùng chung đã hết. Cuối cùng, cần chốt điều kiện thiệt hại rồi khóa S3 trên regime/seed mới trước khi có claim xác nhận.
