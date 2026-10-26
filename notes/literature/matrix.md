# Matrix — prior đã đọc tới đâu

Người phụ trách: **Doan Van Tai** · 24/10/2026 · mọi effect là AI đề xuất.

| ID | Quyết định/uncertainty | Estimand | Evidence đọc | Quan hệ với dự án / giới hạn |
|---|---|---|---|---|
| SOB14 | Health decision, uncertain inputs | Partial EVPI theo joint belief | T Method Eq1–4, pp312–313; AI-only | Cùng functional với GSgivenM1 dưới G1–G4; không cần copy regression method |
| B82 | Stochastic LP, fixed recourse | VSS và bounds | A publisher abstract; full PDF403 | Conditional VSS definition useful; theorem transfer HOLD |
| MAB11 | Multistage linear stochastic program | Chất lượng approximations, value of information | A repository abstract; §2 chưa đủ | Không citation theorem như đã đọc; proof ordering của dự án ở T03 |
| E07 | Multistage stochastic program | EVPI/VSS và bounds | A publisher abstract | Chỉ bối cảnh; dự án chọn action một lần |
| P11 | Unknown structural discrepancy + inputs | EVPI(delta), EVPI(X), diễn giải EVMI | T §§2–6, AI-only | Concept so input/model value đã có; D21 là approximation-use intervention |
| SOC12 | Model discrepancy tại subfunctions | Variance-based sensitivity/refinement theo abstract | S abstract | Tiền thân P11; chưa đánh giá full case study |
| P12/P13 | Chưa xử lý trong Part A | Chưa kiểm | Pending L2.4/L2.5 | Không cấp evidence từ placeholder |

DOI/URL, phiên bản, ngày, Fact/Claim/Evidence/Inference xem các note trong papers/;
metadata đã kiểm nằm ở results/lessons/part_a/source_metadata.json.
Khác estimand/mechanism/regime là việc cần đối chiếu, không tự là novelty.

## L2.4 Part2–3 — cập nhật25/10/2026

[Bảng đối chiếu NDT/networking](ndt_landscape.md#bảng-bản-đồ-nguồn--chỉ-kết-luận-trong-phạm-vi-đã-đọc)
chứa NDT1/NMRG/P05/P10/P08/S07, input/action/metric, vị trí và mức đọc.
NDT1/P05/P10/P08/NMRG có targeted AI reading; S07 abstract-only.
P05 full text qua web, PDF local403 và hình/table chưa kiểm trực tiếp.
Không dùng bảng này tự đổi nhãn PC2/PC5 hay nâng G-level.

## L2.5 Part1 — 26/10/2026

[P04 / crosswalk](state_staleness.md) thêm prior trực tiếp cho PC2/PC3/PC4/PC6.
Metric: connection blocking/overhead; nhiều connection; cost-level heuristic
không tự là repair D20/D21. §V-A/Fig8 là dependence định tính; không tính Γ.
Mức đọc AI-T, nhìn Fig1/Fig8 và công thức; tác giả chưa xác nhận L-self.
Không đổi nhãn PC hoặc estimand của repo.

## L2.5 Part2 — 26/10/2026

| ID | Estimand / mechanism / regime | Phạm vi và vai trò |
|---|---|---|
| M00 | Equilibrium sojourn, repeated dispatch dùng stale board, many-server queues | AI-T abstract/§2/§3.1/§3.4/selected§4–5/§7, submission28trang; [note](papers/M00.md) |
| P01 | Cumulative queue regret so OWR genie biết rates; parameter learning; partial/delayed queues ở Fig2 | AI-T Def1–2/§2.2–2.5/Fig2 PDF3–4; [screen rồi skip full read](papers/P01.md), không thêm hàng bắt buộc |
| R04 | Control re-solving / certainty-equivalent approximation | Chỉ kiểm provenance archived AI-T note; primary mapping chờ A4, không mới đọc lại |

[K-S1…8 và draft khác biệt](prior_boundary.md#trục-state--l25-part2-26102026),
[mechanism/toy và đính chính lesson](information_harm.md). Không đổi nhãn PC/Gate.

## L2.6 Part A — 26/10/2026

| Nguồn | Estimand / mechanism / regime | Evidence thực đọc / giới hạn |
|---|---|---|
| S11 | Long-run average cost, sampling/action feedback, known-kernel controlled finite MDP | AI-T v3 §§I–III/PDF1–7, §VII-C–D/PDF17; [note](papers/S11.md). Journal TIT2026 đã xác minh; VoR full text chưa đối chiếu |
| Kaul2012 | Time-average AoI / FCFS generation-rate tradeoff | AI-A abstract IEEE/kho Rutgers; không proof hoặc full PDF |
| AoII2020 | Time dissatisfaction × error penalty, remote estimation | AI-T arxiv1907.06604v2 §II/Eq3–9; không đọc optimization proofs |
| AY19 | Link-specific uncertainty reduction, quadratic state-estimation errors, NCS scheduling | AI-T arxiv1903.05356v1 §2.2 assumptions1,4 / §2.4 Eq13–19; không phải Shannon bit |
| R32 | Rate–regulation tradeoff, value-function variation | Lượt này AI-A arxiv1812.07534v2 abstract + metadata; giữ record T cũ, không tái tuyên bố full read |

[K3 và các đính chính](freshness_decision_value.md), [H1 queue](h1_candidates.md).
“Cột M1” chỉ là analogy về known-law, không đồng nhất objective hoặc policy set.
Chỉ S11 thêm Excel hiện dùng; bốn nguồn còn lại tra bổ sung, không tạo reading list mới.

## L2.6 Part B — 26/10/2026

| Nguồn | Estimand / mechanism / regime | Đã đọc / phạm vi transfer |
|---|---|---|
| P13 | Average workload+capacity cost; stationary→transient approximation; one Lévy queue/continuous capacity | AI-T CWI journal36trang: Eq2.4/2.7, Theorem1, Prop4–5, §5–selected§6; [note](papers/P13.md). Không cùng D21/model input hoặc binary regret |

[K-F1…3/K-H1…4](prior_boundary.md#l26-part-b--horizon-và-transient-26102026),
[fluid/gap/finite-support examples](horizon_transient.md),
[boundary T-H1](../01_claim_boundary_v1_2.md#t-h1--giới-hạn-diễn-giải-do-horizon-hữu-hạn-26102026).
Chỉ P13 thêm bảng;9notes/progress cũ giữ nguyên. Các record PartA/PartB là
technical evidence, không đủ quyết định novelty/Gate hoặc đổi nhãn PC.

## L2.7 Part A — 26/10/2026

| Nguồn | Estimand / mechanism / regime | Evidence thực đọc và giới hạn |
|---|---|---|
| P03=R51 | Expected policy-value regret trong finite candidate set; learned twin/ranking loss; offline MDP | AI-T PMLR27trang: §2–3/6.1–6.2/7.1, A.1–2/B.3–4.3 chọn lọc; [note](papers/P03.md). MC500rollouts/policy, không hindsight; không D21 intervention |
| P07 DOTE | Expected MLU/direct TE learning; repeated split ratios; evaluation ratio so future-demand oracle | AI-T USENIX §2.2–3.3/4.1–4.2; [note](papers/P07.md). Theory idealized, không guarantee DNN thực; không so số với D18 |
| P02 | Sensitivity theo prediction errors/horizon/update frequency trong signal MPC | **AI-A official abstract**, full text BLOCKED; [note](papers/P02.md). Chưa xác nhận joint biases, recorded-future comparator hoặc dấu Γ |

[Đính chính và bài tập](model_fidelity_methods.md), [K-M1…5](prior_boundary.md#l27-part-a--trục-model-26102026),
[MT1…8/HOLD](../phases/PHASE_4_methodology_threats.md). Excel thêm2hàng P07/P02,
P03 dùng chung R51; giữ10author progress. Part A còn primary P02, Part B chưa làm.

## L2.7 Part B —26/10/2026

| Nguồn | Estimand / mechanism / regime | Evidence thực đọc / giới hạn |
|---|---|---|
| P12 | Equal Bellman updates trên Π,V/state space; restricted model learning/value-based planning | AI-T NeurIPS2020 PDF2–3/đầu4: Eq2,Def1–2,Properties1–4; [note](papers/P12.md). Không full proof/experiments, không trực tiếp normalized selected-policy regret |
| R43 | Approximate VE/error tolerances và performance bounds | **Lượt này AI-A** official NeurIPS2022 abstract; archived AI-T24/10 selected definitions/proposition có provenance, chưa primary tái kiểm; [note](papers/R43.md) |

[Terms/OεRE](terms.md), [bài tập](model_equivalence.md),
[PC5/K-M6–7](prior_boundary.md#l27-part-b--oεre-và-pc5-26102026).
Chỉ P12 thêm Excel12→13, giữ12notes/progress cũ; R43 tra bổ sung ngoài bảng.
Không tự gán PC5 đúng, chọn K5 hoặc nhận formal Gate. P02 full text còn mở.
