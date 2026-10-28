# L3R.2 — Estimand population, T07 và golden toy

Người phụ trách/người soạn: **Doan Van Tai** · 28/10/2026 · DL-065.
Trạng thái: **HOÀN TẤT KỸ THUẬT**. Understanding/read-back kín sách **OPEN**.
T07 và bài giải được soạn theo ủy quyền; không ghi thành tác giả đã tự viết/tự chạy
hoặc human review. G1 không đổi; contract v1.3 vẫn DRAFT, Phase4 thực thi HOLD.

## Đã làm

Đọc đủ ba phần lesson; đối chiếu T01, D9–D23 contractv1.2, draftv1.3 và plan§9.
Viết [T07](../../../notes/theory/T07_population_estimand.md) đủ 8 mục: ba tầng cost,
bốn policy, sáu contrast, D22, giả định, **18 sanity rows** kèm lý do/proof, 4 nhóm
claim có thể sai, lựa chọn còn OPEN và đáp án toy. Giữ người phụ trách Doan Van Tai.

T07 + golden/spec/runner/DL được commit **315d2037c3877c2616212ffccdfd44be9b3e4df9**
trước run toy và trước mọi kết luận audit L3R.3. Đây không là freeze contractv1.3.
Không mở code engine population để viết reference, không merge pilot branch.

Lưu 8 golden test nguồn bằng Fraction; thêm 8 kiểm có mục đích: bảng bias và bước
nhảy trên support hữu hạn, hai cách ratio, invariance với cùng marginal, population
trigger đổi marginal, chiều đảo Γ/harm sai, zero-stakes/D22 vắng, tie ở S0/cb0 và
bound Γ chặt hơn. Không coi số 8/8 reviewer báo là lần chạy local.

## Đã chạy và kết quả thực tế

Chạy từ repo bằng virtualenv:

```bash
.venv/bin/python -m pytest -q tests/test_population_toys.py --junitxml=results/lessons/l3r_2/toy_tests.xml
.venv/bin/python experiments/lessons/run_l3r_2.py --out results/lessons/l3r_2/toys
.venv/bin/python -m pytest -q --junitxml=results/lessons/l3r_2/full_suite.xml
.venv/bin/python experiments/lessons/audit_l3r_2.py
```

Stdout/stderr ba lệnh đầu đã redirect vào log; lệnh audit lưu audit.log/verification.json.

- Golden: **16 passed in 0.47s**, không fail/error/skip.
- Full regression: **439 passed in 61.95s**, không fail/error/skip (trước lesson 423).
- **500 joint laws hữu hạn**, seed **20261028**, **0 vi phạm** identity/bounds trên
  reference đúng. Kiểm bound bổ sung dùng lại cùng 500 laws, không cộng thành 1.000.
  Chạy lại cùng seed trong test/runner là replay, không tăng số plant phân biệt.
- **5/5 mutant KILLED**: S0 nhìn state, tie Switch, M1 dùng gap M0, oracle lấy max,
  cb0 giấu backlog mới. Chỉ gọi KILLED khi có AssertionError của kiểm vốn PASS trên
  baseline, không dùng exception chạy lỗi làm bằng chứng bắt mutant.
- Auditor đối chiếu source/commit/hash, XML/metrics, links và freeze v1.2/A05 cũ;
  **4 source hashes, 4 output hashes và 123 local links PASS**; freeze cũ PASS.
  Trạng thái cuối cùng và số đếm nằm ở [verification.json](verification.json).

Lần gọi `python` global đầu tiên exit127 vì máy không có binary đó; chưa chạy test
hay thí nghiệm. Sau đó dùng `.venv/bin/python` xuyên suốt; không có test khoa học FAIL.

## Bảng số đo toy

Mọi số cost/gain trong bảng là **đơn vị cost quy ước của toy**, không phải packet·s
được đo từ plant mạng. Exact Fraction; không Monte Carlo, không CI hoặc sai số ước
lượng trên các tổng hữu hạn này. 500 law ngẫu nhiên chỉ kiểm reference, không chứng
minh định lý tổng quát hay prevalence ngoài đời.

| Toy | L̄00 (S0/M0) | L̄01 (S0/M1) | L̄10 (S1/M0) | L̄11 (oracle) | ḠS | ḠM | Γ̄ |
|---|---:|---:|---:|---:|---:|---:|---:|
| Ba snapshot | 9.25 | 9.01 | 9.25 | 9.01 | 0 | **0.24** | 0 |
| Tuổi ngắn | 9.5 | 9.3 | 9.5 | 9 | 0 | 0.2 | 0.3 |
| Tuổi dài | 9.5 | 9.5 | 9.5 | 9 | 0 | 0 | 0.5 |
| Lỗi bù trừ (−2,+3) | 10 | 10 | 10.5 | 10 | **−0.5** | 0 | **+0.5** |
| Biến thể (−4,+3) | 11 | 10 | 10.5 | 10 | **+0.5** | 1 | **−0.5** |

Ba snapshot ở runner dùng JStay=10 thay vì 0 trong test nguồn để trình bày cost dương;
cộng cùng baseline không đổi actions, contrasts hoặc đáp án ḠM=6/25.

| D22 | ḠS | L̄cb0 | F̄ (backlog mới) | V̄ (thấy mode) |
|---|---:|---:|---:|---:|
| Hai state chỉ khác mode | −0.5 | 10 | **0** | **−0.5** |
| Hai state chỉ khác backlog | −0.5 | 10.5 | **−0.5** | **0** |
| Bốn state triệt tiêu | 0 | 10 | **−0.5** | **+0.5** |

Cùng GS âm không xác định được harm do backlog hay mode. GS=0 cũng có thể che hai
phần F/V khác 0 triệt tiêu nhau. Đây là minh họa finite toy, chưa phải cơ chế pilot.

Chuẩn hóa: ratio-of-expectations **1%**, expectation-of-ratios **5%** trên cùng toy.
Nếu gain13%C̄ và stakes30%C̄, tỷ lệ lấy lại stakes=**43⅓%**. Không trộn hai mẫu số.
Bảng bias b=.1/.2/.3/.4 cho GM population=.005/.020/.045/.080, còn fixed y=.35 cho
0/.15/.15/.15. Với support hữu hạn này vẫn có bước nhảy GM 0→.005 tại b=.05.

## Những chỗ đã sửa hoặc bổ sung điều kiện trong lesson

1. Các câu remote66f167d/chưa tag/chưa L3R.1 đã cũ: main có L3R.1 bf3915e;
   tag explore-v13-pilot=a7435e9. Không thực hiện lại L3R.1.
2. S1/C̄ref/stakes bất biến chỉ khi **marginal X, cost J và S1 policy cố định**.
   Coherence cho total expectation nói chung; stationary/periodic là giả định target
   population cần quyết sau. Trigger theo Y đổi joint law, có thể đổi marginal và S1.
3. Harm⇒Γ≥|GS| là bắt buộc. Trong **162 cấu hình phân biệt Stage1+2**, 79 cấu hình
   có |Γ|≥1%C̄; cả 79 có GS<0. **79/79 là discovery**, không phải số đếm toàn bộ210
   cấu hình pilot (Stage3 báo riêng). Đã đối chiếu lại aggregate `part1_distinct`
   của L3R.1 đã lưu, không đếm/chạy lại raw. Không
   suy được chiều đảo từ định lý; có toy GS=0,Γ=.5. Không gọi quan sát đó là identity.
4. Chặn [−σ̄,2σ̄] của lesson đúng nhưng lỏng; từ Γ=GM|S1−GM và hai số trong [0,σ̄]
   có chặn **[−σ̄,σ̄]**. Đây là suy toán, không đổi Γ/metric/threshold.
5. Golden nguồn để cb0=0 ngay khi không khai q; F/V lúc đó không có ý nghĩa. Bản này
   bỏ cb0/F/V khi không có q. Mọi đáp án 8 test nguồn vẫn giữ nguyên. F/V có thể âm
   nhưng có bound ±stakes, không hiểu “không có sàn” thành âm vô hạn.
6. Không suy smoothness toàn cục từ toy hữu hạn hoặc tự kế thừa εR1% cho population.

## File lưu

- [T07 định nghĩa/proofs](../../../notes/theory/T07_population_estimand.md).
- [Golden source](../../../tests/test_population_toys.py), [runner](../../../experiments/lessons/run_l3r_2.py),
  [spec/seed/phạm vi](../../../experiments/lessons/l3r_2_spec.json), [auditor](../../../experiments/lessons/audit_l3r_2.py).
- [Cost/contrasts exact + decimal JSON](toys/metrics.json), [mutants](toys/mutants.json),
  [baseline checks](toys/baseline.json), [source hashes/commit](toys/manifest.json).
- [Golden log](toy_tests.log), [runner log](toy_runner.log), [full log](full_tests.log),
  [golden XML](toy_tests.xml), [full XML](full_suite.xml), [audit log](audit.log),
  [verification](verification.json), [intake nguồn](lesson_intake.json).
- [Completion](../../../notes/phases/L3R_2_completion.json), DL-065/exposure/progress/index.

Không tạo CSV, biểu đồ, simulation population mới, pilot raw mới hoặc CF output;
JSON đã giữ exact fractions và decimal cho những số toy được báo.

## Kết luận và phần còn mở

Đã có reference exact bằng toy để phát hiện các lỗi nêu trên và T07 được commit
trước audit. **Chưa xác nhận engine pilot tính đúng**, chưa chứng minh harm/phân bố
hay cơ chế trong plant thực, chưa xác nhận novelty hoặc realism. Full suite gồm các
regression engine v1.2/toy cũ; không phải audit population mới.

Understanding/self-read-back, P0-V10/L8/T05 author-writing vẫn OPEN; v1.3 law/primary/
threshold/numerical policy vẫn OPEN. V9 giữ WAIVED_BY_AUTHOR theo DL-054, G1 giữ nguyên,
Phase4 thực thi HOLD. Tiếp theo **L3R.3: audit engine từ T07**, trong experiments;
không dùng T07 soạn theo ủy quyền để tự promote engine vào src.
