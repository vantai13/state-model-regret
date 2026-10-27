# L3.3 / A03 — prediction card và kiểm chứng

Người phụ trách: **Doan Van Tai** · 27/10/2026. Card do AI hỗ trợ; không là lời giải
kín sách do AI giả làm tác giả. Tác giả tự xác nhận hai read-back ngoài repo và chọn K5;
[record nguyên văn](author_attestation.json), author-attested, không independently verified.

## A. Đã thực hiện

- Card có **4 forecast** P2/P3/P5/P6, **14 sanity**, **1 luật K5**. Giữ nguyên claims.md,
  miền và thresholds. PC1 sanity; PC4 deferred A05-F. Các forecast **không cơ chế**:
  không tự chọn route hoặc viết rồi nhận tác giả viết. Không claim support cơ chế/novelty.
- K5 chọn cả danh sách M19–M22 và luật κ≥2, q90/q90, h8, η∈{.5,.75}, target∈{.3,.7}.
  Main4/held-out2 R03,R04 (κ2 chỉη.5); optionalP2/P3rules chưaadopt; P6không OOS.
- Bộ chấm interval/Kleene tách K/Q/AND, biên mở/đóng, Cref0excluded, missing precision/dt
  →unknown. Sửa công thức signed numerator: [-2,-1]/[1,2]=[-2,-1/2], không phải [-1,-1].
  Dùng e_num thực, không thay bằng budget. Không đổi D23/D24.
- Engine thêm E|e_M| và cận sai số; sanity14 GMgivenS1≤E|e_M|. Guard trỏ đúng card path,
  từ chối committedDRAFT, kiểm cleanHEAD/cardSHA/receipt commit riêng/tag annotated/dependencies.
- Sáu kiểm là **AI self-check cùng phiên**: prior chỉ đối chiếu scope DL-043, joint witness
  chỉ consistency đại số, không chứng nhận feasibility tại tham số grid hoặc reviewer độc lập.

## B. Commands và kết quả thực chạy

```bash
.venv/bin/python -m pytest tests/test_card_grading.py tests/test_card_membership.py tests/test_card_provenance.py tests/test_card_toys.py tests/test_card_batch.py tests/test_engine_guard.py -q --junitxml=results/lessons/l3_3/card_pytest.xml > results/lessons/l3_3/card_pytest.log 2>&1
.venv/bin/python -m experiments.A00_engine.run_mutants --out results/lessons/l3_3/mutants > results/lessons/l3_3/mutation_run.log 2>&1
.venv/bin/python -m pytest -q --junitxml=results/lessons/l3_3/full_pytest.xml > results/lessons/l3_3/full_pytest.log 2>&1
.venv/bin/python -m experiments.A03_card.verify_card --stage prepare > results/lessons/l3_3/verification.log 2>&1
```

- Card+guard: **29 PASS**, 9.162s (5 guard tests cũ,24 mới).
- Toàn repo: **324 PASS**, 66.547s; baseline **300 PASS** tại830227f.
  Lượt cuối failures/errors/skips=0. Lượt đầu subset:25PASS/1FAIL do thiếu
  thư mục A05 ở isolatedrepo sau đổi CARDpath; đã sửa fixture, không sửa ngưỡng để làmPASS.
- **11/11 mutant KILLED**, logs mới lưu riêng L3.3, không ghi đè L3.2.
- Structural/witness checks PASS với giới hạn ghi ở [six_checks.json](six_checks.json).
  Không chạy/tìm paper mới; không re-audit primary literature hoặc đổi nhãn Phase2.

## C. Số đo

Seed4000 ledger=20261031; phép tính Fraction, không Monte Carlo outcomes/CI.

| Kiểm | Kết quả |
|---|---:|
| Ledger kiểm GMgivenS1≤E abs(e_M) | 4.000 |
| Vi phạm cận | **0** |
| E|e_M| sort/cut khác enumeration độc lập | **0** |
| Minimum bound slack | **0** |
| Coordinate rows whitelist (main+held-out) | **50** |
| K5 main / held-out | **4 / 2** |
| Forecast cơ chế / grid outcomes mới / D grid mới | **0 / 0 / 0** |

ToyE8 (K=0 ledger offsets): GS=−1/4,Γ=1/4,F=−7/8,V=5/8; p_sw=1, ngoài dải main.
Đây là ví dụ Γ>0 và V>F theo con đường harm/negativeF, không evidence cơ chế grid.
Persistence toyH3,c3,u2,Aconst2.5,B1/6: s3/4,OFF cho Δ=−57/8,Δhat=−37/8,e=5/2.
Mirror AI-conjecture (A bursty/Bconst) cho dấu ngược. Đủ16 rows, s1 cho e0;
e2.5 phẳng giữa s1/2 và3/4; mọi toy action matchoracle. Không ngoại suy thành K5 mechanism.

Membership dùng κ/quantile/η/h/target và labels thiết kế đã khóa, **không actual p_sw hoặc
lambdaA held-out**. Poison-feature test giữ membership. Full regression vẫn có D-only
và screenM31 cũ: không nhận toàn phiên là “không dựng D grid”. Phần L3.3 mới không gọi gridD/J.
Không có metric regret baseline/new-method trên grid để báo; A01/A04/A05 chưa chạy.

## D. File và provenance

- [Card](../../../notes/phases/PHASE_3_prediction_card.md), [receipt](../../../notes/phases/PHASE_3_prediction_card.lock.json).
- Card commit1 (chỉ một file): `b05ed70bd4e93544bccefc975cdc452ad40d1380`.
- SHA-256 nội dung: `14021a83c6d45a3fbeba6b7cbe27e9c8c0e572734557af1598cf79b819f34639`.
- Quy trình: commit tiếp theo chứa receipt/exposure; tag `a03-card-v1` trên commit receipt;
  post-registration audit và trạng thái remote được bổ sung sau khi thao tác thực sự xong.
- [Config/source hashes](config.json), [expected trước code](expected_before_code.json),
  [verification](verification.json), [ledger bound](ledger_bound.json), [membershipCSV](membership.csv),
  [membershipsJSON](memberships.json), [persistenceCSV](persistence_toys.csv),
  [E8JSON](E8_ledger_toy.json), [gradingexamples](grading_examples.csv),
  [synthetic witnesses](witnesses_not_grid.json), [developmentchecks](development_checks.json).
- Logs/XML: [card](card_pytest.log), [full](full_pytest.log), [mutation](mutation_run.log),
  [mutant summary](mutants/summary.json), [prepare](verification.log), [cardXML](card_pytest.xml), [fullXML](full_pytest.xml).
- Source: [A03 modules](../../../experiments/A03_card/), [enginecore](../../../experiments/A00_engine/factorial_core.py),
  [precision](../../../experiments/A00_engine/precision.py), [guard](../../../experiments/A00_engine/guard.py),
  [mutationrunner](../../../experiments/A00_engine/run_mutants.py).
- Docs: [DL-047–049](../../../notes/02_decision_log.md), [exposure](../../../notes/00_exposure_register.md),
  [queue](../../../notes/lessons/L3.3_equivalence_queue.md), [Phase3](../../../notes/phases/PHASE_3.md),
  [index](../../../notes/03_experiment_index.md), [T05](../../../notes/theory/T05_exact_engine.md),
  [README](../../../README.md), [AGENTS](../../../AGENTS.md).
- Tests: tests/test_card_*.py, tests/card_git_fixture.py, tests/test_engine_guard.py.
Không tạo plot/PDF, A01/A04/A05 output hoặc record người đọc độc lập.

## E. Kết luận

Technical verification PASS; bốn forecast chưa được chấm bằng outcomes, không gọi chúng
đứng hoặc xác nhận hypothesis. Read-back là tác giả tự xác nhận, không transcript/proof độc lập;
AI self-review không thay P0-V10/L8. Không chuyển phần AI hỗ trợ thành author-written mechanism.
T05 chưa có văn bản mới của tác giả trong repo; engine vẫn experiments. V9 chưa gửi/A04chờ;
Phase4 HOLD. Bước học tiếp là L3.4, nhưng phiên này không chạy A01.
