# W2-LIT — kiểm prior có mục tiêu, 14/11/2026

Người phụ trách: **Doan Van Tai**. Mức đọc dưới đây là **AI-T**, không phải tác giả đọc.
Ủy quyền: brief W2-LIT cho phép tải/đọc ba nguồn; không đổi PC/Gate/contract.
Đã đối chiếu [wave-1](../../results/ext_validity/WAVE1_REPORT.md) và
[T12](../theory/T12_plugin_stationarity.md). Q1 = decision period/vòng kín;
Q2 = event so với periodic; Q3 = xử lý stale state. Mục đích là kiểm prior liên quan
DL-143/PC1–PC3 và ranh giới diễn giải, không gán lại nhãn PC lịch sử.
Trang dưới đây là **trang PDF của đúng bản đọc**, không phải trang VoR.

## 1. Bumpensanti & Wang — re-solving DLP

- **Metadata:** Pornpawee Bumpensanti, He Wang, *A Re-Solving Heuristic with Uniformly Bounded Loss for Network Revenue Management*, **Management Science 66(7):2993–3009 (2020)**,
  [DOI 10.1287/mnsc.2019.3365](https://doi.org/10.1287/mnsc.2019.3365).
  Crossref xác nhận số báo; [publisher](https://pubsonline.informs.org/doi/10.1287/mnsc.2019.3365)
  ghi online **16/03/2020** (khác ngày issue 01/07/2020 trong Crossref).
- **Versions checked:** [arXiv](https://arxiv.org/abs/1802.06192) liệt kê v1 17/02/2018,
  v2 23/05/2018, **v3 11/12/2018**. Đọc v3; không đọc/đối chiếu nội dung v1/v2.
  Link PDF publisher chuyển về abstract; chưa đối chiếu theorem với VoR.
- **PDF:** `/home/vantai/papers/state-model-regret/current/Bumpensanti2020_Resolving_arxivv3.pdf`
  (44 trang; SHA256 `8486bbda75160d9575416e1cbb8562539e0566ff65e5f58d3966e8a3f4ea6cbd`).
- **AI-T:** abstract, introduction/§1.1–1.2 tr.1–5; §2 tr.7–10; §3 tr.10–13;
  §4 tr.13–18; §5 tr.18–19; §6 tr.19–23; §7 tr.23–24. Không kiểm appendix proofs.

**Fact — paper nói gì**

| Claim | § / trang / Eq |
|---|---|
| Inventory hữu hạn, không bổ sung; independent Poisson arrivals từng class với rate đã biết; nhận/từ chối ngay và irrevocable, dùng resource theo BOM matrix A; inventory cuối horizon T không có salvage. Policy non-anticipating, phải đủ capacity thật. | §1 tr.1–2; §2 tr.7 |
| DLP thay arrivals ngẫu nhiên bằng mean. FR re-solve ở t=0,…,T−1 bằng **remaining capacity hiện tại** C(t)/(T−t); admission probability giữ trong mỗi unit interval nhưng vẫn cập nhật capacity và kiểm feasibility ở từng arrival. Không có delayed telemetry trong model này. | §2.2.1 tr.8 Eq.(1)–(2); §3 tr.10–11, Algorithm 2 |
| Revenue loss = v*−vπ; regret = vHO−vπ với hindsight biết tổng arrivals; hai benchmark khác nhau. Scaling giữ rates, tăng T và C=bT, tương đương scaling rates/capacity theo k. | §2 tr.7; §2.1 tr.8; §2.2.2 tr.9 Definition 1 |
| FR có upper bound vDLP−vFR=O(√T); **tồn tại instance** có vHO−vFR=Ω(√T), và vHO−v*=O(1) nên worst-case revenue loss FR là Θ(√T). Không phải mọi instance đều Θ(√T); trường hợp nondegenerate có guarantee O(1) từ prior được paper nhắc lại. | §3 tr.10–11; §4.2 tr.16 Theorem 1; §5 tr.18–19 Propositions 2–3 |
| IRT dùng O(log log T) lần re-solve, t*u=T−T^((5/6)^u), **kèm threshold** admission gần 0/1. Theorem 1: vHO−vIRT=O(1), constant phụ thuộc rates/revenues/A, độc lập T và C; không cần nondegeneracy. | §4.1–4.2 tr.14–16, Algorithm 3, Theorem 1 |
| Fig.3 cho FR hơn SPA khi r1/r2=2 nhưng kém SPA khi ratio=5 (b=1). FR phản ứng với thiếu arrivals class giá cao bằng cách nhận class giá thấp, tiêu inventory không thu hồi. Đây là minh họa simulation; không phải theorem thứ tự FR/SPA cho mọi ratio. | §3.1 tr.11–12 Fig.3; §5.1 tr.18–19 giải thích lower bound |
| Chọn lịch thưa **một mình** chưa đủ O(1). Thí nghiệm IR/FRT gợi ý threshold quan trọng hơn lịch; FRT loss có vẻ bounded nhưng paper chưa chứng minh cho FRT của họ. | §6 tr.20–23, nhất là §6.1 tr.21; §7 tr.23–24 |

**Inference — AI đề xuất.** Overlap Q1: mean-value planner được cập nhật bằng state thật
vẫn có loss; không nên viết “re-solving thường xuyên luôn sửa được sai số fluid” hoặc
“mọi FR đều có loss √T”. Estimand ở đây là tổng revenue loss/regret trên horizon với
inventory tiêu hao; repo so chi phí giữa hai information pipelines trong queue lặp quyết định.
Cơ chế degenerate allocation/irrevocable consumption (§3.1, §4.1) khác queue transient/bias
trong T12. **Chưa xác nhận từ các phần đã đọc** một luật harm riêng ở Δ dài, đổi dấu tại
Δ≲T_int hay transient contribution E[g]/Δ; không đồng nhất T với decision period Δ.
IRT so với FR đổi cả schedule và threshold, không cô lập tác động tần suất (§4.1; §6.1).

**Unclear:** chưa kiểm proof bounds/VoR; không suy paper loại trừ mọi monotonicity theo
frequency hay cung cấp threshold Δ* cho repo. Các prior được nhắc trong introduction chỉ
là lời dẫn của nguồn này, chưa được đọc primary trong phiên.

## 2. Soleymani, Baras & Johansson — stale information với optimal control

- **Metadata:** Touraj Soleymani, John S. Baras, Karl H. Johansson, *Stochastic Control with Stale Information–Part I: Fully Observable Systems*, **CDC 2019, tr.4178–4182**,
  [DOI 10.1109/CDC40024.2019.9029447](https://doi.org/10.1109/CDC40024.2019.9029447), Crossref xác nhận.
- **Versions checked:** [arXiv 1810.10983](https://arxiv.org/abs/1810.10983) chỉ liệt kê
  **v1 25/10/2018**, 6 trang. Bản này sớm hơn CDC; IEEE landing bị JavaScript/robot challenge,
  chưa đối chiếu full-text VoR 5 trang.
- **PDF:** `/home/vantai/papers/state-model-regret/current/Soleymani2019_StaleControlI_arxivv1.pdf`
  (SHA256 `34abd7c955775180100c04387e2f30172c427b4e569e8fad3e176bc57a95199a`).
- **AI-T:** abstract/§I tr.1; §II tr.2–3; §III tr.3–5 (Prop.1, Lemma 1,
  Theorems 1–2, Prop.2); §IV tr.5–6; §V tr.6. Kiểm ảnh tr.4 để đối chiếu công thức.

**Fact — paper nói gì**

| Claim | § / trang / Eq |
|---|---|
| Plant linear discrete-time, Gaussian noise độc lập, known dynamics, controllable (A,B), sensor fully observable; channel noiseless nhưng transmitter giữ measurement trong queue. ηk∈[0,ηk−1+1], η0=0; có thể gửi measurement cũ hoặc không gửi, bỏ measurement obsolete. | §II tr.2 Eq.(1), Definitions 1–2 |
| A là expected weighted average age; J là expected average quadratic state/control cost, có terminal cost. Bài tối đa A dưới J≤J0; scalarized χ có **−θkηk** cộng quadratic costs. | §II tr.2 Eq.(2)–(7) |
| Kết quả giới hạn ở information sets: controller bỏ thông tin về state chứa trong lựa chọn age/timing; queuing mechanism dùng phần không dự đoán được bởi controller. | §II tr.3 Assumptions 1–2 |
| Estimator dự báo từ x(k−ηk) qua A^ηk và lịch sử controls, không giữ nguyên stale measurement. Optimal controller là certainty-equivalent u*k=−Kk x̂k, gain Riccati dùng model thật. | §III tr.3 Prop.1 Eq.(8)–(10); tr.4 Theorem 1 Eq.(14) |
| Dưới controller đó, χ bằng phần full-state cost cộng EΣ[−θkηk+e_kᵀΓk e_k], Γk=Kkᵀ(BᵀSk+1B+Rk)Kk≥0. Optimal queuing policy tối ưu cả age reward, error penalty và future value ck; error là tổng propagated innovations. | §III tr.3 Lemma 1 Eq.(11); tr.4 Eq.(15)–(16), Theorem 2/proof |
| Prop.2 bỏ future value để có suboptimal error-dependent queuing policy; chứng minh χ(π′,μ*)≤χ(zero-wait,μ*). **Đây không phải phát biểu J nhỏ hơn zero-wait**. | §III tr.5 Prop.2 Eq.(17) và proof |
| Ví dụ λ nhỏ hơn cho phép age cao hơn và estimation/control kém đi. Fig.3 là lower bound trên frontier A* vì restricted information và suboptimal queuing; critical age cho stabilization chỉ được thảo luận như việc cần nghiên cứu thêm/conjecture. | §IV tr.5–6, Fig.3 tr.4; §V tr.6 |

**Inference — AI đề xuất.** Q1/Q3: không đọc nguồn này thành theorem “J tăng đơn điệu
theo **average AoI của mọi policy**”. Từ Eq.(11), (14)–(16), nếu chỉ xét J, full-state
zero-wait đạt error penalty 0; stale policy có expected penalty không âm trong mô hình
và information assumptions của bài. Điều này khác bias của M0 trong repo.
Với **age cố định/exogenous** và noise i.i.d. covariance W, các công thức ấy cho
E[eᵀΓe]=tr(Γ Σ_{j=0}^{η−1} A^j W(A^j)ᵀ), không giảm theo η. Đây là phép suy
**AI đề xuất có điều kiện**, không phải theorem về endogenous schedules: error có thể
triệt tiêu theo path, average age không sắp thứ tự information sets.

Q2: policy phụ thuộc innovations/error (§III Eq.(16)–(17)) là prior gần cho adaptive
measurement scheduling, nhưng không so alarm q90 với random decision epochs trong
queue của repo. Clock điều khiển vẫn discrete k; không có sweep decision period Δ hay
model-biased controller (§II Eq.(1), §III Theorem 1). Tránh viết “certainty-equivalence
luôn là planner xấp xỉ sai” và “stale beating zero-wait trong bài này chứng minh telemetry
tươi làm tăng J”: phải nói rõ model, estimator, criterion và admissible information.

**Unclear:** monotonicity giữa các endogenous schedules có cùng/different average age
chưa xác nhận; chưa kiểm assumptions đủ để bỏ timing information trong hệ repo;
không có theorem stabilization threshold được xác nhận từ bản đọc.

## 3. Mendelson & Kuang — sparse communication và state approximation

- **Metadata đã đính chính:** Gal Mendelson, Xu Kuang, *Load Balancing Using Sparse Communication*.
  **Có bản journal:** [DOI 10.1287/opre.2022.0359](https://doi.org/10.1287/opre.2022.0359),
  *Operations Research* **74(2):1026–1046**, issue **03–04/2026**, online **19/06/2025**.
  Crossref search + DOI lookup và [publisher](https://pubsonline.informs.org/doi/10.1287/opre.2022.0359)
  khớp title/authors/volume/pages; publisher Cite-as dùng 2025, Crossref issue date 01/03/2026.
  Không lấy “2022” trong DOI làm năm xuất bản. dblp exact-title lookup trả 0;
  Semantic Scholar bị chặn approval, không phải bằng chứng không có publication.
- **Versions checked:** [arXiv](https://arxiv.org/abs/2206.02410) v1 06/06/2022,
  **v2 23/05/2024**; đọc đúng v2, không đọc v1. Footnote tr.1 yêu cầu citation
  **G. Mendelson and X. Kuang**, ghi manuscript từng có tên *CARE: Resource Allocation Using Sparse Communication*.
  VoR link chuyển về abstract/Request Access; không có PDF VoR từ đường đã thử.
  Abstract VoR dùng wording optimality khác v2; không coi hai bản có theorem giống hệt.
- **PDF:** `/home/vantai/papers/state-model-regret/current/Mendelson2022_SparseCommunication_arxivv2.pdf`
  (60 trang; SHA256 `6c406b1524c766586dfa9d319f9814e787e97e903602f99fa04b2e71caf034a4`).
- **AI-T:** abstract/§1 tr.1–5; §2 tr.6–12; §4 tr.16–19; §5 tr.19–21;
  §7.1–7.2 tr.31–35 (theorem statements, không audit proofs);
  §8 statements tr.46–47; §9 setup/discussion tr.49–57. Kiểm ảnh tr.34.

**Fact — paper nói gì**

| Claim | § / trang / Eq |
|---|---|
| Single balancer, K FIFO non-idling servers, infinite buffers; route từng arrival ngay. Messages chứa exact queue length, **không communication delay**. Balancer biết messages và routing history. | §2.1.1–2.1.4 tr.6–8 Eq.(1)–(5) |
| JSAQ chọn queue có **estimated** length nhỏ nhất. General estimator: Q̃i(t)=Qi(tm)+Ai(tm,t]−D̃i(tm,t]; error bằng absolute departure-estimation error. Basic không ước lượng departures nhưng vẫn cộng arrivals, không phải giữ nguyên snapshot. | §2.1.4 tr.8; §4.2–4.3 tr.16–18 Eq.(11)–(14) |
| MSR emulates FIFO queue bằng deterministic mean service requirements 1/μi; MSR-x dừng emulated departures sau x−1. Không định nghĩa Q̃ là Bayes posterior mean queue. | §4.4 tr.18–19 Definitions 4.4, 4.8–4.9, Eq.(15) |
| RT gửi mỗi 1/ri; DT sau mỗi x departures; ET khi absolute approximation error đạt x, server chạy cùng emulation để biết error. Đây là adaptive communication, routing vẫn ở từng arrival. | §5 tr.19–21 Definitions 5.1–5.3 |
| Theorem 2.3: DT/ET + basic/MSR-x có AQ≤x−1 và M(t)≤D(t)/x. ET+MSR có Eτi≥(x/2−1)^2/μi dưới FIFO/Exp services (x≥3); bound mạnh hơn Eτi≥x(x−1)/μi cần **infinite initial backlog** để không idle. | §2.2 tr.10 Theorems 2.3–2.5; §7 mở đầu tr.31 nhắc điều kiện backlog của 2.5 |
| Performance analysis giữ K cố định, rates scale theo n, fixed interval [0,T], empty initial state, modulated renewal input và independent renewal service primitives (finite variance). Theorem 7.3 còn cần λ̄max<∞, λ̄min>Σμ̄i−Kμ̄min và max-error=o_p(√n), uniform trên interval; kết quả là queue imbalance=o_p(√n) (SDDP). | §7.1 tr.31–33; §7.2.1 tr.33–34 Eq.(46)–(48), Theorem 7.3 |
| Theorem 7.7: SDDP + **uniformly bounded service requirements** ⇒ nominal workload gap với pooled server là o_p(√n). Actual-workload corollary thêm homogeneous service rates; heterogeneous actual-workload optimality không được suy ra. | §7.2.2 tr.34–35 Theorems 7.6–7.7, Corollary 7.8, Remark 7.9 |
| Theorem 8.1 cho admissible approximations: RT rate ω(√n); DT thresholds x,y=o(√n) với basic/MSR-y; ET threshold o(√n) với queue emulation. Các điều kiện workload ở trên vẫn phải giữ khi nối theorem. | §8 tr.46–47 Theorem 8.1 |
| Simulation K=30, Bernoulli arrivals/geometric services, loads .5/.8/.95. Ở load .5 và constraint communication 10%, algorithm tốt nhất trong phép so vẫn tệ hơn Round Robin không communication. Đây là harm so baseline trong simulation, không theorem rằng tăng freshness làm hại; không xác nhận herding mechanism từ kết quả này. | §9.1 tr.49–50; §9.3 tr.52–53 Fig.8 |

**Inference — AI đề xuất.** Overlap Q3 mạnh ở thiết kế **communication → estimation →
routing**; MSR dùng mean dynamics nhưng có theorem performance dưới approximation-error
conditions, nên không được gọi mọi mean-based queue estimator là có hại. JSAQ cắm **ước lượng
đã cập nhật** vào routing, khác “plug-in” của T12 là cùng φ áp nguyên quan sát lagged.
Basic cũng khác frozen snapshot vì cộng own arrivals (§4 Eq.(11)–(15)); closed-loop
routing còn thay đổi state law, không tự thỏa stationary sampling trong T12.

Q2: RT/DT/ET đã so periodic với event-based **communication** (§5; §9.3), nên tránh
viết generic “event triggering cải thiện sparse-state load balancing” như đóng góp mới.
Repo đổi **decision epochs** bằng alarm trên path A, estimand là signed freshness effect;
bài này đánh giá workload/JCT và message budget (§2.1.5). Chưa xác nhận từ phần đọc
một theorem herding, nonmonotone value of freshness, ngưỡng Δ/T_int hoặc transient 1/Δ.

**Unclear:** không audit proofs/VoR. Không ghép exponential assumption của Thm.2.4–2.5
với bounded-service assumption Thm.7.7 thành một guarantee vô điều kiện. V2 có mismatch
mô tả load/communication giữa tr.56 và tr.57/Fig.14–15; không dùng các số đó làm evidence.

## Truy cập và giới hạn phiên

- Trước tải: scan tên và first-page text của **29 PDF current + 146 PDF Downloads (recursive)**,
  không thấy ba nguồn; lượt scan không timeout hoàn tất, lượt kiểm phụ timeout ở hai slide
  không liên quan. Sau đó tải **3/3 PDF** trực tiếp `https://arxiv.org/pdf/<ID-version>`;
  kiểm magic `%PDF`, `pdfinfo`, text/identities và SHA256.
- `paper_search` Crossref/dblp/OpenAlex dùng được; download MCP, `scholar_search` details/citations
  và `paper_pilot.get_pdf_page_text` trả **“requires approval, but approval policy is never”**.
  Fallback: Python urllib từ arXiv, `pdftotext -layout`, `pdftoppm` + xem ảnh local.
  Không dùng shadow library. Có OA cho cả ba; không ghi “no OA” cho toàn công trình chỉ vì VoR bị chặn.
- Optional forward: một screen OpenAlex (fallback sau scholar bị chặn), top 20 most-cited;
  payload bị cắt khi hiển thị, **13 record có title/metadata đủ nhìn đã sàng, 7 chưa sàng**.
  Không nhận 20 đã đọc/sàng đầy đủ; **0 đề xuất thêm**, không bước thứ hai, không tải nguồn thứ tư.
- Không simulation/experiment, không thay catalog/Excel/source. Dừng sau ba targeted reads
  và một forward screen giới hạn; không saturation/novelty clearance.

## Tóm tắt Q1/Q2/Q3 — 5 dòng

1. **Q1 đã biết:** FR của mean-value DLP có worst-case loss √T; IRT+threshold có O(1), không phải guarantee do giảm frequency riêng (nguồn 1 §4–6).
2. **Q1 chưa rõ:** harm dài Δ, đổi dấu Δ≲T_int và first-order transient 1/Δ của wave-1 **chưa xác nhận từ các nguồn đã đọc** (đối chiếu nguồn 1 §2–7, nguồn 2 §II–IV, nguồn 3 §7–9).
3. **Q2 đã biết/chưa rõ:** adaptive error-based scheduling và RT/DT/ET là prior; alarm-selected **decision** epochs với signed freshness effect của repo chưa được xác nhận tương đương (nguồn 2 §III; nguồn 3 §5, §9).
4. **Q3 đã biết:** model-aware prediction/emulation khác frozen stale input; true-model CE có error-cost decomposition, JSAQ có guarantee có điều kiện (nguồn 2 §III; nguồn 3 §4, §7–8).
5. **Q3 chưa rõ:** không có kết luận đơn điệu chung theo average AoI, không chuyển guarantee sang biased M0/T12 ngoài giả định; chưa có novelty kết luận, chưa đổi PC/Gate (nguồn 2 §II–IV; nguồn 3 §7.2).
