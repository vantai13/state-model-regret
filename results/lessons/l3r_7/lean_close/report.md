# L3R.7 — đóng gọn bằng card v2 (DL-095–096)

Người phụ trách: **Doan Van Tai** · 30/10/2026.

AI (Claude) soạn, chạy và viết theo ủy quyền: "bạn hãy làm theo hương dẫn và đống lesson này giúp tôi
đi", "tôi chỉ muốn đóng lesson 7 này thôi, làm sao cho phù hợp đi" ([nguyên văn](author_choices.json)).

Ranh giới:
- Không có human review.
- Không ghi tác giả đã dự đoán, đọc card hay tự làm phần nào.
- Không có outcome CF nào được tính.

## Kết luận

**L3R.7 đóng: thiết kế confirmation chạy được đúng một lần đã có đủ.** Cụ thể:
- card v2;
- numerics v1.3.1-lean đã khóa;
- n = 60 cho mỗi vùng chấm điểm và 15 cho mỗi vùng BND, theo luật DL-077;
- root đã commit trước khi rút;
- danh sách **270 regime CF**, chỉ tham số, sinh một lần, 0 lần rút lại;
- dry-run B chạy thông suốt đường ống.

Chưa phải Gate 3R. L3R.8 còn audit D22, người đọc thật (P0-V10/L8), quyết định realism (HOLD_UNSOURCED) và nhãn
Gate 3R. Phase 4 HOLD giữ nguyên.

## Làm gì, theo thứ tự (mỗi bước một commit)

| Bước | Kết quả | Commit |
|---|---|---|
| A. Khai trước luật, code, test, DL-095 | Prereg ghim 126 file nguồn | `1c0cab0` |
| B1. Đối chiếu môi trường | 4/4 ca local (Python 3.14) trùng **chính xác** native05 (GCP, 3.13) | `ca4d3d5` |
| B2. Chọn r | 1/10, 1/20, 1/40 rớt (RATE_MV_EDGE đổi Ḡ_S 0,66/0,66/0,41 pp); **1/100 đạt** (≤ 0,145 pp) | `ca4d3d5` |
| C. Card v2 | Chỉ đổi bước λA/λB/u = 1/100; 9/9 kiểm L3R.6; lock 12 file; card v1 nguyên byte, verify PASS | `b62f329`, `dcfa01c` |
| D. Numerics | 118 ca × 11 mức = 1298 phép tính, 0 UNRESOLVED; mức đầu tiên mọi ca đạt: **(640, 4)**, dt 1/480 | `de87601`, `5d20cb8` |
| E1. Thời gian, n | p95 bundle 59 s (góc) / 457 s (tốc độ lẻ); cố định 2301 s → **n 60, BND 15**, 45,4 CPU-giờ | `5d20cb8` |
| F. Dry-run B | 4 góc discovery → adapter → scorer gốc; control = 0 chính xác; model đồng nhất cho Ḡ_M = Ḡ_M\|S1 = 0 chính xác; 3 anchor PASS | `23ff3ff` |
| E2. Seed, prereg, rút | Root từ OS CSPRNG; prereg LOCKED_BEFORE_SAMPLING; 270 regime, mọi giá trị đúng lưới v2 | `ef6ca77`, `16cfa60`, `7173d70` |

Test: 710/710 toàn repo PASS, trong đó có 9 test mới cho luật, adapter và sampler v2.

## Luật chọn mức số đã hoạt động thế nào

| Mức ứng viên | Ca rớt | Lý do |
|---|---|---|
| (80, 2) | 17 | C̄ hoặc contrast đổi quá 0,25% theo dt hoặc K (C̄ tới 0,40%, contrast tới 0,50 pp) |
| (160, 2) | 9 | C̄ đổi 0,26–0,29% theo dt; RINT_MV có cận số học rộng |
| (160, 4) | 6 | X2065, CAL_057/058: contrast đổi 0,31–0,37 pp theo K; CAL_049/050, RINT_MV: cận số học |
| (320, 4) | 2 | CAL_049/050: cận số học 2,77·10⁻⁴ ở láng giềng (160, 4) |
| **(640, 4)** | **0** | Chọn |

Thay đổi duy nhất so với luật của native05 nằm ở phần kiểm nhất quán.
- Native05 so đồng nhất thức với cận số học khoảng; bản này so với dung sai TOL_NUM = 0,25 pp của C̄.
- Contract R1 đã chấp nhận sai số làm mịn ở mức 0,25 pp, nên kiểm nhất quán chặt hơn mức đó là thừa.
- Sai số số học vẫn phải ≤ 1/4000, và R1 giữ nguyên.

## Những gì phải nói rõ

- **Lưới 1/100 chỉ rẻ hơn 1/1000 khoảng 4–8 lần, không phải 1000 lần.** Lưới thô hơn bị luật loại, vì gần λB = 8
  thì Ḡ_S rất nhạy với λA. Ngân sách vẫn đủ cho n = 60.
- **Lỗi của AI trong lúc làm:** đã sửa `sampler.py`, mà file này nằm trong manifest hash native05, nên bộ chạy tự từ
  chối. Đã revert (`fc6accd`); card v2 dùng sampler gốc, chỉ đặt tạm bước làm tròn trong `frame_v2.card_rounding`
  (có test khôi phục trạng thái).
- **Phạm vi numerics:** chỉ cho card v2 (tốc độ trên lưới 1/100). Numerics của card v1 vẫn mở. Theo R1/R7, chênh lệch
  làm mịn là chẩn đoán, không phải cận sai số đã chứng nhận.
- **Thời gian** đo trên WSL2 local với cache lạnh, mỗi mức của bundle một lần gọi. Đây không phải p95 của quần thể CF.
  Dự toán 45,4 CPU-giờ là kế hoạch, không phải trần cứng.
- **Inventory v3** (1396 khóa v1.3) có thêm:
  - toàn bộ regime map, quy về age 1; 10 điểm nằm trong vùng MV: 2 ở MV+A, 4 ở MV-ii, 4 ở MV-BND;
  - các điểm calibration và kiểm đại diện mới;
  - 8 regime chạy thử trong phiên AI, đã thấy số nhưng không lưu file.

  Không regime CF nào trùng chính xác.
- **Card v2 được đóng băng sau khi regime map đã lộ.** Claim và vùng chép nguyên từ v1, vốn đóng băng 29/10 lúc 10:17,
  trước regime map. Lựa chọn duy nhất mới (r) do luật khai trước quyết định trên dữ liệu calibration.
- Tag `numerics-v1.3.1-lean` chỉ ở local; chưa push.

## Tệp

- Ghi chú thiết kế: [l3r7_lean_close.md](../../../../notes/design/l3r7_lean_close.md).
- Prereg: [prereg.json](../../../../experiments/R3R_14_lean_close/prereg.json),
  [cf_prereg.json](../../../../experiments/R3R_14_lean_close/cf_prereg.json).
- Card v2: [card](../../../../notes/phases/PHASE_3R_hypothesis_cards_v2.md),
  [lock](../../../../notes/phases/PHASE_3R_hypothesis_cards_v2.lock.json).
- Numerics: [spec](../../../../notes/design/numerics_v1_3_1_lean.json),
  [receipt](../../../../notes/phases/numerics_v1_3_1_lean.lock.json).
- Kết quả:
  - [replay](replay_report.json);
  - [chọn r](representation_selection.json);
  - [chọn mức](numerics_selection.json);
  - [thời gian và n](timing_summary.json);
  - [dry-run B](dry_run_B.json);
  - [inventory v3](collision_inventory_v3.json);
  - [danh sách CF](cf_generation/attempt01/regimes_cf.json).
