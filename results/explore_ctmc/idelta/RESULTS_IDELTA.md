# I_Δ — kết quả run01 (14/11/2026, giờ VM 13/11 23:53–23:55 UTC)

Doan Van Tai — **AI (Claude) soạn, chạy và đọc theo ủy quyền**. Exploration, không confirmation, không
author-self, không đổi RQ/contract/PC/Gate/G1. Thiết kế + dự đoán viết trước: [DESIGN_IDELTA.md](DESIGN_IDELTA.md)
(sha256 `a09e56f8…`, khớp lúc chạy và lúc chấm). Code: [idelta.py](../../../experiments/explore_ctmc/idelta.py),
test: [test_explore_idelta.py](../../../tests/test_explore_idelta.py) (8/8 PASS ở local và GCP).

**Run:** một lần trên `dt4n-research-01` (numpy 2.5.3, scipy 1.18.1, `env.sh`); ctmc.py giữ nguyên byte (`46bd482a…`).
9/9 regime COMPLETED, 36 dòng; Part F 0,77 CPU-s, Part C 365,7 CPU-s (trần 7.200). Chưa commit.

## 1. Chấm dự đoán (viết trước khi chạy)

| Mục | Kết quả | Số thực |
|---|---|---|
| P2 control số học | PASS | identity residual 3,4e−12; tower 5,9e−15; posterior 1,2e−13; Γ tự tính khớp engine **từng bit** |
| P3 biên trên/buffer | PASS | bỏ BN đổi E\|I_Δ\| tối đa 2,1e−12 tương đối |
| P4 fluid ngưỡng sắc | PASS | e = 0 chính xác (Fraction) ở mọi q ≥ t* (4,5 OFF; 3,9 ON), ≠ 0 ở 90/90 và 78/78 điểm dưới t* |
| P5 dấu khi rỗng, mode thấp | PASS 36/36 | e_B(0, thấp) < 0, e_A(0, thấp) > 0 |
| P6 dose–response | PASS 48/48 chấm được | 96/144 ô NOT_EVALUABLE vì vùng reach vượt bulk |
| **P1** E\|I_Δ\| ≥ 0,5% Cref và > \|Γ\| | **FAIL** | 19/36 dòng trượt, gần hết ở h ≥ 3 T_int |
| **P7** n_reach tăng theo h | **không chấm được** | 36/36 chuỗi có mức h mà reach vượt bulk (lỗi chọn ngưỡng 1e−6 của thiết kế) |
| D1 (mô tả) | đạt | \|Γ − Γ_add\| ≥ 0,25\|Γ\| ở 31/33 dòng (nhưng hướng lệch đổi theo h, xem §3) |

Không chỉnh dự đoán sau khi thấy kết quả. P7 ghi là chưa kiểm được, không phải PASS hay bằng chứng ngược.

## 2. Q2 — interaction tầng prediction có tồn tại không?

Có. Tính chính xác trên mọi cặp (y, x) của hai path:

| h/T_int | median E\|I_Δ\| (%Cref) | median E\|I_Δ\| (packet·s) | số dòng E\|I_Δ\| > \|Γ\| |
|---|---|---|---|
| 0,3 | 2,97 | 2,06 | 9/9 |
| 1 | 1,09 | 2,89 | 7/9 |
| 3 | 0,19 | 0,88 | 3/9 |
| 7 | 0,08 | 1,12 | 1/9 |

E|I_Δ| theo packet·s gần như bị chặn theo h, trong khi Cref ∝ h; vì vậy tỷ lệ theo %Cref giảm. Kết luận
"interaction tầng prediction lớn hơn Γ" của fluid A04 **không** mang sang CTMC ở h dài (P1 FAIL).

## 3. Q3 — cơ chế biên rỗng

**(a) Nguồn của sai số.** Ở mọi state, e = ΔC0 − μ·ΔI0 + ΔBN với residual ≤ 3,4e−12. Biên trên BN không đáng kể
(≤ 1e−7 packet·s trong bulk). Hai số hạng biên dưới đều lớn hơn e nhiều lần (|ΔC0| ≈ 1,8–32 lần |e| trên path B, có trọng số π)
và triệt tiêu gần hết. Sai số của M0 là phần dư giữa "đường mean bị cắt ở 0" và "idle thật ở 0", tức là Jensen gap
tại biên rỗng. Trong plant này đây là hệ quả toán học, không phải phát hiện về mạng thật.

**(b) "Rỗng hay có backlog" không phải biến đúng; biến đúng là "có thể chạm rỗng trong h hay không".**
- Fluid (P4): ngưỡng sắc t* = hD. Từ t* trở lên, đổi backlog B không làm I_Δ thay đổi chút nào. Dưới t*, sai số
  thậm chí đổi dấu (OFF: âm ở q ≤ 1, dương từ q ≥ 2).
- CTMC: không có ngưỡng sắc. e_B(n, thấp) tại n = 0 / q50 / q90 của π_B:
  - h = 0,3 T_int: thay đổi mạnh theo n (TP0079: −7,1 / −5,4 / +3,1 %Cref; TB0001 về +0,000 ở q99).
    Đây là chỗ I_Δ phụ thuộc backlog B.
  - h ≥ 3 T_int: gần như hằng (TN0003 7T: −21,7 / −21,9 / −22,2). Vì gần như mọi state trong bulk đều chạm
    được rỗng, biên tác động lên mọi state như nhau. Sai số thành **bias cộng tính**: I_Δ nhỏ, Γ vẫn lớn.

**(c) Ví dụ 2×2 (luật chọn của thiết kế), TN0003, h = 29,2 = T_int, y = (0, 0), x_A = (0, thấp), %Cref:**

| Pipeline | B rỗng (n_B = 0) | B backlog (n_B = 203, đuôi 1−1e−9) |
|---|---|---|
| 00 | −0,316 Switch | −0,316 Switch |
| 10 | **0,000 Stay** (hai queue rỗng: M0 thấy hai action giống hệt) | +63,301 Stay |
| 01 | −3,315 Switch | −3,315 Switch |
| 11 | −3,051 Switch | +47,965 Stay |
| I_Δ | −0,05 | −12,34 |

- Khi chỉ đổi B, I_Δ thay đổi đúng bằng −e_B(0, thấp) = +12,3% Cref.
- Mức I_Δ ở cột backlog lớn vì x_A đang rỗng (luật chọn của thiết kế cho y_A = 0), không phải vì B.
- Ở cột B rỗng: sửa State dưới M0 làm quyết định hỏng (Switch → Stay), dưới M1 thì không. Đây là pattern
  "fresher hurts M0" của Phase 7.

## 4. Nối sang Γ — có phải chỉ do ngưỡng không?

Γ_add = Γ của một M0 giả định có sai số **hằng** bằng bias trung bình. Khi đó I_Δ ≡ 0, nên mọi interaction còn lại
chỉ do ngưỡng.

| h/T_int | median \|Γ\| | median \|Γ_add\| | Γ_add < 0,25\|Γ\| | Γ_add ≥ 0,5\|Γ\| |
|---|---|---|---|---|
| 0,3 | 0,062 | 0,034 | 4/9 | 5/9 |
| 1 | 0,274 | 0,011 | 5/9 | 3/9 |
| 3 | 0,977 | 0,454 | 1/9 | 4/9 |
| 7 | 1,419 | 1,307 | 1/9 | 6/9 |

- **Quanh h ≈ T_int:** ở TN0003, TN0000, TP0079, TP0004 và TP0003, Γ_add ≈ 0 trong khi Γ = 0,19–0,45 pp. Interaction
  ở đây đến từ sai số phụ thuộc state, không chỉ từ ngưỡng.
- **Ở h ≥ 3 T_int:** M0 sai gần như cùng một lượng ở mọi state. Một model chỉ lệch hằng cũng sinh Γ cùng cỡ, có khi
  lớn hơn (TB0007 7T: Γ 2,61, Γ_add 5,60). Đây là đúng kịch bản "chỉ do ngưỡng" trong bảng ví dụ thứ nhất.
- **Gỡ từng path ở h = T_int** (chỉ thay phần phụ thuộc state của e_A hoặc e_B bằng hằng):
  - TP0079: Γ 0,452 → Γ_−B −0,048, Γ_−A 0,776 (biên của B quyết định);
  - TP0004: 0,338 → Γ_−B 0,005;
  - TN0000: 0,274 → Γ_−A 0,008, Γ_−B 0,504 (biên của A quyết định);
  - TN0003: cả hai đều cần.
  
  Đây là mô tả post-hoc trên 9 regime đã lộ, chưa phải quy luật.

## 5. Giới hạn

- Plant CTMC, a = 6, τ = 1, c_sw = 0; 9 regime Sobol của L7.5 (G_S/Γ đã lộ; I_Δ và counterfactual là mới).
  Không phải confirmation, không novelty.
- Ở plant này, "biên rỗng là nguồn duy nhất của sai số M0" là hệ quả của tuyến tính kỳ vọng. Thí nghiệm kiểm
  số học, vị trí, dấu, thang theo h và liên kết sang Γ. Nó không chứng minh cơ chế ở mạng thật. Muốn có bằng chứng
  độc lập cần plant hoặc trace có nguồn phi tuyến khác (drop ở buffer hữu hạn, cost có trọng số, multipath).
- Γ_add phụ thuộc lựa chọn b = E_π e. Đây là một counterfactual, không phải phân rã duy nhất. Γ_−A và Γ_−B không cộng tính.
- Ngưỡng reach 1e−6 và bulk 1−1e−9 khiến P6/P7 phần lớn không chấm được. Muốn kiểm thang theo h cần khai lại
  ngưỡng trước một run mới, không sửa trên run này.
- Phần đọc theo quantile π ở §3(b) và gỡ từng path ở §4 là mô tả sau khi thấy dữ liệu, tính từ file đã lưu.

## 6. File

`run01/`: `environment.json` (host, version, sha256), `fluid.json` (Part F), `regimes/<id>.json` (36 dòng),
`regimes/<id>_dose.csv` (cột: id, h, path, mode, n, e, ΔC0, −μΔI0, ΔBN, P_hit St, P_hit Sw, π),
`score.json`, `done.json`; log `results/explore_ctmc/logs/idelta_run01.log`.
