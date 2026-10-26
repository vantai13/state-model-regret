# Khung related work một trang — Phase 2 (L2.9 Part 2)

Người phụ trách: **Doan Van Tai** · 26/10/2026. **Provenance:** AI (Claude) viết theo ủy
quyền tác giả ("đóng vai tác giả", hội thoại 26/10); đoạn 2 dựa trên đoạn mẫu của
lesson, đã đối chiếu lại vị trí. **Tác giả chưa tự viết lại.** Mỗi câu ghi nguồn, vị trí
và mức đọc; AI-T/AI-A là mức đọc của AI, **chưa có L-self** (0/19). Đoạn 5 theo
[nhãn tạm AI chấm theo ủy quyền](prior_boundary.md#l29--nhãn-tạm-do-ai-chấm-theo-ủy-quyền-tác-giả-26102026).

**Đính chính 26/10:** trích dẫn WM26 "diagnostic tools…" là **§8** (Limitations and
Conclusion, trang PDF 9), trước ghi nhầm §9; xem [check](../../results/lessons/l2_9/wm26_author_reading/check.md).

## (1) NDT cho quyết định

NDT được mô tả là mô hình nhận traffic, topology và cấu hình routing/scheduling để dự đoán KPI, rồi làm vòng what-if cho một optimizer đổi trọng số OSPF [NDT1 §II, §IV-B/Fig.4; AI-T]. Kiến trúc tham chiếu của IRTF tách Data và Models thành hai trong năm yếu tố của twin, và vẫn là Internet-Draft [NMRG-13 §4/Fig.1; AI-T]. Một hệ SDN cho twin chạy song song với action để trả feedback thụ động, không chặn action, và báo precision/recall theo từng loại yêu cầu delay, throughput, reliability, carbon [P05 §III-A, §VI-A tr2047–2048; AI-T qua web PDF]. Các hệ Open RAN gần đây đặt twin thành cổng trước action, duyệt candidate khi prediction set nằm trong ràng buộc và resync tham số cấu hình khi drift [P10 §V–VI; AI-T, preprint]. Một hệ khác theo dõi sai số utility trên action đã chạy để quyết định có tin twin hay không và đánh giá bằng regret của utility [NDT26 §III–V, §IV-B; AI-T, preprint].

## (2) State cũ và giá trị của độ tươi

Trong QoS routing, link state cũ có thể làm tăng blocking và gây flapping trong những cấu hình mà nhiều kết nối cùng chọn một link trông nhẹ trước lần cập nhật kế tiếp [P04 §III-A, tr166–167, Fig.1; AI-T]. Trong load balancing, dùng thông tin queue cũ một cách ngây thơ có thể tệ hơn chọn ngẫu nhiên, còn chọn ngẫu nhiên trong ít ứng viên giúp phá đồng bộ trong các regime được xét [M00 §3.4, PDF10–12; AI-T]. Dòng Age of Information đã chuyển từ đo tuổi bản tin sang đo giá trị của độ tươi theo cost của quyết định, kể cả khi action điều khiển chính nguồn được quan sát [S11 §III, Eq10, PDF5–7; AI-T]. Tuổi và sai lệch thông tin là hai đại lượng khác nhau, và có metric phạt cả hai [AoII §II, Eq3–9; AI-T]. Với cost cộng dồn trên horizon hữu hạn, ảnh hưởng của workload ban đầu để lại một hằng số không phai theo horizon, có thể dương, âm hoặc bằng không dưới giả định Lévy và moment [P13 Thm1, tr276, cộng phép nhân T; AI-T].

## (3) Độ chính xác của model so với chất lượng quyết định

Với lớp model bị chỉ định sai, model tối ưu theo sai số mô phỏng vẫn có thể xếp sai thứ tự policy cho một reward và tập policy nào đó [P03 Thm3.1, PDF3; AI-T]. Trong traffic engineering, đã có cách tối ưu trực tiếp objective TE từ demand lịch sử mà bỏ bước dự đoán demand riêng [P07 §2.2–3.2; AI-T]. Value equivalence chỉ đòi model khớp Bellman update trên một tập policy và hàm cho trước [P12 Def1, §3.1, PDF3; AI-T], và đã có dung sai xấp xỉ kèm cận hiệu năng [R43; AI-A]. Dưới quan sát một phần, approximate information state cho cận trên mất mát khi sai số reward và transition bị chặn [AIS22 §3.2 Def7, Thm9, PDF15–18; AI-T]. Trong latent world model, thay center hoặc responses bằng giá trị thật cho thấy repair làm giảm nhiều MSE nhất không phải repair cho lựa chọn tốt nhất [WM26 F.1 Eq10, Table10–12, PDF22–23; AI-T, preprint]. Trong predictive signal control, độ nhạy được đo theo từng nguồn bias một lần một, và cập nhật thường xuyên chỉ bù được một phần [P02 §3.3, Bảng 2, §4; AI-T].

## (4) Khái niệm được mượn

Hai contrast có điều kiện của đề tài trùng EVPPI và trung bình VSS dưới giả định ghi rõ [SOB14 Eq1–4, AI-T; B82, AI-A; T03 v2, phép dẫn AI], còn giá trị học discrepancy được tách khỏi giá trị thông tin đầu vào [P11 §2.4 Eq2.7–2.8; AI-T]. Re-solving một chính sách xấp xỉ có thể làm hại [R02 §5 Ex1; AI-T], và SC cùng Π-accuracy là điều kiện đủ để không hại [R04 §3; AI-T].

## (5) Điều đề tài hỏi

Các đoạn trên cho thấy NDT đã được dùng và chấm theo quyết định, state cũ và độ tươi đã được định giá theo cost, và "model đủ cho quyết định" đã có lý thuyết [đoạn 1–3; AI-T]. Khác WM26, nơi repair center và responses nhập giá trị tương lai thật trên cùng pool candidate và chỉ báo C−P, S−P, C−S [WM26 F.1 Eq10, §8 PDF9; AI-T], đề tài lộ state hiện tại gồm backlog và mode ẩn theo D20, đổi biểu diễn tính ngẫu nhiên của tương lai theo D21 trên cùng posterior, với oracle không biết tương lai và một quyết định làm đổi tải [contract v1.2 D15, D19–D21]. Khác biệt này đổi estimand: dưới M1, repair lộ tương lai cho loss L* − E[EVPI_w], nên phần gain đó chứa giá trị thông tin tương lai mà D18 loại khỏi regret theo thiết kế [D11, D15, D18; suy luận AI, kiểm số học ở audit]. Đề tài hỏi Γ/Cref > 0,005 ở các ô K3 theo câu chữ của PC3, vị trí ranh giới OεRE dưới S0 trên tọa độ queue ở dạng hẹp của PC5, và phần tách backlog với mode ẩn dưới fixed-M0 ở dạng hẹp của PC6 [prior_boundary L2.9, nhãn tạm AI ủy quyền]. Từ các nguồn đã đọc, chưa xác nhận một prior đo Γ theo D19 với oracle không biết tương lai cho một quyết định dời tải có mode ẩn; đây không phải tuyên bố novelty và còn chờ L-self [prior_boundary L2.9; AI-T].

---

Kiểm (PHASE_2 §14): đoạn 4 ngắn hơn mỗi đoạn 1–3; câu nào cũng có nguồn kèm mức đọc;
đoạn 5 không dùng mục nào trong [danh sách không được claim](../01_claim_boundary_v1_2.md)
làm điều mới. Số từ và các luật này được kiểm tự động ở
[audit L2.9 Part 2](../../results/lessons/l2_9/part2/report.md).
