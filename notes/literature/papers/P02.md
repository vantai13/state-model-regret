# P02 — sensitivity analysis trong predictive signal control

Người phụ trách: **Doan Van Tai** · 26/10/2026. **AI-A (abstract-only)**;
targeted full text **BLOCKED**, tác giả chưa xác nhận L-self.

**M. C. Poelman; A. Hegyi; A. Verbraeck; J. W. C. van Lint (2023).**
*Structure-free model-based predictive signal control: A sensitivity analysis
on a corridor with spillback.* TR-C153:104174.
[DOI](https://doi.org/10.1016/j.trc.2023.104174) ·
[TU Delft official record/abstract](https://research.tudelft.nl/en/publications/structure-free-model-based-predictive-signal-control-a-sensitivit/).
Publisher identity/Crossref và TU Delft khớp; institutional record ghi final
published version20trang,CC BY. **Chưa tải được bản đó; không coi metadata là đọc.**

## Đã xác nhận ở abstract chính thức

Paper khảo sát prediction errors trong model-based signal control bằng một
microscopic simulator. Phân biệt aggregation errors với biases trong model,
demand và state input; xét hiệu ứng theo prediction horizon và update frequency.
Abstract báo frequent updates giảm tác động prediction errors và còn loss do
aggregation/bias. Đây là nguồn phương pháp do tác giả chỉ định, không phải paper
NDT hoặc packet network. Không có số liệu được repo tái lập từ paper.

## Chưa xác nhận từ full text

| Việc cần kiểm | Vị trí lesson chỉ dẫn, **chưa đọc được** |
|---|---|
| Simulator/controller, bốn intersections | §2.1 |
| Bias definition và mức−50%…+100% | §2.2.4 |
| Recorded per-vehicle future demand; tuned MPC có phải global optimum? | §3.1 |
| Các con số R²,20%/85%,25%/150%/30% lesson nêu | §3.1–3.3, chưa cấp evidence |
| Bias từng nguồn có crossed prediction/update horizons không? Có joint bias experiments không? | §3.3 và captions/figures |
| Reinitialization bù error và tác động của biased state | §4 |

**Không nhận kết luận “P02 chỉ OAT và không có tổ hợp” từ lesson.** Abstract đã
nói errors được xét theo horizon/frequency; cần đọc thiết kế thực tế. Không gán
dấu Γ cho P02 hoặc biến cơ chế định tính thành D19 factorial contrast.

## Truy cập và dừng

URL file TU Delft trong lesson timeout; một file TU Delft khác được tìm thấy
qua lookup cũng timeout. Pure PDF thất bại; research portal PDF/publisher403.
DOI-only Unpaywall trả “No PDF URL available for this record”; không đồng nghĩa
paper không OA (official record ghi CC BY). Các attempt cuối và trạng thái ở
[source_access](../../../results/lessons/l2_7/part_a/source_access.json).
Không dùng thư viện lậu hoặc gửi email. Dừng sau official routes/OA fallback;
§2–4 và hình/table còn là dependency mở của **L2.7 Part A**, không tự ghi T/PASS.

[Bài và các phần đã làm](../model_fidelity_methods.md) ·
[MT queue](../../phases/PHASE_4_methodology_threats.md).
