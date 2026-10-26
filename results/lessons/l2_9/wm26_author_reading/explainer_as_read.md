<!--
Provenance: văn bản dưới đây là bản giải thích WM26 do một công cụ AI khác viết, được
Doan Van Tai gửi nguyên văn trong chat ngày 26/10/2026 với câu "đây là những gì tôi đã
đọc và đưa AI thuật lại". Chép lại nguyên văn để ghi đúng thứ tác giả đã đọc (L-2nd).
Ảnh là link ngoài tới nguồn khác, không phải hình của WM26. Kiểm nội dung: check.md.
Không sửa nội dung bên dưới.
-->

# Giải thích bài WM26 từ đầu: World Model, Center–Response và sự khác biệt với nghiên cứu NDT của bạn

Dựa trên bản PDF 40 trang bạn gửi · arXiv:2610.05550v1 · 04/10/2026 · Preprint, đang phản biện

Bài báo có tên:

When Low Prediction Error Misleads Planning: Diagnosing Representation, Dynamics, and Decision Failures in Latent World Models

Dịch sát nghĩa:

Khi sai số dự đoán thấp vẫn khiến việc lập kế hoạch sai lệch: Phân tích các lỗi về biểu diễn, động lực học và ra quyết định trong Latent World Models.

Đây là một paper rất đáng đọc đối với nghiên cứu của bạn, không phải vì nó nghiên cứu mạng máy tính, mà vì nó đặt ra một câu hỏi gần với câu hỏi State × Model của bạn: khi một hệ thống ra quyết định sai, chúng ta nên sửa thành phần nào trước?

Tôi sẽ giải thích theo thứ tự: hiểu bài toán thực tế trước, sau đó mới tới khái niệm, công thức, thí nghiệm, kết quả và novelty.

## 1. Paper này thực sự muốn giải quyết vấn đề gì?

Hãy tưởng tượng bạn xây dựng một robot dùng AI để đẩy một vật đến vị trí mong muốn.

[Demonstration Learning via Diffusion Policy on 7 DOF Robot Arm](https://images.openai.com/static-rsc-4/OGx3jk9zgcthL_XzrJRApGxRlgdE-9ubjRhpWmLaTFuXGWCTuG054jyVuejs9ejDpgzOHlbqeOUwVZk2YFdpqKp57mT8kgF-bkcrbRbhx9xDa2yJ1li9QWPSRQYAjeGpI9bSE2SRjCU3VnUmkWMZRWSZcRpOWOxaOYXDyax0fLs?purpose=inline)

[dmc2gym — DI-engine 0.1.0 documentation](https://images.openai.com/static-rsc-4/hemOEzf5Ftv1L-PBUs5LY21YBOhoddn_QONui6Pfi4k15Ee8_wbGdldCOS8-3D1_yZls_GQ2jxc69PQ96QjBonZ0Nel3RX5TUNt0Q2Kw2MIhTqfbWbsaztBam7fHzQATh3Gvc58YV7COaTrNjJVsOvjGqbVNELgdcbTYa4sSN6o?purpose=inline)

[Learning from Reward-Free Offline Data: A Case for Planning with Latent Dynamics Models](https://images.openai.com/static-rsc-4/iZcMQhcPx9DDeFIIEuuhUPwV5GdnRV6q0KDpgaFZQ9oNw8BzKHLW4TnkjFTHHo1ajNH6EvP3lEKoHi7X8PTUnO3-_Ux7hjZrrBfDpDasTY77bxfD6Q-ToY8BZ_cGTqiHgxdQwWGb6EW74MPksdZqRBd08sz1-bJFfWM62oBeBMs?purpose=inline)

7

Robot có thể chọn giữa nhiều phương án:

- Action A: đẩy vật sang trái.
- Action B: đẩy vật sang phải.
- Action C: đẩy vật theo hướng chéo.

Trước khi hành động, robot sử dụng một World Model để dự đoán điều gì sẽ xảy ra sau mỗi phương án.

Ví dụ:

| Action | Vị trí cuối robot dự đoán | Vị trí cuối thực tế |
| ------ | ------------------------- | ------------------- |
| A      | Gần mục tiêu              | Xa mục tiêu         |
| B      | Xa mục tiêu               | Gần mục tiêu        |

Vấn đề là model có thể có sai số dự đoán trung bình rất thấp, nhưng vẫn nhầm thứ tự của các action.

Khi đó robot chọn A, mặc dù B mới là phương án tốt nhất.

Thông thường, người xây dựng World Model tìm cách giảm:

\\[ \text{Prediction Error} \\]

Nhưng tác giả muốn biết:

> Giả sử có thể sửa một phần lỗi của World Model, thì sửa phần nào mới thực sự giúp robot lựa chọn action tốt hơn?

Đây là câu hỏi trung tâm của WM26.

Một điểm mới trong cách tiếp cận là họ không xem tất cả prediction errors giống nhau. Họ chia chúng thành hai thành phần: Center Error và Action-Relative Response Error.&#x20;

2610.05550v1.pdf



## 2. Trước khi đọc paper, cần hiểu sáu khái niệm nền tảng

### 2.1. World Model là gì?

World Model là một mô hình được dùng để dự đoán cách môi trường thay đổi khi một action được thực hiện.

Ta có thể viết đơn giản:

\\[ s\_{t+1}=f(s_t,a_t) \\]

Trong đó:

- \\(s_t\\): trạng thái hiện tại của môi trường.
- \\(a_t\\): hành động mà controller chọn.
- \\(s\_{t+1}\\): trạng thái sau khi hành động.
- \\(f\\): mô hình dynamics của hệ thống.

Ví dụ robot đang ở vị trí \\(x=2\\), chọn hành động đi phải 1 mét, World Model dự đoán vị trí tiếp theo \\(x=3\\).

Nếu có vật cản hay trượt bánh, kết quả thật có thể khác.

Trong một hệ thống có uncertainty, World Model cũng có thể dự đoán cả phân phối của trạng thái tương lai, thay vì chỉ một giá trị duy nhất.

Liên hệ NDT: Model \\(M_0\\) và \\(M_1\\) của bạn cũng là những mô hình dùng để dự đoán kết quả của Stay/Switch. Nhưng chúng không phải là latent neural world models được học từ ảnh như trong WM26.

### 2.2. Latent State là gì?

Đây là khái niệm rất hay gặp trong Deep Learning.

Robot có thể quan sát một ảnh:

[Diffusion policy: Visuomotor policy learning via action diffusion - Cheng Chi, Zhenjia Xu, Siyuan Feng, Eric Cousineau, Yilun Du, Benjamin Burchfiel, Russ Tedrake, Shuran Song, 2025](https://images.openai.com/static-rsc-4/BOw8qJX-exYWX9epZwkti1bmkQwnOeN_Hx8FQMA_qtPSrBme84ZvClP3cQhR_NwI52syxeLVRsvTnMyhavy-MF3-4eCHBTGaEkZbfiC86Qib0sRUHMMgEVPeECCsRHZDMyx4DS-AWo5YYjq5HeN1ja3ioUZQ2I_tVhw5f9rI3vE?purpose=inline)

Ảnh có rất nhiều pixel. Nhưng để dự đoán chuyển động, AI không nhất thiết cần sử dụng từng pixel trực tiếp.

Nó có thể sử dụng một mạng neural để chuyển ảnh thành một vector ngắn hơn:

\\[ o_t\xrightarrow{\text{Encoder}}z_t \\]

Ví dụ:

\\[ z_t=[0.2,-0.8,1.4,\ldots] \\]

Đây là latent representation.

Bạn có thể hiểu nó là một dạng mã hóa thông tin của môi trường để model dễ xử lý hơn.

Cần phân biệt:

- Physical state: trạng thái vật lý thật của hệ thống.
- Observation: dữ liệu cảm biến hoặc hình ảnh mà robot nhìn thấy.
- Latent state: biểu diễn được encoder tạo ra từ dữ liệu quan sát.

Latent state không nhất thiết có từng thành phần tương ứng trực tiếp với vị trí, vận tốc hay góc quay.

### 2.3. Encoder, Predictor và Planner

Một Latent World Model thường có ba thành phần chức năng:

Encoder — Hiểu quan sát

Chuyển ảnh hoặc dữ liệu cảm biến thành latent state \\(z_t\\)

Predictor — Dự đoán hậu quả

Với mỗi action, dự đoán latent state tương lai \\(\hat z\_{t+H}\\)

Planner — Lựa chọn action

So expected hoặc predicted cost của các phương án để tìm action phù hợp

Ví dụ:

Robot nhìn ảnh → encoder tạo vector → predictor thử A, B, C → planner chọn phương án dự đoán gần mục tiêu nhất.

Một sai lầm của hệ thống có thể đến từ ba vị trí:

- Encoder không giữ được thông tin cần thiết.
- Predictor dự đoán sai ảnh hưởng của action.
- Planner sử dụng biểu diễn hoặc hàm cost không phù hợp.

Đây chính là ba loại lỗi trong tiêu đề: Representation, Dynamics và Decision Failures.

### 2.4. Counterfactual là gì?

Counterfactual có thể hiểu là câu hỏi:

> Nếu ở cùng trạng thái ban đầu, tôi chọn một hành động khác, điều gì sẽ xảy ra?

Ví dụ robot ở vị trí ban đầu \\(s_0\\).

Ta muốn biết:

\\[ s_0+\mathrm{Action\ A}\rightarrow z_A \\]

\\[ s_0+\mathrm{Action\ B}\rightarrow z_B \\]

Muốn so sánh công bằng, phải bắt đầu từ cùng một physical state.

WM26 thực hiện điều này bằng cách khôi phục cùng trạng thái simulator rồi thử nhiều action sequences khác nhau.

Họ gọi cách làm đó là same-start branching.

Đây là chi tiết thực nghiệm rất quan trọng: nếu hai action bắt đầu từ những trạng thái khác nhau thì khó biết sự khác biệt đến từ action hay trạng thái xuất phát.&#x20;

2610.05550v1.pdf



### 2.5. Prediction Horizon là gì?

Horizon là khoảng tương lai mà model dự đoán.

Nếu \\(H=5\\), model dự đoán sau 5 bước model.

Trong WM26, một model step tương ứng với năm environment steps. Vì vậy H5 và H20 là 5 hoặc 20 bước model, không phải 5 hay 20 giây theo nghĩa trong contract queue của bạn.

Horizon dài khiến lỗi dự đoán có thể tích lũy hoặc biến dạng qua nhiều bước.

### 2.6. MSE là gì?

MSE viết tắt của Mean Squared Error, tức sai số bình phương trung bình.

Ví dụ model dự đoán:

\\[ \hat z=8 \\]

Nhưng giá trị thật:

\\[ z=10 \\]

Sai số bình phương:

\\[ (8-10)^2=4 \\]

Nếu có nhiều dự đoán, lấy trung bình những sai số bình phương đó.

MSE càng nhỏ có nghĩa dự đoán càng khớp với đại lượng được đo, nhưng không tự bảo đảm model xếp hạng action tốt.

Đây chính là điều WM26 muốn chứng minh bằng thí nghiệm.

## 3. Hai loại lỗi quan trọng nhất: Center Error và Response Error

Đây là phần cốt lõi của paper.

Hãy tưởng tượng một robot có ba hành động và vị trí kết thúc thật như sau:

Ví dụ minh họa — một chiều

Ví dụ do tôi tạo để giải thích, không phải dữ liệu thực nghiệm của WM26.

Vị trí thật của ba action:

\\[ z=[1,2,3] \\]

Vị trí mà model dự đoán:

\\[ p=[4,5,6] \\]

Có điều gì đặc biệt?

Model luôn dự đoán lệch sang phải 3 đơn vị.

Nhưng khoảng cách giữa các action vẫn đúng:

- A đến B: 1.
- B đến C: 1.

Model sai về vị trí chung, nhưng đúng về sự khác biệt giữa các action.

Đó là Center Error.

### 3.1. Center là gì?

WM26 định nghĩa:

\\[ \bar z=\frac1K\sum\_{j=1}^{K}z_j \\]

\\[ \bar p=\frac1K\sum\_{j=1}^{K}p_j \\]

Trong đó \\(K\\) là số candidate actions hoặc action sequences được so sánh từ cùng một trạng thái ban đầu.

Với ví dụ:

\\[ \bar z=(1+2+3)/3=2 \\]

\\[ \bar p=(4+5+6)/3=5 \\]

Center Error:

\\[ E_C=|\bar p-\bar z|^2 \\]

\\[ E_C=(5-2)^2=9 \\]

Bạn có thể hiểu:

Center Error là sai lệch giữa trung tâm nhóm kết quả dự đoán và trung tâm nhóm kết quả thật.

Một điểm cực kỳ quan trọng: center ở WM26 là trung bình của kết quả trên candidate action pool, không phải state hiện tại, không phải zero-action outcome, cũng không phải trung bình của nhiễu tương lai.

### 3.2. Response là gì?

Response đo sự khác biệt của từng action so với center chung.

Response thật:

\\[ r_j=z_j-\bar z \\]

Response dự đoán:

\\[ \hat r_j=p_j-\bar p \\]

Với ví dụ:

\\[ r=[-1,0,+1] \\]

\\[ \hat r=[-1,0,+1] \\]

Như vậy response đúng hoàn toàn.

Dù prediction tuyệt đối lệch rất nhiều, model vẫn biết đúng mỗi action làm thay đổi kết quả như thế nào so với các action khác.

### 3.3. Nếu response sai thì sao?

Giả sử thật:

\\[ z=[1,2,3] \\]

nhưng model dự đoán:

\\[ p=[5,4,3] \\]

Lúc này:

\\[ \bar p=4,\qquad \bar z=2 \\]

Response thật:

\\[ r=[-1,0,+1] \\]

Response dự đoán:

\\[ \hat r=[+1,0,-1] \\]

Model đã đảo ngược response của A và C.

Nó nghĩ A đưa kết quả lệch về một phía, trong khi thực tế A tạo kết quả về phía đối diện so với center.

Response Error nguy hiểm vì nó có thể làm model hiểu sai tác động tương đối của action.

### 3.4. Công thức phân rã MSE

WM26 chứng minh identity:

\\[ \boxed{ MSE\_{\mathrm{total}} = MSE\_{\mathrm{center}} + MSE\_{\mathrm{response}} } \\]

Cụ thể:

\\[ \frac1K\sum_j\\|p_j-z_j\\|^2 = \\|\bar p-\bar z\\|^2 + \frac1K\sum_j\\|\hat r_j-r_j\\|^2 \\]

Tại sao tách được?

Vì sai số mỗi action bằng sai lệch chung của center cộng sai lệch response:

\\[ p_j-z_j=(\bar p-\bar z)+(\hat r_j-r_j) \\]

Khi cộng bình phương qua các action, các hạng tích chéo triệt tiêu vì response đã được trừ trung bình.

Ý nghĩa: ta có thể phân loại chính xác tổng sai số dự đoán thành phần chung và phần phụ thuộc vào action.

Đây là kết quả của Section 4.1 và Equation (3), không phải một xấp xỉ thống kê.&#x20;

2610.05550v1.pdf



## 4. Điều bất ngờ: Lỗi lớn nhất chưa chắc là lỗi nên sửa trước

Đây là thí nghiệm tư duy giúp bạn hiểu gần như toàn bộ paper.

Giả sử có hai action A và B. Robot muốn đi tới mục tiêu tại vị trí 0.

Kết quả thật:

\\[ z_A=1,\quad z_B=3 \\]

Vì A gần mục tiêu hơn, action đúng là A.

Nhưng model dự đoán:

\\[ p_A=6,\quad p_B=4 \\]

Model nghĩ B gần mục tiêu hơn, nên chọn B, tức chọn sai.

Bây giờ chúng ta phân tích hai loại sai số.

Center thật:

\\[ \bar z=2 \\]

Center dự đoán:

\\[ \bar p=5 \\]

Center error bình phương:

\\[ E_C=(5-2)^2=9 \\]

Response thật:

\\[ r=[-1,+1] \\]

Response dự đoán:

\\[ \hat r=[+1,-1] \\]

Response error:

\\[ E_R=\frac{(1+1)^2+(-1-1)^2}{2}=4 \\]

Tổng MSE:

\\[ MSE=9+4=13 \\]

Center Error chiếm:

\\[ \frac9{13}\approx69.2\\% \\]

Response Error chiếm:

\\[ \frac4{13}\approx30.8\\% \\]

Nếu chỉ nhìn MSE, bạn sẽ nghĩ nên sửa Center trước vì nó chiếm gần 70% lỗi.

Nhưng hãy thử hai cách repair.

### Trường hợp 1: Chỉ sửa Center

Ta giữ response dự đoán, nhưng thay center bằng center thật:

\\[ C=[3,1] \\]

So với kết quả thật \\([1,3]\\), sai số MSE chỉ còn 4.

Nhưng nếu mục tiêu ở 0, model vẫn chọn B vì \\(1<3\\).

Sửa phần lỗi lớn nhất làm MSE giảm mạnh, nhưng quyết định vẫn sai.

### Trường hợp 2: Chỉ sửa Response

Ta giữ center dự đoán, nhưng thay response bằng response thật:

\\[ S=[4,6] \\]

Lúc này residual MSE là 9, vẫn lớn hơn nhiều so với trường hợp sửa center.

Nhưng model chọn A vì \\(4<6\\).

Sửa phần lỗi nhỏ hơn lại giúp chọn đúng action.

Thử nghiệm hai action — Goal = 0

P — Chưa sửa

C — Sửa center

S — Sửa response

E — Sửa cả hai

Action A

6

Action B

4

MSE còn lại

# 13

Action được chọn

# B

Sai

Ví dụ số tự xây dựng theo phép phân rã của paper; cost = bình phương khoảng cách đến Goal = 0.

Đây chính là thông điệp chủ đạo của WM26:

> Thành phần gây ra nhiều prediction error nhất có thể không phải thành phần có giá trị sửa chữa cao nhất đối với việc chọn action.

Tuy nhiên, cũng có một điểm phải giữ lại: center error vẫn có thể ảnh hưởng đến quyết định. Với hàm cost khoảng cách bình phương tới goal, dịch chuyển center có thể làm thay đổi thứ tự các action. Vì vậy tác giả không nói lúc nào response repair cũng tốt hơn.

## 5. Bảng 2×2 của WM26: P, C, S, E là gì?

Bạn đã quen bảng bốn ô:

\\[ S_0M_0,\quad S_0M_1,\quad S_1M_0,\quad S_1M_1 \\]

WM26 cũng dùng bảng bốn trường hợp, nhưng hai trục hoàn toàn khác.

Họ định nghĩa:

|                | Response dự đoán | Response thật |
| -------------- | ---------------- | ------------- |
| Center dự đoán | P                | S             |
| Center thật    | C                | E             |

Trong đó:

- P — Predicted: hoàn toàn dùng prediction của model.
- C — Center-repaired: thay center dự đoán bằng center thật.
- S — Response-repaired: thay action-relative responses dự đoán bằng responses thật.
- E — Encoded realized: sử dụng cả center lẫn responses từ các kết quả thật đã mã hóa.

Theo ký hiệu của paper:

\\[ P_j=p_j \\]

\\[ C_j=p_j-\bar p+\bar z \\]

\\[ S_j=z_j-\bar z+\bar p \\]

\\[ E_j=z_j \\]

Đây là Equations (2)–(3), và Section 5/F.1 triển khai chúng để đánh giá các candidate trên cùng một tập action.&#x20;

2610.05550v1.pdf



### 5.1. Vì sao dùng bốn trường hợp?

Giả sử chỉ có P và E.

Bạn biết model dự đoán sai và khi có kết quả thật thì quyết định tốt hơn.

Nhưng không biết lỗi đó chủ yếu đến từ center hay response.

Thêm C và S cho phép hỏi:

- Nếu chỉ sửa center thì decision quality cải thiện bao nhiêu?
- Nếu chỉ sửa response thì sao?
- Nếu sửa cả hai thì sao?

Nhờ đó tác giả có thể xác định repair priority — phần lỗi nào đáng được ưu tiên sửa cho decision.

### 5.2. Oracle trong WM26 là gì?

Oracle ở đây có nghĩa là một nguồn thông tin lý tưởng được dùng làm đối chứng.

WM26 tạo các endpoint thật bằng simulator rồi dùng chúng để sửa prediction.

Đối với C, tác giả cần biết center thật của các candidate endpoints.

Đối với S, tác giả cần biết action-relative responses thật của chúng.

Nhưng những endpoints này chỉ xuất hiện sau khi đã giả lập hành động tương lai.

Vậy tại thời điểm quyết định trong hệ thống thật, controller thường không có sẵn các giá trị đó.

Do đó WM26 gọi chúng là diagnostic oracles — các phép sửa lý tưởng dùng để phân tích nguyên nhân lỗi, không phải thuật toán online có thể triển khai trực tiếp.

Điều này được tác giả thừa nhận rõ trong Section 8.&#x20;

2610.05550v1.pdf



## 6. Paper còn dùng những khái niệm đánh giá nào?

Đến đây bạn đã hiểu World Model, latent representation, center, response và oracle repair.

Bây giờ cần hiểu các metric để đọc kết quả.

| Thuật ngữ            | Giải thích dễ hiểu                                                                           | Dùng để làm gì                                   |
| -------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| Physical ranking     | Thứ tự tốt/xấu của các action theo kết quả vật lý thật                                       | Kiểm model có xếp action đúng không              |
| Spearman correlation | Độ giống nhau giữa hai bảng xếp hạng                                                         | Đánh giá ranking quality                         |
| Top-k elites         | Nhóm k action được model đánh giá tốt nhất                                                   | Xem model chọn được nhóm action chất lượng không |
| Elite quality        | Chất lượng vật lý thật của nhóm action được chọn                                             | Kiểm hiệu quả lựa chọn                           |
| Fixed-pool regret    | Thiệt hại khi chọn từ một tập candidate cố định so với candidate tốt nhất trong chính tập đó | Đo decision loss trong thí nghiệm                |
| CEM                  | Cross-Entropy Method: thuật toán lặp để tìm action sequence tốt                              | Planner của hệ thống                             |
| Closed-loop planning | Thực hiện action, quan sát state mới, rồi lập kế hoạch lại                                   | Kiểm kết quả sau khi hệ thống thực sự vận hành   |
| Bootstrap CI         | Khoảng bất định ước lượng bằng lấy mẫu lại các đơn vị thực nghiệm                            | Phân biệt hiệu ứng có bằng chứng với dao động    |
| Oracle repair        | Sửa một phần prediction bằng dữ liệu thật đặc quyền                                          | Chẩn đoán thành phần lỗi                         |

### Spearman là gì?

Giả sử thứ tự action thật từ tốt đến xấu:

\\[ A>B>C \\]

Model cũng xếp:

\\[ A>B>C \\]

Spearman \\(=1\\), ranking hoàn toàn đồng ý.

Nhưng model xếp:

\\[ C>B>A \\]

Spearman \\(=-1\\), thứ tự đảo ngược hoàn toàn.

Nếu Spearman gần 0, hai thứ tự ít có quan hệ đơn điệu.

Trong WM26, Spearman được dùng để xem latent-goal cost có xếp các action phù hợp với physical error hay không.

### Fixed-pool regret khác regret của bạn thế nào?

WM26 xét một tập candidate action sequences đã tạo sẵn.

Họ có thể đo thiệt hại so với action có physical error nhỏ nhất trong chính tập đó.

Còn bạn so expected true cost của action Stay/Switch với một oracle stochastic không biết future realization theo contract.

Vì comparator khác nhau nên hai con số regret không được coi là cùng một estimand.

## 7. Kết quả thực nghiệm WM26 thực sự tìm được gì?

Paper kiểm trên các nhiệm vụ robot/navigation như PushT, TwoRoom, Reacher, Cube với nhiều họ World Model.

[(PDF) DINO-WM: World Models on Pre-trained Visual Features enable Zero-shot Planning](https://images.openai.com/static-rsc-4/weGLT-t03T3CLREg2z4-9vSdAjl84E11uZchmOSrEtNKYux-BG3ow5LzlYIzWgGX_bUI-kT0WVTRcyp4IJY2Yk6Cv24wEJ85h40ZylzfWHggOVZfPXILqjUeV3L2PSJw_2GwYVQYAMzEYdIRlNnTnPWE7EjybhOGfKGR5eDdxfs?purpose=inline)

PushT

Robot điều khiển thao tác đẩy một vật dạng chữ T. Model phải dự đoán tác động của các chuỗi action.

[dmc2gym — DI-engine 0.1.0 documentation](https://images.openai.com/static-rsc-4/hemOEzf5Ftv1L-PBUs5LY21YBOhoddn_QONui6Pfi4k15Ee8_wbGdldCOS8-3D1_yZls_GQ2jxc69PQ96QjBonZ0Nel3RX5TUNt0Q2Kw2MIhTqfbWbsaztBam7fHzQATh3Gvc58YV7COaTrNjJVsOvjGqbVNELgdcbTYa4sSN6o?purpose=inline)

Reacher

Robot arm di chuyển tới một goal. Đây là bài toán điều khiển theo trạng thái và action.

### Kết quả 1 — Lỗi lớn nhất thường thuộc Center

Trên 16 tổ hợp model–task trong phần confirmation:

CENTER ERROR CHIẾM PHẦN LỚN MSE

# 14/16

Ở 14 trong 16 model–task cells, center error chiếm ưu thế về MSE theo các phép so sánh tác giả báo cáo.

### Kết quả 2 — Nhưng sửa Response có thể giúp decision tốt hơn

Trong 6 cell thuộc nhóm 14 cell trên, Response Repair cải thiện cả ranking và top-30 elite quality tốt hơn Center Repair, dù vẫn để lại MSE lớn hơn.

MSE–DECISION INVERSION

# 6/16

Sáu trường hợp xác nhận sự đảo ngược giữa phần lỗi lớn nhất và phần đáng sửa hơn cho quyết định.

Đây là số trường hợp trong thiết kế tác giả kiểm, không phải xác suất 37,5% cho World Models nói chung hoặc cho network routing.

Các số này nằm trong Abstract, Section 7.1 và Table 1–2.&#x20;

2610.05550v1.pdf



### Kết quả 3 — Có khi lỗi không nằm chủ yếu ở Predictor

Tác giả còn kiểm một phép so sánh:

- P: đánh giá action bằng predicted latent endpoints.
- E: đánh giá bằng latent representation của realized endpoints.

Nếu E tốt hơn P, có cơ sở cho thấy prediction hoặc quá trình cập nhật representation theo observation đã làm giảm khả năng xếp action.

Nhưng ở nhiệm vụ Cube, ngay cả E cũng không xếp hạng physical outcomes tốt.

Điều đó gợi ý nút thắt không thể chỉ sửa bằng cách làm predictor chính xác hơn; representation và latent-goal metric đang được sử dụng có thể không đủ thông tin hữu ích cho decision.

### Kết quả 4 — Cải thiện offline metric chưa chắc cải thiện closed-loop

Trong nghiên cứu huấn luyện objective, tác giả có những trường hợp cải thiện response diagnostics nhưng không chứng minh được cải thiện closed-loop CEM success.

Ví dụ trên Reacher, một objective cải thiện offline H5 response error 8,44%, nhưng thay đổi CEM success ước lượng là −2,34 điểm phần trăm, với khoảng bất định cắt qua 0.

Vì vậy không được kết luận objective đó làm planning tốt hơn hoặc tệ hơn một cách chắc chắn từ phép so sánh này.&#x20;

2610.05550v1.pdf



Điểm đáng học từ WM26: họ tách rất rõ một diagnostic đã được xác nhận với một lợi ích triển khai thực tế chưa được xác nhận.

## 8. So sánh trực tiếp WM26 với nghiên cứu State × Model của bạn

Đây là phần quan trọng nhất đối với Lesson 2.9.

### 8.1. Hai nghiên cứu giống nhau ở đâu?

| Điểm giống                           | WM26                                    | Đề tài bạn                             |
| ------------------------------------ | --------------------------------------- | -------------------------------------- |
| Dùng model để ra quyết định          | Chọn action sequence                    | Chọn Stay/Switch                       |
| Quan tâm decision quality            | Ranking, elite quality, physical regret | Expected decision regret               |
| So nhiều loại cải thiện              | Center repair, Response repair          | State repair, Model repair             |
| Có thiết kế bốn trường hợp           | P, C, S, E                              | \\(S_0M_0,S_0M_1,S_1M_0,S_1M_1\\)      |
| Kiểm xem sửa gì đáng hơn             | C hay S                                 | State hay Model                        |
| Không đánh đồng accuracy với quality | Latent MSE không quyết định ranking     | Model fidelity không quyết định regret |

Như vậy, nếu bài của bạn viết:

> Chúng tôi đề xuất lần đầu tiên bảng \\(2\times2\\) để nghiên cứu hai nguồn lỗi trong một model phục vụ decision.

Thì rất dễ bị WM26 phản biện.

Bởi vì paper này đã có thiết kế repair bốn tổ hợp.

Và nếu bạn chỉ viết:

> Sửa lỗi lớn nhất chưa chắc tốt nhất cho decision.

WM26 và nhiều nghiên cứu khác đã có kết quả gần như vậy.

### 8.2. Nhưng hai trục của bảng \\(2\times2\\) thực chất khác nhau

WM26 — Center × Response

P

Center dự đoán

Response dự đoán

S

Center dự đoán

Response thật

C

Center thật

Response dự đoán

E

Center thật

Response thật

Đề tài của bạn — State × Model

S₀M₀

Thông tin state không đầy đủ

Mean rollout

S₀M₁

Thông tin state không đầy đủ

Stochastic rollout đúng luật

S₁M₀

Current state đầy đủ

Mean rollout

S₁M₁

Current state đầy đủ

Stochastic rollout đúng luật

Bảng nhìn có hình dạng giống nhau, nhưng phép can thiệp khác nhau.

WM26 thay một thành phần của predicted endpoint bằng thành phần tương ứng lấy từ realized endpoint.

Bạn thay lượng thông tin hiện tại của controller hoặc cách model xử lý sự ngẫu nhiên trong tương lai.

Hai cách repair này không tương đương.

### 8.3. Khác biệt quan trọng nhất: thông tin tương lai

Hãy hình dung controller của bạn phải đưa ra quyết định ở thời điểm \\(t_0\\).

Nó biết hiện tại:

\\[ q_A(t_0)=10 \\]

\\[ q_B(t_0)=20 \\]

Và mode B hiện tại là ON.

Đó là những gì \\(S_1\\) có thể cung cấp.

Nhưng nó không biết chính xác traffic sẽ xuất hiện trong 8 giây tới.

Ví dụ:

\\[ w_1=\text{traffic thấp} \\]

\\[ w_2=\text{traffic cao} \\]

Controller không biết \\(w_1\\) hay \\(w_2\\) sẽ xảy ra.

Nó chỉ tính expected cost:

\\[ J(a\mid x) = \mathbb E_w[C(a,x,w)] \\]

Còn trong WM26, phép C/S repair sử dụng encoded realized endpoints của các action sequences.

Tức là trong các thí nghiệm chẩn đoán đó, tác giả đã thực sự thử các action trong simulator rồi sử dụng kết quả tương lai của chúng để sửa prediction.

Đây là một lượng thông tin mạnh hơn rất nhiều so với current-state revelation.

Vì vậy phép sửa Center/Response của WM26 không phải phép sửa State/Model của bạn.

### 8.4. Khác biệt thứ hai: Model \\(M_0\\) của bạn không phải Center Error

Đây là chỗ dễ nhầm nhất.

Bạn có thể nghĩ:

> WM26 sửa Center, còn tôi sửa State. Có phải hai thứ tương đương không?

Không.

Center của WM26 là trung bình latent endpoints trên một tập các action khác nhau:

\\[ \bar z=\frac1K\sum_j z_j \\]

Còn \\(M_0\\) của bạn dùng mean traffic/arrival trong rollout, tức trung bình theo future uncertainty.

Hai phép trung bình khác nhau:

\\[ \boxed{ \text{WM26: trung bình qua actions} } \\]

\\[ \boxed{ M_0:\text{ trung bình qua khả năng traffic tương lai} } \\]

Điều này rất quan trọng.

Nếu bạn chỉ thấy chữ mean ở cả hai bài rồi cho rằng chúng cùng một model approximation, bạn sẽ so sánh sai về mặt toán học.

### 8.5. Khác biệt thứ ba: bài toán và mục tiêu đánh giá

| Thành phần           | WM26                                                   | Đề tài bạn                                                 |
| -------------------- | ------------------------------------------------------ | ---------------------------------------------------------- |
| Hệ thống             | Robot/navigation simulators                            | Queue routing với ON/OFF traffic                           |
| Model                | Neural latent predictors                               | Fluid mean rollout và stochastic rollout                   |
| Action               | Nhiều candidate sequences                              | Stay hoặc Switch                                           |
| Thời điểm quyết định | Các candidate từ cùng start; có thêm closed-loop tests | Một quyết định tại \\(t_0\\)                               |
| Reference            | Realized endpoints, ranking, best fixed-pool candidate | Expected-cost oracle không biết tương lai                  |
| Câu hỏi              | Sửa center hay response hiệu quả hơn?                  | State/model repair gains và \\(\Gamma\\) thay đổi thế nào? |

Nhưng nhớ: khác lĩnh vực tự nó không tạo ra novelty.

Một reviewer không quan tâm việc người khác dùng robot còn bạn dùng network, nếu hai nghiên cứu chỉ lặp lại cùng một kết quả toán học.

Khác biệt thực sự phải làm thay đổi câu hỏi, estimand hoặc những prediction có thể kiểm được.

## 9. WM26 có đe dọa PC3 của bạn không?

Có, nhưng chưa đủ để kết luận PC3 phải DROP.

WM26 là một prior mạnh vì:

- Nó đã dùng bảng repair \\(2\times2\\).
- Nó đã đo repair priority đối với decision quality.
- Nó cho thấy prediction error magnitude và decision improvement có thể không khớp.
- Nó nhấn mạnh cần phân biệt oracle diagnostic với deployable controller.

Tuy nhiên, trong các phần được đối chiếu, WM26 chưa xác nhận đã đo đúng interaction:

\\[ \Gamma= G\_{S\mid M_1}-G_S \\]

với can thiệp lộ current hidden state và sửa mean-future approximation dưới cùng một posterior như contract của bạn.

Vì vậy, cách ghi phù hợp hiện tại là:

| Claim                                                                                             | Đánh giá             |
| ------------------------------------------------------------------------------------------------- | -------------------- |
| “Lần đầu dùng 2×2 repair”                                                                         | Không còn phù hợp    |
| “Lần đầu chứng minh prediction error khác decision quality”                                       | Không còn phù hợp    |
| “Nghiên cứu State × Model interaction trên expected routing regret với những intervention cụ thể” | Còn đáng kiểm        |
| “Interaction do queue dynamics tạo ra một mechanism mới”                                          | Chưa được chứng minh |
| “PC3 chắc chắn novel”                                                                             | Chưa thể kết luận    |

Một điều thú vị nữa: WM26 không chỉ có một kết quả dương rồi tuyên bố thành công. Paper công khai những trường hợp kết quả chưa được xác nhận, đặc biệt khi chuyển từ offline diagnostics sang closed-loop planning.

Đó là một thói quen rất đáng học cho nghiên cứu của bạn.

## 10. Sau khi đọc WM26, bạn cần làm gì cho Lesson 2.9?

Bạn không cần đọc cả 40 trang ngay.

Hãy tự đọc lại ba phần:

- Section 4.1, trang 4: Center/Response decomposition và vì sao tách được MSE.
- Section 5, trang 4–5: P/C/S/E, matched candidates và những metric đánh giá decision.
- Appendix F.1, trang 22–23: Các phép sửa Center/Response sử dụng thông tin gì và những contrast được so sánh.

Sau đó bạn cần tự trả lời:

1. Center của WM26 khác mean rollout của \\(M_0\\) như thế nào?
2. Repair C/S có được phép biết future realized endpoints không?
3. Tại sao bảng P/C/S/E không trực tiếp đo cùng \\(\Gamma\\) của bạn?

Nếu bạn giải thích được ba điều này mà không nhìn tài liệu, bạn đã nắm được phần WM26 quan trọng nhất đối với PC3.

### Gợi ý câu ghi vào Prior Boundary

**WM26 — Closest Prior cho PC3**

WM26 phân rã sai số dự đoán của Latent World Models thành center error và action-relative response error, đồng thời sử dụng thiết kế sửa chữa bốn tổ hợp để đánh giá tác động của từng loại lỗi đến chất lượng lựa chọn hành động. Công trình cho thấy thành phần chiếm phần lớn MSE không nhất thiết là thành phần có giá trị sửa chữa cao nhất đối với quyết định.

So với nghiên cứu hiện tại, WM26 thực hiện center/response repair sử dụng realized future endpoints trên tập candidate actions, trong khi nghiên cứu State × Model thay đổi riêng thông tin trạng thái hiện tại và cách biểu diễn bất định tương lai mà không cung cấp future realization cho controller. Vì vậy, hai thiết kế không trực tiếp đo cùng một estimand.

**Đánh giá tạm thời:** WM26 là prior mạnh cho thiết kế factorial repair và decision-aware fidelity. PC3 có thể tiếp tục được xem xét trong phạm vi can thiệp và estimand đã định nghĩa, nhưng chưa được xác nhận là novel. Cần tiếp tục kiểm bằng chứng thực nghiệm và các prior liên quan.

## 11. Kết luận: bạn cần hiểu điều gì sâu nhất từ paper này?

Nếu phải rút toàn bộ 40 trang còn ba ý:

Thứ nhất: Model dự đoán rất giống thực tế không có nghĩa nó hiểu đúng ảnh hưởng tương đối của từng action.

Thứ hai: Lỗi lớn nhất theo MSE chưa chắc là lỗi nên sửa trước. Cần kiểm xem sửa lỗi nào cải thiện lựa chọn hành động thật sự.

Thứ ba: Nghiên cứu của bạn và WM26 giống nhau ở tư duy đánh giá chất lượng quyết định bằng những can thiệp có kiểm soát. Nhưng WM26 tách Center × Response, còn bạn tách Current-State Information × Stochastic-Model Fidelity, nên chúng chưa phải cùng một estimand.

Điều bạn có thể học sâu nhất từ WM26 không phải là sao chép bảng \\(2\times2\\), mà là cách tác giả đi từ một phép phân rã sai số chính xác → can thiệp từng thành phần → kiểm decision quality → xác định giới hạn của kết luận.

Đó cũng là tiêu chuẩn tốt để bạn xây dựng và đánh giá PC3, PC4, PC5 trong Phase 3.
