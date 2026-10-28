# L3.6 / A05-F — đã đóng băng trước held-out outcomes

Người phụ trách: **Doan Van Tai** · 28/10/2026. **Hoàn tất kỹ thuật L3.6**.
H0/H1, θ, luật chấm, K5/C1 và dự báo đã khóa. **A05-T chưa chạy**; chưa có
kết luận SUPPORT/WEAKEN/FALSIFY hoặc điểm K5/C1 trên held-out.

## 1. Đã làm và thứ tự commit

- Author chọn D25(ii)/thiết kế A: `51c926fda9a2442c02b320d6dad1063def91d075`.
- Prereg, code, budget và luật chấm: `57d84c66fc2cfca6de6fbbda662918959cd99fc5`.
- Fit A04/LOSO và θ: `6aa696a958ec0ee09242812c94762a0f42927f89`.
- Features/predictions/discrimination: `3c75aecd720ef688923d818bc41f3db4a82742ec`.
- Freeze receipt/canonical note: `5f201030cebec0f916ef5db7625ca86c7e11833c`.

Đã thêm addendum headroom vào note A04/boundary theo kiểu append-only.
P5-K đứng đã bị headroom baseline chặn; không nhận rằng nó chứng minh M0
mô tả tốt động học. P3 trượt cũng nằm dưới trần headroom tại các ô của nó.
Kỳ vọng gap M0 bằng0 không tự chứng minh từng state gap0 hoặc không có idle.

## 2. Kết quả chạy và baseline

**369 tests PASS**, gồm21 tests A05; suite60,31s. 80 fold LOSO được replay
đúng từ θ từng fold và scaling tính trên train;2 fit toàn tập sau chọn.
Tổng164 solver starts, 0 start không thành công; fit hoàn tất trong
**5.649635 giây**. Không dùng held-out trong fit.

| Model | Candidate được chọn | k | LOSO summary MSE | LOSO RMSE (điểm %Cref) |
|---|---|---:|---:|---:|
|H0|coordinates_0|12|0.001250847025|3.536732|
|H1|dynamics_1|12|0.000986569557|3.140970|

H1 có LOSO summary MSE thấp hơn H0 **21.1279%**. Đây là so sánh nội bộ
trên discovery để chọn mô hình, không xác nhận RQ2. Loss này dùng4 summaries;
metric PC4 thật đã khóa là MAE đều GS/GM/Gamma, sẽ chấm bằng true intervals
ở A05-T. Không đổi metric để chọn chỉ số thuận lợi.

Cùng Gaussian,12 hệ số,2 candidates/bên,2 starts,optimizer/ridge/scaling/tie
và feasibility. Rho cố định0 cho cả hai; null vẫn sinh Γ>0/GS<0 trên toy.
Scaling mỗi fold chỉ dùng training partition;20 lát, không LOOCV từng ô.
H0 có bias phụ thuộc tọa độ; H1 dùng variance telegraph/fluid-boundary/drain
proxies. Kappa là memory time, rate correlation=2/kappa. Không có queue D
hoặc cost/gap thật trong feature module.

## 3. Khả năng phân biệt trước outcomes

Margin m=0,25 điểm phần trăm Cref. D=mean|predictionH0−predictionH1| trên
metric đã khóa; **D không dùng y thật**, khác với d=MAE0−MAE1 sau test.

| Nhóm | n | D (điểm %Cref) | Kế hoạch comparison |
|---|---:|---:|---|
|interpolation|8|0.59123887|OPEN_COMPARISON|
|weak_interpolation|2|0.21229705|DO_NOT_OPEN_COMPARISON|
|extrapolation|2|0.47495167|OPEN_COMPARISON|

**R09/R10 giữ chưa mở**: D=0,212297<0,25, không outcome nào có thể làm
chênh lệch MAE đạt margin trong comparison này. Không hạ m, đổi candidate
hoặc gộp nhóm sau khi thấy dự báo. Universe vẫn đăng ký đủ12 ô; theo luật
union đã viết trước, A05-T chỉ cần **10 ô R01–R08,R11,R12**. K5/C1 nằm trong
8 ô primary. Nhóm ngoại suy báo riêng, không dùng để cứu verdict primary.
D≥m là điều kiện cần, không guarantee power hoặc causal identification.

## 4. Ba nhánh đã khóa

- **PC4:** H0/H1, MAE đều3 contrasts; SUPPORT nếu lower(d)≥m; FALSIFY
  nếu upper(d)≤0; WEAKEN nếu khoảng nằm trọn(0,m); còn lại INCONCLUSIVE.
  Enclosure paired dùng endpoint của |p0−y|−|p1−y|, không mất correlation.
- **K5:** copy nguyên văn card, m_rule_count=1, test R03/R04; Q-witness
  chỉM01–M04. Giữ luật3 trạng thái của A03 và nguồn “khóa trước A04”.
- **C1:** khóa sau A04, GM/Cref≤0,5% tại mọiR05–R08; không claim GM=0
  chính xác. Base rate cùng sự kiện36/38; heuristic4ô0,80551868. Con số
  0,64088673=(34/38)^4 chỉ cho nominalzero; cả hai không là xác suất thật.
- Với ô equivalence đứng và upper(R00/Cref)<0,5%, báo headroom-limited.
  Chưa biết nhãn ấy của R vì chưa tính headroom thật. Không gộp3 nhánh
  thành một “tỉ lệ thành công”.

Truth quality giữ cặp1/120→1/240 theo A03, bổ sung radius≤m/10 cho PC4.
Primary cho tối đa2/8 ô unavailable, báo n/N;secondary2ô cần đủ2. D phải
còn≥m trên eligible subset. K5/C1 không bỏ ô HOLD khỏi ALL. Chi tiết đầy đủ
trong prereg; không thay các gates đó sau khi thấy true outcomes.

## 5. Hash và kiểm chứng

- predictions_heldout.json SHA256: `9b93e3f3445d4ebc2fbda96f72988bc3bc78c5524df05825405c73f83093bb80`.
- discrimination.json SHA256: `cbd0851a47e5939a9ae68e342befdcb8171f5722c169f00cf77c66b86310afe5`.
-17 registered source hashes,147 A04 hashes và21 preparation hashes khớp.
- Replay24 model-cell predictions và3 nhómD khớp chính xác với files.
- Scorer verify frozen hashes trước đọc inputtruth; tests có dirty/committed
  tamper cases và kiểm không đọc input khi hash guard thất bại.
- Gaussian đã kiểm quadrature và2×2triệu toy samples; 100.000toyD có
  roundoff dương1288trường hợp,max6,66e−16,0vượt allowance; giữ raw số đo.

## 6. Exposure và giới hạn

λA là input cho cả hai theo lựa chọn trực tiếp DL-057. Cùng quyền input
không tự loại endogeneity do anchoring; chỉ claim paired predictive value
trong thiết kế này. Không claim absolute forecast accuracy hay cơ chế queue.
Features của12R đã exposed, bậc0–2, cóλA và stale observations. Không p_sw
thật, không posterior D, cost/gap/Cref/contrast/headroom thật của R. Không
fit/test bằng outcomes held-out; không gọi metadata là chưa từng chạm.
Các giả định Gaussian/rho0/fluid proxies,20lát và ngoại suyh12 vẫn là
limitations. T-H1: định giá cửa sổ[t0,t0+h], không long-run loss.
Không tra paper mới, không đổi thư viện/author reading/human gates.

## 7. Lệnh đã chạy và vị trí file

```bash
.venv/bin/python -m pytest tests/test_a05_math.py tests/test_a05_freeze.py -q
.venv/bin/python -m pytest -q --junitxml=results/lessons/l3_6/preflight/full_freeze_suite.xml
.venv/bin/python -m experiments.A05_freeze.fit
# commit theta6aa696a trước:
.venv/bin/python -m experiments.A05_freeze.predict
# commit prediction3c75aec trước:
.venv/bin/python -m experiments.A05_freeze.freeze
.venv/bin/python -m experiments.lessons.report_l3_6
```

Source/config/prereg/locks/rules/predictions: `experiments/A05_freeze/`.
Theta/CV/fit inputs/manifest/status: `results/A05_F/20261028_01/`.
Logs: `results/lessons/l3_6/fit.log`,predictions.log,freeze.log,final_freeze_audit.log.
Numbers: model_selection.csv,discrimination_groups.csv,freeze_verification.json.
Figure: freeze_diagnostics.png/.pdf. Preflight: full_freeze_suite.log/.xml.
Canonical note: `notes/lessons/A05_F_preregistration.md`; DL-057/DL-058.
report.md và verification.json là snapshot **chuẩn bị cũ f5699aa**, giữ để
không làm hỏng historical hashes; bản tổng kết hiện tại là freeze_report.md.

## 8. Kết luận và bước tiếp

**A05-F/L3.6 đã hoàn tất kỹ thuật.** Bước tiếp L3.7/A05-T sẽ thực hiện đúng
frozen protocol sau quyết định không đảo ngược được ghi trước run. Không
còn thay H0/H1/θ/feature/metric/margin/split theo outcome. L8/P0-V10 và
T05 author-writing/Understanding chưa tự đóng; Phase4 vẫn HOLD.
Chưa có bảng true cost baseline/repair trên R để báo; đó là việc của A05-T.
