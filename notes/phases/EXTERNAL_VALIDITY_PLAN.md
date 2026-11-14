# Kế hoạch external validity (Phase 7 independent validation + Phase 8 practical relevance), bản nháp 14/11/2026

Doan Van Tai — **AI (Claude) soạn theo yêu cầu** ("giải thích kỹ phần này và lên plan chạy cho tôi"). Đây là kế hoạch,
chưa chạy gì. Mục tiêu tác giả: bài Q1 journal hoặc hội nghị A*/A. Không đổi MainRQ/contract/PC/Gate. Mọi thẻ dự đoán ở
đây còn để ngỏ phần ngưỡng; tác giả nên tự viết, hoặc duyệt rõ từng thẻ.

## Phạm vi đã rút gọn (14/11, sau complexity audit; bản này thay mục 1 ở các chỗ khác nhau)

| Stage | Mức | Vì sao giữ hoặc bỏ | Ai làm, ở đâu |
|---|---|---|---|
| EV-A vòng kín | MUST | Reviewer chắc chắn hỏi K4. Claim C1/C3 có thể vỡ | Codex code; VM chính (8 vCPU) |
| EV-B khởi đầu sau alarm | SHOULD | K5 có thể đổi tỷ lệ harm. Tính chính xác, rẻ | Claude, local |
| EV-E các loại twin | SHOULD | Biến K2 thành kết quả. Static/hybrid đã có trong output, nên chỉ phân tích lại | Claude, local |
| EV-C simulator độc lập riêng | **gộp vào EV-D** | Evaluator đã được MC kiểm nhiều lần; simulator chỉ cần làm nền cho EV-D | — |
| EV-D traffic thực tế | MUST (venue networking) | E2/E5; câu P8. Trace thật cần tác giả duyệt nguồn | Codex code; clone 4 vCPU hoặc local |
| EV-F nhiều path | OPTIONAL (bỏ) | Chỉ làm nếu reviewer hỏi | — |
| Twin ML (EV-E) | OPTIONAL | Gần như hệ quả của hybrid; làm nếu còn thời gian | — |

**Giới hạn GCP:**
- CPUS_ALL_REGIONS = 12: VM chính 8 vCPU cộng tối đa một clone 4 vCPU cùng lúc.
- SSD còn 50 GB, nên clone dùng pd-balanced.

**Stop rule mỗi stage:** dừng khi dự đoán khóa trước đã được chấm và đọc được (PASS/FAIL có nguyên nhân). Không thêm kiểm tra chỉ để tăng độ chắc của máy móc.

## 0. Vấn đề trong một câu

Mọi claim hiện có (C1–C6, M1–M8) đúng **trong ctmc-v1**. Plant đó gồm hai path MMPP/M/1, một quyết định giữ suốt h,
khởi đầu dừng, state quan sát chính xác τ giây trước, và twin là rollout trung bình. Reviewer sẽ hỏi claim nào còn
đứng khi bỏ từng giả định.

| Giả định | THREATS | Claim có thể vỡ | Vì sao có thể vỡ |
|---|---|---|---|
| Một quyết định giữ suốt h (open loop) | K4 | C1, C3, M4 | Hệ thật quyết định lại mỗi Δ. Một quyết định sai chỉ trả giá khoảng Δ, và action thay đổi chính phân phối state (feedback) |
| Twin = rollout trung bình mù horizon | K2 | C3, M4 | Twin thật có nhiều loại; loại steady-state không dùng state, loại packet-level gần M1 |
| Khởi đầu dừng (P1) | K5 | C3 (tỷ lệ) | Quyết định thật thường đến sau sự kiện (alarm, burst) |
| MMPP hai mode đối xứng, exponential | E2, E5 | C1 (dạng luật), C6 | Traffic thật bất đối xứng, heavy-tail, đa thang, có chu kỳ |
| Hai path rời, buffer vô hạn | E1 | phạm vi | Link chung, nhiều path, buffer hữu hạn |
| Use case nằm ở đâu trên trục h/T_int | E4 | ý nghĩa thực tế | Không biết thì không nói được harm có xảy ra ngoài đời không |

## 1. Các stage

Thứ tự theo giá trị trên chi phí. Ước tính thời gian là của AI và sẽ đo lại.

### EV-A: vòng kín / quyết định lại (K4). Ưu tiên 1

- **Câu hỏi.** Khi controller quyết định lại mỗi Δ, với twin nhìn trước h_p, harm của state tươi còn không? Luật nào dự đoán nó?
- **Mô hình.**
  - Hai đồng hồ: chu kỳ quyết định Δ và tầm nhìn của planner h_p. One-shot hiện tại là đường chéo h_p = Δ.
  - Planner vẫn dùng gap một lần của M0 hoặc M1 (tầm nhìn h_p), chỉ giữ action trong Δ.
  - Twin cũ dùng posterior cố định: phân phối dừng của action trước, đẩy qua τ. Đây là giả định của twin, ghi rõ.
- **Tính chính xác.**
  - Chuỗi Markov tại các thời điểm quyết định, trên (state hai path, action trước).
  - Hai path độc lập khi biết action, nên π_{k+1} = Σ_a E_A(a)ᵀ (M_a ∘ π_k) E_B(a), với ma trận dày e^{QΔ} từng path.
  - Không có nhiễu MC. Giới hạn N ≤ khoảng 500 mỗi path.
  - Kiểm chéo bằng MC vòng kín (CRN) trên vài regime.
- **Dự đoán zero-fit (trước truth).**
  - Khi Δ ≥ 4 T_int, các epoch gần độc lập. Tốc độ harm theo luật bậc một với h → Δ: [Δ·s·ΔF(h_p) + B]/Δ, trong đó ΔF tính trên phân phối do policy sinh ra.
  - Khi Δ ≪ T_int, feedback chi phối và không có dự đoán. Phần này là bản đồ khám phá.
- **Sản phẩm.** Bản đồ harm trên mặt phẳng (Δ/T_int, h_p/T_int), và luật đúng ở vùng nào.
- **Chi phí.** Khoảng 1–2 ngày code. Chạy khoảng 10–20 CPU-h (30 regime × 4 Δ × 3 h_p × 4 pipeline), GCP hoặc local qua đêm.

### EV-B: khởi đầu sau sự kiện và telemetry không hoàn hảo (K5, một phần E4). Rẻ

- Phân phối đầu bị điều kiện hóa trên alarm (backlog ≥ ngưỡng), tức P2a/P2b của contract làm diagnostic. Tính chính xác.
- Telemetry có nhiễu: backlog đếm thưa (binomial thinning) hoặc có sai số, tính chính xác. Trung bình theo cửa sổ thì dùng MC.
- **Dự đoán:** luật bậc một với trọng số điều kiện. Harm tăng hay giảm theo hướng luật nói.
- **Chi phí:** khoảng 1 ngày, vài CPU-h.

### EV-C: implementation độc lập packet-level (P7 "independent"). Điều kiện cho EV-D

- Bộ mô phỏng gói riêng: Lindley/FIFO, arrival theo sự kiện, CRN giữa hai action. Không dùng `ctmc.py`.
- Đầu tiên tái lập ctmc-v1 bằng arrival MMPP. G_S, z_pred1 và harm phải khớp exact trong sai số MC.
- Sau đó thay arrival và service: kích thước gói, service không exponential.
- **Chi phí:** khoảng 2 ngày, vài CPU-h.
- **Mạnh hơn nữa:** một người khác (mentor hoặc bạn) chạy lại từ README. Đó là L8/P7 đúng nghĩa.

### EV-D: traffic thực tế hoặc trace (E2, E5, E4). Ưu tiên 2

- **Bước 1 (không cần dữ liệu ngoài):** ON/OFF heavy-tail bất đối xứng.
  - Tham số lấy từ nguồn đã có trong repo: GZL22 ON khoảng 2 ms / OFF khoảng 133 ms; BAAZ09 lognormal.
  - Chồng nhiều nguồn để có đa thang / self-similar.
- **Bước 2 (cần tác giả duyệt nguồn dữ liệu):** trace DC hoặc backbone công khai, chỉ dùng làm quá trình arrival.
- **Twin:** fluid với tốc độ ước lượng EWMA, không có mode, giống twin thật.
  - G_S = E[(a00 − a10)·D] chỉ cần quyết định của twin và chi phí thực, nên **không cần biết model đúng**.
- **Dự đoán zero-fit:**
  - z_pred1 lấy s và F_old/F_new từ đoạn train của trace, rồi chấm trên đoạn test.
  - T_int đo từ trace ở tải cho trước, để đặt use case (i)–(iii) lên trục h/T_int.
- **Sản phẩm:**
  - Luật còn đúng với traffic không-Markov không.
  - Harm có ở use case thật không: đây là câu P8.
- **Chi phí:** khoảng 3–5 ngày, cộng thời gian lấy dữ liệu.

### EV-E: các loại twin (K2). Ưu tiên 3

- **Bốn loại twin:**
  - steady-state (công thức queue hoặc kiểu GNN steady-state, tức Static);
  - fluid mù horizon (M0);
  - hybrid M0 + h·s, với s đo từ phân phối dừng;
  - twin học máy (hồi quy chi phí theo state, train trên dữ liệu mô phỏng).
- **Dự đoán từ cơ chế:** harm chỉ cần (dùng state) và (bias gần hằng ở h dài).
  - Steady-state: G_S ≈ 0.
  - Hybrid: harm biến mất.
  - ML: harm tỷ lệ với bias trung bình còn lại.
- Biến câu hỏi "twin thật có mù horizon không?" thành một kết quả: bản đồ loại twin → dấu G_S.
- **Chi phí:** khoảng 2 ngày, ít CPU.

### EV-F: nhiều path / link chung (E1). Tùy chọn

- k > 2 path, hoặc một bottleneck chung.
- Chỉ làm nếu venue đòi, hoặc reviewer hỏi.

## 2. Song song: literature (theo protocol, tối đa 3 nguồn mỗi đợt, tác giả duyệt)

1. Twin NDT thật thuộc loại nào: fluid hay flow-level, steady-state/GNN, packet-level. Cần nguồn primary.
2. Chu kỳ quyết định Δ và tầm nhìn h_p của controller có dùng twin.
3. Prior gần nhất cho vòng kín: re-solving với bias, MPC với state cũ, stochastic/cautious control.

## 3. Thứ tự và điểm quyết định

```
Gate P7 (tác giả chấm)
EV-A ──► EV-B ──► EV-C ──► EV-D bước 1 ──► [tác giả duyệt trace] ──► EV-D bước 2 ──► EV-E ──► (EV-F)
   └─ literature đợt 1 (song song)
```

- Sau EV-A: nếu harm biến mất trong vòng kín ở mọi Δ thực tế, câu chuyện đổi trọng tâm sang "khi nào vòng kín cứu twin". Tác giả quyết.
- Sau EV-D: nếu use case thật nằm ngoài vùng harm, paper là phân tích cơ chế cộng điều kiện thiết kế, không phải cảnh báo thực tế.

## 4. Không nhận

Đây là kế hoạch AI soạn, chưa có truth. Ước tính chi phí chưa đo. Venue nào đòi bao nhiêu external validity là đánh giá
của AI, không phải quy định của venue.
