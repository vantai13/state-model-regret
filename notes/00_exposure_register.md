# Exposure register — khóa phạm vi đã biết ngày 07/10/2026

Tác giả xác nhận: confirmation không chỉ cần seed mới; workload/configuration/parameter regime dùng test prediction cũng không được là chính regime đã được chọn sau khi nhìn pattern. Đổi seed đơn độc không xóa selection theo regime. Không tuyên bố sổ này đầy đủ với mọi máy/sandbox.

| Seed / configuration | Đã dùng cho gì; trạng thái | Nguồn immutable / kiểm |
|---|---|---|
| **9101–9110**, PSA POS_probeB, H=0,5 s, a=0,05 s, C=10 Mb/s, K=83, G_all, luật Ī>0; prior B=0,80 hoặc 0,70; A T_tel=0,5 s/B=30 s | n02 factorial S/M/P; n02b inst/win/noisy; đã chạy/xem pilot, không cấp lại làm held-out RQ mới. S=staleness, M=measurement, P=parameter; không hiểu S/M là State/Model repairs. | [S13/S16–S19](verification/source_checks.json); n02 JSON seeds khớp 9101–9110; n02b CSV cũng khớp. |
| **99001–99002 / 99101–99102**, smoke info-arrangement | Nguồn sandbox nói đã dùng; output bị xóa mà chưa đọc. Không suy ra đã xem outcome; vẫn đánh dấu đã chạy và không cấp làm fresh. Chưa có output để tái kiểm độc lập. | [S08/S09](verification/source_checks.json). |
| **20001–20020**, confirm/frontier/explore anchor | Registry ngày 01/10 ghi đã dùng/đã xem; thắng dòng “20000–29999 chưa dùng” trong F6 ngày 30/09. | [S01/S08](verification/source_checks.json). |
| 30001–30020; 60001–63020; 70001–70008/71001–71008; 72001–72020/73001–73020 | Các dải confirm/map/explore lịch sử, có nhiều dải con; không mặc định fresh. | [Registry toàn bộ](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/notes/seed_registry.md). |
| 80001–80020/81001–81020; 86001–86020/87001–87020; 86001–86020/89001–89020 | GO/rollout, calibration dùng lại; trạng thái FIX/SYM/FF theo registry, không nâng validity thành viewed outcome. | S08. |
| 92001–92020/93001–93020; 94001–94020/95001–95020 | GO-check đã xem sandbox và tái lập local; không còn là xác nhận mù. | S06/S08/S21. |
| 9001–10000; 11001–11932, các dải con F2–F8 | Registry bao rộng, không có nghĩa mọi seed đã dùng; 9101–9110 nằm trong dải bao nhưng **chưa có dòng sử dụng n02 cụ thể**. Sổ này bổ sung mục đích/config, không khẳng định registry không bao phủ các số đó. | S08/S16–S18. |
| 90001–90020/91001–91060, rollout v6/R3_outage | Registry tại snapshot ghi “để dành, chưa mở”; chưa kiểm exposure ở nơi khác hoặc sau snapshot, không tự cấp lại. | S08/S22. |

## Quy tắc cho L1.7–L1.8

Thiết kế confirmation sau khi khóa sổ; tránh cả seed lẫn cấu hình exploratory đã ảnh hưởng hypothesis, chốt calibration/held-out workload trước test. Muốn dùng lại một mục phải gọi rõ replication/sensitivity, không gọi fresh confirmation. RNG phụ `[seed,424242]` không tự tạo test set độc lập.

## Bổ sung exposure Phase 1 — 21/10/2026

Các cấu hình dưới đây đã được dùng để học, kiểm code hoặc đọc outcome trong L1.2–L1.5.
Không có RNG/seed mới. Không gọi việc dùng lại chúng là held-out confirmation của A05.

| Configuration / phép kiểm | Exposure và phạm vi | Artifact |
|---|---|---|
| Ví dụ chuẩn H=2,c_A=c_B=3,u=2,b_A=1,B on/off=5/0,p=s=1/2,y=(2,0),tau=1,prior_on=1/2 | Đã xem J, oracle, gaps bốn ô, gains/gamma/I và patterns; thuộc worked example, không là workload held-out chưa thấy | [L1.3](verification/l1_3/report.md), [L1.4](verification/l1_4/report.md), [L1.5](verification/l1_5/report.md) |
| Lưới L1.2 5.832 cấu hình; L1.4 1.156 cấu hình bước 1/2 và 9.604 cấu hình bước 1/6 | Vét cạn verification, đã xem số đếm và invariants; không tự là target của RQ2 được chấm mù | [L1.2](verification/l1_2/report.md), [L1.4](verification/l1_4/report.md) |
| L1.5 lưới F5 81 cặp, belief 12.288 cấu hình; reweight D=(3/8,1/8,3/8,1/8) và (1/4,1/4,3/8,1/8) | Phép kiểm/negative controls được chọn có chủ đích để kiểm sức phát hiện và blind spot; không phải discovery hoặc confirmation về mạng | [Card L1.5](lessons/L1.5_experiment_card.md), [results.json](verification/l1_5/results.json) |

Chưa chọn/fit H0,H1 hoặc chia workload held-out; record này không tự gán toàn bộ các
regime chưa chạy thành đã exposed. Khi lập A05, phải đối chiếu cả các giá trị tham số
đã dùng ở lesson/sensitivity và outcome đã nhìn, không chỉ seed.

## Bổ sung exposure L1.6 A–D — 22/10/2026

| Configuration / phép kiểm | Exposure | Artifact |
|---|---|---|
| rate_on={3,4,5,6}, (p,s)={(1/2,1/2),(3/4,3/4),(3/4,1/2)}, yA={0,2,4}, yB={0,1,2,3}, u={1,2}, c3,bA1,rate_off0,H2,tau1 | Đã xem 864 matched prior1/4,1/2,3/4 và 576 wrong prior_S0=1/2; biết 5 negative GM. Không cấp lại làm fresh held-out | [L1.6](../results/lessons/l1_6/report.md), [config](../results/lessons/l1_6/config.json) |
| p=s=11/20 hoặc3/4; prior1/2 hoặc1/4; history (2,0)→(2,2), (2,0)→(2,0); observation tuổi2 | Đã xem posterior/evidence/gains theo persistence/cách condition D. Prior1/4 là biến thể khai báo, không là warm-up đã chạy | [Variants](../results/lessons/l1_6/persistence_variants.csv), [posterior](../results/lessons/l1_6/posterior_states.csv) |
| Tau3,H3,rate_on4,rate_off1,p3/4,s1/2,prior1/4,history (2,0)→(2,1)→(2,0) | Đã xem reference posterior/evidence1/16/conditional M0 và mutant bỏ off-rate | [Card](lessons/L1.6_experiment_card.md), [Results](../results/lessons/l1_6/results.json) |

Đây là verification và toy discovery, không có seed/RNG mới, chưa fit H0/H1 hoặc chấm
held-out. B1 sensitivities, state-mean shortcut, iid Jensen và ô backlog hiện tại cũng đã
được xem; dùng lại phải gọi replication/sensitivity đúng phạm vi.

## Giới hạn

Sandbox khác, Colab và máy ngoài phiên này chưa kiểm được. Không có outcome của smoke đã xóa để đo mức exposure mạnh hơn lời nguồn. Không chạy thêm simulation hoặc mở seed để dành trong L0.1 này.

## Bổ sung exposure L1.7 — ghi trước chạy ngày 22/10/2026

| Seed / regime | Đã thấy gì từ tài liệu; kế hoạch dùng | Artifact |
|---|---|---|
| Demo root144558766427411771296652109119745142241,episode0–1999; theta chuẩn,H6,x=(2,2,off) | Đã đọc Δ145/16,variances và MC của nguồn; sẽ kiểm CRN/offset bằng root đã cung cấp. Teaching/verification, không confirmation | [Seed register](seed_registry.md), [card](lessons/L1.7_experiment_card.md) |
| Theta chuẩn,H2 bốn state; H3,x=(2,2,off); H6,x=(2,2,on/off),(6,6,on),(10,10,on) | Đã xem J/Δ/covariance/gain hoặc cost của oracle/leak/honest từ lesson. H3 exact7.75/6.5/8.125 | [Report lần chạy](../results/lessons/l1_7/report.md) |
| H3/4/6,p=s=1/2 hoặc3/4,states(2,2,·),(2,0,·),(6,6,·),(10,10,·) | Phạm vi regime được lesson nhắc; không khẳng định đã chạy mọi Cartesian combination. Những outcome đã đọc không là fresh | Hai tài liệu người dùng cung cấp; hashes trong config L1.7 |
| p3/4,s1/2,H4,x=(2,2,on),(2,0,off) | Sampler verification; nguồn không in J, nhưng runner lần này sẽ lưu/in mean và exact J để kiểm; các outcome đó được đánh dấu đã xem khi chạy | [Sampler CSV](../results/lessons/l1_7/sampler_checks.csv) |
| Tape H6,extra1; H4 hai background khác nhau có weighted arrivals bằng nhau | Golden/negative control có chủ đích; không là quan sát thực nghiệm mạng | [Exact paths](../results/lessons/l1_7/exact_paths.csv), [diagnostics](../results/lessons/l1_7/diagnostics.json) |

Các root discovery/calibration/confirmation chưa cấp và không được mở trong L1.7.
Lưới chỉ kiểm invariants của L1.2/L1.4 được ghi verification, không suy đã đọc
outcome từng regime. Nguồn cũ/L0.5 không được coi là đã rerun bởi demo hiện tại.
