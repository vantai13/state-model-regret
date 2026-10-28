# L3.7 / A05-T — báo cáo mở held-out đúng một lần

Người phụ trách: **Doan Van Tai** · 28/10/2026 · contract-v1.2 · DL-059 (quyết định), DL-060 (kết quả).
AI (Claude) triển khai, chạy và viết báo cáo theo ủy quyền trực tiếp của tác giả
("hãy làm theo hướng dẫn và thực hiện lesson 7 cho tôi đi"). Không human review, không
author-attest Understanding. Kỳ vọng trước run của tác giả: **chưa có**.

## Kết quả, bốn nhánh báo riêng

| Nhánh | Ô | Verdict | Số đo chính |
|---|---|---|---|
| **PC4 nội suy (verdict chính)** | 8/8 eligible | **WEAKEN** | d = 0,247036 điểm % C_ref (m = 0,25); MAE0 = 0,690, MAE1 = 0,443 |
| PC4 ngoại suy (h = 12 s) | 2/2 eligible | **FALSIFY** | d = −0,141751; MAE0 = 2,047, MAE1 = 2,188 |
| PC4 nội suy yếu R09/R10 | niêm phong | DO_NOT_OPEN | D = 0,2123 < m; không có outcome |
| **K5** (R03/R04, khóa trước A04) | 2 ô | **DOES_NOT_STAND** | R03 STANDS (headroom-limited); **R04: G_M/C_ref = 0,5279% > 0,5%** |
| **C1** (R05–R08, khóa sau A04) | 4 ô | **STANDS** | G_M = 0 danh nghĩa ở cả 4 ô; không ô nào headroom-limited |

Đơn vị: điểm phần trăm của C_ref của chính ô đó, ở dt = 1/240 s. Không có lấy mẫu,
nên không có p-value hay CI. Khoảng d là enclosure số, rộng 1,0·10⁻¹⁰ điểm %.

## Provenance và thứ tự commit

| Bước | Commit |
|---|---|
| A05-F freeze (predictions SHA `9b93e3f3…`, discrimination SHA `cbd0851a…`) | `5f20103` |
| Runner, gate, rescorer, 22 test (full suite 391 PASS) | `72903b7` |
| Quyết định không đảo ngược: decision.json + DL-059 + exposure + claim sheet | `146169d` |
| Run một lần, output gốc | `e719157` |
| Báo cáo này, DL-060, claim boundary, exposure sau run | commit kế tiếp |

Engine, card, A01 và A04 không đổi kể từ `0eb42f2` (git diff rỗng).
`preflight()` PASS trước run. Console được chép vào thư mục run sau khi chạy xong, nên
không nằm trong `output_hashes.json`; SHA256 của nó là `342d1450…9e02`.

## Validity (tầng 1, kiểm trước khi chấm)

- p_sw công khai tái lập bitwise **20/20** (10 ô × ref 1, 2).
- 20/20 cell-level BOUNDED, hard_pass. Không ô HOLD; cả 10 cặp 1/120→1/240 đều STANDS.
- max e_num/C_ref_lower = 7,26·10⁻⁶ (budget 0,0025); max unresolved mass = 4,59·10⁻⁶ (cap 0,01);
  max thay đổi giữa hai mức dt = 0,0117% C_ref (dung sai 0,25%).
- Đúng ở mọi ô: C_ref = L11 cùng row; record khớp id/tọa độ; dt đúng; R00/R01/R10 không nằm
  dưới 0; G_S + Γ giao G_S|M1; các identity và cận T01 của A04 `ledger_checks`.
- Cổng precision của PC4 (nửa độ rộng ≤ 0,025 điểm %): 10/10 ô qua; không ô unavailable.
- Chấm lại độc lập `rescore.py` (không import scorer đã khóa): **agreement PASS**, cùng verdict,
  cùng d bằng phân số chính xác, cùng nhãn từng ô.
- R09/R10: không D, không cost, không outcome. Chuỗi "R10" xuất hiện trong output chỉ là
  khóa **regret R10** (nhánh (1,0)), không phải ô R10.

## PC4 nội suy — WEAKEN

- **Fact.** Trên 8/8 ô, d = MAE0 − MAE1 = 0,247036 điểm % C_ref. Giá trị này dương nhưng thấp
  hơn margin 0,25 khoảng 0,003. D trên tập eligible = 0,591, nên d đạt 41,8% mức tối đa có thể;
  SUPPORT cần 42,3%. MAE0 = 0,690 điểm %, lớn hơn ε_E = 0,5; MAE1 = 0,443, nhỏ hơn ε_E nhưng cùng bậc.
- **Claim (theo câu đã viết sẵn).** "H1 gần sự thật hơn H0 nhưng lợi thế nằm dưới margin đã
  khóa; d ∈ [0,247036; 0,247036]."
- **Evidence.** verdict.json, chấm bằng `score_test.score` và lặp lại độc lập.
- **Không được viết:** "gần như SUPPORT", "động học queue thêm sức dự báo", "H1 chính xác".
  d sát margin không đổi verdict. Margin được khóa trước để chặn đúng cách đọc đó.

## PC4 ngoại suy R11/R12 — FALSIFY

- **Fact.** d = −0,141751 điểm %. H0 gần sự thật hơn H1 một chút: MAE0 = 2,047, MAE1 = 2,188.
- **Claim.** "Trên R11/R12 (h = 12 s), H1 ở dạng đã khóa không dự báo tốt hơn H0."
- **Inference (không phải claim).** Cả hai mô hình sai khoảng 2 điểm %, gấp khoảng bốn lần ε_E,
  nên không có cơ sở nói "H0 đủ tốt". R11 có G_M = 3,82% và Γ = −3,02%, nhưng cả hai mô hình đều
  dự báo G_M = 0 và Γ > 0. FALSIFY là kết luận tương đối giữa hai mô hình.

## K5 — DOES_NOT_STAND (luật bị bác ở held-out)

- **Fact.** R03: G_M/C_ref = 0, STANDS, STANDS_HEADROOM_LIMITED (R00/C_ref = 0,339% < 0,5%,
  nên đứng là do headroom chặn). **R04: G_M/C_ref = 0,527926% > 0,5%**, DOES_NOT_STAND.
  Ở R04, a00 = Stay và a01 = Switch: sửa model lật quyết định. Không ô nào nhạy với dt.
  Gộp Kleene "mọi ô" cho DOES_NOT_STAND. Luật đầy đủ (K M19–M22 STANDS, Q STANDS, held-out K)
  là **DOES_NOT_STAND**.
- **Claim.** "Luật tọa độ K5 (κ ≥ 2, A/B q90, h = 8 s) bị bác ở R04 (κ = 2)." Claim ở mức danh
  sách M19–M22 từ A04 **không bị ảnh hưởng**. Không suy rộng sang κ khác hay η = 0,75 ở κ = 2.
- **Inference.** K5 có base rate heuristic khoảng 0,90 (không phải xác suất thật), nên việc
  luật thất bại mang nhiều thông tin hơn việc nó đứng. R04 vượt ngưỡng chỉ 0,028 điểm %;
  đó là sự thật về ô này, không phải lý do đổi ngưỡng.

## C1 — STANDS (khóa sau A04, bằng chứng yếu)

- **Fact.** R05–R08 đều STANDS ở dt cuối, không nhạy dt. G_M = 0 danh nghĩa ở cả bốn ô
  (a00 = a01). Headroom không chứng nhận: R00/C_ref từ 0,714% đến 1,447%, đều > 0,5%.
- **Claim.** "G_M/C_ref ≤ 0,5% đứng ở R05–R08", kèm base rate heuristic ≈ 0,81. Đây là luật
  hình thành **sau** khi thấy A04, nên đứng ở đây là bằng chứng yếu.
- Không claim G_M = 0 chính xác cho cả vùng tọa độ, không claim cơ chế.

## Chẩn đoán khai trước — DIAGNOSTIC_NOT_VERDICT

Các số dưới đây được tính cho mọi ô như đã khai ở DL-059, và không đổi verdict nào.

1. **Lợi thế của H1 dồn vào một ô.** R01 đóng góp 0,177 trên 0,247 điểm % của d (khoảng 72%).
   Các ô còn lại đóng góp từ −0,010 đến +0,053.
2. **Level hay shape.** Ở nhánh nội suy, sai số có dấu trung bình:
   - G_S: H0 −0,74, H1 −0,01;
   - Γ: H0 +1,01, H1 +0,36.

   Như vậy H0 đặt mức G_S quá thấp và Γ quá cao. MAE sau khi bỏ trung bình (shape-only) cũng
   nghiêng về H1 nhưng ít hơn nhiều:
   - G_S: 0,713 so với 0,634;
   - Γ: 0,362 so với 0,312;
   - G_M: 0,470 so với 0,355.

   Đúng như L3.7 đã cảnh báo, phần lớn chênh lệch nằm ở **mức**, phần hình dạng nhỏ hơn.
3. **Vị trí truth (24 cặp ô–contrast nội suy).** 10 cặp nằm ngoài phía H1 (H1 nhận điểm tối đa
   dù vẫn sai), 6 cặp nằm giữa hai dự báo, 6 cặp cắt qua một dự báo, 1 cặp ngoài phía H0, 1 cặp ngoài cả hai.
4. **Regime.**
   - a00 ≠ a01 ở R01, R04, R11: chỉ ba ô này có G_M > 0 (lần lượt 1,98; 0,53; 3,82%).
   - Γ thật âm ở R01 (−1,20) và R11 (−3,02). Ở 10 ô đã mở, không mô hình nào dự báo Γ âm.
   - H0 dự báo G_M = 0 ở mọi ô đã mở; H1 chỉ dự báo G_M > 0 ở R01 (0,61).
   - Ô duy nhất có R00/C_ref < 0,5%: R03 (0,339%).
   - p_sw của engine nằm trong khoảng p_2 công khai ở cả 10 ô.

## Deviations

**Không có deviation phân tích nào.** dt, margin, metric, trọng số, danh sách ô, mô hình và
cổng precision giữ nguyên; scorer chạy nguyên vẹn; run chạy đúng một lần, không retry.

Hai ghi chú quy trình, không phải deviation:
- Console được chép vào thư mục run sau khi chạy, nên nằm ngoài `output_hashes.json`.
- Kỳ vọng trước run của tác giả và người đọc thật trước A05-T, cả hai được khuyến nghị,
  đều không có.

## Không được claim

Network evidence; cơ chế (cần knockout ở Phase 6 và validation ở Phase 7); G2 hay nâng G-level;
"H1 dự báo đúng"; "H0 đủ tốt"; bất kỳ điều gì về R09/R10 hay trục h = 4 s; tần suất ngoài lưới
neo; long-run loss sau h; dùng 10 ô đã mở cho giả thuyết mới (việc đó thuộc Phase 5).

## Lệnh đã chạy

```bash
.venv/bin/python -m pytest -q --junitxml=/tmp/a05t_prerun/full_suite.xml     # 391 passed (trước run)
.venv/bin/python -c "from experiments.A05_test import run; run.preflight()"    # PASS, không engine
.venv/bin/python -u -m experiments.A05_test.run --workers 6                  # exit 0, 22,6 s
.venv/bin/python -m experiments.A05_test.rescore results/A05_test/20261028_01   # agreement PASS
```

## Output

[run](../../A05_test/20261028_01/) ·
[verdict](../../A05_test/20261028_01/verdict.json) ·
[diagnostics](../../A05_test/20261028_01/diagnostics.json) ·
[validity](../../A05_test/20261028_01/validity.csv) ·
[grading input](../../A05_test/20261028_01/grading_input.json) ·
[decision](../../../experiments/A05_test/decision.json) ·
[claim sheet](../../../notes/lessons/A05_T_claim_sheet.md) ·
[số đo máy đọc](verification.json).

## Ý nghĩa cho L3.8

| Nhánh | Kết quả | Ảnh hưởng tới Gate A (§18) |
|---|---|---|
| PC4 | Không SUPPORT | Không đạt điều kiện GO (a) |
| K5 | Equivalence boundary đóng băng bị bác | Không đạt điều kiện GO (b) |
| C1 | Đứng | Post-discovery và base rate cao, nên khó làm căn cứ GO |

**Nhãn Gate A là quyết định của tác giả ở L3.8; báo cáo này không chọn nhãn.**
Phase 4 vẫn HOLD tới P0-V10. L8, T05 author-writing và Understanding giữ OPEN.
