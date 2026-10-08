# T00 — Timescale sanity (thứ tự độ lớn)

Tác giả: **Doan Van Tai** · Ngày: **08/10/2026**.

> **Nguồn gốc.** Tích hợp nội dung File 3 tác giả cung cấp ngày 08/10/2026. Bảng sinh bằng [script](../../experiments/lessons/l0_6_timescale.py), bất biến kiểm bằng [7 test](../../tests/test_timescale.py): **7 passed**, đã chạy và đối chiếu ba mức 0,35 / 0,6 / 1,0 s ngày 08/10/2026. AoI được đối chiếu với JSON/PROVENANCE từ immutable archive; không tái tính raw. Chưa có record tác giả tự tính tay hoặc trả lời kín sách trong L0.6; phần tính minh họa dưới đây không thay bài làm đó.

## Câu hỏi

Queue có còn “nhớ” backlog đủ lâu so với tuổi thông tin cộng độ trễ thực thi action không? Đây là kiểm thứ tự độ lớn cho rủi ro timescale K9, không phải chứng minh State repair có giá trị.

## Công thức fluid và đơn vị

Với một bottleneck, packet cùng kích thước và offered traffic không đổi:

$$
t_{\text{pkt}}=\frac{8L_{\text{pkt}}}{R_{\text{link}}},\qquad
\mu_{\text{pkt}}=\frac{1}{t_{\text{pkt}}},\qquad
T_{\text{drain}}=\frac{q_0}{(1-\rho)\mu_{\text{pkt}}}\quad(0\le\rho<1).
$$

| Ký hiệu | Định nghĩa | Đơn vị / nguồn |
|---|---|---|
| $L_{\text{pkt}}$ | Kích thước packet, dùng 1500 byte trong bảng | byte; lựa chọn minh họa |
| $R_{\text{link}}$ | Tốc độ link | bit/s; bốn mức minh họa, Mb/Gb dùng lũy thừa 10 |
| $t_{\text{pkt}}$ | Thời gian truyền một packet | s; byte nhân 8 đúng một lần |
| $\mu_{\text{pkt}}$ | Tốc độ phục vụ packet | packet/s |
| $q_0$ | Backlog ban đầu | packet; 100/1000 là giá trị khảo sát |
| $\rho$ | Offered load / service rate trước quyết định | Không thứ nguyên; 0,5/0,8 là giá trị khảo sát |
| $T_{\text{drain}}$ | Thời gian xả backlog bằng capacity còn dư theo fluid | s; không phải thời gian mất nhớ đã đo của queue ngẫu nhiên |
| $\tau_{\text{eff}}$ | Tuổi hiệu dụng của thông tin tại lúc quyết định | s; observation tức thời dùng AoI, rate trung bình cửa sổ xấp xỉ AoI + $W/2$ |
| $d_{\text{act}}$ | Từ quyết định tới lúc action có hiệu lực trên data plane | s; cần đo cho use case ở Phase 8 |
| $h$ | Horizon vật lý chung, $h=H\Delta t$ theo contract D2 | s; giá trị khóa ở L1.8 |

Capacity còn dư $(1-\rho)\mu_{\text{pkt}}$ dùng để xả backlog. Khi $\rho\ge1$, queue có backlog không tự xả theo fluid; script trả `inf`. Khi $q_0=0$ và $\rho<1$, drain bằng 0. Chỉ dùng các tỉ số có mẫu số dương, hữu hạn; không suy diễn domain ratios từ `inf` hoặc drain bằng 0.

## ρ nào cho câu hỏi nào

- **Kiểm timescale:** dùng $\rho$ **trước** quyết định, vì trong lúc observation cũ dần và action chưa tới mạng, Switch chưa thay đổi tải. Dùng tải sau Switch để tính giai đoạn này có thể làm queue trông nhớ lâu hơn.
- **Chọn $H$ ở L1.8:** xét động học **sau** Switch, ví dụ $q_0/(\mu-\lambda_B-\delta\lambda)$ khi mẫu số dương; đây là câu hỏi khác. Đối chiếu Final Review §5.3.

## Ba vùng và quy ước phân loại

Đặt $z=T_{\text{drain}}/(\tau_{\text{eff}}+d_{\text{act}})$. Script dùng factor = 3; đây là quy ước đọc thứ tự độ lớn, không phải ngưỡng khoa học hoặc SLA.

| Vùng | Quy tắc trong script | Ý nghĩa trong xấp xỉ fluid |
|---|---|---|
| ① còn nhớ | $z\ge3$ | Backlog có thể còn liên quan khi action có hiệu lực; chưa chứng minh repair có gain |
| ② cùng cỡ | $1/3<z<3$ | Timing có thể quyết định; cần kiểm RQ3 |
| ③ đã quên | $z\le1/3$ | Backlog ban đầu xả nhanh hơn nhiều so với độ trễ; không phải miền ưu tiên cho repair backlog |

`zone` dùng dung sai số học tương đối $10^{-12}$ khi tỉ số nằm sát biên, tránh đổi vùng chỉ do biểu diễn float. Đổi factor thành 2 hoặc 5 có thể đổi một số nhãn vùng; các drain time không đổi.

## Bảng với tổng tuổi và độ trễ 0,6 s

Vùng xếp theo drain **nhỏ hơn** trong hai mức $\rho$, nên thận trọng về khả năng backlog còn sống. Hai cột drain vẫn báo riêng; nhãn chung không có nghĩa hai mức tải luôn cùng vùng.

| Link | $t_{\text{pkt}}$ | $q_0$ | $T_{\text{drain}}$, $\rho=0{,}5$ | $T_{\text{drain}}$, $\rho=0{,}8$ | Vùng |
|---|---:|---:|---:|---:|---|
| 10 Mb/s | 1,2 ms | 100 | 0,24 s | 0,6 s | ② cùng cỡ |
| 10 Mb/s | 1,2 ms | 1000 | 2,4 s | 6 s | ① còn nhớ |
| 100 Mb/s | 0,12 ms | 100 | 24 ms | 60 ms | ③ đã quên |
| 100 Mb/s | 0,12 ms | 1000 | 0,24 s | 0,6 s | ② cùng cỡ |
| 1 Gb/s | 12 µs | 100 | 2,4 ms | 6 ms | ③ đã quên |
| 1 Gb/s | 12 µs | 1000 | 24 ms | 60 ms | ③ đã quên |
| 10 Gb/s | 1,2 µs | 100 | 0,24 ms | 0,6 ms | ③ đã quên |
| 10 Gb/s | 1,2 µs | 1000 | 2,4 ms | 6 ms | ③ đã quên |

Mỗi lần tốc độ link tăng 10 lần, drain giảm 10 lần nếu giữ các tham số khác. Trong lưới này, từ 1 Gb/s trở lên đều là vùng ③; kết luận gắn với backlog, tải và độ trễ đã khai báo, không phải mọi link nhanh.

## Tuổi thông tin: số liệu và nguồn

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

AoI trong nguồn tính từ cuối cửa sổ đọc counter tới khi HTTP GET trả về. Rate được trung bình trên cửa sổ $W\approx0{,}5$ s; tuổi hiệu dụng theo quy ước PROVENANCE xấp xỉ AoI + $W/2$, khoảng **0,58–0,62 s**. Với mẫu backlog tức thời, không cộng $W/2$; **0,35 s** chỉ là kịch bản đại diện dựa trên bậc AoI testbed, chưa là số đo backlog telemetry riêng.

[White paper INT của Parniewicz và cộng sự, 25/02/2021](https://resources.geant.org/wp-content/uploads/2022/02/GN4-3_White-Paper_In-Band-Network-Telemetry.pdf) giới thiệu thử nghiệm INT trong mạng NREN. [GÉANT D6.7, §3](https://resources.geant.org/wp-content/uploads/2022/02/D6.7-Network_Technology_Evolution_Update.pdf) mô tả việc đưa timestamps và link/queue utilisation vào packet. Khả năng thu queue metadata không tự cho tuổi thông tin lúc controller dùng nó: **chưa có nguồn số đo phù hợp cho tuổi backlog telemetry tới controller ở link nhanh trong use case này**.

## Độ trễ action

Kuźniar, Perešíni, Kostić, Canini, *Computer Networks* 2018, §4.1/Table 2 báo một số switch có data plane chậm hơn control-plane confirmation khoảng **250 ms (HP 5406zl)** hoặc **400 ms (Pica8 P-3290)**. Đã đối chiếu kỹ thuật [bản tác giả](https://dejankostic.com/documents/publications/switches-elsevier18-author-copy.pdf) ngày 08/10/2026; có những corner case dài hơn nhiều, nên 400 ms không phải cận trên phổ quát.

Đây là chênh lệch giữa confirmation và rule thực sự có hiệu lực trong các thí nghiệm đó, không phải số đo end-to-end $d_{\text{act}}$ cho use case này. Tổng gần 0 ở phần actuation là giả định ideal diagnostic, không suy rằng paper đã chứng minh mọi hệ có latency dưới 1 ms. Phase 8 còn phải đo timing thật; chưa có record tác giả tự đọc paper.

Nguồn này đã nối với EV-29 trong [inventory](../00_evidence_inventory.md) ở File 5; đối chiếu kỹ thuật không thay record tác giả tự đọc.

## Độ nhạy theo tổng tuổi và độ trễ

**0,35 / 0,6 / 1,0 s là ba kịch bản**, không phải khoảng tin cậy hoặc cận trên của độ trễ. Chúng minh họa tuổi testbed cộng actuation từ ideal tới vài trăm ms; pipeline khác hoặc tail có thể nằm ngoài khoảng này.

| Link, $q_0$ | 0,35 s | 0,6 s | 1,0 s |
|---|---|---|---|
| 10 Mb/s, 100 | ② | ② | ③ |
| 10 Mb/s, 1000 | ① | ① | ② |
| 100 Mb/s, 100 | ③ | ③ | ③ |
| 100 Mb/s, 1000 | ② | ② | ③ |
| ≥ 1 Gb/s (mọi dòng trong lưới) | ③ | ③ | ③ |

Với **tổng 1,0 s**, không còn dòng nào ở vùng ①. Không suy điều đó từ riêng câu “action vài trăm ms”: nhãn còn phụ thuộc $\tau_{\text{eff}}$. Ví dụ tổng 0,65 s vẫn cho vùng ① ở 10 Mb/s, 1000 packet.

**Kết luận có điều kiện:** trong lưới minh họa và độ trễ cỡ testbed, backlog có triển vọng nhất ở link chậm/buffer sâu; ngay cả 10 Mb/s, 1000 packet cũng từ vùng ① xuống ② khi tổng tăng lên 1 s. Giữ domain “tỉ số neo link chậm” làm mặc định DRAFT, không kết luận đã có practical gain.

## Hệ quả với contract

1. **Scope:** báo theo $T_{\text{drain}}/(\tau_{\text{eff}}+d_{\text{act}})$ và $h/T_{\text{drain}}$, với các mẫu số hợp lệ; use case neo link chậm còn cần timing thực tế.
2. **Phần state:** mode chậm có thể còn hữu ích khi backlog nhanh thay đổi. Đây là hypothesis, chưa phải kết quả; ô phụ $S_0^{\tau=0}$ (D22) giúp phân biệt freshness với lợi ích thấy mode. Mode vẫn không có feasible refresh nếu telemetry không đo được nó.
3. **Model repair:** xét horizon so với động học sau Switch; tuổi telemetry không trực tiếp quyết định toàn bộ gain của model.
4. **L1.8:** chọn $\Delta t$, $H$ và regime sao cho nằm trong ①–② cả với kịch bản 1 s, hoặc ghi rõ kết quả chỉ đứng khi action đủ nhanh. Không khóa số chỉ từ note này.
5. **AS4:** actuation delay là ưu tiên kiểm của bản nháp, tác giả còn phải xác nhận lựa chọn trong [L0.6](../lessons/L0.6_scope.md). File 5 đã bổ sung điều kiện timing và giới hạn suy gain vào C9/EV-28 trong boundary/inventory.

## Giới hạn

Fluid một bottleneck, không ngẫu nhiên/drop/TCP; không mô hình persistence của hidden mode. Vùng ③ sàng lọc các regime backlog trong xấp xỉ này, **không phải định lý gain bằng 0 cho queue stochastic hoặc cho toàn bộ State repair**. Vùng ① cũng không chứng minh gain dương. Chưa đo timing mới, chưa rerun mạng và chưa xác nhận held-out cho Main RQ; G1 giữ nguyên.

## Chạy lại và tự kiểm

Từ gốc repo, tạo môi trường riêng rồi chạy:

```bash
python3 -m venv /tmp/state-model-regret-timescale-venv
/tmp/state-model-regret-timescale-venv/bin/python -m pip install pytest
/tmp/state-model-regret-timescale-venv/bin/python -m pytest -p no:cacheprovider tests/test_timescale.py -q
python3 -m experiments.lessons.l0_6_timescale
python3 -m experiments.lessons.l0_6_timescale 0.35
python3 -m experiments.lessons.l0_6_timescale 1.0
```

Đối chiếu AoI từ clone archive có tag:

```bash
git -C /path/to/archive-clone show archive-switch-or-stay-2026-10-02:data/aoi_measured/aoi_v7_estimates.json \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); [print(k, v["aoi"]["n"], round(v["aoi"]["mean"],6), round(v["aoi"]["p95"],6)) for k,v in d["cells"].items()]'
```

**Bài tính tay cho tác giả, chưa có record hoàn thành:** 10 Mb/s, $q_0=100$, $\rho=0{,}8$: tự tính $t_{\text{pkt}}$, $\mu$, $T_{\text{drain}}$, rồi so với 0,6 s. Ghi phép tính, giải thích dùng tải trước quyết định và câu trả lời ba câu về use case vào [L0.6](../lessons/L0.6_scope.md), đã có khung ở File 8. Giá trị tham chiếu từ script/test là 1,2 ms, khoảng 833,333 packet/s, 0,6 s, vùng ②; nhãn bảng dùng min của hai mức tải cũng là ②. Ở tổng 1 s, riêng $\rho=0{,}8$ vẫn ② nhưng nhãn theo min là ③; nhãn chung không loại được mọi mức tải.

### Trạng thái thực hiện

- [x] Note, script và test có đúng đường dẫn; tác giả ghi Doan Van Tai.
- [x] Chạy 7 test: **7 passed**; ba bảng CLI ở 0,35 / 0,6 / 1,0 s khớp bảng trong note.
- [x] Đọc JSON/PROVENANCE từ đúng commit/tag, kiểm hash và 10 ô AoI; không tái tính raw.
- [x] Đối chiếu nguồn primary về độ trễ switch; không coi là số đo use case.
- [ ] Tác giả tự tính tay một dòng, giải thích bằng lời mình và ghi vào L0.6.
- [ ] Tác giả xác nhận domain/rủi ro ưu tiên; cập nhật nguồn gốc khi có bài làm.

V9 có số liệu nguồn và nhãn giả định/thiếu nguồn rõ; chưa coi việc tích hợp tài liệu và chạy code là bằng chứng tác giả đã tự hiểu bài hoặc Phase 0 đã đóng.
