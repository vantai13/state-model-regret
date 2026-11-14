# External validity — Wave 1 report (EV-A, EV-B, EV-D, EV-E), 14/11/2026

Doan Van Tai — **AI (Claude) điều phối, Codex viết code** theo ủy quyền "full quyền" của tác giả.
- Mọi thẻ đều `LOCKED_AI_DELEGATED`: dự đoán là số máy tính hoặc ngưỡng AI chọn, không có dự đoán do tác giả viết, không mentor review.
- Exploration/external-validity. Không đổi MainRQ/contract/PC/Gate/G1.
- Nhánh `ext/validity` (không phải main).

## Tóm tắt

| Stage | Câu hỏi (THREATS) | Panel | Kết quả theo thẻ khóa | Ý nghĩa |
|---|---|---|---|---|
| **EV-A** vòng kín | K4: quyết định lại mỗi Δ | 60 regime ctmc mới × 7 (Δ, h_p); 420 job, 6,2 CPU-h trên GCP | **A1 PASS 180/180**: luật bậc một vòng kín, zero-fit, khớp mọi ô Δ ≥ 3 T_int. **A2 PASS 40/40** (dấu) | Harm bền trong vòng kín: 32/32 regime có harm one-shot vẫn có harm ở Δ = 10 T_int |
| EV-A (mô tả) | Δ nhỏ | cùng panel | Trung vị G_S (neg/pos): −0,86/−0,91 (Δ = 10 T_int) → +0,30/+0,39 (Δ = ½ T_int). Luật vẫn đúng dấu ~80% ở Δ ≤ T_int. Tầm nhìn h_p gần như không ảnh hưởng | **Quyết định lại thường xuyên (Δ ≲ T_int) đảo dấu:** state tươi giúp |
| **EV-B** alarm | K5: quyết định sau sự kiện | 30 regime mới, alarm q90 trên path A | **B1 PASS 30/30, B2 PASS 10/10**. Harm ở thời điểm ngẫu nhiên: 18 regime → dưới alarm: **0/18** | Lúc quyết định (trigger) đổi dấu giá trị telemetry |
| EV-B lặp lại | ngưỡng alarm | 30 regime mới khác, q75 và q95 | Luật R1 30/30, R2 PASS ở cả hai. Đảo dấu R3: **PASS ở q95 (0/18)**, **FAIL ở q75 (4/18 = 22% > 20%)** | Đảo dấu tăng theo độ gắt của alarm; luật dự đoán đúng từng dòng |
| EV-E loại twin (mô tả) | K2 | panel EV-B | Fluid M0: harm 15/20 ở 10 T_int. M0 + margin: 7/20, nhỏ. **M0 + h·s (cả công thức M/M/1): 0/20, regret ≈ 0**. Static: 0. KO: không harm nhưng regret 12% | Sửa fluid twin bằng một công thức hàng đợi đơn giản là xóa được harm |
| **EV-D** traffic thực tế | E2/E5, P7 | Simulator gói độc lập; 20 regime × {MMPP, ON/OFF exp, ON/OFF Pareto α = 1,5}; train/test tách seed | **D1 PASS 116/120**: twin plug-in không có harm dài hạn. **D2 PASS 61/64**: twin nowcast đúng dấu theo luật. **D3 PASS 120/120**: độ lớn. **D4 PASS 120/120**: hybrid xóa harm | Cơ chế chuyển sang traffic không Markov, kể cả heavy-tail |

## Phát hiện có thể nâng novelty (đề xuất, chưa kiểm novelty)

1. **Luật bậc một cho vòng kín** (zero-fit, Poisson analogue của T11):

   J ≈ Σ_b P(b)·[(1 − q_b)·r_St + q_b·r_Sw + E_b(g)/Δ]

   Nó dự đoán đúng tốc độ harm khi Δ ≥ 3 T_int, trước truth (180/180).
2. **Ba "núm" quyết định dấu của giá trị telemetry tươi:**
   - đồng hồ Δ/T_int (hoặc h/T_int);
   - trigger: thời điểm ngẫu nhiên so với alarm;
   - cách twin xử lý dữ liệu cũ: plug-in so với age-aware.
3. **T12** ([notes/theory/T12_plugin_stationarity.md](../../notes/theory/T12_plugin_stationarity.md)): dưới tính dừng, pipeline plug-in có F_old = F_new, nên không thể có harm tăng theo h. Harm cần bất đối xứng giữa xử lý dữ liệu cũ và mới. EV-D xác nhận trên ba lớp traffic.

**Mức (thang của prompt exploration):**
- Luật vòng kín: **Tốt**. Có cơ chế và công thức; dự đoán khóa trước đạt trên điều kiện mới. Chưa có literature hay tác giả tự suy ra.
- T12 + EV-D: **Tốt**.
- Đảo dấu theo Δ: **Ổn**. Luật đã dự đoán hướng trước truth, nhưng ở Δ nhỏ chỉ là mô tả, chưa có thẻ riêng.

## Sai lệch và lỗi (giữ nguyên hồ sơ)

- **EV-A:** lệnh launch của Codex (`ssh -n -f` trong sandbox) không tới VM. Claude launch lại bằng `setsid` phía remote; code và hash không đổi.
- **EV-B R3 (q75) FAIL:** ngưỡng 20% do AI đặt; báo nguyên.
- **EV-D, trước khóa:**
  - pilot phát hiện ŝ_train ước lượng không CRN rất nhiễu (P0: −0,22 so với exact −1,00). Đã sửa sang CRN và thêm test so exact;
  - nới một test R² so từng bit;
  - thêm h = 30 T_int và `spacing_mult`.
- **EV-D, sau khóa:**
  - lần chạy test đầu ở local vỡ vì OOM (73/180). 107 job còn lại chạy tiếp trên GCP 48 GB, cùng code và seed theo (case, h);
  - lần chạy tiếp đầu tiên vỡ do script của Claude thiếu `__main__` guard. Đây là lỗi thực thi, không phải kết quả.
- **Hạ tầng:** VM chính đổi sang n2-custom-12 vCPU (quota 12 vCPU toàn tài khoản). Đã tắt sau khi chạy.

## Giới hạn

- ctmc-v1 / simulator gói hai path rời; quyết định one-shot hoặc vòng kín với c_sw = 0.
- Traffic tổng hợp (chưa trace thật).
- Twin nowcast là hồi quy tuyến tính.
- AI thiết kế và tự chấm (dự đoán chủ yếu là số máy tính).
- Chưa literature cho vòng kín / event-triggered / nowcast. Không novelty.

## Việc cần tác giả quyết (wave 2)

1. **Nguồn trace thật** cho EV-D bước 2 (DC hoặc backbone công khai): cần duyệt.
2. **Literature**, đợt tối đa 3 nguồn theo protocol: prior gần nhất cho vòng kín với state cũ (MPC/re-solving), event-triggered control, nowcasting twin.
3. **Thẻ xác nhận** cho đảo dấu theo Δ: dự đoán Δ* zero-fit trên panel mới. AI có thể soạn; khuyến nghị tác giả viết một câu dự đoán.
4. Tự kiểm phép dẫn T12 và luật vòng kín; nhãn C5/K7.

## File

- `results/ext_validity/ev_a/` (CARD, predictions, run01, score, table)
- `ev_b/`, `ev_b_rep/`, `ev_d/` (CARD, train, test, predictions, score)
- `ev_e_twin_classes.csv`
- Code ở `experiments/ext_validity/`; brief Codex ở `notes/ops/codex/`.

## Đính chính sau audit độc lập (14/11/2026, DL-146)

Codex tính lại mọi verdict từ dữ liệu thô bằng script riêng, không import code chấm: tất cả khớp. Các con số dưới đây được sửa theo mục C của `notes/ops/codex/AUDIT_report.md`:
- **Đảo dấu khi Δ ≤ T_int:** dấu ngược ở **181/240 = 75,4%** hàng Δ ≤ T, không phải "~80%". Các trung vị −0,86/−0,91 → +0,30/+0,39 chỉ đúng trên đường chéo Δ = h_p. Nếu giữ h_p = 10T thì trung vị tại Δ = T vẫn âm (−0,018/−0,091%). Không được nói toàn bộ vùng Δ ≤ T đảo dấu.
- **EV-B:** con số 15/20 và KO ≈ 12% tính trên neg + pos, bỏ band. Trên toàn panel: M0 harm 18/30, regret trung vị của KO 8,68%. Hybrid có 0 harm ở cả hai cách tính.
- **EV-D:** `ev_d/score.json` không tồn tại. Codex tính lại D1–D4 đều khớp report (116/120, 61/64, 120/120, 120/120).
- **EV-B, mô hình alarm:** quần thể alarm là occupancy dừng có điều kiện "backlog cũ ≥ ngưỡng". Mô hình này không có first passage, không có hysteresis và không có retrigger. Kết quả EV-B chưa đại diện cho mọi controller kích hoạt theo sự kiện, vì quần thể khác có thể đổi dấu (toy của audit: +1 so với −1).
