# T05 — engine exact: phép dẫn và read-back

Người phụ trách: **Doan Van Tai** · 27/10/2026 · contract v1.2.

**Văn bản T05 tác giả: chưa có trong repo. Read-back engine/T05: AUTHOR-ATTESTED
27/10/2026 (L3.3, DL-048).** Tác giả trả lời “Đã tự hoàn thành cả hai ngoài repo”
cho câu hỏi read-back already_implied kín sách và engine/T05; [nguyên văn](../../results/lessons/l3_3/author_attestation.json).
Không có transcript hoặc phép dẫn mới được gửi; không đổi phần AI hỗ trợ dưới đây
thành bài tác giả viết. Engine mới vẫn ở `experiments/A00_engine/`; phiên L3.3 không promote.

## Phần tác giả tự viết / xác nhận

⟨Chưa có: phép dẫn separability, idle identity, Jensen, T01 và L10.⟩

⟨Read-back engine/T05 author-attested theo DL-048; chưa chép lời tác giả vào repo.⟩

## Phép dẫn làm việc — AI hỗ trợ

**Separability.** D3/D6 cho recurrence riêng từng queue; D13 cho cost cộng được.
Do tính tuyến tính của kỳ vọng, J=J_A+J_B. D4/D12 còn cho D=D_A×D_B và cho phép
mỗi thành phần chỉ phụ thuộc state riêng. Sự cộng được của expectation tự nó
không cần độc lập; phép factorize D và việc chỉ dùng state riêng thì cần giả định đó.

**Idle identity.** Viết q[n+1]=q[n]+a[n]−c+I[n], I[n]=max(0,c−q[n]−a[n]).
Suy ra q[n]=q[0]+Σ(k<n)(a[k]−c)+Σ(k<n)I[k]. Vì D13 tính dtΣ(n=1..H)q[n],
slot k góp vào H−k endpoint, nên phần idle là W=dtΣ(k=0..H−1)(H−k)I[k].
Hai action dùng cùng background path và tổng managed u không đổi; tổng phần
tuyến tính của A+B triệt tiêu trên từng path. Vì vậy Δ=δ_A+δ_B với δ_l=W_l(Sw)−W_l(St).
Mất u trên A tăng idle: δ_A≥0; thêm u trên B giảm idle: δ_B≤0.
Từng thành phần δ_l khác J_l(Sw)−J_l(St), vì phần tuyến tính chỉ triệt tiêu khi cộng A+B.

**Jensen.** Với state ban đầu cố định, U[n]=max(0, max(m≤n)(−q[0]−Σ(k<m)(a[k]−c)))
là max của các hàm affine theo vector arrivals. W=dtΣU[n] lồi. Cùng θ và cùng mode
ban đầu, M0 dùng vector conditional means, do đó W(E[a|x])≤E[W(a)|x]. Phần tuyến
tính có cùng expectation, nên Jhat≤J cho mỗi action. Hiệu hai Jensen gaps có
thể có cả hai dấu: không suy ra M0 luôn bias về Stay. D10 yêu cầu average rollouts
theo belief, không rollout từ mean backlog/mode.

**T01.** Đặt K=EJ(St), g=EΔ, gh=EΔhat. a00=1[gh<0], a01=1[g<0].
L00=K+a00g; L01=K+min(0,g); L10=K+E[Δ·1(Δhat<0)]; L11=K−EΔ−.
G_M=(a00−a01)g∈{0,|g|} và ≤|gh−g|. G_S|M1=min(EΔ+,EΔ−).
G_M|S1=E[|Δ|·1(a10≠a11)]≥0. GS có thể âm. Mọi contrast conditional trên một y;
hai quantile quan sát không tạo ra phân phối vận hành trên y.

**L10 không tích Descartes.** Với mỗi a, chỉ lấy b có δhat_B<−δhat_A. Sắp B theo
δhat_B; prefix của p_B và p_B·δ_B cho tổng p_A[δ_A·prefix_p+prefix_pδ].
`bisect_left` giữ strict tie Stay. Sort key là dự đoán; score là gap thật.
L11 dùng key thật. D22 gộp mode theo posterior D(m|q), dùng cùng M0, rồi áp cùng cut.
F=L00−Lcb0, V=Lcb0−L10 phụ thuộc thứ tự backlog trước/mode sau. Identity F+V=GS
không tự xác nhận D22 đúng; checker phải gộp theo cặp backlog trực tiếp.

**I_delta.** Theo L1.5: I_delta=bias−(Δhat−Δ). |I_delta| là abs của tổng tách
được; expectation dùng cut của phần âm, quantile dùng CDF cuts, không tạo tích.
Không đồng nhất prediction interaction với Γ.

## Điều chỉnh lỗi / giới hạn trong lesson

1. `cells.py` đã có từ L3.1; baseline là 228 tests, không phải 202. Adapter mới cho
   ba schema nằm trong experiments; nguồn D cũ giữ nguyên.
2. Pseudocode side_table tính idle sau update q có thể đếm sai. Code tính
   idle=max(0,−q_pre−net) rồi mới q_next=max(0,q_pre+net). Biên độ lấy từ rates,
   không hardcode ±6; N01 có amplitude=0.
3. E3/E6 là **toy arrival-law**: arrival slot đầu ngẫu nhiên dù state đã cố định.
   Đây là minh họa Jensen hợp lệ nhưng không là state D7 với mode slot0 đã biết.
   Trong plant ON/OFF D7, H=1 cho Δhat=Δ; randomness xuất hiện ở mode tương lai.
   Giữ E3/E6 ngoài D7, thêm test H=1; không đổi contract để hợp thức ví dụ.
4. `cut_with_bound` mẫu chỉ bao key uncertainty. Engine bổ sung true-value,
   probability-L1, conditional posterior D22, conversion và aggregation rounding.
   Report mỗi L/R/contrast và diagnostic với radius riêng; quantiles có khoảng.
5. Guard mẫu chưa kiểm freeze. Bản mới kiểm HEAD/dirty cho L3.3 và A05-F, chỉ
   purpose A05-T mới dùng held-out. Đây là kiểm cơ học, không xác nhận chất lượng card.
6. “Tầng sổ sách đúng thì mọi sai sót còn lại chắc chắn ở vật lý” là quá mạnh:
   toy tests chưa loại hết lỗi integration, float hoặc phiên bản. Chỉ claim phạm vi đã kiểm.

## Numeric: điều gì được và chưa được chứng nhận

Input gồm cận per-state d/dhat/Jst và cận L1 cho D; D rebuild trả TV bound nên adapter
đổi thành 2·TV và cộng normalization residual. Joint L1 dùng eA+eB+eAeB.
Weighted prefix dùng long double, cộng allowance theo operation count; interval endpoints
được nới outward. Kernel DP/R2 dùng cận có sẵn. Mean-path dùng tính Lipschitz của
reflection và cận nhiễu arrivals/roundoff qua horizon. Các bound giả định arithmetic
finite, không overflow/underflow làm mất support; chúng không là CI hoặc dt-convergence.

Unresolved mass tách oracle/M0/D22. M0/D22 kèm impact bound của true gap trên vùng
chưa phân giải. Nếu gh chưa phân giải, giữ hai L00 khả dĩ và HOLD; không coi nominal
action là kết luận. L11/L01 liên tục theo input; L00/L10/Lcb0 có thể nhảy mạnh.
Không kẹp gap nhỏ; structural zero phải có certificate, sai thì raise.

Chưa chạy engine trên grid, chưa kiểm computational/numeric feasibility toàn grid,
chưa chứng nhận dt; việc đó thuộc A01 sau card. EVPI_w và flip mass hai chiều để sau.

## Read-back cần tác giả tự làm

| Hàm | Câu cần tự giải thích |
|---|---|
| `_cut_sum` | Vì sao sort theo dhat, score theo d, và dùng `<`? |
| `_by_backlog` | Vì sao D10 cho phép average qua posterior mode? |
| `aggregate` | Dòng nào giữ S0 chỉ nhìn expectation? |
| `brute` | Vì sao checker không được dùng helper core? |
| `toy_side` / `side_from_law` | Phép kiểm nào đối chiếu J với idle và Jensen? |
| `enclose` | Vì sao M0 unresolved cần true-gap impact, không chỉ xác suất? |
| `load_cell` / `queue_law` | Ba schema khác nhau ở đâu, prior nào phải tính lại theo ref? |
| `guard` / `evaluate_cell` | File nào phải committed, và guard kiểm trước thao tác nào? |
