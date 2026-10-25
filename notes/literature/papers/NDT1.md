# NDT1 — Almasan et al., 2022

Người phụ trách: **Doan Van Tai** · kiểm **25/10/2026** · **AI-only, tác giả chưa xác nhận đọc**.

- [Nguồn](https://arxiv.org/abs/2205.14206v2); DOI `10.1109/MCOM.001.2200012`.
- IEEE Communications Magazine 60(11):22–27; bản đọc **arXiv v2**, 7 trang, accepted manuscript.
- Mức **T**: abstract, §II–V, PDF tr.2–6; references tr.7. Đã xem Fig.2–4 tr.3,5 bằng render.
- PDF local và checksum: [source access](../../../results/lessons/l2_4/source_access.json).

## Paper nói gì?

§II/Fig.1–2, tr.2–3: twin nhận mô tả traffic/topology/routing/scheduling để dự đoán
KPI; optimizer tìm cấu hình rồi áp lên mạng. Đây đã là workflow dùng twin cho quyết định.

§IV-A, tr.4–5: RouteNet-E được train bằng 100.000 mẫu mô phỏng, topology 25–50 node;
test 500 mẫu trên 50–300 node. Ground truth là OMNeT++; Fig.3 đo MAPE.
Ở 250–300 node, thời gian trung bình RouteNet-E khoảng 6,47 s, simulator khoảng 3 giờ 39 phút.

§IV-B/Fig.4, tr.5: evolutionary optimizer đổi OSPF link weights; đo delay bằng simulator
trên topology tổng hợp 25 node, so shortest path. Không phải oracle D15 của repo.
§V, tr.6 nêu khó khăn dữ liệu, generalization và uncertainty.

## Đối chiếu với repo — AI suy luận

Input case study không phải backlog/mode D7; không gán timescale phút/giờ hay
“state hoàn hảo S1” cho paper. Trong các mục đã đọc chưa xác nhận can thiệp D20/D21
hay regret theo D18. Bằng chứng synthetic topology không tự xác nhận vận hành mạng thật.

PC2/PC5: giữ làm định vị; không claim “twin hỗ trợ chọn routing action” là ý mới.
Không thay nhãn PC, không coi khác metric là bằng chứng contribution.
