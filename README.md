# State × Model — giá trị cải thiện quyết định routing

Người phụ trách: **Doan Van Tai**.

Main RQ:
> For load-changing routing actions, how do improvements in current-state information and action-response model fidelity differ and interact in their effect on expected decision regret?

## Trạng thái hiện hành — 02/11/2026

Phase 5 đã đóng sau bước đọc kết quả L5.3 và discovery Phase 4, theo
[quyết định numbering v1.2](notes/phases/PHASE_4_entry_decision.md).
Hai exploration `mechanism-regime-v2` và `p4-regions` đã được gộp;
chúng vẫn là exploration, không phải confirmation hoặc author-self work.

V1 chính thức **INCONCLUSIVE**; v1.1 **PASS 10/0/0** sau một lần sửa thiết kế có khai báo, chỉ giữ
claim numerical finite-panel ở h/κ 320/640, có exposure một phần.
H-L2 PASS exploratory, nhưng Spearman chịu cấu trúc cụm và MedAE phụ thuộc
thành phần panel; cả hai thay đổi acceptance đều cần để H-L1 PASS, nên đây
là lượng hóa phù hợp một giới hạn được kỳ vọng, chưa phải contribution/novelty.
**Gate C = NARROW, G1 giữ nguyên (DL-128)**; bàn giao Phase 6 theo ủy quyền,
realism/D22/Understanding còn mở;
chưa chạy Phase 6, không retry/resume/refine/v1.2 hoặc confirmation độc lập.

[Closeout L5.3: evidence, sensitivity, prior và claim](notes/phases/PHASE_5_closeout.md) ·
[DL-128](notes/02_decision_log.md#dl-128--phase-5-gate-c-narrow-02112026) ·
[Summary v1](results/phase5/summary.json) · [Summary v1.1](results/phase5_v1_1/summary.json) ·
[Amendment](notes/design/phase5_v1_1_amendment.md) ·
[Runner v1.1](experiments/P5_v11/run.py) · [Tests](tests/test_p5_v11.py).

**Đính chính exposure:** nhánh p4-regions đã tính 77 regime có h/κ>160
trước commit freeze L4.9, trong đó W0347 trùng P5_08 ở mức (160,2).
Ở dòng này S=G_S|M1/Cref=0,0%, M=G_M|S1/Cref=16,21328185%.
16,2% là model value, không phải state value hoặc một FAIL của H-L1.
Panel không còn được gọi là 12 tọa độ hoàn toàn chưa từng tính; chưa có
bằng chứng người chọn panel đã nhìn dòng này. Không sửa lịch sử frozen.
H-L1 giữ bài chấm gốc nhưng được đọc như validation có exposure một phần;
không dùng nó một mình để claim confirmation độc lập.
[Exposure và quyết định](notes/02_decision_log.md#dl-122--dọn-repo-hợp-nhất-exploration-và-đính-chính-exposure-02112026).

## Điểm vào

- [Contract v1.3](notes/01_definitions_v1_3.md), [amendment](notes/design/contract_v1_3_amend1.md), [claim boundary](notes/01_claim_boundary_v1_3.md).
- [Phase 4 v2](notes/phases/PHASE_4_v2.md): bản triển khai tối thiểu, không phải full master plan.
- [Freeze L4.9](notes/design/analysis_plan_v1.md), [lock](notes/design/analysis_plan_v1.lock.json), [report lịch sử](results/lessons/l4_9_v2/report.md).
- [Mechanism exploration](results/explore_mech/SUMMARY.md), [scorecard](results/explore_mech/checks.json), [xstar scorecard](results/explore_mech/checks_xstar.json).
- [Practical regions](results/explore_p4/SUMMARY.md), [raw W0347](results/explore_p4/wide/level_160_2/W0347.json).
- [Decomposition](results/lessons/l4_6_v2/report.md), [T08 clipping](notes/theory/T08_clipping_anchor.md), [T09 limits](notes/theory/T09_stationary_dominance_limits.md).
- [Baseline A3](results/lessons/p4_a3/report.md), [SV FAIL_SCREEN và SUB checkpoint](results/lessons/l4_5/part_b/report.md).
- [Paper library](papers/README.md); mọi lần tìm paper theo [search protocol](notes/literature/search_protocol.md).

SUB/CF-v2 vẫn park, R09/R10 vẫn sealed, D22 native DEFERRED;
G1, realism, L8 và Understanding không tự nâng. Cấu trúc dấu theo x vẫn
exploratory; moment dừng chính xác không tự làm ranh giới x* chính xác.
X1 chỉ có 10/15 crossing quan sát được ở κ=.1; 5 chuỗi còn lại là kiểm phía,
không phải 5 sai số điểm. Biên độ 4/5/6/7 đã có thiết kế/kết quả trong lịch sử;
không mặc định a≠6 là held-out sạch.

## Cấu trúc và kiểm tra

`src/`: thư viện; `experiments/`: Phase 4, exploration và dependency native/guards;
`tests/`: tests còn áp dụng; `notes/`: định nghĩa, theory, freeze và provenance;
`results/`: evidence hiện dùng, CSV/summary/plots và raw native cần replay.
Không tạo thêm file lesson/report cho lượt dọn này; lesson và lộ trình in trong chat.

```bash
.venv/bin/python -m pytest -q -p no:cacheprovider
.venv/bin/python -m experiments.P4_01_recount.verify_artifacts
```

Các audits/runner cũ đã archive không còn được coi là entrypoint hiện hành.
Dữ liệu native 597 nguồn và các mức refinement Phase 4 được giữ để replay;
JSON từng regime của exploration và lesson cũ được lấy lại từ tag khi cần.

## Archive và khôi phục

Lịch sử Git được giữ nguyên. Mốc trước dọn: `archive/main-before-cleanup-2026-11-02`.
Raw exploration: `archive/mechanism-before-cleanup-2026-11-02` và
`archive/p4-regions-before-cleanup-2026-11-02`; còn tag regime-map/population.
Ví dụ đọc một artifact cũ mà không khôi phục cây:

```bash
git show archive/main-before-cleanup-2026-11-02:notes/03_experiment_index.md
git show archive/mechanism-before-cleanup-2026-11-02:results/explore_mech/xstar/level_160_2/S0000.json
```

Cache bị ignore và worktrees được chuyển ra `/home/vantai/state-model-regret-archive/2026-11-02/`;
symlink cache giữ nguyên đường dẫn replay ở máy này. Cache không phải dữ liệu
đã commit; clone mới cần rebuild hoặc cung cấp lại cache. Liên kết lịch sử
trong các tài liệu frozen có thể trỏ tới artifact đã archive: dùng tag tương ứng.


Kiểm trực tiếp bundle Claude6ffe8e84:541testsPASS,16freezehash/3run guards/597
native sources khớp. Bản hiện hành giữ thêm5modules regression còn áp dụng;
587tests đã PASS. Raw exploration đã archive: analyzer từ chối raw thiếu/partial
trước khi ghi CSV/score; replay score từ savedCSV đã khớp cả dự đoán trượt.
Bundle đã import vào branch `archive/claude-cleanup-2026-11-02` và chuyển ngoài repo;
bundle chỉ chứa branch ref, không chứa5tags được kể trong lời trả lời.
