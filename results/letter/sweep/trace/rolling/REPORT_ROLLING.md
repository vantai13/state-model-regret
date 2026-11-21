S1-C rolling ŝ, exploratory POST HOC, 21/11/2026. Người phụ trách Doan Van Tai.

Rolling bằng simulation trên toàn lịch sử test đã qua giảm mạnh lỗi do dấu train không khớp test trên panel này. Ở h lớn nhất khả dụng mỗi case, τ=0, uniform, regret trung bình theo 26 case của M0 là 12.762% C_ref, static gốc 28.321%, hybrid gốc 27.450%, rolling sim_all static/hybrid cùng 0.380%. Đây là sửa estimator theo dữ liệu đã thấy. Chưa xác nhận trên dữ liệu mới và chưa thấy lợi ích riêng của hybrid so với rolling static tại lát này.

Đã thực hiện và kiểm chứng

Giữ đúng 6 biến thể với W∈{60 s, 300 s, toàn lịch sử test} × {sim, mm1}. Không thêm biến thể sau outcome. Giữ nguyên từng cost, C_ref, fluid gap, population uniform/alarm và support từ full/. Raw local có 26 case có decisions, gồm 8 OK và 18 FLIP, cùng 1 NOT_EVALUABLE do train T_int unresolved/censored. Con số 25 và 8/17 trong brief không khớp raw hiện có. Lần đếm sơ bộ 9/17 trong commentary và docstring trước run cũng sai, được đính chính bằng case_groups.csv và rescore độc lập. Source đã chạy được giữ nguyên để kiểm SHA.

Seed test là full_seed 311121 + trace_index×100 + 1000000, khớp simulate_case. Tái tạo qA/qB đúng 89,033/89,033 rows, thay cho lấy mẫu mỗi 37 rows trong nháp. Cửa sổ là [max(0,e−W),e], hoặc [0,e], với e=t−τ. Sim tính time-average tổng backlog của hai shadow histories action 0/1 từ đầu test. Công thức occupation là tổng max(0,min(departure,e)−max(arrival,start)). Packet đến sau e đóng góp 0, packet còn chờ ở e được cắt tại e. Departure sau e không làm lộ thời điểm hoàn thành tương lai. Test thay phần tape/service sau e và test cắt occupation đều PASS. M/M/1 đếm background arrivals trên (start,e], dùng u và μ đã cho, với mean number λ/(μ−λ) khi stable. Không burn thêm đầu cửa sổ.

Các sửa đổi trước outcome gồm chấm dấu theo s_test cấp case, lưu riêng độ khớp dấu với từng future, và sửa fallback M/M/1 khi cả hai action unstable. Nháp dùng hiệu overload có đơn vị packet/s như một slope backlog, làm h·ŝ sai đơn vị. Bản chạy chỉ dùng dấu overload dưới dạng ±∞, hoặc 0 khi hòa, và gắn flag. Đây là heuristic khi không tồn tại stationary M/M/1 mean, mọi flag được giữ trong kết quả. Các sửa đổi khác gồm kiểm mọi backlog, lưu support trống, nhận diện từng window duy nhất, đo CPU/wall, chống ghi đè trước compute. Lần khởi chạy đầu FAIL PermissionError ở forkserver socket, trước khi tạo worker hoặc outcome. Đổi multiprocessing sang spawn như runner gốc, rồi test và chạy lại. Log lần lỗi được giữ trong attempt01_startup_failed/.

36 tests PASS trong 2.003 s wall, gồm test mới và regression runner gốc. Command run hoàn tất với 38.301 CPU-s và 12.001 s wall, 6 worker. Bộ đếm nội bộ task+parent là 28.885 CPU-s, không gồm hết overhead khởi tạo/IPC nên dùng command timing làm tổng. Lần lỗi đầu tốn thêm 0.826 CPU-s. Rescore độc lập dùng stdlib, không import scorer, PASS trên 89,033 rows, 1,289 ô có dữ liệu trong 2,646 ô support, 69,888 windows và 96 hash đầu vào. Rescore tốn 7.236 CPU-s.

Cách đọc số liệu

Trong mỗi case×h×τ×population, regret được tính bằng 100×mean(regret)/mean(C_ref), không lấy trung bình các tỉ số từng decision. Đơn vị cost là packet·s. Mọi ô dưới đây ghi trung vị (trung bình) của các tỉ số case, đơn vị % C_ref, các case có trọng số bằng nhau. h lớn nhất khả dụng nằm trong 1, 2, 3 hoặc 10 T_int tùy case. Không coi đây là cùng physical horizon. Nhãn OK/FLIP dùng dấu s_train so với mean((cost_switch−cost_stay)/h) ở h lớn nhất, uniform, τ=0. s_test dùng outcome nên nhóm chỉ có giá trị chẩn đoán. Không loại case mới để khớp count của brief.

Ở h lớn nhất khả dụng, τ=0, uniform

| Policy | OK, n=8 | FLIP, n=18 |
| --- | --- | --- |
| M0 | 9.402 (11.283) | 9.936 (13.420) |
| static | 0.000 (0.171) | 20.679 (40.833) |
| hybrid | 0.000 (0.171) | 20.679 (39.574) |
| static_sim_60 | 2.811 (18.184) | 0.000 (7.326) |
| hybrid_sim_60 | 2.811 (18.184) | 0.000 (7.326) |
| static_mm1_60 | 2.750 (46.089) | 0.000 (9.454) |
| hybrid_mm1_60 | 2.750 (39.427) | 0.000 (7.908) |
| static_sim_300 | 0.000 (2.290) | 0.000 (3.525) |
| hybrid_sim_300 | 0.000 (2.290) | 0.000 (3.525) |
| static_mm1_300 | 1.274 (16.769) | 0.000 (5.227) |
| hybrid_mm1_300 | 1.274 (16.769) | 0.000 (5.242) |
| static_sim_all | 0.000 (0.171) | 0.000 (0.472) |
| hybrid_sim_all | 0.000 (0.171) | 0.000 (0.472) |
| static_mm1_all | 0.000 (0.171) | 0.000 (7.312) |
| hybrid_mm1_all | 0.000 (0.171) | 0.000 (5.499) |

Đếm case tốt hơn/tệ hơn/trong margin, theo đúng thứ tự a/b/c. Margin là 0,05 điểm %, so sánh cùng case và cùng policy static hoặc hybrid gốc. Bảng này dùng cùng điều kiện với bảng trên.

| Policy | OK so với gốc | OK so với M0 | FLIP so với gốc | FLIP so với M0 |
| --- | --- | --- | --- | --- |
| static_sim_60 | 0/4/4 | 7/1/0 | 18/0/0 | 12/2/4 |
| hybrid_sim_60 | 0/4/4 | 7/1/0 | 17/0/1 | 12/2/4 |
| static_mm1_60 | 0/4/4 | 7/1/0 | 18/0/0 | 12/3/3 |
| hybrid_mm1_60 | 0/4/4 | 7/1/0 | 17/0/1 | 13/1/4 |
| static_sim_300 | 0/3/5 | 7/0/1 | 18/0/0 | 14/0/4 |
| hybrid_sim_300 | 0/3/5 | 7/0/1 | 17/0/1 | 14/0/4 |
| static_mm1_300 | 0/4/4 | 7/1/0 | 18/0/0 | 14/0/4 |
| hybrid_mm1_300 | 0/4/4 | 7/1/0 | 17/0/1 | 14/0/4 |
| static_sim_all | 0/0/8 | 7/0/1 | 18/0/0 | 14/0/4 |
| hybrid_sim_all | 0/0/8 | 7/0/1 | 17/0/1 | 14/0/4 |
| static_mm1_all | 0/0/8 | 7/0/1 | 18/0/0 | 12/2/4 |
| hybrid_mm1_all | 0/0/8 | 7/0/1 | 17/0/1 | 12/2/4 |

Độ đúng dấu và bất đồng static với hybrid, trung bình các share theo case, cùng điều kiện trên. Dấu đúng ở đây so với s_test cấp case. sign_local_ok trong CSV chấm riêng với từng future. Với sim_all, local sign accuracy trung bình trên 26 case là 97,077%, dù dấu cấp case khớp 100%.

| Estimator | OK, dấu đúng / bất đồng | FLIP, dấu đúng / bất đồng |
| --- | --- | --- |
| original | 100.00% / 0.00% | 0.00% / 6.24% |
| sim_60 | 89.22% / 0.00% | 84.85% / 0.00% |
| mm1_60 | 84.07% / 1.39% | 81.50% / 3.89% |
| sim_300 | 94.23% / 0.00% | 94.46% / 0.00% |
| mm1_300 | 92.17% / 0.00% | 92.50% / 0.10% |
| sim_all | 100.00% / 0.00% | 100.00% / 0.00% |
| mm1_all | 100.00% / 0.00% | 92.68% / 0.76% |

Đếm flag M/M/1 trên đơn vị case×W×e duy nhất, không đếm lặp cùng window qua các h. Mỗi W có 23.296 windows. Không dùng các windows này như independent trials.

| W | Stable | Một action unstable | Hai action unstable | Tổng flag |
| --- | --- | --- | --- | --- |
| 60 | 20211 | 1068 | 2017 | 3085/23296 |
| 300 | 19158 | 2286 | 1852 | 4138/23296 |
| all | 20035 | 1671 | 1590 | 3261/23296 |

Theo trace, gộp cả hai nhóm, h lớn nhất khả dụng, τ=0, uniform. Sim trong các bảng còn lại là hybrid dùng estimator tương ứng.

| Trace | n | M0 | Hybrid gốc | Sim 60 | Sim 300 | Sim all |
| --- | --- | --- | --- | --- | --- | --- |
| ditl_20230412 | 8 | 23.473 (25.436) | 9.833 (58.799) | 18.515 (31.908) | 6.168 (10.210) | 0.000 (1.223) |
| mawi_20250311 | 9 | 11.208 (10.214) | 15.647 (14.092) | 0.000 (0.000) | 0.000 (0.000) | 0.000 (0.000) |
| mawi_20260414 | 9 | 3.681 (4.045) | 11.241 (12.942) | 0.000 (2.453) | 0.000 (0.010) | 0.000 (0.010) |

Theo h, chỉ nhóm FLIP, τ=0, uniform. Số case giảm khi thiếu tail support ở h dài. Hai hàng khác h có thể khác panel.

| h/T_int | n FLIP | M0 | Hybrid gốc | Sim 60 | Sim 300 | Sim all |
| --- | --- | --- | --- | --- | --- | --- |
| 0.3 | 18 | 5.903 (6.156) | 12.376 (12.551) | 1.008 (4.373) | 0.800 (2.549) | 0.604 (2.502) |
| 0.5 | 18 | 6.099 (6.436) | 14.080 (14.761) | 0.639 (4.357) | 0.646 (2.133) | 0.620 (1.958) |
| 1.0 | 18 | 5.904 (7.201) | 17.986 (17.901) | 0.593 (3.978) | 0.063 (1.560) | 0.063 (1.288) |
| 2.0 | 10 | 7.137 (6.910) | 16.911 (22.024) | 4.354 (4.120) | 0.462 (3.048) | 0.145 (1.960) |
| 3.0 | 7 | 10.331 (9.119) | 26.326 (37.133) | 8.726 (6.222) | 4.651 (5.249) | 0.000 (2.517) |
| 5.0 | 4 | 21.423 (20.784) | 80.159 (82.038) | 18.752 (18.127) | 10.500 (10.732) | 3.167 (3.592) |
| 10.0 | 4 | 27.762 (35.620) | 99.310 (117.256) | 23.166 (27.448) | 9.080 (15.840) | 1.227 (2.103) |

Theo τ và population, nhóm FLIP, giữ h lớn nhất của case theo uniform. Alarm dùng nguyên nhãn từ policy static gốc, không tính lại theo rolling.

| τ (s) | Population | n FLIP | M0 | Hybrid gốc | Sim 60 | Sim 300 | Sim all |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.0 | uniform | 18 | 9.936 (13.420) | 20.679 (39.574) | 0.000 (7.326) | 0.000 (3.525) | 0.000 (0.472) |
| 0.0 | alarm | 4 | 1.279 (2.243) | 33.088 (39.151) | 0.473 (2.488) | 0.473 (2.689) | 0.473 (0.876) |
| 60.0 | uniform | 18 | 8.263 (11.126) | 18.324 (38.264) | 0.000 (5.977) | 0.000 (4.356) | 0.000 (0.472) |
| 60.0 | alarm | 8 | 0.000 (1.554) | 16.540 (24.368) | 0.000 (0.819) | 0.000 (0.900) | 0.000 (0.721) |
| 300.0 | uniform | 18 | 5.896 (11.355) | 20.679 (39.768) | 0.000 (6.885) | 0.000 (5.318) | 0.000 (0.495) |
| 300.0 | alarm | 3 | 4.203 (4.962) | 35.708 (47.829) | 3.648 (5.227) | 7.332 (6.455) | 5.581 (5.871) |

Toàn bộ joint slices OK/FLIP×trace×h×τ×population cho đủ 15 policy, gồm static và hybrid của cả 6 biến thể, nằm trong aggregate_rolling.csv. Từng case nằm trong summary_rolling.csv. Counts với margin và shares tương ứng nằm trong comparisons_rolling.csv và diagnostics_rolling.csv. Các bảng trên chọn τ=0, 60, 300 s theo brief, CSV giữ cả 7 tuổi gốc.

Cơ chế và giới hạn

Ở h lớn nhất, rolling sim_all tốt hơn hybrid gốc ở 17/0/9 case theo thứ tự tốt/tệ/trong margin và tốt hơn M0 ở 21/0/5. Trong FLIP, mean regret giảm từ 39,574% xuống 0,472%, trong khi M0 là 13,420%. Ở h=10 T_int, chỉ còn 4 FLIP thuộc DITL, mean hybrid gốc 117,256%, sim_60 27,448%, sim_300 15,840%, sim_all 2,103%. W dài hơn hữu ích trong dữ liệu này. W ngắn không luôn bám drift tốt hơn. Chẳng hạn DITL s120 c0 thuộc OK, W=60 có dấu sai 2/9 decisions tại h lớn nhất và regret 114,042%, so với 0% của gốc, W=300 và all. Mẫu hình cho thấy các trung bình ngắn có thể đổi dấu mạnh theo đoạn history, chưa tách được nhiễu Poisson khỏi biến động tải.

Mọi s_test cấp case đều âm trên 26 case. Sim_all có dấu âm tại mọi decision trong lát h lớn nhất, τ=0, uniform, và static/hybrid không bất đồng. Do đó mức cải thiện ở đây đến từ việc đổi estimator và chọn action phù hợp drift đã quan sát, chưa chứng minh thành phần fluid+h·ŝ tốt hơn rolling static. Ở alarm, τ=300 s, 3 case FLIP còn support có mean sim_all 5,871% so với M0 4,962%, nên không kết luận rolling thắng ở mọi population hoặc age. Các trường hợp M/M/1 unstable vẫn là kết quả của fallback có flag, không được diễn giải thành stationary truth.

Thứ nhất, đây là post hoc trên cùng dữ liệu full đã thấy, có nhóm dùng outcome. Thứ hai, chỉ có 3 ngày trace count, dữ liệu gói là Cox replay với service marks mô phỏng, hai shadow histories cần model/tape và không được xem là estimator đo trực tiếp trong production. Thứ ba, futures và windows chồng lấn, các case chia sẻ ngày/seed, số decision ở h lớn nhất có thể chỉ 1, alarm còn ít hơn. Không có population CI hoặc bằng chứng độc lập giữa case. Cuối cùng, không điều chỉnh tuning, tải hoặc population sau khi xem kết quả. Giữ nguyên sáu biến thể là đủ cho câu hỏi chẩn đoán này.

Lệnh thực tế và vị trí lưu

Mọi command dưới đây dùng PYTHONDONTWRITEBYTECODE=1. Test và run source experiments/explore_ctmc/env.sh trước khi chạy.

```bash
.venv/bin/python -B -m pytest -q -p no:cacheprovider --basetemp=results/letter/sweep/trace/rolling/pytest_spawn_tmp results/letter/sweep/trace/rolling/test_rolling.py tests/test_sweep_trace.py
.venv/bin/python -B results/letter/sweep/trace/rolling/analyze_rolling.py
.venv/bin/python -B results/letter/sweep/trace/rolling/summarize_rolling.py
.venv/bin/python -B results/letter/sweep/trace/rolling/render_report.py
```

Các file dưới đây đều trong results/letter/sweep/trace/rolling/.

| Loại | File |
| --- | --- |
| Source và test | analyze_rolling.py, test_rolling.py, summarize_rolling.py, render_report.py |
| Quy tắc trước run | run_started.json, dùng nguyên ../design_ready/plan.json |
| Raw rolling | rows_rolling.csv, windows_rolling.csv, case_groups.csv |
| Metric và slices | summary_rolling.csv, aggregate_rolling.csv, comparisons_rolling.csv, diagnostics_rolling.csv, window_flag_counts.csv, headline_metrics.json |
| Log và timing | tests.log, tests_spawn.log, run.log, rescore.log, tests_timing.json, tests_spawn_timing.json, command_timing.json, rescore_timing.json, run.json |
| Audit và lịch sử | audit_before.json, variant_manifest_before_analysis.json, independent_rescore.json, draft_changes.diff, analyze_rolling.original.py.txt, analyze_rolling.attempt01.py.txt, attempt01_startup_failed/ |
| Báo cáo | REPORT_ROLLING.md |

Không tạo biểu đồ, không tải dữ liệu, không commit, không SSH và không sửa file ngoài rolling/. Giữ nguyên experiments/letter/sweep_trace.py, full/ và không truy cập kết quả sweep/ctmc/. Kết quả xác nhận việc cập nhật ŝ có thể sửa sai dấu train trong panel này, đồng thời ghi nhận thất bại của cửa sổ ngắn và alarm ít support. Muốn suy ra hiệu quả ngoài panel cần một thiết kế xác nhận riêng.
