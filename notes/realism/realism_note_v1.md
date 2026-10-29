# Realism v1 — kết quả và giới hạn

Người phụ trách/người soạn: **Doan Van Tai** · 29/10/2026 · DL-070.

**Hai vùng model value và harm đều HOLD realism ở cả hai bối cảnh: chưa đủ
nguồn tương thích để kết luận IN, EDGE hoặc OUT.** Đây là nhánh(d), không phải
nhánh(c) “đã chứng minh phi thực tế”.

## Điều tôi thấy

| Vùng discovery cũ | Số ID | Cấu hình khác nhau | DC(a) | Edge(b) |
|---|---:|---:|---|---|
| Toàn pilot | 216 | 210 | Toàn bộ UNSOURCED | Toàn bộ UNSOURCED |
| MV: GM/Cref≥1% | 20 | 20 | 20 UNSOURCED | 20 UNSOURCED |
| SH: GS/Cref≤−1% | 80 | 78 | 80 UNSOURCED | 80 UNSOURCED |
| Giao MV∩SH | 14 | 14 | 14 UNSOURCED | 14 UNSOURCED |

Luật/envelope commit6bef959; sửa lỗi xuất bảng, không đổi luật ở830a187;
nhãn đủ216ID commit1164500 trước overlay. f=1.5/2/3 đều cùng nhãn vì missing
sources không được thay bằng khoảng nới. 432dòng features là216ID×2context;
1296dòng labels là216×2×3, không phải1296regimes độc lập.

Buffer/actuation flags đều UNSOURCED do chưa có B_t/d_act cùng định nghĩa;
mode-oracle flag TRUE ở mọi regime. Tạiκ=.1, corr mode cũ-hiện tại chỉ
2.06115e−9; tạiκ3 là.513417. Đây là corr của mode, không corr backlog hay
mức gain. Với Bpost, tail giả định budget=5T chạy từ.00000996356 đến.22794655
(tức.000996%–22.7947%). Budget này chỉ sensitivity, chưa là buffer thực,
và tail queue vô hạn không là xác suất drop.

Kiểm6stationaryqueues trên3regimes discovery đã khai, ref1/2, không J/newgain:
max |atom_slot−atom_fluid| giảm.0184192→.00960711; max chênh meanvirtualdelay
.386527→.0967024ms ở baseτ1s; max chênh tail.000228336→.0000277656.
Không coi fluid approximation là đáp án exact của slot, không dùng TVbound
cho unbounded meanQ. Đây không đóng gate sốL3R.3.

## Điều các kết quả chưa cho phép nói

- Chưa có realism validation của hệ thống mạng thật; không có bằng chứng tất
  cả216ID thực tế hay phi thực tế. IN về sau cũng chỉ là không mâu thuẫn dải nguồn.
- Số đếm là discovery thích nghi, có duplicate; không là prevalence ở mạng thật.
- Model value và harm không hầu như tách rời:14/20MV cũng harm. Không gom hai
  hypothesis hoặc dùng sự đồng xuất hiện để kết luận cơ chế nhân quả mới.
- Scope vẫn fluid,two-level,a/c=.6,idealbacklog,hiddenmodeoracle,buffer vô hạn,
  action tức thời. Cờ rủi ro không dự báo được kết quả đổi giả định sẽ theo hướng nào.

## Quyết định và việc cần bổ sung

MV:(d) HOLD_REALISM_UNSOURCED; SH:(d) HOLD_REALISM_UNSOURCED. Không tự thu hẹp
RQ hoặc đổi plant. Ưu tiên cần evidence: cùng use case có backlog schema+P/L/W,
decision-hold horizon và action delay; offered input rate theo cửa sổ1ms–1s;
buffer-time absolute/perqueue. Measurement traffic structure hiện có đủ để
ghi limitation single-timescale, chưa đủ để fit ranges. Nếu bổ sung nguồn sau
labels phải tạo envelopev2 và ghi sau quan sát, không sửa v1.

Được học/soạn L3R.5; chưa khóa contract hoặc CFframe, chưa chạy Phase4.
Tài liệu này soạn theo ủy quyền, không xác nhận tác giả đã tự hiểu/read-back;
Understanding/P0-V10/L8/T05 vẫn OPEN.
