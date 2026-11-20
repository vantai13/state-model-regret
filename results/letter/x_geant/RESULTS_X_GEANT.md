# X-GÉANT (X2; X4 dừng ở bước 0): kết quả (Claude, 20/11/2026)

- **Người phụ trách:** Doan Van Tai. Claude viết thẻ và chấm theo ủy quyền; Codex code, bước 0, pilot.
- **Không có:** mentor review, dự báo của tác giả.
- **Chấm lại độc lập (Codex):** chờ quota.

## Quy trình
| Bước | Commit / tệp |
|---|---|
| Design | letter_smr `581e769` |
| Code, chọn regime từ train, bước 0, dự đoán train, pilot, `lock.json` | `b7b1df477` |
| Thẻ và scorer khóa ở `lock_card.json` (sau lock gốc, trước truth; lệch protocol đã ghi trong thẻ) | `b7b1df477` |
| Truth một lần trên GCP `n2-highcpu-32`, 30 worker: 87/87 COMPLETE, 7,21 CPU-h, 1619,7 s wall, peak RSS 133 MiB | raw `4f2d79af1` (checksum hai phía `0ebcd1d1`) |
| VM về `n2-custom-12-49152`, TERMINATED | |

## Bước 0
- **X2:** bất đồng fresh/stale trên ngày test-S, mỗi rule trên 5568 quyết định: TH_0,5 = 501, TH_0,65 = 582, TH_0,8 = 361, TH_0,9 = 177, MLU = 443.
  Tie = 0 với TH_0,65/0,8/0,9. Kết quả: SIGNAL_OK.
- **X4:** Hybrid ≠ Stationary 0/8352, M0 tie 100%. Kết quả: NOT_ENOUGH_SIGNAL, không chạy truth.
- **Kiểm sau:** không OD nào có hai path qua **hai** link nghẽn khác nhau. Mọi flow có cả hai path ở 0,9 đều đi chung link bận nhất, như DAY3.

## Verdict
| Test | Kết quả | Verdict |
|---|---|---|
| G1: dấu G_S rule ngưỡng, dự đoán từ ngày train | 0/36 ô gộp phân giải (8–9 ngày evaluable mỗi ô); dấu khớp ở 24/36 ô chưa phân giải; mức bản ghi 34/56 | **NOT_EVALUABLE** |
| G2: luật tĩnh không bị ảnh hưởng, regret thấp | G_S = 0 ở mọi bản ghi; regret both-side trung vị 0,0% | **ĐỨNG** |
| G3: luật tĩnh ≤ mọi rule ngưỡng | 102/102 | **ĐỨNG** |

Phép so với null: NOT_EVALUABLE (khai trước, vì null cùng dấu dự đoán ở mọi ô).

## Dự báo của Claude
| F | Dự báo | Kết quả |
|---|---|---|
| F1 | TH_0,65/0,8 có G_S < 0, TH_0,9 > 0 | Đúng với TH_0,65 và TH_0,9 (chưa phân giải); **sai với TH_0,8** (G_S > 0) |
| F2 | G1 đứng 0,8–1 | **Sai:** NOT_EVALUABLE |
| F3 | G2, G3 đứng | Đúng |

## Phân tích nguyên nhân (post hoc)
- **TH_0,8:** chênh share stale − fresh là +0,05 tới +0,11 trên ngày train (tháng 5–6), nhưng −0,02 tới −0,045 trên ngày test evaluable (mùa hè). Với
  ŝ < 0, dấu quan sát khớp s·ΔF_test. Vậy **luật dấu vẫn đúng**; dự đoán vận hành sai vì share đổi theo mùa.
- **Độ phân giải:** chỉ 8–9 trong 29 ngày ổn định qua cổng evaluability; biến động giữa ngày lớn.
- **Ngày không evaluable** có G_S% rất lớn (tới ±35%) chỉ vì C_ref gần 0. Đây là lạm phát do chuẩn hóa; loại khỏi chấm là đúng.

## Đưa vào paper (theo luật thẻ)
- G1 NOT_EVALUABLE: một câu V-C với số đếm, nêu share đổi theo mùa (post hoc).
- G2, G3 đứng: cùng câu đó.
- X4: một mệnh đề nối câu V74 (0/8352).
