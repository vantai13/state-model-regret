# L4.2 — ghi chú kiểm chứng kỹ thuật và cách đọc hình

Người phụ trách: **Doan Van Tai** · 30/10/2026. **AI theo ủy quyền**.
Đây là technical reference cho các phép chạy; không phải T07 author addendum,
không thay bài tự dẫn của tác giả hoặc xác nhận Understanding.

Nguồn: ba input L4.2 được [lưu nguyên byte](../../../results/lessons/l4_2/input_manifest.json),
T07 và contract frozen, record/output L4.1; hai hình/plot source tại tag574a36f.
`PHASE_4.md` đầy đủ vẫn chưa được cung cấp. Các câu “L4.1 thực thi chưa” trong
input là snapshot cũ: L4.1 đã hoàn tất kỹ thuật ở4a969c5, bài tác giả vẫn OPEN.

## Những phép kiểm đã thực hiện

1. Ba toy supplied dùng Fraction, kiểm đủ bốn loss, sáu contrast, S07/S08/S10/S11/S12
   và lower bound; đối chiếu với helper T07 hiện có. Dhat là số được chọn, không
   phải output M0 queue. T-B là ví dụ bổ sung AI, không bài tác giả tự đặt.
2. Với recurrence endpoint nhỏ, nhân thời gian3 và q0 tương ứng cho backlog×3,
   cost1→9; nhân mọi net rates và q0×5 cho cost1→5. Đối chứng fixed-dt/fixed-buffer
   không giữ scaling. Đây là kiểm fixture, không audit production engine hoặc
   chứng minh tổng quát về stationary law.
3. Từ CSV L4.1 đã kiểm SHA:18cặp scaled-age cùng lớp, lệch6contrasts tối đa
   0.2009889943pp, cặpXA001/XM2S183 ởGS. Pilot giữdt1/120s nên không áp exact
   similarity cho các bản tính này. Kiểm này không đóng E11/E12 hay native readiness.
4. Đếm near-boundary, MV+A, các phần bị oracle inequality ép và các phần mô tả
   không bị ép. Lập bảng λA×λB và δ trên lát238điểm **đã thấy**.
5. Chạy hai mutation implementation thật trong memory và kiểm các golden assertions
   fail; không sửa source/engine frozen. Phân biệt chúng với hai perturbation
   minh họa trong input (đổi Dhat và đổi tie option).

## Năm chiều: phạm vi áp dụng

Kết quả dimensionless nêu trong input chỉ ở plant fluid, infinite/scaled buffer,
linear queue occupancy cost, coherent/scaled q0/stationary law/posterior, và c_sw=0
hoặc surcharge co đúng. Phép co thời gian phải co **dt,κ,h,τ,q0**; cost co theo
bình phương thời gian, không cùng hệ số với backlog. Co rates cũng phải co q0.
Giữamp/μ=.6 và c_sw=0 để còn năm tọa độ vật lý; không xemdt là chiều vật lý thêm.

Toy ramp ∫qdt cho4→16packet·s là **analytic continuous integral**, trong khi với
4slot ởdt=.5→1, endpoint sum là5→20. Hai cặp cùng tỉ số4 nhưng không được gọi
4/16 là output exact của engine endpoint. Không suy similarity sang packet DES,
fixed finite buffer, ngưỡngSLA cố định hoặc biên độ khác namespace.

## Đọc hai hình tại tag

[Differ](../../../results/lessons/l4_2/reading/regime_map_differ.png) và
[mechanism](../../../results/lessons/l4_2/reading/regime_map_mechanism.png)
là bản sao PNG nguyên byte, không vẽ lại hoặc sửa nhãn gốc. Tên “mechanism” và
“cộng hưởng” trong ảnh là nhãn lịch sử, không được xác nhận như claim mới.

| Hình | Trục | Cách đọc / phần bị ép |
|---|---|---|
| differ | x=GS,y=GM (%Cref);symlog,linthresh1 | GM≥0 bị oracle/Bayes ép; màu từ rule, mật độ do lấy mẫu; hollow là trong hộp card sau quyage1 |
| mechanism | x=GS\|M1,y=GM\|S1;symlog,linthresh.1,linscale.5 | Hai trục không âm; đường chấm hai giá trị bằng nhau; không gian outcome không phải hộp tham số |

Trong C, GM|S1≥abs(GS)+GM và minGM|S1=1.0920419565%: phần nằm cao bị ép.
Trong A, GS|M1≥GS−GM; min(GS−GM)=0.5643047019% trên bảng hiện có. Rule A nói
GM<1, **không bắt GM gần0**; cận này không đảm bảo A luôn nằm xa0 một mức cố định.

Các số không bị dấu ép: C có255/334điểmGS|M1<.1%; A có286/301điểmGM|S1<.5%;
AB cómedianGS|M1=.709285075%,67/161<.5% và67/161≥1%. Vì vậy không mô tả toàn
AB như state chỉ bù lỗi model, không mô tả toàn C/A bằng tính chất “gần0” của đa số.
Không có phép đo “một nửa vẻ đẹp” nào: đó là cách nói trong lesson, không metric50%.

## Đính chính logic và giới hạn cần giữ

| Input nói | Cách ghi chính xác |
|---|---|
| “Cùng một lỗi M0” ởAB/C′ | Cùng pattern **action error của S1M0**; vector prediction errors khác ởx2. Chỉ thay một dự đoán làm trung bình qua0; không suy cùng queue mechanism |
| GS\|M1=min(P,N) | Đúng theo từngy (hoặc một snapshot toy); population là **E_Y[min(P(y),N(y))]**, không min(E[P],E[N]). Có test phản ví dụ |
| “Đối chứng lật một nhân tố vô dụng” choΓ | Chỉ trivial khi định nghĩa/điều kiện vùng bảo đảmmin(GS,GM)<ε hoặcGS<0. **Lậtκ tự nó không cho bảo đảm đó**; pilot nhỏ là quan sát, không identity |
| “Cùngδthì cùnglớp” | Sai nếu đọc tất định:δ=.5 có40AB,1A,1B;δ=.75 có9AB,20C,7B. Chỉ có xu hướng tổ chức trên lát discovery |
| AB8/18 “đa số” ở(6.25,7) | Là **plurality** (AB8,C7,B3), không strict majority>50%; CSV ghi rõ cả hai |
| “CardMVđúng” tạiMV+A | Chỉ **18/18điểm discovery** đạtGM≥1%, min1.329633319%. Không phải confirmation của cả hộp/measure |
| δ là tọa độ không thứ nguyên | δ=λB−λA có đơn vịpacket/s; ghi thêmδ/μ để bất biến theo co rates. μ10giữcốđịnh ở map |
| Hai test input gọi “mutant” chứng minh bắt bug | Đó là input/behavior perturbations; run này có thêm hai implementation mutants thật và lưu caught assertions |

δ≤−.25 có27điểm,24C/3D; phía trái chưa có giải thích plant. δ không được chứng minh
tốt hơn headroom ratio; cùngheadroom4/5 còn nhiềuλ/δ khác. Không chọn tọa độ/card
mới từ bảng này. Bảngδ đã thấy từL4.1; không tạo lời “dự đoán trước” sau dữ liệu.
Bài optional short-horizon A-by-δ chưa chạy vì không có dự đoán tác giả trước nó.

## Trạng thái

Technical checks đã chạy, số đo ở [report](../../../results/lessons/l4_2/report.md).
[T07P4 author template](../../theory/T07_P4_author_addendum.md) vẫn trống. G1,
P0-V10/L8/Understanding/ownership giữOPEN; khôngbaseline/card/CF-v3/Gate4 mới.
Có thể họcL4.3; native audit cần đặc tả/tolerance commit trước run theo lesson đó.
