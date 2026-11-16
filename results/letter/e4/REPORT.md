# LETTER E4 — báo cáo triển khai, training checks và pilot

Người phụ trách: **Doan Van Tai**. Triển khai bằng AI theo brief đã được tác giả yêu cầu thực hiện, ngày 16/11/2026.

## Phạm vi và tính toàn vẹn

- Brief khớp byte với commit `db0268e5`, SHA256 `980158ecf06214a4693d5854df68045194ca7812bb6ff5e99caec7895848e064`.
- Không commit, không SSH; giữ nguyên toàn bộ file có sẵn. Audit kiểm 35.174 file: 0 thay đổi.
- Thêm `experiments/letter/e4_geant.py`, `experiments/letter/e4_rhat.py`, `tests/test_letter_e4.py` và các output dưới thư mục này.
- Import engine EV-TE đã khóa; không sửa `experiments/ext_validity/ev_te.py`.
- Chỉ training seed `1`, pilot seed `7000001`. Chưa chạy E4 test seed `3000001`; chưa có card/lock hay verdict E4 confirmatory.
- `E4_DESIGN.md` còn header awaiting approval; brief và commit hiện hành xác nhận đã duyệt. Không sửa header lịch sử.

## Chức năng và kiểm tra

- Per-action `V[n,a,h]` dùng R_eval CRN, tất cả pipeline gather chi phí từ cùng V. M1_new dùng R_dec và stream riêng.
- M0, ba tie-rhat, tie-rand, hybrid i/ii, bốn noise tương đối so với Stay, reversed; onset-hybrid có code và tắt mặc định. Level iii chỉ ordering/tie-break.
- 10 chunks × 50 instances/regime, seed theo seed/regime/chunk/purpose. NPZ ghi độc quyền với ZIP metadata cố định; JSON chứa CPU/wall đo thực.
- Merge tạo bảng regime, cell, regret reduction; score không card chỉ mô tả. Truth yêu cầu card và manifest SHA256 trước khi tạo state/chạy engine.
- Card phải chỉ rõ horizon_rule `all` hoặc `each`, h_multipliers và thresholds; xem `card_format.json`. Không tự chọn cách gộp `h >= 7*T_int`.
- 21/21 tests E4 PASS (0,76 s); 29/29 tests EV-TE PASS (1,15 s). Không chạy full repository suite vì phạm vi kiểm tra là E4 + EV-TE liên quan.
- Regression trên G3_r80_b3_s1, instance đầu của seed1000001, R_eval256, seed derivation EV-TE: M0_new khớp bitwise raw `pipeline_V` ở cả 6 horizons và 4 ages.
- Test NPZ cùng chunk/seed khớp byte; khác chunk dùng stream khác. Kiểm ties chính xác, hybrid constant-rhat, reversed, factor 1/(2*kappa), onset, stale posterior average, independent M1/evaluation streams và scorer.
- Bổ sung guard undefined normalization trong `score_tests` sau khi training/pilot đã bắt đầu, trước truth; 21/21 tests chạy trên bản cuối. Không sửa hàm khoa học nào: AST audit chỉ khác `score_tests`. Snapshot source/tests đã chạy lưu trong `audit/training_pilot_*.txt`, SHA khớp fingerprint trước run; diff ở `audit/scoring_normalization_guard.patch`.

## Training checks

Seed1, N=100/regime, K=128; h/T_int=[1, 2, 4, 7, 15, 30], tau/T_int=[0.3, 1.0, 3.0]. CPU 158.429867 s.

Cả 17 regime stationarity-valid đều có 2 actions; không có regime G4 trong tập confirmatory này. Vì chỉ có 2 actions và không có action-rate ties, best-action agreement và full ordering agreement có cùng số đếm.

| Regime | ii best/full | iii best/full | M0 fresh tie % | M0 stale tie % |
|---|---:|---:|---:|---:|
| G1_r80_b3_s1 | khớp | khớp | 51.00 | 0.00 |
| G1_r80_b6_s0 | khớp | khớp | 43.00 | 0.00 |
| G1_r80_b6_s1 | khớp | khớp | 41.00 | 0.00 |
| G2_r80_b3_s1 | khác | khác | 97.00 | 40.33 |
| G2_r80_b6_s0 | khác | khác | 47.00 | 0.00 |
| G2_r80_b6_s1 | khớp | khớp | 55.00 | 0.00 |
| G2_r90_b3_s0 | khớp | khác | 47.00 | 0.00 |
| G2_r90_b3_s1 | khớp | khớp | 47.00 | 0.00 |
| G2_r90_b6_s0 | khớp | khác | 24.00 | 0.00 |
| G2_r90_b6_s1 | khớp | khớp | 13.00 | 0.00 |
| G3_r80_b3_s1 | khác | khác | 97.00 | 16.67 |
| G3_r80_b6_s0 | khớp | khác | 45.00 | 0.00 |
| G3_r80_b6_s1 | khớp | khớp | 53.00 | 0.00 |
| G3_r90_b3_s0 | khớp | khác | 50.00 | 0.00 |
| G3_r90_b3_s1 | khớp | khớp | 42.00 | 0.00 |
| G3_r90_b6_s0 | khớp | khác | 10.00 | 0.00 |
| G3_r90_b6_s1 | khớp | khớp | 19.00 | 0.00 |

**Gaussian ii: 14/17 = 82,352941%; ordering-only iii: 9/17 = 52,941176%.** Mức 90% dự kiến cho E4-3 chưa đạt; chưa gán verdict từ card chưa tồn tại.

M0 fresh tie trung bình 45,941176%, stale 3,352941%. Fresh trung bình trên 6 horizons; stale trên 3 ages × 6 horizons. Đây là denominator mô tả, không phải các thử nghiệm độc lập hay population CI.

Ba bất đồng ii: G2_r80_b3_s1, G2_r80_b6_s0, G3_r80_b3_s1. Tính độc lập từ trọng số model xác nhận cả công thức Gaussian và ordering-only cho đủ 17 regime. Ở hai cấu hình beta=.3, Gaussian dự báo rate lớn hơn mô phỏng khoảng 384–5519 lần; training P(Q>0) chỉ khoảng 1,08–1,26%. Điều này phù hợp với hạn chế của xấp xỉ diffusion ở vùng queue hiếm; chưa chứng minh đây là nguyên nhân duy nhất. Không fit hoặc thay estimator sau khi thấy bất đồng. Số chi tiết ở `audit/training_disagreements.json`.

## Pilot và dự phóng

Lệnh được yêu cầu dùng workers4, nhưng chỉ có 2 tasks nên đồng thời tối đa 2 chunks. Seed7000001; mỗi chunk N50/K128/R_eval256/R_dec128; onset tắt.

| Regime | EV-TE CPU đầy đủ cũ (s) | E4 CPU/chunk (s) | E4 wall/chunk (s) |
|---|---:|---:|---:|
| G3_r80_b3_s1 | 529.352061 | 11.967745 | 11.968156 |
| G2_r90_b6_s1 | 12521.245988 | 370.887413 | 370.892636 |

Tổng CPU hai chunk: **382.855158 s**, wall runner 371.064897 s.

Dự phóng 17×10=170 chunks: **12160.447 CPU-s = 3.378 CPU-h**. Khoảng nhạy theo hai hệ số pilot: 10527.762–13793.131 CPU-s (2.924–3.831 CPU-h).

Cách tính: mỗi pilot cho hệ số CPU_E4_chunk/(CPU_EV_regime/10); lấy trung bình hai hệ số nhân tổng CPU EV-TE của đủ 17 regime (46.565,934984 s). Dùng lịch sử CPU để phản ánh mix các regime, thay vì coi hai cực là mẫu ngẫu nhiên đại diện.

Giới hạn lý tưởng 32 workers khoảng 380.014 s (6.334 phút), có xét chunk đắt nhất không chia nhỏ được. Đây là dự phóng từ máy local, không là CI, bảo đảm thời gian VM hoặc phép đo GCP mới; startup/I/O và chênh lệch phần cứng vẫn mở.

- Pilot hoàn tất 2/2 chunks, không có lỗi thực thi. Merge đúng 468 hàng cell (2×3×6×13).
- Tính lại độc lập 468 hàng loss/C_ref/G_S từ raw V và decisions khớp; raw SHA và bản sao khớp. C_ref >0 ở mọi horizon pilot.
- Score không card có `tests=null`, `descriptive_only=true`; 0/17 full regimes là đúng vì chỉ chạy 1/10 chunk ở 2 regime.

## Command đã chạy

Mỗi phiên dùng:
```bash
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
export PYTHONDONTWRITEBYTECODE=1
```

Các command chính (stdout được lưu ở audit/):
```bash
python3 -m pytest -q tests/test_letter_e4.py --basetemp=/tmp/le4_pt -o cache_dir=/tmp/le4_cache
python3 -m pytest -q tests/test_ev_te.py --basetemp=/tmp/le4_ev_pt -o cache_dir=/tmp/le4_ev_cache
python3 -m experiments.letter.e4_geant train-checks
python3 -m experiments.letter.e4_geant run --workers 4 --chunks 0 --regimes G3_r80_b3_s1 G2_r90_b6_s1 --pilot --out /tmp/e4_pilot
python3 -m experiments.letter.e4_geant merge --out /tmp/e4_pilot
python3 -m experiments.letter.e4_geant score --out /tmp/e4_pilot
```

Các audit đọc-only bằng Python: kiểm 35.174 hash file có sẵn; tính độc lập công thức/rank 17 regime; tính lại 468 hàng pilot từ V/decisions; so SHA các bản sao; so AST source trước/sau scorer guard. Không gọi engine trong các audit này.

## Bàn giao GCP — chưa thực thi

Claude cần viết card JSON theo `card_format.json`, chốt nghĩa horizon và onset từ W2, tạo lock, commit/push trước truth. Lock dùng `{ "sha256": {path: digest} }`; `input_hashes(out=..., card=...)` trong module trả mandatory input manifest. Chỉ chạy sau card/lock hợp lệ. Không tạo card hoặc lock giả trong lượt này.

Lệnh exact trên GCP, với onset mặc định tắt và card được lưu tại đường dẫn đã nêu:
```bash
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.letter.e4_geant run --workers 32 --chunks all --card results/letter/e4/CARD_E4.json
```

Nếu Claude duyệt onset sau W2, card phải có `onset_theta` và command phải thêm `--onset-theta` cùng giá trị. Không tự chọn theta. Runner từ chối truth thiếu card/lock và từ chối chạy lại/ghi đè output. Sau truth, lưu raw theo protocol trước khi score; không dùng pilot để gán verdict.

## Vị trí artifact và điểm chưa rõ

- Source: `experiments/letter/e4_geant.py`, `experiments/letter/e4_rhat.py`; tests: `tests/test_letter_e4.py`.
- Training: `training_checks.json` (đầy đủ estimates, order, shares theo cell và hashes), `training_checks.csv`, `training_summary.csv`.
- Pilot gốc: `/tmp/e4_pilot/`; bản sao lâu dài có SHA kiểm ở `pilot/`, gồm 2 NPZ+2 JSON raw, run_start/run_summary, CSV cells/regimes/reductions, merge và score mô tả.
- Logs: `audit/pytest_initial.log`, `audit/pytest_final.log`, `audit/pytest_scoring_guard.log`, `audit/pytest_ev_te.log`, `audit/train_checks.log`, `audit/pilot.log`.
- Audits: `audit/existing_files_integrity.json`, `audit/training_validation.json`, `audit/training_disagreements.json`, `audit/pilot_validation.json`.
- Cấu hình card/scoring: `card_format.json`; cấu hình pilot và seed có trong `pilot/run_start.json` và raw JSON. Chưa tạo card/lock truth; không tạo biểu đồ.
- Cần Claude chốt horizon_rule: 51 regime×tau units yêu cầu cùng đạt cả h7/15/30, hay 153 regime×tau×h units. Thresholds đều lấy từ card, không ẩn mặc định trong scorer.
- Nếu Stay không thuộc tập tối thiểu, exact tie giữa các action khác dùng index nhỏ nhất như EV-TE; không chọn action ngoài argmin.
- NPZ khoa học tái tạo byte; JSON CPU/wall là phép đo thực nên không thể cùng byte qua hai lần chạy. Không làm giả thời gian để đạt byte equality.
- Chỉ xác nhận implementation/training/pilot. Chưa xác nhận hiệu quả E4 trên test seed, giả thuyết, generalization 4 actions hoặc số giờ chạy thật trên GCP.
