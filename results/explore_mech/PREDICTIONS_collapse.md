# Dự đoán trước khi chạy pslice

Doan Van Tai — AI (Claude) soạn theo ủy quyền, **exploration**, không phải author-self, không phải claim.
Ghi 01/11/2026 trước khi có dòng pslice nào. Đã xem: sobol4 5.814 dòng, hslice 16 dòng (h/κ ≈ 58),
xslice ≤ 5 dòng (chưa phân tích).

## Điều đã thấy (sobol4, không phải bằng chứng kiểm)

- λA = λB (715 regime): M ≤ 0,23%, R = 1,00 ở mọi dải h/κ ≥ 3 (khi S+M ≥ 0,5%).
- Với δ ≠ 0, điểm R = 0,5 dịch về h/κ nhỏ hơn khi |δ| lớn hơn; gom theo P = (h/κ)·|δ| (δ tính bằng
  packet/s, τ = 1) thì điểm cắt nằm quanh P ≈ 10–20 ở mọi dải |δ|; độ lệch trung bình quanh trung vị
  theo bin là 0,102 với P so với 0,133 với h/κ.

## Cơ chế đề xuất

M (giá trị sửa model khi biết state) đến từ phần chi phí dài hạn mà mean model bỏ qua; phần này tăng theo
h và theo độ bất đối xứng tải |δ| (tính lồi của E_stat[Q]), và triệt tiêu khi δ = 0 (đối xứng hoán đổi:
quyết định chỉ còn so thứ tự state). S bão hòa theo h. Do đó R chuyển từ state sang model khi
(h/κ)·|δ| vượt một mức cỡ 10.

## Dự đoán (ngưỡng ghi trước)

- **C1**: mỗi chuỗi (δ ≠ 0, u, κ) có R cắt 0,5 trong dải đã lấy mẫu thì điểm cắt P* (nội suy log) ∈ [5, 30].
- **C2**: ở cùng (u, κ), tỷ số max/min của P* giữa các |δ| ∈ {1/2, 1, 2} (gộp hai dấu) ≤ 2,5; còn tỷ số
  max/min của (h/κ)* tương ứng ≥ 2,5. Nếu ngược lại thì h/κ gom tốt hơn P và dự đoán sai.
- **C3**: δ = 0: M ≤ 0,3% ở mọi điểm; R ≥ 0,9 ở mọi điểm có S+M ≥ 0,5%.
- **C4** (khám phá, không ngưỡng): báo hướng ảnh hưởng của κ, u và dấu δ lên P*.

Kết quả sai được báo nguyên văn; không đổi ngưỡng hoặc biến gom sau khi xem.
