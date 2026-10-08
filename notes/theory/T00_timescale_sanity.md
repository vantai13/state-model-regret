# T00 — Timescale sanity (thứ tự độ lớn)

Tác giả: **Doan Van Tai** · Ngày: **08/10/2026**.

> **Nguồn gốc.** Cập nhật theo phương án A tác giả cung cấp: giữ cả neo (a), (b), tuổi thông tin thành trục quét thay neo testbed (DL-008). Bảng sinh bằng [script](../../experiments/lessons/l0_6_timescale.py), kiểm bằng [10 test](../../tests/test_timescale.py). Bài tác giả tự tính tay và tự đọc nguồn còn chờ ở [L0.6](../lessons/L0.6_scope.md); đối chiếu kỹ thuật không thay các bài đó.

## Câu hỏi
Queue có còn "nhớ" trạng thái đủ lâu so với tuổi thông tin cộng độ trễ thực thi action không? Đây là sàng lọc thứ tự độ lớn cho K9, chưa phải định lý về gain của repair backlog hoặc toàn bộ State repair.

## Công thức (fluid, một bottleneck) và đơn vị
$t_{\text{pkt}}=8L_{\text{pkt}}/R_{\text{link}}$ (s); $\mu_{\text{pkt}}=1/t_{\text{pkt}}$ (packet/s); $T_{\text{drain}}=q_0/\big((1-\rho)\mu_{\text{pkt}}\big)$ (s), chỉ dùng khi $\rho<1$. $L_{\text{pkt}}=1500$ byte.

$q_0$ tính bằng packet; $R_{\text{link}}$ bằng bit/s (Mb/Gb theo lũy thừa 10); $\rho$ là offered load/service rate, không thứ nguyên. Miền dùng: $q_0\ge0$, $0\le\rho<1$, link và kích thước packet dương. $\tau_{\text{eff}}$ là tuổi hiệu dụng khi quyết định; $d_{\text{act}}$ từ quyết định tới action có hiệu lực trên data plane; $h=H\Delta t$ là horizon vật lý chung. Cả ba tính bằng giây; D8 dùng slot nên cần quy đổi ở L1.8.

## ρ nào cho câu hỏi nào
- **Kiểm timescale (note này):** $\rho$ **trước** quyết định, vì Switch chưa xảy ra trong lúc thông tin đang cũ dần. Dùng tải sau Switch cho giai đoạn trước action có thể làm drain dài hơn ở queue nhận thêm traffic; queue giảm tải có hướng khác. Phải chỉ rõ queue/giai đoạn.
- **Chọn $H$ (L1.8):** $\rho$ **sau** Switch, như $T_{\text{drain}}=q_0/(\mu-\lambda_B-\delta\lambda)$ của Final Review §5.3.

## Từ chu kỳ đo tới tuổi thông tin
Giả định phase quyết định phân bố đều trong chu kỳ đo $P$, độ trễ truyền/xử lý $L$ cố định, không mất mẫu hoặc đảo thứ tự; giá trị đo trung bình trên cửa sổ $W$ ($W=0$ với mẫu tức thời). Quy ước tuổi hiệu dụng theo tâm cửa sổ:

$$\tau_{\text{eff}}\approx \frac{P}{2}+L+\frac{W}{2}\quad(\text{xấu nhất}\approx P+L+W/2)$$

Đây là tuổi **trung bình** theo giả định trên; biểu thức “xấu nhất” là xấp xỉ trong cùng mô hình, không phải cận latency thực tế khi có jitter/mất mẫu. Chu kỳ polling và latency đo đạc trong paper không tự bằng $\tau_{\text{eff}}$.

Ví dụ: SNMP poll 60 s, rate lấy từ hiệu counter ($W=60$ s), $L\approx0$ → $\tau_{\text{eff}}\approx60$ s (hàm `effective_age_s`, có test).

## Chế độ telemetry và độ trễ action theo literature
| Chế độ | Ví dụ | Thang thời gian | Nguồn | Loại nguồn |
|---|---|---|---|---|
| Cỡ ms | Planck: port mirroring | Đo flow/link rate 0,280–7 ms ở 1 Gb/s, 0,275–4 ms ở 10 Gb/s; tùy buffering | [Rasley et al., SIGCOMM 2014](https://users.cs.utah.edu/~brent/docs/planck.sigcomm14.pdf), abstract/§5.5 | Primary cho thí nghiệm Planck; chưa có record tác giả tự đọc |
| Dưới 1 s | Đọc counter OpenFlow; OpenSample; Mahout polling | 75–200 ms; 100 ms; 190 ms | Planck §2.2–2.3, Table 1 | Trích lại so sánh prior trong paper; 190 ms là polling, không phải end-host detection của Mahout |
| Vài giây | MicroTE; Hedera; streaming telemetry | Control loop MicroTE 1 s (Planck §8); Hedera polling/estimate/schedule 5 s (§5.4); streaming cỡ giây là mô tả vendor | [Hedera, NSDI 2010](https://raghavan.usc.edu/papers/hedera-nsdi10.pdf); Planck; Kentik | Hedera primary; MicroTE trích lại; streaming thứ cấp, chưa là đo AoI |
| Vài chục giây trở lên | SNMP polling | Chu kỳ 30 s – 5 phút theo mô tả vendor, không phải AoI đo | [Kentik](https://www.kentik.com/kentipedia/snmp-vs-streaming-telemetry/) | Thứ cấp được cung cấp; chỉ động cơ chọn lưới, cần nguồn measurement tốt hơn |
| $d_{\text{act}}$ | Planck ARP/OpenFlow; switch phần cứng | Response ARP 2,5–3,5 ms / OpenFlow 4–9 ms; gap confirmation/data plane 250/400 ms ở hai switch | Planck §7.2/Fig. 16; [Kuźniar et al. 2018](https://dejankostic.com/documents/publications/switches-elsevier18-author-copy.pdf), §4.1/Table 2 | Primary; định nghĩa khoảng thời gian khác nhau, không cộng máy móc |

**Phạm vi nguồn:** Hedera 5 s do giới hạn đọc register của OpenFlow NetFPGA trong triển khai đó, không phải yêu cầu cố hữu của thuật toán. Planck response đo từ gửi notification tới collector thấy packet có MAC mới, không phải toàn bộ tuổi measurement + decision + actuation. Kuźniar báo chênh lệch confirmation/data plane, không phải end-to-end delay use case hay cận trên phổ quát. Đối chiếu kỹ thuật ngày 08/10; chưa ghi tác giả đã tự đọc.

[Đặc tả gNMI §3.5.1.5.2](https://github.com/openconfig/reference/blob/master/rpc/gnmi/gnmi-specification.md) cho phép yêu cầu `sample_interval`, tùy target hỗ trợ; không ấn định chu kỳ cỡ giây cho mọi gNMI. Các khoảng vendor trong bảng chỉ là mô tả thứ cấp, không là ràng buộc protocol hay số đo use case.

Testbed dt4n cũ (mean AoI theo từng ô 0,33–0,37 s, inventory EV-10) **không dùng làm neo**: đó là một prototype dựng trên Ditto, không đại diện cho telemetry nói chung hoặc đủ để chốt chế độ use case.

**Quan sát được gì:** contract D8 giả định quan sát được **backlog**. Planck chứng minh ước lượng flow/link **rate** từ mirroring, chưa chứng minh đo backlog. INT có thể mang queue metadata ([GÉANT D6.7 §3](https://resources.geant.org/wp-content/uploads/2022/02/D6.7-Network_Technology_Evolution_Update.pdf)); khả năng đó chưa cho tuổi backlog tới controller. Counter byte/packet lấy hiệu cho rate, không tự cho backlog; metric thực có tùy thiết bị/schema. Mô hình observation theo chế độ là OPEN (contract §9). Quét tuổi với schema backlog cố định trước; nếu đổi sang rate-only phải tách scenario/version, giữ observation/estimator giống nhau giữa các ô cùng $S$ và không gán hiệu ứng đổi schema cho riêng tuổi.

## Bảng $T_{\text{drain}}$
| Link | $t_{\text{pkt}}$ | $q_0$ | $T_{\text{drain}}$, $\rho=0{,}5$ | $T_{\text{drain}}$, $\rho=0{,}8$ |
|---|---:|---:|---:|---:|
| 10 Mb/s | 1,2 ms | 100 | 0,24 s | 0,6 s |
| 10 Mb/s | 1,2 ms | 1000 | 2,4 s | 6 s |
| 100 Mb/s | 0,12 ms | 100 | 24 ms | 60 ms |
| 100 Mb/s | 0,12 ms | 1000 | 0,24 s | 0,6 s |
| 1 Gb/s | 12 µs | 100 | 2,4 ms | 6 ms |
| 1 Gb/s | 12 µs | 1000 | 24 ms | 60 ms |
| 10 Gb/s | 1,2 µs | 100 | 0,24 ms | 0,6 ms |
| 10 Gb/s | 1,2 µs | 1000 | 2,4 ms | 6 ms |

## Vùng theo chế độ telemetry
Cột là tổng $\tau_{\text{eff}}+d_{\text{act}}$ **minh họa** trải bốn chế độ. 5 ms không phải một số đo end-to-end backlog/control loop của Planck; chu kỳ polling 0,1–1 s của neo (b) cần đổi qua $P,L,W$ và cộng delay, không tự bằng cột 0,2/1 s. Vùng xếp theo $T_{\text{drain}}$ nhỏ hơn của hai mức $\rho$ (thận trọng khi tìm vùng còn liên quan; không loại mọi mức tải); ngưỡng "gấp 3 lần" là quy ước thứ tự độ lớn, không phải ngưỡng khoa học.

| Link, $q_0$ | 5 ms | 0,2 s | 1 s | 5 s | 30 s |
|---|---|---|---|---|---|
| 10 Mb/s, 100 | ① | ② | ③ | ③ | ③ |
| 10 Mb/s, 1000 | ① | ① | ② | ② | ③ |
| 100 Mb/s, 100 | ① | ③ | ③ | ③ | ③ |
| 100 Mb/s, 1000 | ① | ② | ③ | ③ | ③ |
| 1 Gb/s, 100 | ② | ③ | ③ | ③ | ③ |
| 1 Gb/s, 1000 | ① | ③ | ③ | ③ | ③ |
| 10 Gb/s, 100 | ③ | ③ | ③ | ③ | ③ |
| 10 Gb/s, 1000 | ② | ③ | ③ | ③ | ③ |

| Vùng | Điều kiện | Ý nghĩa |
|---|---|---|
| ① | $z\ge3$ | Thông tin backlog có thể có giá trị |
| ② | $1/3<z<3$ | Có thể có giá trị; timing quyết định, RQ3 thành then chốt |
| ③ | $z\le1/3$ | Backlog ban đầu xả nhanh trong fluid; chưa chứng minh stochastic gain bằng 0. Mode chậm là hypothesis riêng |

Đặt $z=T_{\text{drain}}/(\tau_{\text{eff}}+d_{\text{act}})$. `zone` dùng dung sai tương đối $10^{-12}$ tại biên để tránh đổi nhãn do float. Điểm sát biên 3 hoặc 1/3 không là kết luận chắc; đổi factor có thể đổi vùng.

## Kết luận và domain
Giá trị có thể có của thông tin backlog phụ thuộc **tỉ số** $T_{\text{drain}}/(\tau_{\text{eff}}+d_{\text{act}})$, không phụ thuộc riêng tốc độ link. **Trong lưới đã khai báo**, link 1–10 Gb/s chỉ có vùng ①–② ở cột 5 ms; ở 1/5 s chỉ 10 Mb/s, 1000 packet còn vùng ②; ở 30 s mọi dòng là ③. Không suy điều kiện cần cho mọi backlog, tải hay link.

**Domain của contract:** $\tau_{\text{eff}}+d_{\text{act}}$ là trục quét qua bốn chế độ trên; kết quả báo theo tỉ số. Hai neo cụ thể:

- **(a)** đo cỡ ms + link datacenter 1–10 Gb/s (cột 5 ms): 1 Gb/s ở vùng ①–②; 10 Gb/s ở vùng ② khi backlog hàng nghìn packet, vùng ③ khi backlog nhỏ.
- **(b)** polling 0,1–1 s + link edge 10–100 Mb/s (cột 0,2 s và 1 s): dùng các tổng minh họa 0,2/1 s để kiểm; ở 0,2 s phần lớn ở ①–②, trừ 100 Mb/s, 100 packet; ở 1 s chỉ 10 Mb/s, 1000 packet ở ②. Chu kỳ không đồng nhất với tổng delay.

## Hệ quả
1. **Scope:** báo kết quả theo $T_{\text{drain}}/(\tau_{\text{eff}}+d_{\text{act}})$ và $h/T_{\text{drain}}$; trục chế độ telemetry; hai neo (a), (b).
2. **Phần state đáng sửa:** backlog ở các điểm ③ không là ứng viên ưu tiên theo fluid. Mode bền lâu có thể còn hữu ích, cần kiểm riêng; telemetry không đo mode chưa cho feasible refresh mode. Dùng ô chẩn đoán $S_0^{\tau=0}$ (contract D22). Ở chế độ cỡ ms, backlog có thể quan trọng.
3. **Model repair:** xét $h$ so với động học **sau** Switch; tuổi telemetry không tự quyết định toàn bộ gain của model. Baseline state/observation vẫn ảnh hưởng các contrast có điều kiện.
4. **$\Delta t$, $H$, lưới $\tau$ (L1.8):** lưới $\tau$ phủ bốn chế độ; chọn $\Delta t$, $H$ sao cho mỗi neo có điểm ở vùng ① hoặc ②.
5. **Observation:** metric/schema và pipeline thực quyết định quan sát được backlog hay chỉ rate, không chỉ tên chế độ (D8, §9).

## Giới hạn: note này KHÔNG chứng minh
Xấp xỉ fluid một bottleneck; không có ngẫu nhiên, không có drop, không có TCP. Các chế độ là thang thời gian điển hình trong literature, không phải số đo của use case; số liệu SNMP và streaming đến từ nguồn thứ cấp. Không đo timing thật (Phase 8). Không chứng minh gain dương ở ① hoặc gain bằng 0 ở ③; drain fluid không là mixing time của queue stochastic. Mode persistence cũng chưa được mô hình trong note. Chỉ dùng tỉ số với mẫu số dương/hữu hạn; $\rho\ge1$ trả `inf`, $q_0=0$ drain bằng 0, không suy domain từ các tỉ số không hợp lệ.

## Provenance testbed giữ để đối chiếu lịch sử

AoI dưới đây là một điểm dữ liệu của prototype, **không dùng làm neo** hay đo backlog telemetry. Bảng T00 trước phương án A được lưu tại [commit ce9991d](https://github.com/vantai13/state-model-regret/blob/ce9991df8e1068d76e59416a49842763ccf7afe1/notes/theory/T00_timescale_sanity.md); không đổi archive hoặc mất checksum.

Nguồn immutable tại commit `e669f5c8053a81d6de192de9f9d0d6304ee67802`, tag `archive-switch-or-stay-2026-10-02` của repo cũ:

- [AoI JSON](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/data/aoi_measured/aoi_v7_estimates.json), SHA-256 `5f3e6a01173bb82802a397b260251bc8098b7bbffdb8571966655fd071fca64f`.
- [PROVENANCE](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/data/aoi_measured/PROVENANCE.md), SHA-256 `2b4220c879cba663cdb25169f63a8f7f77086dfc22153f01992f7ccfc8cb823d`.

Đối chiếu kỹ thuật ngày 08/10/2026: 10 ô = 2 mode × 5 mức tải, 28.776 quan sát/ô. Khoảng mean **0,329887–0,374230 s**; khoảng p95 **0,546181–0,604755 s**. Đây là Mininet + Ditto của dt4n; nhãn CLEAN/PROD là hai mode testbed, không phải bằng chứng production. Scope nền xem [EV-10](../00_evidence_inventory.md) và [giới hạn raw backup](../verification/raw_backup_manifest.json).

| Ô | n | Mean AoI (s) | p95 AoI (s) |
|---|---:|---:|---:|
| clean_rho0.700 | 28776 | 0,363145 | 0,570401 |
| clean_rho0.850 | 28776 | 0,367107 | 0,581279 |
| clean_rho0.900 | 28776 | 0,373631 | 0,604755 |
| clean_rho0.925 | 28776 | 0,374230 | 0,604636 |
| clean_rho0.960 | 28776 | 0,366507 | 0,571865 |
| prod_rho0.700 | 28776 | 0,347289 | 0,560401 |
| prod_rho0.850 | 28776 | 0,343216 | 0,559331 |
| prod_rho0.900 | 28776 | 0,345256 | 0,557988 |
| prod_rho0.925 | 28776 | 0,329887 | 0,546181 |
| prod_rho0.960 | 28776 | 0,347054 | 0,558846 |

AoI trong nguồn tính từ cuối cửa sổ đọc counter tới khi HTTP GET trả về. Rate được trung bình trên cửa sổ $W\approx0{,}5$ s; tuổi hiệu dụng theo quy ước PROVENANCE xấp xỉ AoI + $W/2$, khoảng **0,58–0,62 s**. Bản T00 lịch sử dùng 0,35 s làm kịch bản đại diện cho bậc AoI testbed, chưa là số đo backlog telemetry riêng. Phương án A bỏ vai trò neo của những số này; với mẫu backlog tức thời không cộng $W/2$.

## Chạy lại và tự kiểm

```bash
python -m pytest -q                              # 11 test: 10 timescale + 1 smoke
python -m experiments.lessons.l0_6_timescale     # ma trận 8 × 5
python -m experiments.lessons.l0_6_timescale 0.2 # bảng chi tiết
python -m experiments.lessons.l0_6_timescale 1.0
```

Bài tác giả: tự tính dòng 10 Mb/s, 100 packet, rho = 0,8 so với 0,2/1 s; so nhãn min hai tải, rồi đổi SNMP poll/cửa sổ 30 s thành tuổi hiệu dụng. Ghi lời giải riêng tại [L0.6](../lessons/L0.6_scope.md). Cột 30 s đều ③ trong ma trận **không chứng minh** State repair vô ích; mode chậm có thể liên quan nếu đủ bền và suy được từ observation, nhưng chưa có bằng chứng gain hoặc operator refresh khả thi.

**Trạng thái:** lựa chọn phương án A và cả hai neo do tác giả cung cấp ngày 08/10; các bài tự tính/giải thích, tự đọc paper, xác nhận estimator/rủi ro và gate contract/Phase 0 còn chờ.
