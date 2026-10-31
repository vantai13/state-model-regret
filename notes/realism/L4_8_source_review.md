# L4.8 — source review và declared use case

Người phụ trách: **Doan Van Tai** · 31/10/2026. AI targeted reread, không
author-self; không đổi reading progress/PC/catalog26/realismv1. Không có full
lesson4.8 mới; đây là scope thực thi từ hướng dẫn tiếp tục và Phase4v2.

## Use case đang dùng để trình bày

**DC-inspired one-shot aggregate steering:** một twin so hai lựa chọn giữ
managed aggregate trênA hoặc chuyển sangB, hai queue có capacity bằng nhau,
trong một horizon đã cho. Đây là controlled abstraction trong contextDC đã
được duyệt, không nhận đã dựng một production SDN/TCP/flowlet controller.
Giữ contextedge trong các artifact cũ; không xóa hoặc tự gán OUT cho nó.

## Ba nguồn cũ đã kiểm lại

| Nguồn/version/mức đọc phiên này | Evidence có vị trí | Bridge chưa có |
|---|---|---|
| [ZLK17](https://doi.org/10.1145/3131365.3131375), IMC2017, authorPDF8trang, AI-T PDF1/3/4/5/7; Table2/PDF4 xem ảnh | §4.2/PDF3 có server-ToR10Gb/s; §4.1/PDF3 phân biệt byte-counter25us và peak-buffer counter50us. §5.1/PDF4 định nghĩa hot theo egress>50%; p90hotduration<200us. §5.2/Table2/PDF4 cho thấy hot dynamics không giống symmetric exponential mode; §6.4/PDF7 shared-buffer occupancy được normalize theo max đã quan sát | Local sampling interval không bằng tuổi backlog tới controller; peak-buffer khác exact instantaneous backlog; hotduration không bằng mean offered-input mode. Egress rate không cho offered-input peak. Không absolute per-queue buffer. Fig10caption300us và text50ms vẫn giữ riêng |
| [BAM10](https://doi.org/10.1145/1879141.1879175), IMC2010, PDF14trang, AI-T PDF1/3/6/7/9; Table4/PDF7 xem ảnh | §3.1/PDF3 SNMP1–30phút và packet traces10us; §5.2/PDF6–7 định nghĩa ON/OFF bằng interarrival95 và fits lognormal/Weibull; §6.2–6.3/PDF9 dùng5phút/hotspot70% | Definitions khác hai fixed input rates ±.6capacity với symmetric exponential holding. Poll/window/utilization threshold không phải backlog age, holdingh hoặc offered-input envelope |
| [NDT1](https://arxiv.org/abs/2205.14206v2), DOI10.1109/MCOM.001.2200012, accepted arxivv2, AI-T PDF1/2/4/5/6; Fig4/PDF5 xem ảnh | §II/TableI/PDF2 cho workflow what-if; §IV-B/PDF5 optimizer đổiOSPFweights và chọn routing theo predicted delay, groundtruth simulator trên synthetic25nodes; §V/PDF6 nêu data/generalization challenges | Hỗ trợ motivation về decision pipeline; không đo backlog/mode/age/holding của plant, không xác nhận2×2 interventions hoặc deployment validity |

Các observations là theo đúng bản/năm đã đọc; không nhận đại diện mọiDC hiện
nay. Hai measurement studies vừa hỗ trợ motivation vừa cho evidence trái giả
định traffic đơn giản. NDT1 là motivation, không empirical calibration của repo.
Sourceheader/DOI/venue được đối chiếu Crossref phiên này;0nguồn mới/0download.
BaPDFlocal khớp catalogSHA; không đọc abstract thay fulltext cho các claim trên.
Đây là targeted, không full-read, không systematic search hoặc saturation.

T00/realismworksheetv1 được đọc ở mức note: không nhận đã reread primary
Planck/Hedera/Kuźniar trong phiên này. Vì vậy không dùng các thời gian ở đó
như một phép đo end-to-end backlogAge + actuation mới.

## Những gì có thể chốt và chưa thể chốt

1. **Chốt narrative và mathematical domain:** bối cảnhDC, one-shot aggregate,
   fixedlaw/cost/information của contract. Implementation hiện thêm điều kiện
   Bpoststable; đó là computational subset, không điều kiện vật lý cho finiteh.
2. **Chưa có empirical numeric domain:** không có một bộ measurement cùng
   schema cho backlogτ, holdh, inputlaw, buffer vàactuation. Giữnull; không
   lấy những số khác định nghĩa để tạo IN hoặc OUT. Realismv1 giữ nguyên.
3. **Chốt claim boundary:** statements có điều kiện trên plant, không nói
   “refresh backlog triển khai được có hại” khiS1biếtmode vàD22chưa có.
   Không đưa theoremP-clip hoặc identityS_clip/sigma=1 thành hypothesis
   magnitude dự báo held-out. Paper có thể trình bày theorem trong phần giải
   thích; L4.9 vẫn cần prediction có thể sai vàtestdesign riêng.

## Quy đổi vật lý không phải calibration

Cho capacityCbit/s vàtimeScale s=tau_phys/1s, rateScale r=C/10. Đổi rates
theor, time theos, backlog theo**r*s**, cost theo**r*s²**. Khi đó recurrence
và normalizedcontrasts bất biến. Không giữ q=1 là một physicalpacket cố định
đồng thời tự chọnC/tau; đó là một fluid-work quantum sau quy đổi.

Anchor cũ10Gb/s,tau10ms **chỉ minh họa**, không measuredbacklogage. Mộtmodel
backlogunit tương đương1.25MB fluidwork. Horizon/mode times từ metadata sẽ
được báo theo anchor này với nhãnILLUSTRATIVE_ONLY; capacity được quan sát ở
ZLK17 không biến tau giả định hoặc entire tuple thành empirical validation.

Để nâng claim realism cần một trace/measurement cùng usecase có timestamped
backlog, offeredinput + managedaggregate, hold/action timing vàperqueuebuffer,
rồi kiểm mapping/law/cost compatibility. Không yêu cầu đọc thêm hàng chục bài
hoặc chạy thêmclipping để thay thế evidence còn thiếu. Phiên này dừng tại
boundedreview ba nguồn đã có; nếu bổ sung nguồn mới về sau áp approval rule.
