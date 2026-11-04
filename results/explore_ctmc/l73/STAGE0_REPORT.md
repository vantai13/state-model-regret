# L7.3 Phần 2 — Stage 0: evaluator hai thang (ctmc-v2), control, số zero-fit

Doan Van Tai — **AI (Claude) thực hiện theo ủy quyền** (04/11/2026). Không phải author-self. **Không có truth** ngoài hai
regime control C2a, C2b; cả hai bị loại khỏi mọi case list và mọi thẻ.
- Code: [SPEC_v2](../../../experiments/explore_ctmc/SPEC_v2.md), `ctmc2.py`, `mc2.py`, `controls2.py`, `design_l73.py`,
  `scan2.py`, `zf2_report.py`, `check_l73.py`.
- Tests: `tests/test_explore_ctmc2.py` (11 test).

## 1. Đã làm theo checklist Stage 0

| # | Việc | Trạng thái |
|---|---|---|
| 1 | Namespace ctmc-v2, SPEC một trang trước code | Xong. 4 mode mỗi path (σ_f, σ_s), index 4n + m |
| 2 | Mặc định | Đỉnh a_f + a_s = 6; f ∈ {1/20, 1/5, 1/2}; T_s/T_f ∈ {10, 100}; T_f ∈ {1/5, 1}; λ + u ≤ 9 |
| 3 | M0 với phản xạ tổng quát | Xong. q = C + max(n, −min_{s≤t} C), dạng đóng theo ba hình dạng của drift (D, PM, MPM) |
| 4 | Control (a)–(f) | Xem §2: (e) trượt theo tiêu chí bit-identity, xử lý bằng quy tắc một máy |
| 5 | Đại lượng dừng | T_int, T_relax = 1/\|Re λ₂\|, so với công thức §3d |
| 6 | Case list write-once | asym 100 regime × 13 h; mid 180; sobol 360; xs 411. Loại 1 case trùng control, 580 điểm vượt trần N/tải |
| 7 | Zero-fit | 1.051/1.051 case COMPLETED, 0 UNRESOLVED |
| 8 | Guard | Truth bị từ chối trừ a_s = 0, CONTROL_REGIMES, hoặc `locks_l73.json` |
| 9 | Xuất số | `ZEROFIT_2s.csv`, `zerofit_summary.json` |

## 2. Control (tiêu chí ghi trước trong SPEC_v2 §6)

| Control | Kết quả | Ghi chú |
|---|---|---|
| (a) a_s = 0 so với ctmc-v1 | **PASS** (attempt02/03): lệch tối đa 2e−12 pp | attempt01 **FAIL**: 7,5e−4 pp do hòa sát T ≈ h được quyết bằng làm tròn; sửa bằng `saturated()` |
| (b) M0 dạng đóng so với tích phân số | **PASS** (attempt03): 6,2e−9 tương đối; 1.620 phép kiểm ở dạng MPM | attempt02 **FAIL**: 1,19e−6 do sai số trapezoid của chính đường tham chiếu |
| (c) Monte Carlo đầu-cuối, CRN | **PASS**: 200.000 episode/regime, \|z\| tối đa 0,79 (C2a), 1,07 (C2b) | Chạy trên GCP |
| (d) N → 2N | **PASS**: truth ở C2b; zero-fit ở case nặng nhất của case list | |
| (e) bit-identity hai máy | **FAIL theo tiêu chí** | Mọi quyết định, z_∞, T_int, N trùng nhau. 7 giá trị tổng có trọng số ở C2a lệch ở bit cuối (≤ 1,1e−14 tương đối) |
| (f) S, M, G_M ≥ −1e−9 | **PASS** | |
| (g) V hai cách; π so với matrix-geometric; bảng mentor | **PASS**; bảng mentor tái lập (§3) | Không chặn |

**Xử lý (e).** Quyết định thay tác giả là **quy tắc một máy**:
- Mọi số dùng cho thẻ và cho phép chấm đều tính trên GCP `dt4n-research-01`.
- 334 case zero-fit ban đầu chạy ở máy local được tính lại trên GCP vào `m0_l73_gcp/`, và so với bản local (§6).
- Runner truth từ chối máy khác.

## 3. Đại lượng dừng: góp ý (a) của mentor được xác nhận

Bảng dừng của mentor (tải 8,5, T_f = 0,5, T_s = 50), tái lập:

| f | Backlog TB | T_int | T_relax/T_int | Công thức §3d |
|---|---:|---:|---:|---:|
| 0 | 10,9 | 16,8 | 1,91 | 16,8 |
| 0,05 | 14,2 | 44,6 | 1,59 | 57,2 |
| 0,2 | 32,3 | 110,6 | 1,60 | 178,6 |
| 0,5 | 85,9 | 224,1 | 1,72 | 421,3 |

Trên 1.051 case, theo tổ hợp thang (trung vị):

| Tổ hợp | T_int (s) | T_relax/T_int | §3d / chính xác |
|---|---:|---:|---:|
| f = 1/20, T_s/T_f = 10 | 12–26 | 1,82–1,91 | 1,11–1,23 |
| f = 1/20, T_s/T_f = 100 | 24–77 | 1,55–1,68 | 1,17–1,38 |
| f = 1/5, T_s/T_f = 10 | 14–36 | 1,77–1,87 | 1,27–1,51 |
| f = 1/5, T_s/T_f = 100 | 50–111 | 1,46–1,66 | 1,55–1,78 |
| f = 1/2, T_s/T_f = 10 | 18–56 | 1,78–1,86 | 1,48–1,76 |
| f = 1/2, T_s/T_f = 100 | 95–129 | 1,41–1,74 | 1,83–1,98 |

- **T_relax/T_int chỉ 1,4–1,9.** Đồng hồ tích phân và đồng hồ chậm nhất gần nhau trong họ model này, như mentor đã thấy.
  Câu hỏi "đồng hồ nào quyết định onset" gần như không phân biệt được ở đây; onset vẫn phải kiểm bằng truth (L73-1).
- **Công thức §3d ước cao hơn 11–98%**, càng sai khi f và T_s/T_f lớn. Chỉ dùng được ở mức bậc độ lớn (đính chính đã ghi
  trong realism v2).

## 4. Zero-fit

- **Dấu z_∞ (asym ∪ sobol ∪ mid).** Harm (z_∞ < −0,5) ở 78–90% regime; help (z_∞ > 0,5) ở 0–8%. Dải help hẹp như một
  thang.
- **Phần backlog của harm, z_F,∞/z_∞, trên dòng harm (trung vị):**

  | f | T_s/T_f = 10 | T_s/T_f = 100 |
  |---|---:|---:|
  | 1/20 | 0,71 | 0,63 |
  | 1/5 | 0,68 | 0,39 |
  | 1/2 | 0,51 | 0,24 |

  So với 0,83–0,90 của ctmc-v1. Thang chậm làm phần "mode" của harm lớn lên. Đây là lý do L73-4 là claim rủi ro thật.
- **Hội tụ của z_pred1 tới z_∞ (asym, trung vị của |z_pred1 − z_∞|):**

  | h/T_int | n dòng | trung vị |z_pred1 − z_∞| |
  |---|---:|---:|
  | (0; 1] | 154 | 8,7 pp |
  | (1; 4] | 246 | 2,4 pp |
  | (4; 7] | 300 | 0,95 pp |
  | (7; 15] | 350 | 0,46 pp |
  | (15; 40] | 203 | 0,20 pp |

  Ở h hữu hạn, z_pred1 khác z_∞ đáng kể. Vì vậy L73-1 so G_S với **z_pred1 ở cùng h**, không so với z_∞ (checklist mục 1).
- **Bộ horizon giữa hai thang (MID, h = 10·T_f = T_s/10).** h/T_int chỉ 0,015–0,27, tức nằm sâu trong vùng state theo mốc
  0,3. Ở đây z_pred1 không dùng được (trung vị từ −69 tới +36), nên L73-3 đo trực tiếp regret, không qua z_pred1.
- **x\* (dấu z_∞, lát x).** Với họ (u = 1, λA = 7): 0,10–0,28 tùy tổ hợp. Với họ (u = 1/2, λA = 8): không có dải help.
- **Chi phí truth ước lượng:** asym khoảng 0,7 CPU-h, sobol 0,8, mid nhỏ. Không case nào ước lượng vượt 900 s. Ước lượng
  thô, sai tới 2 lần.

## 5. Giới hạn và độ phủ

- **Thiếu asym ở tổ hợp nặng nhất** (f = 1/2, T_f = 1, T_s = 100): N > 3000 ngay ở tải thấp, nên chỉ được phủ bởi sobol và
  mid ở tải nhẹ. f = 1/5, T_f = 1, T_s = 100 chỉ có 3 regime asym.
- **Burst bất đối xứng** (GZL22, BAAZ09) **chưa** có trong ctmc-v2, theo đúng nguyên tắc "không đổi hai thứ cùng lúc".
- **Bộ mốc vùng** đổi sang 0,3/3 ([zone_thresholds_L73.md](../../../notes/realism/zone_thresholds_L73.md)); đây là quyết
  định AI theo ủy quyền.

## 6. Tính lại một máy (control (e), xử lý)

334 case zero-fit (asym 100, mid 180, sobol 54) được tính lại trên GCP, rồi so với bản local:
`m0_l73_gcp/` so với `m0_l73/`, kết quả ở [single_host_compare.json](single_host_compare.json).

- 43.692 trường số; 1.072 trường lệch ở bit cuối (tương đối tối đa 8,7e−13).
- N trùng ở mọi case.
- 6.606 trường tỷ lệ Switch khớp tới ≤ 1e−15. Một quyết định lật sẽ làm tỷ lệ nhảy cả khối lượng của một cặp state, nên
  **không có quyết định nào bị lật**.
- z_pred1 lệch tối đa 1e−12 pp.

`ZEROFIT_2s.csv` và `zerofit_summary.json` hiện là bản một máy (`hosts = ['dt4n-research-01']`). Bản trộn hai máy trước
đó được giữ làm lịch sử: `*_mixedhost.*`.

## 7. Bước tiếp theo

1. Thẻ [CARD_L7_3.md](CARD_L7_3.md): AI soạn theo ủy quyền, **chưa khóa**. Nên có mentor review.
2. Tác giả đọc thẻ và `check_l73.py` (đã thử trên dữ liệu giả), rồi nói "khóa".
3. Sau khi khóa: ghi `locks_l73.json` và chạy truth đúng một lần trên GCP (asym, sobol, mid; trần 900 CPU-s mỗi case).
4. Tác giả tự đọc LPC04, BAAZ11, GZL22: **còn mở**, AI không làm thay được.
