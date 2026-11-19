# R2-PRAC: nguồn cho practical relevance của M0 (19/11/2026)

Người phụ trách: **Doan Van Tai**. Tác giả yêu cầu: "tải thử 3–5 nguồn, kiểm tra thật kĩ, lấy cái tốt nhất".
Note và mức đọc do **Claude (AI)** thực hiện. **Tác giả chưa đọc** (cần đọc abstract trước khi nộp).
PDF lưu ngoài Git tại `~/papers/state-model-regret/intake/r2_prac/`, mỗi nguồn một thư mục.

Câu hỏi: có công trình mạng nào đánh giá cấu hình hoặc quyết định routing bằng mô hình fluid hoặc flow-level bỏ qua chi phí
hàng đợi, như M0 (mô hình không có chi phí hàng đợi dừng dưới capacity)? Chỉ được dùng các nguồn dưới đây cho một claim về
**lớp mô hình**. Không nguồn nào cho thấy hiện tượng freshness harm.

| ID tạm | Nguồn, bản đã đọc | Mức đọc AI | Trích có vị trí (nguyên văn tiếng Anh) | Dùng được cho | Không dùng được cho |
|---|---|---|---|---|---|
| TWN22 | Ferriol-Galmés et al., "Building a Digital Twin for network optimization using Graph Neural Networks", *Computer Networks* 217:109329, 2022, DOI 10.1016/j.comnet.2022.109329. **VoR OA, CC BY-NC-ND** (Unpaywall → UPCommons), 14 tr., sha256 6e5100280bc62ccb… | AI-T: Abstract, §1 tr.1–2, §2 tr.2–3, §3 tr.3, Fig. 3, refs [11,14–17] | §1 tr.2: "fluid models have become a popular alternative for network optimization [11,14–17] … fluid models assume constant per-link delays and do not consider the effects of queuing delays … Therefore, they offer limited accuracy in networks operating at high utilization regimes". §3 tr.3: "State-of-the-art network optimization solutions mainly rely on fluid models"; DEFO's fluid model has MAPE 21% without loss and degrades to "≈50% MAPE" as load grows, "due to the fact that fluid models do not consider the queuing delay". §2 tr.2–3: optimizer on the SDN controller uses "up-to-date measurements of the network state" to explore configurations "for the current traffic load" | (i) Mô hình fluid bỏ hàng đợi được dùng phổ biến để đánh giá cấu hình (theo nhận định của tác giả TWN22); (ii) sai số tăng theo tải, nhất quán với điều kiện "cần nghẽn" của letter; (iii) NDT có tính hàng đợi (chính TwinNet) là ranh giới phạm vi | Không cho thấy freshness harm. "Fluid model" ở đây là delay theo link cố định, **không** phải fluid queue rollout như M0 |
| DEFO15 | Hartert et al., "A Declarative and Expressive Approach to Control Forwarding Paths in Carrier-Grade Networks", SIGCOMM 2015, pp. 15–28, DOI 10.1145/2785956.2787495 (CCR 45(4) 10.1145/2829988.2787495 gộp). **VoR** (IMDEA repo, publishedVersion), 14 tr., sha256 9a0143f1ed2b4dce… Tác giả gồm Cisco (Filsfils, Telkamp) | AI-T: Abstract, §1 tr.1–2, Table 1 tr.3, §3 tr.4, §6 tr.8–10 (đoạn chọn) | §1 tr.2: "DEFO can readily be used both offline (for offline traffic engineering or what-if analyses) and online (for path recomputation upon traffic changes or failures)". §3 tr.4: "the latency of every network path is assumed to be known by DEFO, e.g., as a result of few active measurements". Objective "MinMaxLoad" (maximum link load), Table 1 tr.3; so sánh với Cisco MATE tr.9 | Nguồn gốc cho TWN22 [14]: optimizer cấp nhà mạng đánh giá cấu hình bằng tải link và delay đo cố định (không mô hình hàng đợi); dùng cho what-if và tính lại khi traffic đổi | Không phải fluid queue rollout. Không xét tuổi telemetry hay giữ quyết định |
| M3_24 | Li et al., "m3: Accurate Flow-Level Performance Estimation using Machine Learning", SIGCOMM 2024, pp. 813–827, DOI 10.1145/3651890.3672243. **Bản tác giả** (CSAIL, PDF tạo 15/05/2024), 15 tr., sha256 49c5f64f3acdd8ed…. VoR CC BY tại ACM/DSpace **chưa tải được** (ACM bị chặn, DSpace 429) | AI-T: Abstract tr.1, §1 tr.1–2, §2.2 tr.4–5, §3.3 tr.6 | Abstract: operators need estimates "to guide network configuration"; "a simple and fast flow-level fluid simulation … We use this inaccurate simulation as input to a simple machine-learning model"; "generalizes over … routing". §1 tr.2: max-min models "are particularly inaccurate for short flows since they do not capture queuing dynamics". tr.5: flowSim "does not model queuing effects". §3.3 tr.6: "flowSim underestimates the FCTs of short flows … because it does not model queueing dynamics" | Mô phỏng fluid flow-level bỏ hàng đợi vẫn được dùng để định cấu hình, và được sửa bằng một mô hình học, tương tự ý tưởng M0 + correction | Mục tiêu là FCT của data center, không phải quyết định giữ routing; correction bằng ML, không phải số hạng dừng |
| M4_25 | Li et al., "m4: A Learned Flow-level Network Simulator", arXiv:2503.01770v1, 03/2025, **preprint**, chưa kiểm bản xuất bản | AI-A+: abstract và §1 tr.1 | §1 tr.1: "many research and industrial systems use flow-level models … in traffic engineering [33, 37, 41]"; "flow-level simulators typically do not model queues" | Chỉ để đối chiếu với M3_24 | **Không trích** (preprint, cùng nhóm tác giả với M3_24) |
| P05 (đã có) | Polverini et al., *IEEE TNSM* 23:2038–2050, 2026 (VoR trong `current/`), đang là [2] của letter | AI-T: tr.5 (apps), tr.6–7 (delay model), tr.8 (setup) | tr.7 (journal 2043–2044): delay DT model là GNN "adapted from RouteNet", với feature "capacity, load, and traffic rate". tr.5: mô hình loss "based on the current utilization levels". tr.8: đường truyền mô phỏng có "Queuing delay … a non-linear function of the link utilization" (đây là simulator đánh giá, **không phải** DT) | NDT trong bài đang trích là **có tính hàng đợi** (học từ tải hiện tại), không phải fluid. Nếu Codex T4 cho thấy ŝ phụ thuộc trạng thái gây harm tuyến tính, đây có thể là lớp liên quan (suy luận) | Không được nói P05 là fluid twin |
| LIU03 | Liu et al., "Fluid models and solutions for large-scale IP networks", SIGMETRICS 2003 (10.1145/781027.781039) / TOMACS 2004 (10.1145/1010621.1010625) | Metadata + abstract Crossref (AI-A) | — | — | **Không tải được**: không có OA (Unpaywall/paper-pilot không có URL); chỉ có bản tác giả trên ResearchGate. Cần tác giả tải qua trường nếu muốn dùng |

**Cập nhật 19/11 (tối):** tác giả tải hai PDF vào Downloads; Claude chép vào `intake/r2_prac/`.
- **m3 VoR** (`m3_vor/`): CC BY 4.0, 15 tr., sha256 4343d7449cfafa2f…. Các trích đã kiểm lại trên VoR:
  - tr.2: "do not capture queuing dynamics";
  - tr.4: "does not model queuing effects";
  - tr.6: "because it does not model queueing".

  Vị trí trích phải theo VoR, vì số trang khác bản tác giả.
- **Liu03 VoR** (`liu_fluid/`): SIGMETRICS 2003, 11 tr., sha256 3c4ec74882ce4b73…; AI-T §1 tr.1.
  - Đây là mô hình ODE "represent the expected or mean behavior" của mạng TCP/AQM, dùng để lấy "transient behavior of the average queue lengths".
  - Vì TCP vòng kín đẩy bottleneck lên capacity, mô hình này có hàng đợi cân bằng khác 0, tức **không** thuộc lớp "chi phí dừng bằng 0 dưới capacity" của M0. **Không trích** cho R2: reviewer có thể phản bác đúng điểm này.

## Đánh giá chọn nguồn (Claude)
Nên trích **TWN22 + DEFO15** cho một câu về lớp mô hình. Lý do:
- cả hai là bản chính thức đã kiểm, có trang cụ thể;
- DEFO15 là nguồn gốc, TWN22 là phép đo độc lập;
- cả hai nhắm đúng việc đánh giá cấu hình routing;
- sai số tăng theo tải khớp phạm vi "cần nghẽn" của letter.

M3_24 là nguồn thứ ba tùy chọn, minh họa "fluid + correction". Chỉ trích sau khi có VoR.

**Không được viết:**
- các hệ này "mắc freshness harm";
- M0 "là" mô hình của chúng.

M0 là một thành viên được cách điệu hóa (stylized) của lớp mô hình fluid không có chi phí hàng đợi dừng.
