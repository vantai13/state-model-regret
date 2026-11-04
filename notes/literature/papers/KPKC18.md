# KPKC18 — Kuźniar et al.: đặc tính cập nhật flow table trên switch OpenFlow

Người phụ trách: **Doan Van Tai** · 04/11/2026. Note do AI (Claude) soạn.
Tác giả tự tải file sau danh sách L7.3-R2. Mức đọc: AI-T, chỉ để kiểm số T00 dùng. Tác giả tự đọc: chưa có xác nhận.

Kuźniar, Perešíni, Kostić, Canini. *Methodology, measurement and analysis of flow table update characteristics in
hardware OpenFlow switches*. Computer Networks 136 (2018), tr. 22–36.
[DOI 10.1016/j.comnet.2018.02.014](https://doi.org/10.1016/j.comnet.2018.02.014).

**Phiên bản.** File tác giả tải là **Accepted Manuscript** (25 trang, có watermark), không phải VoR. Lưu tại
`~/papers/state-model-regret/l73/KPKC18/KPKC18_Kuzniar_CompNet18_AM.pdf`, sha256 `6438138d8460…`.
Đọc targeted: §4.1/PDF7–9 (Table 2, Fig. 3, tr. in 8 = PDF9; đã render trang để đọc bảng), §4.2/PDF10.

**Kiểm T00.** T00 ghi "Kuźniar §4.1/Table 2: gap confirmation/data plane 250/400 ms ở hai switch". Bản AM khớp:
- HP 5406zl "often falls behind up to 250 ms";
- Pica8 P-3290 "reorders + behind up to 400 ms" (§4.1, Table 2/PDF9).

**Bổ sung chưa có trong T00 (Table 2/PDF9)**
- HP 5406zl: "Indefinitely in corner cases (up to 22s in our tests)".
- Switch X, firmware V1: "falls behind indefinitely. Up to 4 minutes in our experiments". Firmware V2 thì đồng bộ.
- Dell 8132F, Switch Y, NoviSwitch 1132: đồng bộ với control plane.
- §4.2/PDF10: độ trễ lớn nhất giữa control và data plane tăng theo số rule, tới 250 ms ở 750 rule.

**Suy luận của AI.** Trễ actuation có đuôi dài tới chục giây hoặc vài phút ở một số switch và firmware. Đây là độ lệch
giữa xác nhận và data plane, không phải trễ end-to-end của một use case.

PC liên quan: realism (trễ actuation). Không đổi nhãn PC.
