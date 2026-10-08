# Research contract v0 — `notes/01_definitions.md`

Tác giả: **Doan Van Tai** · Ngày bổ sung: **08/10/2026**.

> **Nguồn gốc.** Bản v0 tích hợp đủ ba phần nội dung tác giả cung cấp ngày 08/10/2026; hướng dẫn dẫn nguồn L0.3–L0.6, master plan Part II và Final Review §2, §5, §11. File 8 đã bổ sung khung lesson L0.3–L0.7, nhưng chưa có bài tự làm; master plan đầy đủ còn thiếu để đối chiếu. Final Review gốc đã được kiểm digest và đối chiếu kỹ thuật ở §10; việc đó không thay record tác giả tự kiểm. Bản này **chưa** qua người đọc độc lập.
> **Mức hoàn thiện.** Đủ nội dung Phần 1–3/3 và năm sửa đổi DL-010; bản kỹ thuật đóng băng tại `contract-v0` theo [closeout B](phases/PHASE_0_closeout.md), ngày 08/10/2026. DRAFT/OPEN bên trong giữ nguyên; V3/V10/V11 và tự kiểm của tác giả còn mở. Đóng băng snapshot không thay phê duyệt độc lập.
> **Trạng thái.** LOCKED = nguyên tắc, đổi phải có DL entry và tăng phiên bản. DRAFT = mặc định hiện tại. OPEN = còn mở, có nơi quyết (§9). Nhãn từng nguyên tắc không có nghĩa toàn bộ contract đã được chốt.
> **Ngân sách.** 25 term (giới hạn khoảng 25), hiện có 25/25. Ký hiệu timescale ($T_{\text{drain}}$, $\tau_{\text{eff}}$, $d_{\text{act}}$) định nghĩa ở [T00](theory/T00_timescale_sanity.md); $I_\Delta$ hoãn tới L1.5. Con số cụ thể ($\Delta t$, $H$, $u$, $c$, tham số Markov, $\varepsilon_R$, $\varepsilon_E$) khoá ở L1.8, thành contract v1.
> **Sửa đổi theo [DL-010](02_decision_log.md) (08/10/2026).** Năm sửa đổi bắt buộc của review chuyển phase đã đưa vào: ngữ nghĩa slot và objective (D1, D13, ghi chú dưới bảng §2); phạm vi model repair (§0, D21, §5); quy tắc chống chỉnh timescale (§6 quy tắc 7); null bảo toàn (§6 quy tắc 8, §7g, §7h); quy tắc cheap kill (§7f). Các mục §7 mới là E0 — hệ quả của thiết kế, không phải phát hiện. Không thêm term D; vẫn 25/25.

Contract quy định thế giới, phép đo, đối tượng so sánh và quyền thông tin trước khi có số liệu. Từ Phase 3, code và thí nghiệm phải khớp contract; thay đổi phải được ghi bằng phiên bản và decision-log entry, không lặng lẽ đổi khi triển khai.

## 0. Contract này phục vụ câu hỏi nào

**Main RQ** (nguyên văn, Final Review cập nhật 06/10/2026): *For load-changing routing actions, how do improvements in current-state information and action-response model fidelity differ and interact in their effect on expected decision regret?*

| Sub-RQ | Loại câu trả lời | Đại lượng trả lời nó (D19, §4) |
|---|---|---|
| RQ1 Characterization | Bản đồ có điều kiện | $G_S, G_M, G_{SM}, \Gamma$, gain có điều kiện, theo toạ độ quan sát được trước action |
| RQ2 Mechanism/falsification | Giải thích có thể bị bác | Sai số dự báo gain của threshold null $H_0$ đóng băng so với $H_1$, trên held-out |
| RQ3 Practical relevance | Đáng hay không đáng | Gain của repair khả thi trừ chi phí, so với $\varepsilon_R$ và baseline mạnh |

RQ1 chia kết quả theo toạ độ controller quan sát được trước action, ví dụ tuổi thông tin hoặc backlog đã đo. Không dùng mode thật chỉ simulator biết làm toạ độ chính của bản đồ này; hệ quả được trình bày ở §7c trong Phần 2.

Đối chiếu câu hỏi với [RQ card L0.2](lessons/L0.2_rq_card.md) và [Final Review reading note](verification/final_review_reading_note.md). D19 và estimand card nằm ở §2/§4; $H_0/H_1$ được định nghĩa ở D25, đặc tả tại A05 trước Phase 4. Chưa có kết quả xác nhận RQ2 hoặc RQ3.

**Phạm vi của “model fidelity” (DL-010).** Trong contract này, “action-response model fidelity” của Main RQ chỉ được đo qua **một** thành phần: cách biểu diễn tính ngẫu nhiên của tương lai, với cùng $\theta$ đúng và cùng recurrence (D21). Sai tham số và sai cấu trúc nằm ngoài primary estimand (§5). Mọi câu trả lời cho Main RQ phải nói đúng phạm vi này.

**Ba hypothesis của [brief v0](00_research_brief.md):** HC1 là dự đoán bản đồ conditional gains cho RQ1; HM1 là kiểm sức dự báo bổ sung của $H_1$ so với $H_0$ cho RQ2; HP1 là kiểm net gain của repair khả thi so ngưỡng và baseline mạnh cho RQ3. Đây là mã hypothesis DRAFT, không thêm term D hoặc tạo kết quả mới. Các vế bác bỏ nằm trong brief; đặc tả metric, predictor, biên kiểm và split phải khóa trước confirmation (§9).

**Cách dùng từ trong brief.** Predictor là hàm của thông tin controller được cấp **trước action**, không dùng state thật, true margin $\lvert\Delta\rvert$ hoặc future $w$. Persistence là mức kéo dài/tương quan của mode qua law Markov D4; chỉ làm predictor nếu biết hoặc ước lượng được từ thông tin được cấp. “Headroom capacity” là capacity còn dư sau offered traffic (T00); “headroom regret” trong HP1 là $R_{00}$ (§7f), hai đại lượng khác đơn vị. Baseline mạnh gồm $M_0$ đưa tải action vào đúng queue (load-aware), $S_0$ bù tuổi bằng lịch sử observation (age-aware). Dự đoán hằng dùng một giá trị fit trên discovery/calibration, không fit trên held-out. Discovery/calibration là dữ liệu xây bản đồ/fit; held-out là dữ liệu không dùng chọn predictor, fit, ngưỡng hoặc giải thích, đối chiếu exposure ở §9.

## 1. Hệ và vòng quyết định

```text
plant (simulator = mạng thật) ──telemetry đo tại t0−τ──► y ──► S ──► x̂ ──► M ──► Ĵ(Stay), Ĵ(Switch)
      ▲                                                                         │ chọn Ĵ nhỏ hơn (tie → Stay)
      └──────────── action có hiệu lực tại t0; plant chạy H slot với tương lai w ◄┘
```

Twin = $S$ + $M$. Luật quyết định nằm ngoài twin và **cố định** trong mọi ô.

Simulator đóng vai plant được đánh giá, còn twin là pipeline ước lượng state và dự đoán cost. State repair thay $S$; model repair thay $M$. Đổi luật quyết định giữa các ô sẽ trộn hiệu ứng của luật với hiệu ứng của twin.

## 2. Định nghĩa

| ID | Term | Định nghĩa vận hành | Đơn vị | Trạng thái |
|---|---|---|---|---|
| D1 | Slot $\Delta t$ | Đơn vị thời gian rời rạc; mọi rate tính theo packet/slot. Slot $k$ là $[t_0+k\Delta t,\,t_0+(k+1)\Delta t)$; trong slot: mode có hiệu lực → arrivals vào queue → phục vụ tối đa $c_l$; $q_{l,k+1}$ là backlog **cuối** slot $k$ (ghi chú dưới bảng) | s | DRAFT (giá trị: L1.8) |
| D2 | Horizon $h$ | $h=H\Delta t$, dùng chung cho mọi ô và mọi action | s | DRAFT ($H$: L1.8) |
| D3 | Path, capacity $c_l$ | Hai path rời $l\in\{A,B\}$, mỗi path một bottleneck queue; $c_l$ là **parameter**, cố định trong episode | packet/slot | DRAFT |
| D4 | Traffic nền, law $\theta$ | $b_{l,k}$ sinh từ Markov on/off độc lập trên mỗi path. $\theta$ = (ma trận chuyển mode, rate on/off, $c_l$), cố định trong episode | packet/slot | DRAFT |
| D5 | Action $a$, lượng chuyển $u$ | Stay: managed traffic $u$ đi A. Switch: $u$ chuyển sang B tại $t_0$, giữ suốt horizon. A giảm đúng lượng B tăng | packet/slot | DRAFT |
| D6 | Recurrence | $q_{l,k+1}=[q_{l,k}+b_{l,k}+u_l(a)-c_l]^+$. Phép $[\cdot]^+$ là nguồn phi tuyến duy nhất của plant | packet | DRAFT |
| D7 | State thật $x$ | $(q_A,q_B,m_A,m_B)$ tại $t_0$: backlog và mode **hiện tại** của traffic nền | packet; on/off | DRAFT |
| D8 | Observation $y$, age $\tau$ | $y$ = backlog hai queue đo tại $t_0-\tau$, có timestamp; mode **không** quan sát được. $\tau$ thuộc observation. Backlog telemetry là giả định ideal; mirroring/rate counter chưa chứng minh đáp ứng. Schema theo chế độ còn OPEN (§9) | packet; slot | DRAFT |
| D9 | Estimator $S$ | Ánh xạ **cố định** từ history observation $(y_{\le t_0},\tau)$ sang $\hat x$ hợp lệ (point state hoặc belief có schema cố định). $S_0$: belief trên $(q,m)$ tại $t_0$ (B2). $S_1$: trả $x$ thật (chỉ diagnostic). Mô hình bên trong $S$ là một phần của $S$ | — | DRAFT |
| D10 | Model $M$ | $M:(\hat x,a)\mapsto\hat J(a)$. $M_0$: mean rollout **load-aware** (đưa $u$ vào đúng queue, khởi tạo từ $\hat x$, arrivals thay bằng kỳ vọng có điều kiện theo mode). $M_1$: kỳ vọng đúng trên toàn bộ law. Cùng $\theta$; khác **cách dùng** $\theta$ | packet·s | DRAFT |
| D11 | Tương lai $w$ | Realization của traffic nền sau $t_0$. Chỉ evaluator sinh | — | **LOCKED** |
| D12 | Episode, phân phối $D$ | Episode = (state thật, history observation, $w$). Cặp (state, observation) sinh **bằng law của plant**; không ghép tuỳ ý | — | DRAFT (lưới: L1.8) |
| D13 | Cost $C$ (cumulative queue occupancy) | $C(a,w)=\Delta t\sum_{k=1}^{H}\sum_{l}q_{l,k}(a,w)+c_{\text{sw}}\mathbf 1\{a=\text{Switch}\}$: diện tích backlog cuối slot của **cả hai** queue trong $h$, gồm packet có sẵn tại $t_0$ và packet chưa xong; **không** gồm $k=0$ và phần chờ sau $h$. Bằng tổng thời gian chờ đo ở độ phân giải slot; **không** phải mean delay | packet·s | DRAFT |
| D14 | Objective $J$ | $J(a;x,\theta)=\mathbb E_w[C(a,w)]$ | packet·s | DRAFT |
| D15 | Oracle $a^*$ | $\arg\min_a J(a;x,\theta)$: biết $x$ và $\theta$, **không** biết $w$. Thước đo chẩn đoán, không phải policy | — | **LOCKED** |
| D16 | Luật quyết định | Chọn $a$ có $\hat J$ nhỏ hơn; nếu $\widehat\Delta=0$ thì Stay | — | DRAFT |
| D17 | Gap, margin | $\Delta=J(\text{Switch})-J(\text{Stay})$; $\widehat\Delta$ là gap twin dự đoán; margin $=\lvert\Delta\rvert$ | packet·s | DRAFT |
| D18 | Regret | $r=J(\hat a)-J(a^*)\ge0$; $R_{sm}=\mathbb E_D[r]$ của ô $(s,m)$; $L_{sm}=\mathbb E_D[J(\hat a_{sm})]$ | packet·s | DRAFT |
| D19 | Contrasts | $G_S=L_{00}-L_{10}$, $G_M=L_{00}-L_{01}$, $G_{SM}=L_{00}-L_{11}$, $\Gamma=G_{SM}-G_S-G_M$, $G_{S\mid M_1}=L_{01}-L_{11}$, $G_{M\mid S_1}=L_{10}-L_{11}$ | packet·s | DRAFT |
| D20 | State repair | Operator $S_0\to S_1$, dose tối đa; gộp ba thành phần: tuổi về 0, thấy mode, bỏ nhiễu/gộp cửa sổ. Tên: *giá trị của thông tin state hiện tại đầy đủ* | — | DRAFT |
| D21 | Model repair | Operator $M_0\to M_1$, dose tối đa; $S$ giữ nguyên kể cả mô hình bên trong. Chỉ đổi **cách biểu diễn tính ngẫu nhiên** của tương lai (kỳ vọng có điều kiện → toàn bộ law), cùng $\theta$ đúng và cùng recurrence D6. **Không** đo sai tham số ($\hat\theta\ne\theta$) hay sai cấu trúc (TCP, buffer hữu hạn, shared link). Tên: *giá trị của biểu diễn đúng tính ngẫu nhiên của phản ứng* | — | DRAFT |
| D22 | Ô chẩn đoán phụ $S_0^{\tau=0}$ | $S_0$ với tuổi 0 nhưng vẫn không thấy mode. Tách "tươi hơn" khỏi "thấy mode". **Không** thuộc primary estimand | — | DRAFT |
| D23 | Practical threshold $\varepsilon_R$ | Ngưỡng tương đối so với một reference cost, chọn **trước** confirmation; vài mức (ví dụ 0,5%, 1%, 2%) là quy ước khảo sát độ nhạy, chưa phải SLA | % | OPEN (L1.8) |
| D24 | Equivalence margin $\varepsilon_E$ | Gain coi là "tương đương 0" khi cả khoảng tin cậy nằm trong $\pm\varepsilon_E$ | % | OPEN (L1.8) |
| D25 | Threshold null $H_0$; giải thích $H_1$ | $H_0$: mô hình chỉ cộng sai số state và sai số model vào gap rồi qua ngưỡng quyết định; fit trên dữ liệu calibration rồi **đóng băng**. $H_1$: giải thích dựa trên động học queue sau action, cùng quyền thông tin và ngân sách fit với $H_0$ | — | DRAFT (đặc tả A05, trước Phase 4) |

**Ngữ nghĩa slot và objective (DL-010).**
- *Mốc thời gian.* $t_0$ là đầu slot 0, action có hiệu lực từ slot 0 (AS4). State $x=(q_{A,0},q_{B,0},m_{A,0},m_{B,0})$: backlog đầu slot 0 và mode có hiệu lực **trong** slot 0. Tương lai $w$ gồm arrivals $b_{l,0},\dots,b_{l,H-1}$ và mode $m_{l,1},\dots,m_{l,H-1}$.
- *Observation.* $\tau$ là số nguyên slot, $\tau\ge0$; $y$ là backlog đầu slot $-\tau$. $\tau=0$ nghĩa là đọc backlog đúng tại $t_0$ (ô phụ D22).
- *Trong một slot.* Arrivals vào trước, phục vụ sau, nên packet đến trong slot có thể được phục vụ ngay trong slot đó. Đổi thứ tự là đổi recurrence D6, phải có DL.
- *Cost đếm gì.* $q_{l,k}$ với $k=1,\dots,H$ là backlog cuối các slot $0,\dots,H-1$. Mỗi packet góp $\Delta t$ cho mỗi ranh giới slot mà nó còn nằm trong queue. Vì vậy $C$ là tổng thời gian chờ **làm tròn theo slot** và **cắt tại $h$**; packet đến và đi trong cùng slot góp 0. Gọi là *cumulative queue occupancy*, không gọi là mean delay (mean delay chia cho số packet và thường chỉ đếm packet đã xong).
- *Vì sao bỏ $k=0$.* $q_{l,0}$ như nhau cho mọi action, nên bỏ hay giữ không đổi $\Delta$, regret hay contrast. Nhưng nó đổi **mức** $L$, nên đổi reference cost và ngưỡng phần trăm; §9 phải dùng cùng quy ước này.
- *Hệ quả.* Đổi $\Delta t$ với cùng tốc độ vật lý làm đổi phần làm tròn của $C$. Kết quả chỉ có nghĩa nếu không phụ thuộc mạnh vào $\Delta t$ (§6 quy tắc 7).

Đã có đủ 25 hàng trong một bảng. Mỗi hàng giữ định nghĩa vận hành, đơn vị và trạng thái; quyền thông tin được gom ở §3. D23–D24 vẫn OPEN, các mức phần trăm nêu ở D23 chỉ là ví dụ, chưa được chọn làm ngưỡng. D25 đặt nguyên tắc cho null và giải thích động học: cả hai phải được đóng băng trước dữ liệu confirmation và có cùng quyền thông tin/ngân sách fit; cách fit cụ thể còn chờ A05.

## 3. Quyền thông tin

| Thông tin | Ô 00 ($S_0M_0$) | Ô 10 ($S_1M_0$) | Ô 01 ($S_0M_1$) | Ô 11 ($S_1M_1$) | Oracle | Evaluator |
|---|---|---|---|---|---|---|
| $y$, $\tau$ | Có | Không cần | Có | Không cần | Không cần | Sinh ra |
| $x$ thật | **Không** | Có (diagnostic) | **Không** | Có (diagnostic) | Có | Có |
| Estimator | $S_0$ | $S_1$ | $S_0$, **giống hệt ô 00** | $S_1$ | — | — |
| Cách dùng $\theta$ trong $M$ | Kỳ vọng có điều kiện | Kỳ vọng có điều kiện | Toàn bộ law | Toàn bộ law | Toàn bộ law | Chạy plant |
| $w$ | **Không** | **Không** | **Không** | **Không** | **Không** | Sinh, không chia sẻ |

**Ba luật chống rò (LOCKED):** (1) không ô nào nhận $w$; (2) chỉ $S_1$ và oracle nhận $x$; (3) $S$, kể cả mô hình bên trong, giống hệt giữa các ô cùng chỉ số $s$. Phase 3–4 ép ba luật này bằng interface của code (controller chỉ nhận $(y,\tau)$).

Luật (2) nói về quyền nhận state thật trong nhánh ra quyết định; evaluator vẫn có $x$ để sinh và đánh giá episode như bảng trên. Interface controller nhận observation áp dụng cho nhánh $S_0$; nhánh diagnostic $S_1$ phải được cấp $x$ riêng theo đúng bảng, không truyền state thật vào ô 00/01.

Hàng “Cách dùng $\theta$” mô tả phép sửa model, không phải khác biệt về quyền biết parameter: cả $M_0$ và $M_1$ được dựng từ cùng $\theta$. Mô hình bên trong estimator vẫn thuộc $S$ và phải đứng yên khi đổi $M$.

| Luật | Nếu vi phạm |
|---|---|
| (1) Không ô nào, kể cả oracle, nhận $w$ | Nhánh ra quyết định thấy trước realization evaluator dùng, khiến regret và gain bị méo |
| (2) Chỉ $S_1$ và oracle nhận $x$ trong nhánh ra quyết định | Ô 00/01 lén biết state thật, làm phép đo giá trị State repair sai |
| (3) $S$ giống hệt giữa các ô cùng chỉ số $s$ | $G_M$ trộn thêm sửa estimator, thành pipeline repair |

## 4. Estimand card

- **Objective:** D13–D14. Cộng cả hai queue vì Switch đẩy tải lên traffic nền của B. Đếm cả packet chưa xong vì “mean delay của packet đã xong” ưu ái action để lại backlog (ví dụ X/Y ở L0.4).
- **Benchmark:** oracle D15, **một** oracle cho cả bốn ô. Nhờ vậy hiệu giữa các $L$ bằng hiệu giữa các $R$.
- **Primary estimand:** $R_{sm}$, $G_S$, $G_M$, $G_{SM}$, $\Gamma$, $G_{S\mid M_1}$, $G_{M\mid S_1}$ trên $D$ đã khai báo, cùng episode, **báo theo điều kiện**.
- **Diagnostics (không thay thế câu trả lời RQ):** sai số state $\hat x-x$; sai số gap $\widehat\Delta-\Delta$; $I_\Delta$ (L1.5); tỉ lệ đổi quyết định; phân phối margin; ô $S_0^{\tau=0}$.
- **Không dùng làm primary:** RMSE của twin; delay của packet đã xong; tail; loss.
- **Quy tắc khoá ngay:** xem §6.
- **Đọc kết quả:**

| Kết quả | Dấu hiệu | Nghĩa |
|---|---|---|
| Bổ trợ | $\Gamma>0$ | Sửa cả hai được nhiều hơn tổng sửa riêng |
| Thay thế | $\Gamma<0$ | Sửa cả hai được ít hơn tổng sửa riêng. Muốn biết “sửa một là đủ chưa” thì so $G_S$ hoặc $G_M$ với $G_{SM}$ |
| Một phía trội | $G_S\gg G_M$ hoặc ngược lại, **trong một vùng** | Phía đó có diagnostic gain lớn hơn trong vùng đó; đầu tư thực tế còn cần kiểm RQ3 |
| Tương đương | Khoảng tin cậy của gain nằm trọn trong $\pm\varepsilon_E$ | Twin hiện trạng đủ đối với phép sửa đã kiểm trong domain; kết luận cho mọi repair cần kiểm cận $R_{00}$ ở §7(f) |
| Chưa kết luận | Khoảng tin cậy chứa cả 0 lẫn giá trị vượt ngưỡng | Cần thêm dữ liệu; **không** gọi là “không có hiệu ứng” |

- **Mapping test:** RQ1 → contrasts theo toạ độ quan sát được trước action. RQ2 → sai số dự báo gain trên held-out của $H_0$ so với $H_1$. RQ3 → gain của repair khả thi trừ chi phí, so với $\varepsilon_R$ và baseline load-aware/age-aware.
- **Câu hỏi construct validity cho người đọc độc lập:** báo primary bằng packet·s kèm quy đổi ms/packet, hay ms/packet làm primary? Nếu đổi primary, phải REFORMULATE và ghi DL-005: mọi contrast dùng cùng đơn vị mới; ngưỡng phần trăm vẫn là phần trăm nhưng reference cost và cách quy đổi phải nhất quán.

**Cùng thước đo.** Đặt $L_*=\mathbb E_D[J(a^*;x,\theta)]$. Khi dùng chung $D$ và oracle, $R_{sm}=L_{sm}-L_*$; vì vậy mọi hiệu trong D19 có thể tính từ $L$ hoặc $R$. $L$ là expected cost, không phải expected regret. D13 tính diện tích backlog trong horizon, bao gồm thời gian chờ tích lũy của packet còn tồn; không tính tiếp phần chờ sau horizon.

**Quy đổi và ngưỡng còn OPEN.** Không so trực tiếp gain packet·s với ngưỡng %. Cần chọn reference cost dương và quy tắc chuẩn hóa trước confirmation (L1.8), rồi dùng cùng thang cho estimate, khoảng tin cậy và $\varepsilon_R/\varepsilon_E$. Bản quy đổi ms/packet cũng cần khai báo mẫu số và tập packet; chưa tự chọn trong lần bổ sung này.

**Thang kiểm hypothesis.** Gọi reference cost dương là $C_{\text{ref}}$, chuẩn hóa một cost/gain/headroom $v$ thành $100v/C_{\text{ref}}$ (%). HP1 dùng $100R_{00}/C_{\text{ref}}$ để sàng lọc headroom; $R_{00}$ chỉ là diagnostic của evaluator, không được cấp vào policy hoặc predictor trước action. Net gain là giảm expected cost do repair khả thi so baseline, đã tính dynamics trong lúc chờ action và trừ chi phí repair quy đổi cùng đơn vị; không tính lại một chi phí đã nằm trong cost. So cả net gain với $\varepsilon_R$ và lợi thế so baseline mạnh. Cận trên net gain dưới ngưỡng hoặc cận trên lợi thế không dương bác HP1 trong miền đã khai báo; khoảng tin cậy rộng chưa đủ bác hay xác nhận.

HM1 phải chấm hai dự báo trên cùng targets/held-out, cùng quyền thông tin và ngân sách fit. “$H_0$ đủ dùng” cần biên sai số chuẩn hóa đã khai báo **và** kiểm $H_1$ không cải thiện vượt biên; không suy từ riêng p > 0,05. Nếu dùng $\varepsilon_E$, phải định nghĩa phép chấm trên thang gain chuẩn hóa phù hợp D24; không áp ngưỡng % trực tiếp cho MSE có đơn vị bình phương. Metric/biên kiểm HC1/HM1 vẫn OPEN; chưa coi vế bác bỏ DRAFT là protocol confirmation đã đóng băng.

$I_\Delta$ là interaction ở tầng dự đoán, còn $\Gamma$ là interaction ở tầng quyết định sau khi qua ngưỡng chọn action. Đặc tả $I_\Delta$ chờ L1.5. Với $S_0$ dạng belief, metric sai số state cũng cần được đặc tả theo schema, không trực tiếp lấy một phân phối trừ point state.

## 5. Repair cards

| Thành phần | State repair | Model repair |
|---|---|---|
| Operator | $\hat x$ của $S_0$ → $x$ thật | $M_0$ → $M_1$ |
| Điểm xuất phát | $S_0$ belief (B2); bản tối thiểu B1 = mode có xác suất cao nhất | $M_0$ load-aware (D10) |
| Dose (diagnostic) | Tối đa | Tối đa |
| Giữ cố định | $M$, plant, episode, $H$, objective | $S$ kể cả mô hình bên trong, plant, episode, $H$, objective |
| Sau khi sửa biết | Ô 10: biết $x$; không biết $w$ | Ô 01: cùng $\theta$, dùng đúng law; vẫn không biết $x$, $w$ |
| Phiên bản khả thi (RQ3) | Refresh phần đo được (backlog) với độ trễ $d$ và chi phí telemetry. Phần “thấy mode” **không** có bản khả thi nếu mode không đo được | Biểu diễn ngẫu nhiên khả thi cùng $\theta$, ví dụ rollout Monte Carlo $K$ mẫu hoặc model trung gian có phương sai, ngân sách tính cố định. Model ước lượng $\theta$ từ dữ liệu hữu hạn là repair **khác** (tham số), cần tên và estimand riêng |
| Rủi ro | Gọi nhầm là “freshness” | $M_0$ thành strawman; estimator đổi theo model; gọi $G_M$ là giá trị “model fidelity” nói chung |
| Nếu không tách được | Đổi tên estimand thành **pipeline repair** (K5) | Như trái |

Hai dose tối đa là diagnostic endpoints; chúng không chứng minh hai repair có cùng chi phí triển khai. RQ3 phải dùng repair khả thi và ngân sách/chi phí khai báo riêng. Nếu gain của State repair chủ yếu đến từ thấy mode ẩn, không được coi toàn bộ gain đó là lợi ích refresh backlog thực tế.

**Phạm vi model repair (DL-010).** $M_0$ và $M_1$ cùng biết $\theta$ đúng và cùng recurrence D6; chúng chỉ khác ở chỗ $M_0$ thay arrivals tương lai bằng kỳ vọng có điều kiện, còn $M_1$ lấy kỳ vọng trên toàn bộ law. Vì vậy $G_M$ là giá trị của **biểu diễn ngẫu nhiên đúng**, một phần nhỏ của “model fidelity”. Ba loại sai số model khác **không** được đo: (i) sai tham số, ví dụ ước lượng sai rate on/off; (ii) sai cấu trúc, ví dụ bỏ qua TCP phản hồi hoặc buffer hữu hạn; (iii) sai mô hình bù tuổi, vốn thuộc $S$. Feasible model repair ở RQ3 phải cùng loại với operator diagnostic (cùng $\theta$, đổi cách biểu diễn ngẫu nhiên); nếu thêm ước lượng $\theta$, đó là repair tham số và phải báo riêng.

B2 đã được tác giả nêu chọn làm baseline chính trong [Ownership Review ngày 08/10](PHASE_0_ownership_review.md); contract tổng thể còn DRAFT, schema/cách triển khai chưa chốt và bài tự kiểm còn chờ. B1 là lựa chọn thay thế cần đặc tả đủ cách ước lượng backlog và mode, ghi lý do ở DL-008 và kiểm lại §7(c); không trộn B1/B2 giữa các ô cùng chỉ số $s$.

## 6. Quy tắc khoá ngay (DRAFT, đổi phải có DL entry)

1. Tie rule: $\widehat\Delta=0$ → Stay.
2. $c_{\text{sw}}=0$ trong diagnostic. Giá trị khác 0 chỉ dùng khi có quy tắc quy đổi công khai, chọn trước khi xem kết quả.
3. $\varepsilon_R$, $\varepsilon_E$ tính theo tỉ lệ một reference cost và chọn **trước** confirmation.
4. Luôn báo đủ $G_S$, $G_M$, $G_{SM}$, $\Gamma$, hai gain có điều kiện, điểm xuất phát và phân phối margin.
5. Ô báo cáo định nghĩa bằng **toạ độ quan sát được trước action** (ví dụ $\tau$, backlog quan sát, persistence). Nếu cắt theo state ẩn (ví dụ mode thật) thì ghi rõ, vì bảo đảm ở §7(c) không còn giữ.
6. Đổi objective, estimand hoặc metric sau khi đã thấy kết quả → DL entry ghi “post hoc”.
7. **Chống chỉnh timescale (DL-010).** Mọi thang thời gian khai báo bằng **giây vật lý** từ chế độ có nguồn (T00, EV-31): tổng tuổi và độ trễ $\tau_{\text{eff}}+d_{\text{act}}$, horizon $h$, thời gian lưu trung bình của mode $T_{\text{mode}}$. Sau đó mới đổi sang slot qua $\Delta t$, ví dụ $H=h/\Delta t$, với chain có thời gian lưu geometric, xác suất rời mode mỗi slot $p=\Delta t/T_{\text{mode}}$ (cần $p\le1$); hoặc khai báo generator thời gian liên tục $Q$ rồi dùng $P(\Delta t)=\exp(Q\Delta t)$. Xác suất có ít nhất một lần rời mode $1-e^{-\Delta t/T_{\text{mode}}}$ không tự là phần tử chuyển mode quan sát cuối slot nếu có thể rời rồi quay lại. Lưới khoá trước khi xem contrast (contract v1, L1.8). Báo **mọi** điểm lưới, kể cả điểm gain bằng 0, kèm $T_{\text{drain}}/(\tau_{\text{eff}}+d_{\text{act}})$, $h/T_{\text{drain}}$ và $T_{\text{mode}}/(\tau_{\text{eff}}+d_{\text{act}})$. Kiểm bất biến thang: chạy lại với $\Delta t/2$ và cùng tốc độ vật lý; contrast đổi dấu hoặc lệch quá dung sai khai báo trước được ghi là artefact rời rạc hoá, không phải kết quả.
8. **Null bảo toàn (DL-010, §7g).** Báo tỉ lệ episode thuộc vùng bảo toàn (không queue nào bỏ phí capacity trong $h$ dưới cả hai action) và tỉ lệ dự đoán hoà $\widehat\Delta=0$ ở mỗi ô. Đây là toạ độ diagnostic của evaluator, không cấp cho predictor (quy tắc 5). Mọi chương trình mô phỏng phải qua **negative control**: trong một cấu hình không idle, bốn ô cho cùng cost và mọi contrast bằng 0 đúng tuyệt đối.

Các quy tắc lần lượt ngăn chọn tie rule sau kết quả, chỉnh switching cost để dịch ranh giới, chọn ngưỡng hậu nghiệm, chỉ báo contrast thuận lợi, chia nhóm bằng thông tin ẩn, âm thầm đổi thước đo, chọn thang thời gian sao cho hiệu ứng xuất hiện, và để các episode tầm thường ($\Delta=0$ do bảo toàn) làm loãng hoặc che trung bình. Persistence chỉ là toạ độ hợp lệ nếu controller biết được nó từ thông tin được cấp trước action.

## 7. Hệ quả biết trước — **không** phải phát hiện

*E0 — hệ quả toán học từ thiết kế, tích hợp theo nội dung Doan Van Tai cung cấp. Tác giả kiểm lại bằng tay ở L1.3–L1.4; chưa ghi nhận đã hoàn thành. [Inventory](00_evidence_inventory.md) đã bổ sung EV-20, EV-25–EV-27 cùng log phép tính và giới hạn kiểm độc lập ở File 5.*

**Quy ước từng episode.** D18–D19 dùng $L,R,G,\Gamma$ cho đại lượng kỳ vọng trên $D$. Khi xét một episode $e$, đặt $\ell_{sm}(e)=J(\hat a_{sm};x,\theta)$, $r_{sm}(e)=\ell_{sm}(e)-J(a^*;x,\theta)$; dùng $g$ và $\gamma(e)$ cho các contrast cùng công thức D19 nhưng thay $L$ bằng $\ell(e)$. Kỳ vọng của chúng lần lượt là $G$ và $\Gamma$.

- **(a) Ô 11 chính là oracle:** theo từng episode, $g_{SM}\ge0$, $g_{S\mid M_1}\ge0$, $g_{M\mid S_1}\ge0$; do đó các $G$ tương ứng cũng không âm. Chỉ $g_S$, $g_M$ và $\gamma$ có thể âm ở mức episode. Dấu của $G_M$ khi lấy trung bình còn phụ thuộc điều kiện ở (c). Ô 11 có $R_{11}=0$, $L_{11}=L_*$.
- **(b) Theo từng episode, với hai action và $J$ tính chính xác:** mỗi ô nhận $J(\text{Stay})$ hoặc $J(\text{Switch})$, nên mỗi contrast là bội nguyên của $\lvert\Delta\rvert$. Vì ô 11 luôn tối ưu, $\gamma(e)\in\{-1,0,1,2\}\times\lvert\Delta(e)\rvert$. Kết quả từng episode không thoả điều này là bug theo các giả định trên. Bất biến này không áp trực tiếp cho $\Gamma$ đã lấy trung bình với margin thay đổi.
- **(c) Nếu belief của $S_0$ là posterior chính xác theo $\theta$ và prior của nó trùng với $D$:** ô 01 dùng $M_1$ tích phân đúng expected cost theo belief, nên Bayes-optimal theo observation. Khi đó $G_M\ge0$ (tính trung bình), và $G_{S\mid M_1}$ bằng **giá trị kỳ vọng của thông tin hoàn hảo (EVPI)** về state hiện tại, sau thông tin observation đã có. Đây không phải biết trước realization $w$. Dấu không âm này không phải phát hiện; literature value-of-information là closest prior phải kiểm ở Phase 2. Hướng dẫn trỏ Final Review P11; cần đối chiếu primary literature khi đến Phase 2.
- **(d) Không có clipping trên mọi sample path liên quan:** với cùng input/belief và cách lấy kỳ vọng nhất quán, recurrence và objective đều tuyến tính, $M_0$ cho đúng expected cost như $M_1$, nên $G_M=G_{M\mid S_1}=0$. Hướng dẫn dẫn Final Review §5.2, ví dụ 60 = 60; cần kiểm tay ở L1.3–L1.4. Chỉ một trajectory quan sát không chạm biên chưa đủ điều kiện này.
- **(e) Đồng nhất thức:** $\Gamma=G_{S\mid M_1}-G_S=G_{M\mid S_1}-G_M$. Đồng nhất thức cũng đúng ở mức episode với $g,\gamma$.
- **(f) Cận trên:** với cùng $D$, objective và tập action, $R_{00}$ là cận trên cho lợi ích của **mọi** repair so với ô 00, vì không repair nào có cost thấp hơn oracle. Gain của **một** oracle repair **không** phải cận trên cho feasible repair cùng loại, vì sai số state và model có thể bù nhau. [L0.4 §3](lessons/L0.4_estimand.md) đã có khung bài phản ví dụ; log tính ở EV-26. Quy tắc dùng $R_{00}$ cho cheap kill/K10 đang DRAFT ở DL-006, chưa có bài tự kiểm/xác nhận của tác giả.
  **Quy tắc cheap kill/K10 đã sửa (DL-006, DL-010):** trên một miền đã khai báo, nếu cận trên khoảng tin cậy của $100R_{00}/C_{\text{ref}}$ nhỏ hơn $\varepsilon_R$, thì loại miền theo mức tin cậy đã khai báo: không repair nào (state, model hay pipeline; oracle hay khả thi) đạt ngưỡng theo cận này → NARROW hoặc dừng miền đó. **Không** loại một feasible repair chỉ vì oracle repair cùng loại có gain nhỏ (EV-26, NC11). Cận chỉ giữ khi feasible repair dùng cùng $D$, objective, tập action và **thời điểm hiệu lực** của action với oracle; nếu repair thêm độ trễ thực thi hoặc đổi tập action, phải dựng lại oracle tương ứng rồi mới dùng cận.
- **(g) Bảo toàn và null tương đương quyết định.** Giả sử D5 (A giảm đúng lượng B tăng), AS1 (cùng $b$ cho hai action), capacity cố định, objective cộng hai queue cùng trọng số, $c_{\text{sw}}=0$. Viết $[z]^+=z+[-z]^+$ thì

  $$\sum_l q_{l,k}(a)=\sum_l q_{l,0}+\sum_{j<k}\Big(\sum_l b_{l,j}+u-\sum_l c_l\Big)+\sum_{j<k}I_j(a),\qquad I_j(a)=\sum_l\big[c_l-q_{l,j}-b_{l,j}-u_l(a)\big]^+ .$$

  $I_j(a)$ là capacity bị **bỏ phí** (queue rỗng, server rảnh) trong slot $j$. Số hạng thứ hai không phụ thuộc action, nên trên cùng $w$:

  $$C(\text{Switch},w)-C(\text{Stay},w)=\Delta t\sum_{j=0}^{H-1}(H-j)\big[I_j(\text{Switch},w)-I_j(\text{Stay},w)\big].$$

  Hệ quả: (i) action chỉ đổi cost qua capacity bỏ phí, và slot càng sớm càng nặng ký; (ii) **null tương đương quyết định:** nếu trên mọi path có xác suất dương, không queue nào idle trong $h$ dưới cả hai action, thì $\Delta=0$, mọi ô có cùng $J$, mọi regret và contrast bằng 0 — vùng đó không mang thông tin cho Main RQ; (iii) cùng đẳng thức áp cho quỹ đạo trung bình của $M_0$: nếu quỹ đạo trung bình không chạm 0 dưới cả hai action thì $\widehat\Delta_{M_0}=0$, tie rule chọn Stay, dù $\Delta$ thật có thể khác 0; (iv) một ví dụ Stay/Switch không suy biến **cần** idle với xác suất dương dưới ít nhất một action. Đây là hệ quả của bảo toàn công việc (work conservation) quen thuộc trong queueing, E0, không phải phát hiện. Nó mạnh hơn (d): (d) nói $M_0$ đúng trong vùng không clipping; (g) nói trong vùng đó cả hai action tương đương.
- **(h) $M_0$ không bao giờ dự đoán cao hơn $M_1$.** Hàm $f(q,b)=[q+b+u_l-c_l]^+$ lồi theo $(q,b)$ và không giảm theo $q$. Quy nạp với bất đẳng thức Jensen cho $\mathbb E[q_{l,k}]\ge\bar q_{l,k}$ khi xuất phát từ cùng state, trong đó $\bar q$ là quỹ đạo trung bình của $M_0$. Ở đây mean arrivals phải là $\mathbb E[b_{l,k}\mid x,\theta]$ đúng cho từng slot, không giữ mode hiện tại bất biến. Với belief, lấy trung bình các mean-rollout theo từng state hợp lệ và cùng trọng số belief; cách plug-in khác phải kiểm lại, chưa tự được hưởng bảo đảm. Do đó với cùng state hoặc cùng belief theo cách trên và cùng action, $\hat J_{M_0}(a)\le\hat J_{M_1}(a)$. Hai action bị đánh giá thấp với lượng khác nhau, nên dấu sai số của $\widehat\Delta$ **không** cố định. Model repair chỉ đổi quyết định khi phần đánh giá thấp, tức khoảng Jensen của capacity bỏ phí, chênh giữa hai action đủ để lật dấu gap. E0.

**Giải thích bất biến (b).** Với $\lvert\Delta\rvert>0$, đặt $i_{sm}=1$ nếu ô chọn action có cost lớn hơn, bằng 0 nếu chọn action tối ưu. Khi đó $\ell_{sm}=J_{\min}+i_{sm}\lvert\Delta\rvert$, $i_{11}=0$ và

$$
\gamma=(i_{10}+i_{01}-i_{00})\lvert\Delta\rvert.
$$

Vì ba indicator chỉ nhận 0/1, hệ số thuộc $\{-1,0,1,2\}$. Ví dụ 20/18 với $e_S=e_M=3$ có $(i_{00},i_{10},i_{01})=(1,1,1)$ nên $\gamma=+2$; với lỗi 1,5 có $(1,0,0)$ nên $\gamma=-2$. Khi $\Delta=0$, mọi action có cùng cost thật, mọi regret/contrast từng episode đều bằng 0; không chia cho margin bằng 0.

**Phạm vi của (c).** Belief xấp xỉ hoặc prior không khớp $D$ làm mất bảo đảm Bayes-optimal. Bảo đảm $G_M\ge0$ vẫn giữ khi chia theo nhóm xác định từ thông tin controller đã có trước action; chia theo state ẩn có thể làm $G_M$ âm trong nhóm đó. $G_{S\mid M_1}\ge0$ vẫn đúng theo (a), kể cả khi không còn diễn giải nó là EVPI. B1 không tự có bảo đảm posterior của B2.

**Vì vậy thông tin khoa học nằm ở:** độ lớn của các gain, vùng điều kiện nơi chúng vượt $\varepsilon_R$, dấu của $G_S$ và $\Gamma$, và việc $H_0$ có dự báo được chúng trên held-out hay không. Các hệ quả trên là ràng buộc thiết kế, không phải network evidence mới hoặc kết luận novelty.

## 8. Scope và assumptions

**Scope:** một managed traffic class; hai path rời, mỗi path một bottleneck queue; quyết định nhị phân Stay/Switch, chuyển lượng cố định $u$ và giữ suốt horizon; traffic nền ngoại sinh; một objective chính; một state repair, một model repair.

**Domain — phương án A:** báo theo tỉ số không thứ nguyên $T_{\text{drain}}/(\tau_{\text{eff}}+d_{\text{act}})$ và $h/T_{\text{drain}}$. $\tau_{\text{eff}}+d_{\text{act}}$ là **trục quét** trải bốn chế độ có nguồn: cỡ ms, dưới 1 s, vài giây, từ vài chục giây ([T00](theory/T00_timescale_sanity.md)). Giữ cả hai neo: **(a)** telemetry cỡ ms + link datacenter 1–10 Gb/s; **(b)** polling 0,1–1 s + link edge 10–100 Mb/s. Tổng 5 ms/0,2/1/5/30 s là lưới minh họa, không phải số đo use case; chu kỳ polling cần đổi qua $P,L,W$ và cộng delay. Lựa chọn A do tác giả cung cấp ngày 08/10/2026; lưới số contract v1 và timing thật chưa chốt. Chỉ dùng mẫu số dương/hữu hạn; drain fluid không chứng minh gain dương/0. $T_{\text{drain}}$ dùng state thật chỉ là diagnostic; HC1 phải dùng proxy tính từ thông tin trước action và ghi cách ước lượng, không lấy state ẩn làm predictor.

Các phương án domain dùng tên mô tả, ví dụ “trục tuổi telemetry, hai neo (a)/(b)”; không dùng lại D1/D2/D3 làm mã domain vì các mã đó đã chỉ Slot/Horizon/Path trong bảng định nghĩa.

**Ngoài scope:** nhiều controller; RL/chuỗi quyết định; active probing; tail/safety; TCP; shared bottleneck và topology lớn.

| ID | Giả định | Nếu sai, dấu hiệu | Kiểm ở |
|---|---|---|---|
| AS1 | Traffic nền ngoại sinh | TCP tự giảm khi nghẽn → cost Switch bị đánh giá cao | Phase 7 |
| AS2 | Traffic nền hai path độc lập | Burst đồng thời làm Switch kém hấp dẫn hơn | Phase 7 |
| AS3 | Slotted, buffer vô hạn | Drop ở biên đầy là phi tuyến thứ hai. Drop làm **giảm** occupancy, nên D13 sẽ thưởng cho action gây mất gói; trước khi nới AS3 phải thêm phạt loss vào objective (DL mới) | Phase 7 |
| AS4 | Action hiệu lực ngay | Độ trễ thực thi làm giảm giá trị state | Phase 8 |
| AS5 | Markov on/off, tham số cố định | Burst đuôi dài làm $(q,m)$ không còn đủ | Phase 7 |
| AS6 | Capacity cố định | Capacity trôi | Phase 8 |
| AS7 | Hai path rời | Shared link đổi tương tác | Phase 7 |
| AS8 | $(q,m)$ là state đủ (Markov) | State ẩn khác ngoài thực tế | Limitation |
| AS9 | Managed traffic tốc độ cố định $u$ | Managed traffic có burst | Phase 7 |

Cột “Nếu sai” là dấu hiệu cần kiểm, không bảo đảm hướng tác động trong mọi cấu hình. Đặc biệt, burst tương quan hoặc actuation delay có thể đổi ranking và magnitude theo regime.

**Ưu tiên rủi ro trong bản nháp:** AS1 cho external validity, vì traffic phản hồi theo nghẽn có thể làm counterfactual replay với offered arrivals cố định sai; AS4 cho giá trị State repair, vì thông tin có thể cũ đi trong thời gian action tới mạng. Tác giả còn cần chọn lại hoặc xác nhận kèm lý do trong `notes/lessons/L0.6_scope.md`; chưa có record bài làm đó.

AS4 là giả định của diagnostic. $d_{\text{act}}$ trong domain/feasible repair thuộc kiểm use case và RQ3; khi đưa delay vào plant, phải mô hình hóa dynamics trong thời gian chờ trên cùng cửa sổ objective, không cấp state tương lai cho oracle.

## 9. Mục còn mở

| Mục | Vì sao chưa quyết | Quyết ở |
|---|---|---|
| $\Delta t$, $H$, lưới $\tau$ | Cần tính tay; quét tuổi/delay phủ bốn chế độ, mỗi neo có điểm ①–② của T00; khai báo bằng giây trước rồi đổi sang slot qua $\Delta t$ (§6 quy tắc 7) | L1.8 |
| Ví dụ Stay/Switch không suy biến sinh từ plant | §7(g): $\Delta\ne0$ cần idle với xác suất dương; bảng 4/4,25 (EV-22) chưa sinh từ plant | Phase 1 (L1.2–L1.4) |
| Dung sai kiểm bất biến $\Delta t$ / $\Delta t/2$ | Cần chọn trước khi xem contrast (§6 quy tắc 7) | L1.8; kiểm ở Phase 1 |
| Tỉ lệ vùng bảo toàn trong $D$ và negative control | Lưới $D$ toàn vùng không idle sẽ cho mọi contrast bằng 0 (§7g); cần báo tỉ lệ và có test negative control | L1.8; Phase 3 |
| Mô hình observation theo chế độ telemetry | D8 giả định backlog, Planck/rate counter chưa chứng minh cung cấp backlog. Quét tuổi giữ schema; rate-only phải tách scenario/version, estimator và observation giữ chung giữa các ô cùng $S$ | L1.8 |
| $u$, $c_A$, $c_B$, tham số Markov | Cần running example có queue; đối chiếu mode persistence (khai báo bằng $T_{\text{mode}}$ giây) với tuổi telemetry/action, phân biệt nhớ mode và backlog | L1.8 |
| Chi tiết $S_0$: belief là posterior chính xác hay xấp xỉ; prior lấy từ đâu; cách $M_0$ dùng belief (khuyến nghị: lấy trung bình mean-rollout theo belief, không plug-in) | Quyết định §7(c) có giữ hay không | L1.6–L1.8 |
| Lưới $D$ cho Phase 3 | Cần exact enumeration | L1.8 |
| Reference cost, mức $\varepsilon_R$, $\varepsilon_E$ | Cần thang cost | L1.8 |
| Seed streams | Cần CRN; tránh mọi mục trong `00_exposure_register.md` (seed **và** cấu hình) | L1.7–L1.8 |
| $\varepsilon$ vận hành, feasible repairs, $d_{\text{act}}$ của use case | Cần chi phí và timing thật | Phase 8 |
| Domain timescale và hai neo (a)/(b) | Phương án A đã được cung cấp; cần chọn lưới hợp lệ cho mỗi neo và đo timing/cost thật, không dùng AoI prototype làm neo | L1.8; Phase 8 |
| Đặc tả $H_0/H_1$ (D25), predictor HC1, metric/biên kiểm HC1/HM1, discovery/calibration/held-out split và ngân sách fit | Brief có vế bác bỏ DRAFT; chưa chọn metric, fit hoặc đóng băng protocol. Phải giữ quyền thông tin và thang chuẩn hóa ở §0/§4 | A05, trước confirmation/Phase 4 |
| Diagnostic $I_\Delta$ | Chưa có đặc tả interaction ở tầng dự đoán | L1.5 |
| Schema belief, metric sai số state và sensitivity B1 | B2 đã được chọn; chi tiết còn OPEN để tránh trộn point state với belief hoặc đổi estimator giữa các ô | L1.6–L1.8; DL-008 |
| Model baseline trung gian có xét biến động traffic | Ownership Review đề xuất kiểm baseline mạnh hơn M0; chưa đặc tả model, quyền thông tin hoặc ngân sách so sánh | L1.8 |
| Quy đổi packet·s sang ms/packet: mẫu số, tập packet và reference cost | Chưa có quy tắc quy đổi công khai, không coi mean delay packet đã xong là cùng objective | DL-005; L1.8 |

Với B2, khuyến nghị chạy mean-rollout cho từng state hợp lệ rồi lấy trung bình theo belief. Khi đó hai model dùng cùng uncertainty về state, khác cách xử lý tương lai ngẫu nhiên. Plug-in một state trung bình có thể thêm xấp xỉ ở tầng state và tạo mode không hợp lệ; nếu chọn cách đó phải ghi rõ estimand và kiểm lại model-only repair, không âm thầm thay mặc định.

CRN là dùng chung primitive streams giữa các action/ô khi evaluator đánh giá để giảm variance; không được chia sẻ realized evaluation future với $M_0$, $M_1$ hoặc oracle. Đối chiếu [exposure register](00_exposure_register.md) cho cả seed lẫn regime đã xem, không chỉ đổi seed.

Các lựa chọn DRAFT về đơn vị, ô phụ D22, chi tiết B2/sensitivity B1 và assumption ưu tiên vẫn được theo dõi trong phụ lục. Nếu thay chúng tạo ra mục chưa quyết mới, bổ sung vào bảng này cùng nơi quyết.

## 10. Kiểm nhất quán trước khi gắn tag `contract-v0`

Kết quả kiểm kỹ thuật ngày **08/10/2026**; không ghi thay record tác giả tự đọc/tự giải thích. Chỉ gắn tag sau khi hoàn tất các điều kiện kiểm còn lại.

| # | Kiểm | Kết quả hiện tại |
|---|---|---|
| 1 | Mỗi khái niệm định nghĩa đúng một lần | Đạt trong contract: 25 ID/term phân biệt, cùng một bảng D1–D25; không dùng mã D làm tên domain. Ký hiệu phụ và timescale có nơi đặc tả/định nghĩa ở §9. |
| 2 | Mọi khái niệm trong brief có định nghĩa | **ĐẠT đối chiếu kỹ thuật bản DRAFT ngày 08/10**: [brief v0](00_research_brief.md) đã có HC1/HM1/HP1 đầy đủ; mapping thuật ngữ dưới đây. Làm rõ predictor trước action, headroom và chuẩn hóa ngưỡng; metric/biên kiểm còn OPEN có nơi quyết §9. Chưa có record tác giả tự gạch thuật ngữ/giải thích hoặc người đọc độc lập. |
| 3 | Mỗi mục OPEN có nơi quyết | Đạt: D23/D24 cùng trỏ dòng reference cost/ngưỡng ở §9, quyết ở L1.8; các chi tiết hoãn khác đều có nơi xử lý trong §9. |
| 4 | Không mâu thuẫn Final Review §2.0, §11.1–11.2, §12.2 | Đã đối chiếu kỹ thuật bản gốc đúng digest: state/observation/parameter/future tách riêng; cùng law/schema; giữ estimator khi sửa model; objective và oracle đúng scope. B1 hoặc belief dùng chung đều được nguồn cho phép; lựa chọn cụ thể vẫn DRAFT. Chưa có record tác giả tự đối chiếu. |
| 5 | Tổng term ≤ khoảng 25 | Đạt: **25** hàng D, không thiếu/trùng ID. |

Nguồn kiểm 4: snapshot Final Review cập nhật 06/10/2026, SHA-256 `fc766e319427ba01da7362de2018cd4da6695dc1fcaa9812ed7badd5c0651fd1`, khớp [source checks](verification/source_checks.json). Snapshot đầy đủ được đọc tại máy, không chép vào repo public; [reading note](verification/final_review_reading_note.md) chỉ là tóm tắt. Kiểm 4 không phải primary-literature verification hoặc xác nhận hướng nghiên cứu của GVHD.

### Mapping thuật ngữ brief → contract/T00

| Khái niệm trong brief | Nơi định nghĩa/phạm vi |
|---|---|
| Twin, State/Model, observation, mode/law/future, mean rollout | §1; D4, D7–D11; quyền thông tin §3 |
| Path, bottleneck, capacity, managed class, action đổi tải, horizon | D1–D6; scope/assumptions §8 |
| Oracle, objective, expected regret, episode/$D$, conditional contrasts/$\Gamma$ | D12–D19; estimand §4 |
| State/Model repair, feasible repair, net gain, baseline load-aware/age-aware | D20–D22; §0/§4/§5 |
| Headroom regret/capacity, predictor, persistence, dự đoán hằng | §0/§4/§7(f); capacity còn dư trong T00 |
| $H_0/H_1$, HC1/HM1/HP1, discovery/calibration/held-out, confirmation | D25; §0/§4; metric/split/ngân sách còn OPEN ở §9 |
| Reference cost, ngưỡng thực dụng, biên tương đương, khoảng tin cậy | D23–D24; §4 và §9; cost/gain/headroom cùng thang % |
| Tuổi telemetry, độ trễ action, drain time, vùng timescale/fluid | D8; [T00](theory/T00_timescale_sanity.md) định nghĩa/công thức/quy ước vùng và giới hạn |
| Posterior/belief, prior khớp $D$, EVPI/value-of-information | D9; §7(c) và phạm vi; exact/xấp xỉ vẫn OPEN ở §9 |
| AS1/AS4, ngoài scope, K5/pipeline repair | §3/§5/§8; K1–K4/K9 là nhãn kill criteria giải thích ngay trong brief |
| G1/candidate gap, prior IDs P01–P13, E0, evidence/motivation | Khái niệm provenance/gate: [inventory](00_evidence_inventory.md), [review reading note](verification/final_review_reading_note.md), [claim boundary](01_claim_boundary_v0.md); không phải term mới của plant |

**Kiểm brief sau DL-010 (08/10):** 984 từ theo `wc -w`, đủ 15 mục; Main RQ khớp nguyên văn; các EV có trong inventory, liên kết local mở được. PDF dựng lại bằng Pandoc/XeTeX có **2 trang A4**, font DejaVu Serif 11 pt, lề 20 mm, không có dòng tràn hoặc ký tự thiếu. Domain hai neo, phạm vi model repair và conservation null nối đúng contract; không thêm novelty hoặc network evidence. Đây là kiểm tài liệu, chưa là bài tự viết lại hoặc kiểm đọc 5 phút.

**Kiểm sau DL-010 (08/10):** vẫn 25 term, các mục mới ở §9 có nơi quyết; §7(g)–(h) là E0 với giả định ghi tại chỗ. Đã tái lập kiểm hữu hạn bằng [verify_dl010.py](verification/verify_dl010.py): **5.832** cặp action cho bảo toàn (2.048 cặp không idle), **72** trường hợp state/action Markov cho Jensen, **0 vi phạm**; [kết quả](verification/dl010_results.json). Không dùng số Monte Carlo/script tạm trong review làm số đã chạy của repo. Kiểm số hữu hạn không chứng minh định lý cho mọi law và không thay bài tự kiểm của tác giả.

**Cách tái kiểm:** đếm/so ID và term trong bảng §2; đối chiếu thuật ngữ brief bằng mapping trên và T00; tìm `OPEN` rồi nối từng mục tới §9; đọc các section Final Review nêu trên với đúng digest; kiểm lại tổng term. Nếu sửa brief làm xuất hiện khái niệm chưa định nghĩa hoặc đổi quyền thông tin/thang đo, mở lại kiểm 2.

**Đóng băng có điều kiện (08/10/2026).** Theo yêu cầu tác giả đóng Phase 0 và phương án B của [closeout §6](phases/PHASE_0_closeout.md), bản kỹ thuật gồm sửa đổi DL-010 được lưu tại tag `contract-v0`; `phase-0-closeout` ghi GO có điều kiện, mang V3/V10/V11. Đây là ngoại lệ có record đối với điều kiện tự kiểm trước tag ở bản nháp cũ, không ghi các bài tự làm đã hoàn thành. Các lựa chọn DRAFT/OPEN vẫn giữ nhãn bên trong bản đóng băng; thay đổi sau tag cần phiên bản mới và DL. Các lệnh dưới đây được thực hiện ở commit closeout; số contract v1 còn khóa ở L1.8:

```bash
git add notes/01_definitions.md
git commit -m "DL-010: five contract amendments and conditional Phase 0 closeout (B)"
git tag -a contract-v0 -m "Research contract v0 (Phase 0). Numbers locked later in contract-v1 (L1.8)."
git push origin main
git push origin contract-v0
```

Sau khi tag thực sự tồn tại, brief/DL/closeout mới trích `contract-v0`. Nếu đổi contract đã đóng băng, tạo phiên bản mới, ví dụ `contract-v0.1`, kèm DL entry; không di chuyển tag cũ. Ghi tác giả commit là **Doan Van Tai** khi thực hiện; không coi tên tài khoản là byline nghiên cứu.

## Phụ lục Phần 1–3 — tự kiểm và phần việc còn lại

Phụ lục này lưu bài tập và tiến độ của cả ba phần; §0–§10 đã bổ sung. Các mục dành cho tác giả tự làm chưa có record hoàn thành.

### Câu hỏi tự kiểm D1–D12

| Hàng | Điểm cần phân biệt | Câu hỏi tự kiểm |
|---|---|---|
| D1–D2 | Rate theo slot, cost trên cùng cửa sổ $h$ | Vì sao $h$ phải giống nhau cho cả Stay và Switch? |
| D3 | Capacity là parameter cố định trong episode | Nếu capacity tự đổi theo một mode thì nó thuộc nhóm nào? |
| D4 | Mode hiện tại thuộc $x$; law chuyển mode thuộc $\theta$; chuỗi tương lai thuộc $w$ | Xác suất on→off thuộc nhóm nào? |
| D5 | Chuyển traffic phải bảo toàn lượng rời A và đến B | Nếu chỉ tăng tải B mà không giảm tải A thì sai ở đâu? |
| D6 | Phép $[\cdot]^+$ tạo phi tuyến của plant | Ở slot nào thì capacity bị “bỏ phí”? |
| D7 | State tại $t_0$ đủ để sinh tương lai khi biết action và law | Utilization trung bình 1 s có phải state không? |
| D8 | Tuổi observation thuộc state pipeline | Vì sao “thông tin cũ” thuộc về state repair trong contract này? |
| D9 | Mô hình bù tuổi bên trong estimator thuộc $S$ | Ví dụ $\hat q_B=3$ ở L0.3 dạy điều gì? |
| D10 | Hai model cùng $\theta$, khác cách xử lý ngẫu nhiên; $M_0$ load-aware | “$M_0$ không biết $\theta$” đúng hay sai? |
| D11 | Tương lai realized chỉ evaluator biết | Nếu oracle biết $w$ thì regret đo cái gì? |
| D12 | State và observation cùng sinh từ law plant | Ví dụ ghép tuỳ ý nào là không thể xảy ra? |

Hướng dẫn gọi đây là “12 câu hỏi”; bảng được cung cấp có **11 câu**, vì D1–D2 dùng chung một câu. Giữ nguyên nhóm câu hỏi này, không ghi đã hoàn thành 12 câu độc lập. [L0.3 §2](lessons/L0.3_objects.md) đã có ví dụ MẪU để đối chiếu; tác giả chưa tự dựng episode thay thế.

### Các lựa chọn DRAFT cần xác nhận

| Mục | Mặc định đang giữ trong bản nháp | Nơi ghi quyết định |
|---|---|---|
| D3 | Capacity là parameter cố định trong episode | DL-004 đã có DRAFT ở [decision log](02_decision_log.md) |
| D8 | Mode không quan sát được qua telemetry; state thật chỉ diagnostic/oracle | Ghi lý do tại decision entry tương ứng nếu thay giả định telemetry |
| D9 | B2 đã được nêu chọn; schema/cách triển khai và tự kiểm còn chờ | [Ownership Review](PHASE_0_ownership_review.md); DL-008 ở [decision log](02_decision_log.md); nối §7(c) |

Ownership Review ghi nhận tác giả đã nêu chọn B2 và domain hai neo; chưa là record tự kiểm hoặc chốt toàn bộ contract. D3/D8 và chi tiết D9 vẫn cần rà soát; DL-004 và phần còn lại của DL-008 còn DRAFT. Chi tiết schema và cách $M_0/M_1$ dùng belief phải được kiểm cùng repair cards ở Phần 2.

### Tự điền bảng quyền thông tin và phát hiện rò

Tác giả tự điền lại bảng §3 khi không nhìn, so với contract, rồi ghi chỗ khác và lời giải vào `notes/lessons/L0.3_objects.md`, mục “Tự điền bảng quyền thông tin”. Chưa tạo bài làm thay tác giả.

Mỗi tình huống sau vi phạm luật nào?

1. Để tiết kiệm thời gian chạy, code cho $M_1$ dùng chung dòng số ngẫu nhiên với evaluator khi rollout.
2. Ở ô 01, estimator bù tuổi dùng quy luật đầy đủ để ước lượng $q$, còn ở ô 00 thì dùng trung bình.
3. Ô 10 nhận state thật tại $t_0$, và nhận luôn mode tại $t_0+1$ “cho chính xác”.

<details>
<summary>Đáp án tham khảo — chỉ mở sau khi tự làm</summary>

1. Luật 1: rollout của $M_1$ thấy đúng realization tương lai evaluator dùng.
2. Luật 3: estimator khác nhau giữa hai ô cùng $S_0$, nên $G_M$ trộn phần sửa estimator.
3. Luật 1: mode tại $t_0+1$ thuộc tương lai $w$; $S_1$ chỉ được biết state tại $t_0$.

</details>

### Câu hỏi tự kiểm D13–D24

| Hàng | Điểm cần phân biệt | Câu hỏi tự kiểm |
|---|---|---|
| D13 | Cộng cả hai queue và cả thời gian chờ của packet chưa xong | Với X: 2, 1, 1 và Y: 1, 1, kẹt 3, mỗi metric chọn action nào? |
| D14 | Kỳ vọng theo tương lai đánh giá chất lượng quyết định, không đánh giá may rủi | Một action tốt gặp tương lai xấu: regret bằng bao nhiêu? |
| D15 | Oracle biết hiện tại và law, không biết tương lai realized | Oracle nhìn trước tương lai sẽ phạt twin vì điều gì? |
| D16 | Luật quyết định và tie rule viết trước, giống nhau ở mọi ô | Khi $\widehat\Delta=0$ mà $\Delta<0$ thì mất bao nhiêu? |
| D17 | Dấu gap quyết định action, margin quyết định tổn thất khi chọn sai | Vì sao dự đoán sai +10/+15 vẫn có thể cho regret 0? |
| D18 | $L$ là expected cost, $R$ là phần dư so với cùng oracle | Vì sao hiệu giữa các $L$ bằng hiệu giữa các $R$? |
| D19 | Gain có điều kiện xét phép sửa khi phép kia đã làm | Trong ví dụ 20/18 với $e_S=e_M=3$, $G_{S\mid M_1}$ bằng bao nhiêu? |
| D20 | State repair đầy đủ gộp ba thay đổi, không chỉ freshness | Ba thành phần đó là gì? |
| D21 | Chỉ đổi $M$, giữ nguyên cả mô hình bên trong estimator | Nếu estimator bù tuổi cũng đổi theo thì $G_M$ đo cái gì? |
| D22 | Ô phụ tách tươi hơn khỏi thấy mode, không thuộc primary | Vì sao ô này không nằm trong primary estimand? |
| D23–D24 | Ngưỡng tương đối chọn trước; kiểm tương đương khác kiểm khác biệt | Vì sao “p > 0,05” không chứng minh tương đương? |

Bảng có 11 nhóm câu hỏi bao phủ 12 term, vì D23–D24 dùng chung một câu. Ví dụ X/Y và phản ví dụ bù sai số đã có mẫu/bài tập ở [L0.4](lessons/L0.4_estimand.md); chưa ghi nhận tác giả đã trả lời.

### Lựa chọn Phần 2 và bài tập đọc estimand card

- **D13:** mặc định primary packet·s, kèm bản quy đổi ms/packet. Nếu chuyển ms/packet thành primary, đặc tả mẫu số, reference cost và ghi DL-005 trước khi dùng kết quả.
- **D22:** giữ ô phụ trong bản nháp; có thể bỏ với lý do, khi đó mất một diagnostic để tách freshness khỏi mode visibility.
- **D23–D24:** giữ OPEN; chưa điền ngưỡng hoặc reference cost.
- **§7/B2:** B2 đã được nêu chọn trong Ownership Review; vị trí giữ §7, chi tiết belief và bài tự kiểm còn chờ, chưa chốt toàn bộ DL-008.

Tự nghĩ một bộ số cho mỗi hàng “Đọc kết quả” ở §4. Với ví dụ thay thế $G_S=G_M=1$, $G_{SM}=1{,}9$, $\Gamma=-0{,}1$: sửa một cái đã đủ chưa? So gain riêng với gain chung và ngưỡng đã khai báo; không suy “một cái đủ” chỉ từ dấu âm của $\Gamma$.

Câu hỏi construct validity ở §4 dành cho người đọc độc lập; chưa có record gửi hoặc phản hồi trong lần bổ sung này.

### Bài tập phản biện §7

Ghi lời giải của tác giả vào [L0.4 §5](lessons/L0.4_estimand.md), đã có khung ở File 8; chưa tạo record bài làm thay tác giả.

1. **(a), một dòng:** vì sao $\ell_{01}(e)\ge\ell_{11}(e)$ trong mọi episode?
2. **(b):** dựng một episode cho $\gamma=0$ và một episode cho $\gamma=2\lvert\Delta\rvert$. Ghi rõ ô nào sai.
3. **(e):** tự chứng minh vế thứ hai, $\Gamma=G_{M\mid S_1}-G_M$.
4. **(c), khó:** chứng minh $G_M\ge0$ khi belief là posterior chính xác và prior khớp $D$. Gợi ý: với cùng thông tin $I$, quyết định Bayes làm nhỏ nhất $\mathbb E[J(a)\mid I]$ trong mọi luật chỉ dùng $I$; ô 00 cũng là một luật chỉ dùng $I$. Nếu belief chỉ xấp xỉ, bước nào của chứng minh bị gãy?

Nếu bác được (c) trong đúng các giả định, phải sửa §7(c), EV-27, NC13 và brief tương ứng; không bỏ qua phản ví dụ. Primary-literature check về value-of-information ở Phase 2 vẫn cần làm, dù các bất đẳng thức đã được kiểm bằng toán.

### Tự kiểm scope và assumptions

| ID | Giả định cho phép điều gì | Lý do chấp nhận trong nghiên cứu đầu |
|---|---|---|
| AS1 | Dùng chung arrivals cho Stay và Switch, cùng $w$ | Cô lập cơ chế queue trước khi thêm feedback TCP |
| AS2 | Tính chính xác từ hai chuỗi Markov riêng | Correlation là cơ chế khác, kiểm sau |
| AS3 | Biên rỗng là nguồn phi tuyến duy nhất của plant | Một cơ chế tại một thời điểm |
| AS4 | Diagnostic đơn giản, action hiệu lực ngay | Delay thuộc feasible repair/RQ3 |
| AS5 | Điều chỉnh persistence qua tham số Markov | Tạo quá trình có nhớ với state gọn |
| AS6 | Không lẫn state với parameter | Đã đặt lựa chọn ở D3 |
| AS7 | Không cần mô hình shared link | Shared link kiểm ở Phase 7 |
| AS8 | Dùng $(q,m)$ làm state Markov đủ | Với mạng thật, đây là limitation cần nêu |
| AS9 | Action có kích thước xác định | Burst managed traffic kiểm sau |

Tác giả tự viết lại câu scope, chọn assumption rủi ro nhất kèm lý do và ghi vào `notes/lessons/L0.6_scope.md`. Không dùng “mọi mạng”, “tổng quát”, “thực tế” thiếu điều kiện. Nếu thêm giả định AS10, ghi đủ dấu hiệu khi sai, nơi kiểm và lý do; có thể tự xét giả định thời gian giữ action bằng horizon. Chưa tạo record bài làm thay tác giả.

### Chuỗi năm bước HC1/HP1 — gợi ý thiết kế, chưa là bài tác giả tự viết

| Hypothesis | Observation | Possible mechanism | Prediction | Hypothesis | Falsification |
|---|---|---|---|---|---|
| HC1 | Cùng cost, thay error/mixture đổi $\Gamma$ (EV-01/25) | Ngưỡng quyết định biến sai số gap thành đổi action; queue có thể thêm phụ thuộc regime | Tọa độ trước action dự báo conditional gains khác nhau | Bản đồ đóng băng tốt hơn dự đoán hằng trên held-out | Không vượt dự đoán hằng theo phép chấm/biên đã khóa; không chọn nhóm bằng state ẩn |
| HP1 | Oracle repair riêng không chặn feasible gain (EV-26); timing có thể hạn chế backlog (EV-28/29) | Bù sai số và thay đổi state trong lúc chờ làm diagnostic gain khác net gain thực tế | Ở một miền có $R_{00}$ đủ lớn, operator khả thi còn lợi ích sau delay/cost | Net gain vượt ngưỡng và baseline mạnh trên cùng thang | Cận trên net gain dưới ngưỡng hoặc cận trên lợi thế so baseline không dương; CI rộng là chưa kết luận |

Đây là chuỗi thiết kế có thể bị bác, không phải bằng chứng cơ chế/gain đã xảy ra. Tác giả còn tự viết lại toàn brief, dựng chuỗi HC1/HP1 và làm bài đọc 5 phút nếu chọn. V11 chưa được đánh dấu đạt; không đưa bảng này vào brief làm vượt ngân sách đọc.

### Câu hỏi tự kiểm DL-010

1. Hai queue A, B có $c_A=c_B=3$, $u=2$, $q_{A,0}=q_{B,0}=10$, $H=2$, $\Delta t=1$; arrivals nền $b_A=(2,2)$, $b_B=(1,1)$. Tính $C(\text{Stay})$ và $C(\text{Switch})$. Có queue nào idle không? Vì sao hai cost bằng nhau?
2. Giữ nguyên câu 1 nhưng $q_{B,0}=0$, $b_B=(0,0)$. Tính lại hai cost, chỉ ra slot nào bỏ phí capacity và kiểm công thức $\Delta t\sum_j (H-j)[I_j(\text{Switch})-I_j(\text{Stay})]$.
3. Vì sao $G_M$ trong contract không trả lời được câu “twin của tôi ước lượng sai rate on/off thì thiệt bao nhiêu”?
4. Nếu đổi $\Delta t$ từ 10 ms xuống 5 ms mà vẫn giữ “xác suất rời mode mỗi slot = 0,1”, persistence vật lý đổi thế nào?

<details>
<summary>Đáp án tham khảo — chỉ mở sau khi tự làm</summary>

1. Stay: A $10\to11\to12$, B $10\to8\to6$, $C=11+12+8+6=37$. Switch: A $10\to9\to8$, B $10\to10\to10$, $C=9+8+10+10=37$. Không queue nào idle, nên tổng backlog đi y hệt nhau (§7g ii).
2. Stay: A $10\to11\to12$, B $0\to0\to0$ với B bỏ phí 3 mỗi slot; $C=23$. Switch: A $10\to9\to8$, B $0\to0\to0$ với B bỏ phí 1 mỗi slot; $C=17$. $I(\text{Stay})=(3,3)$, $I(\text{Switch})=(1,1)$; công thức: $2(1-3)+1(1-3)=-6=17-23$. Switch tốt hơn vì dùng capacity B đang bỏ phí.
3. Vì $M_0$ và $M_1$ cùng biết $\theta$ đúng (D21); sai rate là sai tham số, ngoài estimand.
4. Thời gian lưu trung bình khoảng $\Delta t/0{,}1$: từ 100 ms còn 50 ms. Mode “nhớ” ngắn đi một nửa chỉ vì đổi slot — đúng loại chỉnh nhân tạo quy tắc 7 cấm.

</details>

### Kiểm tiến độ

- [x] Khối 1–5 đã được tích hợp: đầu file, §0–§3, D1–D12 và quyền thông tin.
- [x] DL-010: năm sửa đổi bắt buộc đã đưa vào D1, D13, D21, §0, §5, §6 (quy tắc 7–8), §7(f)–(h), §8 AS3, §9; chờ tác giả rà và làm 4 câu tự kiểm ở trên.
- [ ] Tác giả trả lời được toàn bộ câu hỏi tự kiểm D1–D12.
- [ ] Tác giả xác nhận giữ hay đổi D3, D8, D9 và ghi lý do khi đổi.
- [ ] Tác giả tự điền bảng quyền thông tin và làm bài phát hiện rò trong L0.3.
- [x] Phần 2: D13–D24 đã nối cùng bảng, §4 estimand card, §5 repair cards, §6 quy tắc, §7 hệ quả biết trước đã bổ sung.
- [ ] Tác giả trả lời được toàn bộ câu hỏi tự kiểm D13–D24.
- [x] Ghi nhận lựa chọn B2 làm baseline chính và domain hai neo từ Ownership Review ngày 08/10; chưa thay bài tự kiểm.
- [ ] Tác giả xác nhận D13 (đơn vị), D22 (ô phụ), chi tiết B2/sensitivity B1 và vị trí giữ §7; ghi quyết định tương ứng.
- [ ] Tác giả làm ít nhất bài 1–3 phản biện §7, sau đó bài 4 về Bayes-optimal nếu kịp.
- [x] Phần 3: D25, ngân sách 25 term, §8 scope/assumptions, §9 mục còn mở, §10 kiểm nhất quán đã bổ sung.
- [ ] Tác giả viết lại scope và xác nhận assumption rủi ro nhất kèm lý do.
- [x] T00 đã có trục quét 5 ms–30 s, hai neo (a)/(b), nguồn literature và provenance AoI lịch sử; 10 test timescale đạt, ma trận 40 ô và bảng chi tiết đã đối chiếu.
- [x] File 7: brief đã có, phép kiểm 2 được đối chiếu kỹ thuật với mapping thuật ngữ và cập nhật §10.
- [x] File 8: khung note L0.3–L0.7 đã có, mẫu đối chiếu và ô chưa làm được phân biệt; chưa tính là bài tự làm hoặc gate đạt.
- [ ] Tác giả tự kiểm thuật ngữ, viết lại brief và dựng chuỗi HC1/HP1 bằng lời mình; xác nhận các lựa chọn DRAFT.
- [ ] Tác giả kiểm toàn bộ nội dung và cập nhật nguồn gốc trước khi đóng băng/tag; commit bản nháp theo File 7 không thay bước này.
- [x] Đóng băng bản kỹ thuật `contract-v0` và `phase-0-closeout` theo DL-009/phương án B; V3/V10/V11 là điều kiện còn mở, không được tính PASS.

**Ownership:** xem [review và bảng việc chưa hoàn thành](PHASE_0_ownership_review.md); V3/V10/V11 còn mở.

**Gate:** V4/V5 có định nghĩa và quy tắc ở mức tài liệu; V6 có mapping/estimand card; V7 có repair cards nhưng vẫn có điều kiện vì $S_1$ gộp ba thành phần và chi tiết belief chưa chốt; V8 có scope và danh sách mục mở với nơi quyết. Không ghi các gate này là tác giả đã tự kiểm đạt. Phase 0 đóng **có điều kiện theo B**, V3/V10/V11 mang sang; các con số vẫn khóa ở contract v1 (L1.8).
