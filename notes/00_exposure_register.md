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

## Giới hạn

Sandbox khác, Colab và máy ngoài phiên này chưa kiểm được. Không có outcome của smoke đã xóa để đo mức exposure mạnh hơn lời nguồn. Không chạy thêm simulation hoặc mở seed để dành trong L0.1 này.
