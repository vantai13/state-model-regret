# L7.4 — Hình (mỗi hình đúng một claim)

Doan Van Tai — **AI (Claude) soạn theo ủy quyền** (04/11/2026). Script [`figures_l74.py`](../../experiments/explore_ctmc/figures_l74.py)
chỉ đọc file đã lưu, không gọi evaluator:

  python -m experiments.explore_ctmc.figures_l74

Output ở `results/explore_ctmc/figures_l74/`. Số liệu vẽ từng điểm nằm trong `figure_data.csv`, dùng làm bảng thay hình.

**Màu.** Ba slot đầu của bảng màu tham chiếu dataviz (xanh `#2a78d6`, cam `#eb6834`, aqua `#1baf7a`) đã chạy validator
`--pairs all`, light mode, và qua các kiểm tra cứng. Aqua có tương phản 2,74 : 1 (< 3 : 1), nên mỗi chuỗi có thêm hình
marker riêng và legend.

| Hình | Claim | Nguồn dữ liệu | Đọc | n |
|---|---|---|---|---|
| [F1](../../results/explore_ctmc/figures_l74/F1_onset.png) | C1 luật bậc một | a = 6: `runs/asym` + `m0/asym`; a = 3: `check_l72.load('a3')`; hai thang: `check_l73.load()` (asym ∪ sobol) | \|G_S − z_pred1\| ở cùng h giảm qua 0,1 pp trong vùng 4–7·T_int ở cả ba nguồn. Giá trị 1e−6 là sàn vẽ (sai số 0) | 231 / 831 / 1.660 |
| [F2](../../results/explore_ctmc/figures_l74/F2_static.png) | C2 planner dừng | như F1, δ ≠ 0 | regret Static dưới 0,1% sau 7·T_int; 1e−5 là sàn vẽ (regret 0) | 231 / 755 / 1.660 |
| [F3](../../results/explore_ctmc/figures_l74/F3_band.png) | C3 dải giúp hẹp | `l72/ZEROFIT_a3.csv`, `ZEROFIT_a6_xs.csv`, `ZEROFIT_a7p5.csv`, lát x, κ = 1/5, u = 1 | z_∞ > 0 chỉ ở 0 < x ≲ 0,25. Trục y cắt ở −8 (đuôi tới −150). Họ a = 7,5 có λA = 8, khác hai họ kia | 59 / 59 / 29 |
| [F4](../../results/explore_ctmc/figures_l74/F4_backlog.png) | C4 harm chỉ với backlog | `runs_d22/*`, dòng G_S < −0,5% | F/G_S trung vị 0,89 ở κ ≈ 0,03, giảm còn 0,49 ở κ ≈ 3. n trùng D-R1 (949) | 949 |
| [F5](../../results/explore_ctmc/figures_l74/F5_planner.png) | C5 planner ngầm (giả thuyết) | mọi truth ctmc-v1 a = 6 (`runs/`, `runs_ko/`, `runs_d22/`), mỗi (tham số, h) một dòng; h ≥ 4·T_int, δ ≠ 0 | harm: M0 chọn action dài hạn ở 0,895 (cũ) so với 0,723 (mới); help: 0,257 so với 0,345. **Sau mở, mô tả**. SUMMARY §11A ghi n 543 trên tập hẹp hơn, cùng giá trị | 604 harm / 110 help |
| [F6](../../results/explore_ctmc/figures_l74/F6_clocks.png) | C6 hai đồng hồ | `runs/asym` + `m0/asym`, \|z_∞\| ≥ 0,5 (đúng đại lượng của AS-R4) | ρ = −0,921 (h/T_int) so với −0,735 (h/κ), tái lập đúng `score_asymptote.json` | 210 |
| F7 | τ, liều–đáp ứng (chưa claim) | nhánh `explore/tau-l75`: `results/explore_ctmc/l75/F7_tau_zinf.png`, `F7_data.csv` (commit `a621c633`) | trung vị z_∞ theo τ/T_int theo tầng x: ngoài dải giúp harm tăng rồi bão hòa ở τ ≈ 0,3–1·T_int; trong dải đổi dấu. **Chỉ zero-fit**, chưa truth, chưa được viết thành claim | 91 regime |

**Lưu ý khi dùng trong paper:**
- F1, F2 trộn các nguồn có thiết kế khác nhau (asym, Sobol, lát x). Số điểm theo h/T_int phản ánh lưới, không phản ánh tần
  suất.
- F5 là phân tích sau khi mở, không phải test. Chỉ dùng để minh họa giả thuyết C5, không làm bằng chứng.
- C7 (representation) không có hình riêng: nó so hai bảng chấm (bridge), nên dùng bảng sẽ rõ hơn.
