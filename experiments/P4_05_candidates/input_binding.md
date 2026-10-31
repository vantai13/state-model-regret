# Part B — Input bindings và giới hạn thực thi

Người phụ trách: **Doan Van Tai** · 30/10/2026.

`screen_box` là pure kernel, kiểm bằng synthetic fixtures. `screen_registered`
và CLI `screen` phải chạy preflight trước khi mở dữ liệu/hộp. Hiện preflight
trả BLOCKED_PART_B vì thiếu nhãn/baseline, nên chưa có hộp nghiên cứu nào chạy.

Một combined run mới có prereg/source/coverage phù hợp phải tạo, rồi commit:

- `candidate_readiness.json`: READY_FOR_SCREENING; source_sha256 không rỗng,
  gồm `new_prereg_path`, `author_scope_decision_path`, native_manifest và
  rho_policy_path của từng ứng viên được giữ. Chỉ ghi
  `scope_supersedes_historical_HOLD=true` khi đã có evidence cho support đã đăng
  ký; giữ failure lịch sử. Mỗi candidate phải native_readiness=PASS,
  baseline_readiness=PASS,support_complete=true,rho_policy_frozen=true.
- Native manifest: source_kind=DISCOVERY_NATIVE_BUNDLE_V1, source_sha256 cho
  mọi row table, rows.plus và (SV) rows.minus. Mỗi row có full6key, Cref, GS,
  Gamma, d_normalized (ratio, không pp), r1_ready, arithmetic_ready,
  certified_exact nếu thực có, CF_computed=false, source_kind=DISCOVERY_NATIVE.
  Producer phải kiểm raw source/receipt/readiness trước khi ghi manifest.
- Box spec commit trước counts: candidate,id,status=REGISTERED_BEFORE_BOX_COUNTS,
  plus bounds và (SV) minus bounds. Các coordinate là λA,λB,u,κ,h,c_sw hoặcδ.

Mỗi lần real screen reserve một trial trước membership/counts; result riêng
giữ cả EMPTY/FAIL/ERROR. Tối đa3trial/candidate, không bỏ failed trial. Duplicate
physical keys bị từ chối; input chứa CF/sealed keys hoặc geometric box chạm
CF-v2 bị từ chối. Không đọc outcomesCF để làm bất kỳ bước nào.

Không tạo placeholder readiness=PASS, native rows giả, rho policy giả hoặc
box bounds mới trong lesson hiện tại. Dataset/bounds thực và final card decision
còn phải chờ upstream readiness. Code không có engine/import hoặc fallbackpilot.
