# Dự đoán bridge fluid → CTMC (khóa trước Stage D)

Doan Van Tai — **AI (Claude) soạn theo ủy quyền L7.1**, exploration, không phải author-self, không phải claim.
Ghi ngày 03/11/2026, trước khi tính bất kỳ L, G hay quyết định truth nào của CTMC trên các tập chấm.
Tác giả không ghi dự đoán riêng ở mục 9 của lesson; mọi dự đoán dưới đây là của AI. Bộ chấm:
[check_bridge.py](../../experiments/explore_ctmc/check_bridge.py), chạy nguyên văn, không sửa ngưỡng sau khi thấy kết quả.

## Đã dùng gì để viết

- Dữ liệu fluid: `results/explore_mech/` (SUMMARY H1–H6, sobol4 metrics, các lát và PREDICTIONS cũ).
- CTMC, chỉ M0 và đại lượng dừng (`--mode m0`, 1.407 case): π, r, s, T_int, g, tỷ lệ Switch của M0 trên state
  cũ/mới ở h và ở h = ∞, z_∞. Không gọi `V`, không có gap thật.
- **Exposure phải khai:** trước khi viết file này, lệnh đo thời gian đã in truth của 3 regime (T1–T3 trong
  `controls/v3_ids.json`). Đã thấy: T1 (7, 15/2, 3/2, 1/2, h=4) G_S=+0,459%, S=0,569%, M=0,113%;
  T2 (27/4, 13/2, 3, 20, h=32) G_S=−0,048%, S=0,013%, M=0,063%; T3 (7, 13/2, 5/2, 2) ở h=2000:
  z=−4,418%, z bậc một=−4,405%, z_∞=−5,351%, S≈0, M=8,44%. Ba regime này và ba regime V3 bị loại khỏi mọi tập
  chấm (guard trong scan.py).

## Thay đổi evaluator trước khi khóa

Hai sửa đổi xảy ra sau lượt M0-only đầu tiên và trước khi viết xong file này (cả hai không đụng truth): (1) luật
hòa chính xác của M0 ở state bão hòa (SPEC.md), làm tỷ lệ Switch của M0 ở h ngắn đổi tới 0,48 và z_∞ không đổi;
(2) môi trường số chung và `det_expm1` cho V7. Lượt M0-only được tính lại; bản cũ giữ ở `m0_attempt01/`,
`m0_attempt02/`. Các quan sát dưới đây kiểm lại trên bản mới.

## Những điều đã thấy ở M0/đại lượng dừng (không phải truth) và ảnh hưởng tới dự đoán

1. Tập bridge (1.200 tuple sobol4) trong CTMC gần như toàn là horizon ngắn: h/T_int trung vị 0,01, lớn nhất 3,3.
   Đồng hồ h/κ của fluid không còn là đồng hồ của queue.
2. Tỷ lệ Switch của M0 trên state cũ giảm **dần** theo x (ví dụ u=1, κ=1, h/κ=150: 0,89 ở x=−1 → 0,27 ở x=1), không
   lật gọn như fluid. z_∞ đổi dấu ở x ≈ 0,2–0,3, không phải 0,4–0,5.
3. Trên các tuple bridge, fluid ở κ ≤ 0,05 có S+M ≥ 0,5% ở 81% regime; câu "κ nhỏ là vùng neither" của lesson không
   khớp số fluid tính theo %C_ref. Dự đoán BR-R7 vì thế được viết theo chiều khác.

## Tập chấm

- `bridge`: 1.200 tuple sobol4 (seed 20261103, `design.py`), ghép với dòng fluid cùng ID; chỉ dùng dòng fluid có
  `arith=True` khi so cặp. Phân tầng báo cáo theo κ: (0; 0,05], (0,05; 0,2], (0,2; 1], (1; 5], (5; 20].
- `xslice`: 96 case (u=1, λA=7, x ∈ [−1; 1,9]; u=2, λA=13/2, x ∈ [−1/4; 7/10]; κ ∈ {1/5, 1}; h/κ ∈ {50, 150}).
- `pslice`: 78 case (u=1, λA=7, x ∈ {−1/2, 1/4, 1}, κ ∈ {1/5, 1}, h/κ từ 1 tới 160).
- P = (h/κ)·|δ|. Mọi đại lượng tính bằng % C_ref, C_ref = L11 của CTMC.

## Dự đoán

Nhãn **toán**: suy trực tiếp từ định nghĩa, đối xứng hoặc luật z_∞; đạt nghĩa là code đúng, không tính là bằng
chứng. Nhãn **rủi ro**: chuyển giao từ fluid hoặc dự đoán mới có thể sai; chỉ nhãn này tính là bằng chứng.

| ID | Nhãn | Điều kiện | Dự đoán (ngưỡng) | Lý do |
|---|---|---|---|---|
| BR-G1 | toán | mọi dòng | G_SM = G_S+M = G_M+S, Γ = S−G_S sai ≤ 1e−9 pp; S, M, G_M ≥ −1e−9 | định nghĩa |
| BR-G2 | toán | mọi dòng | δ=0 ⇒ s = 0 và Static = Stay; δ≠0 ⇒ (s<0) ⇔ (λB<λA) | đối xứng, tính lồi |
| BR-R1 | rủi ro | bridge, \|G_S fluid\| ≥ 0,5% | sign(G_S CTMC) = sign(G_S fluid) ở ≥ 75% | cùng cơ chế M0 cận thị |
| BR-R2 | rủi ro | bridge, S+M ≥ 0,5% ở cả hai | nhãn S>M trùng nhau ở ≥ 80% | cùng cấu trúc state/model |
| BR-R3 | rủi ro | bridge CTMC, S+M ≥ 0,5% | ngưỡng đơn tốt nhất trên P đúng ≥ 85%, hơn h/κ ≥ 3 điểm %, ngưỡng P* ∈ [5, 30] | H3 fluid (93,0% / 86,1%) |
| BR-R4a | rủi ro | bridge+xslice+pslice, P ≥ 30, S+M ≥ 0,5%, x < 0 | G_S < −0,1% ở ≥ 90% | H1 fluid (693/693) |
| BR-R4b | rủi ro | như trên, x > 0,5 | G_S < −0,1% ở ≥ 90% | H1 fluid (521/522) |
| BR-R4c | rủi ro | như trên, 0 < x ≤ 0,5 | Γ < 0 ở ≥ 40% | fluid 44% (bridge), 61% (sobol4) |
| BR-R5 | rủi ro | xslice, h/κ = 150, từng chuỗi (u, κ) | x lớn nhất có G_S > 0,1% là ≤ 0,35 ở cả 4 chuỗi | dải giúp hẹp hơn fluid (mục 2 ở trên) |
| BR-R6 | rủi ro | bridge, δ = 0 | M ≤ 0,3% ở ≥ 95% | H2 fluid (100% ≤ 0,253%) |
| BR-R7 | rủi ro | bridge, κ ≤ 0,05, fluid arith-ok | trung vị (S+M) CTMC < trung vị (S+M) fluid | backlog Poisson làm C_ref lớn hơn stake quyết định |
| BR-R8 | rủi ro | xslice+pslice, h/T_int ≥ 3, \|δ\| ≥ 1/2 | tỷ lệ Switch của truth trên state mới ≥ 0,9 khi δ<0, ≤ 0,1 khi δ>0, ở ≥ 90% dòng | P1 fluid, đổi đồng hồ sang h/T_int |
| BR-T1 | toán + onset rủi ro | xslice+pslice, h/T_int ≥ 3, \|z_∞\| ≥ 0,25 | sign(G_S) = sign(z_∞) ở ≥ 90% | luật z_∞; ngưỡng onset 3 là phần rủi ro |

**Ghi kèm (mô tả, không chấm):** độ chính xác ngưỡng đơn theo h/T_int và h·|s|/r_min cho nhãn S>M; bảng lớp theo
tầng κ; tỷ lệ cùng dấu G_S theo tầng κ.

## Ý nghĩa từng kết cục

- BR-G* trượt → bug, dừng và sửa trước khi đọc gì khác.
- BR-R1/R2 đạt → cấu trúc state/model ở horizon ngắn chuyển được sang plant packet; trượt → phụ thuộc representation.
- BR-R3 trượt nhưng R4 đạt → cơ chế ở P lớn đúng, biến gom sai (tìm biến khác ở Stage E).
- BR-R5 đạt → M0 CTMC dự đoán được dải giúp hẹp hơn trước khi thấy truth; trượt → x* của fluid chuyển nguyên.
- BR-R7 trượt → stake quyết định ở κ nhỏ lớn hơn mình nghĩ; ghi lại, không đổi chiều.
- BR-R8/BR-T1 trượt dù h/T_int ≥ 3 → onset muộn hơn, hoặc bug ở phần dài hạn.
