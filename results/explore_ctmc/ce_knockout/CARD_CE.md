# Thẻ "knockout CE" đã sửa — KHÓA theo ủy quyền (14/11/2026)

Doan Van Tai — **AI (Claude) soạn theo ủy quyền** (14/11/2026).
- Các ngưỡng do AI đề xuất từ [hiệu chỉnh](CALIBRATION_CE.md) và nằm trong [predictions_ce.json](predictions_ce.json) (status `DRAFT_AI`).
- Tác giả có thể thay bất kỳ số nào trước khi khóa.
- Exploration, không mentor review, không đổi RQ/contract/PC/Gate/G1. Thiết kế: [DESIGN_CE.md](DESIGN_CE.md).

## 1. Mệnh đề

Đề xuất review ngoài cho rằng harm xuất hiện vì state cũ là "hiệu chỉnh ngẫu nhiên ngầm". Theo design §0 F1, chỉ
K = Jensen của chính sai số M0 mới có thể đóng vai đó. Twin cũ theo contract mang thêm K so với twin plug-in-có-Jensen-đúng
(nhánh NK).

**H_pool (AI):** trong ctmc-v1:
- harm của state tươi không cần K;
- harm vẫn còn khi twin cũ cắm trung bình posterior (twin CE, kiểu twin phổ biến).

## 2. Panel (write-once, đã tạo trước khóa)

- [cases_ce.json](cases_ce.json): 40 regime mới, seed 20261116 (neg 15, band 10, pos 15).
- Cùng miền, Sobol và luật chi phí như I_Δ vòng 3.
- 0 trùng với mọi case list cũ (test `test_ce_panel_is_new`).
- h = {0,3; 1; 3; 7} × T_int_max.
- Chấm trên 30 regime ngoài band; band là exploratory.

## 3. Dự đoán

Quy ước:
- "Dòng harm" là G_S < −0,05 pp.
- "Giữ" là G_S^nhánh / G_S, tính trên các dòng harm.
- Số trong ngoặc là giá trị trên dữ liệu hiệu chỉnh.

| ID | Vai trò | h | Ngưỡng |
|---|---|---|---|
| **N1** | quyết định câu cơ chế | 7 T_int | NK: trung vị giữ ≥ 0,9 **và** ≥ 90% dòng harm vẫn harm (1,00; 39/39) |
| N2 | cùng câu ở h ngắn, nơi K lớn | T_int | NK: trung vị giữ ≥ 0,7 **và** ≥ 90% (0,89; 27/27) |
| N3 | K nhỏ ở h dài | 7 T_int | trung vị E\|K\|/E\|Ĵ\| ≤ 0,15 (0,034) |
| **P1** | phạm vi: twin CE | 7 T_int | ≥ 90% dòng harm vẫn harm dưới PB **và** QM; trung vị giữ PB ≥ 0,6, QM ≥ 0,5 (0,89 / 0,80; 39/39) |

**Control và luật:**
- C1: L khớp engine ≤ 1e−7 pp.
- C2: P_M1 ≥ −1e−9 pp.
- C3: tower ≤ 1e−10.
- C4: PB và PX phải cho cùng verdict, nếu không thì INCONCLUSIVE.
- Dưới 90% regime COMPLETED: INCONCLUSIVE.
- Dưới 6 dòng harm: NOT_EVALUABLE.
- Không đổi ngưỡng sau khi chạy, không chạy lại.

## 4. Cách đọc

| Kết quả | Nghĩa |
|---|---|
| N1 PASS | Ở h dài, "hiệu chỉnh ngầm" không phải cơ chế của harm. Nhánh chính của đề xuất bị bác; đi nhánh dự phòng (gộp quyết định + bias, C5/T11) |
| N1 FAIL | Bỏ K làm harm co: đề xuất có ủng hộ ở h dài |
| N2 | Cùng câu hỏi ở h ≈ T_int. FAIL nghĩa là K đóng vai đáng kể ở h ngắn |
| P1 PASS | Harm C3 không phải artefact của cách gộp Bayes trong contract; twin CE cũng bị hại (chỉ trong ctmc-v1) |
| P1 FAIL | Harm phụ thuộc cách twin gộp bất định; C3 phải giới hạn cho twin gộp Bayes |

## 5. Không nhận và giới hạn

- Chọn "dòng harm" theo outcome của ô L00. Bias này làm harm *dễ co hơn* dưới mọi nhánh, nên PASS của N1/P1 là bảo thủ, còn FAIL cần đọc thận trọng.
- K đo bằng plug-in backlog với nội suy tuyến tính.
- QM là bản đúng nghĩa đen của đề xuất, chỉ cho M0.
- Không novelty (R34, CEH23, Bozkurt). Chỉ plant mô phỏng. AI soạn và tự chấm.

## 6. Khóa và chạy

Tác giả chọn (b) ngày 14/11/2026 ("chấp nhận, chạy đi"): giữ nguyên ngưỡng AI, status `LOCKED_AI_DELEGATED`. Đây
**không** phải dự đoán do tác giả viết. Các lựa chọn ban đầu:

- (a) Tác giả tự ghi số của mình vào `predictions_ce.json` và đặt status `LOCKED_AUTHOR`; hoặc
- (b) chấp nhận bản AI, đặt status `LOCKED_AI_DELEGATED`.

Sau đó chạy một lần:

```
python -m experiments.explore_ctmc.ce_knockout lock
python -m experiments.explore_ctmc.ce_knockout run --out results/explore_ctmc/ce_knockout/run01
python -m experiments.explore_ctmc.ce_knockout score --out results/explore_ctmc/ce_knockout/run01
```

Ước tính khoảng 2 phút wall ở local, 10 nhân.
