# L3R.3 — T07 → code, câu (a)–(n) và danh sách lệch

Người phụ trách: **Doan Van Tai** · 28–29/10/2026 · DL-066–067.
Đọc/soạn theo ủy quyền, chưa human read-back. Không coi việc đọc code là test PASS.
Pilot snapshot byte-identical từ `explore-v13-pilot` (`a7435e9`); nhãn trong docstring
“mọi regime mới/không overlap” đã bị L3R.1 bác bỏ, không adopt lại.

## Ánh xạ 14 câu hỏi

| Câu | Công thức/quyền thông tin | Code được đọc | Kết luận có điều kiện / phép kiểm |
|---|---|---|---|
| (a) | p(y), atom và support | pilot_population.py:57–81; cells.py:32; stationary_spectral.py:25 | p từ marginal stationary trước Stay; node0 giữ riêng. **Renormalization đổi cả weight atom**, nên “atom giữ chính xác” chỉ đúng về node/support, không phải weight unconditional sau truncation. T3 và kiểm sum weights |
| (b) | D(X\|Y) có mode cũ liên hệ backlog, đẩy qua age | cells.py:37–62 | `law.posterior(index)` cho old mode, khởi tạo joint mass tại đúng y; loop120·ref slot pre-Stay. T2 xác suất, C2 và closed R2 mode check |
| (c) | True posterior/shared belief cho M0/M1 | cells.py:32–62; pilot_population.py:84–108 | Một `queue_D`/true-law posterior, cùng vector weights dùng d và dh; không M0 filtering. T2/C2, mutation old-mode và no-age |
| (d) | D10: cost mean-rollout từng state rồi lấy mean theo D | physical.py:24–143; pilot_population.py:118–124 | `dh` tính mean-path idle cost riêng từng q/m; `EDh` mới lấy mean theo weights, không rollout mean-state. **d/dh một phía là idle-gap component**, khác full side JSw−JSt một linear term. Hai phía triệt tiêu linear term khi ghép đúng u. C1/C2 so full side gap đã cộng term đó; D10 fixture/guard |
| (e) | S1 thấy cả hai mode | physical.py:49–55,139–143; pilot_population.py:101–123 | `np.nonzero(union)` gồm q/m; T10 quyết theo hA+hB mỗi cặp state; là quyền oracle mode, không chỉ refresh backlog. T6 và C3 |
| (f) | Switch iff gap<0, tie Stay | pilot_population.py:124; regime.py:51–58 | Strict bool/cut-left đúng quy tắc nominal. T7 cố ý tạo tie; **pilot không trả interval/HOLD cho mọi gap gần0**, giới hạn precision phải giữ cho engine tương lai |
| (g) | C̄ref cùng K/dt với loss | pilot_population.py:139–177 | `C=Lbar['11']` cùng một lần evaluate; không cache Cref mức khác. Test cấu trúc và mutant Cbar_other_dt. Không đồng nghĩa đã hết sai số quadrature |
| (h) | σ̄=E\|Δ\| | pilot_population.py:123,129,157 | `ED−2*T11` đúng vì T11=E[Δ1(Δ<0)], gồm c_sw. Sau đó average theo nodes; là estimate của stakes, chưa benchmark ngoài đời |
| (i) | P_Y(a00≠a01) | pilot_population.py:158–160 | P_flip theo snapshot pairs; khác P_X(oracle Switch), khác P_wrong_ranking theo state. Không đổi nghĩa các cột |
| (j) | Công thức chỉ báo M0-only | population.py/scan.py tại tag, toàn bộ hàm | Không có implementation tái lập chỉ báo đã chọn trong5. **N3 OPEN**; không gọi Spearman reviewer-reported là run này |
| (k) | c_sw một lần, packet·s | pilot_population.py:112–129,141 | Cộng vào dA và dhA; true scoring L=J+a·ED nên chỉ trả khi Switch. Stage3 là scenario ngoài D13v1.2 c_sw0, chưa adopt contractv1.3 |
| (l) | Union không làm đổi state costs; thứ tự hàng đúng | pilot_population.py:84–108; physical.py:49–55,139–143 | Union chọn support; physical d/dh/j chỉ tùy q/m và plant, weights chỉ thành Side.p. Cả bên bảng và weights dùng np.nonzero theo thứ tự hàng. Toy row-permutation test và T6 trên actual posteriors |
| (m) | A1 coherence p/D | pilot_population.py:57–60,88; cells.py:32,45 | Cùng law_for/λ/u/κ/ref trước quadrature. Cắt y và đại diện bin tạo approximate measure khác law đầy đủ; Σnodes wD không cần bằngπ chính xác. T2 tách full-retained propagation và production cost error |
| (n) | Đơn vị y và tuổi | pilot_population.py:88; cells.py:25–45 | y=idx·unit là physical Fraction; queue_D chia lại và reject ngoài lattice; age=120ref=1s. dt giảm thì lattice/prior tính lại; không hiểu idx là packet |

Files: [snapshot pilot](../../../experiments/R3R_02_audit/pilot_population.py),
[cells](../../../src/smr/cells.py), [physical](../../../experiments/A00_engine/physical.py),
[cut](../../../experiments/V13_step1/regime.py),
[T07](../../theory/T07_population_estimand.md),
[test/API layer](../../../experiments/R3R_02_audit/bridge.py).

## Danh sách lệch và giới hạn

| ID | Loại | T07/contract và thực tế | Xử lý |
|---|---|---|---|
| D-A01 | Lựa chọn định nghĩa | Pilot λB6/7 ngoài D4v1.2 λB8; η=u/2 khác headroom ratio | Giữ u trong spec; L3R.5 quyết, không đổi dữ liệu cũ |
| D-A02 | Numerical | Full Y support khác tail cut1e−4 + median bins + renormalize | Đo T2/T3/K/dt; tail probability chưa tự là certified cost bound |
| D-A03 | Numerical | S1 estimand invariant nhưng estimator vẫn qua y nodes | So trực tiếp stationary state costs; κ3 còn UNRESOLVED ở K160 theo khai gốc |
| D-A04 | Thiếu diagnostic | Pilot không tính population cb0/F/V | Prototype finite-toy D22 có test; **chưa coi là D22 đo trên pilot**, L3R.5 quyết báo |
| D-A05 | Claim thiếu provenance | N7 “8 snapshot comparisons” không tìm được code tại tag | Kiểm mới8 snapshot pairs thực tế, báo ngày này; không backdate claim gốc |
| D-A06 | Spec đã làm rõ | S1/S2/S4/S6 của MC trước đó thiếu lời rõ | T07§9/mc_physical_spec lấy R2 và slot order từ tài liệu cũ, trước đọc sâu engine |
| D-A07 | Adapter đã sửa | Fraction toy → LD làm mất exact tie, cost lệch0.15 | Integer-count homogeneity adapter; giữ failed fixture/log và regression, **không đổi production engine** |
| D-A08 | MC arithmetic đã sửa | Raw subtraction gap có roundoff khi true conditional variance0 | Phiên MC độc lập thêm no-idle certificate; raw_gap/raw costs giữ, kiểm lại3 alarm, không nới z |
| D-A09 | Giới hạn thống kê | Bin-policy integral không phải representative-point quadrature; SE rất nhỏ có thể thấy sai số số | Strict z chỉ dùng discrete-node same-law design; full population cộng allowance refinement và ghi nó không certified |
| D-A10 | Precision OPEN | Strict floating signs không tự certify mọi true tie; physical bounds bị lớp pilot bỏ | Không epsilon/clamp, không khóa production v1.3 từ audit này; cần policy HOLD/enclosures trước confirmation |

Đính chính Part1 của hướng dẫn: repo **có evidence L1.5** về checker dùng chung helper
bỏ sót P4 ở test any-belief: [report L1.5, dòng63–81](../l1_5/report.md) và
[test có weighted sum trực tiếp](../../../tests/test_l1_5_identity.py).
Report ghi P4 có1test đỏ ở checker chung,2test đỏ ở checker độc lập; bản replay/log/XML
vẫn được giữ. Vì vậy không chép kết luận “không tìm được bằng chứng” của nguồn lesson
thành fact. Chỉ đối chiếu artifact cũ ở phiên này, không nhận đã chạy lại L1.5 mutants.
Các gap về mức đọc tác giả/P0-V10/L8 không được đóng bằng code hoặc bản soạn theo ủy quyền.
