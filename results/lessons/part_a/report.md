# L2.1–L2.3 — báo cáo triển khai và kiểm chứng

Người phụ trách: **Doan Van Tai** · 24/10/2026. AI triển khai theo yêu cầu hoàn
tất artifact và chạy kiểm. **Technical implementation PASS; formal Part A HOLD**
do điều kiện con người/source reading và deviation đã ghi, không phải lỗi code.

## A. Công việc đã thực hiện

| Lesson | Deliverable đã lưu | Trạng thái kỹ thuật |
|---|---|---|
| L2.1 | 6 claims, falsifiers, K2/K3/K5/K6; prior forecasts; reading/stopping rules; artifact classification; search log, matrix, terms, paper-note structure | Đã lưu, có receipt; forecasts AI-assisted và exposed |
| L2.2 | T03 v2: hai phép dẫn/G1–G5; code và independent VSS checker; full-family CSV/JSON/config/log; SOB14/B82/MAB11/E07 notes; 6 dòng already_implied | 21.952 toy PASS; limitations nguồn ghi riêng |
| L2.3 | P11 note/6-row comparison; SOC12 matrix row; 4-prior toy; 17 checks; corrected boundary/brief/heads-up wording; reference self-check answers | 17 exact checks PASS; không L-self |

Điểm vào: [literature README](../../../notes/literature/README.md),
[claims](../../../notes/literature/claims.md),
[prior boundary](../../../notes/literature/prior_boundary.md),
[T03 v2](../../../notes/theory/T03_primary_reading_start.md),
[đáp án tham khảo](../../../notes/lessons/L2_part_a_review.md).

Contract v1.2/grid/thresholds/held-out giữ nguyên. Chưa chạy Phase3 contrast,
chưa fit H0/H1 hoặc kiểm held-out, chưa xác nhận novelty/G2.

## B. Commands và kết quả thực chạy

Chạy từ repository root:

```bash
python3 -u -m experiments.lessons.l2_2_voi_mapping > results/lessons/l2_2/run.log 2>&1
python3 -u -m experiments.lessons.l2_3_p11 > results/lessons/l2_3/run.log 2>&1
.venv/bin/python -m pytest -q tests/test_l2_part_a.py --junitxml=results/lessons/part_a/pytest_lesson.xml > results/lessons/part_a/pytest_lesson.log 2>&1
.venv/bin/python -m pytest -q --junitxml=results/lessons/part_a/pytest_full.xml > results/lessons/part_a/pytest_full.log 2>&1
python3 -u -m experiments.lessons.audit_l2_part_a > results/lessons/part_a/artifact_audit.log 2>&1
```

System Python experiment: 3.14.5, standard library/Fraction, không RNG, seed=null.
9/9 lesson tests PASS; full suite **202/202 PASS**, 26.72s tại lần chạy lưu log.
Thử gọi system python pytest ban đầu thất bại vì thiếu pytest; đã chuyển sang
.venv có sẵn. [Preflight](preflight.log) giữ lỗi thật; không gọi đó là test PASS.
Audit độc lập đọc toàn CSV, dựng lại costs/contrasts/counts không import scorer,
kiểm golden P11 và source hashes; trạng thái/số links trong [JSON](artifact_audit.json).
Kết quả thực chạy: **21.952/21.952 dòng khớp**, 17 P11 checks được đối chiếu,
**47 local links** hợp lệ, source hashes khớp, không PDF trong literature repo.
Đây là kiểm artifact bằng máy, không thay independent human review.

## C. Số đo — exact verification toy

C=3 packet/s, managed u=2 packet/s, q0=0, dt=1s/H=1; hai mode prior1/2.
Mỗi mode có hai giá trị background đồng xác suất, A/B độc lập conditional mode.
Họ gồm mọi bộ ba cặp phân biệt từ {0,…,7}: 28^3=21.952. Cost/gain đơn vị packet·s;
Fraction exact, không CI/MC uncertainty. Không phải R2-law grid v1.2.

| Phép kiểm L2.2 | Baseline hoặc mutation result |
|---|---:|
| I1–I6 vi phạm | 0 ở từng invariant |
| Wrong belief: I1 vỡ | 410; cả410 tăng, giảm0 |
| Mean-state thay D10: L00 đổi | 3.528 |
| Tie Switch: I1 vỡ | 0, equivalent control đúng kỳ vọng |
| M0 bỏ mode: independent I2 vỡ | 5.730 |
| Cùng lỗi nhưng reused-action checker vỡ | 0, chứng minh blind spot checker |
| GS<0 | 2.048 |
| Gamma>0 / <0 / =0 | 2.698 / 1.436 / 17.818 |
| M0 tốt hơn / tệ hơn global-EV action | 2.434 / 1.094 |
| EV>WS / EV>RP | 137 / 0 |
| Subjective/objective EVPPI khác nhau khi prior sai | 1.940 |

Golden V1: (L00,L10,L01,L11)=(5/4,3/2,5/4,5/4), GS−1/4, GM0,
Gamma1/4, GSgivenM1=0, GMgivenS1=1/4. Golden V2:
(3,5/2,11/4,5/2), GS1/2, GM1/4, Gamma−1/4, GSgivenM1=1/4, GMgivenS1=0.

| P11 toy prior | Action | Belief VOI | True regret |
|---|---|---:|---:|
| −1/+1 | Stay | 1/4 | 1/2 |
| 0/+2 | Switch | 1/4 | 0 |
| Point0 | Stay | 0 | 1/2 |
| Point1 | Switch | 0 | 0 |

L2.3 **17/17 checks PASS**. V2 known-law hidden-state discrepancy disclosure:
cost 11/4→5/2, value1/4. V1 model same-info upper bounds: GM0 dưới S0,
GMgivenS1=1/4 dưới S1; GS−1/4 không bound no-op0.

## D. Đường dẫn output

- Sources: `experiments/lessons/l2_2_voi_mapping.py`, `l2_3_p11.py`,
  `audit_l2_part_a.py`; tests `tests/test_l2_part_a.py`.
- [L2.2 summary](../l2_2/voi_mapping.json), [từng case](../l2_2/cases.csv),
  [config](../l2_2/config.json), [log](../l2_2/run.log).
- [L2.3 summary](../l2_3/p11_toy.json), [bảng CSV](../l2_3/p11_toy.csv),
  [config](../l2_3/config.json), [log](../l2_3/run.log).
- [Lesson test log](pytest_lesson.log), [full test log](pytest_full.log),
  [JUnit lesson](pytest_lesson.xml), [JUnit full](pytest_full.xml).
- [Source metadata](source_metadata.json), [trạng thái tải/checksum](source_access.json).
- [Artifact audit](artifact_audit.json), [audit log](artifact_audit.log).
- [Checksum các file](SHA256SUMS); tái kiểm từ root bằng
  `sha256sum --check results/lessons/part_a/SHA256SUMS`.

PDF/text primary ở `~/papers/l2_part_a/`, ngoài repo. Không tạo biểu đồ vì các
bảng exact đã thể hiện đủ kết quả; không có figure artifact.

## E. Checklist / Gate trung thực

| Yêu cầu | Trạng thái |
|---|---|
| L2.1 claims/dự đoán/file khung/phân loại và receipt | DONE; commit5ab4750 |
| L2.1 dự đoán commit trước đọc L2.2 | DEVIATION không thể khôi phục: chat đã exposed |
| T03 proofs có assumptions/corrections/changelog | DONE; commit3870931, AI-assisted |
| Code, golden, invariant, mutants và output tái lập | PASS |
| Paper notes, source locations, matrix/boundary/already_implied | DONE; mức đọc thật ghi riêng |
| B82 full definition/bounds; MAB11 §2 | ACCESS LIMITED: PDF403, B82 OA fallback thất bại; không dùng theorem chưa đọc |
| Tác giả tự dẫn kín sách/L-self | Chưa có record; không tự cấp PASS |
| Đọc lại sau một ngày / người thật kiểm claims | Chưa có record; không dùng thời gian máy chờ thay evidence |
| Formal Part A đủ điều kiện L3.3 freeze | HOLD; bộ artifact hoàn thành không tự mở gate |
| G-level / Phase4 | G1; HOLD Phase4 như record trước |

Tác giả đã giao AI tự thực hiện, nên các phần AI làm thay được đã lưu đủ.
Những dòng cần hành vi con người hoặc lịch sử trước exposure được giữ rõ,
không dựng evidence. Học tiếp L2.4 được; không tự chạy L3.3/Phase3.

Hai commit đầu là receipts sau exposure, không backdate hoặc gắn tag mù.
Commit tích hợp sau chứa code, data và báo cáo; không ghi hash vào chính commit.
Không push hoặc gửi heads-up trong tác vụ này.
