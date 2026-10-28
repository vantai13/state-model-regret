# A05-F — thiết kế A, shared Gaussian threshold ledger

Người phụ trách: **Doan Van Tai**. [Prereg](prereg.md) và [author decision](author_choices.json).
Prereg/source phải commit trước fit; theta commit trước held-out features;
predictions/discrimination commit trước freeze receipt. Không amend/overwrite.

```bash
.venv/bin/python -m pytest tests/test_a05_math.py tests/test_a05_freeze.py -q
.venv/bin/python -m experiments.A05_freeze.fit
# Commit results/A05_F/20261028_01/ trước lệnh dưới.
.venv/bin/python -m experiments.A05_freeze.predict
# Commit predictions_heldout.json,discrimination.json,features_heldout.json trước:
.venv/bin/python -m experiments.A05_freeze.freeze
# Commit freeze.lock.json và canonical note; rồi kiểm verify_frozen().
```

Features chỉ thiết kế/plant/formula bậc0–2; không import queue/D/kernel.
Fit đọc38ô A04, chia20lát; mỗi bên12coefficients/2candidates/2starts.
Kappa là memory time. Gaussian/feasibility/normalization và optimizer dùng chung.
K5carry nguyên văn; C1 là equivalence≤.005 sau discovery với base36/38.

`score_test.py --input ...` là scorer cho L3.7, kiểm SHA/freeze **trước** đọc true
input; không có engine trong scorer. L3.6 không tạo file outcome hoặc chạy A05-T.
Canonical note là snapshot freeze, không phải chứng nhận human reader hoặc ghi
quyết định không đảo ngược. Frozen A00 source giữ byte để bảo tồn A01/A04.

Thư mục này được source.lock khóa; A05-T runner mới phải ở thư mục khác để
không đổi source snapshot đã dùng tạo predictions. Reporting sau freeze dùng
`experiments/lessons/`, không sửa code/model/config đã đăng ký.
