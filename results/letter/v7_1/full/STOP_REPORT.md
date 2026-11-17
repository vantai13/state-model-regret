# V7-1 — extraction PASS, dừng trước scoring

Người phụ trách: **Doan Van Tai**.

**Verdict card: NOT_EVALUABLE.** Full extraction hoàn tất; push bảng bị từ chối `non-fast-forward`. Theo mục 4 của brief GCP tại HEAD, dừng an toàn. Chưa chạy AUC/CI, bootstrap, Spearman, precision, figure hoặc independent rescore. Lỗi đồng bộ Git không phải evidence bác bỏ hypothesis.

## Đã thực hiện và kiểm tra

- Thêm `experiments/letter/v7_1_gcp.py`, `experiments/letter/v7_1_gcp_pipeline.sh`, `tests/test_letter_v7_1_gcp.py`. Wrapper tách extraction/scoring, giới hạn 16 workers, kiểm input/lock/network SHA256 và chặn scoring trước khi raw commit đã push. Giữ byte code khoa học pilot và card.
- Local: **22/22 tests PASS, 2,09 s**. VM: **22/22 PASS, 0,99 s**. Input/network **833/833** khớp hai phía; trước prepare, 804 input pilot và 11 file L7.2 lock đã kiểm khớp.
- Detached `setsid nohup`; một invocation. Log ghi `PIPELINE_START 2026-11-17T15:03:19Z` và `PIPELINE_EXIT rc=0 2026-11-17T15:06:38Z`.
- Đủ 433 extraction records: 431 mới, 2 pilot tái dùng nguyên byte; 93 CTMC regimes và 17 GÉANT regimes × 2 seeds. Đủ P1–P3/Y cho 3.255 + 612 cells.
- CTMC **1,860 scalar checks PASS**, max relative error **1.44328993201e-15** ≤ 1e−9. GÉANT **1,224,000 decisions** và **1,224,000 tie flags** khớp bitwise trên 340 chunks.
- Rsync về và đối chiếu SHA256: **879/879 files PASS**, gồm log. Raw manifest **875/875 artifacts PASS**. Raw commit được tạo khi summary/figure/scoring outputs chưa tồn tại.

## Kết quả đo được từ extraction

| Dataset | Cells | Scale rows | h* (s) | h*/T_int | AUC P1/P2/P3 và CI | Spearman / precision P2≥1 |
|---|---:|---:|---:|---:|---|---|
| CTMC | 3,255 | 93 | 3.21259198–720.494799 | 0.0385157558–3.30413166 | NOT_RUN | NOT_RUN |
| GEANT | 612 | 34 | 0.0506572859–44.9030596 | 0.0408155351–2.93284794 | NOT_RUN | NOT_RUN |

Nguồn range: `full/regime_scales.csv`, min/max trên toàn bộ rows mỗi dataset, h*=Q90/|s_hat|. CTMC gap có đơn vị packet·s, s_hat packet; GÉANT gap Mb·s, s_hat Mb. Giây theo convention simulator, không calibration deployment. CTMC là truncated; GÉANT maximum empirical, gap ở largest saved h=30T_int. Cells dùng chung regime, không phải trial độc lập. Không chấm một subset để có verdict. Hai forecasts của card đều NOT_EVALUABLE.

## Compute

- GCP wall: **198.235866425 s**; CPU của 431 extraction mới: **3002.752686881 s**.
- Parent CPU 1.590499491 s, children CPU 3016.648780000 s; tổng gồm overhead **3018.239279491 CPU-s**.
- CPU các extraction khi tính cả hai pilot reused: 3219.413075463 s. Max RSS một worker: 138,080 KiB, không phải peak tổng VM.
- Scoring/rescore NOT_RUN. Không start/stop/resize VM; Claude tiếp tục quản lý VM.

## Commands thực tế

```bash
source experiments/explore_ctmc/env.sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_letter_v7_1.py tests/test_letter_v7_1_gcp.py --basetemp=/tmp/v7_1_gcp_local_preflight
PYTHONDONTWRITEBYTECODE=1 SMR_SNDLIB=/home/vantai/papers/data/sndlib .venv/bin/python -m experiments.letter.v7_1_gcp --stage prepare
rsync -ac --relative --files-from=/tmp/v7_1_gcp_rsync_files.txt ./ dt4n-gcp:smr/
rsync -ac /home/vantai/papers/data/sndlib/sndlib-networks-native/geant.txt dt4n-gcp:papers/data/sndlib/sndlib-networks-native/
# Trên VM, sau source env.sh và export SMR_SNDLIB:
.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_letter_v7_1.py tests/test_letter_v7_1_gcp.py --basetemp=/tmp/v7_1_gcp_preflight
setsid nohup bash experiments/letter/v7_1_gcp_pipeline.sh > /dev/null 2>&1 < /dev/null &
# Pipeline chạy đúng một lần:
timeout --signal=TERM --kill-after=30s 2h .venv/bin/python -u -m experiments.letter.v7_1_gcp --stage extract --workers 16 --out results/letter/v7_1/full
# Local:
rsync -ac dt4n-gcp:smr/results/letter/v7_1/full/ results/letter/v7_1/full/
git -C /tmp/smr-v7-1-gcp.dk37pdt9 push origin letter  # raw push: exit 1, non-fast-forward
```

`bash -n` PASS; SHA256 kiểm bằng Python hashlib hai phía. Git whitespace check mặc định gắn cờ CRLF CSV pilot; giữ nguyên byte và kiểm PASS với `-c core.whitespace=cr-at-eol`. Script ghi báo cáo có một SyntaxError trước khi tạo output, đã sửa; không phải scientific invocation hoặc rerun extraction.

## Commits, lỗi và deviations

- Code/pilot đã push: `eb088ebc33d9d42dcddc9edbe1d46f51d5b20ad5`.
- Raw extraction đã commit local: `0a53c1369e5025789c7cdaeb15dc693ebb9a8569`; **chưa push**.
- Remote `letter` quan sát sau lỗi: `c51c0ea4f9e24a332e975b315f834a6856a7cec8`; push bị từ chối vì không fast-forward. Không merge, force-push hoặc thử push lần hai.
- `.git` workspace chính read-only: `git add` không tạo được `index.lock`. Commit/push qua checkout writable `/tmp/smr-v7-1-gcp.dk37pdt9`. HEAD workspace chính vẫn `152f49cc729b97a380885fa08a4c328df3e7219e`; artifact được trả về workspace chính.
- Không rerun extraction, đổi card/threshold, sửa paper hoặc file V7-2/V7-3. Hai artifact pilot reused như handoff; không dùng plant V thay fluid gaps.

## Files và trạng thái

Các đường dẫn dưới đây tương đối với `results/letter/v7_1/`:

- Bảng: `full/cells.csv`, `full/regime_scales.csv`; arrays/checks: `full/extracted/*.json/npz`, `full/extraction_checks.json`.
- Cấu hình/provenance: `CARD_V7_1.md`, `full/source_manifest.json`, `full/input_manifest.json`, `full/extraction_complete.json`.
- Checksums: `full/raw_manifest.json`, `full/input_sync_receipt.json`, `full/transfer_receipt.json`.
- Logs: `full/pipeline.log`, `full/pytest_local_preflight.log`, `full/pytest_gcp_preflight.log`.
- Báo cáo: `REPORT_V7_1.md`, `full/STOP_REPORT.md`; trạng thái: `summary.json`, `full/execution_status.json`.
- Pilot snapshots giữ ở `full/pilot_report_snapshot.md`, `full/pilot_summary_snapshot.json`. `verification.json` gốc là snapshot pilot, không phải kiểm định full scoring.
- Không tạo `full/summary.json`, `full/regime_onsets.csv`, `full/rescore.json` hoặc `fig_rule.pdf/png`: stage (b) chưa chạy.

Đã xác nhận extraction, replay, checksum và đủ population. Card chưa được kiểm định. Bước còn lại là đồng bộ remote và push raw commit trước scoring/rescore; extraction không cần chạy lại. Không tự tiếp tục sau stop condition của brief.
