# Hiệu chỉnh "knockout CE" (dữ liệu đã lộ), 14/11/2026

Doan Van Tai — **AI (Claude) theo ủy quyền**. Hồ sơ này ghi những gì đã thấy trước khi viết thẻ.

Dữ liệu: các panel I_Δ vòng 2 (`cases_fresh.json`, 45 regime) và vòng 3 (`cases_r3.json`, 40 regime). G_S/Γ của
chúng đã thấy trước đó; P_*, K, Ĵ và các nhánh plug-in được **thấy lần đầu ở đây**. Từ giờ 85 regime này đã lộ với
mọi đại lượng của module, nên không dùng để chấm.

Cả hai lượt chạy local (host vantai, `env.sh`), với design sha256 `98f28075…` (khớp [DESIGN_CE.md](DESIGN_CE.md)).
Mỗi lượt 85/85 COMPLETED, khoảng 95 s wall và 8,5 CPU-phút.

## Lượt 1 (`calib_pass1/`, module `bcd3d62c…`)

- **Control:**
  - L khớp engine: max 2,1e−14 pp.
  - tower: 2,4e−15.
  - P_M1: nhỏ nhất 0,0 (Bayes đúng).
  - Nội suy và fluid đúng lệch nhau tối đa 0,204 pp; 39/340 dòng lệch > 0,01 pp. Vì vậy thẻ có control C4.
- **K = Ĵ − J** (Jensen của sai số M0):
  - Ở 7 T_int, E|K|/E|Ĵ| có trung vị 0,03–0,06. Tức là Jensen của M0 và của truth gần bằng nhau, đúng như F1 trong design.
  - Ở 1 T_int, tỷ số này khoảng 0,75. Ngoài band, K cùng dấu s ở 86–90% khối lượng p(y).
- **κ_CE = P_M0/P_sur không dùng được làm phép thử:**
  - Ở 7 T_int, ngoài band, trung vị là 0,11 (neg) và 0,39 (pos).
  - Khi đó P_M1 có trung vị 0,0 nhưng P_sur > P_M0. Kết quả này mâu thuẫn với H_pool như design §4 đã viết.
  - Nhưng K lại nhỏ. Nên tỷ số này phản ánh vị trí của gap so với ngưỡng (surrogate và M0 đặt các gap cũ ở chỗ khác nhau quanh ngưỡng), không phản ánh K.
  - Hạ κ_CE xuống thành đại lượng mô tả.
- **Quyết định sau lượt 1:**
  - Thêm nhánh **NK**: g_NK = E[Δ̂|y] − K(y) = Δ̂_PB(y) + J(y). Nhánh này bỏ đúng phần "hiệu chỉnh ngầm" và giữ Jensen hợp lệ của truth.
  - Thêm sai số cũ có và không có K: E|E[e|y]|, E|e_PB(y)|.
  - Hàm `regime` chỉ được *thêm* trường; các trường cũ giữ nguyên công thức.

## Lượt 2 (`calib/`, module `4ccf604f…`, cùng 85 regime)

"Dòng harm" là G_S < −0,05 pp. "Giữ" là G_S^nhánh / G_S, ghi dạng trung vị [q10; q90].

| | ngoài band, 1 T_int | ngoài band, 7 T_int | band, 7 T_int |
|---|---|---|---|
| Dòng / dòng harm | 50 / 27 | 50 / 39 | 35 / 4 |
| NK giữ; vẫn harm | 0,89 [0,59; 0,97]; 27/27 | **1,00** [1,00; 1,08]; 39/39 | 1,00; 4/4 |
| PB giữ; vẫn harm | 0,82; 27/27 | 0,89 [0,65; 0,98]; 39/39 | 0,24; 3/4 |
| QM giữ; vẫn harm | 0,75; 26/27 | 0,80 [0,23; 0,97]; 39/39 | −0,15; 2/4 |
| E\|K\|/E\|Ĵ\| | 0,76 | 0,034 | 0,057 |
| E\|E[e\|y]\| / E\|e_PB\| | 0,96 (96% < 1) | 1,00 | 1,00 |
| P_M1 trung vị (pp) | 6e−5 | 2e−8 | 2e−4 |

Cách đọc (chỉ để hiệu chỉnh, không phải kết quả):
- Ở h dài, bỏ K không đổi harm.
- Ở h ≈ T_int, K có thật nhưng nhỏ: sai số cũ giảm khoảng 4%, và khoảng 11% harm (trung vị) mất khi bỏ K.
- Twin plug-in vẫn bị hại ở mọi dòng harm ngoài band. Mức harm co 11–20% (trung vị).
- Plug-in trên model đúng gần như không mất gì (P_M1 ≈ 0): truth cũ ở h dài nằm xa ngưỡng.

Ngưỡng của thẻ nháp được chọn từ bảng này (`calibration_ce.json`). Áp chính các ngưỡng đó lên dữ liệu hiệu chỉnh thì
N1/N2/N3/P1 đều PASS. Điều này hiển nhiên vì cùng dữ liệu, không phải bằng chứng.
