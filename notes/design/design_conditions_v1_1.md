# Điều kiện thiết kế v1.1 (ĐK1–ĐK8) — B1 và supplement mốc2

> **Provenance.** Soạn bởi **Claude (AI) theo yêu cầu của Doan Van Tai**, 22/10/2026, sau mock review lưới v1 và [DL-026](../02_decision_log.md). Mọi lựa chọn dưới đây là **AI đề xuất, chờ tác giả xác nhận** (danh sách ở §11). File này **không** là understanding artifact V11 của tác giả.
>
> **Tích hợp và chạy kiểm chứng:** **Doan Van Tai**, **23/10/2026**. Attribution nguồn giữ nguyên; các sửa kỹ thuật/lập luận khi tích hợp được ghi ở §12 và [báo cáo B1](../../results/lessons/l1_8_v1_1_b1/report.md). Yêu cầu “tiếp tục” cho phép triển khai B1, không tự xác nhận bảy lựa chọn nghiên cứu ở §11.
>
> **Vai trò.** Đây là bước **B1** của quy trình v1.1 (§10). File này phải được commit **trước** mọi tính toán trên lưới v1.1 — kể cả screen ĐK1 trên ô ứng viên và chẩn đoán $p_{\text{sw}}$ của ĐK2. Không có con số lưới nào được chọn ở đây.
>
> **Quan hệ với v1.** Tag `contract-v1` giữ nguyên, không di chuyển. Lưới v1 vẫn là bản lịch sử, có lỗi thiết kế đã biết (DL-026); A01/A04 trên lưới v1: HOLD.

## 0. Sự thật làm nền (đã kiểm, chỉ dùng tham số)

| Sự thật | Cách kiểm |
|---|---|
| Ở M01–M12 và S01, $q_A(t_0)=\max(0,\,y_A-(5-u)\cdot\text{age})=0$ và lượng đến A dưới capacity ở cả hai action, nên Stay áp đảo Switch trên mọi path; cả bốn pipeline chọn Stay; mọi contrast bằng 0 theo cấu trúc | `tests/test_dominance_v1_1.py::test_v1_grid_classification_documents_dl026` (support của $D$ đã có, không tính $J$) |
| Cả ba ô calibration của v1 (M01, M02, M10) thuộc nhóm trên | Cùng test |
| N01, N02 là vùng bảo toàn (khớp $s_{bt}=1$ của report CDE) | Cùng test |
| M13–M24, S02: ĐK1 không kết luận được (nhãn `candidate`) | Cùng test — đây là lý do cần ĐK2 |
| Ở mọi ô v1, $\psi=(\lambda_A-\lambda_B)/\mu=(5-8)/10=-0{,}3$ | Đại số (§ĐK5) |
| Repo chưa tính $J$, gap, margin hay contrast nào trên ô lưới v1 | `results/lessons/l1_8_cde` chỉ có support của $D$ và $s_{bt}$; `golden_costs.csv` chỉ có state của ví dụ chuẩn |

## 1. Ba tầng của "không suy biến"

| Tầng | Câu hỏi | Screen |
|---|---|---|
| 1 | Hai action có cost khác nhau ở đâu đó không? | $s_{bt}$ (v1, giữ) |
| 2 | Cả hai action có lúc là tối ưu không? | **ĐK1** (giải tích) và **ĐK2** ($p_{\text{sw}}$) |
| 3 | Pipeline có chọn khác oracle không? | Không screen — đây là outcome của Phase 3 |

Lỗi của v1: chỉ có tầng 1. "Có queue idle" không có nghĩa là "có bài toán quyết định".

## ĐK1 — Screen áp đảo giải tích, cả hai chiều

**Trực giác.** Switch chỉ làm hai việc: giải phóng $u$ capacity mỗi slot trên A và tiêu thụ $u$ trên B. Nó chỉ có lợi khi capacity giải phóng trên A *đang cần* (A có backlog dưới Stay) **và** capacity tiêu thụ trên B *vốn bỏ phí* (B idle dưới Stay). Stay đối xứng.

**Công cụ.** Trên cùng tương lai $w$, đặt $\Delta Q_k=Q_k(\text{Switch})-Q_k(\text{Stay})$ (tổng backlog cuối slot $k$). Theo contract §7(g):

$$
C(\text{Switch},w)-C(\text{Stay},w)=\Delta t\sum_{k=1}^{H}\Delta Q_k,\qquad \Delta Q_k=\sum_{j<k}\big[I_j(\text{Switch})-I_j(\text{Stay})\big].
$$

Recurrence $q'=[q+a-c]^+$ đơn điệu: Switch làm backlog A không tăng, backlog B không giảm; idle A không giảm, idle B không tăng, ở mọi slot.

**Bốn điều kiện đủ** (mọi path có xác suất dương, các slot $0..H-1$):

| Tên | Điều kiện | Path cực trị dùng để kiểm | Kết luận |
|---|---|---|---|
| SD1 | B không thể idle dưới Stay | Ít arrival nhất của B | $C(\text{Sw},w)\ge C(\text{St},w)\ \forall w$ |
| SD2 | Backlog A cuối mọi slot $k\ge1$ bằng 0 dưới Stay | Nhiều arrival nhất của A | $C(\text{Sw},w)\ge C(\text{St},w)\ \forall w$ |
| WD1 | A không thể idle dưới Switch | Ít arrival nhất của A | $C(\text{Sw},w)\le C(\text{St},w)\ \forall w$ |
| WD2 | Backlog B cuối mọi slot $k\ge1$ bằng 0 dưới Switch | Nhiều arrival nhất của B | $C(\text{Sw},w)\le C(\text{St},w)\ \forall w$ |

SD1 ∧ WD1 là vùng bảo toàn: $\Delta\equiv0$.

**Chứng minh.**
- *SD1.* $I_B(\text{St})=0$ ở mọi slot, nên $I_B(\text{Sw})=0$; $\Delta I_A\ge0$. Vậy $\Delta I_j\ge0$, nên $\Delta Q_k\ge0$.
- *SD2.* $q_{A,k}(\text{St})=0$ với $k\ge1$ kéo theo $q_{A,k}(\text{Sw})=0$, nên $\Delta q_{A,k}=0$; $\Delta q_{B,k}\ge0$. Vậy $\Delta Q_k\ge0$.
- *WD1.* A không idle dưới cả hai action, nên $\Delta q_{A,k}=-k\,u$. Với B: $\Delta q_{B,k}=k\,u+\sum_{j<k}\Delta I_{B,j}\le k\,u$. Vậy $\Delta Q_k\le0$.
- *WD2.* Gương của SD2: $\Delta q_{B,k}=0$, $\Delta q_{A,k}\le0$.
- *Bảo toàn.* SD1 ∧ WD1: $\Delta Q_k=-k\,u+k\,u=0$.

**Hai path cực trị là đủ.** Path ít arrival nhất (mode slot 0 thuộc state, rồi mode có rate nhỏ nhất) idle nhiều nhất ở mọi slot; path nhiều arrival nhất (rồi mode có rate lớn nhất) có backlog lớn nhất. Điều kiện: từ slot 1 mọi chuyển mode có xác suất dương (R2 với $T_{\text{mode}}$ hữu hạn), hoặc queue chỉ có một mode. Kiểm idle bằng bất đẳng thức chặt $q+a<c$.

**Pipeline cũng tuân theo.** $M_0$ chạy một path trung bình nằm giữa hai path cực trị, nên cùng điều kiện đúng; $M_1$ là trung bình cost thật; belief lấy trung bình theo state. Nếu **mọi** state trong support thoả cùng điều kiện thì mọi ô dự đoán cùng dấu.

**Bất đối xứng do luật hoà (Stay khi hoà).**
- Ô **SD** ($m_{SD}=1$): cả bốn pipeline chọn Stay, sáu contrast bằng 0 chính xác. Là **ô kiểm âm hợp lệ**.
- Ô **WD** ($m_{WD}=1$): oracle chọn Switch (hoặc Stay khi thật sự hoà), nhưng $M_0$ có thể dự đoán **hoà** khi sự thật nghiêng về Switch, rồi chọn Stay và có regret. Ví dụ đã kiểm chính xác (test `test_tie_rule_makes_wd_cells_not_zero_controls`): A bão hoà, B nền OFF 1 / ON 5 với capacity 3, $H=3$, state $(10,\text{on},0,\text{on})$: $J(\text{Stay})=109/2$, $J(\text{Switch})=54$; $M_0$ cho 54 và 54. Ở ô WD, $G_{S\mid M_1}=0$ nhưng $G_M$ có thể dương. **Ô WD không phải ô kiểm âm**; nhãn: "oracle-hằng".

**Từ state lên ô.** Trên support của $D$: $m_{SD}$ = khối lượng state có SD1 hoặc SD2; $m_{WD}$ tương tự; nhãn ô `SD-cell`, `WD-cell`, `conservation-cell` hoặc `candidate`. Hệ quả: $p_{\text{sw}}\le1-m_{SD}$.

**Giới hạn.** Bốn điều kiện chỉ là điều kiện **đủ**. Ô `candidate` vẫn có thể có oracle gần như luôn chọn một action → cần ĐK2.

Khi cộng mass bằng floating point, `m_SD` có thể bị làm tròn thành 1 dù còn state không-SD có probability dương rất nhỏ. Vì vậy `cell_label` phải dùng thêm chứng chỉ trên **mọi state probability>0**; `tol` không là ngưỡng bỏ support. Support rỗng/zero-mass bị từ chối. Một state có mass 10⁻⁴⁰ vẫn chặn nhãn SD nếu không thỏa SD.

**Code và kiểm.** `src/smr/dominance.py`. Lưới nguồn có9.216 state-parameter configurations nhưng SD2/WD2 không bao giờ kích hoạt (ON+u>capacity trong mọi case H≥2), nên không thể gọi đó là kiểm đầy đủ bốn điều kiện. Tích hợp23/10 giữ nguyên9.216 ca này và thêm3.456 ca low-arrival/H1, tổng12.672 cases/116.352 cặp path; test yêu cầu từng SD1/SD2/WD1/WD2 có coverage dương và đúng cả path-wise lẫn M0. Dạng đóng đối chiếu rollout, ba mutant kiểm bằng assertion thực; kết quả cuối ở report B1. Đây là verification toy, không thay lưới nghiên cứu.

## ĐK2 — Chẩn đoán chỉ dùng plant: $p_{\text{sw}}=P_D(a^*=\text{Switch})$

**Định nghĩa.** $p_{\text{sw}}=\sum_x D(x)\,\mathbf 1\lbrace J(\text{Switch};x)<J(\text{Stay};x)\rbrace$ — bất đẳng thức chặt vì hoà chọn Stay. Chỉ dùng $J$ của plant (truy hồi ngược `smr.exact.value_backward`). **Không** dùng belief, $M_0$ hay pipeline nào. Phương pháp kiểm chứng dấu phải chốt trước B3: R2 chứa exp nên transition probabilities nói chung không hữu tỉ; `Fraction(float_P)` chỉ cho số học chính xác của **law đã rationalize**, không tự là law R2 vật lý chính xác. B1 chưa triển khai/chạy ĐK2 và không chọn ngầm cách xấp xỉ law.

**Vì sao là điều kiện cần cho RQ.** Nếu $a^*$ không đổi trên support của $D$, thông tin state không đổi được quyết định của oracle, nên $G_{S\mid M_1}=0$. Mỗi ô có một observation nên ô $S_0M_1$ chọn một action cho cả ô; quyết định Bayes chọn regret nhỏ hơn, do đó:

$$
G_{S\mid M_1}\le\min(p_{\text{sw}},\,1-p_{\text{sw}})\cdot\max_x\lvert\Delta(x)\rvert .
$$

**Khoảng chấp nhận (đề xuất):** $p_{\text{sw}}\in[0{,}1;\ 0{,}9]$. Ngoài khoảng, giá trị thông tin state không vượt 10% margin lớn nhất của ô.

Đây là convention về mức lệch của oracle, không chứng minh effect vượt εR. Ngoài khoảng nhưng 0<p_sw<1 thì oracle **gần hằng/lệch**, không thật sự hằng. Ngược lại, p_sw trong khoảng vẫn không đủ chứng minh State gain>0: oracle có thể chọn Stay chỉ ở state hòa và chọn Switch ở phần còn lại, trong khi Switch yếu áp đảo toàn support. Không thêm screen pipeline/margin hoặc near-tie rate để loại các ô như vậy; báo giới hạn này khi đọc A04.

**Bảy luật chống chọn lọc hậu nghiệm.**
1. Khoảng chấp nhận, mức $\Delta t$ dùng để tính và các luật này được commit trong file này, **trước** khi tính $p_{\text{sw}}$ cho bất kỳ ô nào.
2. Chỉ tính $p_{\text{sw}}$. Không xem độ lớn margin, không tính $L_*$, không chạy pipeline. Không tính tỉ lệ gần hoà.
3. Ô ngoài khoảng **giữ nguyên trong lưới**, gắn nhãn "oracle-hằng", báo cáo đầy đủ; không xoá, không di chuyển.
4. Lưới được chấp nhận khi ít nhất 2/3 số ô vai trò `main` nằm trong khoảng. Nếu không đạt: thiết kế lại các mức của trục tải A (ĐK5) **tối đa một lần**, ghi DL, rồi chạy lại đúng các luật này. Không lặp lại lần thứ hai; nếu vẫn không đạt thì ghi NARROW/REFORMULATE.
5. Không tính $p_{\text{sw}}$ trên reserve; reserve chỉ chạy ĐK1.
6. Ghi exposure register: ô, mức $\Delta t$, ngày, giá trị $p_{\text{sw}}$.
7. Ở mức phân giải A01 chấp nhận, tính lại $p_{\text{sw}}$ cho ô calibration; ô vượt khoảng thì đổi nhãn, không di chuyển.

**Trạng thái prerequisite:** khoảng/tiêu chí vẫn là đề xuất §11; Δt screen chưa chọn, phương pháp tính dấu R2 chưa khóa. B3 vì vậy **HOLD**. Trước B3 phải có commit chốt các mục này, bổ sung file điều kiện và ghi DL; không diễn giải bản B1 DRAFT là preregistration hoàn tất. Khi p_sw ở0/1 dùng nhãn oracle-hằng; khi chỉ ngoài khoảng dùng nhãn oracle-lệch/gần-hằng và giữ giá trị thật. Quy tắc giữ mọi ô và tối đa một lần thiết kế lại không đổi.

**Đổi quy tắc của v1 và lý do.** `grid_v1.md` cấm tính giá trị action thật để chọn thiết kế. ĐK2 nới quy tắc đó **chỉ cho $p_{\text{sw}}$**: nó đo sự *tồn tại* của bài toán quyết định (giống $s_{bt}$ đo sự tồn tại của chênh lệch cost), không đo contrast. Rủi ro còn lại được khống chế bằng bảy luật trên. Ghi ở DL-027.

## ĐK3 — Tách $y_A$ khỏi $y_B$

Backlog A lớn đẩy về Switch, backlog B lớn đẩy về Stay: hai thành phần của "current queue state" trong RQ1 tác động **ngược chiều**. $y_A=y_B$ làm chúng không tách được.

- Hai toạ độ riêng. Mức của mỗi $y$ chọn theo **quantile của phân phối backlog dừng của chính queue đó** trước quyết định (A dưới Stay, có $u$; B không có $u$). Quantile $\alpha$: giá trị lưới nhỏ nhất có CDF $\ge\alpha$. Mức cụ thể chọn ở B2 (đề xuất q50 "bình thường", q90 "đang nghẽn").
- Lý do dùng quantile: nhất quán với $D$ dừng có điều kiện (quan sát là giá trị có xác suất thật, không phải giá trị hiếm), và có nghĩa vận hành rõ.
- Vẫn tính và báo $z_A$, $z_B$ như tỉ số timescale. Quantile phụ thuộc $\kappa$ và tải: đó là chủ ý — toạ độ là *mức điển hình*.

## ĐK4 — Tách $h$ khỏi $z$

Lưới v1 đặt $h=z/(1-\eta)$, nên trong cùng $\eta$, $h$ tỉ lệ thuận hoàn toàn với $z$ và trục "decision horizon" của RQ1 biến mất.

- Toạ độ riêng $r_h=h/T_{\text{drain}}^{\text{post},B}$, với $T_{\text{drain}}^{\text{post},B}=y_B/(\mu-\lambda_B-\delta\lambda)$ tính từ backlog **quan sát** (biết trước action). Ít nhất hai mức; mức cụ thể chọn ở B2 (đề xuất bao quanh 1, ví dụ 0,5 và 2–3).
- Phương án thay thế: $h/(\tau_{\text{eff}}+d_{\text{act}})$. Chọn một ở B2, ghi lý do.
- Ô có $\eta\ge1$ ($T_{\text{drain}}^{\text{post}}$ vô hạn): giữ quy tắc dự phòng của v1 ($h=T_{\text{drain}}^{\text{pre}}$), ghi nhãn stress.

## ĐK5 — Trục tải của A

**Vì sao cần trục tải A.** Với capacity bằng nhau:

$$
\psi=\rho_A^{\text{Stay}}-\rho_B^{\text{Switch}}=\frac{\lambda_A+u}{\mu}-\frac{\lambda_B+u}{\mu}=\frac{\lambda_A-\lambda_B}{\mu}.
$$

$u$ triệt tiêu. Ở v1, $\psi=-0{,}3$ ở mọi ô: A có tải nền trung bình thấp hơn B. Đây là lý do kiểm thêm trục tải, **không** là chứng minh Stay tối ưu ở các ô ĐK1 chưa kết luận; chi phí còn phụ thuộc backlog, mode, biến thiên và horizon. Ý tưởng đặt các mức quanh $\psi\approx0$ vẫn là lựa chọn thiết kế, chưa có outcome của lưới v1.1.

**Điều kiện.**
1. $\psi$ là trục thiết kế, các mức **nằm hai phía của 0** (ít nhất một mức âm, một mức dương).
2. **A có nền ON/OFF Markov**, cấu trúc giống B. Lý do: nếu A tất định với $\rho_A^{\text{Stay}}<1$ thì A dừng luôn rỗng; áp nhất quán $D$ dừng có điều kiện cho A sẽ cho $y_A=0$ và SD2 đúng ở mọi ô — cả lưới bị áp đảo. Phương án yếu hơn (khai báo $y_A$ là transient có kiểm soát) chỉ dùng nếu tác giả chọn rõ và ghi lý do.
3. $D$ dừng có điều kiện cho **cả hai** queue, độc lập cho trước $(y_A,y_B)$; belief của $S_0$ chung trên mode của cả hai. Không mặc định A có cùng dạng đóng như B: nếu dùng solver số phải kiểm cân bằng dòng, chuẩn hóa **và kiểm soát sai số đuôi/truncation**; residual trên một queue bị cắt hữu hạn chưa đủ chứng nhận law vô hạn. Chưa chọn/chạy solver ở B1.
4. Nếu A dùng prior dừng: $\rho_A^{\text{Stay}}=(\lambda_A+u)/\mu<1$.
5. Ở ô chính, rate ON của A cộng $u$ vượt $c_A$ (A có thể tích backlog trong đợt ON).
6. Mode A dùng cùng $\kappa$ với B (tránh thêm trục); ghi rõ.

## ĐK6 — Ô kiểm âm và ô gắn nhãn

1. Ít nhất một **ô SD2** (A nhẹ: rate ON của A cộng $u$ không vượt $c_A$, $y_A=0$) và một **ô SD1** (backlog B đủ lớn để B không thể idle dưới Stay trong horizon). Điều kiện chấp nhận: ĐK1 cho nhãn `SD-cell`.
2. Kỳ vọng khai báo trước cho ô SD: cả bốn pipeline chọn Stay ở mọi episode; sáu contrast **bằng 0 chính xác**; mọi regret bằng 0. Sai lệch là bug, không phải phát hiện.
3. Giữ hai ô bảo toàn kiểu N01/N02 (nhãn `conservation-cell`; $\Delta\equiv0$).
4. Tuỳ chọn một ô **WD** làm đầu dò luật hoà, gắn nhãn rõ; kỳ vọng $G_{S\mid M_1}=0$, $G_M$ không bắt buộc bằng 0. Không gọi là kiểm âm.

## ĐK7 — Calibration

1. Chỉ chọn trong ô `main` có nhãn ĐK1 là `candidate` **và** $p_{\text{sw}}$ trong khoảng chấp nhận.
2. Trong số đó: một ô $\kappa$ nhỏ nhất (sai số E2 lớn nhất), một ô có $T_{\text{drain}}/\Delta t$ nhỏ nhất (E1 lớn nhất), một ô trung tâm. Hoà thì chọn id nhỏ nhất.
3. Khai báo trước A01; ghi exposure. Ô calibration không dùng làm confirmation.

## ĐK8 — Những gì không đổi so với contract v1

$\varepsilon_R$ chính 1% (0,5% và 2% là độ nhạy); $\varepsilon_E$ 0,5%; dung sai làm mịn 0,25%; $C_{\text{ref}}=L_*$ theo ô và theo mức; luật R2; B2 với prior bằng $D$; objective cumulative occupancy và quy đổi; luật hoà Stay; ba luật chống rò; quy ước stream. Danh sách này là bằng chứng bản sửa nhắm vào **thiết kế lưới**, không chỉnh **thước đo**.

## 9. Khung lưới (cấu trúc; số chọn ở B2)

Lõi factorial + nan hoa, tổng không quá khoảng 30 ô:

| Phần | Cấu trúc | Số ô |
|---|---|---:|
| Lõi | $\psi$ (3 mức, hai phía của 0) × $\kappa$ (3 mức) × $y_B$ (2 mức quantile); cố định $y_A$ ở mức "nghẽn", một mức $r_h$, một mức $\eta$ | 18 |
| Nan hoa quanh ô trung tâm | $y_A$ mức thứ hai; $r_h$ hai mức khác; $\eta$ mức thứ hai | 4 |
| Kiểm âm | 1 SD2, 1 SD1, 2 bảo toàn | 4 |
| Tuỳ chọn | 1 WD (đầu dò), 1 stress $\eta>1$ | 0–2 |
| Reserve | Mức xen giữa và một khối ngoại suy; chỉ khai báo + ĐK1 | — |

Mỗi dòng của `grid_v1_1.json`: id, vai trò, $\psi$, nền A và B (OFF/ON), $\kappa$, $T_{\text{mode}}$, mức và giá trị $y_A$, $y_B$, $z_A$, $z_B$, $\eta$, $u$, $r_h$, $h$, $\Delta t$ ứng viên, $m_{SD}$, $m_{WD}$, $p_{\text{sw}}$, nhãn.

## 10. Quy trình và thứ tự commit

```text
B1  file này + DL-026/027/028 + dominance.py + test         → commit   (mốc 1)
B2  lưới ỨNG VIÊN (số theo §9) + ĐK1 cho mọi ô kể cả reserve → commit
B3  ĐK2 (p_sw) cho ô lõi và nan hoa, đúng bảy luật           → commit + exposure
B4  áp luật → chốt lưới, kiểm âm, calibration                 → commit + DL
B5  sáu kiểm nhất quán (năm kiểm §10 contract + ràng buộc chéo) → tag contract-v1.1
B6  A01 trên calibration mới
```

Kiểm thứ tự: `git merge-base --is-ancestor <commit B1> <commit B3>`.

**Checklist trước tag `contract-v1.1`:**
- [ ] B1 commit trước mọi tính toán trên lưới mới
- [ ] Test ĐK1 (vét cạn, $M_0$, luật hoà, phân loại v1) xanh
- [ ] ĐK1 chạy cho mọi ô kể cả reserve; ĐK2 chỉ cho lõi và nan hoa
- [ ] Không ô nào bị xoá; tối đa một lần thiết kế lại trục A, có DL
- [ ] Calibration là `candidate` và trong khoảng chấp nhận
- [ ] Ô SD có kỳ vọng "sáu contrast bằng 0 chính xác" viết trước
- [ ] Danh sách ĐK8 khớp contract v1
- [ ] Exposure register cập nhật

## 11. Lựa chọn B1 và trạng thái mốc2

| # | Lựa chọn | Đề xuất | Phương án khác |
|---|---|---|---|
| 1 | Khoảng chấp nhận $p_{\text{sw}}$ | $[0{,}1;\ 0{,}9]$ | $[0{,}05;\ 0{,}95]$ (lỏng hơn) |
| 2 | Tiêu chí chấp nhận lưới | ≥ 2/3 ô `main` trong khoảng; tối đa một lần thiết kế lại | Mọi ô lõi trong khoảng (chặt hơn, dễ phải chỉnh nhiều) |
| 3 | Mô hình A | Nền ON/OFF Markov, cùng $\kappa$ với B | A tất định + $y_A$ transient có kiểm soát |
| 4 | Toạ độ horizon | $r_h=h/T_{\text{drain}}^{\text{post},B}$ | $h/(\tau_{\text{eff}}+d_{\text{act}})$ |
| 5 | Mức $y$ | Quantile dừng q50, q90 | Mức theo $z$ như v1 |
| 6 | Cấu trúc lưới | Lõi 18 + nan hoa 4 + kiểm âm 4 | Lõi lớn hơn có $r_h$ là nhân tố (khoảng 40 ô) |
| 7 | Ô WD đầu dò | Có, một ô | Không |

## 12. Giới hạn và sửa khi tích hợp ngày 23/10/2026

- Không tự nhận tác giả đã có bài kín sách/read-back. Nguồn bổ sung nhắc bài ngoài vở; repository chưa có artifact để kiểm, P0-V11 vẫn OPEN. Bản patch và bản tích hợp không thay bài tác giả.
- DL-028 ghi nhận **xung đột nguồn được mock review báo**: attachment Part E cho ngoại lệ, còn review dẫn PHASE_1 §17.1 yêu cầu HOLD. Chưa có full PHASE_1 để đối chiếu trực tiếp; không ghi đã xác minh câu gốc. Không tạo tag v1.1 trong B1.
- `s_bt` ngoài vùng bảo toàn không đủ chứng minh cost khác nhau hoặc có information value. ĐK1/ĐK2 là screen cần cho mục tiêu chính về state-variation; ô oracle-hằng vẫn có thể có Model gain, nên vẫn giữ và báo cáo.
- Quantile là mức theo rank CDF, không đảm bảo point probability lớn trên mọi discretization. B2 phải nêu cách xử lý quantile trùng/zero; nếu yB=0 thì r_h=h/Tdrain_post với drain0 không xác định. Không tự gán h0 hoặc chia cho0.
- Ba tiêu chí chọn calibration còn cần cách tính “trung tâm”, Tdrain của queue nào, cách xử lý drain0/âm và duplicate trước B3/B4. Chưa chọn ID hoặc mức mới ở B1.
- Nguồn review ghi f9ec182 là tag v1; tag thực tế trỏ6bb631f, còn f9ec182 chỉ thêm push receipt. Các scientific files của hai commit giống nhau; giữ tag gốc.
- B1 chỉ kiểm toy vét cạn và support/tham số của v1 đã có; không sinh candidate, không p_sw, không chọn reserve/calibration v1.1, không A01. Báo cáo ghi riêng số test chạy thực tế và provenance của những kiểm ngoài repo chưa tái lập.
- Lần chạy tích hợp đầu tiên có8/8 lesson và154/154 full-suite PASS nhưng coverage assertion của runner FAIL vì SD2/WD2 có0 ca. `first_run/coverage_failure.json` giữ đúng trạng thái này. Chỉ mở rộng verification cases; không hạ điều kiện coverage hoặc sửa ngưỡng nghiên cứu để PASS.


## 13. Mốc2 — N1–N6,23/10/2026

Các lựa chọn §11 ban đầu là DRAFT B1. Theo ủy quyền tác giả “tự thực hiện hết”, người phụ trách **Doan Van Tai** đã chọn/ghi đủ11 mục và commit **27eeed4** trước tính candidate; xem [quyết định mốc2](decisions_v1_1_m2.md), DL-029…031. Đây là chốt kỹ thuật theo ủy quyền, không phải bằng chứng tác giả hiểu kín sách; không tự mở gate/tag.

- N2 giữ một observation/cell, bổ đề E0/reference có tests; A04 companion g/bias/positive-negative margins. GM0 có thể cùng action khác khi g0. Có cả Δ dương và âm mới cho State value dương; mixed Switch/tie không đủ.
- N1 dùng idle-gap với rational coordinates, assert SD/WD/conservation; eps_num1e−9*Cref và alarmuncertifiedband>.01 để tăng precision. Không clamp/đổi true oracle; chưa resolve sign thì HOLD. B3 không tính Cref/Lstar/margins chỉ để đặt band.
- ĐK5 signψ hai phía0 ở coreη.5; highη.9 spoke tạicenterλA7.5. Nền A=λA±6 không đổi khiu đổi, A meanλ={6.5,7.5,8.5}, μ10,B2/14; numeric stationary with tail/law bound. Solver budget cap≤50.000; uncertified posterior/quantile hoặc vượt budget giữ HOLD, không đổi level để đẹp.
- Relative age là1/κ; zA/zB làderived diagnostics. Quantile co giãn gần theoκ trong fluid limit, không bằng nhau tuyệt đối ở finite dt; không claim persistence riêng age/backlog scale.
- **Luật8 ĐK2:** p_sw tạiage/120 vàhalf; acceptance class khác→unstable, không calibration. Nếu error interval chạm threshold thì indeterminate/unstable, không tự chọn side. Chỉ p_sw và numerical-resolution diagnostics ởB3, không reserve p_sw/margins/contrasts. Current task chưa thực thiB3.
- ĐK8 giữ **thước đo**, không nói plant không đổi: D4,D7(mA từhằng→ngẫu nhiên),D12,D20,D22 đổi. Changelog và [contract draft](../01_definitions_v1_1_draft.md); splits không so trực tiếp v1/PartB.
- Selected grid không ước lượng tần suất contrasts lớn trong mạng thật. Protocol review/primary source và V1/V8/P0-V3/V11 còn chờ; active closeout HOLD. Heads-up nội bộ, chưa gửi theo chỉ dẫn tác giả.
