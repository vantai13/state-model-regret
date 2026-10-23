# Lưới v1.2 — ACCEPTED

Người phụ trách: **Doan Van Tai** · 23/10/2026. Sinh tự động từ [grid_v1_2.json](grid_v1_2.json) bằng `experiments/lessons/report_v1_2.py`. Protocol: [v1_2_protocol.md](v1_2_protocol.md) (commit `d696eef`, trước lần chạy). Quyết định: DL-038, DL-039.

**38 ô chính**, **12 ô held-out**, 6 ô kiểm âm, 2 đầu dò cấu trúc. Calibration A01: M01, M09, M22.

Mọi ô chính và held-out: $p_{\text{sw}}$ trong $[0{,}1;0{,}9]$ ở dt, dt/2, dt/4; nhãn ĐK1 `candidate`; budget trong trần $2\times10^{11}$ ở dt/16. Chỉ có xác suất dấu của oracle; **không** có $J$, margin, contrast hay regret.

## Ô chính

| Ô | Nhóm | κ | A | B | η | h (s) | Mục tiêu | λA | ψ | p_sw dt / dt/2 / dt/4 | Kẹp | Budget dt/16 (×10⁹) | Cal. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M01 | core | 0,3 | q90 | q50 | 0,500 | 8 | 0,3 | 7,25 | -0,075 | 0,360 / 0,359 / 0,358 | bracketed | 40,6 | C |
| M02 | core | 0,3 | q90 | q50 | 0,500 | 8 | 0,7 | 7,50 | -0,050 | 0,628 / 0,627 / 0,628 | bracketed | 23,6 |  |
| M03 | core | 0,3 | q90 | q50 | 0,750 | 8 | 0,3 | 7,00 | -0,100 | 0,392 / 0,392 / 0,391 | bracketed | 20,8 |  |
| M04 | core | 0,3 | q90 | q50 | 0,750 | 8 | 0,7 | 7,25 | -0,075 | 0,698 / 0,698 / 0,698 | bracketed | 48,1 |  |
| M05 | core | 0,3 | q90 | q90 | 0,500 | 8 | 0,3 | 7,25 | -0,075 | 0,240 / 0,239 / 0,238 | bracketed | 40,6 |  |
| M06 | core | 0,3 | q90 | q90 | 0,500 | 8 | 0,7 | 7,75 | -0,025 | 0,729 / 0,729 / 0,730 | bracketed | 38,7 |  |
| M07 | core | 0,3 | q90 | q90 | 0,750 | 8 | 0,3 | 7,00 | -0,100 | 0,262 / 0,262 / 0,262 | bracketed | 20,8 |  |
| M08 | core | 0,3 | q90 | q90 | 0,750 | 8 | 0,7 | 7,50 | -0,050 | 0,830 / 0,830 / 0,830 | bracketed | 31,1 |  |
| M09 | core | 1,0 | q90 | q50 | 0,500 | 8 | 0,3 | 6,25 | -0,175 | 0,306 / 0,305 / 0,305 | bracketed | 44,4 | C |
| M10 | core | 1,0 | q90 | q50 | 0,500 | 8 | 0,7 | 7,00 | -0,100 | 0,770 / 0,770 / 0,771 | bracketed | 16,0 |  |
| M11 | core | 1,0 | q90 | q50 | 0,750 | 8 | 0,3 | 6,00 | -0,200 | 0,333 / 0,333 / 0,333 | floor | 34,0 |  |
| M12 | core | 1,0 | q90 | q50 | 0,750 | 8 | 0,7 | 6,50 | -0,150 | 0,652 / 0,653 / 0,653 | bracketed | 33,0 |  |
| M13 | core | 1,0 | q90 | q90 | 0,500 | 8 | 0,3 | 7,00 | -0,100 | 0,312 / 0,311 / 0,311 | bracketed | 16,0 |  |
| M14 | core | 1,0 | q90 | q90 | 0,500 | 8 | 0,7 | 7,50 | -0,050 | 0,693 / 0,693 / 0,693 | bracketed | 23,6 |  |
| M15 | core | 1,0 | q90 | q90 | 0,750 | 8 | 0,3 | 6,50 | -0,150 | 0,240 / 0,241 / 0,240 | bracketed | 33,4 |  |
| M16 | core | 1,0 | q90 | q90 | 0,750 | 8 | 0,7 | 7,00 | -0,100 | 0,617 / 0,617 / 0,617 | bracketed | 21,1 |  |
| M17 | core | 3,0 | q90 | q50 | 0,500 | 8 | 0,7 | 6,00 | -0,200 | 0,745 / 0,745 / 0,745 | floor | 17,0 |  |
| M18 | core | 3,0 | q90 | q50 | 0,750 | 8 | 0,7 | 6,25 | -0,175 | 0,796 / 0,796 / 0,796 | floor | 27,4 |  |
| M19 | core | 3,0 | q90 | q90 | 0,500 | 8 | 0,3 | 7,00 | -0,100 | 0,285 / 0,285 / 0,284 | bracketed | 21,0 |  |
| M20 | core | 3,0 | q90 | q90 | 0,500 | 8 | 0,7 | 7,25 | -0,075 | 0,676 / 0,676 / 0,676 | bracketed | 56,3 |  |
| M21 | core | 3,0 | q90 | q90 | 0,750 | 8 | 0,3 | 6,50 | -0,150 | 0,254 / 0,254 / 0,254 | bracketed | 43,0 |  |
| M22 | core | 3,0 | q90 | q90 | 0,750 | 8 | 0,7 | 6,75 | -0,125 | 0,633 / 0,633 / 0,634 | bracketed | 68,4 | C |
| M23 | spoke_A50 | 1,0 | q50 | q50 | 0,500 | 8 | 0,3 | 7,00 | -0,100 | 0,251 / 0,251 / 0,251 | bracketed | 16,0 |  |
| M24 | spoke_A50 | 1,0 | q50 | q50 | 0,500 | 8 | 0,7 | 8,00 | 0,000 | 0,711 / 0,711 / 0,711 | bracketed | 15,1 |  |
| M25 | spoke_A50 | 1,0 | q50 | q50 | 0,750 | 8 | 0,3 | 6,75 | -0,125 | 0,293 / 0,292 / 0,292 | bracketed | 50,0 |  |
| M26 | spoke_A50 | 1,0 | q50 | q50 | 0,750 | 8 | 0,7 | 7,75 | -0,025 | 0,806 / 0,806 / 0,806 | bracketed | 25,5 |  |
| M27 | spoke_A50 | 1,0 | q50 | q90 | 0,500 | 8 | 0,3 | 8,00 | 0,000 | 0,259 / 0,259 / 0,259 | bracketed | 15,1 |  |
| M28 | spoke_A50 | 1,0 | q50 | q90 | 0,500 | 8 | 0,7 | 8,50 | 0,050 | 0,811 / 0,811 / 0,811 | bracketed | 24,4 |  |
| M29 | spoke_A50 | 1,0 | q50 | q90 | 0,750 | 8 | 0,3 | 7,75 | -0,025 | 0,350 / 0,350 / 0,350 | bracketed | 25,9 |  |
| M30 | spoke_A50 | 1,0 | q50 | q90 | 0,750 | 8 | 0,7 | 8,00 | 0,000 | 0,733 / 0,733 / 0,734 | bracketed | 32,3 |  |
| M31 | spoke_h2 | 0,3 | q90 | q50 | 0,500 | 2 | 0,3 | 6,25 | -0,175 | 0,257 / 0,255 / 0,256 | bracketed | 2,8 |  |
| M32 | spoke_h2 | 0,3 | q90 | q50 | 0,500 | 2 | 0,7 | 7,25 | -0,075 | 0,695 / 0,693 / 0,693 | bracketed | 2,7 |  |
| M33 | spoke_h2 | 0,3 | q90 | q50 | 0,750 | 2 | 0,3 | 6,00 | -0,200 | 0,285 / 0,284 / 0,284 | bracketed | 2,2 |  |
| M34 | spoke_h2 | 0,3 | q90 | q50 | 0,750 | 2 | 0,7 | 6,75 | -0,125 | 0,643 / 0,643 / 0,642 | bracketed | 3,2 |  |
| M35 | spoke_h2 | 0,3 | q90 | q90 | 0,500 | 2 | 0,3 | 6,75 | -0,125 | 0,305 / 0,305 / 0,305 | bracketed | 2,8 |  |
| M36 | spoke_h2 | 0,3 | q90 | q90 | 0,500 | 2 | 0,7 | 7,50 | -0,050 | 0,640 / 0,640 / 0,640 | bracketed | 1,8 |  |
| M37 | spoke_h2 | 0,3 | q90 | q90 | 0,750 | 2 | 0,3 | 6,50 | -0,150 | 0,333 / 0,333 / 0,333 | bracketed | 2,4 |  |
| M38 | spoke_h2 | 0,3 | q90 | q90 | 0,750 | 2 | 0,7 | 7,25 | -0,075 | 0,756 / 0,757 / 0,757 | bracketed | 4,0 |  |

Mục tiêu không neo được (giữ làm ghi nhận, không thay ô khác):

- V09, mục tiêu 0,3: điểm gần nhất λA 6,00 có p 0,745 (floor).
- V10, mục tiêu 0,3: điểm gần nhất λA 6,25 có p 0,796 (floor).

## Held-out

Tọa độ khai báo trong protocol trước khi tính. Không dùng cho discovery hay calibration; $p_{\text{sw}}$ và λA riêng của held-out không được làm biến đầu vào cho $H_0/H_1$.

| Ô | Nhóm | κ | A | B | η | h (s) | Mục tiêu | λA | ψ | p_sw dt / dt/2 / dt/4 | Kẹp | Budget dt/16 (×10⁹) | Cal. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R01 | heldout_kappa | 0,6 | q90 | q50 | 0,500 | 8 | 0,3 | 6,75 | -0,125 | 0,370 / 0,370 / 0,370 | bracketed | 42,5 |  |
| R02 | heldout_kappa | 0,6 | q90 | q50 | 0,500 | 8 | 0,7 | 7,25 | -0,075 | 0,713 / 0,714 / 0,715 | bracketed | 40,6 |  |
| R03 | heldout_kappa | 2,0 | q90 | q90 | 0,500 | 8 | 0,3 | 7,00 | -0,100 | 0,308 / 0,308 / 0,308 | bracketed | 17,6 |  |
| R04 | heldout_kappa | 2,0 | q90 | q90 | 0,500 | 8 | 0,7 | 7,50 | -0,050 | 0,773 / 0,773 / 0,773 | bracketed | 29,7 |  |
| R05 | heldout_quantile | 1,0 | q90 | q75 | 0,500 | 8 | 0,3 | 6,50 | -0,150 | 0,300 / 0,299 / 0,299 | bracketed | 25,5 |  |
| R06 | heldout_quantile | 1,0 | q90 | q75 | 0,500 | 8 | 0,7 | 7,25 | -0,075 | 0,744 / 0,744 / 0,744 | bracketed | 40,6 |  |
| R07 | heldout_eta | 1,0 | q90 | q50 | 0,625 | 8 | 0,3 | 6,00 | -0,200 | 0,269 / 0,269 / 0,268 | bracketed | 67,9 |  |
| R08 | heldout_eta | 1,0 | q90 | q50 | 0,625 | 8 | 0,7 | 6,75 | -0,125 | 0,693 / 0,693 / 0,693 | bracketed | 65,1 |  |
| R09 | heldout_horizon | 0,6 | q90 | q90 | 0,500 | 4 | 0,3 | 6,75 | -0,125 | 0,282 / 0,281 / 0,282 | bracketed | 10,8 |  |
| R10 | heldout_horizon | 0,6 | q90 | q90 | 0,500 | 4 | 0,7 | 7,50 | -0,050 | 0,672 / 0,673 / 0,673 | bracketed | 6,4 |  |
| R11 | heldout_horizon_extrapolation | 0,3 | q90 | q90 | 0,500 | 12 | 0,3 | 7,50 | -0,050 | 0,333 / 0,333 / 0,333 | bracketed | 53,1 |  |
| R12 | heldout_horizon_extrapolation | 0,3 | q90 | q90 | 0,500 | 12 | 0,7 | 7,75 | -0,025 | 0,670 / 0,671 / 0,671 | bracketed | 87,1 |  |

## Ô kiểm âm và đầu dò

| Ô | Vai trò | Nhãn dt / dt/2 | p_sw dt |
|---|---|---|---|
| N01 | negative | SD-cell / SD-cell | 0,000 |
| N02 | negative | SD-cell / SD-cell | 0,000 |
| N03 | negative | conservation-cell / conservation-cell | 0,000 |
| N04 | negative | conservation-cell / conservation-cell | 0,000 |
| W01 | wd_probe | WD-cell / WD-cell | 0,770 |
| S01 | stress | WD-cell / WD-cell | 1,000 |
| P01 | đầu dò cấu trúc | conservation-cell / conservation-cell | 0,000 |
| P02 | đầu dò cấu trúc | WD-cell / WD-cell | 0,524 |

Ở SD-cell và conservation-cell, sáu contrast phải bằng 0 chính xác khi Phase 3 tính; sai lệch là bug.

## Đọc bảng

- **Kẹp** (`bracketed`): mục tiêu nằm giữa hai điểm thang. `floor`: mọi điểm thang đều cao hơn mục tiêu, nên điểm cắt sẽ cần λA dưới đáy vật lý 6.
- So sánh giữa các lát là ở **cùng độ khó**, không cùng tải; λA thay đổi theo lát. Báo $p_{\text{sw}}$ thực, không coi như đúng 0,3 hay 0,7.
- ψ = (λA − 8)/10 là đại lượng dẫn xuất. Kết quả chỉ áp dụng cho khoảng ψ trong bảng.
