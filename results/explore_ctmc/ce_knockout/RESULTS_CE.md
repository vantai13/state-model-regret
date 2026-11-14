# Knockout CE (bản đã sửa) — kết quả run01 (14/11/2026)

Doan Van Tai — **AI (Claude) soạn, khóa, chạy và chấm theo ủy quyền**. Tác giả chọn giữ nguyên ngưỡng AI: "chấp nhận,
chạy đi", status `LOCKED_AI_DELEGATED`. Đây không phải dự đoán do tác giả viết. Không mentor review, không đổi
RQ/contract/PC/Gate/G1.

- Thẻ: [CARD_CE.md](CARD_CE.md). Lock [lock_ce.json](lock_ce.json) gồm 6 file (design, card, predictions, panel, module, ctmc.py), khớp lúc chạy và lúc chấm.
- Một run local (host vantai, `env.sh`): 40/40 regime COMPLETED, 323,8 CPU-s, 47 s wall. Không chạy lại.
- Panel: 40 regime mới (seed 20261116), chấm trên 30 regime ngoài band.

## 1. Chấm

| Mục | Ngưỡng | Kết quả | Verdict |
|---|---|---|---|
| C1–C3 | L khớp engine ≤ 1e−7 pp; P_M1 ≥ −1e−9; tower ≤ 1e−10 | đạt | PASS |
| C4 | PB và PX cùng verdict | cùng verdict ở cả 4 mục (nội suy lệch fluid tối đa 0,66 pp) | PASS |
| **N1** (7 T_int) | NK giữ ≥ 0,9 harm, ≥ 90% vẫn harm | giữ **1,00** [1,00; 1,13]; 26/26 | **PASS** |
| N2 (T_int) | NK giữ ≥ 0,7, ≥ 90% | 0,89 [0,65; 0,96]; 14/15 (93%) | PASS |
| N3 (7 T_int) | E\|K\|/E\|Ĵ\| ≤ 0,15 | 0,043 (q90 0,10) | PASS |
| **P1** (7 T_int) | ≥ 90% vẫn harm dưới PB **và** QM; giữ PB ≥ 0,6, QM ≥ 0,5 | PB 26/26, giữ 0,88; **QM 23/26 = 88,5%**, giữ 0,79 | **FAIL** |

## 2. Đọc theo luật đã khai

- **N1 PASS.** Trong ctmc-v1, ở h dài, "hiệu chỉnh ngẫu nhiên ngầm" không phải cơ chế của harm.
  - Bỏ đúng phần đó (K) thì harm giữ nguyên ở mọi dòng.
  - Jensen của M0 và của truth gần bằng nhau (N3), nên sai số của twin cũ hầu như không đổi: E|E[e|y]|/E|e_PB| = 0,9999.
  - **Nhánh chính của đề xuất review bị bác ở plant này.** Theo luật của chính đề xuất, đi nhánh dự phòng: gộp quyết định cộng bias (C5/T11). Điều này khớp với I_Δ vòng 3 ("harm = ngưỡng + bias hằng").
- **N2 PASS.** Ở h ≈ T_int, K lớn (0,78 của Ĵ) nhưng vai trò nhỏ: bỏ K chỉ mất khoảng 11% harm (trung vị), và 14/15 dòng vẫn harm.
- **P1 FAIL.** Theo luật đã khai, C3 phải giới hạn cho twin gộp Bayes.
  - Thất bại đến **hoàn toàn từ QM** (bản đúng nghĩa đen của đề xuất, cắm cả backlog lẫn mode trung bình): 3/26 dòng harm đổi dấu.
  - Twin CE chỉ cắm backlog (PB) đạt mọi phần: 26/26, giữ 0,88.

## 3. Sau khi mở (mô tả, không đổi verdict)

- **Ba dòng đổi dấu dưới QM** đều thuộc stratum pos:

  | Dòng | x | G_S | G_S^QM |
  |---|---|---|---|
  | KP0021 | 0,41 | −0,97 | +0,23 |
  | KP0033 | 0,86 | −0,41 | +0,004 |
  | KP0038 | 0,44 | −0,14 | +0,022 |

  Hai dòng sau gần như hòa (≤ 0,022 pp). Chỉ KP0021 đổi dấu rõ.
- **Harm co dưới CE vì twin CE cũ tệ đi.** G_S^CE = G_S + P, với P = L00^CE − L00.
  - Trên 26/26 dòng harm, P_PB > 0 và P_QM > 0: twin CE cũ tệ hơn twin contract cũ. State tươi đáng giá hơn với twin CE chính vì twin đó khi dùng state cũ có thêm sai số plug-in, đúng như F2.
  - Ngược lại, bỏ K (NK) làm twin cũ tốt hơn ở 9 dòng, tệ hơn ở 11, không đổi ở 6. K không phải một hiệu chỉnh có hướng.
  - Cắm mode trung bình vào rollout fluid tạo sai số lớn hơn cắm backlog: trung vị G_S theo nhánh B / PB / QM là −0,98 / −0,81 / −0,39.
- **Model đúng gần như không bị plug-in làm hại** (P_M1 trung vị 1e−7 pp). Sai số plug-in chỉ quan trọng khi gap cũ nằm gần ngưỡng, mà đó là trường hợp của twin có bias.
- **Band** (exploratory, 10 regime): ở 7 T_int chỉ có 1 dòng harm. Trung vị G_S tăng 0,13 → 0,50 dưới PB và QM, nghĩa là twin CE được lợi nhiều hơn từ state tươi.

## 4. So với dữ liệu hiệu chỉnh

N1/N2/N3 lặp lại gần như cùng số (NK giữ 1,00 → 1,00; K/Ĵ 0,034 → 0,043). P1 hiệu chỉnh 39/39 cho QM, nay còn 23/26.
QM có đuôi dưới dài ngay từ hiệu chỉnh (q10 của tỷ lệ giữ là 0,23), nên ngưỡng 90% cho QM là quá chặt so với đuôi đó.
Đây là lỗi chọn ngưỡng của AI. Ghi nhận, không sửa sau khi chạy.

## 5. Giới hạn

- Chỉ ctmc-v1 (a = 6, τ = 1, c_sw = 0); chưa kiểm plant fluid.
- Ngưỡng do AI chọn từ dữ liệu đã lộ; AI tự chấm; một run.
- "Dòng harm" được chọn theo outcome của ô L00 (bias làm harm dễ co, nên N1 PASS là bảo thủ).
- K đo bằng plug-in backlog với nội suy tuyến tính. QM chỉ có cho M0.
- Không novelty: CE dưới thông tin cũ đã có prior (R34, CEH23).

## 6. File

- `run01/`: `environment.json` (lock, version), `regimes/<id>.json`, `score.json`, `done.json`.
- Log: `results/explore_ctmc/logs/ce_run01.log`.
- Hiệu chỉnh: [CALIBRATION_CE.md](CALIBRATION_CE.md), `calibration_ce.json`, `calib_pass1/`, `calib/`.
