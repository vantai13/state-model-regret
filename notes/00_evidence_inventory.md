# Evidence inventory — L0.1 Part 3; bổ sung L0.2–L0.6

Tác giả: **Doan Van Tai** · Bổ sung File 5: **08/10/2026**.

Với EV-01…EV-19, Type, Conditions, Tác giả giải thích được, Claim có phạm vi và Vai trò dùng judgment do tác giả xác nhận ngày 07/10/2026; wording factual được sửa theo nguồn immutable. Đối chiếu bằng máy/log được ghi riêng khỏi hiểu bài. Không biến kiểm nguồn thành kiểm vấn đáp độc lập.

**Giới hạn numbering:** EV-01…EV-19 là mapping làm việc của L0.1, lập khi chưa có bảng gốc. File 5 nay cung cấp bảng đối chiếu EV-01…EV-12 của PHASE_0 (§8, Bước 6); các hàng chưa có trong repo được thêm thành EV-20…EV-24, xem **Mapping PHASE_0 → repo**. Không đánh số lại để giữ các tham chiếu C1–C5. EV-25…EV-30 là các mục bổ sung từ L0.2–L0.6. Chưa có bản PHASE_0/master plan đầy đủ để đối chiếu độc lập các đoạn được dẫn; bảng mapping dưới đây ghi theo trích đoạn được cung cấp.

EV-20…EV-30 được tích hợp từ nội dung tác giả cung cấp. Cột đối chiếu ghi việc kiểm nguồn/phép tính thực sự đã làm; các ô tác giả tự giải thích vẫn chờ bài làm hoặc xác nhận tương ứng, không tự đổi thành “Có”.

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
| EV-10 | AoI order of magnitude trên testbed | Reported E5 source; raw revalidation chưa hoàn tất | dt4n Phase 23, AoI cuối cửa sổ tới GET, CLEAN/PROD | Có về scope; raw measurement chưa kiểm lại | F1 báo CLEAN mean 0,369 s, PROD mean 0,343 s; JSON theo 10 ô có mean 0,329887–0,374230 s. Không là một mean chung đã tái đo. | Background/real-measurement report có giới hạn. | S11; raw_backup_manifest.json; [T00: JSON/PROVENANCE tại commit cố định](theory/T00_timescale_sanity.md) | 08/10 kiểm hash/JSON: 10 ô, 28.776 quan sát/ô; không tái tính raw, không đại diện production. |
| EV-11 | GO-check CHƯA GO theo TC1–TC3 | E2 + gate judgment scoped | Old-world VoIP, rollout delay, harm budget; oracle nhìn trước chỉ thang headroom | Có | Bản ghi ngày 01/10 chưa GO; TC2 chưa đủ nguồn, TC3 dưới magnitude floor; DP0 chờ quyết. | Historical evidence + motivation. | S06/S21 | Đọc gate report và protocol, không tự phê duyệt NARROW/PIVOT. |
| EV-12 | Ý tưởng tái sử dụng repo cho sandbox | Idea / research provenance | README §9 tại snapshot 02/10; chưa phải sandbox evaluation hoàn chỉnh | Có | Repo cũ liệt kê finite-load feedback là phần còn thiếu; có thành phần để tham khảo, chưa đủ benchmark Main RQ. | Provenance + background. | S12 | Đọc README §9; không coi ý tưởng là empirical evidence. |
| EV-13 | N2 + n02/n02b factorial pilot | E2 exploratory + Idea/Provenance | PSA POS_probeB, G_all, H=0,5, 10 seeds 9101–9110; no finite-action feedback | Có | Pilot tổ chức sources thành information/model families; bảng có ý tưởng bỏ qua action feedback, nhưng script S/M/P thao tác staleness/measurement/parameter. | Provenance + motivation; không direct evidence. | S13/S16–S19 | Đọc N2/script/run JSON/CSV; xác nhận seeds, scope, missing Δρ; không rerun pilot. |
| EV-14 | N0 question card và N1 verdict concepts | Idea / research provenance | Documents ngày 02/10, sandbox proposal; n01c so chế độ tải không là branching tại cùng state | Có | N0/N1 là tiền thân của hướng hiện tại; N1 có thử CRN/load regime nhưng chưa thiết kế/chấm đúng Main RQ. | Provenance. | S14/S15 | Đọc toàn N0/N1, kiểm ngày commit và giới hạn n01c; không suy nguồn gốc duy nhất của RQ. |
| EV-15 | GO-check exact 2,9855978966 ms | E2 exploratory/post-hoc | R1 94/95, α=0,002, cooldown=0, SC FIX−SC SYM | Có | SC SYM giảm mean delay 2,985598 ms, CI95 [2,495705;3,475490] theo contrast hậu kiểm, làm tròn 2,986. | Motivation; không là finite-load State repair experiment. | S06/S07 | CSV row đúng alpha/cooldown/contrast; metadata và số exact có trong verification_results.json. |
| EV-16 | Ba threshold khác construct | Documentary/methodological clarification | EPS GO-check=1,0 ms; F7 ε=0,5S=1,512 ms tại 4 Mb/s; F6 m/r | Có | Hai ε là event harm thresholds trong hai thiết kế; m=8,1/r=10% là practical magnitude gate. Không có mâu thuẫn chỉ vì khác số. | Methodological clarification. | S10/S02/S01/S11 | Đọc code constant, F7 §2.2/2.3 và F6/CI source. |
| EV-17 | F6 ↔ F8 bound 6,84 và gate T10/FH | Scoped non-oracle bound + oracle validity limitation | T10, quỹ đạo S0_FH, upper clairvoyant gain so baseline; same old world | Một phần — exact statistical interpretation | Bound không cần oracle bin 6,84±0,15 ms vẫn dưới m=8,1; không cứu estimands xác nhận dùng oracle T10/FH lỗi. | Historical evidence/background; không generalize. | S01/S05 | Đọc F6 §1 và F8 §3; phân biệt rõ hai phát biểu, không coi chúng mâu thuẫn. |
| EV-18 | Final Review không có byline rõ | Provenance/source limitation | Full snapshot đúng digest đã đối chiếu | Có | Snapshot hiện không ghi rõ byline/author identity; chưa đủ dữ kiện xác nhận người viết, không bác nội dung chỉ vì thiếu byline. | Provenance limitation. | Review digest / reading note / source_checks.json | Mở snapshot; kiểm đầu file và byline; không suy chắc người viết. |
| EV-19 | Raw AoI backup 30 JSONL | Potential E5 source, incomplete verification | Local tar metadata, 30 aoi_*.jsonl; raw không public, chưa tái tính mean | Có | Có raw backup với metadata/hash; chưa chứng minh là bộ khoảng 427 MiB được nhắc hoặc xác nhận lại 0,36 s. | Source recovery / unresolved. | raw_backup_manifest.json; bundle_manifest.json | Đối chiếu manifest thật; raw AoI 71.674.153 byte; tổng file tar 444.748.020 byte, hai lượng khác nhau. |
| EV-20 | Không có clipping → mean rollout cho đúng expected backlog (60 = 60) | E0 (tuyến tính) + E1 (liệt kê 8 path) | Không chạm 0 trên mọi path liên quan; cùng input/belief và cách lấy kỳ vọng, state đã biết trong ví dụ; objective tuyến tính | Chưa — tác giả tự liệt kê ở L1.2/L1.6 | Nếu recurrence và objective tuyến tính trên mọi path của các action, mean rollout cho đúng expected cost: $G_M=G_{M\mid S_1}=0$ | Evidence logic đã known; không là kết quả novelty | Final Review §5.2; [contract §7(d)](01_definitions.md); log tính dưới bảng | Đọc §5.2 đúng snapshot; liệt kê bằng máy ngày 08/10, mean 60; chưa có bài tự liệt kê của tác giả |
| EV-21 | Đóng góp cumulative của backlog ban đầu không biến mất khi horizon dài | E0 (fluid tất định) | $r>0$, $q(t)=(q_0-rt)^+$, $h\ge q_0/r$: $\int_0^h q\,dt=q_0^2/(2r)$ | Chưa | Không suy $G_S$ giảm đơn điệu về 0 chỉ vì horizon dài; ví dụ không chứng minh gain thực tế dương | Evidence logic | Final Review §5.3; log tính dưới bảng | Đọc §5.3 đúng snapshot; kiểm $q_0=10,r=2,h=10/20$ đều 25 ngày 08/10; tác giả chưa tự tính |
| EV-22 | Running example: $G_S<0$, $\Gamma>0$, $I_\Delta=0$ | E1 minh hoạ (chưa tái kiểm) | Toy; switching cost chọn để dạy | Chưa — tính lại ở L1.3–L1.5 | Không claim gì về mạng; chưa dùng làm evidence đã xác minh | Minh hoạ | Master plan II.6 (theo File 5) | Chưa có nguồn đầy đủ để đối chiếu |
| EV-23 | Lợi thế luật dùng bất định giảm khoảng 97% khi giới hạn tần suất đổi trong một kịch bản | E2 exploratory/post-hoc, old world | R1_dualISP, $\alpha=0{,}2\%$; trần trung bình tương đương 1 lần/30 s trên quỹ đạo tham chiếu, không phải cooldown triển khai; dùng lại test seeds | — | Gain width từ 2,515126 xuống 0,077540 ms (−96,92%); không biến mất hoàn toàn hoặc thành điều kiện cần toàn cục | Lịch sử/motivation; không direct evidence Main RQ | [GO switch report tại commit cố định](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/notes/map/go_switch_report.md) | Đọc toàn report ngày 08/10 và tính lại tỉ lệ; chưa rerun experiment/CSV |
| EV-24 | Bảng delay/loss đo trên Mininet (HTB token bucket) | Reported E6 (calibration); chưa audit nội dung | Token bucket khác server có service time | — | Ứng viên representation độc lập cho Phase 7; chưa coi là validation plant mới | Background/hạn chế | [Mininet calibration tại commit cố định](https://github.com/vantai13/dt4n-decision-risk-project/tree/e669f5c8053a81d6de192de9f9d0d6304ee67802/data/mininet_calibration) | Có 5 file; chưa đối chiếu nội dung/số đo riêng |
| EV-25 | Hai loại episode có $\gamma=+2$ và $\gamma=-2$; tỉ lệ $p$ cho $\Gamma=4p-2$ (50/50 → 0) | E0 | Cost thật 20/18; sai số cộng vào gap; cùng pipeline và objective | Chưa | $\Gamma$ trung bình phụ thuộc $D$; trung bình gần 0 có thể che các vùng trái dấu, nên báo theo điều kiện | Evidence logic cho quy tắc báo theo điều kiện | [RQ card §ví dụ](lessons/L0.2_rq_card.md); [contract §7](01_definitions.md); File 5; log tính dưới bảng | Kiểm đại số ngày 08/10, $p=0{,}7$ → 0,8; chưa có kiểm độc lập/read-back |
| EV-26 | Bù sai số: oracle State repair cho $G_S=0$, sửa một nửa sai số state cho gain 1 | E0 | Cost 20/18; $(e_M,e_S)=(1;1{,}5)$ và $(3;-2{,}5)$, mỗi loại 50%; pipeline, $D$, objective và tập action cố định | Chưa | Gain của một oracle repair không là cận trên cho feasible repair cùng loại; $R_{00}$ là cận trên chung cho gain so với ô 00 | Evidence logic; phản ví dụ cho quy tắc master plan V.3/K10 được trích | File 5 (dẫn L0.4 §7); [contract §7(f)](01_definitions.md); log tính dưới bảng | Kiểm bằng máy ngày 08/10: $R_{00}=R_{10}=1$, $R_{\text{half}}=0$; chưa có bài tự tính/kiểm độc lập |
| EV-27 | Cấu trúc dấu của các contrast | E0 (suy diễn từ thiết kế) | (a) ô 11 = oracle; (c) belief $S_0$ là posterior chính xác, prior trùng $D$, $M_1$ tích phân đúng; nhóm báo cáo chỉ dựa trên thông tin trước action | Chưa | $G_{SM},G_{S\mid M_1},G_{M\mid S_1}\ge0$; thêm (c): $G_M\ge0$, $G_{S\mid M_1}$ = EVPI về state hiện tại sau observation, không về $w$ | Evidence logic; rủi ro novelty K1/value of information | [Contract §7(a),(c) và phạm vi](01_definitions.md) | Đối chiếu suy diễn đã ghi trong contract; **chưa có kiểm độc lập**; belief xấp xỉ/nhóm theo state ẩn không có đầy đủ bảo đảm (c) |
| EV-28 | Bảng timescale ba vùng và độ nhạy timing | E0 + nguồn reported E5 | Fluid một bottleneck; $\rho$ trước quyết định 0,5/0,8; packet 1500 B; backlog 100/1000; link 10 Mb/s–10 Gb/s; factor 3 | Chưa — tác giả tự tính một dòng | Trong lưới T00, link chậm/buffer sâu có triển vọng backlog còn liên quan hơn. Vùng ① có ở tổng 0,35/0,6 s, không còn ở 1 s; 0,6 s không là ngưỡng cứng. Không suy gain dương hay bằng 0 | Evidence thứ tự độ lớn, nối K9; chưa là practical-gain evidence | [T00: bảng, nguồn và giới hạn](theory/T00_timescale_sanity.md) | Script + 7 test timescale đạt, ba bảng đã đối chiếu ngày 08/10; chưa đo timing mới |
| EV-29 | Một số switch áp luật lên data plane hàng trăm ms sau control-plane confirmation | L-primary (đối chiếu kỹ thuật); tác giả chưa tự đọc | Một số switch phần cứng trong thí nghiệm năm 2018; không là end-to-end $d_{\text{act}}$ của use case này | Chưa tự đọc | Table 2 báo khoảng 250 ms/400 ms ở hai switch, có corner case dài hơn; không suy latency dưới 1 ms hoặc cận trên phổ quát | Evidence giới hạn cho AS4/K9 | [Kuźniar et al., Computer Networks 2018, §4.1/Table 2](https://dejankostic.com/documents/publications/switches-elsevier18-author-copy.pdf); [T00](theory/T00_timescale_sanity.md) | Nguồn primary đã đối chiếu kỹ thuật ở File 3 ngày 08/10; chưa có record tác giả tự đọc |
| EV-30 | Engine DES cũ có $[\cdot]^+$; giả định “managed không đổi tải” nằm ở chỗ gọi | Documentary (đọc code) | Code tại immutable archive; engine có finite-buffer admission khác AS3 | Chưa | `workload_after` là Reference; `des_world.py` phải Rebuild phần action/load | Provenance cho legacy map | [Legacy: phân loại và dòng code đã kiểm](../legacy/INDEX.md); tag chính: `experiments/f04b_des_gap.py`, `experiments/scan/des_world.py` | Đọc engine dòng 40–50 và `des_path` ngày 08/10; chưa rerun DES; bài tự kiểm L0.5 còn chờ |

Log máy đọc: [source_checks.json](verification/source_checks.json). Kết quả tính lại: [verification_results.json](verification/verification_results.json). Script và cách chạy: [verification README](verification/README.md).
E0 là logic, E2 là scoped simulation/exploration; F7 có tiền đăng ký riêng nhưng không vì vậy thành E3 cho RQ finite-load mới. L-2nd là literature thứ cấp; chưa có record L-self cho primary papers. E5 của AoI vẫn có điều kiện xác minh raw.

### Log đối chiếu kỹ thuật bổ sung — 08/10/2026

Các phép tính dưới đây được chạy bằng Python trong lần tích hợp File 5; không thay bài tác giả tự làm hoặc kiểm chứng độc lập. Final Review §5.2–5.3 được đọc từ snapshot có digest ghi dưới bảng nguồn.

**EV-20:** $q_{k+1}=\max(0,q_k+2+B_k-3)$, $q_0=20$, $B_k\in\{0,2\}$ độc lập đồng xác suất, $H=3$, cost $q_1+q_2+q_3$ (slot = 1).

| Background path | Backlog $(q_1,q_2,q_3)$ | Tổng |
|---|---|---:|
| (0,0,0) | (19,18,17) | 54 |
| (0,0,2) | (19,18,19) | 56 |
| (0,2,0) | (19,20,19) | 58 |
| (0,2,2) | (19,20,21) | 60 |
| (2,0,0) | (21,20,19) | 60 |
| (2,0,2) | (21,20,21) | 62 |
| (2,2,0) | (21,22,21) | 64 |
| (2,2,2) | (21,22,23) | 66 |

Tổng 480/8 = **60**; backlog nhỏ nhất 17 nên reflection không hoạt động. Mean background = 1, tổng arrivals = 3 bằng service: mean rollout giữ backlog 20 trong ba slot, cũng bằng **60**. Một ví dụ này không chứng minh giả định no-clipping cho mọi action/regime; mệnh đề tổng quát cần các điều kiện EV-20.

**EV-21:** với $q_0=10,r=2$, queue hết tại $t=5$; cả $h=10$ và $h=20$ cho diện tích tam giác $10\times5/2=25$. Cumulative contribution giữ nguyên; time average lần lượt 2,5 và 1,25.

**EV-25:** $\Gamma=p(2)+(1-p)(-2)=4p-2$; $p=0{,}7$ cho **0,8**, $p=0{,}5$ cho **0**.

**EV-26:** true gap Switch − Stay = −2; dự báo gap = $-2+e_M+e_S$, tie → Stay. Giữ $e_M$ và sửa $e_S$ như sau:

| $(e_M,e_S)$ | Gap ô 00 / regret | Gap oracle State / regret | Gap sửa nửa State / regret |
|---|---|---|---|
| (1; 1,5) | 0,5 / 2 | −1 / 0 | −0,25 / 0 |
| (3; −2,5) | −1,5 / 0 | 1 / 2 | −0,25 / 0 |

Lấy trung bình 50/50: $R_{00}=R_{10}=1$, $R_{\text{half}}=0$. Gain oracle State = **0**, gain sửa nửa State = **1**, đúng bằng cận chung $R_{00}$. Đây là phản ví dụ logic, không chứng minh refresh thực tế có gain.

**EV-23:** số trong immutable report S23 cho $100(1-0{,}077540/2{,}515126)=96{,}9171\%$. Source được đọc và kiểm SHA-256; không tái chạy experiment lịch sử.

### Bài tự kiểm còn chờ

Tác giả tự liệt kê EV-20, tính diện tích EV-21, kiểm ví dụ EV-22 ở L1.3–L1.5, giải thích EV-25/26/27 ở L0.2/L0.4, tính tay một dòng EV-28 ở L0.6, tự đọc EV-29 và mở code EV-30 ở L0.5. Chỉ cập nhật cột “Tác giả giải thích lại được?” khi có bài làm/xác nhận thật; EV-27 vẫn cần kiểm độc lập.

## Mapping PHASE_0 → repo

Mapping theo bảng trích trong File 5, chưa đối chiếu bản PHASE_0 §8, Bước 6 đầy đủ. Mã ở cột đầu thuộc PHASE_0; mọi trích dẫn EV ngoài bảng này dùng mã repo. Đặc biệt EV-05/06 đảo vị trí giữa hai bảng.

| PHASE_0 | Nội dung | Repo |
|---|---|---|
| EV-01 | $\Gamma=\pm2$ không cần queue | EV-01 |
| EV-02 | 60 = 60 khi không có clipping | EV-20 |
| EV-03 | Backlog ban đầu không biến mất khi horizon dài | EV-21 |
| EV-04 | Running example | EV-22 |
| EV-05 | Literature map P01–P13 | EV-06 |
| EV-06 | G1, CONDITIONAL GO, HOLD | EV-05 |
| EV-07 | F6/F7 | EV-02, EV-03, EV-04, EV-16 |
| EV-08 | GO-check khoảng 3 ms | EV-08, EV-15 |
| EV-09 | Luật bất định giảm khoảng 97% khi giới hạn tần suất | EV-23 |
| EV-10 | AoI testbed | EV-10, EV-19 |
| EV-11 | Mininet calibration | EV-24 |
| EV-12 | Ý tưởng sandbox | EV-12 |

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
| S09 | [Bản dự đoán GO-check — archive 02/10/2026](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/notes/gocheck/PREDICTIONS_claude.md) | `7c47e5c5e1ab3a464834e5b7180260fe81073eea303ba9e6dcb0f82d4221d944` |
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
| S23 | [GO switch report — đối chiếu File 5 ngày 08/10/2026](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/notes/map/go_switch_report.md) | `10a6730b5ac8363366d92ac66bf89e00876a5758a932ff86fd9f4cf42a54d7cc` |

Final Review: [reading note](verification/final_review_reading_note.md), digest full snapshot `fc766e319427ba01da7362de2018cd4da6695dc1fcaa9812ed7badd5c0651fd1`. Note là summary có thể mở công khai; full source vẫn local-only, limitation ở EV-05/06/18. Raw và bundle cũng chỉ public metadata, không giả có download.

## Exposure

[Exposure register](00_exposure_register.md) là phần dữ liệu đã nhìn của inventory. Sổ ghi seed **và** configuration/workload; đối chiếu registry S08 với S16–S18. Không coi RNG phụ hoặc seed mới cùng regime đã chọn sau outcome là đủ confirmation.

## G-level assessment

| Điều kiện lên G2 | Hàng gần nhất / giới hạn | Trạng thái |
|---|---|---|
| (a) Practical effect/equivalence boundary trong load-changing world | EV-13 gần formulation nhất nhưng là pilot PSA thiếu action-induced feedback; EV-14 chưa đúng branching/estimand | NOT MET |
| (b) Prediction trên dữ liệu chưa dùng xây explanation | Không có E3 đúng Main RQ; EV-09/13 và exposure chỉ ghi data đã xem | NOT MET |
| (c) Use case có timescale và intervention cost hợp lý | EV-28 sàng lọc lưới link chậm/buffer sâu, nhạy với tổng tuổi và độ trễ; EV-29 cho chênh lệch confirmation/data plane ở switch cụ thể; chưa có cost/timing thật của repairs | NOT MET (domain đã thu hẹp) |
| Nhánh mechanism: phân biệt threshold null | EV-01 bác diễn giải Γ quá mạnh; EV-27 cho dấu một số contrast là hệ quả thiết kế có điều kiện; chưa có prediction phân biệt với null | NOT MET |

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
9. Full review public source còn thiếu; chưa có record tác giả tự đọc primary papers hoặc kiểm nguồn trên mọi máy. Bảng đối chiếu EV gốc PHASE_0 nay có trong File 5, nhưng chưa có bản PHASE_0 đầy đủ để đối chiếu độc lập.
10. Theo File 5, master plan V.3 viết “feasible repair luôn kém hơn hoặc bằng oracle” và K10 đo theo oracle headroom. Nếu “oracle” ở đây là **một repair riêng lẻ** trong pipeline cố định, EV-26 bác cận trên đó; $R_{00}$ mới là cận trên chung. Oracle quyết định chung vẫn là cận đúng. Chưa đối chiếu câu gốc master plan.
11. Theo File 5, master plan Part XI xếp `workload_after` là Rebuild vì giả định luồng nhỏ. Đọc code cho thấy engine nhận arrival stream tổng quát; giả định managed không đổi tải nằm ở `des_world.py` (EV-30). PHASE_0 được hướng dẫn ghi là đã phân loại đúng; chưa đối chiếu hai văn bản gốc.

Chuyển các discrepancy này vào changelog master plan khi đóng Phase 0; không sửa master plan không có trong phạm vi phiên này.

## Chưa kiểm được

Tác giả tự đọc primary literature (EV-29 hiện chỉ có đối chiếu kỹ thuật); byline review; full raw identity và AoI recomputation; sandbox/máy khác; PHASE_0/master plan đầy đủ; nguồn EV-22 và nội dung/số đo EV-24; kiểm độc lập EV-25…EV-27; bài tự kiểm và read-back/vấn đáp của người thật. EV-23 đã đọc report nhưng chưa rerun kết quả. Các giới hạn không bị xóa khi tác giả đã phê duyệt understanding.
