# L4.5 — Luật sàng để tác giả duyệt, trước bất kỳ p-hat hộp nào

Người phụ trách: **Doan Van Tai** · 30/10/2026.
Provenance: **AI soạn; DRAFT_PENDING_AUTHOR_CHOICE**.
Đây chưa phải quyết định thêm0/1/2card của DL-103.

“Khi viết luật này tôi đã thấy các p̂ pilot minh họa trong PHASE_4: **72,8% cho
một hộp vùng A, 94,9% cho dải δ**.” Đây là số được input báo, không phải kết quả
tái tính trong phiên này. Đã thấy L4.3/L4.4 HOLD và hai điểm MV baseline trước đó.
Chưa đếm bất kỳ hộp pilot/native nào, chưa chọn bounds hoặc thử hộp thật.

## Gói đề xuất

1. Giữ SV và SUB qua Part A dưới dạng **ứng viên có điều kiện**, theo giới hạn
   prior đã xác nhận DL-043; không gán novelty. Chi tiết ở PartA_candidate_filters.md.
2. n=60,π0=1/2,α=1/40/card; hai card F2 tối đa, không thay F1. FWER F2≤1/20,
   cả hai family≤1/10 theo union bound; không tự coi paper-wide bound là.05.
3. SV hai vùng, tiêu chí GS/Cref≥.01; p_minus_plan=.2 là **giả định thiết kế**,
   không số đo. SUB một vùng, tiêu chí Γ/Cref≤−.01. Thiết kế một vùng là lựa chọn
   theo lesson, không theorem “mọi đối chứng lậtκ đều bịép”.
4. Dùng `robust_region_power`/`robust_pass_power` gốc, với
   p_cond=MEETS/(MEETS+FAILS), p_plan=max(0,p_cond−.10), r=UNRESOLVED/N.
   Mỗi vùng SV có r riêng; không chép r_plus sang r_minus.
5. Power≥.5 và mỗi r≤.05 mới PASS_SCREEN. Không resolved rows thì
   NO_RESOLVED, hộp rỗng EMPTY. UNDEFINED báo riêng và chặn planning v1 vì mô hình
   power giả định UNDEFINED=0; không loại hoặc điền nhãn âm thầm.
6. Mỗi physical key age1 một phiếu; v1 giữ haircut cố định, không split sample
   hoặc thêm measure weights. Grid thích nghi khác measure card: đây là planning
   convention, không confidence bound hoặc frequency estimate.
7. Tối đa3hộp/ứng viên. Bounds/đối chứng SV phải commit trước khi lọc/đếm từng
   hộp, mỗi hộp ghi một dòng immutable ledger, gồm hộp rỗng hoặc FAIL_SCREEN.
   Không tính thử rồi chỉ ghi hộp đẹp. Chưa có hộp nào được khai/chạy lúc viết.
8. Chỉ native discovery có readiness hợp lệ và baseline đúng hỗ trợ candidate
   mới được vào screen. L4.3/L4.4 đangHOLD nên PartB bịchặn trước membership
   hoặc p-hat. Không dùng nhãn pilot hoặc hai MV bundles như kết quả SV/SUB.
9. Baseline giữ điều kiện đối thủ L4.4: GSθ nhỏ với ΔL10>0 không là lý do bỏ SV.
   SUB recovery lớn chỉ thu hẹp câu baseline theo luật đã duyệt, không tự sửa
   card verdict. Candidate-region rho policy/coverage còn cần prereg riêng;
   L4.4 MV/SH rho (chưa có) cũng không tự cấp baseline cho A/AB.
10. CF-v2/R09/R10 chỉ đọc parameter keys để từ chối. Không tính outcome CF,
    không chọn card/budget/Gate4 hoặc gỡ HOLD bằng sàng giả định.

## Những gì có thể chạy ngay

Exact hypothetical power/R5 tables và finite algebra counterexamples, tests
với nhãn synthetic được phép; chúng không lọc hộp nghiên cứu hoặc tạo exposure
plant. Không RNG/seed cho các bảng exact, không engine imports/calls.

## Quyết định còn mở

Tác giả duyệt hoặc sửa gói PartA/rules trước khi khóa. Kết quả PartB và DL số
card cuối cùng còn **PENDING_DEPENDENCIES**, không suy “0card” từ thiếu dữ liệu.
Nếu sau này chọn0card, đây là lựa chọn tác giả với phạm vi claim rõ ràng; nó
không tự giải quyết L4.4 baseline sanity của F1 hoặc P0-V10.
