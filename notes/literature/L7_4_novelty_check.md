# L7.4 — Kiểm novelty cho bốn claim lõi và claim τ (bounded, AI-only)

Người phụ trách: **Doan Van Tai** · 04/11/2026. **AI (Claude) soạn theo ủy quyền** ("về phần bài paper cần bài nào nói tôi
sẽ lấy cho bạn"). Theo [search_protocol](search_protocol.md). Mức đọc lượt này: metadata và abstract (OpenAlex/Crossref),
**không đọc full text bài mới nào**. Chi tiết từng thao tác ở [search log, mục L7.4-N1](search_log.md).

Kết luận chung, viết theo protocol: **đã tìm theo 10 query và 1 lượt dò xuôi (mục 3); chưa xác nhận từ các nguồn đã sàng
một công trình có cùng estimand, cơ chế và regime với bốn claim lõi.** Điều này không chứng minh novelty, không đổi nhãn
PC/Gate và không nâng G-level. Kết quả là "đã sàng", không phải "đã khảo sát lĩnh vực".

## 1. Đã đọc lại trước khi tìm (thư viện hiện có)

- [L6_4_prior_check](L6_4_prior_check.md): Galanis 2015 (harm do unawareness), Whitmeyer 2026, de Lara–Gossner,
  Gao 2010 (road traffic), Scherrer–Perrig–Schmid 2020, Eilat–Eliaz 2025. Kết luận cũ: generic information harm và VOI
  theo action/payoff **không** được nhận là đóng góp mới.
- [M00](papers/M00.md) (Mitzenmacher, TPDS 2000): thông tin cũ trong cân tải. Cơ chế herding: nhiều quyết định cùng dùng
  một bảng cũ. Kết quả có điều kiện (§3.4/PDF10–12).
- [information_harm](information_harm.md), [state_staleness](state_staleness.md) (P04, stale link-state),
  [freshness_decision_value](freshness_decision_value.md) (AoI, AoII, AY19, R32, S11).
- R34 (Kuri–Kumar): bản đọc là CDC 1992, 2 trang. Bản TAC 1995 (DOI 10.1109/9.402238) vẫn **cần lấy** (AGENTS.md).

## 2. Theo từng claim: "paper nào sẽ giết claim này"

| Claim | Paper sẽ giết claim (nếu tồn tại) | Query đã chạy | Tìm thấy gần nhất | Trạng thái |
|---|---|---|---|---|
| **C1** luật bậc một zero-fit cho twin mù horizon | Một bài dẫn khai triển G_S(h) = h s ΔF + B + O(e^{−γh}) cho chính sách certainty-equivalent hoặc mean-model trên thông tin state, với khe phổ làm đồng hồ onset | Q3, Q8 (certainty equivalence, VOI dưới model sai, chi phí trung bình, horizon dài) | Không có trong 40 kết quả đã sàng. Bước 1 của T11 (V = h r + g − e^{Qh} g) là kỹ thuật bias/Poisson chuẩn của bài toán chi phí trung bình; **không nhận là mới**, nguồn sách giáo khoa chưa tra trong phiên này | chưa xác nhận prior; phần toán là kỹ thuật chuẩn |
| **C3/C5** state tươi hại twin mù horizon; cơ chế planner ngầm | Một bài chỉ ra: với **một** quyết định của controller dựa trên model trung bình/fluid, thông tin queue tươi làm quyết định tệ hơn vì controller phản ứng theo dao động, còn thông tin cũ cho hành vi gần chính sách dừng | Q1, Q5, Q9, dò xuôi từ Dahlin | M00, **Dahlin 2000** (diễn giải load theo tuổi), Fischer–Vöcking 2008 (adaptive routing với thông tin cũ, nhiều agent), Kuri–Kumar 1995 (JSEQ tối ưu với trễ 1 bước). Các bài này là herding/nhiều quyết định, hoặc chính sách tối ưu với trễ, **không phải** twin mù horizon một quyết định (đọc từ abstract) | chưa xác nhận; cần đọc Dahlin (đề xuất 1) |
| **C4** harm với telemetry chỉ backlog | Một bài chỉ ra: cập nhật queue length hiện tại (không biết pha traffic) làm controller dựa trên model tệ hơn so với thông tin cũ | Q1, Q5, Q7 | M00/Dahlin (cùng họ), P04 (stale link-state). NDT: không có bài nào trong 20 kết quả đo chất lượng quyết định theo tuổi telemetry cho routing | chưa xác nhận |
| **C6** đồng hồ T_int của backlog | Một bài dùng thời gian tích phân hoặc relaxation của backlog để xếp khi nào state có giá trị cho routing | Q9, Q2 | Moeller–Krishnamachari 2026 (arXiv 2609.06351): ngưỡng theo tỷ số trễ/coherence time cho kiến trúc thông tin. **Đã nằm trong danh sách chờ duyệt** từ L2.8 follow-up | chưa xác nhận; nguồn gần nhất chưa đọc |
| **C5′ / τ** harm tăng theo tuổi của telemetry bị thay (L7.5) | Một bài cho thấy giá trị của độ tươi không đơn điệu, hoặc âm, với controller dùng model, theo tuổi | Q2, Q4, lookup | **Shisher–Sun 2022** (MobiHoc): sai số suy luận có thể không đơn điệu theo AoI; Arı et al. 2024 (ISIT), cùng nhóm. Đây là bài toán học/suy luận, không phải routing với twin mù horizon (đọc từ abstract) | **đe dọa wording**: câu "tươi hơn có thể tệ hơn" đã có prior chung; chỉ cơ chế và regime có thể khác |

**Hệ quả cho wording (AI đề xuất, chờ tác giả):** không viết "lần đầu cho thấy telemetry tươi có thể gây hại". Viết theo
estimand và cơ chế: "với twin mean-value mù horizon ra một quyết định, harm đo bằng G_S có dạng h·s·ΔF và tăng theo tuổi
của telemetry bị thay". Câu này đến giờ chỉ là dự đoán zero-fit, chưa có truth ở τ ≠ 1.

## 3. Thao tác đã chạy (tóm tắt; số thật ở search log)

- **10 query keyword/lookup:** 8 OpenAlex × tối đa 20, 2 lookup Crossref.
- **1 lượt dò xuôi:** OpenAlex, các bài trích Dahlin 2000; sàng 40 trên 114.
- **Ứng viên giữ mới:** 3 (mục 4).
- **Luật dừng 2×20 đạt:** Q7 (NDT/telemetry) và Q8 (VOI/model sai) liên tiếp, mỗi query 20 kết quả, không giữ mới.
  Q9 sau đó cũng không giữ.
- **Lỗi/hạn chế:**
  - OpenAlex trộn nhiều kết quả ngoài ngành (y tế, kinh tế, vehicle routing);
  - không dùng Semantic Scholar hay Google Scholar trong lượt này;
  - không dò ngược (references) từ M00 hay Dahlin;
  - chưa tra venue SIGCOMM/NSDI riêng cho NDT.

## 4. Đề xuất đợt này (tối đa 3 nguồn mới; chờ tác giả duyệt và tải)

| # | Nguồn (đã kiểm metadata) | Claim / PC | Lý do đáng đọc | Mức đọc đề nghị |
|---|---|---|---|---|
| 1 | Michael D. Dahlin, *Interpreting Stale Load Information*, IEEE TPDS 11(10):1033–1047, 2000. DOI [10.1109/71.888643](https://doi.org/10.1109/71.888643) (Crossref). Bản hội nghị ICDCS 1999, DOI 10.1109/icdcs.1999.776530, là cùng công trình | C3, C5, τ; PC3/PC4 | Diễn giải load theo **tuổi** của thông tin. Đây là prior networking gần nhất cho câu thực dụng "telemetry tươi chỉ có ích khi twin nhìn được horizon/tuổi". Có thể làm co claim C5 và câu thực dụng của τ | T: §2 mô hình, §3 chiến lược diễn giải, kết quả theo tuổi |
| 2 | Md Kamran Chowdhury Shisher, Yin Sun, *How Does Data Freshness Affect Real-time Supervised Learning?*, MobiHoc 2022, tr. 31–40. DOI [10.1145/3492866.3549711](https://doi.org/10.1145/3492866.3549711) (Crossref) | τ (C5′); PC4/PC6 | Prior rằng sai số có thể **không đơn điệu** theo AoI. Bài chặn trực tiếp mọi câu "tươi hơn không phải luôn tốt hơn là mới"; cần so cơ chế (tương quan đặc trưng so với twin mù horizon) | T: định nghĩa, định lý chính về tính đơn điệu, điều kiện |
| 3 | Simon Fischer, Berthold Vöcking, *Adaptive Routing with Stale Information*, Theoretical Computer Science 2008 (DOI 10.1016/j.tcs.2008.01.055); bản PODC 2005 DOI 10.1145/1073814.1073868 (OpenAlex; chưa kiểm Crossref) | C3, C6; PC3 | Routing nhiều agent với thông tin định kỳ cũ: dao động và điều kiện hội tụ theo chu kỳ cập nhật. Giúp tách herding (nhiều quyết định) khỏi cơ chế một quyết định của ta | A → T nếu cần: mô hình bulletin board, điều kiện hội tụ |

**Đang chờ từ trước (không tính vào đợt này):**
- Moeller–Krishnamachari 2609.06351, 10.1145/3769700.3771695, 2608.01725: ba đề xuất L2.8 follow-up, chưa duyệt.
- Bản TAC 1995 của R34 (10.1109/9.402238).
- RedTE (SIGCOMM'24), Namyar (NSDI'24) cho realism WAN.

Không tải PDF, không tạo note nội dung cho ba nguồn mới cho tới khi tác giả duyệt (AGENTS.md mục 4). Catalog/Excel trên
`main` giữ nguyên.

## 5. Đã đọc (04/11/2026, sau khi tác giả tải cả ba)

Tác giả tải ba nguồn đề xuất (Downloads/tmp và Downloads), nên ba nguồn được coi là đã duyệt. AI đọc targeted và ghi note:
[DAH00](papers/DAH00.md), [SS22](papers/SS22.md), [FV09](papers/FV09.md). Mức đọc AI-T; tác giả chưa tự đọc.

| Nguồn | Ảnh hưởng tới claim (AI đề xuất, chờ tác giả) |
|---|---|
| DAH00 | **Nghịch lý "thêm thông tin có thể tệ hơn" trong cân tải đã được nêu và chữa** bằng diễn giải theo tuổi và horizon của pha (§6, tr. 1045). Cơ chế ở đó là herding, nhiều request, hại do tin **cũ**. Câu thực dụng của τ ("twin phải nhìn được horizon thì refresh mới có ích") phải trích DAH00 như nguyên tắc gần nhất. Không viết là ý mới |
| SS22 | **"Feature tươi nhất có thể không tốt nhất" đã có định lý** cho người dự đoán Bayes tối ưu khi chuỗi xa Markov (Thm 3.4, tr. 34). Dự đoán L75-3 (S(τ) không giảm, Y chỉ có backlog) là một trường hợp của khung này. Harm của M0 (C-τ1) đến từ model sai, không phải từ tính không Markov, nên không bị SS22 bao trùm, nhưng chưa xác nhận |
| FV09 | Cùng họ M00/Dahlin: dao động do nhiều agent phản ứng theo bảng cũ. Thuốc chữa là làm chậm theo 1/T (§1.1, tr. 3358). Dùng để tách phạm vi một quyết định của ta; không xác nhận C6 |

**Wording đề xuất sau khi đọc:**
- C3/C5: "Với một quyết định giữ suốt h và twin mean-value mù horizon, state tươi có thể hại *mà không cần herding*." Câu
  này phải đi kèm trích M00, DAH00, FV09 cho nhánh herding và SS22 cho nhánh suy luận.
- Không còn đề xuất mới nào trong đợt này. Ba đề xuất L2.8 follow-up và RedTE/Namyar vẫn chờ.
