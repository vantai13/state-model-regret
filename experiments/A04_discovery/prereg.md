# A04 — discovery trên 38 ô chính và chấm A03 — PREREG

Người phụ trách: **Doan Van Tai**. Soạn theo yêu cầu triển khai hai phần L3.5,
trước outcomes A04; AI hỗ trợ triển khai, không là human review.
Thời điểm/commit/SHA được receipt và manifest ghi bằng lệnh thực tế.

## Đầu vào và provenance

- Contract `contract-v1.2`, D1–D25, lưới `notes/design/grid_v1_2.json` giữ nguyên.
- A01 run03 PASS, DL-053: **dt cuối=1/240s**, ref2; A01 engine receipt
  `60a1032e30c6d37a0dc4c69ab70ca272f17e5070`. Không đổi engine đã đăng ký.
- Card `a03-card-v1`, commit `b05ed70bd4e93544bccefc975cdc452ad40d1380`, SHA256
  `14021a83c6d45a3fbeba6b7cbe27e9c8c0e572734557af1598cf79b819f34639`.
  Dùng nguyên `A03_METADATA` và grader A03 đã commit; không thêm/sửa card.
- P1-V9 **WAIVED_BY_AUTHOR** DL-054, memo chưa gửi; không GVHD_APPROVED.
- [Exposure trước run](exposure_plan.md) được commit. Receipt khóa hash code,
  config, prereg, gate và exposure; runner kiểm trước khi dựng D/cost.
- Đây là prereg A04 **sau A01**: M01/M09/M22 đã lộ contrast ở mọi mức A01.
  Card A03 có trước A01, không gọi A04 là dữ liệu hoàn toàn chưa từng thấy.

## Chạy và giới hạn

Chạy mới **38 main + 8 controls/probes**, mỗi ô tại ref1 (1/120s) và ref2
(1/240s): **92 cell-levels**. H=H_coarse×ref của từng ô; không hardcode H1920.
Không dựng D/cost/outcome R01–R12. Không thêm ô, không đổi lưới/ngưỡng, không ref4
toàn lưới, không đổi dt sau khi nhìn kết quả. 1–6 worker trên các ô độc lập,
không early stopping theo outcome; giới hạn tài nguyên trong config.
Exact finite-law expectation bằng long double và enclosure số có điều kiện;
không Monte Carlo, không seed, không sampling CI, không chứng minh dt→0.

## Thứ tự bắt buộc

1. Commit prereg/code/tests/exposure, sau đó commit receipt riêng.
2. Runner lưu JSON đầy đủ nhưng console chỉ `[VALIDITY]`: ID, completion,
   status, invariant flags, normalized error, unresolved mass; chưa in contrast.
3. Đọc `validity.csv` và `validity_status.json` trước. Sai invariant/certificate
   hoặc control exact-zero → STOP, không chấm/discovery; bảo tồn failed run.
   Numeric HOLD giữ ô, ghi rõ, grader dùng UNRESOLVED. Cờ cặp dt cũng giữ ô,
   dùng UNRESOLVED theo card, không xóa/đổi mẫu số. Không coi HOLD là bug đã sửa.
4. Chạy `score_card.py`, dùng grader A03 nguyên bản, ghi `card_scores.csv`,
   `card_details.csv`, `card_scores.json`, hash input/validity/card/code.
   **Commit các kết quả chấm trước mọi đọc bảng contrast/discovery**.
5. Kiểm tay M09/P2 và M17/P6 bằng một phiên AI mới theo yêu cầu L3.5 §6.4;
   chỉ cung cấp đúng hai ô/cặp dt và luật, chưa cung cấp nhãn grader. Báo phạm vi
   review riêng, không gọi reviewer đó là người thật hoặc người hướng dẫn.
6. Chỉ sau commit chấm: bảng, hình, danh sách pattern, note, exposure/boundary.
   Tool discovery phải kiểm kết quả chấm đã commit và hash inputs còn khớp.

## Validity

Kiểm mọi cell-level: dấu δA≥0≥δB (cả d/dh), W0≤W1 trong các cận vật lý,
oracle L11≤Lsm, GM_S1≤E|eM|, T01/bias bound, nonnegative oracle regrets,
identities Γ/F/V và R11=0. Các kiểm float dùng error đã trả về để phát hiện
vi phạm, không diễn giải tolerance-consistency thành proof độc lập.
Physical certificates được engine kiểm trực tiếp; không clamp gap hoặc đổi tie.
N01–N04/P01: sáu contrast `==0`; W01/S01/P02: GS_M1 `==0`.
e_num/Cref_lower≤.0025, unresolved oracle/M0/D22≤.01. Cặp ref1→ref2 theo
**grader A03**, sáu contrast, Cref_fine lower, không meaningful signflip ngoài
±.005. Không dùng selector A01 (mẫu số min hai mức) thay luật card A04.
F/V pair changes là diagnostic, không thêm điều kiện bác/đứng cho P6.

## Cột và diagnostics

`cells.csv`: cả hai mức của 46 ô, tọa độ/design labels/group/slice/anchors,
λA/ψ dẫn xuất, floor, ĐK1, p_sw thực+enclosure, H/dt; L00/L01/L10/L11/Lcb0,
R00, sáu contrast và F/V (packet·s, %Cref); Cref; a00/a01 và nominal actions;
EΔ/EΔhat/bias/EΔ±, E|eM|, E|IΔ|, quantile |Δ| và |IΔ| 50/90/99% từ engine
kèm enclosure; dấu GS và |EΔ|; từng e_num; unresolved oracle/M0/D22; cờ dt.
Giữ đầy đủ JSON cho intervals, source bounds và detail validity.
Margin quantiles dùng các mức sẵn có (lesson nêu 10/50/90 chỉ là ví dụ).
Flip-mass 2D/EVPI_w vẫn deferred như L3.2; không nhận đã tính.

Nhãn điểm dùng `thresholds.verdict` εE=.005, εR=.01/.02. Tại sensitivity εR=.005,
giữ closed equivalence |G|/Cref≤.005 ưu tiên; phần ngoài dải mới nhận practical.
Ghi rõ ranh giới trùng nhau, không sửa hàm frozen vốn yêu cầu εR>εE. Các nhãn
điểm không thay enclosure hoặc luật card. HOLD/cờ dt hiển thị kèm mọi nhãn.

Chẩn đoán R04 cho state repair fixed-M0: predicted gain tính bằng model costs
của a00 và policy10; δold=true00−pred00, δnew=true10−pred10. Kiểm
GS=predicted_gain+δold−δnew; các true costs chỉ là diagnostic, không feature A05.
Không tra/đọc paper mới để làm identity này; dựa hướng dẫn đã được cung cấp.

## Cheap kill đăng ký riêng A04 (DL-006 lịch sử vẫn DRAFT)

Ba miền, **không chọn lại sau run**: core M01–M22; spoke_A50 M23–M30;
spoke_h2 M31–M38. Một miền NARROW gain thực dụng tính từ 00 khi mọi ô eligible
và upper(R00/Cref)<.01 (strict); upper lấy bốn corner của numeric intervals.
Cref không chắc dương/HOLD/cờ dt làm miền chưa chứng nhận. Giữ mọi ô.
Scope gain được chặn: GS, GM, GSM=R00, GS_M1 và repair khả thi xuất phát 00
cùng D/objective/action set/effective time. **Không** áp cận cho GM_S1/Γ.
Γ hay GM_S1 lớn hơn headroom kèm GS<0 là harm/recovery của policy xấp xỉ,
không bằng chứng lợi ích thực dụng từ 00. Báo bảng ba miền, DL nếu NARROW.
Không tự chuyển nhãn PC/Gate hoặc đổi RQ do một miền này.

## Ba hình, sáu luật đọc, MT5

H1: EΔ/Cref × EΔhat/Cref, đường chéo và hai trục, màu κ, marker quantile B,
floor đánh dấu. h2 tách panel khỏi h8. Không nối điểm.
H2: sáu contrast theo ô/thứ tự thiết kế/lát, error bars numeric, ±.005 và .01.
H3: headroom R00/Cref theo ba miền, error bars và .01.
Ghi λA/p_sw thực cạnh mỗi ô trong bảng/panel annotation; ĐK1/caption đi kèm.
Controls/probes có bảng riêng, không trộn vào denominators chính.
Caption nhắc ψ∈[−.2,.05], near-boundary selected cells, không tần suất,
khác λA giữa lát; h2 chỉ κ=.3. MT5 là diagnostic, null chờ A05-F.

## Discovery và điều kiện dừng

Sau score commit, ghi **mọi pattern đã xét** (kể cả loại), tối đa 0–3 retained.
Mỗi pattern phải nêu tọa độ κ/qA/qB/η/h/target (không λA/p_sw thực làm nguyên nhân),
mọi ô khớp/trái, dấu GS/bias/|EΔ|/E|eM|/margin quantiles/F/V; xét sáu thay thế:
λA, MT5, identity, design guarantee, precision/dt, T-H1. Không giải thích bỏ ô trái.
Pattern mới mang nhãn DISCOVERY, tìm prior có mục tiêu theo AGENTS/skills;
metadata/log trước, tối đa3 đề xuất mới và cần duyệt trước PDF/note mới.
Không có pattern vượt identity/confounding thì báo 0 retained, không tạo claim
để đủ quota; không gọi T01/GS<0⇒Γ>0/F+V=GS là phát hiện. Không mở held-out.
K5 carry theo card ngay cả unresolved, không đổi luật để cứu prediction thất bại.

## T-H1 và kết thúc

**Kết quả định giá cửa sổ [t0,t0+h], không phải long-run loss.** D13 có dt·qH,
không có cost xả sau h/terminal surcharge. D phụ thuộc thiết kế (SR8).
Card không preregister cơ chế: mọi route là mô tả, không chấm cơ chế “đúng”.
Note A04, exposure và addendum claim boundary hoàn tất thì dừng L3.5.
Không mở A05-T/Phase4; không tự ghi Understanding/ownership/human reader PASS.
