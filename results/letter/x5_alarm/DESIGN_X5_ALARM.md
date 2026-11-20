# Design X5 và brief cho Codex: quyết định khi có cảnh báo nghẽn trên GÉANT thật (Claude, 21/11/2026 0h)

- **Người phụ trách:** Doan Van Tai. Claude quyết thay tác giả theo ủy quyền toàn bộ (20/11/2026 khuya: "tự thiết kế tự chạy").
- **Thẻ (đã viết trước mọi outcome):** `/home/vantai/state-model-regret/results/letter/x5_alarm/CARD_X5.md`. Đọc kỹ trước khi code.
- **Repo:** `/home/vantai/state-model-regret`, nhánh `letter`. Shell:
  `source .venv/bin/activate && source experiments/explore_ctmc/env.sh` (không có `python`, dùng `python3`; không có `rg`).

## Luật cứng
1. **Không sửa** file có sẵn nào (đặc biệt `experiments/letter/x4b.py`, `x_geant.py`, `v7_3_*.py`, mọi thứ trong `results/letter/x4b/`).
2. Chỉ tạo: `experiments/letter/x5_alarm.py`, `experiments/letter/x5_alarm_card.py`, `experiments/letter/x5_gcp.sh`,
   `tests/test_x5_alarm.py`, và file trong `results/letter/x5_alarm/` (trừ `CARD_X5.md`, không sửa).
3. **Không commit, không push, không ssh.** Không chạy `truth` hay `score`. Claude chạy truth trên GCP.
4. Không thay số trong thẻ. Nếu thẻ mơ hồ ở chỗ nào, chọn cách gần X4b nhất và ghi rõ trong báo cáo cuối.

## Module `experiments/letter/x5_alarm.py`
- Import `experiments.letter.x4b as B` (và qua đó X, S, T, R…). Tái dùng hàm của B bằng import; chỗ cần khác thì viết hàm mới trong x5.
- `OUT = ROOT/'results/letter/x5_alarm'`. Hằng số: `M = 512`, `N = 32`, `MIN_ALARMS = 8`, `ALARM_SERVICE_S = 0.001`,
  `TEST_SEED = 7000001`, `PILOT_SEED = 7000003`; `K, R_DEC, R_EVAL, H_SECONDS, PIPES, SIDES` lấy từ B.
- **Cấu hình:** đọc `results/letter/x4b/configuration.json/.npz` và slope ŝ pooled train của X4b (file step0/train của X4b có `s_hat_pooled_Mbit`).
  Lệnh `configure` ghi `results/letter/x5_alarm/configuration.json` gồm đường dẫn và SHA-256 của các file nguồn X4b, `e_star_index` và
  `alarm_threshold_Mbit = 0.001 * c[e*]` cho từng regime, danh sách 60 bản ghi test-S lấy từ `B.planned_truth_records(B.OUT)`.
- **Seed:** `root = T.seed_for(seed, f'X5|{regime}|{date}')`, nhãn như `B.seeds_for` (warm, posterior-300.0, posterior-900.0,
  reference-decision, evaluation).
- **decision_record_x5:** như `B.decision_record` nhưng:
  1. `S.warm_instances(inc, warm, cap, M, streams['warm'])` cho M ứng viên;
  2. cảnh báo = `fresh_queues[:, e_star] >= alarm_threshold_Mbit`; chọn tối đa N chỉ số đầu tiên có cảnh báo; cắt `fresh` và từng `stale[tau]`
     theo đúng các chỉ số đó (giữ thứ tự);
  3. nếu số cảnh báo < MIN_ALARMS: trả về trạng thái `ALARM_RARE` kèm số đếm, không tính quyết định;
  4. phần còn lại (posterior K, M0 tươi/cũ, `X.fluid_choices` với ŝ, utilization) y như B, với n = số chỉ số đã chọn.
  Ghi vào meta: `candidates=M`, `alarms` (số ứng viên có cảnh báo), `selected_indices`, `alarm_threshold_Mbit`, `e_star_index`.
- **outcome_record_x5:** như `B.outcome_record` (rollout reference R_DEC, evaluation R_EVAL, `B.paired_metrics`), dùng các instance đã chọn.
  Truth phải xác minh lock và kiểm quyết định trùng step0 (như X4b).
- **Lệnh:**
  - `configure`.
  - `step0 --workers W`: chỉ quyết định cho 60 bản ghi test-S với TEST_SEED. Ghi `step0/test/*.npz`, `step0/summary.json` gồm số cảnh báo theo
    bản ghi, số ALARM_RARE, share bất đồng Hybrid ≠ Stationary theo regime × h × side, share tie M0 tươi; và **cổng của thẻ** (SIGNAL_OK hoặc
    NOT_ENOUGH_SIGNAL).
  - `pilot`: 2 bản ghi không RARE với PILOT_SEED, đầy đủ rollout, ghi CPU-s, dự phóng CPU-h cho truth.
  - `lock`: hash module, card scorer, test, gcp script, `CARD_X5.md`, file brief này, configuration, step0 summary và npz; ghi `lock.json`.
  - `verify-lock`, `truth --workers W` (chỉ Claude chạy), `score` (chỉ chạy khi raw đã commit, như `B.require_raw_committed`).
  Nếu cổng là NOT_ENOUGH_SIGNAL thì `truth` phải từ chối.

## Card scorer `experiments/letter/x5_alarm_card.py`
Hiện thực đúng T1–T4 và phần mô tả của `CARD_X5.md` trên raw truth (npz theo bản ghi):
- T1: ô (regime, h ∈ {300,600,900,1200,1800}); đủ điều kiện nếu share bất đồng phía tươi gộp của ô ≥ 0.05 và ≥ 5 bản ghi; D theo ngày
  từ chênh lệch paired Hybrid − Stationary phía tươi (cùng định nghĩa `paired_Hybrid_minus_Stationary_pct` của X4b); GAIN/LOSS/UNRESOLVED với
  ngưỡng 0.05 pp và 2SE (SE = sd/√n qua ngày, ddof = 1); verdict ĐỨNG/ĐỔ/NOT_EVALUABLE như thẻ.
- T2: share trùng Hybrid = Stationary phía tươi ở h = 7200 gộp, ngưỡng 0.95.
- T3: share tie M0 tươi gộp ≤ 0.10 và số regime có regret tươi trung bình của M0 ở 7200 s > 0.5% ≥ 2.
- T4: share bản ghi evaluable (cổng X4b) có regret hai phía của Hybrid ở 7200 s ≤ 0.5%, ngưỡng 0.80.
- Mô tả: G_S theo h cho M0 và Hybrid, share phần chặt trong regret tươi M0 (như `B.tie_strict_regret`), D ở 3600 s.
Ghi `card_verdicts.json` và `REPORT_X5.md` (bảng số, không diễn giải).

## Test `tests/test_x5_alarm.py` (bắt buộc)
1. Với ngưỡng cảnh báo âm vô cùng và M = N, `decision_record_x5` trùng bitwise `B.decision_record` trên một bản ghi (cùng seed/stream).
2. Chọn chỉ số đúng thứ tự; trạng thái cũ cắt khớp chỉ số; ALARM_RARE khi < 8.
3. Card scorer trên dữ liệu tổng hợp: biên GAIN/LOSS/UNRESOLVED, NOT_EVALUABLE khi < 3 ô, T2–T4 ở hai phía ngưỡng.
4. `truth` từ chối khi chưa lock, khi cổng NOT_ENOUGH_SIGNAL, khi stage/count bị ghi đè.
5. Chạy lại test X4b liên quan (`tests/test_x4b.py`) vẫn đạt.

## Chạy
- `configure`, `step0` (dùng tối đa 8 worker local; **nếu pilot nhỏ cho thấy step0 > 40 phút local thì dừng và báo dự phóng**, Claude sẽ chạy
  trên GCP), `pilot`, rồi `lock` (chỉ khi step0 SIGNAL_OK).
- `x5_gcp.sh` như `x4b_gcp.sh`: verify-lock, `timeout` truth với `--workers 30`, log `PIPELINE_START/EXIT`, rồi `sudo -n poweroff`.

## Báo cáo cuối (tiếng Việt)
Tóm tắt step 0 (số cảnh báo, RARE, share bất đồng theo regime × h, share tie), cổng, CPU pilot và dự phóng truth, kết quả test, đường dẫn file,
mọi chỗ bạn phải tự chọn vì thẻ mơ hồ.
