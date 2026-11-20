# X4b — chuẩn bị truth/scorer, chưa chạy truth hoặc score

Người phụ trách: **Doan Van Tai**. Thực hiện theo `CODEX_X4B_TRUTH_BRIEF.md`
khớp byte commit `3dbf9eb` của `letter_smr` và thẻ `CARD_X4B.md` giữ nguyên.
Đây là phần triển khai bằng AI theo yêu cầu; không phải independent review
hoặc dự báo do tác giả tự viết.

**Đã thực hiện**

- Sửa `experiments/letter/x4b.py`: thêm CLI `truth --workers N`, `score`;
  giữ nguyên imports X-GÉANT/V7-3 và toàn bộ preparation raw.
- Tạo `experiments/letter/x4b_card.py`: B1, B2, B3(a), B3(b), card lock/verify.
- Tạo `experiments/letter/x4b_gcp.sh`: kiểm hai lock trước/sau truth,
  `timeout --signal=TERM --kill-after=30s 2h`, 30 worker, log noclobber và
  `sudo -n poweroff` trong EXIT trap. Chỉ kiểm syntax; không chạy wrapper.
- Cập nhật `tests/test_x4b.py`; thêm `tests/test_x4b_truth.py` và
  `tests/test_x4b_card.py`.
- Chuyển lock chuẩn bị cũ nguyên byte thành `preparation_lock.json`;
  tạo `lock.json` schema v2 và `lock_card.json`. Trong 482 mục lock cũ,
  480 mục giữ hash, chỉ `x4b.py` và `test_x4b.py` đổi theo brief. Code chặn
  relock sau v2 hoặc sau khi có truth/card lock.

`protocol.json`, `REPORT.md`, các log/audit cũ là snapshot của bước chuẩn bị
trước thẻ; không viết lại chúng thành trạng thái hiện tại. Source check sau
relock đối chiếu source với lock v2; protocol chuẩn bị vẫn giữ nguyên byte.

**Điều kiện và phép đọc đã triển khai**

- Đủ **60 test-S**, không chọn lại regime/ngày; test-O không vào truth.
  N=32, K=64, R_dec=64, R_eval=128; h và τ giữ nguyên configuration.
- Seed test **7412001**, pilot **7472001**, namespace riêng
  `X4B|regime|date`; reference-decision và evaluation dùng stream riêng.
  Trước future rollout, quyết định/ties/warm states/fluid costs phải khớp
  bit-for-bit với step0 của cùng test seed.
- Evaluability: `mean_instance(C_ref)/h >= 0.001 * 12544.525174`, tức
  **12.544525174 Mbit** mean backlog, tương đương **1 ms** theo c₀ cố định
  trong thẻ. Không lấy capacity e* hoặc min/max capacity làm ngưỡng.
- B1 dùng record × unique side × h≤1800 với local disagreement≥1%.
  Không thêm evaluability gate vào B1. Hiệu paired regret Hybrid−Stationary
  và SE tính qua instance; GAIN/LOSS dùng ngưỡng inclusive 2·SE, mean=0
  là UNRESOLVED. Không gán verdict pass/fail cho phép đọc này.
- B2 giữ quy ước `both_side_regret_pct` của X-GÉANT:
  `100 * max(mean regret fresh, mean regret stale_tau) / mean C_ref`.
  Một case là record × τ × h≤1800; không nhân đôi fresh thành case riêng.
  So sánh Hybrid≤Stationary+0.05 **điểm phần trăm C_ref**, STANDS ở≥95%;
  dưới20 case evaluable là NOT_EVALUABLE. Giữ mọi case evaluable.
- B3(a) chỉ M0, h3600/7200, ngày evaluable; gộp regime × τ × h bằng
  daily means và **SE qua ngày**. Resolved theo X-GÉANT: ít nhất2ngày,
  |mean|≥2·SE và≥0.25%C_ref; train sign0 là abstention. Ít nhất4 ô resolved,
  accuracy≥0.80 thì STANDS.
- B3(b) tách M0 fresh regret bằng chính tie flags. Các thành phần là
  contribution cộng được trên toàn instance, không phải conditional means.
  Chỉ h3600/7200 và record evaluable; fresh xuất hiện một lần mỗi h,
  không lặp theo τ. Tổng phần chặt / tổng regret báo chung, theo h, và từng
  record. Giữ signed finite-MC estimates, không clip; tổng0 cho share=null.
- `truth/` tạo bằng exclusive mkdir: mọi lần gọi sau đều bị chặn, không
  retry/resume. NPZ+JSON từng record ghi exclusive/atomic. Receipt ban đầu
  là INCOMPLETE; nếu bị kill trước finalization, metric còn null thay vì
  báo số đo0. Lần hoàn tất ghi CPU-s parent/children/record, wall và peak RSS
  của process lớn nhất (không phải tổng RSS đồng thời).
- Truth hoàn tất mới ghi raw manifest. `score` kiểm checksum, đủ60record,
  receipt COMPLETE, cùng lock, và mọi file raw/receipt/manifest có byte đúng
  trong Git HEAD trước khi chấm. Scoring trên VM không có Git sẽ bị chặn;
  chấm tại repo local sau khi lấy và commit raw.

**Đã chạy và kiểm chứng**

Môi trường thực tế:

```bash
source experiments/explore_ctmc/env.sh
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR="$PWD/results/letter/x4b/build"
```

Các command đã chạy:

```bash
.venv/bin/python -B -m pytest tests/test_x4b.py tests/test_x4b_truth.py tests/test_x4b_card.py -q -p no:cacheprovider --basetemp=results/letter/x4b/pytest_truth_unit
.venv/bin/python -B -m pytest tests/test_x4b.py tests/test_x4b_truth.py tests/test_x4b_card.py tests/test_x_geant.py tests/test_x_geant_card.py tests/test_letter_v7_3.py tests/test_letter_v7_3_day.py tests/test_letter_v7_3_cong.py -q -p no:cacheprovider --basetemp=results/letter/x4b/pytest_truth_final
bash -n experiments/letter/x4b_gcp.sh
.venv/bin/python -B -m experiments.letter.x4b lock
.venv/bin/python -B -m experiments.letter.x4b verify-lock
.venv/bin/python -B -m experiments.letter.x4b_card lock
.venv/bin/python -B -m experiments.letter.x4b_card verify
git diff --check
```

Lượt đầu **55 PASS / 1.93s**. Sau bổ sung test bảo toàn đủ60test-S,
lượt cuối **134 PASS / 2.81s**, không FAIL. Đây là suite liên quan, không
phải full suite repo. Kiểm numeric summaries/B1–B3 dùng dữ liệu tổng hợp;
regression homogeneous-capacity dùng pilot-seed như test có sẵn. Test CLI
truth/score chỉ dispatch tới stub. Không có test-seed future rollout,
lệnh truth thật hoặc lệnh score thật nào được chạy.

Kiểm thêm: brief đúng commit được chỉ định; gate/baseline/seed giữ nguyên;
không có `truth/`, `score.json`, các score CSV hoặc `card_verdicts.json`.
Shell syntax và `git diff --check` PASS.

| Lock | Kết quả | SHA256 |
|---|---|---|
| `lock.json` | PASS,489 mục | `9deb0d94cfd28ba30f8cc7eb7d37e595d7668429bafe38b760ca22354a2684a2` |
| `lock_card.json` | PASS,hash thẻ/scorer/source lock | `94e3a6fe86533cacb9a5423ef611147e1d4a2ebb314f683aa20b95fe7cd360b6` |

**Artifact hiện có**

- Source/test: các đường dẫn ở phần đầu báo cáo.
- Card/config: `CARD_X4B.md`, `configuration.json`, `configuration.npz`,
  `protocol.json`, `inputs.json`, `predictions.json`, `predictions.csv`.
- Lock: `lock.json`, `lock_card.json`, `preparation_lock.json`.
- Test logs: `pytest_truth_unit.log`, `pytest_truth_final.log`.
- Lock logs: `truth_lock.log`, `truth_verify_lock.log`, `truth_lock_card.log`,
  `truth_verify_card.log`.
- Audit JSON của lượt này: `truth_preparation_verification.json`.
- Báo cáo: `TRUTH_PREPARATION_REPORT.md`.

Các đường dẫn artifact không có prefix tính từ `results/letter/x4b/`.
Không tạo truth raw, score CSV/JSON, scientific verdict hay biểu đồ mới.

**Lệnh bàn giao cho Claude — chưa thực thi trong lượt này**

Sau khi review/commit source+hai lock và đồng bộ đúng dependency lên VM,
chạy trên VM đã chuẩn bị tại `~/smr`:

```bash
bash experiments/letter/x4b_gcp.sh
```

Wrapper dùng đúng layout/môi trường của X-GÉANT. Ngoài repo và SNDlib,
closure hiện có vẫn hash hai design briefs tại các absolute path ban đầu;
thêm truth brief `CODEX_X4B_TRUTH_BRIEF.md`. Phải stage cả ba đúng nội dung
tại `/home/vantai/state-model-regret-papers/letter_smr/briefs/strengthen/`
trên VM; verify-lock sẽ chặn nếu thiếu/sai. Không bỏ qua verify để chạy.

Sau khi lấy raw, kiểm checksum và **commit raw trước**, chạy tại repo local:

```bash
source experiments/explore_ctmc/env.sh
.venv/bin/python -B -m experiments.letter.x4b verify-lock
.venv/bin/python -B -m experiments.letter.x4b_card verify
.venv/bin/python -B -m experiments.letter.x4b score
.venv/bin/python -B -m experiments.letter.x4b_card score
```

Tiếp đó cần independent rescore theo thẻ. Nếu truth bị ngắt, giữ INCOMPLETE,
không chạy lại/resume và không chấm.

**Kết luận**

Đã kiểm chứng implementation, arithmetic của các phép đọc trên synthetic data,
regression liên quan và hai content lock. **Chưa có kết quả thực nghiệm B1/B2/B3**,
chưa xác nhận Hybrid gain/noninferiority hoặc tỉ lệ harm do quyết định chặt.
Không commit, không SSH, không chạy truth/score, không gọi poweroff. Exposure và
giới hạn khoa học đã ghi trong thẻ vẫn giữ nguyên.
