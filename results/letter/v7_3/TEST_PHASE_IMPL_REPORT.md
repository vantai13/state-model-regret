Người phụ trách: **Doan Van Tai**. Triển khai theo brief/card/params tại
`0f8ec8229`, chỉ tạo file mới. Không commit, SSH, chạy `run`, tạo lock thật,
đọc matrix/strata hoặc mô phỏng test day. Chưa có kết quả H1–H3/F1–F7 thật.

Đã xây dựng:

- `experiments/letter/v7_3_test.py`: `lock`, `verify-lock`, `run --workers W`;
  loader có date gate; input strata ghi trước worker; seed theo regime/date;
  ProcessPoolExecutor dừng khi exception hoặc worker chết; không retry/resume.
  NPZ/JSON ghi riêng bằng publish atomic không ghi đè; interruption có trạng
  thái INCOMPLETE, marker lần chạy chặn chạy lại cả khi bị kill đột ngột.
- `experiments/letter/v7_3_test_common.py`: SHA-256 closure 16 source files,
  card/params/brief, training config/protocol/summary, manifest, archive,
  canonical member bytes, topology, train cache và VM script. Khóa dùng tên
  logic cho dữ liệu ngoài repo, tương thích `SMR_SNDLIB` trên VM.
- `experiments/letter/v7_3_score.py`: đủ case metrics, H1–H3 và clause/per-horizon,
  F1–F7, năm sensitivity analyses; phần trăm chỉ khi evaluable, kèm Mbit/ms,
  tie shares, T_int/censoring/h:T_int. G_S giữ dấu stale−fresh; regret có thể âm.
- `experiments/letter/v7_3_rescore.py`: tính lại decisions, strata, costs, SE,
  metrics và verdicts từ raw; không import runner/scorer. Chỉ dùng chung file
  integrity và estimator T_int có sẵn. So từng field với rtol=1e-12, atol=0,
  verdict strings chính xác. Các entry point đều verify-lock trước đọc input.
- `experiments/letter/v7_3_test_gcp.sh`: verify, timeout 6h/30 workers, log
  noclobber `PIPELINE_START`/`PIPELINE_EXIT rc=`, poweroff ở exit. Chỉ kiểm cú pháp.
- `tests/test_letter_v7_3_test.py`: synthetic controls, độc lập score/rescore,
  signed regret/reference streams, tie variants, ngưỡng/rule boundaries,
  lock tamper, gate và hai kiểm tra slow trên train.

Lệnh đã thực thi (NumPy single-threaded):

```bash
source .venv/bin/activate
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 -m pytest tests/test_letter_v7_3_test.py -m slow -q --durations=10 -W ignore::pytest.PytestUnknownMarkWarning
python3 -m pytest tests/test_letter_v7_3*.py -m 'not slow' -q --durations=10 -W ignore::pytest.PytestUnknownMarkWarning
bash -n experiments/letter/v7_3_test_gcp.sh
python3 -m compileall -q experiments/letter/v7_3_test_common.py experiments/letter/v7_3_test.py experiments/letter/v7_3_score.py experiments/letter/v7_3_rescore.py tests/test_letter_v7_3_test.py
```

Kết quả: **77 regression tests PASS/1,64 s; 2 slow tests PASS/91,25 s;
0 FAIL**. Slow equivalence DAY1 `2005-05-05`, pilot seed 7372001, N=2,
K=64/R_dec=64/R_eval=128: **14/14 mảng legacy khớp bit-for-bit**, kể cả dtype
và shape. Loader train trả window/warmup đúng training cache. Synthetic
score→CSV/JSON→rescore MATCH; sửa verdict/case bị phát hiện. Bash/compile PASS.
Không chạy full pytest toàn repo hoặc pipeline VM.

Đo record equivalence: **90,179871 CPU-s**, wall **90,181945 s**, gồm trace
độc lập và estimator (0,338603 CPU-s), chưa gồm ghi NPZ/process startup.
Nội suy từ riêng record này: 150×(32/2)×90,179871 = **60,119914 CPU-h**,
wall lý tưởng **2,004 giờ** trên 30 workers.

Trong phiên, một cập nhật bên ngoài đưa HEAD lên `61670742d`, bổ sung đủ sáu
pilot train và summary; phiên triển khai này không tạo commit đó. Từ sáu pilot
N=2 đã có (90,329–133,649 CPU-s/record), scale projection N=200 cũ về N=32:
**74,153640 CPU-h**, cộng trace theo phép đo trên thành **74,167749 CPU-h**;
wall lý tưởng **2,472258 giờ/30 workers** cho 150 records. Đây là ngoại suy
train-only, không phải thời gian GCP đo được, CI hoặc upper bound; khác biệt
test workload, serialization, khởi tạo process và contention còn chưa đo.

Bằng chứng lưu tại:

- `results/letter/v7_3/test_impl_validation/pytest_complete.log`
- `results/letter/v7_3/test_impl_validation/pytest_slow.log`
- `results/letter/v7_3/test_impl_validation/pilot_equivalence.json`
- `results/letter/v7_3/test_impl_validation/verification.json`

Audit byte: **13/13** source/card/params/brief cũ khớp `0f8ec8229`;
**14/14** file pilot khớp commit pilot bên ngoài. Không tạo
`results/letter/v7_3/test_congested/`, score thật, CSV outcome hoặc biểu đồ.

Trước lock, Claude cần review và chốt cách đọc forecast chưa ghi hết population
trong card: F1 hiện báo weekday S ở cả ba regime và từng regime riêng; F4 gộp
mọi regime/stratum với fresh chỉ đếm một lần; F7 dùng mọi horizon vì card không
giới hạn, đồng thời báo split từng horizon. F5 yêu cầu từng pipeline đạt 80%,
có thêm joint count mô tả. Nếu muốn nghĩa khác, cần làm rõ card **trước** lock;
chưa sửa card/params hoặc bất kỳ threshold nào. Không có FAIL kỹ thuật đã biết;
lock thật, native fingerprint verification, run/pool trên VM và rescore thật
vẫn chưa được thực thi, theo phân công brief.

## Fix 18/11 (Codex theo `V7_3_test_fix_brief.md`; phần ghi này do Claude thêm vì lượt Codex bị ngắt khi tắt máy lúc 07:20)

- **Lỗi:** `capacity` lưu dạng shape (1,), nên `float()` lỗi ở bước strata của `run()`. Đã sửa bằng `np.asarray(...).item()` ở 3 chỗ. Audit 68 phép chuyển scalar trong `scalar_audit.json`: không còn cast size-1 nào khác.
- **Refactor không đổi engine:** tách `write_record` và `prepare_inputs` khỏi `_record`/`run`. Nhánh train-only kiểm đúng code path của run. Diff nằm ở `test_impl_validation/fix_18_11/*.diff`.
- **Integration ngày train S DAY1 2005-05-06** (N=2, K/R đầy đủ, pilot seed): JSON ghi/đọc được, score/rescore khớp **8/8 cases, 0 mismatch**, 91,27 CPU-s. Kết quả trong `integration_result.json`. Dry run trước pool trên 26 ngày train cho 78 nhãn.
- **Claude chạy lại sau khi khởi động lại máy:**
  - toàn bộ `tests/test_letter_v7_3*.py`: **98 passed** (gồm 4 slow, có pilot bit-for-bit), 404,86 s, log ở `resume_18_11/pytest_all.log`;
  - pool spawn 3 workers trên ngày train (DAY1 05-06/05-11, DAY3 05-06, N=2): **3/3 records** ghi đúng.
