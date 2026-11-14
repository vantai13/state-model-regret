# Thiết kế lại "knockout CE": twin state cũ gộp posterior theo Bayes hay cắm trung bình (exploration)

Doan Van Tai — **AI (Claude) soạn theo ủy quyền** ("tự thiết kế và sửa lại làm sao cho hợp lí", 14/11/2026).
Exploration trên ctmc-v1 (a = 6, μ = 10, τ = 1, c_sw = 0). Không phải thẻ tác giả, không mentor review, không đổi
RQ/contract/PC/Gate/G1. File này viết **trước** mọi output của
[ce_knockout.py](../../../experiments/explore_ctmc/ce_knockout.py); sha256 của nó được ghi vào mọi output.

## 0. Đề xuất gốc và vì sao phải sửa

**Đề xuất (review AI ngoài, 14/11):**
- S0M0 theo contract tính chi phí fluid cho từng state rồi lấy trung bình qua posterior.
- Vì chi phí xả lồi theo backlog, cách này cộng thêm một khoản Var/(2r).
- Khoản đó có dạng giống chi phí dài hạn s mà fluid bỏ sót, nên đóng vai "hiệu chỉnh ngẫu nhiên ngầm".
- State tươi xóa khoản đó và sinh ra harm.
- Phép thử: thay S0M0 bằng twin CE cắm trung bình posterior của backlog và mode. Dự đoán harm co lại hoặc đổi dấu.

**Bốn vấn đề (phân tích của AI, đại số sơ cấp):**
- **F1. Jensen có ở cả hai phía.**
  - Theo tower property, E[Δ̂ | y] là trung bình của các gap twin tươi Δ̂(x) trên posterior. Truth cũng vậy: E[Δ | y].
  - Viết g_B = Bayes, g_PB = cắm backlog trung bình. Khi đó E[Δ̂|y] = Δ̂_PB(y) + Ĵ(y) và E[Δ|y] = Δ_PB(y) + J(y).
  - Sai số của twin cũ so với truth cũ là E[e | y] = e_PB(y) + K(y), với K = Ĵ − J là Jensen của **chính sai số** e.
  - Ĵ và J riêng lẻ không đi vào sai số. "Hiệu chỉnh ngầm" chỉ có thể đến từ K.
  - Toy của đề xuất có e ≡ 2,2 hằng nên K ≡ 0: twin cũ và twin tươi mang cùng bias. Harm ở toy là ngưỡng cộng gộp quyết định.
- **F2. CE thêm một sai số mới.**
  - Twin CE cũ sai lệch so với truth cũ một khoản E[e|y] − Ĵ(y).
  - Vì vậy "harm co dưới CE" có thể chỉ phản ánh việc CE tệ hơn Bayes. Ngay với model đúng, cắm kỳ vọng state cũng không tối ưu (R34 trong thư viện; CE nghĩa #2).
- **F3. Selection bias.** Knockout chỉ đổi ô L00, và dòng harm được chọn chính vì L00 thấp. Gần như mọi thay đổi ô đó đều làm harm "co".
- **F4. Trộn hai loại plug-in.** Đề xuất cắm cả backlog lẫn mode, nên không biết hiệu ứng đến từ đâu.

**Hai thí nghiệm phụ của đề xuất:**
- **P3** (hiệu chỉnh khuếch tán tường minh) đã có dưới tên hybrid M0 + h·s ([SUMMARY.md](../SUMMARY.md) §4). Nó gỡ được harm, nhưng không làm state tươi có giá trị ở h dài.
- **P2** (burst bất đối xứng) cần a/κ riêng cho từng path; ctmc-v1 không có. Hoãn.

## 1. Câu hỏi sau khi sửa

- **Q1 (cơ chế: bản mạnh nhất còn hợp lệ của đề xuất).** Jensen của sai số M0, K(y), có đủ lớn và cùng hướng với s để đóng vai hiệu chỉnh ngầm không?
- **Q2 (phạm vi thực tế).** Twin plug-in, kiểu twin phổ biến (Kalman mean, point estimate), có còn bị state tươi làm hại (C3) không?
- **Q3 (đối chứng).** Hiệu ứng plug-in trên M0 có tái tạo được bằng cùng plug-in trên:
  - (a) model đúng M1;
  - (b) surrogate bias hằng M0′ = Δ + b, với b = E_π e, là model không có sai số phụ thuộc state theo cấu trúc?

  Nếu (b) tái tạo được, hiệu ứng CE không cần cấu trúc riêng của M0.

## 2. Các nhánh (chỉ đổi ô state cũ; S1M0, S1M1 giữ nguyên)

| Nhánh | Gap state cũ, từng path | Vai trò |
|---|---|---|
| B | E_D[v(X) \| y] (contract) | tham chiếu |
| PB | Σ_m P(m\|y) · v(n̄(y), m); v tuyến tính giữa hai backlog nguyên | plug-in backlog, giữ Bayes theo mode (sạch nhất) |
| PX | như PB, nhưng rollout fluid đúng tại n̄ thực | kiểm số của phép nội suy (chỉ M0) |
| QM | rollout fluid tại n̄(y) và dấu mode 2p₁(y) − 1 | bản đúng nghĩa đen của đề xuất (chỉ M0, mô tả) |

Mỗi nhánh áp cho v = Δ̂ (M0), v = Δ (M1, đối chứng) và v = Δ + b (surrogate).

## 3. Đại lượng (theo %Cref, mỗi regime × h)

- P_M0 = L00^PB − L00; P_M1 = L01^PB − L01 (≥ 0 chính xác, vì L01 Bayes-tối ưu); P_sur tương tự trên surrogate.
- G_S^PB = L00^PB − L10 = G_S + P_M0. Đây là harm đối với twin plug-in.
- κ_CE = P_M0 / P_sur, chỉ đọc khi |P_sur| ≥ 0,05 pp.
- E|Ĵ|, E|J|, E|K|, E K, và khối lượng p(y) có dấu K trùng dấu s.

## 4. Hai cách đọc cạnh tranh

| | H_V (đề xuất, bản mạnh) | H_pool (đọc từ F1 và I_Δ vòng 3) |
|---|---|---|
| K ở h dài ngoài band | lớn so với Ĵ, cùng dấu s | nhỏ so với Ĵ |
| κ_CE ngoài band | xa 1 | ≈ 1 (surrogate tái tạo) |
| Nghĩa | M0 có hiệu chỉnh ngầm riêng | CE effect = plug-in + bias hằng + ngưỡng; contract chỉ là gộp Bayes |

Band (0 < x < 0,35): vòng 3 cho thấy cần sai số phụ thuộc state, nên ở đây K có thể lớn hơn. Phần band là exploratory.

## 5. Quy trình

1. Code và test (không có outcome).
2. **Hiệu chỉnh trên dữ liệu đã lộ:**
   - Dùng các panel I_Δ vòng 2 (`cases_fresh.json`, 45 regime) và vòng 3 (`cases_r3.json`, 40 regime).
   - G_S/Γ của chúng đã thấy; P_*, K và Ĵ chưa ai thấy.
   - Ngưỡng của thẻ chọn từ đây, kèm số hiệu chỉnh.
3. Thẻ `CARD_CE.md` + `lock_ce.json` (sha256), khóa trước panel mới.
4. **Panel mới và chấm:**
   - Panel: seed 20261116, cùng miền/Sobol/luật chi phí, 0 trùng với mọi case list cũ.
   - Chạy một lần, chấm theo thẻ, không chạy lại.
5. **Control:**
   - C1: L khớp engine ≤ 1e−7 pp.
   - C2: P_M1 ≥ −1e−9 pp.
   - C3: tower ≤ 1e−10.
   - C4: PB và PX phải cho cùng verdict, nếu không thì INCONCLUSIVE.

## 6. Không nhận

- Không novelty: CE/plug-in dưới thông tin cũ đã có prior (R34, CEH23; Bozkurt 2602.02814 mới ở mức abstract).
- Chỉ là plant mô phỏng.
- AI tự soạn, tự chấm.
- Không đổi contract: nhánh PB/QM là diagnostic giống cb0/D22. Contract v1.3 vẫn cấm rollout từ mean-state cho primary.
