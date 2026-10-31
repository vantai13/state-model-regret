# Exploration P4 — vùng nào đáng đầu tư? (nhánh `explore/p4-regions`, 31/10/2026)

Người phụ trách: **Doan Van Tai**. AI (Claude) tự thiết kế và chạy theo ủy quyền ("chạy mọi thứ theo quyền bạn").

**EXPLORATION / DISCOVERY**, không phải prereg, card hay evidence.
- Engine native (code frozen) kèm baseline margin L4.4.
- Biên độ ±6 duy nhất (các biên độ khác giữ cho held-out). τ = 1 s, c_sw = 0.
- Mức số (160, 2); kiểm lại ở (320, 4).
- Không đụng R09/R10 hay 270 CF-v2 (bộ lọc trong code).

## Câu hỏi

So với một controller thực tế J1 = **state cũ + M0 + margin tốt nhất** (ρ ∈ {0; 0,5; 1; 2; 5}%), đầu tư vào đâu thì lời,
tính theo % C̄_ref (C̄_ref = L11)?
- **state:** J1 − min_ρ L10(ρ), tức state tươi với M0 tự chọn margin riêng;
- **model:** J1 − L01;
- **cả hai:** J1 − L11 (tới mức oracle).

## Đã chạy

| Đợt | Regime | Lưới |
|---|---|---|
| wide | 540 (498 xong) | λA {6,7,8} × λB {6,7,8,9} × u {0,5; 1; 1,5} × κ/τ {0,03…10} × h/τ {2, 8, 32} |
| short | 648 (635 xong) | λA {6; 6,5; 7} × λB {6,7,8} × u {1; 1,5; 1,75} × κ/τ {0,03…1} × h/τ {0,25…2} |
| top | 12 | regime nổi bật, chạy lại ở (320, 4): lệch ≤ 0,2 pp, kết luận giữ nguyên |

55 ca không có kết quả vì kiểm sanity của baseline ("margin thắng oracle ngoài sai số số học"); lỗi numerics này đã
biết từ L4.4. Các ca này bị loại, không sửa.

## Kết quả

| Đầu tư so với J1 | wide (h/τ 2–32): max | short (h/τ ≤ 2): max | short: số regime ≥ 3% |
|---|---|---|---|
| Chỉ state tươi | 2,46% | **6,62%** | 27/635 |
| Chỉ model đúng | 2,17% | 0,99% | 0 |
| Cả hai (oracle) | 2,47% | **6,63%** | 30/635 |
| State tươi + M0 **gây hại** | tới −15,6% (33 regime ≤ −2%) | tới −5,4% | — |

1. **Baseline đơn giản gần tối ưu ở hầu hết miền.** Trung vị lợi tối đa (cả hai repair) chỉ 0,11% (wide) và 1,07%
   (short).
2. **State có giá trị** (2–6,6% C̄) chỉ khi **horizon ngắn (h ≲ τ đến 2τ)**, mode đổi nhanh hơn tuổi telemetry
   (κ ≲ 0,3τ), luồng chuyển lớn (u/μ 0,15–0,175) và tải vừa (λ 6–7). Đây là "vùng A" cũ, giờ đo so với baseline có margin.
3. **Model đúng một mình không đáng đầu tư** ở mọi nơi đã quét (≤ 2,2%). Giá trị riêng khổng lồ của model
   (Ḡ_M|S1 tới 57%) chỉ xuất hiện khi đã có state tươi. Đi kèm là **state tươi + M0 gây hại tới 15,6%, kể cả khi đã chỉnh
   margin**, ở vùng h dài, κ nhỏ, λB gần bão hòa.
4. **Không có cộng hưởng đáng kể:** lợi của cả hai vượt max(từng cái) tối đa 0,5 pp.

## Giới hạn

- S1 = backlog **và mode oracle** (D22 chưa có), nên "state tươi gây hại" là của state oracle, không phải telemetry thực.
- Chỉ biên độ ±6.
- Lưới margin chặn ở 5% (ρ* = 5% ở vài ca), nên baseline có thể còn tốt hơn; kết luận 1 chỉ mạnh thêm.
- Vùng h/τ ≤ 1 (quyết định giữ ngắn hơn tuổi telemetry) có thể không thực tế; L4.8 quyết.
- 1188 regime mới là discovery. Nếu miền L4.8 phủ h/τ dài hoặc rất ngắn, phần đó không còn là held-out "miễn phí".

Tệp: [wide/heat_max.png](wide/heat_max.png), [short/heat_max.png](short/heat_max.png), `*/metrics.csv`, code
`experiments/explore_p4/`.
