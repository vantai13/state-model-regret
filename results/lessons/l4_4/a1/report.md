# L44_A1 — HOLD theo cap, không chọn rho

Người phụ trách: **Doan Van Tai**. AI triển khai/soạn forecast theo ủy quyền chat; không tác giả tự viết hoặc human review.

## Kết quả thật

ControlPASS,benchmark3PASS/1NOT_READY. Budget2.929164CPUh/8 đã commit trước full.
Full dừng đúng cap:16/90stagecases =8PASS/8NOT_READY; SH8/72>10%,0BUG. Bao gồm benchmark:19tọa độ đã tính,11PASS/8NOT_READY;71NOT_RUN.
MV:2PASS/16NOT_RUN trên18. SH:9PASS/8NOT_READY/55NOT_RUN trên72. Không lấy tỷ lệ partial làm prevalence.
Toàn bộ19tọa độ quan sát đều native-ready; blockers mới thuộc baseline:9baseline-arithmetic events và12baseline-R1 events (events không phải số điểm).
Unique evaluation CPU gồmcontrol829.655796s,không phải tổng mọi chi phí compiler/import/launcher.

Không có rho_freeze, không chấm MV/SH median forecast, không thu hẹp scientific claim từ hai điểm MV. `summarize` từ chối với exit1 đúng dự kiến.
Forecast NOT_READY<=3SH đã bị8quan sát bác; dự đoán baseline toànscope NOT_EVALUABLE.0same-route/S11/theta0BUG trong scope đã chạy, không chứng minh toàn engine tuyệt đối đúng.

## Lệnh

`.venv/bin/python -m experiments.P4_A1.run control --run L44_A1`
`.venv/bin/python -m experiments.P4_A1.run benchmark --run L44_A1`
`.venv/bin/python -m experiments.P4_A1.run budget --run L44_A1`
Budget commit3cef246, sau đó `run full --run L44_A1`. Không chạy lại schedule sau HOLD.

## Artifacts

prereg: experiments/P4_A1/runs/L44_A1/prereg.json; control/benchmark/budget/full summaries cùngfolder này.
`hold_case_ledger.csv` đủ90điểm; `verification.json` đối chiếu arithmetic/scope độc lập; `native/` giữmọi19bundle/57level rows.
Log: results/lessons/p4_a1/execution/L44_A1/. History L4.4gốc giữnguyênSHA. Native cache giữlocal/ngoàiGit.

## Giới hạn và tiếp theo

HOLD cũ ởoracle sanity đã được tách khỏi same-route check; baseline precision/refinement vẫn chưa đủ. Không gọi đây là hypothesis FAIL hoặc rootcause đã đóng. Nếu tiếp tục phải prereg/package mới cho baseline numerics; không sửa A1 saufreeze, không nới tolerance. G1/F1baselineHOLD/P0V10/L8/Understanding giữ;0CF/sealedoutcomes/boxcounts.
