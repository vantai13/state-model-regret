# Thuật ngữ Part A

Người phụ trách: **Doan Van Tai** · 24/10/2026 · AI hỗ trợ.

| Term | Nghĩa dùng trong lesson | Nguồn/giới hạn |
|---|---|---|
| J(a;x) | Expected cost theo future law khi đã biết x; không phải realized-future hindsight | D14–D15 |
| EVPPI(x\|y) | min_a E[J\|y] − E[min_a J\|y] | SOB14 Method Eq4; T03 ánh xạ sang hidden state |
| RP | min expected cost khi chọn action trước realization | T03 định nghĩa trong finite decision problem |
| WS | E[min realized cost] khi được biết cả realization trước chọn | Có thông tin mạnh hơn oracle D15; không gọi L11 là WS |
| EV / EEV | Giá trị objective của mean-input problem / true expected cost của action do mean-input problem chọn | EV khác EEV; T03 |
| Conditional VSS(x) | EEV(x)−RP(x), thay future bằng conditional mean khi biết x | Identity của dự án; B82 chỉ abstract, không mượn theorem LP |
| EVPI(delta) / EVMI | Giá trị học discrepancy theo belief / diễn giải upper bound cho model improvement | P11 §2.4 Eq2.7; không đồng nhất với D21 |
| EVIU | Tên liên quan trong lesson seed | Original source chưa kiểm, không dùng như primary evidence |
| OεRE | Mục sẽ xử lý ở L2.4 | Chưa định nghĩa/adopt trong contract ở Part A |

Matched belief là điều kiện đủ cho các bảo đảm đã nêu, không phải điều kiện cần
cho equality ở từng instance. Dấu Γ không tự xác nhận network mechanism.
