# Design X5c và brief cho Codex: cảnh báo trên đường mà luật tĩnh chọn, η = 0,3 và 0,6 (Claude, 21/11/2026 ~1h15)

- **Người phụ trách:** Doan Van Tai. Claude quyết theo ủy quyền toàn bộ. **Thẻ:** `results/letter/x5c_alarm/CARD_X5C.md` (đọc trước, kể cả phần "Vì sao sửa").
- **Nền:** X5 đã hiện thực trong `experiments/letter/x5_alarm.py` (brief `DESIGN_X5_ALARM.md` cùng thư mục, test `tests/test_x5_alarm.py`).
  X5b (`DESIGN_X5B_BURST.md`) bị rút trước khi chạy; dùng lại các yêu cầu về η của nó cho nhánh B.
- Repo `/home/vantai/state-model-regret`, nhánh `letter`; `source .venv/bin/activate && source experiments/explore_ctmc/env.sh`.

## Luật cứng
1. **Không sửa** file có sẵn (kể cả `x5_alarm.py`, `x5_alarm_card.py`, `results/letter/x5_alarm/`, mọi file X4b/X-GEANT/V7-3).
2. Chỉ tạo `experiments/letter/x5c_alarm.py`, `experiments/letter/x5c_card.py` (nếu cần), `experiments/letter/x5c_gcp.sh`, `tests/test_x5c_alarm.py`
   và file trong `results/letter/x5c_alarm/` (trừ `CARD_X5C.md`).
3. Không commit, không push, không ssh. Không chạy `truth`/`score`.

## Hiện thực
- Module có tham số `--arm A|B`, OUT = `results/letter/x5c_alarm/arm_A` hoặc `arm_B`.
- **Link cảnh báo:** với ŝ của nhánh, nếu ŝ < 0 dùng `e_star_index` (đường Switch), ngược lại dùng `path_bottleneck_indices_after[0]` (đường Stay) của regime
  trong cấu hình X4b. Ngưỡng = 0,001·c[link] Mbit. Ghi link, ngưỡng, ŝ vào `configuration.json` của nhánh. Phần chọn mẫu như X5 nhưng dùng link này.
- **η:** nhánh A giữ `S.BETA = 0.3`. Nhánh B đặt `S.BETA = 0.6` trong mọi process (chính và worker qua initializer) trước mọi mô phỏng; rà mọi chỗ dùng
  BETA (default argument, hằng nhân sẵn, cache) và liệt kê trong báo cáo. Nhánh B tính lại ŝ pooled trên các bản ghi train X4b, đúng `B.train_record`,
  seed train 7200005, ghi `arm_B/train/` trước khi mở dữ liệu test. Nhánh A dùng ŝ train của X4b.
- Seed: A test 7100001, pilot 7100003; B test 7200001, pilot 7200003. Namespace seed `X5C-A|regime|date`, `X5C-B|regime|date`.
- Lệnh như X5: `configure`, `step0`, `pilot`, `lock`, `verify-lock`, `truth` (từ chối nếu chưa lock hoặc cổng nhánh không qua), `score`
  (chỉ sau khi raw đã commit). Lock gồm module, scorer, test, gcp script, `CARD_X5C.md`, `CARD_X5.md`, brief này, cấu hình, step0 của nhánh.
- Scorer: đúng T1–T4 của `CARD_X5.md`, áp riêng từng nhánh (có thể import `x5_alarm_card`).
- `x5c_gcp.sh ARM`: verify-lock, truth `--workers 30`, log `PIPELINE_START/EXIT`, rồi `sudo -n poweroff`. Thêm biến môi trường để chạy cả hai nhánh
  nối tiếp trong một phiên GCP (`ARMS="A B"`), mỗi nhánh có log riêng, poweroff sau nhánh cuối.

## Test bắt buộc (`tests/test_x5c_alarm.py`)
1. Với link cảnh báo = e* và η = 0,3, đường code X5c trùng bitwise X5 (cùng seed) trên một bản ghi.
2. Chọn link đúng theo dấu ŝ (thử cả hai dấu); ngưỡng theo c[link].
3. Nhánh B: `S.BETA` = 0,6 thật sự trong worker; ŝ train ghi trước khi đọc test.
4. truth từ chối khi chưa lock, khi cổng không qua, khi ghi đè count/seed.
5. Test X5 và X4b liên quan vẫn đạt.

## Chạy
Cho từng nhánh: `configure` (nhánh B gồm ŝ train), `step0 --workers 8`, rồi nếu SIGNAL_OK: `pilot` (2 bản ghi) và `lock`. Nếu dự phóng một bước > 40 phút
local thì dừng bước đó và báo dự phóng (Claude chạy trên GCP).

## Báo cáo cuối (tiếng Việt)
Theo nhánh: ŝ và link cảnh báo theo regime; số cảnh báo/ứng viên; ALARM_RARE; share bất đồng theo regime × h × side; share tie M0 tươi; cổng; CPU pilot và
dự phóng truth; danh sách chỗ BETA đã rà (nhánh B); test; đường dẫn; mọi lựa chọn do thẻ mơ hồ.
