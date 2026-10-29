# L3R.4 — Realism screen đã chạy; realism HOLD_UNSOURCED

Người phụ trách/người soạn: **Doan Van Tai** · 29/10/2026.

**Đã kiểm công thức, đọc nguồn được duyệt, khóa envelope trước bảng216 và
đối chiếu tín hiệu sau checkpoint nhãn. Chưa có đủ evidence để chứng nhận
realism cho model value hoặc harm ở cả DC(a) và edge(b): cả hai nhánh(d) HOLD.**
UNSOURCED nghĩa là chưa sàng lọc được bằng dải nguồn tương thích; không phải
đã chứng minh mô hình phi thực tế, cũng không phải PASS realism.

## Đã triển khai

- Đọc đủ3phần lesson,848dòng, kiểm T00/DL-008 và research/search protocol.
- Viết [implied.py](../../../experiments/R3R_04_realism/implied.py) chỉ toán học,
  stable window CV, tách η=u/2 và φ=u/(c−λB), explicit h/τ, before/after-load,
  CTMC event count/R2 boundary flip và mode correlation.
- [Mô phỏng generic](../../../experiments/R3R_04_realism/generic_sim.py) dùng
  Exp(T) event times, reflected linear queue, exact path integrals; không gọi
  engine đang kiểm. Cost homogeneity test cần q0×ks và c_sw×ks².
- Được duyệt cả3nguồn trước PDF/content notes; đọc targeted BAM10/ZLK17/LTWW94,
  PDF ngoài Git. Catalog/Excel23→26;23catalog records và23+23workbook rows cũ
  giữ nguyên. Không tăng mức đọc tác giả. Không broad survey/saturation/novelty.
- [Worksheet](../../../notes/realism/worksheet_v1.md) giữ missing ranges, không
  đánh đồng polling với tuổi backlog, throughput burst với holding time,
  egress rate với offered arrivals hoặc normalized shared occupancy với buffer budget.
- [Luật/envelope](../../../notes/realism/envelope_v1.json) k1,f2,sensitivity1.5/3;
  hai bối cảnh định trước DL-008. Anchor10ms/100ms chỉ minh họa dịch đơn vị,
  không là tuổi có nguồn. Thiếu một range bắt buộc ⇒ UNSOURCED.
- Sinh432feature rows,1296label rows bằng [runner](../../../experiments/R3R_04_realism/run_screen.py),
  checkpoint trước [overlay](../../../experiments/R3R_04_realism/overlay.py)
  các CSV discovery đã lưu. Không chạy lại216pilot outcomes.
- Kiểm stationary-only tại3ID discovery đã khai: X2041/X2012/X1009,
  Apre/Bpre,ref1/2; không J/gap/decision/regret/contrast mới.
- [Review tự động riêng, giới hạn input](blind_review.md) chỉ xem envelope,
  worksheet,rules,labels,receipt; không thấy gains/outcomes/source. Không human review.
- Soạn [realism note](../../../notes/realism/realism_note_v1.md) và
  [scope proposal](../../../notes/realism/contract_scope_proposal.md) cho L3R.5;
  không adopt contract hoặc CFframe.

## Chuỗi commit và lỗi giữ lại

1. cbed2bc: generic prereg/source trước MC.
2. 6bef959: nguồn/worksheet/envelope/rules trước bảng216.
3. Run đầu dừng ở `dict()` nhận trùng `kappa` khi ghép feature đầu tiên;
   chưa tạo label CSV. [Log FAIL](screen_attempt1_failed.log),
   [regression đỏ](export_regression_red.log). Sửa xuất bảng ở830a187,
   không đổi công thức/ngưỡng/luật/envelope. [Bản ghi sửa](../../../experiments/R3R_04_realism/export_fix.json).
4. 1164500: checkpoint đủ labels/receipt trước đọc lại discovery outcomes
   trong overlay. Scientific envelope vẫn6bef959, execution source830a187.

Full suite trước sửa xuất bảng490PASS chưa bắt được lỗi này; test export generic
thêm vào tái hiện FAIL rồi PASS. Full suite cuối **491/491 PASS,61.94s**,
targeted **24/24 PASS**. Logs gốc và trước sửa đều được giữ.
Local `python` không có và venv không córequests; dùng `.venv/bin/python`/urllib,
không đổi dependencies. BAM10 direct-download timeout/404 được giữ trong access log;
paper-pilot lấy đúng MSR PDF. Leland Stanford là conference1993, bản đọc là journal1994.

## Số đo thực tế

MC dùng c10,a6;3generic cases×8replicates=24roots; burn1000s rồi đo4000s mỗi
replicate. Seeds318400000+1000case+replicate, không dùng cho CF. **18/18 checks
đạt** dung sai khai trước4SE+1%|formula|+1e−8. SE dưới đây là replica SE,
không CI coverage được chứng nhận.

| λ | T(s) | Delay công thức(ms) | Delay MC(ms) | Replica SE(ms) |
|---:|---:|---:|---:|---:|
| 8 | .1 | 60 | 60.768866 | .729376 |
| 8 | .3 | 180 | 180.709173 | 3.431175 |
| 9.5 | .1 | 330 | 333.984490 | 11.769822 |

Tạiλ8,T.1: atom công thức.25, MC.250275872; tail delay>.1s công thức.214878598,
MC.216649713; CV_rate100ms công thức.565077914, MC.564874773.
Toàn bộ18metrics, dung sai/SE: [comparisons.csv](generic/comparisons.csv).

Stationary-only comparison, baseτ=1s,6queues mỗi ref:

| Max absolute difference slot–fluid | ref1 | ref2 |
|---|---:|---:|
| Atom probability | .018419199 | .009607109 |
| Mean virtual delay(ms) | .386527333 | .096702391 |
| Tail tại delay=5T | .000228336 | .000027766 |

Fluid liên tục là reference approximation, không exact slotted answer.
Spectral mean là numerical estimate chưa có certified unbounded-moment bound;
TVcertificate không đủ để chặn meanQ. Không dùng phép kiểm này đóng gateL3R.3.
[12rows và certificates](stationary/comparisons.csv).

| Vùng theo discovery đã lưu | ID | Tọa độ khác nhau | a: DC | b: edge |
|---|---:|---:|---|---|
| ALL | 216 | 210 | 216UNSOURCED | 216UNSOURCED |
| MV:GM/Cref≥1% | 20 | 20 | 20UNSOURCED | 20UNSOURCED |
| SH:GS/Cref≤−1% | 80 | 78 | 80UNSOURCED | 80UNSOURCED |
| MV∩SH | 14 | 14 | 14UNSOURCED | 14UNSOURCED |

Không IN/EDGE/OUT được chứng nhận trong v1. Cảf1.5/2/3 cho cùng nhãn vì thiếu
range, **không phải** evidence rằng nhãn robust khi ranges thay đổi. Ba cờ riêng:
buffer UNSOURCED, actuation UNSOURCED, mode-oracle TRUE. Không nguồn B_t/d_act
thì không tự điền xác suất drop hoặc actuation effect. Tailbudget5T chỉ sensitivity:
Bpost có max.227946550, không phải22.79%drop ở mạng thực.
Mode-correlation overage min2.06115e−9,max.513417119, không backlog correlation/gain.
Đếm ID và coordinate khác nhau, không prevalence do discovery thích nghi.
[Counts đủ24tổ hợp](overlay/summary.csv), [by-ID](overlay/by_id.csv).

## Lệnh đã chạy và nơi lưu

```bash
.venv/bin/python -m experiments.R3R_04_realism.generic_sim
.venv/bin/python -B tools/paper_library/build_notes.py
.venv/bin/python -m experiments.R3R_04_realism.run_screen --freeze 830a187
.venv/bin/python -m experiments.R3R_04_realism.check_stationary --freeze 6bef959
.venv/bin/python -m experiments.R3R_04_realism.overlay --labels-commit 1164500
.venv/bin/python -m pytest -q --junitxml=results/lessons/l3r_4/full_suite.xml
.venv/bin/python -m experiments.R3R_04_realism.verify_saved
```

Commands dùng redirect log riêng; không chạy lại MC/engine để tạo report.
Lệnh stationary6bef959 ở trên là lịch sử trước exportfix. Replay trên worktree
hiện hành dùng `--freeze 830a187`; source stationary/formulas giữ nguyên byte,
verifier kiểm điều này. Muốn replay đúng toàn source cũ thì checkout6bef959 riêng.
[commands.json](commands.json) ghi cả lần FAIL. [full-suite log](full_suite.log),
[targeted log](targeted_tests.log), [MC log](generic_run.log), [A2 log](screen_run.log),
[stationary log](stationary_run.log), [overlay log](overlay_run.log),
[saved-evidence audit](verification.json). Các log trước sửa vẫn giữ.
Audit saved evidence đạt:13frozen inputs,3.024cross-anchor checks,51legacy files,
187artifact auditL3R.3 giữ nguyên; plan nguồn giữ nguyên byte. Lần verifier đầu
kiểm link tới output của chính nó trước khi tạo file nên dừng; đã sửa thứ tự
self-link check, giữ [log](verify_attempt1_self_link.log), không chạy lại engine.

Cấu hình: [generic prereg](../../../experiments/R3R_04_realism/generic_prereg.json),
[envelope](../../../notes/realism/envelope_v1.json). Dữ liệu:
[replicate seeds](generic/replicates.csv), [implied CSV](screen/implied_features.csv),
[labels CSV](screen/labels.csv), [screen receipt](screen/receipt.json),
[summary JSON](summary.json). Không tạo chart trong phiên này.

PDF nguồn ngoàiGit tại `~/papers/state-model-regret/l3r_4/` và bản mở Excel ở
`~/papers/state-model-regret/current/`; không push PDF. [Downloads/errors/hashes](literature/downloads.json),
[approval](literature/approval.json), [library preservation](literature/library_preservation.json).
Môi trường Python3.14.5,NumPy2.5.3,SciPy1.18.1,mpmath1.3.0.

## Kết luận và việc còn mở

Được xác nhận: công thức qua MCgeneric trong dung sai, pipeline giữ missing nguồn,
đủ216/210, provenance envelope→labels→saved-overlay, tests/integrity đạt.
Review riêng xác nhận label consistency và4hashes trong input được phép; không
kiểm primary papers hay chronology. Nó chỉ ra trước envelopev2 cần khóa cách
đếm mean/peak ghép dưới k1 và phép nới định tính; v1 toànmissing nên chưa exercise
phân loại số trên empirical ranges. Unit tests common-τ là toy, không validation.

**MV(d) HOLD; SH(d) HOLD**. Cần số đo/schema phù hợp cho backlogAoI,holdh,
offered input/CVfixedwindows,absoluteperqueuebuffer và action delay trước chứng nhận
realism. Nguồn/ranges mới phải version sau quan sát; không sửa frozenv1 để cứu
vùng tín hiệu. Chưa adopt CFframe hoặc contractv1.3; numericsNOT_FROZEN/auditL3R.3HOLD.
Không CF/R09/R10 outcome mới, không pilot merge/src promotion. Full tests có
regression toy cũ; không là run confirmation mới. G1/Phase4HOLD, Understanding,
P0-V10/L8/T05author-writing vẫn OPEN. Có thể học/soạn L3R.5 trong các giới hạn này.
