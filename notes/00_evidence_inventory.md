# Evidence inventory — L0.1 Part 3

Type, Conditions, Tác giả giải thích được, Claim có phạm vi và Vai trò dùng judgment do tác giả xác nhận ngày 07/10/2026; wording factual được sửa theo nguồn immutable. Đối chiếu bằng máy/log được ghi riêng khỏi hiểu bài. Không biến kiểm nguồn thành kiểm vấn đáp độc lập.

**Giới hạn numbering:** bản PHASE_0 chứa bảng EV-01…EV-12 gốc chưa được cung cấp/tìm thấy theo đúng tài liệu. EV-01/05/06/08/10 giữ các mốc được hướng dẫn nhắc; những số còn lại 02–12 là mapping làm việc có nguồn, không giả đã khôi phục nguyên bảng PHASE_0. EV-13…EV-19 theo đúng danh sách bổ sung tác giả gửi. Việc thiếu mapping không được dùng để bịa source.

## Inventory

| EV | Item | Type | Conditions | Tác giả giải thích lại được? | Claim có phạm vi | Vai trò với Main RQ | Source | Đối chiếu nguồn/log |
|---|---|---|---|---|---|---|---|---|
| EV-01 | Γ=+2/−2 không cần queue | E0 analytical/logical | Binary argmin, cost 20/18, additive errors theo ví dụ review | Có — tác giả xác nhận cách bác mệnh đề mạnh | Γ≠0 tự nó không đủ suy ra network mechanism. | Evidence logic trực tiếp; không là network empirical evidence. | Review §2.3; kết quả counterexamples trong verification_results.json | Tính lại +2/−2; source full chỉ có digest và reading note. |
| EV-02 | F6 negative result và SESOI | E2 tổng hợp old-world simulations | Controlled flow nhỏ, OU-Poisson, M/D/1/K, oracle cùng information; chỉ ô hợp lệ | Conceptual: Có; exact statistical details: Một phần | Ở phạm vi F6, static tune gần same-information oracle theo m=8,1/r=10% và luật CI; đây là đề xuất DP0, chưa GVHD duyệt. | Historical evidence + motivation. | S01/S20/S21 | Đọc F6/CI rule; không tái lập mọi experiment của F6. |
| EV-03 | F7 information share | E2 scoped simulation; F7 có prereg riêng | AA/BB/AB, 4 Mb/s, K=100, α=1%, A0; 90 test seeds 11011–11100 | Conceptual: Có; exact CI: Một phần | Information=headroom−K2(∞); mean share AA 59,4753%, BB 84,4773%, AB 63,5151%; không là % lỗi state. | Historical evidence + motivation. | S02/S03/S04 | Tính lại per-seed, decomposition residual <1e-10 ms. |
| EV-04 | F7 pure-width gain | E2 scoped simulation; không xác nhận RQ mới | Cùng scope EV-03; pure=K2−SCdir; ratio of means | Conceptual: Có; exact CI: Một phần | Pure gain AA 0,062764±0,022628, BB 0,005969±0,018748, AB 0,091141±0,027573 ms; AB 1,5117% là mean, không bound ≤1,5%. | Historical evidence + motivation. | S02/S03/S04 | Tính lại CI95 t ghép theo seed, gate SESOI giữ nguyên. |
| EV-05 | Final Review: Main RQ, G1 và verdict | Judgment / research formulation | Snapshot cập nhật 06/10/2026, search scope trong review | Có — tác giả xác nhận | Review giữ candidate G1, conditional analytical pre-spike, full study HOLD; không chứng minh novelty. | Judgment định hướng. | Review §1/§6/§20/§22.2 | Đọc snapshot, kiểm digest; public reading note, full source chưa public. |
| EV-06 | Literature map P01–P13 | L-2nd; không tự nâng L-self | Current review/search scope; chưa record tự đọc primary papers | Conceptual: Có; primary details: Một phần | Review ghi prediction/decision fidelity khác nhau (P03/P07), stale state ảnh hưởng routing (P04), cùng các prior model/control/queue. | Background + gap threat; không support absence toàn field. | Review §3/§4/§21 | Đã mở các sections review; chưa tự đối chiếu primary papers trong task này. |
| EV-07 | F8 history-twin và gate lỗi | Old-world simulation; confirmatory estimands không diễn giải ở ô lỗi | T10/FH dùng oracle bin; P2/T10, quỹ đạo riêng và hậu kiểm f08b cần phân biệt | Một phần — exact statistical interpretation | F8 không có kết luận xác nhận khi estimands dùng oracle T10/FH hỏng; các quan sát f08b giữ nhãn khám phá. | Historical evidence/background + motivation. | S05 | Đọc toàn F8 §1–4, tách valid non-oracle result khỏi oracle gate. |
| EV-08 | GO-check freshness so với đổi luật | E2 exploratory/post-hoc | R1 old world, 94/95 seeds đã xem; α=0,2%, cooldown=0 | Có | SC SYM giảm delay so SC FIX trong cấu hình cụ thể; không suy State repair dominates ở finite load. | Motivation. | S06/S07/S21 | Đọc source và CSV posthoc, exact contrast tại EV-15. |
| EV-09 | Seed registry và status đã xem | Documentary/exposure record | Snapshot 01/10, không chứng minh exposure ở máy khác | Có | Dải 20001–20020 đã xem; nhãn “để dành” trong snapshot không tự bảo đảm unseen hôm nay. | Methodological background + exposure. | S08/S01 | Đối chiếu registry với F6 và n02 metadata. |
| EV-10 | AoI order of magnitude trên testbed | Reported E5 source; raw revalidation chưa hoàn tất | dt4n Phase 23, AoI cuối cửa sổ tới GET, CLEAN/PROD | Có về scope; measurement exact chưa kiểm lại | F1 báo CLEAN mean 0,369 s, PROD mean 0,343 s; “khoảng 0,36 s” chỉ mô tả bậc, không là một mean chung đã tái đo. | Background/real-measurement report có giới hạn. | S11; raw_backup_manifest.json | Đọc summary/construct; không tái tính raw, không đại diện production. |
| EV-11 | GO-check CHƯA GO theo TC1–TC3 | E2 + gate judgment scoped | Old-world VoIP, rollout delay, harm budget; oracle nhìn trước chỉ thang headroom | Có | Bản ghi ngày 01/10 chưa GO; TC2 chưa đủ nguồn, TC3 dưới magnitude floor; DP0 chờ quyết. | Historical evidence + motivation. | S06/S21 | Đọc gate report và protocol, không tự phê duyệt NARROW/PIVOT. |
| EV-12 | Ý tưởng tái sử dụng repo cho sandbox | Idea / research provenance | README §9 tại snapshot 02/10; chưa phải sandbox evaluation hoàn chỉnh | Có | Repo cũ liệt kê finite-load feedback là phần còn thiếu; có thành phần để tham khảo, chưa đủ benchmark Main RQ. | Provenance + background. | S12 | Đọc README §9; không coi ý tưởng là empirical evidence. |
| EV-13 | N2 + n02/n02b factorial pilot | E2 exploratory + Idea/Provenance | PSA POS_probeB, G_all, H=0,5, 10 seeds 9101–9110; no finite-action feedback | Có | Pilot tổ chức sources thành information/model families; bảng có ý tưởng bỏ qua action feedback, nhưng script S/M/P thao tác staleness/measurement/parameter. | Provenance + motivation; không direct evidence. | S13/S16–S19 | Đọc N2/script/run JSON/CSV; xác nhận seeds, scope, missing Δρ; không rerun pilot. |
| EV-14 | N0 question card và N1 verdict concepts | Idea / research provenance | Documents ngày 02/10, sandbox proposal; n01c so chế độ tải không là branching tại cùng state | Có | N0/N1 là tiền thân của hướng hiện tại; N1 có thử CRN/load regime nhưng chưa thiết kế/chấm đúng Main RQ. | Provenance. | S14/S15 | Đọc toàn N0/N1, kiểm ngày commit và giới hạn n01c; không suy nguồn gốc duy nhất của RQ. |
| EV-15 | GO-check exact 2,9855978966 ms | E2 exploratory/post-hoc | R1 94/95, α=0,002, cooldown=0, SC FIX−SC SYM | Có | SC SYM giảm mean delay 2,985598 ms, CI95 [2,495705;3,475490] theo contrast hậu kiểm, làm tròn 2,986. | Motivation; không là finite-load State repair experiment. | S06/S07 | CSV row đúng alpha/cooldown/contrast; metadata và số exact có trong verification_results.json. |
| EV-16 | Ba threshold khác construct | Documentary/methodological clarification | EPS GO-check=1,0 ms; F7 ε=0,5S=1,512 ms tại 4 Mb/s; F6 m/r | Có | Hai ε là event harm thresholds trong hai thiết kế; m=8,1/r=10% là practical magnitude gate. Không có mâu thuẫn chỉ vì khác số. | Methodological clarification. | S10/S02/S01/S11 | Đọc code constant, F7 §2.2/2.3 và F6/CI source. |
| EV-17 | F6 ↔ F8 bound 6,84 và gate T10/FH | Scoped non-oracle bound + oracle validity limitation | T10, quỹ đạo S0_FH, upper clairvoyant gain so baseline; same old world | Một phần — exact statistical interpretation | Bound không cần oracle bin 6,84±0,15 ms vẫn dưới m=8,1; không cứu estimands xác nhận dùng oracle T10/FH lỗi. | Historical evidence/background; không generalize. | S01/S05 | Đọc F6 §1 và F8 §3; phân biệt rõ hai phát biểu, không coi chúng mâu thuẫn. |
| EV-18 | Final Review không có byline rõ | Provenance/source limitation | Full snapshot đúng digest đã đối chiếu | Có | Snapshot hiện không ghi rõ byline/author identity; chưa đủ dữ kiện xác nhận người viết, không bác nội dung chỉ vì thiếu byline. | Provenance limitation. | Review digest / reading note / source_checks.json | Mở snapshot; kiểm đầu file và byline; không suy chắc người viết. |
| EV-19 | Raw AoI backup 30 JSONL | Potential E5 source, incomplete verification | Local tar metadata, 30 aoi_*.jsonl; raw không public, chưa tái tính mean | Có | Có raw backup với metadata/hash; chưa chứng minh là bộ khoảng 427 MiB được nhắc hoặc xác nhận lại 0,36 s. | Source recovery / unresolved. | raw_backup_manifest.json; bundle_manifest.json | Đối chiếu manifest thật; raw AoI 71.674.153 byte; tổng file tar 444.748.020 byte, hai lượng khác nhau. |

Log máy đọc: [source_checks.json](verification/source_checks.json). Kết quả tính lại: [verification_results.json](verification/verification_results.json). Script và cách chạy: [verification README](verification/README.md).
E0 là logic, E2 là scoped simulation/exploration; F7 có tiền đăng ký riêng nhưng không vì vậy thành E3 cho RQ finite-load mới. L-2nd là literature thứ cấp; chưa có record L-self cho primary papers. E5 của AoI vẫn có điều kiện xác minh raw.

## Bảng nguồn immutable

Mỗi Sxx đã mở toàn file từ tag; full hash/digest ở log. Nội dung lời GVHD không được copy nguyên văn vào repo mới; các file này chỉ ghi trạng thái/phạm vi đã được summary.

| ID | Source mở trên GitHub tại commit cố định | SHA-256 nội dung |
|---|---|---|
| S01 | [`archive-switch-or-stay-2026-10-02:notes/feasibility/F6_DP0_DP1.md`](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/notes/feasibility/F6_DP0_DP1.md) | `b20985665e728c8b67087ab0daf24a2fe63a1bc9b5e8390f31e02154d3a2b65b` |
| S02 | [`archive-switch-or-stay-2026-10-02:notes/feasibility/F7_asym_freshness.md`](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/notes/feasibility/F7_asym_freshness.md) | `fa5bc3fe0d36b07bd4cdd446610c4f4abf40474d680395749d94d861d1d1da87` |
| S03 | [`archive-switch-or-stay-2026-10-02:experiments/results/f07/f07_outcome.json`](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/experiments/results/f07/f07_outcome.json) | `606bba9052e980278865dfd2622c746c1c2c52e47b84cd677dea1a5f466bbc99` |
| S04 | [`archive-switch-or-stay-2026-10-02:experiments/results/f07_outcome_output.txt`](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/experiments/results/f07_outcome_output.txt) | `30e6908e1bdbb6e4094f3f63033c51f5a81e7386b83974a69a1ad4d53b7ed102` |
| S05 | [`archive-switch-or-stay-2026-10-02:notes/feasibility/F8_history_twin.md`](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/notes/feasibility/F8_history_twin.md) | `f180fcac905399378d28988c69d173b7745a6c62f103562887fdf632d6e88ee1` |
| S06 | [`archive-switch-or-stay-2026-10-02:notes/gocheck/GVHD_status.md`](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/notes/gocheck/GVHD_status.md) | `aad18c69943598530587e759c496331616268a4e15eb7cc4ab3a56b818e37436` |
| S07 | [`archive-switch-or-stay-2026-10-02:results/gocheck/reproduction_contrasts.csv`](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/results/gocheck/reproduction_contrasts.csv) | `81281961a1ae2e1425ada091314e89f86c58491959e6897c7dc5a16a5fa18580` |
| S08 | [`archive-switch-or-stay-2026-10-02:notes/seed_registry.md`](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/notes/seed_registry.md) | `21a7337625abafb77a390752606f44915fa2dc57dbe4cf0236f69caa61ea9c12` |
| S09 | [`archive-switch-or-stay-2026-10-02:notes/gocheck/PREDICTIONS_claude.md`](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/notes/gocheck/PREDICTIONS_claude.md) | `7c47e5c5e1ab3a464834e5b7180260fe81073eea303ba9e6dcb0f82d4221d944` |
| S10 | [`archive-switch-or-stay-2026-10-02:experiments/gocheck/rollout.py`](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/experiments/gocheck/rollout.py) | `6d134d66431042f86b7128c715d54329b0302bac1b9f3c549264f1f9f13776b9` |
| S11 | [`archive-switch-or-stay-2026-10-02:notes/feasibility/F1_operating_point.md`](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/notes/feasibility/F1_operating_point.md) | `323965721a30c48af1491ec074fdd2244ee2c71712656cba3c57652b11df5aee` |
| S12 | [`archive-switch-or-stay-2026-10-02:README.md`](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/README.md) | `f57224ddd87d24936bf116eb7dbabc99be2a732ee0677208c1367bace8810215` |
| S13 | [`archive-switch-or-stay-2026-10-02-wip-local-2026-10-07:notes/novelty/N2_error_sources.md`](https://github.com/vantai13/dt4n-decision-risk-project/blob/2e7543b2794a85645d60c0a55afb5a670166a099/notes/novelty/N2_error_sources.md) | `7f101ad80812e0dd2eb4b0ae65397b4834551633271c11322c375be051fbb4ff` |
| S14 | [`archive-switch-or-stay-2026-10-02-wip-local-2026-10-07:notes/novelty/N0_question_card.md`](https://github.com/vantai13/dt4n-decision-risk-project/blob/2e7543b2794a85645d60c0a55afb5a670166a099/notes/novelty/N0_question_card.md) | `5e370db3fb09fa6086d275f20fd20a5f679c2b3e3b8b189e08a6726eb2906078` |
| S15 | [`archive-switch-or-stay-2026-10-02-wip-local-2026-10-07:notes/novelty/N1_verdict_concepts.md`](https://github.com/vantai13/dt4n-decision-risk-project/blob/2e7543b2794a85645d60c0a55afb5a670166a099/notes/novelty/N1_verdict_concepts.md) | `e46078720e5e25223e2053a23b1b2ce154236339b52c8493d40a14d82cc23f59` |
| S16 | [`archive-switch-or-stay-2026-10-02-wip-local-2026-10-07:experiments/results/n02_H0.5_rho0.80_run.json`](https://github.com/vantai13/dt4n-decision-risk-project/blob/2e7543b2794a85645d60c0a55afb5a670166a099/experiments/results/n02_H0.5_rho0.80_run.json) | `58bf8163c19632c2b3fe495c438beeb4b088595b58ccf89ac86346f051ef9b29` |
| S17 | [`archive-switch-or-stay-2026-10-02-wip-local-2026-10-07:experiments/results/n02_H0.5_rho0.70_run.json`](https://github.com/vantai13/dt4n-decision-risk-project/blob/2e7543b2794a85645d60c0a55afb5a670166a099/experiments/results/n02_H0.5_rho0.70_run.json) | `9ada30c34f6aee19bb5ca21b67ab98f9bb14b5abb6a4683f061e72e70f7fa8c8` |
| S18 | [`archive-switch-or-stay-2026-10-02-wip-local-2026-10-07:experiments/results/n02b_measurement_split_seeds.csv`](https://github.com/vantai13/dt4n-decision-risk-project/blob/2e7543b2794a85645d60c0a55afb5a670166a099/experiments/results/n02b_measurement_split_seeds.csv) | `28c55b28017d01f746068b85d9af9d7c156313aa68a52e96a4b0b42d2d88ba93` |
| S19 | [`archive-switch-or-stay-2026-10-02-wip-local-2026-10-07:experiments/n02_source_factorial.py`](https://github.com/vantai13/dt4n-decision-risk-project/blob/2e7543b2794a85645d60c0a55afb5a670166a099/experiments/n02_source_factorial.py) | `eaab34d3e7a0a596d0a590f44fbee5e802a3a0989db5239a4dd840e2bbef11c5` |
| S20 | [`archive-switch-or-stay-2026-10-02:notes/03_experiment_log.md`](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/notes/03_experiment_log.md) | `249bd213e3a3c8f4379e62d025a776a408843c37861923b8fd2669026149c0e8` |
| S21 | [`archive-switch-or-stay-2026-10-02:notes/gocheck/GO_check_spec.md`](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/notes/gocheck/GO_check_spec.md) | `f3281971df38349d719ea2d09f038ed96c7f6677298d4a4029e0d45146912d2b` |
| S22 | [`archive-switch-or-stay-2026-10-02:notes/map/rollout_v6_preparation.md`](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/notes/map/rollout_v6_preparation.md) | `6f989ddcd44072042e5237751904dca0f2189685143f92825072f0494b34c744` |

Final Review: [reading note](verification/final_review_reading_note.md), digest full snapshot `fc766e319427ba01da7362de2018cd4da6695dc1fcaa9812ed7badd5c0651fd1`. Note là summary có thể mở công khai; full source vẫn local-only, limitation ở EV-05/06/18. Raw và bundle cũng chỉ public metadata, không giả có download.

## Exposure

[Exposure register](00_exposure_register.md) là phần dữ liệu đã nhìn của inventory. Sổ ghi seed **và** configuration/workload; đối chiếu registry S08 với S16–S18. Không coi RNG phụ hoặc seed mới cùng regime đã chọn sau outcome là đủ confirmation.

## G-level assessment

| Điều kiện lên G2 | Hàng gần nhất / giới hạn | Trạng thái |
|---|---|---|
| (a) Practical effect/equivalence boundary trong load-changing world | EV-13 gần formulation nhất nhưng là pilot PSA thiếu action-induced feedback; EV-14 chưa đúng branching/estimand | NOT MET |
| (b) Prediction trên dữ liệu chưa dùng xây explanation | Không có E3 đúng Main RQ; EV-09/13 và exposure chỉ ghi data đã xem | NOT MET |
| (c) Use case có timescale và intervention cost hợp lý | EV-10 chỉ báo AoI setup cũ; không khóa cost/timing cho repairs finite-load | NOT MET |
| Nhánh mechanism: phân biệt threshold null | EV-01 bác diễn giải Γ quá mạnh, chưa xác nhận network mechanism | NOT MET |

**G1 — candidate gap.** Có câu hỏi, logical evidence, historical motivation và prior threats; chưa có đủ đúng-world evidence, unseen confirmation hay practical timescale. Archive/provenance mạnh hơn không nâng scientific effect evidence lên G2. Đọc thêm literature có thể giữ/hạ/loại candidate, không tự tạo G2.

## Sai lệch so với hướng dẫn/plan

1. “≤1,5%” chỉ là làm tròn: AB mean=1,5117164712%, không bound hoặc UCB.
2. “1 ms đối lập 8,1 ms” trộn construct: GO-check harm event=1 ms; F7 harm event=1,512 ms; F6 practical gate=8,1 ms và 10% headroom.
3. F6 ngày 30/09 ghi dải 20000–29999 chưa dùng, registry ngày 01/10 ghi 20001–20020 đã dùng/đã xem. Dùng nguồn mới hơn.
4. Chỉ kiểm remote ancestors bỏ sót local N0–N2; tag phụ đã giữ ba commit ngày 02/10.
5. Registry chưa có dòng explicit cho n02/n02b 9101–9110 và configuration. Các số này **đã nằm trong dải bao 9001–10000**, nên diễn đạt “không hề có trong registry” là quá mạnh.
6. S/M của script n02 là staleness/measurement, không State/Model; P mới thao tác prior parameter. Bản đồ N2 có hai family, không có nghĩa experiment đã là factorial hai repairs của Main RQ.
7. N1 có n01c 300 cặp DES với thêm tải từ cả warm-up; nguồn tự nói chưa branch từ cùng workload tại t và chưa đo trực tiếp nhóm chuyển. Không dùng nó xác nhận đúng-world repair effects.
8. AoI “0,36 s” là order of magnitude; F1 tách CLEAN 0,369/PROD 0,343 s. Chưa tái tính raw. 30 JSONL không tự chứng minh khớp dataset khoảng 427 MiB.
9. Bảng PHASE_0 EV-01…EV-12 và full review public source còn thiếu như ghi đầu file; không đánh dấu đã đọc primary papers hoặc đã kiểm nguồn trên mọi máy.

Chuyển các discrepancy này vào changelog master plan khi đóng Phase 0; không sửa master plan không có trong phạm vi phiên này.

## Chưa kiểm được

Primary literature; byline review; full raw identity và AoI recomputation; sandbox/máy khác; original EV numbering; read-back/vấn đáp của người thật. Các giới hạn không bị xóa khi tác giả đã phê duyệt understanding. Không bắt đầu L0.2.
